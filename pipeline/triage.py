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
- Tiers are drained by interleaved quota (TIER_WEIGHTS), never by sorting one tier
  ahead of another. A run that dies on a 429 after two calls must still have looked
  at more than one tier; see the comment on TIER_WEIGHTS for why.
"""

import hashlib
import json
import time

import modal

MODEL = "openai/gpt-oss-120b"  # largest open model on Groq's free tier as of 2026-09
BATCH = 10
BACKFILL_DAYS = 60
DECISIONS = {"discard", "index", "distill", "deep_read"}

# How each run's call budget is shared out, in batches per pass. This replaced a
# single ORDER BY that sorted tier 'a' fourth and left 'a-low' in the CASE's else
# branch, which starved the arXiv firehose for the whole life of the pipeline:
# 2,445 papers, zero triage rows, while every claim in the graph came from tier b.
#
# Quota alone would not have fixed it. The binding constraint is Groq's free tier,
# and a run typically dies on a 429 after a couple of calls, so whichever tier is
# sent first is the only tier that gets read. Fairness therefore has to live in the
# SEND ORDER, not just in the totals: plan_batches() hands out one batch per tier
# per pass, so the truncated run that actually happens is still a fair sample.
#
# Weights are intent, not arithmetic. Tier b is small and hand-curated and earns a
# full share on quality; tier a is the bulk of the corpus and earns one on volume;
# c and d are low-volume feeds that only need occasional service.
TIER_WEIGHTS = {
    "b": 3,      # human-curated paper picks; strongest prior, smallest volume
    "a": 3,      # the arXiv firehose; the corpus's bulk, and its blind spot
    "a-low": 2,  # noisy firehose categories, cs.CR among them
    "c": 1,      # frontier/open-lab owned channels
    "d": 1,      # practitioners, releases, ecosystem signal
}
# Any tier not named above still drains. Silently sorting an unrecognised tier last
# is precisely the bug this replaces, so the default is a real share, not zero.
DEFAULT_WEIGHT = 1

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


def plan_batches(rows: list[tuple], max_calls: int) -> list[list[tuple]]:
    """Interleave the queue into a send order that is fair under truncation.

    Rows arrive already sorted newest-first within each tier. Each pass hands one
    batch to every tier that still has papers and still has weight left; passes
    repeat until the budget is spent. When a tier runs dry its share spills to the
    others, so a quiet day for hf-daily donates its calls to the firehose instead
    of wasting them.
    """
    by_tier: dict[str, list[tuple]] = {}
    for row in rows:
        by_tier.setdefault(row[3], []).append(row)

    # Highest weight first, then alphabetical, so the order is deterministic and a
    # 429 after one call always lands on the same tier rather than a random one.
    order = [t for t in by_tier if TIER_WEIGHTS.get(t, DEFAULT_WEIGHT) > 0]
    order.sort(key=lambda t: (-TIER_WEIGHTS.get(t, DEFAULT_WEIGHT), t))
    cursor = {t: 0 for t in order}
    remaining = {t: TIER_WEIGHTS.get(t, DEFAULT_WEIGHT) for t in order}

    plan: list[list[tuple]] = []
    while len(plan) < max_calls:
        served = 0
        for tier in order:
            if len(plan) >= max_calls:
                break
            if remaining[tier] <= 0 or cursor[tier] >= len(by_tier[tier]):
                continue
            chunk = by_tier[tier][cursor[tier] : cursor[tier] + BATCH]
            cursor[tier] += len(chunk)
            remaining[tier] -= 1
            plan.append(chunk)
            served += 1
        if served == 0:
            # Every tier is out of weight or out of papers. Refill the weights and
            # go round again; this is the spill-over that keeps unused budget from
            # evaporating when one tier's queue is short.
            if all(cursor[t] >= len(by_tier[t]) for t in order):
                break
            remaining = {t: TIER_WEIGHTS.get(t, DEFAULT_WEIGHT) for t in order}
    return plan


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

        # Queue depth per tier, logged every run. Starvation was invisible for the
        # pipeline's whole life because nothing ever printed this; a research brief
        # had to go and find it in the database by hand.
        for tier, depth, oldest in conn.execute(
            """
            select tier, count(*), min(published_at)
            from triage_queue group by tier order by count(*) desc
            """
        ).fetchall():
            print(f"  queue: tier {tier or 'unknown'}: {depth} waiting, oldest {oldest}")

        # Take each tier's candidates separately so no tier can be crowded out of
        # the result set before the planner ever sees it.
        rows = conn.execute(
            """
            select id, title, abstract, tier from (
                select id, title, abstract, tier,
                       row_number() over (
                           partition by tier order by published_at desc nulls last
                       ) as rn
                from triage_queue
            ) ranked
            where rn <= %s
            """,
            (BATCH * max_calls,),
        ).fetchall()

        plan = plan_batches(rows, max_calls)
        planned = {}
        for chunk in plan:
            planned[chunk[0][3]] = planned.get(chunk[0][3], 0) + len(chunk)
        print(f"{sum(len(c) for c in plan)} papers planned across {len(plan)} calls: "
              + ", ".join(f"{t}={n}" for t, n in sorted(planned.items())))

        judged = 0
        per_tier: dict[str, int] = {}
        for chunk in plan:
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
                per_tier[chunk[i][3]] = per_tier.get(chunk[i][3], 0) + 1
            conn.commit()
            time.sleep(3)  # stay under 30 requests/minute

        # The per-tier split is the evidence that the drain is fair. If a future run
        # prints one tier again, the inversion is back.
        split = ", ".join(f"{t}={n}" for t, n in sorted(per_tier.items())) or "none"
        print(f"triaged {judged} papers with {MODEL} ({split})")
        return judged


@app.local_entrypoint()
def main(max_calls: int = 2):
    print(f"judged: {triage.remote(max_calls)}")
