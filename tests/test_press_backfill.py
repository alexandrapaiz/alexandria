"""The press can be asked for a week by name, and a rewrite mails nobody.

The ledger has asked since 2026-09-17 for "institution backfill, then
regenerate and resend the digest". The second verb had no implementation. On
2026-10-26 that was measured rather than assumed: `pipeline/weekly.py::resend`
sends a body that is already stored, so it would re-send whatever the empty
`institutions` column produced, and `weekly()` took no arguments and got its
week from `week_just_ended()`, which reads the calendar. There was no way to
ask this pipeline for a week that had passed.

`week_just_ended`'s own docstring names the consequence: "A press whose week
label depends on the day someone happens to run it cannot be backfilled."

Four properties are pinned here, and the last two are the ones that cost
something if they break.

1. `week_from_label` is the exact inverse of `week_just_ended`, and it refuses
   a label that is not one, a week the ISO year does not have, and a week that
   has not finished. The third refusal is the 2026-W38 incident pointed the
   other way: an issue written for an in-progress week is upserted over by
   that week's own Monday cron.
2. `week_window` is the span the Monday cron would have read, so a regenerated
   issue reports the week on its own masthead rather than the week the
   operator happens to be standing in.
3. Every time-filtered query in `gather` is bounded at both ends and is
   handed the window. An upper bound is what stops a backfilled issue from
   reporting claims distilled after the week it is labelled with.
4. A named-week run writes the row and sends no email. Readers may already
   hold the issue it replaces, and `resend` is the second, deliberate verb.

Run with `python3 tests/test_press_backfill.py` or under pytest.
"""

import re
import sys
import types
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

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

from pipeline import weekly as w  # noqa: E402

SOURCE = (ROOT / "pipeline" / "weekly.py").read_text()

FAILURES: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


def refuses(label: str, fragment: str, today=date(2026, 10, 26)) -> None:
    try:
        w.week_from_label(label, today)
    except ValueError as exc:
        check(f"{label!r} is refused, saying why", fragment in str(exc), str(exc))
    else:
        check(f"{label!r} is refused", False, "it was accepted")


# ---------------------------------------------------------------- 1. the label


def test_the_cron_hour_is_the_crons_own_hour():
    """One number in three places, and this is the only one that is a number.

    `week_window` has to reconstruct the span a scheduled run would have read,
    and the schedule is the only place that span is written down. A constant
    that drifts from the decorator above it would make every backfill read a
    window the cron never read, silently, and the issue would still look
    right.
    """
    print("the cron hour")
    hours = [int(m) for m in re.findall(r'modal\.Cron\("0 (\d+) \* \* 1"\)', SOURCE)]
    check("the module declares exactly one weekly cron", len(hours) == 1, f"{hours}")
    check("PRESS_CRON_HOUR is that cron's hour",
          hours and w.PRESS_CRON_HOUR == hours[0], f"{w.PRESS_CRON_HOUR} vs {hours}")
    health = (ROOT / "tools" / "delivery_health.py").read_text()
    watched = re.search(r'^PRESS_CRON = "(.+)"', health, re.M)
    check("tools/delivery_health.py still pins the press's cron", watched is not None)
    if watched:
        check("and it agrees with this module's hour",
              int(watched.group(1).split()[1]) == w.PRESS_CRON_HOUR,
              f"{watched.group(1)} vs {w.PRESS_CRON_HOUR}")


def test_week_from_label_is_the_inverse_of_week_just_ended():
    """Every day of 2026: name the week the calendar gives and get it back.

    The two functions answer the same question from different inputs, so the
    only thing that makes a backfill trustworthy is that they never disagree.
    Both halves are checked, the label and the reader-facing range, because the
    range is what the issue prints.
    """
    print("the inverse")
    d = date(2026, 1, 8)
    bad = []
    while d < date(2027, 1, 1):
        week, dates = w.week_just_ended(d)
        again = w.week_from_label(week, d)
        if again != (week, dates):
            bad.append(f"{d}: {again} != {(week, dates)}")
        d += timedelta(days=1)
    check("358 days: naming the week returns the calendar's own answer",
          not bad, str(bad[:3]))


def test_the_w38_recovery_week_can_now_be_asked_for_by_name():
    """2026-W38 is the week this whole file is about. Ask for it directly."""
    print("W38 by name")
    week, dates = w.week_from_label("2026-W38", date(2026, 10, 26))
    check("the label comes back unchanged", week == "2026-W38", week)
    check("with W38's own date range", dates == "September 14–20, 2026", dates)


