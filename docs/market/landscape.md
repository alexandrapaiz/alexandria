# Landscape — the living competitor map

Maintained by the market research agent (prompts/market-agent.md). One
entry per competitor or adjacent product. Entries are added and retired
with dated notes, never silently deleted. First full map built
2026-09-18 on the first run.

alexandria sits at the intersection of three categories, so the map has
three sections plus a paid-newsletter pricing comp section. No product
observed so far spans all three. That intersection is the positioning
story, argued in [positioning.md](positioning.md).

## Category 1 — AI research intelligence tools

### Elicit
- What: AI research assistant for literature search, systematic review,
  and data extraction over 138M+ papers.
- Audience: researchers and R&D teams, with an enterprise push.
- Pricing (observed 2026-09-18 at [elicit.com/pricing](https://elicit.com/pricing)):
  Free basic tier, Pro $49/mo ($588/yr), Scale $169/mo ($2,028/yr),
  Enterprise custom.
- Strengths: deep extraction workflows, systematic-review credibility,
  API access, real enterprise motion.
- Weaknesses against alexandria: it is a pull tool, not a judgment
  product. It answers the question you ask and keeps no public running
  record of what the field believes or has abandoned. It ships no
  agent-loadable output. Priced 5x above alexandria's top tier.
- Last observed: 2026-09-18.

### Consensus
- What: AI academic search engine over 200M+ papers with answer
  synthesis, claims "over 5 million researchers, students, and
  clinicians" ([consensus.app/pricing](https://consensus.app/pricing)).
- Audience: students, clinicians, researchers. Consumer-leaning.
- Pricing (pricing page is script-rendered, figures confirmed via
  third-party trackers, e.g.
  [costbench.com](https://costbench.com/software/ai-research-tools/consensus/)):
  Free with ~20 AI searches/mo, Pro ~$10/mo, Deep ~$45/mo, Teams
  ~$9.99/seat/mo annual, Enterprise custom.
- Strengths: huge registered base, clean freemium ladder, the $10 entry
  point proves individual willingness to pay $10/mo for research
  intelligence.
- Weaknesses against alexandria: search over a static corpus, no
  temporal judgment, nothing for agents, no digest habit loop.
- Last observed: 2026-09-18.

### Semantic Scholar
- What: free AI-driven academic search and open APIs (Academic Graph,
  S2ORC) from Ai2, 200M+ papers
  ([semanticscholar.org/about](https://www.semanticscholar.org/about)).
- Audience: the global research community and developers building on the
  corpus. alexandria's own pipeline class of user.
- Pricing: free, nonprofit-funded.
- Strengths: canonical open infrastructure, citation graph at scale.
- Weaknesses against alexandria: infrastructure, not judgment. It gives
  you the graph and leaves the interpretation to you.
- Note: not a revenue competitor, but the free baseline any paid claim
  graph gets compared against.
- Last observed: 2026-09-18.

### Exa
- What: search API built for AI agents, usage-priced
  ([exa.ai/pricing](https://exa.ai/pricing)): search $7/1k requests,
  deep search $12-15/1k, monitors $15/1k, free tier with $10/mo credits.
- Audience: developers and businesses wiring live web search into
  agents.
- Strengths: agent-native distribution, pay-as-you-go with no
  subscription friction, monitors product overlaps with "watch the
  frontier" jobs.
- Weaknesses against alexandria: retrieval without curation. Exa hands
  an agent raw web results, not validated procedures. It is plumbing
  alexandria could even consume, not a library.
- Last observed: 2026-09-18.

## Category 2 — AI digests and technical newsletters

### TLDR AI
- What: free daily AI newsletter, "1,100,000 readers," ad and
  sponsorship funded ([tldr.tech/ai](https://tldr.tech/ai)).
- Audience: engineers and technical professionals who want a 5-minute
  scan.
- Strengths: enormous reach, daily habit, dense engineering-first tone.
- Weaknesses against alexandria: pure coverage. No memory, no verdicts,
  no tracking of which results held up. The inbox-noise problem it
  feeds is alexandria's opening.
- Last observed: 2026-09-18.

### AINews (smol.ai / Latent Space)
- What: automated weekday roundup summarizing AI Discords, subreddits,
  and X, "over 150,000 top AI engineers," free with a paid option
  ([news.smol.ai](https://news.smol.ai/)). Karpathy blurbs it as the
  "best AI newsletter atm."
- Audience: working AI engineers. The closest audience overlap with
  alexandria's digest tier.
- Strengths: automation-first production like alexandria's, credible
  endorsements, high frequency.
- Weaknesses against alexandria: summarizes conversation, not
  literature. No claim-level provenance, no retrospective judgment, no
  skills output.
- Last observed: 2026-09-18.

### Latent Space
- What: newsletter, podcast, and community "by and for AI Engineers,"
  200k+ subscribers, 10M viewers across channels, free
  ([latent.space/about](https://www.latent.space/about)).
- Audience: the self-identified AI Engineer movement.
- Strengths: community moat (Discord, paper club, conferences), owns the
  "AI engineer" identity alexandria sells to.
- Weaknesses against alexandria: editorial essays and interviews, not a
  systematic record. Nothing loads into an agent.
- Last observed: 2026-09-18.

### Import AI
- What: Jack Clark's free weekly long-form research and policy
  newsletter, publishing steadily as of 2026-09-07
  ([jack-clark.net](https://jack-clark.net/)).
- Audience: researchers, policymakers, and readers who want one expert's
  synthesis.
- Strengths: singular authorial judgment, deep credibility.
- Weaknesses against alexandria: scales with one human's attention, no
  structured memory, free so it monetizes nothing alexandria wants.
- Last observed: 2026-09-18.

### The Batch (DeepLearning.AI)
- What: Andrew Ng's free weekly AI newsletter
  ([deeplearning.ai/the-batch](https://www.deeplearning.ai/the-batch/)).
- Audience: practitioners and students in the DeepLearning.AI funnel.
- Strengths: brand authority, education funnel behind it.
- Weaknesses against alexandria: news plus commentary, funnel for
  courses rather than a standalone knowledge product.
- Last observed: 2026-09-18.

### AlphaSignal
- What: "The Front Page of AI," real-time feed and newsletter tracking
  models, repos, and papers, free with a Pro tier surfacing on some
  articles ([alphasignal.ai](https://alphasignal.ai/)).
- Audience: engineers wanting real-time industry tracking.
- Strengths: speed, ranking mechanics, engineer-targeted curation.
- Weaknesses against alexandria: headline velocity without evidence
  depth. Another feed to keep up with rather than a record that keeps up
  for you.
- Last observed: 2026-09-18.

### Last Week in AI
- What: weekly AI news summaries on Substack with free and paid tiers
  ([lastweekin.ai/about](https://lastweekin.ai/about)).
- Audience: general-to-technical AI followers.
- Strengths: consistent cadence, podcast pairing.
- Weaknesses against alexandria: summary coverage in a crowded free
  band.
- Last observed: 2026-09-18.

### The Pragmatic Engineer (paid-newsletter comp)
- What: the #1 software/AI engineering newsletter on Substack, over 1M
  readers, $15/mo or $150/yr
  ([newsletter.pragmaticengineer.com/about](https://newsletter.pragmaticengineer.com/about)).
- Audience: engineers and engineering leaders.
- Strengths: the existence proof that individual engineers pay
  newsletter subscriptions at scale for judgment and depth they cannot
  get free. Clear free-teaser-to-paid mechanics: partial deepdives free,
  full articles paid.
- Weaknesses against alexandria: not AI-research-focused and produces no
  operational artifacts. As a comp rather than a competitor, its lesson
  is the free-sample funnel and the $15/$150 anchor.
- Last observed: 2026-09-18.

## Category 3 — agent skills and knowledge ecosystems

### Anthropic skills repo and the Agent Skills open standard
- What: [github.com/anthropics/skills](https://github.com/anthropics/skills)
  (176.9k stars, 20.9k forks observed 2026-09-18), free Apache-2.0
  skills. The format is an open standard at
  [agentskills.io](https://agentskills.io/), adopted by a large client
  showcase including Claude Code, Cursor, GitHub Copilot, Gemini CLI,
  OpenAI Codex, Goose, OpenCode, and dozens more.
- Audience: everyone building with agents.
- Strengths: the standard alexandria's product rides on. Free, official,
  massive distribution.
- Weaknesses against alexandria: examples and utilities, not distilled
  research judgment. Nobody at the standard layer validates that a skill
  reflects current evidence.
- Last observed: 2026-09-18.

### skills.sh (Vercel)
- What: npm-style skills directory and one-command installer across 22+
  agents, headline counter shows 1.44M skills/installs, top listings in
  the 0.9M-3.4M install range ([skills.sh](https://skills.sh/)).
- Audience: agent builders installing capabilities.
- Strengths: distribution rail with real volume, Vercel backing.
- Weaknesses against alexandria: an unranked free-for-all on quality.
  No provenance, no evidence, no revision-on-contradiction. Also a
  potential distribution channel for alexandria teaser skills rather
  than only a rival.
- Last observed: 2026-09-18.

### SkillsMP and the aggregator class
- What: aggregator indexing 800k+ skills scraped from public GitHub
  ([skillsmp.com](https://skillsmp.com/)), one of roughly eight active
  skills directories in 2026 (survey:
  [localskills.sh guide](https://localskills.sh/blog/claude-skills-marketplace-guide)).
- Strengths: catalog breadth.
- Weaknesses against alexandria: minimal curation by design. The flood
  is the point: skill supply is infinite and trust is the scarce good.
- Last observed: 2026-09-18.

### Smithery
- What: MCP server and skills registry, 21.8k+ hosted servers, hosted
  auth, recently acquired by Arcade.dev ([smithery.ai](https://smithery.ai/)).
- Audience: agent developers wiring tools.
- Strengths: solves auth plumbing, large registry.
- Weaknesses against alexandria: tools, not knowledge. Adjacent
  infrastructure rather than a competing library.
- Last observed: 2026-09-18.

## Paid-comp pricing shelf (non-AI-specific anchors)

- Stratechery Plus: $15/mo or $120/yr
  ([stratechery.com/stratechery-plus](https://stratechery.com/stratechery-plus/)).
- Lenny's Newsletter: $20/mo or $200/yr web pricing observed September
  2026 ([lennysnewsletter.com](https://www.lennysnewsletter.com/)).
- Market norm for paid newsletters generally: $10/mo and $100/yr is the
  standard across industries per beehiiv's State of Paid Newsletters
  2026 ([beehiiv.com](https://www.beehiiv.com/blog/the-state-of-paid-newsletters-2026)).

## Map notes

- 2026-09-18: initial map built on the first run. Categories 1 and 2
  are mature with entrenched free leaders. Category 3 is one year old,
  huge in volume, and has no quality layer yet. No observed product
  combines a judgment digest with validated agent skills, which is the
  slot alexandria claims.
