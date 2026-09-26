"""One-time grading backfill: the 693 claims that have no evidence grade.

    modal run pipeline/backfill_grades.py::count      # the dry run. Writes nothing.
    modal run pipeline/backfill_grades.py::backfill   # then, and only then, write

The owner's count from Neon, 2026-09-25: 746 claims, 693 with a NULL
`evidence_grade`, every one of them distilled before 2026-09-24 11:30Z when the
column started being written. A digest that ranks by evidence grade over a
column that is NULL on 93% of its rows is ranking by nothing, and the
`claims_evidence_grade_idx` index built for that ranking is serving one value.

## What this job is, and what it deliberately is not

It calls no model. Not one. `pipeline/evidence.py` is pure rules over two
inputs, the paper id and the evidence text, so the whole backfill is a SELECT
and an UPDATE and it costs $0 against any provider. That is worth stating
plainly because the rest of today's work is about moving jobs onto a paid
account, and this piece of it is free.

It is also not as good as grading at distill time. The live grader needs the
model's own `measured` boolean to agree with the text; this one has only the
text, because the boolean was never stored. `evidence.backfill_grade` is the
weaker test and its docstring says which direction it errs in. A backfilled
grade can be one step stronger than a fresh one, never weaker.

## Idempotent and resumable, by construction rather than by bookkeeping

Both properties come from one clause: `where evidence_grade is null`. Every
pass reads only ungraded rows and writes a grade to each, so a second pass over
a finished table finds nothing to do and a pass that dies halfway leaves the
rows it already wrote alone. There is no cursor to store, no state table, and
nothing to reset. A run interrupted by a timeout is resumed by running it again.

The grader is deterministic, which is what makes that safe: the same row graded
twice gets the same answer, so even a row somehow visited twice cannot flip.

## The order

Newest claims first. The digest reads the last seven days, so the rows that
change what a reader sees this week are graded in the first batch, and the
2026-06 tail is graded whenever the job gets to it.
"""

import pathlib

import modal

# Rows per transaction. Large enough that 693 rows is one or two commits, small
# enough that a killed run loses at most this many rows of progress. The work per
# row is a regex over a few hundred characters, so the batch size is about
# transaction granularity and not about throughput.
BATCH = 200

image = (
    modal.Image.debian_slim()
    .pip_install("psycopg[binary]==3.2.4")
    .add_local_file("pipeline/evidence.py", "/root/evidence.py")
)

app = modal.App("alexandria-backfill-grades", image=image)


def evidence():
    """pipeline/evidence.py, wherever this is running from.

    The same two-path trick distill.py uses, for the same reason: the rules the
    tests check are the rules this backfill applies. A backfill with its own copy
    of the grading rules would write a column the live grader disagrees with.
    """
    import sys

    here = str(pathlib.Path(__file__).resolve().parent)
    for path in ("/root", here):
        if path not in sys.path:
            sys.path.insert(0, path)
    import evidence as module

    return module


# Newest first, so the rows the digest reads this week are graded in the first
# batch. The join is to `papers` for `source`, which is the grader's fallback
# signal when the paper id is not an arXiv id.
UNGRADED_SQL = """
    select c.id, c.paper_id, c.evidence, p.source
    from claims c
    join papers p on p.id = c.paper_id
    where c.evidence_grade is null
    order by c.id desc
"""


def ungraded(conn, limit: int | None = None) -> list[tuple]:
    """Ungraded claims, newest first. `limit` of None means all of them."""
    if limit is None:
        return conn.execute(UNGRADED_SQL).fetchall()
    return conn.execute(UNGRADED_SQL + " limit %s", (limit,)).fetchall()


def tally(rows: list[tuple], grader) -> dict[str, int]:
    """What these rows would be graded, without writing anything."""
    counts: dict[str, int] = {}
    for _, paper_id, evidence_text, source in rows:
        g = grader.backfill_grade(paper_id, evidence_text, source)
        counts[g] = counts.get(g, 0) + 1
    return counts


def report(counts: dict[str, int], total: int) -> str:
    """The tally in grade order, strongest first, with percentages."""
    grader = evidence()
    lines: list[str] = []
    for g in grader.GRADES:
        n = counts.get(g, 0)
        share = (100 * n / total) if total else 0
        lines.append(f"  {g:<15} {n:>5}  {share:5.1f}%")
    return "\n".join(lines)


