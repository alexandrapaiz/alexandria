"""ADR-13's validator: its judgments, its delegation, its evidence, its wiring.

    python3 -m pytest tests/test_panel_validator.py -q

This reviewer is the easiest of the three to test and that is its distinguishing
property rather than a coincidence. The provenance reviewer needs a database for
most of its duties and the adversary needs one for all of them; everything this
one decides is a file in the repository, so every test below writes the files
and reads the verdict. There is no mode of this reviewer that a test cannot
reach.

Five kinds of test.

**The judgments.** Each duty gets the case that must fail and the case that must
not, because a reviewer that fails everything is as useless as one that passes
everything. The library today fails all six, so the passing cases are the ones
that matter most here: they are the only evidence that the gate will ever open.

**The delegation.** The direction of the A/B result is not decided in this file.
`tools/skill_eval.py`'s `gate_problems` is the organization's one answer to "why
is this result not a pass", and a second copy of that question would give the
panel and the revision gate two answers to one question. The test for that is a
test that the call actually happens, not that the answers happen to agree today.

**The pre-registration check**, which is new machinery rather than a reading of
old machinery. Rule 1 of docs/product/skill-validation.md §V5 says the policy is
fixed before the run so nobody tunes until green, and nothing in this repository
checked it until this reviewer. The suite carries the policy as written and the
result carries the copy that ran, so the check is that they agree.

**The SQL.** One INSERT, parsed with libpg_query and resolved against
`db/schema.sql`, the same instrument the other two reviewers' suites use.

**The wiring**, in two halves that are both easy to get wrong. The Modal image
has to carry two more files, and `skills_from_github` has to fetch the `evals/`
files: a validator pointed at a directory nobody wrote reports every skill
unmeasured in a voice indistinguishable from the truth.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "pipeline"))

import panel                        # noqa: E402
import panel_validator as val       # noqa: E402
import skill_eval                   # noqa: E402
import skill_registrar as registrar  # noqa: E402
import skill_revision as job        # noqa: E402

SCHEMA = (ROOT / "db" / "schema.sql").read_text()


# --------------------------------------------------------------- the SQL

def _walk(node, out):
    """Every AST node under `node`. Same shape as tests/test_graph_audit.py's.

    Written out again rather than imported, for the reason that file gives: a
    walker that silently returns nothing makes every assertion below vacuously
    true, and that is what its own first draft did.
    """
    ast = pytest.importorskip("pglast").ast
    if isinstance(node, ast.Node):
        out.append(node)
        for slot in node.__slots__:
            _walk(getattr(node, slot, None), out)
    elif isinstance(node, (list, tuple)):
        for item in node:
            _walk(item, out)
    return out


def _parse(sql):
    pglast = pytest.importorskip(
        "pglast", reason="pip install -r requirements-dev.txt")
    return pglast.parse_sql(sql.replace("%s", "$1"))


def _schema_names():
    pglast = pytest.importorskip("pglast")
    relations, columns = set(), set()
    for node in _walk(pglast.parse_sql(SCHEMA), []):
        name = type(node).__name__
        if name in ("CreateStmt", "ViewStmt"):
            rel = getattr(node, "relation", None) or getattr(node, "view", None)
            if rel is not None:
                relations.add(rel.relname)
        if name == "ColumnDef" and node.colname:
            columns.add(node.colname)
        if name == "ResTarget" and node.name:
            columns.add(node.name)
    return relations, columns


def test_the_walker_actually_walks():
    assert len(_walk(_parse(val.QUERIES["file"]), [])) > 5


@pytest.mark.parametrize("name", sorted(val.QUERIES))
def test_every_statement_parses(name):
    assert len(_parse(val.QUERIES[name])) == 1, "one statement per entry"


def test_this_reviewer_reads_nothing_and_writes_one_table():
    """Its whole input is files, so a SELECT here would be a design error."""
    assert list(val.QUERIES) == ["file"]
    stmt = _parse(val.QUERIES["file"])[0].stmt
    assert type(stmt).__name__ == "InsertStmt"
    assert stmt.relation.relname == "panel_verdicts"


def test_every_relation_and_column_the_validator_names_exists():
    relations, columns = _schema_names()
    for name, sql in val.QUERIES.items():
        nodes = _walk(_parse(sql), [])
        for node in nodes:
            if type(node).__name__ == "RangeVar":
                assert node.relname in relations, (
                    f"{name} writes {node.relname}, which db/schema.sql does "
                    "not create")
        for node in nodes:
            if type(node).__name__ != "ColumnRef":
                continue
            fields = [f.sval for f in node.fields if hasattr(f, "sval")]
            if fields:
                assert fields[-1] in columns, (
                    f"{name} names a column {fields[-1]}, which is not in "
                    "db/schema.sql")


def test_it_files_under_its_own_reviewer_name():
    """A verdict filed under a sibling's name would make a panel of one read as
    two agreeing reviewers, which is the one arithmetic error
    `panel_consensus` cannot survive.
    """
    assert "'validator'" in val.QUERIES["file"]
    assert "'provenance'" not in val.QUERIES["file"]
    assert "'adversary'" not in val.QUERIES["file"]
    check = SCHEMA.split("check (reviewer in (")[1].split(")")[0]
    assert "'validator'" in check, "the schema does not admit this reviewer"


def test_the_panel_is_now_the_size_its_own_gate_counts_to():
    """`panel_consensus` has required three passes since the table was written.

    Until this reviewer existed the most any skill could earn was two, so the
    arithmetic that decides a merge was unreachable in principle rather than
    merely unmet. This asserts the two numbers agree: the gate's 3, and the
    three reviewer names the column admits.
    """
    gate = SCHEMA.split("create or replace view panel_consensus as")[1]
    gate = gate.split(";")[0]
    assert "= 3" in gate
    check = SCHEMA.split("check (reviewer in (")[1].split(")")[0]
    assert sorted(n.strip().strip("'") for n in check.split(",")) == [
        "adversary", "provenance", "validator"]
    for module in ("panel_provenance", "panel_adversary", "panel_validator"):
        assert (ROOT / "tools" / f"{module}.py").exists(), (
            f"the gate counts to three and {module} is not written")




def _table_columns(table: str) -> set:
    """The columns db/schema.sql gives one table, not the schema's whole union.

    `_schema_names` flattens every column name in the file into one set, which
    is the right looseness for a SELECT whose FROM this test does not resolve.
    It is too loose for an INSERT: `panel_verdicts (model)` would pass against a
    `model` column that belongs to `triage_log`.
    """
    pglast = pytest.importorskip("pglast")
    for node in _walk(pglast.parse_sql(SCHEMA), []):
        if type(node).__name__ != "CreateStmt":
            continue
        relation = getattr(node, "relation", None)
        if relation is None or relation.relname != table:
            continue
        return {c.colname for c in _walk(node, [])
                if type(c).__name__ == "ColumnDef" and c.colname}
    raise AssertionError(f"db/schema.sql creates no table named {table}")


def test_the_schema_reader_finds_the_table_it_is_asked_for():
    """`_table_columns` returning an empty set would make the test below
    vacuously true, which is the failure mode `_walk`'s own guard exists for.
    """
    assert "target_sha" in _table_columns("panel_verdicts")
    assert "to_claim" not in _table_columns("panel_verdicts")


def test_every_column_this_reviewer_writes_exists_in_panel_verdicts():
    """The half the SELECT tests above do not reach, and the only half that
    matters for what a reviewer *writes*.

    An INSERT's target columns are `ResTarget` nodes in `stmt.cols`, not
    `ColumnRef`s, so the column test above never looked at them. Renaming
    `panel_verdicts.target_sha` left all three reviewer suites green and would
    have been discovered by a 16:00 UTC cron raising on every verdict it tried
    to file. Recorded as INC-2026-10-03-reviewer-suites-never-resolved-the-
    insert-columns.
    """
    columns = _table_columns("panel_verdicts")
    stmt = _parse(val.QUERIES["file"])[0].stmt
    assert stmt.cols, "the INSERT names no columns, so the order is positional"
    for col in stmt.cols:
        assert col.name in columns, (
            f"this reviewer writes panel_verdicts.{col.name}, which "
            "db/schema.sql does not define")
    values = stmt.selectStmt.valuesLists[0]
    assert len(stmt.cols) == len(values), (
        f"{len(stmt.cols)} columns and {len(values)} values, so the row would be written into the wrong columns or not at all")


# ------------------------------------------------------- the judgments

class Row:
    """The four fields of a registrar row this reviewer reads."""

    def __init__(self, sha, slug="fixture", status="active", claim_ids=(1,)):
        self.slug = slug
        self.path = f"skills/{slug}"
        self.sha = sha
        self.skill_status = status
        self.claim_ids = list(claim_ids)


def library(tmp_path, body="# fixture\n", status="active", validated="",
            suite=None, result=None, slug="fixture", triggers=None):
    """A skills/ directory on disk, and the registrar row that describes it.

    Written as files rather than as objects on purpose: this reviewer's whole
    input is the filesystem, so a fixture that handed it parsed documents would
    be testing something the production path never does.
    """
    skills = tmp_path / "skills"
    directory = skills / slug
    directory.mkdir(parents=True)
    frontmatter = (f"---\nname: {slug}\nstatus: {status}\nprovenance:\n"
                   f'  validated: "{validated}"\n  claims: [1]\n---\n')
    (directory / "SKILL.md").write_text(frontmatter + body)
    raw = (directory / "SKILL.md").read_text()
    import hashlib
    sha = hashlib.sha256(raw.encode()).hexdigest()
    if suite is not None:
        (directory / "evals").mkdir(exist_ok=True)
        (directory / "evals" / "evals.json").write_text(json.dumps(suite))
    if result is not None:
        (directory / "evals").mkdir(exist_ok=True)
        if result.get("skill_md_sha256") == "THIS":
            result = dict(result, skill_md_sha256=sha)
        (directory / "evals" / "results.json").write_text(json.dumps(result))
    for name, doc in (triggers or {}).items():
        receipts = skills / "_validation" / "results"
        receipts.mkdir(parents=True, exist_ok=True)
        (receipts / name).write_text(json.dumps(doc))
    return skills, Row(sha, slug=slug, status=status)


def gained(**over):
    """A result document that should pass, in the shape `summarize` writes."""
    doc = {
        "contract": 1, "skill": "fixture", "skill_md_sha256": "THIS",
        "date": "2026-10-03", "subject_model": "kimi-k2.6",
        "judge_model": "openai/gpt-oss-120b", "repetitions": 5,
        "tasks": 6, "control_tasks": 2, "unmeasured_tasks": [],
        "spend_usd": 0.41,
        "delta": {"mean": 0.35, "ci95": [0.12, 0.58]},
        "min_delta_registered": 0.15, "verdict": "gain",
        "policy": {"min_delta": 0.15, "repetitions": 5,
                   "subject": "kimi-k2.6", "judge": "openai/gpt-oss-120b"},
        "controls": {"tasks": 2, "delta": 0.01, "ci95": [-0.04, 0.06],
                     "unchanged": True},
    }
    doc.update(over)
    return doc


def task(tid, control=False):
    """One task the harness would agree to run. `conformance` is strict about
    this shape and the reviewer now calls it, so a stub task would read as a
    suite the harness refuses rather than as a suite with a policy problem.
    """
    return {"id": tid, "kind": "treatment" if not control else "control",
            "form": "prompt", "prompt": f"the {tid} question",
            "check": {"type": "rubric",
                      "criteria": [{"id": "c1", "criterion": "declines",
                                    "anchors": {"0": "no", "2": "yes"}}]}}


def suite_for(**policy):
    base = {"min_delta": 0.15, "repetitions": 5, "subject": "kimi-k2.6",
            "judge": "openai/gpt-oss-120b"}
    base.update(policy)
    return {"skill": "fixture", "contract": 1, "policy": base,
            "tasks": [task("t1"), task("t2"), task("c1", control=True)]}


def verdict(tmp_path, **kwargs):
    skills, row = library(tmp_path, **kwargs)
    return val.review(skills_dir=skills, rows=[row])[0]


def checks(v, name):
    return [f for f in v["findings"] if f["check"] == name]


def test_a_measured_skill_that_gained_passes(tmp_path):
    """The case the whole gate exists for, and the only one that can open it."""
    v = verdict(tmp_path, suite=suite_for(), result=gained())
    assert v["verdict"] == "pass", v["findings"]
    assert v["reviewer"] == "validator"
    assert v["target_sha"]
    assert not any(f["severity"] == "fail" for f in v["findings"])


def test_a_skill_with_no_suite_and_no_result_is_unmeasured_and_never_a_pass(tmp_path):
    v = verdict(tmp_path)
    assert v["verdict"] == "fail"
    assert checks(v, "trial-exists")[0]["severity"] == "unknown"
    assert "no evals/ suite and no result" in checks(v, "trial-exists")[0]["detail"]


def test_a_suite_with_no_result_says_the_trial_was_written_and_never_run(tmp_path):
    """The two absences want different people, so they read differently.

    No suite is the skill seat's work. A suite with no result is waiting on
    somebody running `tools/skill_eval.py`, and a reviewer that printed one
    sentence for both would send every reader to the wrong seat half the time.
    """
    v = verdict(tmp_path, status="draft", suite=suite_for())
    detail = checks(v, "trial-exists")[0]["detail"]
    assert "written and never run" in detail
    assert "pre-registered" not in detail, (
        "this sentence must not call the suite pre-registered, because the "
        "finding below it is often that the suite registered nothing")
    assert "tools/skill_eval.py" in detail
    assert v["verdict"] == "unknown"


def test_a_draft_skill_with_no_eval_is_honest_and_an_active_one_is_not(tmp_path):
    """ADR-36 part 2, verbatim: a skill with no eval is draft, never active.

    The discriminating pair. If this check fired on both, it would be a
    complaint about the library having no evals rather than a reading of the
    rule, and the rule is the only reason it is a `fail` rather than a note.
    """
    draft = verdict(tmp_path / "a", status="draft")
    assert checks(draft, "status-vs-eval") == []
    assert draft["verdict"] == "unknown"

    active = verdict(tmp_path / "b", status="active")
    assert checks(active, "status-vs-eval")[0]["severity"] == "fail"
    assert "ADR-36" in checks(active, "status-vs-eval")[0]["detail"]
    assert active["verdict"] == "fail"


def test_an_active_skill_with_a_result_does_not_trip_the_status_rule(tmp_path):
    v = verdict(tmp_path, status="active", suite=suite_for(), result=gained())
    assert checks(v, "status-vs-eval") == []


def test_a_result_measured_against_an_earlier_revision_is_unknown(tmp_path):
    """What `target_sha` exists for, one level down.

    Without this a skill could earn three passes and then be edited, and the
    merge would ship the edit. A stale receipt is the commonest way that
    happens, because editing a skill is cheap and re-running its eval is not.
    """
    v = verdict(tmp_path, suite=suite_for(),
                result=gained(skill_md_sha256="0" * 64))
    finding = checks(v, "trial-pins-text")[0]
    assert finding["severity"] == "unknown"
    assert "earlier revision" in finding["detail"]
    assert "000000000000" in finding["detail"]
    assert v["verdict"] == "unknown"


def test_a_result_that_pins_no_text_at_all_is_unknown(tmp_path):
    v = verdict(tmp_path, suite=suite_for(), result=gained(skill_md_sha256=""))
    finding = checks(v, "trial-pins-text")[0]
    assert finding["severity"] == "unknown"
    assert "no skill_md_sha256" in finding["detail"]


def test_a_matching_sha_is_recorded_with_its_date(tmp_path):
    v = verdict(tmp_path, suite=suite_for(), result=gained())
    finding = checks(v, "trial-pins-text")[0]
    assert finding["severity"] == "note"
    assert "2026-10-03" in finding["detail"]


@pytest.mark.parametrize("word", ["no gain", "regression",
                                  "gain too small to matter"])
def test_a_trial_that_did_not_move_behaviour_fails(tmp_path, word):
    """ADR-13: passes only if behavior moves in the direction the evidence
    supports. "Gain too small to matter" is in this list deliberately: a skill
    earns its place in a context window or it does not.
    """
    v = verdict(tmp_path / word.replace(" ", "-"), suite=suite_for(),
                result=gained(verdict=word))
    fails = [f for f in checks(v, "trial-direction") if f["severity"] == "fail"]
    assert fails and word in fails[0]["detail"]
    assert v["verdict"] == "fail"


def test_a_run_that_did_not_finish_fails(tmp_path):
    v = verdict(tmp_path, suite=suite_for(),
                result=gained(incomplete="cap reached at task 4"))
    assert any("cap reached" in f["detail"]
               for f in checks(v, "trial-direction"))
    assert v["verdict"] == "fail"


def test_controls_that_moved_fail_because_the_skill_touched_what_it_should_not(tmp_path):
    v = verdict(tmp_path, suite=suite_for(),
                result=gained(controls={"tasks": 2, "delta": 0.4,
                                        "ci95": [0.2, 0.6],
                                        "unchanged": False}))
    assert any("control tasks moved" in f["detail"]
               for f in checks(v, "trial-direction"))
    assert v["verdict"] == "fail"


def test_the_direction_is_decided_by_the_harness_and_not_by_this_file(tmp_path,
                                                                     monkeypatch):
    """The delegation, asserted as a call rather than as agreement.

    `gate_problems` is one answer to "why is this result not a pass", shared
    with the ADR-37 revision gate. Two copies would let the panel fail a skill
    the revision gate passes. A test that only compared today's answers would
    stay green the day somebody reimplemented it here.
    """
    monkeypatch.setattr(skill_eval, "gate_problems",
                        lambda result, previous: ["a synthetic problem"])
    v = verdict(tmp_path, suite=suite_for(), result=gained())
    assert any(f["detail"] == "a synthetic problem"
               for f in checks(v, "trial-direction"))
    assert v["verdict"] == "fail"

    source = (ROOT / "tools" / "panel_validator.py").read_text()
    assert "skill_eval.gate_problems(" in source
    for word in ("regression", "no gain", "gain too small"):
        assert f'"{word}"' not in source, (
            "the verdict vocabulary is being re-decided here instead of read "
            "from the harness that computed the numbers")


def test_the_delta_is_recorded_with_its_spread_and_never_as_a_point(tmp_path):
    """Rule 2 of §V5: counts with an interval, never a bare percentage."""
    v = verdict(tmp_path, suite=suite_for(), result=gained())
    note = [f for f in checks(v, "trial-direction")
            if f["severity"] == "note"][0]
    assert "0.35" in note["detail"] and "[0.12, 0.58]" in note["detail"]
    assert "kimi-k2.6" in note["detail"] and "6 tasks" in note["detail"]


# ------------------------------------------------- the pre-registration

def test_a_threshold_edited_after_the_run_fails(tmp_path):
    """Rule 1, and the thing nothing in this repository checked until now.

    The only edit this direction rewards is one made after seeing the numbers:
    a delta of 0.16 misses a registered 0.2 and clears a 0.15 written in
    afterwards. The result carries the policy that ran, so the two disagree and
    that disagreement is the whole evidence.
    """
    v = verdict(tmp_path, suite=suite_for(min_delta=0.15),
                result=gained(policy={"min_delta": 0.2, "repetitions": 5,
                                      "subject": "kimi-k2.6",
                                      "judge": "openai/gpt-oss-120b"}))
    finding = checks(v, "trial-pre-registered")[0]
    assert finding["severity"] == "fail"
    assert "min_delta" in finding["detail"]
    assert v["verdict"] == "fail"


def test_repetitions_added_after_the_run_fail_too(tmp_path):
    v = verdict(tmp_path, suite=suite_for(repetitions=9),
                result=gained())
    assert checks(v, "trial-pre-registered")[0]["severity"] == "fail"


def test_a_policy_that_agrees_is_recorded_rather_than_assumed(tmp_path):
    v = verdict(tmp_path, suite=suite_for(), result=gained())
    finding = checks(v, "trial-pre-registered")[0]
    assert finding["severity"] == "note"
    assert "min_delta" in finding["detail"]


def test_prose_in_a_suite_can_be_edited_without_reading_as_tampering(tmp_path):
    """Only the keys that change what a number means are compared.

    A suite's author note or its `written` date moving is housekeeping. If
    every key counted, the check would fire on edits that cannot affect a
    threshold, and a gate that cries wolf is a gate seats learn to override.
    """
    suite = suite_for()
    suite["note"] = "rewritten for clarity on 2026-10-04"
    suite["author"] = "the skill seat"
    v = verdict(tmp_path, suite=suite, result=gained())
    assert checks(v, "trial-pre-registered")[0]["severity"] == "note"
    assert v["verdict"] == "pass"


def test_a_suite_the_harness_would_refuse_to_run_fails(tmp_path):
    """`conformance` is the harness's answer to "is this file runnable", and
    the reviewer reads it rather than keeping a second opinion.

    The refusal tested here used to be `suite_version: 2`, which is the number
    every real suite carries. The harness accepts 1 and 2 since 2026-10-04, so
    the case is now a version nobody writes, and the live case moved to
    `test_the_skill_seat_s_real_suite_shape_is_reported_the_way_it_is` below.
    """
    suite = suite_for()
    suite["contract"] = 99
    v = verdict(tmp_path, suite=suite, result=gained())
    finding = checks(v, "suite-runnable")[0]
    assert finding["severity"] == "fail"
    assert "contract is 99" in finding["detail"]
    assert v["verdict"] == "fail"


def test_the_version_every_real_suite_carries_is_not_a_refusal(tmp_path):
    """The eight suites on #151, #152 and #159 all say `suite_version: 2`."""
    suite = suite_for()
    suite["contract"] = 2
    v = verdict(tmp_path, suite=suite, result=gained())
    assert checks(v, "suite-runnable") == [], (
        "the version the suites are written in is not a reason to refuse them")


