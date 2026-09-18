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

### 2026-09-18 — Permanent free sample issue on the site (market agent)
- Trigger: walkthrough found "Read an issue" leads to an empty archive,
  while every profiled paid comp converts through free samples
  (Pragmatic Engineer's partial-deepdive mechanic,
  newsletter.pragmaticengineer.com/about). Evidence in
  docs/market/report-2026-09.md §6.
- What: keep at least one complete, current issue publicly readable on
  the site at all times, chosen and rotated by the weekly cron
- First step: publish one full issue body as a public fixture the
  library page renders when no member session exists
- Cost: $0
- Status: proposed

### 2026-09-18 — Email capture before payments exist (market agent)
- Trigger: the Subscribe CTA dead-ends at a "Coming soon" pricing page
  with no way to leave an email, while paid-newsletter conversion runs
  2-5% off a free list that must be built first
  (backlinko.com/substack-users,
  beehiiv.com/blog/the-state-of-paid-newsletters-2026)
- What: a one-field email signup on home and pricing writing to the
  Neon subscribers table as status waitlist, no service needed
- First step: a Next.js server action inserting into the existing table
- Cost: $0
- Status: proposed

### 2026-09-18 — Make the hero metric live (market agent)
- Trigger: "3,431 papers ingested this week" is hardcoded in
  site/app/page.jsx while the repo is public and the target audience
  reads source. A static number styled as telemetry costs trust with
  exactly the buyers alexandria wants (report-2026-09.md §6)
- What: render the weekly ingest count from the database at build or
  revalidate time, with an honest fallback when unavailable
- First step: reuse the desk page's revalidate pattern for one query
- Cost: $0
- Status: proposed

### 2026-09-18 — Show each skill's validation evidence on its page (market agent)
- Trigger: the skills ecosystem now counts 800k+ scraped skills with no
  quality signal anywhere (skillsmp.com, skills.sh), so trust is the
  scarce good, yet alexandria's own A/B validation note sits buried in
  SKILL.md frontmatter where no prospect sees it
- What: render provenance on the public skill card: validation result,
  claim count, paper links, and the revise-or-retire policy
- First step: parseSkill already reads frontmatter, add the validated
  field to the skills page card
- Cost: $0
- Status: proposed

### 2026-09-18 — A free teaser skill on the public directories (market agent)
- Trigger: skills.sh top listings show 0.9M-3.4M installs and support
  22+ agents, a zero-cost distribution rail pointed at the exact $30
  tier buyer. The $30 tier's risk is category education, and a free
  sample is the education (report-2026-09.md §7)
- What: publish one older or reduced alexandria skill free, carrying
  its provenance block and a pointer to the library. The owner performs
  the actual listing, since agents never post
- First step: pick the candidate skill and prepare the listing files in
  the repo for her one-command publish
- Cost: $0
- Status: proposed

### 2026-09-18 — Make "left behind" the public flagship (market agent)
- Trigger: demand signals show the unmet need is retrospective
  judgment, "keeping up with everything in AI is impossible"
  (news.ycombinator.com/item?id=48939630), and no free digest tracks
  what stopped being true. It is alexandria's least copyable section
  because it requires the claim graph's memory
- What: lead marketing with one public "left behind" verdict per week,
  on the site and as the digest's shareable teaser
- First step: surface the newest deprecated claim with its evidence as
  a home-page card
- Cost: $0
- Status: proposed

### 2026-09-18 — Agent-readable public surface: llms.txt and a skills manifest (market agent)
- Trigger: the skills standard's own site ships an llms.txt index for
  machine readers (agentskills.io), and the fourth customer segment is
  agents consuming what humans pay for (report-2026-09.md §3)
- What: publish llms.txt plus a machine-readable manifest of public
  skill metadata so agents can discover the library and route their
  owners to the paywall
- First step: static llms.txt and a JSON route listing skill names,
  descriptions, and provenance summaries
- Cost: $0
- Status: proposed

### 2026-09-18 — A published head-to-head: alexandria skill vs free marketplace skill (market agent)
- Trigger: for the $30 tier the report concludes a stranger needs one
  public demonstration of measurable gain before paying, and the
  harness-engineering skill already has an internal A/B result that was
  never published (skills/harness-engineering/SKILL.md provenance)
- What: run one task with and without the alexandria skill against a
  comparable free directory skill, publish method and numbers on the
  site, win or lose
- First step: rerun the existing harness-engineering A/B with a written
  protocol and a third condition using a popular free skill
- Cost: $0 within existing model budgets
- Status: proposed
