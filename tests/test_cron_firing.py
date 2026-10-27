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
