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

import json
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

image = (
    modal.Image.debian_slim()
    .pip_install("psycopg[binary]==3.2.4", "httpx==0.28.1", "sentence-transformers")
    .add_local_file("prompts/distill.md", "/root/prompts/distill.md")
)

app = modal.App("alexandria-distill", image=image)

hf_cache = modal.Volume.from_name("hf-cache", create_if_missing=True)


def extract_claims(provider: str, title: str, abstract: str) -> list[dict]:
    import os

    import httpx

    p = PROVIDERS[provider]
    prompt = open("/root/prompts/distill.md").read()
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
                    {"role": "user", "content": f"title: {title}\n\nabstract: {abstract}"},
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
        return out.get("claims", [])
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
                entry[provider] = extract_claims(provider, title, abstract[:6000])
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
            select id, title, abstract, triage_decision
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

        new_claims = []  # (claim_id, text) pending embedding
        for pid, title, abstract, decision in papers:
            try:
                claims = extract_claims(PRODUCTION_PROVIDER, title, (abstract or "")[:6000])
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 429:
                    print("rate limited by Groq; stopping — next run resumes")
                    break
                raise
            for c in claims:
                text = (c.get("claim") or "").strip()
                if not text:
                    continue
                row = conn.execute(
                    """
                    insert into claims (paper_id, claim, evidence, topics)
                    values (%s, %s, %s, %s) returning id
                    """,
                    (pid, text, c.get("evidence"), c.get("topics") or []),
                ).fetchone()
                new_claims.append((row[0], text))
            conn.execute("update papers set distilled_at = now() where id = %s", (pid,))
            conn.commit()
            print(f"  {len(claims)} claims <- {title[:60]}")
            time.sleep(PROVIDERS[PRODUCTION_PROVIDER]["pause"])

        if new_claims:
            model = SentenceTransformer(EMBED_MODEL)
            hf_cache.commit()  # persist downloaded weights for future runs
            vectors = model.encode([t for _, t in new_claims], normalize_embeddings=True)
            for (claim_id, _), vec in zip(new_claims, vectors):
                conn.execute(
                    "update claims set embedding = %s::vector where id = %s",
                    (str(vec.tolist()), claim_id),
                )
            conn.commit()
            print(f"embedded {len(new_claims)} claims with {EMBED_MODEL}")
        return len(new_claims)


@app.local_entrypoint()
def main(max_papers: int = 30):
    print(f"claims written: {distill.remote(max_papers)}")


@app.local_entrypoint()
def run_bake_off(n_papers: int = 8):
    results = bake_off.remote(n_papers)
    with open("bakeoff_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"wrote bakeoff_results.json with {len(results)} papers")
