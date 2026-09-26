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

    modal run pipeline/triage.py::retriage_plan    # the re-triage, dry. $0.
    modal run pipeline/triage.py::retriage         # then, and only then, judge

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

## Why this file changed again the same day

The owner's directive of 2026-09-25: research on reasoning models has to reach
the corpus. 209 papers in it have "reasoning" in the title, 147 were never
triaged, and of the 62 that were, 47 went to `index` against 14 to `distill`,
because the prompt rewarded a "construction technique" and a reasoning paper's
contribution is usually a training recipe. `prompts/triage.md` now carries the
research seat's rubric that says so in as many words.

Two things follow for this file, and neither is the prompt.

- **The priority is served inside the tier, never ahead of it.** Reasoning
  papers sort first within every tier and `plan_batches` is untouched, so the
  interleaved quota that fixed the firehose starvation still decides which tier
  is served next. A priority implemented as a global sort would have rebuilt
  that bug with a new favourite.
- **A revised rubric has to re-judge the papers it was written for.** `retriage`
  is that, and it appends rather than edits: a paper ends with two rows, and
  `latest_triage` is the newest one. The disagreement between two rubrics about
  one paper is the most valuable row in an eval set, and an UPDATE would delete
  it. ADR-2026-09-26b has the alternatives.

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

# Reasoning-model research is a standing priority of this pipeline (the owner's
# order of 2026-09-23, and her directive of 2026-09-25 that put it at the front
# of this queue). prompts/triage.md now carries the rubric that says how to judge
# it; this list says which papers meet that rubric first.
#
# The count that produced it, from Neon: 209 papers with "reasoning" in the
# title, 147 of them never triaged at all. Matching is on the TITLE only, and
# that is a deliberate limit rather than an oversight. Half the corpus mentions
# reasoning somewhere in an abstract, so an abstract match would promote
# thousands of papers and a priority that covers everything is not a priority.
# The terms beyond "reasoning" are the named methods the rubric routes to
# `distill`, so a paper whose title says GRPO and never says reasoning is still
# reasoning work and still goes first.
PRIORITY_TERMS = (
    "reasoning",
    "chain-of-thought",
    "chain of thought",
    "rlvr",
    "grpo",
    "verifiable reward",
    "test-time compute",
    "test time compute",
    "inference-time compute",
    "process reward",
    "long cot",
)
# The same predicate twice, in the two languages that need it. Both derive from
# the tuple above, so they cannot drift: `%term%` for Postgres `ilike any`, and a
# substring test for the planner's own report and for the tests.
PRIORITY_PATTERNS = [f"%{term}%" for term in PRIORITY_TERMS]


def is_priority(title: str) -> bool:
    """Is this paper reasoning-model research by its title? Mirrors the SQL."""
    low = (title or "").lower()
    return any(term in low for term in PRIORITY_TERMS)

# Output reservation for one batch. Ten results of {i, decision, score,
# reasoning} measured at ~55 tokens each, doubled, so a verbose run is not
# truncated into invalid JSON.
MAX_COMPLETION_TOKENS = 1_200

