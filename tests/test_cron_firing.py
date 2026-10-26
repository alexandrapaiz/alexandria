"""Does the firing reader tell a lost cycle from a clock that was never set.

Run with `python3 -m pytest tests/test_cron_firing.py -q`.

`tools/cron_firing.py` reads the host's own run logs, which live outside the
repository and are not present on a pull request checkout. So every test here
builds a log tree in a temporary directory in the host's exact format, taken
from a real log of 2026-10-25 with the prompt and the result prose replaced.
Nothing here reads `/srv/asc/state`, because a test that needs the host's disk
is a test nobody runs on a pull request.

The three states are the whole point of the file and they are what most of
these assert. The one worth saying out loud is `unseen`: a slot with no row is
reported as a question rather than a failure, because a retired clock and a
clock that did not fire leave the same absence, and a check that calls the
first one broken cries wolf every week until somebody switches it off.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import cron_firing as cf  # noqa: E402

UTC = timezone.utc

HEADER = (
    "# epito run {seat} {run_id}\n"
    "# trigger={trigger} model=claude-opus-5 repo=alexandrapaiz/alexandria "
    "ref=(default) executor=claude\n"
    "$ git clone --depth 1  https://github.com/alexandrapaiz/alexandria.git\n"
    "$ claude -p <prompt> --permission-mode bypassPermissions\n"
    "# env passed: PATH, HOME, USER, GH_TOKEN, BOARD_API_URL\n"
    "---\n")


def write_log(root, seat, stamp, trigger, result=None, exit_code=None,
              pr=None, turns=None, trailer=True):
    """One run log in the host's format. `trailer=False` is a run still going."""
    run_id = f"{stamp}-{trigger}"
    directory = Path(root) / seat
    directory.mkdir(parents=True, exist_ok=True)
    body = HEADER.format(seat=seat, run_id=run_id, trigger=trigger)
    if result is not None:
        body += json.dumps(result) + "\n\n"
    body += "---\n"
    if trailer:
        body += (f"# exit={exit_code} pr={pr or '-'} "
                 f"session=aa3f969a turns={turns if turns is not None else 0}\n")
    path = directory / f"{run_id}.log"
    path.write_text(body, encoding="utf-8")
    return path


def refused(sentence, status=429):
    return {"type": "result", "is_error": True, "num_turns": 1,
            "api_error_status": status, "result": sentence,
            "terminal_reason": "api_error", "duration_ms": 351}


def completed(text="Done."):
    return {"type": "result", "is_error": False, "num_turns": 25,
            "api_error_status": None, "result": text,
            "terminal_reason": "completed", "duration_ms": 310922}


# The clock this file reasons about, so a test never depends on the real one.
NOW = datetime(2026, 10, 25, 23, 59, tzinfo=UTC)


# --- parsing one log ------------------------------------------------------

def test_filename_gives_the_start_and_the_trigger(tmp_path):
    write_log(tmp_path, "alexandria-engineer", "2026-10-25T11-06-03-756Z",
              "cron", refused("You've hit your weekly limit · resets 11pm (UTC)"),
              exit_code=1, turns=1)
    run, = cf.read_runs(tmp_path)
    assert run["seat"] == "alexandria-engineer"
    assert run["trigger"] == "cron"
    assert run["started"] == datetime(2026, 10, 25, 11, 6, 3, 756000, tzinfo=UTC)
    assert run["day"] == "2026-10-25"
    assert cf.slot(run) == 11 * 60 + 6


def test_a_file_that_is_not_a_run_log_is_skipped_rather_than_guessed_at(tmp_path):
    (tmp_path / "alexandria-engineer").mkdir()
    (tmp_path / "alexandria-engineer" / "notes.txt").write_text("not a log")
    (tmp_path / "alexandria-engineer" / "2026-10-25-cron.log").write_text("no time")
    assert cf.read_runs(tmp_path) == []


