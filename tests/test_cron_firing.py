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
import os
import sys
import time
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


# --- the three limits are three things -----------------------------------

#: The monthly sentence exactly as the host's archive carries it, 257 times
#: across 2026-11-03 to 2026-11-08. Copied rather than paraphrased, because
#: the defect it pins lives in its closing clause.
MONTHLY_SPEND = (
    "You've hit your org's monthly spend limit · ask your admin to raise it "
    "at claude.ai/admin-settings/usage · your weekly limit resets "
    "Nov 8, 11pm (UTC)")


@pytest.mark.parametrize("sentence,expected", [
    ("You've hit your weekly limit · resets 11pm (UTC)", "weekly-limit"),
    ("You've hit your 5-hour limit · resets 4am", "session-limit"),
    ("Your session limit was reached", "session-limit"),
    ("Overloaded", "unclassified-429"),
    (MONTHLY_SPEND, "monthly-spend"),
])
def test_the_refusal_sentence_is_the_only_discriminator(sentence, expected):
    assert cf.classify_refusal(sentence, 429) == expected


def test_the_monthly_cap_is_not_the_weekly_pool_though_it_names_it():
    """The sentence that refused the portfolio for six days names two limits.

    `monthly-spend` has to be tested before `weekly-limit`, because the
    monthly sentence closes by announcing when the weekly limit resets, and a
    substring test for `weekly` matches that clause. Every one of the 257
    refusals from 2026-11-03 to 2026-11-08 was filed as the weekly pool
    running out.

    The two have different remedies and that is why the misfiling cost
    something. A weekly pool is rationed by moving slots and lowering burn. A
    monthly spend cap is raised by the owner in the org's admin settings, and
    no amount of rescheduling touches it.
    """
    assert cf.classify_refusal(MONTHLY_SPEND, 429) == "monthly-spend"
    assert "weekly" in MONTHLY_SPEND.lower(), (
        "if the provider drops the weekly clause this test stops pinning "
        "anything, and the ordering above would no longer be load-bearing")


def test_the_monthly_sentence_survives_a_round_trip_through_a_log(tmp_path):
    """The classifier and the reader agree, and the sentence itself is kept.

    `refusal_text` exists because a weekly refusal announces its own reset
    instant, which is the only authoritative statement of where the provider
    cycle's boundary falls. `tools/provider_cycle.py` reads it rather than
    assuming the Sunday rule.
    """
    write_log(tmp_path, "alexandria-engineer", "2026-11-04T11-06-25-000Z",
              "cron", refused(MONTHLY_SPEND), exit_code=1, turns=1)
    run, = cf.read_runs(tmp_path)
    assert run["refusal"] == "monthly-spend"
    assert run["refusal_text"] == MONTHLY_SPEND


def test_a_run_that_was_not_refused_keeps_no_refusal_text(tmp_path):
    write_log(tmp_path, "alexandria-engineer", "2026-11-04T11-06-25-000Z",
              "cron", completed(), exit_code=0, pr="x/pull/1", turns=9)
    run, = cf.read_runs(tmp_path)
    assert run["refusal"] is None
    assert run["refusal_text"] is None


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


def test_a_log_outside_the_window_is_skipped_on_its_name(tmp_path):
    """The archive only grows, so the reader may not open all of it every day.

    1,714 logs and 9.8 MB after five weeks on this host. Reading the lot to
    answer about one day took 2.6 seconds; reading the window takes 0.22.
    """
    write_log(tmp_path, "alexandria-engineer", "2026-01-01T11-06-00-000Z",
              "cron", completed(), exit_code=0, turns=4, pr="x/pull/1")
    write_log(tmp_path, "alexandria-engineer", "2026-10-25T11-06-00-000Z",
              "cron", completed(), exit_code=0, turns=4, pr="x/pull/2")
    window = cf.days_back("2026-10-25", 14)
    assert len(cf.read_runs(tmp_path)) == 2
    assert [r["day"] for r in cf.read_runs(tmp_path, days=window)] == ["2026-10-25"]


def test_the_window_covers_the_day_asked_about_and_the_days_before_it():
    window = cf.days_back("2026-10-25", 2)
    assert window == {"2026-10-25", "2026-10-24", "2026-10-23"}


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
    cf.main(["--day", "2026-10-25", "--root", str(tmp_path),
             "--now", "2026-10-25T23:30:00Z"])
    out = capsys.readouterr().out
    assert "LOST" in out and "shipped" in out
    assert "unseen" in out and "running" in out
    assert "1 cycle(s) lost" in out


def test_the_clock_is_pinnable_because_one_verdict_depends_on_it(tmp_path, capsys):
    """This test is here because its neighbour above went red on its own.

    The `in-flight` verdict is the run's age, so a test that writes a fixed
    timestamp and reads it against the wall clock asserts something that stops
    being true ninety minutes later. The version of the test above was written
    at 2026-10-26T00:50Z with `23-27-00` in it and no `--now`, it passed, and it
    was red by 00:57Z. Nothing was wrong with the reader. The fixture had aged.
    """
    write_log(tmp_path, "ursa-engineer", "2026-10-25T23-27-00-000Z", "cron",
              trailer=False)
    cf.main(["--day", "2026-10-25", "--root", str(tmp_path),
             "--now", "2026-10-25T23:30:00Z"])
    assert "running" in capsys.readouterr().out

    cf.main(["--day", "2026-10-25", "--root", str(tmp_path),
             "--now", "2026-10-26T06:00:00Z"])
    assert "no-trailer" in capsys.readouterr().out


def test_an_unreadable_now_leaves_the_wall_clock_standing(tmp_path, capsys):
    write_log(tmp_path, "alexandria-engineer", "2026-10-25T11-06-03-756Z", "cron",
              refused("You've hit your weekly limit"), exit_code=1, turns=1)
    assert cf.main(["--day", "2026-10-25", "--root", str(tmp_path),
                    "--now", "half past four"]) == 1
    captured = capsys.readouterr()
    assert "weekly-limit" in captured.out
    assert "not an ISO stamp" in captured.err


def test_an_empty_record_reads_as_empty_rather_than_as_green(tmp_path, capsys):
    (tmp_path / "alexandria-engineer").mkdir()
    cf.main(["--day", "2026-10-25", "--root", str(tmp_path)])
    assert "no cron slot fired" in capsys.readouterr().out


# --- `pr=-` is two different facts, and reading it as one lost a cycle's work ---
#
# The run that produced these tests is the one they describe. This seat's
# message run of 2026-10-26 opened its draft pull request at turn 3, built the
# day's work on it, and was refused at turn 89 by the provider's session limit.
# The host's trailer for it is `# exit=1 pr=- session=5a660600 turns=89`,
# because the pull request url is scraped from a final answer the run never got
# to give. The first version of the reader called that a lost cycle.

def cut_off(sentence="You've hit your session limit · resets 4am (UTC)"):
    """The real shape of a run stopped mid-work, at turn 89 rather than turn 1."""
    return {"type": "result", "is_error": True, "num_turns": 89,
            "api_error_status": 429, "result": sentence,
            "terminal_reason": "api_error", "duration_ms": 1729034}


def pr_entry(number, branch, created):
    return {"number": number, "url": f"https://github.com/o/r/pull/{number}",
            "headRefName": branch, "createdAt": created}


def test_a_clean_exit_with_no_pull_request_really_did_ship_nothing(tmp_path):
    path = write_log(tmp_path, "alexandria-engineer",
                     "2026-10-25T11-06-03-756Z", "cron",
                     completed(), exit_code=0, turns=25)
    assert cf.pr_absence_is_evidence(cf.parse_run(path)) is True


def test_a_refused_run_cannot_prove_it_shipped_nothing(tmp_path):
    path = write_log(tmp_path, "alexandria-engineer",
                     "2026-10-26T00-31-38-049Z", "message",
                     cut_off(), exit_code=1, turns=89)
    assert cf.pr_absence_is_evidence(cf.parse_run(path)) is False


def test_a_run_with_no_trailer_at_all_cannot_prove_it_either(tmp_path):
    path = write_log(tmp_path, "alexandria-engineer",
                     "2026-10-26T00-31-38-049Z", "cron", trailer=False)
    assert cf.pr_absence_is_evidence(cf.parse_run(path)) is False


def test_a_trailer_that_names_a_pull_request_needs_no_judgement(tmp_path):
    path = write_log(tmp_path, "alexandria-engineer",
                     "2026-10-25T11-06-03-756Z", "cron",
                     completed(), exit_code=0, turns=25, pr="x/pull/9")
    assert cf.pr_absence_is_evidence(cf.parse_run(path)) is True


def test_the_pull_request_list_settles_a_cut_off_slot(tmp_path):
    write_log(tmp_path, "alexandria-engineer", "2026-10-26T00-31-38-049Z",
              "cron", cut_off(), exit_code=1, turns=89)
    runs = cf.read_runs(tmp_path)
    index = [pr_entry(530, "alexandria-engineer/2026-10-26-message",
                      "2026-10-26T00:33:05Z")]
    result = cf.judge(runs, "2026-10-26", pr_index=index,
                      now=datetime(2026, 10, 26, 6, tzinfo=UTC))
    assert result["lost"] == []
    finding = result["cut"][0]
    assert finding["why"] == "session-limit"
    assert finding["pr"] == "https://github.com/o/r/pull/530"
    assert finding["pr_source"] == "pull request list"
    assert finding["turns"] == 89


