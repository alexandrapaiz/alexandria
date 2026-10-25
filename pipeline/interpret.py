"""Interpret: relate new claims to existing ones, building the claim graph.

Runs daily on Modal after distill. Requires the `neon`, `moonshot` and `groq`
secrets. No-ops harmlessly while the interpret_queue is empty (blackboard
coordination).

    python3 pipeline/budget.py                      # gate 1: does it fit
    modal run pipeline/interpret.py::preflight      # gate 2: does the model exist
    modal run pipeline/interpret.py::rehearse       # gate 3: one real call, no write
    modal deploy pipeline/interpret.py              # then, and only then, deploy

    modal run pipeline/interpret.py                 # manual run
    modal run pipeline/interpret.py::drain          # plan the drain, spend nothing

Design (ADR-10): append-only and time-directional. A new claim judges its older
neighbors; edges are never edited. Candidates come from pgvector kNN (retrieve
cheap), the relation label from a model (reason on the shortlist).

## Why this file changed on 2026-09-26

The owner's count, from Neon: 746 claims, 487 of them waiting in
interpret_queue, and this job drawing 11 to 14 edges a day. A claim graph that
adds a dozen edges a day is not a graph, and the number was never a property of
the work. It was Groq's free tier: one claim per call, 8,000 tokens a minute,
and a 429 for the rest of the day.

So interpret now writes on Moonshot's Kimi, the funded account ADR-32 bought
for the press, with Groq's free tier kept behind it. Oldest first, because the
owner asked for oldest first and because the oldest claims are the ones whose
neighbors are already in the graph, so they are the edges that connect the most.

## Why this file changed on 2026-10-05: it carries the maintenance step

Modal's free tier caps scheduled functions at five and ADR-12 recorded all five
as taken. `pipeline/skill_revision.py` declared a sixth at 16:00 UTC, so the
daily skill maintenance loop ADR-37 specifies did not have a schedule it could
keep. The owner's directive of 2026-10-05 folds its daily check in here instead,
which is what this job's `maintenance_step` is.

Two things about how, because both are deliberate.

It **spawns** rather than calls. `.remote()` would add that job's fifteen
minutes to this job's wall clock, and this job's window is 14:00-15:00 with
distill waiting at 15:00, so a slow maintenance pass would have pushed interpret
into distill's slot and Moonshot's organization concurrency is 1. A spawn runs
in its own container on its own timeout, and the maintenance job calls no model
at all, so it contends with nothing in KIMI_WINDOWS.

It spawns **first**, before any claim is judged. A step at the end never runs on
the day this job spends its full hour or stops at its cap, and the whole point
of folding it in here is that it runs every day.
"""

import hashlib
import pathlib
import time

import modal

# Kimi first, Groq's free tier behind it. See the same list and the same
# argument in pipeline/triage.py; pipeline/budget.py reads both out of the files
# rather than keeping a copy.
MODELS = [
    "kimi-k2.6",
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b",
]
MODEL = MODELS[0]

NEIGHBORS = 5
RELATIONS = ("supports", "refines", "contradicts", "duplicates")

# One claim against five candidates returns at most five short objects. 600 is
# roughly four times what a full answer needs, which leaves room for a model
# that pads its JSON without leaving room for one that writes an essay.
MAX_COMPLETION_TOKENS = 600

# What one run may spend, in USD, measured from the provider's usage block and
# never estimated. The arithmetic, from real token counts at kimi-k2.6's list
# price ($0.95 per million in, $4.00 per million out):
#
#   system  prompts/interpret.md                      880 tokens
#   user    one claim plus five neighbors             ~390 tokens worst case
#   output  up to five relations with confidences     ~150 tokens measured
#
# Expected cost of a call: 1,270 * 0.95/1e6 + 150 * 4.00/1e6 = $0.0018. The
# ceiling `python3 pipeline/budget.py` prints, which charges the whole 600-token
# reservation whether the model uses it or not, is $0.00364.
#
# The cap is set against the ceiling, so $0.30 buys 82 claims in the worst case
# and about 165 in practice. At 3 requests a minute the clock is what binds
# first either way, and the cap is the guard behind it. The 487-claim backlog
# clears in 3 to 6 runs and costs $0.88 to $1.77 in total. See
# docs/finance/opex.md.
CAP_USD = 0.30

