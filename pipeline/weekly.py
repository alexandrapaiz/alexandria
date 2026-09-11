"""Weekly loop: refresh citation trajectories, then write and publish the digest.

One scheduled function doing two jobs, in order:

1. **Slow loop** — batch-check citation counts on aged papers via Semantic
   Scholar's free API into the append-only citation_log. Trajectory (count now
   vs. last check) is the "gaining traction" evidence: the claim graph shows
   what our corpus thinks, citations show what the field thinks.
2. **Digest** — fixed SQL gathers five evidence streams (new claims, claims
   with 2+ supports edges, citation movers, fresh deprecations, deep-read
   flags); gpt-oss-120b writes the three-section digest; it lands in the
   `digests` table (database of record) and digests/<week>.md in the repo.

They share one function deliberately: Modal's free plan caps scheduled
functions at 5, and the citations exist for the digest — running them in the
same Monday process makes the trajectories maximally fresh and costs no slot.
The digest is a workflow, not an agent (ADR-6): every query is known in
advance, so the model only writes.

Needs secrets: `neon`, `groq`, `github` (GITHUB_TOKEN, fine-grained PAT with
contents read/write on the repo; if absent the run succeeds and skips the push).

    modal run pipeline/weekly.py         # one-off manual run (citations + digest)
    modal deploy pipeline/weekly.py      # install the Monday schedule
"""

import base64
import hashlib
import json
import re
import time
from datetime import date, timedelta

import modal

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "openai/gpt-oss-120b"
REPO = "alexandrapaiz/alexandria"

S2_BATCH_URL = "https://api.semanticscholar.org/graph/v1/paper/batch"
S2_BATCH_SIZE = 100       # ids per API call (S2 allows up to 500; be gentle)
MAX_PAPERS_PER_RUN = 400
MIN_AGE_DAYS = 7          # first check is the baseline; the second makes a trajectory
RECHECK_DAYS = 6          # at most one check per paper per weekly cycle

image = (
    modal.Image.debian_slim()
    .pip_install("psycopg[binary]==3.2.4", "httpx==0.28.1")
    .add_local_file("prompts/digest.md", "/root/prompts/digest.md")
)

app = modal.App("alexandria-weekly", image=image)


# ---------------- slow loop: citations ----------------

def s2_id(paper_id: str) -> str | None:
    """papers.id 'arxiv:2409.01234v2' -> Semantic Scholar id 'ARXIV:2409.01234'."""
    if not paper_id.startswith("arxiv:"):
        return None  # blog posts aren't in the citation graph
    raw = re.sub(r"v\d+$", "", paper_id.removeprefix("arxiv:"))
    return f"ARXIV:{raw}"


def check_citations(conn, max_papers: int = MAX_PAPERS_PER_RUN) -> int:
    import httpx

    rows = conn.execute(
        """
        select p.id
        from papers p
        join triage_log t on t.paper_id = p.id
            and t.decision in ('index', 'distill', 'deep_read')
        left join lateral (
            select max(checked_at) as last_check
            from citation_log where paper_id = p.id
        ) c on true
        where p.id like 'arxiv:%%'
          and p.published_at <= current_date - %s
          and (c.last_check is null or c.last_check < now() - make_interval(days => %s))
        order by c.last_check asc nulls first
        limit %s
        """,
        (MIN_AGE_DAYS, RECHECK_DAYS, max_papers),
    ).fetchall()
    ids = [r[0] for r in rows]
    print(f"{len(ids)} papers due for a citation check")

    written = 0
    for i in range(0, len(ids), S2_BATCH_SIZE):
        chunk = ids[i : i + S2_BATCH_SIZE]
        resp = httpx.post(
            S2_BATCH_URL,
            params={"fields": "citationCount"},
            json={"ids": [s2_id(pid) for pid in chunk]},
            timeout=60,
        )
        if resp.status_code == 429:
            print("rate limited by Semantic Scholar; continuing with what we have")
            break
        resp.raise_for_status()
        # response aligns positionally with the request; unknown papers are null
        for pid, result in zip(chunk, resp.json()):
            if result is None or result.get("citationCount") is None:
                continue
            conn.execute(
                "insert into citation_log (paper_id, citations) values (%s, %s)",
                (pid, result["citationCount"]),
            )
            written += 1
        conn.commit()
        time.sleep(2)
    print(f"citation checks written: {written}")
    return written


