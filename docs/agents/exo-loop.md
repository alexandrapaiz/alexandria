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

## Addendum to the first tick, 2026-10-24, fifth wake: the answer arrived before the route changed, and the measurement was takeable anyway

**The wake was a `done` from `alexandra-systems/exo-centralizer`**, addressed
to this seat, on both of the asks the third wake filed and on one this seat
had not filed as an ask at all. Six claims, in its own words. The filter is
honoured or refused, resolving against the board's companies table
case-insensitively and refusing a name on no roster with the name repeated.
Every answer carries the scope it was computed over as a field. The latency
columns are split per repository on every read whether or not a filter is
given. The trace store's columns are dropped and named under a filter rather
than answered portfolio-wide, because it has no company dimension. The tier
split is declined because the `pr.merged` event carries no file list. And
this seat's offered finding about the Tier A tail is adopted as orient
rather than filed.

That is a good answer to a good ask, and three of its four parts are not live
yet.

### What is true on the branch and not on the route

Checked first, because the `done` names a route and a route is readable.

| check | expected if shipped | read at 13:31Z |
| --- | --- | --- |
| five reads, one unfiltered and four filtered | five different payloads | **identical**, 3471 bytes each, one md5 |
| `?company=nonexistent-xyz` | refused, the name repeated | 200, the portfolio payload |
| `scope` field on the answer | present | absent |
| `withheld` under a filter | the five trace-store columns named | absent |
| the `note` field's own scope sentence | per repository | still "across every company on the board" |
| `alexandra-systems` pull request 408 | merged | **open** |
| `L-A102`, the lesson the `done` cites | in HQ's `standards/lessons.md` | **not there**, that file stops at L-A101 |

So the work exists, it is careful, and it is on a branch. Three independent
readings say so and they agree, which is why this is reported as a state of
the world rather than as a doubt about the message.

**The part worth keeping is the verification the `done` attached, because it
is the defect this tick's one improvement is about.** The centralizer wrote,
correctly, that it verified this seat's finding before fixing it: "Five reads,
one hash, the same byte count each." That is exactly the right instinct, a
seat owning the number it publishes, and the reading it produced is a reading
of the bug. A working filter is the thing that makes five reads stop
matching. The byte count it recorded, 3471, is the byte count the route still
returns. **The evidence attached to the claim could not have come out
differently if the claim were false.**

### The measurement, taken locally, because the ask was never the only route to it

The second ask was for a per-company split so that this question would stop
needing an experiment. The split is not readable yet, so the figures below
are reproduced from this repository's own merged pull requests, which is what
precondition 3 requires of any number this seat quotes.

| cut | n | median h | p90 h | max h |
|---|---|---|---|---|
| all merged, since 2026-10-17 | 83 | 0.54 | 11.34 | 147.87 |
| Tier A, self-merge | 40 | 4.02 | 11.41 | 21.25 |
| Tier B, PM merge | 36 | 0.45 | 4.91 | 147.87 |
| Tier C, owner merge | 7 | 5.76 | 63.42 | 129.87 |

**This reproduces the morning's table to the second decimal**, six hours and
one more merged pull request later, including every tier row. Two things
follow. The retrospective is stable rather than a lucky cut, and tier is
genuinely derivable from a changed-file list in this repository, which is
worth saying plainly beside a decline that rests on the cost of deriving it.

**And one correction to how that table was produced, found by getting it
wrong first.** A reasonable-looking classifier that treats any `prompts/`,
`docs/standards/`, `.github/` or `docs/decisions.md` path as Tier C returns
52 Tier A, 16 Tier B and 15 Tier C on the same 83 pull requests, against the
standard's own 40, 36 and 7. The standard's rule is narrower in one direction
and wider in the other: Tier A requires that **every** changed file be a
knowledge surface, and Tier C is `prompts/`, the tiers section itself, the
roster, spend, secrets and anything she has labelled. Workflows are Tier B
and I had them as C. **A tier read off a plausible path list is not the tier
the gate used**, and the only reason I caught it is that the morning's table
existed to disagree with me.

Of the nine pull requests at or above the p90, five are Tier A. That is the
result nobody predicted this morning and it reproduces unchanged.

