#!/usr/bin/env python3
"""ADR-13's validator: did the builder actually do better work with this skill.

    python3 tools/panel_validator.py                    # review every skill
    python3 tools/panel_validator.py --files-only       # the CI half: no database
    python3 tools/panel_validator.py --skill harness-engineering
    python3 tools/panel_validator.py --record           # DATABASE_URL: file the verdicts
    python3 tools/panel_validator.py --json             # any of the above, for a script

The third and last of ADR-13's reviewers, built 2026-10-03, which completes the
panel. `panel_consensus` has computed its gate as three passes on one text since
the table was written, and until this file existed the most any skill could ever
earn was two, so the arithmetic that decides a merge had never been reachable
even in principle.

ADR-13 gives this reviewer one sentence: *"Runs the A/B trial - bare model vs.
skill-loaded on held-out prompts - and passes only if behavior moves in the
direction the evidence supports."*

## It reads the trial. It does not run it

This is the one design decision in the file and it is the opposite of what the
sentence above sounds like.

The trial exists: `tools/skill_eval.py`, written 2026-09-30 under ADR-36. It
takes a model key, about $0.40 a skill, and several minutes. The build note for
slice 1 (docs/product/reviewer-panel.md) predicted that this reviewer would
therefore be blocked on an open infrastructure question, which job holds a key
and what the per-run cap is. **It is not blocked, and the reason is rule 1 of
docs/product/skill-validation.md §V5: the policy is pre-registered.** A reviewer
that ran its own trial at review time would be choosing the repetitions, the
subject model and the threshold at review time, which is the exact thing
pre-registration forbids, and it would re-run on every review until one came
back green. The trial is a dated receipt somebody ran once under a policy fixed
in advance. The reviewer's job is to judge the receipt.

So the key question moves off the panel entirely. It is now "who runs
`tools/skill_eval.py`, on what schedule, under what cap", which is a scheduling
question with no gate waiting on it, and the panel is complete today.

This is the second time in two days that a reviewer this list said would need a
model key turned out to need none; the adversary was the first. Both for the
same underlying reason, which is worth stating once: ADR-13's duties are
questions about recorded evidence, and recorded evidence is queryable.

## What it decides, and the one bar it did not invent

Four findings carry ADR-13's duty, and all four are file facts:

1. **A trial exists.** No `evals/results.json` is `unknown`, never a pass. A
   suite with no result is reported differently from no suite at all, because
   the two want different people: the first wants whoever runs the harness and
   the second wants the skill seat.
2. **The trial measured this text.** `results.json` carries
   `skill_md_sha256`, and a skill edited after its eval has a result describing
   an earlier revision. A stale receipt is `unknown`. This is the same property
   `panel_verdicts.target_sha` exists for, applied one level down: without it a
   skill could earn three passes and then be edited, and the merge would ship
   the edit.
3. **The direction.** Not re-derived here. `tools/skill_eval.py`'s own
   `gate_problems` is the organization's answer to "why is this result not a
   pass", and this reviewer calls it rather than keeping a second copy, for the
   same reason the adversary reads `deprecated_claims`'s 0.7 instead of
   choosing a threshold: one question deserves one answer. Any problem it
   returns is a `fail`.
4. **The policy was not tuned after the fact.** The suite file carries the
   pre-registered policy and the result carries the copy that ran. If they
   disagree, somebody edited the threshold or the repetitions after seeing the
   numbers, which rule 1 exists to prevent and which nothing in this
   repository checked until now.

One more finding is a duty of ADR-36 rather than of ADR-13, and it is labelled
`status-vs-eval` so nobody mistakes it for one of the four: *"A skill with no
eval is `status: draft`, never `active`."* Those are ADR-36's own words. All six
skills on main say `status: active` and none of them has an eval, so this
reviewer's first run fails the whole library on a rule the owner accepted on
2026-09-29. That is the correct reading of an accepted decision and not this
file legislating, which is the line the adversary's `evidence-grade` finding
stays on the other side of. It is checked here because this is the only reader
in the repository that opens both a skill's frontmatter and its `evals/`
directory.

ADR-36 also says what to do about a skill whose eval shows no gain: it "is
retired with the numbers", a finding rather than a failure. That is not in
tension with a `fail` verdict here. The panel's `fail` means do not promote this
text; ADR-36 says the response to the numbers is retirement rather than a
rewrite. Two different decisions about one measurement.

## Two findings that are evidence and never move a verdict

Labelled the way `spec-conformance` and `evidence-breadth` are labelled in the
other two reviewers, and for the identical reason: no decision in any register
sets a bar for either, and a reviewer that invented one would be legislating.

`trigger-firing` reports the newest `skills/_validation/results/` receipt for
this skill, its pass rate and whether it was measured against the current text.
The trigger test asks whether a skill fires, which is a different question from
whether it helps, and ADR-36 fixes no number for it.

`eval-spend` reports `spend_usd`, because the ledger already asks for skill-eval
spend to appear in the opex table before it becomes a habit and a verdict row is
a place the number is recorded with its date.

## The halves, and why this reviewer's file half is the whole of it

The provenance reviewer's `--files-only` runs most of its checks and the
adversary has no file half at all, because its whole input is the claim graph.
This one is the far end of that range: **every finding above is a file fact, so
`--files-only` and the live half return the same verdict.** The database is
needed only by `--record`, to write the row. A reviewer whose judgment needs no
credential is worth having in a panel of three where the other two do, because
it is the one verdict a pull request can see in full.

The one thing that does not come free: when the daily job reads skills from
`main` over the GitHub API rather than from its own image, it has to fetch the
`evals/` files too. It did not until this build, and a reviewer reading a
directory that was never written would have reported every skill unmeasured
forever, in a voice indistinguishable from the truth. That is the
merged-but-inert shape again and `pipeline/skill_revision.py` now fetches them.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# This file's own directory, which is `tools/` in the repository and `/root`
# inside the Modal image `pipeline/skill_revision.py` builds. One line covers
# both, the same way the other two reviewers do it.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import panel                        # noqa: E402
import skill_eval                   # noqa: E402
import skill_registrar as registrar  # noqa: E402

REVIEWER = "validator"

Finding = panel.Finding
verdict_of = panel.verdict_of
render = panel.render

# The two names a suite file is allowed to have, and the result file's name.
# Read from the harness rather than retyped, because the harness is what writes
# them and a reviewer looking for the wrong filename reports a skill unmeasured
# that is in fact measured. That failure is silent, which is why it is one line.
TASK_FILENAMES = skill_eval.TASK_FILENAMES
RESULTS_FILENAME = "results.json"

# Where the trigger test files its receipts. Not under a skill's own directory,
# because one run measures the whole library against one decoy panel: the
# receipt is a library-level document that happens to contain per-skill rows.
TRIGGER_RESULTS = "_validation/results"

# The policy keys that have to agree between the suite and the result. Only the
# ones that change what a number means: the threshold a gain is measured
# against, how many samples it rests on, and which two models produced it.
# `pre_registered` and prose keys are deliberately not here, so a suite's
# comments can be edited without reading as tampering.
PRE_REGISTERED_KEYS = ("min_delta", "repetitions", "subject", "judge")


# ------------------------------------------------------------- the receipts

def evals_dir(skills_dir: pathlib.Path, slug: str) -> pathlib.Path:
    return skills_dir / slug / "evals"


def read_json(path: pathlib.Path) -> tuple[dict | None, str]:
    """(document, why not). Never raises: a malformed receipt is a finding."""
    if not path.exists():
        return None, "absent"
    try:
        return json.loads(path.read_text()), ""
    except (json.JSONDecodeError, OSError) as exc:
        return None, f"{path.name} could not be read: {exc}"


def suite_of(skills_dir: pathlib.Path, slug: str) -> tuple[dict | None, str]:
    """The pre-registered suite, under either of the two names it may carry."""
    base = evals_dir(skills_dir, slug)
    for name in TASK_FILENAMES:
        doc, why = read_json(base / name)
        if doc is not None or why != "absent":
            return doc, why
    return None, "absent"


def trigger_receipt(skills_dir: pathlib.Path, slug: str) -> dict | None:
    """The newest trigger-test suite row for one skill, or None.

    Newest by filename, which is how these files are named and sorted
    everywhere else in the repository: the date leads. An `-experiment` or
    `-retired` engine's receipt is skipped, because a receipt from an engine the
    library does not run is not evidence about the library.
    """
    results = skills_dir / TRIGGER_RESULTS
    if not results.is_dir():
        return None
    for path in sorted(results.glob("*.json"), reverse=True):
        if "experiment" in path.name or "retired" in path.name:
            continue
        doc, _ = read_json(path)
        if not doc:
            continue
        for suite in doc.get("suites") or []:
            if suite.get("skill") == slug:
                cases = suite.get("cases") or []
                passed = sum(1 for c in cases if c.get("passed"))
                return {"file": path.name, "generated": doc.get("generated"),
                        "engine": doc.get("engine"), "cases": len(cases),
                        "passed": passed,
                        "skill_sha256": suite.get("skill_sha256") or ""}
    return None


# --------------------------------------------------------------- the checks

class Receipts:
    """One skill's eval files, read once.

    Four checks below ask about the result and two ask about the suite, and the
    first draft re-read each file for every one of them. Six reads per skill is
    nothing at this size; one object is still the right shape, because the
    alternative is six chances for two checks in one verdict to disagree about
    what the file said.
    """

    def __init__(self, skills_dir: pathlib.Path, slug: str):
        base = evals_dir(skills_dir, slug)
        self.result, self.result_why = read_json(base / RESULTS_FILENAME)
        self.suite, self.suite_why = suite_of(skills_dir, slug)


def review_trial(row, receipts: Receipts) -> list[Finding]:
    """ADR-13's duty, as the four questions a receipt can answer."""
    findings: list[Finding] = []
    result, why = receipts.result, receipts.result_why
    suite, suite_why = receipts.suite, receipts.suite_why

    if result is None:
        if why != "absent":
            findings.append(Finding("trial-exists", "fail", why))
            return findings
        if suite is not None:
            findings.append(Finding(
                "trial-exists", "unknown",
                f"has a suite of {len(suite.get('tasks') or [])} tasks and "
                f"no {RESULTS_FILENAME}, so the trial was written and never "
                "run. "
                "ADR-13 cannot pass a skill whose behaviour nobody measured, "
                "and this one is waiting on a run of tools/skill_eval.py "
                "rather than on an author."))
        else:
            findings.append(Finding(
                "trial-exists", "unknown",
                "has no evals/ suite and no result. ADR-36: a skill with no "
                "eval is status draft, never active. The suite is the skill "
                "seat's to write, deliberately not this harness's and not the "
                "skill's own author's, because cases written by the author in "
                "the same session are the contamination the corpus warns "
                "about."))
        return findings

    # duty: the trial has to have measured the text under review. The receipt
    # pins itself to a sha256 of the whole SKILL.md and `row.sha` is the same
    # number over the file this panel is judging.
    measured_sha = str(result.get("skill_md_sha256") or "")
    if not measured_sha:
        findings.append(Finding(
            "trial-pins-text", "unknown",
            f"{RESULTS_FILENAME} records no skill_md_sha256, so which revision "
            "of the skill it measured cannot be established."))
    elif measured_sha != row.sha:
        findings.append(Finding(
            "trial-pins-text", "unknown",
            f"was measured against SKILL.md {measured_sha[:12]} and the text "
            f"under review is {row.sha[:12]}. The result describes an earlier "
            f"revision, so it is not evidence about this one. Dated "
            f"{result.get('date') or 'no date'}."))
    else:
        findings.append(Finding(
            "trial-pins-text", "note",
            f"the result was measured against this exact text "
            f"({row.sha[:12]}) on {result.get('date') or 'no date'}"))

    # duty: the direction. One implementation of this question lives in the
    # harness that computed the numbers, and this is a call to it.
    #
    # The second argument is the measurement before this one, read out of the
    # result's own append-only `history` (2026-10-04). Until that record
    # existed this was `None`, because a reviewer holds one file and the older
    # numbers had been overwritten by the run that produced it. With the record
    # the same call also answers "is this a fall from the last one", which is
    # the question ADR-37's gate asks and the panel could not.
    history = skill_eval.history_entries(result)
    prior = history[-2] if len(history) > 1 else None
    problems = skill_eval.gate_problems(result, prior)
    for problem in problems:
        findings.append(Finding("trial-direction", "fail", problem))
    delta = result.get("delta") or {}
    spread = delta.get("ci95") or []
    findings.append(Finding(
        "trial-direction", "note",
        f"verdict {result.get('verdict')!r}, delta "
        f"{delta.get('mean')} with 95% interval {spread}, over "
        f"{result.get('tasks')} tasks at {result.get('repetitions')} "
        f"repetitions on {result.get('subject_model')}, judged by "
        f"{result.get('judge_model')}"))

    findings.append(Finding(
        "trial-record", "note",
        f"{len(history)} measurement{'' if len(history) == 1 else 's'} on the "
        f"record" + (f", and this verdict compares the newest against the one "
                     f"of {prior.get('date') or 'no date'}" if prior else
                     ", so there is no earlier number to compare it against")))

    findings += review_pre_registration(result, suite, suite_why)
    return findings


