"""The unsubscribe path: the token, the SQL, the route's method, and the page.

    python3 -m pytest tests/test_unsubscribe.py -q

Sprint 2026-10-05 item 3, and clause 2 of its definition of done: a subscriber
unsubscribes from the site, "as a request that flips their own row, not a
reply-to-this-email the owner has to read and act on". pipeline/weekly.py said
plainly "No unsubscribe endpoint exists yet" and the foot of every issue has
carried `mailto:...?subject=Unsubscribe` since the press started sending.

The split this file does not cover, said here so the next reader finds it in
the same place as the work. The press still sends the mailto. Putting the real
link in the email means `pipeline/weekly.py` reading `unsubscribe_token` in the
recipient query, which is a change to the press's send path, and the press's
deploy gate (docs/agents/press-rehearsal.md, the third rung of
docs/agents/runtime-changes.md) needs a rehearsal against a real key that no CI
job and no sandbox can run. So the site half lands first and the press half
goes behind that gate.

Three tools, as in tests/test_waitlist.py. The decision logic is executed in
tests/unsubscribe.test.mjs, which this file runs. The SQL is parsed with
libpg_query and resolved against db/schema.sql by tests/sql_schema.py. The
page's copy is read as text, because a page that tells a stranger whether a
token is real is a leak rather than a broken build.
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
CORE = (ROOT / "site" / "lib" / "unsubscribe-core.js").read_text()
HELPER = (ROOT / "site" / "lib" / "unsubscribe.js").read_text()
ROUTE = (ROOT / "site" / "app" / "api" / "unsubscribe" / "route.js").read_text()
PAGE = (ROOT / "site" / "app" / "unsubscribe" / "page.jsx").read_text()


def statements():
    return q.literals(HELPER)


def the_one(fragment):
    """The single statement containing `fragment`, or a clear failure."""
    hits = {n: s for n, s in statements().items() if fragment in s}
    assert len(hits) == 1, f"{len(hits)} statements contain {fragment!r}: {sorted(hits)}"
    return next(iter(hits.values()))


# ---------------------------------------------------------------- the schema

def test_the_token_column_exists_and_is_unique():
    """Unique because the token is the only thing identifying the subscriber.
    Two rows sharing one would make "whose link is this" ambiguous, and the
    update would silently unsubscribe whichever row the planner reached."""
    assert "alter table subscribers add column if not exists unsubscribe_token uuid" in SCHEMA
    assert re.search(
        r"create unique index if not exists\s+subscribers_unsubscribe_token_idx\s*"
        r"\n?\s*on subscribers\s*\(\s*unsubscribe_token\s*\)",
        SCHEMA, re.I)


def test_every_existing_subscriber_gets_a_token_of_their_own():
    """The reason the column is not `not null default gen_random_uuid()`.

    A volatile default on ADD COLUMN forces a table rewrite, and the per-row
    evaluation is a property of that rewrite. This org runs no Postgres in CI,
    so that property cannot be tested here, and if the expression were ever
    evaluated once instead of per row then every subscriber would share a token
    and any of them could unsubscribe all of them. An UPDATE has no such
    ambiguity, so the column arrives nullable and an UPDATE fills it.
    """
    assert re.search(
        r"update subscribers set unsubscribe_token = gen_random_uuid\(\)\s*"
        r"\n?\s*where unsubscribe_token is null;", SCHEMA, re.I)
    line = [l for l in SCHEMA.splitlines()
            if "add column if not exists unsubscribe_token" in l][0]
    assert "not null" not in line.lower()
    assert "default" not in line.lower()


def test_the_default_is_set_for_rows_that_do_not_exist_yet():
    """SET DEFAULT applies to future inserts and rewrites nothing, so it has
    none of the ambiguity above and still means a new subscriber never needs
    the backfill to have run again."""
    assert ("alter table subscribers alter column unsubscribe_token "
            "set default gen_random_uuid();") in SCHEMA


def test_the_migration_is_idempotent_because_the_file_is_applied_in_full():
    """pipeline/db_setup.py applies db/schema.sql every time it runs, so a
    statement that is not safe to repeat is a statement that breaks the next
    deploy. The backfill's `where ... is null` is what makes it safe."""
    block = SCHEMA[SCHEMA.index("add column if not exists unsubscribe_token"):]
    block = block[:block.index("subscribers_unsubscribe_token_idx")]
    assert "if not exists" in block
    assert "is null" in block


def test_unsubscribed_is_already_a_legal_status():
    """The endpoint writes a state the schema has always allowed, so nothing
    about this change widens what a subscriber row may say."""
    allowed = re.search(r"status.*?check \(status in \((.*?)\)\)",
                        q.table_body("subscribers"), re.S | re.I)
    assert "'unsubscribed'" in allowed.group(1)


# ------------------------------------------------------------------- the SQL

def test_there_are_exactly_the_three_statements_this_file_knows_about():
    """A fourth query added without a test is the thing this catches."""
    assert len(statements()) == 3, sorted(statements())


def test_every_relation_and_column_the_endpoint_names_exists():
    """A typo here is a subscriber who cannot leave, found by them and not by
    us. `unsubscribe_token` resolves only because db/schema.sql gained it in
    the same change."""
    for name, sql in statements().items():
        q.assert_resolves(name, sql)


def test_the_update_flips_status_and_the_date_and_nothing_else():
    sql = the_one("update subscribers")
    stmt = q.parse_one(sql).stmt
    assert type(stmt).__name__ == "UpdateStmt"
    assert q.written_columns(stmt) == {"status", "unsubscribed_at"}


