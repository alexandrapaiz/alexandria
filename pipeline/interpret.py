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
#   system  prompts/interpret.md                     ~883 tokens
#   user    one claim plus five neighbors            ~160 tokens
#   output  up to five relations with confidences    ~150 tokens
#   per claim  1,050 * 0.95/1e6 + 150 * 4.00/1e6  =  $0.0016
#
# $0.30 is therefore about 185 claims, which is more than a one-hour slot can
# reach at 3 requests a minute, so the clock is what actually binds and the cap
# is the guard behind it. The 487-claim backlog clears in about three runs and
# costs about $0.79 in total. See docs/finance/opex.md.
CAP_USD = 0.30

# Enough claims that the clock and the cap stop the run rather than this number.
# At 3 RPM a call every 20 seconds plus latency is about 35 seconds, so 90 is
# roughly 52 minutes inside a 60-minute timeout. Claims with no neighbors cost
# no call at all and go much faster, which is why this is above what the pacing
# alone would allow.
MAX_CLAIMS_PER_RUN = 90

image = (
    modal.Image.debian_slim()
    .pip_install("psycopg[binary]==3.2.4", "httpx==0.28.1")
    .add_local_file("prompts/interpret.md", "/root/prompts/interpret.md")
    .add_local_file("pipeline/budget.py", "/root/budget.py")
    .add_local_file("pipeline/llm.py", "/root/llm.py")
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


def drain_forecast(remaining: int, per_run: int) -> str:
    """How many runs are left at this rate. Progress is a remainder, not a total."""
    if per_run <= 0:
        return f"{remaining} claims still queued and this run interpreted none"
    runs = -(-remaining // per_run)
    return (f"{remaining} claims still queued; at {per_run} a run that is "
            f"{runs} more run{'s' if runs != 1 else ''}")


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

    client = llm()
    prompt, sha = load_prompt()
    cap = client.Cap(cap_usd, label="interpret")

    available, notes = client.usable_models(MODELS, os.environ)
    for note in notes:
        print(f"availability: {note}")

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        depth = conn.execute("select count(*) from interpret_queue").fetchone()[0]
        # Oldest first. `order by id` on a bigserial is oldest first, and the
        # owner asked for it by name: an old claim's neighbors are already in the
        # graph, so it is the claim whose edges connect the most.
        queue = conn.execute(
            "select id, claim, embedding from interpret_queue order by id limit %s",
            (max_claims,),
        ).fetchall()
        pause = client.pace(MODEL)
        print(f"{depth} claims queued, {len(queue)} taken this run, oldest first")
        print(f"pacing: {pause:.0f}s between calls ({MODEL} is "
              f"{client.budget().MODELS[MODEL]['rpm']} requests a minute), "
              f"cap ${cap_usd:.2f}")

        linked = 0
        seen = 0
        no_neighbors = 0
        stopped = "queue exhausted"
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
                for cid, rel, confidence in edges_from(
                        out, {nid for nid, _ in neighbors}):
                    conn.execute(
                        """
                        insert into claim_links (from_claim, to_claim, relation, confidence, method)
                        values (%s, %s, %s, %s, %s)
                        on conflict do nothing
                        """,
                        (claim_id, cid, rel, confidence, method),
                    )
                    linked += 1
                time.sleep(pause)
            else:
                no_neighbors += 1
            # The marker is written whether or not the claim had neighbors: a
            # claim with none is interpreted, it simply has no edges, and
            # leaving it unmarked is how a queue stops draining.
            conn.execute("update claims set interpreted_at = now() where id = %s", (claim_id,))
            conn.commit()
            seen += 1

        print(f"interpreted {seen} claims, wrote {linked} edges "
              f"({no_neighbors} had no older neighbor and cost no call), "
              f"stopped on: {stopped}")
        print(cap.line())
        print(drain_forecast(max(depth - seen, 0), seen))
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
    est = guard.cost_usd(1_050, 150, usable[0])
    print(f"cost at list price: ${est:.5f} a claim, about "
          f"{int(CAP_USD / est)} claims inside the ${CAP_USD:.2f} cap")
    return f"preflight ok: {usable[0]} would judge the shortlist"


@app.function(
    # No Neon. A rehearsal must not be able to write an edge, and a missing
    # credential is a stronger promise than a missing function call.
    secrets=[modal.Secret.from_name("moonshot"), modal.Secret.from_name("groq")],
    timeout=900,
)
def rehearse() -> str:
    """Gate 3: one real call, on the real prompt, writing nothing.

        modal run pipeline/interpret.py::rehearse

    The real prompt, provider, key, reservation and timeout. The claim and its
    five candidates are a fixed sample carried in this file, chosen so that the
    right answer is knowable: candidate 101 is the same finding (duplicates or
    supports), 102 narrows it (refines), 103 reports the opposite
    (contradicts), and 104 and 105 are unrelated and should draw nothing. A
    model that labels all five, or none, fails the gate.
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
    if model != MODELS[0]:
        raise client.NoModelAnswered(
            f"the rehearsal was answered by {model}, not by {MODELS[0]}, which "
            "is what the deploy installs. A receipt from a fallback is not a "
            "receipt.")
    return (f"rehearsal ok: {model} drew {len(edges)} of "
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
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        depth, oldest = conn.execute(
            "select count(*), min(created_at) from interpret_queue"
        ).fetchone()
        unembedded = conn.execute(
            "select count(*) from claims where interpreted_at is null "
            "and embedding is null"
        ).fetchone()[0]

    per_claim = guard.cost_usd(1_050, 150, MODELS[0])
    per_run = min(int(CAP_USD / per_claim), MAX_CLAIMS_PER_RUN)
    runs = -(-depth // per_run) if per_run else 0
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
