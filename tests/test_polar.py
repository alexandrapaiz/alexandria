"""The payments layer (ADR-30, ADR-31): the webhook's guards and the gate.

    python3 -m pytest tests/ -q

Polar is the Merchant of Record, so the only thing this product ever
learns is that somebody paid, and the flag written from that is the only
thing standing between a stranger and the paid surfaces. Two properties
therefore matter more than any feature in the diff: the signature check
cannot be skipped, and the gate cannot open on something it failed to
read.

The decision logic is executed for real in tests/polar.test.mjs, which
this file also runs so that one pytest command covers the whole layer.
What is read as source here is the ordering, which is not a function of an
argument and cannot be asserted by calling anything: that the raw body is
read before it is parsed, that verification happens before any write, and
that the handler's own vocabulary agrees with the database's check
constraint it will be writing into.
"""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
CORE = (REPO / "site" / "lib" / "polar-core.js").read_text()
HELPER = (REPO / "site" / "lib" / "polar.js").read_text()
HOOK = (REPO / "site" / "app" / "api" / "polar-webhook" / "route.js").read_text()
CHECKOUT = (REPO / "site" / "app" / "api" / "checkout" / "[plan]" / "route.js").read_text()
ENTITLEMENT = (REPO / "site" / "lib" / "entitlement.js").read_text()
PRICING = (REPO / "site" / "app" / "pricing" / "page.jsx").read_text()
SCHEMA = (REPO / "db" / "schema.sql").read_text()


# --------------------------------------------------------- the signature

def test_the_route_reads_the_raw_body_before_anything_parses_it():
    """The signature covers the bytes that arrived.

    `await request.json()` then `JSON.stringify` loses the key order, the
    spacing and the unicode escaping, and the HMAC stops matching for an
    honest caller. So the route reads text() and the parse happens after
    verification, inside readEvent.
    """
    assert "request.text()" in HOOK
    assert "request.json()" not in HOOK
    text_at = HOOK.index("request.text()")
    read_at = HOOK.index("readEvent(")
    assert text_at < read_at, "the body is parsed before it is verified"


def test_verification_precedes_every_write():
    """There is no path to applyPolarEvent that has not verified first."""
    read_at = HOOK.index("readEvent(")
    guard_at = HOOK.index("if (!read.ok)")
    apply_at = HOOK.index("applyPolarEvent(")
    assert read_at < guard_at < apply_at


def test_a_bad_signature_is_a_401_and_says_nothing_about_why():
    """The reasons describe the secret's state and the freshness window,
    and the caller that failed verification is exactly the caller who
    should not learn either."""
    block = HOOK[HOOK.index("if (!read.ok)") : HOOK.index("const type =")]
    assert "401" in block
    assert '"invalid signature"' in block
    assert "read.reason" in block, "the reason is worth logging"
    # Logged, not returned. The only `read.reason` in the block is inside a
    # console.error, so the response body carries the fixed string above.
    for line in block.splitlines():
        if "read.reason" in line:
            assert "console.error" in line or line.strip().startswith("`"), line


def test_the_route_runs_on_node_and_not_at_the_edge():
    """createHmac is node's. An edge runtime has no node:crypto, so this
    export is load-bearing rather than boilerplate."""
    assert 'export const runtime = "nodejs"' in HOOK
    assert 'export const dynamic = "force-dynamic"' in HOOK


def test_the_tolerance_window_is_named_and_small():
    m = re.search(r"SIGNATURE_TOLERANCE_SECONDS\s*=\s*(\d+)", CORE)
    assert m, "the replay window is not stated"
    assert int(m.group(1)) <= 600, "a replay window wider than ten minutes is not a window"


def test_the_core_names_no_secret_value_and_only_variable_names():
    """A secret name is fine in this repository. A secret is not."""
    for text in (CORE, HELPER, HOOK, CHECKOUT):
        assert "whsec_" not in text or "whsec_" in CORE  # the prefix is a format, not a key
        assert not re.search(r"polar_[a-z]*_[A-Za-z0-9]{20,}", text), "that looks like a key"
    assert "process.env.POLAR_WEBHOOK_SECRET" in HELPER


