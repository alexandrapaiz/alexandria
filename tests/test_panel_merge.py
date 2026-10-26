"""ADR-13 slice 4: every gate between a unanimous verdict and a merged pull request.

    python3 -m pytest tests/test_panel_merge.py -q

Every test here runs with no network and no credential, which is the whole
reason `tools/panel_merge.py` splits its judgment from its three GitHub calls.
A merge executor whose decision could only be exercised by actually merging
something would be tested by merging things.

Four kinds of test.

**The scope gates.** ADR-12 says the panel may merge judgment and never
machinery, so the machinery case has to fail and the clean case has to pass.
The `prompts/` case is its own test because the executor is deliberately
stricter than the ADR that authorises it, and a subtraction nobody asserted
would be read as a bug by the next reader and quietly removed.

**The pin.** `panel_verdicts.target_sha` has existed since the table was
written and this is its first caller, so these are the tests that give it
meaning: three passes on other text, a panel of two, a fail among passes, and
a skill in the pull request that nobody reviewed.

**The token refusal.** The ambient `GH_TOKEN` every seat on this host holds can
merge. The test is that it is declined and named, because a fallback here would
turn the panel into a seat.

**The arithmetic.** `merge_allowed` is `verdict == "pass"` rather than
`verdict != "fail"`, and the difference is every unknown in this file.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import panel                    # noqa: E402
import panel_merge as pm        # noqa: E402

SHA_A = "a" * 64
SHA_B = "b" * 64
OPEN_PR = {"number": 1, "state": "open", "draft": False, "mergeable": True,
           "base": "main", "head_sha": "c" * 40, "title": "t"}
NO_TOKENS: dict = {}


def severities(findings, check):
    return [f["severity"] for f in findings if f["check"] == check]


def checks(result):
    return {f["check"] for f in result["findings"]}


# --------------------------------------------------------------- scope (ADR-12)

def test_a_pull_request_touching_pipeline_code_is_refused_as_machinery():
    """ADR-14 gives the machinery a human merge and no verdict overrides it."""
    findings = [f.as_dict() for f in
                pm.scope_findings(["skills/x/SKILL.md", "pipeline/weekly.py"])]
    assert severities(findings, "machinery") == ["fail"]


def test_sources_yaml_and_skills_are_the_whole_mergeable_surface():
    findings = [f.as_dict() for f in
                pm.scope_findings(["skills/x/SKILL.md", "sources.yaml",
                                   "skills/x/evals/evals.json"])]
    assert severities(findings, "scope") == ["note"]
    assert not [f for f in findings if f["severity"] == "fail"]


def test_a_prompts_path_is_refused_even_though_adr_12_admits_it():
    """The one place this file is stricter than the decision authorising it.

    ADR-12 wrote `prompts/*.md` on 2026-09-17, when that directory held one
    prompt. It holds twelve seat charters now, and HQ standard §21 reserves a
    change to a seat's own authority to the owner with no silence rule. An
    autonomous merge there would be the panel granting a right the owner never
    granted, so the overlap is a finding rather than a decision this tool
    makes.
    """
    findings = [f.as_dict() for f in
                pm.scope_findings(["prompts/engineer-agent.md"])]
    assert severities(findings, "charter-reserved") == ["fail"]
    assert "§21" in findings[0]["detail"]


def test_the_charter_refusal_is_reported_separately_from_machinery():
    """Two different asks of the owner must not arrive as one finding.

    A `docs/` path means the proposal is out of ADR-12's scope and wants a
    human merge. A `prompts/` path means two live rules disagree about who may
    merge it. Collapsing them would hide the second behind the first, which is
    what makes it invisible.
    """
    findings = [f.as_dict() for f in
                pm.scope_findings(["prompts/skill-agent.md", "docs/ideas.md"])]
    assert severities(findings, "charter-reserved") == ["fail"]
    assert severities(findings, "machinery") == ["fail"]


# ------------------------------------------------------------------- the target

def test_only_a_changed_skill_md_is_a_proposal():
    """An eval suite or a review note proposes no new text to judge."""
    assert pm.skill_targets(["skills/x/evals/evals.json",
                             "skills/x/reviews/README.md"]) == []
    assert pm.skill_targets(["skills/x/SKILL.md",
                             "skills/y/SKILL.md"]) == ["skills/x", "skills/y"]


def test_the_validation_directory_is_not_a_skill_target():
    """`skills/_validation/` is harness, and one file decides that for everybody.

    The set is read from `skill_registrar.NOT_A_SKILL` rather than restated, so
    the test asserts the read: a hypothetical `skills/_validation/SKILL.md`
    must not become a merge candidate, and a directory added to that set
    tomorrow must not either.
    """
    import skill_registrar as registrar
    assert registrar.NOT_A_SKILL
    for slug in registrar.NOT_A_SKILL:
        assert pm.skill_targets([f"skills/{slug}/SKILL.md"]) == []
    assert pm.skill_targets(["skills/_validation/trigger_test.py"]) == []


def test_a_pull_request_with_no_skill_md_is_not_the_panels_to_merge():
    findings = [f.as_dict() for f in pm.pin_findings({}, [])]
    assert severities(findings, "proposal") == ["unknown"]


# --------------------------------------------------------------------- the pin

def unanimous_rows(target, sha):
    return [{"target": target, "reviewer": r, "verdict": "pass",
             "target_sha": sha} for r in pm.REVIEWERS]


def test_three_passes_on_this_text_is_the_gate_opening():
    """The only test in this file that opens the gate, and it has to exist.

    A reviewer that fails everything is as useless as one that passes
    everything, and the same is true of a merge executor. This is the evidence
    that the refusals above are gates rather than a wall.
    """
    findings = [f.as_dict() for f in
                pm.pin_findings({"skills/x": SHA_A},
                                unanimous_rows("skills/x", SHA_A))]
    assert severities(findings, "unanimous") == ["note"]


def test_three_passes_on_other_text_is_not_three_passes_on_this_one():
    """What `panel_verdicts.target_sha` was added for, exercised for the first time.

    Without this the panel could pass a proposal, the author could push one
    more commit, and the merge would ship the commit nobody reviewed.
    """
    findings = [f.as_dict() for f in
                pm.pin_findings({"skills/x": SHA_B},
                                unanimous_rows("skills/x", SHA_A))]
    assert severities(findings, "stale-pass") == ["unknown"]
    assert SHA_B[:12] in findings[0]["detail"]


def test_a_panel_of_two_that_agreed_is_not_unanimity():
    rows = [r for r in unanimous_rows("skills/x", SHA_A)
            if r["reviewer"] != "adversary"]
    findings = [f.as_dict() for f in pm.pin_findings({"skills/x": SHA_A}, rows)]
    assert severities(findings, "panel-size") == ["unknown"]
    assert "adversary" in findings[0]["detail"]


def test_one_fail_among_two_passes_leaves_the_pull_request_open():
    rows = unanimous_rows("skills/x", SHA_A)
    rows[1] = dict(rows[1], verdict="fail")
    findings = [f.as_dict() for f in pm.pin_findings({"skills/x": SHA_A}, rows)]
    assert "fail" in severities(findings, "unanimous")


def test_an_unknown_is_not_a_pass():
    rows = unanimous_rows("skills/x", SHA_A)
    rows[0] = dict(rows[0], verdict="unknown")
    findings = [f.as_dict() for f in pm.pin_findings({"skills/x": SHA_A}, rows)]
    assert "unknown" in severities(findings, "unanimous")


def test_a_skill_nobody_reviewed_blocks_a_pull_request_whose_other_skill_passed():
    """Every skill in the proposal has to clear, not the best one.

    #535 is the live case: two SKILL.md files on one branch. A gate that read
    the first and stopped would merge the second unreviewed.
    """
    rows = unanimous_rows("skills/x", SHA_A)
    findings = [f.as_dict() for f in
                pm.pin_findings({"skills/x": SHA_A, "skills/y": SHA_B}, rows)]
    assert severities(findings, "verdict-exists") == ["unknown"]
    assert "skills/y" in [f["detail"].split(":")[0] for f in findings
                          if f["check"] == "verdict-exists"]


def test_the_reviewers_this_file_counts_are_the_reviewers_the_schema_allows():
    """Three names in two places, and a drift between them would be silent.

    `panel_verdicts.reviewer` has a check constraint naming the three. If this
    file counted a fourth, or spelled one differently, `panel-size` would wait
    forever for a reviewer that cannot file a row.
    """
    schema = (ROOT / "db" / "schema.sql").read_text()
    clause = schema.split("check (reviewer in (")[1].split("))")[0]
    assert set(pm.REVIEWERS) == {
        part.strip().strip("'") for part in clause.split(",")}
    assert len(pm.REVIEWERS) == pm.PANEL_SIZE


def test_the_panel_size_is_written_out_rather_than_counted():
    """`panel_consensus` writes the 3 for this reason and so does this file."""
    schema = (ROOT / "db" / "schema.sql").read_text()
    assert "= 3" in schema.split("create or replace view panel_consensus")[1]
    assert pm.PANEL_SIZE == 3


# ------------------------------------------------------------------- the token

def test_the_merge_token_is_the_only_credential_that_may_merge():
    findings = [f.as_dict() for f in
                pm.token_findings({pm.MERGE_TOKEN: "x"})]
    assert severities(findings, "merge-token") == ["note"]


def test_a_seats_own_github_token_is_declined_and_named():
    """The failure this gate exists for: a seat merging from inside a review tool."""
    findings = [f.as_dict() for f in pm.token_findings({"GH_TOKEN": "x"})]
    assert severities(findings, "merge-token") == ["unknown"]
    assert "GH_TOKEN" in findings[0]["detail"]
    assert "declined" in findings[0]["detail"]


def test_do_merge_refuses_without_the_panels_token(monkeypatch):
    """Not only the finding. The call itself refuses, with nothing mocked."""
    for name in (pm.MERGE_TOKEN,) + pm.AMBIENT_TOKENS:
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(RuntimeError, match=pm.MERGE_TOKEN):
        pm.do_merge(1, "c" * 40)


def test_do_merge_sends_the_sha_it_judged(monkeypatch):
    """GitHub refuses the call if the branch moved, which is the pin's other half."""
    monkeypatch.setenv(pm.MERGE_TOKEN, "x")
    seen = {}

    def fake(path, token=None, method="GET", body=None):
        seen.update({"path": path, "token": token, "method": method,
                     "body": body})
        return {"merged": True}

    monkeypatch.setattr(pm, "api", fake)
    pm.do_merge(7, "c" * 40)
    assert seen["body"]["sha"] == "c" * 40
    assert seen["method"] == "PUT"
    assert seen["token"] == "x"


