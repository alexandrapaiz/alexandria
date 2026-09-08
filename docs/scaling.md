# Scaling map: MVP ↔ institutional grade

The logical architecture (medallion data model, blackboard coordination, claims as
the unit of knowledge, human-gated promotion, recursive improvement) is designed to
survive scaling unchanged. What changes at institutional scale is the physical
binding of each concern. This table is the upgrade path — each row is a swap that
can happen independently, in whatever order load demands, without touching the
rows above or below it.

| Concern | MVP (today) | Institutional grade |
|---|---|---|
| Batch orchestration | Modal cron + idempotent SQL resume | Temporal or Dagster/Airflow: durable execution, retries, backfill partitions, SLA alerts |
| Agentic orchestration | Claude agent + MCP tools | LangGraph-style state graphs with checkpoints, human-in-the-loop interrupts, replayable runs |
| Ingestion | feedparser, daily pull, ~16 feeds | Streaming ingestion (Kafka/Kinesis), schema registry, per-source connectors, dead-letter queues |
| Bronze storage | Postgres tables (Neon) | Object storage (S3 + Parquet/Iceberg) — cheap immutable log at any volume; Postgres keeps hot data only |
| Silver/gold compute | Python in Modal jobs | Spark or dbt transformations on a lakehouse (Databricks/Snowflake), with a data catalog + column-level lineage |
| Vector retrieval | pgvector HNSW in the same DB | Dedicated retrieval service (Vespa, Qdrant, OpenSearch): hybrid BM25+dense, learned rerankers, index lifecycle management |
| Claim graph | Edges table in Postgres, recursive CTEs | Graph database (Neo4j/Neptune) or graph compute on the lakehouse, once traversals dominate the query mix |
| Model access | Free-tier Groq + Anthropic API, one key each | Gateway layer: routing, fallbacks across providers, provisioned-throughput contracts, per-stage model registry |
| Model serving | None (APIs only) | Self-hosted vLLM fleet for high-volume fixed tasks; fine-tuned small models replacing prompted large ones where volume justifies training |
| Embeddings | One model, embed-on-ingest | Versioned embedding service; re-embedding pipelines as models improve; embedding version pinned per index |
| Evals | triage_log + human verdicts in SQL | Eval platform (Braintrust/LangSmith): golden datasets, CI-gated prompt regression, A/B prompt rollout, drift monitors |
| Observability | Modal logs, print statements | OpenTelemetry traces per pipeline step, dashboards, cost attribution per stage/model/token, alerting + SLOs |
| Secrets & access | Modal secret store | Vault/KMS, least-privilege service accounts, audit logging, compliance regime (SOC 2) |
| CI/CD | Push to main, `modal deploy` by hand | CI with tests + eval gates, staging environment, canary deploys, infrastructure as code, one-click rollback |
| Human review | One reviewer merging PRs | Review queues with RBAC, editorial workflow, labeling tooling, inter-rater agreement tracking |
| Product surface | Weekly brief to one person | Multi-tenant API + web product, entitlements, caching/CDN, SLAs — the gold layer as a sellable feed |

Reading the table column-wise teaches the pattern: every institutional row is the
MVP row plus one of {durability, throughput, multi-tenancy, auditability}. Scale
pressure names which property you're buying; nothing else should change.

Two standing rules for the upgrade path:

1. **Swap one row at a time, under load evidence.** Each swap is justified by a
   measured bottleneck, never by architecture envy. The MVP bindings are not
   placeholders — at current scale they are the correct engineering.
2. **The schema is the contract.** Any swap that would force a change to the
   medallion semantics, the claims model, or the blackboard queues is not an
   upgrade; it is a different system and gets argued about explicitly.