def test_the_trailer_is_where_the_pull_request_comes_from(tmp_path):
    write_log(tmp_path, "alexandria-engineer", "2026-10-25T23-02-09-113Z",
              "hook", completed(), exit_code=0, turns=25,
              pr="https://github.com/alexandrapaiz/alexandria/pull/516")
    run, = cf.read_runs(tmp_path)
    assert run["pr"].endswith("/pull/516")
    assert run["exit_code"] == 0
    assert run["turns"] == 25
    assert run["truncated"] is False


def test_pr_dash_means_no_pull_request_rather_than_a_pull_request_named_dash(tmp_path):
    write_log(tmp_path, "alexandria-pm", "2026-10-25T11-05-00-000Z", "cron",
              refused("You've hit your weekly limit · resets 11pm (UTC)"),
              exit_code=1, turns=1)
    run, = cf.read_runs(tmp_path)
    assert run["pr"] is None


def test_a_truncated_result_line_does_not_lose_the_facts_before_it(tmp_path):
    path = write_log(tmp_path, "alexandria-exo", "2026-10-25T14-00-04-675Z",
                     "cron", refused("weekly limit"), exit_code=1, turns=1)
    text = path.read_text()
    path.write_text(text.replace('"result": "weekly limit"', '"result": "week'))
    run, = cf.read_runs(tmp_path)
    assert run["trigger"] == "cron"
    assert run["exit_code"] == 1
    assert run["refusal"] is None  # unparseable, so nothing is claimed about it


def test_a_missing_log_root_is_an_empty_reading_and_not_a_traceback(tmp_path):
    assert cf.read_runs(tmp_path / "never-mounted") == []


def test_the_seat_filter_reads_one_directory(tmp_path):
    write_log(tmp_path, "alexandria-engineer", "2026-10-25T11-06-00-000Z",
              "cron", completed(), exit_code=0, pr="x/pull/1", turns=4)
    write_log(tmp_path, "ursa-engineer", "2026-10-25T11-26-00-000Z",
              "cron", completed(), exit_code=0, pr="x/pull/2", turns=4)
    seats = {r["seat"] for r in cf.read_runs(tmp_path, seat="ursa-engineer")}
    assert seats == {"ursa-engineer"}


# --- the two limits are two things ---------------------------------------

@pytest.mark.parametrize("sentence,expected", [
    ("You've hit your weekly limit · resets 11pm (UTC)", "weekly-limit"),
    ("You've hit your 5-hour limit · resets 4am", "session-limit"),
    ("Your session limit was reached", "session-limit"),
    ("Overloaded", "unclassified-429"),
])
def test_the_refusal_sentence_is_the_only_discriminator(sentence, expected):
    assert cf.classify_refusal(sentence, 429) == expected


def test_the_result_line_is_found_whatever_its_whitespace(tmp_path):
    """The first version of this reader matched `"type":"result"` as text.

    It read every log on this host correctly and misread a fixture whose only
    difference was a space after the colon, and the misreading was quiet: the
    refusal stopped being classified and the run read as a plain non-zero
    exit, so the lost-cycle count stayed right and the reason went missing.
    """
    path = write_log(tmp_path, "alexandria-engineer", "2026-10-25T11-06-03-756Z",
                     "cron", refused("You've hit your weekly limit"),
                     exit_code=1, turns=1)
    tight = json.dumps(refused("You've hit your weekly limit"),
                       separators=(",", ":"))
    spaced = json.dumps(refused("You've hit your weekly limit"),
                        separators=(" , ", " : "))
    for variant in (tight, spaced):
        path.write_text(HEADER.format(seat="alexandria-engineer",
                                      run_id="2026-10-25T11-06-03-756Z-cron",
                                      trigger="cron")
                        + variant + "\n\n---\n# exit=1 pr=- turns=1\n")
        run, = cf.read_runs(tmp_path)
        assert run["refusal"] == "weekly-limit", variant[:40]


def test_a_non_429_is_not_a_limit_at_all():
    assert cf.classify_refusal("weekly limit", 500) is None
    assert cf.classify_refusal(None, None) is None