# ---------------- digest ----------------

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
                        filter (where l.from_claim is not null), '{}'),
               c.evidence, c.procedure
        from claims c
        join papers p on p.id = c.paper_id
        left join triage_log t on t.paper_id = c.paper_id
        left join claim_links l on l.from_claim = c.id
        where c.created_at > now() - interval '7 days'
        group by c.id, c.claim, c.topics, p.title, p.url, p.tier, t.decision, t.score,
                 c.evidence, c.procedure
        order by case t.decision when 'deep_read' then 0 else 1 end,
                 t.score desc nulls last
        limit 22
        """
    ).fetchall()

    superseded = conn.execute(
        """
        select old.claim, new.claim, l.confidence,
               po.title, po.url, pn.title, pn.url
        from claim_links l
        join claims old on old.id = l.to_claim
        join claims new on new.id = l.from_claim
        join papers po on po.id = old.paper_id
        join papers pn on pn.id = new.paper_id
        where l.relation = 'refines'
          and coalesce(l.confidence, 0) >= 0.75
          and l.created_at > now() - interval '7 days'
          and old.paper_id != new.paper_id  -- a paper refining itself is not a supersession
        order by l.confidence desc
        limit 10
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
                "claim_id": r[0], "claim": r[1][:280], "topics": r[2],
                "paper": r[3], "url": r[4], "tier": r[5],
                "triage": r[6], "score": r[7], "edges": r[8],
                "evidence": (r[9] or "")[:350] or None,
                "procedure": (r[10] or "")[:600] or None,
            }
            for r in new_claims
        ],
        "superseded": [
            {"old_claim": r[0][:280], "new_claim": r[1][:280], "confidence": r[2],
             "old_paper": r[3], "old_url": r[4], "new_paper": r[5], "new_url": r[6]}
            for r in superseded
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
        "deep_reads": [{"paper": r[0], "url": r[1], "why": (r[2] or "")[:200]} for r in deep_reads],
    }


# Groq's free tier caps request size (413 above it); trim the least-critical
# evidence (the tail of new_claims, already sorted best-first) until we fit
MAX_PAYLOAD_CHARS = 22000


def shrink(payload: dict) -> str:
    body = json.dumps(payload, separators=(",", ":"), default=str)
    while len(body) > MAX_PAYLOAD_CHARS and payload["new_claims"]:
        payload["new_claims"].pop()
        body = json.dumps(payload, separators=(",", ":"), default=str)
    return body


def write_digest(payload: dict, prompt: str) -> str:
    import os

    import httpx

    user = shrink(payload)
    print(f"payload: {len(user)} chars, {len(payload['new_claims'])} new claims kept")
    for attempt in range(4):
        resp = httpx.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY'].strip()}"},
            json={
                "model": MODEL,
                "temperature": 0.3,
                "max_completion_tokens": 6000,  # depth sections got truncated at the default cap
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user},
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
def weekly() -> str:
    import os

    import psycopg

    # label with the ISO week that just ended (yesterday = Sunday)
    y = date.today() - timedelta(days=1)
    week = f"{y.isocalendar().year}-W{y.isocalendar().week:02d}"
    prompt = open("/root/prompts/digest.md").read()
    sha = hashlib.sha256(prompt.encode()).hexdigest()[:12]

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        try:
            check_citations(conn)
        except Exception as exc:
            print(f"citation check failed ({exc}); digest proceeds without fresh citations")
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
    try:
        print(push_to_repo(week, body))
    except Exception as exc:
        # the digests table is the record of record; a push failure (bad token,
        # GitHub outage) must never fail the run
        print(f"repo push failed ({exc}); digest is safe in the database")
    return body


@app.local_entrypoint()
def main():
    body = weekly.remote()
    print("\n" + body)
