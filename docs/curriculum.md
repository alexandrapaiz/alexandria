# The curriculum — the AI systems stack, learned by building

alexandria is two things at once: a pipeline that stays current on AI research,
and a course in **AI systems architecture**, taught bottom-up by building one
real system. This doc follows the original course outline — infrastructure →
models → data → orchestration → agents, plus the cross-cutting patterns (RAG,
MCP, skills, memory) and the engineering stack (context, harness, and loop
engineering) — and maps every layer to the exact place in this repo where it
was learned by hitting a real constraint. [decisions.md](decisions.md) records
*what* was decided; this records *what the decisions teach*.

## Layer 1 — Infrastructure

*The choice: on-premise vs. local (laptop) vs. cloud.*

alexandria chose cloud, and specifically **serverless** cloud: Modal functions
that scale to zero, Neon Postgres that scales to zero. The lesson is that for a
system that works minutes per day, per-second billing plus scale-to-zero makes
the marginal cost of infrastructure effectively nothing — the $0/month bill is
an architectural outcome, not a discount.

- **Containers (Docker).** Every Modal function runs in a container image
  (`debian_slim` + pinned pip installs, declared in code at the top of each
  `pipeline/*.py`). The container is the unit of reproducibility: the same
  image runs identically every day, and "works on my machine" cannot happen
  because there is no machine.
- **State vs. compute.** Compute is disposable (functions die after each run);
  state lives in exactly two durable places — the database and a Modal Volume
  (`hf-cache`) holding the embedding model's weights so they aren't
  re-downloaded daily. Deciding *what deserves to persist* is the
  infrastructure question.
- **Secrets.** Credentials live in Modal's secret store (`neon`, `groq`),
  injected as environment variables, never in the repo. The public repo +
  private secrets split is what makes "public code, sellable research"
  possible.

## Layer 2 — Models

*The choice: open vs. proprietary, and model size.*

- **Right-size the model to the task (ADR-5).** Triage, distill, and interpret
  each get the cheapest model that passes the bar — currently `gpt-oss-120b`
  (an open model) served by Groq's free tier. Frontier models are reserved for
  the interactive layer where judgment quality is the product.
- **The OpenAI-compatible API is the universal seam.** Every provider speaks
  it, so swapping models is a one-constant change. This seam has already paid
  twice: Llama 3.3 was retired from Groq's lineup, and Gemini was disqualified
  — zero pipeline changes either time.
- **Open-source serving (vLLM, llama.cpp).** Not needed at this volume — Groq's
  free tier serves the open model *for* us — but the institutional column in
  [stack.md](stack.md) is where it enters: a vLLM fleet for high-volume fixed
  tasks, and eventually a small model fine-tuned on the accumulated triage log
  (the log is literally the future training set).
- **Model selection is an eval, not a vibe.** The distill model was chosen by
  blind pairwise preference test — two models, shuffled A/B, human grades
  without knowing which is which. That is the data-collection stage of RLHF run
  at n=1, and the graded set is archived as a golden set
  ([evals/2026-09-07-distill-bakeoff.json](evals/2026-09-07-distill-bakeoff.json))
  so every future upgrade is measured against it.
- **Embedding models are load-bearing and sticky.** Vectors from different
  models are mutually meaningless, so the embedding model
  (`Qwen/Qwen3-Embedding-0.6B`) is self-hosted with pinned weights — a
  provider can never deprecate the vector space out from under the stored
  vectors. Judgment models are swappable; embedding models are married.

## Layer 3 — Data

*Datasources, pipelines, vector DBs + retrieval.*

- **Sources as config.** Sixteen sources (arXiv categories, HF daily papers,
  lab blogs) declared in [sources.yaml](../sources.yaml) with tiers that act as
  priors downstream — data about the data travels with the data.
- **The medallion architecture (the Databricks lesson).** Bronze (raw papers) →
  silver (distilled claims) → gold (promoted skills), borrowed from the
  lakehouse world. The deeper lesson: pick the right *unit of knowledge*. Here
  it is the **claim**, not the paper — papers are containers; claims are what
  can support, refine, or contradict each other.
- **One database for vectors *and* structure.** Postgres + pgvector means a
  hybrid query ("nearest neighbors among older claims only") is a single SQL
  statement. A dedicated vector DB (Vespa/Qdrant) is the institutional-scale
  answer, not the starting one.
- **The claim graph is relational (ADR-10).** Nodes and edges as ordinary
  tables (`claims`, `claim_links`), append-only and time-directional: new
  claims judge older ones, nothing is edited or deleted, and "deprecated" is a
  *derived view* over incoming `contradicts` edges — the arrow of time is a
  schema property (`where id < current` is the whole mechanism).

## Layer 4 — Orchestration

*The most rapidly evolving layer.*

- **Cron + blackboard beats a framework at this scale (ADR-9).** Four daily
  Modal crons, coordinated not by messages but by a shared blackboard: each
  worker's inbox is a SQL view (`triage_queue`, `distill_queue`,
  `interpret_queue`) defined by left-joins on what has *not yet* been done.
  This buys idempotency and free crash-resume — the interpret worker proved it
  on day one, stopping mid-run when Groq's budget ran out and resuming next
  cron with no lost work, because state lives in the database, not the process.
