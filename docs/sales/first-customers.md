# First customers — day 1 to day 30 after launch

Written 2026-09-18 by the sales agent (prompts/sales-agent.md, ADR-24)
on owner dispatch, fourth run. This is the plan the owner's critique in
docs/agents/incidents.md item 11 asked for and the previous run did not
deliver: **how customers 1 through 50 actually arrive**, by name, by
motion, by asset, by day — individuals and companies both.

Companions written the same run: docs/sales/idea-list.md (the ranked
idea bank this plan draws its moves from) and
docs/sales/outreach-plan.md (the outreach machine that powers lanes C
and E below, with every draft written out). This file is the schedule;
that file is the engine.

**The law, unchanged and above everything here: the agent prepares, the
owner sends.** Nothing in this document has been sent, posted, listed,
registered, or contacted. Every date below is a date the owner may move,
and every draft is hers to edit or bin.

---

## 1. What counts as a customer

The previous runs blurred this, so it gets fixed first. Three different
numbers get called "growth" around here and only one of them is revenue:

| Term | Definition | Day-30 target |
|---|---|---|
| **Free subscriber** | On the free digest list, full issues, $0 | 600 |
| **Customer** | Paying for the $20/month spine, or on a paid B2B agreement, one seat = one customer | **50** |
| **Comped** | Friends and family on the list at $0 by decision (roadmap sprint 1) | not counted, ever |

"Customers 1 through 50" in this plan means **50 paying seats by
2026-11-11 (day 30)** — $1,000/month recurring at the decided $20 price
(docs/allhands/2026-09-17.md, decision 2). The free-list number is the
leading indicator, not the goal; O1's own tracked-not-graded line asks
for 50 free subscribers by 2026-12-31, and this plan is designed to
clear that in the first week and then keep going, because the free list
is the acquisition engine (docs/sales/distribution-plan.md) and 50 paying
customers cannot come out of a 50-person free list.

Why 50 and not a rounder ambition: O1 KR2 is *profitable at launch*.
Fifty seats at $20 is $1,000/month against a cost base the architecture
designed to be near zero (docs/vision.md:112-114). **Sales does not
invent the actual monthly cost figure** — that number belongs to the
finance seat (prompts/finance-agent.md) and should be on the table
before launch day, because it is the only thing that converts "50
customers" from a nice number into the proven KR. If the real cost base
is higher than $1,000/month, this plan's target is wrong and should be
raised, not the claim of profitability softened.

---

## 2. The arithmetic of 50

Eight lanes. None of them individually has to work for the total to
land, which is the point of building it this way — the previous plan's
implicit bet was "the launch post goes well," which is not a plan, it is
a wish with a date on it.

| # | Lane | Who it reaches | Paid seats by day 30 | Confidence |
|---|---|---|---|---|
| A | The owner's own network, worked deliberately | ~40 named people she already knows | 8 | High — the only lane that doesn't depend on strangers |
| B | Launch-day public posts (HN, X, LinkedIn, Reddit) | 2,000-8,000 visitors | 15 | Medium — highest variance item in the plan |
| C | Direct outreach to practitioners who publicly stated our exact problem | ~60 people over 4 weeks | 5 | Medium-high — small volume, extreme fit |
| D | Curator and community mentions (newsletters, podcasts, subreddit regulars) | their audiences | 3 | Low-medium — slow, lagging, worth starting anyway |
| E | **B2B: team seats** — two small teams closing in month one | 2 companies | 10 (5 seats each) | Medium — needs an invoice path by day 14 |
| F | **B2B: first licensing or retainer conversation** | 1 agreement | 5 (seat-equivalent floor) | Low for month one; the pipeline matters more than the close |
| G | The agent-to-agent channel: skills in public registries carrying their provenance | agents and their humans | 4 | Low-medium — compounding, not spiky |
| H | Second-order: forwards, the referral ask, week-2 and week-3 digests converting the free list | the free list itself | 10 | Medium — mechanical, follows from A-G landing |
|  | **Total** |  | **60** |  |

Sixty planned against a target of fifty, because lanes fail. The plan is
built with a 20% cushion so that one lane going to zero — most likely B,
see §8 — does not put the KR out of reach.

### The conversion assumptions, stated as assumptions

Every number above rests on these, and they are assumptions, not
findings. They are written down so that on day 30 we can see which one
was wrong instead of arguing about it.

1. **Free-to-paid conversion of 2-5%** in the first 30 days. This is not
   invented here: it is the same range docs/market/report-2026-09.md
   used for its SOM math, reused rather than re-derived
   (docs/sales/distribution-plan.md restates it). Day-1 conversion runs
   at the top of that range and decays, because launch-day traffic is
   self-selected toward buyers.