# -------------------------------------------------------------- the arithmetic

def test_the_state_of_a_pull_request_github_has_not_computed_is_unknown():
    """Null `mergeable` means "ask again", never "go" and never "no"."""
    findings = [f.as_dict() for f in
                pm.state_findings(dict(OPEN_PR, mergeable=None))]
    assert severities(findings, "mergeable") == ["unknown"]


def test_a_draft_is_refused():
    findings = [f.as_dict() for f in pm.state_findings(dict(OPEN_PR, draft=True))]
    assert severities(findings, "pr-open") == ["fail"]


def test_merge_is_allowed_only_when_every_gate_returned_a_pass():
    result = pm.judge(OPEN_PR, ["skills/x/SKILL.md"], {"skills/x": SHA_A},
                      unanimous_rows("skills/x", SHA_A),
                      env={pm.MERGE_TOKEN: "x"})
    assert result["verdict"] == "pass"
    assert result["merge_allowed"] is True


def test_an_unknown_anywhere_refuses_the_merge_rather_than_only_the_verdict():
    """`merge_allowed` is `verdict == "pass"`, which is the point of this test.

    Written as `verdict != "fail"` it would merge a proposal two reviewers had
    judged, which is the panel-of-two failure `panel_consensus` was written to
    make impossible.
    """
    rows = [r for r in unanimous_rows("skills/x", SHA_A)
            if r["reviewer"] != "validator"]
    result = pm.judge(OPEN_PR, ["skills/x/SKILL.md"], {"skills/x": SHA_A},
                      rows, env={pm.MERGE_TOKEN: "x"})
    assert result["verdict"] == "unknown"
    assert result["merge_allowed"] is False


