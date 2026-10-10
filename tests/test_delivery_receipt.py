"""The credential-free reader for guardrail 4, and the receipt it reads.

    python3 tests/test_delivery_receipt.py     # or under pytest

Three of the five surfaces in `tools/delivery_health.py` needed `DATABASE_URL`
and no agent seat holds one, so every seat ever asked whether the press printed
answered `unknown`. `site/app/api/delivery/route.js` publishes the rows and this
command reads them.

Two things are checked here and they need different tools.

The site half is read as source for the guarantees that matter on a public
endpoint, and its shaping logic is executed for real in tests/delivery.test.mjs,
which this file also runs so that one pytest command covers the whole path.

The Python half is executed against receipts built here. `dh.fetch` is the only
thing stubbed: no network, no database, no site. The property worth the most is
the last section's, that a receipt and a connection carrying the same rows reach
the same verdict, because two readers of one question is exactly the shape that
grows two answers.
"""

import contextlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import sql_schema as q  # noqa: E402

from tools import delivery_health as dh  # noqa: E402

CORE = (REPO / "site" / "lib" / "delivery-core.js").read_text()
READER = (REPO / "site" / "lib" / "delivery.js").read_text()
ROUTE = (REPO / "site" / "app" / "api" / "delivery" / "route.js").read_text()

FAILURES: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}{': ' + detail if detail else ''}")
        FAILURES.append(name)


# ------------------------------------------------------------- the endpoint

def test_the_endpoint_never_selects_the_product():
    """The issue body and the claim text are what the subscription buys.

    Two defences and this is the first one: the queries do not ask for them.
    The second is in delivery-core.js, which builds every field by name, and
    tests/delivery.test.mjs holds it against a row that carries a body anyway.
    """
    check("digests.body is never selected",
          not re.search(r"select[^;]*\bbody\b", READER, re.S | re.I))
    check("the claims query asks only for a timestamp",
          "max(created_at)" in READER and "c.claim" not in READER)
    check("no subscriber table is read at all", "subscribers" not in READER)
    # The comments are stripped first, or the prose in them joins the table
    # list and the assertion reads a sentence as a schema.
    sql_only = re.sub(r"//[^\n]*", "", READER)
    read = sorted(set(re.findall(r"\bfrom\s+(\w+)", sql_only)))
    check("the only tables read are the ones this answers for",
          read == ["claims", "deploy_runtime", "digests", "distill_queue",
                   "interpret_queue", "latest_triage", "papers"], str(read))
    # The three views added in version 2 are counted and never selected from,
    # which is what keeps a queue depth metadata rather than product. `select
    # count(*) from distill_queue` publishes a number of waiting papers and
    # names no paper, and `distill_queue` is `select p.*` over `papers`, so
    # selecting from it instead of counting it would publish the corpus.
    check("the queue views are counted and never selected from",
          re.findall(r"from\s+(distill_queue|interpret_queue)", sql_only)
          == ["distill_queue", "interpret_queue"]
          and sql_only.count("count(*) from distill_queue") == 1
          and sql_only.count("count(*) from interpret_queue") == 1, sql_only)
    check("the triage backlog asks whether a row exists, not for the row",
          "select 1 from latest_triage" in sql_only
          and sql_only.count("latest_triage") == 1)


def test_every_statement_resolves_against_the_schema():
    """The half the JavaScript tests cannot execute, parsed the way the server
    parses it.

    docs/agents/runtime-changes.md names the site deploy as a runtime, and a
    statement inside a serverless route has no gate between the merge and
    production: this org runs no Postgres in CI, so the first execution is a
    stranger loading the page, or the standup asking whether the press printed.
    libpg_query is the server's own parser, so resolving every relation and
    column against db/schema.sql is the strongest check available here. It
    catches the two failures that actually happen, a typo and a name that was
    added to a query and not to the schema, and tests/test_waitlist.py and
    tests/test_unsubscribe.py have used these same helpers since 2026-10-06.

    The reason this file did not until today is the reason it matters today:
    the queue depths name three views and an anti-join where the rest of the
    route named four tables and nothing else, and `distill_queue` is the only
    relation on this route that db/schema.sql drops and recreates.
    """
    statements = q.literals(READER)
    check("the reader's statements were found at all", len(statements) >= 5,
          sorted(statements))
    for name, sql in sorted(statements.items()):
        try:
            q.assert_resolves(name, sql)
            print(f"  ok   {name} resolves")
        except AssertionError as exc:
            check(f"{name} resolves", False, str(exc).splitlines()[0])
        except Exception as exc:  # pglast absent, which is a skip and not a pass
            print(f"  skip {name}: {type(exc).__name__}: {exc}")
            return


