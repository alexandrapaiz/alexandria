"""Client registration and redirect-URI validation for the MCP server's OAuth flow.

This lives outside `serve()` on purpose. Everything in mcp/server.py's body runs
inside a Modal container with secrets attached, so no test can reach it without a
deployment. These functions take a signing secret and return a verdict, nothing
else, which is what lets tests/test_oauth_redirect_uri.py cover the check on a
laptop or in CI.

The registration stays stateless, like the rest of this server's auth: the
`client_id` *is* a signed token carrying the redirect URIs the client registered.
There is no table to store and no row to look up, but a `client_id` the server
never issued cannot be forged, and a redirect URI the client never registered
cannot be smuggled past `/authorize`.

Signing is stdlib HMAC-SHA256 rather than a JWT, because a `client_id` is opaque
to the client and this module is worth keeping dependency-free.

Why this exists: before it, `/register` echoed a client's `redirect_uris` back and
stored them nowhere, and `/authorize` minted a code against whatever
`redirect_uri` the request carried. A crafted link on the real domain plus the
real passphrase handed an attacker a working token pair. PKCE does not close that
gap, since whoever crafts the link also holds the matching `code_verifier`.
"""

import base64
import hashlib
import hmac
import html
import json
import time
from urllib.parse import urlencode, urlsplit

#: Registrations do not expire on their own. A client that registered a year ago
#: is still the same client, and an expiring `client_id` would just log the
#: owner's connector out on a timer for no security gain.
LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})

#: Schemes that are never a legitimate redirect target, whatever they claim.
DANGEROUS_SCHEMES = frozenset({"javascript", "data", "vbscript", "file"})

MAX_REDIRECT_URIS = 10
MAX_URI_LENGTH = 2000