2. **A Show HN that lands on the front page for a few hours** produces
   low-thousands of visitors. A Show HN that does not produces a few
   hundred. There is no middle. Lane B's 15 assumes the first; §8 is what
   we do on the second.
3. **A visitor who reads one full skill file with its provenance block
   converts at several times the rate of a visitor who reads the
   homepage.** This is the entire product thesis (docs/market/positioning.md)
   and it is testable on day 1: if the skill pages are not the highest
   converting pages on the site, the thesis is wrong and the pitch needs
   rewriting before week 2, not after month 3.
4. **One team seat is sold by talking to one engineer, not one
   procurement department.** At 20-200 person companies the AI-tooling
   budget is usually an engineering-leader card, not a purchasing cycle.
   Lane E is a five-seat sale to a person, not an enterprise deal.

---

## 3. Who exactly — the individual segments, with real archetypes

The segments are docs/market/report-2026-09.md §3. What that report does
not have, and what this plan adds, is **the archetype: a real, dated,
public artifact of a person with this problem**, so the copy can be
written at a specific human instead of a persona.

### A1 — The burned skill installer

**The archetype, real and dated:** whoever ran the audit behind
"Show HN: Linting 216 public Claude Code skills — 69% won't reliably
trigger" ([news.ycombinator.com/item?id=49744398](https://news.ycombinator.com/item?id=49744398),
2026-09-17), and every commenter in that thread who recognised the
number from their own experience.

**What they believe:** skills are a good idea executed badly; most
public ones are LLM-generated filler; there is no way to tell the good
ones apart without reading all of them.

**Why they pay:** they are already spending unpaid time doing manual
verification. Alexandria's provenance block is that work, done, with the
receipts attached — `skills/harness-engineering/SKILL.md` names its
claim IDs, its five source papers by arXiv link, and a dated A/B result.

**The asset that converts them:** not the homepage. The raw skill file
on GitHub, which already exists and already works as a pitch. The one
line that does the work: *"2026-09-12 A/B trial: bare Claude endorsed
imitation fine-tuning on a stronger model's trajectories; with this
skill loaded it refused, cited the 4-30 point regression, and prescribed
harness adaptation plus on-policy single-turn correction."*

**Which lane:** B (they read HN), C (direct note), G (they browse
registries).

### A2 — The multi-agent operator in production

