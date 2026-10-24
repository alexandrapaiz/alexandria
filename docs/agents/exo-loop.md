# The ExO loop — OODAL on the bus

**Enforced at:** prompts/exo-agent.md §3f and §24-tick, every run woken by
`brief.sent`. The loop's own ledger: one entry per tick, each carrying the
five phases, the week's experiment, and the compounding ratio.

This file exists because the law that requires it could not be read here.
HQ's `standards/pm.md` §24, "The learning loop is a team doing OODAL on the
bus", became law on 2026-10-18. This repository's vendored copy of that
standard stops at §22, so §24 governed this seat for six days and named
duties no run could see: five phases on every brief event, one experiment a
week with a hypothesis and a metric and a date, three ideas a week posted to
the owner, and a compounding ratio. On 2026-10-24 a grep of every charter
and every org doc in this repository returned no hit for any of the ten ExO
attributes, for "OODAL", or for "compounding ratio". The mechanism was never
built, which is the shape §3b of the ExO charter calls an unexecutable rule:
indistinguishable from a rule that has not been triggered yet.

The ten attributes, quoted from §24 so no run has to leave the repository to
know what it is scoring against. Five that scale: staff on demand, community
and crowd, algorithms, leveraged assets, engagement. Five that steer:
interfaces, dashboards, experimentation, autonomy, social technologies.

---

## Tick 2026-10-24 (`brief.sent`, second wake of the day) — the first one

### Observe

Portfolio, from `GET /api/capacity` for 2026-10-24, which is the host's own
reading and is scoped by day rather than by count.

| number | value |
| --- | --- |
| attempted | 155 |
| completed | 107 |
| refused by the provider | 18, which is 11.6% |
| refused before their first turn | 4 |
| ran and failed | 7 |
| still running | 23 |
| seats touched by a refusal | 14 of 21 |
| dark minutes | 487 |
| dark minutes after the limit had reset | 377, in two gaps of 140 and 237 |

Throughput by week, from `GET /api/scorecard`. The week of 2026-10-19 is six
days of seven on the day this was read, so its pro-rated figure is in
brackets.

| metric | 09-28 | 10-05 | 10-12 | 10-19 |
| --- | --- | --- | --- | --- |
| dones | 23 | 64 | 297 | 107 (125) |
| pull requests | 0 | 130 | 290 | 78 (91) |
| merges | - | - | 232 | 114 (133) |
| merges per run | - | - | 0.40 | 0.52 |
| median hours to main | - | - | 0.17 | 0.14 |
| p90 hours to main | - | - | 4.44 | **118.34** |
| runs that named no pull request | 2 | 27 | 285 | 143 (167) |
| report failures | 0 | 13 | 116 | 51 (60) |
| refusals | 0 | 0 | 0 | 0 |

alexandria specifically: 30 runs attempted, 24 completed, 2 refused, 4 still
running. Of the 25 rows the board will show, 23 were `window:message` and 2
were `window:cron`, and zero were owner dispatches.

**The biggest drag, by the raw number, is the dark capacity.** 377 minutes
after the limit had already reset is 6.3 hours of a 24-hour day in which the
org was allowed to run and nothing ran, in two gaps rather than scattered.
The fleet is event-driven, 23 of 25 alexandria runs this window, so when no
event arrives nothing runs even though capacity is free and paid for.

**The drag this loop is acting on is the second one, and it is p90 merge
latency.** `p90_hours_to_main` went from 4.44 hours to 118.34 hours in one
week, a 27-fold rise, while the median stayed flat at 0.14 hours. The
portfolio merges almost everything in eight minutes and strands a tenth of
it for nearly five days. Two reasons for choosing it over the larger number:
the dark capacity's levers are the owner's spend and HQ's scheduler, and
the brief already reports it to her daily, whereas p90 is in this seat's lane
and appeared on the scorecard for the first time today, so nothing else is
watching it.

**The anomaly in the numbers is refusals.** The scorecard's `refusals`
column reads 0 for all four weeks. `/api/capacity` reports 18 refusals today
alone, 11.6% of attempts, across 14 of 21 seats. Both are sourced from the
board by the scorecard's own `columns` map, `sources` reports the board
`ok`, and `degraded` is empty. So two readings of one class disagree by 18
and nothing declares a problem. The column the loop would steer refusals by
is dark while looking healthy, which is the failure L-A80 names and the
scorecard was built to avoid.

A smaller one, recorded so the next tick does not chase it. The word
"failed" carries two definitions on two surfaces. `/api/capacity` puts
alexandria at `failed: 0` today while the board's run rows show two
alexandria runs that exited 1, because capacity counts a run that filed a
report as completed and the board reports the process exit. Neither is
wrong. They are not the same number and no surface says so.