def review_suite(slug: str, skills_dir: pathlib.Path,
                 receipts: Receipts) -> list[Finding]:
    """Can the harness run this suite at all. Its question, so its answer.

    `tools/skill_eval.py`'s `conformance` is the organization's answer to "is
    this eval file runnable", and `--check` exists to be a gate over it. So
    this reads it rather than keeping a second opinion, exactly as the
    direction check reads `gate_problems`.

    It is not decoration. The three open skill-seat pull requests that each
    carry eight `evals/evals.json` files (#151, #152, #159) write
    `suite_version: 2`, and until 2026-10-04 this harness spoke only contract
    1, so `conformance` refused every one of them for their version number. It
    speaks both now. What it reports on those eight files instead is the real
    defect underneath: none of them carries a `policy` block, so the
    repetitions rule 1 asks the author to pre-register are not in the file, and
    the harness no longer supplies them. A reviewer that only compared policies
    would have reported those suites as present and fine.
    """
    if receipts.suite is None:
        return []
    try:
        problems = skill_eval.conformance(
            skill_eval.normalize(receipts.suite), slug,
            evals_dir(skills_dir, slug))
    except Exception as exc:                        # pragma: no cover
        return [Finding("suite-runnable", "unknown",
                        f"the suite could not be checked: {exc}")]
    return [Finding("suite-runnable", "fail", problem) for problem in problems]