def test_the_skill_seat_s_real_suite_shape_is_reported_the_way_it_is(tmp_path):
    """The format the skill seat actually wrote, not the one this suite invents.

    Written out here from `skills/harness-engineering/evals/evals.json` on
    `alexandria-skill/2026-09-30-window`: `suite_version: 2`, the two model
    names at the top level, and no `policy` block at all. A reviewer that read
    only `policy` would compare `None` against the result's numbers on every
    key and report four disagreements, which is an accusation of tampering
    against a file nobody tampered with. Two findings, each naming its own
    cause, is the correct reading.
    """
    suite = {"skill": "fixture", "suite_version": 2, "written": "2026-09-30",
             "author": "the skill seat", "subject_model": "kimi-k2.6",
             "judge": "openai/gpt-oss-120b",
             "tasks": [task("t1"), task("t2"), task("c1", control=True)]}
    v = verdict(tmp_path, suite=suite, result=gained())

    runnable = checks(v, "suite-runnable")
    assert not any("contract" in f["detail"] for f in runnable), (
        "the harness speaks this suite's version, so the version is not the "
        "finding")
    assert len(runnable) == 1 and "policy.repetitions" in runnable[0]["detail"], (
        "one problem is left on the real shape and it is the one line the "
        "author writes")

    registration = checks(v, "trial-pre-registered")
    assert len(registration) == 1, "one cause, one finding"
    detail = registration[0]["detail"]
    assert "registers no" in detail and "min_delta" in detail
    assert "disagree" not in detail, (
        "a suite that registered nothing is not a suite that was edited")
    assert "subject_model" in detail and "top level" in detail, (
        "the finding has to tell the skill seat the fix is a move")


