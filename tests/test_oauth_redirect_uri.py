"""The MCP server's OAuth flow, exercised without Modal and without secrets.

These tests mount the real handlers from mcp/oauth_flow.py on a bare FastAPI app, so
what they prove is what the deployed server does, not what a stand-in does. The
one thing they cannot reach is the `/mcp` bearer guard's surroundings, which live
inside serve() with the database and the embedding model.

    pip install fastapi httpx python-multipart pytest pyjwt
    python3 -m pytest tests/ -q

Covers sprint 2026-09-21 item 1: before this, `/register` echoed a client's
redirect_uris back and stored them nowhere, and `/authorize` minted a code
against whatever redirect_uri the request carried.
"""

import base64
import hashlib
import importlib.util
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

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
ATTACKER = "https://evil.example/collect"
VERIFIER = "a" * 64
CHALLENGE = base64.urlsafe_b64encode(
    hashlib.sha256(VERIFIER.encode()).digest()
).rstrip(b"=").decode()


@pytest.fixture
def client():
    api = FastAPI()
    oauth.install_oauth(api, jwt_secret=SECRET, passphrase=PASSPHRASE)
    with TestClient(api) as c:
        yield c


def register(client, redirect_uris=(HONEST,)):
    resp = client.post("/register", json={"redirect_uris": list(redirect_uris)})
    assert resp.status_code == 201, resp.text
    return resp.json()["client_id"]


def authorize_params(client_id, redirect_uri):
    return {"response_type": "code", "client_id": client_id, "redirect_uri": redirect_uri,
            "state": "xyz", "code_challenge": CHALLENGE, "code_challenge_method": "S256"}


# ---------------- the legitimate flow still completes ----------------

def test_owner_passphrase_login_completes_end_to_end(client):
    client_id = register(client)
    params = authorize_params(client_id, HONEST)

    form = client.get("/authorize", params=params)
    assert form.status_code == 200
    assert "passphrase" in form.text

    redirect = client.post("/authorize", data={**params, "passphrase": PASSPHRASE},
                           follow_redirects=False)
    assert redirect.status_code == 302
    location = redirect.headers["location"]
    assert location.startswith(HONEST)
    query = parse_qs(urlsplit(location).query)
    assert query["state"] == ["xyz"]

    tokens = client.post("/token", data={"grant_type": "authorization_code",
                                         "code": query["code"][0], "redirect_uri": HONEST,
                                         "client_id": client_id, "code_verifier": VERIFIER})
    assert tokens.status_code == 200, tokens.text
    body = tokens.json()
    assert body["token_type"] == "Bearer"
    assert oauth.install_oauth  # sanity: module loaded from the real file

    refreshed = client.post("/token", data={"grant_type": "refresh_token",
                                            "refresh_token": body["refresh_token"]})
    assert refreshed.status_code == 200


def test_wrong_passphrase_still_just_reprompts(client):
    client_id = register(client)
    resp = client.post("/authorize",
                       data={**authorize_params(client_id, HONEST), "passphrase": "wrong"},
                       follow_redirects=False)
    assert resp.status_code == 401
    assert "Wrong passphrase" in resp.text


def test_pkce_is_still_enforced(client):
    client_id = register(client)
    params = authorize_params(client_id, HONEST)
    redirect = client.post("/authorize", data={**params, "passphrase": PASSPHRASE},
                           follow_redirects=False)
    code = parse_qs(urlsplit(redirect.headers["location"]).query)["code"][0]
    resp = client.post("/token", data={"grant_type": "authorization_code", "code": code,
                                       "redirect_uri": HONEST, "client_id": client_id,
                                       "code_verifier": "b" * 64})
    assert resp.status_code == 400
    assert resp.json()["error_description"] == "pkce"


# ---------------- the gap this item closes ----------------

def test_crafted_link_never_reaches_the_passphrase_form(client):
    """The attack: a real-domain link whose redirect_uri is the attacker's."""
    client_id = register(client)
    resp = client.get("/authorize", params=authorize_params(client_id, ATTACKER))
    assert resp.status_code == 400
    assert "passphrase" not in resp.text
    assert "did not register" in resp.text


def test_posting_the_right_passphrase_to_a_crafted_redirect_mints_nothing(client):
    """Rewriting the form's hidden fields is the same attack one step later."""
    client_id = register(client)
    resp = client.post("/authorize",
                       data={**authorize_params(client_id, ATTACKER), "passphrase": PASSPHRASE},
                       follow_redirects=False)
    assert resp.status_code == 400
    assert "location" not in {k.lower() for k in resp.headers}
    assert "code=" not in resp.text


def test_an_invented_client_id_is_refused(client):
    """A client_id this server never issued cannot be forged into one."""
    for forged in ["deadbeef", "", "a.b", "x" * 200,
                   register(client)[:-4] + "AAAA"]:  # signature tampered
        resp = client.get("/authorize", params=authorize_params(forged, ATTACKER))
        assert resp.status_code == 400, forged


def test_token_endpoint_refuses_an_unregistered_redirect_uri(client):
    """Belt and braces: even a validly minted code is re-checked at /token."""
    client_id = register(client, [HONEST, ATTACKER])
    params = authorize_params(client_id, ATTACKER)
    redirect = client.post("/authorize", data={**params, "passphrase": PASSPHRASE},
                           follow_redirects=False)
    code = parse_qs(urlsplit(redirect.headers["location"]).query)["code"][0]

    # Now the same code, presented under a client_id that registered only HONEST.
    narrow = register(client, [HONEST])
    resp = client.post("/token", data={"grant_type": "authorization_code", "code": code,
                                       "redirect_uri": ATTACKER, "client_id": narrow,
                                       "code_verifier": VERIFIER})
    assert resp.status_code == 400
    assert resp.json()["error"] == "invalid_grant"


# ---------------- what a client is allowed to register ----------------

def test_registration_requires_redirect_uris(client):
    for body in [{}, {"redirect_uris": []}, {"redirect_uris": "not-a-list"}]:
        resp = client.post("/register", json=body)
        assert resp.status_code == 400, body
        assert resp.json()["error"] in ("invalid_redirect_uri", "invalid_client_metadata")


@pytest.mark.parametrize("uri", [
    "/relative/callback",
    "javascript:alert(1)",
    "data:text/html,<script>1</script>",
    "http://evil.example/collect",          # plaintext, not loopback
    "https://claude.ai/callback#fragment",
])
def test_registration_refuses_hostile_redirect_uris(client, uri):
    assert client.post("/register", json={"redirect_uris": [uri]}).status_code == 400


def test_loopback_keeps_its_ephemeral_port(client):
    """RFC 8252 §7.3: a native client cannot know its port at registration time."""
    client_id = register(client, ["http://127.0.0.1:1234/cb"])
    assert oauth.check_redirect_uri(client_id, "http://127.0.0.1:57218/cb", SECRET)
    assert not oauth.check_redirect_uri(client_id, "http://127.0.0.1:57218/other", SECRET)
    assert not oauth.check_redirect_uri(client_id, "http://evil.example:1234/cb", SECRET)


def test_a_client_id_signed_with_another_secret_is_not_ours(client):
    assert oauth.registered_redirect_uris(
        oauth.issue_client_id([HONEST], "a different secret"), SECRET) is None
