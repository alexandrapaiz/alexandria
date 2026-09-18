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

### 2026-09-17 — Public digest archive page (OKR agent, first benchmark)
- Trigger: baseline benchmark scored product surface 1.3 of 5; TLDR AI
  has a public archive and Elicit a full web app, while alexandria has
  no public page at all
- What: publish past digests as pages on the site behind the teaser
  gate, so the judgment advantage is visible before someone subscribes
- First step: render one issue from the digests store into the existing
  site/app/library route
- Cost: $0
- Status: proposed

### 2026-09-17 — List the gold skills at agentskills.io (OKR agent)
- Trigger: benchmark vs Anthropic's ecosystem scored agent
  actionability 1 of 5; the skills are already in the standard SKILL.md
  format, and distribution is the entire gap
- What: submit harness-engineering (and each later promoted skill) to
  the agentskills.io partner directory, provenance block intact, as the
  first distribution channel for the library tier
- First step: read the directory's submission requirements and check
  they permit a link back to the paid library
- Cost: $0
- Status: proposed

## Purpose proposals (owner decision only)

Not build items. These touch mission and purpose, which vision.md §0
reserves for the owner in her own words. The OKR agent proposes here;
nothing here is canonical until the owner writes it into vision.md
herself.

### 2026-09-18 — Mission proposal: the overarching goal (OKR agent)

- Trigger: owner's directive at the first all-hands, "propose our big
  overarching goal; overly ambitious" (docs/allhands/2026-09-17.md,
  OKR seat directives).
- What: alexandria becomes the operating layer a serious AI builder
  checks before trusting a claim or writing an orchestration script,
  the standard reference for what the frontier currently believes and
  the default skill source their agents load to act on it. Concretely,
  by the end of 2029 (the vision's own three-year horizon): the claim
  graph is cited as a source of record outside alexandria's own
  channels, the skill library is large and validated enough that
  competing agent frameworks point to it rather than duplicate it, and
  the business runs on paying subscribers at a scale that makes it a
  real company, not a side project, with the owner as owner and no
  headcount required to keep the pipeline running. This is deliberately
  overly ambitious, per the owner's instruction. It is a stretch to
  fail forward from, not a KR to be graded, and it must not compete
  with the differentiation statement: technical research, systems, and
  directly applicable orchestration tools, never AI news
  (docs/allhands/2026-09-17.md, Decisions §5).
- Why now: the OKR hierarchy (purpose then OKRs then sprints then days)
  had no top rung above the quarter until this proposal. Quarterly OKRs
  answer "what proves progress this quarter." This answers "progress
  toward what," so O1-O3 in docs/okrs/okrs-2026-Q4.md can be checked
  against it once approved.
- First step: the owner reads this and either writes a version of it
  into vision.md in her own words, edits it, or rejects it. Nothing
  changes in how the quarter is run either way.
- Cost: $0
- Status: proposed
