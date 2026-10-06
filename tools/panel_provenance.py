#!/usr/bin/env python3
"""ADR-13's provenance reviewer: does a skill's evidence hold up, line by line.

    python3 tools/panel_provenance.py                  # review every skill
    python3 tools/panel_provenance.py --files-only      # the CI half: no database
    python3 tools/panel_provenance.py --skill harness-engineering
    python3 tools/panel_provenance.py --record          # DATABASE_URL: file the verdicts
    python3 tools/panel_provenance.py --json            # any of the above, for a script

ADR-13 (2026-09-17) replaced the human merge gate with a panel of three
independent reviewer agents and said the audit trail replaces the approval
queue, because the evidence gets recorded rather than queued on a person. The
panel has never existed. `skills/README.md` says so in its own words: four
skills drafted, "none yet passed by the ADR-13 panel", so every
`provenance.validated` field except one is empty. This file is the first of the
three reviewers, and it is read-only: it files verdicts and merges nothing.

## What this reviewer is asked to decide

ADR-13 gives the provenance reviewer three duties.

1. Every claim id the skill cites must exist.
2. The cited claim must actually support the sentence citing it.
3. Practical judgment not backed by a claim must be marked as ours, not the
   paper's.

Duty 1 is a query, and it had never been run: the six skills on main cite 101
claim ids between them and nothing in this repository has ever asked Postgres
whether those rows are there. Duty 3 is a convention the library already keeps
by hand, so it is checked here as a convention: the marker's wording has to be
one the library's own vocabulary recognises, or a reader grepping for an
unsourced recommendation will not find it.

One check here is not one of the three duties, and it is labelled
`spec-conformance` so nobody mistakes it for one. The published Agent Skills
specification caps `description` at 1024 characters and `name` at 64, and a
file past either is rejected by a client that validates it rather than loaded
with a long description. This reviewer is the only thing in the repository that
opens every SKILL.md on every pull request, so the two numbers are checked here
rather than in a seventh parser.

**Duty 2 cannot be decided today, and this reviewer says so rather than
guessing.** A skill cites its claim ids once, as a flat list in the frontmatter,
for the whole document. No section, paragraph or sentence names the claim behind
it. So "the cited claim supports the sentence citing it" has no pair to judge:
twelve claim ids and six sections produce seventy-two possible pairs and the
file asserts nothing about any of them. A model asked to judge support against
the whole list would be grading its own guess at the mapping. The fix is a
format change that belongs to the skill seat and is filed in the ledger: a claim
id list per section, which ADR-38's per-section *Validation:* tag is already the
natural place for. Until then this reviewer reports duty 2 as `unknown` with the
section count, which is the honest verdict and also the argument for the change.

## The three states, and why a reviewer has them

    ok        measured, and nothing wrong
    failing   measured, and something is wrong
    unknown   not measurable from here

    exit 0    nothing wrong
    exit 1    a finding: a defect in a skill's provenance
    exit 2    nothing wrong, and something could not be measured

Same vocabulary as `tools/graph_audit.py`, `tools/skill_registrar.py` and
`tools/delivery_health.py`, for the same reason. A verdict row carries the same
three words, so `unknown` is a first-class verdict in `panel_verdicts` rather
than a pass with a caveat nobody reads. ADR-13 merges on unanimous pass, and an
`unknown` is not a pass, so a reviewer that cannot measure something blocks the
merge instead of waving it through.

## The two halves, and why the split is not a weakening

Duties 1 and the paper cross-check need Neon. This organization runs no database
in CI (`pending-workflow-changes` item 6: the engineer seat has no read-only URL
either), so the half CI can run is `--files-only`, which is every check that
lives in the file itself. The live half runs in `pipeline/skill_revision.py`,
the daily job that already holds the `neon` secret and already reads every
skill. Both halves write the same verdict shape, and a verdict filed by the
files-only half says which checks it could not run.

## What it needs

`--files-only` needs nothing but the repository. The live half needs
`NEON_RO_URL` or `DATABASE_URL` and `psycopg`. `--record` is the only mode that
writes, it writes one INSERT per skill into `panel_verdicts`, and it needs
`DATABASE_URL`. Nothing here merges a pull request, by design: that is ADR-13's
third slice and it waits on a PR-merge-scoped token the owner has to mint.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# This file's own directory, which is `tools/` in the repository and `/root`
# inside the Modal image that `pipeline/skill_revision.py` builds. One line
# covers both, because `tools/skill_registrar.py` is copied next to this file
# in the image and sits next to it in the checkout.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import panel                        # noqa: E402
import skill_registrar as registrar  # noqa: E402

REVIEWER = "provenance"

# The verdict vocabulary is the panel's, not this reviewer's: `panel_consensus`
# counts passes across all three, so the three severities and the arithmetic
# that turns findings into one verdict live in one file. These names stay bound
# here because this module's own checks read them on every line below, and
# because the three reviewers are independent in their context rather than in
# their grading scale (tools/panel.py says why at length).
Finding = panel.Finding
verdict_of = panel.verdict_of
render = panel.render

# The library's vocabulary for duty 3, normalised to one space. A phrasing
# outside it is a finding rather than a silent pass, because this phrase is the
# only thing separating a recommendation the papers support from one the library
# made up, and a reader (or the next reviewer) finds it by searching for these
# words.
#
# Two grammars, because the library writes in two. The attributive form is the
# parenthetical that follows the advice, and it was the only form in the six
# skills this check was written against. The predicative form arrived with
# ADR-38's *Validation:* tags, where the natural sentence puts the subject
# first: "the file-in-the-repository prescription is ours." Both say exactly
# the same thing, both are equally searchable, and the list stays closed: a
# fifth grammar is still a finding.
OURS_VOCABULARY = (
    "ours, not the paper's",
    "ours, not the papers'",
    "ours rather than the paper's",
    # "so ours: five repeat runs of the unchanged system", the colon form that
    # introduces the library's own prescription instead of naming its source.
    "ours:",
)

# Read backwards from the word instead of forwards. These are the whole phrase,
# so "is ours" matches "the ordering advice is ours, read off the papers' own
# ablations" and a bare "ours" with nothing in front of it still does not match
# anything and is still reported.
OURS_PREDICATIVE = (
    "is ours",
    "are ours",
    "marked ours",
)

# How far past the word "ours" to read when deciding which phrasing this is.
# Long enough for the longest entry above, short enough that two markers in one
# sentence cannot be read as one.
OURS_WINDOW = 32

# The published Agent Skills specification's two hard limits, read live at
# agentskills.io/specification on 2026-10-02. A `description` over 1024
# characters or a `name` over 64 makes a SKILL.md non-conformant, which means a
# client validating it (`skills-ref validate`) rejects the file rather than
# loading a skill with a long description. They are checked here because this
# reviewer is the only thing that opens every SKILL.md on every pull request,
# and because the library is already close: its longest description is 994
# characters, 30 short of the ceiling, and ADR-38's word budget pushes that
# number up with every revision.
SPEC_NAME_MAX = 64
SPEC_DESCRIPTION_MAX = 1024

# The reading queue, read here for one reason only: to tell a draft skill whose
# papers the pipeline has not read yet from a skill that cites nothing and has
# asked for nothing. `waiting_on_the_queue` says why at length. Absent is not an
# error; it just means no skill gets the benefit of the doubt.
QUEUE_PATH = "docs/research/reading-queue.md"

ARXIV = re.compile(r"arxiv\.org/abs/([0-9]{4}\.[0-9]{4,5}(?:v[0-9]+)?)", re.I)
SECTION = re.compile(r"^## +(.+?)\s*$", re.M)
VALIDATION_TAG = re.compile(r"^\*Validation:", re.M)


# ------------------------------------------------------------- the file half

def sections(body: str) -> list[str]:
    """The `##` headings, in order. The unit a per-section citation would key on."""
    return [m.group(1) for m in SECTION.finditer(body)]


def ours_markers(body: str) -> tuple[int, list[str]]:
    """(markers found, phrasings outside the vocabulary).

    Whitespace is normalised before matching, and that is the whole reason this
    is a function rather than a grep. Five of the nineteen markers in the
    library today are wrapped across two lines by the 80-column prose, so
    `grep "ours, not the paper's"` finds fourteen of them and a reviewer built
    on grep would report the other five as unmarked judgment.

    What this cannot see, said plainly: a passage of unsourced judgment that
    carries no marker at all. The word `ours` is the only handle, so drift in
    the words around it is caught and a missing marker is not. Catching that
    needs the model half, where a reviewer reads the section and asks whether
    its advice is in the papers, and it is the same half duty 2 waits on.

    Both grammars are checked, forwards for the attributive phrasings and
    backwards for the predicative ones, because a marker in the second form
    carries its signal before the word rather than after it. Reading only
    forwards is what this check did until 2026-10-05, and it reported seven
    correct markers in four skills as vocabulary drift, which held `main` red
    for as long as those skills were on it.
    """
    flat = " ".join(body.split())
    found, unknown_phrasings = 0, []
    for match in re.finditer(r"\bours\b", flat):
        window = flat[match.start():match.start() + OURS_WINDOW]
        before = flat[max(0, match.start() - OURS_WINDOW):match.end()]
        if (any(window.startswith(v) for v in OURS_VOCABULARY)
                or any(before.endswith(v) for v in OURS_PREDICATIVE)):
            found += 1
        else:
            unknown_phrasings.append(window.rstrip())
    return found, unknown_phrasings


def paper_sources(papers: list[str]) -> tuple[list[str], list[str]]:
    """(arXiv ids the skill attributes, entries this cannot read).

    The library writes one line per paper, a title and a source separated by a
    dash. Only the source is parsed here: a blog post or a handbook has no
    arXiv id, and that is an entry this check cannot resolve rather than a
    defect in the skill.
    """
    ids, unreadable = [], []
    for entry in papers:
        match = ARXIV.search(entry or "")
        if match:
            ids.append(match.group(1).split("v")[0])
        elif (entry or "").strip():
            unreadable.append(entry.strip())
    return ids, unreadable


def waiting_on_the_queue(row, raw: str) -> str:
    """Why this skill cites no claims, when the reason is on the record.

    Returns the sentence to append to the registrar's problem, or "" when the
    skill has no such excuse and the problem stands as a failure.

    Three conditions, all of them required, because each one on its own is the
    state the registrar is right to fail. The skill says `status: draft`, so it
    is not published advice. It lists the papers it was built from, so the
    evidence exists and is named. And at least one of those papers is an
    unchecked line in docs/research/reading-queue.md asked for by this skill,
    so distill has been told to read it and has not got there yet.

    `skills/agent-containment` is why this exists. It landed on 2026-09-30
    citing six papers and zero claims, because three of the six had never been
    triaged and two more were routed and never distilled: there was no claim id
    in the database for it to cite. The queue line is the request that fixes
    that, and `pipeline/reading_queue.py` is what drains it.

    A missing or unreadable queue file returns "", which leaves the failure in
    place. The conservative direction is the one that keeps the finding.
    """
    if (row.skill_status or "").strip().lower() != "draft":
        return ""
    if row.claim_ids:
        return ""
    fm, _ = registrar.split_frontmatter(raw)
    provenance = registrar.parse_frontmatter(fm).get("provenance") or {}
    papers, _unreadable = paper_sources(provenance.get("papers") or [])
    if not papers:
        return ""
    try:
        queue = pathlib.Path(QUEUE_PATH).read_text()
    except OSError:
        return ""
    asked: list[str] = []
    for line in queue.splitlines():
        marker = re.match(r"^\s*-\s*\[ \]\s*(?P<body>.*)$", line)
        if not marker or f"skills/{row.slug}" not in marker.group("body"):
            continue
        found = re.search(r"arxiv:\s*([0-9]{4}\.[0-9]{4,5})", marker.group("body"), re.I)
        if found:
            asked.append(found.group(1))
    pending = [p for p in asked if p in papers] or asked
    if not pending:
        return ""
    return (f"Waiting on the pipeline rather than opting out: it is a draft, it "
            f"names {len(papers)} papers, and {len(pending)} of them are "
            f"unchecked lines in {QUEUE_PATH} asked for by this skill "
            f"({', '.join('arxiv:' + p for p in sorted(pending)[:4])}). It can "
            f"cite a claim id on the run after distill reads them.")


def review_file(row, raw: str, problems: list[str]) -> list[Finding]:
    """Every check that lives in the SKILL.md itself. No database, no model."""
    findings: list[Finding] = []
    slug = row.slug

    for problem in problems:
        if f"skills/{slug}/" not in problem:
            continue
        waiting = waiting_on_the_queue(row, raw) if "cites no claim ids" in problem else ""
        if waiting:
            # Not a defect: a draft whose evidence the pipeline has not read
            # yet. The registrar's sentence turns on the word "silently", and
            # a skill with a pending line in the reading queue is the loudest
            # a skill can be about what it is missing. `unknown` keeps the
            # ADR-36 gate blocking exactly as `fail` did, because this slice
            # can never return `pass` for any skill (see the test of that
            # name), so the only thing the severity decides is whether `main`
            # goes red and the owner gets the panel's alarm mail for a state
            # that is on the record and already being drained.
            findings.append(Finding("registrable", "unknown", f"{problem} {waiting}"))
        else:
            findings.append(Finding("registrable", "fail", problem))

    # duty 1, the half that needs no database: the ids have to be a usable list
    # before anything can ask Postgres about them.
    seen, duplicates = set(), []
    for claim_id in row.claim_ids:
        if claim_id in seen:
            duplicates.append(claim_id)
        seen.add(claim_id)
    if duplicates:
        findings.append(Finding(
            "claim-ids", "fail",
            f"cites {sorted(set(duplicates))} more than once. The provenance "
            "block is the skill's evidence list and a repeated id makes it "
            "read as wider evidence than it is."))
    bad = [c for c in row.claim_ids if c <= 0]
    if bad:
        findings.append(Finding(
            "claim-ids", "fail",
            f"cites {bad} as claim ids, and claims.id is a bigserial that "
            "starts at 1."))

    fm, body = registrar.split_frontmatter(raw)
    parsed = registrar.parse_frontmatter(fm)
    provenance = parsed.get("provenance") or {}

    papers = provenance.get("papers") or []
    if isinstance(papers, str):
        papers = [papers] if papers else []
    if not papers:
        findings.append(Finding(
            "papers-listed", "fail",
            "lists no papers. A reader cannot check a claim id against a "
            "source the skill never names."))
    arxiv_ids, unreadable = paper_sources(papers)
    repeats = sorted({i for i in arxiv_ids if arxiv_ids.count(i) > 1})
    if repeats:
        findings.append(Finding(
            "papers-listed", "fail",
            f"lists {repeats} twice in provenance.papers."))
    if unreadable:
        findings.append(Finding(
            "papers-listed", "unknown",
            f"{len(unreadable)} paper entries carry no arXiv id, so the claims "
            f"cited from them cannot be cross-checked: {unreadable}"))
    if arxiv_ids:
        findings.append(Finding(
            "papers-listed", "note",
            f"arXiv sources attributed: {len(arxiv_ids)}"))

    # The external format the file has to satisfy to be loadable at all. Not
    # one of ADR-13's three duties, and it is here for the reason above: one
    # reader of every SKILL.md, running on every pull request that touches one.
    description = str(parsed.get("description") or "")
    name = str(parsed.get("name") or "")
    if len(description) > SPEC_DESCRIPTION_MAX:
        findings.append(Finding(
            "spec-conformance", "fail",
            f"description is {len(description)} characters and the Agent "
            f"Skills specification allows {SPEC_DESCRIPTION_MAX}. A client "
            "that validates the file rejects it."))
    elif not description:
        findings.append(Finding(
            "spec-conformance", "fail",
            "has no description, which the specification requires and which is "
            "the only part of a skill an agent reads before deciding to load "
            "it."))
    if len(name) > SPEC_NAME_MAX:
        findings.append(Finding(
            "spec-conformance", "fail",
            f"name is {len(name)} characters and the specification allows "
            f"{SPEC_NAME_MAX}."))
    if description and len(description) <= SPEC_DESCRIPTION_MAX:
        findings.append(Finding(
            "spec-conformance", "note",
            f"description is {len(description)} characters, "
            f"{SPEC_DESCRIPTION_MAX - len(description)} under the ceiling"))

    # duty 3: judgment that is ours has to say so, in words the library knows.
    markers, drifted = ours_markers(body)
    if drifted:
        findings.append(Finding(
            "ours-marked", "fail",
            "uses a phrasing for unsourced judgment that is not in the "
            f"library's vocabulary: {drifted}. The three it recognises are "
            f"{list(OURS_VOCABULARY)}."))
    findings.append(Finding(
        "ours-marked", "note",
        f"judgment marked as the library's own, in its own "
        f"vocabulary: {markers}"))

    # duty 2: the mapping the format does not carry.
    heads = sections(body)
    tags = len(VALIDATION_TAG.findall(body))
    findings.append(Finding(
        "claim-supports-sentence", "unknown",
        f"{len(heads)} sections, {len(row.claim_ids)} claim ids cited once for "
        f"the whole document, and {tags} sections carrying an ADR-38 "
        "*Validation:* tag. Nothing in the file says which claim supports "
        "which section, so whether a cited claim supports the sentence citing "
        "it is not decidable from this document."))

    return findings


# --------------------------------------------------------- the database half

# Every statement this file sends, in one place, so tests can parse them with
# libpg_query and resolve every relation and column against db/schema.sql. No
# CI job here can execute them, which is exactly why they are checked this way.
QUERIES = {
    "claims": """
        select c.id, c.paper_id, p.url
        from claims c
        join papers p on p.id = c.paper_id
        where c.id = any(%s)
    """,
    "consensus": """
        select target, verdicts, passes, fails, one_text, unanimous, latest
        from panel_consensus
        where target = any(%s)
    """,
    "file": """
        insert into panel_verdicts
            (target, reviewer, verdict, findings, target_sha, reviewer_sha, model)
        values (%s, 'provenance', %s, %s, %s, %s, null)
        returning id
    """,
}


def connect(writable: bool):
    return panel.connect(writable, cannot=(
        "duty 1 could not be measured and no claim id was checked against the "
        "corpus"))


def live_claims(conn, claim_ids: list[int]) -> dict[int, tuple[str, str]]:
    """{claim id: (paper id, paper url)} for the ids that exist."""
    if not claim_ids:
        return {}
    rows = conn.execute(QUERIES["claims"], (list(claim_ids),)).fetchall()
    return {int(cid): (pid, url) for cid, pid, url in rows}


def consensus(conn, targets: list[str]) -> dict[str, dict]:
    if not targets:
        return {}
    out = {}
    for row in conn.execute(QUERIES["consensus"], (list(targets),)).fetchall():
        target, verdicts, passes, fails, one_text, unanimous, latest = row
        out[target] = {"verdicts": verdicts, "passes": passes, "fails": fails,
                       "one_text": one_text, "unanimous": unanimous,
                       "latest": latest.isoformat() if latest else None}
    return out


def review_claims(row, raw: str, live: dict[int, tuple[str, str]]) -> list[Finding]:
    """Duty 1, and the cross-check that a cited claim's paper is attributed."""
    findings: list[Finding] = []

    missing = sorted({c for c in row.claim_ids if c not in live})
    if missing:
        findings.append(Finding(
            "claims-exist", "fail",
            f"cites {len(missing)} claim ids that are not in the corpus: "
            f"{missing}. ADR-13's first duty is that every cited claim exists."))
    present = [c for c in row.claim_ids if c in live]
    if present:
        findings.append(Finding(
            "claims-exist", "note",
            f"{len(present)} of {len(row.claim_ids)} cited claims resolve to a "
            "row in claims"))

    fm, _ = registrar.split_frontmatter(raw)
    papers = (registrar.parse_frontmatter(fm).get("provenance") or {}).get("papers") or []
    if isinstance(papers, str):
        papers = [papers] if papers else []
    attributed = set(paper_sources(papers)[0])

    unattributed: dict[str, list[int]] = {}
    for claim_id in present:
        paper_id, url = live[claim_id]
        source = (ARXIV.search(url or "") or ARXIV.search(paper_id or ""))
        key = source.group(1).split("v")[0] if source else (paper_id or "")
        if source and key not in attributed:
            unattributed.setdefault(key, []).append(claim_id)
        elif not source:
            unattributed.setdefault(f"non-arxiv:{key}", []).append(claim_id)

    for key, ids in sorted(unattributed.items()):
        if key.startswith("non-arxiv:"):
            findings.append(Finding(
                "claim-paper-attributed", "unknown",
                f"claims {sorted(ids)} come from {key.split(':', 1)[1]}, which "
                "carries no arXiv id, so whether the skill attributes that "
                "source cannot be decided by id."))
        else:
            findings.append(Finding(
                "claim-paper-attributed", "fail",
                f"claims {sorted(ids)} come from arxiv.org/abs/{key}, which is "
                "not in provenance.papers. The skill cites evidence it does "
                "not attribute, so a reader cannot get from the page to the "
                "source."))
    return findings


