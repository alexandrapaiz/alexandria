"""Does the slot reader tell a collision from a clear minute, and a clear
minute from one it never observed.

Run with `python3 -m pytest tests/test_slot_collision.py -q`.

`tools/slot_collision.py` reads the host's own audit log and the deployed
roster, and neither is present on a pull request checkout, so every test here
builds both in a temporary directory in the host's exact format. Nothing
touches `/srv/asc`.

The state worth asserting out loud is `unobserved`. A declared slot with no
occurrence inside its seat's own record is the shape of a clock that moved last
night, and this organization has read a zero over a denominator of zero as
health four separate times. So that case fails rather than printing clear, and
`test_unobserved_slot_fails` is the line that holds it.

The second is `narrow`. It is a prediction and not an observation, so it must
not fail the exit on its own: a slot that cleared every occurrence by two
minutes is a real warning about a slot that is nonetheless, so far, never once
been lost. `test_narrow_does_not_fail_the_exit` holds that boundary.
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import slot_collision as sc  # noqa: E402


def row(ts, agent, action, **kw):
    d = {"ts": ts, "agent": agent, "action": action}
    d.update(kw)
    return json.dumps(d)


def write_audit(tmp_path, lines):
    p = tmp_path / "audit.jsonl"
    p.write_text("\n".join(lines) + "\n")
    return str(p)


def run_of(agent, start, minutes, trigger="message"):
    """The host records the end and the duration, so a run is written that way."""
    s = datetime.fromisoformat(start.replace("Z", "+00:00"))
    e = s + timedelta(minutes=minutes)
    return row(e.isoformat().replace("+00:00", "Z"), agent, "run.end",
               trigger=trigger, durationMs=minutes * 60 * 1000, exit=0)


def write_roster(tmp_path, company, seat, name, cron):
    d = tmp_path / "roster" / company / seat
    d.mkdir(parents=True)
    (d / "agent.toml").write_text(
        '[agent]\nname = "%s"\n\n[trigger]\ncron = "%s"   # a comment the reader ignores\n'
        'webhook = true\n' % (name, cron))
    return str(tmp_path / "roster")


# ------------------------------------------------------------------ cron field

def test_five_fields_or_nothing():
    with pytest.raises(sc.CronError):
        sc.Slot("0 1 * *")
    with pytest.raises(sc.CronError):
        sc.Slot("0 1 * * 1 7")


def test_field_forms():
    s = sc.Slot("0,30 1-3 * * *")
    assert s.minutes == {0, 30}
    assert s.hours == {1, 2, 3}
    assert sc.Slot("*/15 * * * *").minutes == {0, 15, 30, 45}


def test_sunday_is_both_zero_and_seven():
    assert sc.Slot("0 1 * * 0").dow == sc.Slot("0 1 * * 7").dow == {0}


def test_monday_occurrences_are_mondays():
    w = (datetime(2026, 11, 1, tzinfo=timezone.utc),
         datetime(2026, 11, 30, 23, 59, tzinfo=timezone.utc))
    occ = sc.Slot("0 1 * * 1").occurrences(*w)
    assert [t.day for t in occ] == [2, 9, 16, 23, 30]
    assert all(t.hour == 1 and t.minute == 0 for t in occ)


def test_an_occurrence_past_the_window_is_not_counted():
    """The window's last day is not the same as its last minute: a slot at
    01:00 on the closing day is outside a window that closed at midnight, and
    counting it would put an unobservable minute in the denominator."""
    w = (datetime(2026, 11, 1, tzinfo=timezone.utc), datetime(2026, 11, 30, tzinfo=timezone.utc))
    assert [t.day for t in sc.Slot("0 1 * * 1").occurrences(*w)] == [2, 9, 16, 23]


def test_dom_and_dow_both_restricted_is_an_or():
    """cron's own rule, and a reader that ANDs them silently loses slots."""
    w = (datetime(2026, 11, 1, tzinfo=timezone.utc), datetime(2026, 11, 8, tzinfo=timezone.utc))
    occ = sc.Slot("0 1 3 * 1").occurrences(*w)
    assert [t.day for t in occ] == [2, 3]


