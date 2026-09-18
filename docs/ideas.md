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

### 2026-09-18 — Skill-verification badge on every library entry
- Trigger: Show HN "State of Skills" report, 69% of 216 audited public
  Claude Code skills don't reliably trigger, 57% of subagents declare no
  tools list
  ([news.ycombinator.com/item?id=49744398](https://news.ycombinator.com/item?id=49744398),
  2026-09-17)
- What: every skill in the paid library ships with a visible "verified
  against N sources, confidence X" line pulled from the claim graph, plus
  a trigger-reliability score, so the differentiator from every other
  skill marketplace observed (skills.sh, skillbay.sh, Smithery-hosted
  registries, none of which attach evidence to a listed skill) is
  checkable, not asserted
- First step: define the badge schema against the existing claim-graph
  `supports`/`contradicts` edges and prompts/skill-extract.md
- Cost: $0
- Status: proposed

### 2026-09-18 — Scoped skill delivery by default
- Trigger: Show HN "Skillzero — save tokens by omitting skills from agent
  context," a commenter asking whether scoping works "on repo level"
  ([news.ycombinator.com/item?id=49698184](https://news.ycombinator.com/item?id=49698184),
  2026-09-14)
- What: the skill-library UX loads only skills relevant to the current
  task or repo by default, not the full library into context, avoiding
  the context bloat and reliability loss the HN thread describes
- First step: define scoping rule (task/repo signal) with the engineer
  agent before the skill library ships
- Cost: $0
- Status: proposed

### 2026-09-18 — Orchestration-pattern benchmark, tied to the claim graph
- Trigger: Ask HN "Multi-agent workflows in production," practitioners
  explicitly asking for multi-agent observability/benchmark tooling and
  reporting they've "not really seen anything outstanding in this space"
  ([news.ycombinator.com/item?id=49689454](https://news.ycombinator.com/item?id=49689454),
  2026-09-13)
- What: a maintained, versioned table of orchestration/harness patterns
  with measured cost, latency, and error tradeoffs, each row backed by a
  claim-graph citation, exposed as part of the $20/month tier
- First step: scope as a claim-graph query/view before committing to new
  data collection
- Cost: $0
- Status: proposed
