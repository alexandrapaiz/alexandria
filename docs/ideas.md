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
