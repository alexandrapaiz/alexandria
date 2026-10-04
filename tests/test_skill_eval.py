"""The with-versus-without eval harness.

    python3 -m pytest tests/test_skill_eval.py -q

Nothing here calls a model, spends a cent or touches a provider. What it holds
is the half of the harness that decides what a number is allowed to say, which
is the half that can be wrong without anyone noticing: the exact binomial
interval, the clustered bootstrap, the verdict rule, the blinding of the judge,
the refusal to grade a model with itself, and the refusal to start a run inside a
window another Kimi job owns.

The interval has a published check. `docs/product/skill-validation.md` says a
perfect 6 of 6 bounds true reliability at 0.54 from below at 95 percent
confidence. That number was computed by someone else, before this file existed,
and `test_the_interval_matches_the_number_the_design_doc_published` is the
assertion that this implementation agrees with it.
"""

from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "pipeline"))

import skill_eval as ev          # noqa: E402


# ------------------------------------------------------------ the interval

def test_the_interval_matches_the_number_the_design_doc_published():
    low, high = ev.clopper_pearson(6, 6)
    assert round(low, 2) == 0.54, (
        "docs/product/skill-validation.md §6 says a clean sweep of six bounds "
        "reliability at 0.54, and that number is quoted at the owner")
    assert high == 1.0


def test_zero_successes_reports_a_bound_rather_than_certainty():
    low, high = ev.clopper_pearson(0, 6)
    assert low == 0.0
    assert 0.3 < high < 0.6, (
        "zero of six does not mean the true rate is zero, and V5 of the design "
        "requires the finite-sample bound rather than the point estimate")


def test_the_interval_widens_as_n_falls():
    narrow = ev.clopper_pearson(30, 60)
    wide = ev.clopper_pearson(3, 6)
    assert (wide[1] - wide[0]) > (narrow[1] - narrow[0])


def test_a_half_and_half_result_straddles_a_half():
    low, high = ev.clopper_pearson(5, 10)
    assert low < 0.5 < high


def test_an_empty_sample_is_the_whole_interval_rather_than_a_crash():
    assert ev.clopper_pearson(0, 0) == (0.0, 1.0)


def test_the_interval_never_leaves_zero_to_one():
    for n in (1, 2, 7, 13, 40):
        for k in range(n + 1):
            low, high = ev.clopper_pearson(k, n)
            assert 0.0 <= low <= high <= 1.0


# ------------------------------------------------------------ the bootstrap

def task(tid, with_scores, without_scores, control=False):
    return {"id": tid, "control": control, "scored_by": "check",
            "with_scores": with_scores, "without_scores": without_scores,
            "with_mean": ev.mean(with_scores),
            "without_mean": ev.mean(without_scores),
            "delta": ev.mean(with_scores) - ev.mean(without_scores),
            "notes": []}


def test_the_same_data_gives_the_same_interval_twice():
    rows = [task("a", [1, 1, 0], [0, 0, 1]), task("b", [1, 0, 1], [0, 1, 0])]
    assert ev.bootstrap_delta(rows) == ev.bootstrap_delta(rows)


def test_a_unanimous_result_has_no_spread():
    rows = [task("a", [1, 1, 1], [0, 0, 0]), task("b", [1, 1, 1], [0, 0, 0])]
    delta, low, high = ev.bootstrap_delta(rows)
    assert (delta, low, high) == (1.0, 1.0, 1.0)


def test_one_task_carrying_the_whole_gain_shows_it_in_the_spread():
    """The failure this catches is the reason the bootstrap is clustered.

    Two tasks, one of which the skill transforms and one it does not. The mean
    delta is 0.5 either way. Resampling the six repetitions as if they were six
    independent observations would report a tight interval around 0.5. Resampling
    the tasks says what is actually true, which is that the evidence cannot rule
    out zero.
    """
    rows = [task("moved", [1, 1, 1], [0, 0, 0]),
            task("unmoved", [1, 1, 1], [1, 1, 1])]
    delta, low, high = ev.bootstrap_delta(rows)
    assert delta == 0.5
    assert low == 0.0 and high == 1.0


def test_a_regression_reads_as_a_negative_delta():
    rows = [task("a", [0, 0, 0], [1, 1, 1]), task("b", [0, 0, 0], [1, 1, 1])]
    delta, low, high = ev.bootstrap_delta(rows)
    assert delta == -1.0 and high == -1.0


def test_no_tasks_is_zero_rather_than_a_crash():
    assert ev.bootstrap_delta([]) == (0.0, 0.0, 0.0)


# ------------------------------------------------------------ the verdict

@pytest.mark.parametrize("delta,low,high,expected", [
    (0.5, 0.2, 0.8, "gain"),
    (0.5, 0.0, 1.0, "no gain"),
    (0.5, -0.1, 0.9, "no gain"),
    (-0.4, -0.7, -0.1, "regression"),
    (0.05, 0.01, 0.09, "gain too small to matter"),
])
def test_the_verdict_rule(delta, low, high, expected):
    assert ev.verdict_of(delta, low, high, 0.15) == expected


def test_a_lower_bound_at_exactly_zero_is_not_a_gain():
    assert ev.verdict_of(0.9, 0.0, 1.0, 0.1) == "no gain"


# ------------------------------------------------------------ the scoring

def test_a_hard_check_needs_every_pattern():
    t = {"check": {"type": "contains_all", "patterns": ["harness", "on-policy"]}}
    assert ev.hard_check(t, "adapt the harness, then go on-policy",
                         pathlib.Path("."))[0] == 1.0
    assert ev.hard_check(t, "adapt the harness", pathlib.Path("."))[0] == 0.0


def test_a_forbidden_pattern_fails_the_check():
    t = {"check": {"type": "contains_none", "patterns": [r"fine.?tune"]}}
    assert ev.hard_check(t, "adapt the harness", pathlib.Path("."))[0] == 1.0
    assert ev.hard_check(t, "fine-tune it", pathlib.Path("."))[0] == 0.0


