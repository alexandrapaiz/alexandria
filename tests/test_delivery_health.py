"""Guardrail 4's command, tested on the parts that decide something.

The network probes are not mocked into meaninglessness here. What is tested is
the judgement: given an artifact, does this tool call the surface delivering or
not, and does it ever call "I could not look" green. That last one is the whole
reason the file exists, so it gets the most cases.

Run with `python3 tests/test_delivery_health.py` or under pytest.
"""

import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import delivery_health as dh  # noqa: E402

FAILURES: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


class FakeConn:
    """Answers each query with the first canned row whose key it contains."""

    def __init__(self, answers: dict[str, tuple | None]):
        self.answers = answers

    def execute(self, sql, params=None):
        for key, row in self.answers.items():
            if key in sql:
                return _Result(row)
        raise AssertionError(f"no canned answer for {sql!r}")


class _Result:
    def __init__(self, row):
        self.row = row

    def fetchone(self):
        return self.row


def test_unknown_is_never_green_and_never_red():
    """Exit 2 is its own state, and one unknown is enough to earn it."""
    results = [dh.Surface("site", dh.OK, ""), dh.Surface("press", dh.UNKNOWN, "")]
    check("one unknown among ok surfaces exits 2", dh.exit_code(results) == 2,
          str(dh.exit_code(results)))
    check("all ok exits 0", dh.exit_code([dh.Surface("site", dh.OK, "")]) == 0)
    check("one failing exits 1",
          dh.exit_code([dh.Surface("mcp", dh.FAILING, "")]) == 1)
    check("failing outranks unknown",
          dh.exit_code([dh.Surface("press", dh.UNKNOWN, ""),
                        dh.Surface("mcp", dh.FAILING, "")]) == 1)
    check("the unknown report does not read as green",
          "not a green report" in dh.render([dh.Surface("press", dh.UNKNOWN, "x")]))


def test_neither_reader_available_is_unknown_not_failing():
    """No credential and no receipt must never render the press as broken.

    Reporting a healthy press as broken is how a report teaches its reader to
    stop reading it, which is the failure guardrail 4 is trying to prevent, one
    level up.

    `dh.fetch` is stubbed to a dead site rather than left to the real one. This
    test used to pass against the live site because `/api/delivery` answered
    404, so the day that route deployed it would have started failing, and the
    failure would have looked like a regression in the thing it protects.
    """
    old = dh.os.environ.pop("DATABASE_URL", None)
    real_fetch = dh.fetch
    dh.fetch = lambda url, timeout=25: (0, "nothing is listening", {})
    try:
        results = dh.database_surfaces()
        check("every database surface answers",
              {s.name for s in results} == {"press", "pipeline", "deploy"},
              str(sorted(s.name for s in results)))
        check("press is unknown, not failing",
              all(s.state == dh.UNKNOWN for s in results),
              str([s.state for s in results]))
        check("and the message names the missing credential",
              all("DATABASE_URL" in s.headline for s in results))
        check("and the receipt it tried instead",
              all(dh.RECEIPT_URL in s.headline for s in results),
              results[0].headline)
    finally:
        dh.fetch = real_fetch
        if old is not None:
            dh.os.environ["DATABASE_URL"] = old


def test_press_against_the_digests_table():
    """A row for the week that ended is ok; an older newest row is failing."""
    now = datetime.now(timezone.utc)
    conn = FakeConn({"from digests": ("2026-W39", now, "kimi-k2")})
    s = dh.check_press(conn, dh.date(2026, 9, 28))
    check("W39 present on 2026-09-28 is ok", s.state == dh.OK, s.headline)

    conn = FakeConn({"from digests": ("2026-W37", now, "kimi-k2")})
    s = dh.check_press(conn, dh.date(2026, 9, 28))
    check("W37 as the newest row on 2026-09-28 is failing", s.state == dh.FAILING)
    check("and it counts the missing issues", "2 issue(s) missing" in s.headline,
          s.headline)

    conn = FakeConn({"from digests": None})
    s = dh.check_press(conn, dh.date(2026, 9, 28))
    check("an empty digests table is failing", s.state == dh.FAILING, s.headline)


def test_incident_24_would_have_been_caught_in_one_call():
    """2026-09-23, newest row 2026-W37, week that ended 2026-W38.

    The owner found this from her own inbox three days late. This is the same
    question asked of the artifact instead of the scheduler.
    """
    conn = FakeConn({"from digests": ("2026-W37", datetime(2026, 9, 14, tzinfo=timezone.utc),
                                      "groq/compound")})
    s = dh.check_press(conn, dh.date(2026, 9, 23))
    check("incident 24 reads as failing", s.state == dh.FAILING, s.headline)
    check("naming W38 as the week that was missed",
          s.evidence["expected"] == "2026-W38", s.evidence["expected"])