def test_the_weekly_and_session_limits_do_not_collapse_into_one_word(tmp_path):
    write_log(tmp_path, "alexandria-engineer", "2026-10-25T12-06-00-000Z",
              "cron", refused("You've hit your weekly limit · resets 11pm (UTC)"),
              exit_code=1, turns=1)
    write_log(tmp_path, "engineer", "2026-10-25T00-06-00-000Z", "cron",
              refused("You've hit your 5-hour limit · resets 4am"),
              exit_code=1, turns=1)
    result = cf.judge(cf.read_runs(tmp_path), "2026-10-25", now=NOW)
    assert sorted(f["why"] for f in result["lost"]) == [
        "session-limit", "weekly-limit"]


# --- the three states ----------------------------------------------------

def test_a_slot_that_fired_and_shipped_is_read_not_inferred(tmp_path):
    write_log(tmp_path, "exo-centralizer", "2026-10-25T23-00-00-000Z", "cron",
              completed(), exit_code=0, turns=30,
              pr="https://github.com/alexandrapaiz/alexandra-systems/pull/465")
    result = cf.judge(cf.read_runs(tmp_path), "2026-10-25", now=NOW)
    finding, = result["findings"]
    assert finding["state"] == "shipped"
    assert finding["slot"] == "23:00Z"
    assert result["lost"] == []


def test_a_slot_that_fired_and_was_refused_is_a_lost_cycle(tmp_path):
    write_log(tmp_path, "alexandria-engineer", "2026-10-25T11-06-03-756Z",
              "cron", refused("You've hit your weekly limit · resets 11pm (UTC)"),
              exit_code=1, turns=1)
    result = cf.judge(cf.read_runs(tmp_path), "2026-10-25", now=NOW)
    finding, = result["findings"]
    assert finding["state"] == "lost"
    assert finding["why"] == "weekly-limit"
    assert finding["turns"] == 1


def test_a_run_that_exited_clean_and_shipped_nothing_is_still_a_lost_cycle(tmp_path):
    """Incident 3's failure mode, and the reason ship-first is in every charter."""
    write_log(tmp_path, "alexandria-writer", "2026-10-25T16-00-00-000Z", "cron",
              completed("I had a look around and decided not to open a PR."),
              exit_code=0, turns=88)
    result = cf.judge(cf.read_runs(tmp_path), "2026-10-25", now=NOW)
    finding, = result["findings"]
    assert finding["state"] == "lost"
    assert finding["why"] == "silent"


def test_a_nonzero_exit_without_an_api_error_is_named_as_such(tmp_path):
    write_log(tmp_path, "alexandria-skill", "2026-10-25T09-00-00-000Z", "cron",
              completed(), exit_code=2, turns=12)
    result = cf.judge(cf.read_runs(tmp_path), "2026-10-25", now=NOW)
    assert result["lost"][0]["why"] == "nonzero-exit"


def test_a_young_run_with_no_trailer_is_working_rather_than_lost(tmp_path):
    """The run reading this file is itself in that state, every time it runs."""
    write_log(tmp_path, "alexandria-engineer", "2026-10-25T23-52-25-817Z",
              "cron", trailer=False)
    result = cf.judge(cf.read_runs(tmp_path), "2026-10-25", now=NOW)
    finding, = result["findings"]
    assert finding["state"] == "in-flight"
    assert result["lost"] == []


def test_an_old_run_with_no_trailer_is_a_run_nobody_came_back_for(tmp_path):
    write_log(tmp_path, "alexandria-engineer", "2026-10-25T03-00-00-000Z",
              "cron", trailer=False)
    result = cf.judge(cf.read_runs(tmp_path), "2026-10-25", now=NOW)
    finding, = result["findings"]
    assert finding["state"] == "lost"
    assert finding["why"] == "no-trailer"


def test_the_grace_boundary_is_the_run_age_and_nothing_else(tmp_path):
    write_log(tmp_path, "alexandria-engineer", "2026-10-25T22-00-00-000Z",
              "cron", trailer=False)
    run, = cf.read_runs(tmp_path)
    just_inside = datetime(2026, 10, 25, 23, 29, tzinfo=UTC)
    just_outside = datetime(2026, 10, 25, 23, 31, tzinfo=UTC)
    assert cf.verdict_of(run, now=just_inside) == "in-flight"
    assert cf.verdict_of(run, now=just_outside) == "no-trailer"


