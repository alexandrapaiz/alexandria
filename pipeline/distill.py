"""Distill: extract claims from triage-routed papers into silver, with embeddings.

Production model: gpt-oss-120b on Groq — chosen by blind human bake-off over
Qwen3.8-27B (4-1-3; see docs/evals/2026-09-07-distill-bakeoff.json). Claims are
embedded in-process with Qwen3-Embedding-0.6B (pinned open weights; the embedding
model must never change silently — all vectors must come from one model).

Scheduled at 11:30 UTC, BEFORE triage's 12:00 run: both share Groq's daily token
budget, and distill is the higher-value-per-token job, so it spends first and
processes yesterday's triage output.

    modal run pipeline/distill.py --max-papers 5     # manual production run
    modal deploy pipeline/distill.py                 # install the daily schedule
    modal run pipeline/distill.py::bake_off          # rerun the model bake-off
"""

import hashlib
import json
import pathlib
import time

import modal

PROVIDERS = {
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "openai/gpt-oss-120b",
        "key_env": "GROQ_API_KEY",
        "pause": 3,
    },
    # gemini was evaluated and dropped: 7/8 calls failed with 429 even under
    # exponential backoff on the free tier — disqualified on reliability
    "qwen": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "qwen/qwen3.8-27b",
        "key_env": "GROQ_API_KEY",
        "pause": 3,
    },
}

PRODUCTION_PROVIDER = "groq"
EMBED_MODEL = "Qwen/Qwen3-Embedding-0.6B"

# Full-text distillation: skills are the product, and abstracts don't contain
# procedures — so every arXiv paper in the run gets its HTML full text, not
# the abstract. Triage routes ~3-6 papers/day to distill, so this fits the
# Groq budget; the cap is a safety valve for backlog days (deep_read papers
# sort first in the queue, so they always get full text).
FULLTEXT_MAX_PER_RUN = 15
FULLTEXT_CHARS = 24000

image = (
    modal.Image.debian_slim()
    .pip_install("psycopg[binary]==3.2.4", "httpx==0.28.1", "sentence-transformers")
    .add_local_file("prompts/distill.md", "/root/prompts/distill.md")
    .add_local_file("pipeline/evidence.py", "/root/evidence.py")
    # The taxonomy travels with the job, so the list the tests check is the list
    # the insert enforces.
    .add_local_file("pipeline/topics.py", "/root/topics.py")
)

app = modal.App("alexandria-distill", image=image)

hf_cache = modal.Volume.from_name("hf-cache", create_if_missing=True)


def evidence():
    """pipeline/evidence.py, wherever this is running from.

    Modal drops it at /root/evidence.py; a local `python3 pipeline/distill.py`
    import finds it beside this file. Same trick weekly.py uses for the token
    budget, for the same reason: the rules the tests check are the rules the
    run applies.
    """
    import sys

    here = str(pathlib.Path(__file__).resolve().parent)
    for path in ("/root", here):
        if path not in sys.path:
            sys.path.insert(0, path)
    import evidence as module

    return module


def topics():
    """pipeline/topics.py, wherever this is running from. The same two-path trick.

    The taxonomy has to be one object shared by the insert and the tests. A
    second copy of the list is how `prompts/distill.md` came to offer tags the
    database never accepted.
    """
    import sys

    here = str(pathlib.Path(__file__).resolve().parent)
    for path in ("/root", here):
        if path not in sys.path:
            sys.path.insert(0, path)
    import topics as module

    return module


def load_prompt() -> tuple[str, str]:
    """The distill prompt and the first 12 hex of its sha256.

    Written onto every claim as `claims.prompt_sha`, the way triage writes it
    onto every decision and the press writes it onto every issue. Until this
    landed, the deploy state of `prompts/distill.md` was unverifiable except by
    inference from the shape of the output: the research seat's brief of
    2026-09-26 found the interpret prompt seven days stale that way, after the
    stale prompt's output had already reached readers.
    """
    text = open("/root/prompts/distill.md").read()
    return text, hashlib.sha256(text.encode()).hexdigest()[:12]


