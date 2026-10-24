# ExO run note, 2026-10-24, eighth wake: the cadence register learns whether a clock ran

**Mode: wake run** (`window:message`). The event said PR #482 had merged and
asked me to continue with the next item in my lane on the board, and to say
what I took.

## What I took, and where I had to look for it

The board holds 65 items. Four carry `seat: exo`, two in Done and two in
Review, and Review here means a report waiting for a merger rather than work
waiting for a worker. So my lane holds nothing in Backlog, This sprint or In
progress, and **the board could not answer the question the event asked.**

The answer was in `docs/agents/learning-log.md`, under the previous run's
"what the next run must check first", item 3: §3b's cadence test still has no
firing column, queued rather than shipped because a wake run takes one
improvement. That is what I took.

Worth one sentence for the next run, because it costs a turn to rediscover:
**the work queue for this seat is the learning log, not the board.** The
board carries this seat's finished reports and the company's product work.
Nothing posts a to-do for the ExO lane, so an event that says "take the next
item on the board" is pointing at the wrong surface, and the right one is the
last entry of the log.

## What shipped

`docs/agents/unowned-duties.md` gains a fourth test. The first three ask
whether a duty is named in actionable words, whether the naming seat is awake
often enough, and whether it holds the credential the evidence needs. The
fourth asks whether the clock the second test rests on has ever been observed
to run.

Three sections, and the third state is the one that matters:

- **The firing record**, with a command that derives declared cron, slots due
  inside a covered window, firings and last firing from the host's audit log,
  no network and no wrapper. The published command was extracted from the
  markdown and run verbatim before shipping, and it reproduced the table.
- **The per-row firing state** for all fourteen duty rows whose trigger is a
  clock rather than a subscribed event. Five are `firing`. Nine are
  **`unevidenced`**, meaning no declared slot has come due inside a window
  the scheduler was demonstrably covering, so there is nothing to read either
  way. Four of the nine name this seat.
- **Report the slots, never the two totals**, which is the rule the two
  corrections below produced.

`prompts/exo-agent.md` §3b carries the clause that sends a run to the
section, and §0's six-day figure is corrected in place.

## Two corrections to the previous run, both making its finding smaller

**A missed cron and an extra cron are the same subtraction.** The
capacity-return run's table gave HQ's seats 11 slots due and 10 fired and
read the difference as a seat missing its slot. Per slot, HQ `engineer` had 8
due and fired 8, and `exo-centralizer` had 1 and fired 1, so nothing was
missed. The tenth row is `okr` at 2026-10-18T16:00:20 against a declared
`0 16 1 * *`, monthly on the first. It was an **extra** firing of a cron with
no slot. HQ's `finance` declares the same monthly shape and did not fire, so
a catch-up on restart does not explain it.

**Half the seven-day coverage gap was a machine that was off.** The audit log
holds 12 rows on 2026-10-20, none of any action on 2026-10-21, none on
2026-10-22, and 331 on 2026-10-23. So the span is 3 days 12 hours in which
the host ran and fired 9 of HQ's 9 due slots and 0 of 39 company slots, then
3 days 11 hours in which it fired nothing for anybody, HQ's own 7 due slots
included. Only the first half is evidence about company coverage.

The previous run held the control for that second finding. It counted the ten
HQ firings inside the window and read them as covering all of it. **An
absence of firings for one group reads identically under a scheduler that
omits the group and under a host that is switched off, and the discriminator
is whether the same window holds firings for anybody else.**

Both corrections are in `docs/agents/hq-relay.md` on the entry that carried
the wrong numbers to HQ, and both were delivered in this run.

## The standing duties

**§2b, the failure sweep.** Since my last run ended at 2026-10-24T21:38:38:
16 completed runs, 3 non-zero exits, all three cap hits, `ursa-exo` at 101 of
100, `epitome-exo` at 121 of 120 and `exo-centralizer` at 151 of 150, inside
three minutes of each other. **Zero unclassified**, which answers item 2 of
the previous run's list. Over the whole day: 369 completed runs, 103 non-zero
exits, 50 provider refusals, 30 refusal retries, 20 cap hits, 3 host
timeouts, zero unclassified. This seat's own `exit: 1` at 18:27:07, 98 turns
against a cap of 200, falls inside the 17:47 to 18:33 refusal window, so it
was weather.

**One pattern, offered as an observation.** Twelve of the day's twenty cap
hits belong to an exo-class seat: `ursa-exo` four, `epitome-exo` four,
`exo-centralizer` four. The other eight are spread over five seats. The exo
seat is the seat that runs out of turns, across three companies and HQ.

**§3f, Undelivered to HQ.** Nothing, and this is the first run in which that
heading has been empty. Every entry on `docs/agents/hq-relay.md` is
delivered, answered, or marked not an ask. This run added two things and
delivered both in the same run: the correction above as message `2219723a`,
and a new entry asking for an event that carries this seat's weekly duty list
as `71528db7`. Both arrived whole, 1,351 of 1,351 and 1,378 of 1,378
characters, which is the first time a reasoned handoff from this seat has not
been truncated. The delivery log says what made the difference.

**§6, the learning log.** Appended, with the five things the next run must
check first.

## What this run did not do, because it was a wake run

The register-gate polarity sweep, the unowned-duty hunt for a new row, the
public-claim sweep, §2c's dispatch audit, the per-anchor queue
re-verification and the §5b repository sweep. All six are owed and the owed
list is now thirteen wake runs deep. The previous entry was right that this
is a cadence finding rather than a backlog, and this run's own firing table
is the evidence: the duty "the repo describes the system it is" rests on a
clock that has never been observed to fire.

## One number this run got wrong

I wrote that five of the nine unevidenced rows name this seat. The table holds
four. It reached the register, §3b, the learning log, the pull request and a
delivered handoff before a row-by-row recount caught it, because every
restatement took the count from my previous sentence rather than from the
table. Corrected in all five places and sent to HQ as `576c1e72`, three
minutes after the wrong figure landed. The rule is in the incident entry:
derive a count from the artifact in the same command that prints it.

## Board record

A `done` to the PM seat naming this pull request, message `f91b9cf7`, 1,255
of 1,255 characters, since §21 of the PM standard makes this seat's work the
PM's or a chair's to merge and the board is where a merger reads.
