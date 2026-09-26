"""Triage: route untriaged papers with a real model, logging every decision.

Runs daily on Modal after distill. Requires the `neon`, `moonshot` and `groq`
secrets.

    python3 pipeline/budget.py                     # gate 1: does it fit
    modal run pipeline/triage.py::preflight        # gate 2: does the model exist
    modal run pipeline/triage.py::rehearse         # gate 3: one real call, no write
    modal deploy pipeline/triage.py                # then, and only then, deploy

    modal run pipeline/triage.py                   # test run, 2 batches
    modal run pipeline/triage.py --max-calls 40    # bigger manual run
    modal run pipeline/triage.py::drain            # plan the drain, spend nothing

## Why this file changed on 2026-09-26

The owner's count, from Neon: 8,956 papers ingested and 4,973 of them never
triaged. That is not a backlog, it is a pipeline that stopped reading. The
cause was Groq's free tier, where 8,000 tokens a minute means a run makes two
calls and takes a 429 for the rest of the day, and the resume query then makes
that look like patience rather than failure.

So triage now writes on Moonshot's Kimi, the funded account ADR-32 bought for
the press, with Groq's free tier kept behind it as the fallback. The ceiling
that binds is no longer money or tokens. It is Moonshot's tier-0 3 requests a
minute, and the arithmetic is printed every run: one call every 20 seconds,
BATCH papers a call, inside a one-hour slot.

## Design notes

- Papers are triaged BATCH per call, which is now a latency decision rather
  than a budget one: at 3 RPM the cost of a run is its call count.
- Anything older than BACKFILL_DAYS is auto-indexed by rule, not judged by the
  model. Historical archives do not deserve model budget.
- Every run has a spend cap (`CAP_USD`), measured from the provider's own usage
  block and printed whether or not it is reached. A drain loop against a funded
  account without a cap is how a $3 backlog becomes a surprise.
- A 429 that survives backoff ends the run gracefully; tomorrow's run resumes
  where this one stopped (the left-join-on-triage_log query is the resume
  mechanism, and it needs no cursor).
- Tiers are drained by interleaved quota (TIER_WEIGHTS), never by sorting one
  tier ahead of another. A run that dies early must still have looked at more
  than one tier; see the comment on TIER_WEIGHTS for what that cost once.
- The 12:00 UTC slot is unchanged and it is load-bearing: Moonshot's
  organization concurrency is 1, and `pipeline/llm.py` KIMI_WINDOWS is the
  table that keeps this run from colliding with the press or with interpret.
"""

import hashlib
import pathlib
import time

import modal

# Kimi first, Groq's free tier behind it. The order is the whole point of the
# change: rank 1 is a funded account that can actually finish a run, and ranks 2
# to 4 are the free tier that could not, kept because one provider is one point
# of failure and incident 24 is what that costs. Every id here is verified by
# pipeline/budget.py, which reads this list out of this file rather than keeping
# a copy of it.
MODELS = [
    "kimi-k2.6",
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b",
]
MODEL = MODELS[0]           # the default; whichever model answered is logged

BATCH = 10
BACKFILL_DAYS = 60
DECISIONS = {"discard", "index", "distill", "deep_read"}

# Output reservation for one batch. Ten results of {i, decision, score,
# reasoning} measured at ~55 tokens each, doubled, so a verbose run is not
# truncated into invalid JSON.
MAX_COMPLETION_TOKENS = 1_200

# What one run may spend, in USD, measured from the provider's usage block and
# never estimated. The arithmetic, from real token counts at kimi-k2.6's list
# price ($0.95 per million in, $4.00 per million out):
#
#   system  prompts/triage.md + BATCH_INSTRUCTIONS   ~820 tokens
#   user    10 papers, title + abstract[:1500]     ~2,680 tokens
#   output  10 decisions with reasoning              ~700 tokens
#   per call  3,500 * 0.95/1e6 + 700 * 4.00/1e6  =  $0.0062
#   per paper                                     =  $0.00062
#
# $0.60 is therefore about 96 calls, or 960 papers, which is close to what the
# one-hour slot allows at 3 RPM anyway: the cap and the clock bind in the same
# place, which is how a cap should be set. The 4,973-paper backlog clears in
# about six runs and costs about $3.10 in total. See docs/finance/opex.md.
CAP_USD = 0.60

# Enough calls that the clock and the cap are what stop the run, not this
# number. At 3 RPM a call every 20 seconds plus its own latency is roughly 35
# seconds, so 90 calls is about 52 minutes inside a 60-minute timeout.
MAX_CALLS_PER_RUN = 90