def test_a_missing_key_and_an_edited_key_are_two_different_findings(tmp_path):
    suite = suite_for()
    del suite["policy"]["min_delta"]
    suite["policy"]["repetitions"] = 9
    v = verdict(tmp_path, suite=suite, result=gained())
    details = [f["detail"] for f in checks(v, "trial-pre-registered")]
    assert len(details) == 2
    assert any("registers no ['min_delta']" in d for d in details)
    assert any("repetitions: the run used 5" in d for d in details)


def test_neither_reviewer_nor_harness_invents_the_repetitions(tmp_path):
    """`normalize` supplied a repetitions default until 2026-10-04.

    This check read the raw suite to get around that, and the docstring said
    why: a check reading the normalized suite would find a repetitions value on
    every file in the library and report every one of them as compliant with
    the rule they break. That was the quietest possible way for a gate to be
    useless, and `skill_eval.conformance` was in exactly that state, because it
    is handed the normalized suite and has no raw one to read.

    Both halves are asserted here. Reading raw still works, and there is no
    longer a default to read around.
    """
    import skill_eval as ev
    suite = suite_for()
    del suite["policy"]["repetitions"]
    assert "repetitions" not in ev.normalize(suite)["policy"], (
        "a number the author did not write is a number the run chose")
    v = verdict(tmp_path, suite=suite, result=gained())
    assert any("repetitions" in f["detail"]
               for f in checks(v, "trial-pre-registered")
               if f["severity"] == "fail")
    assert any("repetitions" in f["detail"]
               for f in checks(v, "suite-runnable")
               if f["severity"] == "fail"), (
        "and the harness refuses to run it, which is the half that was dead")


