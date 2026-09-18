# The distribution plan — the Thiel doctrine, applied

Maintained by the sales agent (prompts/sales-agent.md, ADR-24). Written
2026-09-18 on owner dispatch, building on the project-board directive
recorded verbatim below and on docs/sales/calendar.md and docs/market/.
Same law as every sales artifact: **the agent prepares, the owner sends;
sales writes no ad copy for a channel it hasn't been told is live, and
proposes no build item it doesn't also flag to the owning engineering
seat.**

## The doctrine, as given

The board card that triggered this document, quoted in full because it's
short and it's the brief:

> Owner directive 2026-09-18: Peter Thiel's claim that distribution is all
> that really matters. The sales seat defines what a distribution system
> means for this product (*Zero to One*: superior distribution beats
> superior product; the power law of channels; distribution designed into
> the product; CAC vs CLV per channel at a $20/mo price point) and
> proposes the system: which single channel to master first, and
> distribution-built-into-product mechanics competitors cannot copy (free
> digest as the machine, skills spreading agent-to-agent, public ADRs as
> proof of work, agent-readable surfaces, in-product referral).

Four claims to work through: the power law of channels (one channel
dominates; pick it, don't spray), CAC vs CLV at $20/mo, which channel to
master first, and the mechanics built into the product itself rather than
bolted on as marketing.

## The power law of channels, applied honestly

*Zero to One*'s argument is that distribution channels follow a power
law — one channel will work far better than all others combined for a
given product, and the discipline is finding and dominating that one
channel rather than diversifying early. Alexandria has, today, exactly
one channel that is fully owned, compounds on its own use, and is already
the product's stated acquisition mechanism rather than a marketing
add-on: **the free weekly digest.**

The case for the digest as the channel to master first, not by default
but by elimination:

- **It's the only channel not rented from a platform.** X, LinkedIn,
  Hacker News, and Reddit (all drafted for launch day in
  docs/sales/launch/) are one-shot posts subject to someone else's feed
  algorithm, someone else's audience, someone else's rules that "change
  without notice" (docs/sales/calendar.md already notes this risk for the
  Reddit subs specifically). The digest is a list alexandria owns outright
  in its own Neon table (docs/vision.md:116-118) sent by its own cron.
  Nothing about it depends on a platform's continued goodwill.
- **It's already the architecturally decided acquisition engine, not a
  campaign choice.** The all-hands pricing decision states it directly:
  "the digest is FREE, full issues, the acquisition engine and the
  human-in-the-loop interface" (docs/allhands/2026-09-17.md, decision 1).
  Sales isn't picking this channel; sales is naming out loud what the
  architecture already committed to and building the machinery around it.
  Under Thiel's framing this is the correct instinct even when arrived at
  for other reasons — the product itself already concentrates on one
  channel instead of assuming ads or paid growth.
- **It's the channel with a comparable proven at the price ceiling we're
  aiming past.** The Pragmatic Engineer, Stratechery, and Interconnects
  all cluster at $15/month built entirely on an owned list with no paid
  acquisition (docs/market/positioning.md). Substack passed 8.4M paid
  subscriptions and beehiiv's paid revenue grew 138% in a year
  (docs/market/report-2026-09.md §5) — the single-owned-list-to-paid-tier
  motion is proven at scale by others; alexandria doesn't need to invent
  a new growth model, only execute this one well.
- **It converts into the paid tier structurally, not persuasively.** The
  $20/month spine (skills, claim graph, automations) is read by the same
  people who already read the digest, at the moment a digest item makes
  them want the tool version of what they just read (this is exactly the
  "digest findings ending in their runnable skill" mechanic below) — the
  channel and the funnel are the same object.

**What this rules out, on purpose:** no paid acquisition channel is
proposed anywhere in this plan. There is no ad budget decided, and the
architecture's whole economic argument is a ~$0 cost base
(docs/vision.md:112-114); buying distribution would be the one move that
breaks the thing that makes this business viable at small scale. If the
owner wants to explore paid acquisition later, that's a pricing/budget
call reserved to her, not a sales-agent proposal.

**What this doesn't mean:** master, not exclusive. The launch-day
multi-channel post (HN, X, LinkedIn, relevant subreddits — already
drafted in docs/sales/launch/) still happens once, for the one-time
proof-of-work spike a launch deserves. The power-law discipline is about
where sustained, compounding effort goes *after* launch day, not about
skipping every other channel entirely on day one.

## CAC vs CLV, at $20/month — stated honestly

Alexandria has no paid channel, so there is no dollar CAC to report, and
inventing one would be exactly the kind of unsourced number the charter
forbids. The honest framing:

- **CAC here is attention-cost, not spend.** The real cost of the digest
  channel is the owner's and the org's time producing a digest good
  enough to forward, plus the ~$0 infrastructure margin already designed
  in. There is no media buy to amortize.
- **CLV, from real evidence, not invention.** docs/market/positioning.md's
  price ladder places $20/month correctly at the boundary between the
  "premium newsletter" cluster ($15/mo) and the "real tool" cluster
  ($20-49/mo) — evidence it is priced right, not evidence of a specific
  retention curve, which nobody has measured yet since the product hasn't
  launched. Using docs/market/report-2026-09.md's SOM math as the
  honest range instead of a single invented number: at a 2-5% paid
  conversion off a free list and a $20/month blended tier, three-year
  obtainable revenue lands at $14k-144k ARR depending on free-list size
  (5,000-20,000 readers) — the same range that report already derived,
  reused here rather than re-invented.
