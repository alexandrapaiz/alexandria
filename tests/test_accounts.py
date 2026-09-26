"""The accounts layer (ADR-30): the schema's linkage and the webhook's guards.

    python3 -m pytest tests/ -q

Two things are checked here and they need different tools.

The schema is read as SQL text, because applying it needs a Postgres with
pgvector and there is not one in this checkout. So these assert the
structural facts the linkage depends on, which is what would actually
break: the unique index that makes the join single-valued, the left join
that keeps an account without a subscription legal, and the absence of any
foreign key between users and subscribers, since merging those two tables
is the thing ADR-30 says not to do.

The route is read as source for its ordering guarantees, and its decision
logic is executed for real in tests/accounts.test.mjs, which this file also
runs so that one pytest command covers the whole layer.
"""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCHEMA = (REPO / "db" / "schema.sql").read_text()
ROUTE = (REPO / "site" / "app" / "api" / "clerk-webhook" / "route.js").read_text()
CORE = (REPO / "site" / "lib" / "account-core.js").read_text()
HELPER = (REPO / "site" / "lib" / "account.js").read_text()


def create_table(name):
    """The body of `create table if not exists <name> ( ... );`."""
    m = re.search(
        r"create table if not exists\s+%s\s*\((.*?)\n\);" % name,
        SCHEMA,
        re.S | re.I,
    )
    assert m, f"no create table for {name}"
    return m.group(1)


def create_view(name):
    m = re.search(
        r"create or replace view\s+%s\s+as(.*?);" % name, SCHEMA, re.S | re.I
    )
    assert m, f"no view {name}"
    return m.group(1)


# ---------------------------------------------------------------- schema

def test_users_table_has_the_columns_adr_30_names():
    body = create_table("users")
    assert re.search(r"clerk_id\s+text\s+primary key", body, re.I)
    assert re.search(r"email\s+text\s+not null", body, re.I)
    assert re.search(r"\bname\s+text", body, re.I)
    assert re.search(r"created_at\s+timestamptz\s+not null\s+default now\(\)", body, re.I)
    assert re.search(r"subscription_status\s+text\s+not null\s+default 'free'", body, re.I)
    assert re.search(r"polar_customer_id\s+text", body, re.I)


def test_polar_column_is_nullable_because_payments_are_not_open():
    """The door is closed this release, so nothing can be required to fill it."""
    line = [l for l in create_table("users").splitlines() if "polar_customer_id" in l][0]
    assert "not null" not in line.lower()


def test_email_uniqueness_is_case_insensitive():
    """A plain unique(email) would let two accounts differ only by case, and
    then 'the user for this subscriber' would have two honest answers."""
    assert re.search(
        r"create unique index if not exists\s+users_email_lower_idx\s+on users\s*\(\s*lower\(email\)\s*\)",
        SCHEMA,
        re.I,
    )
    body = create_table("users")
    assert not re.search(r"email\s+text\s+not null\s+unique", body, re.I)


def test_subscribers_side_of_the_join_is_indexed_on_lower_email():
    assert "subscribers_email_lower_idx" in SCHEMA
    assert re.search(r"on subscribers\s*\(\s*lower\(email\)\s*\)", SCHEMA, re.I)


def test_the_subscribers_index_cannot_abort_the_schema_on_legacy_duplicates():
    """subscribers predates users and its plain unique(email) allows case
    variants, so the unique index can legitimately fail on existing rows.
    It degrades to a non-unique index with a warning instead of taking the
    rest of the file down with it."""
    # Pick the block by what is in it, not by being the first one. schema.sql
    # has grown a second do-block since this was written (the evidence-grade
    # constraint, added above subscribers), and a non-greedy search for the
    # first one had been reading that block and failing on it ever since.
    blocks = re.findall(r"do \$\$(.*?)\$\$;", SCHEMA, re.S | re.I)
    guards = [b for b in blocks if "subscribers_email_lower_idx" in b]
    assert guards, "the subscribers index is not guarded"
    guard = guards[0]
    assert "raise warning" in guard.lower()
    assert "create index if not exists subscribers_email_lower_idx" in guard
    assert "create unique index if not exists subscribers_email_lower_idx" in guard


def test_the_two_tables_are_joined_not_merged():
    """ADR-30: someone may read the digest forever without an account, and
    an account may exist with no subscription. A foreign key either way
    would make one of those two illegal."""
    assert "subscribers" not in create_table("users").lower()
    assert "references users" not in SCHEMA.lower()


def test_the_linkage_view_left_joins_on_folded_email():
    view = create_view("user_accounts")
    assert re.search(r"left join subscribers", view, re.I), "an inner join would hide accounts with no subscription"
    assert re.search(r"lower\(s\.email\)\s*=\s*lower\(u\.email\)", view, re.I)
    for column in ("clerk_id", "subscription_status", "digest_tier", "digest_status", "digest_comp"):
        assert column in view


def test_subscription_status_is_constrained():
    body = create_table("users")
    m = re.search(r"check \(subscription_status in \((.*?)\)\)", body, re.S | re.I)
    assert m, "subscription_status accepts any string"
    assert "'free'" in m.group(1)


# ----------------------------------------------------------------- route