def test_weeks_between_counts_issues_not_days():
    check("W37 to W39 is two issues", dh._weeks_between("2026-W37", "2026-W39") == 2)
    check("same week is zero", dh._weeks_between("2026-W39", "2026-W39") == 0)
    check("never negative", dh._weeks_between("2026-W40", "2026-W39") == 0)
    check("across a year boundary",
          dh._weeks_between("2025-W52", "2026-W02") == 2,
          str(dh._weeks_between("2025-W52", "2026-W02")))


def test_pipeline_staleness():
    now = datetime.now(timezone.utc)
    fresh = FakeConn({"from papers": (now - timedelta(hours=6),),
                      "from claims": (now - timedelta(hours=5),)})
    check("a corpus that moved today is ok",
          dh.check_pipeline(fresh).state == dh.OK)

    stale = FakeConn({"from papers": (now - timedelta(days=5),),
                      "from claims": (now - timedelta(hours=5),)})
    s = dh.check_pipeline(stale)
    check("ingest stopped five days ago is failing", s.state == dh.FAILING, s.headline)
    check("and the headline names which table", "papers" in s.headline, s.headline)

    empty = FakeConn({"from papers": (None,), "from claims": (None,)})
    check("empty corpus tables are failing",
          dh.check_pipeline(empty).state == dh.FAILING)


def test_naive_timestamps_do_not_crash_the_comparison():
    """Postgres columns declared without a time zone come back naive.

    A TypeError here would take out the whole check, so the tool assumes UTC
    rather than refusing to answer.
    """
    naive = datetime.utcnow() - timedelta(hours=2)
    conn = FakeConn({"from papers": (naive,), "from claims": (naive,)})
    check("a naive timestamp is read as UTC",
          dh.check_pipeline(conn).state == dh.OK)


def test_the_week_rule_comes_from_the_press():
    """Not a second copy of it. Same answer as pipeline.weekly, by construction."""
    from pipeline.weekly import week_just_ended

    for d in [dh.date(2026, 9, 28), dh.date(2026, 9, 23), dh.date(2026, 10, 4)]:
        check(f"{d} agrees with the press",
              dh.week_label(d) == week_just_ended(d)[0])


def _press(week, state=None):
    return dh.Surface("press", state or dh.OK, f"{week} is written",
                      {"newest_week": week})


def _site(weeks, state=None):
    return dh.Surface("site", state or dh.OK, f"newest {weeks[0] if weeks else 'none'}",
                      {"published": list(weeks)})


def test_the_archive_surface_catches_a_dead_record_path():
    """The one state this surface exists for.

    site/lib/issues-live.js falls back to the committed markdown when it cannot
    read `digests`, which is the right way to fail and is why the failure is
    invisible: every other surface here stays green while the record path is
    dead. The comparison is the only thing that sees it. L-A16.
    """
    s = dh.judge_archive(_press("2026-W41"), _site(["2026-W39"]), hidden=set())
    check("a record ahead of the page is failing", s.state == dh.FAILING, s.headline)
    check("and it names both weeks",
          "2026-W41" in s.headline and "2026-W39" in s.headline, s.headline)
    check("and it names the likely cause",
          "cannot read the database" in s.headline, s.headline)

    s = dh.judge_archive(_press("2026-W40"), _site(["2026-W40", "2026-W39"]),
                         hidden=set())
    check("agreement is green", s.state == dh.OK, s.headline)
    check("and says what agreed", "2026-W40" in s.headline, s.headline)


def test_the_owners_veto_is_not_a_failure():
    hidden = {"2026-W37"}
    s = dh.judge_archive(_press("2026-W37"), _site(["2026-W37"]), hidden=hidden)
    check("a hidden newest record is deliberate, not broken", s.state == dh.OK,
          s.headline)

    # The hidden week is filtered out of the published list before the
    # comparison, so a site that still lists it cannot make the two agree by
    # accident.
    s = dh.judge_archive(_press("2026-W40"), _site(["2026-W37"]), hidden=hidden)
    check("a page publishing only a hidden week is not agreement",
          s.state == dh.FAILING, s.headline)


def test_a_hand_published_week_ahead_of_the_record_is_not_a_failure():
    s = dh.judge_archive(_press("2026-W39"), _site(["2026-W40", "2026-W39"]),
                         hidden=set())
    check("the old path still working is green", s.state == dh.OK, s.headline)
    check("and it says which week the record lacks", "2026-W40" in s.headline,
          s.headline)


