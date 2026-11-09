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
    # Added 2026-11-09 06:5xZ. These two are **not** this run's files: they
    # reached `main` in this seat's own merged pull requests at 00:26:22 and
    # 00:37:28 and have been unpinned and uncovered ever since, which means
    # `main` itself has failed `test_the_uncovered_set_has_not_grown` for six
    # hours. Reproduced on a clean checkout of `origin/main` before pinning, so
    # this is not a defect of the branch that carries the fix.
    #
    # The gate names three remedies and ranks pinning last. The first two are
    # `.github/workflows/checks.yml` and applying the staged replacement at
    # `.github/workflows-pending/checks.yml`, and **both are a workflow write,
    # which this seat's dispatch forbids outright**. So the last resort is the
    # only resort available to the seat that broke it, which is the standing
    # finding at `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days`
    # and is why that entry counts rather than argues.
    #
    # What each one guards, because the gate requires a reason and not a name.
    # `test_pr_backlog.py`, 21 cases: that the backlog reader refuses to call a
    # queue newest-first on the strength of a backlog count alone, since with no
    # observation of the queue *moving* a count of old rows is not evidence about
    # how they are served. Silent on a pull request, that refusal can be deleted
    # and the tool starts publishing its worst verdict when its subject is
    # freshest.
    # `test_wall_encounters.py`, 15 cases: that the corpus reader tells a run
    # that **met** a provider wall from one that merely **wrote about** one. Its
    # fixtures are two real closing summaries that a file-wide grep counted as
    # refusals, quoted rather than paraphrased so the matcher turns on the real
    # word. Silent on a pull request, the quoted prose is what rots first, and
    # then the test passes against a reader that cannot see the real thing.
    "tests/test_pr_backlog.py",
    "tests/test_wall_encounters.py",
    # And the second file this run added, caught by this gate the same way
    # and pinned for the same reason: no seat can add it to a workflow.
    "tests/test_voice_enforcements.py",
    "tests/accounts.test.mjs",
    # Added 2026-10-13 with the Polar integration, pinned for the same
    # structural reason as every line above and worth more than any of them.
    # These two hold the signature check that stands between a stranger and
    # the paid surfaces, and the gate that decides who may open one. The
    # staged replacement already runs both (measured at `52 of 52`), so this
    # pin is not a judgement that they do not matter. It is the strongest
    # argument in this set for applying item 17, because of everything in
    # `tests/` these are the two files whose silence on a pull request would
    # cost money rather than a red run.
    "tests/polar.test.mjs",
    "tests/test_polar.py",
    # Added 2026-10-14 with the quiet-send guardrail, and pinned for the same
    # structural reason as every line above. This one is pointed: the file it
    # guards is itself a scheduled reader that exists because a correct check
    # ran at the wrong hour, so a test of it that fires on no pull request is
    # the same defect one level down. The staged replacement runs it, measured
    # at `53 of 53`.
    "tests/test_press_watch.py",
    # Added 2026-10-16 with the sources availability check, and pinned for
    # the same structural reason as every line above: the step that would run
    # it goes in `.github/workflows/checks.yml`, which no seat's token may
    # write. The staged replacement runs it, because that file runs the suite
    # rather than naming files. What this one guards is the top of the
    # pipeline: `pipeline/ingest.py` fetched fifty-three sources a day and
    # could not tell whether any answered, and seven were delivering nothing
    # when it was first measured. A corpus that stops growing is invisible
    # for as long as the press keeps printing from what it already has.
    "tests/test_feed_health.py",
    # Added 2026-10-17 with the ledger parser, and pinned for the same
    # structural reason as every line above: the step that would run it goes
    # in `.github/workflows/checks.yml`, which no seat's token may write, and
    # `docs/sprints/sprint-2026-10-12.md` tells this seat in its own words not
    # to attempt that file again because four runs already have. The staged
    # replacement runs it, because that file runs the suite rather than naming
    # files. What this one guards is the planning machinery rather than the
    # product: `docs/ideas.md` is how the PM finds work and how every seat
    # finds `urgent`, and the gate in it is a ratchet, so its silence on a
    # pull request is exactly the merge that pushes the count back up.
    "tests/test_ledger.py",
    # Added 2026-10-17 with the drift alarm's board channel, and pinned for
    # the same structural reason as every line above: the step that would run
    # it goes in `.github/workflows/checks.yml`, which no seat's token may
    # write. This is the eighth line added in ten days and the repeat is
    # already filed, this morning, as
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days`;
    # a second entry for the eighth would be noise on a finding that is
    # already correct. What this one guards is the only path by which a
    # merged change that never reached production reaches a human: the alarm
    # it replaces has a cooldown in a database column no seat can write, so
    # it has raised to nobody since 2026-10-08. A test of that guardrail
    # which is silent on a pull request is the same defect one level down,
    # which is the sentence `tests/test_press_watch.py` above already
    # carries, about the sibling guardrail, for the same reason.
    "tests/test_drift_watch.py",
    # Added 2026-10-18 with the plugin marketplace, and pinned for the same
    # structural reason as every line above: the step that would run it goes
    # in `.github/workflows/checks.yml`, which no seat's token may write, and
    # `docs/sprints/sprint-2026-10-12.md` tells this seat in its own words not
    # to attempt that file again. This is the ninth line added in eleven days.
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days` is
    # already the finding and already correct, so this entry counts itself
    # there rather than opening a third incident on one pattern. What this one
    # guards is the first thing a stranger does with this product: the two
    # lines that install the library, and whether the number of skills they
    # advertise is still the number that ships. The defect it exists for is
    # live on `site/app/skills/page.jsx` today, which says two against nine,
    # so a gate on it that fires on no pull request is the same defect one
    # level down.
    "tests/test_plugin_manifest.py",
    # Added 2026-10-18 with the buyer-path measurement, and pinned for the
    # same structural reason as every line above: the step that would run
    # them goes in `.github/workflows/checks.yml`, which no seat's token may
    # write, and `docs/sprints/sprint-2026-10-12.md` tells this seat in its
    # own words not to attempt that file again. These are the tenth and
    # eleventh lines added in twelve days.
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days` is
    # already that finding and already correct, so these entries count
    # themselves there rather than opening another incident on one pattern.
    #
    # What they guard is worth more than most of this set, and in a direction
    # nothing else here covers. Every other pinned file guards a thing that
    # breaks loudly. These two guard a promise: `site/app/privacy/page.jsx`
    # tells a reader there is no third-party script watching them read, and
    # the only reason that page is still true is that `path_events` holds no
    # identifier. A change that adds one would pass every other test in this
    # repository, ship green, and break a promise to a person rather than a
    # build. `test_the_table_holds_no_column_that_could_identify_a_person`
    # and the two assertions over the privacy page are the only things that
    # would notice, and today they notice on no pull request.
    "tests/path.test.mjs",
    "tests/test_buyer_path.py",
    # Added 2026-10-23 with the till's alarm, and pinned for the same
    # structural reason as every line above: the step that would run it goes
    # in `.github/workflows/checks.yml`, which no seat's token may write, and
    # `docs/sprints/sprint-2026-10-12.md` tells this seat in its own words not
    # to attempt that file again. This is the twelfth line added in fifteen
    # days. `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days`
    # is already that finding and already correct, so this entry counts itself
    # there rather than opening another incident on one pattern.
    #
    # What it guards is the only surface in this product that takes money and
    # the only reader that surface has. The checkout probe has been correct
    # since 2026-10-18 and has raised an alarm to nobody, because printing to
    # a terminal nobody is sitting at is not a channel. The alarm this file
    # covers is what turns it into one, and it also covers
    # `tools/board_alarm.py`, which is the create-or-nudge mechanic all three
    # watchers now share and has no command of its own: a regression there is
    # silent in every one of them at once.
    "tests/test_checkout_watch.py",
    # Added 2026-10-26 with the self-improvement loop's closing condition, and
    # pinned for the same structural reason as every line above: the step that
    # would run it goes in `.github/workflows/checks.yml`, which no seat's
    # token may write, and `docs/sprints/sprint-2026-10-12.md` tells this seat
    # in its own words not to attempt that file again.
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days` is
    # already that finding and already correct, so this entry counts itself
    # there rather than opening another incident on one pattern.
    #
    # What it guards is the rule that decides when a proposal the system made
    # about itself is done. The failure it was written for has already
    # happened once: a prompt merged on 2026-10-05 and the job reading it went
    # on reading the old one for twelve days, 8,861 rows deep. The dangerous
    # direction here is a wrong `live`, because that writes `promotions.live_at`
    # and a closed loop is never asked about again, and the assertions that an
    # unknown stops a close are the ones that would be silent on a pull
    # request.
    "tests/test_loop_close.py",
    # Added 2026-10-26 with the arXiv window's repair, and pinned for the same
    # structural reason as every line above: the step that would run it goes
    # in `.github/workflows/checks.yml`, which no seat's token may write, and
    # `docs/sprints/sprint-2026-10-12.md` tells this seat in its own words not
    # to attempt that file again. The staged replacement runs it, because that
    # file runs the suite rather than naming files.
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days` is
    # already that finding and already correct, so this entry counts itself
    # there rather than opening another incident on one pattern.
    #
    # What it guards is the top of the pipeline, and in the direction this
    # repository has just learned is the expensive one. `pipeline/ingest.py`
    # read a sliding window for its whole life, so a run it missed did not
    # lose time, it lost records: 290 to 570 papers of cs.AI and cs.LG are
    # already beyond the reach of any future run
    # (`INC-2026-10-26-the-arxiv-window-is-smaller-than-two-of-the-categories-behind-it`).
    # The assertions whose silence would cost most are the two bounds rather
    # than the window itself, because a regression that re-caps the window at
    # one page reads as a green run with a smaller corpus, which is exactly
    # how the defect went unmeasured for the job's whole life.
    "tests/test_arxiv_window.py",
    # Added 2026-10-26 with the fifth evidence grade, and pinned for the same
    # structural reason as every line above: the step that would run it goes
    # in `.github/workflows/checks.yml`, which no seat's token may write, and
    # `docs/sprints/sprint-2026-10-12.md` tells this seat in its own words not
    # to attempt that file again. The staged replacement runs it, because that
    # file runs the suite rather than naming files.
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days` is
    # already that finding and already correct, so this entry counts itself
    # there rather than opening another incident on one pattern.
    #
    # What it guards is a guard that has to be wrong in one direction only.
    # `evidence.relay_markers` decides that a claim is another work's result
    # rather than the source's own, and it decides it off the evidence text
    # when the model said otherwise. The assertions whose silence would cost
    # most are not the ones about the sentence that cost a shipped skill; they
    # are the five first-hand sentences that read relational and must not
    # fire. A loosened marker regresses those silently, and the only visible
    # symptom is a corpus that grades its own measurements second-hand, which
    # is the failure this grade exists to stop, running backwards.
    "tests/test_relayed_claims.py",
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
    # Added 2026-10-14 with the pre-send quality gate, pinned for the same
    # structural reason as every line above: the step that would run it goes
    # in `.github/workflows/checks.yml`, which no seat's token may write, and
    # pm.md section 15 gives those files to headquarters rather than to a
    # product seat. The staged replacement runs it. This one guards what does
    # and does not reach a subscriber's inbox, so its silence on a pull
    # request would cost a reader rather than a red run, and the handoff
    # asking headquarters to apply item 17 names it by name.
    "tests/test_digest_quality.py",
    "tests/test_distill_practices.py",
    # Added 2026-10-13 with the institution backfill, pinned for the same
    # structural reason as every line above. This one guards a job that writes
    # into `papers.institutions`, which the digest's attribution line reads,
    # and most of its assertions are refusals: the strings it proves are NOT
    # written are author names and footnotes found in real arXiv headers. The
    # staged replacement runs it, so this pin is not a judgement that it does
    # not matter.
    "tests/test_institution_backfill.py",
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
    # Added 2026-10-24 with the two queue instruments, and pinned for the same
    # structural reason as every line above: the step that would run them goes
    # in `.github/workflows/checks.yml`, which no seat's token may write, and
    # `docs/sprints/sprint-2026-10-12.md` tells this seat in its own words not
    # to attempt that file again. These are the thirteenth and fourteenth lines
    # added in sixteen days.
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days` is
    # already that finding and already correct, so these entries count
    # themselves there rather than opening another incident on one pattern.
    #
    # What they guard is the merge queue, which is this repository's measured
    # throughput constraint rather than any part of the product.
    # `test_merge_order.py` holds the read-only promise L-E12 asks of a
    # measurement that runs inside a checkout somebody else is standing in, and
    # that is the assertion whose silence would cost most: a regression there
    # leaves a seat's clone shallow or its HEAD moved, which breaks the run
    # that took the measurement rather than the measurement.
    # `test_resolve_register_conflict.py` holds the arithmetic that catches a
    # resolution which dropped a line, which is
    # `INC-2026-10-24-a-hand-resolved-register-append-deleted-another-seats-line-with-no-marker`,
    # and a dropped line leaves valid Markdown, so that arithmetic is the only
    # thing in this repository that would notice the next one.
    "tests/test_merge_order.py",
    "tests/test_resolve_register_conflict.py",
    # Added 2026-10-24 with the authority gate's tests, and pinned for the one
    # structural reason every line above is pinned: the step that would run it
    # goes in `.github/workflows/checks.yml`, no seat's token may write that
    # file (`docs/agents/pending-workflow-changes.md`), and
    # `docs/sprints/sprint-2026-10-12.md` tells this seat in its own words not
    # to attempt it again. Counted at
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days`
    # rather than opening a second incident on one pattern. Fifteenth line in
    # seventeen days.
    #
    # What it guards is `tools/check_authority.py`, which decides whether a
    # diff is the owner's to merge. That tool is itself a gate, so the exit
    # status is its whole interface, and L-A9's 2026-10-05 amendment is
    # explicit that a gate is real only when the command is named and its exit
    # status means something. The tests pin that mapping and the four questions
    # behind it, including the three verdicts the tool may not confuse: a
    # charter line that rules the owner, a secret NAME in prose and a price in
    # prose all read `clear`, and each of those three is a false `reserved`
    # away from making the gate useless.
    "tests/test_check_authority.py",
    # Added 2026-10-24 with the incident register's inbox, and pinned for the
    # same structural reason as every line above: the step that would run it
    # goes in `.github/workflows/checks.yml`, which no seat's token may write,
    # and `docs/sprints/sprint-2026-10-12.md` tells this seat in its own words
    # not to attempt that file again. The staged replacement runs it, measured
    # by `tools/ci_coverage.py --only .github/workflows-pending/checks.yml`,
    # which reports an empty uncovered set with this file present. Counted at
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days`
    # rather than opening another incident on one pattern. Sixteenth line in
    # eighteen days.
    #
    # What it guards is the append surface of `docs/agents/incidents.md`, and
    # the pin is pointed in the same way `tests/test_ci_coverage.py` above is.
    # This register is where every seat records a repeat, so a defect in the
    # thing that accepts those filings is the defect that hides every other
    # defect. The tests that matter most in it are the ones that fail when a
    # collision could come back: an id already in the register, two inbox
    # files claiming one id, a filename that disagrees with the heading inside
    # it, and the three-part arithmetic that refuses a fold which dropped or
    # duplicated a line. That last one is not hypothetical. A hand resolution
    # on this same file deleted another seat's line on 2026-10-24 and left
    # valid Markdown behind it, so the invariant is the only reader that would
    # have noticed.
    "tests/test_incidents.py",
    # Added 2026-10-24 with slice 5 of the graph upgrade, and pinned as the
    # last resort this gate's own failure message names, because the other two
    # routes are both closed to this seat. Adding a step goes in
    # `.github/workflows/checks.yml`, and applying the staged replacement is a
    # `git mv` out of `.github/workflows-pending/`; both are workflow writes no
    # seat's token carries. Seventeenth line, and the repeat stays counted at
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days`
    # rather than opening an eighteenth entry on one pattern.
    #
    # What it guards is the claim graph's read path, and the pin costs less
    # here than on most lines above it, because the structural half of that
    # change is caught anyway: the audit now names `latest_links`, and
    # `tests/test_graph_audit.py` resolves every relation the audit names
    # against `db/schema.sql` and IS one of the twelve files a workflow runs.
    # Renaming the view in the schema fails that suite. What this file adds and
    # nothing in CI can reach is the behaviour: that a second opinion inserts
    # at all, that the same judge twice does not, and that `deprecated_claims`
    # follows the newest verdict in both directions. Those six tests need a
    # server, this org runs none in CI, and the company host has one, so they
    # are evidence where a seat runs and a skip where it does not.
    "tests/test_latest_links.py",
    # Added 2026-10-25 with slice 5's second half, the re-judgment trigger, and
    # pinned for the same reason as the line above it and by the same two closed
    # routes: a step goes in `.github/workflows/checks.yml` and applying the
    # staged replacement is a `git mv` out of `.github/workflows-pending/`, and
    # both are workflow writes no seat's token carries. Eighteenth line, and the
    # repeat stays counted at
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days`
    # rather than opening a nineteenth entry on one pattern.
    #
    # What it guards is the only part of this slice that can cost money. The
    # trigger decides which claims get sent to a model again, so the two ways
    # it can be wrong are a bill rather than a wrong answer: keying it on
    # `method` instead of the prompt sha re-judges the whole corpus every time
    # the fallback provider answers, and reading `claim_links` instead of
    # `claim_judgments` re-judges every claim that was read and found nothing,
    # on every run, forever. Both are one-word edits and both pass every other
    # test in this repository. The structural half of that is reachable without
    # a server and is asserted here on the query text itself; the half that
    # needs rows, including the backfill recovering September's shas out of
    # `claim_links.method`, runs on the company host and skips in CI.
    "tests/test_rejudge_queue.py",
    # Added 2026-10-25 with slice 2 of the graph upgrade, and pinned for the
    # same structural reason as every line above: the step that would run it
    # goes in `.github/workflows/checks.yml`, which no seat's token may write,
    # and `docs/sprints/sprint-2026-10-12.md` tells this seat in its own words
    # not to attempt that file again because four runs already have. The staged
    # replacement runs it, because that file runs the suite rather than naming
    # files. `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days`
    # is already this finding and already correct, so this entry counts itself
    # there rather than opening another incident on one pattern.
    #
    # What it guards had no test at all until the day it was pinned, which is
    # the part worth reading. The six lines of SQL that choose which older
    # claims a new claim is judged against decide the shape of the entire claim
    # graph, and every metric `tools/graph_audit.py` reports is downstream of
    # them. Three of the four properties asserted here are silent failures: a
    # shortlist that offers a claim its own paper's siblings produces edges
    # that are true and worthless, a shortlist that pads itself to its limit
    # pays a model to answer `unrelated`, and a shortlist that looked forward
    # in time would write edges the audit can only catch after they are rows.
    # None of the three turns anything red. The live half of the file needs a
    # cluster with pgvector and runs on the company host; the structural half,
    # which includes recomputing the token pair the spend cap is set against,
    # runs anywhere.
    "tests/test_shortlist.py",
    # Added 2026-10-25 with the firing-record reader, and pinned by the same
    # two closed routes as every line above: a step goes in
    # `.github/workflows/checks.yml` and applying the staged replacement is a
    # `git mv` out of `.github/workflows-pending/`, and no seat's token writes
    # either. Twentieth line, counted at
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days`
    # rather than opening another entry on one pattern.
    #
    # This one is cheap to pin and worth saying why. `tools/cron_firing.py`
    # reads logs the repository does not contain, so the tests build the
    # host's log format in a temporary directory and assert against that
    # fixture. A fixture is the one thing CI could run here with no
    # credential and no server, which makes the pin a straight loss rather
    # than a limitation of the environment. What it guards is a reader whose
    # whole failure mode is quiet: the first version matched the result line
    # as text, read every log on the host correctly, and silently stopped
    # classifying refusals against a fixture that differed by one space.
    "tests/test_cron_firing.py",
    # Added 2026-10-26 with ADR-13's merge executor, and pinned for the same
    # structural reason as every line above: the step that would run it goes
    # in `.github/workflows/checks.yml`, which no seat's token may write, and
    # the staged replacement runs the suite rather than naming files, so this
    # pin leaves the set the moment item 17 is applied.
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days` is
    # already that finding and already correct, so this entry counts itself
    # there rather than opening another incident on one pattern.
    #
    # What it guards is the only code in this repository that can merge a pull
    # request without a person, and the direction of almost every assertion in
    # it is a refusal: that machinery is never merged by a verdict, that a
    # charter is never merged by the panel, that three passes on other text
    # are not three passes on this one, that a panel of two is not unanimity,
    # and that the ambient `GH_TOKEN` every seat on this host holds is
    # declined. Those are the tests whose silence costs the most, because the
    # defect they would catch is a merge that already happened.
    "tests/test_panel_merge.py",
    # Added 2026-10-26 with the scoped-delivery measurement, and pinned for
    # the same structural reason as every line above: the step that would run
    # it goes in `.github/workflows/checks.yml`, which no seat's token may
    # write, and the engineer charter says in its own words that this seat
    # cannot push a workflow file. The staged replacement runs it, because
    # that file runs the suite rather than naming files.
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days` is
    # already that finding and already correct, so this entry counts itself
    # there rather than opening another incident on one pattern.
    #
    # What it guards is the only gate in `tools/skill_scope.py`, the verdict
    # that answers whether loading three skills beats loading the library,
    # and the test that matters most in it is the one that builds a checkout
    # where scoping is the wrong move and asserts the verdict says so. A
    # measurement whose verdict has only ever been observed agreeing with the
    # run that wrote it is not a measurement, and that assertion going silent
    # on a pull request is how it would become one.
    "tests/test_skill_scope.py",
    # Added 2026-10-26 with the press's named-week entrypoint, and pinned for
    # the same structural reason as every line above: applying the staged
    # replacement needs a `workflows` permission no seat holds, and the
    # alternative the gate offers is editing `.github/workflows/checks.yml`,
    # which no seat may do either. The reason this pin is in the diff rather
    # than assumed: the file holds the only proof that a regenerated issue
    # mails nobody. A backfill over a quarter of past issues would otherwise
    # mail the subscriber list a dozen times, and that assertion going silent
    # on a pull request is the one failure in this set a reader would notice
    # before the owner did. The staged replacement runs the whole suite, so it
    # runs this too.
    "tests/test_press_backfill.py",
    # Added 2026-10-26 by the ExO seat, and pinned for the same structural
    # reason as every line above: the step that would run them goes in
    # `.github/workflows/checks.yml`, which no seat's token may write by
    # design, and `.github/workflows-pending/README.md` says why in one
    # sentence — an agent that can write its own CI can also write itself out
    # of it. The staged replacement runs the whole suite and therefore runs
    # both of these.
    #
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days` is
    # already the finding about the pattern and it is still correct, so these
    # two count themselves there rather than opening another incident on it.
    # What they add is a number: the staged replacement has been waiting for a
    # hand since 2026-10-07, and this set is now the only measure of that
    # wait. Every test file any seat writes lengthens it, which makes the pin
    # list a ledger of a blocked `git mv` rather than a list of exceptions.
    #
    # `test_wake_routes.py` arrived on the branch this one supersedes and was
    # not pinned there, because that run ran its own test file and never the
    # suite, so it would have merged a red ratchet. That is the second half of
    # why these two lines are worth their comment: a gate whose only trigger
    # is somebody running the whole suite by hand is a gate that catches the
    # careful run and misses the hurried one.
    #
    # What each guards. `test_wake_routes.py` holds the only check in any
    # repository that a seat's event subscriptions can actually reach it; four
    # of twelve seats here have never been woken by the bus. `test_ship_first.py`
    # holds the only measurement of the ship-first rule, which 0.5% of 1,765
    # runs obey, and its seven states exist to keep a run that lost its work
    # apart from one that was refused before it could have any. Both are
    # instruments about silence, so both going silent on a pull request is
    # the defect they exist for, one level down.
    "tests/test_wake_routes.py",
    "tests/test_ship_first.py",
    # Added 2026-11-01 by the security seat with the `db()` DSN redaction, and
    # pinned for the structural reason every line above gives: the step that
    # would run it goes in `.github/workflows/checks.yml`, which this seat's
    # token may not write and which its own charter forbids it to touch. The
    # staged replacement runs it, because it runs the suite rather than naming
    # files. Counted into
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days`
    # rather than opening a second incident on the same pattern, and the number
    # that entry asked for is now 25 days of waiting since 2026-10-07.
    #
    # What it guards, and it is the reason this pin is worth reading twice.
    # `db()` hands psycopg the `DATABASE_URL` secret, and libpq echoes the
    # whole connection string back in its parse error when the value does not
    # begin exactly with `postgres://`. One leading space in the secret is
    # enough, that exception leaves through an MCP tool call to whoever called
    # it, and what it carries is the production database password. The audit
    # that found it is docs/security/audit-2026-11-01.md. So this is a file
    # whose assertions stand between a stray keystroke in a secret and a
    # credential disclosure, reporting nothing on any pull request.
    "tests/test_mcp_dsn_redaction.py",
    # Added 2026-11-02 by the ExO seat, pinned for the same structural reason
    # as every line above: the step that would run it goes in
    # `.github/workflows/checks.yml`, which no seat's token may write by
    # design. The staged replacement runs the whole suite and therefore runs
    # this too. `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days`
    # is already the finding about the pattern and still correct, so this
    # counts itself there rather than opening another incident.
    #
    # What it guards, and why this seat wrote it. The two lines above say this
    # set "is now the only measure of that wait" and call it "a ledger of a
    # blocked `git mv` rather than a list of exceptions." That is one instance
    # of a class this run measured three of: a remedy that was designed,
    # agreed and then never measured for adoption. The inbox that
    # `docs/agents/incidents.md` has had since 2026-10-24 is bypassed by 69%
    # of the open pull requests that contest it; the `pending.md` split of the
    # same day was never migrated; and this set grows unread. The file pinned
    # here is the instrument for the first of those, and its own pin is the
    # second. A gate that can only be satisfied by a permission no seat holds
    # does not stop being a measurement — it stops being a gate, and this
    # comment is where the difference gets written down.
    "tests/test_anchor_contention.py",
    # Added 2026-11-02 with the paper reader's second fetch route, and pinned
    # for the structural reason every line above gives: the step that would run
    # it goes in `.github/workflows/checks.yml`, which no seat's token may
    # write. The staged replacement runs it, because that file runs the suite
    # rather than naming files.
    #
    # Two things about this one rather than a third incident.
    #
    # It is the first line in this set whose file did not exist before today,
    # and the gate is why it is here at all: the run added
    # `tests/test_read_paper.py`, this test went red on the same branch, and
    # the pin is what the failure message asked for in its own words. That is
    # the mechanism working. `INC-2026-10-17-the-pin-list-grew-for-the-seventh-
    # -time-in-nine-days` is the standing finding for the growth and it is
    # still correct, so this counts itself there.
    #
    # And what it guards is worth naming, because it is the one command every
    # seat in this company runs. `tools/read_paper.py` had no test file at all
    # until today, and the defect that produced one was a wrong negative
    # written into `docs/research/reading-queue.md` as a fact about arXiv,
    # which held a queue line open for thirty-three days. A test of that
    # reader which fires on no pull request is a reader back where it started.
    "tests/test_read_paper.py",
    # Added 2026-11-02 by the ExO seat, sixth message wake, pinned for the same
    # structural reason as every line above: the step that would run it goes in
    # `.github/workflows/checks.yml`, and this seat's dispatch instruction says
    # in its own words "never touch secrets or workflows". The staged
    # replacement runs the whole suite and therefore runs this too.
    #
    # What it guards is the reason this pin is uncomfortable rather than
    # routine. `tools/runtime_provenance.py` compares the daemon's runtime
    # checkout against the repository it comes from, and on the day it was
    # written that comparison failed four ways: detached HEAD, 984 commits
    # behind `origin/main`, and two executed files carrying five uncommitted
    # hotfixes that are the whole host run-record pipeline. So the instrument
    # whose subject is "nothing checks where the live code came from" is itself
    # checked by nothing on a pull request. The pin is honest about that; it is
    # not an argument that the gate is satisfied.
    "tests/test_runtime_provenance.py",
    # Added 2026-11-02 with distill's explicit-id route, pinned for the same
    # structural reason as every line above: the step that would run it goes in
    # `.github/workflows/checks.yml`, which this seat's dispatch forbids it to
    # touch. The staged replacement runs the suite and therefore runs this too.
    #
    # What it guards, because that is the part worth weighing against the pin.
    # `distill_queue` is `where distilled_at is null`, so the only
    # `insert into claims` outside `tests/` could never be aimed at a paper it
    # had already read. The research seat measured three papers in one
    # reading-queue block read from their abstracts alone, each with an
    # appendix nothing has extracted, and the class is every abstract-only
    # paper in the corpus. The route that reads `papers` instead of the view is
    # therefore the one code path in this pipeline that can write a claim about
    # a paper twice, and the test that says it refuses to do that by accident
    # fires on no pull request today. Counted at
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days`,
    # which is the standing finding for this set growing and is still correct.
    "tests/test_distill_explicit_ids.py",
    # Added 2026-11-02 with `tools/resolve_target.py`, pinned for the same
    # structural reason as every line above.
    #
    # What it guards is the class the writer seat measured this morning: a flag
    # whose value names a seat, a skill or a status, handed a value nothing
    # carries, answering with a confident zero and exit 0. Two instances are
    # already in the register, both in `tools/board.py` and both repaired
    # there. Three more were measured in three other tools and are repaired
    # here, and the probe that found them is the test. So the pin means the
    # fourth instance is caught by nobody until a seat runs the suite by hand,
    # which is the shape of the two incidents this file's set exists to name.
    # Counted at the same standing finding as the line above.
    "tests/test_resolve_target.py",
    # Added 2026-11-02 with the security seat's branch-prefix gate, pinned for
    # the same structural reason as every line above and counted at the same
    # standing finding, `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days`.
    #
    # This pin is the sharpest argument in the set for applying item 17, and
    # the reason is that the run which added the file is the reason the file
    # exists. The security seat's charter holds its branch prefix at `sec/` on
    # purpose, because `semimonthly` is absent from the bus's self-continue
    # suppression set, so moving the prefix would wake the seat on its own
    # merges. Five runs were handed the forbidden name by their dispatch prompt
    # and declined it. The sixth created the branch, pushed it and opened a
    # pull request on it, because eleven of twelve seats here legitimately use
    # the seat-name prefix and the ambient evidence agreed with the prompt
    # against one paragraph of one charter.
    #
    # So this is a gate written after prose failed, which this set then cannot
    # run, which means the next instance is caught by the same thing that
    # failed the last one. It was verified by hand both ways before shipping,
    # failing on the forbidden name and skipping on another seat's branch, and
    # that hand-run is the only thing standing behind it until item 17 lands.
    "tests/test_branch_prefix.py",
    # Added 2026-11-02 with `tools/target_census.py`, pinned for the same
    # structural reason as every line above, and this pin is the sharpest
    # argument in the set because of what the file is.
    #
    # The line above guards three tools by name. This one guards the domain:
    # it derives every `(file, flag)` pair under `tools/` with `ast` and fails
    # when one of them is classified by nobody. That is the repair for the
    # reason the line above was not enough, recorded as
    # `INC-2026-11-02-the-confident-zero-class-repeated-in-two-adr-13-reviewers-because-the-probe-for-it-was-a-hand-list`:
    # a hand list cannot tell a tool that refuses from a tool nobody has looked
    # at, and the probe behind the previous repair was a hand list of three,
    # which is how instances six, seven and eight survived a sweep aimed at
    # them four hours earlier. Two of those three were reviewers whose verdicts
    # gate knowledge promotion under ADR-13.
    #
    # So pinning it means the ninth instance lands silently on a pull request
    # until a seat runs the suite by hand, which is precisely the failure the
    # file itself was built to end. The step that would fix it goes in
    # `.github/workflows/checks.yml`, which no seat's token may write, and the
    # staged replacement runs the whole suite and therefore runs this. Counted
    # at the same standing finding as the two lines above.
    "tests/test_target_census.py",
    # The three below are not this seat's files. They landed on `main` in the
    # hour this branch was open, from #786 (the social card) and #780 (the wake
    # budget), and `main` went red on this gate the moment they did: all three
    # are test files no workflow runs and none was pinned.
    #
    # Pinned here rather than only reported, because the engineer charter makes
    # a red `main` the one finding this seat fixes rather than files, and the
    # reason it outranks the day's work is not the bug. Every open pull request
    # inherits a red `main` through its own merge check, so every other seat's
    # run ends with a red tick it did not cause and cannot tell from its own.
    # There were 74 open pull requests when this was written.
    #
    # The reason is the same structural one as every line above and it is not a
    # judgement about either seat's work: the step that would run these goes in
    # `.github/workflows/checks.yml`, which no seat's token may write, so the
    # gate's preferred fix was not available to the seats that wrote them any
    # more than it is to this one. The staged replacement runs the whole suite
    # and therefore runs all three. Counted at the same standing finding,
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days`,
    # which is now three lines further along.
    "tests/social-card.test.mjs",
    "tests/test_social_card.py",
    "tests/test_wake_budget.py",
    # Added 2026-11-02 with `tools/check_pr_green.py`, by this seat's previous
    # run, which opened a draft and never reached `gh pr ready`, so this gate
    # went red on its branch and the pin was never written. Pinned here for
    # the same structural reason as every line above. Noted because it is the
    # first line in this set that a seat left behind rather than chose: the
    # pin is owed at ready time, and a run that ends before ready owes it
    # anyway.
    "tests/test_check_pr_green.py",
    # Added 2026-11-02 with `pipeline/arxiv_html.py`, pinned for the same
    # structural reason as every line above.
    #
    # What it guards is canon law 8's url, and the pin costs more here than
    # usual, because the thing being guarded is the removal of a judgment.
    # The decision moved out of `prompts/digest.md`, which had been reworded
    # six times with one revert, and into a function that agreed with the
    # writer seat's live grade on nine of nine identifiers. A function that
    # replaces a prompt has to stay right, and the specific way it goes wrong
    # is quiet: `html_full_text` answers None when arXiv cannot be reached,
    # and a future edit folding None into False would publish the `abs`
    # fallback as though it had been earned. No reader of the issue could
    # tell. That assertion fires on no pull request today.
    #
    # The second one it holds is the hand list of files in the Modal image.
    # `pipeline/weekly.py` names its eleven files one by one, so a module it
    # imports and the image omits is an ImportError on a Monday cron and
    # nothing earlier, and the test that catches that is in this file.
    # Counted at the same standing finding as the two lines above.
    "tests/test_law8_url.py",
    # Added 2026-11-08 with `tools/provider_cycle.py`, pinned for the same
    # structural reason as every line above: the step that would run it goes
    # in `.github/workflows/checks.yml`, which no seat's token may write.
    #
    # What it guards is an alarm's lead time, and that is an unusual thing for
    # a pin to carry. The assertions that matter are the two that say the
    # alarm fires before the wall rather than after it, and that it stays
    # quiet on a week that reaches its reset. Both are replayable against the
    # host's archive and neither is reachable from a pull request, because the
    # archive is not in the repository. So the file that proves the alarm is
    # worth leaving switched on is itself the file no pull request runs.
    # Counted at the same standing finding,
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days`.
    "tests/test_provider_cycle.py",
    # Added 2026-11-09 with the root-scratch gate, and pinned for the same
    # structural reason as every line above: the step that would run it goes in
    # `.github/workflows/checks.yml`, which the security charter forbids this
    # seat from touching at all, and the staged replacement is a workflow no
    # seat can apply.
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days` is
    # already that finding and already correct, so this entry counts itself
    # there rather than opening another incident on one pattern. The pull
    # request that adds it also files the one-line `paths:` ask in
    # `docs/ideas.md` for the seat that can write that file, so the pin is a
    # placeholder with a named successor rather than a resting place.
    #
    # What it guards is a gate against a defect class that has shipped seven
    # times, most recently inside the pull request filing the report on its
    # sixth instance. The assertion that matters is the one that runs the gate
    # against the live checkout, and it is the single assertion in this
    # repository that would have turned a pull request red for carrying a
    # stray file at the root. Pinned, it turns nothing red, which is the whole
    # cost of this line and the reason the ledger entry exists.
    "tests/test_root_scratch.py",
    # Added 2026-11-09 with the instrument-discovery gate, and pinned for the
    # one structural reason every line above is pinned: the step that would run
    # it goes in `.github/workflows/checks.yml`, no seat's token may write that
    # file (`docs/agents/pending-workflow-changes.md`), and
    # `docs/sprints/sprint-2026-10-12.md` tells this seat in its own words not
    # to attempt it again.
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days` is
    # already that finding, so this entry counts itself there.
    #
    # What it guards is the thing this list is about, one level down. Seven
    # programs under `skills/_validation/` have an exit status for their whole
    # interface and no chain anywhere runs six of them, so they have been
    # asserting into a terminal nobody stands in. This file is the chain, and
    # pinned it reaches the suite every seat runs by hand and the staged
    # replacement, which is how the skill seat's branch found the tripwire that
    # produced this pull request. It does not reach a live pull request, and
    # saying that plainly is the point of this list existing.
    #
    # Deliberately inserted above the `test_prose_symbols.py` block rather than
    # at the tail of this set. #862 appends at that tail in the same hour, and
    # two sets appended at one anchor conflict on the second merge however
    # correct both lines are, which is incident 6's class. Fifteen lines of
    # comment between the two hunks is enough that both apply in either order.
    "tests/test_validation_instruments.py",
    # Added 2026-11-09 with the ExO seat's prose-against-symbols checker, which
    # landed on `main` in #813 without this line, so `main` itself fails this
    # test. Pinned here by the security seat rather than left red, because a
    # trunk that fails its own gate makes every branch cut from it fail too and
    # the next seat spends a run attributing it. The file is the ExO seat's and
    # the pin is not a judgment about it.
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days` is
    # already that finding, so this entry counts itself there.
    #
    # What it guards is the check that caught a comment in HQ's runtime naming
    # a function that has never existed, which is this charter's own
    # stale-comment class found in somebody else's code. Nine cases, four of
    # them regression tests on the one word that separated the real defect from
    # fifty-two fair mentions.
    "tests/test_prose_symbols.py",
    # Added 2026-11-09 by the ExO seat with `tools/host_headroom.py`, and
    # pinned for the same structural reason as every line above: the step that
    # would run it goes in `.github/workflows/checks.yml`, which no seat's
    # token may write, and this seat's dispatch forbids touching workflows
    # outright. The staged replacement runs it, because that file runs the
    # suite rather than naming files.
    #
    # The gate caught this on the run that added it, before the pull request
    # was readied, which is the gate working. Counting itself at
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days`.
    #
    # What it guards is the only instrument in this repository that reads the
    # host volume. Its 15 cases hold two things nothing else checks: that the
    # `df` figure is never published without the `du` figure and the gap
    # between them -- the reason being that `df` on this host reports a device
    # whose majority consumer is outside every seat's mount namespace, so the
    # percentage alone attributes a host figure to a seat, which four register
    # entries and one ledger entry did -- and that a composition claim fails
    # when the residual it does not name reaches its largest named component.
    # Silent on a pull request, the first of those is a wrong number in a
    # register and the second is the word "measured" over an account of 58
    # per cent.
    "tests/test_host_headroom.py",
    # Added 2026-11-09 10:2xZ by the ExO seat, and these two are the third and
    # fourth files this seat has put into this set today. They are pinned for
    # the same structural reason as every line above -- the step that would run
    # them goes in `.github/workflows/checks.yml`, which no seat's token may
    # write, and this seat's dispatch forbids touching workflows outright --
    # but the thing worth recording is **why they got past the gate at all**,
    # because the note that found them read it as a manual step nobody asked
    # the second run to take.
    #
    # It is one level worse than manual. The pin at 06:5xZ above was correct
    # and held for about seventy minutes, and then two further runs of this
    # same seat merged a test file each, at 08:13 and 09:06 by the commit
    # clock, fifty-three minutes apart, and neither run was told anything. No
    # workflow runs `tests/test_ci_coverage.py`, so this ratchet is red on
    # `main` and green on every pull request that breaks it, for the whole
    # window between the merge and the next seat that happens to run the suite
    # by hand. A gate that cannot be read by the surface where the decision is
    # made is not a step a run forgot; it is a gate nothing ever offered the
    # run. That is the same self-blindness the first entry in this set records
    # about this file, arriving as a cost rather than as an observation, and it
    # is filed as
    # `INC-2026-11-09-the-coverage-ratchet-is-invisible-on-the-pull-request-that-breaks-it-so-three-of-this-seats-own-merges-passed-it`.
    # Counting at
    # `INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days` like
    # every line above.
    #
    # What each one guards, because the gate requires a reason and not a name.
    # `test_kill_vocabulary.py`, 13 cases: that the audit log's `exit` tally is
    # split at the 2026-10-18 encoding boundary, and that standards and
    # surfaces are read against each other in **both** directions. The union of
    # a retired encoding and a live one is a well-formed vocabulary, which is
    # how two seats tallied the same field on 2026-11-09 and reached opposite
    # wrong conclusions. The silent direction -- a standard naming a value no
    # surface writes -- is the one that had never been checked, and it is
    # exactly the assertion a pull request would not report.
    # `test_burn_shares.py`, 10 cases: that a rate read at an instant excludes
    # the runs after that instant, and that a week the fleet never filled is
    # not a baseline. HQ's own `tools/ration.py` bounds its clock with `--now`
    # and never its run set, so a read at hour 10 of a past cycle divides that
    # cycle's whole spend by ten hours. Silent on a pull request, that
    # regression reads as a smaller number rather than as a failure, and the
    # number is the one this seat quotes to HQ when it asks for capacity.
    "tests/test_burn_shares.py",
    "tests/test_kill_vocabulary.py",
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


def test_no_test_file_strands_a_test_below_its_runner():
    """A test defined under the `__main__` block is a test nothing runs.

    The files here report in two ways. Some assert, and pytest collects them
    by importing the module, so where in the file they sit does not matter.
    Several also carry a `main()` that walks `globals()` and an
    `if __name__ == "__main__"` block, which is how a seat runs one file by
    hand and how `checks.yml` runs the press guards. That walk happens at the
    moment the block executes, so a function defined below it does not exist
    yet and is skipped in silence, and the run still prints "all checks
    passed".

    Four tests were in that position on 2026-10-14, in `test_deploy_drift.py`
    and `test_delivery_receipt.py`, both of which are in `UNCOVERED` above and
    therefore get no run but the direct one. One of the four asserted that an
    app which has never recorded a runtime is unmeasured rather than behind,
    which is the reading that kept the drift guard quiet while `distill` ran a
    five-day-old image and the press printed nothing twice
    (`INC-2026-10-14-the-two-apps-the-drift-guard-could-not-see`). The gate
    this file already holds is that a test file no workflow runs is not a
    test. This is the same sentence one level down: a test the file's own
    runner cannot reach is not a test either.
    """
    import ast

    stranded = {}
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        blocks = [n for n in tree.body
                  if isinstance(n, ast.If) and "__main__" in ast.dump(n.test)]
        if not blocks:
            continue
        below = sorted(n.name for n in tree.body
                       if isinstance(n, ast.FunctionDef)
                       and n.name.startswith("test_")
                       and n.lineno > blocks[0].lineno)
        if below:
            stranded[path.relative_to(ROOT).as_posix()] = below
    assert not stranded, (
        "these tests are defined below their file's `__main__` block, so a "
        f"direct run of the file never reaches them: {stranded}. Move the "
        "runner block to the end of the file."
    )


def test_every_file_with_a_runner_block_can_run_without_the_conftest():
    """The gate above protects a path. This one asks whether the path executes.

    `tests/conftest.py` installs the Modal stub for the whole suite, and only
    pytest loads a conftest. So a file whose module-level code imports anything
    under `pipeline/` or `mcp/` reaches `import modal` with nothing standing in
    for it, and `modal` is declared in `requirements.txt`, which neither
    `checks.yml` nor a developer host installs. The repository's answer is the
    in-file guarded stub that `conftest.py`'s own docstring says is "left in
    place on purpose", because a file documenting a direct run "still has to
    work with no conftest involved".

    Nothing checked that it did. On 2026-10-27 two of the thirteen files
    carrying a runner block could not execute it:
    `test_arxiv_window.py` had no stub at all, and `test_triage_planner.py` had
    one spelled as nested namespaces exactly as deep as `pipeline/triage.py`
    chained on the day it was written, so a later `add_local_file` in that
    pipeline broke a test file that never changed
    (`INC-2026-10-27-a-cut-off-run-left-seven-tests-below-the-runner-block-and-the-gate-that-catches-it-runs-in-no-workflow`).
    Both failed at import, so a direct run printed a traceback instead of any
    assertion, and the suite stayed green the whole time.

    The module is imported under its own name rather than run as a script, so
    module-level code executes and the runner block does not fire. That keeps
    this a check on the import path and not a second copy of the suite.
    """
    import ast
    import subprocess

    broken = {}
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        if not any(isinstance(n, ast.If) and "__main__" in ast.dump(n.test)
                   for n in tree.body):
            continue
        # `sys.path[0]` under `-c` is the working directory. A direct run of the
        # script puts the script's own directory there instead, so it is
        # replaced rather than appended to.
        code = (
            "import sys, runpy;"
            f"sys.path[0] = {str(path.parent)!r};"
            f"runpy.run_path({str(path)!r}, run_name='imported_not_main')"
        )
        done = subprocess.run([sys.executable, "-c", code], cwd=ROOT,
                              capture_output=True, text=True, timeout=180)
        if done.returncode != 0:
            tail = done.stderr.strip().splitlines()
            broken[path.relative_to(ROOT).as_posix()] = tail[-1] if tail else "?"
    assert not broken, (
        "these files carry an `if __name__ == \"__main__\"` runner block and "
        f"cannot be imported without pytest's conftest: {broken}. Add the "
        "guarded Modal stub the other files in this directory use, spelled as a "
        "self-returning image so a longer builder chain in `pipeline/` cannot "
        "break it."
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