# How each run's call budget is shared out, in batches per pass. This replaced a
# single ORDER BY that sorted tier 'a' fourth and left 'a-low' in the CASE's else
# branch, which starved the arXiv firehose for the whole life of the pipeline:
# 2,445 papers, zero triage rows, while every claim in the graph came from tier b.
#
# Quota alone would not have fixed it. A run that dies early reads only the tier
# it was sent first, so fairness has to live in the SEND ORDER and not just in
# the totals: plan_batches() hands out one batch per tier per pass, so the
# truncated run that actually happens is still a fair sample. That argument is
# weaker on Kimi than it was on Groq, because a Kimi run finishes, and it is
# kept because a cap, a timeout and a 429 all still truncate.
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
    # The provider table and the shared client travel with the job, so the
    # numbers CI checks are the numbers this run uses.
    .add_local_file("pipeline/budget.py", "/root/budget.py")
    .add_local_file("pipeline/llm.py", "/root/llm.py")
)

app = modal.App("alexandria-triage", image=image)

BATCH_INSTRUCTIONS = """
You will receive several papers, each numbered and carrying its source tier.
Apply the routing rules to each one independently. Respond with JSON only:
{"results": [{"i": <number>, "decision": "...", "score": 0.0, "reasoning": "..."}]}
Include every paper exactly once.
"""


def llm():
    """pipeline/llm.py, wherever this is running from.

    Modal drops it at /root/llm.py; a local import finds it beside this file.
    Same two-path trick weekly.py uses for the budget guard, for the same
    reason: the client the tests exercise is the client the run uses.
    """
    import sys

    here = str(pathlib.Path(__file__).resolve().parent)
    for path in ("/root", here):
        if path not in sys.path:
            sys.path.insert(0, path)
    import llm as module

    return module


def load_prompt() -> tuple[str, str]:
    text = open("/root/prompts/triage.md").read()
    return text, hashlib.sha256(text.encode()).hexdigest()[:12]


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


def render_batch(chunk: list[tuple]) -> str:
    """The user message for one batch. Pulled out so `rehearse` sends the real one."""
    lines = []
    for i, (_, title, abstract, tier) in enumerate(chunk):
        body = (abstract or "")[:1500] or "(no abstract; judge from title)"
        lines.append(f"[{i}] tier={tier}\ntitle: {title}\nabstract: {body}")
    return "\n\n".join(lines)


def queue_report(conn) -> tuple[int, dict[str, int]]:
    """Depth per tier, printed every run. Returns (total, per-tier).

    Starvation was invisible for the pipeline's whole life because nothing ever
    printed this; a research brief had to go and find it in the database by hand.
    Now it is also the progress line: a drain with no printed remainder is a
    drain nobody can tell is working.
    """
    depths: dict[str, int] = {}
    for tier, depth, oldest in conn.execute(
        """
        select tier, count(*), min(published_at)
        from triage_queue group by tier order by count(*) desc
        """
    ).fetchall():
        depths[tier or "unknown"] = depth
        print(f"  queue: tier {tier or 'unknown'}: {depth} waiting, oldest {oldest}")
    return sum(depths.values()), depths


