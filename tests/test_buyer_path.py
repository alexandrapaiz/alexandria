"""The buyer's path: the SQL that records it, the verdict over it, and the promise.

    python3 -m pytest tests/test_buyer_path.py -q

Board card c688ef2e, "Build a way to measure the buyer's path". Four tools for
four different questions, which is the shape tests/test_waitlist.py set.

The decision logic in JavaScript is executed for real in
`tests/path.test.mjs`, which this file also runs, so one pytest command covers
the whole path.

The SQL is parsed with libpg_query, the server's own parser, and every relation
and column it names is resolved against `db/schema.sql`. That is the check that
matters for a serverless insert, because the alternative first run of it is a
stranger opening a page. tests/sql_schema.py carries the argument for the
technique.

The verdict is executed here, because it is Python and because the states it
can report are the whole value of the file. A measurement that reports zero
when it means "I could not look" is worse than no measurement, and four of the
tests below exist only to hold that line.

And the promise is read as text. `site/app/privacy/page.jsx` tells a reader
there is no third-party script watching them read, and that page is the reason
this measurement has no identifier in it. A later change that adds one would
pass every other test in this repository and break a promise to a person, so
the page and the schema are checked against each other here.
"""

import json
import re
import shutil
import subprocess
import sys
import urllib.error
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sql_schema as q  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import buyer_path as bp  # noqa: E402

SCHEMA = q.SCHEMA
CORE = (ROOT / "site" / "lib" / "path-core.js").read_text()
HELPER = (ROOT / "site" / "lib" / "path.js").read_text()
ROUTE = (ROOT / "site" / "app" / "api" / "funnel" / "route.js").read_text()
MIDDLEWARE = (ROOT / "site" / "middleware.js").read_text()
PRIVACY = (ROOT / "site" / "app" / "privacy" / "page.jsx").read_text()

code_only = q.strip_comments


def flowed(text: str) -> str:
    """One line, single-spaced. Every page in this repository wraps its prose,
    so a sentence a reader sees as one line is three lines in the file and a
    plain `in` check on it fails for a reason that has nothing to do with the
    copy. docs/voice/check_voice.py normalises whitespace for the same reason.
    """
    return " ".join(code_only(text).split())


# ------------------------------------------------------------------ the SQL


def statements():
    return q.literals(HELPER)


def test_there_are_exactly_the_four_statements_this_file_knows_about():
    """A fifth query added without a test is the thing this catches.

    One insert, the counts by step, the counts by skill, and the paying
    accounts read out of the billing record rather than counted here.
    """
    assert sorted(statements()) == ["INLINE_1", "INLINE_2", "INLINE_3", "INLINE_4"]


def test_every_statement_parses_as_postgresql():
    for name, sql in statements().items():
        q.parse_one(sql)


def test_every_relation_and_column_the_measurement_names_exists():
    """A typo fails the pull request instead of losing every count silently.

    `path_events` resolves only because db/schema.sql gained it in the same
    change as the insert. If a later edit drops the table and keeps the
    insert, this is the test that fails.
    """
    for name, sql in statements().items():
        q.assert_resolves(name, sql)


def test_the_insert_writes_three_columns_and_no_fourth():
    """The row is a step, a path and a detail. A fourth column written here
    would be the one change to this file that breaks a promise on the live
    privacy page rather than a build, so it is named rather than left to
    review."""
    stmt = q.parse_one(statements()["INLINE_1"]).stmt
    assert type(stmt).__name__ == "InsertStmt"
    assert q.written_columns(stmt) == {"step", "path", "detail"}


def test_every_read_is_bounded_by_a_window():
    """An unbounded count over a growing table answers a question nobody
    asked, and the endpoint that calls these is public."""
    for name in ("INLINE_2", "INLINE_3"):
        assert "make_interval" in statements()[name], name
    # The clamp, not just its presence. A caller cannot turn a public endpoint
    # into a full scan by asking for ten thousand days, and cannot ask for
    # zero either, which would be a window no row can fall inside.
    assert "MAX_DAYS = 90" in HELPER
    for call in ("clampDays(days)",):
        assert call in HELPER, call
    assert re.search(r"Math\.min\(MAX_DAYS, Math\.max\(1,", HELPER)


def test_the_skill_read_is_capped_as_well_as_windowed():
    assert "limit $1" in statements()["INLINE_3"]
    assert "SKILL_LIMIT" in HELPER


