#!/usr/bin/env python3
"""corpus_row.py — is this paper absent from the corpus, or present and discarded?

    python3 tools/corpus_row.py 2610.07639
    python3 tools/corpus_row.py arxiv:2610.07639v2 2605.18583
    python3 tools/corpus_row.py 2610.07639 --sql      # print the query, run nothing

Those two states need opposite repairs and nothing here could tell them apart.
A paper with no row was never fetched, so the repair is an intake. A paper with
a row and a `discard` decision was fetched and judged, so the repair is the
judgement, and an intake would change nothing because `on conflict (id) do
nothing` is what the insert says. The research seat hit this on 2026-11-09 for
`2610.07639` and routed the query to whoever holds a read credential; it had hit
it before, for `2609.08371`, and the queue line records the same question twice.

**The reason this is a tool and not a sentence in a handoff is that the obvious
query answers the wrong one of the two states.** `papers.id` holds arXiv papers
in two shapes, `arxiv:2610.07639` and `arxiv:2610.07639v2`, because
`pipeline/ingest.py` stores whatever version arXiv's feed put on the entry while
`pipeline/reading_queue.py` strips it. So `where id = 'arxiv:2610.07639'` misses
every paper that arrived through the `arxiv` feed, and it misses it silently, by
returning the empty result that means absent. That is
`INC-2026-10-05-absence-asserted-from-an-unnormalised-id-join`, where a seat
reported five of six papers absent on that query and a corrected measurement
found 21 rows for 19 papers, two of them already serving claims in production.
322 arXiv papers were held twice that day, 656 rows, 73 pairs triaged twice with
different decisions.

So every lookup here matches on the version-stripped id and reports **every**
shape it finds, which makes a duplicate pair visible as a duplicate instead of
resolving silently to one half of it.

## The exit code is the answer

0  present, and the latest decision keeps it (`index`, `distill`, `deep_read`)
1  present, and the latest decision is `discard` — fetched and thrown away
2  present with no triage row at all — fetched, never judged
3  absent: no row under any shape of the id
4  cannot answer: no credential here, or the connection failed

A seat scripting against this wants 3 against 1, because those are the two the
research seat's question is between:

    python3 tools/corpus_row.py 2610.07639; case $? in
      3) echo "intake it" ;; 1) echo "triage threw it away" ;; esac

## What it needs

`NEON_RO_URL` (preferred, read-only) or `DATABASE_URL`, and `psycopg`. Every
statement is a SELECT and `tests/test_corpus_row.py` asserts that by parsing
them rather than by trusting this sentence. No seat in this company holds either
credential: `NEON_RO_URL` is an owner secret, pending in `docs/backlog.md` since
2026-09-26, and the Modal workspace that holds `DATABASE_URL` has been off since
2026-10-23. Until one of them lands this command exits 4 from a seat sandbox and
prints the SQL, so the question costs the credential holder one paste rather
than a reading of this file.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

KEEP = ("index", "distill", "deep_read")

PRESENT_KEPT, PRESENT_DISCARDED, PRESENT_UNTRIAGED, ABSENT, UNKNOWN = 0, 1, 2, 3, 4

# The one place the two id shapes are reconciled. `like` with a literal prefix
# uses the primary key's btree index, where a function on the left of the
# comparison would not, and the `v` is literal so it cannot match a different
# paper: arXiv's numeric ids carry no `v`.
PAPERS_SQL = """
select id, source, tier, title, url, published_at, fetched_at, distilled_at
from papers
where id = %(base)s or id like %(versioned)s
order by id
"""

TRIAGE_SQL = """
select paper_id, decision, score, model, prompt_sha, created_at,
       human_verdict, human_note
