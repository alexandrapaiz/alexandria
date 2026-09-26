"""The invisible claims: tags that are a real topic misspelled, repaired in place.

    modal run pipeline/backfill_topics.py::count      # the dry run. Writes nothing.
    modal run pipeline/backfill_topics.py::backfill   # then, and only then, write

The research seat's census of 2026-09-26 found 18 claims tagged with a
non-breaking-hyphen twin of a real topic: `post‑training` (11),
`harness‑engineering` (4), `loop‑engineering` (2), `context‑engineering` (1).
Those claims are invisible to every query the product runs, because the digest,
the graph page and the skill agent all filter with the correct spelling. The
claims are good, the tag is a typo, and the fix costs nothing.

`pipeline/distill.py` now folds tags through `pipeline/topics.py` before the
insert, so no new claim can arrive this way. This job is the history.

## What it repairs, and what it refuses to touch

It repairs a tag **only** when the fold lands it on the closed list. `post‑training`
becomes `post-training`. `Multi Agent` becomes `multi-agent`.

It leaves a tag that folds to nothing on the list exactly where it is, and
prints it. The same census found 22 invented tags, `training` (8), `analysis`
(5), `safety` (3), `reward-design` (2) and a tail. Deleting those would be this
job making a taxonomy decision, and the taxonomy belongs to `prompts/distill.md`
and therefore to the research seat under ADR-12's whitelist. So the dry run
prints them as a proposal for that seat, and the write pass moves none of them.
A repair that only ever repairs is a repair nobody has to review twice.

## Idempotent, resumable, and free

It calls no model and is given no provider secret, so it cannot acquire a cost
by a later edit. The fold is a pure function and a folded tag folds to itself,
so the second pass over a repaired row finds nothing to change: there is no
cursor, no state table and nothing to reset, and a run killed halfway is resumed
by running it again.
"""

import pathlib

import modal

# Rows per transaction. The whole table is under a thousand claims today, so this
# is about how much progress a killed run loses, not about throughput.
BATCH = 200

image = (
    modal.Image.debian_slim()
    .pip_install("psycopg[binary]==3.2.4")
    .add_local_file("pipeline/topics.py", "/root/topics.py")
)

app = modal.App("alexandria-backfill-topics", image=image)


def topics():
    """pipeline/topics.py, wherever this is running from.

    The same two-path trick distill.py uses, for the same reason: a backfill with
    its own copy of the fold would write spellings the live insert disagrees with.
    """
    import sys

    here = str(pathlib.Path(__file__).resolve().parent)
    for path in ("/root", here):
        if path not in sys.path:
            sys.path.insert(0, path)
    import topics as module

    return module


def repair(tags, taxonomy) -> tuple[list[str], list[str]]:
    """(repaired tags, tags left alone) for one row.

    Order is preserved and duplicates are collapsed, because a fold can make two
    different spellings into one tag and `{post-training, post-training}` is not
    what anybody meant.
    """
    out: list[str] = []
    untouched: list[str] = []
    for raw in tags or []:
        folded = taxonomy.ALIASES.get(taxonomy.fold(raw), taxonomy.fold(raw))
        keep = folded if folded in taxonomy.TOPICS else raw
        if keep not in taxonomy.TOPICS:
            untouched.append(raw)
        if keep not in out:
            out.append(keep)
    return out, untouched


def survey(conn, taxonomy) -> tuple[list[tuple], dict[str, int]]:
    """Every row whose tags would change, plus the tally of what stays off-list."""
    rows = conn.execute(
        "select id, topics from claims where topics is not null "
        "and array_length(topics, 1) > 0 order by id"
    ).fetchall()
    changing: list[tuple] = []
    off_list: dict[str, int] = {}
    for claim_id, tags in rows:
        fixed, untouched = repair(tags, taxonomy)
        for tag in untouched:
            off_list[tag] = off_list.get(tag, 0) + 1
        if fixed != list(tags):
            changing.append((claim_id, list(tags), fixed))
    return changing, off_list


def report(changing: list[tuple], off_list: dict[str, int]) -> list[str]:
    lines = [f"{len(changing)} claims carry a tag that is a real topic misspelled"]
    moves: dict[str, int] = {}
    for _, before, after in changing:
        for tag in before:
            if tag not in after:
                moves[tag] = moves.get(tag, 0) + 1
    for tag, n in sorted(moves.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"  {tag!r} x{n} -> folds onto the list")
    if off_list:
        lines.append(f"{sum(off_list.values())} tag applications stay off-list "
                     "and are left exactly as they are:")
        for tag, n in sorted(off_list.items(), key=lambda kv: (-kv[1], kv[0]))[:12]:
            lines.append(f"  {tag!r} x{n}")
        lines.append("  each of those is a proposal for prompts/distill.md, "
                     "which is the research seat's file")
    return lines


@app.function(secrets=[modal.Secret.from_name("neon")], timeout=600)
def count() -> str:
    """The dry run. Reads the table, writes nothing, prints what would change."""
    import os

    import psycopg

    taxonomy = topics()
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        changing, off_list = survey(conn, taxonomy)
    lines = report(changing, off_list)
    print("\n".join(lines))
    for claim_id, before, after in changing[:10]:
        print(f"  claim {claim_id}: {before} -> {after}")
    print("wrote nothing")
    return lines[0]


@app.function(secrets=[modal.Secret.from_name("neon")], timeout=1800)
def backfill() -> str:
    """Write the repairs. Run `count` first."""
    import os

    import psycopg

    taxonomy = topics()
    written = 0
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        changing, off_list = survey(conn, taxonomy)
        print("\n".join(report(changing, off_list)))
        for start in range(0, len(changing), BATCH):
            for claim_id, _, after in changing[start:start + BATCH]:
                conn.execute("update claims set topics = %s where id = %s",
                             (after, claim_id))
                written += 1
            conn.commit()
            print(f"  repaired {written} of {len(changing)}")
    return f"repaired {written} claims; {sum(off_list.values())} tags left off-list"
