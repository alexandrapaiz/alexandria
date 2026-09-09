"""Slow loop: track citation counts on aged papers via Semantic Scholar.

The fast loop judges papers the day they appear; this loop watches how the
community judges them afterward. Citation trajectory (count now vs. the last
check, in citation_log) is the evidence behind the digest's "gaining traction"
section — the claim graph shows what *our* corpus thinks, citations show what
*the field* thinks.

Runs weekly on Sunday, the day before the Monday digest, so the digest always
reads fresh trajectories. Semantic Scholar's batch endpoint is free and needs
no key; we stay far under its shared rate limits (a few batched calls weekly).

    modal run pipeline/slowloop.py       # one-off manual run
    modal deploy pipeline/slowloop.py    # install the weekly schedule
"""

import re
import time

import modal

S2_BATCH_URL = "https://api.semanticscholar.org/graph/v1/paper/batch"
BATCH_SIZE = 100          # ids per API call (S2 allows up to 500; be gentle)
MAX_PAPERS_PER_RUN = 400
MIN_AGE_DAYS = 7          # first check is the baseline; the second check makes a
                          # trajectory, so start early — citations at age 7d are
                          # usually ~0, which is exactly the right baseline
RECHECK_DAYS = 6          # at most one check per paper per weekly cycle

image = modal.Image.debian_slim().pip_install("psycopg[binary]==3.2.4", "httpx==0.28.1")

app = modal.App("alexandria-slowloop", image=image)


def s2_id(paper_id: str) -> str | None:
    """papers.id 'arxiv:2409.01234v2' -> Semantic Scholar id 'ARXIV:2409.01234'."""
    if not paper_id.startswith("arxiv:"):
        return None  # blog posts aren't in the citation graph
    raw = re.sub(r"v\d+$", "", paper_id.removeprefix("arxiv:"))
    return f"ARXIV:{raw}"


@app.function(
    schedule=modal.Cron("0 15 * * 0"),  # Sunday 15:00 UTC, before Monday's digest
    secrets=[modal.Secret.from_name("neon")],
    timeout=1800,
)
def check_citations(max_papers: int = MAX_PAPERS_PER_RUN) -> int:
    import os

    import httpx
    import psycopg

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        # aged, non-discarded arXiv papers, least-recently-checked first
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
        for i in range(0, len(ids), BATCH_SIZE):
            chunk = ids[i : i + BATCH_SIZE]
            s2_ids = [s2_id(pid) for pid in chunk]
            resp = httpx.post(
                S2_BATCH_URL,
                params={"fields": "citationCount"},
                json={"ids": s2_ids},
                timeout=60,
            )
            if resp.status_code == 429:
                print("rate limited by Semantic Scholar; stopping — next run resumes")
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
            print(f"  batch {i // BATCH_SIZE + 1}: logged {written} so far")
            time.sleep(2)
        return written


@app.local_entrypoint()
def main(max_papers: int = MAX_PAPERS_PER_RUN):
    print(f"citation checks written: {check_citations.remote(max_papers)}")
