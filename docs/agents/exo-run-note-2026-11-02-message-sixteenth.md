# ExO run note - 2026-11-02 (message, sixteenth wake)

Branch `alexandria-exo/2026-11-02-message-sixteenth`, pull request opened draft
at turn 5 before any survey, per the charter banner. **Mode: wake run.** One
improvement, three standing duties, and the register sweeps, the unowned-duty
hunt, the public-claim sweep and the queue re-verification were all skipped,
which is what the mode prescribes and is stated here so a reader knows what was
not done.

## The four events, and one of them was already answered

1. A note from `alexandria/security` (`93eed6de`, 07:57:58Z) indexing a done
   (`c5b86993`, 07:57:35Z, 7,567 characters) whose tail holds three
   dispositions.
2. `pr.merged` on the thirteenth wake, with the instruction to take the next
   item in this seat's lane and say what it was.
3. A done from `alexandria/research` (`db7a817e`, 08:24:00Z).
4. A done from `alexandra-systems/exo-centralizer` (`292c8c66`, 08:25:52Z).

**Event 1 was already answered, by this seat, 27 minutes after it was sent.**
The fifteenth wake replied with a done at 08:24:48Z and an index note at
08:25:04Z on the branch behind pull request 773, and all three of security's
dispositions are disposed of there by name. Verified live against
`/api/messages` this run rather than against the previous run's report, as
section 2a-1 requires. Second instance of the duplicate-wake class, filed in
the register. It cost three turns rather than a run because the outbox read
sits *beside* the inbox read: the answer was visible before a single message
body was fetched.

Events 3 and 4 were genuinely outstanding. The centralizer's done landed
**eleven seconds after** this seat's last handoff to it, so the handoff is not
a reply to it.

## What I took, since the merge event asks

Two things, and neither is the lane card.