# What one run may spend, in USD, measured from the provider's usage block and
# never estimated. The arithmetic, from real token counts at kimi-k2.6's list
# price ($0.95 per million in, $4.00 per million out):
#
#   system  prompts/triage.md + BATCH_INSTRUCTIONS      728 tokens
#   user    10 papers, title + abstract[:1500]        2,753 tokens
#   output  10 decisions with reasoning, measured      ~700 tokens
#
# Two numbers fall out and both matter. The EXPECTED cost of a call is
# 3,513 * 0.95/1e6 + 700 * 4.00/1e6 = $0.0062, or $0.00062 a paper. The CEILING,
# which `python3 pipeline/budget.py` prints because it charges the whole output
# reservation whether the model uses it or not, is $0.00814 a call.
#
# The cap has to be set against the ceiling, so $0.60 buys 73 calls in the worst
# case and about 96 in practice: 730 to 960 papers a run. That is close to what
# the one-hour slot allows at 3 requests a minute anyway, so the cap and the
# clock bind in roughly the same place, which is how a cap should be set. The
# 4,973-paper backlog clears in 6 or 7 runs and costs $3.10 to $4.05 in total.
# See docs/finance/opex.md.
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
    # The owner's number, printed every run so the drain on the priority is as
    # visible as the drain on the whole queue: 147 untriaged reasoning papers on
    # 2026-09-26. When this reaches zero the standing priority is satisfied and
    # the only reasoning papers left are the ones that arrived today.
    waiting = conn.execute(
        "select count(*) from triage_queue where title ilike any(%s)",
        (PRIORITY_PATTERNS,),
    ).fetchone()[0]
    print(f"  queue: {waiting} of those are reasoning-model research by title, "
          "and they are drained first inside every tier")
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
            insert into triage_log (paper_id, decision, reasoning, model, prompt_sha, method)
            select p.id, 'index', 'backfill: predates pipeline, auto-indexed by rule',
                   'rule:backfill', %s, 'rule:backfill@' || %s
            from papers p left join triage_log t on t.paper_id = p.id
            where t.id is null
              and (p.published_at is null or p.published_at < current_date - %s)
            """,
            (sha, sha, BACKFILL_DAYS),
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
                           partition by tier
                           order by case when title ilike any(%s) then 0 else 1 end,
                                    published_at desc nulls last
                       ) as rn
                from triage_queue
            ) ranked
            where rn <= %s
            """,
            (PRIORITY_PATTERNS, BATCH * max_calls),
        ).fetchall()

        plan = plan_batches(rows, max_calls)
        planned: dict[str, int] = {}
        for chunk in plan:
            planned[chunk[0][3]] = planned.get(chunk[0][3], 0) + len(chunk)
        # Reasoning papers sort first inside every tier, so tier fairness is
        # untouched and the queue is still drained by interleaved quota. This
        # line is how anybody can tell the priority is actually being served.
        priority_planned = sum(1 for chunk in plan for row in chunk
                               if is_priority(row[1]))
        print(f"reasoning-first: {priority_planned} of "
              f"{sum(len(c) for c in plan)} planned papers are "
              "reasoning-model research by title")
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
                    insert into triage_log
                        (paper_id, decision, score, reasoning, model, prompt_sha, method)
                    values (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (paper_id, r["decision"], r.get("score"), r.get("reasoning"),
                     model, sha, f"{model}@{sha}"),
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
    print(f"cost at list price: {client.calls_within(CAP_USD, 3_500, 700, usable[0])}"
          + (f", ${est / BATCH:.6f} a paper" if est else ""))
    if usable[0] != MODELS[0]:
        print(f"  NOTE: {MODELS[0]} is not usable here, so the run would fall "
              f"back to {usable[0]}. It can judge a batch, and it will stop on "
              "a 429 long before the cap. The corpus drains at the free tier's "
              "pace again until the head of the list comes back.")
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


# What one re-triage run may spend. 47 papers is 5 calls at BATCH=10, so the
# whole job is about $0.04 at the measured ceiling. The cap is set an order of
# magnitude above that rather than at it, because a re-triage set grows as the
# corpus grows, and a job that stops on its cap on the day the set doubles is a
# job that looks broken. It is still one fifteenth of the daily drain's cap.
RETRIAGE_CAP_USD = 0.10

# The SQL both re-triage functions select with, written once. A paper qualifies
# when its NEWEST decision is `index`, its title is reasoning-model research, and
# that decision was not already made under the prompt now on disk.
#
# The last clause is the whole idempotence story, and it is a guard rather than a
# cursor: a paper re-judged today is excluded tomorrow because its newest row
# carries today's sha, so a killed run is resumed by running it again and a
# finished run is a no-op. It also means the job re-runs itself automatically the
# next time the rubric changes, which is exactly what should happen.
RETRIAGE_CANDIDATES = """
    select p.id, p.title, p.abstract, p.tier, t.score, t.created_at
    from papers p
    join latest_triage t on t.paper_id = p.id
    where t.decision = 'index'
      and t.model != 'rule:backfill'
      and coalesce(t.prompt_sha, '') != %s
      and p.title ilike any(%s)
      and p.distilled_at is null
    order by t.created_at
    limit %s
"""


@app.function(
    secrets=[modal.Secret.from_name("neon")],
    timeout=300,
)
def retriage_plan(max_papers: int = 200) -> str:
    """The dry run for the re-triage. Reads, prints, spends nothing.

        modal run pipeline/triage.py::retriage_plan

    No provider secret in this container, so it cannot call a model even by
    mistake, and no write path, so it cannot record a decision. It answers the
    question the owner asked before any money is spent: which papers does the new
    rubric get a second look at, and what does that cost.
    """
    import os

    import psycopg

    client = llm()
    guard = client.budget()
    _, sha = load_prompt()
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        rows = conn.execute(RETRIAGE_CANDIDATES, (sha, PRIORITY_PATTERNS,
                                                  max_papers)).fetchall()
        already = conn.execute(
            "select count(*) from latest_triage t join papers p on p.id = t.paper_id "
            "where t.decision = 'index' and p.title ilike any(%s) "
            "and coalesce(t.prompt_sha, '') = %s",
            (PRIORITY_PATTERNS, sha),
        ).fetchone()[0]

    calls = -(-len(rows) // BATCH)
    cost = calls * guard.cost_usd(3_500, MAX_COMPLETION_TOKENS, MODELS[0])
    lines = [
        f"re-triage at prompt {sha}: {len(rows)} reasoning papers sit at 'index' "
        f"and have not been judged by this rubric",
        f"{already} have already been re-judged at this prompt and are skipped",
        f"{calls} calls of {BATCH}, about ${cost:.4f} at the measured ceiling, "
        f"cap ${RETRIAGE_CAP_USD:.2f}",
    ]
    for pid, title, _, tier, score, when in rows[:15]:
        lines.append(f"  {pid} tier={tier} score={score} indexed {when:%Y-%m-%d}: "
                     f"{title[:70]}")
    print("\n".join(lines))
    print("wrote nothing, called nothing")
    return lines[0]


@app.function(
    secrets=[modal.Secret.from_name("neon"),
             modal.Secret.from_name("moonshot"), modal.Secret.from_name("groq")],
    timeout=3600,
)
def retriage(max_papers: int = 200, cap_usd: float = RETRIAGE_CAP_USD) -> str:
    """Judge the reasoning papers at `index` again, under the new rubric.

        modal run pipeline/triage.py::retriage_plan     # first. Spends nothing.
        modal run pipeline/triage.py::retriage          # then, and only then

    The owner's directive of 2026-09-25: of 62 triaged reasoning papers, 47 went
    to `index` and 14 to `distill`, because the old prompt rewarded a
    "construction technique" and a reasoning paper's contribution is usually a
    training recipe. `prompts/triage.md` now says that in as many words. A rubric
    change that only applies to tomorrow's papers leaves the papers it was written
    for sitting exactly where the old rubric put them, so this is the half of the
    change that reaches the corpus.

    **It appends; it never edits.** A re-judged paper ends with two rows in
    `triage_log`, the September decision and this one, and `latest_triage` is what
    every consumer reads. That is not bookkeeping. The table is also the eval set
    for the recursive loop (db/schema.sql says so), and two rubrics disagreeing
    about one paper is the most valuable row in it. An UPDATE would delete the
    disagreement and keep only the answer.

    **A paper that stays at `index` is still written.** The new rubric agreeing
    with the old one is a result, and the row is also what stops this job from
    asking the same question forever.

    Run it inside triage's own 12:00-13:00 window or in the 13:00-14:00 margin
    that `pipeline/llm.py` KIMI_WINDOWS deliberately keeps empty. Moonshot's
    organization concurrency is 1, and a manual run is the one caller no cron
    table can schedule around.
    """
    import os

    import psycopg

    client = llm()
    prompt, sha = load_prompt()
    system = prompt + BATCH_INSTRUCTIONS
    cap = client.Cap(cap_usd, label="re-triage")
    available, notes = client.usable_models(MODELS, os.environ)
    for note in notes:
        print(f"availability: {note}")

    moved: dict[str, int] = {}
    judged = 0
    stopped = "plan exhausted"
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        rows = conn.execute(RETRIAGE_CANDIDATES,
                            (sha, PRIORITY_PATTERNS, max_papers)).fetchall()
        print(f"{len(rows)} reasoning papers at 'index' to re-judge at prompt {sha}")
        pause = client.pace(MODEL)
        for start in range(0, len(rows), BATCH):
            chunk = [(pid, title, abstract, tier)
                     for pid, title, abstract, tier, _, _ in rows[start:start + BATCH]]
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
                      "the next run picks up the same papers")
                stopped = "rate limited"
                break
            results = {r.get("i"): r for r in out.get("results", []) if isinstance(r, dict)}
            for i, (paper_id, _, _, _) in enumerate(chunk):
                r = results.get(i)
                if r is None or r.get("decision") not in DECISIONS:
                    print(f"  no valid decision for {paper_id}; leaving it at index")
                    continue
                decision = r["decision"]
                conn.execute(
                    """
                    insert into triage_log
                        (paper_id, decision, score, reasoning, model, prompt_sha, method)
                    values (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (paper_id, decision, r.get("score"),
                     f"re-triage under the reasoning rubric: {r.get('reasoning')}",
                     model, sha, f"{model}@{sha}"),
                )
                moved[f"index -> {decision}"] = moved.get(f"index -> {decision}", 0) + 1
                judged += 1
            conn.commit()
            time.sleep(pause)

        # The movement matrix is the evidence the rubric changed something. If
        # every paper stays at index, the prompt did not do what it says.
        split = ", ".join(f"{k}: {n}" for k, n in sorted(moved.items())) or "none"
        promoted = sum(n for k, n in moved.items()
                       if k.endswith("distill") or k.endswith("deep_read"))
        print(f"re-judged {judged} papers ({split}), stopped on: {stopped}")
        print(f"{promoted} of them now route to distill or deep_read, so they "
              "enter distill_queue on the next distill run")
        print(cap.line())
    return f"re-judged {judged} papers at prompt {sha}, {promoted} promoted"


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
