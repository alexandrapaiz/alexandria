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
              {s.name for s in results} == {"press", "pipeline", "payments",
                                            "deploy"},
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
    # The `papers` row is one statement with two columns since 2026-10-10:
    # (max(fetched_at), max(distilled_at)). The second is a cause rather than a
    # clock, so nothing in this test raises on it.
    fresh = FakeConn({"from papers": (now - timedelta(hours=6),
                                      now - timedelta(hours=4)),
                      "from claims": (now - timedelta(hours=5),)})
    check("a corpus that moved today is ok",
          dh.check_pipeline(fresh).state == dh.OK)

    stale = FakeConn({"from papers": (now - timedelta(days=5),
                                      now - timedelta(hours=4)),
                      "from claims": (now - timedelta(hours=5),)})
    s = dh.check_pipeline(stale)
    check("ingest stopped five days ago is failing", s.state == dh.FAILING, s.headline)
    check("and the headline names which table", "papers" in s.headline, s.headline)

    # A stale `papers` takes no cause clause, because the clause is about the
    # one stage with a queue inside this database and arXiv is not it.
    check("and it does not borrow distill's diagnosis",
          "distill" not in s.headline, s.headline)

    empty = FakeConn({"from papers": (None, None), "from claims": (None,)})
    check("empty corpus tables are failing",
          dh.check_pipeline(empty).state == dh.FAILING)

    # A marker that has never been set must not read as a stage that never ran.
    # It is the same None a version 2 receipt hands over, and the two readers
    # have to reach one sentence from it.
    never = FakeConn({"from papers": (now - timedelta(hours=6), None),
                      "from claims": (now - timedelta(days=4),)})
    n = dh.check_pipeline(never)
    check("a stall with no marker at all still fails", n.state == dh.FAILING, n.headline)
    check("and the marker is reported as absent rather than guessed",
          n.evidence["distilled"] is None, str(n.evidence))


def test_naive_timestamps_do_not_crash_the_comparison():
    """Postgres columns declared without a time zone come back naive.

    A TypeError here would take out the whole check, so the tool assumes UTC
    rather than refusing to answer.
    """
    naive = datetime.utcnow() - timedelta(hours=2)
    conn = FakeConn({"from papers": (naive, naive), "from claims": (naive,)})
    check("a naive timestamp is read as UTC",
          dh.check_pipeline(conn).state == dh.OK)

    # The distill marker is compared against the clock too, so it needs the
    # same assumption. A TypeError there would take out the whole surface at
    # exactly the moment it has something to say. Asked of the clause directly,
    # because this file's fake has no savepoint and so never publishes a queue
    # depth, and the clause does not reach the marker without one.
    deep = {"triage_pending": 41, "distill_pending": 212, "interpret_pending": 7}
    recent = dh.queue_cause("claims", deep, datetime.utcnow() - timedelta(hours=3))
    check("a naive marker from a recent run does not crash",
          "ran and extracted nothing" in recent, recent)
    old = dh.queue_cause("claims", deep, datetime.utcnow() - timedelta(days=4))
    check("and a naive marker from no run at all is read as UTC too",
          "marked nothing read in 4.0 days" in old, old)


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


# --- can a sale happen at all (2026-10-18) -----------------------------------
#
# The state these cases are written from: on 2026-10-18 the live pricing page
# answered HTTP 200, carried no `/api/checkout/` href anywhere in its markup,
# and rendered "Opens shortly" on both paid tiers, while
# `/api/checkout/monthly` answered 303 to `/sign-up`. Both halves verified
# against the deployed site that morning.

PRICING_SHELL = """<main class="page"><h1>Read for free. Build for $20.</h1>
  <div class="tier"><h2>Digest</h2><a class="pill ghost" href="#waitlist">Start reading</a></div>
  <div class="tier featured"><h2>Full access</h2>{monthly}</div>
  <div class="tier"><h2>Lifetime</h2>{lifetime}</div></main>"""

SOLD_OUT = '<span class="pill ghost">Opens shortly</span>'


def _pricing(*linked: str) -> str:
    """The pricing page as it renders with these offers live, and no others."""
    def pill(offer):
        return (f'<a class="pill" href="/api/checkout/{offer}">Buy</a>'
                if offer in linked else SOLD_OUT)
    page = PRICING_SHELL.format(monthly=pill("monthly"), lifetime=pill("lifetime"))
    if "trial" in linked:
        page += '<p class="tier-note"><a href="/api/checkout/trial">Start the trial</a></p>'
    return page