# Enough claims that the clock and the cap stop the run rather than this number.
# At 3 RPM a call every 20 seconds plus latency is about 35 seconds, so 90 is
# roughly 52 minutes inside a 60-minute timeout. Claims with no neighbors cost
# no call at all and go much faster, which is why this is above what the pacing
# alone would allow.
MAX_CLAIMS_PER_RUN = 90

# And the ceiling for the day the primary is absent, which the number above
# cannot be. Every fallback model here is free, so CAP_USD buys infinite calls
# and the claim count is the only bound left; on Groq's free tier the binding
# resource is not calls or money but the 200,000 tokens a day it allows per
# model, shared with triage at 12:00 UTC and distill at 15:00. This job's
# calls are the smallest in the pipeline at a measured 1,000 tokens, so its
# share is generous in calls: 56 of them, where 90 would be 90,000 tokens and
# half of what is left after triage.
#
# 56,000 is the equal share of the allowance after the 15% margin, derived in
# `budget.fallback_share` from the provider's published `tpd` and held against
# this constant by `budget.check_fallback_shares()`.
FALLBACK_TOKENS_PER_RUN = 56_000

image = (
    modal.Image.debian_slim()
    .pip_install("psycopg[binary]==3.2.4", "httpx==0.28.1")
    .add_local_file("prompts/interpret.md", "/root/prompts/interpret.md")
    .add_local_file("pipeline/budget.py", "/root/budget.py")
    .add_local_file("pipeline/llm.py", "/root/llm.py")
    # The drift guard travels with the job, so the job can say what it is
    # actually running. db/schema.sql deploy_runtime carries the argument.
    .add_local_file("pipeline/runtime_sha.py", "/root/runtime_sha.py")
)

app = modal.App("alexandria-interpret", image=image)


def llm():
    """pipeline/llm.py, wherever this is running from. See triage.py's copy."""
    import sys

    here = str(pathlib.Path(__file__).resolve().parent)
    for path in ("/root", here):
        if path not in sys.path:
            sys.path.insert(0, path)
    import llm as module

    return module


def runtime_guard():
    """pipeline/runtime_sha.py, wherever this is running from.

    Same shape as the accessor above, and for the same reason: `/root` inside
    the image, this directory in a checkout.
    """
    import sys

    here = str(pathlib.Path(__file__).resolve().parent)
    for path in ("/root", here):
        if path not in sys.path:
            sys.path.insert(0, path)
    import runtime_sha as module

    return module


def load_prompt() -> tuple[str, str]:
    text = open("/root/prompts/interpret.md").read()
    return text, hashlib.sha256(text.encode()).hexdigest()[:12]


def render_candidates(claim_text: str, neighbors: list[tuple]) -> str:
    """The user message for one claim. Pulled out so `rehearse` sends the real one."""
    lines = [f"NEW claim: {claim_text}", "", "Candidates:"]
    lines += [f"[{nid}] {ntext}" for nid, ntext in neighbors]
    return "\n".join(lines)


def edges_from(out: dict, valid_ids: set) -> list[tuple]:
    """(candidate_id, relation, confidence) for every answer worth writing.

    A relation the schema does not allow, or an id that was not on the
    shortlist, is dropped here rather than at the insert, so the count the run
    prints is the count of edges it actually wrote.
    """
    kept = []
    for r in out.get("results", []):
        if not isinstance(r, dict):
            continue
        cid, rel = r.get("candidate_id"), r.get("relation")
        if cid in valid_ids and rel in RELATIONS:
            kept.append((cid, rel, r.get("confidence")))
    return kept