# --- the absence that is a question -------------------------------------

def test_a_habitual_slot_with_no_row_is_a_question_carrying_its_evidence(tmp_path):
    for day in ("23", "24"):
        write_log(tmp_path, "alexandria-engineer", f"2026-10-{day}T23-06-12-967Z",
                  "cron", completed(), exit_code=0, turns=20, pr="x/pull/1")
    result = cf.judge(cf.read_runs(tmp_path), "2026-10-25", now=NOW)
    finding, = result["findings"]
    assert finding["state"] == "unseen"
    assert finding["slot"] == "23:06Z"
    assert finding["evidence"] == ["2026-10-23", "2026-10-24"]
    assert result["lost"] == []


def test_an_unseen_slot_never_counts_as_a_failure(tmp_path):
    """The whole reason the third state exists. A retired clock is not a bug."""
    write_log(tmp_path, "okr", "2026-10-18T16-00-00-000Z", "cron",
              completed(), exit_code=0, turns=9, pr="x/pull/3")
    result = cf.judge(cf.read_runs(tmp_path), "2026-10-25", now=NOW)
    assert [f["state"] for f in result["findings"]] == ["unseen"]
    assert cf.main(["--day", "2026-10-25", "--root", str(tmp_path)]) == 0


def test_a_slot_that_did_fire_raises_no_question_about_itself(tmp_path):
    for day in ("23", "24"):
        write_log(tmp_path, "alexandria-engineer", f"2026-10-{day}T11-06-00-000Z",
                  "cron", completed(), exit_code=0, turns=20, pr="x/pull/1")
    write_log(tmp_path, "alexandria-engineer", "2026-10-25T11-06-03-756Z", "cron",
              refused("You've hit your weekly limit · resets 11pm (UTC)"),
              exit_code=1, turns=1)
    result = cf.judge(cf.read_runs(tmp_path), "2026-10-25", now=NOW)
    assert [f["state"] for f in result["findings"]] == ["lost"]


def test_a_firing_a_few_minutes_off_is_the_same_slot(tmp_path):
    """11:06:03 one day and 11:06:07 the next is one clock, not two."""
    write_log(tmp_path, "alexandria-engineer", "2026-10-24T11-06-07-705Z", "cron",
              completed(), exit_code=0, turns=20, pr="x/pull/1")
    write_log(tmp_path, "alexandria-engineer", "2026-10-25T11-13-00-000Z", "cron",
              completed(), exit_code=0, turns=20, pr="x/pull/2")
    result = cf.judge(cf.read_runs(tmp_path), "2026-10-25", now=NOW)
    assert [f["state"] for f in result["findings"]] == ["shipped"]


def test_a_firing_far_off_the_habitual_slot_leaves_the_question_standing(tmp_path):
    """2026-10-25: the evening slot had no row and a cron ran 46 minutes later.

    Whether that was the slot requeued or a different clock is not readable
    from a log, so the reading reports both facts and claims neither.
    """
    for day in ("23", "24"):
        write_log(tmp_path, "alexandria-engineer", f"2026-10-{day}T23-06-12-967Z",
                  "cron", completed(), exit_code=0, turns=20, pr="x/pull/1")
    write_log(tmp_path, "alexandria-engineer", "2026-10-25T23-52-25-817Z",
              "cron", trailer=False)
    result = cf.judge(cf.read_runs(tmp_path), "2026-10-25", now=NOW)
    assert [(f["slot"], f["state"]) for f in result["findings"]] == [
        ("23:06Z", "unseen"), ("23:52Z", "in-flight")]


def test_the_history_window_is_what_bounds_the_question(tmp_path):
    write_log(tmp_path, "okr", "2026-09-01T16-00-00-000Z", "cron",
              completed(), exit_code=0, turns=9, pr="x/pull/3")
    result = cf.judge(cf.read_runs(tmp_path), "2026-10-25", now=NOW)
    assert result["findings"] == []


# --- triggers other than a clock ----------------------------------------

