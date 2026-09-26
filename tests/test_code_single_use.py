"""Single-use authorization codes at POST /token, without Modal and without Neon.

Same approach as tests/test_oauth_redirect_uri.py and
tests/test_authorize_throttle.py: mount the real handlers from mcp/oauth_flow.py
on a bare FastAPI app and drive the whole flow in-process, so what these prove is
what the deployed server does rather than what a stand-in does.

    pip install -r requirements-dev.txt
    python3 -m pytest tests/ -q

Covers the ledger entry "MCP authorization codes are replayable for their full
ten minutes" (docs/ideas.md, 2026-09-24), which recorded one code exchanged
three times at /token returning three valid token pairs. OAuth 2.1 section 4.1.2
requires a code to be single-use and requires the server to revoke previously
issued tokens when one is replayed.

The Postgres store is covered too, against a fake connection rather than a real
database. What that can prove is the shape of the SQL and the number of round
trips, not that Neon accepts it. The statements themselves are checked against
db/schema.sql by tests/test_accounts.py's schema parse.
"""

import base64
import hashlib
import importlib.util
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import jwt
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


@pytest.fixture
def ledger():
    return oauth.CodeLedger()


@pytest.fixture
def client(ledger):
    api = FastAPI()
    oauth.install_oauth(api, jwt_secret=SECRET, passphrase=PASSPHRASE, code_ledger=ledger)
    with TestClient(api) as c:
        yield c


def register(client, redirect_uris=(HONEST,)):
    resp = client.post("/register", json={"redirect_uris": list(redirect_uris)})
    assert resp.status_code == 201, resp.text
    return resp.json()["client_id"]


def get_code(client, client_id, redirect_uri=HONEST):
    """Run the real authorize flow and return the code it redirects with."""
    resp = client.post("/authorize", data={
        "passphrase": PASSPHRASE, "response_type": "code", "client_id": client_id,
        "redirect_uri": redirect_uri, "state": "xyz",
        "code_challenge": CHALLENGE, "code_challenge_method": "S256",
    }, follow_redirects=False)
    assert resp.status_code == 302, resp.text
    return parse_qs(urlsplit(resp.headers["location"]).query)["code"][0]


def exchange(client, code, client_id, redirect_uri=HONEST, verifier=VERIFIER):
    return client.post("/token", data={
        "grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri,
        "client_id": client_id, "code_verifier": verifier,
    })


def refresh(client, refresh_token):
    return client.post("/token", data={"grant_type": "refresh_token",
                                       "refresh_token": refresh_token})


def claims_of(token):
    return jwt.decode(token, SECRET, algorithms=["HS256"])


# ---------------- the finding itself ----------------


def test_a_code_is_exchanged_once(client):
    """The reported bug, verbatim: one code, three exchanges, three token pairs."""
    cid = register(client)
    code = get_code(client, cid)

    first = exchange(client, code, cid)
    assert first.status_code == 200
    assert "access_token" in first.json()

    for _ in range(2):
        again = exchange(client, code, cid)
        assert again.status_code == 400
        assert again.json() == {"error": "invalid_grant", "error_description": "replay"}


def test_replay_revokes_the_tokens_the_first_exchange_issued(client):
    """Section 4.1.2's other half. The honest client loses its session too, which
    is the point: the server cannot tell which of the two callers was the thief."""
    cid = register(client)
    code = get_code(client, cid)
    good = exchange(client, code, cid).json()

    assert refresh(client, good["refresh_token"]).status_code == 200, \
        "the session must work before the replay, or this proves nothing"

    exchange(client, code, cid)  # the replay

    dead = refresh(client, good["refresh_token"])
    assert dead.status_code == 400
    assert dead.json() == {"error": "invalid_grant", "error_description": "revoked"}


def test_the_code_ttl_is_sixty_seconds_not_ten_minutes(client):
    cid = register(client)
    c = claims_of(get_code(client, cid))
    assert c["exp"] - c["iat"] == oauth.CODE_TTL == 60


def test_every_token_carries_the_session_the_code_named(client):
    cid = register(client)
    code = get_code(client, cid)
    session = claims_of(code)["jti"]
    assert session, "the code must name a session or nothing can be revoked"

    pair = exchange(client, code, cid).json()
    assert claims_of(pair["access_token"])["sid"] == session
    assert claims_of(pair["refresh_token"])["sid"] == session


def test_two_logins_get_two_sessions(client):
    """Revocation has to be per-login, or one replay kills every connector."""
    cid = register(client)
    first = exchange(client, get_code(client, cid), cid).json()
    second_code = get_code(client, cid)
    second = exchange(client, second_code, cid).json()

    assert claims_of(first["refresh_token"])["sid"] != claims_of(second["refresh_token"])["sid"]

    exchange(client, second_code, cid)  # replay the second login only
    assert refresh(client, second["refresh_token"]).status_code == 400
    assert refresh(client, first["refresh_token"]).status_code == 200


def test_a_refresh_chain_stays_revocable(client):
    """The session must survive refreshing, or revocation only ever reaches the
    first link and an attacker escapes it by refreshing once."""
    cid = register(client)
    code = get_code(client, cid)
    session = claims_of(code)["jti"]
    pair = exchange(client, code, cid).json()

    for _ in range(3):
        pair = refresh(client, pair["refresh_token"]).json()
        assert claims_of(pair["refresh_token"])["sid"] == session

    exchange(client, code, cid)  # replay
    assert refresh(client, pair["refresh_token"]).status_code == 400


