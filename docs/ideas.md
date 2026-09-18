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
