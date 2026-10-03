#!/usr/bin/env python3
"""ADR-13's adversary: does the claim graph disagree with what this skill says.

    python3 tools/panel_adversary.py                    # review every skill
    python3 tools/panel_adversary.py --skill harness-engineering
    python3 tools/panel_adversary.py --record           # DATABASE_URL: file the verdicts
    python3 tools/panel_adversary.py --json

ADR-13 gives this reviewer one sentence and it is the whole specification:
*"Searches the claim graph for contradicting or refining claims the draft
ignored. If the graph disagrees with the skill, the PR fails."* This is the
second of the panel's three reviewers. `tools/panel_provenance.py` is the
first, and the two share only the verdict vocabulary in `tools/panel.py`.

## Why this reviewer has no half that runs in CI, and the provenance one does

The provenance reviewer splits: most of what it decides is in the SKILL.md, so
`--files-only` runs on every pull request. Nothing this reviewer decides is in
the file. A skill cannot tell you whether the graph disagrees with it, by
construction, because the disagreement is a row somebody else wrote after the
skill was merged. So there is no `--files-only` here and no step in
`checks.yml`, and offering an empty one would be worse than offering none: a
green CI step named "the adversary" would read as the graph agreeing, when all
it could mean is that nobody asked the graph.

It therefore runs in exactly one place, `pipeline/skill_revision.py`, the daily
job that already holds the `neon` secret and already reads every skill off
`main`. Run from a seat sandbox with no credential, it files `unknown` on
everything and says that is what happened.

## What it decides, and the direction that makes it decidable

ADR-10 fixes the direction of every edge: `from_claim` is always the newer,
judging claim. So "a contradicting claim the draft ignored" is a precise query
and not a judgment call. For each claim id the skill cites, read the
`contradicts` edges that point *at* it, and ask whether the newer claim on the
other end is in the skill's own citation list.

- **It is not cited: the draft ignored it.** The graph disagrees and the skill
  does not know. `fail`, which is ADR-13's own second sentence.
- **It is cited.** The skill cites both sides of a contradiction and the format
  cannot say whether it discusses the disagreement or asserts both as settled.
  `unknown`, for the same reason the provenance reviewer's duty 2 is unknown,
  and it is the same format change that would fix both.

`refines` edges get the same treatment with a different meaning. A refinement
is not a disagreement: it is newer evidence that narrows a claim the skill
teaches as stated, so a skill that cites both is coherent and a skill that
ignored one is out of date. ADR-13 puts refining claims in this reviewer's
search for that reason, so an ignored refinement is a `fail` by default and
`SEVERITY` below is the one line to change if the owner would rather it were a
warning.

## The threshold, which is not this reviewer's to pick

`deprecated_claims` in `db/schema.sql` already defines what the organization
means by a contradicted claim, and the number is `confidence >= 0.7`.
`skills_needing_revision` is that view joined against what skills cite, and it
is what queues a revision in `pipeline/skill_revision.py`. A reviewer that drew
the line anywhere else would give the panel and the revision queue two
different answers to one question, so this file reads the same 0.7 and reports
weaker contradictions as evidence rather than as defects.

## The check that matters most, and it is an `unknown`

A cited claim with `interpreted_at` null has never been judged against its
neighbours, so it has no edges, so this reviewer finds nothing and would
otherwise report a clean pass. That is the most dangerous output this file
could produce: a pass that means the graph was never asked, dressed as a pass
that means the graph agrees. Those claims are reported `unknown` by id, which
blocks the merge the way ADR-13 intends. The claim graph has stalled twice in
this product's short life (incident 24, and the 2026-09-24 curation brief that
found it frozen since 2026-09-12), so this is a live condition and not a
hypothetical.

## Two checks that are not ADR-13 duties

Labelled `evidence-breadth` and `evidence-grade` so nobody counts them as
duties, the same way the provenance reviewer labels `spec-conformance`.

`duplicates` edges between two claims a skill cites mean its citation list is
wider than its evidence: twelve ids over nine distinct findings is nine
findings. The provenance reviewer catches a literally repeated id and cannot
see this one, because the duplication is in the corpus rather than in the file.

`claims.evidence_grade` says what kind of support a claim has, and a skill
built on `asserted` and `anecdote` rows is teaching something the corpus never
measured. Both are recorded as evidence and neither changes a verdict, because
no decision in any register sets a bar for either, and inventing one here would
be this reviewer legislating.

## The three states

    exit 0    the graph agrees, everywhere it was asked
    exit 1    a fail: the graph disagrees with a skill
    exit 2    nothing disagreed, and something could not be asked
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# `/root` inside the Modal image that pipeline/skill_revision.py builds, and
# `tools/` when a person runs this from the repository. The same two lines
# panel_provenance.py carries, for the same reason.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import panel                        # noqa: E402
import skill_registrar as registrar  # noqa: E402

Finding = panel.Finding
verdict_of = panel.verdict_of
render = panel.render

REVIEWER = "adversary"

# db/schema.sql's own number, in `deprecated_claims`. See the docstring: this
# reviewer reads the organization's threshold rather than choosing one.
CONTRADICTION_CONFIDENCE = 0.7

# What an ignored edge of each kind costs a skill. ADR-13's sentence makes a
# contradiction a fail; the refinement line is argued in the docstring and this
# is the single place to soften it.
SEVERITY = {
    "contradicts": "fail",
    "refines": "fail",
}

# The grades claims.evidence_grade admits, weakest last. Recorded, never graded.
WEAK_GRADES = ("asserted", "anecdote")


# -------------------------------------------------------------------- the SQL
# Every statement this file sends, in one place, so tests can parse them with
# libpg_query and resolve every relation and column against db/schema.sql. No
# CI job here can execute them, which is exactly why they are checked that way.

QUERIES = {
    "cited": """
        select c.id, c.interpreted_at, c.evidence_grade
        from claims c
        where c.id = any(%s)
    """,
    # Edges that point AT a cited claim. ADR-10 makes from_claim the newer,
    # judging claim, so this direction is the one that finds what came after
    # the skill's evidence. `supports` is deliberately not in the list: a
    # supporting claim the draft did not cite is not a disagreement, and
    # reporting it would turn this reviewer into a completeness checker.
    "disagreements": """
        select l.to_claim, l.from_claim, l.relation, l.confidence,
               f.claim, f.paper_id, f.created_at
        from claim_links l
        join claims f on f.id = l.from_claim
        where l.to_claim = any(%s)
          and l.relation in ('contradicts', 'refines', 'duplicates')
        order by l.to_claim, l.relation, l.confidence desc nulls last
    """,
    "file": """
        insert into panel_verdicts
            (target, reviewer, verdict, findings, target_sha, reviewer_sha, model)
        values (%s, 'adversary', %s, %s, %s, %s, null)
        returning id
    """,
}


def connect(writable: bool):
    return panel.connect(writable, cannot=(
        "the claim graph was never searched and no skill's evidence was "
        "checked against what the corpus learned after it"))


def cited_claims(conn, claim_ids: list[int]) -> dict[int, dict]:
    """{claim id: {interpreted_at, evidence_grade}} for the ids that exist."""
    if not claim_ids:
        return {}
    rows = conn.execute(QUERIES["cited"], (list(claim_ids),)).fetchall()
    return {int(cid): {"interpreted_at": seen, "evidence_grade": grade}
            for cid, seen, grade in rows}


def disagreements(conn, claim_ids: list[int]) -> list[dict]:
    """Every contradicts/refines/duplicates edge pointing at a cited claim."""
    if not claim_ids:
        return []
    out = []
    for row in conn.execute(QUERIES["disagreements"], (list(claim_ids),)).fetchall():
        to_claim, from_claim, relation, confidence, claim, paper_id, created_at = row
        out.append({"to_claim": int(to_claim), "from_claim": int(from_claim),
                    "relation": relation, "confidence": confidence,
                    "claim": claim, "paper_id": paper_id,
                    "created_at": created_at})
    return out


# ------------------------------------------------------------- the judgments
# Pure functions of (what the skill cites, what the corpus says about it). No
# connection reaches past this line, which is what lets every duty below be
# exercised against a written-out graph rather than against production.

def quote(edge: dict, limit: int = 110) -> str:
    """The contradicting claim's own words, short enough to read in a log line.

    A finding that says only "claim 412 contradicts claim 207" sends a reader
    to the database. A finding that says what 412 found does not.
    """
    text = " ".join((edge.get("claim") or "").split())
    if len(text) > limit:
        text = text[:limit - 1].rstrip() + "…"
    paper = edge.get("paper_id") or "an unnamed paper"
    return f"claim {edge['from_claim']} ({paper}): {text!r}"


def searchable(row, cited: dict[int, dict]) -> list[Finding]:
    """Could the graph answer at all, for each id this skill cites.

    Two ways it cannot, and they are different. An id with no row in `claims`
    has no node to search around, and that defect is the provenance reviewer's
    duty 1 rather than this reviewer's finding. An id whose `interpreted_at` is
    null has a node and no edges, because nothing has ever judged it against
    its neighbours, and a clean report over one of those means the graph was
    never asked.
    """
    findings: list[Finding] = []
    absent = sorted(c for c in row.claim_ids if c not in cited)
    if absent:
        findings.append(Finding(
            "graph-searchable", "unknown",
            f"cites {len(absent)} ids with no row in claims, so the graph has "
            f"no node to search around them: {absent}. The defect itself is "
            "the provenance reviewer's duty 1; this reviewer only reports that "
            "it could not search."))

    uninterpreted = sorted(c for c in row.claim_ids
                           if c in cited and not cited[c]["interpreted_at"])
    if uninterpreted:
        findings.append(Finding(
            "graph-searchable", "unknown",
            f"{len(uninterpreted)} of {len(row.claim_ids)} cited claims have "
            f"interpreted_at null, so nothing has ever judged them against "
            f"their neighbours: {uninterpreted}. They have no edges because "
            "nobody looked, and a clean adversary report over them would mean "
            "the graph was never asked rather than that the graph agrees."))

    judged = len(row.claim_ids) - len(absent) - len(uninterpreted)
    findings.append(Finding(
        "graph-searchable", "note",
        f"{judged} of {len(row.claim_ids)} cited claims have been judged "
        "against their neighbours, so the search below covers those"))
    return findings


def contradicted(row, edges: list[dict]) -> list[Finding]:
    """ADR-13's sentence: contradicting claims the draft ignored."""
    findings: list[Finding] = []
    cites = set(row.claim_ids)
    hits = [e for e in edges if e["relation"] == "contradicts"]
    firm = [e for e in hits if (e["confidence"] or 0) >= CONTRADICTION_CONFIDENCE]
    weak = [e for e in hits if (e["confidence"] or 0) < CONTRADICTION_CONFIDENCE]

    ignored = [e for e in firm if e["from_claim"] not in cites]
    for edge in ignored:
        findings.append(Finding(
            "contradiction-ignored", SEVERITY["contradicts"],
            f"cites claim {edge['to_claim']}, which {quote(edge)} contradicts "
            f"at confidence {edge['confidence']}. The skill does not cite the "
            "contradicting claim, so the graph disagrees with this skill and "
            "the skill does not know."))

    both = [e for e in firm if e["from_claim"] in cites]
    for edge in both:
        findings.append(Finding(
            "contradiction-both-cited", "unknown",
            f"cites both claim {edge['to_claim']} and {quote(edge)}, which "
            f"contradict each other at confidence {edge['confidence']}. "
            "Whether the skill discusses that disagreement or presents both as "
            "settled is not decidable from a flat citation list, which is the "
            "same format gap the provenance reviewer's duty 2 waits on."))

    if weak:
        findings.append(Finding(
            "contradiction-ignored", "note",
            f"{len(weak)} contradicting edges fall under the "
            f"{CONTRADICTION_CONFIDENCE} confidence deprecated_claims draws "
            f"its own line at, so they are evidence here rather than defects: "
            f"{[(e['from_claim'], e['confidence']) for e in weak]}"))
    if not hits:
        findings.append(Finding(
            "contradiction-ignored", "note",
            "no contradicting edge points at anything this skill cites"))
    return findings


