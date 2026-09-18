# Opportunities report — 2026-09-18

Owner's directive from the 2026-09-17 all-hands (docs/allhands/2026-09-17.md):
"beyond pricing... product quality, gaps in the market, features, and a lot
of creativity on where our project could go." Pricing is decided (free
digest, $20/month paid spine); this report does not revisit it. See
docs/market/positioning.md for the pricing evidence and
docs/market/landscape.md for the full competitor map this report draws on.

Every idea below stays inside the owner's differentiation line, added
2026-09-17: "specifically technical research, systems, and directly
applicable tools for orchestration essentially," not AI news.

## Where the market has a real hole

**A citation-backed claim graph for agent-building technique claims doesn't
exist anywhere observed.** Elicit and Consensus do paper search and
extraction over general academic literature. Neither tracks a persistent,
queryable graph of specific technical claims about orchestration or agent
techniques — "does prompt-caching pattern X reduce cost by Y%," with
supporting and contradicting evidence linked. Alexandria already has the
shape of this (docs/vision.md §1's trailblazing/matured/left-behind
structure, the claim graph's `supports`/`contradicts` edges). This is the
most defensible asset in the whole landscape, because it compounds — a
competitor with the same LLMs cannot replicate a year of curated,
evidence-linked claims overnight.

**"Skills with receipts" is open. Nobody attaches evidence to a skill.**
Every skill marketplace observed this run (skills.sh, skillbay.sh,
Smithery-hosted registries, Anthropic's own directory) sells or lists
skills as unverified catalog items. A Show HN "State of Skills" report
found 69% of 216 public Claude Code skills "won't reliably trigger," and
57% of subagents declare no tools list — a real quality crisis
(news.ycombinator.com/item?id=49744398, 2026-09-17, sourced in
landscape.md). Alexandria uniquely has both the research engine and a
skill-authoring pipeline (prompts/skill-extract.md per the ideas ledger).
Pairing every skill-library entry with the claim-graph citation and a
confidence score that justifies it is not done anywhere in this market.

**No independent benchmark exists for orchestration patterns**, the way
Chatbot Arena benchmarks models. Nobody is systematically tracking which
multi-agent pattern actually reduces latency, cost, or error rate for a
given task class in a reproducible way — an Ask HN thread on multi-agent
production use (news.ycombinator.com/item?id=49689454, 2026-09-13) found
practitioners explicitly asking for this and finding nothing: "I've not
really seen anything outstanding in this space" on multi-agent
observability. Since the digest already curates this territory
editorially, formalizing it into a maintained, versioned benchmark (queryable
as part of the $20/month tier) would be novel and hard to copy given the
curation lead time required.

## Feature ideas, grounded in this week's evidence

1. **A skill-verification badge.** Every skill in the library ships with
   "verified against N sources, confidence X" pulled straight from the
   claim graph, and a trigger-reliability score (directly answering the
   skillcrossroads "69% won't reliably trigger" finding). This turns a
   quality problem the whole ecosystem has into a checkable differentiator
   nobody else can show.

2. **A "from digest to running tool" pipeline**, not a static skill
   library. When a digest issue reports a technique, the paid tier ships a
   versioned, deployable implementation of that exact technique, linked
   back to its claim-graph entry. This is the concrete answer to the HN
   skepticism captured in the skillbay.sh thread ("why would I buy a
   markdown file"): the product isn't a file, it's the file plus the
   evidence plus the working implementation, updated when the evidence
   changes.

3. **Context-scoped skill delivery.** A Show HN post this week
   (news.ycombinator.com/item?id=49698184, "Skillzero," 2026-09-14) surfaced
   a live operational pain: skill libraries bloat the context window across
   unrelated tasks, and a commenter specifically asked whether scoping
   works "on repo level." Any skill-library UX alexandria ships should
   default to scoped loading (only the skills relevant to the current
   task/repo), not a dump of the whole library into context. This is a
   craft detail worth handing to the engineer agent, not a pricing or
   positioning question.

4. **An orchestration-pattern benchmark as a standing feature**, not a
   one-off report: a maintained, versioned table of multi-agent and
   harness patterns with measured cost/latency/error tradeoffs, each row
   backed by claim-graph evidence. This is the productized version of the
   "no observability tooling exists" gap surfaced on HN this week.

5. **A visible provenance trail per subscriber-facing artifact** (digest
   claim, skill, or automation): where the underlying evidence came from,
   whether it has been contradicted since, and when it was last checked.
   Microsoft's Agent Framework team published a post this week arguing
   that giving an orchestrator "competence plus access to operations" (a
   skill) beats spinning up nested specialist agents
   (devblogs.microsoft.com/agent-framework/..., 2026-09-16) — third-party,
   non-alexandria validation that skills-as-a-first-class-unit is the
   right industry direction, worth citing in owner-facing pitch material.

## Where not to compete

- **Don't rebuild paper-search infrastructure.** Elicit (138M papers
  indexed, funded, $49-169/month tiers) and Consensus ($20/month) already
  own academic paper search and extraction. Cite and integrate, don't
  compete.
- **Don't rebuild raw web-search or RAG infrastructure.** Exa has already
  commoditized agent-facing search/retrieval at pay-as-you-go pricing
  ($7/1,000 requests) and just raised a $250M Series C at a $2.2B
  valuation (Bloomberg, 2026-05-20) — well-capitalized infrastructure
  players own this layer now.
- **Don't build "another orchestration engine."** LangGraph, CrewAI, n8n,
  and Dify already give away workflow-building tools for free. The
  defensible move is not a generic engine but automations inseparable
  from alexandria's own editorial content and claim graph — something a
  generic OSS project cannot copy without also doing alexandria's
  research and curation work.
- **Don't chase the AI-news category at all**, confirmed again this run:
  TLDR AI is free, ad-supported, 1.1M subscribers, and no AI-news product
  observed (The Batch, AlphaSignal, Last Week in AI) has a viable paid
  tier for news itself. This is fully commoditized at $0. Staying out of
  it, as the owner directed, is the right call on the evidence, not just
  on principle.

## Later-stage direction (not a launch-day proposal)

SemiAnalysis's retail-vs-institutional split (a $500/year public
newsletter alongside a separately priced "Core Research" product reported
on track for roughly $100M/year from buy-side demand) and Lenny's $350/year
"Insider" tier both show the same pattern: organizations that treat a
research product as infrastructure, not personal reading, will pay a large
multiple over the individual price for API-level claim-graph access, higher
automation quotas, or dedicated support. Worth keeping on the roadmap as a
team/institutional tier once the $20/month individual tier is proven, not
something to build before launch.

## Sourcing

Every claim above is sourced in docs/market/landscape.md or
docs/market/briefs/2026-09-18.md. This report adds no new unsourced
market facts; it recombines this week's evidence into feature and
direction proposals.