def test_the_verdict_vocabulary_is_the_panels_rather_than_a_second_copy():
    """One scale, so a consensus cannot be computed out of two of them.

    `tools/panel.py` holds the three severities and the arithmetic for exactly
    this reason, and a merge executor with its own words would be the drift
    that file was split out to prevent.
    """
    assert pm.Finding is panel.Finding
    assert pm.verdict_of is panel.verdict_of


def test_the_status_description_fits_githubs_cap_and_names_the_first_blocker():
    result = pm.judge(OPEN_PR, ["pipeline/weekly.py"], {}, [], env=NO_TOKENS)
    state, desc = pm.status_of(result)
    assert state == "failure"
    assert len(desc) <= 140
    assert "machinery" in desc


def test_a_clean_pass_files_a_green_status():
    result = pm.judge(OPEN_PR, ["skills/x/SKILL.md"], {"skills/x": SHA_A},
                      unanimous_rows("skills/x", SHA_A),
                      env={pm.MERGE_TOKEN: "x"})
    state, desc = pm.status_of(result)
    assert state == "success"
    assert str(pm.PANEL_SIZE) in desc


# --------------------------------------------- the proposal's own text (slice 4)

def file_rows(verdict, reviewer="validator", detail="d"):
    return [{"target": "skills/x", "reviewer": reviewer, "verdict": verdict,
             "target_sha": SHA_A, "detail": detail}]