def review_pre_registration(result: dict, suite: dict | None,
                            suite_why: str) -> list[Finding]:
    """Rule 1: the policy was fixed before the run, so nobody tuned until green.

    Rule 1's words name three things the suite has to carry: "the repetitions,
    the models and the threshold, and the run copies them into the result
    rather than choosing them". So there are two different failures here, and
    conflating them would produce a wrong accusation, which is worse than a
    missed one.

    **Not registered** is a key the suite never wrote. The run then chose it,
    which is what rule 1 forbids, and the honest finding names which of the
    three are missing. The suites the skill seat has actually written are in
    this state: they carry the two model names at the top level, in prose
    rather than as model ids, and no `policy` block, so there is no threshold
    anywhere and no registered repetitions. This reviewer and
    `skill_eval.conformance` both say so as of 2026-10-04, which is one defect
    reported by the two reviewers whose question it falls under rather than a
    double count: a suite that registers no n cannot be run, and a run that
    chose its own n is not pre-registered.

    **Disagreement** is a key both documents wrote and wrote differently. That
    one means somebody edited one after the other, and the only edit in that
    direction that pays is one made after seeing the numbers: a delta of 0.16
    misses a registered 0.2 and clears a 0.15 written in afterwards.

    The raw suite is read here rather than the normalized one, deliberately.
    `normalize` invented a repetitions default until 2026-10-04, so a
    normalized suite always looked as though it had registered one, and a check
    reading it would report every suite in the library as compliant with the
    rule it breaks. That is exactly the state `skill_eval.conformance` was in,
    because it is handed the normalized suite and has no raw one to read, which
    is why reading raw here is still the rule even now that the default is
    gone: this check's correctness should not depend on another file's default.
    """
    if suite is None:
        return [Finding(
            "trial-pre-registered", "unknown",
            f"has a result and no suite file ({suite_why}), so the policy the "
            "run copied into the result cannot be compared with the policy as "
            "written, and rule 1 cannot be checked.")]

    ran = result.get("policy") or {}
    written = suite.get("policy") or {}
    findings = []

    missing = [k for k in PRE_REGISTERED_KEYS if written.get(k) is None]
    if missing:
        elsewhere = sorted(k for k in ("subject_model", "judge", "repetitions")
                           if suite.get(k) is not None)
        hint = (f" The file does carry {elsewhere} at the top level, so the "
                "fix is moving them into `policy` rather than choosing new "
                "numbers." if elsewhere else "")
        findings.append(Finding(
            "trial-pre-registered", "fail",
            f"registers no {missing} in `policy`, so the run chose them. Rule "
            "1 of docs/product/skill-validation.md section V5 asks the suite "
            "for the repetitions, the models and the threshold, because a "
            f"threshold chosen after the numbers is not a threshold.{hint}"))

    disagreements = [
        f"{key}: the run used {ran.get(key)!r} and the suite now says "
        f"{written.get(key)!r}"
        for key in PRE_REGISTERED_KEYS
        if written.get(key) is not None and ran.get(key) != written.get(key)]
    if disagreements:
        findings.append(Finding(
            "trial-pre-registered", "fail",
            "the policy in the result and the policy in the suite disagree, so "
            "one was edited after the other and the threshold this result is "
            f"measured against is not the one that was registered. "
            f"{'; '.join(disagreements)}"))

    if not findings:
        registered = {k: written.get(k) for k in PRE_REGISTERED_KEYS}
        findings.append(Finding(
            "trial-pre-registered", "note",
            f"the suite and the result agree on the registered policy: "
            f"{registered}"))
    return findings