**The archetype, real and dated:** the practitioners in the Ask HN
thread on production multi-agent systems
([news.ycombinator.com/item?id=49689454](https://news.ycombinator.com/item?id=49689454),
2026-09-13), where the state of observability tooling was summarised as
"I've not really seen anything outstanding in this space."

**What they believe:** multi-agent is mostly vibes; nobody publishes
comparative numbers; every architecture decision is made on a blog post
and a hunch.

**Why they pay:** the claim graph is the only thing in this market that
tracks *which orchestration claims survived contact with evidence*, with
`supports` and `contradicts` edges over time (ADR-10). That is the
substitute for the benchmark that does not exist.

**The asset that converts them:** a single "left behind" verdict, public
— one technique named, with the contradicting evidence and the dates.
This is the public-flagship idea already in the ledger
(docs/ideas.md, market agent, 2026-09-18) and it is, for this segment,
the highest-converting artifact we could possibly publish. Lane B's HN
post should lead with it if one exists by 2026-10-13.

### A3 — The context-budget victim

**The archetype, real and dated:** the Show HN "Skillzero" thread
([news.ycombinator.com/item?id=49698184](https://news.ycombinator.com/item?id=49698184),
2026-09-14) and its commenter asking whether scoping works "on repo
level."

**Why they pay:** a small, scoped, verified library beats a large
unverified one, and that is the shape alexandria has by construction —
two skills in gold today, each dense, each cited, none of it filler.
Our smallness is the feature for this person. Say so out loud.

**Caveat, honestly:** scoped delivery is a *proposed* feature
(docs/market/briefs/2026-09-18.md ledger item), not a shipped one. Copy
for this archetype sells the small-and-verified library that exists, not
the scoping UX that does not.

### A4 — The staff engineer who owes someone an answer

**The archetype:** the Pragmatic Engineer reader — 1M+ of them, paying
$15/month for judgment (docs/market/positioning.md). Their trigger is
being asked "what should we be doing about agents" by someone more
senior, on Thursday, for Monday.

**Why they pay:** a defensible answer with citations, in one place, that
they did not have to assemble. The digest is free; what they buy is the
ability to hand over a claim with its evidence trail attached.

**Note:** this person is also **the doorway to lane E.** They do not just
buy a seat; they are the one who expenses five. Every asset aimed at A4
should carry a plainly visible "there's a team version of this" line the
moment team pricing exists (§5).

### A5 — The applied researcher and the research-adjacent PM

Served by Elicit and Consensus for *search*, by nobody for a maintained
record of *what held up* (docs/market/opportunities-2026-09-18.md).
Smaller segment, lower urgency, real. Reachable through lane D, not
worth dedicated effort in month one — listed so we know we deliberately
deprioritised it rather than forgot it.

---

## 4. The eight lanes, in detail

### Lane A — the owner's own network (target: 8 paid, days 1-7)

The only lane where the conversion rate is 20%+ rather than 2%, and the
only one nobody can take away from us. It is also the lane most founders
skip out of embarrassment, which is why it is first.

**The motion:** before launch, the owner writes a list of ~40 people she
knows personally who build with agents — ex-colleagues, people from
previous teams, founders she's talked to, anyone who has ever asked her
what she's working on. Not a blast. Forty individual messages, ten a day
across days -4 to -1, each one sentence personalised.

**Critical distinction that the first run got wrong:** these people are
*not* the comped friends list. Comped friends get the product free and
are not customers. This list is people who would actually use it and can
expense $20. **Asking a friend to pay is not rude if the thing is worth
paying for**; comping everyone you know is how a business talks itself
out of ever having a customer.

**The asset:** `outreach-plan.md` §"Lane A — the personal forty",
drafted and ready.

**Realistic math:** 40 messages → ~25 replies → ~15 sign up free → 8
pay in the first week. If it is 3 instead of 8, the product is not ready
and every other lane is about to underperform too. **This lane is the
canary**, which is why it runs before the public launch and not after.

### Lane B — launch day in public (target: 15 paid, days 1-5)

Already drafted in full, venue by venue, by an earlier run:
`docs/sales/launch/hn.md`, `x.md`, `linkedin.md`, `reddit.md`,
`email.md`. This plan does not rewrite them. It adds three things:

1. **Fire order and timing.** Email first at 13:00 UTC (warmest list),
   HN at 14:00 UTC / 10:00 ET (the mid-morning ET window the HN draft
   already names), X thread immediately after the HN post goes live so
   the thread can quote-link it, LinkedIn at 16:00 UTC, Reddit last and
   staggered across two days — never three subreddits in one hour, which
   reads as spam to both moderators and readers.
2. **The HN comment plan, which no draft has yet.** The post is 30% of a
   Show HN; the founder's comments are the other 70%. Three responses
   should be drafted before launch morning and are in
   `outreach-plan.md` §"The HN comment kit": the "why would I buy a
   markdown file" objection (which we know is coming — it is the top
   comment on skillbay.sh's thread, dated 2026-09-17), the "this is just
   a newsletter with extra steps" objection, and the "your agents wrote
   this, so why should I trust it" objection, which is the one unique to
   us and the one most likely to decide the thread.
3. **A hard rule for the day:** nothing gets claimed that is not live.
   docs/sales/calendar.md's blocking-dependency list still governs. If
   the digest archive is not rendering on 2026-10-13, the posts link to
   the repo and the skill files, which are real, and say nothing about
   an archive.

### Lane C — direct outreach to people who publicly stated our problem (target: 5 paid, days 3-30)

The entire machine is `docs/sales/outreach-plan.md`. Summary here: ~15
messages a week, each to a person with a dated public artifact showing
they have the exact problem alexandria solves, each note referencing
that artifact specifically. No sequences, no templates sent at volume,
no tool. The owner sends them from her own account, by hand, because at
this volume that is both possible and better.

Five paid from ~60 notes is an 8% conversion, which is high for cold
outreach and reasonable for outreach this targeted — every recipient
has publicly complained about the problem in the last sixty days.

### Lane D — curators and communities (target: 3 paid, days 7-30)

Slow, lagging, and worth starting in week 1 anyway because the lead time
is weeks. Targets and drafts are in `outreach-plan.md` §"Lane D". The
existing `docs/sales/outreach/list.md` already has four verified
entries; this run extends the category list rather than replacing them.

The honest note the previous run got right and this one keeps: a pitch
to TLDR AI or The Batch is asking a rival to promote us. Skip them. Aim
at the adjacent-not-competing tier (Latent Space) and at the researcher
tier who would cite us rather than feature us.

### Lane E — team seats (target: 10 seats / 2 companies, days 10-30)

The B2B lane the owner said was missing. Full treatment in §5.

### Lane F — licensing, retainers, and the data feed (target: 5 seat-equivalents, days 14-30)

Also §5. For month one the realistic output is **a pipeline and one
signed pilot**, not revenue at scale. Said plainly so nobody grades it
as a failure for behaving like the long-cycle motion it is.

### Lane G — the agent-to-agent channel (target: 4 paid, days 5-30)

This is the lane no competitor is running, and the one most native to
what alexandria is. The mechanics are already specified in
docs/sales/geo-plan.md Game 2 — llms.txt, the skills manifest, the
public read-only claims endpoint, the public MCP surface, listings at
agentskills.io and a registry like Smithery. **All of it is engineering
work, none of it is sales' to build**, and it gates on the site being
deployed.

What sales contributes and has ready in this run:

- The listing copy for agentskills.io and for a registry entry, drafted
  in `outreach-plan.md` §"Lane G — listing copy".
- The sequencing ask: **the two gold skills should be listed in public
  registries in launch week, with their provenance blocks intact**,
  because a skill file that travels carries the pitch inside it
  (docs/sales/distribution-plan.md, mechanic 2). A skill in a registry
  is a salesperson that works while the owner sleeps and costs nothing.
- The one number to watch: installs-to-site-visits. If the skills get
  installed and nobody visits, the provenance block is not doing the
  work and the file needs a footer line pointing home.

### Lane H — the second orbit (target: 10 paid, days 7-30)

Everything that happens because lanes A-G happened: forwards, the
referral ask in `docs/sales/launch/referral.md`, and the four Monday
digests (days 7, 14, 21, 28 — 2026-10-19, 10-26, 11-02, 11-09) landing
on a free list that is now much larger than it was on 2026-10-12.

**The mechanic that makes lane H real** and does not exist yet: each of
those four digests must contain **one item whose paid version is
obviously better** — a claim whose full evidence trail is behind the
$20 spine, a skill whose file members can load. Not an upsell banner.
The item itself, with the paid continuation named in a single honest
line. This is docs/market/opportunities-2026-09-18.md idea 2 ("from
digest to running tool") read as a conversion mechanic, and it is the
single highest-leverage editorial decision of the launch month.

---

## 5. The B2B lane — selling to companies, seriously

The owner's critique named this as the biggest omission, and it was.
Everything below is a proposal; **every price is the owner's call, not
sales' (charter boundary), and is argued here from the comps already
sourced in docs/market/positioning.md** — which itself flags team and
institutional pricing as "unexplored... worth flagging as a later rung."
This section is sales making the argument that the later rung should be
reachable in month one, not built in month six.

The evidence that the rung exists at all, all of it already in our own
research: SemiAnalysis runs a $500/year retail newsletter alongside a
separately priced institutional "Core Research" product reported on
track for ~$100M/year; Lenny's runs a $350/year Insider tier over a
$200/year individual tier; Elicit runs $49/month individual against
$169/month Scale. In every observed case **the organisation pays a large
multiple of the individual price once the product is treated as
infrastructure rather than personal reading.** Alexandria's paid spine is
already infrastructure-shaped — it is skills, a claim graph, and
automations, not essays — so this is not a stretch, it is the natural
second SKU.

Four products, ordered by how soon they can honestly be sold.

### B2B-1 — Team seats (sellable at launch, lane E)

**What it is:** the same $20/month spine, bought in blocks of 5 or 10
for an engineering team, on one invoice, with one person administering.

**What it is not, and must not become:** an enterprise tier with SSO, a
security questionnaire, a procurement cycle, or a custom contract. The
whole point is that it closes in one conversation with one engineering
leader on one card.

**Who buys:** archetype A4 (the staff engineer or eng manager at a
20-200 person company with an AI team). The buying trigger is not
"newsletter for the team"; it is **"everyone here is independently
googling the same questions about agent architecture and getting
different answers."**

**The pitch in one sentence:** *five engineers each spending an hour a
week reading papers badly costs you more per month than the whole
team's subscription.*

**Pricing proposal for the owner's decision** (not a sales decision):
- Option 1, simplest: 5 seats for $80/month ($16/seat, a 20% team
  discount). Clean, obviously fair, no negotiation.
- Option 2, the one the comps support better: 5 seats for $100/month,
  no discount, plus one thing individuals do not get — a quarterly
  30-minute call with the owner on what the claim graph says about the
  team's current architecture question. The comps above all show
  organisations paying a *multiple*, not a discount, when the thing is
  infrastructure. **Sales' recommendation is Option 2**, because a
  discount trains the buyer to think of this as a bulk newsletter, and
  the call costs two hours a quarter and is worth more than $20 of
  anyone's money.
- Either way: annual invoicing available, because a company that pays
  annually is a company whose finance team has blessed the line item.

**What must exist by day 10 for this to close:** the ability to send an
invoice and take a payment for more than one seat. That is a Stripe
configuration question for the engineer seat, flagged here as a
dependency, not assumed. If it does not exist, lane E's fallback is
five individual $20 subscriptions on the manager's card and a manual
note — ugly, but it closes, and the ugliness is fixable later.

**Named first prospects:** the owner's network is the source here, not
cold outreach. In lane A's forty messages, **any recipient who works on
an AI team of three or more gets a different closing line** — the one in
`outreach-plan.md` §"Lane E — the team ask". Two closes out of forty
warm contacts is the target and is not ambitious.

### B2B-2 — The skill library, licensed into agent platforms and dev tools (lane F, pipeline in month one)

**What it is:** a platform that hosts or runs agents — an IDE, an agent
framework, a skills marketplace, an MCP registry — ships alexandria's
verified skills to its users, with provenance visible and attributed, on
a licence or revenue share.

**Why anyone would buy it, stated from their side, not ours:** every
observed skill distributor has a quality problem they cannot solve with
distribution, and it is now *quantified and public* — 69% of 216 audited
public Claude Code skills won't reliably trigger
([news.ycombinator.com/item?id=49744398](https://news.ycombinator.com/item?id=49744398)),
SkillsMP carries 800k+ scraped skills with curation absent by design,
skills.sh has millions of installs and no quality signal
(docs/market/report-2026-09.md §4). A marketplace whose catalogue is 69%
unreliable has a trust problem that no amount of listings fixes. **A
small, verified, evidence-carrying set is the thing that fixes it**, and
we are the only ones who have one, because ours is a byproduct of a
research pipeline rather than a content effort.

**Named categories, with real examples drawn from our own landscape:**
- *Skill marketplaces and directories:* skillbay.sh (hand-curated,
  founder publicly conceded AI-generated skills "are usually pretty
  bad" — this is a person who has already told the world he has the
  problem we solve), skills.sh, SkillsMP.
- *MCP registries:* Smithery (21.8k servers, docs/market/report-2026-09.md §4).
- *Agent frameworks and orchestration tools:* the free-and-giving-it-away
  tier named in docs/market/opportunities-2026-09-18.md — LangGraph,
  CrewAI, n8n, Dify. They give away the engine and need content that
  makes the engine work well. That is complementary, not competing; we
  explicitly do not build an engine.
- *AI-native dev tools:* the class named in docs/sales/geo-plan.md as
  already treating MCP as the front door — Cursor, Vercel, Firecrawl,
  Browserbase, Exa, Mem0.

**Honest constraint on all of the above:** with two skills in gold, the
month-one ask is **a pilot, not a licence.** The credible sentence is
"here are two skills with full evidence trails, list them free, show the
provenance, and let's see whether your users behave differently around
them" — and *that* is a conversation we can have on day 14 with
something real in hand. A licensing negotiation needs the twelve-skill
library O2 KR1 targets for Q4. Say the small thing and mean it.

**Pricing shape for later (owner's call, flagged not decided):** per-seat
rev-share on their subscription, or a flat annual content licence. No
number proposed here — there is no comp in our research for licensing a
verified skill library, because nobody has one to license. That absence
is the asset; it also means the first deal sets the market and should
not be priced in a hurry.

### B2B-3 — Evidence-briefing retainers for AI teams (lane F, first conversation in month one)

**What it is:** a monthly retainer under which alexandria answers a
specific team's standing architecture questions from the claim graph —
"is on-policy distillation worth it for our case," "which multi-agent
pattern has evidence behind it for this task class" — and delivers a
short, cited brief. Not consulting: **no bespoke research, no calls, no
scope creep.** The claim graph already knows the answer or it does not;
the retainer buys the query, the synthesis, and the citation, delivered
monthly.

**Why it is defensible and not a services trap:** the marginal cost is
the same pipeline that already runs. The brief is produced by the same
machinery that produces the digest, pointed at one team's question
instead of the frontier generally. The moment it requires the owner's
hours rather than the organism's, it is the wrong deal and should be
declined — the tiebreak is autonomy (docs/vision.md §0), and a retainer
that consumes the owner is a retainer that makes the company less
autonomous, whatever it pays.

**Who buys:** AI platform teams at mid-size companies; AI consultancies
and agencies who resell judgment and would rather buy the evidence layer
than build it; venture and buy-side technical diligence, which is
literally the demand SemiAnalysis's institutional product proves exists
at scale in the adjacent hardware market.

**The month-one goal is one conversation, not one close.** The cycle is
long, the value needs demonstrating, and the honest demo is a free
sample brief: pick one prospect's publicly stated architecture problem,
answer it from the claim graph with citations, send it unsolicited and
unpriced. That is the most persuasive sales asset this company could
possibly produce and it costs a pipeline run.

**Pricing shape (owner's call):** the comps for institutional research
run from Lenny's $350/year to SemiAnalysis's separately-priced Core
Research; a monthly retainer in the low hundreds is consistent with that
band. No number proposed. Flagged for docs/market/positioning.md to
argue properly with evidence.

### B2B-4 — The claim graph as a data feed for tool vendors (lane F, the long one)

**What it is:** programmatic access to the claim graph — claims,
evidence, `supports`/`contradicts` edges, confidence, dates — as a feed
that another vendor's product reads. An agent observability tool
annotating a pattern with "the evidence on this is mixed, last
contradicted 2026-08." A dev tool warning that a technique its user just
adopted is in the deprecated view. A research tool citing our verdicts.

**Why it is the most valuable thing here and the slowest:** it is the
only product on this list with a moat that compounds — a competitor with
identical models cannot replicate a year of curated, evidence-linked
claims overnight (docs/market/opportunities-2026-09-18.md says exactly
this). It is also the one that most needs the graph to be large, stable,
and trustworthy, which at 254 claims and 88 edges
(`site/lib/graph-data.js`, a hardcoded snapshot) it is not yet.

**Month one action, and it is deliberately small:** the public read-only
claims endpoint already proposed in docs/sales/geo-plan.md Game 2 item 3
ships, scoped to matured and deprecated claims only. That endpoint is
simultaneously a GEO asset, an agent-channel asset, and **the free tier
of a future data product** — the thing a vendor integrates before they
ever pay for it. Nothing is sold in month one. The surface that makes
selling possible gets built.

**The one warning worth writing down:** a data feed sold to tool vendors
is the one product here that could cannibalise the $20 spine, if a
vendor resells our verdicts to the same engineers who would otherwise
subscribe. Any deal in this lane should be non-exclusive, attributed,
and priced on the assumption that attribution drives traffic back. That
is a term to hold, not a detail.

### The B2B sequencing rule

Do not run all four at once. **Month one: B2B-1 closes, B2B-2 pilots,
B2B-3 gets one free sample brief out, B2B-4 gets its endpoint built.**
The failure mode for a small company is four enterprise conversations
and no product; the discipline is one sellable SKU (team seats) and
three pipelines that cost almost nothing to keep warm.

---

## 6. Day 0 — the week before (2026-10-06 to 2026-10-12)

The 30-day plan fails if this week does not happen. docs/sales/calendar.md
already holds the pre-launch teaser schedule; this is what is *additional*
and specific to getting paid customers rather than attention.

| Day | Who | What | Why it blocks |
|---|---|---|---|
| Tue 10-06 | Owner | Writes the personal forty (§lane A). Names in a file, not in her head. | Lane A is 8 of the 50 and cannot be improvised on launch morning |
| Tue 10-06 | Finance seat | Real monthly cost base on the table | Without it, "profitable at launch" (O1 KR2) is unmeasurable and 50 may be the wrong number |
| Wed 10-07 | Engineer | Stripe: can we take a 5-seat payment on one invoice? Yes or no, in writing | Lane E's 10 seats depend on the answer; the fallback is workable but must be known in advance |
| Wed 10-07 | Owner | Decides team pricing (§B2B-1, Option 1 or 2) | Cannot sell a team seat without a price |
| Thu 10-08 | Owner + sales | HN comment kit reviewed and in her voice | The comments decide the thread; drafting them live at 10am is how threads get lost |
| Thu 10-08 | Engineer/frontend | Honest-claims audit: every number on the site is live or removed (the hardcoded "papers ingested" counter, the graph snapshot) | This audience checks. One stale number costs more than the post earns |
| Fri 10-09 | Skill seat | Both gold skills' provenance blocks complete; `self-improving-post-training-loops` has an empty `validated:` field today | The A/B validation line is the single best sales asset we own. Two of them is twice the asset |
| Fri 10-09 | Sales (this run) | Sample evidence brief drafted for one named B2B-3 prospect | It is the demo; it needs to exist before the conversation |
| Sat-Sun 10-10/11 | Owner | Sends lane A's forty, ten a day, personalised | The canary. If this goes badly, move the launch |
| Mon 10-12 | — | Final pre-launch digest to the comped list; mention tomorrow only if the site is real | calendar.md dependency 1 |

**The one thing to say out loud:** if on 2026-10-09 the site cannot take
money, the launch moves. A Show HN that converts nobody because there is
no checkout is a card played for zero, and it is the only card of its
kind we get. Launching late costs a week; launching broken costs the
launch.

---

## 7. The thirty days

Digest sends are Mondays: day 7 (10-19), day 14 (10-26), day 21 (11-02),
day 28 (11-09). Those four are the spine of the month; everything else
hangs off them.

### Week 1 — the spike (days 1-7, 2026-10-13 to 10-19)

| Day | Date | Motion | Asset | Owner's time |
|---|---|---|---|---|
| 1 | Tue 10-13 | 13:00 UTC launch email to free list → 14:00 UTC Show HN → X thread quoting it → 16:00 UTC LinkedIn. Then **she stays in the HN thread all day.** | `launch/email.md`, `launch/hn.md`, `launch/x.md`, `launch/linkedin.md`, HN comment kit | Most of the day. This is the one day that is not an hour a week |
| 2 | Wed 10-14 | Reddit r/ClaudeAI (check the sub's current self-promo rule first). Reply to every launch-day email reply personally. Lane A follow-up to non-responders. | `launch/reddit.md` | 2h |
| 3 | Thu 10-15 | Reddit r/AI_Agents. **Lane C outreach batch 1: 5 notes** to named practitioners. First thank-you post with a real number — whatever it honestly is. | `outreach-plan.md` Lane C batch 1 | 1.5h |
| 4 | Fri 10-16 | Lane G: both gold skills submitted to agentskills.io and one registry, provenance intact (engineer submits, sales drafted the copy). Lane D: 3 curator notes. | `outreach-plan.md` Lane D + Lane G | 1h |
| 5 | Sat 10-17 | Nothing. Deliberately. | — | 0 |
| 6 | Sun 10-18 | Read the week: which page converted, which lane produced, log it in `results.md` with real numbers only. | `results.md` | 30m |
| 7 | **Mon 10-19** | **Digest #1 post-launch**, to a list that is now much bigger. Carries one item with an obvious paid continuation (§lane H) and the plain forwarding ask from `referral.md`. | digest + `referral.md` | — |

**Week 1 target: 25 of the 50.** Front-loaded on purpose. If day 7 shows
fewer than 12 paying customers, go to §8 immediately, not on day 20.

### Week 2 — the conversion week (days 8-14, 10-20 to 10-26)

The spike is over and this is where most launches quietly die, because
the founder is tired and the numbers stop moving. The week is designed
to be boring and mechanical.

| Day | Date | Motion |
|---|---|---|
| 8 | Tue 10-20 | "What shipped in week 1" post — receipts, what is true now that was not true on launch morning (already on calendar.md) |
| 9 | Wed 10-21 | **Lane E opens.** The team ask goes to every lane-A contact who works on a team of 3+. This is the B2B start and it is warm, not cold |
| 10 | Thu 10-22 | Lane C batch 2: 5 notes. Lane F: the free sample evidence brief (B2B-3) goes to its one named prospect |
| 11 | Fri 10-23 | Lane F: pilot note to 2-3 skill marketplaces / registries (B2B-2), offering listing with provenance, asking nothing |
| 12-13 | Sat-Sun | Off |
| 14 | **Mon 10-26** | **Digest #2.** Paid continuation item again. First real read on digest-driven conversion: did the free list added in week 1 convert at all? |

**Week 2 target: +10 (cumulative 35).**

### Week 3 — the B2B week (days 15-21, 10-27 to 11-02)

| Day | Date | Motion |
|---|---|---|
| 15 | Tue 10-27 | Second-orbit X post: a real usage anecdote if one exists, skipped if not (calendar.md already says this) |
| 16 | Wed 10-28 | Lane E: follow up the team asks. One conversation, one price, one invoice — no proposals, no decks |
| 17 | Thu 10-29 | Lane C batch 3: 5 notes. Lane D: 3 more curator notes, now with real issue links, which is the thing `outreach/list.md` said to wait for |
| 18 | Fri 10-30 | Lane F: follow up B2B-2 and B2B-3. Whatever came back, log it in `results.md` |
| 19-20 | Sat-Sun | Off |
| 21 | **Mon 11-02** | **Digest #3.** By now the format of the paid-continuation item is either working or it is not; the day-21 checkpoint (§9) decides whether to change it |

**Week 3 target: +10 (cumulative 45), and at least one team deal closed.**

### Week 4 — the close (days 22-30, 11-03 to 11-11)

| Day | Date | Motion |
|---|---|---|
| 22 | Tue 11-03 | The one honest nudge to free subscribers who joined in week 1 and have not upgraded: what is behind the spine, one email, no urgency, no discount. Sent once, ever |
| 23 | Wed 11-04 | Lane C batch 4: 5 notes |
| 24 | Thu 11-05 | Lane E: second team deal close attempt |
| 25 | Fri 11-06 | Lane G review: installs vs site visits. Fix the skill footer if the ratio is bad |
| 26-27 | Sat-Sun | Off |
| 28 | **Mon 11-09** | **Digest #4** |
| 29 | Tue 11-10 | Write the month: every lane's real number into `results.md` |
| 30 | Wed 11-11 | **The 30-day review** (§9). Sales' next run plans month two off this, not off this document |

**Week 4 target: +5 (cumulative 50).**

### The owner's time, totalled

One very long day (day 1), two moderate days (days 2-3), and then
**roughly 3-4 hours a week for weeks 2-4**, almost all of it sending
notes she has already read and approved. That is the design constraint,
not an accident — the idea list is explicitly filtered for motions she
can run in an hour a week (docs/sales/idea-list.md marks them).

---

## 8. The floor plan — what we do if the launch post flops

Lane B is 15 of 60 planned seats and it is a coin flip. Show HN either
catches the front page or it does not, and no amount of drafting
controls that. A plan that has no answer for this is the plan that got
this seat a rerun.

**Trigger:** by 18:00 UTC on day 1, the Show HN is below ~15 points and
off the front page.

**Do not:** repost it, ask anyone to upvote it, post it again under a
different title, or run the same post on a second account. Every one of
those is a trust-spending growth hack and the charter forbids them, and
HN detects all of them anyway.

**Do, in this order:**

1. **Treat day 1 as a private launch and run lane A twice as hard.**
   Forty becomes eighty: second-degree contacts, with the first forty
   asked for one introduction each. Warm beats broad and always did.
2. **Re-aim, do not repost.** The Show HN failing usually means the
   *framing* failed, not the product. The strongest alternative framing
   is already known and is not a launch post at all: publish the "left
   behind" artifact — one named technique, the contradicting evidence,
   the dates — as a standalone piece of work with no product ask
   attached. That is a post that stands on its own merit and it is the
   thing this company can produce that literally nobody else can
   (docs/ideas.md, market agent, 2026-09-18). Target it at day 8-10,
   not day 2.
3. **Shift the week-2 budget from broad to narrow.** Lane C batches go
   from 5 notes a week to 15. At 8% these are worth more per hour than
   a second attempt at a crowd.
4. **Bring lane E forward from day 9 to day 3.** Team deals do not need
   public attention at all; they need one warm conversation each. If the
   public channel is dead, the B2B lane is not — it never depended on it.
5. **Tell the truth in the week-1 digest.** "The launch post didn't
   land; here's what we're doing instead" is, for this audience,
   better content than a victory lap. The company's whole credibility
   position is that it publishes its decisions including the bad ones
   (docs/vision.md §0, docs/decisions.md). A visible recovery is on-brand
   in a way a flawless launch is not.

**Floor-plan target: 30 paying customers by day 30 instead of 50**, with
the 50 moved to day 60. That is the honest downside case. It is not a
failure of the business; it is a failure of one channel, which is what
having eight lanes is for.

---

## 9. Checkpoints, and what each one changes

Not a dashboard. Four moments where a specific decision gets made.

| When | The question | If the answer is no |
|---|---|---|
| **Day -4 (10-09)** | Can the site take money, and did lane A's first ten messages get warm replies? | **Move the launch.** A week's delay is cheap; a broken launch is not repeatable |
| **Day 3 (10-15)** | Did launch day produce ≥8 paying customers? | Go to §8. Do not wait for week 2 to "see how it settles" |
| **Day 10 (10-22)** | Are skill pages converting better than the homepage? | The provenance thesis is not landing in the copy. Rewrite the homepage around one skill's evidence trail before digest #2, and tell market the positioning needs a second look |
| **Day 21 (11-02)** | Has one team deal closed or is one clearly closing? | The team-seat SKU is either mispriced or the ask is buried. Try the other pricing option from §B2B-1 on the next two conversations rather than concluding B2B doesn't work from a sample of two |
| **Day 30 (11-11)** | 50? | Write what actually happened per lane into `results.md`, and let month two be planned off real numbers. **No number in that file is ever estimated** |

---

## 10. What sales cannot fix, restated because it decides everything

docs/sales/calendar.md's blocking-dependency list still stands and is
not sales' to clear. Updated to today's truth (2026-09-18):

1. **No email capture and no checkout on the site.** Both homepage CTAs
   dead-end. This is the single hard dependency for every paid number in
   this document. O1 KR1 commits it for 2026-10-13.
2. **The digest archive renders empty.** Affects lane B (nothing to link),
   lane D (curators need an issue, not a repo — `outreach/list.md` says
   this explicitly), and the entire GEO plan.
3. **Two skills in gold, not a library** — updated from calendar.md's
   "one," which was true when written and is not now
   (`harness-engineering`, `self-improving-post-training-loops`). Copy
   says "two, each with its evidence," never "a library" and never a
   projected count. O2 KR1's twelve is a Q4 arc, not a launch fact.
   Note for the skill seat: `self-improving-post-training-loops` has an
   empty `validated:` field; the A/B line is our best sales sentence and
   the second skill does not have one yet.
4. **The homepage's "papers ingested this week" counter is hardcoded**,
   and `site/lib/graph-data.js` is a static snapshot. Nothing in any
   draft points at either as a live metric.
5. **Multi-seat billing is unverified.** Lane E depends on it; day -6
   answers it.

---

## 11. Change log

- 2026-09-18: first version, fourth sales run, owner dispatch following
  docs/agents/incidents.md item 11. Adds what the critique named missing:
  the B2B lane (§5), the day-by-day first-30-days schedule (§7), named
  archetypes from dated public evidence (§3), and a floor plan for the
  launch post failing (§8). Companion files: docs/sales/idea-list.md,
  docs/sales/outreach-plan.md.