def test_the_endpoint_takes_no_input():
    """A public endpoint with no parameter has no injection surface and no
    amplification: every caller gets the same four queries or none."""
    check("GET takes no arguments", re.search(r"export async function GET\(\s*\)", ROUTE))
    check("there is no other method", not re.search(r"export async function (POST|PUT|DELETE|PATCH)", ROUTE))
    check("nothing reads searchParams or a body",
          "searchParams" not in ROUTE and "request.json" not in ROUTE)


def test_an_unreadable_database_is_a_503_and_not_an_empty_receipt():
    """The route must not turn an unreadable database into a receipt of nulls.

    A reader that cannot tell "nothing published" from "could not look" will
    eventually call a healthy press broken, which is the failure guardrail 4
    exists to prevent, one level up.

    The two causes are also kept apart, because they are the diagnosis a seat
    cannot otherwise reach: `DATABASE_URL` absent from the site's environment is
    one setting away from working, and a query that throws is not.
    """
    check("the route answers 503", "status: 503" in ROUTE)
    check("the failure is not cached", "no-store" in ROUTE)
    check("a missing credential names itself",
          "DATABASE_URL is not set in the site's environment" in READER)
    check("a failing query says so separately",
          "a query failed:" in READER)
    check("and the reason reaches the response", "reason" in ROUTE)
    check("no driver error text is passed through whole",
          "error.message" not in READER and "${error}" not in READER)


def test_the_python_reader_relays_the_site_s_reason():
    """Otherwise the diagnosis dies at the HTTP status, and `HTTP 503` is the
    one answer that tells a seat nothing it did not already know."""
    body = json.dumps({"receipt": "alexandria-delivery", "ok": False,
                       "reason": "DATABASE_URL is not set in the site's environment"})
    with served(status=503, text=body):
        payload, why = dh.read_receipt()
    check("the payload is refused", payload is None)
    check("and the reason is carried through",
          "DATABASE_URL is not set in the site's environment" in why, why)
    with served(status=503, text="not json at all"):
        _, why = dh.read_receipt()
    check("a 503 with no readable reason still reports the status",
          "HTTP 503" in why, why)


def test_the_response_is_cached_at_the_edge():
    """The standup reads this once a day. A person refreshing it must not be
    able to turn it into load on Neon."""
    check("a shared max-age is set", re.search(r"s-maxage=\d+", ROUTE))
    check("and stale answers are served while revalidating",
          "stale-while-revalidate" in ROUTE)


def test_the_pure_core_stays_import_free():
    """tests/delivery.test.mjs loads it by evaluating its source, which only
    works while it has no imports to resolve."""
    check("delivery-core.js imports nothing",
          not re.search(r"^\s*import\s", CORE, re.M))


def test_the_two_sides_agree_on_the_version():
    """The reader has to know which version the site is publishing, and it can
    only know that while the two constants are the same number.

    READABLE_VERSIONS is the separate question of which older receipts it will
    still accept, and the newest of them is this one: a reader that claimed to
    read a version ahead of the one the site serves would be describing a
    receipt that does not exist yet.
    """
    m = re.search(r"RECEIPT_VERSION\s*=\s*(\d+)", CORE)
    check("the site declares a version", m is not None)
    check("and the reader speaks the same one",
          m and int(m.group(1)) == dh.RECEIPT_VERSION,
          f"site={m.group(1) if m else None} reader={dh.RECEIPT_VERSION}")
    check("the version the site serves is the newest one the reader reads",
          max(dh.READABLE_VERSIONS) == dh.RECEIPT_VERSION,
          str(dh.READABLE_VERSIONS))