def test_the_update_is_scoped_to_the_token_and_never_to_an_address():
    """An endpoint that accepted an email would let anybody who knows an
    address remove that person. The token is the whole authorisation."""
    sql = the_one("update subscribers")
    assert "where unsubscribe_token = $1" in sql
    assert "email" not in sql.split("returning")[0]


def test_a_second_click_writes_nothing_and_keeps_the_original_date():
    """`unsubscribed_at` should say when they asked, not when they last
    clicked a link in an email they kept."""
    sql = the_one("update subscribers")
    assert "and status <> 'unsubscribed'" in sql


def test_the_lookups_only_read():
    for name, sql in statements().items():
        if "update subscribers" in sql:
            continue
        assert type(q.parse_one(sql).stmt).__name__ == "SelectStmt", name


def test_nothing_on_this_path_selects_a_whole_row():
    """`select *` from a table of people's addresses, into a page, is how an
    extra column added later becomes an extra column published later."""
    for name, sql in statements().items():
        assert "*" not in sql, name


# ----------------------------------------------------------------- the route

def test_the_api_route_exports_post_and_no_get():
    """The property the whole design rests on. Mail scanners, link previewers
    and corporate security proxies fetch every link in a message before any
    person reads it, so a GET that flipped the row would unsubscribe people who
    never clicked anything. Verified live as well: GET /api/unsubscribe answers
    405."""
    assert "export async function POST(" in ROUTE
    assert "export async function GET(" not in ROUTE
    assert not re.search(r"^export (async )?function (GET|HEAD|PUT|DELETE)",
                         q.strip_comments(ROUTE), re.M)


def test_the_page_changes_nothing_on_load():
    """It reads who the token belongs to so the person can see the address
    they are about to remove, and the only write is behind the form's POST."""
    code = q.strip_comments(PAGE)
    assert "subscriberForToken" in code
    assert "unsubscribeByToken" not in code
    assert 'method="post"' in code
    assert 'action="/api/unsubscribe"' in code


def test_the_token_is_accepted_from_the_query_as_well_as_the_form():
    """RFC 8058 one-click unsubscribe, which is what a mail client's own
    Unsubscribe button performs. The receiver POSTs to the URI in the
    `List-Unsubscribe` header with the fixed body `List-Unsubscribe=One-Click`,
    so the token can only be in the query string for that caller. Reading both
    is what lets the press add the header later without a second endpoint.

    It does not reopen the scanner problem the confirm page exists for, because
    the route is still POST-only, which the test above holds.
    """
    code = q.strip_comments(ROUTE)
    assert 'url.searchParams.get("t")' in code
    assert 'form.get("t")' in code


def test_the_answer_comes_back_as_a_redirect_the_back_button_cannot_resubmit():
    assert "NextResponse.redirect(back, 303)" in ROUTE


def test_no_address_rides_back_in_the_redirect():
    """An email address in a URL ends up in browser history, in a referrer
    header and in any log the request passes through. The person already knows
    which address they just removed."""
    redirect = ROUTE[ROUTE.index('const back = new URL("/unsubscribe"'):]
    assert "email" not in redirect
    assert 'back.searchParams.set("state", state)' in redirect
    assert redirect.count("searchParams.set(") == 1


def test_an_error_inside_the_update_cannot_take_the_endpoint_down():
    assert ".catch(() => ({" in ROUTE
    assert ".catch(() => ({" in q.strip_comments(PAGE)


def test_no_credential_appears_in_any_file_on_this_path():
    assert "process.env.DATABASE_URL" in HELPER
    for name, text in (("unsubscribe.js", HELPER), ("route.js", ROUTE),
                       ("unsubscribe-core.js", CORE), ("page.jsx", PAGE)):
        assert not re.search(r"postgres(ql)?://", text), name
        assert not re.search(r"DATABASE_URL\s*=\s*['\"]", text), name


def test_the_pure_core_stays_import_free():
    """tests/unsubscribe.test.mjs loads it by evaluating its source, which
    only works while it has no imports to resolve."""
    assert not re.search(r"^\s*import\s", CORE, re.M)


# ------------------------------------------------------------------ the page

def test_the_page_never_tells_a_stranger_whether_a_token_is_real():
    """A token nobody recognises and a token that was right once are
    indistinguishable from the server, and saying "that link is invalid" to one
    and something else to the other would be a way to test addresses."""
    assert "invalid" not in PAGE.lower()
    assert "not found" not in PAGE.lower()
    assert "We could not read that link." in PAGE


def test_all_four_states_have_their_own_words():
    for state in ("done", "already", "unavailable", "unknown"):
        assert f'state === "{state}"' in PAGE, state
    for heading in ("You are unsubscribed.", "You were already unsubscribed.",
                    "We could not read that link.",
                    "We cannot reach the list right now."):
        assert heading in PAGE, heading


def test_an_unreachable_list_is_ours_and_says_so():
    """The person did nothing wrong and there is nothing for them to fix, so
    the page must not send them looking."""
    assert "This is ours, not yours." in PAGE


def test_the_copy_keeps_the_house_voice():
    """No em dash and no semicolon joining two clauses, per
    docs/voice/ban-list.md, over the sentences a stranger reads."""
    lines = re.findall(r"^\s{6,}([A-Z][^<>{}]{15,})$", q.strip_comments(PAGE), re.M)
    assert len(lines) >= 4, lines
    for line in lines:
        assert "—" not in line, line
        assert ";" not in line, line


# -------------------------------------------------------------- executed js

def test_unsubscribe_core_logic():
    """Runs tests/unsubscribe.test.mjs, which executes the real module."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed; run "
                    "`node --test tests/unsubscribe.test.mjs`")
    proc = subprocess.run(
        [node, "--test", str(Path(__file__).parent / "unsubscribe.test.mjs")],
        capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