def test_the_webhook_verifies_before_it_reads_the_payload():
    """An unverified body is a stranger claiming to be Clerk. Reading it
    first, even to decide whether to care, is the whole vulnerability."""
    assert "verifyWebhook" in ROUTE
    verify_at = ROUTE.index("await verifyWebhook(")
    for read in ("evt.type", "evt?.type", "evt.data"):
        if read in ROUTE:
            assert ROUTE.index(read) > verify_at, f"{read} is read before verification"


def test_the_signing_secret_appears_by_name_only():
    """verifyWebhook reads CLERK_WEBHOOK_SIGNING_SECRET from the environment
    itself, so no value passes through this file and none is ever logged."""
    assert "CLERK_WEBHOOK_SIGNING_SECRET" in ROUTE
    assert not re.search(r"CLERK_WEBHOOK_SIGNING_SECRET\s*[=:]\s*['\"]", ROUTE)
    assert "process.env.CLERK_WEBHOOK_SIGNING_SECRET" not in ROUTE


def test_a_failed_verification_says_nothing_about_why():
    body = ROUTE[ROUTE.index("} catch {") :]
    assert "invalid signature" in body
    assert "status: 400" in body


def test_all_three_user_events_are_handled():
    assert '"user.created"' in CORE
    assert '"user.updated"' in CORE
    assert '"user.deleted"' in CORE
    assert "deleteUserByClerkId" in ROUTE
    assert "upsertUserFromClerk" in ROUTE


def test_unhandled_events_are_acknowledged_not_retried():
    """A 4xx makes Svix retry on a schedule forever for an event that was
    delivered perfectly well."""
    m = re.search(r"if \(!isHandledEvent\(type\)\) \{(.*?)\n  \}", ROUTE, re.S)
    assert m, "unhandled events are not short-circuited"
    assert "status" not in m.group(1), "an ignored event must answer 2xx"


def test_a_missing_database_url_is_retryable_but_a_bad_event_is_not():
    """The status code is the only way to tell Svix which failure this was.
    The owner setting DATABASE_URL makes the retry succeed; an event with no
    email never will."""
    assert 'retryable: true, reason: "DATABASE_URL is not set"' in HELPER
    assert HELPER.count("retryable: false") == 2
    assert "status: 503" in ROUTE


def test_the_upsert_is_idempotent_so_retries_are_harmless():
    assert "on conflict (clerk_id) do update" in HELPER
    assert "updated_at = now()" in HELPER


def test_deleting_an_account_leaves_the_digest_list_alone():
    """They asked Clerk to forget them, not to unsubscribe from a newsletter
    they may still want. Two different requests (ADR-30)."""
    m = re.search(r"export async function deleteUserByClerkId.*?\n\}", HELPER, re.S)
    assert m
    assert "delete from users" in m.group(0)
    assert "subscribers" not in m.group(0)


def test_the_helper_fails_closed_when_the_database_is_unreachable():
    assert re.search(r"entitled:\s*false", HELPER), "the default account must not be entitled"
    assert "catch {" in HELPER


def test_the_desk_is_the_only_surface_wired_to_the_helper():
    """Per this run's scope. mcp/ is the follow-on, not this."""
    wired = [
        p.relative_to(REPO).as_posix()
        for p in (REPO / "site" / "app").rglob("*.jsx")
        if "currentAccount" in p.read_text()
    ]
    assert wired == ["site/app/desk/page.jsx"], wired


def test_the_desk_renders_per_request_now_that_it_reads_a_session():
    """Reading a session reads request headers, which a statically
    revalidated route cannot do."""
    desk = (REPO / "site" / "app" / "desk" / "page.jsx").read_text()
    assert 'export const dynamic = "force-dynamic"' in desk
    assert "export const revalidate" not in desk


def test_the_pure_core_stays_import_free():
    """tests/accounts.test.mjs loads it by evaluating its source, which only
    works while it has no imports to resolve."""
    assert not re.search(r"^\s*import\s", CORE, re.M)


# ------------------------------------------------------------ executed js

def test_account_core_logic():
    """Runs tests/accounts.test.mjs, which executes the real module."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed; run `node --test tests/accounts.test.mjs`")
    proc = subprocess.run(
        [node, "--test", str(Path(__file__).parent / "accounts.test.mjs")],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


# ------------------------------------------------------- the real parser

def test_schema_parses_as_postgresql():
    """Every assertion above reads schema.sql as text, which cannot tell a
    valid statement from a typo. pglast is libpg_query, the server's own
    parser, so this is the one check that says the file would actually
    apply. It covers the whole file, not just this run's additions."""
    pglast = pytest.importorskip("pglast", reason="pip install -r requirements-dev.txt")
    statements = pglast.parse_sql(SCHEMA)
    assert len(statements) > 20

    created = {
        s.stmt.relation.relname
        for s in statements
        if type(s.stmt).__name__ == "CreateStmt"
    }
    assert {"users", "subscribers"} <= created

    # The DO block's body is plpgsql, which the SQL parser accepts as an
    # opaque string. What runs is the plpgsql, so parse that too.
    block = re.search(r"do \$\$.*?\$\$;", SCHEMA, re.S | re.I)
    pglast.parse_plpgsql(block.group(0))
