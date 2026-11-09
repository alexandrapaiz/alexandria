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
#     - [ ] arxiv:<id> -- why -- asked by skills/<slug> -- YYYY-MM-DD
# The separator is U+2014 or the plain ` - ` / ` -- ` above, which is what
# docs/voice/ban-list.md entry 13 requires and what the file now mostly holds.
# Written in ASCII here so this file holds none of the character it reads.
# Lines without an arXiv id are the questions the reading raised, addressed to
# the research seat rather than to a fetcher, and they are skipped here rather
# than treated as malformed.
ITEM = re.compile(r"^\s*-\s*\[(?P<mark>[ xX])\]\s*(?P<body>.*)$")
ARXIV = re.compile(r"arxiv:\s*(?P<id>\d{4}\.\d{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?",
                   re.IGNORECASE)
# The asker, read to this format's own field separator, the way `why` above it
# already is. **It used to take one whitespace token, and that was wrong about
# 52 of the 167 lines in the live file** (measured 2026-11-02): every line the
# chair signs "asked by the chair (owner: ...)" and every line a seat signs
# "asked by the research seat's L-R1 check" displayed as the single word `the`.
# The comment below used to record that truncation as acceptable because the
# field is only for display, which it is, and a display field that answers `the`
# to "who asked for this" is not displaying anything.
#
# The research seat found the sharp end of it on 2026-11-02: `compose` guards
# this field by comparing the parsed value against the first word of what was
# passed, so with a one-token pattern the two sides were the same word and the
# guard could not fail. An asker of "the research seat" composed, passed every
# check, and read back as "the". Widening the pattern is what gives that guard
# something to compare, and `compose` refuses an em dash in either text field,
# so nothing a writer can pass is cut short here.
# **And the separator is not only the em dash, which cost a red `main` on
# 2026-11-02.** `docs/voice/ban-list.md` entry 13 bans every non-ASCII
# character in this repository, amended 2026-09-21 to be the class rather than
# three examples. So the research seat's ASCII sweep of its own blocks is the
# law working, and it writes ` - ` or ` -- ` where this pattern required U+2014.
# Three lines arrived that way and each one parsed with the date, and sometimes
# a paragraph, inside the asker. Repairing the data loses: the next sweep is
# correct and undoes it, and the file still holds 857 non-ASCII characters for
# that sweep to reach. So the parser meets the law instead.
#
# This is a widening and the writer seat's rule against widening a delimiter
# rule still holds, which is why it is worth saying why this one is different:
# a spelling rule is only ever right about the delimiters somebody has already
# typed, and here BOTH forms have been typed deliberately, one by this format
# and one by a standing law. Accepting a form a law mandates is not inviting
# the next convention.
ASKED_BY = re.compile("asked by\\s+(?P<who>.+?)(?:\\s+\u2014|\\s+--(?=\\s)|\\s+-(?=\\s)|\\s*$)")

# The asker, when the asker is a skill. `ASKED_BY` above is for display and is
# still wrong for any decision, because "the chair" and "skills/x" are both
# askers and only one of them is a skill waiting on a read. On 2026-10-05 that
# distinction became load-bearing, because `pending` started treating an asker
# outside `sourced` as a blocked skill. The documented format is the only thing
# that may answer "which skill is stuck on this line", so this pattern matches
# that format and nothing else.
SKILL_ASKER = re.compile(r"asked by\s+(?P<slug>skills/[A-Za-z0-9_-]+)")

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
    # The asker as written, for display: "skills/x", "the chair (owner: ...)".
    # Read to the em dash, so it is the whole asker and not its first word.
    asked_by: str
    line_no: int
    raw: str
    # The skill this line is blocked on, or "" when the asker is not a skill.
    # A seat, a person or an unsigned line all give "", because none of them is
    # a skill waiting on a read. Only this field may decide the order.
    asking_skill: str = ""


def normalise_asker(raw: str) -> str:
    """One asker, as the reader of this format sees it: `the chair (owner: x)`.

    One function rather than two expressions, because `compose` checks the
    writer against the reader and a check whose two sides normalise differently
    fires on its own normalisation rather than on the line. Both callers go
    through here, so the only way that guard can disagree is if the line itself
    does not carry what the writer passed, which is the one thing it is for.
    """
    return " ".join(raw.split()).rstrip(",.").strip()


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
        slug = SKILL_ASKER.search(m.group("body"))
        items.append(Item(
            arxiv_id=arxiv_id,
            paper_id=f"arxiv:{arxiv_id}",
            checked=m.group("mark").lower() == "x",
            asked_by=normalise_asker(who.group("who")) if who else "",
            line_no=n,
            raw=line.strip(),
            asking_skill=slug.group("slug").rstrip("/") if slug else "",
        ))
    return items