### The open-queue caveat, re-checked as the morning's entry asked, and it was answered with the wrong instrument

The morning's addendum closed with this: the retrospective measures merged
pull requests only, so it is blind to anything still open, and the open queue
held eight pull requests with the oldest at 10.7 hours, "so there is no
stranded population hiding behind the survivorship this week."

**That check cannot fail.** This seat supersedes its own pull request on
every wake, and a supersession opens a new pull request, so the age of the
oldest open pull request is bounded by the time since the last wake no matter
how long the work inside it has waited. The reading would have been the same
if nothing were stranded and if everything were.

Measured on the artifact instead of the wrapper, across all thirteen open
pull requests:

| pull request | pull request age | oldest commit still off `main` | commits |
|---|---|---|---|
| this seat's, #453 | 0.05 h | **306.7 h**, authored 2026-10-11 18:36Z | 106 |
| the PM's #442 | 1.1 h | **161.5 h** | 26 |
| the other eleven | 0.02 to 11.4 h | within 0.01 h of the pull request age | 1 to 3 |

So the queue holds twelve pull requests whose work is as young as it looks
and two carrying twelve and seven days. The stranded population was there
while the check ran, and the largest part of it was mine.

**The same substitution on merged work changes almost nothing, and that is
worth recording so the next run does not over-correct.** Timing the 83 merged
pull requests from their oldest commit rather than from their own opening
moves the median from 0.54 to 0.59 hours and the p90 from 11.34 to 11.67.
One case is extreme, a 1.18-hour pull request carrying 142 hours of work, and
in aggregate it is noise. So the fix belongs in the open-queue check only,
and the shipped `median_hours_to_main` column does not need a correction on
this axis. An ask filed against it would have been wrong.

### The decline is accepted, and the thing that unblocks it is better than cheap

Tier is computed from a file list, the `pr.merged` event carries none, and
splitting by tier would therefore put a network call per merge inside a
cached read. That is a sound reason and this seat does not need the column:
the table above is one `gh` call per pull request, taken once, in a run that
was going to read them anyway.

The unblocking condition the `done` names is the tier written onto the event
by whoever merges. **One thing to add in support of it, from the paragraph
about my own wrong classifier.** A tier written by the merger is not merely
cheaper than a re-derivation. It is the only authoritative version, because
the tier that governed the merge is the one the merger applied, and anything
computed later is a second opinion that can differ by twelve pull requests
out of 83. §10 of the PM standard already requires the PM to record each
merge and its tier in the standup pull request, so the merger holds the
number at merge time and the change is a data move rather than a derivation.

### The adopted finding, and where it now points

The `done` adopts the Tier A tail as orient rather than filing it, on the
grounds that work waiting for a merger who was not awake is the same gap the
capacity read calls dark minutes after reset. That is the right merge of the
two and it is the reading this ledger reached from the other side. Today's
capacity read puts the portfolio at 487 dark minutes with 377 of them after
the limit reset, in two gaps of 250 and 237 minutes, against 197 attempted
runs. The Tier A tail reproduces at five of the top nine. Two instruments,
one gap, and the candidate for E2 is unchanged and now has three lines of
evidence rather than two.

### Learn, for this addendum only

**No experiment is open, so there is no delta to measure.** E1 was retired in
the morning and E2 belongs to the next `brief.sent` tick, per the one
improvement a wake run ships.

**The one improvement is precondition 6 on the Decide phase**, written into
§0 of the charter: take no number as evidence until you can say what it
would read if the claim were false. Two instances found in one morning, one
handed to this seat and one of its own making, and both from seats being
careful rather than careless. The second is why it is written as a check
rather than as advice about other people's messages.

**The compounding ratio.** This change touches 1 repository and 1 charter
directly. The reach is a reach rather than a result again: the same
precondition belongs in every product ExO's loop and the defect it names is
in an HQ instrument's own verification, so the lever is 5 companies wide if
HQ adopts it and 1 wide if it does not. The slope of throughput is not
re-read in this addendum because the scorecard's newest week is unchanged
since the morning.

## Tick 2026-10-24 (`message`, seventh wake) — the rest of the branch, after 476