def test_the_reader_and_the_route_name_the_same_url():
    check("RECEIPT_URL points at the route this change adds",
          dh.RECEIPT_URL.endswith("/api/delivery"), dh.RECEIPT_URL)
    check("and the route file is where that path resolves",
          (REPO / "site" / "app" / "api" / "delivery" / "route.js").exists())


def test_the_route_is_inside_the_paths_that_trigger_a_deploy():
    """site/vercel.json disables Git deploys and .github/workflows/deploy-main.yml
    fires the hook on pushes to main under `site/**`. The receipt is under
    site/, so merging this is what puts it live. Nothing to remember by hand,
    which is the whole argument of the drift guard this surface also feeds."""
    workflow = (REPO / ".github" / "workflows" / "deploy-main.yml").read_text()
    check("the deploy hook fires on site/** pushes to main", '"site/**"' in workflow)


# -------------------------------------------------------------- the reader

WEEK_FORMAT = "%Y-%m-%dT%H:%M:%S+00:00"


QUEUES = {"triage_pending": 41, "distill_pending": 212, "interpret_pending": 7}


def receipt(week="2026-W39", created="2026-09-28T09:03:00+00:00",
            papers=None, claims=None, deploy=None, version=None,
            press_present=True, queues="default"):
    """A receipt whose corpus moved last night, whatever night it is.

    The press surface is judged against the `today` these tests pass in, so the
    week label can be a constant. The corpus is not: `judge_pipeline` measures
    age against the real clock, because a corpus is stale when it stopped
    moving and no caller gets to decide what day it is. A fixture pinned to
    2026-10-01 02:00 therefore aged into a stale corpus 14 hours later and
    turned this file red on 2026-10-02 with nothing in the code changed, which
    is the one kind of red that teaches nobody anything.
    """
    now = datetime.now(timezone.utc)
    fresh = (now - timedelta(hours=14)).strftime(WEEK_FORMAT)
    return {
        "receipt": "alexandria-delivery",
        "version": dh.RECEIPT_VERSION if version is None else version,
        # The receipt's own timestamp, which nothing judges an age against
        # today. It stays next to `fresh` on purpose: the moment a reader does
        # start checking how old a receipt is, this has to move with it.
        "observed_at": now.strftime(WEEK_FORMAT),
        "press": ({"newest_week": week, "created_at": created, "model": "kimi-k2"}
                  if press_present else None),
        "pipeline": {"papers_newest": papers if papers is not None else fresh,
                     "claims_newest": claims if claims is not None else fresh},
        "queues": QUEUES if queues == "default" else queues,
        "deploy": deploy if deploy is not None else [],
    }


class served:
    """Stubs `dh.fetch` so these tests never touch the network."""

    def __init__(self, status=200, body=None, text=None):
        self.status = status
        self.body = text if text is not None else json.dumps(body or {})
        self.calls: list[str] = []

    def __enter__(self):
        self.real = dh.fetch

        def fake(url, timeout=25):
            self.calls.append(url)
            return self.status, self.body, {}

        dh.fetch = fake
        return self

    def __exit__(self, *exc):
        dh.fetch = self.real
        return False


def surfaces(today=None, **kwargs):
    """`database_surfaces` with no DATABASE_URL, so the receipt is the reader."""
    old = dh.os.environ.pop("DATABASE_URL", None)
    try:
        return {s.name: s for s in dh.database_surfaces(today=today, **kwargs)}
    finally:
        if old is not None:
            dh.os.environ["DATABASE_URL"] = old


def test_a_current_receipt_answers_the_press_green():
    with served(body=receipt(week="2026-W39")) as net:
        out = surfaces(today=dh.date(2026, 10, 1))
    check("the press is ok", out["press"].state == dh.OK, out["press"].headline)
    check("the headline names the week and the model",
          "2026-W39" in out["press"].headline and "kimi-k2" in out["press"].headline)
    check("the evidence says it was read second-hand",
          out["press"].evidence["read_via"] == dh.RECEIPT_URL,
          str(out["press"].evidence.get("read_via")))
    check("the receipt was fetched once", net.calls == [dh.RECEIPT_URL], str(net.calls))