def has_column(conn, table: str, column: str) -> bool:
    """Whether db/schema.sql has been applied since `column` landed.

    The column ships in the same PR as the code that writes it, and the schema
    is applied by hand (`modal run pipeline/db_setup.py`). Asking the database
    rather than assuming means a deploy that lands before the schema run
    distills normally instead of failing every insert.
    """
    return conn.execute(
        """
        select 1 from information_schema.columns
        where table_name = %s and column_name = %s
        """,
        (table, column),
    ).fetchone() is not None


def has_evidence_grade(conn) -> bool:
    """Whether db/schema.sql has been applied since evidence_grade landed.

    The column ships in the same PR as the code that writes it, and the schema
    is applied by hand (`modal run pipeline/db_setup.py`). Asking the database
    rather than assuming means a deploy that lands before the schema run
    distills normally instead of failing every insert.
    """
    return conn.execute(
        """
        select 1 from information_schema.columns
        where table_name = 'claims' and column_name = 'evidence_grade'
        """
    ).fetchone() is not None


def fetch_fulltext(paper_id: str) -> str | None:
    """arXiv serves full-paper HTML for most recent papers. Returns cleaned
    text (~FULLTEXT_CHARS) or None so the caller falls back to the abstract."""
    import html as htmllib
    import re

    import httpx

    if not paper_id.startswith("arxiv:"):
        return None  # blog posts: the feed summary already is the content
    arxiv_id = re.sub(r"v\d+$", "", paper_id.removeprefix("arxiv:"))
    try:
        resp = httpx.get(f"https://arxiv.org/html/{arxiv_id}",
                         follow_redirects=True, timeout=30)
        if resp.status_code != 200 or len(resp.text) < 5000:
            return None
        text = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", resp.text)
        text = re.sub(r"<[^>]+>", " ", text)
        text = htmllib.unescape(text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:FULLTEXT_CHARS] if len(text) > 2000 else None
    except Exception as exc:
        print(f"  fulltext fetch failed for {paper_id}: {exc}")
        return None


def extract_claims(provider: str, title: str, abstract: str) -> list[dict]:
    import os

    import httpx

    p = PROVIDERS[provider]
    prompt, _ = load_prompt()
    for attempt in range(4):
        resp = httpx.post(
            p["url"],
            headers={"Authorization": f"Bearer {os.environ[p['key_env']].strip()}"},
            json={
                "model": p["model"],
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"title: {title}\n\ncontent: {abstract}"},
                ],
            },
            timeout=180,
        )
        if resp.status_code == 429 and attempt < 3:
            wait = float(resp.headers.get("retry-after") or 20 * (attempt + 1))
            print(f"  {provider} rate limited; backing off {wait:.0f}s")
            time.sleep(min(wait, 120))
            continue
        resp.raise_for_status()
        out = json.loads(resp.json()["choices"][0]["message"]["content"])
        return out
    raise RuntimeError(f"{provider}: exhausted retries")


@app.function(
    secrets=[modal.Secret.from_name("neon"), modal.Secret.from_name("groq")],
    timeout=3600,
)
def bake_off(n_papers: int = 8) -> list[dict]:
    import os

    import psycopg

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        papers = conn.execute(
            """
            select id, title, abstract, url, triage_decision
            from distill_queue
            where abstract is not null and length(abstract) > 200
            order by case triage_decision when 'deep_read' then 0 else 1 end,
                     case tier when 'b' then 0 when 'c' then 1 else 2 end,
                     published_at desc nulls last
            limit %s
            """,
            (n_papers,),
        ).fetchall()

    results = []
    for pid, title, abstract, url, decision in papers:
        entry = {"paper_id": pid, "title": title, "url": url, "decision": decision}
        for provider in PROVIDERS:
            try:
                entry[provider] = extract_claims(provider, title, abstract[:6000]).get("claims", [])
            except Exception as exc:
                entry[provider] = [{"claim": f"PROVIDER ERROR: {exc}", "evidence": "", "topics": []}]
            time.sleep(PROVIDERS[provider]["pause"])
        results.append(entry)
        print(f"distilled both: {title[:60]}")
    return results