def test_a_cut_off_cycle_is_not_counted_as_lost_and_is_still_reported(tmp_path, capsys):
    write_log(tmp_path, "alexandria-engineer", "2026-10-26T00-31-38-049Z",
              "cron", cut_off(), exit_code=1, turns=89)
    index = tmp_path / "prs.json"
    index.write_text(json.dumps([
        pr_entry(530, "alexandria-engineer/2026-10-26-message",
                 "2026-10-26T00:33:05Z")]))
    code = cf.main(["--day", "2026-10-26", "--root", str(tmp_path),
                    "--prs", str(index), "--now", "2026-10-26T06:00:00Z"])
    out = capsys.readouterr().out
    assert code == 0
    assert "cut      alexandria-engineer 00:31Z session-limit at turn 89" in out
    assert "cut off after shipping" in out
    assert "LOST" not in out


def test_without_the_list_the_doubt_is_stated_rather_than_resolved(tmp_path, capsys):
    write_log(tmp_path, "alexandria-engineer", "2026-10-26T00-31-38-049Z",
              "cron", cut_off(), exit_code=1, turns=89)
    code = cf.main(["--day", "2026-10-26", "--root", str(tmp_path),
                    "--now", "2026-10-26T06:00:00Z"])
    out = capsys.readouterr().out
    assert code == 1, "an unsettled cycle is not silently green"
    assert "LOST?" in out
    assert "is not evidence" in out
    assert "--prs to settle it" in out


def test_a_silent_run_stays_silent_even_with_the_list(tmp_path, capsys):
    """The state the ship-first rule exists to prevent must not be explained away.

    A run that exited 0 and shipped nothing is `silent`, and a pull request
    another run of the same seat opened in the same window must not be lent to
    it. Only a run that was stopped gets resolved.
    """
    write_log(tmp_path, "alexandria-engineer", "2026-10-26T00-31-38-049Z",
              "cron", completed(), exit_code=0, turns=25)
    index = tmp_path / "prs.json"
    index.write_text(json.dumps([
        pr_entry(530, "alexandria-engineer/2026-10-26-message",
                 "2026-10-26T00:33:05Z")]))
    code = cf.main(["--day", "2026-10-26", "--root", str(tmp_path),
                    "--prs", str(index), "--now", "2026-10-26T06:00:00Z"])
    out = capsys.readouterr().out
    assert code == 1
    assert "LOST     alexandria-engineer 00:31Z silent" in out
    assert "no pull request" in out


def test_another_seats_pull_request_is_never_borrowed(tmp_path):
    write_log(tmp_path, "alexandria-engineer", "2026-10-26T00-31-38-049Z",
              "cron", cut_off(), exit_code=1, turns=89)
    runs = cf.read_runs(tmp_path)
    index = [pr_entry(531, "alexandria-pm/2026-10-26-message",
                      "2026-10-26T00:34:34Z")]
    result = cf.judge(runs, "2026-10-26", pr_index=index,
                      now=datetime(2026, 10, 26, 6, tzinfo=UTC))
    assert result["cut"] == []
    assert result["lost"][0]["pr_unknown"] is True


def test_the_bare_role_branch_prefix_still_matches(tmp_path):
    """`engineer/2026-10-18-slug` is the older convention and it is still live."""
    write_log(tmp_path, "alexandria-engineer", "2026-10-26T00-31-38-049Z",
              "cron", cut_off(), exit_code=1, turns=89)
    runs = cf.read_runs(tmp_path)
    index = [pr_entry(481, "engineer/2026-10-26-slug", "2026-10-26T00:40:00Z")]
    result = cf.judge(runs, "2026-10-26", pr_index=index,
                      now=datetime(2026, 10, 26, 6, tzinfo=UTC))
    assert result["cut"][0]["pr"].endswith("/481")


def test_a_pull_request_opened_before_the_run_started_is_not_its_own(tmp_path):
    write_log(tmp_path, "alexandria-engineer", "2026-10-26T00-31-38-049Z",
              "cron", cut_off(), exit_code=1, turns=89)
    runs = cf.read_runs(tmp_path)
    index = [pr_entry(526, "alexandria-engineer/2026-10-25-cron",
                      "2026-10-25T23:58:00Z")]
    result = cf.judge(runs, "2026-10-26", pr_index=index,
                      now=datetime(2026, 10, 26, 6, tzinfo=UTC))
    assert result["cut"] == []


def test_the_next_run_of_the_seat_closes_the_window(tmp_path):
    """Two runs an hour apart must not both claim the later one's pull request."""
    write_log(tmp_path, "alexandria-engineer", "2026-10-26T00-31-38-049Z",
              "cron", cut_off(), exit_code=1, turns=89)
    write_log(tmp_path, "alexandria-engineer", "2026-10-26T04-02-26-533Z",
              "cron", cut_off(), exit_code=1, turns=40)
    runs = cf.read_runs(tmp_path)
    index = [pr_entry(536, "alexandria-engineer/2026-10-26-hook",
                      "2026-10-26T04:10:00Z")]
    result = cf.judge(runs, "2026-10-26", pr_index=index,
                      now=datetime(2026, 10, 26, 8, tzinfo=UTC))
    claimed = {f["slot"]: f["pr"] for f in result["findings"]}
    assert claimed["00:31Z"] is None
    assert claimed["04:02Z"].endswith("/536")


def test_a_pull_request_past_the_longest_plausible_run_is_not_claimed(tmp_path):
    """With no later run to bound it, the session window does the bounding."""
    write_log(tmp_path, "alexandria-engineer", "2026-10-26T00-31-38-049Z",
              "cron", cut_off(), exit_code=1, turns=89)
    runs = cf.read_runs(tmp_path)
    index = [pr_entry(540, "alexandria-engineer/2026-10-26-later",
                      "2026-10-26T09:00:00Z")]
    result = cf.judge(runs, "2026-10-26", pr_index=index,
                      now=datetime(2026, 10, 26, 12, tzinfo=UTC))
    assert result["cut"] == []


def test_an_unreadable_pull_request_file_is_a_note_and_not_a_traceback(tmp_path, capsys):
    write_log(tmp_path, "alexandria-engineer", "2026-10-26T00-31-38-049Z",
              "cron", cut_off(), exit_code=1, turns=89)
    code = cf.main(["--day", "2026-10-26", "--root", str(tmp_path),
                    "--prs", str(tmp_path / "nope.json"),
                    "--now", "2026-10-26T06:00:00Z"])
    captured = capsys.readouterr()
    assert code == 1
    assert "LOST?" in captured.out
    assert "could not be read" in captured.err


def test_the_json_surface_carries_the_cut_state_too(tmp_path, capsys):
    write_log(tmp_path, "alexandria-engineer", "2026-10-26T00-31-38-049Z",
              "cron", cut_off(), exit_code=1, turns=89)
    index = tmp_path / "prs.json"
    index.write_text(json.dumps([
        pr_entry(530, "alexandria-engineer/2026-10-26-message",
                 "2026-10-26T00:33:05Z")]))
    cf.main(["--day", "2026-10-26", "--root", str(tmp_path), "--json",
             "--prs", str(index), "--now", "2026-10-26T06:00:00Z"])
    payload = json.loads(capsys.readouterr().out)
    assert [f["state"] for f in payload["findings"]] == ["cut"]
    assert payload["cut"][0]["why"] == "session-limit"


# --- the retry's claim file, and the slot it rescues -----------------------
#
# Added 2026-10-27, after research's 2026-10-26T16:30Z slot — the first
# class-A slot in `docs/agents/unowned-duties.md` ever to come due — was
# reported as a lost cycle by this file's own tool. It fired on time, the
# provider refused it, HQ's retry re-fired it and the re-fire shipped PR #589,
# merged. The window in `resolve_shipped` closes at the seat's next run, which
# for a refused slot is the retry itself, so the one run whose work belongs to
# the slot was the one run the window could never contain.


@pytest.fixture(autouse=True)
def _no_host_claim_file(tmp_path_factory, monkeypatch):
    """Keep this file's promise that no test reads `/srv/asc/state`.

    `main` defaults `--claims` to the host's claim file, which exists on the
    host and does not exist on a pull request checkout. A test that happened to
    pass because no claim matched would still be reading the host's disk, so
    the default is pointed at an absent path for every test here and the tests
    that care about claims pass their own.
    """
    absent = tmp_path_factory.mktemp("no-claims") / "capacity-retry.json"
    monkeypatch.setattr(cf, "CLAIM_FILE", absent)


def claim_file(tmp_path, **seats):
    path = tmp_path / "capacity-retry.json"
    path.write_text(json.dumps(seats))
    return path


def test_a_missing_claim_file_is_the_ordinary_case_and_not_an_error():
    assert cf.read_retry_claims("/nowhere/capacity-retry.json") == {}


def test_a_claim_file_that_is_not_a_mapping_is_ignored(tmp_path):
    path = tmp_path / "capacity-retry.json"
    path.write_text(json.dumps(["a-log.log"]))
    assert cf.read_retry_claims(path) == {}


