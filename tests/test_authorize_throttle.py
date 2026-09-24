"""The passphrase throttle on POST /authorize, exercised without Modal and without Neon.

Same approach as tests/test_oauth_redirect_uri.py: mount the real handlers from
mcp/oauth_flow.py on a bare FastAPI app, so what these prove is what the deployed
server does. The clock is the one thing stubbed, because a test that waits out a
sixty-second backoff is a test nobody runs.

    pip install -r requirements-dev.txt
    python3 -m pytest tests/ -q

Covers the ledger entry "The MCP passphrase can be guessed without limit"
(docs/ideas.md, status urgent), which recorded forty consecutive wrong
passphrases returning forty 401s with no delay, no lockout, and no counter.
"""

import base64
import hashlib
import importlib.util
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("alexandria_oauth", REPO / "mcp" / "oauth_flow.py")
oauth = importlib.util.module_from_spec(spec)
sys.modules["alexandria_oauth"] = oauth
spec.loader.exec_module(oauth)

SECRET = "test-signing-secret-not-a-real-one"
PASSPHRASE = "open sesame"
HONEST = "https://claude.ai/api/mcp/auth_callback"
VERIFIER = "a" * 64
CHALLENGE = base64.urlsafe_b64encode(
    hashlib.sha256(VERIFIER.encode()).digest()
).rstrip(b"=").decode()


class FakeClock:
    """A clock the test moves by hand, so backoffs elapse in no real time."""

    def __init__(self):
        self.now = 1_000_000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


@pytest.fixture
def clock(monkeypatch):
    fake = FakeClock()
    monkeypatch.setattr(oauth.time, "time", fake)
    return fake


@pytest.fixture
def throttle(clock):
    return oauth.Throttle()


@pytest.fixture
def client(throttle):
    api = FastAPI()
    oauth.install_oauth(api, jwt_secret=SECRET, passphrase=PASSPHRASE, throttle=throttle)
    with TestClient(api) as c:
        yield c


def register(client, redirect_uris=(HONEST,)):
    resp = client.post("/register", json={"redirect_uris": list(redirect_uris)})
    assert resp.status_code == 201, resp.text
    return resp.json()["client_id"]


def form(client_id, passphrase):
    return {"response_type": "code", "client_id": client_id, "redirect_uri": HONEST,
            "state": "xyz", "code_challenge": CHALLENGE, "code_challenge_method": "S256",
            "passphrase": passphrase}


def attempt(client, client_id, passphrase="wrong"):
    return client.post("/authorize", data=form(client_id, passphrase), follow_redirects=False)


# ---------------- the finding this was built for ----------------

def test_forty_wrong_passphrases_no_longer_cost_nothing(client, clock):
    """The audit's own reproduction: forty in a row, previously forty free 401s."""
    client_id = register(client)
    statuses = [attempt(client, client_id).status_code for _ in range(40)]

    assert statuses[:3] == [401, 401, 401], "the free allowance should stay free"
    assert 429 in statuses, "forty free 401s in a row is the finding itself"
    assert statuses.count(401) == oauth.FREE_ATTEMPTS
    assert statuses.count(429) == 40 - oauth.FREE_ATTEMPTS


def test_the_wait_grows_and_then_stops_growing(clock):
    """Doubling while it climbs, flat at the cap, never unbounded."""
    assert [oauth.backoff_seconds(n) for n in range(0, 8)] == [0, 0, 0, 1, 2, 4, 8, 16]
    assert oauth.backoff_seconds(50) == oauth.MAX_BACKOFF
    assert oauth.backoff_seconds(10_000) == oauth.MAX_BACKOFF


def test_waiting_it_out_lets_the_next_attempt_through(client, clock):
    client_id = register(client)
    for _ in range(oauth.FREE_ATTEMPTS):
        attempt(client, client_id)

    assert attempt(client, client_id).status_code == 429
    clock.advance(oauth.MAX_BACKOFF + 1)
    assert attempt(client, client_id).status_code == 401, "the wait should expire, not persist"


def test_the_refusal_tells_the_caller_how_long_to_wait(client, clock):
    client_id = register(client)
    for _ in range(oauth.FREE_ATTEMPTS):
        attempt(client, client_id)

    blocked = attempt(client, client_id)
    assert blocked.status_code == 429
    assert blocked.headers["Retry-After"] == "1"
    assert "Nothing is\nlocked" in blocked.text


# ---------------- and it must not become a lockout ----------------

def test_the_owner_still_gets_in_after_the_longest_possible_wait(client, clock):
    """An attacker holding the counter at the ceiling costs the owner a minute, not her access."""
    client_id = register(client)
    for _ in range(200):
        attempt(client, client_id)

    clock.advance(oauth.MAX_BACKOFF)
    good = attempt(client, client_id, PASSPHRASE)
    assert good.status_code == 302, good.text
    assert good.headers["location"].startswith(HONEST)


def test_the_right_passphrase_clears_the_counter(client, clock):
    client_id = register(client)
    for _ in range(oauth.FREE_ATTEMPTS):
        attempt(client, client_id)

    clock.advance(oauth.MAX_BACKOFF)
    assert attempt(client, client_id, PASSPHRASE).status_code == 302
    assert [attempt(client, client_id).status_code for _ in range(3)] == [401, 401, 401]


def test_an_old_run_of_failures_decays(client, clock, throttle):
    client_id = register(client)
    for _ in range(oauth.FREE_ATTEMPTS + 3):
        attempt(client, client_id)

    clock.advance(throttle.decay + 1)
    assert [attempt(client, client_id).status_code for _ in range(3)] == [401, 401, 401]