def test_a_stale_receipt_answers_the_press_red_with_a_count():
    """The point of the whole change: this answer was `unknown` yesterday."""
    with served(body=receipt(week="2026-W37")):
        out = surfaces(today=dh.date(2026, 10, 1))
    check("the press is failing", out["press"].state == dh.FAILING,
          out["press"].headline)
    check("and it says how many issues are missing",
          "2 issue(s) missing" in out["press"].headline, out["press"].headline)


def test_an_empty_digests_table_is_failing_not_unknown():
    with served(body=receipt(press_present=False)):
        out = surfaces(today=dh.date(2026, 10, 1))
    check("an empty table is a real answer",
          out["press"].state == dh.FAILING, out["press"].headline)


def test_a_stale_corpus_answers_the_pipeline_red():
    old = (datetime.now(timezone.utc) - timedelta(days=5)).strftime(WEEK_FORMAT)
    with served(body=receipt(papers=old)):
        out = surfaces(today=dh.date(2026, 10, 1))
    check("the pipeline is failing", out["pipeline"].state == dh.FAILING,
          out["pipeline"].headline)
    check("and it names which table stopped moving",
          "papers has not moved" in out["pipeline"].headline,
          out["pipeline"].headline)
    with served(body=receipt()):
        fresh = surfaces(today=dh.date(2026, 10, 1))
    check("a corpus that moved last night reads ok",
          fresh["pipeline"].state == dh.OK, fresh["pipeline"].headline)


# ---------------------------------------------- refusals, which are the point

def test_every_way_the_receipt_can_be_wrong_is_unknown():
    """Five rejections, and not one of them may read as a verdict about the
    press. A reader that guesses from a half-understood payload is worse than
    one that says it could not look."""
    cases = {
        "the site did not answer": served(status=0, text="connection refused"),
        "the route is not deployed yet": served(status=404, text="not found"),
        "the response is not JSON": served(status=200, text="<!doctype html>"),
        "the JSON is some other endpoint": served(status=200, body={"ok": True}),
        "the version is one this reader does not speak":
            served(status=200, body=receipt(version=99)),
    }
    for name, net in cases.items():
        with net:
            out = surfaces(today=dh.date(2026, 10, 1))
        check(f"{name}: all three surfaces unknown",
              all(s.state == dh.UNKNOWN for s in out.values()),
              str({k: v.state for k, v in out.items()}))
        check(f"{name}: the message names both readers",
              all("DATABASE_URL" in s.headline and dh.RECEIPT_URL in s.headline
                  for s in out.values()),
              out["press"].headline)


def test_a_version_this_reader_cannot_read_is_refused_rather_than_partly_read():
    """The failure mode this prevents: a version renames a field, this reader
    reads the old name, gets None, and reports an empty digests table as a
    press that printed nothing."""
    unknown = max(dh.READABLE_VERSIONS) + 1
    with served(status=200, body=receipt(version=unknown)):
        payload, why = dh.read_receipt()
    check("the payload is refused", payload is None)
    check("and the reason names the version it got and the ones it speaks",
          f"version {unknown}" in why
          and all(str(v) in why for v in dh.READABLE_VERSIONS), why)


def test_the_previous_version_is_still_readable_through_the_deploy_window():
    """Why this is not laxity. The site deploys on a merge to `main` and a
    seat's checkout updates the instant the branch lands, so between those two
    the newest reader meets the previous receipt. Exact-match version checking
    turned that window into all three database surfaces answering `unknown`,
    which is the same blindness the receipt was built to end.

    The rule that makes it safe is in READABLE_VERSIONS' own header: a version
    stays readable only while every field this reader needs is present in it or
    optional in it. `queues` is optional by construction.
    """
    check("version 1 is in the readable list", 1 in dh.READABLE_VERSIONS)
    payload = receipt(version=1)
    payload.pop("queues", None)
    with served(status=200, body=payload):
        got, why = dh.read_receipt()
    check("a version 1 receipt is accepted", got is not None, why)
    _, pipeline_row, _ = dh.receipt_facts(payload)
    check("and its absent queue depth reads as unknown, not as zero",
          pipeline_row["queues"] is None, str(pipeline_row))