class RegistrationError(ValueError):
    """A client sent redirect URIs that cannot be registered."""


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _b64d(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def validate_redirect_uri(uri: str) -> str:
    """Return `uri` if a client may register it, else raise RegistrationError.

    The bar here is deliberately low, because the real protection is the exact
    match at authorize time. This only turns away URIs that could never be an
    honest callback: relative ones, ones carrying a fragment, plaintext HTTP to
    somewhere other than the loopback interface, and the script-ish schemes.
    """
    if not isinstance(uri, str) or not uri.strip():
        raise RegistrationError("redirect_uris entries must be non-empty strings")
    if len(uri) > MAX_URI_LENGTH:
        raise RegistrationError("redirect_uri is too long")

    parts = urlsplit(uri)
    scheme = parts.scheme.lower()
    if not scheme:
        raise RegistrationError(f"redirect_uri must be absolute: {uri}")
    if scheme in DANGEROUS_SCHEMES:
        raise RegistrationError(f"redirect_uri scheme is not allowed: {scheme}")
    if parts.fragment:
        raise RegistrationError("redirect_uri must not carry a fragment")
    if scheme == "http" and (parts.hostname or "").lower() not in LOOPBACK_HOSTS:
        raise RegistrationError("plaintext http is allowed only on the loopback interface")
    if scheme in ("http", "https") and not parts.hostname:
        raise RegistrationError(f"redirect_uri has no host: {uri}")
    return uri


def normalize_redirect_uris(raw) -> list[str]:
    """Validate the `redirect_uris` field of a registration request."""
    if not isinstance(raw, list) or not raw:
        raise RegistrationError("redirect_uris is required and must be a non-empty array")
    if len(raw) > MAX_REDIRECT_URIS:
        raise RegistrationError(f"at most {MAX_REDIRECT_URIS} redirect_uris may be registered")
    return [validate_redirect_uri(uri) for uri in raw]


def issue_client_id(redirect_uris: list[str], secret: str) -> str:
    """Mint the signed `client_id` that carries this client's registered URIs."""
    payload = json.dumps(
        {"v": 1, "typ": "client", "ru": list(redirect_uris), "iat": int(time.time())},
        separators=(",", ":"), sort_keys=True,
    ).encode()
    signature = hmac.new(secret.encode(), payload, hashlib.sha256).digest()
    return f"{_b64e(payload)}.{_b64e(signature)}"


def registered_redirect_uris(client_id: str, secret: str) -> list[str] | None:
    """Return the URIs registered under `client_id`, or None if it is not ours."""
    if not isinstance(client_id, str) or client_id.count(".") != 1:
        return None
    body, signature = client_id.split(".")
    try:
        payload = _b64d(body)
        expected = hmac.new(secret.encode(), payload, hashlib.sha256).digest()
        if not hmac.compare_digest(_b64d(signature), expected):
            return None
        claims = json.loads(payload)
    except (ValueError, json.JSONDecodeError):
        return None
    if claims.get("typ") != "client" or not isinstance(claims.get("ru"), list):
        return None
    return [uri for uri in claims["ru"] if isinstance(uri, str)]


def redirect_uri_matches(registered: str, presented: str) -> bool:
    """Exact string comparison, with the one loopback carve-out OAuth allows.

    OAuth 2.1 requires simple string comparison. RFC 8252 §7.3 carves out the
    loopback interface, because a native client picks an ephemeral port at
    runtime and cannot know it at registration time. The carve-out is safe for
    exactly the reason it exists: a redirect to the victim's own loopback is not
    something a remote attacker can receive on.
    """
    if hmac.compare_digest(registered, presented):
        return True

    reg, pres = urlsplit(registered), urlsplit(presented)
    if reg.scheme != "http" or pres.scheme != "http":
        return False
    if (reg.hostname or "").lower() not in LOOPBACK_HOSTS:
        return False
    return (
        (reg.hostname or "").lower() == (pres.hostname or "").lower()
        and reg.path == pres.path
        and reg.query == pres.query
    )


def check_redirect_uri(client_id: str, redirect_uri: str, secret: str) -> bool:
    """True only if `client_id` is one we issued and registered `redirect_uri`."""
    if not client_id or not redirect_uri:
        return False
    registered = registered_redirect_uris(client_id, secret)
    if not registered:
        return False
    return any(redirect_uri_matches(uri, redirect_uri) for uri in registered)


# ---------------- the endpoints themselves ----------------
#
# They live here rather than inside serve() so that a test can mount the real
# handlers on a bare FastAPI app and drive the whole flow in-process. A test that
# re-implements these endpoints would only ever prove the re-implementation safe.

ACCESS_TTL = 24 * 3600
REFRESH_TTL = 180 * 24 * 3600

LOGIN_FORM = """<!doctype html><title>alexandria</title>
<body style="font-family:system-ui;max-width:22rem;margin:15vh auto">
<h2>alexandria</h2><p>{msg}</p>
<form method="post" action="/authorize">
{hidden}
<input type="password" name="passphrase" placeholder="passphrase" autofocus
       style="width:100%;padding:.5rem;font-size:1rem">
<button style="margin-top:.75rem;padding:.5rem 1.25rem;font-size:1rem">Authorize</button>
</form></body>"""

BAD_REDIRECT = """<!doctype html><title>alexandria</title>
<body style="font-family:system-ui;max-width:26rem;margin:15vh auto">
<h2>alexandria</h2>
<p>This link asks to send your access somewhere the application did not register.
Nothing was authorized. If you followed a link from an email or a message, close
this page.</p></body>"""

AUTH_PARAMS = ["response_type", "client_id", "redirect_uri", "state",
               "code_challenge", "code_challenge_method"]


def install_oauth(api, *, jwt_secret: str, passphrase: str,
                  access_ttl: int = ACCESS_TTL, refresh_ttl: int = REFRESH_TTL):
    """Mount the OAuth 2.1 endpoints on `api`, and return `read_access_token`.

    FastAPI and PyJWT are imported here rather than at module scope so the
    registration helpers above stay importable with nothing but the standard
    library.
    """
    import jwt
    from fastapi import Form, Request
    from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

    def base_url(request) -> str:
        # `.get`, not `[...]`: a request without a Host header is malformed
        # rather than exceptional, and indexing turned it into a 500. The
        # value is still the client's to choose, which is the open finding
        # in docs/security/audit-2026-09-24.md on pinning the public host.
        return f"https://{request.headers.get('host', '')}"

    def mint(claims: dict, ttl: int) -> str:
        return jwt.encode({**claims, "iat": int(time.time()), "exp": int(time.time()) + ttl},
                          jwt_secret, algorithm="HS256")

    def read_token(token: str, expected_type: str) -> dict | None:
        try:
            claims = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            return claims if claims.get("typ") == expected_type else None
        except jwt.PyJWTError:
            return None

    def registered(client_id: str, redirect_uri: str) -> bool:
        return check_redirect_uri(client_id, redirect_uri, jwt_secret)

    @api.get("/.well-known/oauth-authorization-server")
    def auth_metadata(request: Request):
        b = base_url(request)
        return {
            "issuer": b,
            "authorization_endpoint": f"{b}/authorize",
            "token_endpoint": f"{b}/token",
            "registration_endpoint": f"{b}/register",
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code", "refresh_token"],
            "code_challenge_methods_supported": ["S256"],
            "token_endpoint_auth_methods_supported": ["none"],
        }

    @api.get("/.well-known/oauth-protected-resource")
    @api.get("/.well-known/oauth-protected-resource/mcp")
    def resource_metadata(request: Request):
        b = base_url(request)
        return {"resource": f"{b}/mcp", "authorization_servers": [b]}

    @api.post("/register")
    async def register(request: Request):
        try:
            body = await request.json()
        except ValueError:
            return JSONResponse({"error": "invalid_client_metadata",
                                 "error_description": "body must be JSON"}, status_code=400)
        try:
            redirect_uris = normalize_redirect_uris(body.get("redirect_uris"))
        except RegistrationError as exc:
            return JSONResponse({"error": "invalid_redirect_uri",
                                 "error_description": str(exc)}, status_code=400)
        return JSONResponse(
            {"client_id": issue_client_id(redirect_uris, jwt_secret),
             "redirect_uris": redirect_uris,
             "token_endpoint_auth_method": "none",
             "client_id_issued_at": int(time.time())},
            status_code=201,
        )

    @api.get("/authorize")
    def authorize_form(request: Request):
        q = request.query_params
        if q.get("response_type") != "code" or q.get("code_challenge_method") != "S256":
            return JSONResponse({"error": "unsupported_response_type"}, status_code=400)
        # Checked before the passphrase form is ever drawn, so a crafted link
        # never becomes a place to type the passphrase into. The refusal renders
        # here and never redirects: bouncing to an unvalidated redirect_uri is
        # the same leak in a politer costume.
        if not registered(q.get("client_id", ""), q.get("redirect_uri", "")):
            return HTMLResponse(BAD_REDIRECT, status_code=400)
        hidden = "".join(
            f'<input type="hidden" name="{p}" value="{html.escape(q.get(p, ""), quote=True)}">'
            for p in AUTH_PARAMS
        )
        return HTMLResponse(LOGIN_FORM.format(msg="Enter the passphrase to connect.", hidden=hidden))

    @api.post("/authorize")
    def authorize_submit(request: Request,
                         passphrase_field: str = Form("", alias="passphrase"),
                         response_type: str = Form(""),
                         client_id: str = Form(""), redirect_uri: str = Form(""),
                         state: str = Form(""), code_challenge: str = Form(""),
                         code_challenge_method: str = Form("")):
        # Re-checked on the post, not only on the get: the form is a client-side
        # artifact and its hidden fields are the attacker's to rewrite.
        if not registered(client_id, redirect_uri):
            return HTMLResponse(BAD_REDIRECT, status_code=400)
        if not hmac.compare_digest(passphrase_field, passphrase):
            hidden = "".join(
                f'<input type="hidden" name="{p}" value="{html.escape(v, quote=True)}">'
                for p, v in [("response_type", response_type), ("client_id", client_id),
                             ("redirect_uri", redirect_uri), ("state", state),
                             ("code_challenge", code_challenge),
                             ("code_challenge_method", code_challenge_method)]
            )
            return HTMLResponse(LOGIN_FORM.format(msg="Wrong passphrase — try again.", hidden=hidden),
                                status_code=401)
        code = mint({"typ": "code", "cid": client_id, "ru": redirect_uri,
                     "cc": code_challenge}, ttl=600)
        # `state` is the client's opaque round-trip value and it arrives from a
        # form field, so it is encoded rather than pasted in. Pasted raw, a
        # state of "a&scope=admin" adds a parameter to the client's callback
        # and one containing "#" truncates the query into a fragment. The JWT
        # in `code` is unaffected: its alphabet is already URL-safe.
        query = urlencode({"code": code, "state": state})
        sep = "&" if "?" in redirect_uri else "?"
        return RedirectResponse(f"{redirect_uri}{sep}{query}", status_code=302)

    @api.post("/token")
    def token(grant_type: str = Form(...), code: str = Form(None),
              redirect_uri: str = Form(None), client_id: str = Form(None),
              code_verifier: str = Form(None), refresh_token: str = Form(None)):
        if grant_type == "authorization_code":
            claims = read_token(code or "", "code")
            if not claims or claims.get("ru") != redirect_uri or claims.get("cid") != client_id:
                return JSONResponse({"error": "invalid_grant"}, status_code=400)
            # The third check. A code minted before a registration changed, or
            # replayed against a different redirect_uri, dies here.
            if not registered(client_id, redirect_uri):
                return JSONResponse({"error": "invalid_grant",
                                     "error_description": "redirect_uri"}, status_code=400)
            digest = hashlib.sha256((code_verifier or "").encode()).digest()
            challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
            if not hmac.compare_digest(challenge, claims.get("cc", "")):
                return JSONResponse({"error": "invalid_grant", "error_description": "pkce"},
                                    status_code=400)
        elif grant_type == "refresh_token":
            claims = read_token(refresh_token or "", "refresh")
            if not claims:
                return JSONResponse({"error": "invalid_grant"}, status_code=400)
        else:
            return JSONResponse({"error": "unsupported_grant_type"}, status_code=400)
        return {
            "access_token": mint({"typ": "access"}, access_ttl),
            "token_type": "Bearer",
            "expires_in": access_ttl,
            "refresh_token": mint({"typ": "refresh"}, refresh_ttl),
        }

    def read_access_token(token_str: str) -> dict | None:
        return read_token(token_str, "access")

    return read_access_token