def review_status(row, receipts: Receipts) -> list[Finding]:
    """ADR-36's own sentence, labelled so it is not read as an ADR-13 duty.

    "A skill with no eval is `status: draft`, never `active`." The frontmatter
    field is the skill's claim about itself and the `evals/` directory is the
    evidence for it, and this is the only reader in the repository that opens
    both.
    """
    status = (row.skill_status or "").strip().lower()
    if receipts.result is not None or status != "active":
        return []
    return [Finding(
        "status-vs-eval", "fail",
        f"says status: {row.skill_status!r} and has no evals/"
        f"{RESULTS_FILENAME}. ADR-36 part 2: a skill with no eval is status "
        "draft, never active. The field is the library's own strongest claim "
        "about a skill and it is currently making it without a measurement.")]


def review_validated_claim(row, raw: str, receipts: Receipts) -> list[Finding]:
    """`provenance.validated` asserts a trial. This asks for the receipt.

    Deliberately a different question from the provenance reviewer's check on
    the same field, which asks whether `panel_consensus` passed this text. That
    one is a database fact about the panel. This one is a file fact about the
    trial, and a skill can fail either without failing the other. ADR-13's
    independence is about context rather than code, so two reviewers reading one
    field from two sources is the design and not a duplicate.
    """
    fm, _ = registrar.split_frontmatter(raw)
    provenance = registrar.parse_frontmatter(fm).get("provenance") or {}
    asserted = str(provenance.get("validated") or "").strip()
    if not asserted:
        return []
    if receipts.result is not None:
        return []
    return [Finding(
        "validated-has-a-receipt", "unknown",
        "provenance.validated describes an A/B trial in prose and no "
        f"evals/{RESULTS_FILENAME} exists, so the trial it names cannot be "
        "read, reproduced or dated by anything in this repository. The "
        f"assertion begins {asserted[:60]!r}.")]