def drain_forecast(remaining: int, per_run: int) -> str:
    """How many runs are left at this rate. The owner asked for progress, and
    progress is a remainder and a date, not a count of what one run did."""
    if per_run <= 0:
        return f"{remaining} papers still queued and this run judged none"
    runs = -(-remaining // per_run)
    return (f"{remaining} papers still queued; at {per_run} a run that is "
            f"{runs} more run{'s' if runs != 1 else ''}")


@app.function(
    # 12:00 UTC, unchanged, and now load-bearing rather than incidental.
    # Moonshot's organization concurrency is 1, so this slot has to miss the
    # press's band (09:00-11:00, which includes the chair's manual rehearsal)
    # and interpret's slot (14:00-15:00). The one-hour timeout is what makes
    # 12:00 a window rather than a moment, and pipeline/llm.py KIMI_WINDOWS is
    # the table that says so; budget.py fails CI if two windows overlap.
    #
    # Runtime change under docs/agents/runtime-changes.md: this job's provider
    # moved. Its three gates are in this module's docstring, and the deploy
    # does not happen until the rehearsal passes.
    schedule=modal.Cron("0 12 * * *"),
    secrets=[modal.Secret.from_name("neon"),
             # ADR-32's funded account, primary since 2026-09-26.
             modal.Secret.from_name("moonshot"), modal.Secret.from_name("groq")],
    timeout=3600,
)
def triage(max_calls: int = MAX_CALLS_PER_RUN, cap_usd: float = CAP_USD):
    import os

    import psycopg

    client = llm()
    prompt, sha = load_prompt()
    system = prompt + BATCH_INSTRUCTIONS
    cap = client.Cap(cap_usd, label="triage")

    available, notes = client.usable_models(MODELS, os.environ)
    for note in notes:
        print(f"availability: {note}")

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

        depth_before, _ = queue_report(conn)

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
        planned: dict[str, int] = {}
        for chunk in plan:
            planned[chunk[0][3]] = planned.get(chunk[0][3], 0) + len(chunk)
        pause = client.pace(MODEL)
        print(f"{sum(len(c) for c in plan)} papers planned across {len(plan)} calls: "
              + ", ".join(f"{t}={n}" for t, n in sorted(planned.items())))
        print(f"pacing: {pause:.0f}s between calls ({MODEL} is "
              f"{client.budget().MODELS[MODEL]['rpm']} requests a minute), "
              f"cap ${cap_usd:.2f}")

        judged = 0
        per_tier: dict[str, int] = {}
        stopped = "plan exhausted"
        for chunk in plan:
            try:
                out, model = client.ask_json(
                    MODELS, system, render_batch(chunk), os.environ, cap,
                    max_completion=MAX_COMPLETION_TOKENS, temperature=0.2,
                    available=available)
            except client.CapReached as exc:
                print(exc)
                stopped = "spend cap"
                break
            except (client.RateLimited, client.NoModelAnswered) as exc:
                print(f"no model could judge this batch ({exc}); stopping — "
                      "next run resumes from the same queue")
                stopped = "rate limited"
                break
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
                    (paper_id, r["decision"], r.get("score"), r.get("reasoning"), model, sha),
                )
                judged += 1
                per_tier[chunk[i][3]] = per_tier.get(chunk[i][3], 0) + 1
            conn.commit()
            time.sleep(pause)

        # The per-tier split is the evidence that the drain is fair. If a future run
        # prints one tier again, the inversion is back.
        split = ", ".join(f"{t}={n}" for t, n in sorted(per_tier.items())) or "none"
        print(f"triaged {judged} papers ({split}), stopped on: {stopped}")
        print(cap.line())
        print(drain_forecast(max(depth_before - judged, 0), judged))
        return judged


@app.function(
    secrets=[modal.Secret.from_name("moonshot"), modal.Secret.from_name("groq")],
    timeout=300,
)
def preflight() -> str:
    """Gate 2: do the models exist? Run before every deploy.

    `modal deploy` runs no entrypoint, so without this nothing asks the provider
    between one day's cron and the next. It needs the real key, which only
    exists inside Modal, which is why it is a deployed function and not a local
    script. It raises, so a failure stops the chair's `&&` chain.
    """
    import os

    client = llm()
    guard = client.budget()
    available, notes = client.usable_models(MODELS, os.environ)
    for note in notes:
        print(f"  {note}")
    problems = [p for rank, model in enumerate(MODELS, start=1)
                for p in guard.model_problems(f"triage fallback {rank}", model,
                                              available)]
    for line in problems:
        print(f"  PROBLEM: {line}")
    usable = [m for m in MODELS if available is None or m in available]
    if not usable:
        raise client.NoModelAnswered(
            "preflight: no model in triage's list is listed by its provider "
            "for these keys, so triage cannot judge a single paper. Fix "
            "pipeline/triage.py MODELS and pipeline/budget.py MODELS together.")
    est = guard.cost_usd(3_500, 700, usable[0])
    print(f"cost at list price: ${est:.5f} a call, ${est / BATCH:.6f} a paper, "
          f"about {int(CAP_USD / est)} calls inside the ${CAP_USD:.2f} cap")
    return f"preflight ok: {usable[0]} would judge the batch"