def test_a_cross_month_week_renders_both_months():
    print("a cross-month week")
    _, dates = w.week_from_label("2026-W40", date(2026, 10, 26))
    check("W40 names both months", dates == "September 28 – October 4, 2026", dates)


def test_the_three_refusals():
    """A backfill that writes the wrong week is worse than one that stops."""
    print("the refusals")
    refuses("W38", "not an ISO week label")
    refuses("2026-38", "not an ISO week label")
    refuses("", "not an ISO week label")
    refuses("2026-W99", "not a week 2026 has")
    refuses("2025-W53", "not a week 2025 has")
    # 2026-W44 ends 2026-11-01, so on 2026-10-26 it is still running.
    refuses("2026-W44", "has not finished yet")
    refuses("2027-W01", "has not finished yet")


def test_the_iso_year_that_has_53_weeks_is_accepted():
    """2026 has 53 ISO weeks. A refusal that rejected W53 everywhere would
    make the one week a year that needs naming most the one that cannot be."""
    print("the 53rd week")
    week, dates = w.week_from_label("2026-W53", date(2027, 2, 1))
    check("2026-W53 is a week 2026 has", week == "2026-W53", week)
    check("and it runs into January", dates == "December 28 – January 3, 2027", dates)


# --------------------------------------------------------------- 2. the window


def test_the_window_is_the_span_the_cron_would_have_read():
    """For every week of 2026, the window is the cron's own seven days.

    The cron fires at 09:00 on the Monday after the week ends and its SQL says
    "the last seven days". So the window has to start on that week's Monday at
    09:00 and end seven days later. Checked as arithmetic against the cron's
    own firing time rather than against a second copy of the formula.
    """
    print("the window")
    bad = []
    for number in range(1, 53):
        week = f"2026-W{number:02d}"
        window = w.week_window(week, date(2027, 2, 1))
        sunday = date.fromisocalendar(2026, number, 7)
        fires = datetime(sunday.year, sunday.month, sunday.day,
                         w.PRESS_CRON_HOUR, tzinfo=timezone.utc) + timedelta(days=1)
        if window["until"] != fires or window["since"] != fires - timedelta(days=7):
            bad.append(f"{week}: {window} vs cron at {fires}")
    check("52 weeks: the window is the cron's seven days", not bad, str(bad[:2]))


def test_the_window_is_utc_and_covers_the_whole_week():
    print("the window's edges")
    window = w.week_window("2026-W38", date(2026, 10, 26))
    check("it starts on W38's own Monday",
          window["since"] == datetime(2026, 9, 14, 9, tzinfo=timezone.utc),
          str(window["since"]))
    check("it ends on the Monday the W38 cron fired",
          window["until"] == datetime(2026, 9, 21, 9, tzinfo=timezone.utc),
          str(window["until"]))
    check("both ends are UTC",
          window["since"].tzinfo is timezone.utc
          and window["until"].tzinfo is timezone.utc)
    check("it is seven days wide",
          window["until"] - window["since"] == timedelta(days=7))


def test_the_window_refuses_what_the_label_refuses():
    """One gate, not two. `week_window` goes through `week_from_label`."""
    print("the window's refusals")
    for label in ["2026-W99", "nonsense", "2027-W20"]:
        try:
            w.week_window(label, date(2026, 10, 26))
        except ValueError:
            check(f"{label!r} is refused by the window too", True)
        else:
            check(f"{label!r} is refused by the window too", False, "accepted")


# --------------------------------------------------------------- 3. gather

class FakeCursor:
    def __init__(self, rows):
        self.rows = rows

    def fetchone(self):
        return self.rows[0] if self.rows else None

    def fetchall(self):
        return self.rows


class FakeConn:
    """Records every statement and its parameters. Executes nothing."""

    def __init__(self):
        self.calls: list[tuple[str, object]] = []
        self.committed = 0

    def execute(self, sql, params=None):
        self.calls.append((sql, params))
        if "count(*) from papers" in sql:          # gather's stats row
            return FakeCursor([(1, 2, 3, 4, 5)])
        if "from digests where week <> " in sql:   # prior titles
            return FakeCursor([("# An older title\n\nbody",)])
        if "from digests \nwhere week = " in sql or "from digests where week = " in sql:
            return FakeCursor([])
        return FakeCursor([])

    def commit(self):
        self.committed += 1

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


WINDOWED = re.compile(
    r"coalesce\(%\(since\)s::timestamptz, now\(\) - interval '7 days'\)")


