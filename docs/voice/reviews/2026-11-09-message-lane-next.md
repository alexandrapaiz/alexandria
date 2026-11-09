# Writer run 69, 2026-11-09 (message wake, next lane item)

**The single biggest thing this run found: the gate this seat built to catch a
reservation going stale had been scoped to the one table where every row was
already answered, so it printed green over thirteen copy candidates nobody has
ruled on, the oldest forty-four days old and four of them serving a sentence
another gate calls false in the same minute.**

`deadlines` has a finding named `unasked`, whose printed advice is that a row
"is owed an ask from the PM and has never had one". It could not reach a single
row that was actually in that state, because the premise excusing the other
table was written into its own source and the premise was false.

## What woke it, and what this run took

PR #831 merged and is `889aa17e`, the tip of `main`. The event said to continue
with the next item in the writer lane.

The lane has nine cards and every one of them is in Review, which is to say
they are shipped pull requests waiting on a merge rather than work waiting on
this seat. Nothing sits in This Sprint or Backlog under `writer`. So there is no
queued card to take, and this run says that plainly rather than picking a
Review card and pretending it was open.

The one inbox message, `31f301e6` from the PM, refers to #816 and was discharged
by #831. Nothing was owed there.

What this run took instead is the charter's own standing work, and the register
it is required to read first is where the finding was.

## No grade, and the reason is a fact about the press rather than a quiet day

The newest edition is `2026-W44`, recorded 2026-11-02T09:00:05Z. #804, #812,
#816 and run 68 have each already graded it, on a generator that has not changed
since 2026-10-15. `press` reports the deployed commit `f16e2775` carrying
`prompts/digest.md` as of `9b6410ea`, 25.4 days old, with 30 merged commits to
the generator queued behind the deploy.

A fifth scoring of one edition inside eight days produces the same verdicts in
new sentences and is the thing step 3 was amended to stop. `editions` adds the
other half: three of the four served editions are not files in this repository,
so the artifact cannot be read cold here at all without the live fetch.

**So no prompt diff, and the ask is the deploy.** Thirty commits of generator
work are written and undelivered. Nothing this run could add to that file would
reach a reader sooner than the thirty already waiting.

## The register the charter reads first, and what was in it

`docs/voice/awaiting-her-word.md` holds two tables. The lower one is questions
for the owner. §22 of the company standard gave it a clock in 2026-10-26, and
`deadlines` reads it. That table is empty today, because run 67 resolved both
rows on their clocks, so the gate reports zero rows and no failures and exits 0.

The upper table is copy candidates. Thirteen rows, eleven surfaces, drafted
between 2026-09-26 and 2026-11-01. Not one of them carries an ask, a readable
deadline or a handoff id. The oldest is `site/app/page.jsx:44` at forty-four
days.

Read against the other gates in the same run, those rows are not paperwork:

| gate | what it says about the open table |
| --- | --- |
| `reading` | red on four of the surfaces, four lines giving the arriving count a verb of reading |
| `claims` | `site/app/mission/page.jsx:29` carries a `contradicted` claim, unhedged at 100% of the claim's words |
| `taste` | verdict 6, never "read" for ingested, is not held, because the rule enforcing it is red |

`QUESTIONS`'s own note carried the premise: a deadline only lands in the lower
table, because "the surface rows above it wait on a seat's diff and nothing
about them expires". The second clause is the load-bearing one and the register
refutes it four hundred lines up in its own words. A row leaves the open table
when she rules or when the frontend seat sets it, and that seat sets APPROVED
copy. A candidate she has never ruled on is not waiting on anybody's diff.

And the register had been saying so in plain words for fourteen days. Its
closing section read "Nothing fires when a row here goes stale", which is not a
warning but the fact, sitting two screens under the gate that would have had to
read it.

## The refusal, which is the part of this run worth arguing with

The obvious repair is to post all thirteen as §22 asks. The first version of the
widened gate told its reader to do exactly that, in six printed lines. It is
wrong, and it is written down here because the advice reads as diligence.

§22's ask proceeds as recommended after forty-eight hours of her silence.
Applied here it sets thirteen lines of copy she never ruled on, on the
recommendation of the seat whose last eight unsupervised rounds she rejected one
after another. `docs/agents/copy-pipeline.md` phase 1 step 2 reserves the ruling
to her in words that leave nothing to interpret, "Her verdict is the only
verdict. This step is hers and it does not move", and incident 25 is the
evidence under it rather than a preference.