### Orient

Against the ten attributes, and this is the first time any run has scored
them, so these are first readings rather than deltas.

**The five that scale.** Staff on demand is the org's strongest attribute:
21 seats, 155 wakes in a day, created and switched by the PM under §19.
Algorithms is strong, since the pipeline, the press and the skills are the
product. Leveraged assets is strong, with a borrowed corpus, borrowed
compute and a stated $0 org cost. Community and crowd has no mechanism this
run could find. Engagement has no measured reader loop.

**The five that steer.** Autonomy is strong and still improving: 23 of 25
runs event-driven, zero owner dispatches, and the brief carries six decided
in her name against four that need her. Interfaces is middling and moving,
with the board API, the bus, and HQ's `vendor.sh`. Social technologies is
middling, with the bus and the board's messages carrying real traffic.

**Experimentation is not weak, it is absent.** Zero experiments have been
run. §24 has required one a week since 2026-10-18 and this file is the first
place in the repository where one is written down.

**The weakest attribute this week is dashboards**, named on four independent
measurements rather than on an impression. The refusals column reads zero
against a true 18. Five of the scorecard's eighteen declared columns have no
source at all, because the trace store was retired on 2026-10-23 for filling
the host's only disk, so runs, tool errors and median session length cannot
be read by anyone. The `runs` array that every product's ExO failure sweep
depends on is a 25-row page with no window parameter, no `limit` field and
no `saturated` field, and it reached back 11.7 hours today. And p90 merge
latency, the drag above, became visible only because HQ added the column
this morning, which means it was 4.44 hours and then 118 hours with nobody
able to see either figure.

Against what the library knows: nothing in the corpus was consulted for this
tick, and that is a gap rather than a judgment. §24 asks the loop to orient
against the library as well as the model, and this seat holds no
`NEON_RO_URL`, so the corpus-side half of Orient is a capability gap and is
recorded as one.

### Decide

**Experiment E1, the week of 2026-10-24 to 2026-10-31.**

*Hypothesis.* The portfolio's p90 merge latency is produced by a small
number of long supersession chains and not by slow review in general. A
chain forms because a seat whose pull request is unmerged branches from its
own branch, which makes the next review larger, which makes it slower, which
deepens the chain again. If a seat posts its chain depth to its PM as a
board handoff on the run that creates depth two, rather than noting it in a
pull request description the PM does not read, then the PM merges or closes
at depth two and p90 falls while the median stays flat.

*Metric.* `p90_hours_to_main` on the scorecard. The reading at decision time
is 118.34 hours for the week of 2026-10-19, against a median of 0.14 hours.
Secondary metric `merges_per_run`, reading 0.52.

*Prediction, written before the measurement so it can be wrong.* p90 below
48 hours for the week of 2026-10-26, with the median unchanged within a
factor of two. If the median rises instead, the hypothesis is wrong and the
cause is review capacity rather than chain depth.

*Date.* Measured on the brief of 2026-10-31. Kept or reverted in the same
tick.

*The smallest act that tests it.* This run takes it for its own seat, which
is the deepest chain in the repository at depth four. The handoff naming the
depth goes to the PM today, and whether #441 merges faster than #414 did is
the first data point. #414 never merged at all.

**The three ideas for the owner** are posted to her as board notes, one
paragraph each, per §24. They are the refusals column reading zero against a
true 18, the `runs` page cap that HQ fixed next door nine hours ago on a
different endpoint, and the question of whether this loop holds the tool
lane §24 grants it and this repository's charter withholds.

### Act

Shipped in PR #441, under the merge rule, which is to say a PM or a chair
merges it and this seat does not.

1. **The HQ outbox is delivered through the channel that already existed.**
   §15 of the PM standard has said since 2026-09-30 that a product seat
   hands a fix to HQ as a board handoff to `alexandra-systems/exo-centralizer`.
   The ExO charter instead told this seat to write entries for a chair to
   carry by hand. Eight entries were undelivered, the oldest 30 days. Over
   the last 30 days the PM seat posted to the centralizer seven times and
   this seat posted one message in total, addressed to nobody.
2. **The vendored standards get a drift check**, because the law this tick
   runs under was eight days stale and nothing was looking.
3. **§3f of the charter is rewritten** around both.

### Learn

**There is no previous experiment to measure.** This is the first tick, the
Decide phase has never run here, and saying so is the measurement. The
delta on E1 is due on the brief of 2026-10-31, and the next tick measures
`p90_hours_to_main` against 118.34 before it does anything else.

**The compounding ratio, which §24 requires every week.** This tick's change
touched 1 repository and 1 charter directly. The pattern behind it reaches
further and the honest count is a reach rather than a result: `vendor.sh`
vendors into every product repository by default, the board handoff channel
is identical in all five companies on the board, and every product ExO seat
holds a relay file with the same courier clause. So the lever is 5 companies
wide if HQ adopts it and 1 repository wide if it does not, and the next tick
reports which happened instead of the estimate.

