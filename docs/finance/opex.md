# OPEX ledger

The living cost ledger. First entries as of 2026-09-18, the first
activation of these books (ADR-24), triggered by alexandria's first
real expenditure.

## The two-book structure

Per the owner's parent-company structure: costs are booked at the
**alexandria book** when they are alexandria's own direct cost, and at
the **parent book** when they are shared infrastructure the owner
holds across ventures. Shared items get, at most, a **notional
allocation** to alexandria when alexandria's own use of them is real
and specific; otherwise the allocation is $0 and the line stays fully
at parent. Nothing here moves cash between the books; this is
reporting only.

## Alexandria book — direct costs

| Service | Tier | Status | Amount | Notes |
|---|---|---|---|---|
| Domain: libraryofalexandria.dev | GoDaddy, 1-year registration | Pending receipt | ~$19.99/yr (**estimate**) | Bought 2026-09-18 by the owner personally on GoDaddy. Alexandria's first direct cost. The owner has not yet reported the actual price; the placeholder is the typical GoDaddy first-year list price for a `.dev` domain, from public pricing research this run, not a receipt. Replace with the real figure once she reports it. |
| Vercel Pro | Pro | Committed at launch (2026-10-13) | ~$20/month (**forecast**) | Hobby tier is non-commercial; the Oct 13 commercial launch (ADR-26) requires Pro. Not yet incurred — booking now as a known near-term commitment, not a current-month cost. |
| Modal | Starter credits | Active | $0 measured this run | Running against starter credits; no overage evidence found via public/repo surfaces this run. |
| Neon | — | Active | $0 measured this run | No billing evidence found via public/repo surfaces this run; ask the owner if a paid tier has been selected. |
| Groq | Free tier | Active | $0 | Free tier per the charter's known-lines list. |
| GitHub Actions | — | Active | Not measured this run | Cost applies only if the repo is private; this run did not confirm repo visibility or pull Actions-minutes usage via `gh api`. Carries as a question for next run. |
| Clerk | — | Not yet confirmed live | Not measured this run | No billing evidence found; env vars for Clerk are a separate open item on the pending tracker (owner-only, due 2026-09-19), unrelated to this ledger. |
| Stripe fees | — | Not yet live | $0 | Stripe account setup is still an owner-only pending item (docs/sprints/pending.md). No transactions exist. |

**Alexandria-book known/forecast monthly run rate once Vercel Pro is
live:** domain amortized (~$19.99/12 ≈ **$1.67/month**) plus Vercel Pro
(**$20/month**) ≈ **~$21.67/month**. Everything else measured this run
is $0 or unmeasured against free tiers.

## Parent book — shared infrastructure (notional allocation to alexandria)

| Service | Tier | Status | Amount | Allocation to alexandria | Notes |
|---|---|---|---|---|---|
| Apple Developer Program | Annual | Planned, owner's purchase | $99/yr | **$0** | Per the owner's structure, this is shared infrastructure booked at the parent unless she names an alexandria iOS product as planned. No such product is named as of this run. |
| Claude subscription | — | Active | **Unknown — named placeholder** | Not allocated (figure missing) | The org's compute, per the charter's known-lines list. The monthly figure is the owner's still-pending item, first raised at the 2026-09-18 closing all-hands and standing on docs/sprints/pending.md (item 11) as of this run. Booked at parent level with no allocation until she supplies it; do not guess this number. |

## Under evaluation — not booked

- **Linear** — under evaluation per the owner's 2026-09-18 note. The
  chair recommends against purchasing now: the GitHub Projects board
  (project #4) was just rebuilt to real Scrum structure
  (docs/sprints/pending.md, "Board reorg" section), so a second
  project-management tool has no clear job yet. Linear has a free tier
  available if the owner wants to trial it without a booked cost.
  **Booked amount: $0.** This line stays open until she decides.

## What this run could not measure

- GitHub Actions minutes/storage cost (needs `gh api` usage pull against
  confirmed repo visibility).
- Whether Neon or Modal usage this month is inside free/starter
  allowances or has started metering overage.
- Clerk's plan and whether it has moved past its own free tier.

These stay as open questions rather than guesses; next run should
attempt the `gh api` pull for Actions usage now that the pattern is
established.