def _site_that_answers(page: str, hops: dict) -> callable:
    """A stand-in for `dh.fetch`: one pricing page, and one answer per route."""
    def fake(url, timeout=25, follow=True):
        if url == dh.PRICING_URL:
            return 200, page, {}
        for offer, answer in hops.items():
            if url.endswith(f"/api/checkout/{offer}"):
                return answer
        raise AssertionError(f"the probe fetched something unexpected: {url}")
    return fake


def _to_sign_up(offer: str) -> tuple:
    return 303, "", {"location": "https://libraryofalexandria.dev/sign-up"
                                 f"?redirect_url=%2Fapi%2Fcheckout%2F{offer}"}


def _with_fetch(fake, call):
    real = dh.fetch
    dh.fetch = fake
    try:
        return call()
    finally:
        dh.fetch = real


def test_the_pricing_page_with_no_checkout_link_is_failing():
    """2026-10-18, and the one case this surface was built for.

    Both paid tiers render the words and neither renders a link, so the state
    of the till is that nothing on the page can be bought. Every other surface
    in this file was green about it.
    """
    s = _with_fetch(_site_that_answers(_pricing(), {}), dh.check_checkout)
    check("no checkout link at all is failing", s.state == dh.FAILING, s.headline)
    check("and the headline says a buyer cannot buy",
          "nothing on it a buyer can buy" in s.headline, s.headline)
    check("and it names the three variables that are unset",
          all(name in s.headline for name in ("POLAR_CHECKOUT_TRIAL",
                                              "POLAR_CHECKOUT_MONTHLY",
                                              "POLAR_CHECKOUT_LIFETIME")),
          s.headline)
    check("and no link was followed, because there was none",
          "followed" not in s.evidence, str(s.evidence))


def test_probing_the_route_instead_of_the_page_would_report_green():
    """The reason the page is read first, as a test rather than as a comment.

    `/api/checkout/[plan]` asks for a signed-in account before it looks up the
    checkout link, so a stranger gets the same 303 to `/sign-up` whether the
    offer is configured or not. A probe built on the route alone is green on
    the exact morning both tiers were unbuyable.
    """
    status, _, headers = _to_sign_up("monthly")
    hop, why = dh.judge_hop(status, headers["location"])
    check("the route's answer to a stranger reads as a door that opens",
          hop == "sign-in", f"{hop}: {why}")
    check("so only the page read catches an unset offer",
          _with_fetch(_site_that_answers(_pricing(), {}),
                      dh.check_checkout).state == dh.FAILING)


def test_every_ending_one_followed_link_can_meet():
    """Five answers, judged without a network and without a Polar account."""
    hop, why = dh.judge_hop(0, "", "connection refused")
    check("silence is not a door", hop is None and "did not answer" in why, why)

    hop, why = dh.judge_hop(303, "https://buy.polar.sh/checkout-abc")
    check("a hop off-site is the seller", hop == "seller", why)
    check("and it names the host it reached", "buy.polar.sh" in why, why)

    hop, why = dh.judge_hop(303, "https://libraryofalexandria.dev/pricing")
    check("a bounce back to the pricing page is not a door",
          hop is None, why)
    check("and it says what sends a buyer back there",
          "checkout link" in why and "unset" in why, why)

    hop, why = dh.judge_hop(303, "")
    check("a redirect with no Location goes nowhere", hop is None, why)

    hop, why = dh.judge_hop(200, "")
    check("a 200 from a route that only redirects is a finding",
          hop is None and "only ever redirects" in why, why)

    hop, why = dh.judge_hop(404, "")
    check("a 404 says the route is not deployed",
          hop is None and "not deployed" in why, why)


def test_a_link_that_leads_back_to_the_page_that_sent_it_is_failing():
    """A link on the page the route does not recognise is a loop, not a sale."""
    bounce = (303, "", {"location": "https://libraryofalexandria.dev/pricing"})
    fake = _site_that_answers(_pricing("monthly"), {"monthly": bounce})
    s = _with_fetch(fake, dh.check_checkout)
    check("a link that loops is failing", s.state == dh.FAILING, s.headline)
    check("and the headline says the link does not open a sale",
          "does not open a sale" in s.headline, s.headline)
    check("and the evidence keeps where it went",
          s.evidence["followed"]["monthly"]["hop"] is None, str(s.evidence))


