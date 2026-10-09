"""The coverage gate: a test file CI never runs is not a test.

INC-2026-10-02-markdown-suite-claims-a-ci-step-it-never-had. `checks.yml`
runs fourteen test files as fourteen named steps, and the suite holds
rather more than fourteen. `tests/test_markdown.py` is one of the ones left
out, it holds the 2026-09-19 finding where a crafted passage in an arXiv
paper reached the public archive as live HTML, and its own docstring says
the other half of it "is the half that runs in CI". Neither half runs
anywhere. `tests/test_accounts.py` is in the same position and it holds the
account and entitlement layer.

No count appears in this docstring on purpose. `UNCOVERED` below is the
count, it is checked on every run, and a number repeated in prose beside it
is a second copy that nothing checks. Two numbers written into this
repository's documents this run were stale by the end of the same run,
which is the defect this file exists to make noisy, so it does not commit
it in its own header.

The ledger entry for that incident names four files and the measurement
found many more, and the gap between those two is the reason this is a gate
rather than a sentence. Nobody counted, because counting meant reading a
`paths` list of twenty-four entries against a step list of fourteen against
a directory, and the two places a filename can appear in that workflow mean
opposite things.

Three things are under test here.

The parser, because the whole measurement rests on one distinction:
`tests/test_press_resilience.py` appears in the live `checks.yml` both as a
step that executes it and as a `paths` entry that only decides whether the
job starts. A scan that conflates those reports the defect as absent.

The pin, which is the gate. `UNCOVERED` below is the exact set of test
files that no workflow runs today. The set may shrink and may not grow, so
a new test file added to `tests/` with no CI step turns red on the pull
request that adds it, instead of passing quietly for a month.

The staged fix, because `.github/workflows-pending/checks.yml` is a
workflow no seat can apply and therefore a workflow nothing executes. The
last test asserts that applying it leaves no test file unexecuted, so the
owner moving that file is moving something measured rather than something
asserted.

No network, no database, no GitHub API. Everything here is the workflow
files and the test directory as they sit in the checkout.

Run with `python3 -m pytest tests/test_ci_coverage.py -q`.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import ci_coverage as cc  # noqa: E402

LIVE = ".github/workflows/checks.yml"
STAGED = ".github/workflows-pending/checks.yml"


# --------------------------------------------------------------- the parser

RUN_VS_PATHS = """\
name: checks
on:
  pull_request:
    paths:
      - "tests/test_press_resilience.py"
      - "pipeline/**"
jobs:
  one:
    steps:
      - name: inline
        run: python3 tests/test_email_template.py
      - name: a block
        run: |
          pip install -r requirements-dev.txt
          python3 -m pytest tests/test_board.py tests/test_run_report.py -q
      - name: env only
        env:
          HOOK: x
        run: echo nothing