@app.function(
    # Neon is deliberately absent. A rehearsal must not be able to write a
    # triage decision, and the strongest form of that promise is a missing
    # credential rather than a missing function call.
    secrets=[modal.Secret.from_name("moonshot"), modal.Secret.from_name("groq")],
    timeout=900,
)
def rehearse() -> str:
    """Gate 3: one real call, on the real prompt, writing nothing.

        modal run pipeline/triage.py::rehearse

    The first two gates ask questions about the request. This one exercises the
    provider, and every one of the four failures of
    INC-2026-09-24-press-provider-migration was on this question. The prompt,
    the provider, the key, the reservation and the timeout are all the real
    ones. What is fake is the batch, which is a fixed sample carried in this
    file, and what is absent is the database.

    It raises on any failure, so the chair's `&&` chain stops before the deploy,
    and it refuses to pass on a fallback: a receipt from a different model is
    not a receipt for the model about to be deployed.
    """
    import os

    client = llm()
    prompt, sha = load_prompt()
    cap = client.Cap(CAP_USD, label="triage rehearsal")
    available, notes = client.usable_models(MODELS, os.environ)
    for note in notes:
        print(f"  {note}")

    user = render_batch(REHEARSAL_BATCH)
    started = time.monotonic()
    out, model = client.ask_json(MODELS, prompt + BATCH_INSTRUCTIONS, user,
                                os.environ, cap,
                                max_completion=MAX_COMPLETION_TOKENS,
                                temperature=0.2, available=available)
    elapsed = time.monotonic() - started

    results = [r for r in out.get("results", []) if isinstance(r, dict)]
    good = [r for r in results if r.get("decision") in DECISIONS]
    print("triage rehearsal:")
    print(f"  model: {model}   prompt_sha: {sha}   "
          f"reservation: {MAX_COMPLETION_TOKENS}   elapsed: {elapsed:.1f}s")
    print(f"  {len(REHEARSAL_BATCH)} papers in, {len(results)} results back, "
          f"{len(good)} with a valid decision")
    for r in results:
        print(f"    [{r.get('i')}] {r.get('decision')} "
              f"score={r.get('score')} {str(r.get('reasoning'))[:90]}")
    print(f"  {cap.line()}")
    print("  wrote nothing: this container has no database credential")

    if len(good) != len(REHEARSAL_BATCH):
        raise client.NoModelAnswered(
            f"the rehearsal got {len(good)} valid decisions for "
            f"{len(REHEARSAL_BATCH)} papers. A model that answers for some of a "
            "batch will silently leave the rest untriaged forever, because the "
            "resume query cannot tell 'not yet judged' from 'judged and "
            "dropped'. Nothing was deployed.")
    if model != MODELS[0]:
        raise client.NoModelAnswered(
            f"the rehearsal was answered by {model}, not by {MODELS[0]}, which "
            "is what the deploy installs. A receipt from a fallback is not a "
            "receipt: fix the head of the list before deploying, because "
            "tomorrow's cron meets it first.")
    return (f"rehearsal ok: {model} judged {len(good)} papers at prompt {sha} "
            f"in {elapsed:.1f}s for ${cap.spent:.5f}, wrote nothing")


@app.function(
    secrets=[modal.Secret.from_name("neon")],
    timeout=300,
)
def drain() -> str:
    """What the drain looks like from here, spending nothing. The dry run.

        modal run pipeline/triage.py::drain

    No model secret in this container, so it cannot call anything even by
    mistake. It answers the only question the owner asked that a plan can
    answer: how deep is the queue, how many runs at this cap, how much money.
    """
    import os

    import psycopg

    client = llm()
    guard = client.budget()
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        depth, per_tier = queue_report(conn)

    per_call = guard.cost_usd(3_500, 700, MODELS[0])
    calls_per_run = min(int(CAP_USD / per_call), MAX_CALLS_PER_RUN)
    per_run = calls_per_run * BATCH
    runs = -(-depth // per_run) if per_run else 0
    lines = [
        f"triage queue: {depth} papers across {len(per_tier)} tiers",
        f"per call: ${per_call:.5f} at list price, {BATCH} papers",
        f"per run: {calls_per_run} calls inside the ${CAP_USD:.2f} cap "
        f"(MAX_CALLS_PER_RUN is {MAX_CALLS_PER_RUN}), so {per_run} papers",
        f"the backlog clears in {runs} daily runs for about "
        f"${depth * per_call / BATCH:.2f} in total",
    ]
    print("\n".join(lines))
    return lines[-1]


# A fixed sample for the rehearsal: one paper that should clearly be read, one
# that should clearly be discarded, and one in between, so a model answering
# 'index' to everything fails the gate rather than passing it. Abstracts are
# written here rather than fetched, because a rehearsal must not depend on the
# database being in any particular state.
REHEARSAL_BATCH = [
    ("rehearsal:1",
     "Context Rot: Compaction Strategies for Million-Token Agent Loops",
     "We study how agent performance degrades as conversation context grows "
     "past 200K tokens, and compare four compaction strategies across 1,400 "
     "task episodes. Recursive summarization loses 31% of tool-call accuracy; "
     "a scratchpad with explicit eviction loses 4%. We give the eviction policy "
     "and the prompt that implements it.",
     "a"),
    ("rehearsal:2",
     "A Fast Fourier Transform Variant for Radio Astronomy Interferometry",
     "We present a cache-oblivious FFT decomposition tuned for the correlator "
     "stage of radio interferometry pipelines, achieving a 1.8x speedup on "
     "ARM64 against FFTW for the array geometries used at MeerKAT.",
     "a-low"),
    ("rehearsal:3",
     "Announcing our new embeddings endpoint",
     "Today we are making our text embedding model available through the API. "
     "It supports 8,192-token inputs and costs less than our previous model. "
     "Read the docs to get started.",
     "d"),
]


@app.local_entrypoint()
def main(max_calls: int = 2):
    print(f"judged: {triage.remote(max_calls)}")
