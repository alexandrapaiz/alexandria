# The curriculum — what this architecture teaches

alexandria is two things at once: a pipeline that stays current on AI research,
and a systems-architecture course taught by building. This doc names the
disciplines being learned and points at the exact place in this repo where each
lesson is instantiated. If [decisions.md](decisions.md) records *what* was
decided, this records *what the decisions teach*.

The two core disciplines are **harness engineering** and **loop engineering**.
They are the two halves of agentic system design: the harness is everything
*around* a model call that makes a stochastic component behave like a reliable
one; the loops are the *shapes of repetition* the system runs in, and where
human judgment gates them.

## Harness engineering

A model call is a stochastic function. Harness engineering is the deterministic
scaffolding around it — input discipline, output discipline, failure discipline,
and coordination — so the system as a whole is dependable even though its core
component is not. It is distinct from *context engineering* (what goes into the
context window, covered below): the harness is what surrounds the call.

Where it lives in this repo:

- **Output discipline — JSON mode + low temperature.** Every batch call
  (triage, distill, interpret) runs in JSON mode at temperature 0.1–0.2, and
  the schema is stated in the prompt. The model is never trusted to freestyle;
  the harness defines the contract and the DB schema enforces it
  (`triage_log.decision` has a CHECK constraint — a hallucinated category
  cannot even be written). See `pipeline/triage.py`, `db/schema.sql`.

- **Failure discipline — retries that respect the provider.** Free tiers rate-
  limit constantly, so 429s are a normal operating condition, not an error.
  `extract_claims()` in `pipeline/distill.py` retries with backoff *honoring
  the Retry-After header*; when the daily budget is truly gone, workers stop
  gracefully instead of thrashing. Lesson: reliability under someone else's
  constraints is a design input, not an afterthought — it even became a model-
  selection axis (Gemini was disqualified on reliability, not quality).

- **Coordination — the blackboard (ADR-9).** Workers never message each other.
  Each reads its inbox as a SQL view (`triage_queue`, `distill_queue`,
  `interpret_queue`) defined by left-joins on what has *not yet* been done.
  This buys idempotency and free crash-resume: a worker killed mid-run picks up
  tomorrow exactly where it stopped, because state lives in the database, not
  in the process. The interpret worker did precisely this on day one when
  Groq's budget ran out mid-run.

- **Provenance — every judgment is auditable.** Each routing decision records
  its model, score, reasoning, and `prompt_sha`; each graph edge records
  `method = model@prompt_sha`. When a prompt changes, its outputs are
  distinguishable from the old prompt's outputs. The triage log is thereby also
  the future eval set and the future fine-tuning set.

- **Right-sizing and swappability.** Each task gets the cheapest model that
  passes its bar, behind an OpenAI-compatible interface. That seam has already
  paid twice (Llama retired from Groq's lineup; Gemini dropped) with zero
  pipeline changes — only a constant changed. See ADR-5 and the bake-off in
  [evals/](evals/).

- **Budget scheduling as harness.** Distill runs *before* triage on the daily
  clock because both spend the same Groq token budget and distill is the
  higher-value spend. Ordering jobs by value-per-token is harness engineering
  applied to the calendar.

## Loop engineering

Loop engineering is deciding what repeats, on what clock, with how much
autonomy, and where the human gate sits. alexandria runs four loops on three
timescales, and the placement of the single human gate is the central design
decision of the whole system (ADR-7).

- **The fast loop (daily) — a workflow, not an agent.** Ingest → distill →
  triage → interpret. Every step is hardwired: fixed retrieval, fixed prompts,
  fixed order. Per the Anthropic workflows-vs-agents canon, batch work with a
  known shape should not be given agency — agency is spent where the task shape
  is unknown. No human in this loop at all.

- **The knowledge loop (continuous) — append-only and time-directional.** New
  claims judge older ones (ADR-10): each claim is embedded, retrieves its
  nearest predecessors, and an LLM classifies the relation
  (supports/refines/contradicts/duplicates). Nothing is ever edited or deleted;
  deprecation is *derived* (a view over incoming `contradicts` edges ≥ 0.7).
  Lesson: in a system that learns over time, the arrow of time is a schema
  property — `where id < current` is the whole mechanism.

- **The human-gated loop (weekly, planned) — the brief and promotion.** The one
  place a person appears: an agentic pass (flexible retrieval via MCP) writes
  the brief; the human promotes claims to gold. Everything below this gate is
  autonomous; nothing above it is. "As out of the loop as possible" is achieved
  not by removing the human but by concentrating them at the single highest-
  leverage point.

- **The recursive loop (weekly, planned) — self-evolution as pull requests.**
  The meta-review reads the triage log, the human's verdicts, and the claim
  graph, and proposes diffs to the system's own prompts and sources. It may
  only *propose*; the human merge is the gate (ADR-7). Prompts are versioned
  files precisely so self-improvement is expressible as a git diff — the loop's
  output format was a schema decision.

- **The preference loop (episodic) — evals as RLHF's first stage.** Model
  selection ran as a blind pairwise preference test: two models, shuffled A/B,
  human grades without knowing which is which. That is literally the data-
  collection stage of RLHF, run at n=1 to pick a model instead of to train
  one; the graded set is archived as a golden set so future upgrades are
  measured, not vibed. See [evals/2026-09-07-distill-bakeoff.json](evals/2026-09-07-distill-bakeoff.json).

## Context engineering (the third discipline, in supporting role)

What goes *into* each call is engineered too, just more simply so far:

- **Priors travel with the data.** Source tiers (a/a-low/b/c/d in
  `sources.yaml`) reach the triage prompt as explicit priors, and the queue is
  ordered so high-tier work is judged first when budget is scarce.
- **Retrieve-then-reason.** Interpret never asks a model to "know" the corpus;
  pgvector kNN narrows 5 candidates, the model only classifies pairs put in
  front of it. Retrieval scopes the context; the model reasons inside it.
- **Rules before models.** The backfill rule (>60 days old → index, no LLM
  call) is context engineering by subtraction: the cheapest token is the one
  never spent.

## The meta-lesson

Every one of these was learned by hitting the real constraint — a retired
model, a rate-limit storm, a mid-run crash — not by reading about it. That is
the pedagogy of the project: the architecture is the textbook, the free-tier
constraints are the exercises, and the ADRs are the notes taken. The
institutional-grade column in [stack.md](stack.md) is the same curriculum at
the next difficulty level.