def review_evidence(row, skills_dir: pathlib.Path,
                    receipts: Receipts) -> list[Finding]:
    """Recorded, never graded. Both of these are notes by construction."""
    findings: list[Finding] = []

    trigger = trigger_receipt(skills_dir, row.slug)
    if trigger is None:
        findings.append(Finding(
            "trigger-firing", "note",
            "no trigger-test receipt names this skill"))
    else:
        current = "the current text"
        if trigger["skill_sha256"] and not row.sha.startswith(
                trigger["skill_sha256"]):
            current = (f"an earlier text ({trigger['skill_sha256']}, and this "
                       f"one is {row.sha[:16]})")
        findings.append(Finding(
            "trigger-firing", "note",
            f"{trigger['passed']} of {trigger['cases']} trigger cases passed "
            f"on {trigger['generated']} under {trigger['engine']}, measured "
            f"against {current}"))

    result = receipts.result
    if result is not None and result.get("spend_usd") is not None:
        findings.append(Finding(
            "eval-spend", "note",
            f"the trial behind this verdict cost ${result['spend_usd']} on "
            f"{result.get('date') or 'an unrecorded date'}"))
    return findings


# --------------------------------------------------------- the database half

# Every statement this file sends, in one place, so the tests can parse them
# with libpg_query and resolve every relation and column against db/schema.sql.
# No CI job here can execute them, which is exactly why they are checked that
# way. This reviewer sends one, because nothing it decides is in the database.
QUERIES = {
    "file": """
        insert into panel_verdicts
            (target, reviewer, verdict, findings, target_sha, reviewer_sha, model)
        values (%s, 'validator', %s, %s, %s, %s, null)
        returning id
    """,
}


