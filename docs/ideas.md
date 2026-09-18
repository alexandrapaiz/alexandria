# Ideas ledger

The engineer agent's proposal surface and the owner's steering wheel. The
agent appends; the owner writes verdicts. Contract in
[prompts/engineer-agent.md](../prompts/engineer-agent.md).

Statuses: `proposed`, `accepted`, `rejected`, `built`, `urgent`.

## Standing backlog (owner-directed, all accepted)

Groomed 2026-09-18 by the PM agent (ADR-15), per the owner's all-hands
directive to build one consolidated backlog. The full leverage-ordered
view, plus the OKR agent's and market agent's proposals and the launch
blockers, now lives in [docs/backlog.md](backlog.md); this ledger stays
the append-and-verdict contract exactly as prompts/engineer-agent.md
defines. Statuses below are untouched; only the owner moves them.

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
- Groomed 2026-09-18 (PM): superseded in shape, not in status, by the
  owner's 2026-09-17 pricing decision (vision.md §0). The digest is now
  free in full; there is no digest-tier paywall to gate. The teaser gate
  described above moves to the $20 spine only: the skill library, the
  claim graph, and automations. Clerk auth and the Vercel deploy still
  stand as written. This week's sprint (docs/sprints/sprint-2026-09-21.md)
  carries the first two engineer items that redesign this entry's gate
  before the rest of it is built.

### 2026-09-17 — Skill-extract prompt
- Trigger: gold layer needs its authoring prompt
- What: write `prompts/skill-extract.md`, the prompt that turns a cluster of
  claims into a draft skill for the panel to judge
- First step: draft against one real claim cluster
- Cost: $0
- Status: accepted

## Proposals
