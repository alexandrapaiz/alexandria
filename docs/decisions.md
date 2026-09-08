# Architecture decision records

Each entry: the decision, the alternatives weighed, and why. These are the study
material as much as the system is — the meta-goal of alexandria is learning systems
architecture by making these calls deliberately.

## ADR-1: Terminal state of a paper is an artifact, not "read"

Every ingested paper ends as a skill, a pattern note, or a discard. This single
decision drives the rest of the design: it makes the claim (not the paper) the unit
of storage, makes triage a routing problem rather than a summarization problem, and
gives the system a falsifiable purpose.

## ADR-2: Compute on Modal, serverless, scale-to-zero

Alternatives: GitHub Actions cron (free forever, no card, but unpunctual cron, no
GPU, push-to-test dev loop), rented GPU instance (billed while idle — wrong cost
structure for minutes-per-day workloads). Modal wins on scheduling reliability,
seconds-fast dev loop (`modal run`), first-class logs, and an open GPU path; the
$30/month starter credits cover the entire workload. GitHub Actions remains the
documented fallback — the swap was designed and costed before choosing.

## ADR-3: One Postgres (Neon) with pgvector, not a dedicated vector DB

Alternatives: Pinecone/Qdrant/Chroma (a second system to sync), Supabase (fine, but
an app platform whose auth/storage/API batteries we would not use), Turso (not
Postgres). Neon is exactly the needed thing: serverless Postgres, scale-to-zero,
vectors and structured data in one store so hybrid queries (semantic ranking +
SQL filters) are single statements.

## ADR-4: Medallion data model (bronze / silver / gold)

Borrowed from the lakehouse world: bronze = raw papers, silver = distilled claims,
gold = human-approved skills and patterns. Adopting the pattern at 1/1000th scale is
also the cheapest way to genuinely understand Databricks-style architectures.

## ADR-5: Right-size the model to the task

Triage: the largest open model on Groq's free tier (gpt-oss-120b as of 2026-09;
Groq rotates its lineup, which is exactly why the model name is one constant).
Distillation: originally slated for Claude (paid); AMENDED 2026-09-07 by blind
bake-off (docs/evals/2026-09-07-distill-bakeoff.json): gpt-oss-120b won 4–1–3
over Qwen3.8-27B on faithfulness and claim readability, so distillation is $0 on
Groq too; Qwen3.8 is the fallback, and Gemini was disqualified on free-tier
reliability (7/8 calls 429'd under backoff). Upgrading to a paid frontier
distiller stays on the roadmap, now with a golden set to measure it against.
Embeddings: Qwen3-Embedding-0.6B in-process on Modal (top open family on MTEB;
batch jobs load the model in the job, no serving endpoint needed). All providers sit
behind swappable interfaces; free-tier limits change, so portability is designed in.

## ADR-6: Retrieval is hardwired for batch, agentic for humans

The triage loop uses classic pipeline retrieval (embed, dedupe, route) because the
retrieval need is known in advance — hardwired is cheaper and more predictable. The
interactive side exposes `semantic_search` and `sql_query` as MCP tools and lets the
agent decide what to search and when to stop. Same database, two consumption modes.

## ADR-7: The system proposes changes to itself; a human merges them

The weekly meta-review reads the triage log (every decision + reasoning, labeled by
human verdicts — the eval set the pipeline emits as exhaust) and newly distilled
claims, and opens pull requests against the system's own prompts and code. It never
self-modifies: unsupervised drift in triage criteria is the eval problem eating
itself, and the human review step is where the owner's learning happens. Prompts are
versioned files precisely so that self-improvement proposals are literal git diffs.

## ADR-8: The digest looks backward as well as forward

The weekly brief is not only "what's new." Two retrospective sections are part of
the design (implemented once the claims layer has accumulated history):

- **Matured** — a slow loop revisits past claims and index-tier papers after
  months, using citation counts (Semantic Scholar API) and reinforcement by later
  claims to surface what aged well — including sleepers our triage under-rated,
  which become labeled eval failures for the meta-review.
- **Deprecated** — when a new claim lands, semantic search finds its nearest older
  claims and a model classifies the relation (supports / refines / contradicts);
  contradiction edges surface superseded techniques in the digest.

Citation counts are deliberately NOT used at the leading edge: papers arrive with
zero citations, so citations are a lagging signal — useful for retrospectives,
useless for daily triage. The fast attention proxy at the front edge is tier `b`
(human curation).

## ADR-9: Blackboard coordination — the schema is the orchestrator

Workers (ingest, triage, distill, meta-review) never message each other. They read
and write a shared store, and coordination emerges from the data's state — the
blackboard pattern (Hearsay-II, 1970s AI), rediscovered by every pipeline that
scales. Each worker's inbox is a SQL view (`triage_queue`, `distill_queue`):
an item is claimed when the worker's output row exists, which makes idempotency
and resume properties of the schema rather than of any worker's code. The
alternative — multi-agent message passing — buys parallelism at the cost of an
order of magnitude more tokens and much harder debugging; it is the institutional
swap (see docs/scaling.md), not the default. Corollary: adding a pipeline stage
means adding a view, and the stage's contract is reviewable as one SQL statement.

## ADR-10: Claim graph in Postgres, append-only, time-directional

The interpreting layer relates claims: supports / refines / contradicts /
duplicates, stored as an edges table (`claim_links`). Relational over Neo4j
because our traversals are shallow (1–3 hops), our graph queries constantly fuse
with SQL filters and pgvector similarity (one store, one query), and the graph is
small and derived — rebuildable from silver at any time. Neo4j is the
institutional swap when deep traversals dominate (docs/scaling.md); Apache AGE is
the middle rung if Cypher ergonomics are ever wanted inside Postgres.

Edges are append-only and time-directional: a new claim judges strictly older
claims; edges are never edited. Re-judgment (a later claim recontextualizing an
old edge) belongs to the slow loop. Mechanism per edge: pgvector kNN retrieves
candidate neighbors cheaply, a small model classifies the shortlisted pairs —
the same retrieve-then-reason shape as triage and RAG, one level up. The
`deprecated_claims` view (a confident incoming `contradicts` edge from a newer
claim) is ADR-8's digest section expressed as SQL.
