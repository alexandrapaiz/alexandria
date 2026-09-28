"""Guardrail 4's command, tested on the parts that decide something.

The network probes are not mocked into meaninglessness here. What is tested is
the judgement: given an artifact, does this tool call the surface delivering or
not, and does it ever call "I could not look" green. That last one is the whole
reason the file exists, so it gets the most cases.

Run with `python3 tests/test_delivery_health.py` or under pytest.
"""

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


def test_a_missing_credential_is_unknown_not_failing(monkeypatch=None):
    """No DATABASE_URL must never render the press as broken.

    Reporting a healthy press as broken is how a report teaches its reader to
    stop reading it, which is the failure guardrail 4 is trying to prevent, one
    level up.
    """
    old = dh.os.environ.pop("DATABASE_URL", None)
    try:
        results = dh.database_surfaces()
        check("both database surfaces answer", len(results) == 2)
        check("press is unknown, not failing",
              all(s.state == dh.UNKNOWN for s in results),
              str([s.state for s in results]))
        check("and the message names the variable",
              all("DATABASE_URL" in s.headline for s in results))
    finally:
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


def main() -> int:
    for fn in [
        test_unknown_is_never_green_and_never_red,
        test_a_missing_credential_is_unknown_not_failing,
        test_press_against_the_digests_table,
        test_incident_24_would_have_been_caught_in_one_call,
        test_weeks_between_counts_issues_not_days,
        test_pipeline_staleness,
        test_naive_timestamps_do_not_crash_the_comparison,
        test_the_week_rule_comes_from_the_press,
    ]:
        print(f"\n{fn.__name__}")
        fn()
    print(f"\n{len(FAILURES)} failing" if FAILURES else "\nall green")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
