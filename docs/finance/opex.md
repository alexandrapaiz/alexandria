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
| Domain: libraryofalexandria.dev | GoDaddy, 1-year registration | Receipt | $16.19/yr (**receipt**) | Bought 2026-09-18 by the owner personally on GoDaddy. Alexandria's first direct cost. Figure owner-reported the same day, relayed by the chair. |
| Vercel Pro | Pro | Committed at launch (2026-10-13) | ~$20/month (**forecast**) | Hobby tier is non-commercial; the Oct 13 commercial launch (ADR-26) requires Pro. Not yet incurred — booking now as a known near-term commitment, not a current-month cost. |
| Modal | Starter credits | Active | $0 measured this run | Running against starter credits; no overage evidence found via public/repo surfaces this run. |
| Neon | — | Active | $0 measured this run | No billing evidence found via public/repo surfaces this run; ask the owner if a paid tier has been selected. |
| Moonshot (Kimi) | Prepaid, funded 2026-09-20 | Active | ~$3.50/month (**forecast**), $27/month ceiling | ADR-32 books Moonshot as a direct alexandria cost. Three jobs now call it: the weekly press (~$0.13 an issue, ~$0.57/month), triage and interpret (see the 2026-09-26 section below). The ceiling is enforced in code, not in policy: `python3 pipeline/budget.py` fails the deploy if the per-run caps are raised past it. |
| Groq | Free tier | Active | $0 | Free tier per the charter's known-lines list. Still carries distill, and is the fallback list behind every Kimi job. |
| GitHub Actions | — | Active | $0 (confirmed) | `gh repo view` confirms the repo is public (`isPrivate: false`), 2026-09-24. Public repos get unlimited free Actions minutes and storage, so per the charter's own rule ("Actions minutes if the repo is private") this line is $0 as a fact of the repo's visibility, not a measurement gap. Resolved; drop from open questions. |
| Clerk | — | Not yet confirmed live | Not measured this run | No billing evidence found; env vars for Clerk are a separate open item on the pending tracker (owner-only, due 2026-09-19), unrelated to this ledger. |
| Merchant of Record fees (Polar, fallback Lemon Squeezy) | — | Not yet live | $0 | Renamed from "Stripe fees": ADR-30 (2026-09-19) replaced Stripe direct with a Merchant of Record, Polar first, because Stripe does not operate in Guatemala. MoR account setup is still an owner-only pending item, due 2026-09-26 (docs/sprints/pending.md item 2). No transactions exist. |

**Alexandria-book known/forecast monthly run rate once Vercel Pro is
live:** domain amortized ($16.19/12 ≈ **$1.35/month**) plus Vercel Pro
(**$20/month**) ≈ **~$21.35/month**. Everything else measured this run
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

- Whether Neon or Modal usage this month is inside free/starter
  allowances or has started metering overage. Two of the fleet's press
  incidents this week (23, 24 in docs/agents/incidents.md) touch these
  services — Kimi routing reverted off Groq-adjacent models back to
  Sonnet, and the weekly Modal press cron returned no output for
  2026-09-21 — but neither incident has a cost signature this seat can
  find: a failed or 404'd call doesn't meter, and both services stay on
  their free/starter tier either way. Engineer and ExO own the actual
  fix; this line is watching for a cost consequence, not duplicating
  that work.
- Clerk's plan and whether it has moved past its own free tier.

These stay as open questions rather than guesses.

## 2026-09-24 update (mid-month, synchronous dispatch)

Two changes from the 2026-09-18 first close, both resolved above: the
GitHub Actions line closed out at $0 (repo visibility confirmed), and
"Stripe fees" renamed to Merchant of Record fees per ADR-30/31
(2026-09-19), which this ledger had not yet caught up to. No other line
moved; no new cash was spent this run.

## 2026-09-26 — the corpus moves to Kimi (engineer seat, owner-directed)

Reported here because the owner's directive of 2026-09-25 asked for the
projected monthly cost in this file, and because this is the first time
alexandria has a recurring metered cost whose size the org chooses
rather than discovers.

**Why there is a cost at all.** The corpus was not being read. Counted
in Neon on 2026-09-25: 8,956 papers ingested and 4,973 never triaged,
746 claims and 487 never linked, interpret drawing 11 to 14 edges a day.
The cause was Groq's free tier, where 8,000 tokens a minute means a run
makes two calls and then takes a 429 for the rest of the day. Triage and
interpret therefore move to the Moonshot account ADR-32 already funded
(ADR-2026-09-26). Distill stays on Groq and stays free.