def review_validated(row, raw: str, panel: dict | None) -> list[Finding]:
    """`provenance.validated` is the panel's field, so it needs a panel row.

    ADR-38's ruling (docs/decisions.md): the frontmatter `validated` field stays
    the ADR-13 panel's. A skill that asserts it with no unanimous verdict behind
    it is the library making its own strongest claim about itself.
    """
    fm, _ = registrar.split_frontmatter(raw)
    provenance = registrar.parse_frontmatter(fm).get("provenance") or {}
    validated = str(provenance.get("validated") or "").strip()
    if not validated:
        return [Finding("validated-field", "note",
                        "validated is empty, which is honest for a skill the "
                        "panel has not passed")]
    if panel is None:
        return [Finding("validated-field", "unknown",
                        "asserts validated, and whether the panel ever passed "
                        "this text cannot be read without the database")]
    if panel.get("unanimous"):
        return [Finding("validated-field", "note",
                        "asserts validated, and the panel's three verdicts "
                        "pass on one text")]
    return [Finding(
        "validated-field", "fail",
        "asserts validated, and panel_consensus has "
        f"{panel.get('passes', 0)} passes from {panel.get('verdicts', 0)} "
        "verdicts on this target. ADR-38 makes that field the panel's.")]


# ------------------------------------------------------------------ the pass

