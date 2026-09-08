"""Interpret: relate new claims to existing ones, building the claim graph.

Runs daily on Modal after distill. Requires the `neon` and `groq` secrets.
No-ops harmlessly while the interpret_queue is empty (blackboard coordination).

    modal run pipeline/interpret.py               # manual run
    modal deploy pipeline/interpret.py            # install the daily schedule

Design (ADR-10): append-only and time-directional — a new claim judges its
older neighbors; edges are never edited. Candidates come from pgvector kNN
(retrieve cheap), the relation label from a model (reason on the shortlist).
"""

import hashlib
import json
import time

import modal

MODEL = "openai/gpt-oss-120b"
NEIGHBORS = 5
MAX_CLAIMS_PER_RUN = 100

image = (
    modal.Image.debian_slim()
    .pip_install("psycopg[binary]==3.2.4", "httpx==0.28.1")
    .add_local_file("prompts/interpret.md", "/root/prompts/interpret.md")
)

app = modal.App("alexandria-interpret", image=image)


def call_groq(api_key: str, system: str, user: str) -> dict:
    import httpx

    resp = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key.strip()}"},
        json={
            "model": MODEL,
            "temperature": 0.1,
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
    schedule=modal.Cron("0 14 * * *"),  # after distill's slot
    secrets=[modal.Secret.from_name("neon"), modal.Secret.from_name("groq")],
    timeout=3600,
)
def interpret(max_claims: int = MAX_CLAIMS_PER_RUN):
    import os

    import httpx
    import psycopg

    prompt = open("/root/prompts/interpret.md").read()
    sha = hashlib.sha256(prompt.encode()).hexdigest()[:12]
    method = f"{MODEL}@{sha}"

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        queue = conn.execute(
            "select id, claim, embedding from interpret_queue order by id limit %s",
            (max_claims,),
        ).fetchall()
        print(f"{len(queue)} claims queued for interpretation")

        linked = 0
        for claim_id, claim_text, embedding in queue:
            # time-directional: only judge against strictly older claims
            neighbors = conn.execute(
                """
                select id, claim from claims
                where id < %s and embedding is not null
                order by embedding <=> %s
                limit %s
                """,
                (claim_id, embedding, NEIGHBORS),
            ).fetchall()
            if neighbors:
                lines = [f"NEW claim: {claim_text}", "", "Candidates:"]
                lines += [f"[{nid}] {ntext}" for nid, ntext in neighbors]
                try:
                    out = call_groq(os.environ["GROQ_API_KEY"], prompt, "\n".join(lines))
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code == 429:
                        print("rate limited by Groq; stopping — next run resumes")
                        break
                    raise
                valid_ids = {nid for nid, _ in neighbors}
                for r in out.get("results", []):
                    cid, rel = r.get("candidate_id"), r.get("relation")
                    if cid in valid_ids and rel in ("supports", "refines", "contradicts", "duplicates"):
                        conn.execute(
                            """
                            insert into claim_links (from_claim, to_claim, relation, confidence, method)
                            values (%s, %s, %s, %s, %s)
                            on conflict do nothing
                            """,
                            (claim_id, cid, rel, r.get("confidence"), method),
                        )
                        linked += 1
                time.sleep(3)
            conn.execute("update claims set interpreted_at = now() where id = %s", (claim_id,))
            conn.commit()

        print(f"interpreted {len(queue)} claims, wrote {linked} edges")
        return linked


@app.local_entrypoint()
def main(max_claims: int = MAX_CLAIMS_PER_RUN):
    print(f"edges written: {interpret.remote(max_claims)}")
