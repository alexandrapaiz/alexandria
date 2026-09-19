# Revenue

First entries as of 2026-09-18, first activation. No revenue exists
yet: alexandria has zero subscribers and Stripe is not live.

## Current state

| Metric | Value |
|---|---|
| Subscribers | 0 |
| MRR | $0 |
| ARR | $0 |

Pricing is set (vision.md §0, amended 2026-09-17): the digest is free
as the acquisition engine, and the paid spine is **$20/month**, live
at commercial launch, 2026-10-13 (ADR-26).

## Launch-month forecast and breakeven

Using the alexandria-book known/forecast monthly run rate from
docs/finance/opex.md (~$21.67/month: $20 Vercel Pro once live at
launch, plus the domain amortized at ~$1.67/month), and the $20/month
subscription price:

- **Breakeven on known alexandria-book costs alone: 2 paying
  subscribers.** ($21.67 / $20 ≈ 1.08, rounded up.) This excludes
  Stripe's per-transaction fee (not yet applicable, Stripe isn't live)
  and excludes any allocation of the parent-book Claude subscription,
  whose monthly figure the owner has not yet supplied.
- **This is a narrow, honest number, not a target.** It answers "how
  many subscribers cover what we can currently measure," not "how many
  subscribers make the business real." The moment the Claude
  subscription gets a real monthly figure and any allocation to
  alexandria, or Stripe fees start applying, this breakeven count will
  move, most likely up.

## What this run cannot measure

- Actual subscriber count and MRR: no read-only channel or subscribers
  table figure was available to this run, and none is expected yet,
  since the Stripe account setup is still an owner-only pending item
  (docs/sprints/pending.md) as of this run. Next run should pull from
  whatever channel the owner has set up by then.
- Unit economics beyond the above breakeven: CAC, LTV, and churn have
  no data at zero subscribers and are not estimated here.
