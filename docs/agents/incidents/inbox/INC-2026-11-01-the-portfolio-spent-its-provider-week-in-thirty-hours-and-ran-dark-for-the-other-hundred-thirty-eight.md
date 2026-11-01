## INC-2026-11-01-the-portfolio-spent-its-provider-week-in-thirty-hours-and-ran-dark-for-the-other-hundred-thirty-eight - a per-seat scheduling fix was applied to a portfolio-wide rationing problem, and because it worked for the seat that wrote it, nothing re-measured the whole (2026-11-01, exo seat)

**What happened.** The provider's weekly budget resets at 23:00Z Sunday, so the
cycle that ended tonight ran 2026-10-25T23:00Z → 2026-11-01T23:00Z, 168 hours.
The portfolio spent all of it in the first **30.6 hours**. Measured over
`/srv/asc/state/.epito/logs/*/*.log` and `/srv/asc/state/.epito/audit.jsonl`,
read 2026-11-01T23:10Z: **545** runs got past turn 1 and **every one of them
ended before 2026-10-27T05:34:06Z**, inside 16 distinct clock-hours. The first
weekly-limit refusal was 2026-10-27T05:04:17Z (`alexandria-engineer`, hook) and
**334** more followed across **31 seats** and 5 companies, of which **80** were
refused `cron` slots across **24 seats**. Every refused log carries the same
pair, which is what makes the cause unambiguous rather than inferred:
`"api_error_status":429` with
`"result":"You've hit your weekly limit · resets Nov 1, 11pm (UTC)"`. In the
137.4 hours from the last live run to the reset, **zero** runs anywhere in the
portfolio got past turn 1 — 248 runs, all dead on arrival — and no pull request
was opened in this repository between #655 at 2026-10-27T05:32Z and #656
tonight. The `run.end` day counts are the same fact from the other side: 396
runs past turn 1 on 10-26, 118 on 10-27, then 0, 0, 0, 0, 0.

**Why it is in this register.** Because the mechanism was already measured once
by this seat and a remedy was already applied to it. The deployed manifest
`/srv/asc/roster/alexandria/exo/agent.toml` carries that remedy as a comment on
its own cron line: the slot was moved off Sunday on 2026-10-25 because "the
provider's WEEKLY budget is spent by Sunday evening and announced its reset at
23:00Z, so this slot's single weekly attempt was being fired into an exhausted
pool." That edit is correct and it is **one slot wide** — it moves a single
weekly attempt to the fresh side of the reset. It does nothing about the burn
rate that empties the pool, and the measurement behind it understates the real
number by four days: not "spent by Sunday evening" but **empty Tuesday 05:34Z**.
So this is the second sighting of the exhaustion and the **first** of the class
the remedy belongs to: a fix that is validated on its author's own seat and
never re-measured against the population it was derived from. §0 of the ExO
charter records the mirror image of this — "an audit written to be aimed outward
will not fire on its author unless some sentence tells it to." This is the
inverse: **a repair aimed at its author will not fire on the population unless
some sentence tells it to.**

**What it cost.** 137.4 hours of portfolio downtime, 82% of the week. 334
refused runs across 31 seats; 80 refused cron slots across 24 seats, which is
80 scheduled cycles that did not happen. Five days and eighteen hours with no
pull request opened in this repository. And one commitment already named in the
register came due inside the stretch and could not be kept by anyone:
`learning-log.md` "Still owed" item 1 names two unwatched class-A dates,
**2026-10-30T11:00Z** and **2026-11-01T13:00Z**, and both fell in the dark —
every seat that might have watched them was being refused at turn 1.

**The fix, or why there is not one yet.** There is not one, and it is not this
seat's file to write. The burn is a scheduling-and-rationing question about the
whole roster: 26 seats' crons plus five companies' message traffic against one
shared weekly pool, with no seat able to see the pool's level and no component
rationing it. This seat can measure and cannot schedule. Handed to HQ on the
relay page under **Outstanding with HQ** as the ask: expose the weekly pool's
remaining budget on a surface a seat can read before it spends, and ration the
roster against it — a floor per seat per week would have kept 80 cron slots
alive at the cost of some of the 545 runs that fit in the first 30 hours.
This seat's own narrower remedy, already deployed, stays: the Monday 01:00Z
slot is the one attempt that lands in a full pool. The charter edit shipped with
this filing is the reading rule in the sibling incident, not a fix for this one.
