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

The second half of this module is the attempt throttle on `POST /authorize`. The
redirect-URI check above decides *where* a token may be sent. The throttle
decides *how often* someone may guess the one passphrase that decides whether a
token is minted at all. Registration is open by design, so an attacker registers
their own client, reaches the form legitimately, and meets the passphrase with
the redirect-URI check already satisfied. Before the throttle, being wrong cost
nothing: forty consecutive wrong passphrases returned forty 401s with no delay,
no counter, and no ceiling.
"""

import base64
import hashlib
import hmac
import html
import json
import time
import uuid
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


# ---------------- the attempt throttle on the passphrase ----------------

#: Wrong passphrases that cost nothing. The owner mistypes, and three free
#: attempts mean she never meets this machinery at all in normal use.
FREE_ATTEMPTS = 3

#: The ceiling on the required wait, in seconds. It is deliberately low. The
#: brief this was built from says the limiter must back off rather than bar,
#: because the passphrase behind it is the owner's only way into her own
#: connector. A minute is the longest an attacker can make her wait, and it
#: still cuts a guesser from unbounded to sixty attempts an hour.
MAX_BACKOFF = 60

#: A run of failures this old is not the same run of failures. Without a decay
#: the counter only ever climbs, and an owner who mistyped six times last March
#: would pay the ceiling forever.
ATTEMPT_DECAY = 3600

#: One passphrase, one user, one gate, so one counter. Per-IP scoping was
#: considered and dropped: behind Modal's proxy the client address comes from a
#: forwarded header, and both ways of getting that wrong are bad. Trust the
#: header and an attacker rotates it for free. Do not trust it and every caller
#: collapses to the proxy's own address, which turns a per-IP limit into a
#: second global limit that an attacker can hold down on the owner. A global
#: counter cannot be escaped by rotating addresses and cannot be aimed at one
#: victim, because there is only one account to aim at.
GLOBAL_SCOPE = "mcp-authorize"


def backoff_seconds(fails: int) -> int:
    """Seconds that must pass before the next attempt, given `fails` already recorded.

    Zero until the free allowance is spent, so FREE_ATTEMPTS wrong passphrases
    in a row cost nothing at all. Then doubling, then flat at MAX_BACKOFF.
    """
    if fails < FREE_ATTEMPTS:
        return 0
    return min(2 ** (fails - FREE_ATTEMPTS), MAX_BACKOFF)


class MemoryAttemptStore:
    """Attempt counts in process memory. Correct, and forgetful.

    This is what the throttle falls back to when the database cannot be
    reached, and what the tests use. On Modal it is not enough on its own: the
    container scales to zero, so the count dies with it, and a second replica
    keeps its own. That is the reason the real store below is in Postgres.
    """

    def __init__(self):
        self._rows: dict[str, tuple[int, float]] = {}

    def read(self, scope: str) -> tuple[int, float] | None:
        row = self._rows.get(scope)
        if row is None:
            return None
        fails, last = row
        return fails, time.time() - last

    def record_failure(self, scope: str, decay: int) -> int:
        fails, last = self._rows.get(scope, (0, 0.0))
        fails = 1 if time.time() - last > decay else fails + 1
        self._rows[scope] = (fails, time.time())
        return fails

    def reset(self, scope: str) -> None:
        self._rows.pop(scope, None)


class PostgresAttemptStore:
    """Attempt counts in the `auth_attempts` table, so they survive a cold start.

    Takes a zero-argument `connect` callable rather than a connection, because
    the MCP server opens a connection per call and the throttle should not hold
    one open between requests. Every statement is a single round trip.
    """

    READ = "select fails, extract(epoch from (now() - last_fail)) from auth_attempts where scope = %s"
    RECORD = """
        insert into auth_attempts (scope, fails, last_fail) values (%s, 1, now())
        on conflict (scope) do update
           set fails = case when auth_attempts.last_fail < now() - make_interval(secs => %s)
                            then 1 else auth_attempts.fails + 1 end,
               last_fail = now()
        returning fails
    """
    RESET = "delete from auth_attempts where scope = %s"

    def __init__(self, connect):
        self._connect = connect

    def read(self, scope: str) -> tuple[int, float] | None:
        with self._connect() as conn:
            row = conn.execute(self.READ, (scope,)).fetchone()
        return (int(row[0]), float(row[1])) if row else None

    def record_failure(self, scope: str, decay: int) -> int:
        with self._connect() as conn:
            row = conn.execute(self.RECORD, (scope, decay)).fetchone()
            conn.commit()
        return int(row[0])

    def reset(self, scope: str) -> None:
        with self._connect() as conn:
            conn.execute(self.RESET, (scope,))
            conn.commit()


class Throttle:
    """How long the next passphrase attempt has to wait, and why.

    The store is pluggable and the degraded path is deliberate. If Postgres
    cannot be reached, this falls back to an in-process counter rather than
    either barring the owner or dropping the limit entirely. A database outage
    should cost the throttle its memory, not cost the owner her connector, and
    an attacker who wants the weaker limit has to take Neon down to get it.
    """

    def __init__(self, store=None, *, fallback=None, on_error=None,
                 free=FREE_ATTEMPTS, cap=MAX_BACKOFF, decay=ATTEMPT_DECAY):
        self.store = store if store is not None else MemoryAttemptStore()
        self.fallback = fallback if fallback is not None else MemoryAttemptStore()
        self.on_error = on_error
        self.free, self.cap, self.decay = free, cap, decay

    def _wait(self, fails: int) -> int:
        if fails < self.free:
            return 0
        return min(2 ** (fails - self.free), self.cap)

    def _with_store(self, call):
        """Run `call(store)` against Postgres, and against memory if that fails."""
        try:
            return call(self.store)
        except Exception as exc:  # noqa: BLE001 - any driver error degrades the same way
            if self.on_error is not None:
                self.on_error(exc)
            return call(self.fallback)

    def retry_after(self, scope: str = GLOBAL_SCOPE) -> int:
        """Seconds the caller must still wait, or 0 if the attempt may proceed.

        Read-only on purpose. A blocked attempt does not count as a failure,
        so hammering the endpoint while blocked cannot push the wait out
        further. The wait is always measured from the last *counted* failure.
        """
        row = self._with_store(lambda store: store.read(scope))
        if row is None:
            return 0
        fails, since = row
        if since > self.decay:
            return 0
        return max(0, self._wait(fails) - int(since))

    def record_failure(self, scope: str = GLOBAL_SCOPE) -> int:
        """Count one wrong passphrase. Returns the new failure count."""
        return self._with_store(lambda store: store.record_failure(scope, self.decay))

    def record_success(self, scope: str = GLOBAL_SCOPE) -> None:
        """The right passphrase clears the slate."""
        self._with_store(lambda store: store.reset(scope))


# ---------------- single-use authorization codes ----------------

#: How long a freshly minted code is good for. It was 600 seconds, which is ten
#: minutes in which a leaked code could be spent. A real exchange takes well
#: under a second, because the client redirects straight from `/authorize` to
#: `/token`, so this is generous already and shrinks the leaked-code window
#: tenfold. It is the cheap half of the fix; the ledger below is the real half.
CODE_TTL = 60


class MemoryCodeLedgerStore:
    """Spent codes in process memory. Correct, and forgetful.

    Same role the memory attempt store plays for the throttle: the tests use it,
    and it is what the ledger degrades to when Postgres cannot be reached. On
    Modal it is not enough on its own, for the same reason. A container that
    scales to zero forgets which codes it has seen, and a second replica never
    knew.
    """

    def __init__(self):
        self._rows: dict[str, bool] = {}

    def consume(self, jti: str, expires_at: float) -> bool:
        if jti in self._rows:
            return False
        self._rows[jti] = False
        return True

    def revoke(self, jti: str) -> None:
        if jti in self._rows:
            self._rows[jti] = True

    def is_revoked(self, jti: str) -> bool:
        return self._rows.get(jti, False)


class PostgresCodeLedgerStore:
    """Spent codes in the `consumed_codes` table, so they survive a cold start.

    Takes a zero-argument `connect` callable for the same reason the attempt
    store does: the MCP server opens a connection per call and nothing here
    should hold one open between requests.

    `CONSUME` is the whole single-use guarantee and it is one statement on
    purpose. `on conflict do nothing returning jti` returns a row only when this
    insert was the one that created it, so two replicas racing on the same code
    cannot both be told they were first. A read-then-write would have that race;
    this does not.

    A row is not a spent code, it is a session: `expires_at` is set to the death
    of the longest-lived token the exchange hands out, not to the code's own
    60-second expiry. If it were the latter, the row would be purged a minute
    after login and there would be nothing left to mark revoked for the 180 days
    the refresh token still works.
    """

    CONSUME = """
        insert into consumed_codes (jti, expires_at) values (%s, to_timestamp(%s))
        on conflict (jti) do nothing
        returning jti
    """
    REVOKE = "update consumed_codes set revoked = true where jti = %s"
    IS_REVOKED = "select revoked from consumed_codes where jti = %s"
    PURGE = "delete from consumed_codes where expires_at < now()"

    def __init__(self, connect):
        self._connect = connect

    def consume(self, jti: str, expires_at: float) -> bool:
        with self._connect() as conn:
            row = conn.execute(self.CONSUME, (jti, expires_at)).fetchone()
            # Opportunistic, in the same transaction as the insert that pays for
            # the connection. Exchanges happen once per login, so this is a rare
            # statement against a table with one row per login.
            conn.execute(self.PURGE)
            conn.commit()
        return row is not None

    def revoke(self, jti: str) -> None:
        with self._connect() as conn:
            conn.execute(self.REVOKE, (jti,))
            conn.commit()

    def is_revoked(self, jti: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(self.IS_REVOKED, (jti,)).fetchone()
        return bool(row[0]) if row else False


class CodeLedger:
    """Which authorization codes have been spent, and which sessions are dead.

    Two jobs, both required by OAuth 2.1 section 4.1.2: a code may be exchanged
    once, and a code exchanged twice revokes the tokens already issued from it.

    The degraded path matches the throttle's, and for the same stated reason. If
    Postgres cannot be reached this falls back to an in-process ledger rather
    than refusing every exchange. That choice is fail-open and it is deliberate:
    a Neon outage should cost this check its memory, not cost the owner the only
    way into her own connector. An attacker who wants the weaker behaviour has
    to take the database down to get it, and the throttle is still in front of
    the passphrase while they try.
    """

    def __init__(self, store=None, *, fallback=None, on_error=None):
        self.store = store if store is not None else MemoryCodeLedgerStore()
        self.fallback = fallback if fallback is not None else MemoryCodeLedgerStore()
        self.on_error = on_error

    def _with_store(self, call):
        try:
            return call(self.store)
        except Exception as exc:  # noqa: BLE001 - any driver error degrades the same way
            if self.on_error is not None:
                self.on_error(exc)
            return call(self.fallback)

    def consume(self, jti: str, expires_at: float) -> bool:
        """True if this is the code's first exchange. False means a replay."""
        return self._with_store(lambda store: store.consume(jti, expires_at))

    def revoke(self, jti: str) -> None:
        """Kill every token issued from this code.

        Called when a code is presented twice. The server cannot tell which of
        the two callers was the attacker, so the spec's answer is to trust
        neither, and this follows it. The owner's cost is that she authorizes
        again, which the passphrase still lets her do at any time. Revoking
        cannot lock her out, it can only log her out.
        """
        self._with_store(lambda store: store.revoke(jti))

    def is_revoked(self, jti: str) -> bool:
        return self._with_store(lambda store: store.is_revoked(jti))


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

