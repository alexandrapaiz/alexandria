# The stack — current, and industrial-grade at scale

Two snapshots of the same logical architecture. The first is what runs today,
named exactly. The second is what each binding becomes if alexandria scales to a
team- or product-grade system — specific technologies, not categories. The
upgrade path between them is governed by [scaling.md](scaling.md): swap one row
at a time, under measured load, never breaking the schema contract.

## Current stack (v1, running now — $0/month)

**Infrastructure**
- Compute: **Modal** (Starter plan, workspace `ap4509`), serverless functions on
  `debian_slim` Python 3.11 images; scale-to-zero, per-second billing inside the
  free monthly credits. One persistent **Modal Volume** (`hf-cache`) holds
  embedding-model weights across runs.
- Schedules (UTC daily): ingest 11:00 → distill 11:30 → triage 12:00 →
  interpret 14:00. Distill runs before triage on purpose: they share Groq's
  daily token budget and distill is the higher-value spend.
- Database: **Neon** serverless Postgres (project `alexandria`, AWS us-east-2)
  with **pgvector**; HNSW indexes, cosine distance. 5 tables (`papers`,
  `triage_log`, `claims`, `claim_links`, `promotions`), 4 views (`triage_queue`,
  `distill_queue`, `interpret_queue`, `deprecated_claims`).
- Code: public GitHub repo `alexandrapaiz/alexandria` — code, prompts, ADRs,
  golden evals, and (eventually) gold skills, all versioned together.
- Secrets: Modal secret store (`neon`, `groq`). Nothing sensitive in the repo.

**Models**
- Judgment (triage, distill, interpret): **`openai/gpt-oss-120b` via Groq free
  tier**, OpenAI-compatible chat completions, JSON mode, temperature 0.1–0.2.
  Chosen for distill by blind human bake-off 4–1–3 over Qwen3.8-27B
  ([evals/2026-09-07-distill-bakeoff.json](evals/2026-09-07-distill-bakeoff.json)).
- Fallback: **`qwen/qwen3.8-27b`** (also Groq). Disqualified: Gemini free tier
  (7/8 calls 429'd under exponential backoff).
- Embeddings: **`Qwen/Qwen3-Embedding-0.6B`**, self-hosted in-process on Modal
  via `sentence-transformers`; 1024-dim, normalized, cosine. Self-hosted so the
  vector space can never be deprecated out from under the stored vectors.
- Interactive layer (planned): Claude via a scheduled agent + MCP tools.

**Data & libraries**
- Sources: 7 arXiv categories (cs.CL, cs.AI, cs.MA, cs.IR + low-prior cs.LG,
  cs.DC) + Hugging Face `api/daily_papers` + 11 verified RSS feeds
  ([sources.yaml](../sources.yaml)), tiered a/a-low/b/c/d as triage priors.
- Python: `psycopg[binary]` 3.2, `httpx` 0.28, `feedparser` 6.0, `pyyaml` 6.0,
  `sentence-transformers`, `modal` ≥1.5.
- Patterns: medallion (bronze/silver/gold), blackboard coordination via SQL
  views, append-only time-directional claim graph, prompts as versioned files.

**Evals & observability**
- Triage log: every routing decision with score, reasoning, model, prompt hash,
  and a human-verdict column. Golden set: the graded distill bake-off. Runtime
  logs: Modal dashboard per app.

## Industrial-grade stack (if/when it scales)

The same system serving a team or paying customers, each binding named:

**Infrastructure**
- Orchestration: **Temporal** (durable execution) or **Dagster** (partitioned
  backfills) replacing bare crons; **LangGraph** for the agentic components'
  state machines, checkpoints, and human-in-the-loop interrupts.
- Streaming ingestion: **Kafka** (Confluent Cloud) with per-source connectors,
  schema registry, dead-letter queues, replacing daily RSS pulls.
- Storage: bronze moves to **S3 + Apache Iceberg** (immutable log at any
  volume); silver/gold computed by **dbt** or **Spark on Databricks**, with
  **Unity Catalog** for lineage. Hot serving data stays in Postgres (managed
  HA — Neon scale tier or RDS).
- Retrieval: dedicated engine — **Vespa** or **Qdrant** — for hybrid BM25 +
  dense + learned reranking (e.g. a Qwen3-Reranker) once corpus size or QPS
  outgrows pgvector.
- Claim graph: **Neo4j Aura** when multi-hop traversals dominate the query mix.
- IaC + CI/CD: **Terraform**, GitHub Actions with test + eval gates, staging
  environment, canary deploys.
- Secrets/compliance: **Vault** or cloud KMS, least-privilege service accounts,
  audit logging, SOC 2 posture.

**Models**
- Gateway: **LiteLLM** or a managed AI gateway for routing, fallback chains,
  and per-stage cost attribution; provisioned-throughput contracts with
  **Anthropic** (frontier distillation/synthesis) alongside open models.
- Self-hosted serving: **vLLM** fleet on rented GPUs (Modal or Kubernetes) for
  high-volume fixed tasks; **fine-tuned small models** (e.g. an 8B tuned on the
  accumulated triage log) replacing prompted large ones where volume justifies
  training — the triage log is literally the future training set.
- Embeddings: versioned embedding **service** with blue/green re-embedding
  pipelines; index versions pinned to model versions.

**Evals & observability**
- **Braintrust** or **LangSmith**: golden datasets, CI-gated prompt regression,
  A/B prompt rollout; LLM-as-judge calibrated against the human golden sets
  (the RLAIF pattern).
- **OpenTelemetry** traces per pipeline step into **Grafana/Datadog**; cost per
  stage/model/token; SLOs and alerting.

**Product surface**
- Multi-tenant API + web app (Next.js on Vercel), auth via **WorkOS/Auth0**,
  entitlements, and the gold layer as a subscribable research feed — the
  commercial form of this system.
