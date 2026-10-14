"""The signup path: the row it writes, the SQL that writes it, and the copy.

    python3 -m pytest tests/test_waitlist.py -q

Sprint 2026-10-05 item 2. Until this change `site/lib/waitlist.js` appended to
a JSONL file on local disk, and its own comment left the database insert as
"the seam the engineer wires later". This file is how that seam is checked
without a Postgres, which this org runs nowhere in CI.

Three tools for three different questions.

The decision logic is executed for real in `tests/waitlist.test.mjs`, which
this file also runs, so one pytest command covers the whole path.

The SQL is parsed with libpg_query, the server's own parser, and every
relation and column it names is resolved against `db/schema.sql`. That is the
check that matters here, because an insert in a serverless route is otherwise
run for the first time by a stranger submitting a form, and a typo in it is a
person lost rather than a build failed. The same technique holds
`tools/graph_audit.py` (tests/test_graph_audit.py) and the two files share the
reasoning rather than the code, since the audit's queries are a dict in Python
and these are template literals in JavaScript.

The copy is read as text, because a form that creates a real subscriber while
promising to write only "on the day subscriptions open" is a broken promise
rather than a broken build, and nothing else in the repository would notice.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sql_schema as q  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = q.SCHEMA
CORE = (ROOT / "site" / "lib" / "waitlist-core.js").read_text()
HELPER = (ROOT / "site" / "lib" / "waitlist.js").read_text()
ROUTE = (ROOT / "site" / "app" / "api" / "waitlist" / "route.js").read_text()
FORM = (ROOT / "site" / "app" / "components" / "Waitlist.jsx").read_text()

code_only = q.strip_comments
parse_one = q.parse_one


# ------------------------------------------------------------------ the SQL
# The parser, the schema resolver and the comment stripper are in
# tests/sql_schema.py, shared with tests/test_unsubscribe.py. That file carries
# the argument for the technique and for why tests/test_graph_audit.py keeps
# its own copy.

def statements():
    return q.literals(HELPER)


def test_there_are_exactly_the_three_statements_this_file_knows_about():
    """A fourth query added without a test is the thing this catches.

    Two inserts (one for a database that has had today's migration and one for
    a database that has not) and the status read that tells a returning
    subscriber from one who never left.
    """
    assert sorted(statements()) == ["INLINE_1", "INSERT_WITHOUT_SOURCE",
                                    "INSERT_WITH_SOURCE"], sorted(statements())


def test_every_statement_parses_as_postgresql():
    """A typo fails the pull request instead of losing a subscriber."""
    for name, sql in statements().items():
        parse_one(sql)


def test_every_relation_and_column_the_signup_names_exists():
    """A typo fails the pull request instead of losing a subscriber.

    `source` resolves only because db/schema.sql gained it in the same change
    as the insert. If a later edit drops the ALTER TABLE and keeps the insert,
    this is the test that fails. `xmax` is PostgreSQL's own column and not in
    any schema file, so it is named here rather than allowed everywhere.
    """
    for name, sql in statements().items():
        q.assert_resolves(name, sql, system={"xmax"})


def test_the_insert_writes_an_active_comped_digest_row():
    """The sprint item, read off the SQL rather than off the helper's comment.

    `status = 'active'` is the whole of it. pipeline/weekly.py selects
    `status = 'active'` and nothing else, so a signup in any other state is a
    row waiting on a human, which clause 1 of the definition of done rules out.
    """
    for name in ("INSERT_WITH_SOURCE", "INSERT_WITHOUT_SOURCE"):
        sql = statements()[name]
        assert type(parse_one(sql).stmt).__name__ == "InsertStmt", name
        assert re.search(r"insert into subscribers", sql, re.I), name
    assert "status: \"active\"" in CORE
    assert "comp: true" in CORE
    assert "tier: \"digest\"" in CORE


def test_no_signup_can_land_in_a_state_the_press_does_not_read():
    """The status check still names two states, and 'waitlist' is not one.

    site/lib/waitlist.js used to ask, in its own comment, for 'waitlist' to be
    added to this constraint. Following that instruction would have rebuilt the
    manual promotion step the sprint item exists to remove, so the instruction
    was dropped rather than followed, and this is the test that keeps it
    dropped.
    """
    body = re.search(r"create table if not exists\s+subscribers\s*\((.*?)\n\);",
                     SCHEMA, re.S | re.I).group(1)
    allowed = re.search(r"status.*?check \(status in \((.*?)\)\)", body, re.S | re.I)
    assert allowed, "subscribers.status accepts any string"
    assert sorted(re.findall(r"'(\w+)'", allowed.group(1))) == ["active", "unsubscribed"]


def test_the_upsert_revives_an_unsubscriber_and_touches_nothing_else():
    """Somebody who unsubscribed in March and signs up in June has asked
    twice, and the second ask is the current one. But if the owner has comped
    or upgraded somebody by hand, a form must not undo it, so the conflict
    branch writes `status` and `unsubscribed_at` and no other column."""
    for name in ("INSERT_WITH_SOURCE", "INSERT_WITHOUT_SOURCE"):
        sql = statements()[name]
        assert "on conflict (email) do update" in sql, name
        clause = sql[sql.index("do update"):]
        clause = clause[:clause.index("returning")]
        written = set(re.findall(r"^\s*(?:set\s+)?(\w+)\s*=", clause, re.M))
        assert written == {"status", "unsubscribed_at"}, (name, written)


def test_the_insert_reports_whether_it_inserted_rather_than_asking_again():
    """A second query to find out would race with a concurrent signup for the
    same address, and `xmax = 0` is the server's own answer."""
    for name in ("INSERT_WITH_SOURCE", "INSERT_WITHOUT_SOURCE"):
        assert "(xmax = 0) as inserted" in statements()[name], name


