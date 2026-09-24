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
- Done this run (skill agent, 2026-09-18, PR skill/2026-09-18-production-line):
  `prompts/skill-extract.md` is written, but not yet drafted against a real
  claim cluster as planned, because `NEON_RO_URL` had no usable value this
  run (see the urgent ledger entry below) — the "first step" above still
  stands for next Tuesday. One resolved ambiguity worth recording: the
  charter (prompts/skill-agent.md) says "every claim-backed sentence citing
  its claim id," but the gold specimen actually cites by paper title inline
  ("(Co-Evolving Harnesses and Models)") and keeps numeric ids only in
  `provenance.claims`. skill-extract.md now codifies the specimen's
  approach as the rule: paper-title citation in prose, numeric ids in
  frontmatter for the provenance reviewer to check against the database.
  Inline numeric ids would make the prose unreadable without making it any
  more checkable, since the reviewer needs the stable id either way.
- Done this run (skill agent, 2026-09-18, PR skill/2026-09-18-b-self-improving-post-training-loops):
  the "first step" above is now done. `prompts/skill-extract.md` itself is
  still only on the still-open PR #12 branch
  (`skill/2026-09-18-production-line`), not yet merged to main, so this run
  followed that branch's version as the extraction method rather than
  re-proposing a second copy of the same new file in this PR. It held up
  well end to end: the cluster-scoring criteria (procedure-rich,
  cross-supported, on-topic, not-already-gold) picked out a real 5-paper,
  21-claim cluster on self-improving post-training loops with genuine
  supports/refines edges between all five papers, not just topic-tag
  overlap, and the frontmatter/citation split (paper title in prose,
  numeric id only in `provenance.claims`) worked cleanly against a second
  real skill. One friction point worth a note for whoever finalizes
  skill-extract.md: several of the strongest-looking supports edges by
  confidence score (0.6-0.85) connected claims that were topically
  unrelated in substance despite the topic-tag overlap the query filtered
  on (e.g. a safety-tuning claim and a TPU-kernel-optimization claim both
  "supporting" an unrelated search-agent claim); the prompt's cluster-
  scoring section should say explicitly that an edge's existence and
  confidence score are necessary but not sufficient, and that the drafting
  agent must read the actual claim text of every edge before trusting it,
  not just the edge table.

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
- Status: rejected
- Owner verdict 2026-09-18: rejected for Q4 by the skills-focus decision (all-hands decision 6). Not current work; may be re-proposed after Q4.

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
- Status: rejected
- Owner verdict 2026-09-18: rejected for Q4 by the skills-focus decision (all-hands decision 6). Not current work; may be re-proposed after Q4.

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
- Status: rejected
- Owner verdict 2026-09-18: rejected for Q4 by the skills-focus decision (all-hands decision 6). Not current work; may be re-proposed after Q4.

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
- Cost: $0 to build; a metered API is a pricing proposal for the owner
- Status: rejected
- Owner verdict 2026-09-18: rejected for Q4 by the skills-focus decision (all-hands decision 6). Not current work; may be re-proposed after Q4.

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
- Status: rejected
- Owner verdict 2026-09-18: rejected for Q4 by the skills-focus decision (all-hands decision 6). Not current work; may be re-proposed after Q4.

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
- Grooming note (PM, 2026-09-18): cut from sprint-2026-09-21 revision 2
  under the product-first re-triage (incident 12, all-hands decision
  11). Still accepted-in-spirit and correct, but it does not move the
  score the release gate now measures, so it carries to a future sprint
  rather than competing with this week's digest and skills quality work.
  It is also the fix for one of the coming-soon surfaces named in
  docs/sprints/pending.md's audit (`/pricing`'s two dead "Coming soon"
  pills), worth remembering when it is picked back up.

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
- Grooming note (PM, 2026-09-18): cut from sprint-2026-09-21 revision 2
  under the product-first re-triage (incident 12, all-hands decision
  11), same reasoning as "Email capture before payments exist" above.
  Carries to a future sprint.

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
- Grooming note (skill agent, 2026-09-18): "parseSkill already reads
  frontmatter" is not quite true for this field, verified against the gold
  specimen this run. `site/lib/content.js`'s `get(key)` regex
  (`^${key}:\s*(.+)$`) requires the key at column 0; `validated` and
  `claims` both sit indented under `provenance:` in the gold specimen, so
  `get("validated")` and `get("claims")` both return `""` today, confirmed
  by running `parseSkill` against `skills/harness-engineering/SKILL.md`
  directly (papers still parses fine, since its list-item regex doesn't
  care about the parent key). This is the same gap the "receipt-rendering
  schema" entry below covers in full; that entry is the fuller fix,
  this note just pins the exact bug for whichever engineer run picks
  either one up first.

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
- Status: accepted
- Groomed 2026-09-18 (PM, closing all-hands triage): accepted. Sales'
  redispatched plan (PR #22, merged) independently proposes a
  "Left-Behind Index" public page (see that entry under "Sales agent
  proposals" below) as a lane-C gate for two already-drafted outreach
  notes, and the sales floor statement at the 2026-09-18 closing
  all-hands asked the owner to greenlight it. This is a product/backlog
  call, not money, a secret, or purpose, so it is decidable under
  standing liberty (all-hands decision 4) rather than owner-only.
  Accepting this entry (the weekly public verdict) covers the same
  ground sales' page-shaped version needs; treat that entry as the same
  accepted idea rather than a second build. Not yet carded into a
  specific sprint; the first step above (one home-page card from the
  newest deprecated claim) is
  small enough to fold into whichever sprint has a spare slot, and
  directly serves the two gated outreach notes sales is waiting on.

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
- Status: built
- Owner outcome 2026-09-18, final after a full brainstorm: the mission is
  "Accelerate every builder to frontier speed." alone, everywhere, no
  subtitle or companion line (one was considered and deleted).
  Recorded at the top of vision.md §0. This entry is done.
- Status: proposed

## Security agent findings (first run, 2026-09-18)

Full report at docs/security/audit-2026-09-18.md. The three below are
`urgent` because each needs an owner decision or action, not an engineer
build.

### 2026-09-18 — MCP OAuth: redirect_uri not validated against registration (security agent)

- Trigger: OAuth flow review of mcp/server.py per this seat's charter.
- What: `/register` (server.py:277) issues a client_id but never persists
  the submitted `redirect_uris`. `/authorize` (server.py:301-330) then
  accepts any `redirect_uri` from the request with no check against what
  was registered, and redirects the signed authorization code there once
  the passphrase is entered. PKCE does not close this: an attacker who
  crafts the entire authorize link (their own redirect_uri and
  code_challenge) legitimately holds the matching code_verifier, so a
  phishing link on the real domain that gets the real passphrase typed
  into it hands the attacker a working access+refresh token pair with
  full MCP tool access, including the PR-authority tools.
- First step: persist client_id to redirect_uris at `/register` (signed
  token or a small store) and reject `/authorize` or `/token` calls whose
  redirect_uri does not match. Needs a real test against a live Modal
  deployment before shipping, which this run could not do.
- Cost: $0
- Status: urgent

### 2026-09-18 — Public git history still holds a full pre-privacy-pivot digest (security agent)

- Trigger: public/private boundary check across full git history (this
  repo is public on GitHub).
- What: digests/2026-W37.md was committed nine times (2026-09-08 through
  the "digests go private" commit) before the folder was gitignored. The
  file is no longer tracked on main, but every historical version,
  including the full digest text, is still retrievable by anyone who
  clones the public repo (`git show <commit>:digests/2026-W37.md`). This
  is the paid product's actual content sitting in public history ahead of
  the Oct 13 launch.
- First step: the owner decides whether to rewrite history (BFG /
  `git filter-repo`) to purge the blob, weighed against the disruption
  (force-push, breaks the two branches currently ahead of main and any
  existing clones/forks) versus leaving it and accepting the exposure.
  This agent does not rewrite history or force-push on its own authority.
- Cost: $0
- Status: urgent

### 2026-09-18 — Grant the GitHub App the `workflows` permission, or accept no agent can fix workflow files (security agent)

- Trigger: pushing this run's branch with a workflow-file fix (pinning
  actions/checkout and anthropics/claude-code-action to resolved SHAs,
  see the next section) was rejected by GitHub: "refusing to allow a
  GitHub App to create or update workflow
  `.github/workflows/agent-engineer.yml` without `workflows` permission."
  That is a GitHub App installation permission, separate from each
  workflow's own `permissions:` block, and none of the six workflows
  request `workflows: write` either, so no seat's token can land a
  workflow-file change today, including ExO's, whose charter explicitly
  names agent workflows as writable.
- What: the owner decides whether to grant the GitHub App installation
  the `workflows` permission so an agent (this one, or ExO per its
  charter) can push a workflow-file fix directly, or to keep workflow
  edits owner-only and treat every future finding in this category as a
  ledger entry the owner applies by hand. Either is a real choice about
  how much authority this class of change should have, not an oversight
  to just fix.
- First step: the owner's call. If she grants it, the pinning fix in the
  next entry is ready to apply verbatim.
- Cost: $0
- Status: urgent

## Security agent proposals (first run, 2026-09-18)

### 2026-09-18 — Pin actions/checkout and claude-code-action to resolved SHAs (security agent)

- Trigger: both `actions/checkout@v4` and `anthropics/claude-code-action@v1`
  in all six `agent-*.yml` workflows are floating major-version tags, not
  immutable references. Whoever controls the tag controls what code runs
  in every future scheduled or dispatched run. This is the fix this run
  prepared and verified but could not push (see the `workflows`
  permission entry above).
- What: replace `uses: actions/checkout@v4` with
  `uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4.4.0`
  and `uses: anthropics/claude-code-action@v1` with
  `uses: anthropics/claude-code-action@a4f54ef2c58884867281bd8e2f8d63352ad019a9 # v1.0.229`
  in all six workflow files. Verified tonight that both SHAs are exactly
  what the tags already resolve to, so this changes nothing about current
  behavior. Trade-off to weigh: pinning trades away automatic upstream
  fixes, and claude-code-action's v1 tag moved as recently as tonight, so
  whoever applies this should plan to re-check the SHA periodically
  (a natural fit for this seat's biweekly cadence) or use Dependabot's
  GitHub Actions update support instead.
- First step: apply the two substitutions above across the six files, or
  wait for the `workflows` permission decision.
- Cost: $0
- Status: proposed

### 2026-09-18 — Verify pipeline/weekly.py's Gmail secret name against Modal before wiring it live (security agent)

- Trigger: `weekly()`'s decorator requests two Modal secrets, `Gmail`
  (capital G) and `gmail_pass`, while the function's own docstring
  describes one combined secret it calls "the gmail secret." Unlike
  `neon`/`groq`, which are single lowercase secrets used consistently
  everywhere, this pairing does not match any pattern used elsewhere in
  the pipeline. Could not verify against the actual Modal secret store
  from this session.
- What: before the owner creates the real Gmail secret(s) in Modal,
  confirm the name(s) `pipeline/weekly.py` expects and either fix the
  code to request one `gmail` secret (matching the neon/groq pattern) or
  fix the docstring to match two secrets, whichever is actually true.
- First step: check what's created in the Modal secret dashboard, or the
  owner's preference, before the newsletter send goes live.
- Cost: $0
- Status: proposed

### 2026-09-18 — Confirm interpret.py's neighbor query casts the embedding parameter (security agent)

- Trigger: `interpret.py`'s nearest-neighbor query passes a claim's
  `embedding` value, read back from Postgres with no pgvector adapter
  registered, straight into `order by embedding <=> %s` with no explicit
  `::vector` cast on the parameter. `distill.py`'s writes always cast
  (`%s::vector`), and this read path doesn't. Could not verify against a
  live pgvector database from this session, so this may already work
  fine depending on how psycopg3 types the round-tripped value.
- What: run interpret.py once against a real database and confirm the
  neighbor query executes without a cast or type error. If it errors,
  add `%s::vector`.
- First step: a single live run of the interpret step with logging on the
  neighbor query.
- Cost: $0
- Status: proposed

### 2026-09-18 — Pin the open-ended Python dependency floors (security agent)

- Trigger: dependency audit found several unpinned or open-ended
  requirements: `modal>=1.5` (root requirements.txt), and in
  `mcp/server.py`'s inline `pip_install`, `pyjwt>=2.9` and
  `fastapi>=0.115`. `sentence-transformers` (used by distill.py) carries
  no version pin at all and pulls in unconstrained `transformers`/`torch`.
  No currently known CVE was confirmed against the exact resolved
  versions, but open floors mean a future `pip install` can silently pick
  up a different, unreviewed version, which matters most for `pyjwt`
  since it signs the MCP server's own auth tokens.
- What: pin `pyjwt` to `>=2.12,<3` (guarantees the `crit`-header
  validation fix), add an upper bound to `fastapi`, and pin
  `sentence-transformers`/`transformers` to tested versions.
- First step: pin `pyjwt` first, since it's the security-relevant one,
  then test the MCP server still deploys and authenticates after the bump.
- Cost: $0
- Status: proposed

### 2026-09-18 — Automate the weekly meta-review seat (engineer agent)
- Trigger: writing docs/product/source-discovery.md (owner's discovery
  addendum) meant tracing where Step 4 of prompts/weekly-agent.md
  (the ADR-12 meta-review, now also this doc's discovery step) actually
  runs. It doesn't: README's status checklist still carries "Claude
  weekly agent scheduled task" unchecked, and unlike engineer, PM,
  market, OKR, security, exo, and skill, there is no `agent-weekly.yml`
  in .github/workflows/. Step 3 (skill authoring) was superseded by the
  dedicated skill agent (ADR-22); Step 4 has no seat at all
- What: add `agent-weekly.yml` on the pattern the other seven seats
  already use, running prompts/weekly-agent.md with direct database
  access the way skill-agent.md already does (NEON_RO_URL, psql)
  instead of depending on the MCP server's human-oriented OAuth login,
  which was designed for the owner's own claude.ai connector, not a bot
- First step: stand up the workflow file and a Sunday or Monday
  schedule (before or after the PM's Monday grooming), pointed at the
  existing charter unchanged; confirm Step 4's propose_change calls
  work the same way gh pr create already does for every other seat
- Cost: $0
- Status: proposed

### 2026-09-18 — Store each paper's arXiv category (engineer agent)
- Trigger: same doc. The arXiv firehose can only ever confirm categories
  already listed in sources.yaml, by construction, so it can never
  discover that an untracked category now matters. hf_daily_papers is
  the one source we ingest that isn't category-filtered, but papers has
  no category column, so a paper landing there from an uncovered
  category leaves no trace to query against
- What: add `category text` to papers, populated in ingest.py's
  fetch_arxiv (from the source category) and fetch_hf_daily (from the
  arXiv id's primary category, one extra field already in HF's payload)
- First step: the schema migration plus the two ingest.py call sites;
  a follow-up query (repeated hf-daily hits in an uncovered category)
  is the actual discovery signal and can wait for a few weeks of data
- Cost: $0
- Status: proposed

### 2026-09-18 — sources.yaml watchlist for authors and institutions (engineer agent)
- Trigger: same doc. discovery_report's rising_authors and
  rising_institutions signals (mcp/server.py) often name a researcher
  or lab with no blog or RSS feed to add as a `feeds:` entry — the
  current schema (arxiv categories + feeds only) has no way to
  represent "watch this person or lab" directly, so today those
  findings can only become a ledger note, not a structural change
- What: a `watchlist: {authors: [...], institutions: [...]}` block in
  sources.yaml; triage.py applies a tier-b-equivalent prior when a
  paper's authors or institutions match an entry, even before a
  dedicated feed exists for them
- First step: the sources.yaml schema addition plus the triage.py
  lookup, proposed together so the field is never dead configuration
- Cost: $0
- Status: proposed

### 2026-09-18 — Unified traction-confidence score for discovery_report (engineer agent)
- Trigger: owner's architecture-run directive to build on
  docs/product/source-discovery.md so the pipeline "reliably catches
  what is genuinely gaining traction." Today discovery_report returns
  three independent signals (embedding-space novelty, rising
  authors/institutions, citation velocity from an untrusted tier); a
  candidate that clears two signals at once is stronger evidence than
  one that clears either alone, but nothing computes that today — a
  human or the weekly agent has to hold three lists in their head and
  cross-reference by hand
- What: fuse the three discovery_report signals into one ranked score
  per candidate (paper, author, or institution), returned as a single
  ordered list showing which signals fired and by how much, so
  independent agreement across signals — the evidence bar
  source-discovery.md §5 already requires — is a number in the
  propose_change rationale instead of an implicit read
- First step: define the scoring function against the three existing
  queries in mcp/server.py's discovery_report (no new data collection,
  pure recombination of what it already returns)
- Cost: $0
- Status: proposed

### 2026-09-18 — Discovery precision audit: track discovery→diff→outcome (engineer agent)
- Trigger: same directive. "Reliably catches" is a claim about
  precision that nothing today measures — every discovery_report
  finding that becomes an accepted sources.yaml diff via propose_change
  is untracked once merged, so there is no way to say whether the
  signal was actually right
- What: tag the promotions row (kind = 'system_diff') that originated
  from a discovery_report finding, then a few weeks later check whether
  that source's subsequent papers cleared triage at a materially higher
  rate than the corpus baseline — the same measured-before-trusted
  method as the distill bake-off (docs/evals/2026-09-07-distill-bakeoff.json),
  applied to the discovery signal instead of a model choice
- First step: add the tag at propose_change time (a note in the
  rationale is enough, no schema change required yet), then design the
  follow-up query once a few tagged diffs exist to check against
- Cost: $0
- Status: proposed

### 2026-09-18 — Executable trigger tests for skills, checked in CI (engineer agent)
- Trigger: ADR-22 already requires five prompts (three should fire, two
  shouldn't) narrated in every skill-agent PR body, answering the
  market audit's "69% of public skills won't reliably trigger" finding.
  A narrated PR description is evidence for a human reader the day it's
  written; it is not a check that runs, and it goes stale silently the
  moment a skill's `description:` frontmatter is edited later without
  anyone re-running the five prompts by hand
- What: a `skills/<slug>/trigger-test.json` fixture per skill (the same
  five prompts, structured as prompt text + expected fire/no-fire), plus
  a small script that checks a skill's activation-condition text against
  its fixture, run in CI on any change under skills/ — the reviewer
  panel's future adversary/provenance checks stay judgment calls; this
  is the one piece of ADR-22's requirement that is mechanical enough to
  automate outright
- First step: convert skills/harness-engineering's existing (narrated,
  in its promotion PR) five prompts into the first trigger-test.json, as
  the worked example before asking the skill agent to produce one every
  week going forward
- Cost: $0
- Status: proposed

### 2026-09-18 — Self-application step for prompts/weekly-agent.md (engineer agent, charter-text proposal)
- Trigger: owner's architecture-run directive, verbatim: "the big things
  that we research, let's build" — findings in our own claim graph
  (harness patterns, loop designs, orchestration techniques) should
  change our own pipeline and agents, not only get written up for
  someone else to load. Today that only happens when a human happens to
  notice the resemblance while reading; docs/product/architecture-next.md
  §3 designs the mechanism in full, with three worked examples against
  the one skill already in gold
- What: this ledger entry carries the exact step to add to
  prompts/weekly-agent.md's Step 4 (meta-review), which already runs
  weekly via agent-weekly.yml and already holds propose_change
  authority: after gathering the week's evidence, ask whether any
  finding, applied to alexandria's own prompts/pipeline/agent design,
  predicts a concrete nameable change (name the file and the practice
  it contradicts or improves, not a resemblance). A prompt/sources.yaml-
  shaped answer calls propose_change directly, citing the claim ids,
  exactly as Step 4 already does for any other finding. A pipeline-code-
  shaped answer becomes a ledger entry tagged `self-application` for the
  engineer's next run. No new cron, tool, or secret — reuses the
  meta-review step and the ADR-12 channel that already exist
- First step: this is charter text, not code — prompts/weekly-agent.md is
  an agent charter, which per ADR-19 only the ExO edits (gated by the
  owner's merge like every charter change). The engineer cannot commit
  this directly; the owner or the ExO's next run applies the step above
  verbatim or edited, into Step 4
- Cost: $0
- Status: proposed

### 2026-09-18 — Self-application example: sample-and-select bake-off for distill.py (engineer agent)
- Trigger: docs/product/architecture-next.md §3.2, example 1 — the one
  skill already in gold cites its own headline finding (claim 203,
  "What Else Needs Fixing?"): best-of-three parallel sampling with a
  cheap selection step beat sequential self-reflection by 2.2-9.7% for
  less compute. distill.py samples once per paper today; the skill's
  own procedure, applied to the pipeline that produced it, predicts a
  concrete change
- What: sample distillation 2-3 times per paper on the same free-tier
  Groq model (still $0 — more calls against the same free budget, not a
  new one), embed each candidate's extracted claims, and select the
  medoid (or use an LLM judge with 2 samples) before writing to silver,
  on the bet that it reduces missed or hallucinated claims the same way
  it improved accuracy in the source paper
- First step: a measured blind comparison against the current
  single-sample baseline on a fixed set of papers, same method as the
  2026-09-07 distill bake-off, before changing production behavior —
  do not ship this on the skill's say-so alone; measure it the way the
  house style already requires
- Cost: $0 to test (same free-tier budget, more calls per paper — watch
  the daily rate limit)
- Status: proposed

### 2026-09-18 — Repeatable prose benchmark: blind read test against that week's TLDR issue (engineer agent)
- Trigger: owner's finding that the digest reads stale and mechanical
  despite improvement, and her directive that digest quality get
  measured, not vibed, per the market seat's blind-pairwise-comparison
  method already established for model choices (the distill bake-off,
  docs/evals/2026-09-07-distill-bakeoff.json) and proposed again for a
  future skill head-to-head (docs/ideas.md, "A published head-to-head")
- What: a repeatable weekly or biweekly check — take alexandria's digest
  opening plus its top Trailblazing item and a comparably-scoped section
  of that week's TLDR AI issue, strip both of branding, and have blind
  readers (the comped friends list first, before any wider readership
  exists) score prose quality only — clarity, whether it reads as
  written by a person versus a template, whether the point lands without
  rereading — with no visibility into which is which. Track the score as
  a trendline the way the OKR check-in tracks everything else, so
  "less mechanical" becomes a number over successive issues instead of
  an impression
- First step: write the one-page rubric (3-4 questions, same shape as
  the distill bake-off's pairwise grading) and run it once, by hand,
  against the next issue and that week's TLDR AI issue, before proposing
  any automation around it
- Cost: $0 (uses the existing comped friends list; no new tool or panel)
- Status: proposed
- Grooming note (PM, 2026-09-18): picked up as sprint-2026-09-21 revision
  2's item 1, per the product-first re-triage (incident 12, all-hands
  decision 11). Run it for real this sprint, filed in docs/evals/, not
  deferred again.

### 2026-09-18 — NEON_RO_URL has no usable value this run (skill agent)
- Trigger: this run's step 1, picking a claim cluster. The PM's board
  already carries "the NEON_RO_URL secret for the skill agent" as an
  owner-logistics card, and this run's dispatch stated the secret is now
  set. It is present as an environment variable name but its value is
  empty: `psql "$NEON_RO_URL" -c "select 1;"` fails immediately trying a
  local unix socket, the shape of error `psql` gives an empty connection
  string, not a network or auth error. Ruled out sandboxing as the cause:
  `getent hosts neon.tech` resolves fine, so egress works and the failure
  is specific to the secret's value.
- What: the owner or engineer should re-check the `NEON_RO_URL` repo
  secret's actual stored value (GitHub masks secret values in the UI, so a
  blank paste is easy to miss) and re-save it. Until fixed, every
  Tuesday run of this agent and the newly-added weekly agent
  (agent-weekly.yml, also reads `NEON_RO_URL`) will silently degrade to
  the no-database fallback path, which blocks O2 KR2 (docs/okrs/okrs-2026-Q4.md,
  "at least one draft skill per week from claim clusters from 2026-11-01
  onward") before that window even opens.
- First step: `gh secret list` confirms the secret exists by name only
  (GitHub never exposes values via the API either); the owner needs to
  re-enter the value directly in the repo settings UI, then any agent run
  can re-verify with the same psql one-liner above.
- Cost: $0
- Status: urgent

### 2026-09-18 — Receipt-rendering schema for the skill library (skill agent)
- Trigger: O2 ("Make the skill library a real asset") and the composed
  product thesis ("skills with receipts," docs/allhands/2026-09-17.md
  decision 6) both depend on the claim ids and validation evidence in a
  skill's frontmatter actually reaching the site. Verified this run that
  they currently do not (see the grooming note on "Show each skill's
  validation evidence on its page" above): `site/lib/content.js`'s
  `parseSkill` is a flat-line regex parser, blind to anything nested
  under `provenance:`, and has no extraction for `provenance.claims` at
  all, only `papers`.
- What: replace the hand-rolled regex parser with a real YAML frontmatter
  parse (any small `js-yaml`-class dependency, or a hand-written nested
  parser if the site wants to stay dependency-free), and extend the
  skill-card data shape to carry, per skill: `extracted` date, `validated`
  string (empty = not yet promoted), `claims` (the id list, count is
  `claims.length`), and `papers` (already parsed). This is the minimum
  schema the verification-badge entry below needs as its data source; the
  two are one piece of work split for review size, not two independent
  builds. This entry supersedes "parseSkill already reads frontmatter" as
  the first step on the validation-evidence entry above — it does not yet,
  this is now the fix.
- First step: swap the regex parser for real nested-YAML parsing first
  (a pure bugfix, testable against the one gold specimen on disk today),
  then extend `Skills` in `site/lib/content.js` and the skill-card
  component to surface the new fields; the card's visual design is the
  market/engineer seats' call, not this agent's.
- Cost: $0 (a small parsing dependency at most)
- Status: proposed
- Grooming note (PM, 2026-09-18): picked up as sprint-2026-09-21 revision
  2's item 5, per the product-first re-triage (incident 12, all-hands
  decision 11). This is the sprint's one kept piece of site plumbing,
  kept because the digest and skills quality work in items 1 through 4
  is invisible to a stranger until it renders.

### 2026-09-18 — Verification badge data schema (skill agent)
- Trigger: docs/market/opportunities-2026-09-18.md's badge proposal
  ("verified against N sources, confidence X," directly answering the
  Show HN finding that 69% of public skills won't reliably trigger) is
  accepted in principle (see "Skill-verification badge on every library
  entry" above, proposed 2026-09-18) but has no defined data shape yet.
  Drafting prompts/skill-extract.md this run required deciding exactly
  what a draft skill's frontmatter can and cannot honestly claim before
  the panel has run, which is the same question the badge needs answered.
- What: define the badge as four fields, all derivable from data this
  system already produces and none inventable by an agent drafting a
  skill:
  - `source_count` — `provenance.papers.length`, already on every skill.
  - `claim_count` — `provenance.claims.length`, needs the parser fix
    above to reach the site.
  - `validated` — boolean plus the recorded trial sentence, true only
    once `provenance.validated` is non-empty; a drafted-but-unpromoted
    skill (this run's fallback state, and any future draft still awaiting
    the ADR-13 panel) must render as "pending validation," never as a
    silent false or a blank, so a prospect never mistakes a draft for a
    proven skill.
  - `trigger_reliability` — not yet computable from anything the system
    tracks today. The honest options are (a) leave it out of v1 and ship
    only the three fields above, or (b) the panel logs whether each
    trigger-test prompt in the skill's PR actually activated the skill
    when replayed, and the badge shows a fraction (e.g. "3/3 positive
    triggers confirmed"). Recommend (b), since it reuses the trigger test
    prompts/skill-agent.md already requires in every PR rather than
    inventing new measurement machinery, but flagging both options for
    the engineer and panel-builder to weigh, since (b) depends on the
    still-unbuilt ADR-13 panel actually replaying the trigger prompts.
- First step: ship the three data-backed fields first (needs only the
  parser fix above), land `trigger_reliability` as a fast-follow once the
  panel exists to compute it.
- Cost: $0
- Status: proposed
- Grooming note (PM, 2026-09-18): the three data-backed fields ride along
  with sprint-2026-09-21 revision 2's item 5 (same reasoning as the
  receipt-rendering entry above); `trigger_reliability` still waits on
  the ADR-13 panel or an equivalent honest check, per its own note here.

### 2026-09-18 — The skills production line, sequenced end to end (skill agent)
- Trigger: the owner's directive that skills are the selling point and
  the team is "far behind on them," and that this run should propose
  "the skills production line done right." Four pieces of it already
  exist as separate ledger entries (skill-extract prompt, receipt
  rendering, verification badge, ADR-13 panel); none of them names the
  order they need to land in or who is blocked on whom.
- What: the dependency order, as this run's extraction work surfaced it:
  1. `NEON_RO_URL` fixed (urgent entry above) — nothing downstream runs
     without it.
  2. `prompts/skill-extract.md` (this run, done) — the extraction method.
  3. One real draft skill through this agent's normal weekly cadence,
     once (1) is fixed — proves the prompt against real data, which this
     run could not do.
  4. The ADR-13 panel, validator reviewer first per the PM's resequencing
     (docs/backlog.md item 4) — a draft sitting in `status: active` with
     an empty `validated` field is not yet a promoted skill, and the
     badge schema above depends on the panel actually running to ever
     show `validated: true` on anything.
  5. The parser fix + badge fields (both entries above) — can build in
     parallel with (3)-(4) since it only needs the one gold specimen
     already on disk to develop and test against, but the badge's
     `validated` field only ever shows real data once (4) exists.
  6. `trigger_reliability` (badge entry, option b) — depends on (4)
     existing to replay trigger prompts.
  The current state of every draft skill until (4) ships: `status:
  active` but not panel-reviewed. Recommend the site never call an
  unpromoted draft "verified" regardless of its `status` field — gate the
  badge's verified state on `validated` being non-empty, not on the
  skill file merely existing in `skills/`, so an unreviewed draft never
  reads as a receipt it hasn't earned.
- First step: none — this is a sequencing map for the engineer, PM, and
  next skill-agent runs to read before picking up any one piece, not a
  build task itself.
- Cost: $0
- Status: proposed
### 2026-09-18 — Knowledge graph upgraded to industry standard
- Trigger: owner's directive, verbatim: "the knowledge graph needs
  maintenance and to be upgraded to be industry standard right now it's
  very junior and behind and prehistoric and almost like a toy"
- What: the claim graph grows up. Audit the current edges table against
  industry practice (GraphRAG-class systems, entity resolution and
  dedup, calibrated edge confidence, richer relation semantics, the
  slow-loop re-judgment ADR-10 promised but never built, graph quality
  metrics tracked over time), design the upgrade, and build it in
  day-sized slices. ADR-10's escalation ladder (Apache AGE, Neo4j)
  is on the table if the evidence justifies it, but the first gains
  are likely in edge quality, not storage engine.
- First step: a graph-quality audit with metrics (edge precision on a
  sample, duplicate rate, contradiction coverage) and an upgrade design
  doc, engineer seat
- Cost: $0
- Status: accepted

### 2026-09-18 — Digest issue permalinks with real share meta tags (sales agent)
- Trigger: building the launch campaign (docs/sales/, ADR-24) surfaced
  the cheapest available growth loop and found it structurally blocked:
  the digest archive currently renders empty (docs/market/report-2026-09.md
  §6), so there is no per-issue URL to share, and no digest issue can
  become its own acquisition surface the way every comped competitor's
  archive does.
- What: once the archive renders real content, give each issue a stable
  permalink with correct social meta tags (title, description, maybe an
  OG image), and put a plain "share this issue" link on the issue page.
  This is the highest-leverage cheap mechanic in the whole campaign
  (docs/sales/launch/referral.md) because it costs a subscriber nothing
  and turns every good issue into distribution without any outreach.
- First step: confirm the archive-rendering fix (already tracked in
  docs/backlog.md's launch runway table) lands, then add per-issue meta
  tags on top of it — small enough to fold into that same fix rather
  than a separate sprint item.
- Cost: $0
- Status: proposed
### 2026-09-18 — Corpus expansion scoping spike (Q4) and Q1 objective
- Trigger: owner's directive to cover everything related to building in
  the AI age, adopted with the three seats' guardrails (all-hands
  decision 10): scope = only findings that carry cited evidence and
  ship as directly usable tools, never stories.
- What: the Q4 day-sized spike from the engineer's consultation: an
  evidence_grade column on claims set at distill so anecdotes and
  peer-reviewed results never mix silently, five engineering-blog
  feeds added to sources.yaml, and a practices variant of
  prompts/distill.md that asks what they did, why, and what broke.
  Full expansion (repo design docs, talks, handbooks) is a Q1 2027
  objective behind the OKR seat's three gates.
- First step: the evidence_grade migration and one blog feed, engineer
- Cost: $0
- Status: accepted

### 2026-09-18 — A public, read-only, cited claims endpoint (sales agent)
- Trigger: the GEO plan (docs/sales/geo-plan.md, Game 2) and the board's
  "Define alexandria's distribution system (Thiel)" directive both need
  a claim-graph surface an outside agent can query without the owner's
  own credentials. Today the only way to read real claim text is the
  MCP server's authenticated tools (ADR-11), built for one user's agent,
  not a public surface — the graph's own site page ships a hardcoded
  structure-only snapshot with claim text deliberately withheld
- What: a narrow, unauthenticated `GET` route (e.g. `/api/claims/{id}`)
  returning a claim's text, evidence, and supports/contradicts counts,
  scoped to matured or deprecated claims only — never anything still
  paywalled or in-progress, never a bulk graph dump
- First step: pick the claim-status filter (matured/deprecated only) and
  ship one route against one claim before generalizing
- Cost: $0
- Status: proposed

### 2026-09-18 — A public, read-only MCP surface, scoped and separate from the owner's authenticated layer (sales agent)
- Trigger: same GEO plan (docs/sales/geo-plan.md, Game 2) and 2026-09-web
  research showing MCP already functions as "the front door" for
  agent-native infrastructure companies (Firecrawl, Browserbase, Exa,
  Mem0). Alexandria's existing MCP server (ADR-11, `mcp/server.py`) is
  real and deployed but sits entirely behind the owner's own OAuth 2.1
  passphrase — built for her agent, not for outside agents to query
- What: a second, read-only MCP surface exposing `semantic_search` and
  `rag_answer` against the same matured/deprecated claim set as the
  claims-endpoint item above, no auth required, returning the same
  `[C<id>]`-cited answer format `rag_answer` already produces
  internally. The owner's existing authenticated MCP layer is untouched
  — this is an additive, narrowly scoped surface, not a loosening of it
- First step: confirm the read-only scope excludes anything paywalled or
  still in-progress before writing a single route, then reuse the
  existing `semantic_search`/`rag_answer` logic against that filtered set
- Cost: $0
- Status: proposed
## Skill agent findings (2026-09-18)

### 2026-09-18 — NEON_RO_URL fixed, connection verified (skill agent)
- Trigger: resolves the urgent entry "NEON_RO_URL has no usable value this
  run," filed against the prior skill-agent run in the still-open PR #12
  (`skill/2026-09-18-production-line`). That run found the secret present
  as an environment variable name but empty in value.
- What: this run's dispatch stated the owner had re-entered the secret.
  Verified as the first action before anything else: `psql "$NEON_RO_URL"
  -c 'select count(*) from claims;'` returned `441` with no error, so the
  read-only connection works end to end. This run went on to query
  `claims`, `claim_links`, `papers`, and `promotions` directly and drafted
  a real skill against a live cluster
  (`skills/self-improving-post-training-loops/SKILL.md`), which the prior
  run could not do. O2 KR2's "at least one draft skill per week from claim
  clusters" is unblocked as of this dispatch.
- First step: none remaining on this finding. The one-liner above is the
  standing re-verification check for any future run that hits the same
  failure mode.
- Cost: $0
- Status: built

## Frontend agent findings (2026-09-18)

### 2026-09-18 — The skills page shows agents' routing text to people (frontend agent)
- Trigger: the copy pass this run rewrote every line the site owns, and
  then hit the two lines it does not. `/skills` renders each skill's
  `description` from its `SKILL.md` frontmatter, and that field is written
  for an agent's router, not for a reader. On the page it comes out as
  "Evidence-backed practices for designing, improving, and debugging agent
  harnesses (the scaffold around a model - tools, prompts, loop structure,
  feedback). Use when building an agent or multi-agent system, when an
  agent underperforms and the cause is unclear, when ..." and runs for
  eight lines of "use when" clauses. The second card's text carries a
  semicolon join, which the house voice does not allow. It is the longest
  block of prose on the page and the worst-written text on the site.
- What: give each skill a second frontmatter field, a one-sentence
  `summary` for people, and have `site/app/skills/page.jsx` render that
  and keep `description` for routing. Both audiences then get text aimed
  at them, and the trigger test in `skills/_validation/` keeps scoring the
  field it already scores.
- Why this run did not simply make the edit: `skills/` is outside the
  frontend lane by the charter, and the `description` field is the exact
  string the trigger test measures, so editing it from this seat would
  move a number another seat owns.
- First step: the skill seat adds `summary` to the two gold skills, then
  one line changes in the skills page. The page falls back to
  `description` when `summary` is absent, so the two can land in either
  order.
- Cost: $0
- Status: proposed

### 2026-09-18 — Confirm or reject renaming "the spine" for visitors (frontend agent)
- Trigger: the owner's copy order for this run bans buzzwords and asks
  that the site sell the product rather than the recipe. "The spine" is
  the owner's own word from the 2026-09-17 all-hands, and it is the right
  word internally, but on the site it was the name of the paid tier and
  the subject of four gate messages, and it tells a first-time visitor
  nothing about what they would be paying for. This run renamed the tier
  to "Full access" and rewrote the gates to say "the paid plan", which is
  a naming decision above this seat.
- What: the owner keeps "Full access" or restores "The spine". If it is
  restored, the tier needs a subtitle that says what it contains, because
  the word alone does not carry it.
- First step: one word in `site/app/pricing/page.jsx` and one phrase each
  in the skills, graph and routines gates plus the issue foot. Reverting
  is a five-line diff either way.
- Cost: $0
- Status: proposed

### 2026-09-18 — The digest's own text says "ingested" where the site now says "read" (frontend agent)
- Trigger: the home page's metric line was changed this run from "papers
  ingested this week" to "papers read this week", because "ingested" is
  pipeline vocabulary and a reader does not use it. The digest itself
  still ends with "3431 papers ingested / 216 claims distilled / 80 edges
  drawn this week", which is written by the weekly agent and rendered
  verbatim on every issue page, so the same number is now described two
  ways on two pages of the same site.
- What: the weekly agent's digest template says "papers read" instead of
  "papers ingested". Nothing else changes, and the claims and edges lines
  are already fine.
- Why this run did not simply make the edit: the digest is the weekly
  agent's output and its published issues are a record, so rewriting one
  from this seat would edit a publication after the fact.
- First step: the line in the weekly agent's template, applied to future
  issues rather than to the ones already out.
- Cost: $0
- Status: proposed

### 2026-09-18 — Choose the hero metric's count source (frontend agent)
- Trigger: sprint item 5 asked for the weekly ingest count at build or
  revalidate time, and the hardcoded "3,431" is now gone from
  `site/app/page.jsx`. The count still has nowhere real to come from.
  `site/` has no database client, adding one is a dependency the charter
  says needs a ledger proposal first, and Neon's HTTP query path is not a
  documented public endpoint, so writing a fetch against it would be a
  guess this run could not verify.
- What: decide between two wirings, both $0. Either the site gains a Neon
  client and reads `DATABASE_URL` at revalidate time, or the pipeline
  publishes the number it already computes and the site reads that. The
  pipeline already has the query in `pipeline/weekly.py` gather(), and
  `NEON_RO_URL` is proven to work from Actions per the skill agent's
  entry above, so the second path needs no new credential in the site at
  all.
- First step: `site/lib/metrics.js` holds the whole seam. It reads
  `INGEST_COUNT_URL`, a JSON endpoint answering `{"papers_ingested": n}`,
  and it carries the canonical SQL in a comment. Swapping it to a client
  query is a change to one function.
- Cost: $0
- Status: proposed

### 2026-09-18 — Give the waitlist a durable home before launch (frontend agent)
- Trigger: sprint item 4's capture is live on home and pricing, and it
  writes through `site/lib/waitlist.js`. That file appends to local disk,
  which is the right holding pen while Stripe does not exist, but it is
  not a list. Two things block the real insert. `db/schema.sql` constrains
  `subscribers.status` to ('active', 'unsubscribed'), so the sprint's own
  `waitlist` status will fail its check, and local disk does not survive a
  redeploy on a serverless host, so anything captured between now and the
  wiring is lost at the next deploy.
- What: add 'waitlist' to the status check, then point
  `saveWaitlistEmail()` at `insert into subscribers (email, tier, status)
  values ($1, 'digest', 'waitlist') on conflict (email) do nothing`. The
  endpoint is already idempotent on duplicates, so no behaviour changes.
- First step: the schema line, since the insert cannot run before it.
  db/ is outside the frontend lane, so this is the engineer's to make.
### 2026-09-18 — harness-engineering does not fire on its own test-time-compute case (skill agent)
- Trigger: the executable trigger test built this run
  (`skills/_validation/trigger_test.py`, board card "Design the skill
  validation system") fails one of twelve cases, and the failure is in
  the library rather than in the instrument. The prompt "We have budget
  for extra inference compute on one hard planning step. Should the agent
  reflect on and revise its own answer, or should we sample three
  candidates in parallel and select one?" does not select
  `harness-engineering`. It loses by 0.010 to a decoy about cluster
  capacity, because the skill's description claims the case with the
  phrase "when allocating test-time compute" and contains none of the
  words a user actually reaches for: inference, sample, parallel, select,
  revise, reflect.
- What: amend the `description` of `skills/harness-engineering/SKILL.md`
  so the activation condition carries the vocabulary of the question, not
  only its term of art. Suggested replacement for the existing clause:
  "or when deciding how to spend extra inference compute on a hard step,
  for instance sampling several candidates in parallel and selecting one
  versus having the model revise its own answer". The skill's body and
  provenance are untouched by this, only the trigger surface.
- Why this run did not simply make the edit: `harness-engineering` is the
  one skill in gold carrying a recorded validation result, and editing a
  validated artifact is the case the V4 regression gate
  (docs/product/skill-validation.md) exists to govern. That gate is not
  built, so there is nothing to re-run against the edit yet. Recording
  the defect and leaving the suite red is the honest state.
- First step: apply the clause, re-run
  `python3 skills/_validation/trigger_test.py`, expect 12 of 12, and
  record the new bundle next to the failing one so the before and after
  both stay on the record.
- Cost: $0
- Status: accepted
- Groomed 2026-09-18 (PM, closing all-hands triage): the skill seat's own
  ask at the closing all-hands was whether this ships red or gets fixed
  before launch. Decided: fix it, on the skill agent's normal Tuesday
  cadence (next run 2026-09-22), not as an engineer sprint item. The V4
  regression gate not existing yet is a reason to record the before/after
  bundle carefully, per this entry's own first step, not a reason to
  leave a known, cheap, one-clause fix red through launch.

### 2026-09-18 — trigger_reliability is now computable, and option (b) is the one to build (skill agent)
- Trigger: the verification-badge schema entry filed earlier on
  2026-09-18 left `trigger_reliability` as the one field with no data
  source, and flagged two options: drop it from v1, or have the panel
  replay each trigger-test prompt. The executable test built this run
  settles it. The prompts now live in `skills/<slug>/triggers.json` and
  replay deterministically in about a second with no model, no network,
  and no database.
- What: wire the badge's `trigger_reliability` to the newest bundle in
  `skills/_validation/results/`, rendering the fraction with its exact
  binomial interval and the engine version that produced it, never a bare
  percentage. Until the model-in-the-loop engine exists (slice 5 of
  docs/product/skill-validation.md), the number is a lower bound and the
  page must say so.
- First step: this depends on the parser fix already in the ledger
  ("Receipt-rendering schema for the skill library"), since the bundle
  keys off each skill's name and the site cannot currently read nested
  frontmatter at all. Build the parser fix first, then read the bundle.
- Cost: $0
- Status: proposed

### 2026-09-18 — Run the trigger test in CI on every PR touching skills/ (skill agent)
- Trigger: the test is executable, stdlib-only, and finishes in about a
  second, so the marginal cost of running it on every PR is effectively
  zero. Nothing runs it today, which means the next skill PR can silently
  regress another skill's routing.
- What: a small GitHub Actions job on pull requests touching `skills/**`
  running `python3 skills/_validation/trigger_test.py --json` and posting
  the summary. Workflow files are the engineer's surface, not this
  agent's, hence a proposal rather than a commit.
- Note on the gate: the suite is red today by design (see the
  harness-engineering entry above), so wiring it as a required check
  before that clause lands would block every PR. Either land the
  description fix first, or have the job compare against the last
  recorded bundle and fail only on regression, which is the V4 rule and
  the better long-run design.
- First step: land the description amendment, then add the job as a
  non-blocking check for one week before making it required.
- Cost: $0
- Status: proposed

### 2026-09-18 — skill-extract's SQL sketch names a column the schema does not have (skill agent)
- Trigger: found while querying silver this run. The candidate-cluster
  query in `prompts/skill-extract.md` selects `c.text` from `claims`, but
  the column is `claims.claim` (db/schema.sql). Copied as written, the
  query errors out, which costs a future run a turn on a trivial fix.
- What: fixed in this run's PR, since `prompts/skill-extract.md` is this
  agent's writable surface. Recorded here because the same drift can
  recur: the prompt carries a hand-written copy of the schema, and
  nothing checks it against `db/schema.sql`.
- First step: none required. Worth considering, when the panel is built,
  whether the extract prompt should reference the schema file rather than
  restate it.
- Cost: $0
- Status: built
## Engineer agent findings (2026-09-18, sprint 2026-09-21 items 1-3)

### 2026-09-18 — Read the archive from the `digests` table, fixture as fallback (engineer agent)
- Trigger: sprint item 3 asked for real digest content on the archive.
  This session had no database credentials (`NEON_RO_URL` is wired into the
  research and skill workflows but not `agent-engineer.yml`, and it was
  empty here), so the issue body had to be recovered from git history at
  commit `d98885e`, from before `digests/` went gitignored. Meanwhile
  `db/schema.sql` already calls the `digests` table "the database of
  record," one row per ISO week with the markdown in `body`. The site and
  the database of record are not connected, so the archive will still show
  only 2026-W37 the day 2026-W38 sends.
- What: give `site/lib/content.js` a Neon-backed implementation behind the
  interface it already exposes (`listIssues`, `getIssue`). Query `digests`
  ordered by week, fall back to the checked-in fixtures when
  `DATABASE_URL` is absent so local development and preview builds keep
  working with no credentials. The driver is already a site dependency as
  of this PR (`@neondatabase/serverless`), added for the spine entitlement
  check, so this is a query and a fallback branch rather than new plumbing.
- First step: add `NEON_RO_URL` to `.github/workflows/agent-engineer.yml`
  so an engineer session can see the table it is coding against, then
  write the query behind the existing interface.
- Cost: $0
- Status: proposed

### 2026-09-18 — A "why this matters" line on every digest item (engineer agent)
- Trigger: this run's craft scan of Import AI (jack-clark.net, 116,000+
  free subscribers, 450+ issues). Every item in every issue ends with a
  named "Why this matters" annotation that states the consequence for the
  reader, separate from the finding itself. Reading our own 2026-W37 issue
  end to end while wiring it to the archive, the contrast is sharp: our
  items give the claim and then the procedure, both accurate, and leave
  the reader to work out what to do differently. Import AI never makes the
  reader do that work.
- What: add one required slot to the item template in `prompts/digest.md`:
  a single sentence naming what a builder should do differently now that
  this holds. It is a prompt change, not a pipeline change, so it is
  cheap to try and cheap to revert. Pair it with the blind read test
  already proposed in this ledger so the change is judged rather than
  assumed.
- First step: add the slot to `prompts/digest.md` and regenerate 2026-W37
  from the stored payload, then read the two versions side by side.
- Cost: $0
- Status: proposed

### 2026-09-18 — Editorial titles for the pre-overhaul issues (engineer agent)
- Trigger: with the archive finally rendering, the 2026-W37 row reads
  "alexandria digest — 2026‑W37" and tells a visitor nothing, because the
  first editions predate the voice overhaul that made the H1
  "{Editorial title} [{dates}]" (`prompts/digest.md`). The archive is now
  a public acquisition surface, so a title that carries no information is
  a cost on every issue that has one. The date range is already handled:
  `weekRange()` derives the ISO week's Monday-to-Sunday span, so the row
  reads "[September 7–13, 2026]" rather than an empty bracket.
- What: a one-off pass that gives each pre-overhaul issue an editorial
  title in the current format, taken from what the issue actually argued,
  and rewrites its H1. Small, but it is the difference between an archive
  that sells the product and a list of week numbers.
- First step: retitle 2026-W37, the only issue on the site today.
- Cost: $0
- Status: proposed

### 2026-09-18 — Craft scan: Import AI (jack-clark.net)
- Scanned: the public archive and issue pages, as a signed-out visitor.
  Chosen because this run built alexandria's public archive, and Import AI
  runs the same shape at scale: every issue free and complete in public,
  with the paid tier selling access rather than content.
- Worth stealing: the per-item "Why this matters" annotation, filed as its
  own ledger entry above. Also structural, and cheaper: issues are
  numbered and titled with their actual topics ("Import AI 472: topic;
  topic; topic"), so the archive index is scannable without opening
  anything. Ours is titled by week number, which is the entry above.
- Where alexandria is better: Import AI's "gaining traction" equivalent is
  one author's judgment, stated well but unfalsifiable. Ours is counted.
  The "gaining traction" section is backed by `supports` edge counts in
  the claim graph and citation trajectories from the slow loop, and "left
  behind" is backed by `contradicts` edges and the `deprecated_claims`
  view. A reader can ask why a claim moved and get a number and an edge,
  not an opinion. No profiled digest can answer that question at all.
## ExO findings (2026-09-18, second run)

Filed by the ExO agent under charter §5b: staleness found in surfaces
that belong to other seats, flagged here rather than edited there. Each
is a documented fact contradicting a decision the owner has already
made, so none of these needs a new decision, only the owning seat's
hand. Statuses left blank for the owner as always.

### 2026-09-18 — pipeline/weekly.py still calls the newsletter the paid product (engineer)
- Trigger: README and diagram audit. `pipeline/weekly.py`'s module
  docstring says the digest "goes to subscribers by email ... the
  newsletter is the paid product." The owner decided the opposite on
  2026-09-17, recorded in vision.md §0: the digest is free and full as
  the acquisition engine, and the $20 spine is the operational layer.
- What: correct the docstring to the current pricing. The code is right,
  only the prose about why it exists is wrong, which is the lying-
  docstring class the security seat's charter already hunts.
- First step: one docstring, engineer or security, whoever runs first
- Cost: $0
- Status:

### 2026-09-18 — four product docs still point at prompts/weekly-agent.md (engineer)
- Trigger: ADR-25 renamed the weekly seat to the research agent and moved
  its charter to `prompts/research-agent.md`. Nine references to the old
  path survive in `docs/product/architecture-next.md`,
  `docs/product/source-discovery.md` and `docs/product/pipeline.md`, two
  of which also name an `agent-weekly.yml` that does not exist. A reader
  following any of them lands on nothing. The README and ADR-12 were
  fixed in the ExO's PR this run; these are the engineer's surface.
- What: update the paths, and check whether the self-application step
  those docs propose is now the research seat's step 4 rather than a new
  one.
- First step: `grep -rn weekly-agent docs/product/`
- Cost: $0
- Status:

### 2026-09-18 — skills/README.md says the gold layer is empty (skill agent)
- Trigger: `skills/README.md` reads "Empty is the honest starting state."
  Two skills are merged and live: `harness-engineering` (2026-09-12) and
  `self-improving-post-training-loops` (2026-09-18). Honesty was the
  point of that sentence, so it should keep being honest.
- What: describe what is actually in gold, and what a reader should
  expect a skill file to contain, since skills are the sellable product.
- First step: rewrite three lines, skill agent's next Tuesday run
- Cost: $0
- Status:

### 2026-09-18 — the Q4 OKR file calls the mission unapproved (okr agent)
- Trigger: `docs/okrs/okrs-2026-Q4.md` says the mission is "proposed
  2026-09-18, pending the owner's approval, not yet canonical."
  vision.md §0 records it as the owner's words, final, same day:
  *accelerate every builder to frontier speed.* The OKR file is the
  document that holds every quarter against the mission, so it is the
  worst single place for that line to be stale.
- What: cite the approved mission and drop the pending language.
- First step: the OKR agent's next run, or sooner if the owner prefers
- Cost: $0
- Status:

### 2026-09-18 — the diagram atlas needs fresh counts from the database (engineer)
- Trigger: `docs/diagrams.md` diagram 1 carries per-node counts from
  2026-09-08 (2,312 papers, 1,446 triaged, 80 claims, 22 edges). The one
  verified newer number is 441 claims on 2026-09-18 (PR #16). The ExO
  fixed which stations are live and labelled the counts as stale this
  run, but has no database access and will not guess numbers.
- What: refresh the five counts in diagram 1 and the four in diagram 2
  from a live query, and consider printing the query beside them so any
  future run can re-check rather than re-guess.
- First step: five `select count(*)` statements, engineer's next run
- Cost: $0
- Status:

## Sales agent proposals (2026-09-18)

Filed by the sales seat (ADR-24) on owner dispatch. Each is a build the
launch plan depends on and that sales cannot do itself, flagged to the
owning seat rather than assumed. Arguments in docs/sales/.

### 2026-09-18 — A team/seat purchase path, manual first
- Trigger: `docs/sales/first-customers.md` lane E targets ten seats
  across two companies in month one, and §5 B2B-1 flags that taking
  payment for more than one seat does not exist today. First evidenced
  public prospect: HN commenter keks0r describing a company-wide shared
  skill library ([item 49698184](https://news.ycombinator.com/item?id=49698184),
  2026-09-14, verified 2026-09-18)
- What: **not a seat-management UI.** Entitlement is already a row in the
  Neon `subscribers` table checked server-side by email (vision.md,
  Sprint 2), so ten seats is ten rows. The ask is a line on the pricing
  page and in the launch email — "Buying for a team? Reply and I'll set
  it up" — plus whatever minimum Stripe configuration lets one invoice
  cover several seats. Owner adds rows by hand for the first ten teams;
  automate at the eleventh, not before
- First step: confirm whether the planned Stripe Payment Link can take a
  multi-seat payment at all, since that answer decides whether lane E
  closes cleanly or falls back to five individual subscriptions
- Cost: $0
- Status: proposed
- Groomed 2026-09-18 (PM, closing all-hands triage): this is the
  "multi-seat Stripe question" the sales floor statement asked to have
  routed to the engineer. Already routed, by existing here as a ledger
  entry; no separate action needed from this triage.

### 2026-09-18 — The Left-Behind Index as a public page
- Trigger: the `deprecated_claims` view already exists, nothing in the
  competitive landscape publishes negative results
  (docs/market/landscape.md), and it is the only honest answer to the
  "everyone here is selling a solution" objection recorded on HN
  ([item 49689454](https://news.ycombinator.com/item?id=49689454),
  commenter taurath, verified 2026-09-18). Two drafted outreach notes
  (`outreach-plan.md` C3d and the launch-day skeptic reply) are gated on
  this page existing and cannot be sent until it does
- What: a permanent public page listing practices the evidence has
  abandoned, each with its citation and the date it stopped being
  supported — a thin public face over a view the pipeline already
  computes
- First step: decide what is public versus paywalled before writing the
  route; the digest-content boundary (vision.md §4) applies
- Cost: $0
- Status: accepted
- Groomed 2026-09-18 (PM, closing all-hands triage): accepted, same
  decision as "Make 'left behind' the public flagship" above (market
  agent's entry). This page-shaped version and that weekly-verdict
  version are the same accepted idea; whoever builds it first should
  treat the other entry as satisfied rather than build both. Greenlit as
  a product/backlog call within PM authority (all-hands decision 4), not
  money, a secret, or purpose, per the owner's dispatch for this triage.

### 2026-09-18 — The Receipt Standard: publish the provenance spec plus a conformance linter
- Trigger: 69% of 216 audited public Claude Code skills won't reliably
  trigger ([item 49744398](https://news.ycombinator.com/item?id=49744398),
  2026-09-17) and no registry attaches evidence to a listing
  (docs/market/opportunities-2026-09-18.md)
- What: publish the `provenance:` frontmatter already in
  `skills/harness-engineering/SKILL.md` (`extracted`, `validated`,
  `claims`, `papers`) as an open spec anyone may implement, with a free
  linter that checks conformance. Give the format away; the
  unreplicable part is a claim graph that can fill the fields. Argued in
  `docs/sales/b2b-lane.md` B2B-7 and `docs/sales/idea-list.md` 49
- First step: spec page and linter **in the same change** — a spec
  without a checker invites empty `claims: []` blocks that dilute the
  signal the spec exists to create
- Cost: $0
- Status: proposed

### 2026-09-18 — Check `contradicts` density before building Claim Watch
- Trigger: `docs/sales/b2b-lane.md` B2B-5 proposes contradiction alerts
  as a paid monitoring product, and its value depends entirely on how
  often such an alert would actually fire
- What: one query, not a build — over the last quarter, how many
  `contradicts` edges landed on claims that a team could plausibly have
  pinned? The answer gates whether the product is worth building at all,
  and it is cheap enough that it should gate the build rather than
  follow it
- First step: run the query against `claim_links`; record the number in
  the sales results file either way, including if it is zero
- Cost: $0

## PM findings (owner-priority re-triage, 2026-09-18)

### 2026-09-18 — Raise the skill-agent cadence, conditioned on staying honest (charter-text proposal, PM-recorded for the ExO)

- Trigger: incident 12 and all-hands decision 11 (docs/agents/incidents.md,
  docs/allhands/2026-09-17.md, 2026-09-18): the owner's release gate names
  "a real repository of validated, tested newsletter issues and skills,
  not two of each." The skill agent runs once a week (prompts/skill-agent.md,
  Tuesdays); at that pace, docs/market/report-2026-09.md §7's own bar for a
  credible library (double digits, validated) is roughly two and a half
  months out from today. The gate cannot be met on the current cadence
  without also moving the launch date; docs/sprints/pending.md's release-
  gate reconciliation costs this exact tradeoff for the owner's decision.
- What: raise the skill agent's charter cadence toward multiple draft-to-
  validated skills per week, hard-conditioned on the same charter's own
  discipline holding: "quality over count," a recorded validation (not
  judgment alone) before promotion, and "zero skills is a fine outcome; a
  padded skill is not." A cadence increase that produces more skills but
  fewer of them honestly validated does not move the score decision 11
  set; it just moves the number of items in `skills/` with `validated: ""`
  in their frontmatter, which is the exact state the owner already
  criticized. If the corpus cannot honestly support more than one strong
  cluster a week, the charter should say that explicitly rather than
  create pressure to pad.
- First step: this is charter text (prompts/skill-agent.md's cadence line
  and Step 1's "one skill per run" instruction), which per ADR-19 only the
  ExO edits, gated by the owner's merge like every charter change. This PM
  run cannot commit it directly. Recorded here as a `proposed` entry for
  the ExO's next run (PR #18, currently open, is already mid-flight on a
  charter sweep) or for the owner to apply directly if she would rather
  decide the exact number herself.
- Cost: $0
- Status: proposed
- Groomed 2026-09-18 (PM, closing all-hands triage): PR #18 merged
  2026-09-18 without picking this up. Superseded by the entry directly
  below, which the skill seat's own closing all-hands floor statement
  made concrete: not "more skills per run" but a second parallel
  extraction session per week on a different claim cluster, same quality
  bar. That is the shape this entry left underspecified. See "Adopt a
  second weekly skill-extraction session" below for the exact charter
  and workflow text.

### 2026-09-18 — Adopt a second weekly skill-extraction session (charter-and-workflow proposal, PM-decided for the ExO and owner to apply)

- Trigger: the skill seat's own floor statement at the closing all-hands
  (docs/allhands/2026-09-18-close.md): "the honest state: two skills, one
  validation that is n of 1... At one skill per week the library reaches
  five or six by Oct 13," short of docs/market/report-2026-09.md §7's
  double-digit, validated bar. The proposal, in the skill seat's own
  words: "not more skills per run but a second parallel extraction
  session per week on a different claim cluster, same quality bar,
  doubling throughput without padding." The owner's dispatch for this
  triage run named the decision explicitly as this seat's to rule on, to
  be written as a charter-and-workflow proposal for her merge if adopted.
- Decision: **adopted**. Reasoning: the proposal keeps every discipline
  the entry above worried about losing (one skill per session, quality
  over count, a recorded validation before promotion) and only adds a
  second, independent session against a different cluster. It does not
  ask the agent to draft two skills in one sitting, which would be the
  actual padding risk; it asks for two normal sessions in a week instead
  of one. This is the floor's own "doubling throughput without padding"
  framing, taken at face value, and it directly serves decision 11's
  phased gate (this same triage, adopted provisionally above): the paid
  spine's gate opens at a benchmark five, which needs the skill library
  at double digits, validated, and one session a week does not reach
  that on any date this quarter.
- What: the exact charter and workflow text for the ExO to apply and the
  owner to merge, since both charters and workflow files are owner-merge
  only (this PM run's writable surface is docs/sprints/ and grooming
  notes in docs/ideas.md, neither of which includes prompts/ or
  .github/workflows/):
  - `prompts/skill-agent.md`, line 6: change "You run once a week,
    Tuesdays, in a fresh cloud session." to "You run twice a week,
    Tuesdays and Fridays, in a fresh cloud session each time." Step 1's
    "One skill per run, quality over count" is unchanged text, since it
    already states the per-session rule this proposal relies on; add one
    sentence after it: "The Friday session works a different claim
    cluster than the one already picked (or in progress) that week, so
    the two sessions never compete for the same evidence."
  - `.github/workflows/agent-skill.yml`: add a second cron entry
    alongside the existing Tuesday one, `- cron: "0 12 * * 5" # 8:00 AM
    ET Fridays`, under the same `schedule:` key. No other change to the
    workflow file; the embedded prompt already reads the charter fresh
    each run, so it needs no edit once the charter line above changes.
  - `docs/agents/org-chart.md`'s skill row (`Tue 8:00 ET`) should become
    `Tue + Fri 8:00 ET` once this lands; flagged here since org-chart.md
    is also outside this run's writable surface tonight.
- Cost: $0 in new services. It roughly doubles the skill seat's weekly
  usage against the existing Claude subscription; docs/sprints/pending.md
  already carries the subscription's monthly figure as an owner-only,
  not-yet-costed item, so this is worth re-checking once that figure
  exists rather than assumed free of any real cost.
- Status: proposed

### 2026-09-18 — Let a skill declare its own shelf and its own summary (frontend proposal)

- Trigger: the owner's order 3 of 2026-09-18, to reorganise the skills
  library so it scales to fifty. The page is now shelves, and it works,
  but the shelf a skill lands on is decided in `site/lib/skill-shelves.js`
  by matching the skill's name, then by scanning its description for
  keywords. `skills/` belongs to the skill agent and the frontend seat
  does not write there, so this was the only honest way to do it from
  this lane.
- The problem with it: it is a guess made outside the file it describes.
  A new skill whose name is unknown and whose description happens to say
  "context" lands on Context engineering whether or not that is where its
  author would have put it, and nobody who writes a skill can see where
  it will appear. At two skills the guess is checkable by eye. At fifty
  it is not.
- What: two optional fields in a skill's frontmatter, both written by the
  skill agent when it extracts:
  - `shelf:` one of the shelf ids in `site/lib/skill-shelves.js`
    (`harnesses`, `context`, `multi-agent`, `training`, `serving`,
    `multimodal`). The site keeps its keyword fallback for skills that
    do not carry the field, so nothing breaks on the way in.
  - `summary:` one plain sentence for a person. `description:` stays
    exactly as it is, because it is what the router matches on and what
    the trigger test scores. This is the same proposal an earlier run in
    PR #26 filed against the routing text showing up as page copy, and
    the shelves make it worth a second mention: the page currently
    derives the human sentence by cutting `description` at its first
    "Use when", which works on both of today's skills and is a
    convention, not a guarantee.
- Cost: $0. It is two frontmatter lines per skill and a few lines in
  `site/lib/skill-shelves.js` to prefer them when present.
- Whose call: the skill agent's charter and `skills/`, so not this
  seat's. Filed for the owner.
- Status: proposed

### 2026-09-19 — The masthead is the recipe, and it is in code (writer seat)
- Trigger: first editorial run (ADR-28) graded 2026-W37 against the ten
  laws. Law 3 says sell the product, never the recipe. The issue's second
  line is the recipe.
- What is there now: `MASTHEAD` at `pipeline/weekly.py:311` prints under
  every H1: "*The latest in AI research, read in full and distilled
  weekly: what's new, what's gaining acceptance, and what newer evidence
  has overturned.*" It describes how the digest is made, then recites its
  own table of contents in the order the sections used to appear.
- Why it is filed here rather than fixed: it is fixed in code, on purpose,
  so the brand line never drifts. That reasoning is sound and this seat
  does not write pipeline code. No change to prompts/digest.md can reach
  it, so the structure-watch rule fires on the first run instead of the
  third.
- Two things make it worse than it was. The section order it recites is
  now wrong, because this PR moves compounding work ahead of new work
  under law 5. And a reader who opens the issue meets a description of
  alexandria's process before meeting a single finding.
- What to put there instead: a line that sells the product rather than
  the method, and that does not enumerate sections. The dual-audience
  close is the house's best sentence and already carries the promise:
  "You read to decide. Your agents load to act." Either promote it to
  the masthead as well as the close, or drop the masthead and let the
  finding land first. This seat's recommendation is to drop it, because
  the headline under law 4 now carries a real finding and a subtitle
  between it and the opening only delays the payoff.
- Cost: deleting or rewriting one constant and its helper, plus a test if
  one covers `add_masthead`.
- Whose call: the owner's on the words, the engineer's on the code.
- Status: proposed

### 2026-09-19 — The date range arrives as an en dash (writer seat, run 2)
- Trigger: reading prompts/digest.md end to end. The prompt tells the
  issue to print `dates` verbatim in the title, and it also forbids
  non-ASCII punctuation, because typesetter characters break the reader's
  search box and the agent that loads the issue. The payload's example
  range is "September 7–13, 2026", with an en dash, so the two rules
  contradict each other on the single most-read line of the issue.
- Fixed for now in the prompt: the title rule normalizes the range to a
  plain hyphen, and the payload glossary says the dash arrives and ships
  as ASCII. That works, but it asks the model to remember a character
  substitution on every issue, which is the least reliable place to put
  it.
- Better fix, in code: emit `dates` with an ASCII hyphen where the
  payload is assembled, and the prompt rule becomes unnecessary.
- Whose call: the engineer's. This seat does not write pipeline code.
- Status: mostly moot as of run 3. The owner's ruling took the date range
  out of the title entirely, so the en dash no longer reaches the
  most-read line of the issue. The prompt still asks for an ASCII hyphen
  where a range genuinely belongs in the prose, which is a much smaller
  surface, and the code fix is still the better place for it if the
  engineer is in there anyway.

### 2026-09-19 — The newsletter prose guide was merged as a stub (writer seat, run 2)
- Trigger: the owner ordered the market seat's prose guide applied to the
  generator. `docs/market/newsletter-prose-guide.md` is on main, but it
  contains its header, its commissioning note, and "Work in progress —
  populating from primary sources now." No guidance points. PR #38's
  description said "Research in progress — marking ready when the guide
  is complete" and it was merged anyway.
- Consequence: this run's craft changes came from the canon's References
  section and the owner's taste rulings instead, which is stated plainly
  in the run 2 review. The greeting, heading, item and sign-off rules now
  in prompts/digest.md were not derived from any study of the actual
  newsletters, because no such study exists yet in the repo.
- What is owed: when the guide is populated, the writer seat re-applies
  it on its own terms and reconciles it against what is already in the
  prompt. Where it contradicts a taste ruling, the ruling wins.
- Also worth deciding: whether a draft-in-progress PR should be
  mergeable at all when a downstream seat is ordered to depend on it.
  That is a process question for the PM, not a voice question.
- Whose call: the market seat to finish it, this seat to apply it, the
  PM on the process point.
- Status: proposed

### 2026-09-19 — A taste ruling reaches the register but not the generator (writer seat, run 3)
- Trigger: incident 20, read from the inside. Her heading ruling was
  recorded in docs/voice/taste.md the same hour, and prompts/digest.md,
  docs/voice/ban-list.md and canon law 9 all still instructed the
  violation. The model that printed "Gaining traction" was obeying the
  file that writes issues. Recording a ruling is not enforcing it, and
  the register is not where enforcement lives.
- The gap is a missing step, not a missing rule. Nothing in the process
  says "and now find every file that contradicts this". taste.md is
  append-only by design, so a ruling lands there and stops.
- Proposal: when a ruling is recorded in taste.md, the recorder also
  names the files it now contradicts, and the writer seat's next run
  clears that list. A one-line "contradicts:" note on the ruling would
  be enough. Cheaper than an incident.
- Whose call: the PM on the process, the chair on who records. This seat
  has taken its own half already, as the taste-compliance first gate in
  docs/voice/reviews/2026-09-19.md §8.
- Status: proposed

### 2026-09-19 — The heading gate, pre-registered for the pipeline (writer seat, run 3)
- Trigger: the charter's structure-watch rule. The framework-name
  violation has now happened twice, and run 3 answers it with a hard
  check inside prompts/digest.md, which is still the model policing
  itself. If it holds, nothing is owed. If the next issue prints one of
  the eight banned strings as a heading, the prompt has failed twice at
  the same fix and the third attempt belongs in code, not in the prompt.
- The code fix, stated now so it is not designed in a hurry later: after
  generation and before the insert into `digests`, scan the body's
  heading lines for the banned strings and fail the run loudly rather
  than publish. The banned list is small, the check is a few lines, and
  failing loudly is right because a heading violation is the one defect
  the owner has had to report twice.
- Whose call: the engineer's, and only if the prompt gate fails. Filed
  now so the trigger is unambiguous.
- Status: proposed, conditional

### 2026-09-19 — The title's date bracket becomes dead code on the site (writer seat, run 3)
- Trigger: her ruling took the date out of the H1, and the prompt now
  emits a bare title. `site/lib/content.js:31` parses the title with
  `/^(.*?)\s*\[(.+)\]\s*$/` and falls back to `weekRange(week)` when no
  bracket is there, so the archive keeps showing a date and nothing
  breaks. Checked before the prompt change shipped.
- What is left: once no issue carries a bracketed range, the parse branch
  and its comment describe a format that no longer exists. Retiring it is
  tidying, not a fix.
- Whose call: the frontend seat's. This seat does not touch site code.
- Status: proposed

### 2026-09-19 — Does the newsletter get a first person? (writer seat, run 4)
- Trigger: the prose benchmark. Import AI and Money Stuff score A on
  voice for one reason, which is that a named person is visibly making
  the judgments ("I think sometimes, in our age of artificial
  intelligence..."). The Batch signs its letter "Andrew". Morning Brew
  signs every item with the writer's initials. alexandria has no person
  anywhere, and the benchmark grades the patched generator C+ on voice
  largely because of it.
- The question for the owner, not for this seat: may an issue say "I" or
  "we" when it disagrees with a paper? A stance is the cheapest remaining
  point of voice, and it is also a claim about who alexandria is.
  Autonomy is the product's thesis, so an invented human byline is out,
  but an unsigned editorial "we" is a real option and so is staying in
  the third person on purpose.
- Whose call: the owner's, recorded in taste.md. The prompt change is
  two sentences once she rules either way.
- Status: proposed

### 2026-09-19 — The prose guide and the benchmark should merge (writer seat, run 4)
- Trigger: `docs/market/newsletter-prose-guide.md` is still a stub on
  main, and canon law 9 and a taste ruling both point at it. Run 4
  produced `docs/voice/prose-benchmark-2026-09-19.md`, which reads the
  same newsletters from primary sources and quotes them.
- Proposal: the market seat writes its guide on top of the benchmark's
  quotes rather than starting over, and the benchmark stays the dated
  measurement it is. Two studies of the same five newsletters is waste,
  and worse, they will disagree.
- Whose call: the market seat's, on its own file. This seat does not
  write in docs/market/.
- Status: proposed

### 2026-09-19 — The traction section counts a paper supporting itself (writer seat, run 5)
- Trigger: run 5 pulled the claims behind today's issue to rewrite two
  items and checked where their support came from. The on-policy
  distillation item that leads the traction slot has five of its six
  `supports` edges drawn from its own paper, `arxiv:2609.04172`
  supporting `arxiv:2609.04172`.
- The measurement, run today against the live database: 68 of 98
  `supports` edges join two claims from the SAME paper. Under the
  current query, 24 claims clear the `having count(*) >= 2` bar. If the
  bar were two distinct supporting PAPERS, 4 would.
- Why it matters more than a normal data bug: traction is the owner's
  standing law, the traction slot leads every issue, and
  prompts/digest.md instructs the writer to translate the count into
  "three separate papers built on it this week" or "three independent
  groups now report the same effect". For most of today's traction
  items that sentence is false, and the prompt cannot detect it, because
  the payload carries the supported claim and its count and never the
  supporting papers' ids.
- Proposal, `pipeline/weekly.py:172`, the `supported` query: join the
  source claim to its paper and add `and sc.paper_id <> c.paper_id`,
  then count distinct source papers rather than edges. Carry the
  distinct-paper count into the payload so the issue says a true thing.
  Four honest traction items beat 24 that rest on a paper agreeing with
  itself, and canon law 11 already says a thin day is honestly short.
- Whose call: the engineer's. This seat does not touch pipeline code,
  and a prompt rule cannot fix it (charter, structure watch).
- Status: proposed

### 2026-09-19 — `institutions` is empty on 99.2% of papers (writer seat, run 5)
- Trigger: run 5 went to attribute two reconstructed items by institution
  and found nothing to attribute with. `arxiv:2609.20784` and
  `arxiv:2609.04172` both carry an empty `institutions` array.
- The measurement, run today: 38 of 4,756 rows in `papers` have a
  non-empty `institutions`. That is 0.8%.
- Why it matters: canon law 9 and the owner's fine-tuning both put
  institution-first attribution in the prompt because readers know labs
  and not author names. In practice the generator falls back to "a team
  led by <first author>" on essentially every item, which is the weaker
  line AND a repeated construction, so it reads as template furniture by
  the third use. The prompt now tells the writer to vary the fallback,
  which treats the symptom.
- Proposal: populate `institutions` at ingest or distill time. arXiv
  listings carry affiliations in the paper's own front matter and the
  Semantic Scholar record often carries them too, and the field already
  exists in the schema, so this is a fill rather than a migration.
- Whose call: the engineer's. This seat does not touch pipeline code.
- Status: proposed

### 2026-09-19 — Grow an eye for epitome's territory: agent interop and identity coverage
- Trigger: incident 21. The first real agent user (epitome's session) searched the corpus for agent identity, portability, and credential security and found nothing; best similarity 0.69 on unrelated capability papers. Filed on the epitome session's own offer, relayed by the owner.
- What: make agent-interop and identity a reachable, processed slice of the corpus: (a) signal feeds added same-day (A2A releases, SPIFFE releases; MCP spec was already watched); (b) research seat steers ingestion toward delegation protocols, agent credentials, A2A-class interop papers wherever they publish (cs.CR now ingested, cs.MA watched); (c) the monthly source census (ADR-29) measures this slice explicitly: "could epitome's two queries be answered from the corpus" is the acceptance test, re-run until yes or consciously declined.
- First step: research seat's Monday brief includes the epitome-queries test against the corpus and names the three most valuable missing sources for this slice.
- Cost: $0.
### 2026-09-18 — The site's own values have drifted off the canon's measurement system (frontend proposal)

- Trigger: the design canon became charter this run, and its measurement
  system is the only type, spacing and radius scale the seat may use. The
  skill row anatomy rebuilt this run was built on it. The chrome around
  it was not, because the owner's order for this run says to keep the
  shelves, the filter, the empty-shelf lines and the header exactly as
  they are, and she likes them. So the drift was left in place and is
  filed here rather than changed.
- What is off, measured in `site/app/globals.css`:
  - Type off the scale (12, 14, 17, 19, 21, 24, 28, 32, 40, 48...):
    `.lib-count` and `.lib-note` at 13, `.lib-filter input` and
    `.lib-empty p` at 15, `.shelf.is-empty .shelf-head h2` at 18, and
    `.shelf-head h2` at 22.
  - Spacing off the 8-point grid (4, 8, 12, 16, 24, 32, 48, 64, 96,
    128): the shelf's 26px padding, the empty shelf's 40 and 22, the
    shelf blurb's 14, the rows' 30, the filter's 11 by 14.
  - `--line` is `#e8e8e8`. The canon's palette names `#e5e5e5`.
- Why it is worth doing on purpose rather than drifting back: every one
  of these is within two or three pixels of a legal value, which is
  exactly why nobody catches them one at a time. A single pass that
  moves 13 to 14, 15 to 14 or 17, 18 and 22 to 19 or 21, and the spacing
  to its nearest grid step, costs one diff and one screenshot set and
  ends the drift.
- The colour is not this seat's call. `#e8e8e8` to `#e5e5e5` is a
  palette change and the canon says palette changes are the owner's
  alone, so it needs her word even though it is three hex digits.
- Cost: $0, one run's work.
- Whose call: the owner, because the values sit inside elements she has
  said she likes.
### 2026-09-18 — Data-handling disclosure ("permissions label") on every alexandria skill and automation (market, later Friday run)

- Trigger: a top HN story this run (215 points), "ZCode, the GLM coding
  agent, silently uploads your Git history"
  ([news.ycombinator.com/item?id=49752422](https://news.ycombinator.com/item?id=49752422),
  2026-09-18). Top comments argue for open-source, auditable harnesses
  over trusting a vendor's word: "Never use a Harness if it is not
  opensourced," and "Either these people are honest and deserve your
  trust and business, or they don't." This is a distinct trust axis from
  the skill-verification badge already proposed above (which scores
  whether a skill's *claims* are evidence-backed): this is about whether
  a skill or automation's *behavior* — what it reads, writes, and calls
  — is disclosed up front, before install.
- What: every skill and automation in alexandria's paid library ships
  with a short, checkable line stating what it reads (e.g. repo files,
  claim graph), what it writes (e.g. nothing, a report file), and what
  it calls externally (e.g. no network calls, or a named API). Same
  spirit as a mobile app permissions label, sized to a skill file.
- First step: define the label as a small, required frontmatter block
  (read/write/network) alongside the `shelf`/`summary` fields already
  proposed above, so the skill agent fills it in at extraction time
  rather than bolting it on later.
- Cost: $0.
- Status: proposed
### 2026-09-18 — Bind MCP access tokens to their audience (engineer agent)

- Trigger: while fixing the redirect-URI gap (sprint 2026-09-21 item 1),
  read the MCP authorization spec end to end. It states as a MUST that
  "MCP servers MUST validate that access tokens were issued specifically
  for them as the intended audience," per RFC 8707, and that clients MUST
  send a `resource` parameter on both the authorization and the token
  request. alexandria's access tokens carry `{"typ": "access"}` and
  nothing else. Any token this server's own JWT secret signs and typed
  `access` opens `/mcp`, whatever it was minted for.
- What: record the `resource` parameter at `/authorize`, carry it into the
  code and the access token as an `aud` claim, and have the bearer guard
  reject a token whose `aud` is not this server's canonical URI. Advertise
  the canonical URI in the protected-resource metadata that already
  exists. Today the exposure is small, because one secret signs one
  server's tokens and nothing else uses it. It stops being small the day a
  second Modal surface shares the `JWT` secret, which the public read-only
  MCP proposal in this ledger would do.
- First step: one session. Add `aud` to the mint and one check in the
  guard, extend tests/test_oauth_redirect_uri.py with a
  wrong-audience case, and keep accepting audience-less tokens for one
  release so the owner's live connector does not drop mid-flight.
- Cost: $0
- Status: proposed

### 2026-09-18 — Scope the MCP tools, so a stolen token cannot open a PR (engineer agent)

- Trigger: the security seat's own finding named the blast radius
  precisely: a stolen token pair reaches "PR-opening tools." Today's fix
  closes the theft path it described, but it does not shrink what a token
  is worth once taken. Every access token this server mints reaches every
  tool, so `semantic_search` and `propose_change` sit behind the same
  bearer check. The MCP spec spends a whole section on this, and expects
  a server to answer an under-scoped request with 403 plus a
  `WWW-Authenticate: Bearer error="insufficient_scope", scope="..."`
  header naming what the operation needs.
- What: two scopes, `corpus:read` for the five retrieval tools and
  `repo:propose` for `propose_skill` and `propose_change`. Mint the scope
  set into the access token, check it per tool, and advertise
  `scopes_supported` in the protected-resource metadata so a client asks
  for the smaller set first. A read-only client then holds a token that
  cannot write to the repository at all, which is the shape the public
  read-only MCP proposal in this ledger needs anyway.
- First step: one session, on top of the audience work above, since both
  touch the same mint and the same guard. Scope enforcement lands per
  tool; the spec's step-up flow can wait.
- Cost: $0
- Status: proposed

### 2026-09-18 — Nothing runs the repo's tests (engineer agent)

- Trigger: this run added `tests/` and `requirements-dev.txt`, the repo's
  first Python tests, and had to `pip install fastapi httpx
  python-multipart pytest` by hand to run them. They pass, and four of
  them fail against the pre-fix behaviour when the check is stubbed out,
  which is the whole point of having them. But nothing runs them on a PR,
  so the next change to `mcp/oauth_flow.py` gets no warning at all.
- What: one GitHub Actions job on pull requests touching `mcp/`,
  `pipeline/`, or `tests/`: install `requirements-dev.txt`, run
  `python3 -m pytest tests/ -q`. Free on a public repo, seconds per run.
  This is the same job the skill seat's "run the trigger test in CI"
  entry above wants for `skills/`, and both should land as one workflow
  file rather than two.
- Blocked on an owner decision already pending: no seat's token can push
  a workflow file until the GitHub App's `workflows` permission is
  granted (docs/sprints/pending.md, owner-only items 5 and 13). That is
  the only thing standing between this entry and a first step.
- First step: once the permission exists, one workflow file, one session.
- Cost: $0
- Status: proposed

### 2026-09-18 — Craft scan: Anthropic's MCP connector platform (modelcontextprotocol.io)

- Scanned: the MCP authorization specification's draft pages, as the
  standard alexandria's own connector is judged against. Chosen because
  this run rebuilt that exact surface, and because the platform is the
  distribution channel the $20 spine actually arrives through: a builder
  does not visit alexandria, a builder adds a connector.
- Worth stealing: the spec treats a token's blast radius as a first-class
  design question, not an afterthought. It expects a server to answer an
  under-scoped call with 403 and a header naming the scopes that call
  needs, so the client can ask for exactly those and no more. alexandria
  mints one all-powerful token. Both of the entries above came out of
  this, and the scoped-token one is the one that matters: it is what lets
  a public read-only corpus exist next to the owner's writable one
  without a second server.
- Where alexandria is better: the spec stops at the door. It standardises
  who may knock and never says anything about whether what is behind the
  door is worth reaching, which is the honest division of labour for a
  protocol. alexandria's answer to that second question is the claim
  graph, so a tool call comes back with edges and claim ids a caller can
  follow, not prose it has to trust. Most connectors on this platform
  wrap an API and return whatever it returned. The retrieval is the
  product here, and the protocol is the doorway.
### 2026-09-19 — Wire the digest email template into the send path (frontend, for the engineer)

- Trigger: the owner's order of 2026-09-19, relayed by the chair. "The daily
  sample does not look like a newsletter. Also i want it sent via email,
  theres no design otherwise." `site/emails/digest.html` and its slot
  contract in `site/emails/README.md` ship in the frontend PR of the same
  date. Nothing sends through it until the pipeline fills it, and filling it
  is engineer's lane, so this is the handoff.
- The exact insertion point: `send_newsletter()` in `pipeline/weekly.py`,
  the `html = (` assignment at line 363 on main and line 552 on PR #35's
  branch `engineer/2026-09-19-daily-digest`. That one statement, which wraps
  `html_body` in a Georgia serif div, is the whole change. It becomes a read
  of `/root/site/emails/digest.html` and a fill. Everything around it stays:
  the multipart message, the plain-text part, the subscriber loop.
- One more line, in the image definition: `.add_local_file("site/emails/
  digest.html", "/root/site/emails/digest.html")` next to the existing
  `prompts/digest.md` line, `weekly.py` line 51 on main and line 67 on the
  PR #35 branch. Without it the file is not in the container.
- It covers the daily too, with no second change. PR #35 renamed the function
  to `digest()` and branches on `kind_for(today)`, but both kinds still send
  through the one `send_newsletter()`. Wiring the template there wires both.
  The template's sections are generic, so an issue's H2s become its sections
  whatever they are called.
- Already correct, and worth not breaking: the subject line is the issue's
  H1 (lines 376 to 378 on main), which is the owner's "the subject is the
  title, and the title is a finding".
- `docs/design/reviews/2026-09-19/render_sample.py` is a working filler,
  standard library plus `markdown`, both already in the Modal image. It parses
  the digest markdown into the slots and it is the file to lift or to read,
  not a file to import from `docs/`.
- The one open dependency: `{{unsubscribe_url}}`. There is no unsubscribe
  endpoint, so the honest value today is a `mailto:` to the sending address
  with an unsubscribe subject, which is what the current email means when it
  says "reply to this email". The real endpoint is already an idea in this
  file from PR #35 and should land before the list outgrows twenty people.
- Two fill-time details the template assumes, both verified at 3x on
  2026-09-19: values arrive HTML-escaped, and narrow no-break spaces (U+202F,
  30 of them in 2026-W37 alone) are normalised, because Helvetica draws them
  so tight that "Claude Opus 5" reads as "ClaudeOpus5" in a mail client.
- Cost: $0. No new dependency, no new service, no new font.
- Status: proposed

### 2026-09-19 — The writing model emits narrow no-break spaces (frontend observation, for the writer)

- What: `site/content/issues/2026-W37.md` contains 30 U+202F narrow no-break
  spaces, inside names ("Claude Opus 5", "122 B") and before percent signs
  ("23.9 %"). English takes no space before a percent sign, and the tight
  gaps inside names are a legibility bug in any client that renders U+202F
  faithfully. Screenshots: `fix-narrow-space-3x-before.png` in this date's
  review folder.
- The email template's filler normalises them so the delivered issue reads
  correctly, but the database row, the site and the plain-text part still
  carry them. The fix at the source is a line in the digest prompt.
- Whose call: the writer seat owns `prompts/digest.md` and `prompts/daily.md`.
  Filed here rather than edited.
- Status: proposed
## Engineer agent findings (2026-09-19, sprint 2026-09-21 item 3)

### 2026-09-19 — Keep every digest body, not one row per week (engineer agent)
- Trigger: the accuracy audit
  (docs/evals/2026-09-19-digest-accuracy-audit.md) tried to answer the
  owner's question of how many issues have gone out and could not. Git
  history holds nine materially different bodies for 2026-W37, generated
  2026-09-08 and 2026-09-11, ranging from 4,897 to 10,237 bytes. Every one
  overwrote the last, because `pipeline/weekly.py` upserts with
  `on conflict (week) do update set body = excluded.body`. The Monday
  2026-09-14 cron overwrote it again, since `weekly()` labels a run with
  yesterday's ISO week and Sunday 2026-09-13 is still week 37. The
  `digests` table calls itself the database of record and holds one row,
  the last write. Nothing in the system knows which text a subscriber
  actually received.
- What: make `digests` append-only. Drop the unique constraint on `week`,
  add `sent_at` and `recipient_count` written by `send_newsletter` after
  the SMTP loop returns, and read the archive off the most recent row per
  week that has a `sent_at`. The row that went to readers is then a
  different and knowable thing from the row a rerun produced. This is the
  precondition for every future audit: without it, item 3 is unanswerable
  by construction, not by accident.
- First step: the migration in `db/schema.sql` plus the two new columns
  written at the end of `send_newsletter`. The read path can keep using
  the newest row until the site is pointed at the sent one.
- Cost: $0
- Status: proposed

### 2026-09-19 — Bind every digest claim to a link, including the graph sections (engineer agent)
- Trigger: the same audit. Ten "Gaining traction" lines and three "Left
  behind" lines in 2026-W37 shipped with no link, no title and no
  identifier, thirteen claims a reader cannot check. Three were traced to
  their papers by hand this run and all three were accurate, so the
  content is not the problem. The presentation is: the issue asks for
  trust on the sections where it offers the least evidence, which is
  exactly backwards, and it is the part of O1 KR3's evidence floor the
  digest currently skips.
- What: carry the paper link through into the two graph-derived sections
  the way the Trailblazing items already do. The claim graph knows the
  supporting papers for every edge it emits, so this is a change to what
  `gather()` puts in the payload and to what `prompts/digest.md` requires
  of each line, not new data. Pair it with
  `tools/check_issue_citations.py` as a pre-send gate so an issue with an
  unresolvable or misnamed link never leaves the pipeline.
- First step: add the supporting paper's title and url to the
  `gaining_traction` and `deprecated` rows in `gather()`, then make the
  prompt require them per line.
- Cost: $0
- Status: proposed

### 2026-09-19 — Ask Semantic Scholar for the field it already gives us free (engineer agent)
- Trigger: today's craft scan, below. `check_citations` in
  `pipeline/weekly.py` requests `fields=citationCount` from the S2 batch
  endpoint. The same request, same quota, same latency, also returns
  `influentialCitationCount`, which is S2's own judgment of which citing
  papers build on a work rather than mention it in passing.
- What: add the field to the existing request and log it alongside
  `citations` in `citation_log`. A paper going from 40 to 60 citations
  with zero influential ones is noise. A paper going from 4 to 9 with
  five influential ones is the "gaining traction" signal the digest
  claims to report and currently approximates with our own support-edge
  count. One field name in one existing call, and a column.
- First step: `fields=citationCount,influentialCitationCount` in
  `check_citations`, plus the column in `citation_log`.
- Cost: $0
- Status: proposed

### 2026-09-19 — URGENT: an uncited claim about a named product is live on the site (engineer agent)
- Trigger: the audit. The archived 2026-W37 issue states that "Claude
  Opus 5 under Claude Code solves only 23.9 % of simulations", with no
  link, no paper title and no identifier. Targeted arXiv searches this
  session did not locate the source. It is almost certainly a real edge
  from our own corpus, since the corpus is where it came from, but the
  claim graph was unreachable this session and nothing on the public page
  lets a reader or a lawyer check it. The neighbouring bullet in the same
  section contradicts a claim the issue never made, which suggests that
  whole block rendered from edges the writer did not fully resolve.
- What: identify the paper and add the citation, or cut the line from the
  archive. This needs one `sql_query` against the claim graph, which is
  thirty seconds of work for any seat that has `NEON_RO_URL`, and it is
  not a judgement call this seat should make unilaterally on live copy
  about a named commercial product.
- First step: query the claim graph for the 23.9 % edge and its papers.
- Cost: $0
- Status: urgent

### 2026-09-19 — Craft scan: Semantic Scholar's Graph API (semanticscholar.org)
- Scanned: the free Graph API's `paper/batch` endpoint, live, against a
  paper this run had just audited. Chosen because the day's work was
  citation provenance, and S2 is both the closest thing to a public claim
  graph and already a dependency in `pipeline/weekly.py`.
- Worth stealing: they publish a judgment, not just a count.
  `influentialCitationCount` separates citations that build on a paper
  from citations that name it, and they give it away in the same call we
  already make for `citationCount`. Filed as its own ledger entry above.
  The wider lesson is the one alexandria keeps rediscovering: the
  valuable layer is the opinion on top of the data, and S2 charges
  nothing for theirs because their product is the graph.
- Better here: their summarisation is unattended and it shows. The
  `tldr` returned for the T1 paper this run ends "rewarded by executing
  each task's own verifier by executing each task's own verifier", a
  duplicated clause shipped straight to callers. More to the point, S2
  will tell you a paper is influential and never tell you what it says
  that you should do differently on Monday. The distill step's claims
  with their procedures are a different artifact, and the audit above
  confirms they are accurate where they copy the paper. The gap is not
  our synthesis, it is our provenance.
### 2026-09-19 — Sanitize the issue body before it renders as HTML (security agent)
- Trigger: the 2026-09-19 audit. `site/app/library/[week]/page.jsx` passes
  the issue body through `marked.parse` into `dangerouslySetInnerHTML`,
  and `marked` has not sanitized HTML since v8, so raw HTML in the body
  reaches the page intact. The body is written by gpt-oss-120b in
  `pipeline/weekly.py` from claims distilled out of arXiv abstracts and
  full text, which anyone can write. The chain from a crafted passage in
  a paper to live HTML on alexandr.ia has no human in it.
- What: sanitize on the way out. Either run the parsed HTML through a
  sanitizer before rendering, or configure the renderer so raw HTML in
  the source is escaped rather than passed through. The same sink exists
  on `/skills` and `/desk`, and both take bodies a human merged, so they
  are lower priority but belong in the same change for consistency.
- First step: decide sanitize-on-write (in `pipeline/weekly.py`, before
  the row lands in `digests`) or sanitize-on-render (in the route). On
  render is safer, because it also covers rows already in the database.
- Cost: $0, one small dependency.
- Whose call: the engineer, with the frontend seat, since it is the
  rendering path.
- Status: urgent

### 2026-09-19 — Pin the embedding model, and stop sharing its cache with the MCP server (security agent)
- Trigger: the owner's incident 19 dispatch and the 2026-09-19 audit.
  `pipeline/distill.py` and `mcp/server.py` both load
  `Qwen/Qwen3-Embedding-0.6B` with no pinned revision, into one Modal
  volume (`hf-cache`) that both mount read-write. The internet-facing
  MCP server can therefore write into the cache the nightly pipeline
  loads from, and nothing verifies what comes back out. No exposure is
  suspected: our first download postdates the closed intrusion by eight
  weeks and the model repo has no commit inside the window. The gap is
  forward-looking.
- What: five changes, described in full in `docs/security/upstreams.md`.
  Pin `revision="97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3"` in both
  files. Move `EMBED_MODEL` and the new revision constant into one
  shared module, because the two files must never disagree and every
  vector in the database has to come from one model. Record and verify
  the safetensors SHA-256. Set `HF_HUB_OFFLINE=1` once the cache is
  warm. Split the volume, or mount it read-only in the MCP server, which
  only ever reads it.
- First step: the pin. It is four lines and it is the whole of the
  high-value part.
- Cost: $0.
- Whose call: the engineer.
- Status: urgent

### 2026-09-19 — Pin the agent image to a digest, not `latest` (security agent)
- Trigger: the 2026-09-19 audit. The engineer and frontend seats run
  `ghcr.io/alexandrapaiz/alexandria-agent:latest`, a mutable tag. We
  build the image ourselves, so this is not third-party supply chain
  risk, but `latest` means neither seat can say which image it ran, and
  a bad build silently becomes the next run's environment. Two frontend
  runs on 2026-09-19 died on a uid mismatch introduced by an image
  rebuild, which is exactly the failure mode a digest makes legible.
- What: `build-agent-image.yml` emits the pushed digest, and both
  container workflows reference `alexandria-agent@sha256:...`. Bumping
  the digest becomes an ordinary PR, which is the same posture as the
  action SHA pinning already in the ledger from 2026-09-18.
- First step: it is the same blocker as action pinning, being the
  GitHub App `workflows` permission from ADR-27. Land both together.
- Cost: $0.
- Whose call: the engineer, after the App handover.
- Status: proposed

### 2026-09-19 — Instrument the repository as the declared inter-agent channel (security agent)
- Trigger: the 2026-09-19 audit's answer to the owner's sandboxing
  question. The Hugging Face incident's agents coordinated through a
  shared package cache that nobody had declared as a communication
  channel, and the CSA post mortem's governance recommendation is to
  define which forms of inter-agent coordination are permitted,
  instrument the permitted channels, and treat any undocumented channel
  found in production as a security incident. Alexandria already has a
  deliberate inter-agent channel, being `docs/agents/incidents.md`,
  `docs/agents/learning-log.md`, `docs/ideas.md`, and each other's open
  PRs, and the seats use it constantly. Ours is documented, append-only,
  and human-gated at merge, which is most of the recommended posture.
  The missing clause is the last one.
- What: one paragraph in the ExO charter naming the repository as the
  only sanctioned channel between seats, and making any other channel a
  discovery that gets recorded in the incident register. That is the
  whole change. It costs nothing and it means the next time a seat finds
  an unexpected shared surface, the response is already written down.
- First step: the ExO decides whether this belongs in her charter or in
  the playbook.
- Cost: $0.
- Whose call: the ExO. Charters are not this seat's to edit.
- Status: proposed
### 2026-09-19 — The 60-day backfill rule silently writes off unread papers
- Trigger: found while sizing the triage backlog for the URGENT dispatch.
  `BACKFILL_DAYS = 60` in `pipeline/triage.py` auto-marks any untriaged paper
  older than 60 days as `index` with `model = 'rule:backfill'`, and
  `distill_queue` in `db/schema.sql` explicitly excludes `rule:backfill` rows.
  So a paper that waits 60 days in the queue is not just late, it is
  permanently excluded from ever producing a claim, and it leaves the queue
  without anyone deciding anything about it.
- What: the rule is correct for what it was written for, the one-time
  historical import, where spending model budget on old blog archives would be
  waste. It is wrong for a live firehose that is behind, which is what we now
  have. The 2,445-paper backlog is not sitting still; it is aging out at
  roughly the rate it arrived. Two candidate fixes, and the choice needs the
  owner because it is a judgment about what "we read the field" means: either
  exempt papers whose `ingested_at` is recent (age the rule off ingestion, not
  publication, so the rule only catches genuine historical imports), or keep
  the rule and record the write-off honestly with a distinct decision value so
  the digest can say how much it did not read.
- First step: a one-line query against `papers` joined to `triage_log` for how
  many rows already carry `rule:backfill` while having been ingested by the
  live firehose. That number is either small, and this is a future problem, or
  large, and the corpus is already quieter than it looks.
- Cost: $0.
- Status: proposed

### 2026-09-19 — Read the Groq 429 body before guessing at throughput
- Trigger: the triage fix shipped today makes the drain fair but not faster,
  and there are three free ways to make it faster which are mutually exclusive
  in what they imply. Raising `BATCH` helps if the limit is per-request; it
  does nothing if the limit is per-token. Shortening the 1,500-character
  abstract slice helps if the limit is per-token; it costs triage quality for
  nothing if the limit is per-request. Nobody has read the 429.
- What: run `modal app logs alexandria-triage`, read what the 429 body says,
  and write the answer into `docs/product/triage-capacity.md` where the three
  branches are already spelled out. Then take the branch it names. This is
  perhaps ten minutes of work that decides whether the backlog is a budget
  problem or a batching problem, and the pipeline has been guessing about it
  for its whole life.
- First step: the log read itself. It needs Modal credentials, which the
  engineer seat's GitHub Actions runner does not carry, so this is the chair's
  or the owner's to run, or it needs a Modal token available to this seat.
- Cost: $0.
- Status: urgent

### 2026-09-19 — Every queue view should log its depth per partition
- Trigger: the tier starvation fixed today was invisible for the pipeline's
  entire life, and it took a research seat querying Neon by hand to find it.
  The triage cron printed how many papers it triaged and never once printed how
  many were waiting, so a run that read 20 papers out of 2,445 and a run that
  read 20 out of 20 produced identical-looking logs.
- What: the blackboard design (ADR-9) gives every worker a queue view, so the
  same blind spot exists in `distill_queue`, `interpret_queue` and the digest's
  own inputs. Add the one-line depth log this change added to triage to each of
  them, partitioned by whatever dimension that queue could starve on (tier for
  distill, source for interpret). The rule worth adopting: a worker that drains
  a queue must log the depth of the queue it did not drain.
- First step: `pipeline/distill.py`, the same three-line query and print this
  PR added to `pipeline/triage.py`.
- Cost: $0.
- Status: proposed

### 2026-09-19 — Competitive scan: Elicit's screening step
- Elicit's paper screening puts its inclusion and exclusion criteria in front
  of the user as an editable list, then shows, per paper, which criterion
  decided it. The screening is the product surface, not a hidden preprocessing
  step.
- **Worth stealing:** we already have this data and throw it away. Every
  `triage_log` row carries a decision, a score and the model's reasoning, and
  none of it is visible anywhere. A page that showed what the pipeline read
  this week and why it discarded most of it would be the most honest thing on
  the site, and after today's fix it would finally show more than one feed.
  Filed here rather than built because it is a site change and belongs to the
  frontend seat's lane.
- **Where alexandria is better:** Elicit screens a corpus you bring to it. The
  screening quality is bounded by your search query, so a blind spot in the
  query is a blind spot in the result and nothing tells you it is there.
  alexandria screens a standing firehose against standing sources, which means
  its blind spots are properties of a checked-in file, `sources.yaml`, that a
  research seat can audit and diff. Today's finding is the case in point: the
  blind spot was real, and it was findable, and it was fixable in one file,
  because the corpus is ours rather than a query's leftovers.
### 2026-09-19 — Signal feeds are routed by a triage prompt that has never heard of them (ExO finding)

- Trigger: the coherence audit of the four ecosystem patches merged on
  2026-09-19, ordered by the owner after incident 19.
- The contradiction, stated plainly. Three places now say that signal
  sources never become claims: the research charter ("news, RSS feeds,
  and releases are ATTENTION SIGNALS ... never become claims"), the
  design agreed in docs/backlog.md ("signal sources are never distilled
  into claims"), and the new comment in sources.yaml itself ("never
  laundered into claims"). The pipeline does not implement any of it.
  The four new feeds, `hf-blog`, `openai-blog`, `deepmind-blog` and
  `hn-frontpage`, were added to the same `feeds:` list as everything
  else with `tier: d`, so `ingest.py` writes them into `papers` and
  `triage.py` hands them to `prompts/triage.md`, which has exactly one
  special rule and it is for `gh-*` release feeds. A Hacker News
  front-page item is therefore judged as if it were a paper, and
  nothing stops it being routed to `distill` or `deep_read`.
- Second, smaller inconsistency in the same commit: the sources.yaml
  comment says triage "routes technical substance to index and news-only
  items to discard," which is a behavior nobody implemented, in a file
  that cannot cause behavior. A comment describing a routing rule
  belongs in the triage prompt, which is where routing happens.
- Third: `hnrss.org/frontpage` entries carry a comments-link blob as
  their summary rather than an abstract, so `ingest.py` line 65 will
  store that blob as the abstract and triage will judge the item on it.
  Worth one look before the next ingest run.
- What: the `role:` field the backlog already designed, wired for real.
  `role: signal` on the four new feeds plus the 19 existing blog and
  release feeds, `role: evidence` on arXiv and HF daily papers, a
  `roles` default of evidence so nothing breaks on the way in, and one
  paragraph in `prompts/triage.md` saying that a signal-role item is
  `index` at most unless it contains a technique or a measurement, in
  which case it is `distill` on the same evidence bar as a paper. That
  last clause matters and should not be dropped: the research charter's
  coherence fix of 2026-09-19 turns on the difference between the report
  of an event, which is never evidence, and an artifact with method,
  which is admissible whatever feed carried it. The published Hugging
  Face postmortems are the case that proves it.
- Cost: $0. One field in a yaml file, one filter in ingest or triage,
  one paragraph in a prompt.
- Whose call: the engineer's, since sources.yaml, `pipeline/` and
  `prompts/triage.md` are all outside this seat's writable surface.
  Filed rather than fixed for that reason.
- Status: proposed

### 2026-09-19 — The org chart is missing a seat (ExO finding, for the PM)

- Trigger: §5b upkeep during the 2026-09-19 ExO run.
- What: `docs/agents/org-chart.md` lists nine active seats and two
  dormant ones. The writer seat is neither. It has a charter at
  `prompts/writer-agent.md`, a workflow at `.github/workflows/agent-writer.yml`
  running daily at 16:00 UTC after the digest publishes, an ADR at
  ADR-28, two successful runs on 2026-09-19, and an open PR at #36. The
  org's own chart of itself has been missing a working seat since that
  seat was created. README is already fixed in open PR #39, which takes
  the count to twelve and adds the writer row, so the chart is the last
  stale copy.
- Why it is filed here rather than fixed: the chart's header says the PM
  maintains it under charter §1b, and quietly editing another seat's
  living document is how two seats start disagreeing about the truth.
- The smaller point worth carrying into that edit: this is the same
  shape as incident 19 in miniature. Nobody was wrong, and the org's
  self-description drifted from the org anyway, because keeping it true
  is a duty whose failure is silent.
- Cost: $0, one row and one count.
- Whose call: the PM's.
- Status: proposed
### 2026-09-19 — ExO cross-seat flags (four surfaces, none of them this seat's)
- Trigger: the ExO run's §5b housekeeping pass over the GitHub home.
  Filed rather than edited, because each belongs to another seat.
- What, in order of how wrong each is today:
  - **`docs/agents/org-chart.md` is missing the writer seat and calls
    finance dormant.** ADR-28 created the writer seat and it has run
    twice (35417517511, 35419120149). The finance seat ran once on
    dispatch (35410872874) and opened PR #32. The file is the PM's by
    charter §1b, so the PM updates it, not this seat.
  - **The ExO seat should be the next one containerized.** Its §5b duty
    is to render any mermaid it changes before shipping it, which needs
    a browser. On the uncontainerized runner that costs a download and
    then fails anyway on the Chromium sandbox until `--no-sandbox` is
    passed by hand, which this run had to do. The image already bakes
    Chromium at a fixed path. One workflow edit, and the seat can do its
    own job. Whose call: the owner, since no seat can push a workflow.
  - **`pm/sprint-2026-09-14` is a stale remote branch** carrying PR #1,
    which was closed without merging. Not deleted by this run, because
    deleting an unmerged branch destroys work and the call is the PM's.
  - **There is no ADR for Stage 1 containerization.** The Dockerfile's
    own header says "ADR pending". Decisions of this size belong in
    docs/decisions.md, and recording an owner decision is the chair's
    job rather than this seat's.
- Cost: $0 for all four.
- Status: proposed
- **Merge order, per the ledger-collision rule.** Five other open PRs
  append to this file: #28 (market), #29 (engineer), #31 (security), #35
  (engineer), #36 (writer). Every one of them appends at the end, so
  whichever merges second onward conflicts textually. This note is the
  cheapest of the six to re-apply by hand, so merge it last.

### 2026-09-19 — The `Enforced at:` line belongs on the voice and design registers too (ExO finding)

- Trigger: the enforcement-gate audit ordered by the owner after
  incident 20. Every register the org keeps was mapped to the place its
  rules are actually checked, in docs/agents/registers.md.
- What: the audit established one cheap invariant, that every register
  carries an `Enforced at:` line near its top naming the charter and
  step that checks artifacts against it. A register that cannot name one
  is documentation and says so, which makes the gap visible by grep
  instead of by postmortem.
- The seven registers under docs/agents/ carry the line as of this PR.
  Five do not, and none of them are this seat's to edit:
  - `docs/voice/canon.md`, `docs/voice/ban-list.md` and
    `docs/voice/taste.md`, the writer's surface. The enforcement itself
    already shipped, in the writer's charter, which now runs a
    taste-compliance pass as its first grading gate. What is missing is
    only the marker line.
  - `docs/design/canon.md`, `docs/design/ban-list.md`,
    `docs/design/taste.md` and `docs/design/motion.md`, the frontend's
    surface, same situation.
  - `docs/agents/org-chart.md` and `docs/agents/frameworks.md`, the
    PM's. Both are genuinely enforced at the PM's own steps, so the line
    is a one-line confirmation rather than a fix.
- Whose call: the writer seat, the frontend seat and the PM, each in
  their own next run. One line each.
- Cost: $0.
- Status: proposed

### 2026-09-19 — A CI job could make the register checks mechanical (ExO proposal, not built)

- Trigger: the honest limit at the end of the incident 20 postmortem. A
  charter line is an instruction to a model, not a gate a runner
  enforces. This run moved the rules from files nobody opens into files
  every seat opens, which is real and is not enforcement.
- What: a GitHub Actions check on pull requests that greps the diff for
  the cheap, mechanical entries in the ban lists and taste registers,
  and fails when an artifact violates one. The genuinely checkable subset
  is small and worth having anyway: the printed framework names
  ("Gaining traction", "Trailblazing", "Left behind", "Read these
  yourself" as headings), the stylistic em dash, the semicolon join, and
  the named ban-list buzzwords.
- Why it is filed rather than built: a CI job is a runtime change under
  docs/agents/runtime-changes.md, so it needs a smoke test on a throwaway
  branch and the owner's merge. It is also a workflow file, which no
  seat's token can push.
- Whose call: the owner, with the engineer implementing.
- Cost: $0, GitHub Actions minutes on a public repo.
- Status: proposed

- **Merge order for these two entries.** They append at the end of this
  file, like every other open PR's ledger note. PR #45 merges after #39
  and #43, whose notes are above, and it already carries both of them,
  so only the seats' PRs (#28, #29, #31, #35, #36) conflict here. These
  two are cheap to re-apply by hand, so merge them last.
### 2026-09-19 — ASCII normalization is a function, not a paragraph (writer seat, run 5)
- Trigger: 2026-W37 shipped 87 non-breaking hyphens, 19 narrow no-break
  spaces and a multiplication sign, so the prompt grew a punctuation
  rule (ban list 13) and the reread gate grew a punctuation check. Both
  are a 120B model policing its own keystrokes, which is the weakest
  enforcement available for the one defect class that needs no judgment
  at all.
- Proposal: normalize in code between generation and the insert into
  `digests`. U+2011 to `-`, U+202F and U+00A0 to a space or nothing
  before `%`, U+00D7 to `x`, curly quotes to straight. Unlike the
  heading gate filed under run 3, this one should fix silently rather
  than fail the run: there is exactly one correct output for each
  character, so failing would cost an issue to save a substitution.
- Why it is worth the few lines: it is deterministic, it is untestable
  by prose review, and every character it fixes is one the reader's
  search box and the agent loading the issue currently miss.
- Whose call: the engineer's. The prompt rule stays either way, because
  the daily may not run through the same code path.
- Status: proposed

## Research agent findings (2026-09-19, run b — owner's off-schedule dispatch)

Full charter run against the live corpus (`NEON_RO_URL` set). Every item
below is reproducible from Appendix A of
[docs/research/briefs/2026-09-19-b.md](research/briefs/2026-09-19-b.md).
The "all claims come from hf-daily" finding is PR #34's and is not
re-claimed here; these are additive to #34 and #42 and engineer PR #44.

### 2026-09-19 — The tier c/d index ceiling: feeds have never produced a claim
- Trigger: the epitome acceptance test (incident 21) re-run and still
  failing. Best similarity 0.562 ("agent identity and portability") and
  0.543 ("frameworks and credential security"), with no identity,
  delegation, credential or portability result in either top-8.
- The measurement: triage has decided 1,464 tier `c`/`d` papers all time
  and routed **100% of them to `index`**. Zero have ever become a claim.
  That is separate from the tier `a` priority inversion PR #44 fixes —
  those papers were read and decided, not skipped.
- Why it matters: `semantic_search` searches claims only, so `index` means
  invisible to the agent-facing product. Incident 21's same-day
  remediation added three tier `d` identity feeds; under the current
  ceiling they cannot produce a single claim, before or after #44 merges.
  Searching against `papers.embedding` confirms it: every nearest paper on
  every identity phrasing tried is `distilled = false`, including
  "Securing the future of AI agents" and "LangSmith LLM Gateway: runtime
  governance". The material is reached and declined, not missed.
- The tension is in the charter, not the pipeline: it says feeds are
  attention signals that "never become claims, because a headline is not
  evidence," and also that "identity standards qualify alongside papers
  when they carry real technical substance." Both cannot hold for a SPIFFE
  spec.
- Whose call: the owner's. This is the ruling that unblocks the mission's
  first live user failure; no prompt or source diff should precede it.
- Status: proposed

### 2026-09-19 — gh-spiffe is a permanently empty feed that passes a 200 check
- Trigger: verifying the dispatch's claim that the interop feeds are flowing.
- The measurement: `https://github.com/spiffe/spiffe/releases.atom` returns
  **HTTP 200 with zero entries** — `spiffe/spiffe` holds the specification
  and cuts no GitHub releases. Incident 21 records these feeds as "all
  verified live," which is what a status-code check reports.
- Fix, verified 2026-09-19: `https://github.com/spiffe/spire/releases.atom`
  → 10 entries. A2A (10), MCP spec (9), HF blog (862) and HN (20) are
  genuinely fine and will flow at the next deploy.
- Also in `sources.yaml`: `openai`/`openai-blog` and `deepmind`/`deepmind-blog`
  are duplicate URLs at conflicting tiers (`c` and `d`). Ingest dedupes by
  URL so the `-blog` twins are inert, but the file misreports its coverage.
- Not proposed as a diff this week: PR #42 already edits `sources.yaml` and
  a second diff only creates a conflict. For whoever merges #42.
- Whose call: the engineer's, alongside #42.
- Status: proposed

### 2026-09-19 — Merging sources.yaml or prompts/*.md does nothing until someone deploys
- Trigger: asking why feeds added to `main` at 11:31 and 13:41 today had
  produced no rows.
- The measurement: `pipeline/ingest.py:23` bakes `sources.yaml` into the
  Modal image with `add_local_file`, and every prompt is baked the same way
  (`triage.md`, `distill.md`, `interpret.md`, `digest.md`, `rag-answer.md`).
  `grep -rl "modal deploy" .github/` returns nothing — no workflow deploys
  the pipeline.
- Why it matters: `sources.yaml` and `prompts/*.md` are exactly the ADR-12
  whitelist. The self-improvement channel ADR-7 describes terminates at a
  manual `modal deploy` that is written down nowhere, so every meta-review
  proposal this seat has ever merged may still be inert. Under the vision's
  autonomy tiebreak this outranks most of what is in flight.
- Whose call: the engineer's and the chair's.
- Status: proposed

### 2026-09-19 — 29% of claims have no embedding and are invisible to search
- The measurement: 158 of 543 claims have `embedding is null`, and every
  one was created between 2026-09-17 and 2026-09-19. Before 09-17 the rate
  is zero, so this is a regression in the distill run's embedding step, not
  a backlog.
- Why it matters: unembedded claims cannot be returned by `semantic_search`
  and cannot be reached by `interpret`'s neighbour query, so they draw no
  edges. The corpus is silently three days stale to its own agent-facing
  surface, which compounds the epitome failure above. It also means the
  `discovery_report` novelty signal is computed blind to the newest claims.
- Whose call: the engineer's. Backfill, then re-run novelty.
- Status: proposed

### 2026-09-19 — The digest's traction section counts papers citing themselves
- The measurement: as of the 2026-W37 digest's publication, **8 of its 10
  "Gaining traction" items had zero external support** — every supporting
  edge came from the same paper as the claim. C73 and C34 were 3-for-3
  self-supporting. Only C4 (Iris) had a meaningful external majority.
- Cause: `weekly.py:170-181` counts every `supports` edge with no origin
  check. The guard already exists twelve lines above, in the `superseded`
  query: `old.paper_id != new.paper_id`, commented "a paper refining itself
  is not a supersession." It was never applied to `supported`.
- Vision §1 defines that section as claims "accepted by the community," so
  this is a product-quality defect, not a cosmetic one.
- To the digest's credit, its printed counts were correct at publication;
  today's higher numbers are five more `interpret` runs, not a miscount.
- Whose call: the engineer's (one clause in `weekly.py`).
- Status: proposed

### 2026-09-19 — The interpret neighbour query has no paper boundary
- The measurement: 138 of 185 edges (75%) are intra-paper — 68/98
  `supports`, 67/81 `refines`, 2/5 `contradicts`.
- Cause, in code: `pipeline/interpret.py:78-85` selects neighbours with
  only `where id < %s`, and the prompt is built from `[id] claim_text`
  alone, so the model is never told which paper any claim came from. A
  paper's claims are distilled from one text in one batch and are each
  other's nearest neighbours by construction, so they dominate the
  shortlist.
- This is why a prompt-only fix is not enough, and it caught a mistake in
  this run's own first draft: a proposed rule saying "same paper, never
  `contradicts`" was unenforceable, because the model has no paper identity
  to check. The shipped rule asks it to infer co-reporting from shared
  system names and results-table shape instead.
- Proposed fix (engineer's, one line): add
  `and paper_id <> (select paper_id from claims where id = %s)` to the
  neighbour query. Deletes the failure class, mirrors the guard already in
  `weekly.py`, and spends the `NEIGHBORS` budget on other papers.
- Status: proposed

### 2026-09-19 — Two fabrications in the published digest
- The measurement, against the claims the items rest on:
  (a) the digest says T1 resolves 64% "surpassing **GPT-3.5-Turbo** and
  approaching Claude Opus"; claim C204 says it outperforms **GPT-5.4
  (54.8%)** and **DeepSeek-V4-Flash (56.9%)**. Neither GPT-3.5-Turbo nor
  the Claude comparison exists in the corpus. A frontier-beating result was
  published as a trivial one.
  (b) the digest ties T1 to the FEE paper as "researchers at the same
  group". FEE is Hongbang Yuan / Zhuoran Jin / Yixin Cao
  (`arxiv:2609.08404`); T1 is Junyao Yang / Yucheng Shi / Zhongzhi Li /
  Ruhan Wang (`arxiv:2609.11042`). No overlap; the relationship was invented.
- Both are generation-layer, not graph-layer: the claims are right and the
  writer departed from them. Points at `prompts/digest.md` and at the
  factual-audit work already open in PR #40.
- Whose call: the writer seat's.
- Status: proposed

### 2026-09-19 — Smaller corpus-hygiene findings
- **127 arXiv version-twin paper rows** (`arxiv:X` and `arxiv:Xv1` both
  ingested as separate rows). Claims attach to only one twin, so evidence
  is not double-counted; the cost is wasted triage calls, on the budget
  PR #44 shows is the binding constraint.
- **24 off-vocabulary topic tags** against the closed 13-tag set
  `prompts/distill.md` declares. Five are homoglyph splits using U+2011
  non-breaking hyphens: `post‑training` (3) shadowing `post-training`
  (209), plus `loop‑engineering`, `anti‑hacking`, `task‑refinement`,
  `data‑augmentation`. Any `topics`-based grouping silently drops them.
  Candidate for a future `prompts/distill.md` diff; below this week's
  higher-value target.
- **Citation velocity is not broken, it is mid-cycle.** `citation_log`
  holds 68 rows and **zero papers have a second check** (`MIN_AGE_DAYS = 7`,
  `RECHECK_DAYS = 6`, weekly cadence). The digest's "no citation movers
  were recorded this week" was a mechanism that could not yet emit, not a
  quiet week. First trajectories arrive with the 2026-09-21 run — which is
  also when the relevance law's primary instrument becomes usable.
- **Store epitome's verbatim query strings.** Incident 21 records "best
  similarity 0.69"; re-running the topic labels it quotes gives 0.562 and
  0.543. The direction is unchanged and the failure is starker, but the
  acceptance test cannot be regression-tested without the exact strings.
- Status: proposed

### 2026-09-19 — Verify the archive: the press may have printed once, not four times (engineer seat)
- Trigger: measuring incident 22. The one issue in git history is
  2026-W37, written 2026-09-08 with a 677-token generator prompt. Counted
  with `o200k_base`, every request since has asked for more tokens than
  `openai/gpt-oss-120b` allows in one request on Groq's free tier, which is
  8,000: prompt plus payload plus the 6,000-token output reservation has
  been over that ceiling since roughly 2026-09-11, and the prompt alone
  passed it today at 8,651. Incident 22 is the first run that failed
  loudly, not necessarily the first run that failed. The ledger's own note
  of 2026-09-18 says the archive "will still show only 2026-W37 the day
  2026-W38 sends," which points the same way.
- What: settle it with one query against the database of record, then act
  on the answer. `select week, created_at, model, prompt_sha from digests
  order by week;`. If W38 and W39 are absent, the newsletter has sent once
  in eleven days, subscribers have had eleven quiet days, and the honest
  next move is a catch-up issue plus a note to them rather than a silent
  resumption. The README's status checklist would also need its "weekly
  digest live" line qualified.
- Why it could not be settled today: the engineer workflow has no database
  credentials (`NEON_RO_URL` is wired into the research and skill
  workflows only), and `digests/` is gitignored, so this session could
  measure the request and not the archive. The ledger already carries the
  proposal to add `NEON_RO_URL` to `agent-engineer.yml`, filed 2026-09-18
  for a different reason. This is the second reason.
- First step: run the query. It takes a minute and it decides whether this
  is a fixed bug or an eleven-day outage.
- Cost: $0.
- Status: urgent

### 2026-09-19 — Budget every model call, not just the press (engineer seat)
- Trigger: today's fix put a token budget around the digest generator, and
  checking the other callers while doing it showed the press was only the
  loudest one. `rag_answer` in `mcp/server.py` builds its context from a
  caller-supplied `k` with no upper bound, concatenates untruncated claim
  and evidence text into the prompt, and sets no `max_completion_tokens`
  at all. An authenticated caller passing a large `k` gets a 413 back as
  "synthesis model unavailable," and a caller doing it repeatedly spends
  the day's token allowance on nothing. Triage, distill and interpret are
  in better shape because they batch at fixed sizes, but none of them
  states a budget anywhere a reader can check it.
- What: point every Groq caller at `pipeline/budget.py`, which already
  holds the published per-model limits and the arithmetic. Concretely:
  cap `k` in `rag_answer` and truncate the claim and evidence text the way
  `gather()` does, give it an explicit output reservation, and have each
  batched job assert its batch fits before it sends. The module was built
  for the press and is deliberately general, so this is wiring rather than
  new machinery.
- First step: cap `k` and add the reservation in `rag_answer`. That is the
  one caller whose request size is set by someone outside the system, so
  it is the one worth fixing first.
- Cost: $0.
- Status: proposed

### 2026-09-19 — Craft scan: AlphaSignal (alphasignal.ai)
- Trigger: the engineer seat's daily craft scan, next in the landscape
  rotation after Import AI (scanned 2026-09-18). Read with today's work in
  mind, which was deciding which items a constrained issue keeps and which
  it drops.
- What is worth stealing: AlphaSignal ranks items by reader upvotes and
  shows the count on every item, so the readers' judgment is a live input
  to what surfaces next. alexandria has no reader signal at all. Every
  ranking decision it makes, including the one the new trimmer makes when
  it drops the tail of a week's claims, comes from triage score and the
  claim graph. Those are the field's judgment, which is the right primary
  axis, and they say nothing about whether the thing we chose was worth a
  reader's Monday. A per-item signal in the email, even one link labelled
  "this one was useful," would give the selection a second axis and would
  cost a query string and a table.
- What alexandria does better: AlphaSignal ranks by attention, and
  attention cannot tell you what was wrong. An upvote feed has no way to
  say that last month's result was overturned, because nothing in its
  model of the world is a claim that can be contradicted. The "left
  behind" section is a thing alexandria can print and a feed structurally
  cannot.
- First step: one tracked link per item in the email template, writing to
  a small `item_feedback` table keyed by claim id and issue week. The
  frontend seat already owns the template (PR #37).
- Cost: $0.
- Status: proposed

### 2026-09-19 — Competitive scan: Consensus meters the expensive step, not the catalog
- Trigger: today's accounts build needed an entitlement gate, so the
  question "what exactly does a free account not get" became concrete.
  Consensus was the scan target. Its free tier does not withhold the
  corpus. Search is unlimited and free; what is metered is the expensive
  synthesis, reported as roughly 10 analyses a month free, more on Pro,
  and a separate higher tier for heavy use. Prices still disagree across
  aggregators, so treat the numbers as medium confidence, but the shape
  is consistent everywhere: a per-month allowance of the costly
  operation, refreshing, rather than a wall around the content. This
  also updates what docs/market/landscape.md records for Consensus,
  which has it as one Pro price rather than a three-plan ladder. The
  market seat owns that file, so this note is the handoff.
- What alexandria does better: the gate Consensus is defending is a
  search index, which every competitor also has. alexandria's costly
  operation produces something none of them keep, which is a claim
  graph with contradiction edges. A metered allowance on a commodity
  search is a tax on the reader. A metered allowance on "judge this
  against everything the field has said since" is a fair price for work
  that actually costs money to do.
- What is worth stealing: the free tier should be generous about
  reading and strict about computing. Today's `isEntitled` is a
  boolean, so the only paywall it can express is a wall. It cannot say
  "your tenth deep answer this month".
- First step: a `usage_log` table (clerk_id, operation, created_at) and
  a count-this-month function next to `isEntitled`, so the gate can
  return an allowance instead of a yes or no. The MCP tools are the
  first callers, since `rag_answer` is the expensive operation.
- Cost: $0.
- Status: proposed

### 2026-09-19 — The Clerk webhook has no dead letter, and its log ages out
- Trigger: writing site/app/api/clerk-webhook/route.js today. The route
  separates retryable failures from permanent ones, which is right: a
  missing DATABASE_URL answers 503 so Svix brings the event back, and an
  event with no id or email is acknowledged, because retrying it can
  never succeed. But "acknowledged" currently means a console.error and
  nothing else. On a serverless host that line is a log entry that ages
  out, so an account that silently failed to sync is unrecoverable and,
  worse, invisible. Nobody would ever know to look.
- What: one table, `webhook_events`, keyed by the `svix-id` header,
  holding the event type, the outcome, and the reason when it was
  skipped. It pays for itself twice. It is the dead-letter queue, so a
  permanently-failed event survives as a row the owner can query
  instead of a log line she will never read. And because svix-id is
  unique per event, inserting it first makes the endpoint idempotent at
  the transport layer rather than relying on `on conflict (clerk_id)`
  to absorb duplicates, which is a weaker guarantee: it dedupes retries
  of the same event, but it cannot tell a retry from a genuine second
  update.
- First step: the table, plus an insert at the top of the route after
  verification and a status update before each return.
- Cost: $0.
- Status: proposed

### 2026-09-19 — Two entitlement gates now exist and they disagree
- Trigger: today's build added `isEntitled` in site/lib/account-core.js,
  reading the `user_accounts` view by clerk_id. site/lib/entitlement.js
  already had `hasSpine`, reading `subscribers` by email. They are not
  the same check. `hasSpine` requires `tier = 'full'` and does not
  honour `comp`, so the owner's comped friends fail it; `isEntitled`
  honours comp and also reads `subscription_status`, which is where
  Polar will write once payments open. Two functions that answer "may
  this person through" and answer differently is the kind of thing that
  is fine for a week and then decides a refund argument.
- What: collapse them into one. `account-core.isEntitled` is the one to
  keep, because it is pure, it is tested, and it reads the view that
  already joins both sides. `entitlement.js` becomes a thin wrapper
  during the transition and then goes away. Its `currentEmail()` stub,
  which returns null and has a comment saying Clerk is not wired yet,
  is now false: Clerk is wired, and `currentAccount()` is the answer it
  was waiting for.
- First step: hold until PR #31 merges, since the security run is
  editing entitlement.js right now and this would collide. Then one
  commit that reroutes `hasSpine` through `currentAccount` and deletes
  the duplicate logic.
- Cost: $0.
- Status: proposed

### 2026-09-20 — The digest on WhatsApp (owner's idea)
- Trigger: the owner, 2026-09-20: "an option for the newsletter to be also sent through WhatsApp." The chair's read of why it is bigger than a delivery option: open rates on WhatsApp run far above email (industry figures cluster around 90%+ versus 20-40% for newsletters), it is the default channel across Latin America, India, and much of Europe where email newsletters underperform, and a WhatsApp channel is natively forwardable, which is distribution built into the product (the Thiel doctrine in docs/sales/distribution-plan.md). No AI research digest in the landscape does it.
- What: a WhatsApp delivery channel alongside email, opt-in at sign-up (the consent screen gains a phone field and a second checkbox). Two viable mechanisms, to be decided on evidence: (a) a WhatsApp Channel (broadcast, one-to-many, followers subscribe by link, no per-message cost, no phone numbers collected, limited formatting) for the free digest; (b) the WhatsApp Business Cloud API via a provider (Twilio or 360dialog) for one-to-one delivery with the reader's number, template-message approval required, per-conversation pricing after the free tier, which fits the paid spine and lets a subscriber reply. The writer seat owns a WhatsApp rendering of the issue (short, the first-screen promise as the whole message, links to the full issue on the site; the outsider test applies harder on a phone), the frontend seat owns the opt-in moment, the engineer owns the send path and the number.
- First step: market seat evaluates (a) versus (b) with real pricing and the compliance rules (opt-in proof, template approval, the 24-hour window), and tests whether a Channel can carry the daily without formatting loss; engineer costs the send path. Both in one brief, before anything is built.
- Cost: Channels $0; Cloud API free up to 1,000 conversations a month then roughly $0.005-0.08 per conversation by country; a dedicated business number.
- Status: proposed

### 2026-09-24 — The sectioned press: one request per section, not one per issue
- Trigger: `python3 pipeline/budget.py` on this branch, against Groq's
  free-tier limits re-read from the live docs today. Every free text
  model is capped at 8,000 tokens per minute, which incident 22 proved
  is also a per-request ceiling, and `prompts/digest.md` is 9,865
  tokens on its own. The prompt plus the output reservation is 15,865
  tokens against 6,800 usable, before one row of payload. The press
  cannot print the weekly issue in one request on any free model, and
  the three-model fallback list this run added does not change that: all
  three fail identically, because all three sit at the same ceiling.
- What: stop sending one request for a whole issue. The digest has a
  fixed section skeleton, so send one request per section, each carrying
  a shared editorial core (voice, the house rules, the masthead
  contract) plus only that section's own instructions and only that
  section's slice of the payload. Stitch the returned sections in a
  fixed order in code, the way `add_masthead` already writes the brand
  line in code rather than asking the model for it. Three effects, all
  of them wanted independently of the budget. Each request is small
  enough to fit a ceiling far below today's. A section whose payload is
  empty is skipped rather than hallucinated, which is the defect the
  writer seat's PR #62 found ("the section printed over nothing"). And a
  single section failing costs one section, not the issue, which is the
  first time this press would degrade instead of stopping.
- First step: split the generator prompt's reading, not the file. Parse
  `prompts/digest.md` into its shared preamble and its per-section
  blocks by heading, and have `budget.py` prove that preamble + the
  largest section block + that section's worst-case payload + a 1,500
  token reservation fits 6,800. That is one afternoon and it either
  works on paper or it does not, before any editorial file is touched.
  If the arithmetic holds, the second day builds the loop.
- Cost: $0.
- Status: proposed

### 2026-09-24 — Every external dependency gets an existence check, not just the press
- Trigger: incident 24's root cause, stated precisely. The budget guard
  was correct, thorough, tested, and ran three times per send. It
  checked that the request would fit and never checked that the thing it
  was fitting still existed, so a withdrawn model passed every gate the
  repo had. The press now checks. Nothing else does: `ingest.py` assumes
  arXiv's feed shape, `distill.py` assumes an embedding model id,
  `check_citations` assumes Semantic Scholar's batch endpoint, and
  `send_newsletter` assumes Gmail will accept an app password that
  Google can revoke without telling us.
- What: one small module the whole pipeline shares, with one function
  per external dependency that answers "is this still there, and is it
  still the shape we think", plus the alarm path the press just got. Run
  it at the start of every cron, cheap enough to be unconditional: a
  `GET /models` for Groq, a one-paper batch call for Semantic Scholar, a
  feed fetch with a shape assertion for arXiv, an SMTP login with no
  message for Gmail. Each failure names the dependency, the assumption
  that broke, and the file that holds it, and each failure emails rather
  than printing into a log nobody reads until the owner asks.
- What this is really about: the org has repeatedly discovered a broken
  dependency by noticing the absence of an output. That is the slowest
  possible detector and it has now cost three days once. A dependency
  check is not defensive programming, it is the difference between a
  failure the org responds to and a failure the owner reports.
- First step: `pipeline/health.py` with the Groq and Semantic Scholar
  probes lifted out of this PR's `check_availability`, plus one
  `@app.function` per app calling it. One cron adopts it first, ingest,
  because its dependency is the one with no key and therefore no
  excuses.
- Cost: $0.
- Status: proposed

### 2026-09-24 — Proposal, not an action: a paid floor under the press
- Trigger: the arithmetic above. Groq's free tier moved from 70,000 TPM
  to 8,000 TPM under this project inside five days, without notice, and
  took the weekly issue with it. The press is the acquisition engine
  (docs/vision.md §0) and it is currently the least reliable thing the
  company owns, because it is the only reader-facing surface whose
  supplier can change the terms on a Tuesday.
- What: put the press, and only the press, on a paid floor. Groq's
  Developer plan raises the same three models from 8,000 to 250,000 TPM,
  which makes both incident 22 and this one arithmetically impossible
  and costs a low monthly fee. Two alternatives worth costing beside
  it: a second free-tier account in a separate Groq organization, which
  is free but is a terms question and gives one bucket rather than a
  larger one; and a second provider behind the same interface, which
  buys real vendor independence and is the only option that survives
  Groq itself changing.
- Why it belongs to the owner and no agent: it costs money, so the
  standing rule makes it a proposal. Recorded here rather than acted on,
  and written into docs/sprints/pending.md as her decision alongside the
  two $0 paths, so it is a choice and not a surprise.
- First step: the finance seat costs all three against the sectioned
  press above, since the sectioned press may make the paid floor
  unnecessary rather than merely cheaper.
- Cost: not $0. The Developer plan's monthly fee for option one.
- Status: proposed

### 2026-09-24 — Craft scan: The Batch (deeplearning.ai, Andrew Ng)
- Trigger: the engineer seat's daily craft scan, next unscanned entry in
  the newsletter half of docs/market/landscape.md. Chosen today over the
  academic tools because the day's failure was a publishing failure, and
  The Batch is the comp in that column that has printed weekly for years.
- Worth stealing: **the issue's shape is fixed before the week's news
  exists.** Every issue opens with Ng's signed letter and then runs the
  same named sections, business, research, culture, hardware, career, in
  the same order. The skeleton is editorial furniture, not a response to
  what happened that week. Two things fall out of that, and the second
  is the one this project needs. A reader learns where to look once and
  never relearns it. And the issue can be assembled section by section,
  because each section's brief is independent of the others, which is
  precisely the property the sectioned-press idea above depends on.
  alexandria's press currently asks one model, in one request, for a
  whole issue at once, and it therefore fails as a whole issue at once.
  A fixed skeleton is what makes partial success possible.
- What alexandria does better: every item is checkable rather than
  authoritative. The Batch is trustworthy because Andrew Ng signs it, and
  that trust does not transfer, decompose, or survive him. An alexandria
  item carries the claim, the claim-graph edge that supports it, the
  paper, and a citation trajectory showing whether the field has come
  around, so a reader who does not know or trust us can verify a single
  line without taking anything on faith. That is also why the digest can
  be read by an agent, which no signed letter can be.
- Where it goes: the stealable thing is already the ledger entry above,
  which is the point of naming it here rather than filing a second copy.

### 2026-09-24 — Sovereign hosting's first verifiable slice: the press's own model on Modal
- Trigger: writing the provider table in this PR. ADR-32 names sovereign
  hosting as the destination, an open-weight writer served by alexandria
  itself so no provider can withdraw the press's model again, and puts it
  on the post-launch roadmap next to the router evaluation. Building the
  provider layer today changed what that destination costs. A provider is
  now five lines in `budget.PROVIDERS` and an entry in `budget.MODELS`.
  There is no second code path to write, no branch in `call_model`, and
  nothing in `weekly.py` that knows a vendor's name.
- What: a Modal function serving one open-weight writer over vLLM's
  OpenAI-compatible server, registered as a third provider called
  `self`, with `kimi-k2.6` staying primary and the self-hosted model
  taking rank two. That ordering is the point. The press keeps writing on
  the model that works while the sovereign path proves itself on real
  Mondays, and the day Moonshot withdraws `kimi-k2.6` the fallback is not
  a free tier that cannot print, it is a model nobody can take away.
  vLLM's server speaks the same dialect both current providers speak, so
  the whole integration is configuration.
- Why the press is the right first tenant: ADR-6 makes it the simplest
  possible workload, one prompt in, one issue out, no tools, running once
  a week. Compare the corpus crons, which are five jobs, thousands of
  calls, and a latency budget. If sovereign hosting cannot carry one
  weekly request it cannot carry anything, and finding that out costs one
  Monday.
- Cost: not $0, and that is the whole proposal. A GPU minute on Modal for
  one weekly request is real money against $0.05 an issue on Moonshot, so
  this is worth building for independence and never for price. The number
  the owner needs before she decides is what one issue costs on a cold
  container, including the model load, which is exactly what the first
  slice measures.
- First step: one `@app.function` with a GPU, a small open-weight writer,
  and no schedule. Run it by hand against last week's payload, print the
  issue and the wall-clock cost, and put both in the ledger. No press
  change until that number exists.
- Status: proposed

### 2026-09-24 — Watch the deprecation notices, not just the catalog
- Trigger: this run's near miss, now incident 24's third entry. ADR-32
  named the press's model "Kimi K2" and the obvious id, `kimi-k2`, had
  been discontinued for four months. It was caught by reading the
  provider's catalog on the day, which is luck dressed as process.
- What: the existence check proposed above answers "is it gone", and it
  answers it after the fact. Providers say so first. Moonshot's model
  page carries dated deprecation waves, 2026-05-25 and 2026-08-31, both
  published before the models stopped answering, and Groq marks a model
  production or preview, which is the same information in weaker form.
  So a weekly job reads each provider's catalog page, diffs it against
  every model id the repo names, and opens an issue when a model the code
  depends on is marked deprecated, previewed, or scheduled for removal.
  Not when it breaks. When the provider says it will.
- Why it is a different thing from the existence check: one is a smoke
  alarm and one is a calendar. `GET /models` tells you the press cannot
  print this morning. This tells you in March that the press will stop
  printing in May, which is the only warning long enough to be acted on
  by a project that ships once a day.
- First step: a `models_in_use()` function that scrapes the ids out of
  `budget.MODELS` and the pipeline's constants, then one weekly Modal
  function that fetches both catalog pages and diffs. Reuse the alarm
  path this PR gave the press.
- Cost: $0.
- Status: proposed

### 2026-09-24 — Publish a retrieval benchmark with named competitors and real numbers
- Trigger: today's craft scan, below. Undermind publishes a recall
  benchmark on its front page with competitors named and beaten by
  specific margins. alexandria has a blind prose benchmark for the issue
  (PR #66, built and still unscored) and nothing at all for retrieval,
  which is the half of the product a paying reader actually queries.
- What: fifty questions with a hand-marked answer set drawn from the
  corpus, run through `semantic_search` and `rag_answer`, scored on
  recall at ten and on whether the cited claim actually supports the
  answer. Published as a page on the site with the questions and the
  marking open, so a reader can rerun it. The number matters far less
  than its being checkable, because an unaudited benchmark is marketing
  and an audited one is a product claim.
- Why it earns its day: the paid product is the spine, the skills and the
  graph, not the issue, and nothing in the repo currently measures
  whether the spine answers questions well. The prose benchmark measures
  the free thing. This measures the thing people would pay for.
- First step: the fifty questions, written from real claims already in
  silver so the answer set is knowable, committed as a fixture before any
  scoring code exists. Writing the questions after seeing the scores is
  how a benchmark becomes a mirror.
- Cost: $0.
- Status: proposed

### 2026-09-24 — Craft scan: Undermind.ai
- Trigger: the engineer seat's daily craft scan, next unscanned entry in
  the academic-tools half of docs/market/landscape.md, where it has sat
  since 2026-09-18 with search-snippet confidence only. Read live today.
- What it actually is, now that someone has looked: an AI co-researcher
  for literature discovery. Free tier, Pro at $16 a month billed
  annually, Team at $15 a person, and an MCP endpoint at `/mcp` so it
  works inside Claude and ChatGPT.
- Worth stealing: **it publishes a benchmark that names its competitors
  and gives them numbers.** 85% recall on the twenty most relevant papers
  against 50% for GPT-5.6 Sol and 47% for Claude Opus 5, stated on the
  front page rather than in a whitepaper. Two things make that work, and
  both are available to us. The claim is falsifiable, which is why it
  persuades a scientist. And it reframes the product's biggest apparent
  weakness as the source of the number: a search takes 2.9 minutes on
  average, published as plainly as the recall figure, because reading
  hundreds of papers is what buys the recall. A slow honest instrument
  beats a fast opaque one, and saying so out loud is cheaper than
  arguing it. The ledger entry above is this thing, applied.
- What alexandria does better: Undermind answers the question you bring
  it. It cannot tell you that an answer it gave you in March has since
  been contradicted, because a search engine has no memory of what it
  told you and no opinion about what the field did next. alexandria's
  left-behind section is exactly that, and the citation trajectory
  underneath it is evidence rather than editorial. Both products are
  reachable by an agent over MCP, so the difference is not the interface.
  It is that one serves a search box and the other serves a graph that
  knows when it has changed its mind.

## Engineer agent findings (2026-09-24, owner directive: the emails get the UI)

### Craft scan — TLDR AI (tldr.tech/ai, fetched 2026-09-24)

- What it is: a free weekday AI newsletter, 1,100,000 subscribers by its
  own FAQ, positioned as "keep up with AI in 5 minutes" for engineers and
  researchers. Each item is a few sentences with a link to the source.
- Worth stealing: **the time contract, printed on the issue.** "5 minutes"
  is not a tagline, it is a promise about the reader's afternoon, and it
  appears before the reader has committed to anything. alexandria's issues
  are long, deliberately, and the reader currently discovers that by
  scrolling. Our email now has an `edition` line with room in it, and a
  preheader that is the first thing an inbox shows. Both are places to
  state the cost of reading before the reader pays it. Filed as an idea
  below.
- Where alexandria is better: TLDR summarizes what was published, and
  every item carries the same weight because a summary has no opinion
  about which claim survived. alexandria's issue is the only one of the
  two that can tell a reader that something they read last month has been
  overturned. The left-behind section and the evidence grade are that
  difference, and a reader who only ever sees new things accumulates
  stale beliefs at exactly the rate the field moves.

### 2026-09-24 — Print the cost of reading on the issue, in the edition line

- Trigger: today's craft scan of TLDR AI, whose whole promise is "5
  minutes", read against the issue I rendered this morning: 2026-W39 is
  10,278 bytes of markdown across 14 items, and nothing anywhere tells the
  reader that before they open it. The email template's `edition` slot
  currently reads "Weekly synthesis · September 21–27, 2026" and has room
  for one more clause.
- What: compute a reading estimate from the issue body at fill time and
  print it in the edition line, "Weekly synthesis · September 21–27, 2026
  · 9 minute read". It is arithmetic on a word count, so it costs nothing
  and cannot be wrong in an interesting way. The honest version counts the
  prose a reader actually reads and not the source URLs. The same number
  belongs on the site's issue pages, where the archive currently gives a
  visitor no way to tell a short issue from a long one.
- Why it is more than a nicety for this product specifically: alexandria's
  pitch is that it reads the papers so the reader does not have to. A
  number that says "this week cost you nine minutes instead of nine
  papers" is that pitch, stated as a measurement, in the one place the
  reader is deciding whether to open it.
- First step: one function in `pipeline/email_render.py` beside
  `preheader_for()`, a slot value, and a test that a known body produces a
  known number. Half a session.
- Cost: $0
- Status: proposed

### 2026-09-24 — The writer should choose the preheader, because it is the sentence that sells the issue

- Trigger: building `preheader_for()` today. The preheader is the grey
  sentence an inbox prints next to the subject, and it is the second
  thing every reader sees. Having no better source, I derive it from the
  first sentence of the issue's opening, which for 2026-W39 gives "You
  spent last week watching agents get faster by doing less at test time."
  That happens to be good. It is good by luck: the opening is written to
  start an issue a reader has already opened, and the preheader has to do
  the opposite job, which is to make someone open it.
- What: add a preheader to the generator's output contract in
  `prompts/digest.md`, one plain sentence, written to be read next to the
  subject and never a restatement of the title. It becomes a line in the
  issue's own front matter or a labelled first line the parser lifts and
  removes. The derived version stays as the fallback for every issue
  already in the `digests` table.
- Whose call: the writer seat owns `prompts/digest.md` and the voice. This
  is filed for that seat rather than edited, the same way the frontend
  seat filed the template for me. The engineer half is the parse and the
  fallback, which is an hour.
- The connection to today's incident: a slot the template asks for and no
  seat owns is how the last one of these went unnoticed for five days.
  `{{preheader}}` currently has a value because I invented a rule for it,
  which is the weakest of the three possible answers.
- Cost: $0
- Status: proposed

### 2026-09-24 — Grep every designed asset for a call site, as a check

- Trigger: INC-2026-09-24-email-template-never-opened, recorded today. The
  email template was complete, correct, reviewed at 3x, and filed in the
  right directory on 2026-09-19, and the press never opened it. Verified
  the fingerprint on main before writing the incident: `git grep
  "emails/digest.html"` at `a693776` returned six hits, and every one was
  the design review that produced the file, the file's own README, its own
  sample renderer, or the ledger entry proposing that somebody use it. Not
  one was code that runs.
- What: a check that walks the assets a design review produces (anything
  under `docs/design/reviews/*/` and the files those reviews say they
  shipped, plus `site/emails/`, and `skills/` templates) and reports any
  whose only inbound references are its own documentation. That is a
  mechanical definition of "delivered but not in the product", and it is
  the artifact-side gate that incident 20 said every register needs,
  applied to assets instead of rulings.
- Why it generalizes past this one email: the handoff that failed here is
  the normal shape of work in this org. One seat produces a finished thing
  and files it correctly, and the seat that would use it is never told,
  because the telling lives in a directory that seat has no reason to
  open. The org has twelve seats and one of them runs each day. Assets
  will keep being handed across that gap.
- First step: `tools/check_unreferenced_assets.py`, a list of asset globs,
  `git grep -l` per filename, and a rule that discounts self-references.
  Run it once over the whole repo first and read the output before wiring
  it into CI, because the first run is also an inventory of what else has
  been shipped and never used.
- Cost: $0
- Status: proposed
