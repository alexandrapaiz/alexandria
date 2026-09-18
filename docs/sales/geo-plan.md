# The GEO plan — getting cited by the machines that answer for us

Maintained by the sales agent (prompts/sales-agent.md, ADR-24). Written
2026-09-18 on owner dispatch (complete creative liberty, ambitious brief),
building on docs/sales/calendar.md, docs/market/ (in full), and the
project-board directive "Define alexandria's distribution system (Thiel)"
— see docs/sales/distribution-plan.md for that doctrine; this doc is its
GEO-specific companion. One law still governs every action item below:
**the agent prepares, the owner or the named engineering seat builds and
ships; sales never posts, publishes, or deploys anything itself.**

## Why this, why now

Generative engine optimization (GEO) is the practice of shaping content so
AI systems that synthesize answers — ChatGPT, Claude, Perplexity, Google's
AI Overviews, and the agents built on top of them — trust it enough to
cite it or load it. It is the successor discipline to SEO for a world
where, per GEO firm Brandlight's tracking, the overlap between top Google
results and AI-cited sources has fallen from roughly 70% to under 20%
(reported in [Digital Authority's 2026 GEO trends piece](https://www.digitalauthority.me/resources/generative-engine-optimization-trends/)).
The same piece reports Princeton research finding that citing sources,
adding statistics, and including quotations lift AI-citation visibility
30-40% over unoptimized content — precisely the three things a claim in
alexandria's graph already does by construction, not as a copywriting
trick bolted on afterward.

Two adjacent findings from this run's research, both relevant to sequencing
below:

- **Citation mechanics reward exactly our shape.** Reporting aggregated in
  [Omnibound's 2026 AEO statistics](https://www.omnibound.ai/blog/answer-engine-optimization-aeo-statistics)
  and [Acquia's AEO content-structure guide](https://www.acquia.com/blog/aeo-content-strategy-how-structure-pages-ai-citation)
  describes AI engines preferring pages with a dense, front-loaded
  data point, comparison tables and FAQ sections (because they arrive
  "pre-broken into extractable units"), and content refreshed within the
  last 6-12 months. A single page with one real statistic can out-cite
  pages with many backlinks, because AI engines cite *original data*, not
  authority — third-party stats get cited back to their original source,
  never to whoever merely repeats them.
- **The agent-readable layer is early and thin, which is an opening, not a
  blocker.** [llmstxt.org](https://llmstxt.org/) (the spec's own site) and
  [a 2026 llms.txt adoption survey](https://codersera.com/blog/llms-txt-complete-guide-2026/)
  agree it remains a community proposal, not an IETF/W3C standard, sitting
  at roughly 5-15% adoption among tech/dev-tool sites, treated as the
  "gold standard" move for AI-native companies (Anthropic, Cursor, Vercel
  are named), even though major crawlers don't yet fetch it and no citation
  study has proven it works. On MCP: 2026 coverage of agent-facing
  infrastructure ([tooldirectory.ai's "state of MCP servers"](https://tooldirectory.ai/blog/state-of-mcp-servers-2026),
  [Obot AI's MCP discovery survey](https://obot.ai/resources/learning-center/mcp-tool-discovery/))
  describes MCP as already "the front door" for agent-native infrastructure
  companies (Firecrawl, Browserbase, Exa, Mem0 are the named examples), with
  discovery now standardizing around `.well-known` server manifests
  (SEP-1649/SEP-1960). Doing this now, while the bar is low and the
  standard is still forming, is cheap; waiting until it is obvious is not.

## Our unfair advantage, stated plainly

Every other player in this market has to *manufacture* GEO-friendly
content: bolt statistics onto marketing copy, retrofit quotable pull-quotes
onto essays that weren't written that way. Alexandria doesn't, because the
product's actual internal structure already is the GEO/AEO recipe:

- **A claim is already an atomic, evidenced, quotable unit.** Per ADR-10
  (docs/decisions.md:98-113), every claim in the graph carries its
  evidence and time-directional relations (`supports` / `refines` /
  `contradicts` / `duplicates`) in Postgres, append-only. That is
  structurally identical to what AEO guides mean by "pre-broken into
  extractable units" — we didn't design it for search engines, we designed
  it for research integrity, and it happens to be the exact shape.
- **A skill's provenance block is a ready-made citation card.** The one
  skill that exists today, `skills/harness-engineering/SKILL.md:5-16`,
  ships with a `provenance` block naming its source papers by arXiv link,
  its supporting claim IDs, and a dated, quoted validation result: *"2026-
  09-12 A/B trial: bare Claude endorsed imitation fine-tuning on a
  stronger model's trajectories; with this skill loaded it refused, cited
  the 4-30 point regression, and prescribed harness adaptation plus
  on-policy single-turn correction."* That sentence is an original number
  nobody else publishes, attached to a real claim, dated. It is, unedited,
  a GEO-optimized quote.
- **The public repo is already positioned as the credibility engine.**
  Vision.md says it outright: "the public repo carries the code, prompts,
  and ADRs as the credibility engine, and the newsletter is the product"
  (docs/vision.md:139-140). Twenty-four dated ADRs (docs/decisions.md)
  already exist. This is the training-data game's raw material, already
  produced as a byproduct of how the company runs itself, not as a
  marketing initiative.

## The honest baseline today

Per charter, no claim below promises what the product does not do yet.
The current, checked-2026-09-18 state:

- **Nothing about the claim graph is crawlable or citable by anything
  outside the owner's own MCP session.** The graph has no public API.
  `site/app/graph/page.jsx` renders a hardcoded static snapshot ("254
  claims, 88 edges," `site/lib/graph-data.js:1-3`) with claim *text*
  deliberately withheld ("claim texts are the product and never ship to
  non-members"). The only thing that can query real claim text is the
  MCP server's `semantic_search`/`sql_query`/`rag_answer` tools
  (`mcp/server.py`), and those sit behind the owner's own OAuth 2.1
  passphrase (ADR-11, docs/decisions.md:116-142) — built for one user's
  agent, not as a public surface.
- **The digest itself is not on the public web at all.** Digests are
  email-only; the `digests/` folder is gitignored by design (docs/vision.md:138-139).
  There is no page today for a crawler to index, which is the same
  blocker docs/sales/calendar.md already flagged for the signup ask —
  here it is fatal for GEO specifically: you cannot get cited from a page
  that doesn't exist.
- **`llms.txt` does not exist yet.** It is already a proposed ledger item
  (docs/ideas.md, "Agent-readable public surface: llms.txt and a skills
  manifest," market agent, 2026-09-18; also docs/backlog.md:122,228),
  gated behind the site actually being deployed. This plan sequences it,
  it does not re-propose it.
- **One skill exists in gold** (skills/harness-engineering/SKILL.md).
  Every claim below that says "per skill" describes a repeatable motion
  applied as new skills ship, not a claim that a library exists today.

Everything sequenced below is written against that baseline, and every
day-sized item names the engineering seat that would actually build it —
sales drafts the plan and can log it to the ledger; it builds nothing.

## Three games, sequenced

### Game 1 — retrieval citations (get quoted in the answer)

Goal: make individual, narrow, stats-forward pages that an AI answer
engine can lift a sentence from and attribute to alexandria by name.

| Day | Item | Depends on | Seat |
|---|---|---|---|
| 1 | **Per-claim public pages.** One static, server-rendered page per matured or deprecated claim (not the whole graph — one claim, its evidence, its `supports`/`contradicts` history), URL-stable, with a 40-60 word direct-answer block at the top of the page (the AEO front-loading pattern above) stating the claim and its confidence in plain declarative prose. Sequenced *after* the already-proposed "Public digest archive page" (docs/ideas.md, OKR agent, 2026-09-17) and "Make 'left behind' the public flagship" (docs/ideas.md, market agent, 2026-09-18) land, since both need the same digest-to-page rendering path this reuses. | Public digest archive + left-behind flagship items | engineer/frontend |
| 2 | **Schema markup and entity naming.** Add `Article`/`FAQPage` structured data (schema.org) to claim pages and the one live skill page, and standardize the entity name "alexandria" identically across the site, GitHub, and any future off-site listing (agentskills.io, MCP registries) — AI crawlers and answer engines use consistent entity naming to resolve who is being cited. | Item 1 | frontend |
| 3 | **Crawler allow-list audit.** Check `site`'s `robots.txt` and any Vercel edge config explicitly allow the named AI crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended) rather than silently blocking them by default — a real, common failure mode the GEO research above calls out ("many sites block AI crawlers without realizing it"). One-line config check, zero design work. | Site deployed | engineer |
| 4 | **Freshness as a byproduct, not a task.** The graph is already append-only and time-directional (ADR-10) — when a claim page's supporting or contradicting edge count changes, its "last checked" date should update automatically from `claim_links.created_at`, not from a manual edit. AEO research above ties freshness within 6-12 months to the majority of citations; alexandria's weekly cadence already produces this if the page just reads the timestamp instead of hardcoding it (the same hardcoded-metric mistake market's report already flagged on the homepage counter — don't repeat it here). | Item 1 | engineer |
| 5 | **Publish the existing A/B result as its own quotable page.** The harness-engineering skill's validation stat is real and dated but has never left the frontmatter of a markdown file in this repo. Give it one page: the method, the "4-30 point regression" number, and the claim IDs it rests on. This is also market's already-proposed "published head-to-head" ledger item (docs/ideas.md, 2026-09-18) — this plan just marks it GEO-relevant, not a new item. | — | market/skill |

### Game 2 — the agent game (get loaded, not just read)

Goal: make alexandria a source an *agent* can query or load directly,
not only a page a human reads and an AI happens to summarize.

| Day | Item | Depends on | Seat |
|---|---|---|---|
| 1 | **`llms.txt`.** Already proposed (docs/ideas.md, market agent, 2026-09-18): a static file at the site root pointing agents to the highest-signal pages (mission, one skill, the digest archive once public). This plan sequences it first in this game since everything else here assumes it exists. | Site deployed | engineer |
| 2 | **The skills manifest.** The same ledger item's second half: a JSON route listing skill name, description, and provenance summary for every gold skill — the "agent-readable skills manifest" the owner's dispatch names directly. At one skill, this ships as a manifest of one; the shape is what matters, since it grows automatically as the skill agent ships more. | Item 1 | engineer/skill |
| 3 | **NEW — a public, read-only, cited claims endpoint.** Distinct from the existing MCP tools, which are authenticated and built for the owner's own agent (ADR-11): a narrow, unauthenticated `GET` surface (e.g. `/api/claims/{id}`) returning exactly the claim text, its evidence, and its supports/contradicts counts for *matured or deprecated* claims only — never anything still paywalled, never a bulk dump of the graph. This is the "claim graph as an agent-queryable cited endpoint" the dispatch asks for, scoped narrowly enough to ship in a day and to never leak paywalled or in-progress claims. Logged as a new ledger item below. | Item 1, claim pages (Game 1 item 1) | engineer |
| 4 | **NEW — MCP as the public front door.** Not a change to the existing owner-only MCP server (ADR-11's OAuth passphrase layer stays exactly as it is — it holds real authority and should never be loosened). A *second*, read-only MCP surface exposing `semantic_search` and `rag_answer` scoped to the same matured/deprecated claim set as item 3, no auth required, so any MCP host — Claude, or any other agent that speaks the protocol — can query alexandria's claim graph as a tool and get a `[C<id>]`-cited answer back, the same citation format `mcp/server.py`'s `rag_answer` already produces internally (`mcp/server.py:176-203`). This is genuinely new build work, not a docs change, and it is the one item on this whole plan that most directly matches "MCP as the front door" — flagged here as the highest-leverage, hardest item, not claimed as already live. | Item 3 | engineer |
| 5 | **Submit to the surfaces that index agents.** Once items 1-4 exist: list on agentskills.io (docs/ideas.md already flags this as OKR-proposed, 2026-09-17, "List the gold skills at agentskills.io") and register the public MCP surface with at least one MCP registry (Smithery is the one this run's market research names as already hosting the skills-adjacent ecosystem, docs/market/landscape.md). Distribution for the agent game specifically, not a repeat of the digest's own distribution channel (see docs/sales/distribution-plan.md). | Items 1-4 | sales drafts the listing copy; engineer submits |

### Game 3 — the training-data game (get remembered, not just retrieved)

Goal: seed the long-run, uncontrollable layer — what a model's own weights
"know" about alexandria the next time it's trained, independent of any
live retrieval at all.

This game has no day-sized build items, honestly, because it is mostly
already true and moves on a timeline nobody controls (model pretraining
cycles, not sprints):

- **It's already happening.** The public repo — code, prompts, 24 dated
  ADRs — is already vision.md's stated credibility engine
  (docs/vision.md:139-140), already public, already the ExO's standing
  responsibility to keep truthful (all-hands 2026-09-17, decision 9). The
  single highest-leverage action here is *keep doing exactly that,
  consistently*, not a new initiative.
- **One real addition worth a day:** a plain-prose, third-person
  self-description of what alexandria is — company, product, mission,
  differentiation — living at the repo root (or folded into the existing
  README) in the declarative, encyclopedic register that pretraining
  corpora tend to weight (as opposed to this repo's own first-person,
  in-progress ADR voice). Right now, nowhere in the repo states "alexandria
  is a company that does X" in one clean paragraph a future model could
  lift whole. This is the single artifact most likely to become the
  seed of what a model "knows" about us before launch, since it's one of
  the only descriptions of alexandria that will exist anywhere on the
  public web pre-launch. Seat: exo (README is its lane per all-hands
  decision 9) or PM; sales flags it here, does not own the README.
- **Otherwise: patience is the strategy.** No tracking metric exists for
  "did a model learn about us," and inventing one would be exactly the
  kind of unfalsifiable claim the charter prohibits. Log it, don't chase it.

## Sequencing summary

Games 1 and 2 both gate on the site actually being deployed and the digest
archive existing publicly — neither is sales' lane to build, both are
already-proposed engineering ledger items this plan depends on rather than
duplicates. Game 3 needs nothing except continuing what the org already
does. Read as: **GEO is not a pre-launch campaign, it is a permanent
property of how the product is built** — every item above, once shipped,
keeps producing citations for free, forever, at the ~$0 marginal cost the
whole architecture is built around (docs/vision.md:112-114).

## Measurement, honestly

No paid GEO-tracking tool is proposed here — there is nothing to track yet
(zero public claim pages, zero llms.txt, zero public MCP surface as of
this writing). Once Game 1 item 1 ships, the honest measurement is manual
and cheap: periodically ask ChatGPT, Claude, and Perplexity what alexandria
is and whether they cite a claim page, and log any real citation sighted
the same way docs/sales/results.md already logs only what actually
happened, never an estimate.

## New ledger items this plan proposes

Appended to docs/ideas.md in the standing append-and-verdict format,
trigger and status intact for the owner to accept or reject:

1. **A public, read-only, cited claims endpoint** (Game 2, item 3 above).
2. **A public, read-only MCP surface, scoped to matured/deprecated claims
   only, distinct from the owner's authenticated MCP layer** (Game 2, item 4
   above).

Both are engineering builds, not sales output; sales logs them because the
distribution and GEO case for building them is sales' evidence to make.

## Sources

- [Digital Authority — Generative Engine Optimization Trends To Watch In 2026](https://www.digitalauthority.me/resources/generative-engine-optimization-trends/)
- [Omnibound — Answer Engine Optimization (AEO) Statistics (2026)](https://www.omnibound.ai/blog/answer-engine-optimization-aeo-statistics)
- [Acquia — AEO Content Strategy: How to Structure Pages for AI Citation](https://www.acquia.com/blog/aeo-content-strategy-how-structure-pages-ai-citation)
- [llmstxt.org — the /llms.txt file, v2](https://llmstxt.org/)
- [Codersera — llms.txt Explained (May 2026)](https://codersera.com/blog/llms-txt-complete-guide-2026/)
- [tooldirectory.ai — The state of MCP servers in 2026](https://tooldirectory.ai/blog/state-of-mcp-servers-2026)
- [Obot AI — MCP Tool Discovery: How It Works & 5 Tools to Know in 2026](https://obot.ai/resources/learning-center/mcp-tool-discovery/)

## Change log

- 2026-09-18: first version, this run, owner dispatch (third run tonight,
  full creative liberty).