def test_half_a_launch_does_not_read_green():
    """One tier buyable and two advertised with no link behind them."""
    fake = _site_that_answers(_pricing("monthly"),
                              {"monthly": _to_sign_up("monthly")})
    s = _with_fetch(fake, dh.check_checkout)
    check("one offer of three is still failing", s.state == dh.FAILING, s.headline)
    check("and it counts what can be bought", "1 of 3 offers" in s.headline,
          s.headline)
    check("and names the offers that cannot, with their variables",
          "POLAR_CHECKOUT_LIFETIME" in s.headline
          and "POLAR_CHECKOUT_TRIAL" in s.headline, s.headline)


def test_every_offer_linked_and_opening_is_the_only_green():
    hops = {offer: _to_sign_up(offer) for offer in ("trial", "monthly", "lifetime")}
    fake = _site_that_answers(_pricing("trial", "monthly", "lifetime"), hops)
    s = _with_fetch(fake, dh.check_checkout)
    check("three offers, three open links, is ok", s.state == dh.OK, s.headline)
    check("and the headline says where the hop stops",
          "account before a card" in s.headline, s.headline)
    check("and every link was actually followed",
          sorted(s.evidence["followed"]) == ["lifetime", "monthly", "trial"],
          str(sorted(s.evidence["followed"])))

    seller = {offer: (303, "", {"location": f"https://buy.polar.sh/{offer}"})
              for offer in ("trial", "monthly", "lifetime")}
    s = _with_fetch(_site_that_answers(_pricing("trial", "monthly", "lifetime"), seller),
                    dh.check_checkout)
    check("and a hop to the real seller is ok too", s.state == dh.OK, s.headline)


def test_the_offers_are_read_from_the_site_and_not_copied():
    offers = dh.checkout_offers()
    check("the three offers come out of site/lib/polar-core.js",
          [offer for offer, _ in offers] == ["trial", "monthly", "lifetime"],
          str(offers))
    check("with the environment variable behind each one",
          dict(offers)["monthly"] == "POLAR_CHECKOUT_MONTHLY", str(offers))

    core = (Path(__file__).resolve().parents[1]
            / "site" / "lib" / "polar-core.js").read_text()
    check("and that is where the list lives", "export const OFFERS" in core)

    check("an unreadable file yields no offers",
          dh.checkout_offers(Path("/nonexistent")) == [])
    s = _with_fetch(_site_that_answers(_pricing(), {}),
                    lambda: dh.check_checkout(Path("/nonexistent")))
    check("and the surface says so instead of implying it looked",
          "unreadable" in s.evidence["expected_read_from"],
          s.evidence["expected_read_from"])
    check("while the floor check still fails an empty page",
          s.state == dh.FAILING, s.headline)


def test_the_checkout_surface_is_in_the_default_run():
    source = (Path(__file__).resolve().parents[1]
              / "tools" / "delivery_health.py").read_text()
    check("checkout is one of the surfaces", "checkout" in dh.ORDER, str(dh.ORDER))
    check("and it reads beside payments, which is the other money surface",
          dh.ORDER.index("checkout") == dh.ORDER.index("payments") + 1,
          str(dh.ORDER))
    check("run() reaches it", 'if "checkout" in asked' in source)
    check("and the default is every surface", "args.surfaces or ORDER" in source)
    check("and the help text counts them all",
          "all eight" in source, "the --surface help text is out of date")

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
        test_the_pricing_page_with_no_checkout_link_is_failing,
        test_probing_the_route_instead_of_the_page_would_report_green,
        test_every_ending_one_followed_link_can_meet,
        test_a_link_that_leads_back_to_the_page_that_sent_it_is_failing,
        test_half_a_launch_does_not_read_green,
        test_every_offer_linked_and_opening_is_the_only_green,
        test_the_offers_are_read_from_the_site_and_not_copied,
        test_the_checkout_surface_is_in_the_default_run,
    ]:
        print(f"\n{fn.__name__}")
        fn()
    print(f"\n{len(FAILURES)} failing" if FAILURES else "\nall green")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