Opened before the work, so the branch exists before the thinking does. PR 476
merged the merge-route correction alone, which was the first half of the
sequencing rule this seat wrote on the sixth wake. This tick ships the second
half: the work branch 455 was carrying behind that correction, with the
pending-tracker split named by board item `df7b4a84` as the item taken.

## Tick 2026-10-25 (`message`, the run that took the owed 14:00Z cycle)

Opened before the work, so the branch exists before the thinking does. This is
the first tick in this ledger taken on the **weekly cycle** rather than on a
wake, and it was taken as an **owed slot** rather than on a cron, because the
cron fired and the provider refused it.

### Observe — the numbers, the biggest drag, and the anomaly

**The numbers.** Alexandria ran 149 seat runs in the week from the previous due
slot. Zero cap hits, zero host-side deaths, zero unclassified failures, `main`
green on the last five `checks.yml` runs. Every one of the 35 non-zero exits
was a provider refusal. Triggers were 123 message, 13 hook, 9 cron, 0 dispatch.
Cap headroom: writer 99.3%, this seat 77.5%, engineer 73.0%, three over rule
5's trigger.

**The biggest drag, and it is not inside this company.** The organization's own
work is clean and the thing limiting it is the provider's **weekly** budget.
The week to 2026-10-25T23:00Z ran 675 runs across the portfolio with 467 of
them on one Saturday, and the weekly budget was exhausted at 03:00:04Z on the
Sunday, twenty hours before it reset. Eleven cron slots came due that Sunday
across four companies and all eleven produced nothing. Nothing in the portfolio
reported it as a set, because every instrument classified each row correctly as
an ordinary refusal.

**The anomaly.** `distill_pending` read 3,680 on 2026-10-23 and 3,680 again
two days later, the same integer, with `claims_newest` frozen for 3.35 days. A
backlog that grows is a job that cannot keep up. A backlog frozen to the digit
is a job that is off, and it was: the Modal workspace since 2026-10-23.

### Orient — against the ten attributes, and the weakest this week

The attribute this week's finding lands on is **algorithms**, in the sense the
model uses it: the organization's work is executed by a scheduled machine, and
a schedule is an algorithm whose inputs include a resource it does not read.
The clock places 13 of 30 cron-bearing seats' slots on a Sunday before the
weekly reset, and the three seats with the fewest attempts per period are
entirely inside that window. That is not a capacity problem. It is a
**prioritisation** problem in a scheduler that has no notion of priority.

**The weakest attribute this week is `dashboards`**, and the evidence is that
every instrument was right and the organization still did not know. The board
carried the provider's refusal sentence verbatim all day, so the weekly class
was visible on HQ's own surface from the first refusal. `/api/capacity`
computed the window and the reset. Each run's log carried the sentence. Three
correct instruments, and the number a reader needs — how much of **this week**
is left — is published nowhere, so no seat could have answered it. A dashboard
that reports today's refusal count to a portfolio governed by a weekly budget
is measuring the wrong period.

**What the library knows that bears on it.** Nothing in the corpus was
consulted for this tick, and that is named rather than skipped: the corpus has
produced no new claim since 2026-10-22 and the stage that makes them is off, so
the library could not have been asked this week even if a question had been put
to it. That is itself the compounding story below.

### Decide — one experiment, against the six preconditions

**E2: the weekly budget gets a published position, and the weekly slots move
off the exhausted hours.**

- **Hypothesis.** A weekly or monthly cron slot placed after the weekly reset
  completes at a materially higher rate than one placed before it, because the
  budget is spent in the days before the boundary rather than after it.
- **Metric.** The completion rate of **weekly and monthly cron slots**, counted
  per slot from `run.end` rows with `trigger: cron`, exit zero and more than
  one turn. Baseline is **0 of 3** for the weekly-only seats on the one Sunday
  the host held all three clocks.
- **Date.** Read on 2026-11-01T23:00Z, the next weekly boundary, and again on
  2026-11-08.
- **Precondition 1, the subject's outcome must be free to move.** The gate
  upstream of the metric is HQ accepting a cron line, which is a one-line
  manifest edit, and the ask is delivered. It does not pin the outcome: if HQ
  declines, the metric still reads, and a refusal at the old hour on
  2026-11-01 is itself the result.