def test_every_windowed_query_is_handed_the_window():
    """gather passes `window` to each statement that reads a time bound."""
    print("gather's parameters")
    conn = FakeConn()
    window = w.week_window("2026-W38", date(2026, 10, 26))
    w.gather(conn, window)
    check("gather ran every one of its seven statements",
          len(conn.calls) == 7, f"{len(conn.calls)}")
    missing = [sql.strip().splitlines()[1].strip()
               for sql, params in conn.calls
               if ("%(since)s" in sql or "%(until)s" in sql) and params is not window]
    check("every statement with a bound got this run's window",
          not missing, str(missing))


def test_the_default_window_is_the_rolling_seven_days():
    """`gather(conn)` with no window is the cron's own path, unchanged.

    The SQL carries its old predicate inline as the `coalesce` default, so the
    scheduled run evaluates the same bound it evaluated before this change.
    Both keys present and both None is what makes that true: a missing key
    would be a psycopg KeyError at the cron rather than a fallback.
    """
    print("the default")
    conn = FakeConn()
    w.gather(conn)
    windows = [params for sql, params in conn.calls if "%(since)s" in sql]
    check("the default window is passed, not omitted", windows, "no statement saw one")
    check("and it is both keys, both None",
          all(p == {"since": None, "until": None} for p in windows), str(windows[:1]))


def test_no_time_bound_is_open_at_the_top():
    """Every lower bound in gather has an upper bound beside it.

    This is the property a backfill actually rests on. A query that says "newer
    than the window's start" and nothing else returns everything since that
    start, which for 2026-W38 is six weeks of claims printed under one week's
    label. Counted on the source rather than on a database, because no agent
    seat holds a database credential.
    """
    print("gather's bounds")
    body = SOURCE.split("def gather(")[1].split("\ndef budget(")[0]
    lowers = len(WINDOWED.findall(body))
    uppers = body.count("coalesce(%(until)s::timestamptz, now())")
    check("gather still has the nine lower bounds it had before", lowers == 9, f"{lowers}")
    check("and at least one upper bound for each of them, plus the two "
          "state-of-now streams", uppers == 11, f"{uppers}")
    check("no bare rolling interval is left in gather",
          "now() - interval '7 days'" not in WINDOWED.sub("", body))


# --------------------------------------------------------------- 4. the no-send


def run_weekly(week: str = "") -> dict:
    """Drive `weekly()` with no Modal, no database and no model.

    Every collaborator is replaced by a recorder, so what this asserts is
    `weekly`'s own control flow and nothing else. The prompts are served from
    the repository, because the container path they live at only exists inside
    the image.
    """
    import builtins
    import os

    seen: dict = {"sent": [], "mailed": [], "gathered": [], "citations": 0}
    conn = FakeConn()
    fake_psycopg = types.ModuleType("psycopg")
    fake_psycopg.connect = lambda *a, **k: conn

    real_open = builtins.open

    def rerouted_open(path, *a, **k):
        text = str(path)
        if text.startswith("/root/prompts/"):
            return real_open(ROOT / "prompts" / Path(text).name, *a, **k)
        return real_open(path, *a, **k)

    saved_psycopg = sys.modules.get("psycopg")
    saved_env = os.environ.get("DATABASE_URL")
    originals = {name: getattr(w, name) for name in [
        "check_availability", "runtime_guard", "check_citations", "gather",
        "print_issue", "ensure_fresh_title", "hold_for_quality",
        "send_newsletter", "notify_owner"]}
    try:
        sys.modules["psycopg"] = fake_psycopg
        os.environ["DATABASE_URL"] = "postgres://nowhere/none"
        builtins.open = rerouted_open

        def gather(conn, window=None):
            seen["gathered"].append(window)
            return {"stats": {"papers_ingested": 1, "papers_triaged": 2,
                              "papers_read_in_full": 3, "claims_distilled": 4,
                              "links_drawn": 5},
                    "new_claims": [], "superseded": [],
                    "traction": {"supported_claims": [], "citation_movers": []},
                    "deprecated": [], "deep_reads": []}

        def citations(conn):
            seen["citations"] += 1
            return 0

        w.check_availability = lambda: {"moonshot"}
        w.runtime_guard = lambda: types.SimpleNamespace(
            record_runtime=lambda *a, **k: (None, "runtime: test"))
        w.check_citations = citations
        w.gather = gather
        w.print_issue = lambda *a, **k: ("# A title\n\nbody", "kimi-k2.6",
                                         w.EDITION_FULL)
        w.ensure_fresh_title = lambda body, *a, **k: body
        w.hold_for_quality = lambda body, model, label, **k: (body, model, True)
        w.send_newsletter = lambda c, week, body, **k: (
            seen["sent"].append(week) or "sent to 3")
        w.notify_owner = lambda subject, detail: (
            seen["mailed"].append(subject) or "mailed")

        seen["returned"] = w.weekly(week)
    finally:
        builtins.open = real_open
        for name, fn in originals.items():
            setattr(w, name, fn)
        if saved_psycopg is None:
            sys.modules.pop("psycopg", None)
        else:
            sys.modules["psycopg"] = saved_psycopg
        if saved_env is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = saved_env
    seen["conn"] = conn
    return seen


