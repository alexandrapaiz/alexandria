"""The scoping stage, tested against a checkout where scoping is the wrong move.

Incident 32's rule, verbatim: every gate is tested against an artifact known
to fail it before the gate is trusted. `tools/skill_scope.py` carries one gate,
`verdict`, which answers whether loading three skills beats loading the
library. A measurement whose verdict has only ever been seen saying "wins" is
indistinguishable from a verdict that cannot say anything else, so the tree
built in `misleading_tree` exists to make it say the other thing.

    python3 -m pytest tests/test_skill_scope.py -q
"""

import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "skill_scope", REPO / "tools" / "skill_scope.py")
ss = importlib.util.module_from_spec(spec)
sys.modules["skill_scope"] = ss
spec.loader.exec_module(ss)

tt = ss._trigger_test(REPO)


def candidate(name, description, body):
    return {"name": name, "description": description,
            "activation": tt.activation_clause(description),
            "body": body, "origin": "library", "library": True}


# ---------------------------------------------------------------------------
# Stage 1
# ---------------------------------------------------------------------------

def test_the_arithmetic_holds_against_its_own_fixtures():
    lines = ss.smoke(tt)
    assert any("scopes to nothing" in line for line in lines)


def test_a_query_nothing_covers_loads_nothing():
    index = ss.BM25Index(tt, {
        "alpha": candidate("alpha", "", "pelican roosting habits"),
        "beta": candidate("beta", "", "diesel engine timing"),
    }, "body")
    assert ss.scope(index, "quantum chromodynamics lattice")["loaded"] == []


def test_the_cutoff_drops_a_candidate_the_query_barely_touches():
    index = ss.BM25Index(tt, {
        "alpha": candidate("alpha", "", "pelican pelican roosting pelican"),
        "beta": candidate("beta", "", "diesel engine timing belts"),
    }, "body")
    s = ss.scope(index, "pelican roosting")
    assert s["loaded"] == ["alpha"]
    assert s["cutoff"] == round(s["top_score"] * ss.KEEP_RATIO, 4)


def test_k_max_is_a_ceiling_even_when_everything_matches():
    pool = {f"s{i}": candidate(f"s{i}", "", "pelican roosting habits")
            for i in range(8)}
    index = ss.BM25Index(tt, pool, "body")
    assert len(ss.scope(index, "pelican roosting habits")["loaded"]) == ss.K_MAX


def test_length_does_not_buy_a_scope_slot():
    """lexical/2.1 rewards a longer candidate on any prompt both cover, which
    is incident 31. A stage that indexes whole bodies would inherit that at
    three times the scale, so BM25 is the scorer and this is the property that
    earns it."""
    index = ss.BM25Index(tt, {
        "short": candidate("short", "", "pelican roosting"),
        "long": candidate("long", "",
                          "pelican roosting " + "unrelated filler prose " * 80),
    }, "body")
    assert index.rank("pelican roosting")[0][0] == "short"


# ---------------------------------------------------------------------------
# Outcomes: a wrong skill is not the same failure as no skill
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fired,expect,want", [
    ("alpha", "alpha", "correct"),
    ("beta", "alpha", "wrong"),
    (None, "alpha", "none"),
    (None, None, "correct"),
    ("alpha", None, "wrong"),
])
def test_the_four_outcomes_stay_separate(fired, expect, want):
    assert ss.outcome(fired, expect) == want


def test_recall_ignores_the_cases_that_have_no_golden_skill():
    t = ss.tally([{"expect": "a", "outcome": "correct"},
                  {"expect": "a", "outcome": "none"},
                  {"expect": None, "outcome": "wrong"}])
    assert t["recall"] == 0.5
    assert t["golden_cases"] == 2
    assert t["silence_held"] == 0.0
    assert t["suite_pass"] == round(1 / 3, 4)


# ---------------------------------------------------------------------------
# The gate, against a checkout where it must fail
# ---------------------------------------------------------------------------

def write_skill(root, name, description, body):
    d = root / "skills" / name
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n"
        f"version: 1\nstatus: active\n---\n\n{body}\n")


def write_cases(root, name, cases):
    (root / "skills" / name / "triggers.json").write_text(json.dumps({
        "skill": name, "suite_version": 1, "written": "2026-10-26",
        "author": "test", "note": "fixture", "cases": cases}))


