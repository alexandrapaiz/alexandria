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

# The site's own `UNREADABLE_REASONS`, read out of its source rather than
# retyped here. Retyping it would make this file agree with itself while the
# two halves disagreed, which is the failure the version constant next to it
# already has a test for.
CORE_REASONS = re.findall(
    r'"([^"]+)",',
    re.search(r"UNREADABLE_REASONS = Object\.freeze\(\[(.*?)\]\)", CORE,
              re.S).group(1))
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
          read == ["claim_links", "claims", "deploy_runtime", "digests",
                   "distill_queue", "interpret_queue", "latest_triage",
                   "papers", "payment_exceptions", "triage_log"], str(read))
    # The table version 5 added is the first one on this endpoint whose rows
    # are about a person rather than about a paper. `payment_exceptions` holds
    # the buyer's address and the Polar customer and subscription ids, because
    # the owner needs them to invite the person or find the charge, and this
    # endpoint is public and unauthenticated. So the reader counts and groups
    # and never selects one: a count of waiting payments names no payer.
    check("the till is counted and grouped, never selected from",
          re.findall(r"from\s+(payment_exceptions)", sql_only)
          == ["payment_exceptions", "payment_exceptions"]
          and "email" not in sql_only
          and "polar_customer_id" not in sql_only
          and "polar_subscription_id" not in sql_only
          and "detail" not in sql_only, sql_only)
    # The two tables version 4 added, asked for a timestamp and nothing else.
    # `triage_log.reasoning` is a model's prose about a paper and
    # `claim_links.relation` is an edge of the graph the subscription buys, so
    # a `max()` over one column each is the whole of what belongs here.
    check("the sibling reads ask for a timestamp and a model, nothing else",
          re.findall(r"from (triage_log|claim_links)", sql_only)
          == ["triage_log", "claim_links"]
          and "reasoning" not in sql_only and "relation" not in sql_only
          and "score" not in sql_only and "confidence" not in sql_only,
          sql_only)
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

# A till with nothing open, which is the state the product is in whenever it is
# working. The default on purpose: a fixture whose till was broken would make
# every other test on this page read `failing` for a reason it is not about.
CLEAR_TILL = {"unresolved": 0, "needs_a_hand": 0, "oldest_unresolved_at": None,
              "newest_unresolved_at": None, "codes": []}


def TILL(unresolved, needs_a_hand, oldest, codes):
    """An open-exception block, with `oldest` as hours ago rather than a date.

    Hours, because the verdict measures the oldest row against a six-hour
    window and against the real clock. A fixture pinned to a date would age
    past that window and turn this file red with nothing in the code changed,
    which is the mistake the `receipt` docstring below records.
    """
    at = (datetime.now(timezone.utc) - timedelta(hours=oldest)).replace(microsecond=0)
    return {"unresolved": unresolved, "needs_a_hand": needs_a_hand,
            "oldest_unresolved_at": at.strftime(WEEK_FORMAT),
            "newest_unresolved_at": at.strftime(WEEK_FORMAT),
            "codes": codes}


def SIBLINGS(when, model="kimi-k2.6"):
    """A sibling block where both stages wrote at `when`, on a Moonshot model.

    The model is not decoration. Every corpus stage falls back to Groq's free
    tier, so the judgement reads which account served the newest row, and a
    fixture that left the model out would exercise the "cannot say" branch
    while looking like the healthy one.
    """
    return {"triage": {"newest": when, "model": model},
            "interpret": {"newest": when, "model": model}}