def test_a_number_out_of_range_fails():
    t = {"check": {"type": "number_in_range", "pattern": r"([\d.]+)\s*points",
                   "low": 4, "high": 30}}
    assert ev.hard_check(t, "a 12 points regression", pathlib.Path("."))[0] == 1.0
    assert ev.hard_check(t, "a 90 points regression", pathlib.Path("."))[0] == 0.0
    assert ev.hard_check(t, "no number here", pathlib.Path("."))[0] == 0.0


def test_a_check_on_json_reads_the_keys():
    t = {"check": {"type": "json_parses", "required_keys": ["plan"]}}
    assert ev.hard_check(t, '{"plan": "x"}', pathlib.Path("."))[0] == 1.0
    assert ev.hard_check(t, '{"other": "x"}', pathlib.Path("."))[0] == 0.0
    assert ev.hard_check(t, "not json", pathlib.Path("."))[0] == 0.0


def test_a_project_check_runs_the_command_in_a_fresh_copy(tmp_path):
    project = tmp_path / "proj"
    project.mkdir()
    (project / "check.py").write_text(
        "import answer, sys; sys.exit(0 if answer.value == 42 else 1)\n")
    t = {"kind": "project", "project": "proj", "answer_file": "answer.py",
         "check": {"type": "command", "run": ["python3", "check.py"],
                   "timeout": 30}}
    good = ev.hard_check(t, "```python\nvalue = 42\n```", tmp_path)
    bad = ev.hard_check(t, "```python\nvalue = 7\n```", tmp_path)
    assert good[0] == 1.0 and good[1] == "exit 0"
    assert bad[0] == 0.0
    # The copy is fresh every time, so the first run cannot have left the second
    # one a passing answer file.
    assert not (project / "answer.py").exists()


def test_a_project_check_that_hangs_costs_one_timeout(tmp_path):
    project = tmp_path / "proj"
    project.mkdir()
    (project / "loop.py").write_text("while True: pass\n")
    t = {"kind": "project", "project": "proj", "answer_file": "x.py",
         "check": {"type": "command", "run": ["python3", "loop.py"],
                   "timeout": 1}}
    score, why = ev.hard_check(t, "anything", tmp_path)
    assert score == 0.0 and "timed out" in why


def test_the_fenced_block_is_what_a_project_check_writes():
    assert ev.extract_code("here it is:\n```py\nx = 1\n```\nhope that helps"
                           ) == "x = 1\n"
    assert ev.extract_code("x = 1") == "x = 1"


def test_a_rubric_scores_the_fraction_satisfied():
    rubric = [{"id": "a", "asks": "?"}, {"id": "b", "asks": "?"}]
    assert ev.rubric_score({"a": "yes", "b": "no"}, rubric)[0] == 0.5
    assert ev.rubric_score({"a": "Yes", "b": "YES"}, rubric)[0] == 1.0
    # A criterion the judge did not answer is not satisfied. Silence is never
    # scored as a pass.
    assert ev.rubric_score({}, rubric)[0] == 0.0


# ------------------------------------------------------------ the blinding

def test_the_judge_is_never_told_which_arm_it_is_grading():
    t = {"ask": "what should we do?", "rubric": [{"id": "a", "asks": "does it?"}]}
    prompt = ev.judge_prompt(t, "adapt the harness")
    lowered = prompt.lower()
    for leak in ("with the skill", "without the skill", "arm ", "skill under test",
                 "baseline", "control"):
        assert leak not in lowered, f"the judge prompt leaks {leak!r}"
    assert ev.JUDGE_SYSTEM.count("do not know how the answer was produced")


def test_both_arms_get_the_same_wrapper_and_only_the_skill_differs():
    calls = []

    class Recorder:
        def ask(self, system, user, max_tokens):
            calls.append((system, user, max_tokens))
            return {"answer": "x"}

    t = {"id": "t", "ask": "the question",
         "check": {"type": "contains_all", "patterns": ["x"]}}
    ev.run_task(Recorder(), Recorder(), t, "BODY OF THE SKILL", 1,
                pathlib.Path("."))
    systems = [c[0] for c in calls]
    assert len(calls) == 2
    assert {c[1] for c in calls} == {"the question"}
    assert {c[2] for c in calls} == {ev.SUBJECT_MAX_TOKENS}
    loaded = [s for s in systems if "BODY OF THE SKILL" in s]
    bare = [s for s in systems if "BODY OF THE SKILL" not in s]
    assert len(loaded) == 1 and len(bare) == 1
    assert loaded[0].startswith(bare[0]), (
        "the with-arm's system prompt has to be the without-arm's plus the "
        "skill, or the two arms differ by more than the skill and the run is "
        "measuring the harness")


# ------------------------------------------------------------ the refusals

def test_a_model_may_not_grade_itself(tmp_path, monkeypatch, capsys):
    spec = {"contract": 1, "skill": "x", "policy": {"repetitions": 2},
            "tasks": [{"id": "a", "ask": "?",
                       "check": {"type": "contains_all", "patterns": ["x"]}}]}
    monkeypatch.setattr(ev, "load_tasks", lambda slug: (spec, []))
    code = ev.main(["--skill", "x", "--subject", "kimi-k2.6",
                    "--judge", "kimi-k2.6"])
    assert code == 1
    assert "grading its own answer" in capsys.readouterr().out