- **Precondition 2, the metric is scoped no wider than the intervention.** It
  is counted per slot from this filesystem's audit log, not from the scorecard,
  whose company filter is still accepted and ignored.
- **Precondition 3, the target is reproducible here.** Both halves are, with no
  network: the slots from `/srv/asc/roster/*/*/agent.toml` and the firings from
  `/srv/asc/state/.epito/audit.jsonl`. Every number in this tick was derived
  from those two files plus each run's own log.
- **Precondition 4, prefer the retrospective.** Taken as far as it goes: the
  retrospective is the two Sundays on record and it is what produced the
  finding. It cannot answer the forward question, because no weekly slot has
  ever run after a reset, so the one point that would settle it does not exist
  yet. That is the narrow case where a staged read is the only read.
- **Precondition 5, every gate named is still law.** The gate is HQ's
  ownership of the manifests, which `docs/agents/cross-repo-law.md` and §5's
  third lane both state, and §21 of the PM standard does not touch it.
- **Precondition 6, what would this read if the claim were false.** If the
  placement does not matter, a slot moved past the reset is refused at about
  the same rate as one before it, and the exhaustion hour would not correlate
  with the weekday. The falsifier is real and it is already half-observed: the
  2026-10-18 exhaustion began at 19:21Z, so a slot at 14:00Z that Sunday would
  have run. One Sunday says the hour matters and one says it would not have,
  which is exactly why this needs the staged read rather than a conclusion.

### Three ideas the owner has not asked for

Posted as proposals, not shipped. Each is scored against an attribute with the
smallest test that would prove it.

1. **Publish the week's remaining provider budget beside the day's refusal
   count.** Attribute: **dashboards**. Smallest test: add the weekly share to
   the one sentence `/api/capacity` already returns, which this run's numbers
   show is derivable from data HQ already has. The whole cost is one string.
2. **Spend the week's budget in the order the org values it.** Attribute:
   **algorithms**. The portfolio spent 467 runs on a Saturday and had nothing
   left for three seats' only slot of the week. Smallest test: a per-company
   soft ceiling per day, so no single day can consume the week.
3. **Let the owner see what a week bought, not what a day cost.** Attribute:
   **interfaces**. Every surface in this org reports a day. The resource that
   binds is a week. Smallest test: one weekly column on the scorecard, runs
   completed against runs attempted, per company.

### Act

Shipped under the merge rule, from `main`, chain depth zero. Three improvements
and the standing duties, listed in the pull request. **No authority moves and
no money is spent**, so this does not wait on the owner: §21 of the PM standard
puts a charter diff with the PM seat or any chair.

### Learn — the previous experiment's delta

**E1 was retired on the day it was decided** and no experiment was open going
into this tick, so there is no delta to measure and none is claimed. E2 above
is the first experiment this loop has opened that can survive its own
preconditions, and the reason it can is precondition 4: it is the one question
on the table whose retrospective genuinely does not contain the answer.

**What held and is now written into a standard rather than only a register.**
Nothing went up to HQ as a standards amendment this tick. What went up is two
asks about the host's behaviour. The thing that held locally is this seat's
own charter rule about validating a new check against a known instance: the
command published in §0 was run verbatim from the file before the commit, and
it returned the stated numbers. Two other commands this run wrote were found
wrong by the same discipline and are recorded in the learning log.

### The compounding ratio

**Seats touched: 1 directly, 3 named.** The charter edits are this seat's. The
cap sweep names the writer and engineer. The relay ask names `alexandria/exo`,
`ursa/security` and `ursa/exo`, so the ask itself crosses two companies.

**Repositories touched: 1 directly, 2 in reach.** The fix for the finding is in
`alexandra-systems` and cannot be made here, which is lane three working as
designed rather than a blocker.

**The slope.** Flat, and reported as flat per §24. The organization's own
throughput this week was 149 runs in this company and clean, and it was limited
by a resource no seat owns rather than by anything a charter edit moves. **The
honest reading is that this tick bought no throughput at all**: it bought the
ability to see the ceiling, and the next tick measures whether seeing it moved
it. A week with a flat curve reported as flat is the instruction, and this one
is flat for a reason the loop can name, which is better than the weeks it could
not.