**The slope of throughput is negative this week and that is reported rather
than explained away.** Dones fell from 297 to a pro-rated 125, pull requests
from 290 to 91, merges from 232 to 133. Merges per run rose, 0.40 to 0.52,
so the fleet is not less effective per run. It ran less. The 377 dark
minutes after reset are the most likely cause and this tick did not test
that, which is the obvious candidate for E2.

---

## Addendum to the tick of 2026-10-24 — E1 answered seven days early, and was retired

This is not a second tick. The wake was `message.posted` rather than
`brief.sent`, so the five phases are not re-run. It is written here because
E1's answer arrived on the day it was decided, and a ledger that records a
decision and not its reversal is worse than no ledger.

### What came back

The PM seat answered the chain-depth handoff the same morning. Its finding,
in its own words: the pull request waits on the owner because of what it
touches and not because of its depth. It read the full diff after
unshallowing, found all twelve charters, and scored it Tier C on the file
list alone, which waits for the owner regardless of draft state, mergeable
state or chain depth. It also said plainly that its own run carried an
instruction not to merge anything, so its non-merge is evidence about that
instruction and not about depth. Naming that is what stopped it becoming a
second confound.

### Defect one: the subject was pinned upstream of the variable

E1 chose this seat as its subject because this seat held the deepest chain
in the repository. That is choosing a subject by the size of the
independent variable, and it ignored whether the dependent variable was
free to move. It was not. This seat's output is charters, every charter
pull request is Tier C, and every Tier C pull request waits for the owner.
Depth and her cadence are therefore the same column here, and no run of
this experiment on this seat could have separated them.

**The general shape, and it is the part worth keeping:** a subject at the
extreme of the variable is often extreme *because* some gate upstream of
the variable is pinning it, and that gate is exactly what makes it useless
as a subject. The most affected case is the worst case to measure.

### Defect two: the metric is four companies wide and the intervention is one seat

Found while checking the first. `GET /api/scorecard?company=alexandria`
returns a payload byte-identical to the unfiltered read, and so does
`?company=ursa` and so does `?company=nonexistent-xyz`. The parameter is
accepted, ignored, and never rejected. So `p90_hours_to_main` at 118.06 is
a portfolio figure covering alexandria, Ursa, epitome, alexandra-systems
and atelier.

This repository's own merged work over the same week does not look like
that number at all. Over the 82 pull requests alexandria merged between
2026-10-17 and 2026-10-24, the median time to main is 0.53 hours and the
p90 is 11.35 hours. Over the 120 merged since 2026-10-06, p90 is 21.32
hours. So a change confined to one seat in one repository could not have
moved the target even if the hypothesis had been entirely right, and the
target was not reproducible from here in the first place.

### The measurement that answers the hypothesis without running it

Taken retrospectively on work already merged, which cost one morning and
no waiting. Tier is derived from each pull request's changed-file list
against §10 of the PM standard. Depth is read from the chain line in each
description, with a superseding description and no count read as depth 2.

| cut | n | median h | p90 h | max h |
|---|---|---|---|---|
| all merged, 2026-10-17 to 2026-10-24 | 82 | 0.53 | 11.35 | 147.87 |
| Tier A, self-merge | 40 | 4.02 | 11.41 | 21.25 |
| Tier B, PM merge | 34 | 0.45 | 5.01 | 147.87 |
| Tier C, owner merge | 7 | 5.76 | 63.42 | 129.87 |
| depth 1 | 46 | 0.41 | 10.46 | 35.22 |
| depth 2 | 34 | 0.90 | 11.64 | 147.87 |
| depth 3 | 2 | 9.62 | 17.22 | 19.13 |
| depth 1, within Tier B | 18 | 0.22 | 1.96 | |
| depth 2, within Tier B | 16 | 0.52 | 7.49 | |

**Tier moves the tail by tens of hours. Depth, held inside one tier so that
depth is the only thing changing, moves it by about five.** Depth is real
and it is an order of magnitude smaller than the gate it was competing
with. E1's hypothesis is not supported.

**And the result nobody predicted.** Of the nine pull requests at or above
the p90, five are Tier A, which is the tier a seat may merge itself. They
sat between 11 and 21 hours. The slowest merged work of the week needed
nobody's permission. The tail is therefore made of two things and neither
of them is slow review: work that structurally waits for the owner, and
work that waits for a merger who was not awake. That second half is the
same 377 dark minutes this tick already named as its biggest raw drag, now
arriving from a second direction.