def test_a_refused_slot_the_retry_rescued_is_retried_and_not_lost(tmp_path):
    """Research's real 2026-10-26 slot, in the shape the host wrote it."""
    write_log(tmp_path, "alexandria-research", "2026-10-26T16-30-23-798Z",
              "cron", refused("You've hit your session limit · resets 7pm (UTC)"),
              exit_code=1, turns=1)
    write_log(tmp_path, "alexandria-research", "2026-10-26T19-03-27-547Z",
              "hook", completed(), exit_code=0, turns=94,
              pr="https://github.com/alexandrapaiz/alexandria/pull/589")
    claims = cf.read_retry_claims(claim_file(
        tmp_path,
        **{"alexandria-research": ["2026-10-26T16-30-23-798Z-cron.log"]}))
    result = cf.judge(cf.read_runs(tmp_path), "2026-10-26", claims=claims,
                      now=datetime(2026, 10, 26, 23, 59, tzinfo=UTC))
    assert result["lost"] == []
    finding, = result["retried"]
    assert finding["seat"] == "alexandria-research"
    assert finding["slot"] == "16:30Z"
    assert finding["why"] == "session-limit"
    assert finding["retried_by"] == "2026-10-26T19-03-27-547Z-hook"
    assert finding["retry_pr"].endswith("/pull/589")
    assert finding["late_minutes"] == 153


def test_the_rescued_slot_does_not_set_the_exit_code(tmp_path, capsys):
    write_log(tmp_path, "alexandria-research", "2026-10-26T16-30-23-798Z",
              "cron", refused("You've hit your session limit · resets 7pm (UTC)"),
              exit_code=1, turns=1)
    write_log(tmp_path, "alexandria-research", "2026-10-26T19-03-27-547Z",
              "hook", completed(), exit_code=0, turns=94,
              pr="https://github.com/alexandrapaiz/alexandria/pull/589")
    path = claim_file(tmp_path,
                      **{"alexandria-research": ["2026-10-26T16-30-23-798Z-cron.log"]})
    code = cf.main(["--day", "2026-10-26", "--root", str(tmp_path),
                    "--claims", str(path), "--now", "2026-10-26T23:59:00Z"])
    out = capsys.readouterr().out
    assert code == 0, "a cycle that arrived late did not go missing"
    assert "retried  alexandria-research 16:30Z session-limit" in out
    assert "2h33m late" in out
    assert "LOST" not in out


def test_without_the_claim_file_the_same_slot_reads_as_lost(tmp_path, capsys):
    """The defect this section was written for, kept as a test.

    This is not a wish for the old behaviour. It pins the fact that the claim
    file is the only thing joining the two rows, so a reading taken without it
    on a host that has one is wrong rather than merely less decided.
    """
    write_log(tmp_path, "alexandria-research", "2026-10-26T16-30-23-798Z",
              "cron", refused("You've hit your session limit · resets 7pm (UTC)"),
              exit_code=1, turns=1)
    write_log(tmp_path, "alexandria-research", "2026-10-26T19-03-27-547Z",
              "hook", completed(), exit_code=0, turns=94,
              pr="https://github.com/alexandrapaiz/alexandria/pull/589")
    code = cf.main(["--day", "2026-10-26", "--root", str(tmp_path),
                    "--now", "2026-10-26T23:59:00Z"])
    out = capsys.readouterr().out
    assert code == 1
    assert "LOST?" in out


def test_a_claimed_slot_with_no_hook_after_it_says_the_re_fire_is_owed(tmp_path, capsys):
    write_log(tmp_path, "ursa-engineer", "2026-10-26T23-26-03-533Z", "cron",
              refused("You've hit your session limit · resets 7pm (UTC)"),
              exit_code=1, turns=1)
    path = claim_file(tmp_path,
                      **{"ursa-engineer": ["2026-10-26T23-26-03-533Z-cron.log"]})
    code = cf.main(["--day", "2026-10-26", "--root", str(tmp_path),
                    "--claims", str(path), "--now", "2026-10-27T06:00:00Z"])
    out = capsys.readouterr().out
    assert code == 1, "an owed re-fire is still an owed cycle"
    assert "the re-fire is owed and has not happened" in out
    assert "--prs to settle it" not in out


def test_a_re_fire_that_shipped_nothing_leaves_the_cycle_lost(tmp_path, capsys):
    write_log(tmp_path, "epitome-pm", "2026-10-26T12-00-08-284Z", "cron",
              refused("You've hit your session limit · resets 7pm (UTC)"),
              exit_code=1, turns=1)
    write_log(tmp_path, "epitome-pm", "2026-10-26T14-03-06-824Z", "hook",
              completed(), exit_code=0, turns=40)
    path = claim_file(tmp_path,
                      **{"epitome-pm": ["2026-10-26T12-00-08-284Z-cron.log"]})
    code = cf.main(["--day", "2026-10-26", "--root", str(tmp_path),
                    "--claims", str(path), "--now", "2026-10-26T23:59:00Z"])
    out = capsys.readouterr().out
    assert code == 1
    assert "lost after a recovery attempt" in out


def test_a_message_wake_between_the_two_is_never_mistaken_for_the_retry(tmp_path):
    """The retry arrives as a hook, and these seats take message wakes all day.

    Crediting a slot with whatever ran next would attribute an unrelated wake's
    pull request to the cycle, which is the same error in the generous
    direction.
    """
    write_log(tmp_path, "alexandria-exo", "2026-10-25T14-00-04-675Z", "cron",
              refused("You've hit your weekly limit · resets 11pm (UTC)"),
              exit_code=1, turns=1)
    write_log(tmp_path, "alexandria-exo", "2026-10-25T18-00-00-000Z",
              "message", completed(), exit_code=0, turns=60,
              pr="https://github.com/alexandrapaiz/alexandria/pull/999")
    write_log(tmp_path, "alexandria-exo", "2026-10-25T23-02-09-170Z", "hook",
              completed(), exit_code=0, turns=66,
              pr="https://github.com/alexandrapaiz/alexandria/pull/518")
    claims = cf.read_retry_claims(claim_file(
        tmp_path,
        **{"alexandria-exo": ["2026-10-25T14-00-04-675Z-cron.log"]}))
    result = cf.judge(cf.read_runs(tmp_path), "2026-10-25", claims=claims,
                      now=datetime(2026, 10, 25, 23, 59, tzinfo=UTC))
    finding, = result["retried"]
    assert finding["retried_by"] == "2026-10-25T23-02-09-170Z-hook"
    assert finding["retry_pr"].endswith("/pull/518")


def test_a_re_fire_that_shipped_without_saying_so_is_still_credited(tmp_path):
    """`alexandria-writer`'s real 2026-10-26 16:00Z slot.

    Its re-fire exited 0 after 124 turns with `pr=-`, and it had opened #591 on
    a branch named `2026-10-26-hook-refired-slot`. `pr_absence_is_evidence`
    called that `silent`, on the reasoning that a run exiting 0 would have
    named its pull request. A run known to be re-firing a refused slot is the
    exception: the host scrapes the url out of the final answer and a long run
    can simply not be scraped.
    """
    write_log(tmp_path, "alexandria-writer", "2026-10-26T16-00-23-647Z",
              "cron", refused("You've hit your session limit · resets 7pm (UTC)"),
              exit_code=1, turns=1)
    write_log(tmp_path, "alexandria-writer", "2026-10-26T19-03-27-600Z",
              "hook", completed(), exit_code=0, turns=124)
    write_log(tmp_path, "alexandria-writer", "2026-10-26T19-54-45-367Z",
              "message", completed(), exit_code=0, turns=30)
    claims = cf.read_retry_claims(claim_file(
        tmp_path,
        **{"alexandria-writer": ["2026-10-26T16-00-23-647Z-cron.log"]}))
    index = [pr_entry(591, "alexandria-writer/2026-10-26-hook-refired-slot",
                      "2026-10-26T19:06:00Z")]
    result = cf.judge(cf.read_runs(tmp_path), "2026-10-26", claims=claims,
                      pr_index=index,
                      now=datetime(2026, 10, 26, 23, 59, tzinfo=UTC))
    assert result["lost"] == []
    finding, = result["retried"]
    assert finding["retry_pr"] == "https://github.com/o/r/pull/591"


def test_an_ordinary_silent_run_is_still_silent_after_the_retry_change(tmp_path, capsys):
    """The narrowness of the exception above, asserted rather than asserted of.

    A run nothing claimed keeps the old reading, so `silent` survives as the
    state incident 3 exists to keep visible.
    """
    write_log(tmp_path, "alexandria-engineer", "2026-10-26T11-15-37-106Z",
              "cron", completed(), exit_code=0, turns=98)
    index = tmp_path / "prs.json"
    index.write_text(json.dumps([
        pr_entry(600, "alexandria-engineer/2026-10-26-cron",
                 "2026-10-26T11:20:00Z")]))
    code = cf.main(["--day", "2026-10-26", "--root", str(tmp_path),
                    "--prs", str(index), "--now", "2026-10-26T23:59:00Z"])
    out = capsys.readouterr().out
    assert code == 1
    assert "LOST     alexandria-engineer 11:15Z silent" in out


def test_the_prs_hint_stops_telling_a_reader_to_do_what_they_did(tmp_path, capsys):
    write_log(tmp_path, "alexandria-engineer", "2026-10-26T00-31-38-049Z",
              "cron", cut_off(), exit_code=1, turns=89)
    index = tmp_path / "prs.json"
    index.write_text(json.dumps([]))
    code = cf.main(["--day", "2026-10-26", "--root", str(tmp_path),
                    "--prs", str(index), "--now", "2026-10-26T06:00:00Z"])
    out = capsys.readouterr().out
    assert code == 1
    assert "--prs to settle it" not in out
    assert "`pr=-` stands" in out


