"""Does the corpus reader tell a run that met a wall from one that wrote about one.

Run with `python3 -m pytest tests/test_wall_encounters.py -q`.

Like `tests/test_cron_firing.py`, every test here builds a log tree in a
temporary directory in the host's exact format. Nothing reads
`/srv/asc/state`, because a test that needs the host's disk is a test nobody
runs on a pull request.

The prose fixtures are real. `EXO_PROSE_WEEKLY` is a clause of the closing
summary of `alexandria-exo` 2026-11-01T23-04-44-468Z, which ran 77 turns and
exited zero, and `EXO_PROSE_SESSION` is from `epitome-exo`
2026-10-26T09-02-46-416Z at 118 turns. Both were counted as refusals by a
file-wide grep and offered as evidence that an in-run retry survives a wall.
They are quoted rather than paraphrased on purpose: a paraphrase would drop
whichever word the matcher actually turns on, and then the test would pass
against a reader that cannot see the real thing
(`INC-2026-11-09-the-three-runs-that-closed-the-corpus-question-never-met-a-wall`).
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import cron_firing as cf  # noqa: E402
from tools import wall_encounters as we  # noqa: E402

HEADER = (
    "# epito run {seat} {run_id}\n"
    "# trigger={trigger} model=claude-opus-5 repo=alexandrapaiz/alexandria "
    "ref=(default) executor=claude\n"
    "$ git clone --depth 1  https://github.com/alexandrapaiz/alexandria.git\n"
    "$ claude -p <prompt> --permission-mode bypassPermissions\n"
    "# env passed: PATH, HOME, USER, GH_TOKEN, BOARD_API_URL\n"
    "---\n")

# The refusal sentences, as the provider sends them.
WEEKLY = "You've hit your weekly limit · resets 11pm (UTC)"
SESSION = "You've hit your session limit · resets 9am (UTC)"
SPEND = ("You've hit your org's monthly spend limit · ask your admin to raise "
         "it at claude.ai/admin-settings/usage · your weekly limit resets "
         "Nov 8, 11pm (UTC)")

# The same sentences inside a run's own report of somebody else's refusal.
EXO_PROSE_WEEKLY = (
    "**1. The portfolio spent its 168-hour provider week in 30.6 hours.** "
    "334 runs across 31 seats and 5 companies were refused for 137 hours. "
    "The cause is read, not inferred — every log carries `429` with "
    "\"You've hit your weekly limit.\"")
EXO_PROSE_SESSION = (
    "The payload was right: the run at 2026-10-26T06:04:46Z was cut by the "
    "provider at **turn 78** — `terminal_reason: api_error`, *\"You've hit "
    "your session limit · resets 9am (UTC)\"*, $6.17, 17m13s — and its branch "
    "carried exactly one commit. I continued it rather than restarting it.")


def write_log(root, seat, stamp, trigger, result=None, exit_code=None,
              pr=None, turns=None):
    run_id = f"{stamp}-{trigger}"
    directory = Path(root) / seat
    directory.mkdir(parents=True, exist_ok=True)
    body = HEADER.format(seat=seat, run_id=run_id, trigger=trigger)
    if result is not None:
        body += json.dumps(result) + "\n\n"
    body += "---\n"
    body += (f"# exit={exit_code} pr={pr or '-'} session=aa3f969a "
             f"turns={turns if turns is not None else 0}\n")
    path = directory / f"{run_id}.log"
    path.write_text(body, encoding="utf-8")
    return path


def refused(sentence):
    """What the host writes for a run the provider stopped."""
    return {"type": "result", "is_error": True, "num_turns": 1,
            "api_error_status": 429, "result": sentence,
            "terminal_reason": "api_error", "subtype": "success"}


def refused_mid_run(sentence, turns):
    """The same, for a run that had got somewhere first."""
    return {"type": "result", "is_error": True, "num_turns": turns,
            "api_error_status": 429, "result": sentence,
            "terminal_reason": "api_error", "subtype": "success"}


def completed(text="Done.", turns=25):
    """And what it writes for a run that finished. Note `subtype`.

    `subtype` reads `success` on a refused run too — the real 78-turn refusal
    of 2026-10-26 carries it — so it is in these fixtures precisely so that
    nothing here is tempted to classify on it.
    """
    return {"type": "result", "is_error": False, "num_turns": turns,
            "api_error_status": None, "result": text,
            "terminal_reason": "completed", "subtype": "success"}


# --- the distinction itself -----------------------------------------------

def test_a_refused_run_met_a_wall(tmp_path):
    write_log(tmp_path, "alexandria-engineer", "2026-11-01T13-00-27-000Z",
              "cron", refused(WEEKLY), exit_code=1, turns=1)
    run, = cf.read_runs(tmp_path)
    assert we.classify(run) == we.MET_A_WALL
    assert run["refusal"] == "weekly-limit"
    assert run["wall_prose"] is False


def test_a_run_quoting_another_runs_refusal_did_not_meet_one(tmp_path):
    """The defect that closed the corpus question with the wrong cause."""
    write_log(tmp_path, "alexandria-exo", "2026-11-01T23-04-44-468Z", "hook",
              completed(EXO_PROSE_WEEKLY, turns=77), exit_code=0, turns=77)
    run, = cf.read_runs(tmp_path)
    assert we.classify(run) == we.WROTE_ABOUT_ONE
    assert run["refusal"] is None
    assert run["wall_prose"] is True
    # And the thing that matters: it is not a survival.
    assert we.survived(run) is False


def test_the_other_two_prose_runs_read_the_same_way(tmp_path):
    write_log(tmp_path, "epitome-exo", "2026-10-26T09-02-46-416Z", "hook",
              completed(EXO_PROSE_SESSION, turns=118), exit_code=0, turns=118)
    run, = cf.read_runs(tmp_path)
    assert we.classify(run) == we.WROTE_ABOUT_ONE
    assert we.survived(run) is False


def test_a_quiet_run_is_neither(tmp_path):
    write_log(tmp_path, "alexandria-writer", "2026-11-01T09-00-00-000Z",
              "message", completed(), exit_code=0, turns=25)
    run, = cf.read_runs(tmp_path)
    assert we.classify(run) == we.NEITHER
    assert run["wall_prose"] is False


# --- the two counts, side by side -----------------------------------------

def test_the_grep_count_and_the_refusal_count_differ_by_the_prose(tmp_path):
    """Both readings are right; the survey is what keeps them apart."""
    write_log(tmp_path, "alexandria-engineer", "2026-11-01T13-00-27-000Z",
              "cron", refused(WEEKLY), exit_code=1, turns=1)
    write_log(tmp_path, "alexandria-engineer", "2026-11-01T14-00-27-000Z",
              "cron", refused(SESSION), exit_code=1, turns=1)
    write_log(tmp_path, "alexandria-engineer", "2026-11-05T14-00-27-000Z",
              "cron", refused(SPEND), exit_code=1, turns=1)
    write_log(tmp_path, "alexandria-exo", "2026-11-01T23-04-44-468Z", "hook",
              completed(EXO_PROSE_WEEKLY, turns=77), exit_code=0, turns=77)
    write_log(tmp_path, "alexandria-writer", "2026-11-01T09-00-00-000Z",
              "message", completed(), exit_code=0, turns=25)

    found = we.survey(tmp_path)
    assert found["runs"] == 5
    assert found["counts"][we.MET_A_WALL] == 3
    assert found["counts"][we.WROTE_ABOUT_ONE] == 1
    assert found["counts"][we.NEITHER] == 1
    assert dict(found["scopes"]) == {
        "weekly-limit": 1, "session-limit": 1, "monthly-spend": 1}
    assert [r["seat"] for r in found["prose"]] == ["alexandria-exo"]
    assert found["survivals"] == []


def test_the_spend_sentence_is_not_dragged_into_weekly_by_its_own_tail(tmp_path):
    """The monthly cap names the weekly reset inside itself. Order is the fix."""
    write_log(tmp_path, "alexandria-market", "2026-11-06T11-00-10-855Z",
              "cron", refused(SPEND), exit_code=1, turns=1)
    run, = cf.read_runs(tmp_path)
    assert run["refusal"] == "monthly-spend"
    assert we.classify(run) == we.MET_A_WALL


# --- the survival question ------------------------------------------------

def test_a_wall_met_at_turn_one_is_not_a_survival(tmp_path):
    write_log(tmp_path, "alexandria-engineer", "2026-11-01T13-00-27-000Z",
              "cron", refused(WEEKLY), exit_code=1, turns=1)
    run, = cf.read_runs(tmp_path)
    assert we.survived(run) is False


def test_a_wall_met_mid_run_is_not_a_survival_when_the_host_exits_nonzero(tmp_path):
    """The real 2026-10-26 control: 78 turns, cut, exit 1."""
    write_log(tmp_path, "epitome-exo", "2026-10-26T06-04-46-651Z", "message",
              refused_mid_run(SESSION, 78), exit_code=1, turns=78)
    run, = cf.read_runs(tmp_path)
    assert we.classify(run) == we.MET_A_WALL
    assert we.survived(run) is False


def test_a_survival_is_what_it_would_take_and_the_reader_can_see_one(tmp_path):
    """Built here because the host has none, and a zero from a reader that
    cannot see the thing it counts is not a measurement
    (§2b's rule: prove the instrument can see the seat before you believe a
    zero from it). This is that proof for `survived`."""
    write_log(tmp_path, "alexandria-engineer", "2026-11-01T13-00-27-000Z",
              "cron", refused_mid_run(WEEKLY, 40), exit_code=0, turns=40)
    run, = cf.read_runs(tmp_path)
    assert we.survived(run) is True
    found = we.survey(tmp_path)
    assert len(found["survivals"]) == 1
    assert we.main(["--root", str(tmp_path), "--survivals"]) == 1


def test_the_survival_gate_is_quiet_when_there_are_none(tmp_path):
    write_log(tmp_path, "alexandria-engineer", "2026-11-01T13-00-27-000Z",
              "cron", refused(WEEKLY), exit_code=1, turns=1)
    assert we.main(["--root", str(tmp_path), "--survivals"]) == 0
    assert we.main(["--root", str(tmp_path)]) == 0


# --- the matcher -----------------------------------------------------------

def test_the_three_real_sentences_are_all_recognised_as_prose():
    for sentence in (WEEKLY, SESSION, SPEND, EXO_PROSE_WEEKLY,
                     EXO_PROSE_SESSION):
        assert cf.mentions_a_wall(sentence) is True


def test_prose_about_limits_that_is_not_a_limit_sentence_is_not_matched():
    """A charter, a run note and a relay page all use these words."""
    for sentence in (
            "the weekly limit resets on Sunday",
            "max_turns is a cap and not a limit",
            "I asked HQ to ration the roster against the weekly pool",
            "39 refused, all at turn one, all spend",
            None, ""):
        assert cf.mentions_a_wall(sentence) is False


# --- the seat argument, which must never answer about a seat nobody named ----

def test_an_unresolvable_seat_is_refused_rather_than_counted_as_zero(tmp_path, capsys):
    """`INC-2026-10-27-two-readers-answer-a-wrong-seat-name-with-a-confident-zero`.

    A zero is the right answer to "this seat met no walls" and the wrong answer
    to "there is no such seat", and nothing in this tool's output distinguishes
    them. So the resolution happens before any reading, and it exits 2 naming
    the value it refused — the survivals gate in particular would otherwise
    report all-clear for a typo.
    """
    write_log(tmp_path, "alexandria-exo", "2026-11-01T23-04-44-468Z", "hook",
              completed(EXO_PROSE_WEEKLY, turns=77), exit_code=0, turns=77)
    assert we.main(["--root", str(tmp_path), "--seat", "no-such-seat"]) == 2
    said = capsys.readouterr()
    assert "no-such-seat" in said.err
    # And the gate does not report clean on the refusal either.
    assert we.main(["--root", str(tmp_path), "--seat", "no-such-seat",
                    "--survivals"]) == 2


def test_a_bare_seat_name_resolves_to_the_directory_the_host_wrote(tmp_path, capsys):
    write_log(tmp_path, "alexandria-exo", "2026-11-01T23-04-44-468Z", "hook",
              completed(EXO_PROSE_WEEKLY, turns=77), exit_code=0, turns=77)
    write_log(tmp_path, "alexandria-writer", "2026-11-01T09-00-00-000Z",
              "message", completed(), exit_code=0, turns=25)
    assert we.main(["--root", str(tmp_path), "--seat", "exo"]) == 0
    said = capsys.readouterr()
    assert "reading alexandria-exo for --seat 'exo'" in said.err
    assert "1 runs under" in said.out


def test_a_seat_that_exists_and_met_nothing_is_a_zero_the_tool_may_report(tmp_path):
    """The other half, so the refusal above is not read as banning zeroes."""
    write_log(tmp_path, "alexandria-writer", "2026-11-01T09-00-00-000Z",
              "message", completed(), exit_code=0, turns=25)
    found = we.survey(tmp_path, seat="alexandria-writer")
    assert found["runs"] == 1
    assert found["counts"][we.MET_A_WALL] == 0
    assert we.main(["--root", str(tmp_path), "--seat", "alexandria-writer"]) == 0