def test_the_step_the_schema_accepts_is_checked_rather_than_free_text():
    """The funnel is grouped by `step`, so a typo would quietly become a sixth
    step rather than an error. tests/path.test.mjs asserts the schema's five
    words and the core's five words are one list; this asserts the constraint
    exists at all."""
    body = q.table_body("path_events")
    assert re.search(r"check \(step in \(", body, re.I), (
        "path_events.step accepts any string")


def test_the_table_holds_no_column_that_could_identify_a_person():
    """The whole design, as a refusal. Checked against the schema rather than
    against the comment above it, because the comment is not what runs."""
    body = q.table_body("path_events")
    columns = set(re.findall(r"^\s{4}(\w+)\s", body, re.M))
    assert columns == {"id", "step", "path", "detail", "occurred_at"}, columns
    for banned in ("ip", "ip_address", "user_agent", "visitor", "session",
                   "fingerprint", "clerk_id", "email", "referrer", "cookie"):
        assert banned not in columns, f"path_events carries {banned}"


# ------------------------------------------------------------------ the promise


def test_the_privacy_page_no_longer_claims_there_is_no_analytics():
    """The sentence this measurement had to survive.

    Until this change the live page said "There is no analytics, no tracking
    pixel, no advertising network, and no third-party script watching you
    read". Counting page views makes the first clause false, so it was
    rewritten rather than left to go stale. This is the test that stops it
    coming back on a later copy pass.
    """
    prose = flowed(PRIVACY)
    assert "There is no analytics" not in prose
    assert "no tracking pixel" in prose
    assert "no third-party script watching you read" in prose


def test_the_privacy_page_says_what_a_page_count_actually_holds():
    """A policy that is silent about a thing the product does is the same
    defect as one that denies it."""
    prose = flowed(PRIVACY)
    assert "Page counts." in prose
    for promise in ("No cookie is set", "your browser is not fingerprinted",
                    "There is no identifier in it"):
        assert promise in prose, promise


def test_the_policy_date_moved_with_the_policy():
    """The page's own last section says the date changes when the policy
    changes in a way that matters. Adding a collected thing is that."""
    assert "Last updated 18 October 2026" in flowed(PRIVACY)


def test_nothing_on_the_measuring_path_reaches_for_an_identifier():
    """The same list tests/path.test.mjs checks the JavaScript against, over
    the Python too, so the reader cannot reintroduce what the recorder
    refuses."""
    reader = (ROOT / "tools" / "buyer_path.py").read_text()
    for name, text in (("path-core.js", CORE), ("path.js", HELPER),
                       ("route.js", ROUTE), ("middleware.js", MIDDLEWARE)):
        code = code_only(text)
        for banned in ("x-forwarded-for", "user-agent", "createHash",
                       "localStorage", "cookies.get"):
            assert banned not in code, f"{name} reaches for {banned}"
    assert "x-forwarded-for" not in reader


def test_no_credential_appears_in_any_file_on_this_path():
    """DATABASE_URL by name, read from the environment, never a literal."""
    assert "process.env.DATABASE_URL" in HELPER
    for name, text in (("path.js", HELPER), ("route.js", ROUTE),
                       ("path-core.js", CORE), ("middleware.js", MIDDLEWARE)):
        assert not re.search(r"postgres(ql)?://", text), name
        assert not re.search(r"DATABASE_URL\s*=\s*['\"]", text), name
    reader = (ROOT / "tools" / "buyer_path.py").read_text()
    assert not re.search(r"gh[pousr]_[A-Za-z0-9]{10,}", reader)


def test_the_pure_core_stays_import_free():
    """tests/path.test.mjs loads it by evaluating its source, which only works
    while it has no imports to resolve."""
    assert not re.search(r"^\s*import\s", CORE, re.M)


# --------------------------------------------------------------- the recorder


def facts(**over):
    """A funnel receipt as the site publishes it, with the fields a test varies."""
    rows = [{"step": s, "events": 0, "measured": True, "note": None}
            for s in bp.PATH_STEPS]
    base = {
        "receipt": "alexandria-funnel",
        "ok": True,
        "days": 7,
        "off": False,
        "counts_read": True,
        "counts_reason": None,
        "last_record_error": None,
        "skills": [],
        "skills_reason": None,
        "funnel": {"rows": rows, "rate": None, "rate_reason": "..."},
    }
    if "counts" in over:
        counts = over.pop("counts")
        for row in rows:
            row["events"] = counts.get(row["step"], 0)
    if "extra_rows" in over:
        rows.extend(over.pop("extra_rows"))
    base.update(over)
    return base


