"""alexandria MCP server: the agentic layer's doorway into the corpus (ADR-11).

A thin MCP server on a Modal web endpoint. Tools — semantic_search, rag_answer
(retrieve-then-generate over the corpus, ADR-20), sql_query (SELECT-only),
discovery_report (candidate new topics/authors/institutions/sources, evidence
for a sources.yaml proposal — docs/product/source-discovery.md), get_digest,
propose_skill (opens a PR; the human merge is the promotion,
ADR-7). All intelligence stays in the calling agent; all authority (DB
password, GitHub token, embedding model) stays here. rag_answer is the one
exception: synthesis has to happen somewhere, so it happens server-side,
against a fixed prompt, over context the server itself retrieved — never
against the open corpus or the model's own training data.

Auth is OAuth 2.1 as the MCP spec standardizes it: authorization code + PKCE +
dynamic client registration, implemented stateless with signed JWTs and a
single passphrase login (one user). claude.ai custom connectors speak this flow
natively. Registration is stateless too: the `client_id` is itself a signed
token carrying the client's redirect URIs, so `/authorize` can reject a
redirect URI the client never registered without a store to look it up in. See
mcp/oauth_flow.py, which holds that check outside this container so it is testable.

Secrets: `neon` (DATABASE_URL), `github` (GITHUB_TOKEN), `JWT`
(AUTH_JWT_SECRET — long random signing string), `MCP` (MCP_PASSPHRASE — the
login passphrase typed on the authorize page).

    modal deploy mcp/server.py    # serve at https://<workspace>--alexandria-mcp-serve.modal.run
"""

import modal

EMBED_MODEL = "Qwen/Qwen3-Embedding-0.6B"
RAG_MODEL = "openai/gpt-oss-120b"  # same model as interpret.py; free-tier Groq
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
    .add_local_file("prompts/rag-answer.md", "/root/prompts/rag-answer.md")
    .add_local_file("mcp/oauth_flow.py", "/root/oauth_flow.py")
)

app = modal.App("alexandria-mcp", image=image)
hf_cache = modal.Volume.from_name("hf-cache", create_if_missing=True)


