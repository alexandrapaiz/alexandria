# Ideas ledger

The engineer agent's proposal surface and the owner's steering wheel. The
agent appends; the owner writes verdicts. Contract in
[prompts/engineer-agent.md](../prompts/engineer-agent.md).

Statuses: `proposed`, `accepted`, `rejected`, `built`, `urgent`.

## Standing backlog (owner-directed, all accepted)

Groomed 2026-09-17 by the PM agent (ADR-15). Leverage order against
vision.md §0, autonomy first and product quality as the north star:
1 reviewer panel, 2 skill-extract prompt, 3 institution backfill, 4 member
site. Entries larger than a day carry a day-sized split below their
original text. Statuses are untouched; only the owner moves them.

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
- Groomed 2026-09-17 (PM): leverage rank 1, the only entry that directly
  raises autonomy. Larger than a day, split into five day-sized items:
  (a) verdict table and unanimous-pass view in `db/schema.sql` plus the
  provenance reviewer as a local function, in sprint 2026-09-14 item 1;
  (b) the provenance pass wired into the weekly cron over open promotion
  PRs, recording rows and merging nothing, sprint 2026-09-14 item 4;
  (c) adversary reviewer, a claim-graph search for `contradicts` and
  `refines` edges the draft ignored; (d) validator reviewer, the A/B trial
  on held-out prompts; (e) unanimous-pass merge through the server-held
  token, blocked until the owner mints the PR-merge scope. (c) through (e)
  are next sprint's candidates.

### 2026-09-17 — Institution backfill, then regenerate and resend digest
- Trigger: known gap; scratchpad script `backfill_institutions.py` exists
- What: backfill institutions within the Groq budget, then regenerate the
  digest and resend
- First step: run the backfill inside the daily budget window
- Cost: $0
- Status: accepted
- Groomed 2026-09-17 (PM): leverage rank 3, a visible digest-quality fix
  that fits one session. Day-sized as written. Sprint 2026-09-14 item 3.
  Dependency: the scratchpad script lives outside the repo, so the first
  act is bringing it into `pipeline/`.

### 2026-09-17 — Member site auth and deploy
- Trigger: Sprint 2 plan in vision.md
- What: Clerk auth plus Vercel deploy on the ALEX team, server-side teaser
  gate against the Neon subscribers table
- First step: Clerk integration on the local site
- Cost: $0 (free tiers)
- Status: accepted
- Groomed 2026-09-17 (PM): leverage rank 4, the business end state but
  blocked on the owner's prerequisites (a Clerk account, and the Neon
  connection string plus Clerk keys as Vercel env vars, per
  docs/roadmap.md). Larger than a day, split into four: (a) Clerk sign-in
  on the local site; (b) server-side entitlement check of the signed-in
  email against `subscribers` where status is active; (c) the teaser gate
  on issue pages, first paragraph public and the rest entitled-only,
  rendered server-side; (d) Vercel deploy on the ALEX team with env vars
  set by the owner. Not in sprint 2026-09-14. Enters the first sprint
  after the Clerk keys exist.

### 2026-09-17 — Skill-extract prompt
- Trigger: gold layer needs its authoring prompt
- What: write `prompts/skill-extract.md`, the prompt that turns a cluster of
  claims into a draft skill for the panel to judge
- First step: draft against one real claim cluster
- Cost: $0
- Status: accepted
- Groomed 2026-09-17 (PM): leverage rank 2, because the panel needs drafts
  to judge and the library is the paid tier. Day-sized as written.
  Sprint 2026-09-14 item 2. Independent of the panel work, so it does not
  wait on item 1.

## Proposals