def test_a_deploy_without_the_endpoint_is_unknown_and_never_failing():
    """The window between the merge that adds /api/funnel and the build that
    ships it. A red tick there is one every other seat then inherits through
    its own merge check and cannot tell from its own, which the charter's
    register step names as the reason a red main outranks the sprint."""
    surface = bp.judge_recorder(bp.NOT_DEPLOYED)
    assert surface.state == bp.UNKNOWN


def test_any_other_unreachable_funnel_is_failing():
    for reason in ["https://x/api/funnel answered 500",
                   "https://x/api/funnel never answered: timed out"]:
        assert bp.judge_recorder(reason).state == bp.FAILING, reason


def test_an_unreadable_table_is_failing_and_carries_the_reason():
    surface = bp.judge_recorder(
        facts(counts_read=False, counts_reason="path_events does not exist yet"))
    assert surface.state == bp.FAILING
    assert "does not exist yet" in surface.detail


def test_an_insert_that_failed_is_read_before_the_counts_are():
    """The one fault a count of zero hides completely. A recorder whose last
    insert threw reports failing even though every count it publishes is a
    perfectly readable zero."""
    surface = bp.judge_recorder(facts(last_record_error="connection closed"))
    assert surface.state == bp.FAILING
    assert "connection closed" in surface.detail


def test_a_readable_empty_table_is_idle_and_says_what_it_cannot_tell():
    """The state that keeps the report readable before launch, and the one
    that must never be called ok. An empty table is not proof the recorder
    works."""
    surface = bp.judge_recorder(facts())
    assert surface.state == bp.IDLE
    assert "quiet week" in surface.detail


def test_a_table_with_rows_is_ok_and_counts_them():
    surface = bp.judge_recorder(facts(counts={"visit": 4, "skill": 2}))
    assert surface.state == bp.OK
    assert surface.evidence["recorded"] == 6


def test_the_switch_being_off_is_unknown_and_is_read_before_the_counts():
    """PATH_MEASUREMENT=off is the owner's to hold. The counts under it are a
    frozen number that would otherwise read as live, which is why this is
    checked ahead of them rather than after."""
    surface = bp.judge_recorder(facts(off=True, counts={"visit": 99}))
    assert surface.state == bp.UNKNOWN
    assert "PATH_MEASUREMENT is off" in surface.detail


# ------------------------------------------------------------------ the steps


def test_the_seven_steps_print_in_the_order_a_buyer_walks_them():
    """The install sits between the catalogue and the pricing page, where the
    gap actually is, rather than appended at the end where a reader would take
    it for the last thing a buyer does."""
    assert bp.ORDER == ["visit", "catalog", "skill", "install", "pricing",
                        "checkout", "payment"]


def test_every_step_carries_a_sentence_saying_what_it_means():
    assert set(bp.MEANS) == set(bp.ORDER)
    for step, means in bp.MEANS.items():
        assert means and means[0].islower(), step


def test_an_unmeasured_step_reads_unmeasured_and_never_zero():
    data = facts()
    steps = bp.steps_of(data, {"clones": None, "reason": "403"},
                        bp.judge_recorder(data))
    install = [s for s in steps if s["step"] == "install"][0]
    assert install["events"] is None
    assert install["measured"] is False
    assert install["note"] == "403"


def test_a_zero_is_withdrawn_when_the_recorder_was_not_proved_to_work():
    """The distinction the whole file turns on. A failing recorder publishes
    readable zeros, and printing them would be a claim nobody made."""
    data = facts(last_record_error="connection closed")
    recorder = bp.judge_recorder(data)
    assert recorder.state == bp.FAILING
    for step in bp.steps_of(data, {"clones": None}, recorder):
        if step["step"] in bp.PATH_STEPS:
            assert step["measured"] is False, step["step"]
            assert step["events"] is None, step["step"]


def test_a_zero_stands_when_the_recorder_is_idle_or_working():
    for data in (facts(), facts(counts={"visit": 3})):
        recorder = bp.judge_recorder(data)
        for step in bp.steps_of(data, {"clones": None}, recorder):
            if step["step"] in bp.PATH_STEPS:
                assert step["measured"] is True, (recorder.state, step["step"])