# ------------------------------------------------------------- the writes

def test_the_payment_webhook_never_inserts_an_account():
    """An account is created at Clerk and a payment is not an account.

    /api/clerk-webhook owns every insert into `users`. If this one inserted
    too, a payment from an email nobody signed up with would mint a row
    with no clerk_id, which is the table's primary key.
    """
    assert "insert into users" not in HELPER
    assert "update users" in HELPER


def test_a_missing_users_row_is_retryable_and_a_missing_account_is_not():
    """Two failures, two status codes. Webhook delivery is eventually
    consistent, so a users row that has not landed yet is temporary. A
    buyer with no Clerk account at all will never succeed, and retrying it
    for a day changes nothing."""
    assert 'retryable: true, reason: "DATABASE_URL is not set"' in HELPER
    assert "no users row for that clerk_id yet" in HELPER
    assert "retryable: false" in HELPER
    assert "503" in HOOK


def test_an_ambiguous_email_matches_nobody():
    """Granting paid access to the wrong one of two people with the same
    address is worse than granting it to nobody and logging why."""
    assert "limit: 2" in HELPER
    assert "found.length > 1" in HELPER
    assert "email is ambiguous" in HELPER


def test_the_billing_vocabulary_is_the_one_the_schema_allows():
    """The cross-file assertion, and the one that would fail at runtime.

    users.subscription_status carries a check constraint. A webhook that
    writes a value outside it raises 23514 inside a retrying delivery,
    which is a failure nobody sees until a customer does.
    """
    m = re.search(
        r"subscription_status\s+text\s+not null\s+default\s+'free'\s*"
        r"check\s*\(subscription_status\s+in\s*\(([^)]*)\)\)",
        SCHEMA,
        re.S | re.I,
    )
    assert m, "no check constraint on users.subscription_status"
    allowed = set(re.findall(r"'([a-z_]+)'", m.group(1)))

    written = set(re.findall(r"billing:\s*\"([a-z_]+)\"", CORE))
    assert written, "polar-core.js writes no billing status at all"
    assert written <= allowed, f"{sorted(written - allowed)} is not in the constraint"

    unknown = re.search(r"UNKNOWN_SUBSCRIPTION_STATUS\s*=\s*\{[^}]*billing:\s*\"([a-z_]+)\"", CORE)
    assert unknown, "there is no fallback for a status Polar adds later"
    assert unknown.group(1) in allowed


def test_an_unknown_status_is_logged_rather_than_swallowed():
    """A vocabulary gap that nobody is told about stays a gap until a
    customer complains."""
    assert "unknownStatus" in HOOK
    assert "unknown status" in HOOK


# --------------------------------------------------------------- the gate

def test_the_gate_reads_clerk_before_it_reads_the_database():
    """The flag rides in the session token, so the common case costs no
    round trip, and the comped-subscriber query only runs for someone who
    has no flag."""
    assert "spineFromMetadata" in ENTITLEMENT
    meta_at = ENTITLEMENT.index("spineFromMetadata(")
    sql_at = ENTITLEMENT.index("neon(url)")
    assert meta_at < sql_at


def test_current_email_is_no_longer_the_stub_that_shut_the_whole_spine():
    """It returned null for everyone until 2026-10-13, which meant
    hasSpine() could not return true for a paying subscriber or anybody
    else. The $20 tier was shut and the gate was the thing shutting it."""
    body = ENTITLEMENT[ENTITLEMENT.index("export async function currentEmail") :]
    body = body[: body.index("export async function hasSpine")]
    assert "currentUser(" in body
    assert "primaryEmail(" in body
    assert "return null;\n}" not in body


def test_every_failure_in_the_gate_is_a_closed_door():
    """No session, no flag, an unreadable expiry, no connection string or a
    query that throws. A check that opens when something is unreachable is
    not a check."""
    body = ENTITLEMENT[ENTITLEMENT.index("export async function hasSpine") :]
    assert body.count("return false") >= 3
    assert "catch {\n    return false;\n  }" in body
    assert "return true" in body