def test_a_credential_that_does_not_work_falls_through_to_the_receipt():
    """The order is connection first, receipt second. A DATABASE_URL that is
    present and broken must not strand the check: that is the owner's laptop
    with a stale password, and it used to answer `unknown` for all three."""
    old = dh.os.environ.get("DATABASE_URL")
    dh.os.environ["DATABASE_URL"] = "host=127.0.0.1 port=1 dbname=nope connect_timeout=1"
    try:
        with served(body=receipt(week="2026-W39")):
            out = {s.name: s for s in dh.database_surfaces(today=dh.date(2026, 10, 1))}
    finally:
        if old is None:
            dh.os.environ.pop("DATABASE_URL", None)
        else:
            dh.os.environ["DATABASE_URL"] = old
    check("the receipt answered instead", out["press"].state == dh.OK,
          out["press"].headline)
    check("and the evidence says which reader it was",
          out["press"].evidence["read_via"] == dh.RECEIPT_URL)


# ------------------------------------------------- the deploy surface by proxy

def test_a_receipt_with_no_deploy_rows_at_all_is_unknown_not_an_alarm():
    """The site sends null when it could not run that query, which happens
    while `apply_schema` is still a pending hand step. Reading that as three
    jobs that never reported would fire the drift alarm on a schema step."""
    payload = receipt()
    payload["deploy"] = None
    with served(body=payload):
        out = surfaces(today=dh.date(2026, 10, 1))
    check("deploy is unknown", out["deploy"].state == dh.UNKNOWN,
          out["deploy"].headline)
    check("and it says the site could not read it either",
          "could not be read by the site" in out["deploy"].headline,
          out["deploy"].headline)
    check("the press is still answered", out["press"].state == dh.OK,
          "one missing table must not cost the two urgent surfaces")


def test_a_drift_read_from_the_receipt_is_reported_and_not_mailed():
    """`notified_at` is the alarm's once-a-day cooldown and it lives in the row.

    A reader with no credential cannot write, so it cannot keep a cooldown, so
    it reports the drift and says plainly that nobody was mailed. Mailing
    without a cooldown would be one mail every time the standup runs, which is
    the argument DEPLOY_NOTIFY_COOLDOWN_HOURS already makes.

    The checkout is the same real git fixture tests/test_deploy_drift.py builds,
    nine days stale, because the dating logic is `git log` and mocking it would
    test the mock.
    """
    sys.path.insert(0, str(Path(__file__).parent))
    import test_deploy_drift as drift  # the fixture, not the tests

    with tempfile.TemporaryDirectory() as tmp:
        repo = drift.fixture_repo(Path(tmp), days_ago=9)
        ran = datetime.now(timezone.utc) - timedelta(hours=2)
        payload = receipt(deploy=[
            {"app": app, "runtime_sha": "0000stale000", "entrypoint": module,
             "file_count": 3, "recorded_at": ran.strftime(WEEK_FORMAT),
             "first_seen_at": ran.strftime(WEEK_FORMAT), "notified_at": None}
            for app, module in sorted(drift.rs.APPS.items())])
        _, _, deploy_rows = dh.receipt_facts(payload)

        from_receipt = dh.judge_deploy(deploy_rows, repo, source=dh.RECEIPT_URL)
        from_direct = dh.judge_deploy(deploy_rows, repo, notify_conn=None)

    check("a nine-day drift is failing", from_receipt.state == dh.FAILING,
          from_receipt.headline)
    check("the headline names every stale job",
          all(app in from_receipt.headline for app in drift.rs.APPS),
          from_receipt.headline)
    alarm = from_receipt.evidence.get("alarm", "")
    check("nobody was mailed", "not mailed" in alarm, alarm)
    check("and the reason given is the cooldown it cannot write",
          "cooldown" in alarm, alarm)
    check("the reason names the receipt as the source", dh.RECEIPT_URL in alarm, alarm)
    check("the same facts read directly still reach the same state",
          from_direct.state == dh.FAILING)
    check("and a caller that asked not to notify is told exactly that",
          from_direct.evidence.get("alarm") == "not notified",
          str(from_direct.evidence.get("alarm")))