@app.function(
    secrets=[
        modal.Secret.from_name("neon"),
        modal.Secret.from_name("github"),
        modal.Secret.from_name("groq"),
        modal.Secret.from_name("JWT"),
        modal.Secret.from_name("MCP"),
    ],
    volumes={"/root/.cache/huggingface": hf_cache},
    timeout=600,
    scaledown_window=300,
)
@modal.asgi_app()
def serve():
    import base64
    import os
    import re
    import sys
    import time

    import httpx
    import psycopg

    sys.path.insert(0, "/root")  # where the image put oauth_flow.py
    import oauth_flow as oauth_clients
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    from fastmcp import FastMCP

    JWT_SECRET = os.environ["AUTH_JWT_SECRET"]
    PASSPHRASE = os.environ["MCP_PASSPHRASE"]
    ACCESS_TTL = 24 * 3600
    REFRESH_TTL = 180 * 24 * 3600

    def db():
        # Modal web containers sometimes resolve Neon to IPv6, which is
        # unroutable here ("Network is unreachable") — pin to IPv4. TLS still
        # verifies against the hostname; hostaddr only skips DNS.
        import socket
        from urllib.parse import urlparse

        # No startup options: Neon's pooler (PgBouncer) rejects them — timeouts
        # are set per-transaction with `set local` where untrusted SQL runs.
        url = os.environ["DATABASE_URL"]
        kwargs = {}
        try:
            host = urlparse(url).hostname
            kwargs["hostaddr"] = socket.getaddrinfo(host, 5432, socket.AF_INET)[0][4][0]
        except OSError:
            pass  # fall back to default resolution
        return psycopg.connect(url, **kwargs)

    def call_groq(api_key: str, system: str, user: str) -> dict:
        import json

        resp = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key.strip()}"},
            json={
                "model": RAG_MODEL,
                "temperature": 0.1,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
            timeout=60,
        )
        resp.raise_for_status()
        return json.loads(resp.json()["choices"][0]["message"]["content"])

    # ---------------- MCP tools ----------------

    mcp = FastMCP("alexandria")
    _embedder = []  # lazy singleton; loading takes ~20s on a cold container

    def embed(text: str) -> str:
        if not _embedder:
            from sentence_transformers import SentenceTransformer

            _embedder.append(SentenceTransformer(EMBED_MODEL))
        vec = _embedder[0].encode([text], normalize_embeddings=True)[0]
        return str(vec.tolist())

    def _retrieve(query: str, k: int) -> list[dict]:
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
    def semantic_search(query: str, k: int = 8) -> list[dict]:
        """Search the claim corpus by meaning. Returns the k nearest claims with
        their evidence, topics, source paper, and cosine similarity. This is
        retrieval only — no synthesis. Use rag_answer when you want a
        cited answer instead of a ranked list to read yourself."""
        return _retrieve(query, k)

    _rag_prompt = open("/root/prompts/rag-answer.md").read()

    @mcp.tool
    def rag_answer(question: str, k: int = 8) -> dict:
        """Retrieval-augmented generation over the claim corpus: retrieves the
        k nearest claims by meaning, then asks a model to synthesize a short,
        cited answer grounded only in that retrieved context — never in the
        model's own training data. Returns the answer with inline [C<id>]
        citations plus the source claims, so every sentence is checkable.
        Use this for "what does the corpus say about X" questions; use
        semantic_search instead when you want to read the raw claims yourself."""
        claims = _retrieve(question, k)
        if not claims:
            return {"answer": "The corpus has no embedded claims yet.", "citations": []}
        context = "\n\n".join(
            f"[C{c['claim_id']}] {c['claim']} (evidence: {c['evidence']}) "
            f"— {c['paper']}"
            for c in claims
        )
        user = f"CONTEXT:\n{context}\n\nQUESTION: {question}"
        try:
            out = call_groq(os.environ["GROQ_API_KEY"], _rag_prompt, user)
        except httpx.HTTPStatusError as exc:
            return {"error": f"synthesis model unavailable: {exc.response.status_code}"}
        by_id = {c["claim_id"]: c for c in claims}
        used_ids = [cid for cid in out.get("claim_ids_used", []) if cid in by_id]
        citations = [
            {"claim_id": cid, "paper": by_id[cid]["paper"], "url": by_id[cid]["url"]}
            for cid in used_ids
        ]
        return {"answer": out.get("answer", ""), "citations": citations}

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
            conn.execute("set local statement_timeout = 15000")
            cur = conn.execute(cleaned)
            cols = [d.name for d in cur.description] if cur.description else []
            rows = cur.fetchmany(200)
        return {"columns": cols, "rows": [[str(v) if v is not None else None for v in r] for r in rows]}

    @mcp.tool
    def discovery_report(days: int = 21) -> dict:
        """Surface candidates for what to start watching next: new topics,
        rising authors and institutions, and sources gaining traction faster
        than sources.yaml credits them for. This is evidence for a
        sources.yaml proposal via propose_change (docs/product/source-discovery.md)
        — it gathers, it does not decide, and a single instance of any signal
        below is an anecdote, not a proposal.

        Three read-only queries over data the pipeline already collects:

        - novel_topic_clusters: claims from the last `days` days whose nearest
          neighbor in the older corpus is distant in embedding space, grouped
          with other recent claims making the same move. The topics column is
          a closed 13-tag vocabulary (prompts/distill.md) that cannot name a
          genuinely new topic, so novelty has to be read from the embedding
          space instead — a higher cluster_size and nearest_old_distance means
          more independent papers converging on something the corpus has not
          seen before.
        - rising_authors / rising_institutions: authors and institutions first
          seen within `days` days with 2+ papers already routed past discard —
          a candidate new prolific researcher or lab. Reads thin until the
          corpus has a few months of depth: right after launch, everyone looks
          "first seen recently."
        - citation_velocity_outliers: papers gaining Semantic Scholar citations
          fastest (citation_log, the weekly slow loop) that came from a tier we
          do not already curate as a strong prior (not 'b' or 'c') — traction
          from a source sources.yaml treats as neutral or skeptical today.
        """
        window = max(1, min(days, 180))
        with db() as conn:
            novel = conn.execute(
                """
                with recent as (
                    select c.id, c.claim, c.embedding, c.paper_id, p.title, p.url
                    from claims c join papers p on p.id = c.paper_id
                    where c.created_at > now() - make_interval(days => %s)
                      and c.embedding is not null
                ),
                novelty as (
                    select r.id, r.claim, r.paper_id, r.title, r.url, r.embedding,
                        (select min(c2.embedding <=> r.embedding)
                         from claims c2
                         where c2.embedding is not null
                           and c2.created_at <= now() - make_interval(days => %s)) as nearest_old_distance
                    from recent r
                ),
                candidates as (
                    select * from novelty
                    where nearest_old_distance is null or nearest_old_distance > 0.35
                )
                select a.id, a.claim, a.title, a.url, a.nearest_old_distance,
                    (select count(*) from candidates b
                     where b.id != a.id and b.paper_id != a.paper_id
                       and (b.embedding <=> a.embedding) < 0.3) as cluster_size
                from candidates a
                order by cluster_size desc, a.nearest_old_distance desc nulls first
                limit 15
                """,
                (window, window),
            ).fetchall()

            rising_authors = conn.execute(
                """
                with author_rows as (
                    select unnest(p.authors) as author, p.id, p.published_at
                    from papers p
                    join triage_log t on t.paper_id = p.id
                        and t.decision in ('distill', 'deep_read')
                    where p.authors is not null
                ),
                first_seen as (
                    select author, min(published_at) as first_seen
                    from author_rows group by author
                )
                select ar.author, fs.first_seen, count(*) as papers_in_window
                from author_rows ar
                join first_seen fs on fs.author = ar.author
                where fs.first_seen > current_date - make_interval(days => %s)
                group by ar.author, fs.first_seen
                having count(*) >= 2
                order by papers_in_window desc, fs.first_seen desc
                limit 15
                """,
                (window,),
            ).fetchall()

            rising_institutions = conn.execute(
                """
                with inst_rows as (
                    select unnest(p.institutions) as institution, p.id, p.published_at
                    from papers p
                    join triage_log t on t.paper_id = p.id
                        and t.decision in ('distill', 'deep_read')
                    where p.institutions is not null
                ),
                first_seen as (
                    select institution, min(published_at) as first_seen
                    from inst_rows group by institution
                )
                select ir.institution, fs.first_seen, count(*) as papers_in_window
                from inst_rows ir
                join first_seen fs on fs.institution = ir.institution
                where fs.first_seen > current_date - make_interval(days => %s)
                group by ir.institution, fs.first_seen
                having count(*) >= 2
                order by papers_in_window desc, fs.first_seen desc
                limit 15
                """,
                (window,),
            ).fetchall()

            velocity = conn.execute(
                """
                with checks as (
                    select paper_id, citations, checked_at,
                           row_number() over (partition by paper_id order by checked_at desc) as rn
                    from citation_log
                )
                select p.title, p.url, p.tier, p.institutions,
                       prev.citations, latest.citations,
                       extract(epoch from (latest.checked_at - prev.checked_at)) / 86400 as days_between,
                       (latest.citations - prev.citations)
                         / greatest(extract(epoch from (latest.checked_at - prev.checked_at)) / 86400, 1) as citations_per_day
                from checks latest
                join checks prev on prev.paper_id = latest.paper_id and prev.rn = 2
                join papers p on p.id = latest.paper_id
                where latest.rn = 1
                  and latest.citations > prev.citations
                  and p.tier not in ('b', 'c')
                order by citations_per_day desc
                limit 15
                """
            ).fetchall()

        return {
            "novel_topic_clusters": [
                {"claim_id": r[0], "claim": r[1][:300], "paper": r[2], "url": r[3],
                 "nearest_old_distance": round(float(r[4]), 3) if r[4] is not None else None,
                 "cluster_size": r[5]}
                for r in novel
            ],
            "rising_authors": [
                {"author": r[0], "first_seen": str(r[1]), "papers_in_window": r[2]}
                for r in rising_authors
            ],
            "rising_institutions": [
                {"institution": r[0], "first_seen": str(r[1]), "papers_in_window": r[2]}
                for r in rising_institutions
            ],
            "citation_velocity_outliers": [
                {"paper": r[0], "url": r[1], "tier": r[2], "institutions": r[3],
                 "citations_before": r[4], "citations_now": r[5],
                 "days_between": round(float(r[6]), 1), "citations_per_day": round(float(r[7]), 2)}
                for r in velocity
            ],
        }

    @mcp.tool
    def get_digest(week: str | None = None, kind: str = "weekly") -> dict:
        """Fetch an issue of the digest. Pass an issue key for a specific one:
        an ISO week like '2026-W37' for a weekly, or a date like '2026-09-19'
        for a daily. With no key, returns the latest issue of `kind`, which is
        'weekly' (the Monday synthesis) unless you ask for 'daily'."""
        if kind not in ("weekly", "daily"):
            return {"error": "kind must be 'weekly' or 'daily'"}
        with db() as conn:
            if week:
                row = conn.execute(
                    "select week, kind, body, created_at from digests where week = %s",
                    (week,),
                ).fetchone()
            else:
                # explicitly filtered by kind: before the newsletter went daily
                # (2026-09-19) the latest row was always the weekly, and an
                # unfiltered "latest" now silently means "yesterday's daily"
                row = conn.execute(
                    """
                    select week, kind, body, created_at from digests
                    where kind = %s order by created_at desc limit 1
                    """,
                    (kind,),
                ).fetchone()
        if not row:
            return {"error": "no digest found"}
        return {"week": row[0], "kind": row[1], "body": row[2], "created_at": str(row[3])}

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

    @mcp.tool
    def propose_change(path: str, new_content: str, rationale: str) -> dict:
        """Meta-review: propose a change to the system's own prompts or sources
        as a pull request (ADR-7 — the human merge is the gate). Only
        prompts/*.md and sources.yaml may be targeted. `new_content` is the
        complete new file; `rationale` must cite the evidence (triage stats,
        graph errors, human verdicts) that justifies the change."""
        if not re.match(r"^(prompts/[a-z0-9_-]+\.md|sources\.yaml)$", path):
            return {"error": "only prompts/*.md and sources.yaml can be changed by proposal"}
        gh = httpx.Client(
            base_url=f"https://api.github.com/repos/{REPO}",
            headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN'].strip()}",
                     "Accept": "application/vnd.github+json"},
            timeout=30,
        )
        main_sha = gh.get("/git/ref/heads/main").raise_for_status().json()["object"]["sha"]
        branch = f"meta/{int(time.time())}"
        gh.post("/git/refs", json={"ref": f"refs/heads/{branch}", "sha": main_sha}).raise_for_status()
        existing = gh.get(f"/contents/{path}", params={"ref": "main"})
        put = {"message": f"meta-review proposal: {path}", "branch": branch,
               "content": base64.b64encode(new_content.encode()).decode()}
        if existing.status_code == 200:
            put["sha"] = existing.json()["sha"]
        gh.put(f"/contents/{path}", json=put).raise_for_status()
        body = (f"{rationale}\n\n"
                "Proposed by the alexandria meta-review — merging this PR is the approval (ADR-7).")
        pr = gh.post(
            "/pulls",
            json={"title": f"meta: {path}", "head": branch, "base": "main", "body": body},
        ).raise_for_status().json()
        with db() as conn:
            conn.execute(
                "insert into promotions (claim_ids, kind, path) values ('{}', 'system_diff', %s)",
                (pr["html_url"],),
            )
            conn.commit()
        return {"pr_url": pr["html_url"]}

    # ---------------- OAuth 2.1 (spec flow, stateless via JWTs) ----------------
    #
    # The endpoints live in mcp/oauth_flow.py, mounted here. That is not tidiness: it
    # is what lets tests/test_oauth_redirect_uri.py drive the real authorize and
    # token handlers in-process, with no Modal deployment and no secrets.

    mcp_app = mcp.http_app(path="/mcp")
    api = FastAPI(lifespan=mcp_app.lifespan)

    read_access_token = oauth_clients.install_oauth(
        api, jwt_secret=JWT_SECRET, passphrase=PASSPHRASE,
        access_ttl=ACCESS_TTL, refresh_ttl=REFRESH_TTL,
    )

    # ---------------- bearer guard on /mcp, then mount ----------------

    @api.middleware("http")
    async def guard(request: Request, call_next):
        if request.url.path.startswith("/mcp"):
            auth = request.headers.get("authorization", "")
            token_ok = auth.startswith("Bearer ") and read_access_token(auth[7:])
            if not token_ok:
                meta = f"https://{request.headers['host']}/.well-known/oauth-protected-resource"
                return JSONResponse(
                    {"error": "unauthorized"},
                    status_code=401,
                    headers={"WWW-Authenticate": f'Bearer resource_metadata="{meta}"'},
                )
        return await call_next(request)

    api.mount("/", mcp_app)
    return api
