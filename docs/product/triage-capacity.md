# Triage capacity: what the queue actually does

Written 2026-09-19 by the engineer seat, alongside the fix to the tier
priority inversion in `pipeline/triage.py`. The question this answers is the
one the dispatch asked: at the drain rate we can actually achieve, how long
until the 2,445-paper backlog clears, and is a one-time catch-up run worth
running.

The short answer is that the backlog does not clear by being read. It clears
by expiring, and it is already expiring.

## The numbers, and where each one comes from

| Quantity | Value | Source |
|---|---|---|
| Untriaged papers | 2,445 | Research brief, PR #42, measured against Neon on 2026-09-19 |
| Triage rows for the firehose, all time | 0 | Same |
| Arrivals | ~300/day | Same |
| Observed drain | ~20/day | Same, and consistent with two Groq calls at `BATCH = 10` |
| Capacity the code asks for | 250/run | `triage()` defaults to `max_calls = 25`, and the cron passes no argument |

The gap between 250 asked for and 20 delivered is not a scheduling problem.
It is the Groq free tier. The run stops on a 429 and resumes tomorrow, which
is the intended behaviour, so the daily budget is the real throughput number.

That budget is shared. `distill` (11:30), `triage` (12:00), `interpret`
(14:00) and the Monday `weekly` run all use the same `groq` secret, and three
of them use the same model. `distill` is scheduled ahead of `triage` on
purpose: the comment at `pipeline/distill.py:158` says "after ingest, BEFORE
triage (budget priority)". So triage does not get a small budget by accident.
It gets whatever distill leaves, by design.

## The backlog never clears by reading

Arrivals are ~300/day against a ~20/day drain. The queue grows by ~280 papers
every day. There is no drain rate reachable from here that catches up, and the
tier fix does not change this: it changes **which** 20 papers get read, not how
many. That distinction is the entire point of the fix and is worth stating
plainly, because it would be easy to read the fix as a throughput change.

Reading a fair sample of every tier is a different product from reading one
feed exhaustively, even at identical throughput. Today the digest reads
hf-daily and calls it the field. After this fix it reads all of them thinly.
Thin and honest beats complete and blinkered, and that is the ADR-26 argument
for shipping this before any feature.

## The backlog does clear, by expiry, and that is the real deadline

Every run auto-indexes anything older than `BACKFILL_DAYS = 60` without an LLM
call, marked `model = 'rule:backfill'`. That rule was written for the initial
historical import, where it is correct: old blog archives should not spend
model budget.

Against a live firehose it does something else. `distill_queue` in
`db/schema.sql` requires `decision in ('distill','deep_read') and model !=
'rule:backfill'`. So a backfilled paper can never be distilled, and a paper
that is never distilled can never produce a claim. Put together:

**Every paper has 60 days from its publication date to be judged. After that it
is permanently marked "indexed by rule", permanently excluded from claim
production, and it never appears in the queue again to remind anyone.**

The 2,445 papers in the backlog are all inside that 60-day window already,
because anything older was backfilled on a previous run. So the backlog is not
static. It is draining at roughly the rate it arrived, into a decision nobody
made. If the firehose has been accumulating for about twelve days, the oldest
of it starts expiring in early November 2026 and essentially all of today's
backlog is written off by around 2026-11-18, unread.

This estimate is the one number here I could not measure directly: this runner
has no Neon or Modal credentials, so the published_at distribution is inferred
from the brief's counts rather than queried. The fix makes it checkable. The
new per-tier queue log prints `oldest` every run, so the first run after deploy
states the true expiry date in its own logs.

## Is a one-time catch-up run warranted?

No, and it is worth being precise about why, because the instinct is a good one.

The command would be `modal run pipeline/triage.py --max-calls 250`. In dollars
it costs nothing: Groq is free tier and Modal's compute for a single
short-lived container is inside the free allowance. Steady-state cost stays $0.

It would not work. A manual run hits the same daily token budget as the cron
does, so it stops at roughly the same place. A catch-up run cannot exceed the
budget; it can only take a larger share of it, at distill's and interpret's
expense on the same day, which costs the digest a day of claim production. The
constraint is the budget, not the schedule, and no amount of manual invocation
moves a constraint that is measured per day.

## What would actually raise throughput

Three free levers exist. Which one applies depends on what Groq's 429 is
actually complaining about, and that is one observation away:

    modal app logs alexandria-triage

The 429 response body names the limit it hit. Nobody has read it. With that
answer:

- **If the limit is requests per day or per minute**, raise `BATCH` from 10.
  The same papers in fewer, larger calls is a direct multiplier and costs
  nothing in quality.
- **If the limit is tokens per day**, `BATCH` does not help at all, and the
  lever is the 1,500-character abstract slice in the prompt. A routing decision
  between discard, index, distill and deep_read does not need 1,500 characters;
  the title plus a few hundred would roughly double throughput. That is a real
  quality trade and should be measured against `triage_log`, not assumed.
- **Either way**, the distill-before-triage ordering is now a decision with a
  known cost rather than an unexamined default. It was set when triage had
  nothing to read. It now has 2,445 things to read and a 60-day clock.

None of these are this PR. They need the log line first, and guessing between
them would be exactly the kind of unmeasured change this document exists to
argue against.
