# alexandria

A self-evolving pipeline that stays current on AI research and converts what it reads into
operational assets — skills, context-engineering patterns, and agentic loop designs.

The terminal state of a paper is never "read." It is a **skill**, a **pattern note**, or a
**discard**. A paper that doesn't eventually change how an agent is built was, for this
system's purposes, noise.

## Architecture

```mermaid
flowchart TB
    SRC[arXiv + lab blogs] --> ING[Ingest<br/>daily cron, Modal]
    ING --> BR[(Bronze<br/>raw papers)]
    BR --> TRI[Triage<br/>small model routes]
    TRI --> LOG[(Triage log<br/>every decision + reasoning)]
    TRI --> DIS[Distill<br/>frontier model]
    DIS --> SI[(Silver<br/>distilled claims)]
    SI --> BRIEF[Weekly brief]
    BRIEF --> YOU{Human review}
    YOU --> GO[(Gold<br/>skills + patterns)]
    LOG --> META[Meta-review<br/>weekly]
    SI --> META
    META --> PR[Proposed diffs<br/>as pull requests]
    PR --> YOU
```

The data model follows the **medallion architecture** (borrowed from the lakehouse world):

| Layer | Contents | Written by |
|---|---|---|
| Bronze | Raw papers, abstracts, source metadata | Ingest job |
| Silver | Distilled claims — the unit of knowledge is the *claim*, not the paper | Distill job |
| Gold | Promoted assets: skill files, pattern notes | Human approval only |

Two loops run over this data:

1. **The pipeline loop** (daily/weekly): ingest → triage → distill → brief → human promotion.
2. **The recursive loop** (weekly): the meta-review reads the triage log (the eval set — every
   decision is recorded with its reasoning, and human verdicts label it) plus newly distilled
   claims, and proposes diffs to the system's own prompts and pipeline **as pull requests**.
   The system never modifies itself autonomously; the human merge is the gate.

## Stack

| Concern | Choice | Why |
|---|---|---|
| Compute | [Modal](https://modal.com) — scheduled functions, scale to zero | Per-second billing matches a system that works minutes per day; free credits cover it entirely |
| Database | [Neon](https://neon.tech) — serverless Postgres + pgvector | Scale-to-zero; one DB holds vectors *and* structured data, so hybrid queries are single statements |
| Triage model | Llama 3.3 70B via Groq free tier | Open model, $0, 10× headroom over our volume |
| Distill model | Claude (Anthropic API) | Frontier reasoning where quality matters; the only metered cost (~$1–2/mo) |
| Embeddings | Qwen3-Embedding-0.6B, in-process on Modal | Top open family on MTEB; batch jobs need no serving endpoint |
| Interactive search | MCP tools over Postgres (`semantic_search` + `sql_query`) | Agentic retrieval for humans; hardwired retrieval for batch |
| Code, prompts, gold | This repo | Prompts are versioned files, so self-improvement proposals are literal git diffs |

Standing cost: **$0/month**. See [docs/decisions.md](docs/decisions.md) for every
architectural decision and the reasoning behind it.

## Layout

```
db/schema.sql        bronze / silver / gold tables + triage log (the eval set)
pipeline/            Modal apps: ingest, triage, distill, meta-review
prompts/             versioned prompts — the recursive loop proposes diffs against these
skills/              the gold layer: promoted skills and pattern notes
docs/decisions.md    architecture decision records
```

## Status

- [x] Architecture designed (see decisions doc)
- [x] Repo scaffold, schema, ingest job
- [ ] Neon database provisioned, schema applied
- [ ] Triage job wired to Groq
- [ ] Distill job wired to Anthropic
- [ ] Weekly brief + promotion flow
- [ ] Meta-review recursive loop