from triage_log
where paper_id = %(base)s or paper_id like %(versioned)s
order by created_at, id
"""

ARXIV_ID = re.compile(r"^(?:arxiv:)?(?P<num>[0-9]{4}\.[0-9]{4,5})(?:v[0-9]+)?$", re.I)


def base_id(value: str) -> str:
    """Any shape of an arXiv reference, as the version-stripped `papers.id`.

    `2610.07639`, `arxiv:2610.07639v2`, `https://arxiv.org/abs/2610.07639v1` and
    `arXiv:2610.07639` all return `arxiv:2610.07639`. Anything this does not
    recognise comes back stripped and otherwise untouched, because `papers.id`
    is also a url hash for a blog post and those are not ours to rewrite.
    """
    text = (value or "").strip()
    text = text.rsplit("/", 1)[-1] if "/" in text else text
    match = ARXIV_ID.match(text)
    return f"arxiv:{match.group('num')}" if match else text


def params(value: str) -> dict:
    base = base_id(value)
    return {"base": base, "versioned": f"{base}v%"}


def connect():
    """A connection, or the reason there is not one. Never both."""
    for name in ("NEON_RO_URL", "DATABASE_URL"):
        url = os.environ.get(name, "").strip()
        if url:
            break
    else:
        return None, ("neither NEON_RO_URL nor DATABASE_URL is in this "
                      "environment, so the corpus cannot be read from here")
    try:
        import psycopg
    except ImportError:
        return None, "psycopg is not installed here (pip install 'psycopg[binary]')"
    try:
        return psycopg.connect(url, connect_timeout=15), None
    except Exception as exc:              # noqa: BLE001 - the reason is the answer
        return None, f"{name} is set but the connection failed: {exc}"


def verdict(papers: list[tuple], decisions: list[tuple]) -> tuple[int, str]:
    """The state, and the sentence that says which repair it asks for."""
    if not papers:
        return ABSENT, (
            "ABSENT: no row under any shape of this id, so the paper was never "
            "fetched. The repair is an intake: `python3 pipeline/reading_queue.py "
            "--add <id> --why ...` needs no credential and reaches the next "
            "deploy of distill, and `modal run pipeline/ingest.py --ids <id>` is "
            "the hand route for whoever holds a Modal credential."
        )
    if not decisions:
        return PRESENT_UNTRIAGED, (
            "PRESENT, NEVER JUDGED: the paper has a row and `triage_log` has "
            "none for it, so it is waiting on a triage run rather than on an "
            "intake. An intake would change nothing: the insert is `on conflict "
            "(id) do nothing`."
        )
    latest = decisions[-1][1]
    if latest == "discard":
        return PRESENT_DISCARDED, (
            "PRESENT AND DISCARDED: the paper was fetched and triage threw it "
            "away, so the repair is the judgement and not the intake. The row "
            "below carries the model and the prompt sha that decided it, and "
            "`triage_log.human_verdict = 'overturn'` is the label this table "
            "exists to collect."
        )
    return PRESENT_KEPT, (
        f"PRESENT AND KEPT: the latest decision is `{latest}`, so nothing here "
        "is a reach gap or a triage defect. If no claim cites it, the question "
        "is distill's and `papers.distilled_at` below is where that starts."
    )


def report(value: str, papers: list[tuple], decisions: list[tuple], out=print) -> int:
    base = base_id(value)
    code, sentence = verdict(papers, decisions)
    out(f"## {value}  ->  {base}")
    out("")
    out(sentence)
    out("")
    if len(papers) > 1:
        out(f"!! {len(papers)} rows carry this paper, which is the duplicate "
            "shape INC-2026-10-05 measured at 322 papers and 656 rows. Every "
            "row is printed below, and a claim written against one of them does "
            "not attach to the other.")
        out("")
    for pid, source, tier, title, url, published, fetched, distilled in papers:
        out(f"papers  {pid}")
        out(f"        title       {title}")
        out(f"        source      {source}   tier {tier}")
        out(f"        url         {url}")
        out(f"        published   {published}   fetched {fetched}")
        out(f"        distilled   {distilled if distilled else 'never'}")
    if papers:
        out("")
    for pid, decision, score, model, sha, created, human, note in decisions:
        out(f"triage  {created}  {decision}  score {score}")
        out(f"        on          {pid}")
        out(f"        by          {model}  prompt {sha}")
        if human:
            out(f"        human       {human}: {note}")
    if papers and not decisions:
        out("triage  no row")
    return code


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Is this paper absent from the corpus, or present and discarded?")
    ap.add_argument("ids", nargs="*", help="arXiv ids, in any shape")
    ap.add_argument("--sql", action="store_true",
                    help="print the two queries with this id bound, and run nothing")
    args = ap.parse_args(argv)

    if not args.ids:
        ap.error("name at least one paper id")

    if args.sql:
        for value in args.ids:
            bound = params(value)
            print(f"-- {value} -> {bound['base']}")
            for sql in (PAPERS_SQL, TRIAGE_SQL):
                rendered = sql.strip()
                for key, val in bound.items():
                    rendered = rendered.replace(f"%({key})s", f"'{val}'")
                print(rendered + ";")
            print()
        return 0

    conn, why = connect()
    if conn is None:
        print(f"cannot answer: {why}")
        print("")
        print("The two states this would separate need opposite repairs, so "
              "guessing between them is worse than waiting. `--sql` prints the "
              "query for whoever holds the credential:")
        print("")
        print(f"    python3 tools/corpus_row.py {' '.join(args.ids)} --sql")
        return UNKNOWN

    worst = PRESENT_KEPT
    try:
        with conn:
            for n, value in enumerate(args.ids):
                if n:
                    print("")
                bound = params(value)
                papers = conn.execute(PAPERS_SQL, bound).fetchall()
                decisions = conn.execute(TRIAGE_SQL, bound).fetchall()
                code = report(value, papers, decisions)
                worst = max(worst, code)
    finally:
        conn.close()
    return worst


if __name__ == "__main__":
    sys.exit(main())