def test_an_unreadable_surface_is_unknown_and_never_a_verdict():
    s = dh.judge_archive(None, _site(["2026-W39"]), hidden=set())
    check("no press surface is unknown", s.state == dh.UNKNOWN, s.headline)

    s = dh.judge_archive(
        dh.Surface("press", dh.UNKNOWN, "no credential"), _site(["2026-W39"]),
        hidden=set())
    check("an unknown press makes the comparison unknown",
          s.state == dh.UNKNOWN, s.headline)
    check("and it says which surface could not be read",
          "press" in s.headline, s.headline)

    s = dh.judge_archive(_press("2026-W39"),
                         dh.Surface("site", dh.UNKNOWN, "no answer"), hidden=set())
    check("an unknown site makes the comparison unknown",
          s.state == dh.UNKNOWN, s.headline)

    s = dh.judge_archive(_press("2026-W40"), _site([]), hidden=set())
    check("a record with an empty archive is failing, not unknown",
          s.state == dh.FAILING, s.headline)


def test_hidden_weeks_is_read_from_the_site_and_not_copied():
    weeks = dh.hidden_weeks()
    check("2026-W37 is read out of site/lib/content.js", "2026-W37" in weeks,
          str(weeks))
    content = (Path(__file__).resolve().parents[1]
               / "site" / "lib" / "content.js").read_text()
    check("and that is where the set lives", "HIDDEN_WEEKS = new Set" in content)

    missing = dh.hidden_weeks(Path("/nonexistent"))
    check("an unreadable file yields an empty set, which can only add noise",
          missing == set(), str(missing))


def test_asking_for_the_archive_alone_fetches_what_it_needs():
    """`--surface archive` must not report 'needs both surfaces' forever."""
    source = (Path(__file__).resolve().parents[1]
              / "tools" / "delivery_health.py").read_text()
    check("run() widens the fetch for archive",
          '{"press", "site"} if "archive" in asked' in source)
    check("and narrows the report back to what was asked",
          "if s.name in asked" in source)
    check("archive sits between site and mcp in the printed order",
          dh.ORDER.index("site") < dh.ORDER.index("archive") < dh.ORDER.index("mcp"),
          str(dh.ORDER))


# --- the press's deadline, not just its week (2026-10-08) ---------------------
#
# 2026-10-05 is a Monday and the week that ended the day before is 2026-W40, so
# every case below stands on the cron's own day, which is the only day the two
# rules disagree.

def _digests(week):
    return FakeConn({"from digests": (week, datetime(2026, 10, 5, 9, 1,
                                                     tzinfo=timezone.utc),
                                      "kimi-k2")})


def test_the_monday_morning_window_is_the_schedule_and_not_a_fault():
    """Nine hours a week, this surface called a working press a missing issue.

    The cron is `0 9 * * 1`. At 03:00 on a Monday the week that ended on Sunday
    has no row yet, correctly, and the old rule compared the newest row against
    that week and reported an issue missing. Sprint 2026-10-05's item 4 named
    it: the press surface "reads FAILING on any Monday before the cron fires".
    """
    before = datetime(2026, 10, 5, 3, 0, tzinfo=timezone.utc)
    s = dh.check_press(_digests("2026-W39"), before)
    check("W39 at 03:00 on the cron's own Monday is ok", s.state == dh.OK,
          s.headline)
    check("and the headline names the issue it is waiting for and by when",
          "2026-W40" in s.headline and "not due" in s.headline, s.headline)
    check("and the evidence keeps the week that ended apart from the week owed",
          (s.evidence["expected"], s.evidence["due"], s.evidence["pending"])
          == ("2026-W40", "2026-W39", "2026-W40"), str(s.evidence))


def test_the_grace_covers_a_run_in_progress_and_then_expires():
    """The press takes minutes, not an instant, so 09:00 sharp is too early to
    call it late. Two hours later is not."""
    s = dh.check_press(_digests("2026-W39"),
                       datetime(2026, 10, 5, 9, 30, tzinfo=timezone.utc))
    check("a run still going at 09:30 is not a missing issue",
          s.state == dh.OK, s.headline)

    s = dh.check_press(_digests("2026-W39"),
                       datetime(2026, 10, 5, 11, 30, tzinfo=timezone.utc))
    check("the same row at 11:30 is failing", s.state == dh.FAILING, s.headline)
    check("and it counts exactly one issue missing",
          "1 issue(s) missing" in s.headline, s.headline)


def test_the_window_does_not_blind_the_check_to_a_real_backlog():
    """The one way this fix could be wrong is a window that forgives
    everything. Two weeks behind is still two weeks behind at 03:00."""
    before = datetime(2026, 10, 5, 3, 0, tzinfo=timezone.utc)

    s = dh.check_press(_digests("2026-W38"), before)
    check("W38 inside the window is still failing", s.state == dh.FAILING,
          s.headline)
    check("against the week that is actually due, W39",
          "2026-W39" in s.headline, s.headline)

    s = dh.check_press(FakeConn({"from digests": None}), before)
    check("and an empty digests table is failing inside the window too",
          s.state == dh.FAILING, s.headline)