`docs/agents/cross-repo-law.md` rule 3 is what settles it: a local law's
preconditions survive a parent override unless the override names them. §22
decided that reservations get clocks. It never named the copy pipeline's clause
and nothing suggests it meant to.

**So the open table gets an age and not a deadline.** That is incident 23's
class read correctly for once, rather than a parent standard eating a local
safety clause by silence.

## What shipped

`deadlines` reads both tables. `drafted_rows` keeps the open rows whole where
`open_rows` keyed them by surface, because the question here is how long a row
has waited rather than whether a surface was written for. `row_age` reads the
drafted cell. One line per row and the standing reason once, because the first
draft printed three lines of identical explanation under each of thirteen rows
and buried the only thing that differs, which is the age.

Two codes, and the split is about which seat owes the next move. `unshown` is a
row with no trail at all and it is this seat's failure. `routed` is a row handed
over, and scoring that as a failure of the run that already did its part trains
the next run to ignore the gate.

The code is `unshown` and not `unasked` on purpose. The word `unasked` is what
produced the six lines of wrong advice, because it points at the one mechanism
that must not be used here.

**And the fix shipped a false green of its own, which is recorded rather than
tidied away.** Renaming the code left the reporting half filtering on the old
string. Both lists went empty, the gate printed "every open candidate carries an
ask" over thirteen that carry nothing, and it exited 0. A case over
`open_findings` could not catch it, because `open_findings` was right. The
defect was one vocabulary held under two names in two functions.

`code_vocabulary` is the repair. It reads `deadlines`' own source for the
strings it matches against a code and fails where those and `OPEN_CODES`
disagree in either direction. Negative-tested by reintroducing the rename, which
it caught with both halves named.

## What was routed, and to whom

Board handoff `1bc20f1b` to the PM. It names the thirteen rows, the ages, the
four surfaces serving false lines, and it asks for one route to her attention as
a reading rather than a reservation. It asks explicitly NOT for a §22 clock and
gives the two laws for that.

Each of the thirteen rows now carries that handoff id, so the gate reads them as
owed rather than as never shown, and the trail is in the register rather than
only in a pull request body that nothing sweeps.

The ledger entry is the structural half, under step 4. The finding there is not
the instrument, which is fixed. It is that the copy pipeline's second step has
no terminating condition: every candidate needs the same scarce input and the
pipeline requests it one surface at a time, so eleven surfaces queue behind one
server with no batching and no answer for a candidate she has not looked at. Its
first step costs one read and could cut eleven to seven, by asking whether
pulling a sentence a gate calls FALSE needs her taste at all or only her
permission to leave a gap.

## Three drifting counts, found while annotating

Three cells carried durations measured on the day they were written and never
since. One said the row was twenty-two days old on a row that was forty-four.
Each is anchored to its measurement date now, and the metric-line row says
plainly that the age is the gate's to print rather than the cell's.

## Checks

`deadlines` 9/9, 5/5, 4/4 and 1/1 with the open table read, exit 0 once the
thirteen rows carry their handoff and exit 1 before it. `tests/test_voice_enforcements.py`
4 passed. `enforcements`, `doubles`, `dispatch` and `flags` all exit 0.
`candidates` and `routed` both clean against this run's own diff, with the
review file read as a record rather than a candidate. `ledger.py --check` 0
blocking and 71 warnings, at the recorded baseline. `tools/incidents.py check`
375 entries, nothing malformed. All thirteen open rows still render as six-cell
table rows after annotation.

`exits` reports one CANNOT on `tools/noship.py`. Checked against a worktree at
`origin/main` and it is there too, so it is not this run's.

`selfcheck` caught a semicolon in this run's own first commit, in the stub of
this file. Struck rather than excused.

No conflict markers in `docs/`, `prompts/` or `README.md`. Every scratch path in
this run came from `mktemp -d`, which is step 0b.

One repeat filed:
`INC-2026-11-09-the-gate-for-stale-reservations-could-not-see-the-table-that-holds-them`.
It is the third instance of a gate in this instrument answering a question it
cannot see and the second in two days, run 68's law 8 entry being the first.

This pull request changes no seat's authority and spends no money, so it does
not wait on the owner.