def test_hammering_while_blocked_does_not_push_the_wait_out(client, clock):
    """Otherwise an attacker could keep the owner waiting indefinitely for free."""
    client_id = register(client)
    for _ in range(oauth.FREE_ATTEMPTS + 2):   # wait is now 4 seconds
        attempt(client, client_id)

    for _ in range(500):
        assert attempt(client, client_id).status_code == 429
    clock.advance(4)
    assert attempt(client, client_id).status_code == 401


# ---------------- the throttle sits behind the redirect-URI check ----------------

def test_a_bad_redirect_uri_is_still_refused_and_does_not_count(client, clock, throttle):
    """Junk that never had a client_id cannot run the owner's counter up."""
    for _ in range(50):
        resp = client.post("/authorize", data=form("not-a-client-id", "wrong"))
        assert resp.status_code == 400

    assert throttle.retry_after() == 0
    client_id = register(client)
    assert attempt(client, client_id).status_code == 401


def test_a_blocked_attempt_never_compares_the_passphrase(client, clock, monkeypatch):
    """The 429 must be decided before the comparison, so it leaks nothing."""
    client_id = register(client)
    for _ in range(oauth.FREE_ATTEMPTS):
        attempt(client, client_id)

    # compare_digest is also how the redirect-URI check runs, so watch the
    # operands rather than the call count: the passphrase must never be one.
    operands = []
    real = oauth.hmac.compare_digest
    monkeypatch.setattr(oauth.hmac, "compare_digest",
                        lambda a, b: operands.append((a, b)) or real(a, b))
    assert attempt(client, client_id, PASSPHRASE).status_code == 429
    assert not any(PASSPHRASE in pair for pair in operands), \
        "a throttled request should never reach the passphrase comparison"


# ---------------- degraded mode: Neon unreachable ----------------

class BrokenStore:
    def read(self, scope):
        raise RuntimeError("could not connect to server")

    def record_failure(self, scope, decay):
        raise RuntimeError("could not connect to server")

    def reset(self, scope):
        raise RuntimeError("could not connect to server")


def test_a_database_outage_degrades_the_count_instead_of_dropping_it(clock):
    seen = []
    throttle = oauth.Throttle(BrokenStore(), on_error=seen.append)

    api = FastAPI()
    oauth.install_oauth(api, jwt_secret=SECRET, passphrase=PASSPHRASE, throttle=throttle)
    with TestClient(api) as client:
        client_id = register(client)
        statuses = [attempt(client, client_id).status_code for _ in range(10)]

    assert statuses[:3] == [401, 401, 401]
    assert 429 in statuses, "the limit should survive in memory, not vanish"
    assert seen, "and the outage should be reported rather than swallowed"


def test_a_database_outage_does_not_bar_the_owner(clock):
    throttle = oauth.Throttle(BrokenStore())
    api = FastAPI()
    oauth.install_oauth(api, jwt_secret=SECRET, passphrase=PASSPHRASE, throttle=throttle)
    with TestClient(api) as client:
        client_id = register(client)
        assert attempt(client, client_id, PASSPHRASE).status_code == 302


# ---------------- the store the deployed server actually uses ----------------

class RecordingConnection:
    """Enough of a psycopg connection to prove what PostgresAttemptStore sends."""

    def __init__(self, log, row):
        self.log, self.row = log, row
        self.committed = False

    def execute(self, sql, params=None):
        self.log.append((" ".join(sql.split()), params))
        return self

    def fetchone(self):
        return self.row

    def commit(self):
        self.committed = True

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def recording_store(row=None):
    log, conns = [], []

    def connect():
        conn = RecordingConnection(log, row)
        conns.append(conn)
        return conn

    return oauth.PostgresAttemptStore(connect), log, conns


def test_postgres_store_reads_the_count_and_the_age_together():
    store, log, _ = recording_store(row=(7, 12.5))
    assert store.read("mcp-authorize") == (7, 12.5)
    sql, params = log[0]
    assert params == ("mcp-authorize",)
    assert "extract(epoch from (now() - last_fail))" in sql


def test_postgres_store_reports_a_scope_it_has_never_seen():
    store, _, _ = recording_store(row=None)
    assert store.read("mcp-authorize") is None


def test_postgres_store_upserts_the_failure_and_commits():
    store, log, conns = recording_store(row=(4,))
    assert store.record_failure("mcp-authorize", 3600) == 4
    sql, params = log[0]
    assert params == ("mcp-authorize", 3600)
    assert "on conflict (scope) do update" in sql
    assert conns[0].committed


def test_postgres_store_deletes_the_row_on_success():
    store, log, conns = recording_store()
    store.reset("mcp-authorize")
    assert log[0] == ("delete from auth_attempts where scope = %s", ("mcp-authorize",))
    assert conns[0].committed


def test_the_throttles_sql_parses_as_postgres():
    """pglast is already a dev dependency for db/schema.sql; point it at these too."""
    pglast = pytest.importorskip("pglast")
    for sql in (oauth.PostgresAttemptStore.READ,
                oauth.PostgresAttemptStore.RECORD.replace("%s", "$1"),
                oauth.PostgresAttemptStore.RESET):
        pglast.parse_sql(sql.replace("%s", "$1"))


def test_the_schema_declares_the_table_the_store_writes_to():
    schema = (REPO / "db" / "schema.sql").read_text()
    assert "create table if not exists auth_attempts" in schema
    for column in ("scope", "fails", "last_fail"):
        assert column in schema.split("create table if not exists auth_attempts")[1][:400]
