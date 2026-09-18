# Pitch deck — slide-by-slide content

Maintained by the sales agent (prompts/sales-agent.md, ADR-24). Written
2026-09-18 on owner dispatch, for the chair to build the actual deck from.
Every fact and figure below is sourced to a file in this repo or to
docs/market/'s dated research; nothing here is invented or aspirational
phrased as fact. Where a number carries a stated confidence level in the
source doc, that confidence is carried into the copy rather than smoothed
over — an investor-grade pitch that oversells its own market sizing is a
worse pitch, not a better one.

**For the designer:** each slide below is "Copy" (the words that go on
the slide, use verbatim or trim, don't embellish) plus "Visual direction"
(a plain-language brief for imagery/chart/layout — no chart has been
built, these are content briefs, not finished assets) plus, where useful,
"Speaker notes" (context for whoever presents, not meant to appear on the
slide itself). The owner decides the actual ask, the actual audience, and
the actual room this gets presented in — this file is the content
substrate, not the strategy for using it.

---

## Slide 1 — Title

**Copy:**
> Accelerate every builder to frontier speed.

That is the entire slide. No subtitle, no tagline underneath — this is
the owner's mission statement, final as of 2026-09-18, stated everywhere
alone by design (docs/vision.md:8-14: "the owner considered and deleted
[a companion line] on 2026-09-18; do not resurrect it"). Company name
"alexandria" and nothing else accompanies it.

**Visual direction:** the mission line, large, centered, on its own. No
logo lockup competing for attention if one doesn't exist yet.

---

## Slide 2 — The problem, two-sided

**Copy:**
> AI research moves faster than anyone can track — and faster than any
> skill library can stay trustworthy.

> "Keeping up with everything in AI is impossible." — practitioner
> comment, Hacker News, 2026

> A 2026 audit of 216 public Claude Code skills found 69% "won't
> reliably trigger," and 57% of subagents declare no tools list at all.

**Speaker notes:** two audiences, two failure modes. Humans can't track
the literature; agents are being handed unverified, unreliable
instructions. Sources: docs/market/report-2026-09.md §5 (HN quote,
news.ycombinator.com/item?id=48939630); docs/market/landscape.md
(skillcrossroads "State of Skills" report,
news.ycombinator.com/item?id=49744398).

**Visual direction:** split slide, human-side pain / agent-side pain.

---

## Slide 3 — The insight

**Copy:**
> Every AI product answers "what's new." None answers "what should I now
> believe — and what did we stop believing."
>
> Every skill marketplace sells instructions. None sells evidence.

**Speaker notes:** this is the gap docs/market/opportunities-2026-09-18.md
identifies as unclaimed by any observed competitor — retrospective
verdicts, and skills with attached evidence.

**Visual direction:** two short declarative statements, heavy whitespace.

---

## Slide 4 — What alexandria is

**Copy:**
> alexandria is an autonomous research organism building a standalone
> knowledge business. It turns the moving frontier of AI research into
> operational knowledge — a digest people read, and skills agents load.
>
> The product is the data layer and orchestration layer for frontier AI
> research and architecture. It's sold as skills, and — as the graph and
> automations mature — a memory layer. The newsletter is the interface
> that keeps a human in the loop; it is not the whole product.

**Speaker notes:** owner's own reframing, all-hands 2026-09-17, recorded
in docs/vision.md:18-21 and 43-46.

**Visual direction:** simple layered diagram — data layer, orchestration
layer, then the two customer-facing surfaces (digest, skills) on top.

---

## Slide 5 — Skills with receipts

**Copy:**
> Every skill ships with the evidence that justifies it: the papers it
> came from, the specific claims it rests on, and a dated result showing
> it actually changes model behavior.

> From the one skill live today:
> *"2026-09-12 A/B trial: bare Claude endorsed imitation fine-tuning on a
> stronger model's trajectories; with this skill loaded it refused, cited
> the 4-30 point regression, and prescribed harness adaptation plus
> on-policy single-turn correction."*

> Nobody else observed in this market attaches evidence to a skill.

**Speaker notes:** the quote is real, from
`skills/harness-engineering/SKILL.md`'s provenance block, not written for
this deck. "Nobody else" claim sourced to
docs/market/opportunities-2026-09-18.md ("800k+ scraped skills and zero
evidence trails").

**Visual direction:** show the actual provenance block, lightly restyled
— arXiv links, claim IDs, the dated quote — as a literal artifact, not a
mockup. Real receipts read better than any illustration of the concept.

---

## Slide 6 — The claim graph: a memory that never forgets

**Copy:**
> A graph that never forgets. Research on the research.
>
> Every claim is linked to what supports it, what contradicts it, and
> what came before it — append-only, time-directional, so nothing gets
> quietly rewritten. 254 claims, 88 edges, and growing every week.

**Speaker notes:** "A graph that never forgets" and "research on the
research" are the site's own live mission-page copy, independently
verified by the market agent's hands-on walkthrough
(docs/market/report-2026-09.md, "Where it beats the profiled class").
The 254/88 figure is the site's real structure-only snapshot as of
2026-09-13 (same report) — state the date if this deck is used after that
snapshot goes stale.

**Visual direction:** a small node-and-edge illustration, `supports` in
one color, `contradicts` in another — the shape, not a literal data dump.

---

## Slide 7 — The org of agents

**Copy:**
> alexandria runs itself. Nine active AI agent "seats" — engineering,
> skills, frontend, market research, project management, the weekly
> digest, organizational review, security, and OKRs — each with a
> standing charter, each shipping one pull request per run, reviewed by
> an independent agent panel before anything merges.
>
> This slide, and the plan behind it, was itself drafted by one of those
> seats — the sales agent — on the owner's dispatch, not written by a
> human from scratch.

**Speaker notes:** nine active seats plus two dormant (finance, sales)
per docs/agents/org-chart.md. The agent-panel gate is ADR-13
(docs/decisions.md:162+); the self-improving loop is ADR-7 and ADR-12.
The meta "this was agent-drafted" line is the same authentic hook
docs/sales/launch/x.md already plans to lead launch day with — true here
for the same reason, not a rhetorical flourish.

**Visual direction:** an org chart, human (owner, Product Owner) at top,
nine seats below, one arrow showing the agent panel gate before merge.

---

## Slide 8 — Why now

**Copy:**
> Skills became an open standard and instantly commoditized — hundreds of
> thousands of listings, almost no curation. Trust is now the scarce
> good, and nobody sells it.
>
> Paid newsletters are compounding: Substack's paid subscriptions grew
> from 5M to 8.4M in about a year; beehiiv's paid revenue more than
> doubled. Individuals are normalized to paying for niche expertise.
>
> Content is starting to publish for agents, not just humans — the
> leading skills directory already ships an agent-readable index.

**Speaker notes:** all three trends sourced to docs/market/report-2026-09.md
§5, with the Substack/beehiiv figures traced to Backlinko's Substack
statistics and beehiiv's own 2026 paid-newsletter report.

**Visual direction:** three short trend cards, one line each.

---

## Slide 9 — Market opportunity

**Copy:**
> TAM (arena ceiling): ~$1.8B/yr — 12M AI-building developers and
> technical leaders at a $150/yr blended price. A top-down ceiling, not a
> forecast.
>
> SAM (bought today): $20-40M/yr in individual-paid AI research
> intelligence and prosumer tooling, cross-checked from newsletter-audience
> and research-tool-platform data.
>
> SOM (alexandria, 3 years): $14k-144k ARR depending on free-list growth
> (5,000-20,000 readers) at a 2-5% paid conversion — on a ~$0 marginal
> cost base, which is the point: this business clears its bar at a scale
> that would kill a funded, ad-supported competitor.

**Speaker notes:** all three figures and their arithmetic are in
docs/market/report-2026-09.md §2, verbatim, including its own stated
confidence level: "moderate at order-of-magnitude level" — say that out
loud rather than let the numbers imply more certainty than they carry.

**Visual direction:** a funnel, TAM → SAM → SOM, each ring labeled with
its range, not a single point estimate.

---

## Slide 10 — Competitive landscape

**Copy:**
> | | Research tools (Elicit, Consensus) | AI digests (TLDR, Import AI) | Skill marketplaces (skills.sh, Smithery) | alexandria |
> |---|---|---|---|---|
> | Judgment, not just search | ✕ | ✕ | ✕ | ✓ |
> | Evidence attached to output | ✕ | ✕ | ✕ | ✓ |
> | AI-engineering specific | ✕ | partial | ✓ | ✓ |
> | Paid tier that isn't "more content" | partial | ✕ | ✕ | ✓ |
>
> alexandria doesn't outcover TLDR or outsearch Elicit — and shouldn't
> try. It sits in the one cell nobody else occupies.

**Speaker notes:** table condensed from docs/market/report-2026-09.md §4
and its full competitor detail in docs/market/landscape.md. Say plainly:
this is a narrow, honest position, not a claim of beating every axis.

**Visual direction:** the table as shown; keep it to four rows so it
reads at a glance from the back of a room.

---

## Slide 11 — Pricing

**Copy:**
> The digest is free — full issues, no paywall. It's the acquisition
> engine and the human-in-the-loop interface.
>
> The operational layer is $20/month: the skill library, claim-graph
> access, and automations as they ship.
>
> No dark patterns: subscribers actively choose autorenew or a monthly
> reminder to renew. The subscription can lapse at the end of any month
> until someone says yes again — never by someone forgetting to cancel.

**Speaker notes:** pricing decided at the 2026-09-17 all-hands
(docs/allhands/2026-09-17.md, decision 1); billing-honesty principle is
docs/vision.md:106-110. If asked about annual pricing: a ten-month
annual anchor (~$200/yr) is evidence-supported by the comp set but not
yet a decided price — say "under evaluation," not "$200/year."

**Visual direction:** two tiers side by side, free vs. $20/month; a small
badge or line calling out the renewal-honesty point as a trust signal,
not buried in fine print.

---

## Slide 12 — Distribution: master one channel first

**Copy:**
> Peter Thiel's law: distribution follows a power law. One channel wins;
> the discipline is picking it and mastering it, not spraying across ten.
>
> alexandria's one channel is the free digest — the only channel it owns
> outright, already the architecturally decided acquisition engine, and
> the same audience that converts into the paid tier without needing a
> separate campaign to reach.
>
> Distribution is also built into the product itself: every skill's
> evidence trail travels with the file when it's shared agent-to-agent;
> every digest finding is designed to end in its own runnable skill;
> every ADR is free proof-of-work content, because the org would have
> written it anyway to run itself.

**Speaker notes:** full detail and sourcing in
docs/sales/distribution-plan.md.

**Visual direction:** one large channel (the digest) with smaller arrows
showing how it feeds the paid tier and the other one-time launch
channels (HN, X, LinkedIn) as secondary spokes, not equal peers.

---

## Slide 13 — GEO: getting cited by the machines that answer for us

**Copy:**
> alexandria's structure is already the format AI answer engines quote:
> claims with evidence, statistics, and citations, built for research
> integrity — and, it turns out, exactly what gets cited.
>
> Three games, three horizons:
> - **Retrieval** — per-claim public pages, stats-forward and quotable,
>   built from original numbers only alexandria publishes.
> - **Agents** — an agent-readable manifest, a public cited claims
>   endpoint, and MCP as a front door agents can query directly.
> - **Training data** — the public repo and its decision record, seeding
>   what future models know about alexandria before most competitors
>   have any public footprint at all.

**Speaker notes:** full sequencing, honest current-state caveats (none of
this is live yet — it's a sequenced build plan), and sourcing in
docs/sales/geo-plan.md. Say clearly that this is a plan, not a claim of
current citations.

**Visual direction:** three horizons on a simple timeline — near
(retrieval), mid (agents), long/uncontrollable (training data).

---

## Slide 14 — Where we actually are today

**Copy:**
> Under 20 subscribers, all comped friends and family, by design — quality
> before paywall.
>
> One skill in gold, with a real validation result.
>
> Launching Tuesday, October 13, 2026. Scrum style: ship minimal, then
> update continuously — not wait for every feature to be ready.

**Speaker notes:** deliberately unglamorous and exact. docs/vision.md:120
for the subscriber count and comped status; docs/allhands/2026-09-17.md
decision 2 for the launch date and scrum framing. An honest early-stage
slide reads as credible, not as weak — especially next to the $0
cost-base story on slide 9.

**Visual direction:** plain text, no chart — this slide is the reality
check, keep it visually quiet.

---

## Slide 15 — Why this compounds

**Copy:**
> The claim graph and every skill's evidence trail get stronger every
> week and can't be copied backward — a competitor starting today would
> need alexandria's last year of curated, evidence-linked claims to catch
> up, and there's no shortcut for that.
>
> Because the pipeline's marginal cost is near zero, subscription revenue
> is nearly pure margin — this business is durable at a scale that would
> sink a funded, ad-dependent competitor.

**Speaker notes:** docs/vision.md:112-114 and
docs/market/report-2026-09.md §7 ("both compound with time, which is the
moat volume players cannot copy backward").

**Visual direction:** an upward-compounding line (claims/skills over
time) next to a flat line (a hypothetical same-day competitor) — simple,
not a real chart, illustrative only.

---

## Slide 16 — Close

**Copy:**
> Accelerate every builder to frontier speed.
>
> [The specific ask — subscribe, partner, invest, cover — is the owner's
> to choose for this room. This deck's job ends at making the case;
> she decides what to ask for and sends it herself.]

**Speaker notes:** deliberately left open. The sales-agent charter's one
law is "the agent prepares, the owner sends" (prompts/sales-agent.md) —
that applies to the ask itself, not only to who clicks send.

**Visual direction:** return to the title slide's treatment — the
mission line alone — as a bookend.

---

## Change log

- 2026-09-18: first version, this run, owner dispatch (draft PR, branch
  sales/2026-09-18-geo).