#: The trigger slice 5 asked for and did not build. A claim is due for a second
#: opinion when the current prompt has never read it, which is a question about
#: `claim_judgments` and not about `claim_links`: a pass that found no relation
#: wrote no edge, and the absence of an edge cannot tell "October read this and
#: found nothing" from "October never read it". db/schema.sql says why that
#: distinction is worth a table.
#:
#: `interpreted_at is not null` is what keeps this disjoint from
#: `interpret_queue`. A claim nobody has ever judged is a first opinion, it is
#: already the fresh queue's job, and a claim must not be able to arrive twice
#: in one run.
#: The order is the second half of the trigger and it was `c.id`, which is
#: arbitrary. It stopped being free on 2026-10-25: `interpret_pending` read 0,
#: so the leftovers are the whole run and the sweep spends the cap rather than
#: returning nothing. What the sweep buys is not uniform, so the cheap fix is
#: to buy the valuable half first.
#:
#: A claim carrying a pass under a known older sha is the slow loop's own case:
#: two prompts read it, and the second verdict is a changed mind or a
#: confirmation, which is the measurement ADR-10 wanted. A claim whose only
#: pass is `unknown` is the backfill's bookkeeping, recovered from a corpus
#: that predates `claim_judgments`, and re-reading it mostly buys a row. Both
#: are due and both terminate; only the order between them is a choice, and
#: a sweep that is cut short by the cap should be cut short at the cheap end.
REJUDGE_QUEUE_SQL = """
    select c.id, c.claim, c.embedding
      from claims c
      left join lateral (
            select max(j.created_at) filter (where j.prompt_sha <> 'unknown')
                       as known_at,
                   max(j.created_at) as any_at
              from claim_judgments j
             where j.claim_id = c.id
           ) p on true
     where c.interpreted_at is not null
       and c.embedding is not null
       and not exists (select 1 from claim_judgments k
                        where k.claim_id = c.id and k.prompt_sha = %s)
     order by (p.known_at is null), coalesce(p.known_at, p.any_at), c.id
     limit %s
"""


def rejudge_budget(fresh_taken: int, max_claims: int) -> int:
    """How many re-judgments this run may take: the leftovers, and only those.

    A first opinion is worth more than a second one. An unjudged claim has no
    edges at all, so judging it can only add to the graph, where re-judging a
    claim that already has edges usually confirms them. So the fresh queue is
    served first and re-judgment takes what is left, which is the right order
    whatever the depths are.

    **What this rule does not do is make the loop free, and the sentence that
    used to stand here said it did.** It read "the fresh queue is 2,000-odd
    deep today, so this returns 0 and the slow loop stays latent". That was
    true of the reading it was written from and false the next morning:
    `/api/delivery` reported `interpret_pending: 0` on 2026-10-25, because the
    backlog moved one stage upstream rather than drained. `distill_pending` was
    3,680 and no claim had been written since 2026-10-22, so there was nothing
    fresh to judge and the leftovers were the entire run. A safety claim keyed
    to a queue depth expires the moment the queue moves, which is why this
    paragraph names the instrument instead of a number.

    The bound that does hold is the one that was always here. The run's ceiling
    is `max_claims` and `CAP_USD`, and re-judgment is inside both rather than
    beside them, so no run can cost more than it could before the loop existed.
    The sweep also terminates: every pass writes a row, including the passes
    that find nothing, and a claim with a row at this sha is never selected
    again. What it is not is $0 a day while it runs, and `drain` is where that
    bill is read before it is spent rather than after.
    """
    return max(max_claims - fresh_taken, 0)