def test_a_field_outside_its_range_is_refused():
    with pytest.raises(sc.CronError):
        sc.Slot("0 25 * * *")


# ----------------------------------------------------------------- the verdicts

def test_a_slot_inside_a_live_run_collides(tmp_path):
    a = "co-seat"
    audit = write_audit(tmp_path, [
        row("2026-11-01T00:00:00.000Z", a, "run.start", trigger="message"),
        run_of(a, "2026-11-02T00:49:00Z", 26),      # straddles 01:00Z
        run_of(a, "2026-11-09T00:49:00Z", 21),
    ])
    rc = sc.main(["--audit", audit, "--seat", a, "--slot", "0 1 * * 1",
                  "--now", "2026-11-09T12:00:00Z", "--json"])
    assert rc == 1


def test_a_clear_slot_passes(tmp_path):
    a = "co-seat"
    audit = write_audit(tmp_path, [
        row("2026-11-01T00:00:00.000Z", a, "run.start", trigger="message"),
        run_of(a, "2026-11-02T00:49:00Z", 26),
        run_of(a, "2026-11-09T00:49:00Z", 21),
    ])
    rc = sc.main(["--audit", audit, "--seat", a, "--slot", "0 13 * * 1",
                  "--now", "2026-11-09T23:00:00Z", "--json"])
    assert rc == 0


def test_narrow_does_not_fail_the_exit(tmp_path):
    """Two minutes of clearance is a warning about the future, not a loss."""
    a = "co-seat"
    audit = write_audit(tmp_path, [
        row("2026-11-01T00:00:00.000Z", a, "run.start", trigger="message"),
        run_of(a, "2026-11-02T01:02:00Z", 20),
        run_of(a, "2026-11-09T01:02:00Z", 20),
    ])
    runs, first, last = sc.read_runs(audit, datetime(2026, 11, 9, 23, tzinfo=timezone.utc))
    out = sc.judge_slot("0 1 * * 1", a, runs,
                        (first[a], last[a]), sc.DEFAULT_MARGIN_MIN)
    assert out["verdict"] == "narrow"
    assert out["collided"] == 0 and out["narrow"] == 2
    assert out["min_margin_min"] == pytest.approx(2.0)
    rc = sc.main(["--audit", audit, "--seat", a, "--slot", "0 1 * * 1",
                  "--now", "2026-11-09T23:00:00Z", "--json"])
    assert rc == 0


def test_margin_governs_the_narrow_boundary(tmp_path):
    a = "co-seat"
    audit = write_audit(tmp_path, [
        row("2026-11-01T00:00:00.000Z", a, "run.start", trigger="message"),
        run_of(a, "2026-11-02T01:10:00Z", 20),
    ])
    runs, first, last = sc.read_runs(audit, datetime(2026, 11, 3, tzinfo=timezone.utc))
    w = (first[a], last[a])
    assert sc.judge_slot("0 1 * * 1", a, runs, w, 5)["verdict"] == "clear"
    assert sc.judge_slot("0 1 * * 1", a, runs, w, 15)["verdict"] == "narrow"


def test_unobserved_slot_fails(tmp_path):
    """A clock whose slot has never come due inside the record is unread, and
    an unread slot must not print as a clear one."""
    a = "co-seat"
    audit = write_audit(tmp_path, [
        row("2026-11-02T00:00:00.000Z", a, "run.start", trigger="message"),
        run_of(a, "2026-11-02T00:10:00Z", 5),
    ])
    runs, first, last = sc.read_runs(audit, datetime(2026, 11, 2, 1, tzinfo=timezone.utc))
    out = sc.judge_slot("0 1 * * 4", a, runs, (first[a], last[a]), 5)
    assert out["verdict"] == "unobserved" and out["occurrences"] == 0
    rc = sc.main(["--audit", audit, "--seat", a, "--slot", "0 1 * * 4",
                  "--now", "2026-11-02T01:00:00Z", "--json"])
    assert rc == 1


