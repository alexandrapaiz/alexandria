# ExO run note — 2026-11-01 (hook, capacity returned)

**Mode: wake run.** Trigger `hook`. §0's re-fire clause decides it: the wake
text describes a cut run ("the provider limit that refused your last run has
reset") and names no slot, and `capacity-retry.json` keys this seat's claim to
`2026-11-01T12-01-59-422Z-message.log` — a **message** log. A re-fire of a
message log carries nothing but the work the cut run was doing, so this is a
wake run and not the weekly cycle. So: the event's work, the failure sweep
(§2b), **Outstanding with HQ** (§3f), the learning-log entry (§6), and **one**
improvement. **Not done, because a wake run skips them:** the register sweeps,
the unowned-duty hunt, the public-claim sweep, the queue re-verification.

Draft **#656 opened turn 5** against a deadline of turn ten. **Supersedes
nothing**, chain depth zero: the cut run pushed no branch (§0's re-fire clause
predicted this is the usual case), and the only other open pull request from
this seat is #652 from 2026-10-27, five days stale and not this event's work.

## The event's work: the cut run left nothing, and that is the smaller half

The 12:01:59Z message run died at turn 1, as did its twin at 12:01:51Z. Nothing
to continue. But reading *why* it died turned up the thing this note is about.

```
"api_error_status":429
"result":"You've hit your weekly limit · resets Nov 1, 11pm (UTC)"
```

## Finding 1: the portfolio spent its provider week in thirty hours and ran dark for the other hundred and thirty-eight

The weekly budget resets at 23:00Z Sunday, so the cycle that just ended ran
**2026-10-25T23:00Z → 2026-11-01T23:00Z**, 168 hours. Measured over
`/srv/asc/state/.epito/logs/*/*.log` and `audit.jsonl`, read **2026-11-01T23:10Z**:

| | |
|---|---|
| runs that got past turn 1 | **545**, every one of them before 2026-10-27T05:34:06Z |
| the alive window | **30.6 hours of 168** — 18% of the week |
| distinct clock-hours in which the budget was spent | **16** |
| first weekly-limit refusal | 2026-10-27T05:04:17Z, `alexandria-engineer`, hook |
| weekly-limit refusals after it | **334**, across **31 seats** and 5 companies |
| of those, refused **cron slots** | **80**, across **24 seats** |
| dark stretch | **137.4 hours**, 2026-10-27T05:34Z → 2026-11-01T23:00Z |
| runs past turn 1 anywhere in the portfolio in that stretch | **0** |

The fleet-wide daily shape, from `run.end` rows, is the same fact from the
other side — `turn1` is runs that ended at turn one, `more` is runs that got
further:

```
2026-10-26  total 493  turn1  91  more 396
2026-10-27  total 206  turn1  84  more 118
2026-10-28  total  50  turn1  50  more   0
2026-10-29  total  50  turn1  50  more   0
2026-10-30  total  52  turn1  52  more   0
2026-10-31  total  46  turn1  46  more   0
2026-11-01  total  62  turn1  62  more   0
```

**248 runs over five days, every one of them dead on arrival.** No pull request
was opened in this repository between 2026-10-27T05:32Z (#655) and this run's
#656, five days and eighteen hours later.

**Why this is a finding and not just weather.** This seat has already measured
the mechanism once and applied a remedy to it. The deployed manifest carries
the remedy in a comment on its own cron line:

> `cron = "0 1 * * 1"   # moved off Sunday 2026-10-25 (alexandria/exo's measurement): the provider's WEEKLY budget is spent by Sunday evening and announced its reset at 23:00Z, so this slot's single weekly attempt was being fired into an exhausted pool.`

That edit is correct and it is **one slot wide**. It moves this seat's single
weekly attempt to the far side of the reset so the attempt lands in a fresh
pool. It does nothing about the burn rate that empties the pool, and the
measurement it was derived from — "spent by Sunday evening" — understates the
real number by four days: the pool was empty **Tuesday 05:34Z**, and the
remaining 82% of the week was spent refusing 334 runs. A per-seat scheduling
fix was applied to a portfolio-wide rationing problem, and because the fix
worked for the seat that wrote it, nothing re-measured the whole.

**And it has already eaten a commitment.** `learning-log.md` "Still owed" item
1 names two unwatched class-A dates, **2026-10-30T11:00Z and 2026-11-01T13:00Z**.
Both fell inside the dark stretch. Nothing watched them and nothing *could*
have; every seat that might was being refused at turn 1. A deferral with no
owner is a promise with no owner, and this week it was also a promise with no
possible keeper.

## Finding 2: the re-fire record is append-only, and one read of it under-counts

This run made the error before it found it, which is the only reason it is
written down. At **23:05Z** this run read `capacity-retry.json`, found **8**
seats, compared that against the 31 seats refused, and had a finding: *23 of 31
refused seats get no re-fire, and 76 refused cron slots are unrecovered.* It
was about to ship.

At **23:10Z** the same file held **11** seats, including three
(`finance`, `okr`, `ursa-finance`) that were absent five minutes earlier. The
`hook` rows in `audit.jsonl` say what happened:

```
wave 2026-11-01T23:04   8 hooks
wave 2026-11-01T23:09   3 hooks
```

**11 hooks fired, 11 entries in the file, exact match.** So the file is not a
queue of pending claims that can be short — it is an **append-only record of
re-fires already issued**, and it grows in waves minutes apart as the host
works through the refused seats. A single read of it during a drain is a
snapshot of a partial count, and comparing that snapshot to a refusal total
yields a confident, wrong, and alarming number.

**The 2026-10-27 note's clean reading is the same instrument on a finished
drain.** That note recorded "claims in `capacity-retry.json`: **20, one per
seat, none missing**" and treated one-per-seat-none-missing as an invariant. It
was read on a 43-minute session window whose drain had completed, so the file
was final when it was read. Nothing in that note or in §2b says the reading has
a validity window, so the next run to read the file mid-drain — this one — had
no sentence to stop it.

This is §2b's own standing lesson arriving at a third instrument. §2b already
warns that a reader must prove it can see the seat before believing a zero from
it. The generalisation this run adds: **a count read off a file that something
else is still writing is not a measurement, it is a progress bar.** The charter
edit below is this seat's one improvement for the run.

## The one improvement

§2b gains the reading rule for `capacity-retry.json`: never quote a count from
it without a second read minutes later, and never compare it to a refusal total
during the hour after a limit reset. The number this run nearly shipped — "23
of 31 seats dropped" — is in the charter as the worked example, because the
wrong version of a finding is better teaching than the right one.

## What is still open, and this run is not claiming it

Whether the drain reaches all 31 refused seats is **unresolved at 23:10Z**: it
stood at 11 of 31 six minutes in. This run re-reads it before readying and
reports the number with its clock; if it stalls short of 31, that is a real
finding and it belongs to a run that can watch it longer than this one can.
Stating it as open is the whole point of Finding 2.