def test_the_json_surface_carries_the_retried_state(tmp_path, capsys):
    write_log(tmp_path, "alexandria-research", "2026-10-26T16-30-23-798Z",
              "cron", refused("You've hit your session limit · resets 7pm (UTC)"),
              exit_code=1, turns=1)
    write_log(tmp_path, "alexandria-research", "2026-10-26T19-03-27-547Z",
              "hook", completed(), exit_code=0, turns=94,
              pr="https://github.com/alexandrapaiz/alexandria/pull/589")
    path = claim_file(tmp_path,
                      **{"alexandria-research": ["2026-10-26T16-30-23-798Z-cron.log"]})
    cf.main(["--day", "2026-10-26", "--root", str(tmp_path), "--json",
             "--claims", str(path), "--now", "2026-10-26T23:59:00Z"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["lost"] == []
    assert payload["retried"][0]["retry_pr"].endswith("/pull/589")
    assert payload["findings"][0]["state"] == "retried"


# --- the claim names the window's last refused log, not the costly one -----
#
# ursa-pm's real 2026-10-26, which is where this was found: the 11:05Z cron was
# refused 55 turns in, the same window refused the seat five more times, the
# claim file named the last of those (a turn-1 message log) and one hook at
# 14:03Z brought the seat back. The seat recovered. The cycle did not, because
# the re-fire was dispatched for the turn-1 log and its wake text named that.

def _orphaning_window(root):
    """A seat cut mid-cycle, refused again at turn 1, then re-fired once."""
    write_log(root, "ursa-pm", "2026-10-26T11-05-07-892Z", "cron",
              cut_off("You've hit your session limit · resets 2pm (UTC)"),
              exit_code=1, turns=55)
    write_log(root, "ursa-pm", "2026-10-26T12-20-01-389Z", "message",
              refused("You've hit your session limit · resets 2pm (UTC)"),
              exit_code=1, turns=1)
    write_log(root, "ursa-pm", "2026-10-26T14-03-07-542Z", "hook",
              completed(), exit_code=0, turns=37,
              pr="https://github.com/alexandrapaiz/Ursa/pull/700")
    return claim_file(root,
                      **{"ursa-pm": ["2026-10-26T12-20-01-389Z-message.log"]})


def test_a_cycle_refused_before_the_claimed_log_is_orphaned_not_rescued(tmp_path):
    claims = cf.read_retry_claims(_orphaning_window(tmp_path))
    result = cf.judge(cf.read_runs(tmp_path), "2026-10-26", claims=claims,
                      now=datetime(2026, 10, 26, 23, 59, tzinfo=UTC))
    assert result["retried"] == [], "the claim did not name this slot's log"
    finding, = result["orphaned"]
    assert finding["seat"] == "ursa-pm"
    assert finding["slot"] == "11:05Z"
    assert finding["turns"] == 55
    assert finding["orphaned_behind"] == "2026-10-26T12-20-01-389Z-message"
    assert finding["retry_claimed"] is False


def test_an_orphaned_cycle_still_sets_the_exit_code(tmp_path, capsys):
    """Naming these rows changes the sentence and not the contract.

    Before `orphaned` existed they read as `lost` and set the exit code, so a
    gate that ran on the old behaviour must not go quiet on the new one.
    """
    path = _orphaning_window(tmp_path)
    code = cf.main(["--day", "2026-10-26", "--root", str(tmp_path),
                    "--claims", str(path), "--now", "2026-10-26T23:59:00Z"])
    out = capsys.readouterr().out
    assert code == 1
    assert "orphaned ursa-pm 11:05Z session-limit, 55 turns" in out
    assert "2026-10-26T12-20-01-389Z-message" in out, \
        "the reader needs the log the claim did name"
    assert "1 cycle(s) orphaned" in out
    assert "the remedy is the claim's key" in out


def test_the_orphaned_row_is_not_double_counted_as_lost(tmp_path):
    claims = cf.read_retry_claims(_orphaning_window(tmp_path))
    result = cf.judge(cf.read_runs(tmp_path), "2026-10-26", claims=claims,
                      now=datetime(2026, 10, 26, 23, 59, tzinfo=UTC))
    assert result["lost"] == []
    assert len(result["orphaned"]) == 1


def test_a_run_the_seat_survived_breaks_the_cascade(tmp_path):
    """The bound on the walk back, and the reason it is not a time window.

    A claim says the seat was refused and re-fired. It says nothing about a
    refusal from an earlier window that the seat already recovered from on its
    own, and crediting that one to this claim would be the same error in the
    generous direction. One completed run in between is the whole proof.
    """
    write_log(tmp_path, "ursa-pm", "2026-10-26T06-05-00-000Z", "cron",
              cut_off("You've hit your session limit · resets 9am (UTC)"),
              exit_code=1, turns=55)
    write_log(tmp_path, "ursa-pm", "2026-10-26T09-13-02-944Z", "message",
              completed(), exit_code=0, turns=39,
              pr="https://github.com/alexandrapaiz/Ursa/pull/690")
    write_log(tmp_path, "ursa-pm", "2026-10-26T12-20-01-389Z", "message",
              refused("You've hit your session limit · resets 2pm (UTC)"),
              exit_code=1, turns=1)
    write_log(tmp_path, "ursa-pm", "2026-10-26T14-03-07-542Z", "hook",
              completed(), exit_code=0, turns=37,
              pr="https://github.com/alexandrapaiz/Ursa/pull/700")
    claims = cf.read_retry_claims(claim_file(
        tmp_path, **{"ursa-pm": ["2026-10-26T12-20-01-389Z-message.log"]}))
    result = cf.judge(cf.read_runs(tmp_path), "2026-10-26", claims=claims,
                      now=datetime(2026, 10, 26, 23, 59, tzinfo=UTC))
    assert result["orphaned"] == []
    finding, = result["lost"]
    assert finding["slot"] == "06:05Z"
    assert finding["orphaned_behind"] is None


def test_an_exactly_claimed_slot_is_still_retried_when_one_follows_it(tmp_path):
    """The regression guard on the state this cascade sits beside.

    The 2026-10-26 research slot was claimed by its own log filename, and the
    cascade must not steal it: a claimed log is `retried`, and only the
    unclaimed refusals behind it are `orphaned`.
    """
    write_log(tmp_path, "alexandria-research", "2026-10-26T15-26-00-000Z",
              "message", refused("You've hit your session limit · resets 7pm (UTC)"),
              exit_code=1, turns=6)
    write_log(tmp_path, "alexandria-research", "2026-10-26T16-30-23-798Z",
              "cron", refused("You've hit your session limit · resets 7pm (UTC)"),
              exit_code=1, turns=1)
    write_log(tmp_path, "alexandria-research", "2026-10-26T19-03-27-547Z",
              "hook", completed(), exit_code=0, turns=94,
              pr="https://github.com/alexandrapaiz/alexandria/pull/589")
    claims = cf.read_retry_claims(claim_file(
        tmp_path,
        **{"alexandria-research": ["2026-10-26T16-30-23-798Z-cron.log"]}))
    result = cf.judge(cf.read_runs(tmp_path), "2026-10-26", claims=claims,
                      now=datetime(2026, 10, 26, 23, 59, tzinfo=UTC))
    assert result["orphaned"] == []
    assert result["lost"] == []
    finding, = result["retried"]
    assert finding["slot"] == "16:30Z"
    assert finding["late_minutes"] == 153


def test_the_json_surface_carries_the_orphaned_state(tmp_path, capsys):
    path = _orphaning_window(tmp_path)
    cf.main(["--day", "2026-10-26", "--root", str(tmp_path), "--json",
             "--claims", str(path), "--now", "2026-10-26T23:59:00Z"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["lost"] == []
    assert payload["orphaned"][0]["slot"] == "11:05Z"
    assert payload["findings"][0]["state"] == "orphaned"
    assert payload["findings"][0]["orphaned_behind"] == \
        "2026-10-26T12-20-01-389Z-message"


def test_a_claim_with_no_hook_after_it_orphans_nothing_silently(tmp_path):
    """No re-fire means no recovery, so the earlier refusal is plainly lost.

    `orphaned` is a claim about a re-fire that happened and went elsewhere.
    Where no hook follows the claim, the seat never came back and the honest
    word is the one the file already had.
    """
    write_log(tmp_path, "ursa-pm", "2026-10-26T11-05-07-892Z", "cron",
              cut_off("You've hit your session limit · resets 2pm (UTC)"),
              exit_code=1, turns=55)
    write_log(tmp_path, "ursa-pm", "2026-10-26T12-20-01-389Z", "message",
              refused("You've hit your session limit · resets 2pm (UTC)"),
              exit_code=1, turns=1)
    claims = cf.read_retry_claims(claim_file(
        tmp_path, **{"ursa-pm": ["2026-10-26T12-20-01-389Z-message.log"]}))
    result = cf.judge(cf.read_runs(tmp_path), "2026-10-26", claims=claims,
                      now=datetime(2026, 10, 26, 23, 59, tzinfo=UTC))
    assert result["orphaned"] == []
    finding, = result["lost"]
    assert finding["slot"] == "11:05Z"
# --- the seat argument, which answered instead of resolving ----------------
#
# `INC-2026-10-27-two-readers-answer-a-wrong-seat-name-with-a-confident-zero`.
# `--seat research` and `--seat totallyfake` printed the same sentence, byte for
# byte: no slot fired, and none in the trailing 14 days. The research slot had
# fired on time the afternoon before. The reason that is urgent is the duty card
# in `docs/agents/unowned-duties.md`, which instructs its next reader to read
# each slot here and never from the absence of a pull request, and which exists
# because an earlier run nearly retired three working seats on a bad absence. On
# the one argument a reader supplies by hand, the remedy reproduced the failure
# it was built to prevent.

def test_the_host_directory_name_resolves_to_itself(tmp_path):
    write_log(tmp_path, "alexandria-research", "2026-10-26T16-30-23-001Z",
              "cron", completed(), exit_code=0, turns=30)
    assert cf.resolve_seat("alexandria-research", tmp_path) == "alexandria-research"


def test_the_bare_seat_name_the_charters_use_resolves_to_the_directory(tmp_path):
    write_log(tmp_path, "alexandria-research", "2026-10-26T16-30-23-001Z",
              "cron", completed(), exit_code=0, turns=30)
    assert cf.resolve_seat("research", tmp_path) == "alexandria-research"


def test_a_seat_name_in_no_directory_is_not_found_rather_than_quiet(tmp_path):
    write_log(tmp_path, "alexandria-research", "2026-10-26T16-30-23-001Z",
              "cron", completed(), exit_code=0, turns=30)
    with pytest.raises(cf.SeatNotFound) as exc:
        cf.resolve_seat("totallyfake", tmp_path)
    # The roster is named, because "not found" without it leaves the reader
    # guessing at the spelling that was wanted.
    assert "alexandria-research" in str(exc.value)


def test_a_bare_name_in_several_companies_is_asked_about_rather_than_picked(tmp_path):
    for seat in ("alexandria-exo", "ursa-exo", "epitome-exo"):
        write_log(tmp_path, seat, "2026-10-26T16-30-23-001Z", "cron",
                  completed(), exit_code=0, turns=30)
    with pytest.raises(cf.SeatNotFound) as exc:
        cf.resolve_seat("exo", tmp_path, company="atelier")
    assert "3 companies" in str(exc.value)


def test_a_collision_is_settled_by_the_company_whose_checkout_this_is(tmp_path):
    for seat in ("alexandria-research", "ursa-research"):
        write_log(tmp_path, seat, "2026-10-26T16-30-23-001Z", "cron",
                  completed(), exit_code=0, turns=30)
    assert cf.resolve_seat("research", tmp_path, company="alexandria") == "alexandria-research"
    assert cf.resolve_seat("research", tmp_path, company="ursa") == "ursa-research"


def test_an_exact_directory_name_beats_the_suffix_search(tmp_path):
    # This host carries a directory literally named `engineer` beside
    # `alexandria-engineer`, `atelier-engineer` and `epitome-engineer`. The
    # name the reader typed is the one that wins.
    for seat in ("engineer", "alexandria-engineer", "atelier-engineer"):
        write_log(tmp_path, seat, "2026-10-26T16-30-23-001Z", "cron",
                  completed(), exit_code=0, turns=30)
    assert cf.resolve_seat("engineer", tmp_path, company="alexandria") == "engineer"


def test_no_seat_argument_still_means_every_seat(tmp_path):
    assert cf.resolve_seat(None, tmp_path) is None


def test_an_unmounted_log_root_is_still_observation_skipped_and_not_a_bad_seat(tmp_path):
    # A pull request checkout has no `/srv/asc`, and that path must stay the
    # "observation skipped" answer rather than becoming "no such seat".
    missing = tmp_path / "nothing-here"
    assert cf.resolve_seat("research", missing) == "research"
    assert cf.main(["--seat", "research", "--root", str(missing)]) == 0


def test_a_seat_that_does_not_resolve_exits_two_instead_of_reporting_quiet_days(tmp_path, capsys):
    write_log(tmp_path, "alexandria-research", "2026-10-26T16-30-23-001Z",
              "cron", completed(), exit_code=0, turns=30)
    code = cf.main(["--seat", "totallyfake", "--root", str(tmp_path),
                    "--now", "2026-10-27T01:00:00Z"])
    captured = capsys.readouterr()
    assert code == 2
    assert "not a seat" in captured.err
    # The sentence that used to be printed here, and must not be any more.
    assert "none has in the trailing" not in captured.out


def test_a_real_seat_and_an_invented_one_no_longer_read_the_same(tmp_path, capsys):
    # The defect itself, as one assertion.
    write_log(tmp_path, "alexandria-research", "2026-10-26T16-30-23-001Z",
              "cron", completed(), exit_code=0, turns=30)
    cf.main(["--day", "2026-10-26", "--seat", "research", "--root", str(tmp_path),
             "--now", "2026-10-26T23:00:00Z"])
    real = capsys.readouterr().out
    cf.main(["--day", "2026-10-26", "--seat", "totallyfake", "--root", str(tmp_path),
             "--now", "2026-10-26T23:00:00Z"])
    invented = capsys.readouterr().out
    assert real != invented
    assert "alexandria-research" in real


def test_the_resolution_is_said_out_loud_when_it_rewrites_the_argument(tmp_path, capsys):
    write_log(tmp_path, "alexandria-research", "2026-10-26T16-30-23-001Z",
              "cron", completed(), exit_code=0, turns=30)
    cf.main(["--day", "2026-10-26", "--seat", "research", "--root", str(tmp_path),
             "--now", "2026-10-26T23:00:00Z"])
    assert "reading alexandria-research for --seat 'research'" in capsys.readouterr().err


def test_the_company_is_taken_from_the_checkouts_own_remote(monkeypatch):
    monkeypatch.delenv("ASC_COMPANY", raising=False)
    monkeypatch.setenv("GITHUB_REPOSITORY", "alexandrapaiz/alexandria")
    assert cf.company_here() == "alexandria"
    monkeypatch.setenv("ASC_COMPANY", "ursa")
    assert cf.company_here() == "ursa"


def test_a_re_fire_that_is_still_running_leaves_the_cycle_in_recovery(tmp_path):
    """Security's real 2026-11-01 slot, read while the re-fire was still going.

    The refused run's own verdict was never the problem: `reason_of` has
    refused to call a live run lost since it was written. What nobody applied
    that reasoning to was the *successor*, and the promotion out of `lost`
    required `successor["pr"]` to be truthy, which a run with no trailer can
    never be. So a slot in recovery scored `lost` and set the exit code.
    """
    write_log(tmp_path, "alexandria-security", "2026-11-01T13-00-27-477Z",
              "cron", refused("You've hit your weekly limit · resets 11pm (UTC)"),
              exit_code=1, turns=1)
    write_log(tmp_path, "alexandria-security", "2026-11-01T23-04-44-320Z",
              "hook", trailer=False)
    claims = cf.read_retry_claims(claim_file(
        tmp_path,
        **{"alexandria-security": ["2026-11-01T13-00-27-477Z-cron.log"]}))
    result = cf.judge(cf.read_runs(tmp_path), "2026-11-01", claims=claims,
                      now=datetime(2026, 11, 1, 23, 34, tzinfo=UTC))
    assert result["lost"] == [], "a live re-fire is not a lost cycle"
    finding, = result["recovering"]
    assert finding["seat"] == "alexandria-security"
    assert finding["slot"] == "13:00Z"
    assert finding["why"] == "weekly-limit"
    assert finding["retried_by"] == "2026-11-01T23-04-44-320Z-hook"


def test_a_cycle_in_recovery_does_not_set_the_exit_code(tmp_path, capsys):
    write_log(tmp_path, "alexandria-security", "2026-11-01T13-00-27-477Z",
              "cron", refused("You've hit your weekly limit · resets 11pm (UTC)"),
              exit_code=1, turns=1)
    write_log(tmp_path, "alexandria-security", "2026-11-01T23-04-44-320Z",
              "hook", trailer=False)
    path = claim_file(
        tmp_path,
        **{"alexandria-security": ["2026-11-01T13-00-27-477Z-cron.log"]})
    code = cf.main(["--day", "2026-11-01", "--root", str(tmp_path),
                    "--claims", str(path), "--now", "2026-11-01T23:34:00Z"])
    out = capsys.readouterr().out
    assert code == 0, "a gate must not go red on a recovery that is working"
    assert "recover  alexandria-security 13:00Z weekly-limit" in out
    assert "still running" in out
    assert "LOST" not in out
    assert "cycle(s) lost" not in out


def test_once_the_re_fire_is_too_old_the_cycle_is_lost_again(tmp_path, capsys):
    """The grace is a wait, not an amnesty.

    Same two logs as the test above, read past `GRACE_MINUTES`. The successor's
    missing trailer has stopped being evidence of a live run and become
    evidence that nobody is coming to write it, so the cycle is lost and the
    exit code says so.
    """
    write_log(tmp_path, "alexandria-security", "2026-11-01T13-00-27-477Z",
              "cron", refused("You've hit your weekly limit · resets 11pm (UTC)"),
              exit_code=1, turns=1)
    write_log(tmp_path, "alexandria-security", "2026-11-01T23-04-44-320Z",
              "hook", trailer=False)
    path = claim_file(
        tmp_path,
        **{"alexandria-security": ["2026-11-01T13-00-27-477Z-cron.log"]})
    code = cf.main(["--day", "2026-11-01", "--root", str(tmp_path),
                    "--claims", str(path), "--now", "2026-11-02T06:00:00Z"])
    out = capsys.readouterr().out
    assert code == 1
    assert "lost after a recovery attempt" in out


def test_a_finished_re_fire_that_shipped_nothing_is_still_lost(tmp_path, capsys):
    """The guard is liveness and never the mere absence of a pull request.

    This is the regression that matters: `recovering` must not swallow the
    case the `lost` hint was written for, a re-fire that ran to completion and
    reached no pull request.
    """
    write_log(tmp_path, "alexandria-security", "2026-11-01T13-00-27-477Z",
              "cron", refused("You've hit your weekly limit · resets 11pm (UTC)"),
              exit_code=1, turns=1)
    write_log(tmp_path, "alexandria-security", "2026-11-01T23-04-44-320Z",
              "hook", completed(), exit_code=0, turns=40)
    path = claim_file(
        tmp_path,
        **{"alexandria-security": ["2026-11-01T13-00-27-477Z-cron.log"]})
    code = cf.main(["--day", "2026-11-01", "--root", str(tmp_path),
                    "--claims", str(path), "--now", "2026-11-01T23:34:00Z"])
    out = capsys.readouterr().out
    assert code == 1
    assert "lost after a recovery attempt" in out
    assert "recover  " not in out, "the recovering row must not appear"

# --- the pull request index can be blind to a seat, and that is not a verdict
#
# Added 2026-11-02. Three readings of one slot in one run, in this order:
# `LOST?` because the index was blind to `sec/`, then `retried` because the
# alias made #657 visible, then `LOST?` again because #657 is a draft. Only
# the third is both right and right for the right reason, and the first two
# are what these tests stand against.

def test_a_seat_whose_branch_prefix_no_rule_derives_is_still_matched():
    """`alexandria-security` ships from `sec/`, which neither prefix forms."""
    assert "sec" in cf._branch_prefixes("alexandria-security")
    assert "alexandria-security" in cf._branch_prefixes("alexandria-security")


def test_an_index_that_knows_no_branch_of_a_seats_is_blind_to_it():
    index = [pr_entry(660, "alexandria-writer/2026-11-01-hook", "2026-11-01T23:16:37Z")]
    assert cf.index_is_blind_to("alexandria-okr", index) is True
    assert cf.index_is_blind_to("alexandria-writer", index) is False


def test_an_empty_index_is_not_blindness_because_it_was_never_passed():
    """`--prs` unpassed is the ordinary case; calling it blindness cries wolf."""
    assert cf.index_is_blind_to("alexandria-writer", []) is False


def test_a_blind_index_says_so_rather_than_reporting_no_pull_request(tmp_path, capsys):
    write_log(tmp_path, "alexandria-security", "2026-11-01T13-00-27-000Z", "cron",
              refused("You've hit your weekly limit · resets 11am (UTC)"),
              exit_code=1, turns=1)
    index = [pr_entry(660, "alexandria-writer/2026-11-01-hook", "2026-11-01T23:16:37Z")]
    cf.judge(cf.read_runs(tmp_path), "2026-11-01", pr_index=index,
             now=datetime(2026, 11, 1, 23, 59, tzinfo=UTC))
    finding, = cf.judge(cf.read_runs(tmp_path), "2026-11-01", pr_index=index,
                        now=datetime(2026, 11, 1, 23, 59, tzinfo=UTC))["lost"]
    assert finding["pr_index_blind"] is True


def test_a_re_fire_that_left_its_pull_request_a_draft_has_not_carried_the_cycle(tmp_path):
    """L-A32: no gate can reach a draft, so a draft is not an arrival.

    Security's 13:00Z slot on 2026-11-01, as the host recorded it: refused at
    turn one, claimed by the retry, re-fired at 23:04:44Z, and that run opened
    #657 and exited 124 before `gh pr ready`.
    """
    write_log(tmp_path, "alexandria-security", "2026-11-01T13-00-27-000Z", "cron",
              refused("You've hit your weekly limit · resets 11am (UTC)"),
              exit_code=1, turns=1)
    write_log(tmp_path, "alexandria-security", "2026-11-01T23-04-44-320Z", "hook",
              None, exit_code=124, turns=None)
    claims = cf.read_retry_claims(claim_file(
        tmp_path,
        **{"alexandria-security": ["2026-11-01T13-00-27-000Z-cron.log"]}))
    index = [dict(pr_entry(657, "sec/2026-11-01", "2026-11-01T23:06:23Z"),
                  isDraft=True)]
    result = cf.judge(cf.read_runs(tmp_path), "2026-11-01", claims=claims,
                      pr_index=index, now=datetime(2026, 11, 2, 0, 5, tzinfo=UTC))
    assert result["retried"] == []
    finding, = result["lost"]
    assert finding["retry_pr_is_draft"] is True
    assert finding["retry_pr"] == "https://github.com/o/r/pull/657"


def test_the_same_re_fire_with_the_draft_readied_does_carry_the_cycle(tmp_path):
    """The mirror, so the draft check cannot pass by refusing everything."""
    write_log(tmp_path, "alexandria-security", "2026-11-01T13-00-27-000Z", "cron",
              refused("You've hit your weekly limit · resets 11am (UTC)"),
              exit_code=1, turns=1)
    write_log(tmp_path, "alexandria-security", "2026-11-01T23-04-44-320Z", "hook",
              None, exit_code=124, turns=None)
    claims = cf.read_retry_claims(claim_file(
        tmp_path,
        **{"alexandria-security": ["2026-11-01T13-00-27-000Z-cron.log"]}))
    index = [dict(pr_entry(657, "sec/2026-11-01", "2026-11-01T23:06:23Z"),
                  isDraft=False)]
    result = cf.judge(cf.read_runs(tmp_path), "2026-11-01", claims=claims,
                      pr_index=index, now=datetime(2026, 11, 2, 0, 5, tzinfo=UTC))
    assert result["lost"] == []
    finding, = result["retried"]
    assert finding["retry_pr_is_draft"] is False


def test_an_index_built_without_isdraft_is_unknown_rather_than_readied(tmp_path):
    """An absent field is not a false one, which is how the claim file is read."""
    write_log(tmp_path, "alexandria-security", "2026-11-01T13-00-27-000Z", "cron",
              refused("You've hit your weekly limit · resets 11am (UTC)"),
              exit_code=1, turns=1)
    write_log(tmp_path, "alexandria-security", "2026-11-01T23-04-44-320Z", "hook",
              None, exit_code=124, turns=None)
    claims = cf.read_retry_claims(claim_file(
        tmp_path,
        **{"alexandria-security": ["2026-11-01T13-00-27-000Z-cron.log"]}))
    index = [pr_entry(657, "sec/2026-11-01", "2026-11-01T23:06:23Z")]
    result = cf.judge(cf.read_runs(tmp_path), "2026-11-01", claims=claims,
                      pr_index=index, now=datetime(2026, 11, 2, 0, 5, tzinfo=UTC))
    finding, = result["retried"]
    assert finding["retry_pr_is_draft"] is False


# --- the host does not always write a number for `exit`
#
# Added 2026-11-02. `# exit=timeout pr=- session=- turns=-` is what the host
# writes when it kills a run on the wall clock. The trailer pattern took digits
# only, so the one trailer that proves a run is dead was the one this reader
# could not see, and `recovering` held security's dead re-fire as "still
# running" for the whole grace window. Fourth reading of that slot in one run,
# and the first that is right for the right reason.

def timeout_log(root, seat, stamp, trigger):
    """A run the host killed on the wall clock, trailer and all."""
    run_id = f"{stamp}-{trigger}"
    directory = Path(root) / seat
    directory.mkdir(parents=True, exist_ok=True)
    body = HEADER.format(seat=seat, run_id=run_id, trigger=trigger)
    body += "---\n# exit=timeout pr=- session=- turns=-\n"
    path = directory / f"{run_id}.log"
    path.write_text(body, encoding="utf-8")
    return path


def test_a_word_exit_is_a_trailer_rather_than_a_missing_one(tmp_path):
    run = cf.parse_run(timeout_log(tmp_path, "alexandria-security",
                                   "2026-11-01T23-04-44-320Z", "hook"))
    assert run["truncated"] is False
    assert run["ended"] is True
    assert run["exit_word"] == "timeout"
    assert run["exit_code"] is None, "callers compare exit_code to 0; keep it numeric"
    assert run["turns"] is None, "`turns=-` is unknown, not zero"


def test_a_timeout_is_not_a_clean_finish(tmp_path):
    """Falling through to None here would read `exit=timeout` as success."""
    run = cf.parse_run(timeout_log(tmp_path, "alexandria-security",
                                   "2026-11-01T23-04-44-320Z", "hook"))
    assert cf.reason_of(run, now=datetime(2026, 11, 2, 0, 30, tzinfo=UTC)) == "timeout"


def test_a_wall_kill_leaves_its_pull_request_unknown_rather_than_absent(tmp_path):
    """The claim the docstring makes, pinned so prose cannot drift off it again.

    A killed run's `pr=-` must never read as "this run chose to stop and
    shipped nothing". The seat's own 2026-11-01T23:04:44Z re-fire is the
    worked example: killed on the wall, `pr=-` in its trailer, and #657 open
    on the branch it had already pushed. The function gets this right through
    `exit_code` being None rather than through any mention of the wall clock,
    which is why it is worth a test of its own: the behaviour is correct by
    side effect, and a later edit to the final clause could take it away
    without touching anything that currently fails.
    """
    run = cf.parse_run(timeout_log(tmp_path, "alexandria-security",
                                   "2026-11-01T23-04-44-320Z", "hook"))
    assert run["pr"] is None
    assert cf.pr_absence_is_evidence(run) is False


def test_a_numeric_trailer_is_unchanged_by_the_widening(tmp_path):
    path = write_log(tmp_path, "alexandria-engineer", "2026-10-25T11-06-03-756Z",
                     "cron", completed(), exit_code=0,
                     pr="https://github.com/o/r/pull/516", turns=25)
    run = cf.parse_run(path)
    assert (run["exit_code"], run["turns"], run["exit_word"]) == (0, 25, None)
    assert run["ended"] is True


def test_a_re_fire_killed_on_the_clock_is_not_in_recovery(tmp_path):
    """Security's slot, as the host actually recorded it.

    The re-fire's trailer says `exit=timeout`, so it has finished and its
    `pr=-` is not the absence of a trailer. Before the widening this read as
    `recovering` — "which is still running" — and the draft check could not
    fire, because `recovering` outranks it.
    """
    write_log(tmp_path, "alexandria-security", "2026-11-01T13-00-27-000Z", "cron",
              refused("You've hit your weekly limit · resets 11am (UTC)"),
              exit_code=1, turns=1)
    timeout_log(tmp_path, "alexandria-security", "2026-11-01T23-04-44-320Z", "hook")
    claims = cf.read_retry_claims(claim_file(
        tmp_path,
        **{"alexandria-security": ["2026-11-01T13-00-27-000Z-cron.log"]}))
    index = [dict(pr_entry(657, "sec/2026-11-01", "2026-11-01T23:06:23Z"),
                  isDraft=True)]
    result = cf.judge(cf.read_runs(tmp_path), "2026-11-01", claims=claims,
                      pr_index=index, now=datetime(2026, 11, 2, 0, 25, tzinfo=UTC))
    assert result["recovering"] == []
    finding, = result["lost"]
    assert finding["retry_pr_is_draft"] is True


def test_a_re_fire_with_no_trailer_at_all_is_still_in_recovery(tmp_path):
    """The mirror: the widening must not take `recovering` away from its own case."""
    write_log(tmp_path, "alexandria-security", "2026-11-01T13-00-27-000Z", "cron",
              refused("You've hit your weekly limit · resets 11am (UTC)"),
              exit_code=1, turns=1)
    write_log(tmp_path, "alexandria-security", "2026-11-01T23-04-44-320Z", "hook",
              None, trailer=False)
    claims = cf.read_retry_claims(claim_file(
        tmp_path,
        **{"alexandria-security": ["2026-11-01T13-00-27-000Z-cron.log"]}))
    result = cf.judge(cf.read_runs(tmp_path), "2026-11-01", claims=claims,
                      now=datetime(2026, 11, 1, 23, 30, tzinfo=UTC))
    assert len(result["recovering"]) == 1


# ---------------------------------------------------------------------------
# A slot the host folded into a run already going (2026-11-02). These are the
# only tests here that read a second surface, because the class is defined by
# the absence of the first one: a coalesced slot starts no run, so it writes no
# log, so nothing above can see it. The audit log is written beside the log
# root on the host and these build it the same way.


def write_audit(root, rows):
    """`audit.jsonl` in the host's layout: a sibling of the log root."""
    root.parent.mkdir(parents=True, exist_ok=True)
    (root.parent / "audit.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    return root.parent / "audit.jsonl"


def cron_row(seat, stamp, coalesced=True):
    row = {"ts": stamp, "action": "cron", "agent": seat, "trigger": "cron"}
    if coalesced:
        row["coalesced"] = True
    return row


def test_a_coalesced_slot_has_no_log_and_is_reported_anyway(tmp_path):
    """The whole point. No log is written, so `read_runs` is empty, and the
    slot is still named rather than silently absent."""
    logs = tmp_path / "logs"
    audit = write_audit(logs, [cron_row("alexandria-exo", "2026-11-02T01:00:20.061Z")])
    result = cf.judge(cf.read_runs(logs), "2026-11-02", now=NOW,
                      coalesced=cf.read_coalesced(audit, day="2026-11-02"))
    finding, = result["findings"]
    assert finding["state"] == "coalesced"
    assert finding["slot"] == "01:00Z"
    assert result["coalesced"] == [finding]


def test_a_coalesced_slot_sets_the_exit_code(tmp_path):
    logs = tmp_path / "logs"
    write_audit(logs, [cron_row("alexandria-exo", "2026-11-02T01:00:20.061Z")])
    logs.mkdir(parents=True, exist_ok=True)
    (logs / "alexandria-exo").mkdir()
    assert cf.main(["--day", "2026-11-02", "--root", str(logs),
                    "--now", "2026-11-02T04:00:00Z"]) == 1


def test_the_coalesced_row_names_the_run_that_absorbed_it(tmp_path):
    logs = tmp_path / "logs"
    write_log(logs, "alexandria-exo", "2026-11-02T00-49-18-438Z", "message",
              completed(), exit_code=0, turns=103)
    audit = write_audit(logs, [cron_row("alexandria-exo", "2026-11-02T01:00:20.061Z")])
    result = cf.judge(cf.read_runs(logs), "2026-11-02", now=NOW,
                      coalesced=cf.read_coalesced(audit, day="2026-11-02"))
    finding, = [f for f in result["findings"] if f["state"] == "coalesced"]
    assert finding["absorbed_into"] == "00:49Z message"


def test_a_coalesced_slot_a_later_cron_run_carried_is_deferred_not_lost(tmp_path):
    """`ursa-exo`, 2026-11-02: coalesced at 01:30:23Z and dispatched at
    01:40:48Z, three milliseconds after the run it was waiting on ended. The
    same audit row means dropped for one seat and ten minutes late for
    another, and only a later `cron` run separates them."""
    logs = tmp_path / "logs"
    write_log(logs, "ursa-exo", "2026-11-02T01-40-48-770Z", "cron",
              completed("Had a look, opened nothing."), exit_code=0, turns=130)
    audit = write_audit(logs, [cron_row("ursa-exo", "2026-11-02T01:30:23.908Z")])
    result = cf.judge(cf.read_runs(logs), "2026-11-02", now=NOW,
                      coalesced=cf.read_coalesced(audit, day="2026-11-02"))
    finding, = result["findings"]
    assert result["coalesced"] == []
    assert finding["deferred_minutes"] == 10
    assert finding["coalesced_at"] == "01:30:23Z"


def test_a_deferred_slot_is_labelled_with_its_slot_and_not_its_dispatch(tmp_path):
    """The defect this found in the existing output: `ursa-exo` was reported at
    `01:40Z`, a minute no cron line anywhere puts a slot at."""
    logs = tmp_path / "logs"
    write_log(logs, "ursa-exo", "2026-11-02T01-40-48-770Z", "cron",
              completed("Had a look, opened nothing."), exit_code=0, turns=130)
    audit = write_audit(logs, [cron_row("ursa-exo", "2026-11-02T01:30:23.908Z")])
    plain = cf.judge(cf.read_runs(logs), "2026-11-02", now=NOW)
    assert plain["findings"][0]["slot"] == "01:40Z"
    with_audit = cf.judge(cf.read_runs(logs), "2026-11-02", now=NOW,
                          coalesced=cf.read_coalesced(audit, day="2026-11-02"))
    assert with_audit["findings"][0]["slot"] == "01:30Z"


def test_a_non_coalesced_cron_row_in_the_audit_log_is_not_a_finding(tmp_path):
    """The audit log has a row for every firing. Only the folded ones are this
    class, and reading the rest as coalesced would report every slot twice."""
    logs = tmp_path / "logs"
    audit = write_audit(logs, [cron_row("alexandria-pm", "2026-11-02T11:05:00.000Z",
                                        coalesced=False)])
    assert cf.read_coalesced(audit, day="2026-11-02") == []


def test_an_absent_audit_log_is_an_empty_reading_and_not_a_traceback(tmp_path):
    """A pull request checkout has no audit log, and the rest of the reading is
    still correct without it: less decided, not broken."""
    assert cf.read_coalesced(tmp_path / "nothing.jsonl") == []


def test_the_audit_reader_scopes_to_the_seat_and_the_day_it_was_asked_for(tmp_path):
    logs = tmp_path / "logs"
    audit = write_audit(logs, [
        cron_row("alexandria-exo", "2026-11-02T01:00:20.061Z"),
        cron_row("ursa-security", "2026-11-02T01:15:23.753Z"),
        cron_row("alexandria-exo", "2026-10-26T01:00:20.061Z"),
    ])
    both = cf.read_coalesced(audit, day="2026-11-02")
    assert [row["seat"] for row in both] == ["alexandria-exo", "ursa-security"]
    mine = cf.read_coalesced(audit, seat="alexandria-exo", day="2026-11-02")
    assert [row["at"] for row in mine] == ["01:00:20Z"]


def test_the_rendering_names_the_coalesced_state_a_reader_will_meet(tmp_path, capsys):
    logs = tmp_path / "logs"
    (logs / "alexandria-exo").mkdir(parents=True)
    write_audit(logs, [cron_row("alexandria-exo", "2026-11-02T01:00:20.061Z")])
    cf.main(["--day", "2026-11-02", "--root", str(logs),
             "--now", "2026-11-02T04:00:00Z"])
    out = capsys.readouterr().out
    assert "COALESCED alexandria-exo 01:00Z" in out
    assert "1 slot(s) coalesced into a run already going." in out


def test_a_malformed_audit_line_is_skipped_rather_than_fatal(tmp_path):
    logs = tmp_path / "logs"
    logs.parent.mkdir(parents=True, exist_ok=True)
    (logs.parent / "audit.jsonl").write_text(
        '{"coalesced": true, not json\n'
        + json.dumps(cron_row("ursa-security", "2026-11-02T01:15:23.753Z")) + "\n",
        encoding="utf-8")
    rows = cf.read_coalesced(logs.parent / "audit.jsonl", day="2026-11-02")
    assert [row["seat"] for row in rows] == ["ursa-security"]
# --- the provider's third refusal, which is not a limit --------------------
#
# Added by the security seat on 2026-11-02 from its own 03:48:09Z run. The two
# refusals this file knew were capacity limits carrying `api_error_status:
# 429`. A content safeguard is a third kind: it declines the message, it
# carries `stop_reason: "refusal"` with `api_error_status: null`, and it never
# clears by waiting.

def safeguard_refused(classifier="bio", model="Opus 5", turns=17):
    """The real shape of the 2026-11-02 03:48:09Z refusal of this seat.

    Copied field for field from the log, including the two that mislead:
    `subtype` reads `success` beside `is_error: true`, and `api_error_status`
    is null rather than a status. No prompt text and no classifier payload,
    only the shape.
    """
    return {"type": "result", "subtype": "success", "is_error": True,
            "num_turns": turns, "api_error_status": None,
            "stop_reason": "refusal", "terminal_reason": "api_error",
            "result": (f"API Error: {model}'s safeguards flagged this message "
                       f"(https://www.anthropic.com/legal/aup). Our "
                       f"intentionally broad safeguards allow us to deliver "
                       f"more capabilities faster, but can sometimes flag "
                       f"legitimate tasks.\n\nTry rephrasing the request in a "
                       f"new session or change your model.\n\nDetails: "
                       f"`[{classifier}]`"),
            "duration_ms": 154602}


def test_a_content_safeguard_refusal_is_classified_and_not_read_as_our_crash(tmp_path):
    """The defect this exists for: it used to come back `nonzero-exit`.

    `classify_refusal` gated on `api_error_status == 429`, and a safeguard
    refusal carries null there, so the provider declining our message was
    reported in the same word as the seat's own code failing.
    """
    path = write_log(tmp_path, "alexandria-security", "2026-11-02T03-48-09-517Z",
                     "message", safeguard_refused(), exit_code=1, turns=17)
    run = cf.parse_run(path)
    assert run["refusal"] == "safeguard-refusal"
    assert run["api_error_status"] is None
    assert cf.reason_of(run) == "safeguard-refusal"


def test_a_safeguard_refusal_is_not_one_of_the_two_capacity_limits(tmp_path):
    """The distinction is the point, so it is asserted rather than implied.

    A weekly or session limit tells a reader to wait and says until when. A
    safeguard refusal has no reset at all, so collapsing it into either one
    tells a reader to wait for a window that never arrives. That was the live
    misreading on the night this was found.
    """
    for classifier in ("bio", "cyber"):
        path = write_log(tmp_path, "alexandria-security",
                         f"2026-11-02T03-48-09-51{len(classifier)}Z", "message",
                         safeguard_refused(classifier=classifier),
                         exit_code=1, turns=17)
        refusal = cf.parse_run(path)["refusal"]
        # Positively, so the assertion below cannot be satisfied by `None`,
        # which is what the first draft of this test allowed: it passed
        # against the unfixed code because an unclassified refusal is also
        # not one of the three words.
        assert refusal == "safeguard-refusal"
        assert refusal not in (
            "weekly-limit", "session-limit", "unclassified-429")


def test_the_two_capacity_limits_still_classify_as_they_did(tmp_path):
    """The narrowness of the change above, asserted rather than assumed."""
    weekly = write_log(tmp_path, "alexandria-engineer",
                       "2026-11-02T11-06-03-756Z", "cron",
                       refused("You've hit your weekly limit · resets 11pm (UTC)"),
                       exit_code=1, turns=1)
    session = write_log(tmp_path, "alexandria-engineer",
                        "2026-11-02T12-06-03-756Z", "cron",
                        cut_off(), exit_code=1, turns=89)
    assert cf.parse_run(weekly)["refusal"] == "weekly-limit"
    assert cf.parse_run(session)["refusal"] == "session-limit"


def test_a_clean_run_is_not_turned_into_a_refusal_by_the_new_branch(tmp_path):
    """`stop_reason` is absent from an ordinary result object, not empty."""
    path = write_log(tmp_path, "alexandria-engineer", "2026-11-02T13-06-03-756Z",
                     "cron", completed(), exit_code=0, turns=25)
    assert cf.parse_run(path)["refusal"] is None


# --- the company probe's bound, added 2026-11-09 by the security seat --------
#
# Three tests, each with a control, against the one call in this file that
# leaves the process. Each failure shape is driven by a real `git` on a real
# `PATH` rather than a mock, because what is under test is an exit code and a
# hang crossing a process boundary, and a mock cannot be wrong about those in
# the way the real thing is.


def _shim(tmp_path, name, script):
    """A directory holding one executable, for putting at the head of PATH."""
    d = tmp_path / f"bin-{name}"
    d.mkdir(exist_ok=True)
    (d / "git").write_text(script)
    (d / "git").chmod(0o755)
    return d


def test_the_company_probe_is_bounded_and_a_hang_is_not_an_answer(
        tmp_path, monkeypatch, capsys):
    """A hanging git returns None in bounded time rather than stalling.

    The control is the same call with a git that answers: it must still return
    the company, or this test would pass against a probe that never runs.
    """
    monkeypatch.delenv("ASC_COMPANY", raising=False)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)

    answers = _shim(tmp_path, "answers",
                    "#!/bin/sh\necho https://github.com/alexandrapaiz/ursa\n")
    monkeypatch.setenv("PATH", f"{answers}:{os.environ['PATH']}")
    assert cf.company_here(timeout=2) == "ursa"          # the control

    hangs = _shim(tmp_path, "hangs", "#!/bin/sh\nsleep 600\n")
    monkeypatch.setenv("PATH", f"{hangs}:{os.environ['PATH']}")
    started = time.monotonic()
    assert cf.company_here(timeout=2) is None
    assert time.monotonic() - started < 30, "the probe waited past its bound"
    assert "did not answer within 2s" in capsys.readouterr().err


def test_a_missing_git_binary_is_a_skipped_tie_break_and_not_a_traceback(
        tmp_path, monkeypatch, capsys):
    """No git on PATH used to raise FileNotFoundError out of a tie-break."""
    monkeypatch.delenv("ASC_COMPANY", raising=False)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)

    answers = _shim(tmp_path, "answers2",
                    "#!/bin/sh\necho https://github.com/alexandrapaiz/ursa.git\n")
    monkeypatch.setenv("PATH", f"{answers}:{os.environ['PATH']}")
    assert cf.company_here(timeout=5) == "ursa"          # the control, .git stripped

    empty = tmp_path / "bin-empty"
    empty.mkdir()
    monkeypatch.setenv("PATH", str(empty))
    assert cf.company_here(timeout=5) is None
    assert "could not run git" in capsys.readouterr().err


def test_a_failed_probe_is_not_the_answer_that_there_is_no_company(
        tmp_path, monkeypatch):
    """The conflation this fix exists to refuse.

    `proc.stdout if returncode == 0 else ""` made every way the probe can fail
    arrive as a company named "", which a caller reads as a fact about the
    world. Each failing shape now answers None, and the control still answers
    a name.
    """
    monkeypatch.delenv("ASC_COMPANY", raising=False)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)

    answers = _shim(tmp_path, "answers3",
                    "#!/bin/sh\necho https://github.com/alexandrapaiz/atelier\n")
    monkeypatch.setenv("PATH", f"{answers}:{os.environ['PATH']}")
    assert cf.company_here(timeout=5) == "atelier"       # the control

    for script, why in [
        ("#!/bin/sh\nexit 1\n", "git exits non-zero"),
        ("#!/bin/sh\nexit 128\n", "not a git repository"),
        ("#!/bin/sh\necho\n", "git exits clean and prints nothing"),
        ("#!/bin/sh\necho '   '\n", "git prints only whitespace"),
    ]:
        d = _shim(tmp_path, f"fail-{abs(hash(script))}", script)
        monkeypatch.setenv("PATH", f"{d}:{os.environ['PATH']}")
        assert cf.company_here(timeout=5) is None, why


def test_an_unanswerable_tie_break_raises_the_collision_it_cannot_settle(
        tmp_path, monkeypatch):
    """`resolve_seat` reads None rather than formatting it into a prefix.

    Two companies carry a seat named `exo` here, so the bare name needs the
    tie-break. With the probe answering, the checkout's company wins. With the
    probe unable to look, the collision raises, which is the same observable
    outcome the old empty string produced and the first one that says why.
    """
    monkeypatch.delenv("ASC_COMPANY", raising=False)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    for name in ("alexandria-exo", "ursa-exo"):
        (tmp_path / name).mkdir()

    answers = _shim(tmp_path, "answers4",
                    "#!/bin/sh\necho https://github.com/alexandrapaiz/ursa\n")
    monkeypatch.setenv("PATH", f"{answers}:{os.environ['PATH']}")
    assert cf.resolve_seat("exo", root=str(tmp_path)) == "ursa-exo"   # the control

    empty = tmp_path / "bin-empty-4"
    empty.mkdir()
    monkeypatch.setenv("PATH", str(empty))
    with pytest.raises(cf.SeatNotFound) as caught:
        cf.resolve_seat("exo", root=str(tmp_path))
    assert "2 companies" in str(caught.value)
