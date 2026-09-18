# Ideas ledger

The engineer agent's proposal surface and the owner's steering wheel. The
agent appends; the owner writes verdicts. Contract in
[prompts/engineer-agent.md](../prompts/engineer-agent.md).

Statuses: `proposed`, `accepted`, `rejected`, `built`, `urgent`.

## Standing backlog (owner-directed, all accepted)

### 2026-09-17 — Reviewer panel harness (ADR-13)
- Trigger: owner's decision to replace the human gate with an agent panel
- What: implement the three reviewers (provenance, adversary, validator) as
  a pass in the weekly agent over open promotion PRs, structured verdicts as
  `promotions` rows, unanimous pass merging via the server-held token. Note:
  the current GitHub fine-grained PAT has contents read/write only; the
  owner must mint the PR-merge scope herself.
- First step: verdict schema and the provenance reviewer
- Cost: $0
- Status: accepted

### 2026-09-17 — Institution backfill, then regenerate and resend digest
- Trigger: known gap; scratchpad script `backfill_institutions.py` exists
- What: backfill institutions within the Groq budget, then regenerate the
  digest and resend
- First step: run the backfill inside the daily budget window
- Cost: $0
- Status: accepted

### 2026-09-17 — Member site auth and deploy
- Trigger: Sprint 2 plan in vision.md
- What: Clerk auth plus Vercel deploy on the ALEX team, server-side teaser
  gate against the Neon subscribers table
- First step: Clerk integration on the local site
- Cost: $0 (free tiers)
- Status: accepted

### 2026-09-17 — Skill-extract prompt
- Trigger: gold layer needs its authoring prompt
- What: write `prompts/skill-extract.md`, the prompt that turns a cluster of
  claims into a draft skill for the panel to judge
- First step: draft against one real claim cluster
- Cost: $0
- Status: accepted

## Proposals

### 2026-09-18 — competitive scan: the Agent Skills marketplace ecosystem
This is the day's craft-scan note (engineer charter, Observe step 4), not a
build proposal on its own — the actionable idea it produced is "Agent packs"
below.

- Trigger: rotating the daily scan to Anthropic's open Agent Skills spec
  (agentskills.io) and its resale ecosystem, per Agentman's *Agent Skills
  Ecosystem Report 2026* — eight marketplaces by Q2 2026, up from one
  registry in December 2025.
- Worth stealing: several marketplaces sell "a skill plus the activation
  prompt that drives a whole multi-step job" as a distinct SKU, priced above
  a bare skill file (roughly $9-32 for a prompt pack/agent vs. $3.99-19 for a
  skill alone).
- What alexandria already does better: every skill here traces to specific
  claim ids and gets revised or retired when the evidence moves (ADR-13's
  panel, the claim graph's `contradicts` edges). A marketplace skill, once
  bought, is a static file with no mechanism to update when the underlying
  research changes.

### 2026-09-18 — Ask alexandria: hosted RAG API
- Trigger: all-hands directive to build RAG as a sellable capability, not
  only an internal tool (docs/product/pipeline.md §5); `rag_answer` shipped
  this run inside the MCP server (ADR-20) but only reaches Claude-connector
  users today.
- What: expose the same retrieval + synthesis outside the MCP connector as a
  metered HTTP endpoint (API key auth, per-key rate limit) so a non-Claude
  customer can ask a question and get a cited answer over the corpus. No new
  synthesis logic — the new work is auth and metering around what exists.
- First step: an API-key table plus one FastAPI route on the existing Modal
  app that calls the same retrieval + `rag_answer` logic, gated by a free,
  unmetered friends-and-family tier first
- Cost: $0 to build; a per-query or per-seat price is a pricing proposal for
  the owner before anything is charged
- Status: proposed

### 2026-09-18 — Frontier-model synthesis tier for RAG
- Trigger: ADR-5's right-size-the-model rule (cheap model for routine work,
  frontier model where judgment quality is the product) applies to RAG
  synthesis exactly as it already does to distill.
- What: let a paying tier's `rag_answer` calls route to Claude instead of the
  free-tier `gpt-oss-120b`, on the bet that synthesis quality is worth
  metered cost for a customer who's paying, the same way distill quality
  was worth it for the pipeline.
- First step: a measured blind pairwise comparison of the two models on
  `rag_answer` outputs, same method as the 2026-09-07 distill bake-off
  (docs/evals/2026-09-07-distill-bakeoff.json), before spending anything
- Cost: metered Anthropic API cost per paid query — a pricing proposal, not
  an action this ledger authorizes
- Status: proposed

### 2026-09-18 — Harness audit as a sellable service
- Trigger: docs/product/pipeline.md §3 — the five harness disciplines
  alexandria already runs on itself (state outside the model, small stable
  steps instead of one heroic prompt, schema-constrained output, retries
  that honor rate limits, provenance on every judgment) are a checklist most
  agent builders don't have and don't know they're missing.
- What: a short, structured review of someone else's agent codebase against
  that checklist, delivered as a written report naming what's missing and
  the concrete fix for each gap.
- First step: run the checklist against alexandria's own pipeline first, as
  the worked example a first customer would want to see before buying a
  review of their own system
- Cost: $0 to build the checklist/template; delivery is a sold service, not
  an automation, so it costs nothing standing
- Status: proposed

### 2026-09-18 — Agent packs: skill + activation prompt as a priced SKU
- Trigger: this run's competitive scan (above) — marketplaces built on
  Anthropic's Agent Skills spec sell a skill bundled with its activation
  prompt as a distinct, higher-priced SKU than a bare skill.
- What: package a gold-layer skill together with the prompt/workflow that
  invokes it end to end (e.g. "run the distill-model bake-off methodology
  against your own candidate models") as a tier above the $20 library,
  carrying the same evidence-and-revision discipline as every skill here.
- First step: pick the first gold skill with an obvious end-to-end activation
  workflow (harness-engineering is the current candidate) and draft the
  bundle format
- Cost: $0 to build; pricing above the $20 spine is a proposal for the owner
- Status: proposed

### 2026-09-18 — Claim graph API
- Trigger: docs/product/pipeline.md §6 — the claim graph
  (`supports`/`refines`/`contradicts` edges) is structured data with no
  competitor equivalent, and today it only ever surfaces as digest prose.
- What: a read-only API surface over `claim_links` (already queryable
  internally via `sql_query`) for programmatic access — a builder queries
  "what contradicts claim X" directly instead of reading a summary of it.
- First step: define a small, fixed query surface (2-3 endpoints, not open
  SQL) reusing the MCP server's existing read-only-DB pattern
- Cost: $0
- Status: proposed