def refined(row, edges: list[dict]) -> list[Finding]:
    """Newer evidence that narrows a claim the skill teaches as stated."""
    findings: list[Finding] = []
    cites = set(row.claim_ids)
    hits = [e for e in edges if e["relation"] == "refines"]

    for edge in [e for e in hits if e["from_claim"] not in cites]:
        findings.append(Finding(
            "refinement-ignored", SEVERITY["refines"],
            f"cites claim {edge['to_claim']}, which {quote(edge)} refines. The "
            "skill teaches the broader claim and does not cite the narrower "
            "one, so what it says is out of date rather than wrong."))

    acknowledged = [e for e in hits if e["from_claim"] in cites]
    if acknowledged:
        findings.append(Finding(
            "refinement-ignored", "note",
            f"{len(acknowledged)} refinements of cited claims are themselves "
            f"cited: {[(e['to_claim'], e['from_claim']) for e in acknowledged]}"))
    if not hits:
        findings.append(Finding(
            "refinement-ignored", "note",
            "no refining edge points at anything this skill cites"))
    return findings


def breadth(row, edges: list[dict]) -> list[Finding]:
    """How many distinct findings the citation list actually represents.

    Not an ADR-13 duty. A `duplicates` edge between two claims a skill cites
    means its list is wider than its evidence, and the provenance reviewer
    cannot see it: the duplication is in the corpus, not in the file.
    """
    cites = set(row.claim_ids)
    pairs = sorted({tuple(sorted((e["to_claim"], e["from_claim"])))
                    for e in edges
                    if e["relation"] == "duplicates" and e["from_claim"] in cites})
    if not pairs:
        return [Finding("evidence-breadth", "note",
                        f"{len(cites)} distinct claim ids, none of them "
                        "duplicates of each other in the graph")]
    merged = len({b for _, b in pairs})
    return [Finding(
        "evidence-breadth", "note",
        f"{len(cites)} cited ids cover about {len(cites) - merged} distinct "
        f"findings: the graph calls these pairs duplicates of each other, "
        f"{pairs}")]