def test_the_install_count_arrives_with_no_other_change_the_day_it_can():
    data = facts(counts={"visit": 10})
    steps = bp.steps_of(data, {"clones": 7, "reason": None},
                        bp.judge_recorder(data))
    install = [s for s in steps if s["step"] == "install"][0]
    assert install["events"] == 7
    assert install["measured"] is True


# ------------------------------------------------------------------- the drop


def test_the_drop_is_two_counts_and_never_a_percentage():
    data = facts(counts={"visit": 100, "catalog": 10, "skill": 9,
                         "pricing": 8, "checkout": 1})
    steps = bp.steps_of(data, {"clones": None}, bp.judge_recorder(data))
    drop = bp.biggest_drop(steps)
    assert drop["from"] == "visit" and drop["to"] == "catalog"
    assert drop["lost"] == 90
    assert "percent" not in json.dumps(drop)


def test_an_unmeasured_step_is_skipped_rather_than_breaking_the_chain():
    """The install is unmeasured today and a reader still wants to know what
    happens between the catalogue and the pricing page."""
    data = facts(counts={"visit": 10, "catalog": 9, "skill": 8,
                         "pricing": 2, "checkout": 1})
    steps = bp.steps_of(data, {"clones": None}, bp.judge_recorder(data))
    drop = bp.biggest_drop(steps)
    assert drop["from"] == "skill" and drop["to"] == "pricing"
    assert drop["lost"] == 6


def test_no_drop_is_reported_from_one_measured_step():
    steps = [{"step": "visit", "events": 1, "measured": True},
             {"step": "catalog", "events": None, "measured": False}]
    assert bp.biggest_drop(steps) is None


def test_a_step_that_gained_is_not_a_drop():
    """A page a buyer lands on directly can outcount the one before it, and
    calling that a negative drop would be arithmetic rather than a finding."""
    steps = [{"step": "visit", "events": 2, "measured": True},
             {"step": "catalog", "events": 5, "measured": True}]
    assert bp.biggest_drop(steps) is None


def test_the_report_refuses_a_rate_in_the_field_a_script_reads():
    data = bp.report(url="http://127.0.0.1:1/api/funnel", slug="a/b", token="")
    assert data["rate"] is None
    assert "not counts of people" in data["rate_reason"]


# ----------------------------------------------------------------- the install


class FakeHTTPError(urllib.error.HTTPError):
    def __init__(self, code):
        super().__init__("https://api.github.com", code, "no", {}, None)

    def read(self):
        return b"{}"


def test_a_403_names_the_one_permission_between_this_and_an_install_count(monkeypatch):
    """The live state of this org on the day this shipped, and the reason the
    step is `unmeasured` rather than absent. A reader who is told only that it
    failed cannot act; a reader who is told the permission can."""
    monkeypatch.setattr(bp.urllib.request, "urlopen",
                        lambda *a, **k: (_ for _ in ()).throw(FakeHTTPError(403)))
    out = bp.clone_facts("a/b", token="t")
    assert out["clones"] is None
    assert "administration: read" in out["reason"]
    assert bp.judge_install(out).state == bp.UNKNOWN


def test_a_404_is_a_wrong_repository_and_not_a_missing_permission(monkeypatch):
    """Two refusals that need different hands, so they are not one message."""
    monkeypatch.setattr(bp.urllib.request, "urlopen",
                        lambda *a, **k: (_ for _ in ()).throw(FakeHTTPError(404)))
    out = bp.clone_facts("a/b", token="t")
    assert "no repository a/b" in out["reason"]


def test_no_token_is_said_plainly_rather_than_attempted():
    out = bp.clone_facts("a/b", token="")
    assert out["clones"] is None
    assert "GH_TOKEN" in out["reason"]


def test_a_clone_count_is_labelled_with_githubs_own_window(monkeypatch):
    """GitHub's window is fourteen days and is not configurable, so the number
    carries its own period rather than the one that was asked for. A count
    over a different window than the steps around it, reported as though it
    matched, is the quiet kind of wrong."""

    class Response:
        def read(self):
            return json.dumps({"count": 12, "uniques": 5}).encode()

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(bp.urllib.request, "urlopen", lambda *a, **k: Response())
    out = bp.clone_facts("a/b", token="t")
    assert out["clones"] == 12 and out["window_days"] == 14
    assert bp.judge_install(out).state == bp.OK