### The numbers, from measured token counts

Every figure below comes from `tiktoken` counts of the real prompts and
the real payloads, priced at kimi-k2.6's list rate of $0.95 per million
input tokens and $4.00 per million output. `python3 pipeline/budget.py`
prints the same arithmetic on every run, so this table cannot drift away
from the code without CI saying so.

| Job | Per call, expected | Per call, ceiling | Per-run cap | Monthly at the cap |
|---|---|---|---|---|
| Triage (10 papers a call) | $0.0066 | $0.00852 | $0.60 | $18.00 |
| Interpret (1 claim a call) | $0.0018 | $0.00364 | $0.30 | $9.00 |
| Re-triage, one-time (10 papers a call) | $0.0066 | $0.00852 | $0.10 | one run, ~$0.04 |
| **Total, the daily jobs** | | | **$0.90/run** | **$27.00** |

Triage's per-call figures rose on 2026-09-26, from $0.0062 expected and
$0.00814 at the ceiling. The reasoning rubric made `prompts/triage.md`
1,133 tokens instead of 728, so the $0.60 cap buys 70 calls in the worst
case instead of 73: 700 papers a run instead of 730. The monthly ceiling
does not move, because the cap did not move. This is what a prompt change
costs and it is cheap, but it is not free, and a rubric that grows every
month would eventually buy fewer papers than the queue receives.

The re-triage (`modal run pipeline/triage.py::retriage`) is a one-time job
with a cap of its own: 47 reasoning papers judged again under the new
rubric, five calls, about four cents. It has no schedule, so it adds
nothing to the monthly ceiling.

"Ceiling" charges the whole output reservation whether the model uses it
or not, which is how the provider's own per-request accounting works and
therefore the number a cap has to be set against.

### Two numbers, and the gap between them matters

- **$27.00/month is the ceiling**, if both caps are reached every day
  for thirty days. It is the number to book as the exposure, and it is
  enforced by `budget.MONTHLY_CAP_CEILING_USD`: raising a per-run cap
  past it fails the deploy command and sends the change to the owner
  with this file attached.
- **~$2.90/month is the expectation.** A cap is only reached while a
  backlog exists, and both backlogs are finite. Once they are drained,
  the steady-state work is whatever one day ingests: roughly 100 new
  papers (10 triage calls, $0.06) and 20 new claims (20 interpret calls,
  $0.04), which is $0.10 a day.

**One-time cost to clear the backlogs:** $3.10 to $4.05 for the 4,973
untriaged papers over 6 or 7 daily runs, and $0.88 to $1.77 for the 487
unlinked claims over 3 to 6 runs. Call it **$5 once**, at the ceiling
price, spread across the first week.

**The grading backfill costs $0.** All 693 ungraded claims are graded by
`pipeline/evidence.py`, which is pure rules over the paper id and the
evidence text. It calls no model, and its Modal function is deliberately
given no provider secret, so it cannot acquire a cost by a later edit.

### The whole Kimi line

| Caller | Frequency | Expected | Ceiling |
|---|---|---|---|
| Weekly press (ADR-32) | 4.3 issues/month | $0.57 | $0.57 |
| Triage | daily | ~$1.80 | $18.00 |
| Interpret | daily | ~$1.20 | $9.00 |
| Chair's rehearsals | ad hoc, pre-deploy | pennies | pennies |
| **Moonshot total** | | **~$3.60/month** | **~$27.60/month** |

Against the alexandria book's known run rate of ~$21.35/month once
Vercel Pro is live, this takes the forecast to **~$25/month** expected
and **~$49/month** at the enforced ceiling. Steady-state $0 is over as
of ADR-32; what this section adds is that the successor number is
bounded in code rather than in a policy sentence.

### What this section could not measure

The prepaid balance on the Moonshot account. The owner funded it on
2026-09-20 and this seat never sees a provider console or a key value,
so the balance and the burn against it are hers to read. The number
worth watching there is whether ~$3.60/month against the funded amount
gives more runway than the launch needs. If the account runs dry the
symptom is legible rather than silent: every Kimi call 401s or 402s, the
fallback walk drops to Groq's free tier, and the run says which model
answered.