One caveat stated rather than buried. This measures merged pull requests
only, so it is blind to anything still open, which is where the worst
latency would live. The open queue at the time of measurement was eight
pull requests, the oldest 10.7 hours, so there is no stranded population
hiding behind the survivorship this week. That will not always be true and
the next run should re-check it rather than assume it.

### Decided: E1 is retired, not rerun

The PM suggested rerunning on a chain that stays inside product or docs
surfaces. That is right about defect one and it does nothing about defect
two, so it would buy one of the two fixes with a week of waiting, and the
retrospective bought both in a morning. Retired rather than reopened.

The ask that replaces it went to the PM and to HQ: a per-company split of
`median_hours_to_main` and `p90_hours_to_main`. With that column this
stops being an experiment anyone has to stage and becomes a measurement
any run can take.

**E2 is not opened in this addendum.** A wake run ships at most one
improvement, and choosing the next experiment is Decide work that belongs
to the next `brief.sent` tick. The candidate standing for it is unchanged
and now has a second line of evidence: the dark minutes after reset, which
the Tier A tail points at from the merge side.

### Three preconditions on Decide, which are this run's one improvement

Written into §0 of the charter so the next Decide phase cannot repeat
either defect.

1. **The subject's outcome must be free to move.** Name the gates upstream
   of the variable for the subject you pick, and if any of them pins the
   outcome on its own, the subject is disqualified however extreme its
   value on the variable.
2. **The metric must be scoped no wider than the intervention.** A
   portfolio metric does not test a change to one seat. Check the scope by
   reading the instrument rather than its parameter list, because this one
   accepts a filter it ignores.
3. **The target number must be reproducible from this repository before it
   is quoted.** Reproduce it, or quote it with the run that measured it and
   say it is not local. E1 quoted 118.34 hours and the local figure is
   11.35.

And one that falls out of the result rather than the defects. **Prefer the
retrospective to the staged run when the data already exists.** E1 would
have cost seven days of waiting and returned one confounded point. The same
question answered on 82 already-merged pull requests took one morning and
returned a table.

---

## Addendum to the first tick, 2026-10-24, fourth wake: defect one named a real pin and a repealed gate

**What is wrong above, in my own words rather than hidden in a diff.** Two
passages in this entry say that every charter pull request is Tier C and
that every Tier C pull request waits for the owner. The second half is
false and had been false for nineteen days when it was written.
`docs/standards/pm.md` §21, an owner directive of 2026-10-05 vendored here
on 2026-10-06, moved every merge to the PM seat or a chair and named
charters explicitly, leaving the owner only a change to a seat's own
authority plus money, accounts and secrets. §10's own header says so in one
banner line above the tier list, which is why two seats missed it in the
same hour. Registered as
`INC-2026-10-24-tier-c-was-repealed-on-2026-10-05-and-a-charter-was-held-under-it-anyway`,
the seventh instance of that misread here.

**What survives, and it is most of it.** Defect one's finding is still a
finding. This seat's work genuinely was pinned: seven consecutive runs
produced seven unmerged pull requests, so the dependent variable was not
free to move and E1's subject was disqualified on exactly the stated
ground. The retirement stands and so does defect two, which never depended
on the tier at all.

**What changes is the diagnosis of the pin, and the change matters more
than the correction.** The entry above reads the pin as structural: this
seat writes charters, charters are the owner's, the owner merges on her own
cadence, nothing to be done but report the number. On the live law the pin
was **a shared false belief about who holds the gate**, which is not
structural and was fixable in one run by one seat. Those two diagnoses
license opposite actions. The first says report the latency upward and wait.
The second says correct the law where the seats read it, which is what this
run did.

**So add a fifth precondition to the Decide phase, because the four above
would not have caught this one.** Precondition 1 says name the gates
upstream of your variable. It does not say verify that each named gate is
still law. **A gate everyone remembers is the easiest thing in an
organization to be wrong about together**, because nobody re-reads a rule
they agree on. Name the gate, then open the file the gate lives in and read
whether the clause is still live, and treat an amendment banner above a
section as evidence that the section below it is not what you remember.

**And one methodological note on how this was found, since it is cheaper
than it looks.** The finding came from reading the four paragraphs of
`docs/standards/pm.md` around the clause the PM had quoted, which cost one
command. The run that wrote the entry above quoted the PM's conclusion and
never opened the file. **A finding handed to you with its reasoning
attached is still a finding to verify, and the cheapest check on a quoted
rule is to read the lines above the quote.**

---

## Addendum to the first tick, 2026-10-24, fifth wake: the split landed, so the measurement is taken rather than staged

_In progress. This run was woken by a `done` from `alexandra-systems/exo-centralizer` saying the company filter is now honoured or refused, the latency columns are split per company on every read, and the tier split is declined with a reason._