def skills_with_claims(conn) -> set[str]:
    """Skill paths that cite at least one claim id, from `promotions`.

    Everything NOT in this set is a skill that cannot cite a single claim, and
    `pending` puts its requests first. Read from `promotions` rather than from
    `skills/` because `skills/` is not in distill's Modal image and should not
    be: baking the library into the reading job would mean every skill edit
    needs a distill redeploy.

    A skill with no `promotions` row at all is correctly absent here, which is
    the case that matters. `skills/agent-containment` has no row because
    `tools/skill_registrar.py` refuses to write one for a skill citing nothing.
    """
    try:
        rows = conn.execute(
            "select path from promotions where kind = 'skill' "
            "and path is not null and array_length(claim_ids, 1) > 0"
        ).fetchall()
    except Exception:                               # noqa: BLE001
        # No table, no permission, no connection. Returning nothing makes every
        # line look blocked, which collapses the order below back to file order:
        # the behaviour this module had before the ordering existed.
        return set()
    return {str(row[0]).rstrip("/") for row in rows}


def pending(text: str, limit: int | None = MAX_PER_RUN,
            sourced: set[str] | None = None) -> list[Item]:
    """Unchecked items, deduplicated, at most `limit`.

    Deduplication is by id and not by line: the same paper asked for twice by
    two skills is one fetch, and striking either line is the research seat's
    business rather than this module's.

    Order is oldest line first WITHIN two groups, and the groups are the point.
    A line asked for by a skill that cannot cite a single claim comes before a
    line asked for by a skill that already cites plenty, because the first one
    is blocked and the second one is being improved.

    ## Why the order had to change on 2026-10-05

    Strict file order is fair and it starved the thing it was built for. The
    queue held 47 pending lines, `MAX_PER_RUN` is 6, and the 2026-09-30
    containment requests sat behind 27 older lines from two skills that already
    carry claims. So `skills/agent-containment` was eight runs from being read,
    and it is a draft with `claims: []` that cannot be revised, cannot appear in
    `skills_needing_revision`, and holds thirteen tests red across four suites
    until one of its papers is distilled. Meanwhile the lines ahead of it were
    asked for by skills that are already published and already sourced.

    FIFO is the right default for a queue of equals. These are not equals: one
    line unblocks a skill and the next one footnotes one.

    `sourced` absent means no grouping, which is the old behaviour exactly.

    ## Why classification comes before deduplication (2026-11-02)

    This function used to deduplicate first and classify the survivor, and the
    survivor was whichever line came first in the file. So the group a paper
    landed in was decided by line position rather than by who was waiting on
    it, and line position in this file is decided by whichever merge landed
    last. Two merges of identical content, ordered differently, gave different
    reading orders: the research seat measured three priority members at
    positions one, two and three one way, and zero members at eighty-eight,
    eighty-nine and ninety the other.

    The file has two writers today and a third was being proposed, which is a
    third way for a line to land on top. Rather than make every writer preserve
    an order nothing declares, the two steps are reversed here, which removes
    the dependence instead of managing it.

    So: every unchecked line is classified, and a paper is blocked when ANY
    line asking for it is a blocked skill's request. That is the reading the
    group was always for, because one fetch serves every line, and the fetch
    unblocks the blocked asker whether its line is first or last. The line kept
    is the earliest of the ones that decided the group, so the asker reported
    is the asker the priority is owed to.
    """
    def is_blocked(item: Item) -> bool:
        # Three kinds of line are one kind here: a line nobody signed, a line a
        # seat or the chair signed, and a line a skill that already cites claims
        # signed. None of them is a skill that cannot cite a claim, which is the
        # only thing the group is for.
        return bool(sourced is not None and item.asking_skill
                    and item.asking_skill not in sourced)

    lines: dict[str, list[Item]] = {}
    for item in parse(text):
        if item.checked:
            continue
        lines.setdefault(item.paper_id, []).append(item)

    # Each entry is `(the group's earliest line, the item to serve)`. The two
    # are not always the same line and that is the whole of the 2026-11-09
    # repair below.
    blocked: list[tuple[int, Item]] = []
    rest: list[tuple[int, Item]] = []
    for group in lines.values():
        earliest = min(item.line_no for item in group)
        deciding = [item for item in group if is_blocked(item)]
        if deciding:
            blocked.append((earliest, min(deciding, key=lambda i: i.line_no)))
        else:
            rest.append((earliest, min(group, key=lambda i: i.line_no)))

    # Oldest line first within each group, keyed on the group's EARLIEST line
    # rather than on the line of the item being served. The sort is what makes
    # the output a function of the file's content and not of its line order,
    # and keying it on the served item's line did not finish that job.
    #
    # ## Why the key had to change on 2026-11-09
    #
    # The item served from a blocked group is the earliest of the lines that
    # DECIDED the group, which is deliberate and stays: the asker reported has
    # to be the asker the priority is owed to. But that is a subset of the
    # group, so its line is not the group's earliest, and a subset's position
    # is exactly what moves when the file's duplicate lines are permuted.
    #
    # Eight of the twelve ids repeating on the live queue today are signed by a
    # skill on one of their two lines and unsigned on the other, so for each of
    # them `deciding` holds one line and which physical position that line
    # occupies is decided by whichever merge landed last. Swapping such a pair
    # in place moved the served order, which is the defect the 2026-10-05 and
    # 2026-11-02 notes above each removed one layer of. The earliest line of
    # the group is invariant under permuting the group's own lines, because
    # both positions stay in the group, so this is the key that finishes it.
    #
    # `tests/test_reading_queue.py::
    # test_the_live_queue_order_does_not_move_when_its_duplicates_are_reordered`
    # is the assertion, and it was red on `main` when this landed. That test's
    # docstring said no live duplicate was signed by a skill at all, which was
    # true when it was written and is not true now, and the condition it
    # described as unreachable is what made it fail.
    blocked.sort(key=lambda pair: pair[0])
    rest.sort(key=lambda pair: pair[0])
    out = [item for _, item in blocked] + [item for _, item in rest]
    return out[:limit] if limit else out


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