def test_a_result_with_no_suite_cannot_have_its_registration_checked(tmp_path):
    v = verdict(tmp_path, result=gained())
    finding = checks(v, "trial-pre-registered")[0]
    assert finding["severity"] == "unknown"
    assert "rule 1 cannot be checked" in finding["detail"]
    assert v["verdict"] == "unknown"


def test_the_alias_filename_the_harness_accepts_is_read_here_too(tmp_path):
    """`tools/skill_eval.py` reads `evals.json` and accepts `tasks.json`.

    A reviewer looking for only one of them would report a skill unmeasured
    that is measured, which is the kind of wrong that never raises.
    """
    assert val.TASK_FILENAMES == skill_eval.TASK_FILENAMES
    skills, row = library(tmp_path, result=gained())
    (skills / "fixture" / "evals" / "tasks.json").write_text(
        json.dumps(suite_for()))
    v = val.review(skills_dir=skills, rows=[row])[0]
    assert checks(v, "trial-pre-registered")[0]["severity"] == "note"


def test_a_malformed_receipt_is_a_defect_and_not_an_absence(tmp_path):
    skills, row = library(tmp_path, suite=suite_for())
    (skills / "fixture" / "evals" / "results.json").write_text("{not json")
    v = val.review(skills_dir=skills, rows=[row])[0]
    finding = checks(v, "trial-exists")[0]
    assert finding["severity"] == "fail"
    assert "could not be read" in finding["detail"]


