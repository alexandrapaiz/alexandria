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

Triage: Llama 3.3 70B on Groq's free tier (~100 calls/day against a 1,000/day cap).
Distillation: Claude via the Anthropic API — the only metered cost, ~$1–2/month.
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
