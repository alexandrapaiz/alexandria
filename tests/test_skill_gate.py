"""ADR-37's gate: what it refuses, and the two clauses that are deltas.

The gate is the one thing in this repository that can put a change on main
without the owner reading it, so the tests that matter are the refusals. Every
clause is exercised both ways here, against fixtures, with no network and no
database.

Two of the clauses are deltas against the base branch rather than absolutes, and
that decision is itself under test below, because it is the kind of decision that
looks like a weakening until you have the measurement. On 2026-09-30 the trigger
test exits 1 on main with three standing failures, and all six skills carry
mechanical ban-list findings. Absolutes would mean no revision can ever merge,
which is the loop switched off by a detail rather than by a decision.
"""

from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import ban_list                       # noqa: E402
import skill_gate as gate             # noqa: E402
import skill_triggers as triggers     # noqa: E402

TODAY = "2026-09-30"


# --------------------------------------------------------------- scope

def test_a_diff_that_touches_code_is_not_a_revision_the_loop_may_merge():
    clause, slug = gate.scope_clause(
        ["skills/x/SKILL.md", "pipeline/llm.py"], "", "origin/main")
    assert clause.state == gate.FAILING
    assert any("outside skills/" in r for r in clause.reasons)


def test_a_diff_that_touches_a_workflow_is_refused():
    clause, _ = gate.scope_clause(
        ["skills/x/SKILL.md", ".github/workflows/agent-skill.yml"], "",
        "origin/main")
    assert clause.state == gate.FAILING


def test_two_skills_in_one_diff_are_refused():
    clause, slug = gate.scope_clause(
        ["skills/a/SKILL.md", "skills/b/SKILL.md"], "", "origin/main")
    assert clause.state == gate.FAILING and slug == ""


def test_a_file_that_is_not_the_skill_its_evals_or_its_reviews_is_refused():
    clause, _ = gate.scope_clause(["skills/a/notes.txt"], "", "origin/main")
    assert clause.state == gate.FAILING


def test_the_reviews_lane_adr_38_added_is_allowed(monkeypatch):
    monkeypatch.setattr(gate, "file_at", lambda ref, path: "---\nname: a\n---\n")
    clause, slug = gate.scope_clause(
        ["skills/a/reviews/2026-09-30-ursa-chair.md"], "", "origin/main")
    assert clause.state == gate.OK and slug == "a"


def test_a_new_skill_still_goes_to_the_owner(monkeypatch):
    """The loop maintains, it does not originate (ADR-37, amended 2026-09-29)."""
    monkeypatch.setattr(gate, "file_at", lambda ref, path: "")
    clause, _ = gate.scope_clause(["skills/new/SKILL.md"], "", "origin/main")
    assert clause.state == gate.FAILING
    assert any("new skill rather than a revision" in r for r in clause.reasons)


def test_a_receipt_bundle_is_allowed_and_said_out_loud(monkeypatch):
    monkeypatch.setattr(gate, "file_at", lambda ref, path: "---\nname: a\n---\n")
    clause, slug = gate.scope_clause(
        ["skills/a/SKILL.md",
         gate.RECEIPTS + "2026-09-30-lexical-2.1.json"], "", "origin/main")
    assert clause.state == gate.OK and slug == "a"
    assert any("were allowed" in n for n in clause.notes), (
        "the one allowance outside the skill's folder has to be visible in "
        "every comment, or it becomes invisible")


def test_receipts_alone_are_not_a_revision():
    clause, _ = gate.scope_clause([gate.RECEIPTS + "x.json"], "", "origin/main")
    assert clause.state == gate.FAILING


def test_an_empty_diff_is_unknown_rather_than_a_pass():
    clause, _ = gate.scope_clause([], "", "origin/main")
    assert clause.state == gate.UNKNOWN


def test_a_mixed_pull_request_is_not_the_automatic_path_at_all():
    assert gate.applies(["skills/a/SKILL.md"])
    assert not gate.applies(["skills/a/SKILL.md", "README.md"])
    assert not gate.applies([])


# --------------------------------------------------------------- the verdict

def test_an_unmeasured_clause_is_never_a_pass():
    assert gate.verdict([gate.Clause("a", gate.OK, [])]) == "passed"
    assert gate.verdict([gate.Clause("a", gate.OK, []),
                         gate.Clause("b", gate.UNKNOWN, ["no credential"])]) \
        == "failed"
    assert gate.verdict([gate.Clause("a", gate.FAILING, ["no"])]) == "failed"