# ------------------------------------------------------- the validated field

def test_a_validated_field_with_no_receipt_cannot_be_read_or_reproduced(tmp_path):
    """Deliberately a different question from the provenance reviewer's.

    That one asks whether `panel_consensus` passed this text, which is a fact
    about the panel in the database. This asks whether the trial the field
    describes exists as a file. A skill can fail either without failing the
    other, and today harness-engineering's field names an A/B trial from
    2026-09-12, before the harness that would have produced a receipt existed.
    """
    v = verdict(tmp_path, validated="2026-09-12 A/B trial: it refused")
    finding = checks(v, "validated-has-a-receipt")[0]
    assert finding["severity"] == "unknown"
    assert "2026-09-12 A/B trial" in finding["detail"]


def test_a_validated_field_with_a_receipt_is_not_a_finding(tmp_path):
    v = verdict(tmp_path, validated="2026-10-03 trial", suite=suite_for(),
                result=gained())
    assert checks(v, "validated-has-a-receipt") == []
    assert v["verdict"] == "pass"


def test_an_empty_validated_field_is_not_a_finding(tmp_path):
    v = verdict(tmp_path, validated="", suite=suite_for(), result=gained())
    assert checks(v, "validated-has-a-receipt") == []


# ----------------------------------------------- evidence that never grades

def trigger_doc(sha, passed, cases, generated="2026-09-29",
                engine="lexical/2.1"):
    return {"generated": generated, "engine": engine,
            "suites": [{"skill": "fixture", "skill_sha256": sha,
                        "cases": [{"passed": i < passed}
                                  for i in range(cases)]}]}


def test_a_trigger_test_the_skill_failed_outright_never_moves_the_verdict(tmp_path):
    """The line the adversary's `evidence-grade` finding also stays on.

    The trigger test asks whether a skill fires, which is a different question
    from whether it helps, and no register sets a number for it. A reviewer
    that failed a skill on it would be legislating a bar the owner never set.
    """
    v = verdict(tmp_path, suite=suite_for(), result=gained(),
                triggers={"2026-09-29-lexical-2.1.json":
                          trigger_doc("", 0, 9)})
    finding = checks(v, "trigger-firing")[0]
    assert finding["severity"] == "note"
    assert "0 of 9" in finding["detail"]
    assert v["verdict"] == "pass"