- **The structural point Thiel's framing is actually making:** because
  CAC on the owned channel is near-zero, alexandria's CLV bar to clear is
  much lower than a funded competitor's. docs/vision.md's own thesis is
  the same point from the cost side: "the pipeline's marginal cost is
  ~$0, so subscription revenue is nearly pure margin" (docs/vision.md:113-114).
  A single-digit-percent conversion on a five-figure free list already
  clears profitability at launch, which is the decided bar
  (docs/allhands/2026-09-17.md, decision 3).

## Distribution designed into the product

The doctrine's sharper claim, and the owner's own phrase on the board
card, is mechanics competitors cannot copy because they're built into the
product's shape, not layered on as campaigns. Four exist or are proposed
today; none require a marketing budget, only engineering that's mostly
already planned elsewhere.

1. **The free digest as the distribution machine itself.** Every issue is
   already an asset designed to be forwarded, not just read — the sales
   charter's own mandate includes "referral and share-this-issue
   mechanics" (prompts/sales-agent.md:25-26), drafted in
   docs/sales/launch/referral.md. A subscriber who forwards one good
   "left behind" verdict (docs/ideas.md's proposed public flagship,
   market agent, 2026-09-18) is doing the acquisition work a channel
   normally has to be paid to do.

2. **Provenance headers as a distribution unit competitors cannot copy.**
   Every skill's frontmatter — today, `skills/harness-engineering/SKILL.md`'s
   `provenance` block naming claim IDs, source papers, and a dated A/B
   result — travels with the skill file wherever it gets loaded, forked,
   or shared agent-to-agent. Market's own report is blunt about the gap
   this exploits: "800k+ scraped skills and zero evidence trails" exist on
   every observed marketplace (docs/market/opportunities-2026-09-18.md).
   A competitor can copy a skill's *instructions*; they cannot copy its
   evidence trail without doing alexandria's research work first. Every
   download is, structurally, a piece of the pitch traveling with the
   file — see docs/sales/geo-plan.md's Game 1 for the same mechanic read
   as a citation strategy rather than a distribution one; it's the same
   asset serving both purposes at once.

3. **Digest findings ending in their runnable skill.** Already proposed
   as a feature, not yet built: "when a digest issue reports a technique,
   the paid tier ships a versioned, deployable implementation of that
   exact technique, linked back to its claim-graph entry"
   (docs/market/opportunities-2026-09-18.md, idea 2). Read as
   distribution rather than product: this turns the free channel's
   *content itself* into the paid tier's on-ramp, without a CTA banner or
   an upsell email — reading the free thing and wanting the tool version
   are the same motion, because the tool is that exact thing, not a
   generic adjacent product.

4. **The citable endpoint.** docs/sales/geo-plan.md (Game 2, items 3-4)
   proposes a public, read-only claims endpoint and a public MCP surface
   distinct from the owner's private agentic layer. Read as distribution:
   an agent that queries alexandria's claim graph on someone else's behalf
   is alexandria being pulled into a workflow it never marketed into, at
   the ~$0 marginal cost the whole business is built on. This is the
   Agent-as-delivery-surface segment docs/market/report-2026-09.md already
   names ("the human pays, the agent consumes... no observed competitor
   treats this as a paid channel yet," §3) — currently unbuilt, logged as
   a ledger item in the GEO plan, not claimed as live here.

5. **Public ADRs as proof-of-work distribution.** docs/sales/launch/pre-launch-teasers.md
   already drafts this exact move: "introduce the premise: a company
   whose decisions are public. Links to docs/decisions.md, no ask."
   Twenty-four dated ADRs are free content marketing that required zero
   incremental production, because the org would have written them
   anyway to run itself (docs/vision.md's "school continues as a
   byproduct" framing, docs/vision.md:40-41, applies to distribution as
   much as to the ADR habit itself).

## Sequencing against the runway

Nothing here changes a single date on docs/sales/calendar.md. The channel
discipline above applies from launch day forward, once the calendar's own
flagged blocker — no public digest archive, no email capture on the site
today (docs/sales/calendar.md, "blocking dependencies") — is cleared by
engineer/frontend. Pre-launch, the calendar's proof-of-work posts (public
repo, one skill's receipts, countdown) already are the "master one channel
carefully" discipline in miniature: real content, no ask, on the one
surface (the public repo) that's actually live today.

## What this plan explicitly does not propose

- No paid acquisition channel or budget — reserved to the owner
  (pricing/budget authority), not a sales-agent call.
- No growth hack that spends trust: no fake urgency, no inflated reach
  claims, no dark-pattern retention — the same billing-honesty line
  vision.md draws for Stripe (docs/vision.md:106-110) extends to every
  distribution mechanic here.
- No claim that any "distribution designed into the product" mechanic
  above is live today beyond what's cited; items 3 and 4 are proposed
  builds, flagged as such, cross-referenced to the ledger items
  docs/sales/geo-plan.md logs.

## Change log

- 2026-09-18: first version, this run, owner dispatch. Answers the board
  card "Define alexandria's distribution system (Thiel)."