def connect(writable: bool):
    return panel.connect(writable, cannot=(
        "no verdict could be filed. Every check this reviewer makes is a file "
        "fact, so its verdict is unaffected"))


# ------------------------------------------------------------------ the pass

def reviewer_sha() -> str | None:
    """The git blob sha of this file, so a verdict says which reviewer judged."""
    return panel.reviewer_sha("tools/panel_validator.py")


def review(skills_dir: pathlib.Path | None = None, conn=None,
           only: str | None = None, rows=None,
           problems: list[str] | None = None) -> list[dict]:
    """One verdict per skill, as the dicts a `panel_verdicts` row is built from.

    `conn` is accepted and never read. The signature is the panel's, because
    `pipeline/skill_revision.py`'s `review_pass` calls all three reviewers with
    the same arguments, and a third shape there would be a third code path for
    the thing that files the rows. That it goes unused is this reviewer's whole
    distinguishing property and the docstring above says why.

    `problems` is accepted and not read, for the reason the adversary gives: the
    registrar's problems are defects the provenance reviewer already files, and
    a second reviewer repeating them would make one defect look like two
    independent findings.
    """
    if rows is None:
        rows, _ = registrar.read_skills(skills_dir)
    if only:
        rows = [r for r in rows if r.slug == only]
    skills_dir = skills_dir or registrar.SKILLS_DIR

    out = []
    for row in rows:
        raw = (skills_dir / row.slug / "SKILL.md").read_text()
        receipts = Receipts(skills_dir, row.slug)
        findings = review_trial(row, receipts)
        findings += review_suite(row.slug, skills_dir, receipts)
        findings += review_status(row, receipts)
        findings += review_validated_claim(row, raw, receipts)
        findings += review_evidence(row, skills_dir, receipts)
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
                    help="the CI half. Identical verdicts: nothing this "
                         "reviewer decides is in the database.")
    ap.add_argument("--record", action="store_true",
                    help="file each verdict as a panel_verdicts row")
    ap.add_argument("--skill", default="", help="one skill slug")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.files_only and args.record:
        ap.error("--record needs the database; drop --files-only")

    conn = None
    if args.record:
        conn = connect(writable=True)
        if conn is None:
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