def test_the_newest_receipt_wins_and_a_retired_engine_is_not_evidence(tmp_path):
    """A receipt from an engine the library does not run says nothing about the
    library, and the names lead with the date so the newest is pickable.
    """
    v = verdict(tmp_path, suite=suite_for(), result=gained(), triggers={
        "2026-09-22-lexical-2.1.json": trigger_doc("", 1, 9,
                                                   generated="2026-09-22"),
        "2026-09-29-lexical-2.1.json": trigger_doc("", 8, 9),
        "2026-09-30-lexical-3-experiment.json": trigger_doc(
            "", 2, 9, generated="2026-09-30", engine="lexical/3"),
    })
    detail = checks(v, "trigger-firing")[0]["detail"]
    assert "8 of 9" in detail and "2026-09-29" in detail


def test_a_trigger_receipt_measured_against_an_older_text_says_so(tmp_path):
    v = verdict(tmp_path, suite=suite_for(), result=gained(),
                triggers={"2026-09-29-lexical-2.1.json":
                          trigger_doc("deadbeefdeadbeef", 6, 6)})
    assert "an earlier text" in checks(v, "trigger-firing")[0]["detail"]


def test_a_trigger_receipt_on_this_text_says_that_instead(tmp_path):
    skills, row = library(tmp_path, suite=suite_for(), result=gained())
    receipts = skills / "_validation" / "results"
    receipts.mkdir(parents=True)
    (receipts / "2026-09-29-lexical-2.1.json").write_text(
        json.dumps(trigger_doc(row.sha[:16], 6, 6)))
    v = val.review(skills_dir=skills, rows=[row])[0]
    assert "the current text" in checks(v, "trigger-firing")[0]["detail"]


def test_no_receipt_at_all_is_said_rather_than_left_blank(tmp_path):
    v = verdict(tmp_path, suite=suite_for(), result=gained())
    assert checks(v, "trigger-firing")[0]["detail"] == (
        "no trigger-test receipt names this skill")


def test_the_spend_is_recorded_with_its_date(tmp_path):
    """The ledger asks for skill-eval spend in the opex table before it becomes
    a habit, and a verdict row is where the number is durable with its date.
    """
    v = verdict(tmp_path, suite=suite_for(), result=gained())
    finding = checks(v, "eval-spend")[0]
    assert finding["severity"] == "note"
    assert "0.41" in finding["detail"] and "2026-10-03" in finding["detail"]


def test_an_unmeasured_skill_records_no_spend(tmp_path):
    assert checks(verdict(tmp_path), "eval-spend") == []


# ----------------------------------------------------- shape of the findings

def test_every_character_a_finding_can_print_is_ascii(tmp_path):
    """These details go into a Modal log line and a notify mail, and
    INC-2026-09-26-slack-notify-jq-control-chars is what a clever character
    costs. Same assertion as the adversary's suite makes.
    """
    for v in (verdict(tmp_path / "a"),
              verdict(tmp_path / "b", suite=suite_for(),
                      result=gained(verdict="regression"))):
        for finding in v["findings"]:
            finding["detail"].encode("ascii")
            assert "\n" not in finding["detail"]


def test_a_finding_is_short_enough_to_read_in_a_log_line(tmp_path):
    for v in (verdict(tmp_path / "a"),
              verdict(tmp_path / "b", suite=suite_for(), result=gained())):
        for finding in v["findings"]:
            assert len(finding["detail"]) < 600, finding


def test_the_severities_are_the_panel_s_and_not_this_file_s():
    assert val.Finding is panel.Finding
    assert val.verdict_of is panel.verdict_of


# ----------------------------------------------------------- independence

def test_this_reviewer_imports_neither_sibling():
    """ADR-13's independence is about context, not code: a reviewer that read
    another's conclusions would make agreement an echo rather than evidence.
    """
    source = (ROOT / "tools" / "panel_validator.py").read_text()
    assert "panel_provenance" not in source.split('"""', 2)[2]
    assert "panel_adversary" not in source.split('"""', 2)[2]


def test_the_registrar_s_problems_are_not_repeated_by_this_reviewer(tmp_path):
    """One defect must not read as two independent findings."""
    skills, row = library(tmp_path, suite=suite_for(), result=gained())
    v = val.review(skills_dir=skills, rows=[row],
                   problems=["skills/fixture/SKILL.md is broken"])[0]
    assert not any("broken" in f["detail"] for f in v["findings"])


# ------------------------------------------- the reviewer over the library

def test_the_live_library_is_reviewable_and_fails_for_one_stated_reason():
    """A reviewer that only works on fixtures is a reviewer nobody can read.

    Every skill on this branch fails, and the assertion is about *why*: ADR-36
    part 2, with no eval behind an `active` status. If a future branch adds the
    evals, this test changes shape, and that is the point of asserting the
    reason rather than the count.
    """
    live, _ = registrar.read_skills()
    assert live, "the library has no skills to review"
    verdicts = val.review(rows=live)
    assert len(verdicts) == len(live)
    for v in verdicts:
        reasons = {f["check"] for f in v["findings"]
                   if f["severity"] == "fail"}
        if v["verdict"] == "fail":
            assert reasons <= {"status-vs-eval"}, (
                f"{v['target']} fails for a reason this test does not know "
                f"about: {reasons}")