def test_a_legacy_refresh_token_without_a_session_still_works(client, ledger):
    """Merging this must not log the owner out of a connector she authorized
    months ago. Those tokens were minted before `sid` existed."""
    legacy = jwt.encode({"typ": "refresh", "iat": 0, "exp": 2 ** 31}, SECRET, algorithm="HS256")
    assert refresh(client, legacy).status_code == 200


# ---------------- a code is spent only when it would otherwise succeed ----------------


def test_a_failed_exchange_does_not_burn_the_code(client):
    """Every cheaper refusal runs first. If a wrong code_verifier spent the code,
    anyone who could guess a client_id could kill a login in flight."""
    cid = register(client)
    code = get_code(client, cid)

    bad = exchange(client, code, cid, verifier="b" * 64)
    assert bad.status_code == 400
    assert bad.json()["error_description"] == "pkce"

    assert exchange(client, code, cid).status_code == 200, \
        "the honest client must still be able to spend its own code"


def test_a_code_with_no_session_is_refused(client):
    """A code this server minted always carries a jti. One that does not is
    forged or predates the check, and both are dead."""
    forged = jwt.encode({"typ": "code", "cid": "x", "ru": HONEST, "cc": CHALLENGE,
                         "iat": 0, "exp": 2 ** 31}, SECRET, algorithm="HS256")
    resp = client.post("/token", data={
        "grant_type": "authorization_code", "code": forged, "redirect_uri": HONEST,
        "client_id": "x", "code_verifier": VERIFIER})
    assert resp.status_code == 400
    assert resp.json()["error"] == "invalid_grant"


# ---------------- the ledger on its own ----------------


def test_memory_ledger_consumes_once():
    store = oauth.MemoryCodeLedgerStore()
    assert store.consume("abc", 0) is True
    assert store.consume("abc", 0) is False


def test_ledger_degrades_to_memory_when_the_store_raises():
    """A Neon outage costs this check its memory, not the owner her connector."""
    class Broken:
        def consume(self, jti, expires_at):
            raise RuntimeError("connection refused")

        def revoke(self, jti):
            raise RuntimeError("connection refused")

        def is_revoked(self, jti):
            raise RuntimeError("connection refused")

    seen = []
    led = oauth.CodeLedger(Broken(), on_error=seen.append)
    assert led.consume("abc", 0) is True    # the exchange still works
    assert led.consume("abc", 0) is False   # and is still single-use in-process
    assert len(seen) == 2, "every degraded call is reported, not silently swallowed"


def test_an_outage_is_fail_open_not_fail_closed(client):
    """Stated as a test because it is a deliberate choice and not an obvious one."""
    class Broken:
        def consume(self, jti, expires_at):
            raise RuntimeError("connection refused")

        def revoke(self, jti):
            raise RuntimeError("connection refused")

        def is_revoked(self, jti):
            raise RuntimeError("connection refused")

    api = FastAPI()
    oauth.install_oauth(api, jwt_secret=SECRET, passphrase=PASSPHRASE,
                        code_ledger=oauth.CodeLedger(Broken()))
    with TestClient(api) as c:
        cid = register(c)
        assert exchange(c, get_code(c, cid), cid).status_code == 200


# ---------------- the Postgres store's shape ----------------


class FakeConn:
    def __init__(self, results):
        self.results, self.statements, self.commits = list(results), [], 0

    def execute(self, sql, params=None):
        self.statements.append((" ".join(sql.split()), params))
        self._row = self.results.pop(0) if self.results else None
        return self

    def fetchone(self):
        return self._row

    def commit(self):
        self.commits += 1

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def fake_connect(results):
    conns = []

    def connect():
        conns.append(FakeConn(results))
        return conns[-1]

    connect.conns = conns
    return connect


def test_postgres_consume_is_one_insert_that_returns_only_to_the_winner():
    connect = fake_connect([("abc",), None])
    store = oauth.PostgresCodeLedgerStore(connect)
    assert store.consume("abc", 1_800_000_000.0) is True

    sql, params = connect.conns[0].statements[0]
    assert "on conflict (jti) do nothing" in sql, \
        "the single-use guarantee is this clause, not a read-then-write"
    assert "returning jti" in sql
    assert params == ("abc", 1_800_000_000.0)
    assert connect.conns[0].commits == 1


def test_postgres_consume_reports_a_replay_when_no_row_comes_back():
    connect = fake_connect([None, None])
    assert oauth.PostgresCodeLedgerStore(connect).consume("abc", 0.0) is False


def test_postgres_consume_purges_expired_rows_in_the_same_connection():
    connect = fake_connect([("abc",), None])
    oauth.PostgresCodeLedgerStore(connect).consume("abc", 0.0)
    assert len(connect.conns) == 1, "one round trip, not two"
    assert "delete from consumed_codes where expires_at < now()" in \
        connect.conns[0].statements[1][0]


def test_postgres_revoke_and_is_revoked():
    connect = fake_connect([None])
    oauth.PostgresCodeLedgerStore(connect).revoke("abc")
    assert connect.conns[0].statements[0][0] == \
        "update consumed_codes set revoked = true where jti = %s"
    assert connect.conns[0].commits == 1

    connect = fake_connect([(True,)])
    assert oauth.PostgresCodeLedgerStore(connect).is_revoked("abc") is True
    connect = fake_connect([])
    assert oauth.PostgresCodeLedgerStore(connect).is_revoked("abc") is False


def test_the_table_the_store_writes_to_is_in_the_schema():
    schema = (REPO / "db" / "schema.sql").read_text()
    assert "create table if not exists consumed_codes" in schema
    for column in ("jti", "consumed_at", "expires_at", "revoked"):
        assert column in schema, f"consumed_codes is missing {column}"