def test_a_run_refuses_to_start_inside_another_kimi_job_s_window(monkeypatch,
                                                                capsys):
    import datetime as dt

    import llm

    spec = {"contract": 1, "skill": "x", "policy": {"repetitions": 2},
            "tasks": [{"id": "a", "ask": "?",
                       "check": {"type": "contains_all", "patterns": ["x"]}}]}
    monkeypatch.setattr(ev, "load_tasks", lambda slug: (spec, []))

    start, _ = sorted(llm.KIMI_WINDOWS.values())[0]

    class Inside(dt.datetime):
        @classmethod
        def utcnow(cls):
            return dt.datetime(2026, 9, 30, start // 60, start % 60 + 5)

    monkeypatch.setattr(ev.dt, "datetime", Inside)
    assert ev.main(["--skill", "x"]) == 1
    out = capsys.readouterr().out
    assert "organization concurrency is 1" in out
    assert "INC-2026-09-24-press-provider-migration" in out


def test_the_window_check_names_the_job_that_owns_the_minute():
    import datetime as dt

    import llm

    for label, (start, end) in llm.KIMI_WINDOWS.items():
        middle = dt.datetime(2026, 9, 30, (start + 1) // 60, (start + 1) % 60)
        assert ev.window_conflict(middle) == label
    assert ev.window_conflict(dt.datetime(2026, 9, 30, 16, 30)) == ""


def test_a_free_judge_is_not_blocked_by_a_kimi_window(monkeypatch):
    """The refusal is about Moonshot's account, so a Groq subject runs anyway."""
    import llm

    assert llm.budget().provider_of(ev.DEFAULT_JUDGE) == "groq"
    assert llm.budget().provider_of(ev.DEFAULT_SUBJECT) == "moonshot"


def test_the_default_subject_and_judge_are_different_providers():
    import llm

    assert ev.DEFAULT_SUBJECT != ev.DEFAULT_JUDGE
    guard = llm.budget()
    assert ev.DEFAULT_SUBJECT in guard.MODELS
    assert ev.DEFAULT_JUDGE in guard.MODELS
    assert ev.DEFAULT_SUBJECT not in guard.DECOMMISSIONED
    assert ev.DEFAULT_JUDGE not in guard.DECOMMISSIONED


# ------------------------------------------------------------ conformance

def base_spec(**over):
    spec = {"contract": 1, "skill": "s", "policy": {"repetitions": 5},
            "tasks": [{"id": "a", "ask": "?",
                       "check": {"type": "contains_all", "patterns": ["x"]}}]}
    spec.update(over)
    return spec


def test_a_conformant_file_has_no_problems(tmp_path):
    assert ev.conformance(base_spec(), "s", tmp_path) == []


@pytest.mark.parametrize("spec,fragment", [
    (base_spec(contract=99), "this harness speaks 1 and 2"),
    (base_spec(contract=2), None),
    (base_spec(skill="other"), "the file says skill"),
    (base_spec(policy={}), "not pre-registered"),
    (base_spec(policy={"repetitions": 3, "subject": "m", "judge": "m"}),
     "the same model"),
    (base_spec(policy={"repetitions": 3, "subject": "gpt-9", "judge": "m"}),
     "not a model in pipeline/budget.py's table"),
    (base_spec(tasks=[]), "no tasks"),
    (base_spec(tasks=[{"id": "a", "ask": "?"}]), "neither a hard check nor a rubric"),
    (base_spec(tasks=[{"id": "a", "check": {"type": "contains_all",
                                            "patterns": ["x"]}}]), "no `ask`"),
    (base_spec(tasks=[{"id": "a", "ask": "?",
                       "check": {"type": "vibes"}}]), "is not one of"),
    (base_spec(tasks=[{"id": "a", "ask": "?",
                       "check": {"type": "contains_all", "patterns": ["("]}}]),
     "not a regular expression"),
    (base_spec(tasks=[{"id": "a", "ask": "?",
                       "check": {"type": "contains_all", "patterns": []}}]),
     "with no patterns"),
    (base_spec(tasks=[{"id": "a", "ask": "?", "rubric": [{"id": "x"}]}]),
     "needs an id and an `asks`"),
    (base_spec(tasks=[{"id": "a", "ask": "?", "control": True,
                       "check": {"type": "contains_all", "patterns": ["x"]}}]),
     "every task is a control"),
    (base_spec(tasks=[{"id": "a", "ask": "?", "kind": "project",
                       "project": "nowhere", "answer_file": "x.py",
                       "check": {"type": "command", "run": ["true"]}}]),
     "is neither"),
])
def test_conformance_catches(spec, fragment, tmp_path):
    """A `None` fragment is a case that must produce no problem at all."""
    problems = ev.conformance(spec, "s", tmp_path)
    if fragment is None:
        assert problems == [], problems
    else:
        assert any(fragment in p for p in problems), problems


def test_two_tasks_with_one_id_is_caught(tmp_path):
    spec = base_spec(tasks=[
        {"id": "a", "ask": "?", "check": {"type": "contains_all", "patterns": ["x"]}},
        {"id": "a", "ask": "?", "check": {"type": "contains_all", "patterns": ["y"]}},
    ])
    assert any("share the id" in p for p in ev.conformance(spec, "s", tmp_path))


def test_a_missing_eval_file_is_unmeasured_and_never_a_failure(capsys):
    """Exit 2, not 1. The skill seat writes the tasks, not this harness."""
    code = ev.main(["--check"])
    out = capsys.readouterr().out
    assert code == 2
    assert "unmeasured:" in out
    assert "failing:" not in out


# ------------------------------------------------------------ end to end

def test_the_smoke_run_proves_the_whole_pipeline(capsys):
    assert ev.smoke() == 0
    assert "the harness measures what it should" in capsys.readouterr().out


def test_a_result_carries_every_field_the_site_contract_names(tmp_path):
    subject = ev.ScriptedSubject(with_answer="adapt the harness",
                                 without_answer="fine-tune it")
    spec = base_spec(tasks=[
        {"id": "graded", "ask": "?",
         "check": {"type": "contains_all", "patterns": ["harness"]}},
        {"id": "held", "control": True, "ask": "?",
         "check": {"type": "contains_none", "patterns": ["nonsense"]}},
    ])
    rows = [ev.run_task(subject, subject, t, "body", 4, tmp_path)
            for t in spec["tasks"]]
    result = ev.summarize("s", "a" * 64, spec, rows, "kimi-k2.6",
                          "openai/gpt-oss-120b", 4, 0.12, "2026-09-30")
    contract = (ROOT / "site" / "app" / "skills" / "README.md").read_text()
    for field in ("contract", "skill", "skill_md_sha256", "date",
                  "subject_model", "judge_model", "repetitions", "tasks",
                  "control_tasks", "spend_usd", "with_skill", "without_skill",
                  "delta", "verdict", "per_task", "controls"):
        assert field in result, field
        assert f"`{field}`" in contract, (
            f"{field} is in the result and not in the contract the frontend "
            "reads, so the page cannot know it exists")
    assert result["delta"]["mean"] == 1.0
    assert result["verdict"] == "gain"
    assert json.loads(json.dumps(result)) == result, "the result must be JSON"


def test_the_result_names_its_own_seed_so_a_reader_can_replay_it(tmp_path):
    subject = ev.ScriptedSubject(with_answer="harness", without_answer="no")
    rows = [ev.run_task(subject, subject, t, "body", 3, tmp_path)
            for t in ev.SMOKE_SPEC["tasks"]]
    result = ev.summarize("s", "b" * 64, ev.SMOKE_SPEC, rows, "m", "j", 3, 0.0,
                          "2026-09-30")
    assert str(ev.BOOTSTRAP_SEED) in result["delta"]["method"]
    assert str(ev.BOOTSTRAP_DRAWS) in result["delta"]["method"]


def test_no_number_prints_without_its_n(tmp_path):
    subject = ev.ScriptedSubject(with_answer="harness", without_answer="no")
    rows = [ev.run_task(subject, subject, t, "body", 3, tmp_path)
            for t in ev.SMOKE_SPEC["tasks"]]
    result = ev.summarize("s", "c" * 64, ev.SMOKE_SPEC, rows, "m", "j", 3, 0.0,
                          "2026-09-30")
    text = ev.render(result)
    import re

    # "95% CI" is the label on an interval and is allowed. A score rendered as a
    # percentage is not: V5 of the design says "8 of 10" is a receipt and "80%"
    # is marketing, and this is the assertion that keeps the second one out.
    assert not re.search(r"\d+(\.\d+)?\s*%(?!\s*CI)", text), text
    assert "3 repetitions" in text and "tasks" in text


# ------------------------------------------------- indicators, and the gate

def test_an_indicator_task_cannot_inflate_the_delta(tmp_path):
    """The defect this catches was in this harness until 2026-09-30.

    A check that names something only the skill could supply, "the answer cites
    the 4 to 30 point regression", scores 0 in the without-arm by construction.
    Counting it does not measure the skill, it measures that the number is in the
    skill, and it drags the headline delta up by one task's worth for free. The
    task file declares such a task `scored_in: with_only`, and it is then reported
    and never scored. Anthropic's own `claude plugin eval` excludes the same class
    of grader from both arms for the same reason.
    """
    subject = ev.ScriptedSubject(with_answer="harness", without_answer="no")
    spec = base_spec(tasks=[
        {"id": "real", "ask": "?",
         "check": {"type": "contains_all", "patterns": ["harness"]}},
        {"id": "only-with", "ask": "?", "scored_in": "with_only",
         "check": {"type": "contains_all", "patterns": ["harness"]}},
    ])
    rows = [ev.run_task(subject, subject, t, "body", 3, tmp_path)
            for t in spec["tasks"]]
    result = ev.summarize("s", "d" * 64, spec, rows, "m", "j", 3, 0.0,
                          "2026-09-30")
    assert result["tasks"] == 1, "the indicator must not be a graded task"
    assert result["indicator_tasks"] == 1
    assert result["with_skill"]["n"] == 3, (
        "the indicator's repetitions must be out of the arm totals too")
    assert result["indicators"] == [{"id": "only-with", "fires": 1.0, "n": 3}]


def test_a_task_cannot_be_a_control_and_an_indicator(tmp_path):
    spec = base_spec(tasks=[{"id": "a", "ask": "?", "control": True,
                            "scored_in": "with_only",
                            "check": {"type": "contains_all",
                                      "patterns": ["x"]}}])
    problems = ev.conformance(spec, "s", tmp_path)
    assert any("at once" in p for p in problems)


def test_an_unknown_scored_in_value_is_caught(tmp_path):
    spec = base_spec(tasks=[{"id": "a", "ask": "?", "scored_in": "sometimes",
                            "check": {"type": "contains_all",
                                      "patterns": ["x"]}}])
    assert any("only value this harness knows" in p
               for p in ev.conformance(spec, "s", tmp_path))


def test_a_suite_of_nothing_but_indicators_has_nothing_to_measure(tmp_path):
    spec = base_spec(tasks=[{"id": "a", "ask": "?", "scored_in": "with_only",
                            "check": {"type": "contains_all",
                                      "patterns": ["x"]}}])
    assert any("every task is a control" in p
               for p in ev.conformance(spec, "s", tmp_path))


# --------------------------------------- the shape the skill seat actually wrote

FIXTURE = ROOT / "tests" / "fixtures" / "skill-eval-suite"


def fixture_suite():
    return ev.normalize(json.loads((FIXTURE / "evals.json").read_text()))


def test_the_skill_seat_s_vocabulary_leaves_one_problem_and_it_is_rule_one():
    """The suites were written in a different vocabulary than this harness proposed.

    The skill seat wrote its suites under `evals/evals.json` on 2026-09-30, in the
    same window this harness was written, with `suite_version` for `contract`,
    `kind: treatment|control`, `form` for `kind`, `prompt` for `ask`, and rubric
    criteria carrying 0/1/2 anchors. `normalize` is the one place the two meet.
    This fixture holds one task of every form and check type they use.

    It asserted zero problems until 2026-10-04 and passed, on a fixture that
    said `suite_version: 1`. Every one of the eight real files says 2. The
    version was the single field where the two vocabularies did not meet, and
    it was the one field this fixture did not copy, so the test that existed to
    prove the reader speaks the suites' language was passing because the one
    sentence of that language it got wrong was the one under test.

    One problem is left, on all eight real files and on this one: no `policy`
    block, so the repetitions and the threshold rule 1 asks the author to
    pre-register are not in the file. That is not a problem the reader may
    solve, which is the subject of the next test.
    """
    spec = fixture_suite()
    problems = ev.conformance(spec, "fixture-skill", FIXTURE)
    assert len(problems) == 1 and "policy.repetitions" in problems[0], problems
    assert spec["contract"] == 2 and spec["contract"] in ev.SUITE_CONTRACTS
    ids = {t["id"] for t in spec["tasks"]}
    assert ids == {"fx-t1", "fx-t2", "fx-t3", "fx-t4", "fx-c1", "fx-c2"}
    controls = {t["id"] for t in spec["tasks"] if t.get("control")}
    assert controls == {"fx-c1", "fx-c2"}
    rubrics = {t["id"] for t in spec["tasks"] if t.get("rubric")}
    assert rubrics == {"fx-t1", "fx-c2"}


def test_one_policy_block_is_the_whole_fix_for_a_real_suite():
    """Measured against the eight real files, not asserted: adding the block
    the error message prints is the only edit any of them needs."""
    raw = json.loads((FIXTURE / "evals.json").read_text())
    raw["policy"] = {"repetitions": 3, "subject": ev.DEFAULT_SUBJECT,
                     "judge": ev.DEFAULT_JUDGE, "min_delta": 0.2}
    assert ev.conformance(ev.normalize(raw), "fixture-skill", FIXTURE) == []


def test_a_prose_model_field_is_kept_as_prose_and_never_dialled():
    """The two top-level model fields are sentences in every real suite.

    `"subject_model": "kimi (ADR-32 funded account) by default; a Claude run is
    the monthly OKR benchmark"` is documentation. Lifting it into
    `policy.subject` verbatim, which is what the obvious reading of the
    2026-10-03 ledger entry asks for, would send that sentence to a provider as
    a model name and would publish it on the library page as the model a skill
    was measured on, through `skill_triggers.subject_for`.
    """
    policy = fixture_suite()["policy"]
    assert "subject" not in policy and "judge" not in policy
    assert policy["subject_described"].startswith("kimi (ADR-32")
    assert policy["judge_described"].startswith("a model other than")


def test_a_model_id_at_the_top_level_is_lifted():
    """The same fields filled in the way the contract document's example shows."""
    raw = json.loads((FIXTURE / "evals.json").read_text())
    raw["subject_model"] = ev.DEFAULT_SUBJECT
    raw["judge"] = ev.DEFAULT_JUDGE
    policy = ev.normalize(raw)["policy"]
    assert policy["subject"] == ev.DEFAULT_SUBJECT
    assert policy["judge"] == ev.DEFAULT_JUDGE
    assert "subject_described" not in policy


def test_a_registered_model_outside_the_budget_table_is_not_runnable():
    """A typo costs $0 to catch here and three minutes of a cap to catch live."""
    raw = json.loads((FIXTURE / "evals.json").read_text())
    raw["policy"] = {"repetitions": 3, "subject": "kimi-k2.5",
                     "judge": ev.DEFAULT_JUDGE, "min_delta": 0.2}
    problems = ev.conformance(ev.normalize(raw), "fixture-skill", FIXTURE)
    assert len(problems) == 1
    assert "policy.subject is 'kimi-k2.5'" in problems[0]
    assert "pipeline/budget.py" in problems[0]


def test_normalize_is_idempotent():
    once = fixture_suite()
    assert ev.normalize(once) == once


def test_an_anchored_criterion_is_scored_on_its_own_scale():
    rubric = [{"id": "a", "asks": "?", "anchors": {"0": "no", "1": "half", "2": "yes"}}]
    assert ev.rubric_score({"a": 2}, rubric)[0] == 1.0
    assert ev.rubric_score({"a": 1}, rubric)[0] == 0.5
    assert ev.rubric_score({"a": 0}, rubric)[0] == 0.0
    # Out of scale is clamped, absent is zero, and a judge that answered `yes` on
    # an anchored criterion has not used the scale and never gets full marks.
    assert ev.rubric_score({"a": 9}, rubric)[0] == 1.0
    assert ev.rubric_score({}, rubric)[0] == 0.0
    assert ev.rubric_score({"a": "yes"}, rubric)[0] == 0.5


def test_the_judge_sees_the_anchors():
    task = [t for t in fixture_suite()["tasks"] if t["id"] == "fx-t1"][0]
    prompt = ev.judge_prompt(task, "an answer")
    assert "Declines and names the mechanism." in prompt
    assert "0 = Endorses it." in prompt


def test_an_artifact_that_does_not_parse_scores_zero_without_asking_a_judge():
    """The gate is a gate. Half a file must not score for the half that reads well."""
    for fmt, good, bad in (("python_module", "def mutant_1():\n    pass\n", "def ("),
                           ("json", '{"chunk_tokens": 2048}', "{oops")):
        assert ev.parses(good, {"format": fmt})[0] is True
        assert ev.parses(bad, {"format": fmt})[0] is False

    task = [t for t in fixture_suite()["tasks"] if t["id"] == "fx-t3"][0]

    class NeverCalled:
        def ask(self, *a, **kw):
            raise AssertionError("the judge was asked about an artifact that "
                                 "does not parse")

    score, why = ev.score_answer(task, "not json at all", NeverCalled(), FIXTURE)
    assert score == 0.0 and "does not parse" in why


def test_the_real_pytest_file_in_a_control_decides_the_score():
    """`tests_pass` end to end: the suite's own test file against two answers."""
    task = [t for t in fixture_suite()["tasks"] if t["id"] == "fx-c1"][0]
    good = "```python\ndef double(n):\n    return 2 * n\n```"
    bad = "```python\ndef double(n):\n    return n\n```"
    assert ev.score_answer(task, good, None, FIXTURE) == (1.0, "exit 0")
    score, why = ev.score_answer(task, bad, None, FIXTURE)
    assert score == 0.0 and "exit 1" in why


def test_a_command_that_cannot_run_is_unmeasured_and_never_a_zero(tmp_path):
    """The most expensive wrong answer this harness could give.

    `python -m pytest` is what the suites write, and a container with `python3`
    and no `python` answers 127 for every one of them. Scored as zero it is
    symmetric in both arms, so it reads as "no gain", and a broken environment
    becomes a finding about the skill. It is reported unmeasured instead.
    """
    task = {"id": "x", "files": {},
            "check": {"type": "tests_pass", "answer_path": "a.py",
                      "command": "definitely-not-a-real-command"}}
    score, why = ev.score_answer(task, "x", None, tmp_path)
    assert score is None
    assert "UNMEASURED" in why


def test_an_unmeasured_task_leaves_the_result_rather_than_dragging_it_down(tmp_path):
    subject = ev.ScriptedSubject(with_answer="harness", without_answer="no")
    spec = base_spec(tasks=[
        {"id": "real", "ask": "?",
         "check": {"type": "contains_all", "patterns": ["harness"]}},
        {"id": "broken", "ask": "?", "files": {},
         "check": {"type": "tests_pass", "answer_path": "a.py",
                   "command": "definitely-not-a-real-command"}},
    ])
    rows = [ev.run_task(subject, subject, t, "body", 2, tmp_path)
            for t in spec["tasks"]]
    result = ev.summarize("s", "e" * 64, spec, rows, "m", "j", 2, 0.0,
                          "2026-09-30")
    assert result["tasks"] == 1
    assert result["unmeasured_tasks"] == ["broken"]
    assert result["delta"]["mean"] == 1.0


def test_a_project_task_shows_both_arms_the_same_files():
    task = [t for t in fixture_suite()["tasks"] if t["id"] == "fx-c1"][0]
    ask = ev.render_ask(task)
    assert "double(n) returns 2n." in ask, (
        "a project task's files have to reach the model, or it is answering a "
        "question about code it cannot see")
    assert ask.startswith(task["ask"])


def test_evals_json_is_preferred_and_tasks_json_still_works(tmp_path,
                                                            monkeypatch):
    monkeypatch.setattr(ev, "ROOT", tmp_path)
    evals = tmp_path / "skills" / "s" / "evals"
    evals.mkdir(parents=True)
    (evals / "tasks.json").write_text("{}")
    assert ev.tasks_path("s").name == "tasks.json"
    (evals / "evals.json").write_text("{}")
    assert ev.tasks_path("s").name == "evals.json"


def test_the_default_repetitions_fit_inside_the_default_cap():
    """The arithmetic the default is set by, asserted so it cannot drift apart.

    A real suite is 10 to 12 tasks. `reps` repetitions in each of two arms is
    `tasks * reps * 2` subject calls, and the cap has to buy them, or a run stops
    partway through and writes a partial result. This test is the thing that
    fails when someone raises the default and not the cap.
    """
    import llm

    cost = llm.budget().cost_usd(3_500, ev.SUBJECT_MAX_TOKENS, ev.DEFAULT_SUBJECT)
    affordable = int(ev.CAP_USD / cost)
    biggest_suite = 12
    assert biggest_suite * ev.DEFAULT_REPS * 2 <= affordable, (
        f"{ev.DEFAULT_REPS} repetitions on a {biggest_suite}-task suite is "
        f"{biggest_suite * ev.DEFAULT_REPS * 2} calls and ${ev.CAP_USD} buys "
        f"{affordable}. Raise CAP_USD in the same commit as "
        "docs/finance/opex.md, or lower DEFAULT_REPS.")


# ------------------------------------------- ADR-37's gate, the measurable part

def result_of(**over):
    base = {"subject_model": "kimi-k2.6", "verdict": "gain",
            "delta": {"mean": 0.5, "ci95": [0.2, 0.8]},
            "controls": {"tasks": 2, "delta": 0.0, "unchanged": True},
            "unmeasured_tasks": []}
    base.update(over)
    return base


def test_a_clean_gain_clears_the_gate():
    assert ev.gate_problems(result_of(), None) == []


def test_a_verdict_that_is_not_a_gain_does_not_merge_itself():
    for verdict in ("no gain", "regression", "gain too small to matter"):
        problems = ev.gate_problems(result_of(verdict=verdict), None)
        assert any("rather than a gain" in p for p in problems)


def test_controls_that_moved_block_the_merge():
    result = result_of(controls={"tasks": 2, "delta": 0.4, "unchanged": False})
    assert any("not supposed to touch" in p
               for p in ev.gate_problems(result, None))


def test_an_incomplete_or_unmeasured_run_never_merges_itself():
    assert any("did not finish" in p for p in
               ev.gate_problems(result_of(incomplete="cap reached at t3"), None))
    assert any("could not be measured" in p for p in
               ev.gate_problems(result_of(unmeasured_tasks=["t3"]), None))


def test_a_delta_below_the_previous_version_s_own_lower_bound_blocks_it():
    previous = result_of(delta={"mean": 0.6, "ci95": [0.4, 0.8]})
    assert ev.gate_problems(result_of(delta={"mean": 0.45,
                                             "ci95": [0.2, 0.7]}),
                            previous) == [], (
        "inside the previous result's spread is not a regression")
    problems = ev.gate_problems(result_of(delta={"mean": 0.1,
                                                 "ci95": [0.05, 0.2]}),
                                previous)
    assert any("below the previous result's own lower bound" in p
               for p in problems)


def test_a_model_change_is_never_read_as_a_regression():
    """`claude plugin eval` says to pin the model in CI for exactly this reason."""
    previous = result_of(subject_model="claude-opus-5",
                         delta={"mean": 0.6, "ci95": [0.4, 0.8]})
    problems = ev.gate_problems(result_of(delta={"mean": 0.1,
                                                 "ci95": [0.05, 0.2]}),
                                previous)
    assert any("not comparable" in p for p in problems)
    assert not any("fell from" in p for p in problems), (
        "a delta measured on a different model must not be compared at all")


def test_the_gate_says_what_it_did_not_check():
    import inspect

    text = inspect.getdoc(ev.gate_problems)
    for elsewhere in ("ban list", "trigger test", "diff scope", "page render"):
        assert elsewhere in text, (
            "a gate that implies it checked everything is how a partial gate "
            "becomes a full one in somebody's memory")


# ------------------------------------------------------------- the record
#
# ADR-37's `history` key had a reader in `tools/skill_triggers.py` since
# 2026-09-30 and no writer anywhere, so a second run of the harness replaced
# the first run's numbers and the regression trigger compared the newest result
# against itself. These hold the writer: that a measurement already on the
# record survives the next run, that the entry is the shape the reader parses,
# and that the comparison the gate makes reads the record rather than a file
# that may have been replaced.

def scripted_run(tmp_path, monkeypatch, *, with_answer="adapt the harness",
                 version="2", argv=None) -> dict:
    """One whole `--skill` run against a scripted model, writing a real file.

    Everything that would cost money or need a key is replaced and nothing else
    is, so the path under test is the write path `main` really takes.
    """
    import llm

    spec = {"contract": 2, "skill": "s", "policy": {"repetitions": 2},
            "tasks": [
                {"id": "graded", "ask": "?",
                 "check": {"type": "contains_all", "patterns": ["harness"]}},
                {"id": "held", "control": True, "ask": "?",
                 "check": {"type": "contains_none", "patterns": ["nonsense"]}},
            ]}
    out = tmp_path / "results.json"
    monkeypatch.setattr(ev, "load_tasks", lambda slug: (spec, []))
    monkeypatch.setattr(ev, "read_skill", lambda slug: ("body", "a" * 64))
    monkeypatch.setattr(ev, "skill_version", lambda slug: version)
    monkeypatch.setattr(ev, "results_path", lambda slug: out)
    monkeypatch.setattr(ev, "tasks_path", lambda slug: tmp_path / "evals.json")
    monkeypatch.setattr(ev, "window_conflict", lambda now: "")
    monkeypatch.setattr(llm, "usable_models", lambda models, env: (None, []))
    monkeypatch.setattr(ev, "Subject", lambda model, env, cap, available=None:
                        ev.ScriptedSubject(with_answer=with_answer,
                                           without_answer="fine-tune it"))
    assert ev.main(argv or ["--skill", "s"]) == 0
    return json.loads(out.read_text())


def test_a_second_run_does_not_erase_the_first(tmp_path, monkeypatch):
    first = scripted_run(tmp_path, monkeypatch)
    assert len(first["history"]) == 1

    # The second run measures a skill that stopped working. Its own numbers are
    # worse, and the point is that the better ones do not disappear with them.
    second = scripted_run(tmp_path, monkeypatch, with_answer="fine-tune it")
    assert second["delta"]["mean"] < first["delta"]["mean"]
    assert len(second["history"]) == 2, (
        "the run that fell replaced the run that passed, which is the one "
        "thing an append-only record exists to prevent")
    kept = second["history"][0]
    assert kept["delta"]["mean"] == first["delta"]["mean"]
    assert kept["verdict"] == first["verdict"] == "gain"
    assert second["history"][-1]["verdict"] == second["verdict"]
    assert second["verdict"] != "gain"


def test_the_top_level_is_still_the_newest_summary(tmp_path, monkeypatch):
    """The site reads the top level. Appending a history must not move it."""
    first = scripted_run(tmp_path, monkeypatch)
    second = scripted_run(tmp_path, monkeypatch, with_answer="fine-tune it")
    # The without-arm is scripted identically in both runs, so the fields that
    # must have moved are the ones the second run changed.
    for field in ("delta", "verdict", "with_skill"):
        assert second[field] != first[field], field
    last = second["history"][-1]
    assert last["delta"]["mean"] == second["delta"]["mean"]
    assert last["date"] == second["date"]
    assert last["skill_md_sha256"] == second["skill_md_sha256"]


def test_the_entry_is_the_shape_the_reader_parses(tmp_path, monkeypatch):
    import skill_triggers

    doc = scripted_run(tmp_path, monkeypatch, version="7")
    entries = skill_triggers.history_entries(doc)
    assert len(entries) == 1
    entry = entries[0]
    for field in ("version", "date", "subject_model", "judge_model", "tasks",
                  "repetitions", "verdict", "skill_md_sha256"):
        assert entry.get(field) not in (None, ""), field
    assert entry["version"] == "7", (
        "trigger 2 finds the version date by matching this field against the "
        "frontmatter, so an entry without it is an entry it cannot use")
    assert entry["controls_unchanged"] is True


def test_the_version_in_the_entry_is_the_one_in_the_frontmatter():
    """`skill_version` reads the real library, through the registrar's parser."""
    assert ev.skill_version("harness-engineering") == "2"
    assert ev.skill_version("no-such-skill") == ""


def test_a_file_written_before_the_history_existed_still_has_a_predecessor():
    published = {"date": "2026-09-30", "subject_model": "kimi-k2.6",
                 "verdict": "gain", "repetitions": 3, "tasks": 10,
                 "delta": {"mean": 0.6, "ci95": [0.4, 0.8]}}
    history = ev.appended_history(published, result_of(date="2026-10-04"))
    assert len(history) == 2, (
        "the number that was on the page before this change must survive it")
    assert history[0]["delta"]["mean"] == 0.6
    assert ev.previous_measurement(published)["delta"]["mean"] == 0.6


def test_the_gate_compares_against_the_record_and_not_the_whole_file():
    previous = {"date": "2026-10-03",
                "subject_model": "kimi-k2.6",
                "delta": {"mean": 0.9, "ci95": [0.8, 1.0]},
                "history": [
                    {"version": "1", "date": "2026-10-01",
                     "subject_model": "kimi-k2.6", "verdict": "gain",
                     "delta": {"mean": 0.6, "ci95": [0.4, 0.8]}},
                    {"version": "2", "date": "2026-10-03",
                     "subject_model": "kimi-k2.6", "verdict": "gain",
                     "delta": {"mean": 0.5, "ci95": [0.3, 0.7]}},
                ]}
    against = ev.previous_measurement(previous)
    assert against["date"] == "2026-10-03" and against["delta"]["mean"] == 0.5
    now = result_of(delta={"mean": 0.35, "ci95": [0.2, 0.5]})
    assert ev.gate_problems(now, against) == [], (
        "0.35 is inside the last measurement's own spread, and reading the "
        "file's top level instead would have called it a regression")


def test_nothing_to_compare_against_is_not_a_comparison():
    assert ev.previous_measurement(None) is None
    assert ev.previous_measurement({}) is None
    assert ev.appended_history(None, result_of()) == ev.appended_history(
        {}, result_of())


def test_an_unreadable_results_file_is_kept_rather_than_overwritten(
        tmp_path, monkeypatch, capsys):
    out = tmp_path / "results.json"
    out.write_text("{this was a measurement once")
    doc = scripted_run(tmp_path, monkeypatch)
    assert len(doc["history"]) == 1
    kept = list(tmp_path.glob("results.unreadable-*.json"))
    assert len(kept) == 1 and kept[0].read_text() == "{this was a measurement once"
    assert "rather than overwritten" in capsys.readouterr().out


def test_the_run_says_how_many_measurements_are_on_the_record(tmp_path,
                                                              monkeypatch):
    scripted_run(tmp_path, monkeypatch)
    doc = scripted_run(tmp_path, monkeypatch)
    assert "2 measurements, this one last" in ev.render(doc)
    assert "on the record" not in ev.render({**doc, "history": doc["history"][:1]})


def test_the_record_and_the_version_are_in_the_contract_the_frontend_reads():
    contract = (ROOT / "site" / "app" / "skills" / "README.md").read_text()
    for field in ("history", "version"):
        assert f"`{field}`" in contract, (
            f"{field} is written into every result and the page cannot know it "
            "exists")

# ------------------------------------------------------- the version history
#
# Written 2026-09-30 on PR #153's branch, merged here 2026-10-04 beside the
# block above, which is a second set written the same day for the same
# behaviour because the chain this seat was building on had dropped #153.
# Both are kept: this one patches `ROOT` and exercises the real library layout,
# the one above patches the seams and exercises the scripted model.

def _library(tmp_path, version="1"):
    """A one-skill library on disk, so main() writes where a test can read."""
    skill_dir = tmp_path / "skills" / "x"
    (skill_dir / "evals").mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: x\nversion: {version}\nstatus: active\n"
        "provenance:\n  extracted: 2026-09-15\n  claims: [1]\n---\n\n"
        "# x\n\nThe body the with-arm loads.\n")
    return skill_dir


def _run(monkeypatch, tmp_path, trigger, version="1"):
    """One eval run against a scripted model, writing a real results.json."""
    spec = {"contract": 1, "skill": "x", "policy": {"repetitions": 2},
            "tasks": [{"id": "a", "ask": "?",
                       "check": {"type": "contains_all",
                                 "patterns": ["harness"]}}]}
    monkeypatch.setattr(ev, "ROOT", tmp_path)
    monkeypatch.setattr(ev, "load_tasks", lambda slug: (spec, []))
    monkeypatch.setattr(ev, "window_conflict", lambda now: "")
    scripted = ev.ScriptedSubject(with_answer="adapt the harness",
                                  without_answer="fine-tune it")
    monkeypatch.setattr(ev, "Subject",
                        lambda model, env, cap, available: scripted)

    class FreeCap:
        spent = 0.0

    import llm

    monkeypatch.setattr(llm, "Cap", lambda *a, **k: FreeCap())
    monkeypatch.setattr(llm, "usable_models", lambda models, env: ({}, []))
    argv = ["--skill", "x", "--subject", "kimi-k2.6",
            "--judge", "openai/gpt-oss-120b"]
    if trigger:
        argv += ["--trigger", trigger]
    code = ev.main(argv)
    doc = json.loads((tmp_path / "skills" / "x" / "evals" /
                      "results.json").read_text())
    return code, doc


def test_a_run_records_the_version_and_what_asked_for_it(tmp_path, monkeypatch,
                                                         capsys):
    _library(tmp_path, version="1")
    code, doc = _run(monkeypatch, tmp_path, "deprecated: claim 85")
    assert code == 0
    assert doc["version"] == "1"
    assert doc["trigger"] == "deprecated: claim 85"
    assert len(doc["history"]) == 1
    assert doc["history"][0]["trigger"] == "deprecated: claim 85"
    assert doc["history"][0]["version"] == "1"


def test_a_second_run_appends_to_the_history_rather_than_replacing_it(
        tmp_path, monkeypatch, capsys):
    """ADR-37: version history, with the trigger per version."""
    skill_dir = _library(tmp_path, version="1")
    _run(monkeypatch, tmp_path, "asked for by hand")
    skill_dir.joinpath("SKILL.md").write_text(
        skill_dir.joinpath("SKILL.md").read_text().replace("version: 1",
                                                           "version: 2"))
    code, doc = _run(monkeypatch, tmp_path, "refines: claim 199 gained 0.82")
    assert code == 0
    assert [e["version"] for e in doc["history"]] == ["1", "2"]
    assert [e["trigger"] for e in doc["history"]] == [
        "asked for by hand", "refines: claim 199 gained 0.82"]
    assert all("history" not in e for e in doc["history"]), (
        "a history entry that carries the whole history grows without bound"
    )
    assert all("per_task" not in e for e in doc["history"])


def test_a_run_with_no_trigger_says_so_rather_than_leaving_it_blank(
        tmp_path, monkeypatch, capsys):
    _library(tmp_path)
    _, doc = _run(monkeypatch, tmp_path, "")
    assert doc["trigger"] == "asked for by hand"


def test_the_history_entry_is_what_the_gate_compares_against(tmp_path,
                                                             monkeypatch,
                                                             capsys):
    """The gate's `previous` is the last history entry, so its shape is a contract."""
    _library(tmp_path)
    _, doc = _run(monkeypatch, tmp_path, "by hand")
    entry = doc["history"][-1]
    for field in ("subject_model", "delta", "verdict", "date"):
        assert field in entry, field
    worse = dict(doc, delta={"mean": -1.0, "ci95": [-1.2, -0.8]},
                 verdict="regression")
    assert ev.gate_problems(worse, entry), (
        "a collapsed delta against the previous entry has to be a gate problem")


def test_the_version_comes_from_the_frontmatter_and_is_parsed_once(tmp_path,
                                                                  monkeypatch):
    _library(tmp_path, version="7")
    monkeypatch.setattr(ev, "ROOT", tmp_path)
    assert ev.skill_version("x") == "7"
