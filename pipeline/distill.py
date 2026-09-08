"""Distill: extract claims from triage-routed papers.

Currently in bake-off mode (README roadmap): two free-tier models run the same
distill prompt on the same papers; the human grades anonymized outputs and the
winner becomes the production distiller. Provider-agnostic by construction —
every provider speaks the OpenAI-compatible chat API.

    modal run pipeline/distill.py::bake_off --n-papers 8
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

image = (
    modal.Image.debian_slim()
    .pip_install("psycopg[binary]==3.2.4", "httpx==0.28.1")
    .add_local_file("prompts/distill.md", "/root/prompts/distill.md")
)

app = modal.App("alexandria-distill", image=image)


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


@app.local_entrypoint()
def main(n_papers: int = 8):
    results = bake_off.remote(n_papers)
    with open("bakeoff_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"wrote bakeoff_results.json with {len(results)} papers")
