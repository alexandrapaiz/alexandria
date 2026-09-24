# Revenue

First entries as of 2026-09-18, first activation. No revenue exists
yet: alexandria has zero subscribers and the Merchant of Record (MoR)
is not live.

## Current state

| Metric | Value |
|---|---|
| Subscribers | 0 |
| MRR | $0 |
| ARR | $0 |

Pricing is set (vision.md §0, amended 2026-09-17; shape refined by
ADR-31, 2026-09-19): the digest is free as the acquisition engine, and
the paid spine ("Full access") sells through a Merchant of Record
(ADR-30: Polar first, Lemon Squeezy fallback, since Stripe does not
operate in Guatemala) three ways:

1. A 3-day free trial on the monthly plan, converting automatically.
2. **$20/month**, recurring or a non-recurring month that lapses.
3. **$200 lifetime access**, one payment, permanent entitlement.

## Launch-month forecast and breakeven

Using the alexandria-book known/forecast monthly run rate from
docs/finance/opex.md (~$21.35/month: $20 Vercel Pro once live at
launch, plus the domain amortized at ~$1.67/month):

- **Breakeven on known alexandria-book costs alone, monthly plan only:
  2 paying subscribers.** ($21.35 / $20 ≈ 1.07, rounded up.) This
  excludes any MoR per-transaction fee (not yet applicable, the MoR
  isn't live) and excludes any allocation of the parent-book Claude
  subscription, whose monthly figure the owner has not yet supplied.
- **This is a narrow, honest number, not a target.** It answers "how
  many subscribers cover what we can currently measure," not "how many
  subscribers make the business real." The moment the Claude
  subscription gets a real monthly figure and any allocation to
  alexandria, or MoR fees start applying, this breakeven count will
  move, most likely up.

### The lifetime tier's breakeven is a separate line, not blended in

ADR-31 named this directly for this seat: the chair's flag is that a
$200 lifetime sale is ten months of the $20 monthly price paid up
front, so it is a **launch-liquidity instrument, not a steady-state
price**, and the OKR seat's benchmark watches whether it cannibalizes
monthly signups. Blending it into one subscriber count would hide
that trade-off, so the two are kept apart:

- **On cash alone, a single lifetime sale ($200) covers roughly 9.4
  months of the current ~$21.35/month run rate** — effectively the
  entire pre-launch cost base paid off in one purchase, ahead of any
  monthly subscriber ever converting.
- **On steady state, a lifetime sale is a liability, not revenue,**
  past month 10: the buyer keeps the product with no further payment,
  so every month after roughly month 10 that a lifetime buyer would
  otherwise have paid $20/month is $20 of monthly revenue the business
  will never collect from that seat.
- **The number to watch, once sales exist, is the lifetime-to-monthly
  mix.** A launch skewed toward lifetime sales buys immediate runway
  (good, given the near-zero cost base already covers itself fast) but
  trades away recurring revenue the business needs for anything past
  the first year. This seat cannot compute that mix yet — it needs the
  first month of real sales data — but is naming the metric now so the
  first revenue-bearing close can report it on day one rather than
  discovering the question after the fact.

## What this run cannot measure

- Actual subscriber count and MRR: no read-only channel or subscribers
  table figure was available to this run, and none is expected yet,
  since the MoR account setup is still an owner-only pending item, due
  2026-09-26 (docs/sprints/pending.md item 2). Next run should pull
  from whatever channel the owner has set up by then.
- The lifetime/monthly sales mix named above: needs the first month of
  real sales data.
- Unit economics beyond the above breakeven: CAC, LTV, and churn have
  no data at zero subscribers and are not estimated here.