def test_a_file_half_pass_counts_only_from_the_reviewer_whose_halves_agree():
    """The validator's suite asserts its two halves return one verdict.

    So a pass from its file half is a pass. The provenance reviewer's file half
    runs a subset of its checks and says so in its own build note, which makes
    the same word mean something weaker, and `proposal_findings` has to keep
    the two apart or the panel's trail says more than the panel measured.
    """
    whole = [f.as_dict() for f in proposal_of(file_rows("pass", "validator"))]
    partial = [f.as_dict() for f in
               proposal_of(file_rows("pass", "provenance"))]
    assert "note" in severities(whole, "proposal-review")
    assert "unknown" in severities(partial, "proposal-review")


def proposal_of(rows):
    """`proposal_findings` without the adversary's standing unknown."""
    return [f for f in pm.proposal_findings(rows)
            if "no file half by design" not in f.detail]


def test_a_file_half_fail_is_a_fail_from_any_reviewer():
    """A check that can fail from files alone is a fact about the file."""
    for reviewer in ("provenance", "validator"):
        findings = [f.as_dict() for f in
                    proposal_of(file_rows("fail", reviewer))]
        assert severities(findings, "proposal-review") == ["fail"]


def test_the_adversary_is_always_an_unknown_from_a_checkout():
    """Its build note argues it has no file half, so nothing can fake one.

    Nothing the adversary decides is in the SKILL.md, because a disagreement is
    a row somebody wrote after the skill was merged. A reviewer silently
    omitted here would let a panel of two read as unanimous, which is the one
    thing `panel_consensus` was written to prevent.
    """
    findings = [f.as_dict() for f in pm.proposal_findings(file_rows("pass"))]
    adversary = [f for f in findings if "adversary" in f["detail"]]
    assert [f["severity"] for f in adversary] == ["unknown"]


def test_a_file_half_review_never_opens_the_merge_gate():
    """Even three file-half passes do not merge, and that is deliberate.

    `panel_verdicts` is the audit trail ADR-13 replaces an approval with. A row
    filed from half a reviewer would make the trail claim a duty nobody ran, so
    the file halves inform and the database rows decide.
    """
    rows = [dict(r, reviewer=who) for who in pm.REVIEWERS
            for r in file_rows("pass")]
    result = pm.judge(OPEN_PR, ["skills/x/SKILL.md"], {"skills/x": SHA_A},
                      [], env={pm.MERGE_TOKEN: "x"}, proposal=rows)
    assert result["merge_allowed"] is False


def test_the_reviewers_run_against_a_directory_rather_than_the_checkout():
    """`review_proposal` has to point the reviewers at the branch's own tree.

    This runs the two credential-free halves against this repository's real
    skills, which is the same call `--review` makes against a materialized pull
    request. A reviewer that ignored `skills_dir` would review `main` here and
    pass this test only by accident, so the assertion is the target it named.
    """
    rows = pm.review_proposal(ROOT / "skills", ["skills/agent-memory-selection"])
    assert {r["reviewer"] for r in rows} == {"provenance", "validator"}
    assert {r["target"] for r in rows} == {"skills/agent-memory-selection"}
    assert all(len(r["target_sha"]) == 64 for r in rows)


def test_the_status_write_is_refused_by_the_seats_token_with_the_grant_named(monkeypatch):
    """A 403 here is a permission, not an outage, so it must not read as one.

    Probed 2026-10-26: reads of `/commits/{sha}/statuses` return 200 and writes
    to `/statuses/{sha}` return 403 for the token every seat holds. A traceback
    would send the next run to look for a broken endpoint.
    """
    import urllib.error

    def forbidden(path, token=None, method="GET", body=None):
        raise urllib.error.HTTPError(path, 403, "Forbidden", {}, None)

    monkeypatch.setattr(pm, "api", forbidden)
    out = pm.post_status("c" * 40, pm.judge(OPEN_PR, ["skills/x/SKILL.md"],
                                            {}, [], env=NO_TOKENS))
    assert out["refused"] == 403
    assert "Commit statuses" in out["needs"]


def test_the_comment_carries_every_blocking_finding_and_claims_nothing_more():
    """ADR-13's "verdicts attached" is this, and it must not read as a gate.

    The panel holds no required check in this repository, so a comment that
    looked like one would change how a human merges without any decision
    saying so.
    """
    result = pm.judge(OPEN_PR, ["pipeline/weekly.py"], {}, [], env=NO_TOKENS)
    body = pm.comment_body(result)
    assert "advisory" in body
    assert "no required check" in body
    for f in result["findings"]:
        if f["severity"] != "note":
            assert f["check"] in body
