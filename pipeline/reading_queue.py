"""The reading queue, parsed and put at the front of distill's drain.

    python3 pipeline/reading_queue.py                 # pending ids, one per line
    python3 pipeline/reading_queue.py --long          # with who asked and why

ADR-35 made reading a precondition of skill creation: the skill seat surveys
the claim graph, reads its papers in full, and appends what it could not read
to docs/research/reading-queue.md. That file is a request addressed to the
pipeline, and until this module existed nothing in the pipeline read it. A
queue that only a human drains is a list of things nobody did.

So distill reads it first. Every unchecked line's arXiv id is resolved against
`papers`, anything the corpus has never seen is ingested from arXiv on the
spot, and the result goes to the front of the day's drain, ahead of the daily
intake. The queue is a handful of lines a week and distill's `max_papers` is
30, so "ahead of" costs the intake a few slots on the days the skill seat has
asked for something and nothing at all on the other days.

Each id is printed on its own `reading-queue:` line in the run log, with what
happened to it, because the research seat is the one who strikes the line and
it cannot strike what it cannot see (charter: the research seat drains this
file, reads, files, and strikes with a date and a PR).

Nothing here decides what a paper is worth. A line in that file is the skill
seat saying it needed the paper and could not read it, which is reason enough;
triage's job is to filter a firehose nobody asked for.
"""

from __future__ import annotations

import pathlib
import re
import sys
from typing import Callable, NamedTuple

QUEUE_PATH = "docs/research/reading-queue.md"

# The format the file documents at its own head:
#     - [ ] arxiv:<id> — why — asked by skills/<slug> — YYYY-MM-DD
# Lines without an arXiv id are the questions the reading raised, addressed to
# the research seat rather than to a fetcher, and they are skipped here rather
# than treated as malformed.
ITEM = re.compile(r"^\s*-\s*\[(?P<mark>[ xX])\]\s*(?P<body>.*)$")
ARXIV = re.compile(r"arxiv:\s*(?P<id>\d{4}\.\d{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?",
                   re.IGNORECASE)
ASKED_BY = re.compile(r"asked by\s+(?P<who>\S+)")

# How many queue lines one run will take. The queue is drained by two seats and
# refilled by one, so a backlog is possible: twelve lines landed on 2026-09-26
# from a single skill run. Six per day drains that in two days without ever
# handing a whole run to the queue, and `--max-papers` still bounds the total.
MAX_PER_RUN = 6

# A paper nobody triaged still needs a triage row, or the next triage run spends
# a model call deciding about a paper that has already been distilled. The model
# name follows `rule:backfill`, the existing convention for a row written by a
# rule rather than by a model.
TRIAGE_MODEL = "rule:reading-queue"


class Item(NamedTuple):
    arxiv_id: str          # 2602.12670
    paper_id: str          # arxiv:2602.12670, the key in `papers`
    checked: bool
    asked_by: str          # skills/<slug>, or "" when the line does not say
    line_no: int
    raw: str


def parse(text: str) -> list[Item]:
    """Every checklist line in the file that carries an arXiv id, in file order."""
    items = []
    for n, line in enumerate(text.splitlines(), start=1):
        m = ITEM.match(line)
        if not m:
            continue
        found = ARXIV.search(m.group("body"))
        if not found:
            continue  # a question for the research seat, not a paper to fetch
        arxiv_id = found.group("id")
        who = ASKED_BY.search(m.group("body"))
        items.append(Item(
            arxiv_id=arxiv_id,
            paper_id=f"arxiv:{arxiv_id}",
            checked=m.group("mark").lower() == "x",
            asked_by=who.group("who").rstrip(",.") if who else "",
            line_no=n,
            raw=line.strip(),
        ))
    return items


def pending(text: str, limit: int | None = MAX_PER_RUN) -> list[Item]:
    """Unchecked items, oldest line first, deduplicated, at most `limit`.

    Deduplication is by id and not by line: the same paper asked for twice by
    two skills is one fetch, and striking either line is the research seat's
    business rather than this module's.
    """
    seen, out = set(), []
    for item in parse(text):
        if item.checked or item.paper_id in seen:
            continue
        seen.add(item.paper_id)
        out.append(item)
        if limit and len(out) >= limit:
            break
    return out