def reviewer_sha() -> str | None:
    """The git blob sha of this file, so a verdict says which reviewer judged."""
    return panel.reviewer_sha("tools/panel_provenance.py")


def review(skills_dir: pathlib.Path | None = None, conn=None,
           only: str | None = None, rows=None,
           problems: list[str] | None = None) -> list[dict]:
    """One verdict per skill, as the dicts a `panel_verdicts` row is built from.

    `rows` and `problems` are passed in by the daily job, which reads every
    skill from `main` over the GitHub API rather than from its own image. The
    image is as old as the last deploy, and reviewing a skill the image cannot
    see is the merged-but-inert failure this sprint exists to close.
    """
    if rows is None:
        rows, problems = registrar.read_skills(skills_dir)
    problems = problems or []
    if only:
        rows = [r for r in rows if r.slug == only]
    skills_dir = skills_dir or registrar.SKILLS_DIR

    panels: dict[str, dict] = {}
    if conn is not None:
        panels = consensus(conn, [r.path for r in rows])

    out = []
    for row in rows:
        raw = (skills_dir / row.slug / "SKILL.md").read_text()
        findings = review_file(row, raw, problems)
        if conn is not None:
            findings += review_claims(row, raw, live_claims(conn, row.claim_ids))
            findings += review_validated(row, raw, panels.get(row.path, {}))
        else:
            findings.append(Finding(
                "claims-exist", "unknown",
                f"{len(row.claim_ids)} cited claim ids were not checked "
                "against the corpus, because this run holds no database "
                "credential."))
            findings += review_validated(row, raw, None)
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
    ap.add_argument("--files-only", action="store_true",
                    help="only the checks that live in the file. No database.")
    ap.add_argument("--record", action="store_true",
                    help="file each verdict as a panel_verdicts row")
    ap.add_argument("--skill", default="", help="one skill slug")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    conn = None
    if not args.files_only:
        conn = connect(writable=args.record)
        if conn is None and args.record:
            print("nothing was recorded.")
            return 2
    elif args.record:
        ap.error("--record needs the database half; drop --files-only")

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
                          "recorded": written}, indent=2))
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
