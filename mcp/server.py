"""alexandria MCP server: the agentic layer's doorway into the corpus (ADR-11).

A thin MCP server on a Modal web endpoint. Four tools — semantic_search,
sql_query (SELECT-only), get_digest, propose_skill (opens a PR; the human merge
is the promotion, ADR-7). All intelligence stays in the calling agent; all
authority (DB password, GitHub token, embedding model) stays here.

Auth is OAuth 2.1 as the MCP spec standardizes it: authorization code + PKCE +
dynamic client registration, implemented stateless with signed JWTs and a
single passphrase login (one user). claude.ai custom connectors speak this flow
natively.

Secrets: `neon` (DATABASE_URL), `github` (GITHUB_TOKEN), `alexandria-auth`
(AUTH_JWT_SECRET — long random string; MCP_PASSPHRASE — the login passphrase).

    modal deploy mcp/server.py    # serve at https://<workspace>--alexandria-mcp-serve.modal.run
"""

import modal

EMBED_MODEL = "Qwen/Qwen3-Embedding-0.6B"
REPO = "alexandrapaiz/alexandria"

image = (
    modal.Image.debian_slim()
    .pip_install(
        "fastmcp>=2.10,<3",
        "fastapi>=0.115",
        "pyjwt>=2.9",
        "psycopg[binary]==3.2.4",
        "httpx==0.28.1",
        "sentence-transformers",
    )
)

app = modal.App("alexandria-mcp", image=image)
hf_cache = modal.Volume.from_name("hf-cache", create_if_missing=True)


