"""Digest: assemble and publish the weekly three-section research digest.

This is a workflow, not an agent (ADR-6 logic): the digest's queries are known
in advance — new claims, accumulating supports-edges, citation movers, fresh
deprecations — so retrieval is hardwired SQL and the model only writes. Runs
Monday 15:00 UTC, after Sunday's slow loop has refreshed citation trajectories.

The digest lands in two places: the `digests` table (database of record) and
digests/<week>.md in the GitHub repo via the contents API (the published form).
The push needs the `github` Modal secret (GITHUB_TOKEN, a fine-grained PAT with
contents read/write on alexandrapaiz/alexandria); without the env var the run
still succeeds and only skips the push.

    modal run pipeline/digest.py         # one-off manual run
    modal deploy pipeline/digest.py      # install the weekly schedule
"""

import base64
import hashlib
import json
import time
from datetime import date, timedelta

import modal

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "openai/gpt-oss-120b"
REPO = "alexandrapaiz/alexandria"
WINDOW_DAYS = 7

image = (
    modal.Image.debian_slim()
    .pip_install("psycopg[binary]==3.2.4", "httpx==0.28.1")
    .add_local_file("prompts/digest.md", "/root/prompts/digest.md")
)

app = modal.App("alexandria-digest", image=image)


def gather(conn) -> dict:
    """Fixed queries; the model never chooses what to retrieve."""
    stats = conn.execute(
        """
        select
          (select count(*) from papers where fetched_at > now() - interval '7 days'),
          (select count(*) from claims where created_at > now() - interval '7 days'),
          (select count(*) from claim_links where created_at > now() - interval '7 days')
        """
    ).fetchone()

    new_claims = conn.execute(
        """
        select c.id, c.claim, c.topics, p.title, p.url, p.tier,
               t.decision, t.score,
               coalesce(array_agg(l.relation || ' -> claim ' || l.to_claim)
                        filter (where l.from_claim is not null), '{}')
        from claims c
        join papers p on p.id = c.paper_id
        left join triage_log t on t.paper_id = c.paper_id
        left join claim_links l on l.from_claim = c.id
        where c.created_at > now() - interval '7 days'
        group by c.id, c.claim, c.topics, p.title, p.url, p.tier, t.decision, t.score
        order by case t.decision when 'deep_read' then 0 else 1 end,
                 t.score desc nulls last
        limit 60
        """
    ).fetchall()

    supported = conn.execute(
        """
        select c.id, c.claim, p.title, p.url, count(*) as supports
        from claims c
        join papers p on p.id = c.paper_id
        join claim_links l on l.to_claim = c.id and l.relation = 'supports'
        group by c.id, c.claim, p.title, p.url
        having count(*) >= 2
        order by count(*) desc
        limit 12
        """
    ).fetchall()

    movers = conn.execute(
        """
        with checks as (
            select paper_id, citations, checked_at,
                   row_number() over (partition by paper_id order by checked_at desc) as rn
            from citation_log
        )
        select p.title, p.url, prev.citations, latest.citations
        from checks latest
        join checks prev on prev.paper_id = latest.paper_id and prev.rn = 2
        join papers p on p.id = latest.paper_id
        where latest.rn = 1 and latest.citations > prev.citations
        order by latest.citations - prev.citations desc
        limit 12
        """
    ).fetchall()

    deprecated = conn.execute(
        """
        select old.claim, new.claim, l.confidence, p.title, p.url
        from claim_links l
        join claims old on old.id = l.to_claim
        join claims new on new.id = l.from_claim
        join papers p on p.id = old.paper_id
        where l.relation = 'contradicts'
          and coalesce(l.confidence, 0) >= 0.7
          and l.created_at > now() - interval '7 days'
        """
    ).fetchall()

    deep_reads = conn.execute(
        """
        select p.title, p.url, t.reasoning
        from triage_log t
        join papers p on p.id = t.paper_id
        where t.decision = 'deep_read'
          and t.created_at > now() - interval '7 days'
        limit 10
        """
    ).fetchall()

    return {
        "stats": {"papers_ingested": stats[0], "claims_distilled": stats[1], "edges_drawn": stats[2]},
        "new_claims": [
            {
                "claim_id": r[0], "claim": r[1][:400], "topics": r[2],
                "paper": r[3], "url": r[4], "tier": r[5],
                "triage": r[6], "score": r[7], "edges": r[8],
            }
            for r in new_claims
        ],
        "traction": {
            "supported_claims": [
                {"claim_id": r[0], "claim": r[1][:400], "paper": r[2], "url": r[3], "supports": r[4]}
                for r in supported
            ],
            "citation_movers": [
                {"paper": r[0], "url": r[1], "citations_before": r[2], "citations_now": r[3]}
                for r in movers
            ],
        },
        "deprecated": [
            {"old_claim": r[0][:400], "contradicted_by": r[1][:400], "confidence": r[2],
             "paper": r[3], "url": r[4]}
            for r in deprecated
        ],
        "deep_reads": [{"paper": r[0], "url": r[1], "why": r[2]} for r in deep_reads],
    }