def test_the_gate_does_not_open_on_the_comp_flag():
    """The trap found while wiring this, and the one that would have been
    expensive.

    `subscribers.comp` reads as "free access (friends)" in db/schema.sql,
    and site/lib/account-core.js's isEntitled treats it as entitling. But
    site/lib/waitlist-core.js sets `comp: true` on every signup the site
    takes, because the friends-and-family phase charges nobody for the
    digest. A gate that opened on `comp` would hand the skill library and
    the claim graph to the whole free list, quietly, on merge.
    """
    waitlist = (REPO / "site" / "lib" / "waitlist-core.js").read_text()
    assert "comp: true" in waitlist, "the premise of this test changed"

    body = ENTITLEMENT[ENTITLEMENT.index("export async function hasSpine") :]
    sql = body[body.index("select 1") : body.index("limit 1")]
    assert "comp" not in sql, "the gate opens on comp, which is the whole free list"
    assert "tier = ${SPINE_TIER}" in sql
    assert "status = 'active'" in sql


def test_an_expiring_flag_is_what_makes_a_late_revoke_harmless():
    """Polar's revoke event can be late or can go missing. The expiry is
    written at grant time so the entitlement cannot outlive what was paid
    for, with nothing on a clock to enforce it."""
    assert "spineUntil" in CORE
    body = CORE[CORE.index("export function spineFromMetadata") :]
    assert "Date.parse" in body
    assert "Number.isFinite" in body


# ------------------------------------------------------------- the offers

def test_the_pricing_page_hard_codes_no_polar_url():
    """The three products are created in a dashboard, so their links are
    environment values. A URL in the page is a deploy every time one of
    them is renamed or repriced."""
    assert "polar.sh" not in PRICING
    assert "checkoutOffers(process.env)" in PRICING
    for name in ("POLAR_CHECKOUT_TRIAL", "POLAR_CHECKOUT_MONTHLY", "POLAR_CHECKOUT_LIFETIME"):
        assert name in CORE
        assert name not in PRICING


def test_the_page_shows_three_offers_and_the_lifetime_price():
    """ADR-31: a 3-day trial, $20 a month, $200 lifetime."""
    assert "$200" in PRICING
    assert "$20" in PRICING
    assert "byId.trial" in PRICING
    assert "byId.monthly" in PRICING
    assert "byId.lifetime" in PRICING


def test_checkout_asks_for_the_account_before_the_card():
    """This is what closes the integration's one real gap. A payment with
    no Clerk account behind it has nothing to grant access to, and no
    number of webhook retries produces an account."""
    assert "currentAccount()" in CHECKOUT
    assert "/sign-up" in CHECKOUT
    assert "redirect_url" in CHECKOUT
    signin_at = CHECKOUT.index("/sign-up")
    polar_at = CHECKOUT.index("checkoutRedirect(")
    assert signin_at < polar_at, "a stranger reaches Polar before being asked to sign up"


def test_an_unconfigured_plan_goes_back_to_pricing_rather_than_nowhere():
    assert CHECKOUT.count('new URL("/pricing", request.url)') >= 2


# ----------------------------------------------------- the loader's premise

def test_polar_core_has_no_imports():
    """tests/polar.test.mjs loads it by evaluating its source, which only
    works while there is nothing to resolve. The same premise as
    site/lib/account-core.js and the same test."""
    assert not re.search(r"^\s*import\s", CORE, re.M)
    assert not re.search(r"\brequire\s*\(", CORE)


def test_the_hmac_arrives_as_an_argument():
    """The core cannot import node:crypto and stay loadable by that test,
    so the one primitive it needs is injected. The caller passes node's
    crypto and so does the test, which is what makes the signature
    assertions real bytes rather than a stub agreeing with itself."""
    assert "hmacSha256Base64" in CORE
    assert "createHmac" not in CORE
    assert 'from "node:crypto"' in HELPER


# ------------------------------------------------------------ executed js

def test_polar_core_logic():
    """Runs tests/polar.test.mjs, which executes the real module."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed; run `node --test tests/polar.test.mjs`")
    proc = subprocess.run(
        [node, "--test", str(Path(__file__).parent / "polar.test.mjs")],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