def sourced_from_tree(root: str | pathlib.Path = ".") -> set[str]:
    """`skills_with_claims`'s answer, read from the working tree instead of a table.

    For `--order` only, and never for a run. The table is the truth, because a
    skill's claim ids are written to `promotions` by the registrar and a working
    tree can be any branch. This is the offline stand-in a reader has when there
    is no `DATABASE_URL` in the sandbox, which is every seat's sandbox, and it is
    labelled as a stand-in everywhere it is printed.
    """
    sourced = set()
    for skill in sorted(pathlib.Path(root).glob("skills/*/SKILL.md")):
        try:
            cited = re.search(r"claims:\s*\[([^\]]*)\]", skill.read_text())
        except OSError:
            continue
        if cited and cited.group(1).strip():
            sourced.add(f"skills/{skill.parent.name}")
    return sourced


# The documented format, as one template rather than as prose a writer retypes.
# `docs/research/reading-queue.md`'s own header states it, every reader in this
# module parses it, and until 2026-11-02 the only writer of it was a hand.
LINE = "- [ ] arxiv:{arxiv_id} \u2014 {why} \u2014 asked by {asked_by} \u2014 {date}"


def normalise_id(raw: str) -> str:
    """`arxiv:2602.05366v2`, `2602.05366`, ` 2602.05366 ` -> `2602.05366`.

    The version suffix is dropped because `papers` is keyed on the bare id and
    `resolve` looks the line up there: a line that carries `v2` and a corpus row
    that does not are the same paper, and keeping the suffix here would make the
    duplicate check below miss its own file. `parse` already reads a `v2` line
    correctly, so existing lines are unaffected.
    """
    found = ARXIV.search(raw if raw.lower().startswith("arxiv:") else f"arxiv:{raw}")
    return found.group("id") if found else ""