TOO_MANY = """<!doctype html><title>alexandria</title>
<body style="font-family:system-ui;max-width:26rem;margin:15vh auto">
<h2>alexandria</h2>
<p>Too many wrong passphrases. Wait {wait} and try again. Nothing is locked.
If this was not you, someone is guessing. The wait is what stops them.</p>
<form method="post" action="/authorize">
{hidden}
<input type="password" name="passphrase" placeholder="passphrase"
       style="width:100%;padding:.5rem;font-size:1rem">
<button style="margin-top:.75rem;padding:.5rem 1.25rem;font-size:1rem">Authorize</button>
</form></body>"""

AUTH_PARAMS = ["response_type", "client_id", "redirect_uri", "state",
               "code_challenge", "code_challenge_method"]


def install_oauth(api, *, jwt_secret: str, passphrase: str,
                  access_ttl: int = ACCESS_TTL, refresh_ttl: int = REFRESH_TTL,
                  throttle=None, code_ledger=None):
    """Mount the OAuth 2.1 endpoints on `api`, and return `read_access_token`.

    FastAPI and PyJWT are imported here rather than at module scope so the
    registration helpers above stay importable with nothing but the standard
    library.

    `throttle` and `code_ledger` both default to in-process ones. The deployed
    server passes Postgres-backed ones, because a Modal container that scales to
    zero forgets an in-process count, or an in-process list of spent codes, the
    moment it stops.
    """
    import jwt
    from fastapi import Form, Request
    from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

    if throttle is None:
        throttle = Throttle()
    if code_ledger is None:
        code_ledger = CodeLedger()

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
        hidden = "".join(
            f'<input type="hidden" name="{p}" value="{html.escape(v, quote=True)}">'
            for p, v in [("response_type", response_type), ("client_id", client_id),
                         ("redirect_uri", redirect_uri), ("state", state),
                         ("code_challenge", code_challenge),
                         ("code_challenge_method", code_challenge_method)]
        )
        # Asked after the registration check, so junk that never had a client_id
        # cannot run the counter up, and before the comparison, so a blocked
        # attempt learns nothing at all about the passphrase.
        wait = throttle.retry_after()
        if wait > 0:
            plural = "1 second" if wait == 1 else f"{wait} seconds"
            return HTMLResponse(TOO_MANY.format(wait=plural, hidden=hidden),
                                status_code=429, headers={"Retry-After": str(wait)})
        if not hmac.compare_digest(passphrase_field, passphrase):
            throttle.record_failure()
            return HTMLResponse(LOGIN_FORM.format(msg="Wrong passphrase, try again.", hidden=hidden),
                                status_code=401)
        throttle.record_success()
        # `jti` is what makes the code single-use: it is the name the ledger
        # records when the code is spent, and the name every token minted from
        # this code carries so the whole session can be revoked together.
        code = mint({"typ": "code", "cid": client_id, "ru": redirect_uri,
                     "cc": code_challenge, "jti": uuid.uuid4().hex}, ttl=CODE_TTL)
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
            # Spending the code is the last check, deliberately. Every cheaper
            # reason to refuse has already run, so a request that fails one of
            # them does not burn a code the honest client is about to present.
            session = claims.get("jti") or ""
            if not session:
                # A code this server minted always carries one. Missing means a
                # code from before this check existed, and those are already
                # dead: the old TTL was ten minutes and this shipped long after.
                return JSONResponse({"error": "invalid_grant"}, status_code=400)
            if not code_ledger.consume(session, time.time() + refresh_ttl):
                # OAuth 2.1 section 4.1.2: a code presented twice revokes what
                # the first exchange issued. Neither caller can be trusted now.
                code_ledger.revoke(session)
                return JSONResponse({"error": "invalid_grant",
                                     "error_description": "replay"}, status_code=400)
        elif grant_type == "refresh_token":
            claims = read_token(refresh_token or "", "refresh")
            if not claims:
                return JSONResponse({"error": "invalid_grant"}, status_code=400)
            # A refresh token from a revoked session is dead, and this is where
            # revocation is actually enforced. `sid` missing means a token minted
            # before sessions existed: allowed, so that merging this does not log
            # the owner out of a connector she authorized months ago.
            session = claims.get("sid") or ""
            if session and code_ledger.is_revoked(session):
                return JSONResponse({"error": "invalid_grant",
                                     "error_description": "revoked"}, status_code=400)
        else:
            return JSONResponse({"error": "unsupported_grant_type"}, status_code=400)
        # Both grants carry the session forward, so a refresh chain stays
        # revocable for as long as it lives rather than only at its first link.
        session = claims.get("jti") or claims.get("sid") or ""
        return {
            "access_token": mint({"typ": "access", "sid": session}, access_ttl),
            "token_type": "Bearer",
            "expires_in": access_ttl,
            "refresh_token": mint({"typ": "refresh", "sid": session}, refresh_ttl),
        }

    def read_access_token(token_str: str) -> dict | None:
        return read_token(token_str, "access")

    return read_access_token