def test_a_named_week_writes_the_row_and_mails_nobody():
    """The one behaviour a backfill must not get wrong.

    A regenerated issue replaces something subscribers may already hold. If
    the rewrite mailed them, running the institution backfill over a quarter
    of issues would mail the list a dozen times, and the apology would be the
    product's first contact with most of its readers.
    """
    print("a named week")
    seen = run_weekly("2026-W38")
    check("no newsletter was sent", seen["sent"] == [], str(seen["sent"]))
    check("no alarm was mailed either", seen["mailed"] == [], str(seen["mailed"]))
    check("the row was written", seen["conn"].committed == 1,
          f"{seen['conn'].committed} commits")
    upserts = [sql for sql, _ in seen["conn"].calls if "insert into digests" in sql]
    check("one upsert, on the week asked for", len(upserts) == 1, f"{len(upserts)}")
    check("and it carries W38's label",
          any(p and p[0] == "2026-W38" for sql, p in seen["conn"].calls
              if "insert into digests" in sql))
    check("the body came back to the caller",
          seen["returned"].startswith("# A title"), seen["returned"][:40])


def test_a_named_week_reads_that_weeks_window_and_not_todays():
    print("the window a named week reads")
    seen = run_weekly("2026-W38")
    check("gather was handed W38's window",
          seen["gathered"] == [w.week_window("2026-W38", date(2026, 10, 26))], str(seen["gathered"]))


def test_a_named_week_does_not_write_todays_citation_counts():
    """A rewrite reads the record. It does not add to it."""
    print("the citation pass on a rewrite")
    check("the citation check is skipped", run_weekly("2026-W38")["citations"] == 0)
    check("and it still runs on the scheduled path", run_weekly()["citations"] == 1)


def test_the_scheduled_path_still_sends():
    """The whole no-send rule is conditional, and this is the condition.

    A guard that stopped the Monday cron from mailing anybody would be a
    silent outage of the only thing this product publishes, and it would look
    exactly like a successful run.
    """
    print("the scheduled path")
    seen = run_weekly()
    week, _ = w.week_just_ended()
    check("the cron's own run sends", seen["sent"] == [week], str(seen["sent"]))
    check("and it reads the rolling window, not a named one",
          seen["gathered"] == [None], str(seen["gathered"]))


def test_a_bad_label_raises_before_anything_is_spent():
    """An operator's typo is a traceback, not an alarm in the owner's inbox."""
    print("a typo at the command line")
    try:
        run_weekly("2026-W99")
    except ValueError as exc:
        check("it raises ValueError", "not a week 2026 has" in str(exc), str(exc))
    else:
        check("it raises ValueError", False, "it ran")


def main() -> int:
    for fn in [
        test_the_cron_hour_is_the_crons_own_hour,
        test_week_from_label_is_the_inverse_of_week_just_ended,
        test_the_w38_recovery_week_can_now_be_asked_for_by_name,
        test_a_cross_month_week_renders_both_months,
        test_the_three_refusals,
        test_the_iso_year_that_has_53_weeks_is_accepted,
        test_the_window_is_the_span_the_cron_would_have_read,
        test_the_window_is_utc_and_covers_the_whole_week,
        test_the_window_refuses_what_the_label_refuses,
        test_every_windowed_query_is_handed_the_window,
        test_the_default_window_is_the_rolling_seven_days,
        test_no_time_bound_is_open_at_the_top,
        test_a_named_week_writes_the_row_and_mails_nobody,
        test_a_named_week_reads_that_weeks_window_and_not_todays,
        test_a_named_week_does_not_write_todays_citation_counts,
        test_the_scheduled_path_still_sends,
        test_a_bad_label_raises_before_anything_is_spent,
    ]:
        print(f"\n{fn.__name__}")
        fn()
    print(f"\n{len(FAILURES)} failing" if FAILURES else "\nall green")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