# ------------------------------------- one judgement, two readers, same answer

class FakeConn:
    """Answers each query with the first canned row whose key it contains."""

    def __init__(self, answers):
        self.answers = answers

    def execute(self, sql, params=None):
        for key, row in self.answers.items():
            if key in sql:
                return _Result(row)
        raise AssertionError(f"no canned answer for {sql!r}")

    def transaction(self):
        """psycopg's savepoint, which `queue_facts` runs its read inside.

        A real one matters to the behaviour under test: without the savepoint a
        missing view aborts the transaction and takes the deploy surface down
        with it on the same connection. Here it only has to exist, and a fake
        that lacked it would make `queue_facts` return None for the wrong
        reason and quietly pass the tests that assert a cause.
        """
        return contextlib.nullcontext()


class _Result:
    def __init__(self, row):
        self.row = row

    def fetchone(self):
        return self.row

    def fetchall(self):
        return self.row


def test_a_connection_and_a_receipt_reach_the_same_verdict():
    """The property that keeps this honest. Two readers of one question is the
    shape that grows two answers, so the judgement takes facts rather than a
    connection and both readers hand it the same shapes. Any divergence here
    means a seat and the press could disagree about the same week.
    """
    created = datetime(2026, 9, 28, 9, 3, tzinfo=timezone.utc)
    moved = datetime.now(timezone.utc) - timedelta(hours=14)
    today = dh.date(2026, 10, 1)

    for week, expect in (("2026-W39", dh.OK), ("2026-W36", dh.FAILING)):
        conn = FakeConn({
            "from digests": (week, created, "kimi-k2"),
            "max(fetched_at)": (moved,),
            "max(created_at) from claims": (moved,),
            "distill_queue": (41, 212, 7),
        })
        direct_press = dh.judge_press(dh.press_facts(conn), today)
        direct_pipeline = dh.judge_pipeline(dh.pipeline_facts(conn))

        payload = receipt(week=week, created=created.strftime(WEEK_FORMAT),
                          papers=moved.strftime(WEEK_FORMAT),
                          claims=moved.strftime(WEEK_FORMAT))
        press_row, pipeline_row, _ = dh.receipt_facts(payload)
        via_receipt_press = dh.judge_press(press_row, today, dh.RECEIPT_URL)
        via_receipt_pipeline = dh.judge_pipeline(pipeline_row, source=dh.RECEIPT_URL)

        check(f"press {week}: the direct read is {expect}",
              direct_press.state == expect, direct_press.headline)
        check(f"press {week}: the receipt agrees on the state",
              via_receipt_press.state == direct_press.state)
        check(f"press {week}: and on the headline, word for word",
              via_receipt_press.headline == direct_press.headline,
              f"{direct_press.headline!r} vs {via_receipt_press.headline!r}")
        check(f"press {week}: only `read_via` differs",
              direct_press.evidence["read_via"] == dh.DIRECT
              and via_receipt_press.evidence["read_via"] == dh.RECEIPT_URL)
        check(f"pipeline {week}: both readers agree",
              via_receipt_pipeline.state == direct_pipeline.state
              == dh.OK)