@pytest.fixture
def misleading_tree(tmp_path):
    """Two skills whose bodies are about each other's subject.

    The descriptions are correct, so the unscoped selector gets both cases
    right. The bodies are swapped, so a stage that trusts them scopes every
    query to the wrong skill and the golden one is never loaded. Scoping on
    this tree is strictly worse than not scoping, which is exactly what
    `verdict` has to be able to say.
    """
    root = tmp_path / "checkout"
    (root / "skills" / "_validation").mkdir(parents=True)
    shutil.copy(REPO / "skills" / "_validation" / "trigger_test.py",
                root / "skills" / "_validation" / "trigger_test.py")
    (root / "skills" / "_validation" / "decoys.json").write_text(json.dumps({
        "note": "fixture", "version": 1, "written": "2026-10-26",
        "decoys": [
            {"name": "decoy-knitting",
             "description": "Knitting gauge and yarn weight. Use when a "
                            "sweater comes out the wrong size."},
            {"name": "decoy-tax",
             "description": "Payroll tax filing deadlines. Use when a "
                            "quarterly return is late."},
        ]}))
    write_skill(root, "pelican",
                "Pelican roosting sites. Use when pelicans choose a roost.",
                "diesel engine timing belts and injector pumps " * 40)
    write_skill(root, "diesel",
                "Diesel engine timing. Use when a diesel engine mistimes.",
                "pelican roosting sites and colony nesting ledges " * 40)
    write_cases(root, "pelican", [
        {"id": "p-1", "kind": "positive", "expect": "pelican",
         "prompt": "where do pelicans choose a roost at dusk"}])
    write_cases(root, "diesel", [
        {"id": "d-1", "kind": "positive", "expect": "diesel",
         "prompt": "my diesel engine mistimes under load"}])
    return root


def test_the_verdict_can_say_scoping_loses(misleading_tree):
    report = ss.measure(misleading_tree)
    full = report["conditions"][-1]["arms"]
    assert full["unscoped"]["recall"] == 1.0
    assert full["scope/body"]["recall"] < full["unscoped"]["recall"]
    assert full["scope/body"]["scope_miss_rate"] == 1.0
    assert ss.verdict(report) == 1


def test_the_cli_exits_nonzero_when_scoping_loses(misleading_tree, capsys):
    code = ss.main(["--measure", "--root", str(misleading_tree)])
    assert code == 1
    assert "scoping does not win" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# This repository, which is the result the sprint item asks for
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def live():
    return ss.measure(REPO)


def test_the_suite_is_the_published_one_and_not_a_new_exam(live):
    """The cases come from skills/*/triggers.json, the same file the trigger
    receipts in skills/_validation/results/ are scored on. A measurement that
    writes its own query set can pass by writing easy queries."""
    assert live["cases"]["total"] == 67
    assert live["cases"]["golden"] + live["cases"]["silent"] == 67


def test_the_distractors_are_real_skills_from_this_checkout(live):
    assert live["distractor_pool"]["count"] == 20
    assert live["distractor_pool"]["source"] == ss.DISTRACTOR_DIR
    assert all((REPO / ss.DISTRACTOR_DIR / n / "SKILL.md").exists()
               for n in live["distractor_pool"]["names"])


def test_scoping_loads_fewer_skills_and_keeps_recall(live):
    full = live["conditions"][-1]["arms"]
    assert full["unscoped"]["mean_skills_loaded"] == 29
    assert full["scope/body"]["mean_skills_loaded"] <= ss.K_MAX
    assert full["scope/body"]["recall"] >= full["unscoped"]["recall"]
    assert full["scope/body"]["mean_context_words"] < \
        full["unscoped"]["mean_context_words"]


def test_the_control_arm_is_measured_and_reported(live):
    """scope/desc indexes the same text the baseline already sees, so it can
    only narrow the pool. It is in the report so that a win on scope/body
    cannot be read as a win for narrowing alone."""
    for cond in live["conditions"]:
        assert "scope/desc" in cond["arms"]
        assert cond["arms"]["scope/desc"]["recall"] is not None


def test_the_cost_of_scoping_is_reported_rather_than_hidden(live):
    """Scope misses are the mechanism's own failure mode: a query whose golden
    skill the scope dropped can never fire it. The number has to be in the
    report even when recall still goes up."""
    full = live["conditions"][-1]["arms"]["scope/body"]
    assert full["scope_misses"] > 0
    assert full["scope_miss_rate"] > 0


def test_a_flat_baseline_is_stated_rather_than_implied(live):
    """This checkout holds twenty distractors, not a thousand. If the unscoped
    baseline does not move across the sweep, the report says the pool failed
    to stage the collapse rather than leaving a reader to infer it did."""
    drift = ss.baseline_drift(live)
    note = " ".join(ss.render_baseline_note(live))
    if drift["flat"]:
        assert "does not reproduce" in note
    else:
        assert "moved" in note