def receipt(week="2026-W39", created="2026-09-28T09:03:00+00:00",
            papers=None, claims=None, deploy=None, version=None,
            press_present=True, queues="default", distilled="default",
            siblings="default", payments="default", unreadable=None):
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
                     "claims_newest": claims if claims is not None else fresh,
                     "distilled_newest": fresh if distilled == "default" else distilled},
        "siblings": (SIBLINGS(fresh) if siblings == "default" else siblings),
        "queues": QUEUES if queues == "default" else queues,
        "payments": (CLEAR_TILL if payments == "default" else payments),
        "deploy": deploy if deploy is not None else [],
        # Version 6's block, and absent by default rather than empty, because
        # that is what a receipt whose every query ran looks like.
        **({"unreadable": unreadable} if unreadable is not None else {}),
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
    optional in it. `queues` is optional by construction and so is
    `distilled_newest`, which is why both bumps left every older version
    readable instead of costing a window of three unknown surfaces each.
    """
    check("version 1 is in the readable list", 1 in dh.READABLE_VERSIONS)
    payload = receipt(version=1)
    payload.pop("queues", None)
    payload.pop("siblings", None)
    payload["pipeline"].pop("distilled_newest", None)
    with served(status=200, body=payload):
        got, why = dh.read_receipt()
    check("a version 1 receipt is accepted", got is not None, why)
    _, pipeline_row, _, _ = dh.receipt_facts(payload)
    check("and its absent queue depth reads as unknown, not as zero",
          pipeline_row["queues"] is None, str(pipeline_row))
    check("and its absent distill marker reads as unknown too",
          pipeline_row["distilled"] is None, str(pipeline_row))

    # Version 2 is the one actually live while this lands, so it is the window
    # that really happens rather than the one that happened last time.
    live = receipt(version=2)
    live.pop("siblings", None)
    live["pipeline"].pop("distilled_newest", None)
    with served(status=200, body=live):
        got, why = dh.read_receipt()
    check("a version 2 receipt is accepted", got is not None, why)
    _, row2, _, _ = dh.receipt_facts(live)
    check("it keeps its queue depths", row2["queues"] == QUEUES, str(row2))
    check("and its absent marker is still not a stage that never ran",
          row2["distilled"] is None, str(row2))


def test_the_version_three_window_is_the_one_this_change_opens():
    """Version 3 is live while version 4 lands, so it is the window that really
    happens this time rather than the one that happened last time. Its absent
    sibling markers have to read as a fact the reader does not have, and never
    as two stages that have written nothing, because the second of those names
    the Moonshot account as the suspect."""
    live = receipt(version=3)
    live.pop("siblings", None)
    with served(status=200, body=live):
        got, why = dh.read_receipt()
    check("a version 3 receipt is accepted", got is not None, why)
    _, row, _, _ = dh.receipt_facts(live)
    check("it keeps its distill marker", row["distilled"] is not None, str(row))
    check("and its absent sibling block reads as cannot say",
          row["siblings"] is None, str(row))


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
        _, _, deploy_rows, _ = dh.receipt_facts(payload)

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
            # One statement, two columns: (max(fetched_at), max(distilled_at)).
            "max(fetched_at)": (moved, moved),
            "max(created_at) from claims": (moved,),
            "distill_queue": (41, 212, 7),
        })
        direct_press = dh.judge_press(dh.press_facts(conn), today)
        direct_pipeline = dh.judge_pipeline(dh.pipeline_facts(conn))

        payload = receipt(week=week, created=created.strftime(WEEK_FORMAT),
                          papers=moved.strftime(WEEK_FORMAT),
                          claims=moved.strftime(WEEK_FORMAT))
        press_row, pipeline_row, _, _ = dh.receipt_facts(payload)
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

    A stale `claims` has three causes and two facts separate them. The depth
    says whether the stage had anything to read, and `papers.distilled_at` says
    whether it read any of it. The 2026-10-09 ledger entry had to stop at
    "whether it fired and found an empty queue, or whether it fired and raised"
    because the depth needed a credential no seat holds, and the 2026-10-10
    reading stopped one step later, with a depth of 2099 that settled the first
    of those and not the second.

    If the receipt and a connection disagreed about the cause, the seat with no
    credential would read a different diagnosis from the one the owner reads,
    which is worse than the silence it replaced.
    """
    # Whole seconds, because the marker is compared across a round trip through
    # the receipt's own ISO format and that format carries no microseconds. A
    # fixture with them would fail on the formatting rather than on the
    # behaviour, and the behaviour is that both readers reach one sentence.
    moved = (datetime.now(timezone.utc) - timedelta(hours=14)).replace(microsecond=0)
    stalled = (datetime.now(timezone.utc) - timedelta(days=3)).replace(microsecond=0)
    empty = {"triage_pending": 41, "distill_pending": 0, "interpret_pending": 7}

    # The fourth column is the distill marker, and the last three cases are
    # what it was added for: a deep queue is one fact with two causes, and the
    # marker is what picks between them. Each phrase below is the first step a
    # reader would actually take, so a case that named the wrong one would send
    # the owner to the wrong place with full confidence.
    cases = (("an empty queue", (41, 0, 7), empty, moved,
              "distill_queue empty"),
             ("a deep queue the stage read from", (41, 212, 7), QUEUES, moved,
              "it ran and extracted nothing"),
             ("a deep queue the stage never reached", (41, 212, 7), QUEUES, stalled,
              "it never reached a paper"),
             ("a deep queue and no marker", (41, 212, 7), QUEUES, None,
              "no distill marker is readable here"),
             ("no depth at all", None, None, moved,
              "no queue depth is published here"))

    for name, row, published, marker, phrase in cases:
        answers = {"max(fetched_at)": (moved, marker),
                   "max(created_at) from claims": (stalled,)}
        if row is not None:
            answers["distill_queue"] = row
        direct = dh.judge_pipeline(dh.pipeline_facts(FakeConn(answers)))

        # Sibling markers held at absent on both sides, because this test is
        # about the depth and the distill marker. The clause they add is the
        # subject of test_the_sibling_stages_split_the_provider_from_this_one_cron
        # below, and a fixture that published them here while `FakeConn` had no
        # answer for the statement would fail on the difference between two
        # tests rather than on either one's behaviour.
        payload = receipt(papers=moved.strftime(WEEK_FORMAT),
                          claims=stalled.strftime(WEEK_FORMAT),
                          queues=published,
                          distilled=marker.strftime(WEEK_FORMAT) if marker else None,
                          siblings=None)
        _, pipeline_row, _, _ = dh.receipt_facts(payload)
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
        check(f"{name}: and so is the marker, by both readers",
              direct.evidence["distilled"] == via_receipt.evidence["distilled"],
              f"{direct.evidence['distilled']!r} vs "
              f"{via_receipt.evidence['distilled']!r}")

    # A deep queue on a corpus that is still moving is not this surface's
    # alarm. Its unit is staleness, and a depth threshold here would be a
    # second alarm nobody specified.
    healthy = dh.judge_pipeline(dh.pipeline_facts(FakeConn({
        "max(fetched_at)": (moved, moved),
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
    facts = dh.pipeline_facts(NoViews({"max(fetched_at)": (moved, stalled),
                                       "max(created_at) from claims": (stalled,)}))
    check("the depth is None and not zero", facts["queues"] is None)
    surface = dh.judge_pipeline(facts)
    check("the staleness still reports", "claims has not moved in 3 days" in surface.headline)
    check("and the headline says the cause is unavailable",
          "no queue depth is published here" in surface.headline, surface.headline)


# ------------------------------------------------------------- the till

def test_a_till_with_nothing_open_is_green_and_an_unreadable_one_is_unknown():
    """Zero is the good news, and it is only good news when somebody looked.

    `payment_exceptions` is newer than every other table this receipt reads
    and `apply_schema` is a hand step, so a site deployed before the table is
    applied publishes null here. A reader that collapsed null onto zero would
    report a till nobody can see as a till with nothing wrong, which is the
    half of L-A21 this org keeps rediscovering: a gate that saw nothing
    reading as a quiet pass.
    """
    with served(body=receipt()):
        clear = surfaces(today=dh.date(2026, 10, 1))["payments"]
    check("an empty till is ok", clear.state == dh.OK, clear.headline)
    check("and it says so plainly",
          "every verified payment reached an account" == clear.headline)

    for absent in (None, "not a block", 7):
        with served(body=receipt(payments=absent)):
            blind = surfaces(today=dh.date(2026, 10, 1))["payments"]
        check(f"a till published as {absent!r} is unknown, not ok",
              blind.state == dh.UNKNOWN, blind.headline)

    # And an older receipt, which carries no `payments` key at all. The four
    # versions before this one stay readable, so the press and the pipeline
    # still answer through a deploy window, and the till reads unknown rather
    # than clear for exactly the reason above.
    old = receipt(version=4)
    del old["payments"]
    with served(body=old):
        was = surfaces(today=dh.date(2026, 10, 1))
    check("version 4 is still readable", was["press"].state == dh.OK)
    check("and its silence about the till is unknown",
          was["payments"].state == dh.UNKNOWN, was["payments"].headline)


def test_a_refusal_is_an_alarm_from_the_first_row_and_a_retry_is_not():
    """The distinction the whole surface turns on.

    A deferred row is this product's own Clerk webhook not having landed yet,
    which is a race measured in seconds, and alarming on it would make every
    signup-then-buy inside one second a red report. A refused row is somebody
    who paid and will never be let in without the owner doing something: no
    account holds that address, or two accounts do. The grace window for a
    person waiting on the owner is the wrong idea, so there is none.
    """
    today = dh.date(2026, 10, 1)

    refused = TILL(1, 1, 2, [{"code": "no_account", "n": 1}])
    with served(body=receipt(payments=refused)):
        s = surfaces(today=today)["payments"]
    check("one refusal is failing with no grace at all",
          s.state == dh.FAILING, s.headline)
    check("and the headline names the job rather than only the number",
          "no_account" in s.headline and "will not retry" in s.headline,
          s.headline)

    deferred = TILL(2, 0, 1, [{"code": "no_users_row", "n": 2}])
    with served(body=receipt(payments=deferred)):
        s = surfaces(today=today)["payments"]
    check("two fresh deferrals are ok", s.state == dh.OK, s.headline)
    check("and the count is still reported rather than hidden",
          "2 payment(s) deferred" in s.headline, s.headline)


def test_a_retry_that_never_lands_stops_being_a_retry():
    """The case that would otherwise be invisible forever.

    A deferred row is excused because Polar will bring the event back. Six
    hours and many retries later it is not waiting on a race, it is waiting on
    somebody, and nothing else on this page would ever say so: the row is
    retryable, so the refusal count stays zero and the surface would read
    green while a paid customer sat locked out.
    """
    today = dh.date(2026, 10, 1)
    codes = [{"code": "no_users_row", "n": 1}]

    inside = TILL(1, 0, dh.PAYMENT_DEFER_GRACE_HOURS - 1, codes)
    with served(body=receipt(payments=inside)):
        s = surfaces(today=today)["payments"]
    check("an hour inside the window is still the schedule",
          s.state == dh.OK, s.headline)

    outside = TILL(1, 0, dh.PAYMENT_DEFER_GRACE_HOURS + 1, codes)
    with served(body=receipt(payments=outside)):
        s = surfaces(today=today)["payments"]
    check("an hour outside it is an alarm",
          s.state == dh.FAILING, s.headline)
    check("and it says what window was crossed",
          f"{dh.PAYMENT_DEFER_GRACE_HOURS}-hour" in s.headline, s.headline)


def test_the_till_fails_the_command_rather_than_only_colouring_a_line():
    """A surface that cannot change the exit code is a surface nothing reads.

    `exit_code` is what the standup and any future workflow branch on, so a
    red till has to reach it. This is the gate half of the two the register
    rule names: recording the finding and acting on it are different gates and
    the second is the one this org keeps forgetting.
    """
    red = dh.judge_payments({"unresolved": 1, "needs_a_hand": 1,
                             "oldest": datetime.now(timezone.utc),
                             "newest": datetime.now(timezone.utc),
                             "codes": [{"code": "no_account", "n": 1}]})
    check("a refused payment is a non-zero exit", dh.exit_code([red]) == 1)
    check("and the surface is in the default run",
          "payments" in dh.ORDER)
    # Rendered, because a surface missing from `render`'s mark table would
    # raise a KeyError on the one day it was not green.
    check("and it renders", "payments" in dh.render([red]))


def test_a_connection_and_a_receipt_reach_the_same_verdict_about_the_till():
    """The same property the press and the pipeline hold, for the till.

    Two readers of one question is the shape that grows two answers. The
    credentialled reader is the owner's laptop and the Modal jobs; the
    credential-free one is every agent seat. If they disagreed, the standup
    would report a till the owner could not reproduce.
    """
    at = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(hours=9)
    cases = ((0, 0, [], dh.OK),
             (1, 1, [("no_account", 1)], dh.FAILING),
             (3, 1, [("no_users_row", 2), ("ambiguous_email", 1)], dh.FAILING),
             (2, 0, [("no_users_row", 2)], dh.FAILING))

    for unresolved, stuck, codes, expect in cases:
        conn = FakeConn({
            # Keyed on the two statements `payment_facts` runs, in the order it
            # runs them: the aggregate first, then the grouping.
            "filter (where not retryable)":
                (unresolved, stuck, at if unresolved else None,
                 at if unresolved else None),
            "group by reason_code": [(code, n) for code, n in codes],
        })
        direct = dh.judge_payments(dh.payment_facts(conn))

        published = {"unresolved": unresolved, "needs_a_hand": stuck,
                     "oldest_unresolved_at": at.strftime(WEEK_FORMAT) if unresolved else None,
                     "newest_unresolved_at": at.strftime(WEEK_FORMAT) if unresolved else None,
                     "codes": [{"code": code, "n": n} for code, n in codes]}
        _, _, _, till = dh.receipt_facts(receipt(payments=published))
        via_receipt = dh.judge_payments(till, source=dh.RECEIPT_URL)

        label = f"{unresolved} open / {stuck} stuck"
        check(f"{label}: the direct read is {expect}",
              direct.state == expect, direct.headline)
        check(f"{label}: the receipt agrees on the state",
              via_receipt.state == direct.state,
              f"{direct.state} vs {via_receipt.state}")
        check(f"{label}: and on the headline, word for word",
              via_receipt.headline == direct.headline,
              f"{direct.headline!r} vs {via_receipt.headline!r}")
        check(f"{label}: only `read_via` differs",
              direct.evidence["read_via"] == dh.DIRECT
              and via_receipt.evidence["read_via"] == dh.RECEIPT_URL)


def test_a_missing_payments_table_costs_the_till_and_nothing_else():
    """The savepoint, which is load-bearing rather than tidy.

    A failed statement in psycopg aborts the whole transaction, and
    `check_deploy` runs after this on the same connection. Without the
    savepoint a database one migration behind would lose the deploy surface
    too, and the drift alarm would fire on a schema step. `queue_facts` met
    this first and this read is inside the same guard for the same reason.
    """
    class Aborting(FakeConn):
        def __init__(self, sqlstate="42P01"):
            super().__init__({})
            self.inside = False
            self.sqlstate = sqlstate

        def execute(self, sql, params=None):
            if "payment_exceptions" in sql:
                # Shaped like the psycopg error this really meets: the sqlstate
                # is what `why_unreadable` reads, and 42P01 is undefined_table.
                exc = RuntimeError('relation "payment_exceptions" does not exist')
                exc.sqlstate = self.sqlstate
                raise exc
            return _Result(("2026-W39", datetime.now(timezone.utc), "kimi-k2"))

        def transaction(self):
            self.inside = True
            return contextlib.nullcontext()

    conn = Aborting()
    why = dh.payment_facts(conn)
    surface = dh.judge_payments(why)
    check("an absent table is unknown, not failing", surface.state == dh.UNKNOWN)
    check("and the read was inside a savepoint", conn.inside)
    check("so the next surface on the same connection still answers",
          dh.judge_press(dh.press_facts(conn), dh.date(2026, 10, 1)).state == dh.OK)
    # The half this test did not hold until 2026-10-24, which is the whole
    # reason the till read `unknown` in every standup for a month: the surface
    # said it could not look and never said that one hand-run migration was all
    # it was waiting for.
    check("the reason is carried rather than swallowed", why == dh.NO_TABLE, why)
    check("and the headline names the hand that closes it",
          "apply_schema" in surface.headline, surface.headline)
    check("and the evidence carries the reason for a machine reader",
          surface.evidence.get("unreadable") == dh.NO_TABLE)

    other = dh.payment_facts(Aborting(sqlstate="57014"))
    check("a failure that is not a schema gap is not called one",
          other == dh.QUERY_FAILED, other)
    check("and it sends the reader to a log rather than to a migration",
          "apply_schema" not in dh.judge_payments(other).headline)


def test_the_two_readers_reach_the_same_hand_for_an_unreadable_till():
    """The contract the credential-free half of this file rests on, for version 6.

    A receipt and a connection must not reach different first steps from the
    same database. The direct reader classifies a psycopg sqlstate; the site
    classifies the same sqlstate in site/lib/delivery.js and publishes the word
    in `unreadable.payments`. If those two vocabularies drifted, the standup
    and the owner's laptop would disagree about whether a migration was owed.
    """
    class Absent(FakeConn):
        def __init__(self):
            super().__init__({})

        def execute(self, sql, params=None):
            if "payment_exceptions" in sql:
                exc = RuntimeError("undefined table")
                exc.sqlstate = "42P01"
                raise exc
            return _Result(None)

        def transaction(self):
            return contextlib.nullcontext()

    direct = dh.judge_payments(dh.payment_facts(Absent()))
    _, _, _, till = dh.receipt_facts(
        receipt(payments=None, unreadable={"payments": "no such table"}))
    via_receipt = dh.judge_payments(till, source=dh.RECEIPT_URL)

    check("both readers answer unknown",
          direct.state == dh.UNKNOWN and via_receipt.state == dh.UNKNOWN)
    check("and the headline is the same word for word",
          direct.headline == via_receipt.headline,
          f"{direct.headline!r} vs {via_receipt.headline!r}")
    check("and the site's three words are the reader's three words",
          set(dh.UNREADABLE_HANDS) == set(CORE_REASONS),
          f"reader={sorted(dh.UNREADABLE_HANDS)} site={sorted(CORE_REASONS)}")


def test_a_reason_this_reader_does_not_know_claims_nothing():
    """A newer site inventing a fourth reason must not put a first step in a
    report on no evidence. The generic sentence is the honest answer there, and
    `unreadable_reason` is the one place that decides it."""
    _, _, _, till = dh.receipt_facts(
        receipt(payments=None, unreadable={"payments": "the vibes were off"}))
    check("an unknown reason is dropped", till is None)
    surface = dh.judge_payments(till, source=dh.RECEIPT_URL)
    check("so the verdict is the sentence that names no hand",
          surface.state == dh.UNKNOWN and "apply_schema" not in surface.headline,
          surface.headline)
    check("and a receipt with no unreadable block at all behaves the same",
          dh.receipt_facts(receipt(payments=None))[3] is None)


def test_the_receipt_publishes_no_reason_it_does_not_own():
    """The vocabulary is closed on the site's side too.

    `unreadable` is the one block on this receipt built from a value a caught
    exception produced, so it is the one place where an error's own text could
    reach a public response. buildReceipt filters it to three strings this
    codebase chose, and to the four blocks it publishes, so neither a driver
    message nor a key for a block that does not exist comes out.
    """
    check("the vocabulary is frozen", "Object.freeze" in CORE
          and "UNREADABLE_REASONS" in CORE)
    check("every value goes through the filter", "reason(given)" in CORE)
    check("and the blocks it will key are named one by one",
          '["siblings", "queues", "payments", "deploy"]' in CORE)
    check("the site reads the sqlstate and not the message",
          '"42P01"' in READER and '"42703"' in READER)

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


def test_the_sibling_stages_split_the_provider_from_this_one_cron():
    """The property version 4 was added for, held across both readers.

    "Distill never reached a paper" leaves three suspects and its own headline
    names them: the cron, the model availability gate and the spend cap. Two of
    those are the Moonshot organization key that triage, interpret and the
    press share, and one is this job alone, so they do not have the same first
    step and the stall's own markers cannot choose between them.

    Triage runs at 12:00 UTC and interpret at 14:00, both before distill's
    15:00, and triage writes a `triage_log` row for every paper it judges. So a
    sibling row written while distill wrote nothing is evidence the account
    answered a caller, and three stages quiet since the same day are one cause
    rather than three. The sentence has to be identical from a connection and
    from the receipt for the same reason every other sentence here does: the
    seat with no credential and the owner must not read different first steps.
    """
    moved = (datetime.now(timezone.utc) - timedelta(hours=14)).replace(microsecond=0)
    stalled = (datetime.now(timezone.utc) - timedelta(days=3)).replace(microsecond=0)

    kimi, groq = "kimi-k2.6", "openai/gpt-oss-120b"
    cases = (
        ("Moonshot answered a caller", (moved, kimi), (stalled, kimi),
         "the Moonshot account answered a caller after distill stopped"),
        ("the fallback carried the small stages", (moved, groq), (moved, groq),
         "which is the Groq fallback and not Moonshot"),
        ("every stage on the key went quiet", (stalled, kimi), (stalled, kimi),
         "every stage on the shared Moonshot key went quiet together"),
        ("a model no price table knows", (moved, "who-knows-9"), (None, None),
         "no table here says which account served that"),
        ("neither sibling has written at all", (None, None), (None, None),
         "no sibling stage's marker is readable here"),
    )

    for name, triage, interpret, phrase in cases:
        direct = dh.judge_pipeline(dh.pipeline_facts(FakeConn({
            "max(fetched_at)": (moved, stalled),
            "max(created_at) from claims": (stalled,),
            "distill_queue": (41, 212, 7),
            # The two sibling statements, keyed on the table each one reads.
            # A None timestamp stands for an empty table, which `fetchone`
            # answers with no row at all.
            "from triage_log": triage if triage[0] else None,
            "from claim_links": interpret if interpret[0] else None,
        })))

        def published(entry):
            when, model = entry
            return (None if when is None else
                    {"newest": when.strftime(WEEK_FORMAT), "model": model})

        payload = receipt(papers=moved.strftime(WEEK_FORMAT),
                          claims=stalled.strftime(WEEK_FORMAT),
                          distilled=stalled.strftime(WEEK_FORMAT),
                          siblings={"triage": published(triage),
                                    "interpret": published(interpret)})
        _, pipeline_row, _, _ = dh.receipt_facts(payload)
        via_receipt = dh.judge_pipeline(pipeline_row, source=dh.RECEIPT_URL)

        check(f"{name}: both readers say failing",
              direct.state == via_receipt.state == dh.FAILING, direct.headline)
        check(f"{name}: the headline names which of the three it is",
              phrase in direct.headline, direct.headline)
        check(f"{name}: and both readers word it identically",
              direct.headline == via_receipt.headline,
              f"{direct.headline!r} vs {via_receipt.headline!r}")
        check(f"{name}: the markers are in the evidence either way",
              direct.evidence["siblings"] == via_receipt.evidence["siblings"],
              f"{direct.evidence['siblings']!r} vs "
              f"{via_receipt.evidence['siblings']!r}")

    # Two empty tables and a query that could not run are one answer, and that
    # is deliberate rather than a convenience: a reader that reported "no
    # sibling has ever written" from a failed read would name the provider on
    # no evidence at all.
    unreadable = dh.judge_pipeline(dh.pipeline_facts(FakeConn({
        "max(fetched_at)": (moved, stalled),
        "max(created_at) from claims": (stalled,),
        "distill_queue": (41, 212, 7)})))
    check("a sibling read that failed says cannot say, not never wrote",
          "no sibling stage's marker is readable here" in unreadable.headline,
          unreadable.headline)
    check("and it is reported as absent rather than as two nulls",
          unreadable.evidence["siblings"] is None,
          str(unreadable.evidence["siblings"]))

    # A fresh sibling on a corpus that is still moving says nothing at all,
    # because this clause only exists inside a stall. The surface's unit is
    # staleness and these two markers are never an alarm of their own.
    healthy = dh.judge_pipeline(dh.pipeline_facts(FakeConn({
        "max(fetched_at)": (moved, moved),
        "max(created_at) from claims": (moved,),
        "distill_queue": (41, 212, 7),
        "from triage_log": (stalled, "kimi-k2.6"),
        "from claim_links": (stalled, "kimi-k2.6@abc123")})))
    check("a quiet sibling alone does not raise", healthy.state == dh.OK,
          healthy.headline)
    check("but it is still reported",
          healthy.evidence["siblings"]["triage"]["newest"] == str(stalled),
          str(healthy.evidence["siblings"]))
    check("and the prompt sha in claim_links.method never reaches the evidence",
          healthy.evidence["siblings"]["interpret"]["model"] == "kimi-k2.6",
          str(healthy.evidence["siblings"]))


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