@app.function(
    secrets=[
        modal.Secret.from_name("neon"),
        modal.Secret.from_name("github"),
        modal.Secret.from_name("alexandria-auth"),
    ],
    volumes={"/root/.cache/huggingface": hf_cache},
    timeout=600,
    scaledown_window=300,
)
@modal.asgi_app()
def serve():
    import base64
    import hashlib
    import hmac
    import os
    import re
    import time
    import uuid

    import httpx
    import jwt
    import psycopg
    from fastapi import FastAPI, Form, Request
    from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
    from fastmcp import FastMCP

    JWT_SECRET = os.environ["AUTH_JWT_SECRET"]
    PASSPHRASE = os.environ["MCP_PASSPHRASE"]
    ACCESS_TTL = 24 * 3600
    REFRESH_TTL = 180 * 24 * 3600

    def db():
        return psycopg.connect(
            os.environ["DATABASE_URL"],
            options="-c statement_timeout=15000",
        )

    def mint(claims: dict, ttl: int) -> str:
        return jwt.encode({**claims, "iat": int(time.time()), "exp": int(time.time()) + ttl},
                          JWT_SECRET, algorithm="HS256")

    def read_token(token: str, expected_type: str) -> dict | None:
        try:
            claims = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            return claims if claims.get("typ") == expected_type else None
        except jwt.PyJWTError:
            return None

    # ---------------- MCP tools ----------------

    mcp = FastMCP("alexandria")
    _embedder = []  # lazy singleton; loading takes ~20s on a cold container

    def embed(text: str) -> str:
        if not _embedder:
            from sentence_transformers import SentenceTransformer

            _embedder.append(SentenceTransformer(EMBED_MODEL))
        vec = _embedder[0].encode([text], normalize_embeddings=True)[0]
        return str(vec.tolist())

    @mcp.tool
    def semantic_search(query: str, k: int = 8) -> list[dict]:
        """Search the claim corpus by meaning. Returns the k nearest claims with
        their evidence, topics, source paper, and cosine similarity."""
        qvec = embed(query)
        with db() as conn:
            rows = conn.execute(
                """
                select c.id, c.claim, c.evidence, c.topics, p.title, p.url,
                       1 - (c.embedding <=> %s::vector) as similarity
                from claims c join papers p on p.id = c.paper_id
                where c.embedding is not null
                order by c.embedding <=> %s::vector
                limit %s
                """,
                (qvec, qvec, min(max(k, 1), 25)),
            ).fetchall()
        return [
            {"claim_id": r[0], "claim": r[1], "evidence": r[2], "topics": r[3],
             "paper": r[4], "url": r[5], "similarity": round(float(r[6]), 3)}
            for r in rows
        ]

    @mcp.tool
    def sql_query(sql: str) -> dict:
        """Run a read-only SQL query against the corpus (tables: papers,
        triage_log, claims, claim_links, citation_log, digests, promotions;
        views: deprecated_claims, triage_queue, distill_queue, interpret_queue).
        SELECT/WITH only; anything else is rejected. Returns up to 200 rows."""
        cleaned = sql.strip().rstrip(";")
        if ";" in cleaned or not re.match(r"^(select|with)\b", cleaned, re.IGNORECASE):
            return {"error": "only a single SELECT (or WITH ... SELECT) statement is allowed"}
        with db() as conn:
            conn.execute("set transaction read only")
            cur = conn.execute(cleaned)
            cols = [d.name for d in cur.description] if cur.description else []
            rows = cur.fetchmany(200)
        return {"columns": cols, "rows": [[str(v) if v is not None else None for v in r] for r in rows]}

    @mcp.tool
    def get_digest(week: str | None = None) -> dict:
        """Fetch the weekly digest — the latest one, or a specific ISO week
        like '2026-W37'."""
        with db() as conn:
            if week:
                row = conn.execute(
                    "select week, body, created_at from digests where week = %s", (week,)
                ).fetchone()
            else:
                row = conn.execute(
                    "select week, body, created_at from digests order by created_at desc limit 1"
                ).fetchone()
        if not row:
            return {"error": "no digest found"}
        return {"week": row[0], "body": row[1], "created_at": str(row[2])}

    @mcp.tool
    def propose_skill(slug: str, title: str, content: str,
                      claim_ids: list[int], rationale: str) -> dict:
        """Propose a new skill for the gold layer. Opens a pull request adding
        skills/<slug>.md to the repo and records a promotions row. The human
        merge is the promotion (ADR-7) — this tool cannot commit to main.
        `content` is the full markdown skill file; `rationale` explains why
        these claims justify a skill and appears in the PR description."""
        if not re.match(r"^[a-z0-9][a-z0-9-]{2,60}$", slug):
            return {"error": "slug must be lowercase-kebab-case, 3-61 chars"}
        gh = httpx.Client(
            base_url=f"https://api.github.com/repos/{REPO}",
            headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN'].strip()}",
                     "Accept": "application/vnd.github+json"},
            timeout=30,
        )
        main_sha = gh.get("/git/ref/heads/main").raise_for_status().json()["object"]["sha"]
        branch = f"skill/{slug}-{int(time.time())}"
        gh.post("/git/refs", json={"ref": f"refs/heads/{branch}", "sha": main_sha}).raise_for_status()
        gh.put(
            f"/contents/skills/{slug}.md",
            json={"message": f"skill proposal: {title}", "branch": branch,
                  "content": base64.b64encode(content.encode()).decode()},
        ).raise_for_status()
        body = (f"{rationale}\n\nClaims: {claim_ids}\n\n"
                "Proposed by the alexandria weekly agent — merging this PR is the promotion (ADR-7).")
        pr = gh.post(
            "/pulls",
            json={"title": f"skill: {title}", "head": branch, "base": "main", "body": body},
        ).raise_for_status().json()
        with db() as conn:
            row = conn.execute(
                "insert into promotions (claim_ids, kind, path) values (%s, 'skill', %s) returning id",
                (claim_ids, pr["html_url"]),
            ).fetchone()
            conn.commit()
        return {"pr_url": pr["html_url"], "promotion_id": row[0]}

    # ---------------- OAuth 2.1 (spec flow, stateless via JWTs) ----------------

    mcp_app = mcp.http_app(path="/mcp")
    api = FastAPI(lifespan=mcp_app.lifespan)

    def base_url(request: Request) -> str:
        return f"https://{request.headers['host']}"

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
        body = await request.json()
        return JSONResponse(
            {"client_id": uuid.uuid4().hex,
             "redirect_uris": body.get("redirect_uris", []),
             "token_endpoint_auth_method": "none",
             "client_id_issued_at": int(time.time())},
            status_code=201,
        )

    LOGIN_FORM = """<!doctype html><title>alexandria</title>
    <body style="font-family:system-ui;max-width:22rem;margin:15vh auto">
    <h2>alexandria</h2><p>{msg}</p>
    <form method="post" action="/authorize">
    {hidden}
    <input type="password" name="passphrase" placeholder="passphrase" autofocus
           style="width:100%;padding:.5rem;font-size:1rem">
    <button style="margin-top:.75rem;padding:.5rem 1.25rem;font-size:1rem">Authorize</button>
    </form></body>"""

    AUTH_PARAMS = ["response_type", "client_id", "redirect_uri", "state",
                   "code_challenge", "code_challenge_method"]

    @api.get("/authorize")
    def authorize_form(request: Request):
        q = request.query_params
        if q.get("response_type") != "code" or q.get("code_challenge_method") != "S256":
            return JSONResponse({"error": "unsupported_response_type"}, status_code=400)
        hidden = "".join(
            f'<input type="hidden" name="{p}" value="{q.get(p, "")}">' for p in AUTH_PARAMS
        )
        return HTMLResponse(LOGIN_FORM.format(msg="Enter the passphrase to connect.", hidden=hidden))

    @api.post("/authorize")
    def authorize_submit(request: Request,
                         passphrase: str = Form(""), response_type: str = Form(""),
                         client_id: str = Form(""), redirect_uri: str = Form(""),
                         state: str = Form(""), code_challenge: str = Form(""),
                         code_challenge_method: str = Form("")):
        if not hmac.compare_digest(passphrase, PASSPHRASE):
            hidden = "".join(
                f'<input type="hidden" name="{p}" value="{v}">'
                for p, v in [("response_type", response_type), ("client_id", client_id),
                             ("redirect_uri", redirect_uri), ("state", state),
                             ("code_challenge", code_challenge),
                             ("code_challenge_method", code_challenge_method)]
            )
            return HTMLResponse(LOGIN_FORM.format(msg="Wrong passphrase — try again.", hidden=hidden),
                                status_code=401)
        code = mint({"typ": "code", "cid": client_id, "ru": redirect_uri,
                     "cc": code_challenge}, ttl=600)
        sep = "&" if "?" in redirect_uri else "?"
        return RedirectResponse(f"{redirect_uri}{sep}code={code}&state={state}", status_code=302)

    @api.post("/token")
    def token(grant_type: str = Form(...), code: str = Form(None),
              redirect_uri: str = Form(None), client_id: str = Form(None),
              code_verifier: str = Form(None), refresh_token: str = Form(None)):
        if grant_type == "authorization_code":
            claims = read_token(code or "", "code")
            if not claims or claims.get("ru") != redirect_uri or claims.get("cid") != client_id:
                return JSONResponse({"error": "invalid_grant"}, status_code=400)
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
            "access_token": mint({"typ": "access"}, ACCESS_TTL),
            "token_type": "Bearer",
            "expires_in": ACCESS_TTL,
            "refresh_token": mint({"typ": "refresh"}, REFRESH_TTL),
        }

    # ---------------- bearer guard on /mcp, then mount ----------------

    @api.middleware("http")
    async def guard(request: Request, call_next):
        if request.url.path.startswith("/mcp"):
            auth = request.headers.get("authorization", "")
            token_ok = auth.startswith("Bearer ") and read_token(auth[7:], "access")
            if not token_ok:
                meta = f"{base_url(request)}/.well-known/oauth-protected-resource"
                return JSONResponse(
                    {"error": "unauthorized"},
                    status_code=401,
                    headers={"WWW-Authenticate": f'Bearer resource_metadata="{meta}"'},
                )
        return await call_next(request)

    api.mount("/", mcp_app)
    return api