- **Budget scheduling is orchestration.** Distill runs *before* triage because
  both spend the same Groq token budget and distill is the higher-value spend.
  Ordering jobs by value-per-token is a real orchestration decision.
- **Workflows vs. agents (the Anthropic canon).** Batch work with a known shape
  is a hardwired workflow — fixed retrieval, fixed prompts, fixed order, no
  agency. Agency is reserved for the interactive layer, where the task shape is
  unknown. Temporal/Dagster/LangGraph (institutional column) solve the same
  problems — durable execution, backfills, checkpoints — when scale demands it.

## Layer 5 — Agents

*The loop: perceive → memory → reason → act → observe.*

The daily pipeline **is** this loop, unrolled across cron jobs:

| Stage | In alexandria |
|---|---|
| Perceive | Ingest pulls the day's papers from all sources |
| Memory | Bronze/silver/gold + the claim graph — everything ever learned |
| Reason | Triage routes; distill extracts claims; interpret judges relations |
| Act | Writes to the database; (planned) promotes skills, opens PRs |
| Observe | Triage log records every decision + reasoning; human verdicts label it |

And the *flows* pattern (query → routing → tool calling) appears as: every
paper is a "query," triage is the router (discard / index / distill /
deep-read), and each route leads to different downstream work. Routing by a
small model so the expensive model only sees what deserves it is the
load-management pattern.

**Loop engineering** is deciding what repeats, on what clock, with how much
autonomy, and where the human gate sits. alexandria runs four loops:

1. **Fast loop (daily):** ingest → distill → triage → interpret. Fully
   autonomous, zero agency, zero humans.
2. **Knowledge loop (continuous):** new claims judge old ones; deprecation
   emerges from accumulated contradictions.
3. **Human-gated loop (weekly, planned):** the brief + promotion to gold. The
   *only* place a person appears — "as out of the loop as possible" is achieved
   not by removing the human but by concentrating them at the single
   highest-leverage point.
4. **Recursive loop (weekly, planned):** the meta-review reads the triage log,
   human verdicts, and claim graph, and proposes diffs to the system's own
   prompts and sources — **as pull requests only** (ADR-7). The system never
   modifies itself; the human merge is the gate. Prompts are versioned files
   precisely so self-improvement is expressible as a git diff.

## Cross-cutting patterns

- **RAG.** The full chain from the notes exists here: documents → chunks
  (abstracts and claims are the chunk unit; no PDF parsing needed yet, docling
  is the tool when it is) → embedding model → vector DB → similarity search →
  top-k into the LLM. Interpret is RAG in miniature: each new claim retrieves
  its 5 nearest *older* neighbors via pgvector kNN, and the model only
  classifies pairs put in front of it. **Retrieve-then-reason:** the model is
  never asked to "know" the corpus, only to reason inside a retrieved context —
  that is the hallucination reduction. Two retrieval modes on the same data
  (ADR-6): hardwired kNN for batch, agentic search (MCP) for humans.
- **MCP.** The planned interactive layer: a thin MCP server exposing
  `semantic_search` + `sql_query` over Neon, so a Claude agent (MCP host) can
  interrogate the corpus with flexible, multi-step retrieval when writing the
  weekly brief or answering questions.
- **Skills.** The gold layer *is* the skills concept: procedure + judgment
  distilled into files an agent can load. The terminal state of a paper worth
  keeping is a skill — knowledge in operational form, not archival form.
- **Memory.** The databases are the agent's memory — things picked up and
  stored from what occurred previously. The design decisions that make memory
  work: append-only (never destroy what you learned), time-directional (know
  *when* you learned it), and provenance-stamped (know *how*).

## The engineering stack

- **Context engineering — prompting right.** Prompts are versioned files in
  [prompts/](../prompts/) with their sha recorded on every output, so a prompt
  change is a git diff and its effects are measurable. Tier priors travel into
  the triage prompt; retrieval scopes the interpret prompt; and the backfill
  rule (>60 days → index, no LLM call) is context engineering by subtraction —
  the cheapest token is the one never spent.
- **Harness engineering — managing context and stability from outside the
  model.** The agent can't hold everything and is leaky with important details,
  so the harness holds it instead: the database holds the state, RAG feeds in
  only what's needed per call, and the task is broken down into small stable
  steps (route one batch, distill one paper, classify one pair) rather than one
  heroic prompt. The harness is also the *reliability* layer around a
  stochastic component: JSON mode + schema CHECK constraints (a hallucinated
  category cannot even be written), retries honoring `Retry-After` (429s are
  normal weather on free tiers, not errors), graceful stop + blackboard resume,
  and provenance on every judgment. Free-tier reliability even became a
  model-selection axis: Gemini was disqualified on it.
- **Loop engineering** — covered under Agents above: the four loops, their
  clocks, their autonomy levels, and the placement of the one human gate as the
  central design decision.

## The meta-lesson

Every entry above was learned by hitting the real constraint — a retired model,
a rate-limit storm, a mid-run budget exhaustion — not by reading about it. The
architecture is the textbook, the free-tier constraints are the exercises, and
the ADRs are the notes taken. The institutional-grade column in
[stack.md](stack.md) is the same curriculum at the next difficulty level.
