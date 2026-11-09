"""Does the pool instrument say the week is going before the week is gone.

Run with `python3 -m pytest tests/test_provider_cycle.py -q`.

Every test builds its own log tree in a temporary directory, in the host's
exact format, reusing the writers from `tests/test_cron_firing.py`. Nothing
here reads `/srv/asc/state`, because a test that needs the host's disk is a
test nobody runs on a pull request.

The two properties worth saying out loud, because they are what makes an
alarm worth leaving switched on:

It must fire with time to spare. The cycle of 2026-11-01 emptied its weekly
pool 9.8 hours in. Replayed against the host's own archive at 3.0 hours in,
this fires and predicts the wall within one and a quarter hours of where it
actually fell, which is 6.8 hours of warning.

It must stay quiet otherwise. The cycle of 2026-10-18 spent 39,918 turns over
148 hours and reached its reset, and replayed at 2026-10-20T12:00Z this says
`ok`. An alarm that is red on a healthy week is an alarm switched off by
Wednesday, which is the week it exists to save.
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import provider_cycle as pc  # noqa: E402

from test_cron_firing import completed, refused, write_log  # noqa: E402

UTC = timezone.utc

#: The live monthly sentence, which names the weekly reset in its own closing
#: clause. That clause is why `classify_refusal` had to learn an ordering, and
#: it is also a legitimate source for the boundary, so it appears here twice
#: over for two different reasons.
MONTHLY = ("You've hit your org's monthly spend limit · ask your admin to raise "
           "it at claude.ai/admin-settings/usage · your weekly limit resets "
           "Nov 8, 11pm (UTC)")
WEEKLY_DATED = "You've hit your weekly limit · resets Nov 8, 11pm (UTC)"
WEEKLY_BARE = "You've hit your weekly limit · resets 11pm (UTC)"

#: 2026-11-01 and 2026-11-08 are both Sundays, which is the weekday the
#: fallback rule assumes and the dated announcements independently confirm.
CYCLE_START = datetime(2026, 11, 1, 23, 0, tzinfo=UTC)
CYCLE_END = datetime(2026, 11, 8, 23, 0, tzinfo=UTC)


def stamp(when):
    return when.strftime("%Y-%m-%dT%H-%M-%S-000Z")


def spend(root, when, turns, seat="alexandria-engineer", trigger="message"):
    """A run that got past turn 1 and cost `turns` of the pool."""
    result = dict(completed())
    result["num_turns"] = turns
    write_log(root, seat, stamp(when), trigger, result,
              exit_code=0, pr="x/pull/1", turns=turns)


def refuse(root, when, sentence, seat="alexandria-engineer", trigger="cron"):
    write_log(root, seat, stamp(when), trigger, refused(sentence),
              exit_code=1, turns=1)


def burn(root, start, hours, per_hour, runs_per_hour=5, seat_prefix="seat"):
    """`hours` of steady spending, spread over several seats and runs.

    Five runs an hour is not arbitrary: a cycle needs `MIN_RUNS_TO_BOUND`
    priced runs before its total is allowed to bound the pool, so a ten-hour
    fixture at four an hour is `thin` and measures nothing. Five also divides
    every `per_hour` used below, which keeps the turn totals exact.
    """
    each = max(1, per_hour // runs_per_hour)
    for hour in range(hours):
        for n in range(runs_per_hour):
            when = start + timedelta(hours=hour, minutes=1 + n * 7)
            spend(root, when, each, seat=f"{seat_prefix}-{n}")


def anchor(root, before):
    """One run in the cycle before `before`, so the archive reaches back past it.

    A cycle is `clipped` when the archive holds nothing from before it opened,
    which is the only question that can be asked without inventing a
    tolerance. That makes the oldest cycle in any archive a floor, correctly,
    and it means a fixture whose earliest run *is* the cycle under test has
    built a clipped cycle on purpose. This is how a test says "assume the host
    had not just started pruning".
    """
    spend(root, before - timedelta(days=1), 3, seat="anchor")


# --- the reset instant is read, not assumed -------------------------------

def test_the_dated_announcement_is_the_boundary():
    observed = datetime(2026, 11, 4, 11, 6, tzinfo=UTC)
    assert pc.parse_reset(WEEKLY_DATED, observed) == CYCLE_END
    assert pc.parse_reset(MONTHLY, observed) == CYCLE_END


def test_the_undated_announcement_establishes_nothing():
    """`resets 11pm (UTC)` carries an hour and not a date.

    Eleven of the 141 undated refusals in the host's archive were observed on
    a Saturday, where the reset they name is 25 hours out rather than one.
    Reading it as 11pm on the day of observation invented a Saturday cycle
    edge in two of five weeks and split one real cycle in half, leaving a
    pool height of zero turns on the half that opened already refused.
    """
    saturday = datetime(2026, 11, 7, 16, 0, tzinfo=UTC)
    assert saturday.weekday() == 5
    assert pc.parse_reset(WEEKLY_BARE, saturday) is None


def test_a_december_refusal_naming_january_resets_next_year():
    observed = datetime(2026, 12, 28, 9, 0, tzinfo=UTC)
    reset = pc.parse_reset("You've hit your weekly limit · resets Jan 3, 11pm (UTC)",
                           observed)
    assert reset == datetime(2027, 1, 3, 23, 0, tzinfo=UTC)


def test_a_sentence_with_no_reset_in_it_is_not_guessed_at():
    assert pc.parse_reset("Overloaded", datetime(2026, 11, 4, tzinfo=UTC)) is None
    assert pc.parse_reset(None, datetime(2026, 11, 4, tzinfo=UTC)) is None


def test_the_weekday_rule_is_the_fallback_and_says_so(tmp_path):
    spend(tmp_path, CYCLE_START + timedelta(hours=1), 40)
    result = pc.assess(pc.cf.read_runs(tmp_path), CYCLE_START + timedelta(hours=3))
    assert result["live"]["boundary"] == "weekday rule"
    assert result["live"]["end"] == "2026-11-08T23:00:00Z"


def test_an_announced_boundary_is_marked_as_read(tmp_path):
    spend(tmp_path, CYCLE_START + timedelta(hours=1), 40)
    refuse(tmp_path, CYCLE_START + timedelta(hours=2), WEEKLY_DATED)
    result = pc.assess(pc.cf.read_runs(tmp_path), CYCLE_START + timedelta(hours=3))
    assert result["live"]["boundary"] == "announced"


# --- what bounds the pool -------------------------------------------------

def test_the_pool_is_the_turns_spent_before_the_wall(tmp_path):
    """Everything after the wall is turn-1 refusals, which are not spending."""
    anchor(tmp_path, CYCLE_START)
    burn(tmp_path, CYCLE_START, hours=10, per_hour=400)
    wall = CYCLE_START + timedelta(hours=10)
    refuse(tmp_path, wall, WEEKLY_DATED)
    for n in range(40):
        refuse(tmp_path, wall + timedelta(minutes=n + 1), WEEKLY_DATED,
               seat=f"late-{n}")

    result = pc.assess(pc.cf.read_runs(tmp_path), CYCLE_END + timedelta(hours=1))
    cycle, = [c for c in result["cycles"] if c["start"] == "2026-11-01T23:00:00Z"]
    assert cycle["verdict"] == "weekly-exhausted"
    assert cycle["turns_before_the_wall"] == 4000
    assert cycle["turns"] == 4000 + 41, "the refusals cost a turn each"
    assert result["pool"]["low"] == 4000, "the wall's height, not the cycle's total"


def test_a_cycle_that_was_never_refused_is_a_floor_and_not_a_ceiling(tmp_path):
    """It spent less than the pool holds and says nothing about how much less."""
    anchor(tmp_path, CYCLE_START)
    burn(tmp_path, CYCLE_START, hours=100, per_hour=40)
    result = pc.assess(pc.cf.read_runs(tmp_path), CYCLE_END + timedelta(hours=1))
    cycle, = [c for c in result["cycles"] if c["start"] == "2026-11-01T23:00:00Z"]
    assert cycle["verdict"] == "complete"
    assert result["pool"]["cycles"] == 0
    assert result["pool"]["floor_from_unbounding_cycles"] == 4000


def test_a_cycle_clipped_by_the_archives_own_start_is_a_floor(tmp_path):
    """The host prunes, so a cycle's opening hours age out before it does.

    Measured while this file was written: the log count under the root fell
    from 3,385 to 3,209 in twenty minutes, and the cycle of 2026-10-18 went
    from holding its whole week to beginning on 2026-10-23. A cycle whose
    first hours are gone cannot say what was spent in them.
    """
    late = CYCLE_START + timedelta(days=4)
    burn(tmp_path, late, hours=10, per_hour=400)
    refuse(tmp_path, late + timedelta(hours=10), WEEKLY_DATED)
    result = pc.assess(pc.cf.read_runs(tmp_path), CYCLE_END + timedelta(hours=1))
    cycle, = [c for c in result["cycles"] if c["start"] == "2026-11-01T23:00:00Z"]
    assert cycle["clipped"] is True
    assert cycle["verdict"] == "clipped"
    assert result["pool"]["cycles"] == 0, "a clipped cycle bounds nothing"
    assert result["pool"]["excluded"]["clipped"] == 1


def test_a_cycle_that_opened_already_refused_has_no_height(tmp_path):
    """Zero turns before the wall is a statement about the window's edges.

    A ceiling of zero would make every projection fail for ever, which is the
    shape of a gate that is red for a reason nobody can act on.
    """
    refuse(tmp_path, CYCLE_START + timedelta(minutes=1), WEEKLY_DATED)
    for n in range(60):
        refuse(tmp_path, CYCLE_START + timedelta(minutes=n + 2), WEEKLY_DATED,
               seat=f"late-{n}")
    result = pc.assess(pc.cf.read_runs(tmp_path), CYCLE_END + timedelta(hours=1))
    assert result["pool"]["cycles"] == 0


def test_a_run_with_no_turn_count_is_unread_rather_than_free(tmp_path):
    burn(tmp_path, CYCLE_START, hours=10, per_hour=400)
    write_log(tmp_path, "timed-out", stamp(CYCLE_START + timedelta(hours=2)),
              "cron", exit_code=None, turns=None)
    path = (tmp_path / "timed-out" /
            f"{stamp(CYCLE_START + timedelta(hours=2))}-cron.log")
    path.write_text(path.read_text().replace("turns=0", "turns=-")
                    .replace("exit=None", "exit=timeout"))
    result = pc.assess(pc.cf.read_runs(tmp_path), CYCLE_START + timedelta(hours=11))
    assert result["live"]["runs_unpriced"] == 1


# --- the three limits are three things ------------------------------------

def test_the_monthly_cap_stops_the_projection_rather_than_feeding_it(tmp_path):
    """It is not a function of the weekly pool, so projecting it would lie.

    And its remedy is the owner raising a limit in the org's admin settings,
    which no amount of rescheduling touches, so the report says that instead
    of a time.
    """
    burn(tmp_path, CYCLE_START, hours=10, per_hour=400)
    refuse(tmp_path, CYCLE_START + timedelta(hours=10), WEEKLY_DATED)
    refuse(tmp_path, CYCLE_START + timedelta(days=2), MONTHLY, seat="pm")
    now = CYCLE_START + timedelta(days=3)

    result = pc.assess(pc.cf.read_runs(tmp_path), now)
    assert result["live"]["verdict"] == "monthly-capped"
    assert result["live"]["monthly_refusals"] == 1
    assert result["projection"]["projectable"] is False
    assert "monthly spend cap" in result["projection"]["why_not_projectable"]
    assert result["exit"] == 1
    assert "admin-settings" in pc.render(result, "root")


def test_a_session_limit_bounds_nothing_and_raises_nothing(tmp_path):
    """A few hours wide. It costs a run, never a week."""
    burn(tmp_path, CYCLE_START, hours=20, per_hour=40)
    refuse(tmp_path, CYCLE_START + timedelta(hours=5),
           "You've hit your session limit · resets 5am (UTC)")
    result = pc.assess(pc.cf.read_runs(tmp_path), CYCLE_START + timedelta(hours=21))
    assert result["live"]["session_refusals"] == 1
    assert result["live"]["verdict"] == "live"
    assert result["exit"] == 0


# --- the projection -------------------------------------------------------

def test_the_first_minutes_of_a_cycle_do_not_project(tmp_path):
    """Every seat the last cycle refused re-fires at once.

    Measured at 0.4 hours into the cycle of 2026-11-08 against the host's own
    archive, the average read 496 turns an hour and projected the pool gone
    107 hours early, which was false.
    """
    anchor(tmp_path, CYCLE_START - timedelta(days=7))
    burn(tmp_path, CYCLE_START - timedelta(days=7), hours=10, per_hour=400)
    refuse(tmp_path, CYCLE_START - timedelta(days=7) + timedelta(hours=10),
           WEEKLY_DATED)
    spend(tmp_path, CYCLE_START + timedelta(minutes=10), 200)

    result = pc.assess(pc.cf.read_runs(tmp_path),
                       CYCLE_START + timedelta(minutes=24))
    assert result["projection"]["projectable"] is False
    assert "elapsed" in result["projection"]["why_not_projectable"]
    assert result["exit"] == 0, "a herd at the top of the week is not an alarm"
    # The share is still answerable, because it needs no sample.
    assert result["projection"]["share_of_pool_low"] == pytest.approx(200 / 4000)


def test_a_rate_that_lasts_the_week_is_quiet(tmp_path):
    anchor(tmp_path, CYCLE_START - timedelta(days=7))
    burn(tmp_path, CYCLE_START - timedelta(days=7), hours=10, per_hour=400)
    refuse(tmp_path, CYCLE_START - timedelta(days=7) + timedelta(hours=10),
           WEEKLY_DATED)
    burn(tmp_path, CYCLE_START, hours=20, per_hour=20)

    result = pc.assess(pc.cf.read_runs(tmp_path), CYCLE_START + timedelta(hours=21))
    assert result["projection"]["certain"] is False
    assert result["exit"] == 0
    assert "reaches the reset" in pc.render(result, "root")


def test_a_rate_that_cannot_last_is_an_alarm_with_hours_to_spare(tmp_path):
    """The property the whole file exists for: red before the wall, not after.

    The pool here is 4,000 turns. Spending 400 an hour empties it ten hours
    in, and at three hours in the report is already red and names an instant
    inside an hour of the truth.
    """
    anchor(tmp_path, CYCLE_START - timedelta(days=7))
    burn(tmp_path, CYCLE_START - timedelta(days=7), hours=10, per_hour=400)
    refuse(tmp_path, CYCLE_START - timedelta(days=7) + timedelta(hours=10),
           WEEKLY_DATED)
    burn(tmp_path, CYCLE_START, hours=3, per_hour=400)

    now = CYCLE_START + timedelta(hours=3)
    result = pc.assess(pc.cf.read_runs(tmp_path), now)
    proj = result["projection"]
    assert proj["certain"] is True
    assert result["exit"] == 1

    empties = datetime.fromisoformat(proj["empties_at_latest"].replace("Z", "+00:00"))
    assert abs((empties - (CYCLE_START + timedelta(hours=10))).total_seconds()) < 3600
    assert empties > now, "an alarm about the past is a post-mortem"


def test_the_gate_fires_on_the_largest_pool_measured_not_the_smallest(tmp_path):
    """A spread has to be allowed to straddle the reset without crying wolf.

    Two prior cycles measure the pool at 4,000 and 8,000 turns. A rate that
    empties the smaller before the reset and the larger after it is a watch
    and not an alarm, because being red has to mean trouble rather than
    meaning the estimate was conservative.
    """
    anchor(tmp_path, CYCLE_START - timedelta(days=14))
    first = CYCLE_START - timedelta(days=14)
    burn(tmp_path, first, hours=10, per_hour=400)
    refuse(tmp_path, first + timedelta(hours=10), WEEKLY_DATED)
    second = CYCLE_START - timedelta(days=7)
    burn(tmp_path, second, hours=20, per_hour=400)
    refuse(tmp_path, second + timedelta(hours=20), WEEKLY_DATED)

    # 40 an hour over 168 hours is 6,720: past the 4,000 pool, short of 8,000.
    burn(tmp_path, CYCLE_START, hours=24, per_hour=40)
    result = pc.assess(pc.cf.read_runs(tmp_path), CYCLE_START + timedelta(hours=25))
    pool = result["pool"]
    assert (pool["low"], pool["high"]) == (4000, 8000)
    proj = result["projection"]
    assert proj["hours_short_soonest"] > 0, "the smaller pool runs out early"
    assert proj["hours_short_latest"] < 0, "the larger one reaches the reset"
    assert proj["certain"] is False
    assert result["exit"] == 0
    assert "watch" in pc.render(result, "root")


# --- the replay can only see the past -------------------------------------

def test_a_replay_cannot_see_its_own_future(tmp_path):
    """Without this filter `--now` reads the whole archive and dates it wrong.

    Asked about 2026-11-02T02:00Z, this reported 39,775 turns spent and 257
    monthly refusals that had not happened yet, and printed `dark for 0.0h`
    against a last-live stamp in its own future. A replay that sees the future
    cannot answer whether an alarm would have fired in time, which is the one
    question a new alarm has to answer.
    """
    burn(tmp_path, CYCLE_START, hours=3, per_hour=400)
    burn(tmp_path, CYCLE_START + timedelta(hours=4), hours=3, per_hour=400,
         seat_prefix="later")
    refuse(tmp_path, CYCLE_START + timedelta(hours=20), WEEKLY_DATED)

    early = pc.assess(pc.cf.read_runs(tmp_path), CYCLE_START + timedelta(hours=3))
    assert early["live"]["turns"] == 1200
    assert early["live"]["weekly_refusals"] == 0
    assert early["live"]["verdict"] == "live"

    late = pc.assess(pc.cf.read_runs(tmp_path), CYCLE_START + timedelta(hours=21))
    assert late["live"]["turns"] == 2400 + 1
    assert late["live"]["weekly_refusals"] == 1


# --- it refuses to answer where it cannot ---------------------------------

def test_a_checkout_with_no_log_root_is_not_a_failure(tmp_path):
    """A pull request checkout has no `/srv/asc/state`, and that is not a bug."""
    assert pc.main(["--root", str(tmp_path / "nothing")]) == 0


def test_the_json_and_the_exit_code_agree(tmp_path, capsys):
    anchor(tmp_path, CYCLE_START - timedelta(days=7))
    burn(tmp_path, CYCLE_START - timedelta(days=7), hours=10, per_hour=400)
    refuse(tmp_path, CYCLE_START - timedelta(days=7) + timedelta(hours=10),
           WEEKLY_DATED)
    burn(tmp_path, CYCLE_START, hours=3, per_hour=400)
    code = pc.main(["--root", str(tmp_path), "--json",
                    "--now", (CYCLE_START + timedelta(hours=3)).isoformat()])
    assert code == 1
    assert '"certain": true' in capsys.readouterr().out