"""


def test_run_commands_reads_steps_and_ignores_paths():
    commands = cc.run_commands(RUN_VS_PATHS)
    joined = "\n".join(commands)
    assert "tests/test_email_template.py" in joined
    assert "tests/test_board.py" in joined
    # The distinction the whole measurement rests on. This file names
    # test_press_resilience.py in `paths` and never runs it, exactly as the
    # live checks.yml does for several files.
    assert "tests/test_press_resilience.py" not in joined
    assert "echo nothing" in joined


def test_run_commands_keeps_every_line_of_a_block():
    commands = cc.run_commands(RUN_VS_PATHS)
    block = [c for c in commands if "pip install" in c][0]
    assert "python3 -m pytest" in block, "a block's later lines were dropped"


UNIVERSE = ["tests/test_a.py", "tests/test_b.py", "tests/c.test.mjs"]


@pytest.mark.parametrize(
    "command,expected",
    [
        ("python3 tests/test_a.py", {"tests/test_a.py"}),
        (
            "python3 -m pytest tests/test_a.py tests/test_b.py -q",
            {"tests/test_a.py", "tests/test_b.py"},
        ),
        # The suite form. pytest collects the Python files; the node halves
        # are reached through their wrappers, not by this command.
        ("python3 -m pytest tests/ -q", {"tests/test_a.py", "tests/test_b.py"}),
        ("python3 -m pytest tests -q", {"tests/test_a.py", "tests/test_b.py"}),
        ("pip install -r requirements-dev.txt", set()),
        # A path outside the universe is not a test file.
        ("python3 pipeline/budget.py", set()),
    ],
)
def test_files_executed_by(command, expected):
    assert cc.files_executed_by(command, UNIVERSE, root=str(ROOT)) == expected


def test_files_executed_by_expands_a_glob(tmp_path):
    (tmp_path / "tests").mkdir()
    for name in ("one.test.mjs", "two.test.mjs", "notatest.js"):
        (tmp_path / "tests" / name).write_text("")
    universe = ["tests/one.test.mjs", "tests/two.test.mjs"]
    hit = cc.files_executed_by(
        "node --test tests/*.test.mjs", universe, root=str(tmp_path)
    )
    assert hit == set(universe)


# ------------------------------------------------- the subprocess chain

def test_children_of_finds_the_real_node_wrapper():
    """`tests/test_markdown.py` runs its node half in a subprocess."""
    universe = cc.test_files()
    children = cc.children_of("tests/test_markdown.py", universe)
    assert "tests/markdown.test.mjs" in children


def test_children_of_finds_the_real_pytest_wrapper():
    """`tests/test_skill_receipts.py` runs the reviewer's 43 cases itself.

    This is the case a cruder scan gets wrong in the expensive direction:
    report `tests/test_panel_provenance.py` as uncovered and the obvious fix
    is a second step that runs it a second time.
    """
    universe = cc.test_files()
    children = cc.children_of("tests/test_skill_receipts.py", universe)
    assert "tests/test_panel_provenance.py" in children


def test_children_of_ignores_a_filename_in_prose():
    """Several of these files name each other in docstrings.

    `tests/test_panel_adversary.py` says "Same shape as
    tests/test_graph_audit.py's" in a docstring and executes nothing.
    """
    universe = cc.test_files()
    children = cc.children_of("tests/test_panel_adversary.py", universe)
    assert "tests/test_graph_audit.py" not in children


# ------------------------------------------------------------- the pin

# Every test file that no workflow in `.github/workflows/` executes, measured
# 2026-10-07 by `python3 tools/ci_coverage.py`. Thirty-three of forty-seven.
#
# This list may shrink and may not grow. When a step is added that runs one of
# these, delete the line and the test below goes green again. When the staged
# replacement in `.github/workflows-pending/checks.yml` is applied, the list
# becomes empty.
#
# A line here is not an exemption. It is a file whose assertions report
# nothing on any pull request, and the test that reads this list prints that
# sentence when it fails so the next seat does not have to infer it.
UNCOVERED = {
    # This file, and the entry is worth more than the rest of the set.
    # The gate against test files that no workflow runs is itself a test file
    # that no workflow runs, because adding the step needs a `workflows`
    # permission no seat holds. It caught itself on the first run, which is
    # the only evidence anyone should accept that it works. It leaves the set
    # when the staged replacement is applied, like every other line here.
    "tests/test_ci_coverage.py",
    # And the second file this run added, caught by this gate the same way
    # and pinned for the same reason: no seat can add it to a workflow.
    "tests/test_voice_enforcements.py",
    "tests/accounts.test.mjs",
    "tests/delivery.test.mjs",
    "tests/issues.test.mjs",
    "tests/markdown.test.mjs",
    "tests/test_accounts.py",
    "tests/test_authorize_throttle.py",
    "tests/test_check_helper_is_enforced.py",
    "tests/test_check_registers.py",
    "tests/test_code_single_use.py",
    "tests/test_corrections.py",
    "tests/test_delivery_health.py",
    "tests/test_delivery_receipt.py",
    "tests/test_deploy_drift.py",
    # Added 2026-10-08 with today's deploy ladder, and pinned for the same
    # structural reason as every line above: the step that would run it goes in
    # `.github/workflows/checks.yml`, which no seat's token may write. The
    # staged replacement already runs it, measured at `50 of 50` with `--only`.
    "tests/test_deploy_gate.py",
    "tests/test_distill_practices.py",
    "tests/test_evidence_grade.py",
    "tests/test_issue_route.py",
    "tests/test_markdown.py",
    "tests/test_oauth_redirect_uri.py",
    "tests/test_panel_adversary.py",
    "tests/test_panel_validator.py",
    "tests/test_press_week_label.py",
    "tests/test_prose_benchmark.py",
    "tests/test_reading_queue.py",
    "tests/test_retag_threads.py",
    "tests/test_skill_eval.py",
    "tests/test_skill_gate.py",
    "tests/test_skill_registrar.py",
    "tests/test_skill_triggers.py",
    "tests/test_triage_planner.py",
    "tests/test_unsubscribe.py",
    "tests/test_waitlist.py",
    "tests/unsubscribe.test.mjs",
    "tests/waitlist.test.mjs",
}


def test_this_file_is_in_the_pin_or_is_covered():
    """The gate cannot be a file the gate does not see."""
    report = cc.coverage()
    mine = "tests/test_ci_coverage.py"
    assert mine in report["covered"] or mine in UNCOVERED, (
        f"{mine} is neither run by a workflow nor pinned, so it is the one "
        "kind of file this file exists to make impossible"
    )


def test_the_uncovered_set_has_not_grown():
    report = cc.coverage()
    actual = set(report["uncovered"])
    grew = sorted(actual - UNCOVERED)
    shrank = sorted(UNCOVERED - actual)
    assert not grew, (
        f"{len(grew)} test file(s) run in no workflow and are not pinned:\n"
        + "\n".join(f"  {name}" for name in grew)
        + "\n\nA test file no workflow runs reports nothing on any pull "
        "request: it passes locally, it passes for the seat that wrote it, "
        "and it is silent on the merge that breaks what it guards. Either "
        "add a step to .github/workflows/checks.yml, or apply the staged "
        f"replacement at {STAGED}, which runs the whole suite. Pinning it "
        "in UNCOVERED is the last resort and needs a reason in the diff."
    )
    assert not shrank, (
        f"{len(shrank)} pinned file(s) now run in CI. That is the good "
        "direction. Delete them from UNCOVERED in tests/test_ci_coverage.py:\n"
        + "\n".join(f"  {name}" for name in shrank)
    )


def test_every_test_file_the_live_workflow_names_exists():
    """A step naming a file that was renamed is a step that cannot be green."""
    report = cc.coverage()
    for name, sources in report["where"].items():
        if sources:
            assert (ROOT / name).exists(), f"{name} is run by {sources} and is gone"


def test_the_live_workflow_still_runs_the_press_guards():
    """The fourteen named steps are the floor, not the ceiling.

    This is the assertion that would catch the structural change being
    applied badly: whatever shape `checks.yml` takes, these four files are
    the press's own guards and every one of them has an incident behind it.
    """
    covered = set(cc.coverage()["covered"])
    for name in (
        "tests/test_press_resilience.py",
        "tests/test_email_template.py",
        "tests/test_press_rehearsal.py",
        "tests/test_skill_receipts.py",
    ):
        assert name in covered, f"{name} stopped running in CI"


# ------------------------------------------------------- the staged fix

def test_the_staged_checks_file_exists():
    assert (ROOT / STAGED).exists(), (
        f"{STAGED} is the queued fix for item 17 of "
        "docs/agents/pending-workflow-changes.md"
    )


def test_the_staged_checks_file_would_cover_the_whole_suite():
    """The reason to apply it, measured rather than claimed."""
    report = cc.coverage(only=[STAGED])
    assert report["uncovered"] == [], (
        f"{STAGED} is the fix for the gate above and it leaves "
        f"{len(report['uncovered'])} file(s) unexecuted: "
        + ", ".join(report["uncovered"])
    )
    assert len(report["covered"]) == report["total"]


def test_the_staged_checks_file_keeps_both_triggers():
    """A guard scoped to pull requests is not a guard on this repository.

    INC-2026-09-30-the-guard-went-red-and-nobody-read-it: this exact file
    sat in `workflows-pending` without a push trigger, two runtime changes
    went straight to main in the gap, and two guards stayed red for six days.
    """
    text = (ROOT / STAGED).read_text()
    assert "pull_request:" in text
    assert "push:" in text and "branches: [main]" in text


def test_the_report_is_a_gate_by_default():
    """Exit non-zero when a test file runs in no workflow.

    The first draft of the staged workflow's last step was named "every test
    file in tests/ is executed by some workflow" and exited 0 while naming
    thirty-three that were not. A step whose name claims a property it does
    not enforce is this file's own subject matter, so the tool carries the
    verdict rather than the workflow.
    """
    assert cc.main([]) == 1, "the live tree has uncovered test files today"
    assert cc.main(["--report-only"]) == 0
    assert cc.main(["--only", STAGED]) == 0, (
        "the staged replacement covers every test file, so it must exit 0"
    )


def test_the_staged_checks_file_runs_the_gate_without_report_only():
    """The step is only a gate if it is not asked to be quiet."""
    text = (ROOT / STAGED).read_text()
    gate = [
        line.strip()
        for line in text.splitlines()
        if "tools/ci_coverage.py" in line and line.strip().startswith("run:")
    ]
    assert gate, "the staged file does not run the coverage gate at all"
    assert all("--report-only" not in line for line in gate), (
        "the staged file runs the coverage gate with --report-only, which "
        "makes the step print the defect instead of failing on it"
    )


def test_the_staged_checks_file_installs_node():
    """Seven test files are `*.test.mjs` and their wrappers skip without node.

    A skip is not a pass. Without this the account, markdown, unsubscribe
    and waitlist halves would be named by the suite and still never run.
    """
    text = (ROOT / STAGED).read_text()
    assert "actions/setup-node" in text