def test_the_comment_carries_every_reason_and_names_what_it_did_not_check():
    clauses = [gate.Clause("provenance", gate.FAILING,
                           ["claim 85 is deprecated"]),
               gate.Clause("eval", gate.OK, [], ["version 3"])]
    body = gate.comment(clauses, "harness-engineering", "origin/main", TODAY)
    assert "claim 85 is deprecated" in body
    assert "did not pass" in body
    assert "Nothing was merged and nothing was reverted" in body


def test_a_passing_comment_still_says_what_a_harness_cannot_judge():
    body = gate.comment([gate.Clause("a", gate.OK, [])], "x", "origin/main",
                        TODAY)
    assert "whether the trigger that asked for this revision was" in body


# --------------------------------------------------------------- pause

def test_the_kill_switch_fails_the_gate_and_prints_the_reason(monkeypatch,
                                                             tmp_path):
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    (tmp_path / "skills").mkdir()
    (tmp_path / gate.PAUSE_PATH).write_text("the contradicts edges are wrong\n")
    clause = gate.pause_clause()
    assert clause.state == gate.FAILING
    assert "the contradicts edges are wrong" in clause.reasons[0]


def test_no_kill_switch_is_an_ok_clause_rather_than_a_silence():
    assert gate.pause_clause().state == gate.OK


# --------------------------------------------------------------- provenance

def test_a_snapshot_two_missed_runs_old_fails_rather_than_passes():
    assert gate.SNAPSHOT_MAX_AGE_DAYS == 3
    stale = triggers.snapshot([[1, 9]], [], "2026-09-20")
    assert triggers.snapshot_problems(stale, TODAY, gate.SNAPSHOT_MAX_AGE_DAYS)


def test_provenance_is_unknown_when_the_scope_clause_found_no_skill():
    assert gate.provenance_clause("", TODAY).state == gate.UNKNOWN


# --------------------------------------------------------------- eval

def _doc(sha, version="3", trigger="refines", delta=0.4, ci=(0.2, 0.6),
         history=None):
    entry = {"version": version, "date": TODAY, "subject_model": "kimi-k2.6",
             "verdict": "gain", "trigger": trigger, "skill_md_sha256": sha,
             "delta": {"mean": delta, "ci95": list(ci)},
             "controls_unchanged": True}
    return {"contract": 1, "skill": "x", "skill_md_sha256": sha, "date": TODAY,
            "subject_model": "kimi-k2.6", "judge_model": "openai/gpt-oss-120b",
            "repetitions": 3, "tasks": 6, "verdict": "gain",
            "delta": {"mean": delta, "ci95": list(ci), "method": "fixture"},
            "controls": {"tasks": 2, "delta": 0.0, "ci95": [-0.05, 0.05],
                         "unchanged": True},
            "history": (history or []) + [entry]}


class Tree:
    """A repository with one skill in it, for the file-reading clauses."""

    def __init__(self, tmp_path, body="# x\n\nPlain prose only.\n", version="3"):
        self.root = tmp_path
        self.dir = tmp_path / "skills" / "x"
        (self.dir / "evals").mkdir(parents=True)
        self.skill = self.dir / "SKILL.md"
        self.skill.write_text(
            f"---\nname: x\nversion: {version}\nstatus: active\n"
            "provenance:\n  extracted: 2026-09-15\n  claims: [1, 2]\n---\n"
            + body)

    def sha(self):
        import hashlib

        return hashlib.sha256(self.skill.read_text().encode()).hexdigest()

    def write_results(self, **kwargs):
        (self.dir / "evals" / "results.json").write_text(
            json.dumps(_doc(self.sha(), **kwargs), indent=2))


@pytest.fixture
def tree(tmp_path, monkeypatch):
    t = Tree(tmp_path)
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    monkeypatch.setattr(gate.skill_eval, "ROOT", tmp_path)
    monkeypatch.setattr(gate.registrar, "ROOT", tmp_path)
    monkeypatch.setattr(gate.registrar, "SKILLS_DIR", tmp_path / "skills")
    monkeypatch.setattr(gate, "file_at", lambda ref, path: "")
    return t


def test_a_skill_with_no_results_file_cannot_merge_itself(tree):
    clause = gate.eval_clause("x", "origin/main")
    assert clause.state == gate.FAILING
    assert "results.json is missing" in clause.reasons[0]


def test_a_result_measured_against_a_different_skill_text_is_refused(tree):
    tree.write_results()
    tree.skill.write_text(tree.skill.read_text() + "\nAn unmeasured sentence.\n")
    clause = gate.eval_clause("x", "origin/main")
    assert clause.state == gate.FAILING
    assert any("different SKILL.md" in r for r in clause.reasons)