def grades(row, cited: dict[int, dict]) -> list[Finding]:
    """What kind of support the cited claims have. Not an ADR-13 duty either."""
    counts: dict[str, int] = {}
    for claim_id in row.claim_ids:
        grade = (cited.get(claim_id) or {}).get("evidence_grade") or "ungraded"
        counts[grade] = counts.get(grade, 0) + 1
    shape = ", ".join(f"{n} {name}" for name, n in sorted(counts.items()))
    weak = sum(counts.get(g, 0) for g in WEAK_GRADES)
    tail = (f"; {weak} of them carry no measurement behind them"
            if weak else "")
    return [Finding("evidence-grade", "note",
                    f"evidence behind the cited claims: {shape}{tail}")]


# ------------------------------------------------------------------- the pass

def reviewer_sha() -> str | None:
    """The git blob sha of this file, so a verdict says which reviewer judged."""
    return panel.reviewer_sha("tools/panel_adversary.py")


def review(skills_dir: pathlib.Path | None = None, conn=None,
           only: str | None = None, rows=None,
           problems: list[str] | None = None) -> list[dict]:
    """One verdict per skill, as the dicts a `panel_verdicts` row is built from.

    `rows` is passed in by the daily job, which reads every skill from `main`
    over the GitHub API rather than from its own image, because the image is as
    old as the last deploy and reviewing a skill the image cannot see is the
    merged-but-inert failure this sprint exists to close.

    `problems` is accepted and not read. The registrar's problems are defects
    in a SKILL.md and the provenance reviewer already files them; a second
    reviewer repeating them would make one defect look like two independent
    findings, which is exactly what ADR-13's independence is for.
    """
    if rows is None:
        rows, _ = registrar.read_skills(skills_dir)
    if only:
        rows = [r for r in rows if r.slug == only]

    out = []
    for row in rows:
        if conn is None:
            findings = [Finding(
                "graph-searchable", "unknown",
                f"{len(row.claim_ids)} cited claim ids were not searched in "
                "the claim graph, because this run holds no database "
                "credential. Nothing this reviewer decides is in the SKILL.md, "
                "so there is no reduced check it can run instead.")]
        else:
            cited = cited_claims(conn, row.claim_ids)
            edges = disagreements(conn, row.claim_ids)
            findings = searchable(row, cited)
            findings += contradicted(row, edges)
            findings += refined(row, edges)
            findings += breadth(row, edges)
            findings += grades(row, cited)
        out.append({
            "target": row.path,
            "reviewer": REVIEWER,
            "verdict": verdict_of(findings),
            "findings": [f.as_dict() for f in findings],
            "target_sha": row.sha,
        })
    return out


def file_verdicts(conn, verdicts: list[dict], sha: str | None = None) -> list[int]:
    return panel.file_verdicts(conn, QUERIES["file"], verdicts, sha)


# ---------------------------------------------------------------------- cli

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--record", action="store_true",
                    help="file each verdict as a panel_verdicts row")
    ap.add_argument("--skill", default="", help="one skill slug")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    conn = connect(writable=args.record)
    if conn is None and args.record:
        print("nothing was recorded.")
        return 2

    try:
        verdicts = review(conn=conn, only=args.skill or None)
        written = []
        if args.record and conn is not None:
            written = file_verdicts(conn, verdicts, reviewer_sha())
    finally:
        if conn is not None:
            conn.close()

    if args.json:
        print(json.dumps({"reviewer": REVIEWER, "verdicts": verdicts,
                          "recorded": written}, indent=2, default=str))
    else:
        print(render(verdicts))
        if written:
            print(f"filed {len(written)} verdict rows: {written}")

    if any(v["verdict"] == "fail" for v in verdicts):
        return 1
    if any(v["verdict"] == "unknown" for v in verdicts):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
