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