def test_both_readers_name_the_same_cause_for_a_stalled_stage():
    """The property the queue depths were added for, held across both readers.

    A stale `claims` has two causes and one number separates them. The 2026-10-09
    ledger entry had to stop at "whether it fired and found an empty queue, or
    whether it fired and raised", because the depth needed a credential no seat
    holds. If the receipt and a connection disagreed about the cause, the seat
    with no credential would read a different diagnosis from the one the owner
    reads, which is worse than the silence it replaced.
    """
    moved = datetime.now(timezone.utc) - timedelta(hours=14)
    stalled = datetime.now(timezone.utc) - timedelta(days=3)

    cases = (("an empty queue", (41, 0, 7), {"triage_pending": 41,
                                             "distill_pending": 0,
                                             "interpret_pending": 7},
              "distill_queue empty"),
             ("a deep queue", (41, 212, 7), QUEUES,
              "212 papers waiting in distill_queue"),
             ("no depth at all", None, None,
              "no queue depth is published here"))

    for name, row, published, phrase in cases:
        answers = {"max(fetched_at)": (moved,),
                   "max(created_at) from claims": (stalled,)}
        if row is not None:
            answers["distill_queue"] = row
        direct = dh.judge_pipeline(dh.pipeline_facts(FakeConn(answers)))

        payload = receipt(papers=moved.strftime(WEEK_FORMAT),
                          claims=stalled.strftime(WEEK_FORMAT),
                          queues=published)
        _, pipeline_row, _ = dh.receipt_facts(payload)
        via_receipt = dh.judge_pipeline(pipeline_row, source=dh.RECEIPT_URL)

        check(f"{name}: both readers say failing",
              direct.state == via_receipt.state == dh.FAILING, direct.headline)
        check(f"{name}: the headline names the cause",
              phrase in direct.headline, direct.headline)
        check(f"{name}: and both readers word it identically",
              direct.headline == via_receipt.headline,
              f"{direct.headline!r} vs {via_receipt.headline!r}")
        check(f"{name}: the depths are in the evidence either way",
              direct.evidence["queues"] == via_receipt.evidence["queues"],
              str(direct.evidence["queues"]))

    # A deep queue on a corpus that is still moving is not this surface's
    # alarm. Its unit is staleness, and a depth threshold here would be a
    # second alarm nobody specified.
    healthy = dh.judge_pipeline(dh.pipeline_facts(FakeConn({
        "max(fetched_at)": (moved,),
        "max(created_at) from claims": (moved,),
        "distill_queue": (41, 9000, 7)})))
    check("a deep queue alone does not raise", healthy.state == dh.OK, healthy.headline)
    check("but it is still reported",
          healthy.evidence["queues"]["distill_pending"] == 9000)


def test_a_missing_view_costs_the_depth_and_nothing_else():
    """`apply_schema` is a hand step, so a database one migration behind is a
    state this really meets. It must cost the cause and not the staleness."""
    class NoViews(FakeConn):
        def execute(self, sql, params=None):
            if "distill_queue" in sql:
                raise RuntimeError('relation "distill_queue" does not exist')
            return super().execute(sql, params)

    stalled = datetime.now(timezone.utc) - timedelta(days=3)
    moved = datetime.now(timezone.utc) - timedelta(hours=14)
    facts = dh.pipeline_facts(NoViews({"max(fetched_at)": (moved,),
                                       "max(created_at) from claims": (stalled,)}))
    check("the depth is None and not zero", facts["queues"] is None)
    surface = dh.judge_pipeline(facts)
    check("the staleness still reports", "claims has not moved in 3 days" in surface.headline)
    check("and the headline says the cause is unavailable",
          "no queue depth is published here" in surface.headline, surface.headline)


def test_the_direct_reader_is_still_the_one_that_mails():
    """`check_deploy(conn, notify=True)` is unchanged, so the Modal jobs and the
    owner's machine keep the alarm. Only the receipt path declines to mail."""
    source = (REPO / "tools" / "delivery_health.py").read_text()
    m = re.search(r"def check_deploy\(.*?\n\n", source, re.S)
    check("check_deploy still passes a connection to notify with",
          m and "notify_conn=conn if notify else None" in m.group(0))


# ------------------------------------------------------------ executed js

def test_delivery_core_logic():
    """Runs tests/delivery.test.mjs, which executes the real module."""
    node = shutil.which("node")
    if node is None:
        print("  skip node is not installed; run `node --test tests/delivery.test.mjs`")
        return
    proc = subprocess.run(
        [node, "--test", str(Path(__file__).parent / "delivery.test.mjs")],
        capture_output=True, text=True)
    check("tests/delivery.test.mjs passes", proc.returncode == 0,
          proc.stdout[-2000:] + proc.stderr[-2000:])


def main() -> int:
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            print(name)
            fn()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} failed: {', '.join(FAILURES)}")
        return 1
    print("every check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
