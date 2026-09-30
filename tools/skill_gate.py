#!/usr/bin/env python3
"""ADR-37's gate, as something a pull request can run.

    python3 tools/skill_gate.py                          # against origin/main
    python3 tools/skill_gate.py --base origin/main --comment /tmp/body.md
    python3 tools/skill_gate.py --json
    python3 tools/skill_gate.py --smoke                  # the clauses, on fixtures

ADR-37, amended 2026-09-29 after the owner confirmed no human in the loop: a
revision or retirement of an existing skill merges on its own when every clause
below passes, and anything else stays a draft pull request for her. This file is
the harness that answers the question. It reports, it labels, and it does not
merge: the merge is a separate step in the workflow, and putting the judgement
somewhere a person can run it by hand is what makes the judgement reviewable.

    scope        every changed file is under skills/<slug>/, one skill only, and
                 the skill already exists. A first version still goes to the
                 owner: the loop maintains, it does not originate.
    pause        skills/MAINTENANCE_PAUSED is not in the tree (guardrail 2).
    provenance   the block parses, cites claim ids, and every id exists in the
                 corpus and is not deprecated.
    eval         results.json describes this exact SKILL.md, its history names
                 the version and the trigger, and its delta is not below the
                 previous version's own lower bound on the same subject model,
                 with the controls unchanged.
    ban list     the revision introduces no new finding against the mechanical
                 entries of docs/voice/ban-list.md.
    trigger test skills/_validation/trigger_test.py exits 0 on this tree.
    page         tests/test_skill_receipts.py passes, which is what "the skill's
                 page still renders" means in this repository.

## The clause that cannot be measured in CI, and what is done about it

The provenance clause is a question about the claim graph, and the only Postgres
this organization has is production. CI holds no credential for it and should
not. So the daily job that does hold the `neon` secret writes
`docs/research/claim-status.json` every day: which claim ids exist, which are
deprecated, and the date it was measured. This gate reads that file, and refuses
to pass on a snapshot older than SNAPSHOT_MAX_AGE_DAYS. A stale snapshot means
the daily job has stopped, and a gate that keeps passing after its evidence
stopped arriving is worse than no gate.

Given `NEON_RO_URL` or `DATABASE_URL` it asks the database directly and says so.

## Why the ban list is judged on the diff and not on the file

Measured on 2026-09-30, before this gate existed: all six skills in the library
carry findings against the mechanical entries, mostly em dashes inside the
`papers:` list in their own frontmatter, plus two uses of "very" and one
"unlock". A gate that failed the whole file would block every revision of every
skill on a debt none of those revisions created, which is how a check gets turned
off. So the clause is that the revision adds none, and the pre-existing count is
reported in the comment as the skill seat's backlog. It is a ledger entry, not a
merge blocker.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import ban_list                     # noqa: E402
import skill_eval                   # noqa: E402
import skill_registrar as registrar  # noqa: E402
import skill_triggers as triggers    # noqa: E402

SNAPSHOT_PATH = "docs/research/claim-status.json"

# How old the claim-status snapshot may be. The job that writes it runs daily, so
# three days is two missed runs: enough that one failed cron does not stop the
# library maintaining itself, short enough that a job which has quietly died
# cannot keep waving revisions through for a week.
SNAPSHOT_MAX_AGE_DAYS = 3

PAUSE_PATH = "skills/MAINTENANCE_PAUSED"

# What a revision is allowed to touch inside its own directory. `reviews/` is
# ADR-38's consumer-report lane.
ALLOWED = ("SKILL.md", "evals/", "reviews/")

# One path outside the skill's own folder, and it needs the owner's eye.
#
# ADR-37's amendment says the diff carries "no file outside the skill's folder".
# Measured against this repository, that clause and `tests/test_skill_receipts.py`
# cannot both be satisfied: every trigger-test receipt is pinned by sha to the
# exact SKILL.md text, the receipts live in `skills/_validation/results/`, and so
# a revision that edits a SKILL.md must either rewrite a receipt there or ship a
# receipt that describes a document nobody can see. The first breaks the scope
# clause and the second breaks the page clause, which means with the clause read
# strictly no revision can ever merge itself.
#
# So a machine-written receipt bundle under this one prefix is allowed, it is
# called out in the comment every single time it is used, and the ledger entry of
# 2026-09-30 asks the owner to confirm the reading or overrule it. It is not a
# skill's content, it is the output of one of the gate's own clauses.
RECEIPTS = "skills/_validation/results/"

OK, FAILING, UNKNOWN = "ok", "failing", "unknown"


class Clause:
    """One clause of the gate: its state, and the sentences behind it."""

    def __init__(self, name: str, state: str, reasons: list[str],
                 notes: list[str] | None = None):
        self.name = name
        self.state = state
        self.reasons = reasons
        self.notes = notes or []

    def as_dict(self) -> dict:
        return {"clause": self.name, "state": self.state,
                "reasons": self.reasons, "notes": self.notes}


# --------------------------------------------------------------- git

def git(*args: str) -> tuple[int, str]:
    proc = subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True)
    return proc.returncode, proc.stdout


def changed_files(base: str) -> tuple[list[str], str]:
    code, out = git("diff", "--name-only", f"{base}...HEAD")
    if code != 0:
        code, out = git("diff", "--name-only", base)
        if code != 0:
            return [], (f"git could not diff against {base}, so the scope "
                        "clause could not be measured")
    return [line.strip() for line in out.split("\n") if line.strip()], ""


def file_at(ref: str, path: str) -> str:
    code, out = git("show", f"{ref}:{path}")
    return out if code == 0 else ""


# --------------------------------------------------------------- the clauses

def scope_clause(files: list[str], error: str, base: str) -> tuple[Clause, str]:
    """Every changed file inside one existing skill. Returns (clause, slug)."""
    if error:
        return Clause("scope", UNKNOWN, [error]), ""
    if not files:
        return Clause("scope", UNKNOWN,
                      [f"nothing changed against {base}, so there is no "
                       "revision to judge"]), ""

    reasons, slugs, receipts = [], set(), []
    for path in files:
        if path.startswith(RECEIPTS):
            receipts.append(path)
            continue
        if not path.startswith("skills/"):
            reasons.append(
                f"{path} is outside skills/, so this is not a revision the loop "
                "may merge. ADR-37 bounds the automatic path to skill files a "
                "harness has measured")
            continue
        parts = path.split("/")
        if len(parts) < 3:
            reasons.append(f"{path} sits at the top of skills/ rather than "
                           "inside one skill's directory")
            continue
        slugs.add(parts[1])
        inside = "/".join(parts[2:])
        if not any(inside == a or inside.startswith(a) for a in ALLOWED):
            reasons.append(f"{path} is not one of {', '.join(ALLOWED)} inside "
                           "the skill's directory")
    if len(slugs) > 1:
        reasons.append("this diff revises " + ", ".join(sorted(slugs))
                       + ". One revision, one skill, so the gate's evidence is "
                       "about one measured thing")
    slug = sorted(slugs)[0] if len(slugs) == 1 else ""
    if slug and not file_at(base, f"skills/{slug}/SKILL.md"):
        reasons.append(
            f"skills/{slug}/SKILL.md does not exist on {base}, so this is a new "
            "skill rather than a revision. A skill's first version goes to the "
            "owner: the loop maintains, it does not originate")
    if not slugs and receipts:
        reasons.append(
            "this diff rewrites trigger-test receipts and revises no skill, so "
            "there is nothing for the gate to measure a delta on")
    state = FAILING if reasons else OK
    notes = [] if reasons else [f"one skill, skills/{slug}, {len(files)} files"]
    if receipts and not reasons:
        notes.append(
            f"{len(receipts)} trigger-test receipt file(s) under {RECEIPTS} are "
            "in this diff and were allowed. ADR-37's amendment says no file "
            "outside the skill's folder, and a receipt is pinned by sha to the "
            "SKILL.md text, so a revision that edits the skill has to rewrite "
            "one or ship a stale receipt. The ledger entry of 2026-09-30 asks "
            "the owner to confirm this reading")
    return Clause("scope", state, reasons, notes), slug


def pause_clause() -> Clause:
    path = ROOT / PAUSE_PATH
    if path.exists():
        why = " ".join(path.read_text().split()) or "no reason given in the file"
        return Clause("pause", FAILING, [
            f"{PAUSE_PATH} is in the tree, so automatic skill maintenance is "
            f"paused. The file says: {why}. Only the owner or the chair removes "
            "it (ADR-37, amended 2026-09-29, guardrail 2)"])
    return Clause("pause", OK, [], ["the kill switch is not set"])


def snapshot_doc() -> dict:
    path = ROOT / SNAPSHOT_PATH
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def live_claim_status(today: str) -> tuple[dict, str]:
    """(snapshot-shaped answer, how it was measured). Database first, file next."""
    conn = registrar.connect(writable=False)
    if conn is None:
        return snapshot_doc(), f"{SNAPSHOT_PATH}, written by the daily job"
    with conn:
        return triggers.claim_status(conn, today), "a live read of the corpus"


def provenance_clause(slug: str, today: str) -> Clause:
    if not slug:
        return Clause("provenance", UNKNOWN,
                      ["the scope clause found no single skill to read"])
    rows, problems = registrar.read_skills()
    row = next((r for r in rows if r.slug == slug), None)
    if row is None:
        return Clause("provenance", FAILING,
                      [f"skills/{slug} yields no registrable row: "
                       + "; ".join(problems or ["no SKILL.md"])])
    mine = [p for p in problems if f"skills/{slug}/" in p]
    if mine:
        return Clause("provenance", FAILING, mine)

    status, how = live_claim_status(today)
    stale = triggers.snapshot_problems(status, today, SNAPSHOT_MAX_AGE_DAYS)
    if stale:
        return Clause("provenance", FAILING, stale,
                      ["the clause is a question about the claim graph and "
                       "this run had no live answer to it"])
    reasons = triggers.claim_problems(row.claim_ids, status)
    state = FAILING if reasons else OK
    return Clause("provenance", state, reasons,
                  [f"{len(row.claim_ids)} cited claims, checked against {how}"])


def eval_clause(slug: str, base: str) -> Clause:
    if not slug:
        return Clause("eval", UNKNOWN,
                      ["the scope clause found no single skill to read"])
    doc = triggers.read_results(ROOT / "skills" / slug)
    if not doc:
        return Clause("eval", FAILING, [
            f"skills/{slug}/evals/results.json is missing or unreadable, so "
            "there is no measured delta and nothing may merge on its own. "
            "ADR-36 makes a skill with no eval draft rather than active"])

    reasons, notes = [], []
    body, sha = skill_eval.read_skill(slug)
    if doc.get("skill_md_sha256") != sha:
        reasons.append(
            "results.json was measured against a different SKILL.md than the "
            "one in this diff (its sha is "
            f"{str(doc.get('skill_md_sha256'))[:12]}, the file's is "
            f"{sha[:12]}), so the delta on the page does not describe this text. "
            "Re-run the eval in this pull request")

    history = triggers.history_entries(doc)
    version = skill_eval.skill_version(slug)
    entry = next((e for e in reversed(history)
                  if str(e.get("version") or "") == version), None)
    if entry is None:
        reasons.append(
            f"the results history carries no entry for version {version!r}, "
            "which is what the frontmatter says this text is. ADR-37 asks for a "
            "version history with the trigger per version")
    elif not str(entry.get("trigger") or "").strip():
        reasons.append(
            f"version {version} has a history entry with no trigger. The "
            "trigger is what the skill's page shows as the reason for the "
            "revision, so a revision that cannot say what asked for it does "
            "not merge itself")
    else:
        notes.append(f"version {version}, asked for by {entry['trigger']}")

    previous = history[-2] if len(history) > 1 else None
    if previous is None:
        base_doc = {}
        raw = file_at(base, f"skills/{slug}/evals/results.json")
        if raw:
            try:
                base_doc = json.loads(raw)
            except json.JSONDecodeError:
                base_doc = {}
        base_history = triggers.history_entries(base_doc)
        previous = base_history[-1] if base_history else None
        if previous is not None:
            notes.append("the previous result was read from "
                         f"{base}, because this file's history has one entry")
    reasons += skill_eval.gate_problems(doc, previous)
    if previous is None:
        notes.append("no previous result exists anywhere, so the delta was "
                     "judged on its own terms and not against an earlier one")
    state = FAILING if reasons else OK
    return Clause("eval", state, reasons, notes)


def ban_list_clause(slug: str, base: str) -> Clause:
    if not slug:
        return Clause("ban list", UNKNOWN,
                      ["the scope clause found no single skill to read"])
    path = f"skills/{slug}/SKILL.md"
    now = ban_list.check((ROOT / path).read_text())
    before_text = file_at(base, path)
    before = ban_list.check(before_text) if before_text else []

    def fingerprint(findings):
        counted = {}
        for f in findings:
            key = (f["entry"], f["found"])
            counted[key] = counted.get(key, 0) + 1
        return counted

    after, prior = fingerprint(now), fingerprint(before)
    added = []
    for key, count in sorted(after.items()):
        extra = count - prior.get(key, 0)
        if extra > 0:
            entry, found = key
            added.append(f"entry {entry} of docs/voice/ban-list.md, {extra} new "
                         f"occurrence of {found!r}")
    notes = [f"{len(before)} findings already in the file on {base}, "
             f"{len(now)} now. Pre-existing tells are the skill seat's backlog, "
             "not this revision's"]
    notes.append("six entries of the ban list are mechanical and were checked. "
                 "The rest need a reader, so this clause is a floor")
    return Clause("ban list", FAILING if added else OK, added, notes)


def command_clause(name: str, argv: list[str], meaning: str) -> Clause:
    proc = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode == 0:
        return Clause(name, OK, [], [meaning])
    tail = (proc.stdout + proc.stderr).strip().split("\n")[-12:]
    return Clause(name, FAILING,
                  [f"`{' '.join(argv)}` exited {proc.returncode}"],
                  ["  " + line for line in tail])


def trigger_test_clause() -> Clause:
    return command_clause(
        "trigger test",
        [sys.executable, "skills/_validation/trigger_test.py"],
        "every case in the library still fires, stays silent, and stays "
        "distinct from its neighbours")


def page_clause() -> Clause:
    try:
        import pytest        # noqa: F401
    except ImportError:
        return Clause("page", UNKNOWN, [
            "pytest is not installed here, so whether the skill's page still "
            "renders its receipts could not be measured. The workflow installs "
            "requirements-dev.txt"])
    return command_clause(
        "page", [sys.executable, "-m", "pytest",
                 "tests/test_skill_receipts.py", "-q"],
        "the page renders this skill's provenance and its dated result")


# --------------------------------------------------------------- the report

def run(base: str, today: str) -> tuple[list[Clause], str]:
    files, error = changed_files(base)
    scope, slug = scope_clause(files, error, base)
    clauses = [scope, pause_clause()]
    if scope.state == OK:
        clauses += [provenance_clause(slug, today), eval_clause(slug, base),
                    ban_list_clause(slug, base), trigger_test_clause(),
                    page_clause()]
    else:
        for name in ("provenance", "eval", "ban list", "trigger test", "page"):
            clauses.append(Clause(name, UNKNOWN, [
                "not measured, because the scope clause did not pass and the "
                "rest of the gate is about one identified skill"]))
    return clauses, slug


def verdict(clauses: list[Clause]) -> str:
    if any(c.state == FAILING for c in clauses):
        return "failed"
    if any(c.state == UNKNOWN for c in clauses):
        return "failed"
    return "passed"


def comment(clauses: list[Clause], slug: str, base: str, today: str) -> str:
    """The pull request comment. Reasons, never a bare label."""
    result = verdict(clauses)
    head = ("**The skill gate passed.**" if result == "passed"
            else "**The skill gate did not pass.**")
    lines = [
        f"{head} {today}, against `{base}`"
        + (f", skill `{slug}`" if slug else "") + ".",
        "",
        "ADR-37, amended 2026-09-29: a revision of an existing skill may merge "
        "with no human in the loop when every clause below passes. Anything "
        "else stays a draft pull request for the owner, with these reasons.",
        "",
        "| Clause | State | What it means |",
        "|---|---|---|",
    ]
    for clause in clauses:
        first = (clause.reasons + clause.notes + ["-"])[0]
        lines.append(f"| {clause.name} | {clause.state} | {first} |")
    lines.append("")
    for clause in clauses:
        if clause.state == OK and not clause.reasons:
            continue
        lines.append(f"**{clause.name}: {clause.state}**")
        lines.append("")
        for reason in clause.reasons or ["no reason recorded"]:
            lines.append(f"- {reason}")
        for note in clause.notes:
            lines.append(f"- note: {note}")
        lines.append("")
    if result != "passed":
        lines.append("Nothing was merged and nothing was reverted. The failing "
                     "clause is the work, and the gate re-runs on the next "
                     "push.")
    else:
        lines.append("Every clause a harness can measure is clear. What this "
                     "gate does not check is what ADR-37 left to people: "
                     "whether the trigger that asked for this revision was "
                     "itself right, which the skill seat is asked to state in "
                     "the pull request.")
    return "\n".join(lines)


def render(clauses: list[Clause], slug: str, base: str, today: str) -> str:
    lines = [f"skill gate, {today}, against {base}"
             + (f", skill {slug}" if slug else "")]
    for clause in clauses:
        lines.append(f"  {clause.state:8} {clause.name}")
        for reason in clause.reasons:
            lines.append(f"    - {reason}")
        for note in clause.notes:
            lines.append(f"    note: {note}")
    lines.append(f"verdict: {verdict(clauses)}")
    return "\n".join(lines)


# --------------------------------------------------------------- the smoke

def smoke() -> int:
    """The clause logic, against fixtures. No git, no database, no network."""
    today = "2026-09-30"
    checks = {}

    outside, _ = scope_clause(["skills/x/SKILL.md", "pipeline/llm.py"], "",
                              "origin/main")
    checks["a diff that touches the pipeline fails the scope clause"] = (
        outside.state == FAILING and any("outside skills/" in r
                                         for r in outside.reasons))

    two, _ = scope_clause(["skills/a/SKILL.md", "skills/b/SKILL.md"], "",
                          "origin/main")
    checks["two skills in one diff fail the scope clause"] = (
        two.state == FAILING and any("One revision, one skill" in r
                                     for r in two.reasons))

    receipts_only, _ = scope_clause(
        [RECEIPTS + "2026-09-30-lexical-2.1.json"], "", "origin/main")
    checks["a diff of nothing but receipts has no delta to judge"] = (
        receipts_only.state == FAILING)

    weird, _ = scope_clause(["skills/a/notes.txt"], "", "origin/main")
    checks["a file that is not SKILL.md, evals/ or reviews/ fails"] = (
        weird.state == FAILING)

    fresh = triggers.snapshot_problems(
        {"generated_at": today, "claim_id_ranges": [[1, 300]],
         "deprecated_claim_ids": [85]}, today, SNAPSHOT_MAX_AGE_DAYS)
    old = triggers.snapshot_problems(
        {"generated_at": "2026-09-01", "claim_id_ranges": [[1, 300]],
         "deprecated_claim_ids": []}, today, SNAPSHOT_MAX_AGE_DAYS)
    checks["a fresh snapshot is usable and a month-old one is not"] = (
        fresh == [] and len(old) == 1 and "past the 3" in old[0])

    status = {"generated_at": today, "claim_id_ranges": [[1, 300]],
              "deprecated_claim_ids": [85]}
    checks["a deprecated cited claim fails, a live one passes"] = (
        triggers.claim_problems([85], status) and
        triggers.claim_problems([86], status) == [])
    checks["a claim id the corpus does not have fails"] = bool(
        triggers.claim_problems([9001], status))

    before = "The harness is the scaffold. Keep it plain.\n"
    after_clean = before + "One more plain sentence.\n"
    after_slop = before + "This will unlock a very seamless tapestry.\n"
    checks["a clean revision adds no ban-list finding"] = (
        len(ban_list.check(after_clean)) == len(ban_list.check(before)))
    checks["a revision that adds slop is caught"] = (
        len(ban_list.check(after_slop)) > len(ban_list.check(before)))

    passed = [Clause("a", OK, []), Clause("b", OK, [])]
    unknown = [Clause("a", OK, []), Clause("b", UNKNOWN, ["no credential"])]
    checks["an unmeasured clause is never a pass"] = (
        verdict(passed) == "passed" and verdict(unknown) == "failed")

    body = comment(unknown, "harness-engineering", "origin/main", today)
    checks["the comment carries the reason, not just the label"] = (
        "no credential" in body and "did not pass" in body)

    for label, ok in checks.items():
        print(("ok:   " if ok else "FAIL: ") + label)
    return 0 if all(checks.values()) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", default=os.environ.get("GATE_BASE") or "origin/main")
    ap.add_argument("--comment", metavar="PATH",
                    help="write the pull request comment here")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args(argv)

    if args.smoke:
        return smoke()

    today = dt.date.today().isoformat()
    clauses, slug = run(args.base, today)
    result = verdict(clauses)
    if args.json:
        print(json.dumps({"verdict": result, "skill": slug, "base": args.base,
                          "date": today,
                          "clauses": [c.as_dict() for c in clauses]},
                         indent=2, sort_keys=True))
    else:
        print(render(clauses, slug, args.base, today))
    if args.comment:
        pathlib.Path(args.comment).write_text(
            comment(clauses, slug, args.base, today) + "\n")
    return 0 if result == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