def test_no_skill_on_this_branch_fails_a_check_this_reviewer_invented():
    """The companion to the provenance suite's version of this assertion.

    Every `fail` over the real library has to trace to a sentence in a register
    the owner accepted. `status-vs-eval` traces to ADR-36 part 2 and that is
    the only one allowed to fire here.
    """
    adr36 = (ROOT / "docs" / "decisions.md").read_text()
    section = adr36.split("## ADR-36")[1].split("## ADR-37")[0]
    assert "status: draft`, never `active`" in section
    for v in val.review(rows=registrar.read_skills()[0]):
        for finding in v["findings"]:
            if finding["severity"] == "fail":
                assert finding["check"] == "status-vs-eval"


def test_the_files_only_half_and_the_live_half_return_the_same_verdict():
    """This reviewer's distinguishing property, asserted rather than claimed.

    The provenance reviewer's file half runs a subset of its checks and the
    adversary has no file half at all. Here the database is needed only to
    write the row, so a pull request can see the whole verdict. If that stops
    being true, the docstring and the queued CI step both become wrong.
    """
    live, _ = registrar.read_skills()
    assert val.review(rows=live, conn=None) == val.review(
        rows=live, conn=object())


def test_the_cli_exit_codes_are_the_three_the_panel_shares():
    """0 nothing wrong, 1 a finding, 2 something could not be measured."""
    assert val.main(["--files-only"]) == 1, (
        "the library fails today, so this is 1; a day it returns 0 is a day "
        "every skill has an eval that gained")
    with pytest.raises(SystemExit):
        val.main(["--files-only", "--record"])


# ----------------------------------------------------------- the wiring

def test_the_image_carries_the_validator_and_the_harness_it_calls():
    """A missing line here is an ImportError at 16:00 UTC.

    `skill_eval.py` is in this list because the validator calls its
    `gate_problems`, and it imports nothing third-party at module scope, so it
    costs the image one file and nothing else.
    """
    source = (ROOT / "pipeline" / "skill_revision.py").read_text()
    for name in ("panel.py", "panel_provenance.py", "panel_adversary.py",
                 "panel_validator.py", "skill_eval.py", "skill_triggers.py"):
        assert f'.add_local_file("tools/{name}", "/root/{name}")' in source

    # The image mounts each tool as a flat file at /root, and `tools()` is what
    # imports two of them, so the directory it searches has to be the one the
    # image writes. This pairing is the whole content of the 2026-10-04 merge
    # between the branch that mounted a directory and the branch that mounted
    # files: either half alone imports nothing at 16:00 UTC.
    assert 'for path in ("/root", "/root/tools", here)' in source


def test_all_three_reviewers_run_in_the_daily_job_before_the_early_return():
    source = (ROOT / "pipeline" / "skill_revision.py").read_text()
    first = source.index("log.extend(reviewed(")
    second = source.index("log.extend(adversary_reviewed(")
    third = source.index("log.extend(validator_reviewed(")
    early = source.index("if not pending:")
    assert first < second < third < early
    assert source.index("triggers.live(conn") > third, (
        "the four triggers run after the panel and inside the same connection")


class FakeConn:
    """Enough of a connection to catch what the pass inserts."""

    def __init__(self):
        self.inserted = []

    def execute(self, sql, params):
        self.inserted.append(params)
        return _Result([(len(self.inserted),)])

    def commit(self):
        pass


class _Result:
    def __init__(self, rows):
        self.rows = rows

    def fetchone(self):
        return self.rows[0]

    def fetchall(self):
        return self.rows


def test_the_validator_files_its_own_row(tmp_path):
    """A pass that merged reviewers' findings into one row would make a panel
    of three read as a panel of one to `panel_consensus`.
    """
    skills, row = library(tmp_path, suite=suite_for(), result=gained())
    conn = FakeConn()
    log = job.validator_reviewed(conn, [row], [], skills, dry_run=False)
    assert len(conn.inserted) == 1
    assert conn.inserted[0][1] == "pass"
    assert conn.inserted[0][4], "the row carries no reviewer_sha"
    assert any(line.startswith("validator: 1 skills reviewed")
               for line in log)


def test_a_dry_run_files_nothing(tmp_path):
    skills, row = library(tmp_path, suite=suite_for(), result=gained())
    conn = FakeConn()
    log = job.validator_reviewed(conn, [row], [], skills, dry_run=True)
    assert conn.inserted == []
    assert any("no verdict row was filed" in line for line in log)


def test_a_validator_fail_reaches_the_owner_alarm(tmp_path):
    skills, row = library(tmp_path, status="active")
    log = job.validator_reviewed(FakeConn(), [row], [], skills, dry_run=False)
    alarms = [line for line in log if line.startswith(job.VERDICT_ALARM)]
    assert len(alarms) == 1 and "status-vs-eval" in alarms[0]


def test_the_reviewer_sha_is_the_sha_git_would_give():
    """The column exists so a verdict says which reviewer code judged, and
    asking git for it would leave it null on every row production ever files.
    """
    expected = subprocess.run(["git", "hash-object", "tools/panel_validator.py"],
                              cwd=ROOT, capture_output=True, text=True,
                              check=True)
    assert val.reviewer_sha() == expected.stdout.strip()


def test_all_three_reviewers_file_a_sha_rather_than_a_null():
    for name in ("panel_provenance", "panel_adversary", "panel_validator"):
        module = __import__(name)
        assert module.reviewer_sha(), f"{module.REVIEWER} files a null sha"


# ------------------------------------- the files the daily job has to fetch

class FakeGitHub:
    """The two calls `skills_from_github` makes, over a dict of paths."""

    def __init__(self, files, dirs):
        self.repo = "owner/repo"
        self.files = files
        self.dirs = dirs
        self.listed = []
        self.read = []

        outer = self

        class _Client:
            def get(self, url, params=None):
                path = url.split("/contents/", 1)[1]
                outer.listed.append(path)
                return _Resp(outer.dirs.get(path))

        self.client = _Client()

    def read_file(self, path, ref):
        self.read.append(path)
        if path not in self.files:
            raise RuntimeError(f"GET contents/{path} answered 404")
        return self.files[path], "blob"


