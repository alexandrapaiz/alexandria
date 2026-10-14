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
- **Last observed:** 2026-09-25. Re-checked pricing directly: unchanged
  (Pro $49/mo, Scale $169/mo, same tier contents).
  [elicit.com/pricing](https://elicit.com/pricing)

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
- **Last observed:** 2026-10-02. Fourth direct attempt, same result: the
  pricing page and the help-center article both returned no plain-text
  price again (403 on both). But a search pass this run surfaced several
  independent pricing-aggregator sites (costbench.com,
  aiproductivity.ai, top50aitools.com) now converging on a different
  figure than the one tracked here since 2026-09-18: Pro at $15/month or
  $120/year, and a higher Deep tier at $65/month or $540/year for 200
  deep searches/month. None of these are the primary source, and
  aggregator convergence is not the same as a confirmed price, so this
  is recorded as a second, differing medium-confidence reading rather
  than a correction. The $20/month figure is not retracted, only now
  contested by newer secondary sources. Flagged for the next pass to
  resolve, not averaged or picked between here.
  [costbench.com](https://costbench.com/software/ai-research-tools/consensus/),
  [aiproductivity.ai](https://aiproductivity.ai/pricing/consensus/).
- **Last observed again, 2026-10-05.** Fifth direct attempt at the
  primary source (consensus.app/pricing) and the help-center article:
  both still blocked (one still JS-rendered with no plain-text price,
  the other now a flat 403). But the same two secondary sources flagged
  three days ago as having "converged on a different figure" were
  re-fetched directly, and both now read Pro at $20/month ($12/month
  billed annually, $144/year) and Deep at $65/month ($45/month billed
  annually), matching the figure this doc has carried since 2026-09-18,
  not the $15/month reading recorded on 2026-10-02.
  [costbench.com](https://costbench.com/software/ai-research-tools/consensus/),
  [aiproductivity.ai](https://aiproductivity.ai/pricing/consensus/).
  Not treated as a correction of the $15 reading either, for the same
  reason the $15 reading was not treated as a correction of $20: the
  same URL returning two different numbers three days apart from the
  same seat's reads means the source is unstable, not that either
  number is wrong. Recorded plainly because the instability is itself
  the finding: a secondary aggregator's price is a snapshot of
  whatever that site rendered that day, not a fact about Consensus's
  actual price, and this doc should stop treating one aggregator read
  as a resolution until the primary page is reachable directly.

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

### TheSequence (thesequence.substack.com) — new find, added 2026-10-02
- **What it is:** Twice-weekly ML-research newsletter (Edge) plus a free
  weekly roundup (Scope), reviewing papers, concepts, and new frameworks.
- **Pricing:** Edge (paid) is $5/month or $50/year. Scope (free) covers
  general roundup content.
  [thesequence.substack.com](https://thesequence.substack.com/)
- **Weaknesses against alexandria:** Essay/explainer format, no claim
  graph, no skills or automation layer, no evidence-linking.
- **Why it matters for positioning:** the cheapest confirmed paid
  technical AI newsletter found in this landscape, well below the
  $15/month essay-newsletter cluster. It shows a paid technical
  newsletter can work at $5/month, which is a data point about the
  newsletter category's floor, not a challenge to $20/month — alexandria
  doesn't compete on newsletter economics, and this sharpens the
  contrast between "pay for more reading" (priced low, commoditized) and
  "pay for a tool" (priced at $20-49/month, see the ladder in
  positioning.md).
- **Last observed:** 2026-10-02.

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

### Claude Code "mods" — platform note, added 2026-10-02
- **What it is:** not a competitor, a platform change worth tracking
  because every alexandria agent runs on this exact harness. On
  2026-10-01, Anthropic shipped "mods": small TypeScript functions, shipped
  inside plugins, that can rewrite a prompt before it reaches the model,
  block/rewrite/retry a tool call, approve or deny a permission request,
  redact secrets from tool output, and replace parts of the UI.
  [claude.com/blog/claude-code-mods](https://claude.com/blog/claude-code-mods)
  (primary).
- **Not sandboxed.** Anthropic's own post says a mod "operates with the
  same machine access as Claude Code itself" and to "only install mods
  from sources you trust, the same way you'd install any code on your
  computer." Mods from different authors stack and run in load order on
  the same event.
- **Why it matters for positioning:** not a pricing or competitor signal.
  It is a new, higher-privilege extensibility layer (prompt rewriting,
  permission approval, secret redaction) on the infrastructure this org's
  every seat already runs on every turn, shipped with no sandbox and a
  trust-the-source caveat. Named here rather than assessed. Threat
  assessment of what this means for alexandria's own agents is the
  security seat's call, not this one's (see this week's brief).
- **Last observed:** 2026-10-02.

### NVIDIA SkillSpector, a third and larger security scan, new to this doc 2026-10-05

- **What it is:** an open-source scanner for Claude Code, Codex, and MCP
  skills (open-sourced 2026-03-21) that runs 64 detection patterns across
  16 categories against a SKILL.md file and every script beside it, and
  produces a 0-100 risk score. [github.com/NVIDIA/SkillSpector](https://github.com/nvidia/skillspector)
- **The number, not new this week but new to this landscape doc:** across
  42,447 real skills scanned, 26.1% contained a vulnerability and 5.2%
  showed signs of deliberate malicious intent.
- **Reading for alexandria:** a third independent security scan, larger
  than Snyk's ToxicSkills pass (3,984 skills, 13.4% critical-severity),
  now with a major infrastructure vendor's name on it (NVIDIA) rather
  than only a security-research firm's. The skills-trust thread this
  doc has tracked since 2026-09-18 (skillbay.sh, Bastionskill, Skillcop,
  Skill Federation, Snyk's ToxicSkills, SkillsBench) gains a fourth
  independent confirmation that raw skill distribution is unsafe, from
  a different measurement each time (code safety twice now, discoverability
  twice, task-outcome quality once). None of the four attaches
  research-backed evidence to a skill's claims, so alexandria's
  claim-graph differentiation is unaffected, same reading as every prior
  entry in this thread.
- **Last observed:** 2026-10-05.

### Anthropic's own upstream risk, named here rather than assessed, platform note added 2026-10-05

- **What it is:** not a competitor, the same kind of entry as the Claude
  Code "mods" note above, because every alexandria agent runs entirely
  on Anthropic's models and this run found the first concrete precedent
  for that dependency carrying government-relations risk rather than a
  hypothetical one. Anthropic's IPO prospectus (reported 2026-10-02,
  prospectus itself not public) discloses that in February 2026 the
  president ordered federal agencies to stop using Anthropic's models,
  that the Department of Defense designated Anthropic a supply-chain
  risk to national security (a federal appeals court upheld that
  designation on 2026-09-25), and that in June 2026 the Department of
  Commerce imposed worldwide export restrictions on two Claude models,
  Fable 5 and Mythos 5, which Anthropic disabled for all customers
  globally for 19 days before the restriction lifted.
  [Yahoo Finance](https://finance.yahoo.com/technology/ai/articles/anthropic-ipo-prospectus-warns-u-133449998.html),
  [Techzine](https://www.techzine.eu/news/privacy-compliance/144724/anthropic-government-attitudes-pose-risk-to-ipo/).
  Government revenue is under 1% of Anthropic's own business, which is
  why the prospectus frames the risk as reputational and relational
  (commercial customers and partners), not a direct revenue line.
- **Why it matters for positioning:** not a pricing or competitor
  signal, named here for the security seat's assessment, the same
  routing this doc used for Claude Code's mods. The difference worth
  stating plainly: that entry was a new, theoretical risk on the
  harness every seat runs on. This one is a live precedent, already
  executed once this year, of the single vendor every seat's compute
  depends on having two of its own models disabled globally by a
  government order for nineteen days. Two prior briefs (2026-10-02,
  2026-09-18) have named that Anthropic sits outside the charter's
  named upstream-vendor list (Hugging Face, arXiv, Groq, Neon, Modal,
  GitHub) despite supplying every seat's compute. This is the third
  time and the first with a concrete incident behind it rather than a
  structural observation.
- **Last observed:** 2026-10-05.

### Skly — new find, added 2026-10-02
- **What it is:** a marketplace for buying and selling AI agent skills,
  compatible with Claude, ChatGPT, Cursor, and other agents. Both free
  and paid skills are supported.
- **Why it matters:** its HN launch thread reopened the "should skills be
  free or paid" debate this landscape has tracked since skillbay.sh's
  launch (2026-09-18): commenters noted a well-crafted vertical skill
  pack represents real compressed domain expertise, against the
  open-source ethos of the developer-tool ecosystem (the same tension
  that played out with VS Code extensions, npm, and GitHub Actions, per
  the thread). Unresolved, same as every prior round of this argument.
- **Reading for alexandria:** another data point that the market has not
  settled whether a bare skill file is worth paying for at all, which
  is exactly why the why-pay paragraph in positioning.md sells the
  operational layer (claim graph, evidence, automations), never a skill
  file alone.
- **Last observed:** 2026-10-02.

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
    Re-checked 2026-09-30 against Vercel's own "State of agent skills"
    report: the registry crossed 1 million skills in seven months from
    launch, faster than GitHub took to reach 1 million repositories (27
    months), the App Store took to reach 1 million apps (63 months), or
    npm took to reach 1 million packages (117 months). Install activity
    is sharply concentrated: nearly half of all listed skills have been
    installed exactly once, while 0.04% of skills account for 62% of
    all installs. [vercel.com/blog/state-of-agent-skills](https://vercel.com/blog/state-of-agent-skills)
    **Reading for alexandria:** the concentration number is the more
    important one. A registry where half the supply gets one install
    ever is not a curation gap in theory, it is a measured fact about
    this exact registry: readers are already filtering hard for
    themselves, at a rate no listing mechanism here explains. That is
    the demand-side twin of the SkillsBench quality finding below,
    which measures the same registries from the supply side.
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

### The skills-trust gap now has a number behind it, and two more entrants found this run — added 2026-09-25
- **The number:** Snyk's ToxicSkills research (published 2026-02-05,
  cited in alexandria's own docs for the first time this run) scanned
  3,984 agent skills from ClawHub and skills.sh with its mcp-scan engine:
  13.4% (534 skills) carried at least one critical-severity flaw, 36.82%
  (1,467 skills) had a flaw of any severity, and human review confirmed
  76 outright malicious payloads across eight threat categories (prompt
  injection, malicious code, credential theft, embedded secrets, and
  more).
  [snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/).
- **Two more entrants found this run, neither new this week but both new
  to this landscape doc, and both citing that number as their reason to
  exist.** Show HN, "Skillcop: Block malicious Claude Skills before they
  execute" — an LLM-based security scanner run as a Claude Code hook,
  built directly against the ToxicSkills taxonomy, posted 2026-03-20.
  [news.ycombinator.com/item?id=47457995](https://news.ycombinator.com/item?id=47457995).
  Show HN, "Skill Federation — private search across 87k skills for AI
  coding agents," posted 2026-07-02.
  [news.ycombinator.com/item?id=48760839](https://news.ycombinator.com/item?id=48760839).
  Verified both post dates directly against Algolia's HN search API
  after an earlier pass mistook a third-party aggregator's digest date
  for the posts' actual dates. Worth recording precisely: the aggregator
  resurfaces relevant older threads under a current-looking date, so any
  future run treating one of its digests as same-week evidence needs to
  check the item's own `created_at` first.
- **Reading for alexandria:** counting all four, spread from March
  through this week, four independent founders have now built trust or
  curation infrastructure on top of raw skill distribution over about
  six months — skillbay.sh and Bastionskill (2026-09-18, above),
  Skillcop (2026-03-20) and Skill Federation (2026-07-02). None of the
  four attaches
  research-backed evidence to a skill's underlying *claims*, only to its
  code safety or its discoverability, so alexandria's claim-graph layer
  stays differentiated. But the market no longer needs alexandria to
  argue that raw skill distribution has a trust problem. Four builders
  have already spent their own time proving it, and now there is a
  citable number behind the pattern.
- **Last observed:** 2026-09-25.

### SkillsBench — the first benchmark for whether a skill actually helps, added 2026-09-30
- **What it is:** an academic benchmark, published to arXiv, that measures
  whether Agent Skills change task outcomes rather than whether they are
  safe. 47,150 unique skills retained from 6,323 GitHub repositories after
  deduplication, run against a shared set of agent tasks.
  [arXiv 2602.12670](https://arxiv.org/abs/2602.12670)
- **The number:** mean quality score across the whole ecosystem, 6.2 out of
  12 (SD 2.8). Applying curation lifted the pass rate by a mean of 16.2
  percentage points over uncurated skills on the same tasks.
- **Why it matters for positioning:** every prior entry in this section
  (Snyk's ToxicSkills, Skillcop, Skill Federation, skillbay.sh,
  Bastionskill) argues the open ecosystem is unsafe or untrusted.
  SkillsBench is the first number found that argues it is mediocre even
  when it is not malicious: half the quality points on the table, on
  average, sit unclaimed in the typical public skill. That is a second,
  independent axis of evidence for alexandria's curation thesis, not a
  restatement of the security one.
- **Last observed:** 2026-09-30.

### ComposioHQ's awesome-claude-skills — a free curated directory, added 2026-09-30
- **What it is:** a hand-curated, community-maintained GitHub list of
  1,000+ Claude Skills and plugins, trending on GitHub with 75,800+ stars.
  [github.com/ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)
- **Weaknesses against alexandria:** curation here means inclusion in a
  list, not evidence attached to a claim. No provenance, no claim graph,
  no verification against research, and no business model — it is a
  volunteer README, not a product.
- **Why it matters:** it is free, popular, and solves a real piece of the
  problem SkillsBench just measured (a reader does not have to sort 47,150
  skills alone). It is also a second data point, after skills.sh's own
  install concentration above, that the market is already curating for
  itself for $0. Alexandria's differentiation has to rest on the
  evidence attached to a skill, not on curation existing at all, since
  curation-that-exists is now free in at least two independent places.
- **Last observed:** 2026-09-30.

### Strands Harness (AWS) and the CMU message-passing paper — orchestration-pattern signal, added 2026-09-25
- **What happened:** AWS's Strands Agents team shipped "Strands Harness,"
  claiming frontier performance at 28% lower token cost.
  [strandsagents.com/blog/introducing-strands-harness](https://strandsagents.com/blog/introducing-strands-harness/).
  HN gave it real traction (146 points, 96 comments) and real skepticism:
  top comments could not tell "whether it's a harness, an orchestrator,
  or an agent framework," questioned whether Terminal-Bench 2.1 is
  saturated enough that the gain is noise, and asked for comparison
  against other harnesses (Pi) that nobody but the vendor has run.
  [news.ycombinator.com/item?id=49817289](https://news.ycombinator.com/item?id=49817289),
  2026-09-25.
- **The same week, The Batch (issue 372, 2026-09-25) covered two more
  harness/orchestration items:** Cognition's "Devin Fusion," a two-model
  harness pairing a planner with a coding specialist at 36-39% lower cost
  than single-model baselines, and a Carnegie Mellon-affiliated paper,
  "Message Passing Language Models" (arXiv
  [2607.01077](https://arxiv.org/abs/2607.01077), posted 2026-07-01, only
  now picking up press attention), which lets parallel reasoning threads
  send and receive messages directly instead of routing through a
  coordinator.
- **Reading for alexandria:** every one of these is a vendor or lab
  claiming a harness-design win with no independent evaluation attached —
  the same gap alexandria's claim graph exists to close, and the same
  gap behind the still-open orchestration-pattern-benchmark ledger
  proposal. Named here for the research seat's signal read: the CMU
  paper in particular sits squarely in the harness-and-orchestration
  vein this week's own digest issue (2026-W39, harness distillation) is
  already mining.
- **Last observed:** 2026-09-25.

### OrchBench — the orchestration-pattern benchmark this doc has watched for since 2026-09-18, added 2026-10-02
- **What it is:** an academic benchmark, submitted to arXiv 2026-07-28,
  that evaluates multi-agent orchestration plans via deterministic
  simulation rather than live execution: directed acyclic graphs encode
  task dependencies at controlled sizes and parallelism, and the
  simulation scores how planners assign subtasks, pass information
  between agents, and retain task-critical context.
  [arXiv 2607.25656](https://arxiv.org/abs/2607.25656)
- **The number:** simulated scores correlate with real Claude Code
  executions at Pearson r=0.816, for 1.3% of the tokens and 10.3% of the
  wall-clock time of running the real thing. Preserving task-critical
  information mattered more than adding agents. Parallelism's benefit
  fades as coordination failures accumulate.
- **What this resolves and what it doesn't.** This landscape has said
  since the first run that no independent benchmark exists for
  orchestration-pattern cost/latency/error tradeoffs, and the ledger's
  still-open "Orchestration-pattern benchmark" proposal
  (docs/ideas.md, 2026-09-18) cites that exact gap. OrchBench closes it
  for the specific question of whether a given orchestration plan is any
  good, cheaply and reproducibly. It does not compete with alexandria's
  claim graph: OrchBench scores a plan's structure in simulation, it does
  not attach research-backed evidence to a technique's claims, track
  `supports`/`contradicts` edges, or sit inside a product a reader pays
  for. Read together, it is a tool the claim graph could cite rather than
  a product that replaces it. Named in this week's brief for the
  research seat's signal read.
- **Last observed:** 2026-10-02.

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
- 2026-09-25 (regular Friday ceremony): re-checked Elicit directly, no
  change. Attempted to re-check Consensus; its pricing page now renders
  client-side, no figure confirmed this pass. Added a dated skills-trust
  entry (Snyk's ToxicSkills stat, first cited here, plus Skillcop and
  Skill Federation, two entrants found this run though neither is new
  this week) and a Strands Harness / CMU message-passing-paper
  orchestration-signal entry. See docs/market/briefs/2026-09-25.md for
  this week's full brief.
- 2026-09-30 (regular ceremony, triggered by a synchronous work window):
  re-checked Elicit (unchanged) and Consensus (still unconfirmable, third
  attempt) directly. Updated the skills.sh entry with Vercel's own "State
  of agent skills" report: 1 million skills in seven months, the fastest
  of any major software platform measured, and install activity
  concentrated so sharply that half of all skills have exactly one
  install. Added two new entries: SkillsBench, the first benchmark
  measuring whether a public skill actually helps (mean quality 6.2/12,
  curation lifts pass rate 16.2 points), and ComposioHQ's
  awesome-claude-skills, a free curated directory at 75,800+ GitHub
  stars. Both extend the skills-trust thread this doc has tracked since
  the first run, from "is it safe" and "is it discoverable" to "is it any
  good" and "is curation itself now free." See
  docs/market/briefs/2026-09-30.md for this week's full brief, including
  a major agent-safety event (OpenAI's GPT-6.1 Astra) named there rather
  than here since it is not a competitor to alexandria.
- 2026-10-02 (regular Friday ceremony): re-checked Elicit directly, no
  change. Re-checked Consensus a fourth time. Still no primary-source
  figure, but a search pass found several aggregator sites now
  converging on a different medium-confidence reading ($15/month Pro,
  $65/month Deep) than the one tracked here since 2026-09-18, recorded
  as a second, contested reading rather than a correction. Added
  TheSequence as a new pricing-ladder find ($5/month, the cheapest
  confirmed paid AI newsletter found yet). Added Claude Code's new
  "mods" capability (2026-10-01, unsandboxed TypeScript hooks that can
  rewrite prompts, tool calls, and permissions) as a platform note, since
  every alexandria agent runs on this harness. Added Skly as a new
  skills-marketplace find, reopening the free-vs-paid-skill debate.
  Resolved the long-tracked "no independent orchestration-pattern
  benchmark exists" watchlist item: OrchBench (arXiv 2607.25656)
  correlates r=0.816 with real Claude Code executions at 1.3% of the
  token cost, closing the specific gap without competing with the claim
  graph. See docs/market/briefs/2026-10-02.md for this week's full
  brief, including the first lawsuit against an AI developer over a
  rogue agent incident, named there for the security seat rather than
  here since OpenAI is not a competitor to alexandria.
- 2026-10-05 (synchronous work window, three days after the last brief):
  re-checked Consensus's pricing a fifth time. Primary source still
  blocked, but the same two secondary sources that read $15/month three
  days ago now read $20/month again on direct re-fetch, matching the
  figure tracked since 2026-09-18. Recorded as evidence the secondary
  source is unstable, not that either number is confirmed. Added NVIDIA
  SkillSpector (42,447 skills scanned, 26.1% vulnerable, 5.2% likely
  malicious) as a fourth independent skills-trust confirmation, not new
  this week but new to this doc. Added a platform note on Anthropic's
  IPO prospectus disclosing a Department of Defense supply-chain-risk
  designation (upheld by a federal appeals court 2026-09-25) and a
  19-day global export-control shutdown of two Claude models in June
  2026, the first concrete precedent behind two prior briefs' structural
  observation that Anthropic sits outside the charter's named upstream
  list. See docs/market/briefs/2026-10-05.md for this run's full brief.