def test_the_deadline_is_the_monday_after_the_week_it_judges():
    d = dh.press_deadline(dh.date(2026, 10, 4))  # a Sunday
    check("the week ending Sunday 10-04 is due on Monday 10-05",
          (d.year, d.month, d.day) == (2026, 10, 5), str(d))
    check("at the cron's own hour plus the grace",
          d.hour == int(dh.PRESS_CRON.split()[1]) + dh.PRESS_GRACE.seconds // 3600,
          str(d))


def test_the_cron_this_check_assumes_is_the_cron_the_press_runs():
    """`PRESS_GRACE` is a judgement. `PRESS_CRON` is a copy, so it is pinned.

    `week_label` goes to the press for the week rule rather than keeping its
    own, which is this file's standing argument. The schedule cannot be read
    the same way: it lives in a decorator argument that the Modal stub throws
    away. So it is pinned here instead, and this test is what sends a reader
    back to `tools/delivery_health.py` when the press's schedule moves.
    """
    source = (Path(__file__).resolve().parents[1] / "pipeline" / "weekly.py").read_text()
    crons = re.findall(r'modal\.Cron\(\s*"([^"]+)"\s*\)', source)
    check("pipeline/weekly.py declares exactly one cron", len(crons) == 1,
          str(crons))
    check(f"and it is the one this check assumes ({dh.PRESS_CRON})",
          crons == [dh.PRESS_CRON], str(crons))


def test_a_bare_date_still_asks_about_a_day_that_is_over():
    """Every caller written before the deadline rule passes a date, and they
    all mean a day that has finished. Midnight would change their question."""
    check("a bare date is the end of that day",
          dh._instant(dh.date(2026, 10, 5)).hour == 23,
          str(dh._instant(dh.date(2026, 10, 5))))
    check("a naive datetime is read as UTC",
          dh._instant(datetime(2026, 10, 5, 3, 0)).tzinfo == timezone.utc)
    check("an aware one is left exactly as it came",
          dh._instant(datetime(2026, 10, 5, 3, 0, tzinfo=timezone.utc)).hour == 3)
    check("--today still takes a day",
          dh.parse_moment("2026-10-05") == dh.date(2026, 10, 5))
    check("and now an instant inside one",
          dh.parse_moment("2026-10-05T03:00:00Z")
          == datetime(2026, 10, 5, 3, 0, tzinfo=timezone.utc))
    check("and nothing stays nothing", dh.parse_moment(None) is None)


def test_the_site_surface_reads_the_same_deadline():
    """It judged the archive against the week that ended too, so it cried wolf
    on exactly the Mondays the press surface did."""
    real_fetch = dh.fetch
    dh.fetch = lambda url, timeout=25: (200, "2026-W39 2026-W38", {})
    try:
        s = dh.check_site(datetime(2026, 10, 5, 3, 0, tzinfo=timezone.utc))
        check("W39 newest at 03:00 on the cron's Monday is ok",
              s.state == dh.OK, s.headline)
        check("and failing once the deadline has passed",
              dh.check_site(datetime(2026, 10, 5, 11, 30,
                                     tzinfo=timezone.utc)).state == dh.FAILING)
    finally:
        dh.fetch = real_fetch


def main() -> int:
    for fn in [
        test_unknown_is_never_green_and_never_red,
        test_neither_reader_available_is_unknown_not_failing,
        test_press_against_the_digests_table,
        test_incident_24_would_have_been_caught_in_one_call,
        test_weeks_between_counts_issues_not_days,
        test_pipeline_staleness,
        test_naive_timestamps_do_not_crash_the_comparison,
        test_the_week_rule_comes_from_the_press,
        test_the_archive_surface_catches_a_dead_record_path,
        test_the_owners_veto_is_not_a_failure,
        test_a_hand_published_week_ahead_of_the_record_is_not_a_failure,
        test_an_unreadable_surface_is_unknown_and_never_a_verdict,
        test_hidden_weeks_is_read_from_the_site_and_not_copied,
        test_asking_for_the_archive_alone_fetches_what_it_needs,
        test_the_monday_morning_window_is_the_schedule_and_not_a_fault,
        test_the_grace_covers_a_run_in_progress_and_then_expires,
        test_the_window_does_not_blind_the_check_to_a_real_backlog,
        test_the_deadline_is_the_monday_after_the_week_it_judges,
        test_the_cron_this_check_assumes_is_the_cron_the_press_runs,
        test_a_bare_date_still_asks_about_a_day_that_is_over,
        test_the_site_surface_reads_the_same_deadline,
    ]:
        print(f"\n{fn.__name__}")
        fn()
    print(f"\n{len(FAILURES)} failing" if FAILURES else "\nall green")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