def write_digest(payload: dict, prompt: str) -> str:
    import os

    import httpx

    for attempt in range(4):
        resp = httpx.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY'].strip()}"},
            json={
                "model": MODEL,
                "temperature": 0.3,
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": json.dumps(payload, default=str)},
                ],
            },
            timeout=300,
        )
        if resp.status_code == 429 and attempt < 3:
            wait = float(resp.headers.get("retry-after") or 30 * (attempt + 1))
            print(f"rate limited; backing off {wait:.0f}s")
            time.sleep(min(wait, 180))
            continue
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    raise RuntimeError("groq: exhausted retries")


def push_to_repo(week: str, body: str) -> str:
    import os

    import httpx

    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        return "no GITHUB_TOKEN; skipped repo push (digest is in the database)"
    path = f"digests/{week}.md"
    api = f"https://api.github.com/repos/{REPO}/contents/{path}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    existing = httpx.get(api, headers=headers, timeout=30)
    put = {
        "message": f"digest: {week}",
        "content": base64.b64encode(body.encode()).decode(),
    }
    if existing.status_code == 200:
        put["sha"] = existing.json()["sha"]
    resp = httpx.put(api, headers=headers, json=put, timeout=30)
    resp.raise_for_status()
    return f"pushed {path}"


@app.function(
    schedule=modal.Cron("0 15 * * 1"),  # Monday 15:00 UTC, after the daily crons
    secrets=[modal.Secret.from_name("neon"), modal.Secret.from_name("groq"),
             modal.Secret.from_name("github")],
    timeout=1800,
)
def digest() -> str:
    import os

    import psycopg

    # label with the ISO week that just ended (yesterday = Sunday)
    y = date.today() - timedelta(days=1)
    week = f"{y.isocalendar().year}-W{y.isocalendar().week:02d}"
    prompt = open("/root/prompts/digest.md").read()
    sha = hashlib.sha256(prompt.encode()).hexdigest()[:12]

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        payload = gather(conn)
        payload["week"] = week
        print(f"{week}: {payload['stats']} | new_claims={len(payload['new_claims'])} "
              f"deprecated={len(payload['deprecated'])}")
        body = write_digest(payload, prompt)
        conn.execute(
            """
            insert into digests (week, body, model, prompt_sha) values (%s, %s, %s, %s)
            on conflict (week) do update
                set body = excluded.body, model = excluded.model,
                    prompt_sha = excluded.prompt_sha, created_at = now()
            """,
            (week, body, MODEL, sha),
        )
        conn.commit()
    print(push_to_repo(week, body))
    return body


@app.local_entrypoint()
def main():
    body = digest.remote()
    print("\n" + body)