class _Resp:
    def __init__(self, payload):
        self.payload = payload
        self.status_code = 200 if payload is not None else 404
        self.text = ""

    def json(self):
        return self.payload


def test_the_daily_job_fetches_the_receipts_its_third_reviewer_reads(tmp_path):
    """The failure this exists to prevent, stated as a test.

    `skills_from_github` wrote only SKILL.md. The skill seat merges six suites
    and six results, the daily reviewer keeps filing `unknown`, and the first
    person to notice is whoever eventually asks why a passing library never
    passed. That is merged-but-inert one level down.
    """
    root = tmp_path / "skills"
    (root / "fixture").mkdir(parents=True)
    gh = FakeGitHub(
        files={"skills/fixture/evals/evals.json": json.dumps(suite_for()),
               "skills/fixture/evals/results.json": json.dumps(gained())},
        dirs={"skills/fixture/evals": [
            {"type": "file", "name": "evals.json"},
            {"type": "file", "name": "results.json"},
            {"type": "file", "name": "README.md"}]})
    written = job.receipts_from_github(gh, "main", root, "fixture")
    assert written == ["evals.json", "results.json"]
    assert (root / "fixture" / "evals" / "results.json").exists()
    assert "skills/fixture/evals/README.md" not in gh.read, (
        "it read a file no reviewer opens")


def test_a_skill_with_no_evals_directory_is_not_an_error(tmp_path):
    """The honest majority state of the library on 2026-10-03, so absence here
    has to be silent rather than an exception inside the daily cron.
    """
    root = tmp_path / "skills"
    (root / "fixture").mkdir(parents=True)
    gh = FakeGitHub(files={}, dirs={})
    assert job.receipts_from_github(gh, "main", root, "fixture") == []
    assert not (root / "fixture" / "evals").exists()


def test_one_listing_call_per_skill_rather_than_three_reads(tmp_path):
    root = tmp_path / "skills"
    (root / "fixture").mkdir(parents=True)
    gh = FakeGitHub(files={}, dirs={})
    job.receipts_from_github(gh, "main", root, "fixture")
    assert gh.listed == ["skills/fixture/evals"]
    assert gh.read == []


def test_the_newest_trigger_receipt_is_fetched_and_only_that_one(tmp_path):
    """One file, not the directory. There are fifteen receipts and the reviewer
    reads exactly one, so fetching the rest is fourteen calls for one note.
    """
    root = tmp_path / "skills"
    root.mkdir(parents=True)
    names = ["2026-09-22-lexical-2.1.json", "2026-09-29-lexical-2.1.json",
             "2026-09-30-lexical-3-experiment.json",
             "2026-09-18-lexical-1-retired.json",
             "2026-09-29-lexical-2.1.txt"]
    gh = FakeGitHub(
        files={"skills/_validation/results/2026-09-29-lexical-2.1.json":
               json.dumps(trigger_doc("", 8, 9))},
        dirs={"skills/_validation/results": [{"type": "file", "name": n}
                                             for n in names]})
    picked = job.trigger_receipt_from_github(gh, "main", root)
    assert picked == "2026-09-29-lexical-2.1.json"
    assert len(gh.read) == 1
    assert (root / "_validation" / "results" / picked).exists()


def test_the_receipt_fetch_is_wired_into_the_read_from_main(tmp_path):
    source = (ROOT / "pipeline" / "skill_revision.py").read_text()
    fetch = source.index("def skills_from_github")
    body = source[fetch:source.index("EVAL_FILES =")]
    assert "receipts_from_github(gh, ref, root, row.slug)" in body
    assert "trigger_receipt_from_github(gh, ref, root)" in body


def test_the_files_the_fetch_names_are_the_files_the_reviewer_opens():
    """Two lists in two modules, and a reviewer looking for a name the fetch
    does not write reports every skill unmeasured in production only.
    """
    assert set(job.EVAL_FILES) == set(val.TASK_FILENAMES) | {
        val.RESULTS_FILENAME}


def test_the_validator_compares_the_newest_measurement_against_the_last_one(
        tmp_path):
    """The record the harness started writing on 2026-10-04, read by the panel.

    A result whose delta fell below the previous measurement's own lower bound
    is a fail, and before `history` existed this reviewer could not see it: it
    holds one file, and the run that produced it had overwritten the older
    numbers.
    """
    entry = {"version": "1", "date": "2026-10-01",
             "subject_model": "kimi-k2.6", "verdict": "gain",
             "delta": {"mean": 0.6, "ci95": [0.4, 0.8]}}
    fell = gained(delta={"mean": 0.1, "ci95": [0.05, 0.2]})
    fell["history"] = [entry, {**entry, "version": "2", "date": "2026-10-04",
                               "delta": fell["delta"]}]
    v = verdict(tmp_path, suite=suite_for(), result=fell)
    direction = [f for f in checks(v, "trial-direction")
                 if f["severity"] == "fail"]
    assert any("below the previous result's own lower bound" in f["detail"]
               for f in direction), direction
    assert v["verdict"] == "fail"
    record = checks(v, "trial-record")
    assert len(record) == 1
    assert "2 measurements on the record" in record[0]["detail"]
    assert "2026-10-01" in record[0]["detail"]


def test_one_measurement_is_not_compared_against_itself(tmp_path):
    only = gained()
    only["history"] = [{"version": "1", "date": "2026-10-03",
                        "subject_model": only["subject_model"],
                        "verdict": "gain", "delta": only["delta"]}]
    v = verdict(tmp_path, suite=suite_for(), result=only)
    assert v["verdict"] == "pass", v["findings"]
    record = checks(v, "trial-record")
    assert len(record) == 1 and "no earlier number" in record[0]["detail"]