def test_a_version_with_no_trigger_in_the_history_is_refused(tree):
    tree.write_results(trigger="")
    clause = gate.eval_clause("x", "origin/main")
    assert clause.state == gate.FAILING
    assert any("no trigger" in r for r in clause.reasons)


def test_a_history_that_never_names_this_version_is_refused(tree):
    tree.write_results(version="2")
    clause = gate.eval_clause("x", "origin/main")
    assert clause.state == gate.FAILING
    assert any("no entry for version" in r for r in clause.reasons)


def test_a_clean_revision_with_a_named_trigger_passes(tree):
    tree.write_results()
    clause = gate.eval_clause("x", "origin/main")
    assert clause.state == gate.OK, clause.reasons
    assert any("asked for by refines" in n for n in clause.notes)


def test_a_delta_below_the_previous_version_s_lower_bound_is_refused(tree):
    previous = {"version": "2", "date": "2026-09-20",
                "subject_model": "kimi-k2.6", "verdict": "gain",
                "trigger": "by hand",
                "delta": {"mean": 0.5, "ci95": [0.3, 0.7]}}
    tree.write_results(delta=0.1, ci=(-0.1, 0.3), history=[previous])
    clause = gate.eval_clause("x", "origin/main")
    assert clause.state == gate.FAILING
    assert any("below the previous result's own lower bound" in r
               for r in clause.reasons)


def test_controls_that_moved_are_refused(tree):
    tree.write_results()
    doc = json.loads((tree.dir / "evals" / "results.json").read_text())
    doc["controls"] = {"tasks": 2, "delta": 0.4, "ci95": [0.2, 0.6],
                       "unchanged": False}
    (tree.dir / "evals" / "results.json").write_text(json.dumps(doc))
    clause = gate.eval_clause("x", "origin/main")
    assert clause.state == gate.FAILING


# --------------------------------------------------------------- the ban list

def test_the_clause_is_the_delta_because_the_library_already_carries_findings():
    """The measurement behind the decision, asserted so it cannot rot silently."""
    library = sorted((ROOT / "skills").glob("*/SKILL.md"))
    assert library
    total = sum(len(ban_list.check(p.read_text())) for p in library)
    assert total > 0, (
        "if the library is clean now, this clause can become an absolute and "
        "this test is the place that says so")


def test_a_revision_that_adds_a_tell_is_refused(tree, monkeypatch):
    before = tree.skill.read_text()
    monkeypatch.setattr(gate, "file_at", lambda ref, path: before)
    tree.skill.write_text(before + "\nThis will unlock a seamless tapestry.\n")
    clause = gate.ban_list_clause("x", "origin/main")
    assert clause.state == gate.FAILING
    assert any("entry 1" in r for r in clause.reasons)


def test_a_revision_that_inherits_a_tell_is_not_punished_for_it(tree,
                                                               monkeypatch):
    dirty = tree.skill.read_text() + "\nThis is a very old sentence.\n"
    tree.skill.write_text(dirty + "\nOne plain new sentence.\n")
    monkeypatch.setattr(gate, "file_at", lambda ref, path: dirty)
    clause = gate.ban_list_clause("x", "origin/main")
    assert clause.state == gate.OK
    assert any("backlog" in n for n in clause.notes)


def test_the_clause_says_that_most_of_the_ban_list_needs_a_reader(tree,
                                                                 monkeypatch):
    monkeypatch.setattr(gate, "file_at", lambda ref, path: tree.skill.read_text())
    clause = gate.ban_list_clause("x", "origin/main")
    assert any("floor" in n for n in clause.notes)


# --------------------------------------------------------------- ban list core

def test_the_mechanical_entries_are_quoted_by_number():
    findings = ban_list.check("It is important to note this very seamless work.")
    entries = {f["entry"] for f in findings}
    assert 1 in entries and 4 in entries and 5 in entries


def test_code_and_inline_spans_are_exempt():
    assert ban_list.check("```\nvery = delve(x)\n```\n") == []
    assert ban_list.check("Call `delve_into(x)`.") == []


def test_every_character_outside_ascii_is_caught_not_just_the_three_examples():
    """Entry 13, amended 2026-09-21 after incident 27."""
    findings = ban_list.non_ascii("an em dash —, a 3× move, a "
                                  "curly ’ apostrophe")
    assert len(findings) == 3
    assert all(f["entry"] == 13 for f in findings)


def test_a_name_the_source_spells_that_way_can_be_allowed():
    assert ban_list.non_ascii("Klärner", allow="ä") == []


def test_the_ban_list_smoke_passes():
    assert ban_list.smoke() == 0


def test_the_gate_smoke_passes():
    assert gate.smoke() == 0
