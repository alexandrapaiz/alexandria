# Capital

First entries as of 2026-09-18, first activation. Same two-book
structure as docs/finance/opex.md: alexandria's own invested capital,
and the parent's shared infrastructure with notional allocations only
where alexandria's own use is real and specific.

## Invested-capital base

What has actually been put into alexandria, in cash, to date.

| Item | Amount | Status |
|---|---|---|
| Domain: libraryofalexandria.dev | $16.19 (receipt, owner-reported 2026-09-18) | Cash the owner put in on alexandria's behalf, 2026-09-18. First entry in this base. |
| Owner's time | **Not priced** | The charter allows this line as its own item once she confirms a rate, or leaves it explicitly unpriced. Neither has happened yet; carried as a named open line, not a guess. |

**Alexandria invested-capital base as of 2026-09-18: $16.19
(estimate), plus unpriced owner time.**

Nothing from the parent book (Apple Developer Program, the Claude
subscription) counts toward alexandria's invested-capital base while
their allocation to alexandria is $0.

## CapEx vs. OPEX

The charter's OPEX enumeration (prompts/finance-agent.md §1) names
domains explicitly as an OPEX line, not CapEx, so the domain
registration sits in docs/finance/opex.md as a recurring annual cost,
not here as a one-time capitalized asset.

**Alexandria-book CapEx this month: $0 in cash terms.** The real
durable assets alexandria has built to date, the pipeline, the corpus,
and the growing skill library, were built with agent labor, not
purchased cash spend, so they carry no cash CapEx figure even though
they are economically the company's actual capital. This is worth
saying plainly rather than smoothing over: the invested-capital base
above ($16.19) badly understates what has been built, because the
main asset is unpriced work, not cash. Pricing that gap is exactly
what the "owner's time" line above is for, once she sets a rate.

## ROIC and EVA

Not yet a headline metric: **ROIC requires NOPAT, and alexandria has
$0 revenue and therefore $0 NOPAT.** Once revenue exists
(docs/finance/revenue.md), ROIC = NOPAT / invested capital, arithmetic
shown in full each month, and EVA = NOPAT − (invested capital × cost
of capital) will run alongside it as the operating lens: a quarter
only counts as value-creating once returns clear the capital's cost.

**What is missing to make this measurable:** a stated cost-of-capital
rate. The owner has not yet given one; until she does, EVA cannot be
computed even once revenue exists, only NOPAT and ROIC in isolation.
Flagging this now so it is not a surprise at the first month with real
revenue.

## Funding scenarios (analysis only — the owner's call, never ours)

At the current, near-zero cost base (~$21.35/month alexandria-book run
rate once Vercel Pro goes live at launch, per docs/finance/opex.md;
parent-book items not allocated), there is no case for outside capital
yet:

- **What it would buy:** at this cost base, even a small raise
  (say $25-50k) would fund years of infrastructure with room to spare.
  The constraint on alexandria today is not cash, it is time and
  judgment, neither of which a typical seed check accelerates linearly
  for a single-owner, agent-run company.
- **What it would cost:** dilution logic only makes sense against a
  cash need that dilution actually solves. With opex this low, any
  raise now would trade equity for money that is not the binding
  constraint, at a valuation with almost no revenue evidence behind
  it.
- **The honest case for staying self-funded:** the founding
  $0-cost-base principle (prompts/finance-agent.md's premise) is itself
  the thing worth protecting. Self-funding at ~$20-40/month keeps every
  future decision, including whether to ever raise, entirely the
  owner's, made from a position of not needing the money. Revisit this
  analysis once monthly figures include a real Claude-subscription cost
  and, ideally, first-subscriber revenue, since both change the shape
  of the cost base this reasoning rests on.

No action follows from this section. Raising, taking, or negotiating
money stays the owner's alone, per the charter.