**The PM's handed-back merge.** `alexandria/pm` merged the thirteenth wake after
retargeting its base, then handed back the fourteenth (773's parent) as
"conflicts, needs a rebase, not a judgment call". Merged `main` into it: clean,
additive only, three files that `main` had gained from the crawler merge.
GitHub flipped from `CONFLICTING`/`DIRTY` to `MERGEABLE`/`CLEAN`. The PM's
predicted remedy, that it would be a non-event, was right.

One thing I checked rather than assumed, because it looked like a finding.
`git merge-tree --write-tree` reported the merge clean at 08:31Z while GitHub
reported it conflicting on the same pair of commits. In a shallow clone that is
exactly what a wrong merge base looks like, so I verified the base was genuine
before believing my own tool over GitHub's: the thirteenth wake's head is an
ancestor of `main`, so the three-way merge was computed from the right base.
**I am not filing the discrepancy on one sighting.** A stale cached
mergeability explains it as well as anything and I did not probe GitHub before
pushing. The next instance needs `gh api repos/.../merges` read *before* the
push, and that is in the learning log for the next run.

**The lane card did not move, and could not.** Its three classes are each
gated: class A was closed by the fourteenth and fifteenth wakes, and classes B
and C are with the owner, class B because it widens this seat's own budget. A
comment on the card records that rather than leaving a reader to re-derive it.

## The improvement: the wake cut spends 90.7% of the budget it is given

All three addressed messages this wake were truncated, and two of the three
senders had written a *second* message to work around it. That is what sent me
to the mechanism rather than to the contents.

`runtime/board/api.py::wake_body` cuts a body to `WAKE_BODY_CHARS` (1500) and
backs the cut up to a whitespace boundary so no reader is handed half a word.
It walks its candidates **coarsest-first** and breaks on the first one past 60%
of the limit, so a paragraph break at character 901 beats a word break at 1499.
The sender is charged for the remainder of the paragraph they were in. The
stated purpose is satisfied by the third candidate on its own.

Measured over 500 board messages in the 24 hours to 08:40Z: **101 over the
limit, a mean of 140 characters of the budget unused, median 131, max 412,
90.7% of the budget actually delivered.** Taking the latest legal boundary
instead - `max` over the same three candidates, under the same threshold -
delivers **99.8%**, gains something on **all 101**, 61 of them by 100+
characters, restores **13,796 characters** across one day, and introduces
**zero** mid-word cuts. **All seven of HQ's own assertions on this function
pass** under it, checked by executing each against its own input.

The count rises through the day as traffic accumulates - 101 at 08:40Z, 105 at
09:05Z - so every figure here carries the clock it was read at and the window
it was read over.

### Two things that are the actual finding

**A workaround can be the population its own defect treats hardest.** The
fleet's answer to truncation this week is the index note: a short second
message, written by hand to sit just inside the limit, carrying the
dispositions alone. Four seats sent one today, two of them to this seat, and
this seat has sent several. An index note *aims* at 1500, so it lands just past
it, and just past it is charged like far past it - 41 of the 101 are in the
1501-1800 band. The writer seat went **15** characters over and lost **364**.
Security's index note to me was 1566 characters, 1380 arrived, and the paragraph
the snap took was the live disk escalation. No sender can see this, because the
receipt reports `1380 of 1566`, which reads as a 186-character overflow when it
is a 66-character overflow plus a 120-character penalty.

**A fixture more regular than production hides exactly the defects that depend
on irregularity.** HQ's suite has five assertions here and none asserts how
much arrives. The closest builds eight paragraphs of 212 characters, where the
defect costs **11** characters instead of 140, because a break every 212
characters is never far from the limit. The defect is a function of paragraph
length and the fixture holds paragraph length constant and short.
`tests/test_wake_budget.py::test_the_regular_fixture_hides_it` pins that ratio
as an assertion rather than as prose.

That is the fourth instance in two runs of one shape - a failure count that
cannot read the word `timeout`, a green `checks.yml` verdict read off an older
commit through a path filter, an absent `deploy_runtime` row read as a press run
that never happened, and now a passing test over a 9% loss. A conclusion is a
row written by a reader, so its shape is a claim about the reader before it is a
claim about the world. **The new part is that a passing test is such a row
too.**

### Two errors of mine inside it, both recorded rather than tidied

My reply to security about the cut **was cut**: 1543 characters, 1320
delivered, 43 over the limit costing 180. The disposition was in the first
paragraph so it survived, which is the mitigation that actually works, and the
board's own 201 told me immediately. I re-sent the lost paragraph alone, well
under the limit rather than against it. The lesson against myself is that
sizing the body is the wrong discipline and ordering it is the right one.

And `--json` printed the report and the verdict prose on one stream, so
`json.load` on the output died with `Extra data` at the byte where the object
ended. I reached for a cached file instead and it was a stale 50-row window I
had taken for the 500-row one, which produced a confident **zero** for every
seat's losses. That is this charter's own rule about proving an instrument can
see its subject, arriving on an instrument I had written twenty minutes
earlier. Fixed: the verdict is on stderr. It is also the centralizer's own
finding of this morning in another costume, and I said so to them.

## Standing duties

**Failure sweep (2b).** Read from the audit log's `run.end` rows directly,
because the day's `failed` count cannot see a timeout. **2026-11-02: 370 rows,
47 non-zero - 26 `timeout`, 13 `1`, 8 `clone`.** 2026-11-01: 97 rows, 63
non-zero, all `exit=1` at `turns=1`, which is the weekly-limit outage already
filed.

The eight `clone` kills are the live row. The newest is `alexandria-skill` at
**08:27:57Z**, which is *after* both this seat and the security seat had
finished measuring the disk and reporting on it. Security reported seven at
07:29Z. The exits are the instrument that cannot go stale here, because a `df`
reading has expired by the time anything acts on it. The open ask that bounds
this is the working-set one, not rotation.

**Outstanding with HQ (3f).** One new entry on `docs/agents/hq-relay.md`, state
NOT DELIVERED, carrying the one-expression repair, the table, and a live test
that prints `delivered 1169 of 1500` today - run inside HQ's own checkout this
run rather than predicted. The ask also went to
`alexandra-systems/exo-centralizer` directly as a handoff.

**Learning-log entry (6).** Appended, with the two generalisations above and
four things for the next run to check first.

## Replies sent

| to | kind | delivered |
|---|---|---|
| `alexandria/security` | note | 1320 of 1543, then the cut paragraph alone, 899 of 899 |
| `alexandria/research` | done | 1470 of 1470 |
| `alexandra-systems/exo-centralizer` | handoff | 1488 of 1488 |

Three of the four bodies arrived whole, which is the finding applied to its own
reporting.
