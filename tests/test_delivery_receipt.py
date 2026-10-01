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
    check("the only tables read are the four this answers for",
          read == ["claims", "deploy_runtime", "digests", "papers"], str(read))


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
    """A reader that speaks version 1 must refuse a version 2 receipt, and it
    can only do that while the two constants are the same number."""
    m = re.search(r"RECEIPT_VERSION\s*=\s*(\d+)", CORE)
    check("the site declares a version", m is not None)
    check("and the reader speaks the same one",
          m and int(m.group(1)) == dh.RECEIPT_VERSION,
          f"site={m.group(1) if m else None} reader={dh.RECEIPT_VERSION}")


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


def receipt(week="2026-W39", created="2026-09-28T09:03:00+00:00",
            papers=None, claims=None, deploy=None, version=1,
            press_present=True):
    now = datetime(2026, 10, 1, 2, 0, tzinfo=timezone.utc)
    fresh = (now - timedelta(hours=14)).strftime(WEEK_FORMAT)
    return {
        "receipt": "alexandria-delivery",
        "version": version,
        "observed_at": now.strftime(WEEK_FORMAT),
        "press": ({"newest_week": week, "created_at": created, "model": "kimi-k2"}
                  if press_present else None),
        "pipeline": {"papers_newest": papers if papers is not None else fresh,
                     "claims_newest": claims if claims is not None else fresh},
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


def test_a_newer_version_is_refused_rather_than_partly_read():
    """The failure mode this prevents: version 2 renames a field, this reader
    reads the old name, gets None, and reports an empty digests table as a
    press that printed nothing."""
    with served(status=200, body=receipt(version=2)):
        payload, why = dh.read_receipt()
    check("the payload is refused", payload is None)
    check("and the reason names both versions", "version 2" in why and "version 1" in why, why)


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