def test_the_window_is_the_seats_own_record(tmp_path):
    """A slot that came due before the seat's first row is not a clear slot.

    The audit log starts when the host started writing it; a seat's rows start
    when that seat first ran. Reading occurrences over the file's span instead
    of the seat's would score every pre-existence Monday as clear and turn one
    collision into one of six.
    """
    a, other = "co-seat", "co-other"
    audit = write_audit(tmp_path, [
        row("2026-10-01T00:00:00.000Z", other, "run.start", trigger="message"),
        run_of(other, "2026-10-01T00:00:00Z", 5),
        row("2026-11-09T00:30:00.000Z", a, "run.start", trigger="message"),
        run_of(a, "2026-11-09T00:49:00Z", 21),
    ])
    runs, first, last = sc.read_runs(audit, datetime(2026, 11, 9, 12, tzinfo=timezone.utc))
    out = sc.judge_slot("0 1 * * 1", a, runs, (first[a], last[a]), 5)
    assert out["occurrences"] == 1 and out["collided"] == 1


def test_a_live_run_is_held_open_to_now(tmp_path):
    """The asking run is itself a run, and leaving it out reports its own
    minute as free."""
    a = "co-seat"
    audit = write_audit(tmp_path, [
        run_of(a, "2026-11-09T00:10:00Z", 5),
        row("2026-11-09T00:50:00.000Z", a, "run.start", trigger="message"),
    ])
    runs, _, _ = sc.read_runs(audit, datetime(2026, 11, 9, 1, 30, tzinfo=timezone.utc))
    assert any(s <= datetime(2026, 11, 9, 1, 0, tzinfo=timezone.utc) <= e for s, e, _t in runs[a])


# ------------------------------------------------------------------ the roster

def test_declared_slots_read_the_agent_name_not_the_path(tmp_path):
    roster = write_roster(tmp_path, "alexandria", "exo", "alexandria-exo", "0 1 * * 1")
    assert sc.declared_slots(roster) == [("alexandria-exo", "0 1 * * 1",
                                          str(Path(roster) / "alexandria" / "exo" / "agent.toml"))]


def test_a_seat_with_no_cron_is_not_a_finding(tmp_path):
    d = tmp_path / "roster" / "alexandria" / "pm"
    d.mkdir(parents=True)
    (d / "agent.toml").write_text('[agent]\nname = "alexandria-pm"\n\n[trigger]\nwebhook = true\n')
    assert sc.declared_slots(str(tmp_path / "roster")) == []


def test_an_empty_cron_string_is_not_a_slot(tmp_path):
    roster = write_roster(tmp_path, "alexandria", "exo", "alexandria-exo", "")
    assert sc.declared_slots(roster) == []


def test_declared_mode_reads_the_roster(tmp_path):
    a = "alexandria-exo"
    roster = write_roster(tmp_path, "alexandria", "exo", a, "0 1 * * 1")
    audit = write_audit(tmp_path, [
        row("2026-11-01T00:00:00.000Z", a, "run.start", trigger="message"),
        run_of(a, "2026-11-02T00:49:00Z", 26),
    ])
    rc = sc.main(["--audit", audit, "--roster", roster, "--now", "2026-11-02T12:00:00Z", "--json"])
    assert rc == 1


def test_an_unreadable_cron_line_is_a_finding_not_a_crash(tmp_path):
    a = "alexandria-exo"
    roster = write_roster(tmp_path, "alexandria", "exo", a, "every monday at one")
    audit = write_audit(tmp_path, [run_of(a, "2026-11-02T00:49:00Z", 26)])
    rc = sc.main(["--audit", audit, "--roster", roster, "--now", "2026-11-02T12:00:00Z", "--json"])
    assert rc == 1