def test_a_wake_that_is_not_a_clock_is_not_a_cadence_finding(tmp_path):
    """A message or hook wake that shipped nothing is somebody else's problem.

    This file is about cadence. A hook wake has no slot and no schedule to be
    late for, so counting it here would turn every refused message wake into a
    lost cron cycle and bury the ones that are.
    """
    write_log(tmp_path, "alexandria-engineer", "2026-10-25T03-29-04-905Z",
              "message", refused("You've hit your weekly limit"), exit_code=1,
              turns=1)
    write_log(tmp_path, "alexandria-engineer", "2026-10-25T02-20-32-011Z",
              "hook", completed(), exit_code=0, turns=25, pr="x/pull/500")
    result = cf.judge(cf.read_runs(tmp_path), "2026-10-25", now=NOW)
    assert result["findings"] == []


# --- the surface a caller sees ------------------------------------------

def test_the_exit_code_is_the_gate(tmp_path):
    write_log(tmp_path, "alexandria-engineer", "2026-10-25T11-06-03-756Z", "cron",
              refused("You've hit your weekly limit · resets 11pm (UTC)"),
              exit_code=1, turns=1)
    assert cf.main(["--day", "2026-10-25", "--root", str(tmp_path)]) == 1
    assert cf.main(["--day", "2026-10-24", "--root", str(tmp_path)]) == 0


def test_a_sandbox_without_the_record_says_so_and_does_not_fail(tmp_path, capsys):
    assert cf.main(["--root", str(tmp_path / "absent")]) == 0
    assert "observation skipped" in capsys.readouterr().out


def test_the_json_surface_carries_the_same_verdict(tmp_path, capsys):
    write_log(tmp_path, "alexandria-engineer", "2026-10-25T11-06-03-756Z", "cron",
              refused("You've hit your weekly limit · resets 11pm (UTC)"),
              exit_code=1, turns=1)
    cf.main(["--day", "2026-10-25", "--root", str(tmp_path), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["day"] == "2026-10-25"
    assert payload["findings"][0]["why"] == "weekly-limit"


def test_nothing_from_a_log_body_reaches_the_output(tmp_path, capsys):
    """The whitelist is the point: a log carries a prompt, and prompts carry anything.

    The header names the environment variables a run was handed and the body
    carries whatever its tools printed. Neither is secret on this host today,
    and a reader that never echoes a line is what keeps that true tomorrow.
    """
    path = write_log(tmp_path, "alexandria-engineer", "2026-10-25T11-06-03-756Z",
                     "cron", refused("You've hit your weekly limit"),
                     exit_code=1, turns=1)
    path.write_text(path.read_text() + "\nsk-ant-oat01-NOT-A-REAL-TOKEN\n")
    cf.main(["--day", "2026-10-25", "--root", str(tmp_path)])
    out = capsys.readouterr().out
    assert "NOT-A-REAL-TOKEN" not in out
    assert "env passed" not in out
    assert "GH_TOKEN" not in out


def test_the_rendering_names_every_state_a_reader_will_meet(tmp_path, capsys):
    write_log(tmp_path, "alexandria-engineer", "2026-10-24T23-06-00-000Z", "cron",
              completed(), exit_code=0, turns=20, pr="x/pull/1")
    write_log(tmp_path, "alexandria-engineer", "2026-10-25T11-06-03-756Z", "cron",
              refused("You've hit your weekly limit"), exit_code=1, turns=1)
    write_log(tmp_path, "exo-centralizer", "2026-10-25T23-00-00-000Z", "cron",
              completed(), exit_code=0, turns=30, pr="x/pull/465")
    write_log(tmp_path, "ursa-engineer", "2026-10-25T23-27-00-000Z", "cron",
              trailer=False)
    cf.main(["--day", "2026-10-25", "--root", str(tmp_path)])
    out = capsys.readouterr().out
    assert "LOST" in out and "shipped" in out
    assert "unseen" in out and "running" in out
    assert "1 cycle(s) lost" in out


def test_an_empty_record_reads_as_empty_rather_than_as_green(tmp_path, capsys):
    (tmp_path / "alexandria-engineer").mkdir()
    cf.main(["--day", "2026-10-25", "--root", str(tmp_path)])
    assert "no cron slot fired" in capsys.readouterr().out