def test_the_source_column_is_optional_at_the_point_of_insert():
    """`source` and the column arrive in one change, and the deploy that
    applies db/schema.sql is a separate step the owner runs. For the window
    between the merge and that step the column does not exist, so the insert
    falls back rather than refusing the signup. 42703 is undefined_column, and
    it is matched by code because the message is localised and the code is
    not."""
    assert '"42703"' in HELPER
    assert "INSERT_WITHOUT_SOURCE" in HELPER
    assert "source" not in statements()["INSERT_WITHOUT_SOURCE"]
    assert "source" in statements()["INSERT_WITH_SOURCE"]
    line = [l for l in SCHEMA.splitlines()
            if "add column if not exists source" in l][0]
    assert "not null" not in line.lower(), (
        "a not-null column with no default cannot be added to a live table")


# ---------------------------------------------------------------- no file

def test_nothing_on_the_signup_path_writes_to_disk():
    """The holding pen is gone, which is the point. A file on a serverless
    host is a list that can lose the list, which its own comment admitted."""
    for name, text in (("waitlist.js", HELPER), ("route.js", ROUTE),
                       ("waitlist-core.js", CORE)):
        code = code_only(text)
        assert "node:fs" not in code, name
        assert "appendFile" not in code, name
        assert "waitlist.jsonl" not in code, name
        assert "WAITLIST_FILE" not in code, name


def test_the_pure_core_stays_import_free():
    """tests/waitlist.test.mjs loads it by evaluating its source, which only
    works while it has no imports to resolve."""
    assert not re.search(r"^\s*import\s", CORE, re.M)


def test_no_credential_appears_in_any_file_on_this_path():
    """DATABASE_URL by name, read from the environment, never a literal."""
    assert "process.env.DATABASE_URL" in HELPER
    for name, text in (("waitlist.js", HELPER), ("route.js", ROUTE),
                       ("waitlist-core.js", CORE)):
        assert not re.search(r"postgres(ql)?://", text), name
        assert not re.search(r"DATABASE_URL\s*=\s*['\"]", text), name


# ----------------------------------------------------------------- the route

def test_a_bad_address_is_refused_before_the_database_is_opened():
    """The person's own typo gets a 400 they can act on, and it costs no
    round trip. Everything after that point is ours, not theirs."""
    check = ROUTE.index("normalizeEmail(")
    insert = ROUTE.index("subscribe(")
    assert check < insert, "the route inserts before it validates"
    assert "status: 400" in ROUTE


def test_an_unreachable_list_answers_503_and_a_refused_address_400():
    """The status code is the only place the difference survives. The request
    was fine and the list was not, and a 500 says neither."""
    assert "result.retryable ? 503 : 400" in ROUTE
    assert 'retryable: true, reason: "DATABASE_URL is not set"' in HELPER


def test_the_route_never_tells_the_person_which_outcome_they_were():
    """They are on the list in all three cases, and the distinction is for the
    owner's counts. Saying it would only make them wonder."""
    assert "already" not in ROUTE
    assert "resubscribed" not in ROUTE
    assert "{ ok: true, outcome: result.outcome }" in ROUTE


def test_an_error_inside_the_insert_cannot_take_the_endpoint_down():
    assert ".catch(() => ({" in ROUTE


# ------------------------------------------------------------------ the copy

def test_the_form_no_longer_promises_a_single_email_that_never_comes():
    """The submit creates a subscriber the Monday press sends to. The old
    sentence, "We will write on the day subscriptions open", was true of a
    holding pen and is a broken promise now."""
    for stale in ("on the day subscriptions open", "Join the waitlist",
                  "We write once", "We send one email"):
        for page in ("page.jsx", "pricing/page.jsx"):
            text = code_only((ROOT / "site" / "app" / page).read_text())
            assert stale not in text, f"{page} still says {stale!r}"
        assert stale not in code_only(FORM), f"the form still says {stale!r}"


def test_the_form_says_what_actually_happens_next():
    assert "You are subscribed." in FORM
    assert ">Subscribe<" in FORM or '"Subscribe"' in FORM


def test_the_copy_keeps_the_house_voice():
    """No em dash and no semicolon joining two clauses, per
    docs/voice/ban-list.md, over the sentences a stranger reads."""
    sentences = re.findall(r'(?:note=|>)\s*"?([A-Z][^"<>{}]{15,})', FORM)
    assert sentences, "no copy found to check"
    for line in sentences:
        assert "—" not in line, line
        assert ";" not in line, line


# -------------------------------------------------------------- executed js

def test_waitlist_core_logic():
    """Runs tests/waitlist.test.mjs, which executes the real module."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed; run `node --test tests/waitlist.test.mjs`")
    proc = subprocess.run(
        [node, "--test", str(Path(__file__).parent / "waitlist.test.mjs")],
        capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
