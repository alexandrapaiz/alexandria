#!/usr/bin/env python3
"""ADR-13 slice 4: the gates between a unanimous verdict and a merged pull request.

    python3 tools/panel_merge.py                  # every open PR that proposes a skill
    python3 tools/panel_merge.py --pr 535         # one of them, with its blockers named
    python3 tools/panel_merge.py --pr 535 --json  # the same thing for a machine
    python3 tools/panel_merge.py --pr 535 --status  # file the verdict as a commit status
    python3 tools/panel_merge.py --pr 535 --merge   # merge it, if every gate passes

Three reviewers have existed since 2026-10-03 and `panel_consensus` has
computed unanimity since the table was written. `docs/product/reviewer-panel.md`
called slice 3 "the merge" and said one sentence about it: blocked on the owner
minting a PR-merge-scoped token. This file is what that sentence was hiding,
and the token turns out to be the fourth of four blockers rather than the only
one.

**The first blocker is that nothing has ever filed a verdict about a pull
request.** All three reviewers read skills from `main`, over the GitHub API, in
step 2 of `pipeline/skill_revision.py`. A verdict therefore describes text that
is already merged, so `panel_consensus` can be unanimous only about a proposal
that no longer needs merging. ADR-13's sentence is "unanimous pass merges the
PR"; the panel as built cannot name a PR.

**The second is that ADR-12's whitelist excludes every proposal the panel will
ever see, and this was measured rather than reasoned.** The whitelist is
`skills/`, `prompts/*.md` and `sources.yaml`, and never machinery. Of the 21
pull requests the skill seat has opened in this repository's life, **21 carry at
least one path outside it** and none is whitelist-clean. The cause is not
carelessness: `prompts/skill-agent.md` requires the seat to append its ideas to
`docs/ideas.md` and its repeats to `docs/agents/incidents.md` on the same
branch, so the org's own charter contract guarantees that every skill proposal
is out of scope for the gate meant to merge it. A whitelist that refuses 21 of
21 inputs is not a safety margin, it is an unreachable gate, and the fix is the
owner's: either the skill seat's ledger append moves to its own pull request, or
ADR-12's whitelist admits the two append-only registers by name.

**The third is `prompts/*.md`, which this file refuses on purpose.** ADR-12
wrote that line on 2026-09-17, when `prompts/` held the weekly agent's own
prompt. It holds twelve seat charters today, and HQ standard §21 reserves a
change to a seat's own authority to the owner with no silence rule attached. So
an autonomous merge of `prompts/engineer-agent.md` would be the panel granting
a seat a right the owner never granted. This file narrows its own authority
below ADR-12's text rather than above it, and files the disagreement as a
finding for the owner instead of resolving it quietly.

**The fourth is the token, and this file will not accept a substitute for it.**
The merge call reads `PANEL_MERGE_TOKEN` and nothing else. Every agent seat on
this host already holds `GH_TOKEN`, which can merge, so a merge executor that
fell back to the ambient credential would turn "the panel merged it" into "a
seat merged it from inside a review tool", which is the one thing every charter
in this repository forbids. The refusal is a test rather than a comment.

The judgment in this file is pure and the GitHub calls are three functions at
the bottom, for the reason `tools/panel_validator.py` states about its own
halves: the part that decides has to be runnable with no credential at all.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import panel                                                 # noqa: E402
from panel import Finding, verdict_of                         # noqa: E402

REPO = "alexandrapaiz/alexandria"
API = "https://api.github.com"

# ADR-12's whitelist, minus `prompts/*.md`. The docstring argues the subtraction;
# `CHARTER_RESERVED` below is what the subtracted prefix becomes.
MERGEABLE_PREFIXES = ("skills/",)
MERGEABLE_PATHS = ("sources.yaml",)
CHARTER_RESERVED = "prompts/"

# ADR-13 fixes the panel at three, and `panel_consensus` writes the 3 out rather
# than counting whoever filed. This file does the same, for the same reason: a
# panel of one that passed must never read as unanimous.
PANEL_SIZE = 3
REVIEWERS = ("provenance", "adversary", "validator")

MERGE_TOKEN = "PANEL_MERGE_TOKEN"
AMBIENT_TOKENS = ("GH_TOKEN", "GITHUB_TOKEN")

STATUS_CONTEXT = "panel/consensus"


# ------------------------------------------------------------------ the gates

def scope_findings(paths: list[str]) -> list[Finding]:
    """ADR-12's scope, as two findings that mean different things.

    A machinery path is a `fail`: ADR-14 gives the machinery a human merge and
    no verdict can override that. A `prompts/` path is also a `fail`, and it is
    reported under its own check name so the owner can see the one case where
    this file is deliberately stricter than the ADR that authorises it.
    """
    findings = []
    charter = sorted(p for p in paths if p.startswith(CHARTER_RESERVED))
    outside = sorted(p for p in paths
                     if not p.startswith(CHARTER_RESERVED)
                     and not p.startswith(MERGEABLE_PREFIXES)
                     and p not in MERGEABLE_PATHS)
    if charter:
        findings.append(Finding(
            "charter-reserved", "fail",
            f"{len(charter)} path(s) under {CHARTER_RESERVED} "
            f"({', '.join(charter[:3])}): ADR-12's whitelist admits "
            "`prompts/*.md` and HQ standard §21 reserves a change to a seat's "
            "own authority to the owner. This file refuses the overlap rather "
            "than deciding it."))
    if outside:
        findings.append(Finding(
            "machinery", "fail",
            f"{len(outside)} path(s) outside ADR-12's whitelist "
            f"({', '.join(outside[:3])}{', ...' if len(outside) > 3 else ''}): "
            "autonomy applies to what the system knows, never to what the "
            "system is, so this pull request is ADR-14's human merge."))
    if not findings:
        findings.append(Finding(
            "scope", "note",
            f"all {len(paths)} changed path(s) are inside ADR-12's whitelist."))
    return findings


def skill_targets(paths: list[str]) -> list[str]:
    """`skills/<slug>` for every slug whose SKILL.md this pull request changes.

    The target of a verdict is the skill rather than the file, because
    `panel_verdicts.target` is `skills/<slug>` and `promotions.path` is the same
    string. A PR that edits only a skill's eval suite proposes no new text to
    review, so it has no target here and `pin_findings` says so.
    """
    out = []
    for path in paths:
        parts = path.split("/")
        if len(parts) >= 3 and parts[0] == "skills" and parts[-1] == "SKILL.md":
            target = f"skills/{parts[1]}"
            if target not in out:
                out.append(target)
    return sorted(out)


def pin_findings(heads: dict[str, str], rows: list[dict]) -> list[Finding]:
    """Unanimity, pinned to the text this pull request actually proposes.

    `heads` maps each target to the sha256 of its SKILL.md at the PR's head
    sha. `rows` are `panel_latest` rows. Every check here is about the pin:
    three passes on some other text are not three passes on this one, which is
    what `panel_verdicts.target_sha` was added for and what this function is
    the first caller of.
    """
    if not heads:
        return [Finding(
            "proposal", "unknown",
            "this pull request changes no skills/<slug>/SKILL.md, so it "
            "proposes no text for the panel to judge. A merge here is "
            "ADR-14's, not ADR-13's.")]

    findings = []
    for target, head_sha in sorted(heads.items()):
        mine = [r for r in rows if r["target"] == target]
        on_text = [r for r in mine if r["target_sha"] == head_sha]
        if not mine:
            findings.append(Finding(
                "verdict-exists", "unknown",
                f"{target}: no reviewer has ever filed a verdict about it. "
                "The panel reads skills from `main` in step 2 of "
                "pipeline/skill_revision.py, so a proposal on a branch is "
                "reviewed by nobody."))
            continue
        if not on_text:
            seen = sorted({r["target_sha"][:12] for r in mine})
            findings.append(Finding(
                "stale-pass", "unknown",
                f"{target}: {len(mine)} verdict(s) exist and every one "
                f"describes other text ({', '.join(seen)}), not this pull "
                f"request's {head_sha[:12]}. A pass earned before an edit is "
                "not a pass on the edit."))
            continue

        filed = {r["reviewer"] for r in on_text}
        missing = [r for r in REVIEWERS if r not in filed]
        fails = sorted(r["reviewer"] for r in on_text if r["verdict"] == "fail")
        unknowns = sorted(r["reviewer"] for r in on_text
                          if r["verdict"] == "unknown")
        passes = sum(1 for r in on_text if r["verdict"] == "pass")

        if fails:
            findings.append(Finding(
                "unanimous", "fail",
                f"{target}: {', '.join(fails)} failed this text. ADR-13 "
                "leaves the pull request open with the verdicts attached."))
        if missing:
            findings.append(Finding(
                "panel-size", "unknown",
                f"{target}: {len(filed)} of {PANEL_SIZE} reviewers have "
                f"judged {head_sha[:12]}; {', '.join(missing)} has not. A "
                "panel of two that agreed is not unanimity."))
        if unknowns:
            findings.append(Finding(
                "unanimous", "unknown",
                f"{target}: {', '.join(unknowns)} could not measure this "
                "text, and an unknown is not a pass."))
        if not fails and not missing and not unknowns and passes == PANEL_SIZE:
            findings.append(Finding(
                "unanimous", "note",
                f"{target}: {PANEL_SIZE} passes on {head_sha[:12]}, one text, "
                "which is ADR-13's gate as arithmetic."))
    return findings


def state_findings(pr: dict) -> list[Finding]:
    """The pull request has to be open, unlocked and actually mergeable.

    `mergeable` is null while GitHub computes it, and null is an `unknown`
    rather than a `fail`: a merge executor that read "not yet computed" as "do
    not merge" would refuse every pull request opened in the last few seconds,
    and one that read it as "go" would merge a conflict.
    """
    findings = []
    if pr.get("state") != "open":
        findings.append(Finding("pr-open", "fail",
                                f"#{pr['number']} is {pr.get('state')}."))
    if pr.get("draft"):
        findings.append(Finding(
            "pr-open", "fail",
            f"#{pr['number']} is a draft, which its author has not finished."))
    mergeable = pr.get("mergeable")
    if mergeable is False:
        findings.append(Finding("mergeable", "fail",
                                f"#{pr['number']} does not merge cleanly into "
                                f"{pr.get('base', '?')}."))
    elif mergeable is None:
        findings.append(Finding(
            "mergeable", "unknown",
            f"GitHub has not finished computing whether #{pr['number']} "
            "merges cleanly. Ask again rather than guessing."))
    return findings


def token_findings(env: dict | None = None) -> list[Finding]:
    """The panel's own token, and the refusal of every seat's.

    This is the gate that keeps "the panel merged it" from quietly meaning "a
    seat merged it from inside a review tool". The ambient credential is named
    in the finding because a reader whose run has `GH_TOKEN` set needs to know
    that it was seen and declined rather than missed.
    """
    env = os.environ if env is None else env
    if (env.get(MERGE_TOKEN) or "").strip():
        return [Finding("merge-token", "note",
                        f"{MERGE_TOKEN} is present in this environment.")]
    ambient = [n for n in AMBIENT_TOKENS if (env.get(n) or "").strip()]
    detail = (f"{MERGE_TOKEN} is not set, so no merge was attempted. ADR-13's "
              "merge runs on a token minted for the panel, scoped to "
              "`contents: write` and `pull_requests: write` on this repository "
              "and held by nothing else.")
    if ambient:
        detail += (f" {', '.join(ambient)} is set here and can merge; it was "
                   "declined, because a seat's credential merging a skill "
                   "proposal is a seat merging, not a panel.")
    return [Finding("merge-token", "unknown", detail)]


def judge(pr: dict, paths: list[str], heads: dict[str, str],
          rows: list[dict], env: dict | None = None) -> dict:
    """One verdict over all four gates, in `tools/panel.py`'s vocabulary.

    `merge_allowed` is deliberately not `verdict != "fail"`. It is
    `verdict == "pass"`, which means every gate returned a pass or a note:
    `fail` beats `unknown` beats `pass` is the panel's own arithmetic, and an
    unknown blocks a merge here for exactly the reason it blocks a verdict
    there.
    """
    findings = (state_findings(pr) + scope_findings(paths)
                + pin_findings(heads, rows) + token_findings(env))
    verdict = verdict_of(findings)
    return {
        "pr": pr.get("number"),
        "head_sha": pr.get("head_sha"),
        "targets": sorted(heads),
        "verdict": verdict,
        "merge_allowed": verdict == "pass",
        "findings": [f.as_dict() for f in findings],
    }


def render(result: dict) -> str:
    lines = [f"#{result['pr']}  {result['verdict']}"]
    for f in result["findings"]:
        if f["severity"] == "note":
            continue
        lines.append(f"    {f['severity']}: {f['check']}: {f['detail']}")
    notes = [f["detail"] for f in result["findings"] if f["severity"] == "note"]
    for note in notes:
        lines.append(f"    measured: {note}")
    lines.append("    merge: " + ("allowed" if result["merge_allowed"]
                                  else "refused"))
    return "\n".join(lines)


def status_of(result: dict) -> tuple[str, str]:
    """The commit status a pull request can see, and its one-line description.

    GitHub caps a status description at 140 characters, so the first blocking
    finding is named rather than all of them, with the tool that prints the
    rest.
    """
    blocking = [f for f in result["findings"] if f["severity"] != "note"]
    state = "success" if result["merge_allowed"] else "failure"
    if result["merge_allowed"]:
        desc = f"{PANEL_SIZE} passes on one text, every ADR-12 gate clear"
    else:
        first = blocking[0]
        desc = f"{first['severity']}: {first['check']}"
        if len(blocking) > 1:
            desc += f" (+{len(blocking) - 1} more)"
        desc += " - python3 tools/panel_merge.py --pr N"
    return state, desc[:140]


# ------------------------------------------------------------------- the i/o

def api(path: str, token: str | None = None, method: str = "GET",
        body: dict | None = None) -> dict | list:
    """One GitHub call. Reads may use the ambient token; the merge may not.

    Separated from every function above so that the whole of this file's
    judgment is testable with no network and no credential, which is the
    property `tests/test_panel_merge.py` rests on.
    """
    token = token or next((os.environ[n] for n in AMBIENT_TOKENS
                           if (os.environ.get(n) or "").strip()), None)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{API}{path}", data=data, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
    return json.loads(raw) if raw else {}


def read_pr(number: int) -> tuple[dict, list[str], dict[str, str]]:
    """The pull request, its changed paths, and the sha256 of each proposed SKILL.md.

    The sha256 is computed from the bytes at the head sha rather than taken
    from the API's `sha` field, because the API gives git's blob sha and
    `panel_verdicts.target_sha` is sha256 of the text, the way
    `tools/skill_registrar.py` computes it.
    """
    raw = api(f"/repos/{REPO}/pulls/{number}")
    pr = {
        "number": raw["number"],
        "state": raw["state"],
        "draft": bool(raw.get("draft")),
        "mergeable": raw.get("mergeable"),
        "base": raw["base"]["ref"],
        "head_ref": raw["head"]["ref"],
        "head_sha": raw["head"]["sha"],
        "title": raw.get("title", ""),
    }
    paths, page = [], 1
    while True:
        batch = api(f"/repos/{REPO}/pulls/{number}/files?per_page=100&page={page}")
        if not batch:
            break
        paths += [f["filename"] for f in batch]
        if len(batch) < 100:
            break
        page += 1

    heads = {}
    for target in skill_targets(paths):
        slug = target.split("/", 1)[1]
        blob = api(f"/repos/{REPO}/contents/skills/{slug}/SKILL.md"
                   f"?ref={pr['head_sha']}")
        text = base64.b64decode(blob["content"]).decode()
        heads[target] = hashlib.sha256(text.encode()).hexdigest()
    return pr, paths, heads


def read_verdicts(targets: list[str]) -> list[dict]:
    """`panel_latest` for these targets, or an empty list and a printed reason.

    No agent seat holds a database credential, so the ordinary answer here is
    the empty list. That is not a silent zero: `pin_findings` turns it into
    `verdict-exists` unknown, which is the honest statement that nobody has
    judged the proposal.
    """
    if not targets:
        return []
    conn = panel.connect(writable=False,
                         cannot="no verdict could be read, so unanimity "
                                "could not be checked")
    if conn is None:
        return []
    try:
        rows = conn.execute(
            "select target, reviewer, verdict, target_sha "
            "from panel_latest where target = any(%s)", (targets,)).fetchall()
    finally:
        conn.close()
    return [{"target": r[0], "reviewer": r[1], "verdict": r[2],
             "target_sha": r[3]} for r in rows]


def open_skill_prs() -> list[int]:
    """Open pull requests that change a SKILL.md, newest first."""
    out = []
    for raw in api(f"/repos/{REPO}/pulls?state=open&per_page=100"):
        files = api(f"/repos/{REPO}/pulls/{raw['number']}/files?per_page=100")
        if skill_targets([f["filename"] for f in files]):
            out.append(raw["number"])
    return out


def post_status(head_sha: str, result: dict) -> dict:
    state, desc = status_of(result)
    return api(f"/repos/{REPO}/statuses/{head_sha}", method="POST", body={
        "state": state, "context": STATUS_CONTEXT, "description": desc,
    })


def do_merge(number: int, head_sha: str) -> dict:
    """The merge, on the panel's own token and no other.

    `sha` is sent so GitHub refuses the call if the branch moved between the
    verdict and the merge. Without it a proposal could earn three passes and
    then be pushed to, and this call would ship the push, which is the failure
    `target_sha` exists to prevent one level up.
    """
    token = (os.environ.get(MERGE_TOKEN) or "").strip()
    if not token:
        raise RuntimeError(f"{MERGE_TOKEN} is not set; refusing to merge.")
    return api(f"/repos/{REPO}/pulls/{number}/merge", token=token,
               method="PUT", body={
                   "sha": head_sha,
                   "merge_method": "squash",
                   "commit_title": f"Panel: unanimous pass merges #{number}",
               })


# ------------------------------------------------------------------- the cli

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pr", type=int, default=0,
                    help="one pull request number; default is every open one "
                         "that proposes a skill")
    ap.add_argument("--merge", action="store_true",
                    help=f"merge when every gate passes. Needs {MERGE_TOKEN}.")
    ap.add_argument("--status", action="store_true",
                    help=f"file the verdict as the {STATUS_CONTEXT} commit "
                         "status on the pull request's head")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    numbers = [args.pr] if args.pr else open_skill_prs()
    if not numbers:
        print("no open pull request proposes a skill, so the panel has "
              "nothing to merge.")
        return 0

    results = []
    for number in numbers:
        pr, paths, heads = read_pr(number)
        result = judge(pr, paths, heads, read_verdicts(sorted(heads)))
        result["title"] = pr["title"]
        if args.status:
            post_status(pr["head_sha"], result)
            result["status_filed"] = STATUS_CONTEXT
        if args.merge and result["merge_allowed"]:
            do_merge(number, pr["head_sha"])
            result["merged"] = True
        results.append(result)

    if args.json:
        print(json.dumps({"results": results}, indent=2))
    else:
        for result in results:
            print(render(result))
            print()
        allowed = sum(1 for r in results if r["merge_allowed"])
        print(f"{len(results)} pull request(s) judged, {allowed} mergeable "
              "by the panel")

    if any(r["verdict"] == "fail" for r in results):
        return 1
    if any(r["verdict"] == "unknown" for r in results):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