@app.function(
    schedule=modal.Cron("30 11 * * *"),  # after ingest, BEFORE triage (budget priority)
    secrets=[modal.Secret.from_name("neon"), modal.Secret.from_name("groq")],
    volumes={"/root/.cache/huggingface": hf_cache},
    timeout=3600,
)
def distill(max_papers: int = 30):
    import os

    import httpx
    import psycopg
    from sentence_transformers import SentenceTransformer

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        papers = conn.execute(
            """
            select id, title, abstract, triage_decision, source
            from distill_queue
            order by case triage_decision when 'deep_read' then 0 else 1 end,
                     published_at desc nulls last
            limit %s
            """,
            (max_papers,),
        ).fetchall()
        print(f"{len(papers)} papers queued for distillation")
        if not papers:
            return 0

        marking_fulltext = has_column(conn, "papers", "fulltext_chars")
        if not marking_fulltext:
            print("papers.fulltext_chars is missing, so the weekly issue cannot "
                  "say how much was read in full; run db/schema.sql")
        grading = has_evidence_grade(conn)
        grader = evidence() if grading else None
        if not grading:
            print("claims.evidence_grade is missing; run db/schema.sql to start grading")
        stamping = has_column(conn, "claims", "prompt_sha")
        if not stamping:
            print("claims.prompt_sha is missing, so nothing records which distill "
                  "prompt wrote a claim; run db/schema.sql")
        taxonomy = topics()
        _, sha = load_prompt()
        print(f"prompt_sha {sha} ({len(taxonomy.TOPICS)} topics accepted)")
        off_list: dict[str, int] = {}

        wrote_any = False
        fulltexts_used = 0     # the fetch budget: how many HTML pulls were tried
        read_in_full = 0       # how many papers' claims actually came from one
        graded: dict[str, int] = {}
        for pid, title, abstract, decision, source in papers:
            body = None
            if fulltexts_used < FULLTEXT_MAX_PER_RUN:
                body = fetch_fulltext(pid)
                if body:
                    fulltexts_used += 1
                    print(f"  full text ({len(body)} chars): {title[:50]}")
            used_fulltext = body is not None
            if body is None:
                body = (abstract or "")[:6000]
            try:
                out = extract_claims(PRODUCTION_PROVIDER, title, body)
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 429:
                    print("rate limited by Groq; stopping — next run resumes")
                    break
                if body is not None and len(body) > 6000:
                    # full text too large for the provider — fall back to abstract.
                    # The claims then came from the abstract, so this paper was
                    # NOT read in full and the marker has to say so: a stat the
                    # issue prints cannot be generous about what was read.
                    print(f"  provider rejected full text ({exc.response.status_code}); retrying with abstract")
                    used_fulltext = False
                    out = extract_claims(PRODUCTION_PROVIDER, title, (abstract or "")[:6000])
                else:
                    raise
            claims = out.get("claims", [])
            institutions = [i for i in (out.get("institutions") or []) if i][:3]
            if institutions:
                conn.execute(
                    "update papers set institutions = %s where id = %s",
                    (institutions, pid),
                )
            for c in claims:
                text = (c.get("claim") or "").strip()
                if not text:
                    continue
                # The taxonomy is enforced here, at the only place claims are
                # written. Tags are folded onto the closed list and anything
                # still unknown is dropped and counted, never stored: a tag that
                # no query can match is worse than no tag, because it looks like
                # coverage. pipeline/topics.py explains what the fold will and
                # will not do.
                tags, dropped = taxonomy.normalize(c.get("topics"))
                for tag in dropped:
                    off_list[tag] = off_list.get(tag, 0) + 1
                # Columns are assembled rather than branched because two optional
                # columns is four INSERTs, and the next one is eight. Every name
                # here is a literal from this file, so nothing user-supplied ever
                # reaches the statement text.
                cols = ["paper_id", "claim", "evidence", "topics", "procedure"]
                vals = [pid, text, c.get("evidence"), tags, c.get("procedure")]
                if grading:
                    row_grade = grader.grade(pid, c.get("evidence"), c.get("measured"), source)
                    graded[row_grade] = graded.get(row_grade, 0) + 1
                    cols.append("evidence_grade")
                    vals.append(row_grade)
                if stamping:
                    cols.append("prompt_sha")
                    vals.append(sha)
                conn.execute(
                    f"insert into claims ({', '.join(cols)}) "
                    f"values ({', '.join(['%s'] * len(cols))})",
                    tuple(vals),
                )
                wrote_any = True
            # fulltext_chars is how the weekly issue knows how much was read in
            # full. NULL means the abstract, which is the honest answer when
            # arXiv served no HTML.
            if used_fulltext:
                read_in_full += 1
            if marking_fulltext:
                conn.execute(
                    "update papers set distilled_at = now(), fulltext_chars = %s "
                    "where id = %s",
                    (len(body) if used_fulltext else None, pid),
                )
            else:
                conn.execute("update papers set distilled_at = now() where id = %s", (pid,))
            conn.commit()
            print(f"  {len(claims)} claims <- {title[:60]}")
            time.sleep(PROVIDERS[PRODUCTION_PROVIDER]["pause"])

        print(f"read {read_in_full} papers in full, "
              f"{len(papers) - read_in_full} from the abstract alone")
        if graded:
            tally = ", ".join(f"{g} {n}" for g, n in sorted(graded.items()))
            print(f"evidence grades this run: {tally}")
        # The off-list rate, printed every run. It was 3.9% for the pipeline's
        # whole life and nobody could have known, because nothing counted it.
        if off_list:
            worst = sorted(off_list.items(), key=lambda kv: (-kv[1], kv[0]))[:8]
            print("tags dropped as off-list: "
                  + ", ".join(f"{t!r} x{n}" for t, n in worst))
            print("  a tag dropped often is a proposal for prompts/distill.md, "
                  "which belongs to the research seat (ADR-12 whitelist)")

        # Embedding is blackboard work: sweep every unembedded claim and paper,
        # not just this run's, so any crash or missed backfill heals next run.
        pending = conn.execute(
            "select id, claim from claims where embedding is null"
        ).fetchall()
        pending_papers = conn.execute(
            """
            select id, title, coalesce(abstract, '')
            from papers where embedding is null
            order by fetched_at limit 500
            """
        ).fetchall()
        if pending or pending_papers:
            model = SentenceTransformer(EMBED_MODEL)
            hf_cache.commit()  # persist downloaded weights for future runs
        if pending:
            vectors = model.encode([t for _, t in pending], normalize_embeddings=True)
            for (claim_id, _), vec in zip(pending, vectors):
                conn.execute(
                    "update claims set embedding = %s::vector where id = %s",
                    (str(vec.tolist()), claim_id),
                )
            conn.commit()
            print(f"embedded {len(pending)} claims with {EMBED_MODEL}")
        if pending_papers:
            texts = [f"{t}\n\n{a[:2000]}" for _, t, a in pending_papers]
            vectors = model.encode(texts, normalize_embeddings=True)
            for (paper_id, _, _), vec in zip(pending_papers, vectors):
                conn.execute(
                    "update papers set embedding = %s::vector where id = %s",
                    (str(vec.tolist()), paper_id),
                )
            conn.commit()
            print(f"embedded {len(pending_papers)} papers with {EMBED_MODEL}")
        return len(pending)


@app.local_entrypoint()
def main(max_papers: int = 30):
    print(f"claims written: {distill.remote(max_papers)}")


@app.local_entrypoint()
def run_bake_off(n_papers: int = 8):
    results = bake_off.remote(n_papers)
    with open("bakeoff_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"wrote bakeoff_results.json with {len(results)} papers")