def hits(text: str, arxiv_id: str) -> list[Item]:
    """Every checklist line in the file that already carries this id.

    This is the file's own rule, which is the first thing its header asks a
    writer to do and the thing nothing enforced:

        grep -n '<the arxiv id>' docs/research/reading-queue.md

    That rule arrived after `INC-2026-10-27-a-paper-struck-as-read-was-requeued-
    as-the-highest-value-unread-paper-the-next-day`, where a line landed 1,374
    lines below a strike of the same id and repeated the mis-attribution the
    strike existed to correct. A rule in a header is not a gate: append-only is
    exactly the property that means a writer never has to read the file, so the
    one writer who most needs the grep is the one the format lets skip it.

    Matched on the normalised id, so a `v2` line and a bare line collide the way
    they do in `papers`.
    """
    want = normalise_id(arxiv_id)
    return [i for i in parse(text) if normalise_id(i.arxiv_id) == want]


def compose(arxiv_id: str, why: str, asked_by: str, date: str) -> str:
    """One queue line in the documented format, or a reason it cannot be one.

    Raises `ValueError` rather than returning something malformed. A malformed
    line in an append-only file is invisible: `parse` skips any line it cannot
    read, so a request that does not match the format is not a broken request,
    it is a request that silently does not exist. That is the failure this
    whole path is built to make impossible, so it is checked before the write
    and again after it.
    """
    want = normalise_id(arxiv_id)
    if not want:
        raise ValueError(f"{arxiv_id!r} is not an arXiv id this file's parser reads")
    why = " ".join(why.split())
    if not why:
        raise ValueError("a line needs a reason: it is what the research seat "
                         "reads to decide whether the paper answers it")
    asked_by = " ".join(asked_by.split())
    if not asked_by:
        raise ValueError("a line needs an asker: `pending` groups by it and the "
                         "strike is addressed to it")
    if "\u2014" in why or "\u2014" in asked_by:
        raise ValueError("neither the reason nor the asker may contain an em "
                         "dash: it is this format's field separator")
    line = LINE.format(arxiv_id=want, why=why, asked_by=asked_by, date=date)
    # The writer checked by the reader, which is the only check worth having
    # here. Everything above is a rule about the format; this asks the parser
    # that actually decides what distill fetches.
    read = parse(line)
    if len(read) != 1 or read[0].arxiv_id != want or read[0].checked:
        raise ValueError(f"composed a line this module's own parser does not "
                         f"read back as one unchecked request: {line!r}")
    # The whole asker, not its first word. Until 2026-11-02 this compared
    # `read[0].asked_by` against `asked_by.split()[0]`, and the reader took one
    # whitespace token, so the two sides were the same word by construction and
    # this guard could not refuse any asker a writer could pass. The research
    # seat measured it: "the research seat" composed, passed every check here,
    # and went into an append-only file reading "the".
    if read[0].asked_by != normalise_asker(asked_by):
        raise ValueError(f"composed a line whose asker reads back as "
                         f"{read[0].asked_by!r} rather than {asked_by!r}")
    return line


def add(text: str, arxiv_id: str, why: str, asked_by: str, date: str,
        section: str = "") -> tuple[str, str]:
    """The file's new text and the line that was added, or a raised reason.

    Appends, never inserts. `section` names a `## ` heading to file the line
    under, and it is honoured only when it is the file's **last** heading or
    absent from it: filing under an earlier heading would mean writing into the
    middle of a file two seats treat as append-only, which is how a concurrent
    append loses a line. An earlier heading is refused with its line number
    rather than silently appended to the end, because a writer who named a
    section wants that section.
    """
    line = compose(arxiv_id, why, asked_by, date)
    found = hits(text, arxiv_id)
    if found:
        raise ValueError(
            f"{normalise_id(arxiv_id)} is already in this file on "
            + "; ".join(f"line {i.line_no} ({'struck' if i.checked else 'open'})"
                        for i in found)
            + ". A struck line means the paper is read and the answer is on it; "
              "an open line means add your reason to it rather than opening a "
              "second.")
    headings = [(n, l.strip()) for n, l in enumerate(text.splitlines(), start=1)
                if l.startswith("## ")]
    body = text.rstrip("\n")
    if section:
        want = f"## {section}" if not section.startswith("## ") else section
        existing = [n for n, l in headings if l == want]
        if existing and headings and headings[-1][1] != want:
            raise ValueError(
                f"{want!r} is at line {existing[0]} and is not the last "
                f"heading in the file, so filing under it would write into the "
                f"middle of an append-only file. Name a new section.")
        if not existing:
            body += f"\n\n{want}"
    return f"{body}\n\n{line}\n", line


