"""Triage: route untriaged bronze papers with a small model, logging every decision.

Runs daily on Modal after ingest. Requires the `neon` and `groq` secrets.

    modal run pipeline/triage.py                  # test run, 2 batches
    modal run pipeline/triage.py --max-calls 25   # bigger manual run
    modal deploy pipeline/triage.py               # install the daily schedule

Design notes:
- Groq's free tier binds on tokens/day, so papers are triaged BATCH per call.
- Anything older than BACKFILL_DAYS is auto-indexed by rule, not judged by the
  model — historical blog archives don't deserve LLM budget.
- A 429 from Groq ends the run gracefully; tomorrow's run resumes where we left off
  (the left-join-on-triage_log query is the resume mechanism).
"""

import hashlib
import json
import time

import modal

MODEL = "openai/gpt-oss-120b"  # largest open model on Groq's free tier as of 2026-09
BATCH = 10
BACKFILL_DAYS = 60
DECISIONS = {"discard", "index", "distill", "deep_read"}

image = (
    modal.Image.debian_slim()
    .pip_install("psycopg[binary]==3.2.4", "httpx==0.28.1")
    .add_local_file("prompts/triage.md", "/root/prompts/triage.md")
)

app = modal.App("alexandria-triage", image=image)

BATCH_INSTRUCTIONS = """
You will receive several papers, each numbered and carrying its source tier.
Apply the routing rules to each one independently. Respond with JSON only:
{"results": [{"i": <number>, "decision": "...", "score": 0.0, "reasoning": "..."}]}
Include every paper exactly once.
"""


def load_prompt() -> tuple[str, str]:
    text = open("/root/prompts/triage.md").read()
    return text, hashlib.sha256(text.encode()).hexdigest()[:12]


def call_groq(api_key: str, system: str, user: str) -> dict:
    import httpx

    resp = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": MODEL,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
        timeout=120,
    )
    resp.raise_for_status()
    return json.loads(resp.json()["choices"][0]["message"]["content"])


@app.function(
    schedule=modal.Cron("0 12 * * *"),  # one hour after ingest
    secrets=[modal.Secret.from_name("neon"), modal.Secret.from_name("groq")],
    timeout=3600,
)
def triage(max_calls: int = 25):
    import os

    import httpx
    import psycopg

    prompt, sha = load_prompt()
    system = prompt + BATCH_INSTRUCTIONS

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        backfilled = conn.execute(
            """
            insert into triage_log (paper_id, decision, reasoning, model, prompt_sha)
            select p.id, 'index', 'backfill: predates pipeline, auto-indexed by rule', 'rule:backfill', %s
            from papers p left join triage_log t on t.paper_id = p.id
            where t.id is null
              and (p.published_at is null or p.published_at < current_date - %s)
            """,
            (sha, BACKFILL_DAYS),
        ).rowcount
        conn.commit()
        print(f"backfilled {backfilled} old papers as index")

        rows = conn.execute(
            """
            select p.id, p.title, p.abstract, p.tier
            from papers p left join triage_log t on t.paper_id = p.id
            where t.id is null
            order by case p.tier when 'b' then 0 when 'c' then 1 when 'd' then 2
                                 when 'a' then 3 else 4 end,
                     p.published_at desc nulls last
            limit %s
            """,
            (BATCH * max_calls,),
        ).fetchall()
        print(f"{len(rows)} papers queued for model triage")

        judged = 0
        for start in range(0, len(rows), BATCH):
            chunk = rows[start : start + BATCH]
            lines = []
            for i, (_, title, abstract, tier) in enumerate(chunk):
                body = (abstract or "")[:1500] or "(no abstract; judge from title)"
                lines.append(f"[{i}] tier={tier}\ntitle: {title}\nabstract: {body}")
            try:
                out = call_groq(os.environ["GROQ_API_KEY"], system, "\n\n".join(lines))
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 429:
                    print("rate limited by Groq; stopping — next run resumes")
                    break
                raise
            results = {r.get("i"): r for r in out.get("results", []) if isinstance(r, dict)}
            for i, (paper_id, _, _, _) in enumerate(chunk):
                r = results.get(i)
                if r is None or r.get("decision") not in DECISIONS:
                    print(f"  no valid decision for {paper_id}; leaving untriaged")
                    continue
                conn.execute(
                    """
                    insert into triage_log (paper_id, decision, score, reasoning, model, prompt_sha)
                    values (%s, %s, %s, %s, %s, %s)
                    """,
                    (paper_id, r["decision"], r.get("score"), r.get("reasoning"), MODEL, sha),
                )
                judged += 1
            conn.commit()
            time.sleep(3)  # stay under 30 requests/minute

        print(f"triaged {judged} papers with {MODEL}")
        return judged


@app.local_entrypoint()
def main(max_calls: int = 2):
    print(f"judged: {triage.remote(max_calls)}")