@app.function(
    secrets=[modal.Secret.from_name("neon")],
    timeout=900,
)
def count() -> str:
    """The dry run. How many rows, what they would be graded, nothing written.

        modal run pipeline/backfill_grades.py::count

    Run this first. It is the whole of the backfill except the UPDATE, so if the
    tally looks wrong the rules are wrong and no rows were touched finding out.
    """
    import os

    import psycopg

    grader = evidence()
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        total, ungraded, no_evidence = conn.execute(
            """
            select count(*),
                   count(*) filter (where evidence_grade is null),
                   count(*) filter (where evidence_grade is null
                                      and coalesce(evidence, '') = '')
            from claims
            """
        ).fetchone()
        existing = dict(conn.execute(
            """
            select evidence_grade, count(*) from claims
            where evidence_grade is not null group by 1
            """
        ).fetchall())
        # Every ungraded row, not a page of them: the dry run's job is to tally
        # the whole backfill, and 693 rows of a few hundred characters is
        # nothing to hold in memory.
        rows = ungraded(conn)

    would = tally(rows, grader)
    print(f"claims: {total} total, {ungraded} ungraded ({100 * ungraded / total:.1f}%)")
    print(f"already graded, by grade ({sum(existing.values())} rows):")
    print(report(existing, sum(existing.values()) or 1))
    print(f"the backfill would write ({len(rows)} rows):")
    print(report(would, len(rows) or 1))
    print(f"{no_evidence} of the ungraded rows have no evidence text at all, so "
          "they grade on source class alone: a paper becomes 'asserted' and a "
          "field report becomes 'anecdote'. That is the correct answer for a "
          "claim with nothing behind it.")
    if ungraded != len(rows):
        print(f"NOTE: {ungraded - len(rows)} ungraded claims did not join to a "
              "papers row and would be skipped. claims.paper_id is a foreign "
              "key, so this should be zero; if it is not, the join is the bug.")
    return (f"dry run: {len(rows)} rows would be graded, "
            + ", ".join(f"{g} {n}" for g, n in sorted(would.items()))
            + ". Nothing was written.")


@app.function(
    secrets=[modal.Secret.from_name("neon")],
    timeout=1800,
)
def backfill(max_rows: int = 0) -> str:
    """Write the grades. Idempotent and resumable; see the module docstring.

        modal run pipeline/backfill_grades.py::backfill

    `max_rows` of 0 means every ungraded row. Pass a small number to write one
    batch and look at it before committing to the rest.
    """
    import os

    import psycopg

    grader = evidence()
    written: dict[str, int] = {}
    skipped = 0
    batches = 0

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        if conn.execute(
            """
            select 1 from information_schema.columns
            where table_name = 'claims' and column_name = 'evidence_grade'
            """
        ).fetchone() is None:
            raise RuntimeError(
                "claims.evidence_grade does not exist in this database, so "
                "there is nothing to backfill into. It is in db/schema.sql:\n"
                "    modal run pipeline/db_setup.py::apply_schema\n"
                "Nothing was written.")

        while True:
            take = BATCH if not max_rows else min(BATCH, max_rows - sum(written.values()) - skipped)
            if take <= 0:
                break
            rows = ungraded(conn, take)
            if not rows:
                break
            for claim_id, paper_id, evidence_text, source in rows:
                g = grader.backfill_grade(paper_id, evidence_text, source)
                # The `is null` in the WHERE is the idempotence, repeated at the
                # row level: if a concurrent distill graded this row between the
                # SELECT and here, that run's grade is the better one and this
                # UPDATE correctly does nothing.
                if conn.execute(
                    "update claims set evidence_grade = %s "
                    "where id = %s and evidence_grade is null",
                    (g, claim_id),
                ).rowcount:
                    written[g] = written.get(g, 0) + 1
                else:
                    skipped += 1
            conn.commit()
            batches += 1
            done = sum(written.values())
            remaining = conn.execute(
                "select count(*) from claims where evidence_grade is null"
            ).fetchone()[0]
            print(f"batch {batches}: {done} graded so far, {remaining} still null")

        total_graded = sum(written.values())
        print(f"backfilled {total_graded} claims in {batches} batches:")
        print(report(written, total_graded or 1))
        if skipped:
            print(f"{skipped} rows were already graded by the time this reached "
                  "them and were left alone, which is the idempotence working")
        remaining = conn.execute(
            "select count(*) from claims where evidence_grade is null"
        ).fetchone()[0]
        print(f"{remaining} claims still have no grade. Run this again to "
              "continue; it resumes by itself." if remaining
              else "no claim in the corpus is ungraded.")
    return f"backfilled {total_graded} claims, {remaining} still null"


@app.local_entrypoint()
def main():
    print(count.remote())