def read_file(path: str | pathlib.Path = QUEUE_PATH) -> str:
    """The queue file's text, or "" when it is not where it should be.

    Absent is not an error. Distill runs on Modal with the file baked into the
    image, and a run that cannot find it should distill the day's intake and
    say the queue was unreadable, not fail.
    """
    try:
        return pathlib.Path(path).read_text()
    except OSError:
        return ""


def resolve(conn, items, *, fetch_metadata: Callable[[str], dict | None],
            log=print) -> list[tuple]:
    """Resolve queue items into rows distill can distill, ingesting what is new.

    Returns rows shaped exactly like distill's own `distill_queue` select,
    `(id, title, abstract, triage_decision, source)`, so the caller can put
    them at the front of its list and change nothing else.

    Four things can happen to a line, and each one prints:

    - `queued`: the corpus has the paper and has not distilled it. Read today.
    - `ingested`: the corpus had never seen it. Fetched from arXiv, inserted,
      read today.
    - `already read`: the corpus distilled it before the line was written. The
      research seat can strike the line now; nothing is re-read.
    - `unavailable`: arXiv returned no metadata for the id, which usually means
      the id is wrong. The line stays for a human.
    """
    rows = []
    for item in items:
        who = f" (asked by {item.asked_by})" if item.asked_by else ""
        found = conn.execute(
            "select title, abstract, source, distilled_at from papers where id = %s",
            (item.paper_id,),
        ).fetchone()
        if found:
            title, abstract, source, distilled_at = found
            if distilled_at is not None:
                log(f"reading-queue: {item.paper_id} already read "
                    f"{str(distilled_at)[:10]}, nothing to do{who}")
                continue
            log(f"reading-queue: {item.paper_id} queued, read first today{who}")
            rows.append((item.paper_id, title, abstract, "deep_read", source))
            continue

        meta = fetch_metadata(item.paper_id)
        if not meta:
            log(f"reading-queue: {item.paper_id} unavailable at arXiv, "
                f"left on the queue{who}")
            continue
        conn.execute(
            """
            insert into papers (id, source, tier, title, authors, abstract, url, published_at)
            values (%s, 'reading-queue', 'b', %s, %s, %s, %s, %s)
            on conflict (id) do nothing
            """,
            (item.paper_id, meta["title"], meta.get("authors") or [],
             meta.get("abstract"), meta["url"], meta.get("published_at")),
        )
        conn.execute(
            """
            insert into triage_log (paper_id, decision, model, reasoning)
            values (%s, 'deep_read', %s, %s)
            """,
            (item.paper_id, TRIAGE_MODEL,
             f"requested in {QUEUE_PATH}"
             + (f" by {item.asked_by}" if item.asked_by else "")),
        )
        log(f"reading-queue: {item.paper_id} ingested from arXiv, "
            f"read first today{who}")
        rows.append((item.paper_id, meta["title"], meta.get("abstract"),
                     "deep_read", "reading-queue"))
    return rows


def merge(first: list[tuple], intake: list[tuple], max_papers: int) -> list[tuple]:
    """The queue's rows, then the day's intake, deduplicated, at most `max_papers`.

    "Ahead of the daily intake" is this function, and the only subtlety is the
    overlap: a requested paper the corpus already holds is usually in the
    intake too, once triage has routed it, and distilling it twice would write
    every claim twice. First position wins and the duplicate is dropped.

    The queue is not bounded by `max_papers`, only trimmed against it: a day
    whose queue is longer than the cap reads the queue and no intake, which is
    the correct reading of "first". `MAX_PER_RUN` is what keeps that from
    becoming a week of no intake at all.
    """
    already = {row[0] for row in first}
    room = max(0, max_papers - len(first))
    return first + [row for row in intake if row[0] not in already][:room]


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    long = "--long" in argv
    args = [a for a in argv if not a.startswith("-")]
    text = read_file(args[0] if args else QUEUE_PATH)
    if not text:
        print(f"no reading queue at {args[0] if args else QUEUE_PATH}", file=sys.stderr)
        return 1
    items = pending(text, limit=None)
    for item in items:
        print(f"{item.paper_id}\t{item.asked_by}\tline {item.line_no}" if long
              else item.paper_id)
    print(f"{len(items)} pending, {MAX_PER_RUN} of them per distill run",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
