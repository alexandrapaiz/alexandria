# Landscape — the living competitor map

Maintained by the market research agent (prompts/market-agent.md), Fridays.
One entry per competitor or adjacent product. Entries are added and retired
with dated notes, never silently deleted. First built 2026-09-18.

Alexandria's shape, for reference when reading "weaknesses against
alexandria" below: a free research digest (trailblazing, matured, and
left-behind findings, evidence-cited via a claim graph) as the acquisition
engine, plus a $20/month paid layer of Claude-loadable skills, claim-graph
access, and automations. Differentiation, owner's words (2026-09-17):
"specifically technical research, systems, and directly applicable tools
for orchestration essentially," not AI news.

## Academic research tools

### Elicit (elicit.com)
- **What it is:** AI research assistant for finding, reading, and
  extracting structured data from academic papers.
- **Who it serves:** Individual researchers, grad students, research teams.
- **Pricing:** Free (5,000 credits, unlimited search over 138M+ papers,
  unlimited summaries/chat). Pro $49/month ($588/year). Scale $169/month
  ($2,028/year). Enterprise custom. [elicit.com/pricing](https://elicit.com/pricing)
- **Strengths:** Deep systematic-review workflow, huge paper index, API
  access even on Pro.
- **Weaknesses against alexandria:** Purely academic-paper-centric. No
  coverage of AI engineering or systems, no orchestration/automation
  layer, not built for agent builders.
- **Funding signal:** ~$22M Series A, early 2025, Spark Capital and
  Footwork. [Crunchbase](https://www.crunchbase.com/organization/elicit-52a6)
- **Last observed:** 2026-09-18.

### Consensus (consensus.app)
- **What it is:** AI search engine that surfaces consensus/claims across
  academic papers.
- **Who it serves:** Students, academic researchers, clinicians.
- **Pricing:** Free tier exists. Pro reported at roughly $20/month or
  $144/year (sources conflict; consensus.app/pricing returned 403 on
  direct fetch 2026-09-18, figure from
  [costbench.com](https://costbench.com/software/ai-research-tools/consensus/),
  verified there 2026-09-02, and a
  [help-center article title](https://help.consensus.app/en/articles/11408820-what-do-you-get-with-a-pro-subscription)
  — treat as medium confidence until independently reconfirmed).
- **Strengths:** Claim-style synthesis across papers, the closest seed-set
  product to alexandria's "claim graph" framing, though scoped to general
  academic literature not AI engineering.
- **Weaknesses against alexandria:** Same academic-only scope as Elicit;
  no orchestration/automation product; no AI-engineer-specific framing.
- **Note:** a same-named, unrelated B2B sales-demo tool (goconsensus.com)
  exists — do not conflate in future notes.
- **Last observed:** 2026-09-18.

### Semantic Scholar (semanticscholar.org)
- **What it is:** Free, nonprofit AI-powered academic search engine and
  open research-graph API.
- **Who it serves:** Researchers and developers; infrastructure other
  tools (including Elicit) build on.
- **Pricing:** Free, nonprofit-funded, no paid tier.
- **Strengths:** Massive open graph (200M+ papers, 2.4B citation edges),
  TLDR summaries and citation-intent classification already in the API.
- **Weaknesses against alexandria:** Infrastructure, not a product —
  no digest, no synthesis, no skills layer, no consumer habit loop.
- **Last observed:** 2026-09-18. [semanticscholar.org/faq/public-api](https://www.semanticscholar.org/faq/public-api)

### Paperguide (paperguide.ai) — new find, added 2026-09-18
- **What it is:** End-to-end AI research assistant (discovery, lit review,
  extraction, academic writing), increasingly cited as an Elicit/Consensus
  alternative.
- **Pricing:** Free tier; Plus $12/month; Pro $24/month; annual saves
  ~41%. [g2.com/products/paperguide/pricing](https://www.g2.com/products/paperguide/pricing)
- **Weaknesses against alexandria:** Academic-paper-focused like the
  others, not AI-engineering-focused.
- **Last observed:** 2026-09-18.

### Undermind.ai — new find, added 2026-09-18
- **What it is:** AI research assistant for scientific-literature
  discovery and novelty-checking with cited answers.
- **Weaknesses against alexandria:** Academic-search-only, same as above.
- **Last observed:** 2026-09-18 (search-snippet confidence only).

## Digests and newsletters (the category alexandria does not compete in)

### TLDR AI (tldr.tech/ai)
- **What it is:** Free daily 5-minute AI-news email digest, part of the
  TLDR network.
- **Pricing:** Free, ad/sponsorship-supported. No paid tier found.
- **Reach:** ~1.1M subscribers to the AI edition; TLDR network 7.2M+
  readers across 13 editions; 47% open rate vs ~34% industry benchmark
  (TLDR's own July 2026 data).
  [genai.works — Top 12 AI Newsletters 2026](https://genai.works/insights/top-12-ai-newsletters-to-follow-in-2026)
- **Weaknesses against alexandria:** Link-dump format, no synthesis, no
  claim graph, no tooling. This is the acquisition comp, not a peer —
  proof that pure AI news is fully commoditized at $0 with no viable
  paid tier.
- **Last observed:** 2026-09-18.

### Import AI (jack-clark.net, Jack Clark)
- **What it is:** Weekly AI research/policy essay newsletter by an
  Anthropic co-founder.
- **Pricing:** Free tier; paid $10/month or $100/year (early access,
  commenting); "Founding Member" pay-what-you-wish from $10,000.
  [jack-clark.net](https://jack-clark.net/)
- **Reach:** 116,000+ free subscribers, 450+ issues by mid-2026.
- **Weaknesses against alexandria:** One person's editorial essays, no
  structured claims, no tooling; cadence and depth bound to one author's
  bandwidth; potential conflict of interest (author is an Anthropic
  co-founder).
- **Last observed:** 2026-09-18.

### The Batch (deeplearning.ai, Andrew Ng)
- **What it is:** Free weekly AI news/insights newsletter.
- **Pricing:** Free, no paid tier — monetized via DeepLearning.AI courses,
  not the newsletter.
- **Weaknesses against alexandria:** News-and-opinion format, no claim
  structure, no skills/tooling layer.
- **Notable drift:** a 2026-09-11 issue on "how skilled AI engineers
  shape products" shows the editorial voice drifting toward the
  AI-engineering audience alexandria targets.
  [deeplearning.ai/the-batch](https://www.deeplearning.ai/the-batch)
- **Last observed:** 2026-09-18.

### AlphaSignal (alphasignal.ai)
- **What it is:** Daily AI newsletter/site tracking models, repos,
  papers, and announcements.
- **Pricing:** Free tier confirmed; a "Pro" tier exists (articles marked
  Pro) but exact price not found on the primary domain.
- **Reach:** Claimed 300,000+ engineer subscribers.
- **Weaknesses against alexandria:** Still a news-summary product, no
  claim graph or tooling, opaque Pro pricing.
- **Caution:** an unrelated crypto-signals company also uses the
  "AlphaSignal" name (alphasignal.digital) — do not conflate.
- **Last observed:** 2026-09-18.

### Last Week in AI (lastweekin.ai)
- **What it is:** Weekly AI-news podcast and Substack newsletter.
- **Pricing:** Free; no confirmed paid tier.
- **Weaknesses against alexandria:** Discussion/podcast format, general
  AI-news framing, no technical depth or tooling.
- **Last observed:** 2026-09-18.

### Latent Space (latent.space, Swyx)
- **What it is:** Technical media for AI engineers — newsletter, podcast,
  and (since Jan 2026) a daily AINews roundup.
- **Who it serves:** AI engineers specifically — the closest seed-set
  audience match to alexandria's reader.
- **Pricing:** Free plus a paid subscription; exact price not confirmed
  on the live page (JS-rendered pricing widget, search suggests roughly
  $8/month or $80/year, low-medium confidence).
- **Reach:** 200,000+ subscribers, 10M+ viewers/listeners across channels.
- **Structural precedent worth tracking:** AINews (smol.ai) merged into
  Latent Space "under one subscription" around 2026-01-23 — a free daily
  roundup folded into one paid brand, structurally similar to alexandria's
  free-digest-plus-paid-layer shape, though Latent Space's paid layer is
  more content/access than tooling.
  [latent.space/about](https://www.latent.space/about)
- **Weaknesses against alexandria:** Long-form interviews/essays, not a
  structured claim product; no orchestration-tools or skills-marketplace
  layer.
- **Last observed:** 2026-09-18.

### The Pragmatic Engineer (Gergely Orosz) — pricing comp, not an AI peer
- **What it is:** Paid software-engineering-practice newsletter, used
  here purely as a pricing benchmark.
- **Pricing:** $15/month or $150/year (up from an original $10/month or
  $100/year at launch).
  [newsletter.pragmaticengineer.com/about](https://newsletter.pragmaticengineer.com/about)
- **Reach:** 1,073,929+ total readers by end of 2025, 200,000+ added in
  the prior year.
- **Relevance:** validates a $15-20/month price point for a single-brand
  technical-professional newsletter; alexandria's paid layer is a
  materially different value prop (tooling, not more essays).
- **Last observed:** 2026-09-18.

### Ben's Bites (bensbites.com) — new find, added 2026-09-24
- **What it is:** High-frequency, community-driven AI newsletter and
  Discord/community product, casual tone, optimized for habit over
  depth.
- **Pricing:** Free digest. Community membership $80/year (~$6.67/mo).
  Pro tier $150/year, discounted from $250/year (~$12.50-20.83/mo).
  [catalog.bensbites.com](https://catalog.bensbites.com/topic/newsletters),
  [stackviv.ai](https://stackviv.ai/ai-tools/bens-bites).
- **Reach:** ~120,000 subscribers.
  [aiforautomation.io](https://aiforautomation.io/news/2026-03-30-bens-bites-120k-ai-newsletter-founder-a16z)
- **Weaknesses against alexandria:** community and content product, no
  claim structure, no agent-loadable tooling.
- **Why it matters for positioning:** its Pro tier is the closest
  content-brand comp to $20/month found yet, closer than The Pragmatic
  Engineer's $15/month. Folded into positioning.md's price ladder.
- **Last observed:** 2026-09-24.

## Agent-knowledge ecosystems

### Anthropic Claude Marketplace — new find, added 2026-09-24
- **What it is:** Anthropic's own marketplace, launched 2026-09-23, organized
  around three actions: **Add** (2,000+ connectors and plugins built on MCP
  and Agent Skills, from Google, Microsoft, Notion, Salesforce, Atlassian and
  others), **Buy** (Claude-powered partner products — Cursor, CrowdStrike,
  Harvey, Legora, Lovable, Snowflake — purchasable with committed Anthropic
  spend), and **Scale** (implementation services from Accenture, BCG,
  Deloitte). [claude.com/blog/claude-marketplace](https://claude.com/blog/claude-marketplace)
  (primary), corroborated by
  [runtimewire.com](https://runtimewire.com/article/anthropic-claude-marketplace-software-connectors-consultants).
- **Who it serves:** Enterprise buyers with an existing Anthropic spend
  commitment, redirecting procurement toward partner software, not
  individual developers or skill authors.
- **Resolves last week's flagged rumor:** 2026-09-18's landscape entry
  flagged an unverifiable secondary-source claim of a paid Anthropic skills
  marketplace with 15% revenue share. Checked this real, primary-sourced
  launch directly against that claim: **not the same thing**. The actual
  announcement contains no pricing, no revenue share, and no mechanism for
  individual community skill authors to sell anything — it is an enterprise
  procurement catalog for partner *products*, not a creator marketplace for
  skill *files*. The 15%-revenue-share claim stays unverified and now looks
  like SEO-blog conflation of this launch with a rumor, rather than an
  advance report of it.
- **Weaknesses against alexandria:** No evidence attached to any listing —
  a connector or partner product appears because a partnership exists, not
  because of measured reliability. No claim-graph-style verification layer.
  Still no first-party competitor to alexandria's $20/month individual
  operational tier.
- **Why it matters for positioning:** the platform owner is building
  distribution for *enterprise* partner software, not a monetization path
  for individual curated, evidence-backed skills. That gap — the one
  alexandria's paid tier occupies — stays open one more week, from the
  strongest possible source (Anthropic itself declining to fill it, for now).
- **Last observed:** 2026-09-24.

### Anthropic's Claude Skills ecosystem / skill marketplaces
- **What it is:** Not one product — a fast-growing, fragmented set of
  directories/marketplaces for Claude "Agent Skills."
- **Landscape:**
  - `anthropics/skills` — Anthropic's own curated examples (GitHub).
  - Claude Marketplace / `anthropics/claude-plugins-official` —
    Anthropic's own curated plugin directory.
  - **skills.sh** (Vercel-backed) — open, npm-style skill registry,
    launched 2026-01-20. Free, MIT-licensed CLI. ~20K installs shortly
    after launch; by June 2026, ~669,670 skills listed, top skill at
    2.0M installs.
    [Vercel changelog](https://vercel.com/changelog/introducing-skills-the-open-agent-skills-ecosystem)
    Re-checked 2026-09-24: the registry's own "All Time" leaderboard
    count now reads 1,540,973 skills, more than double the June figure
    (flagged for this seat's refresh in PR #86's "Seen and not mine").
    Growth rate, not just scale, is the signal: an open registry more
    than doubling in three months is a low, falling cost bar for a free
    alternative to alexandria's skills layer, unchanged in direction
    from the 2026-09-18 reading but now with a number behind it.
    [skills.sh](https://skills.sh)
  - Smithery.ai (MCP-server infra, hosts skill-registry products on top).
  - Other catalogs: localskills.sh, SkillsMP, ClawHub,
    claudemarketplaces.com, mcpmarket.com.
- **Monetization model:** distribution is free everywhere observed — no
  native billing/take-rate layer. No dominant *paid* skills marketplace
  exists yet. Open lane for alexandria's $20/month skills layer, but also
  a low-cost bar for a free alternative to appear.
- **Quality signal (new find, added 2026-09-18):** a Show HN post,
  "Linting 216 public Claude Code skills — 69% won't reliably trigger"
  (skillcrossroads.com "State of Skills — 2026-09" report), found 57% of
  subagents declare no tools list (an unintended permission-escalation
  risk). [news.ycombinator.com/item?id=49744398](https://news.ycombinator.com/item?id=49744398),
  2026-09-17.
- **Weaknesses against alexandria:** fragmented, no quality guarantee at
  most nodes, no research/claim-graph layer, no editorial component.
- **Last observed:** 2026-09-18.

### skillbay.sh — new find, added 2026-09-18
- **What it is:** "Craigslist for agent skills, curated by a human" — a
  small, hand-curated skill marketplace, launched to HN 2026-09-17.
- **Why it matters:** HN's reaction is the clearest willingness-to-pay
  data point found this run. Top comment: "Why would I buy a markdown
  file that someone most likely got an LLM to generate while I can just
  simply get my own LLM to generate a similar one for me for free?" The
  founder conceded AI-generated skills "are usually pretty bad," which is
  why he hand-curates; another commenter called the business model
  "no valuable moat." A third said only "nontechnical people" would pay
  $5 for something that "just works."
  [news.ycombinator.com/item?id=49743459](https://news.ycombinator.com/item?id=49743459),
  2026-09-17.
- **Reading for alexandria:** the market is skeptical of paying for raw
  skill *content*, but concedes curation and verification are the
  defensible value — supports alexandria's "distilled procedure +
  judgment, evidence-cited" framing over a raw skill dump.
- **Last observed:** 2026-09-18.

### Bastionskill — new find, added 2026-09-18 (later run)
- **What it is:** Show HN launch, a scanner that checks an AI agent
  skill for malicious code before install.
  [news.ycombinator.com/item?id=49753727](https://news.ycombinator.com/item?id=49753727),
  2026-09-18. Low traction at discovery (1 point, a few hours old),
  flagged for a traction re-check next pass rather than a full entry.
- **Why it matters:** a second, independent entrant (after skillbay.sh)
  building specifically toward trust/verification of skills rather than
  distribution. The gap alexandria is built for is now attracting
  founders on both sides: curated distribution (skillbay.sh) and
  automated safety scanning (Bastionskill). Neither attaches
  research-backed evidence to a skill's *claims*, only its code safety —
  alexandria's claim-graph verification is still differentiated, but the
  "skills need trust infrastructure" thesis now has multiple, independent
  confirmations in one week.
- **Last observed:** 2026-09-18.

### Cloudflare's security-audit-skill — landscape note, 2026-09-18 (later run)
- Not a competitor entry (Cloudflare is not selling this), but a signal
  worth recording under the skills ecosystem: a first-party engineering
  team shipping a real, in-production Claude skill drew a heavily
  upvoted HN thread (205 points) whose top complaints were token bloat
  ("I threw 1M tokens for nothing in a medium codebase," "at least 150k
  on my relatively small FastAPI project") and unscoped context loading
  ("you should consolidate all of your skills into a single skill and
  route everything thru that skill," acknowledged by a Cloudflare
  engineer as "being worked on").
  [news.ycombinator.com/item?id=49736466](https://news.ycombinator.com/item?id=49736466),
  2026-09-18.
- **Reading for alexandria:** direct, first-party confirmation of the
  "Scoped skill delivery by default" ledger proposal already filed
  2026-09-18 (docs/ideas.md) from the Skillzero find — this is now two
  independent pieces of evidence, one hypothetical (a commenter's
  question) and one lived (a real company's users hitting the problem in
  production).

### OpenAI's 10,000-agent swarm — orchestration-at-scale precedent, added 2026-09-24
- Not a competitor, a signal: OpenAI published a proposed resolution of the
  Navier-Stokes existence-and-smoothness Millennium Prize problem on
  2026-09-08, produced by roughly 10,000 concurrent agents coordinated by an
  internal model, generating about 2.7 million agent messages and 130
  billion output tokens over 88 hours, then 17 more hours of Lean
  verification. [neowin.net](https://www.neowin.net/news/openai-agent-swarm-triggers-verification-for-navier-stokes-math-problem/),
  widely corroborated. The Clay Mathematics Institute's verification process
  is multi-year and not yet complete.
- **A public credit dispute followed.** NYU mathematician Tristan Buckmaster
  said OpenAI's Sébastien Bubeck pressured him over credit for related,
  Lean-verified work Buckmaster had done with Anthropic's Levent Alpöge,
  building on an approach opened by Córdoba and Martínez-Zoroa.
  [The Batch, issue 371](https://www.deeplearning.ai/the-batch/issue-371).
- **Reading for alexandria:** the loudest orchestration story of the year
  is now also the loudest attribution dispute of the year — a live
  demonstration of the exact gap alexandria's claim graph is built to
  close (who gets credit, whose work an approach builds on, whether a
  claim has independent verification yet). It also strengthens last week's
  still-open orchestration-pattern-benchmark ledger proposal: multi-agent
  orchestration at extreme scale just became front-page news, not a niche
  practitioner ask.
- **Last observed:** 2026-09-24.

## Watchlist (not yet full entries, flagged for next pass)

- **Exa (exa.ai)** — not a digest/skills competitor but the closest
  seed-set infrastructure comp for "directly applicable orchestration
  tools": pay-as-you-go search/retrieval API for agents ($7/1,000
  requests). Raised an $85M Series B (fall 2025, Benchmark, $700M
  valuation) then a $250M Series C in May 2026 (a16z, $2.2B valuation) —
  a signal that agent-facing infrastructure is attracting large capital
  fast. [exa.ai/pricing](https://exa.ai/pricing),
  [Bloomberg, 2026-05-20](https://www.bloomberg.com/news/articles/2026-05-20/andreessen-backed-ai-search-startup-exa-valued-at-2-2-billion).
  Do not compete here directly — integrate/cite, don't rebuild.
- **SemiAnalysis** — retail newsletter $500/year; a separate,
  higher-priced "Core Research" institutional product reported on track
  for ~$100M/year from buy-side demand. Evidence that a free-or-cheap
  retail tier plus a much higher institutional tier is a repeatable
  pattern worth watching as alexandria matures past the individual
  $20/month tier.
  [aiweekly.co](https://aiweekly.co/alerts/semianalysis-core-research-eyes-100m-year-on-buy-side-demand)
- **Agent Memory Leaderboard (agentmemoryleaderboard.ai)** — new find,
  2026-09-18 (later run). An open, academically-backed (Tsinghua, Peking
  University, Oxford, and others) benchmark for AI agent memory systems
  across textual, multimodal, and coding-agent tracks, free to enter,
  no commercial pricing. Refines rather than reverses this morning's "no
  independent benchmark exists for multi-agent orchestration" finding: a
  credible academic benchmark now exists for agent *memory* specifically,
  but the broader orchestration-pattern space (cost/latency/error
  tradeoffs across harness and multi-agent designs, the shape of the
  ledger's "Orchestration-pattern benchmark" proposal) is still
  unaddressed by anything observed. Worth citing as a possible claim-graph
  integration rather than building memory-evaluation data collection from
  scratch. [agentmemoryleaderboard.ai](https://agentmemoryleaderboard.ai/)

## Change log

- 2026-09-18: initial landscape built (first run). Full seed set covered:
  Elicit, Consensus, Semantic Scholar, Exa, TLDR AI, Import AI, The
  Batch, AlphaSignal, Last Week in AI, Latent Space, The Pragmatic
  Engineer, Anthropic's skills ecosystem. Added Paperguide, Undermind.ai,
  skillbay.sh as new finds not in the original seed set.
- 2026-09-18 (later run): checked a claim from secondary-source blogs
  (500k.io and reposts) that Anthropic shipped a paid "Skills
  Marketplace" on 2026-05-01 with a 15% revenue share. Could not verify
  against any primary source — the `anthropics/skills` marketplace.json
  and claude.com/blog/skills both describe only a free, open directory of
  skills with no pricing or revenue-share mechanism. Not recorded as fact
  here; flagged in case a future pass finds a primary source, but treated
  as unreliable for now. Added Bastionskill and a Cloudflare
  security-audit-skill note to the skills-ecosystem section; added the
  Agent Memory Leaderboard to the watchlist.
- 2026-09-24: added Anthropic Claude Marketplace (launched 2026-09-23),
  checked directly against last week's flagged, unverified paid-skills-
  marketplace rumor — not the same product, rumor still unverified. Added
  OpenAI's 10,000-agent Navier-Stokes swarm and the credit dispute it
  triggered as an orchestration-at-scale watchlist note. Re-checked Elicit
  and Consensus pricing (docs/market/briefs/2026-09-24.md); no change
  found at either.
- 2026-09-24 (second run, the owner's ranking dispatch): added Ben's
  Bites as a new digests-and-newsletters entry. Re-checked skills.sh's
  listed-skill count directly (1,540,973, more than double the June
  figure), flagged for refresh by PR #86's "Seen and not mine." See
  docs/market/briefs/2026-09-24-b.md for the newsletter and product
  ranking this run produced.
