"""The week an issue is labelled with is the week that actually ended.

2026-W38 is the reason this file exists. The press cron did not fire on
Monday 2026-09-21 (incident 24). The recovery run went out on Wednesday
2026-09-23, and `week_just_ended` answered "2026-W39" that day, because it
anchored on yesterday and yesterday was a Tuesday inside the in-progress
week. So the run whose whole job was to recover the missing week published
under the *next* week's label. W38 was never written by anything, and the
following Monday's scheduled run upserted over what the recovery had left
behind, because `digests` is keyed on week.

Two properties are worth pinning, and the second is the one that was broken:

1. Monday is unchanged. A fix to an off-schedule path that moves the
   scheduled path is not a fix, it is a second incident.
2. Every day of the week gives the same answer, and that answer is a week
   that has finished.

Run with `python3 tests/test_press_week_label.py` or under pytest.
"""

import sys
import types
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if "modal" not in sys.modules:  # see tests/conftest.py
    modal = types.ModuleType("modal")

    class _Image:
        def __getattr__(self, name):
            return lambda *a, **k: self

    modal.Cron = lambda *a, **k: None
    modal.Secret = types.SimpleNamespace(from_name=lambda *a, **k: None)
    modal.Volume = types.SimpleNamespace(from_name=lambda *a, **k: None)
    modal.Image = types.SimpleNamespace(debian_slim=lambda *a, **k: _Image())
    modal.App = lambda *a, **k: types.SimpleNamespace(
        function=lambda *a, **k: (lambda f: f),
        local_entrypoint=lambda *a, **k: (lambda f: f),
        cls=lambda *a, **k: (lambda c: c),
    )
    modal.asgi_app = lambda *a, **k: (lambda f: f)
    sys.modules["modal"] = modal

from pipeline.weekly import last_sunday, week_just_ended  # noqa: E402

FAILURES: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def test_monday_answer_is_unchanged():
    """The scheduled path keeps the answer it had before the fix.

    The old code was `date.today() - timedelta(days=1)`, which on a Monday is
    Sunday. This recomputes that literal expression for every Monday in a
    year and requires the new anchor to agree with it.
    """
    d = date(2026, 1, 5)  # a Monday
    while d < date(2027, 1, 4):
        check(f"monday {d} anchors on yesterday", last_sunday(d) == d - timedelta(days=1))
        d += timedelta(days=7)


def test_every_day_of_a_week_gives_that_week():
    """Monday 2026-09-28 through Sunday 2026-10-04 all report 2026-W39.

    W39 is the week 2026-09-21 to 2026-09-27, the last one that finished
    before any of those days. Under the old code this run of seven days
    produced two different labels and a silent handover on the Tuesday.
    """
    for offset in range(7):
        d = date(2026, 9, 28) + timedelta(days=offset)
        week, dates = week_just_ended(d)
        check(f"{d} ({d.strftime('%A')}) reports W39", week == "2026-W39", week)
        check(f"{d} reports the W39 date range",
              dates == "September 21–27, 2026", dates)


def test_the_recovery_run_that_lost_w38():
    """Wednesday 2026-09-23 now labels its issue 2026-W38, not 2026-W39.

    This is the regression itself, as a date. Nothing else in this file is
    the bug; this case is.
    """
    week, dates = week_just_ended(date(2026, 9, 23))
    check("the 2026-09-23 recovery run labels W38", week == "2026-W38", week)
    check("and carries W38's own date range",
          dates == "September 14–20, 2026", dates)


def test_label_and_range_always_describe_the_same_week():
    """The date range is always the Monday-to-Sunday of the label's own week.

    The old code derived the two from different anchors, so this property
    held on Mondays and nowhere else. Checked across a full year, every day.
    """
    d = date(2026, 1, 1)
    bad = []
    while d < date(2027, 1, 1):
        week, _ = week_just_ended(d)
        sunday = last_sunday(d)
        monday = sunday - timedelta(days=6)
        iso_year, iso_week, iso_day = monday.isocalendar()
        if iso_day != 1 or f"{iso_year}-W{iso_week:02d}" != week:
            bad.append(str(d))
        d += timedelta(days=1)
    check("365 days: the range's Monday is the label's Monday", not bad, str(bad[:5]))


def test_the_week_reported_has_finished():
    """The reported week's Sunday is always strictly in the past."""
    d = date(2026, 1, 1)
    bad = []
    while d < date(2027, 1, 1):
        if last_sunday(d) >= d:
            bad.append(str(d))
        d += timedelta(days=1)
    check("365 days: the week reported has already ended", not bad, str(bad[:5]))


def test_a_month_boundary_still_renders_both_months():
    """September 28 to October 4, 2026 is a real week and spans two months."""
    _, dates = week_just_ended(date(2026, 10, 6))
    check("cross-month range names both months",
          dates == "September 28 – October 4, 2026", dates)


def main() -> int:
    for fn in [
        test_monday_answer_is_unchanged,
        test_every_day_of_a_week_gives_that_week,
        test_the_recovery_run_that_lost_w38,
        test_label_and_range_always_describe_the_same_week,
        test_the_week_reported_has_finished,
        test_a_month_boundary_still_renders_both_months,
    ]:
        print(f"\n{fn.__name__}")
        fn()
    print(f"\n{len(FAILURES)} failing" if FAILURES else "\nall green")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