def test_a_missing_audit_log_says_so_rather_than_printing_clear(tmp_path):
    rc = sc.main(["--audit", str(tmp_path / "nothing.jsonl"), "--seat", "co-seat",
                  "--slot", "0 1 * * 1"])
    assert rc == 2


def test_sweep_ranks_the_clear_hours_first(tmp_path):
    a = "co-seat"
    audit = write_audit(tmp_path, [
        row("2026-11-02T00:00:00.000Z", a, "run.start", trigger="message"),
        run_of(a, "2026-11-02T00:49:00Z", 26),
        run_of(a, "2026-11-09T00:49:00Z", 21),
    ])
    runs, first, last = sc.read_runs(audit, datetime(2026, 11, 9, 12, tzinfo=timezone.utc))
    rows = sc.sweep(a, runs, (first[a], last[a]), 5, 0)
    assert rows[0]["collided"] == 0
    mon1 = next(r for r in rows if r["slot"] == "0 1 * * 1")
    assert mon1["collided"] == 2
    assert rows.index(mon1) > 0


def test_a_bad_now_is_refused(tmp_path):
    audit = write_audit(tmp_path, [run_of("co-seat", "2026-11-02T00:49:00Z", 5)])
    assert sc.main(["--audit", audit, "--seat", "co-seat", "--slot", "0 1 * * 1",
                    "--now", "monday"]) == 2


def test_the_slots_own_run_is_not_a_near_miss(tmp_path):
    """A slot that is received starts a run seconds later, so that run's own
    start is the nearest boundary to every healthy slot in the fleet. Counting
    it reported twelve of twelve clear slots as `narrow` with a sub-minute
    margin, which is an artifact and not twelve coincidences."""
    a = "co-seat"
    audit = write_audit(tmp_path, [
        row("2026-11-01T00:00:00.000Z", a, "run.start", trigger="message"),
        run_of(a, "2026-11-02T01:00:11Z", 14, trigger="cron"),
        run_of(a, "2026-11-09T01:00:06Z", 12, trigger="cron"),
    ])
    runs, first, last = sc.read_runs(audit, datetime(2026, 11, 9, 12, tzinfo=timezone.utc))
    out = sc.judge_slot("0 1 * * 1", a, runs, (first[a], last[a]), sc.DEFAULT_MARGIN_MIN)
    assert out["verdict"] == "clear", out
    assert out["narrow"] == 0


def test_a_message_run_just_after_the_slot_is_still_a_near_miss(tmp_path):
    """The exclusion is narrow on purpose: it covers the slot's own delivery,
    which carries `trigger: cron`, and nothing else."""
    a = "co-seat"
    audit = write_audit(tmp_path, [
        row("2026-11-01T00:00:00.000Z", a, "run.start", trigger="message"),
        run_of(a, "2026-11-02T01:00:30Z", 14, trigger="message"),
    ])
    runs, first, last = sc.read_runs(audit, datetime(2026, 11, 2, 12, tzinfo=timezone.utc))
    out = sc.judge_slot("0 1 * * 1", a, runs, (first[a], last[a]), sc.DEFAULT_MARGIN_MIN)
    assert out["verdict"] == "narrow"


def test_a_cron_run_long_after_the_slot_is_not_excluded(tmp_path):
    """The grace is one minute, so a cron run two minutes later is some other
    slot's delivery and is measured like any other run."""
    a = "co-seat"
    audit = write_audit(tmp_path, [
        row("2026-11-01T00:00:00.000Z", a, "run.start", trigger="message"),
        run_of(a, "2026-11-02T01:02:00Z", 14, trigger="cron"),
    ])
    runs, first, last = sc.read_runs(audit, datetime(2026, 11, 2, 12, tzinfo=timezone.utc))
    out = sc.judge_slot("0 1 * * 1", a, runs, (first[a], last[a]), sc.DEFAULT_MARGIN_MIN)
    assert out["verdict"] == "narrow" and out["min_margin_min"] == pytest.approx(2.0)