def test_the_repository_whose_clones_are_counted_is_read_off_the_manifest():
    """Not written twice. tools/check_plugin_manifest.py already holds that the
    install line and the manifest agree, so reading the same file is what keeps
    the install count pointed at the repository a buyer actually clones."""
    assert bp.repo_slug() == "alexandrapaiz/alexandria"


def test_a_missing_or_broken_manifest_falls_back_rather_than_throwing(tmp_path):
    assert bp.repo_slug(tmp_path / "nope.json") == bp.FALLBACK_REPO
    broken = tmp_path / "plugin.json"
    broken.write_text("{not json")
    assert bp.repo_slug(broken) == bp.FALLBACK_REPO


# ----------------------------------------------------------------- the payment


def test_no_paying_account_is_idle_and_not_a_failure():
    """ADR-30 keeps the door shut until the owner creates the Polar account,
    so a red tick here would land on a correct deploy every day."""
    data = facts(extra_rows=[{"step": "payment", "events": 0, "measured": True}])
    assert bp.judge_payment(data).state == bp.IDLE


def test_an_unreadable_billing_record_is_unknown_and_not_zero():
    data = facts(extra_rows=[{"step": "payment", "events": None,
                              "measured": False, "note": "no database"}])
    surface = bp.judge_payment(data)
    assert surface.state == bp.UNKNOWN
    assert "no database" in surface.detail


def test_a_paying_account_is_ok():
    data = facts(extra_rows=[{"step": "payment", "events": 3, "measured": True}])
    assert bp.judge_payment(data).state == bp.OK


# ------------------------------------------------------------------ the skills


def test_the_most_opened_skills_are_named_because_that_is_the_cards_question():
    """"Without it nobody can tell which skill actually sells" is the card's
    own sentence."""
    data = facts(skills=[{"skill": "harness-engineering", "events": 9},
                         {"skill": "agent-memory-selection", "events": 4}])
    surface = bp.judge_skills(data)
    assert surface.state == bp.OK
    assert "harness-engineering (9)" in surface.detail


def test_no_skill_opened_is_idle_and_an_unreadable_list_is_unknown():
    assert bp.judge_skills(facts(skills=[])).state == bp.IDLE
    assert bp.judge_skills(
        facts(skills=None, skills_reason="no database")).state == bp.UNKNOWN


# ---------------------------------------------------------------- the exit code


def test_the_exit_code_separates_failing_from_unanswerable(monkeypatch):
    """0 every surface ok, 1 something failing, 2 nothing failing and
    something unanswered. The same ladder tools/delivery_health.py uses, so a
    caller does not have to parse prose to tell those three apart."""
    cases = [
        (facts(counts={"visit": 2}), {"clones": 3}, 0),
        (facts(counts_read=False, counts_reason="x"), {"clones": 3}, 1),
        (facts(counts={"visit": 2}), {"clones": None, "reason": "403"}, 2),
    ]
    for data, install, expected in cases:
        data = dict(data)
        data["skills"] = [{"skill": "a", "events": 1}]
        data["funnel"]["rows"] = data["funnel"]["rows"] + [
            {"step": "payment", "events": 1, "measured": True}]
        monkeypatch.setattr(bp, "funnel_facts", lambda url, d=data: d)
        monkeypatch.setattr(bp, "clone_facts", lambda slug, token=None, i=install: i)
        assert bp.report()["exit"] == expected, (expected, data["counts_read"])


def test_the_report_renders_without_a_funnel_rather_than_throwing():
    """Every seat runs this with no credential and against a site that may be
    mid-deploy, so the unhappy path is the common one."""
    data = bp.report(url="http://127.0.0.1:1/api/funnel", slug="a/b", token="")
    text = bp.render(data)
    assert "the buyer's path" in text
    assert "could not be read" in text


def test_an_unknown_surface_name_is_refused_rather_than_silently_empty(capsys):
    assert bp.main(["--surface", "nope", "--url", "http://127.0.0.1:1/x"]) == 2


# ------------------------------------------------------------------ executed js


def test_path_core_logic():
    """Runs tests/path.test.mjs, which executes the real module."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed; run `node --test tests/path.test.mjs`")
    proc = subprocess.run(
        [node, "--test", str(Path(__file__).parent / "path.test.mjs")],
        capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