def _flag(argv: list[str], name: str, default: str = "") -> str:
    """`--name value`, or `--name=value`, or the default."""
    for n, arg in enumerate(argv):
        if arg == name and n + 1 < len(argv):
            return argv[n + 1]
        if arg.startswith(f"{name}="):
            return arg.split("=", 1)[1]
    return default


def add_cli(argv: list[str], today: str = "") -> int:
    """`--add`, the one command that puts a paper in front of a scheduled job.

    Why this is a command rather than a hand edit, in the words of the handoff
    that asked for it. On 2026-11-02 the research seat asked this seat to run
    `modal run pipeline/ingest.py --ids ...` for two papers the fourteen-day
    ingest window can never reach, and said in the same message that the
    credential for it has been absent for eleven consecutive runs. The by-id
    backfill is a hand run by construction. This file is the other route to the
    same place, it is drained by a scheduled job, and writing to it needs no
    credential at all, so it is the route that can be taken from here.

    What it prints is the part that matters as much as what it writes: the
    pending count before and after, and the two conditions between an appended
    line and a paper in the corpus. The queue's CONTENT is baked into distill's
    image at deploy time, so a line appended today reaches the cron on the next
    `modal deploy` and reaches a hand `modal run` immediately.
    """
    import datetime

    path = _flag(argv, "--file", QUEUE_PATH)
    text = read_file(path)
    if not text:
        print(f"no reading queue at {path}", file=sys.stderr)
        return 1
    date = today or _flag(argv, "--date") or \
        datetime.date.today().isoformat()
    try:
        after, line = add(
            text,
            arxiv_id=_flag(argv, "--add"),
            why=_flag(argv, "--why"),
            asked_by=_flag(argv, "--asked-by"),
            date=date,
            section=_flag(argv, "--section"),
        )
    except ValueError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2
    before = len(pending(text, limit=None))
    now = len(pending(after, limit=None))
    # The reader's count, not an increment this function assumes. A line that
    # composes and parses can still fail to become a request, and the only
    # thing that can say it did is `pending` over the file as it will be.
    if now != before + 1:
        print(f"refused: the queue goes from {before} pending to {now}, and an "
              f"append must be exactly one more", file=sys.stderr)
        return 2
    if "--dry-run" in argv:
        print(line)
        print(f"dry run, nothing written. {before} pending now, {now} after",
              file=sys.stderr)
        return 0
    pathlib.Path(path).write_text(after)
    print(line)
    print(f"appended to {path}: {before} pending before, {now} after, "
          f"{MAX_PER_RUN} of them per distill run", file=sys.stderr)
    print("the route from here: distill resolves every unchecked line against "
          "`papers` and ingests what the corpus has never seen at tier b with a "
          "deep_read triage row, ahead of the day's intake. The queue's content "
          "is baked into distill's image, so this line reaches the cron on the "
          "next `modal deploy` and a hand `modal run pipeline/distill.py::distill` "
          "immediately.", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--add" in argv or any(a.startswith("--add=") for a in argv):
        return add_cli(argv)
    long = "--long" in argv
    # The order a distill run will actually use. Without this the CLI printed
    # file order and the run used the grouped order, so the one tool that exists
    # to read this module's state could not show the thing that decides what
    # gets read. That is how `asked by the chair` spent two days parsing as a
    # blocked skill: nothing printed the group a line landed in.
    order = "--order" in argv
    args = [a for a in argv if not a.startswith("-")]
    text = read_file(args[0] if args else QUEUE_PATH)
    if not text:
        print(f"no reading queue at {args[0] if args else QUEUE_PATH}", file=sys.stderr)
        return 1
    sourced = sourced_from_tree() if order else None
    items = pending(text, limit=None, sourced=sourced)
    for n, item in enumerate(items):
        mark = ""
        if order:
            blocked = bool(item.asking_skill) and item.asking_skill not in sourced
            mark = f"\t{'blocked' if blocked else 'waits'}" \
                   f"\t{item.asking_skill or '-'}" \
                   f"\t{'NEXT' if n < MAX_PER_RUN else ''}"
        print(f"{item.paper_id}\t{item.asked_by}\tline {item.line_no}{mark}"
              if long or order else item.paper_id)
    print(f"{len(items)} pending, {MAX_PER_RUN} of them per distill run",
          file=sys.stderr)
    if order:
        print(f"order: grouped, blocked skills first. `sourced` is "
              f"{len(sourced)} skills read from the working tree, which stands "
              f"in for `promotions` and may differ from it.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