def drain_forecast(remaining: int, per_run: int) -> str:
    """How many runs are left at this rate. Progress is a remainder, not a total."""
    if per_run <= 0:
        return f"{remaining} claims still queued and this run interpreted none"
    runs = -(-remaining // per_run)
    return (f"{remaining} claims still queued; at {per_run} a run that is "
            f"{runs} more run{'s' if runs != 1 else ''}")


#: The maintenance job this run starts: (app name, function name). Named as
#: strings rather than imported, because importing skill_revision.py here would
#: pull its image, its secrets and its own `app` into this module and give
#: Modal two apps in one file.
MAINTENANCE = ("alexandria-skill-revision", "skill_revision")


def maintenance_step() -> str:
    """Start the daily skill maintenance pass. Never raises, and never blocks.

    ADR-37 specifies a daily maintenance pass and
    `pipeline/skill_revision.py` is it: register anything that merged
    unregistered, compute the four revision triggers, append what the library
    needs read to the reading queue, and dispatch the skill seat once if it
    found anything. Modal's free tier allows five scheduled functions and
    ADR-12 recorded all five as taken, so that job's own `modal.Cron` was a
    sixth that the plan does not run. Folding the trigger in here is the
    owner's directive of 2026-10-05, and it is one spawn.

    ## This function swallows every exception on purpose

    It is the first thing the scheduled run does, so anything it let escape
    would cost the day's claim graph to protect the day's skill maintenance,
    and that is the wrong trade in both directions. The maintenance pass is
    idempotent and tomorrow's run does the same work, while an interpret run
    that does not happen is a day of edges nobody draws.

    Observability does not depend on this returning an error either, which is
    the thing that makes swallowing safe here rather than lazy. The spawned
    function mails the owner from inside its own container when it fails
    (`notify_owner`, in skill_revision.skill_revision), and this process has no
    mail secret and could not do better. What this catches is the narrower
    case: the app is not deployed, or the function was renamed, so nothing ran
    and nothing could mail. That case prints a line that names itself and goes
    into the string this job returns, where the run report reads it.
    """
    import modal as modal_sdk

    app_name, function_name = MAINTENANCE
    try:
        handle = modal_sdk.Function.from_name(app_name, function_name)
        call = handle.spawn()
        return (f"maintenance: spawned {app_name}::{function_name} "
                f"(call {getattr(call, 'object_id', '?')}); it runs in its own "
                "container, calls no model, and mails the owner itself if it "
                "fails. This is the sixth schedule, folded in per the owner's "
                "directive of 2026-10-05.")
    except Exception as exc:                        # noqa: BLE001 - never fatal
        return (f"maintenance: COULD NOT START {app_name}::{function_name}: "
                f"{type(exc).__name__}: {exc}. Nothing ran, and because nothing "
                "ran, nothing mailed. ADR-37's daily pass did not happen today: "
                f"check `modal app list` for {app_name} and redeploy it with "
                "`modal deploy pipeline/skill_revision.py`. The claim graph "
                "below is unaffected.")


@app.function(
    # 14:00 UTC, unchanged, and now load-bearing. Moonshot's organization
    # concurrency is 1, so this slot has to miss triage's window
    # (12:00-13:00) and the press's band (09:00-11:00, which includes the
    # chair's manual rehearsal). pipeline/llm.py KIMI_WINDOWS is the table that
    # says so, and budget.py fails CI if two windows overlap.
    #
    # Runtime change under docs/agents/runtime-changes.md: this job's provider
    # moved. Its three gates are in this module's docstring.
    schedule=modal.Cron("0 14 * * *"),
    secrets=[modal.Secret.from_name("neon"),
             modal.Secret.from_name("moonshot"), modal.Secret.from_name("groq")],
    timeout=3600,
)
def interpret(max_claims: int = MAX_CLAIMS_PER_RUN, cap_usd: float = CAP_USD):
    import os

    import psycopg

    # The folded-in sixth schedule. First, and it cannot raise: see this
    # module's docstring and maintenance_step's.
    maintenance = maintenance_step()
    print(maintenance)

    client = llm()
    prompt, sha = load_prompt()
    cap = client.Cap(cap_usd, label="interpret")

    available, notes = client.usable_models(MODELS, os.environ)
    for note in notes:
        print(f"availability: {note}")

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        # Guardrail, sprint 2026-09-28 item 2: say what this container is
        # actually running before anything else happens. It cannot raise and
        # cannot abort this transaction; pipeline/runtime_sha.py says how.
        print(runtime_guard().record_runtime(conn, "interpret", __file__)[1])
        depth = conn.execute("select count(*) from interpret_queue").fetchone()[0]
        # Oldest first. `order by id` on a bigserial is oldest first, and the
        # owner asked for it by name: an old claim's neighbors are already in the
        # graph, so it is the claim whose edges connect the most.
        queue = conn.execute(
            "select id, claim, embedding from interpret_queue order by id limit %s",
            (max_claims,),
        ).fetchall()
        print(f"{depth} claims queued, {len(queue)} taken this run, oldest first")
        # The slow loop, on the leftovers. Oldest first here too, and for the
        # same reason: an old claim has the most neighbors to have changed its
        # mind about.
        rejudge_depth = conn.execute(
            "select count(*) from claims c where c.interpreted_at is not null "
            "and c.embedding is not null and not exists "
            "(select 1 from claim_judgments j where j.claim_id = c.id "
            "and j.prompt_sha = %s)",
            (sha,),
        ).fetchone()[0]
        room = rejudge_budget(len(queue), max_claims)
        rejudged = conn.execute(REJUDGE_QUEUE_SQL, (sha, room)).fetchall() if room else []
        print(f"prompt {sha}: {rejudge_depth} judged claims it has never read, "
              f"{len(rejudged)} taken on this run's {room} leftover slots")
        # Fresh first in the list, because the walk below stops on a cap or a
        # 429 and whatever it did not reach is what gets dropped. It is also
        # what lets the count be split after the fact: the walk is in order, so
        # anything past the first `fresh_taken` entries is a re-judgment.
        fresh_taken = len(queue)
        queue = queue + rejudged
        # The rule, not a number: the pause is chosen after each call from the
        # model that answered it and the tokens it drew. See llm.pace.
        print("pacing: chosen per call from the answering model's published "
              "limits, whichever binds, "
              + ", ".join(f"{m} {limits['rpm']} RPM / {limits['tpm']:,} TPM"
                          for m, limits in ((m, client.budget().MODELS[m])
                                            for m in MODELS
                                            if m in client.budget().MODELS))
              + f"; cap ${cap_usd:.2f}")

        linked = 0
        seen = 0
        no_neighbors = 0
        stopped = "queue exhausted"
        # Tokens drawn on a model that is not the primary's, and only those:
        # the ceiling below is a share of the free tier's day, so a call
        # Moonshot answered does not spend it.
        fallback_drawn = 0
        for claim_id, claim_text, embedding in queue:
            # Before the call, so the run stops at its share rather than one
            # call past it. Leaving this day's remainder to distill is the
            # whole point: this job holds 14:00 UTC and distill holds 15:00.
            if fallback_drawn >= FALLBACK_TOKENS_PER_RUN:
                stopped = f"the {FALLBACK_TOKENS_PER_RUN:,}-token fallback share"
                print(f"stopping: {fallback_drawn:,} tokens drawn off the "
                      "primary's provider, which is this job's share of the "
                      "free tier's day. The next run resumes from the same "
                      "queue.")
                break
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
                try:
                    out, model = client.ask_json(
                        MODELS, prompt, render_candidates(claim_text, neighbors),
                        os.environ, cap, max_completion=MAX_COMPLETION_TOKENS,
                        temperature=0.1, available=available)
                except client.CapReached as exc:
                    print(exc)
                    stopped = "spend cap"
                    break
                except (client.RateLimited, client.NoModelAnswered) as exc:
                    print(f"no model could judge claim {claim_id} ({exc}); "
                          "stopping — next run resumes from the same queue")
                    stopped = "rate limited"
                    break
                method = f"{model}@{sha}"
                kept = edges_from(out, {nid for nid, _ in neighbors})
                for cid, rel, confidence in kept:
                    conn.execute(
                        """
                        insert into claim_links (from_claim, to_claim, relation, confidence, method)
                        values (%s, %s, %s, %s, %s)
                        on conflict do nothing
                        """,
                        (claim_id, cid, rel, confidence, method),
                    )
                    linked += 1
                # Paced by the model that ANSWERED and the size of the
                # call it just took, not by the head of the list: the
                # fallback's minute is 8,000 tokens where Moonshot's is
                # 500,000, so a pause chosen before the walk ran is a
                # 429 this caller caused. llm.pace says why.
                if client.on_fallback(model):
                    fallback_drawn += cap.last_tokens
                time.sleep(client.pace(model, cap.last_tokens))
                wrote, answered = len(kept), method
            else:
                no_neighbors += 1
                wrote, answered = 0, None
            # The pass itself, including the empty ones, and this is the row
            # that makes the loop terminate. Without it a claim the current
            # prompt read and found nothing in looks identical to one the
            # current prompt has never seen, so it would come back on every
            # run and pay for a model call every time.
            conn.execute(
                """
                insert into claim_judgments (claim_id, prompt_sha, method, edges)
                values (%s, %s, %s, %s)
                on conflict (claim_id, prompt_sha) do nothing
                """,
                (claim_id, sha, answered, wrote),
            )
            # The marker is written whether or not the claim had neighbors: a
            # claim with none is interpreted, it simply has no edges, and
            # leaving it unmarked is how a queue stops draining.
            #
            # `is null` is the slow loop's half. This timestamp says when a
            # claim was first judged, `claim_judgments` carries every pass
            # since, and a re-judgment that moved the marker would date
            # September's claim to today and put it back in the seven-day
            # sections of the issue as new.
            conn.execute("update claims set interpreted_at = now() "
                         "where id = %s and interpreted_at is null", (claim_id,))
            conn.commit()
            seen += 1

        # Split, because the two halves answer different questions and one
        # number for both would answer neither. `seen` counts the claims this
        # run judged; the drain is about the queue, and a re-judgment takes
        # nothing out of it.
        fresh_seen = min(seen, fresh_taken)
        print(f"interpreted {seen} claims, wrote {linked} edges "
              f"({no_neighbors} had no older neighbor and cost no call), "
              f"of which {fresh_seen} were first opinions and "
              f"{seen - fresh_seen} were second ones, "
              f"stopped on: {stopped}")
        print(cap.line())
        # Fresh only. Counting a re-judgment as drain progress would forecast a
        # queue emptying at a rate nothing is emptying it at, and the forecast
        # is the number the owner reads to decide whether the corpus is moving.
        print(drain_forecast(max(depth - fresh_seen, 0), fresh_seen))
        return linked


@app.function(
    secrets=[modal.Secret.from_name("moonshot"), modal.Secret.from_name("groq")],
    timeout=300,
)
def preflight() -> str:
    """Gate 2: do the models exist? Raises, so a failure stops the `&&` chain."""
    import os

    client = llm()
    guard = client.budget()
    available, notes = client.usable_models(MODELS, os.environ)
    for note in notes:
        print(f"  {note}")
    for rank, model in enumerate(MODELS, start=1):
        for line in guard.model_problems(f"interpret fallback {rank}", model,
                                         available):
            print(f"  PROBLEM: {line}")
    usable = [m for m in MODELS if available is None or m in available]
    if not usable:
        raise client.NoModelAnswered(
            "preflight: no model in interpret's list is listed by its provider "
            "for these keys, so no edge can be drawn. Fix "
            "pipeline/interpret.py MODELS and pipeline/budget.py MODELS together.")
    print("cost at list price: "
          + client.calls_within(CAP_USD, 1_050, 150, usable[0]))
    if usable[0] != MODELS[0]:
        print(f"  NOTE: {MODELS[0]} is not usable here, so the run would fall "
              f"back to {usable[0]} and the graph grows at the free tier's pace "
              "again until the head of the list comes back.")
    return f"preflight ok: {usable[0]} would judge the shortlist"


@app.function(
    # No Neon. A rehearsal must not be able to write an edge, and a missing
    # credential is a stronger promise than a missing function call.
    secrets=[modal.Secret.from_name("moonshot"), modal.Secret.from_name("groq")],
    timeout=900,
)
def rehearse(allow_fallback: bool = False) -> str:
    """Gate 3: one real call, on the real prompt, writing nothing.

        modal run pipeline/interpret.py::rehearse
        modal run pipeline/interpret.py::rehearse --allow-fallback

    The real prompt, provider, key, reservation and timeout. The claim and its
    five candidates are a fixed sample carried in this file, chosen so that the
    right answer is knowable: candidate 101 is the same finding (duplicates or
    supports), 102 narrows it (refines), 103 reports the opposite
    (contradicts), and 104 and 105 are unrelated and should draw nothing. A
    model that labels all five, or none, fails the gate.

    `--allow-fallback` is the hatch for the day the head of the list is itself
    what is broken and the change in the image is the degraded path the outage
    needs. `llm.head_receipt` holds the argument and the morning that proved
    it. It forgives the head and nothing else: an edge set that labels
    everything or nothing still raises, because that is a fault in the answer
    rather than in which account gave it.
    """
    import os

    client = llm()
    prompt, sha = load_prompt()
    cap = client.Cap(CAP_USD, label="interpret rehearsal")
    available, notes = client.usable_models(MODELS, os.environ)
    for note in notes:
        print(f"  {note}")

    valid_ids = {nid for nid, _ in REHEARSAL_NEIGHBORS}
    user = render_candidates(REHEARSAL_CLAIM, REHEARSAL_NEIGHBORS)
    started = time.monotonic()
    out, model = client.ask_json(MODELS, prompt, user, os.environ, cap,
                                max_completion=MAX_COMPLETION_TOKENS,
                                temperature=0.1, available=available)
    elapsed = time.monotonic() - started
    edges = edges_from(out, valid_ids)

    print("interpret rehearsal:")
    print(f"  model: {model}   prompt_sha: {sha}   "
          f"reservation: {MAX_COMPLETION_TOKENS}   elapsed: {elapsed:.1f}s")
    print(f"  {len(REHEARSAL_NEIGHBORS)} candidates in, "
          f"{len(out.get('results') or [])} results back, "
          f"{len(edges)} would become edges")
    for cid, rel, confidence in edges:
        print(f"    claim {cid}: {rel} (confidence {confidence})")
    print(f"  {cap.line()}")
    print("  wrote nothing: this container has no database credential")

    if not edges:
        raise client.NoModelAnswered(
            "the rehearsal drew no edge from a shortlist built to contain three "
            "of them. A model that relates nothing would leave the graph flat "
            "while marking every claim interpreted, which is the failure that "
            "hides best. Nothing was deployed.")
    if len(edges) == len(REHEARSAL_NEIGHBORS):
        raise client.NoModelAnswered(
            f"the rehearsal related the new claim to all {len(edges)} "
            "candidates, two of which are unrelated by construction. A model "
            "that labels everything makes the graph noise. Nothing was deployed.")
    forgiven = client.head_receipt(
        model, MODELS, allow_fallback,
        gate="pipeline/interpret.py::rehearse")
    if forgiven:
        print(forgiven)
    on = "on the degraded path" if forgiven else "ok"
    return (f"rehearsal {on}: {model} drew {len(edges)} of "
            f"{len(REHEARSAL_NEIGHBORS)} candidates at prompt {sha} in "
            f"{elapsed:.1f}s for ${cap.spent:.5f}, wrote nothing")


@app.function(
    secrets=[modal.Secret.from_name("neon")],
    timeout=300,
)
def drain() -> str:
    """What the drain looks like from here, spending nothing. The dry run.

    No model secret in this container, so it cannot call anything by mistake.
    """
    import os

    import psycopg

    client = llm()
    guard = client.budget()
    _, sha = load_prompt()
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        depth, oldest = conn.execute(
            "select count(*), min(created_at) from interpret_queue"
        ).fetchone()
        unembedded = conn.execute(
            "select count(*) from claims where interpreted_at is null "
            "and embedding is null"
        ).fetchone()[0]
        rejudge_depth, rejudge_known = conn.execute(
            "select count(*), count(*) filter (where exists "
            "(select 1 from claim_judgments k where k.claim_id = c.id "
            "and k.prompt_sha <> 'unknown')) "
            "from claims c where c.interpreted_at is not null "
            "and c.embedding is not null and not exists "
            "(select 1 from claim_judgments j where j.claim_id = c.id "
            "and j.prompt_sha = %s)",
            (sha,),
        ).fetchone()
        reflects = conn.execute(
            "select prompt_sha, count(*) from latest_judgment "
            "group by 1 order by 2 desc limit 3"
        ).fetchall()

    per_claim = guard.cost_usd(1_050, 150, MODELS[0])
    per_run = min(int(CAP_USD / per_claim), MAX_CLAIMS_PER_RUN)
    runs = -(-depth // per_run) if per_run else 0
    rejudge_runs = -(-rejudge_depth // per_run) if per_run else 0
    lines = [
        f"interpret queue: {depth} claims, oldest {oldest}",
        f"{unembedded} more claims are uninterpreted but unembedded, so they "
        "are not in the queue at all until distill's embedding sweep reaches "
        "them (that sweep is unconditional, so they will arrive)",
        f"per claim: ${per_claim:.5f} at list price",
        f"per run: {per_run} claims inside the ${CAP_USD:.2f} cap "
        f"(MAX_CLAIMS_PER_RUN is {MAX_CLAIMS_PER_RUN})",
        f"the backlog clears in {runs} daily runs for about "
        f"${depth * per_claim:.2f} in total",
        f"re-judgment: prompt {sha} has never read {rejudge_depth} of the "
        "judged claims, and it takes the slots the fresh queue leaves, which "
        f"is {rejudge_budget(min(depth, per_run), per_run)} at this depth",
        f"that sweep is {rejudge_runs} daily runs for about "
        f"${rejudge_depth * per_claim:.2f}, and it is $0 only while the fresh "
        "queue is deep enough to crowd it out, which on 2026-10-25 it was not",
        f"of those, {rejudge_known} carry a pass under a known older prompt "
        "and are read first, because a second verdict there is a changed mind "
        f"or a confirmation; the other {rejudge_depth - rejudge_known} are the "
        "backfill's unknown rows and buy mostly a row",
        "the graph currently reflects: "
        + (", ".join(f"{n} claims under {psha}" for psha, n in reflects)
           or "nothing, no claim has been judged yet"),
    ]
    print("\n".join(lines))
    return lines[-1]


# The rehearsal's fixed shortlist. Ids are small on purpose: they are never
# written anywhere, and a reader who sees 101 in a log knows immediately that it
# is not a real claim id.
REHEARSAL_CLAIM = (
    "Explicit scratchpad eviction keeps tool-call accuracy within 4 percent of "
    "baseline past 200K tokens of agent context, where recursive summarization "
    "loses 31 percent."
)
REHEARSAL_NEIGHBORS = [
    (101, "Evicting scratchpad entries explicitly holds tool-call accuracy to "
          "within a few points of baseline in long agent loops, while "
          "recursive summarization degrades it sharply."),
    (102, "Recursive summarization of agent context degrades tool-call "
          "accuracy as the conversation grows."),
    (103, "Recursive summarization preserves tool-call accuracy at long "
          "context lengths and is the recommended compaction strategy."),
    (104, "A cache-oblivious FFT decomposition gives a 1.8x speedup on ARM64 "
          "for radio interferometry correlators."),
    (105, "Instruction tuning on 1,000 curated examples matches the "
          "performance of tuning on 50,000 noisy ones."),
]


@app.local_entrypoint()
def main(max_claims: int = MAX_CLAIMS_PER_RUN):
    print(f"edges written: {interpret.remote(max_claims)}")
