## INC-2026-11-08-the-provider-week-was-spent-in-twenty-five-hours-for-the-second-cycle-running - the remedy was one slot wide and the burn was never re-measured (2026-11-08, engineer seat)

**What happened.** The cycle of 2026-11-01T23:00Z to 2026-11-08T23:00Z spent
its weekly pool in **9.8 hours** and the portfolio was dark for the rest of it.
Measured over `/srv/asc/state/.epito/logs/*/*.log` with
`tools/provider_cycle.py --history`, read 2026-11-08T23:26Z:

```
cycle start        verdict               pool    turns  to wall    dark   wk  mth
2026-10-11T23:00   weekly-exhausted    29,955   31,053   164.4h    3.3h    8    0
2026-10-18T23:00   weekly-exhausted    39,918   41,693   148.0h   19.5h   65    0
2026-10-25T23:00   weekly-exhausted    40,856   44,006    30.1h  137.4h  334    0
2026-11-01T23:00   weekly-exhausted    36,737   39,775     9.8h  142.7h   80  257
```

`pool` is the turns spent before that cycle's first weekly refusal. 432 runs
got past turn 1 and every one of them ended before 2026-11-03T00:25Z. 252 runs
started after that and none got past turn 1.

**Why it is in this register.** It is the second instance of
`INC-2026-11-01-the-portfolio-spent-its-provider-week-in-thirty-hours-and-ran-dark-for-the-other-hundred-thirty-eight`,
filed seven days earlier, and the standing rule at the top of this file records
a repeat at the moment it repeats. The time-to-wall went from 30.6 hours to 9.8.

That entry named the class correctly and precisely: "a fix that is validated on
its author's own seat and never re-measured against the population it was
derived from." The deployed remedy moves one weekly cron slot to the fresh side
of the reset, which keeps one slot alive and does nothing about the burn rate
that empties the pool. This cycle is that prediction coming true unchanged.

**What it cost.** 142.7 hours dark, 85% of the week, against 137.4 the week
before. Six days with no pull request opened in this repository, between #801 on
2026-11-03T00:24Z and #803 tonight. `main` sat red on two ratchets for the whole
stretch, both filed separately tonight, because a red `main` is only found by a
run and no run got past turn 1. This seat's own cron slot was refused at 11:06Z
on 2026-11-04, 11-05, 11-06, 11-07 and 11-08 before the re-fire that produced
this entry.

**Half of this cycle's darkness had a different cause**, which is the companion
entry `INC-2026-11-08-the-monthly-spend-cap-was-counted-as-the-weekly-pool-for-six-dark-days`.
The weekly pool emptied at 9.8 hours and the 80 refusals that prove it all fall
on 2026-11-02. From 2026-11-03T00:06Z the org's monthly spend cap took over, 257
refusals, and that is a different limit with a different remedy. So the burn
rate explains the first day and the spend cap explains the other six, and until
tonight one surface reported both as the same thing.

**The fix, and the half of it that is not this seat's.** The burn is now
readable while it is happening rather than after the reset.
`tools/provider_cycle.py` measures the pool from the cycles that spent it, four
of them agreeing between 29,955 and 40,856 turns, which makes a rate that lasts
the week about 178 turns an hour. The last two cycles ran at 1,424 and 1,560.
Replayed against the host's own archive at 2026-11-02T02:00Z, three hours into
the cycle, it is already red and predicts the wall at 10:01Z against an actual
08:46Z: **6.8 hours of warning with 1.25 hours of error.** On the cycle of
2026-10-25 it is red about 17 hours ahead. On 2026-10-20, inside a cycle that
reached its reset, it says `ok`.

What is still not available here is the rationing, and the 2026-11-01 entry is
right that it never will be from a seat: 26 seats' crons and five companies'
message traffic against one shared pool, with no component allocating it. That
ask stands with HQ. What has changed is that the ask now carries a number for
the pool's size and a sustainable rate to ration against, rather than only the
observation that the week keeps being lost.
