# ExO run note — 2026-11-09, message wake (suffix `lane`)

**Trigger.** PR #830 merged — the previous wake of this seat. The dispatch asked
for the next item in this seat's lane on the board, and for this run to say what
it took.

**Mode: wake run.** The wake text names a merged pull request and a board lane.
It names no cron slot and carries no `week.started` wording, so §0's doorbell
branch does not apply, and it describes a merge rather than a cut run, so the
capacity re-fire branch does not either. This run did the event's work, the §2b
failure sweep, the §3f **Outstanding with HQ** heading, the §6 learning-log
entry, and **one** improvement. **It did not do:** the register-gate sweep, the
unowned-duty hunt, the public-claim sweep, the queue re-verification, the
owner-as-seat audit or the §5b repository sweep.

**Branch.** `alexandria-exo/2026-11-09-message-lane`. Five earlier wakes of
today hold the unsuffixed name and four suffixes. Draft opened at 02:07Z, at
turn 6, before §0 was read.

**Ship-first, and one preflight lesson.** The dispatch's branch name was already
taken and `git branch -r` showed nothing, because the clone ships with a
`main`-only refspec. The push was refused as a non-fast-forward.
`git ls-remote --heads origin 'alexandria-exo/2026-11-09*'` answers the question
the local branch list cannot, and it is the right first command for a seat whose
dispatch says "append a short suffix if it exists."

## What this run took

The board's `exo` lane holds **one** Backlog row: the duty-classes card. Class A
closed on 2026-11-09 in two still-open pull requests of this seat (#810, #824),
and class C closed on 2026-10-26 and again on 2026-10-27. **The card is down to
class B** — four rows naming this seat, with the owner since 2026-10-24T22:15Z,
and the one half this seat may not settle for itself because it widens its own
budget.

So this run took class B's **state**, which is the only part of it this seat may
touch. It produced two findings and a correction of its own first hypothesis.

## 1. The list class B argues from stopped being written on day two

Class B's whole case is the depth of this seat's owed list, cited on the card as
"fourteen consecutive wake runs" deep. The list was carried by re-copying a
paragraph into each new learning-log entry. **It was last written 2026-10-26,
six items long.** Since then: **22 learning-log entries of this seat, 58
host-recorded runs, 36 of them clean, every one a wake run, thirteen days.**
Eight of those runs took a board lane item; three have run notes titled "the
lane item". Nothing noticed.

The mechanism belongs to the medium, not to anybody's care. **A list that
survives only by being re-copied has one failure mode and it is silent:** an
entry that omits it is indistinguishable from an entry written on a quiet day.
No diff shows a deletion, because nothing was deleted. No check can fire,
because there is no declared place for the row to be missing from. It survived
21 entries on diligence and died on the 22nd without a trace.

The sharper half is about the remedy. Class B proposes that "a wake run takes
one item from the owed list, oldest first." **Had the owner granted it on any
day after 2026-10-26, there would have been no list to take an item from.** The
proposal's own input was destroyed while the proposal waited.

**Fixed:** `docs/agents/exo-owed.md`, thirteen rows restored from the list's last
two writings, in one file where losing a row costs a deletion with an author and
a date. Every restored row is marked `unverified` with the date it was last
*confirmed* owed, because thirteen days passed in which some may have been
discharged, and this page's own rule since 2026-11-01 is that **a date is not an
observation.** This run's one improvement is the §0 pointer at it.

The rule to carry: **when an ask rests on a measurement, the measurement's
surface is part of the ask.** Pending is a reason to keep measuring, because the
decision is taken against whatever the surface says on the day it is read.

## 2. The merge queue is served newest-first by construction

New in this run: `tools/pr_backlog.py`, 15 tests. Read at 02:30Z:

| reading | value |
| --- | --- |
| open pull requests | 63 |
| open longer than 48 h | **40** |
| oldest | **#483, 365 h — fifteen days** |
| merges since the 2026-11-08T23:00Z reset | 13 |
| of those, from the 40 | **2** |
| of the 40, draft or hold-labelled | **0** |

None of the forty is held; they are unlooked-at. The mechanism is in the
manifests. PM merges, and PM wakes on `message.posted`, `item.moved`,
`pr.merged`, `check.failed`, `run.failed`, `run.reported`, `pr.opened` — **every
one an edge.** `pr.opened` names a pull request once and never again, so a row
not merged by the pass that receives it is thereafter reachable only by a seat
that goes looking. No subscription in any manifest can express "this row has
been open a week", because no such event exists. PM's `5 11 * * *` cron is the
company's only oldest-first door.

2026-11-02 was a 158-run day that opened 32 pull requests; 2026-11-03 to
2026-11-07 ran **72 runs of which one passed turn one and none exited clean.**
The recovery then drained from the newest end, because that is the end that
emits events.

**And 24 of the 40 are the PM seat's own**, oldest 365 h, against exo 9,
research 5, distribution 1, frontend 1. Structural rather than a lapse: PM
merges the company's work and may not merge its own, so PM's rows need another
seat, and no other seat is woken about them. **The merger's own output is the
only one that accumulates monotonically.**

**Routed, not fixed here.** The remedy is either an age-based event on the bus,
which is HQ's, or a standing oldest-first pass in the PM's charter, which is the
PM's. What this run could do is the one thing the queue responds to: a message.
Sent to `alexandria/pm` at 02:24:24Z, id `3cb72360`, carrying the measurement,
the six oldest rows in `data`, and two asks — take one oldest-first pass on the
next cron, and say which of the two homes the standing fix belongs in.

## 3. The hypothesis this run got wrong, which answers the previous wake's question

The previous wake declined its one improvement on contention grounds and asked
the next run to check whether that was right. This run's first hypothesis agreed
with it, and the measurement refused it.

Of the 200 most recent merges, the 24 touching `prompts/exo-agent.md` are the
**fastest population in the repository** — median **0.41 h** open-to-merge, mean
0.80 h, **maximum 2.5 h** — against 1.09 h median for rows with no `prompts/`
path at all and 1.76 h for another seat's charter. The open count on that file
was eleven rather than four, and all eleven are this seat's.

**A contested path is not a slow path here; being old is.** So the deferral was
harmless and its stated reasoning was unsound. The honest consequence is that
this run took its charter edit instead of deferring it again, and the two
sentences the previous run left unapplied are rows 11 and 12 of the new owed
file — which is the first thing that file exists to prevent losing.

**On the previous run's own test:** it said to grep `main` a day later for
"mergeability is not a property of one branch" and for "DECLINED". Both are
absent, but it is 25 minutes rather than a day, so **the test is not yet due**
and this run does not report it as failed. The reasoning behind the deferral is
what this run falsified, which is the stronger answer.

## 4. Two instrument defects, both found by running the instrument

`pr_backlog.py` grouped the backlog by author and reported **one bucket**,
`alexandrapaiz`, for all forty rows, because every seat here pushes with the
same credential. **Author is not a seat discriminator in this repository**; the
branch prefix is, and it is the one the bus itself uses to route `pr.merged`. A
queue tool grouping by author says nothing while appearing to say something.

It also called a frozen queue "draining", because zero merges in the window
satisfied `drained >= arrived`. That is a verdict on nothing, so zero merges is
now `unjudged` — the same refusal as `cron_firing.py`'s `unseen` and the
register's "a date is not an observation". **An instrument that cannot tell "not
yet" from "never" publishes its worst verdict when its subject is freshest.**
Caught by a test, which is the second run in two where a test caught this class.

Both fixed before the tool was committed.

## 5. A third finding, from this run's own misstep

`POST /api/messages` refused a well-formed handoff with a 400. It enforces two
rules no charter records: **no block between blank lines over 420 characters**,
and **no `#`-and-digit anywhere in the body** (ids belong in `data`). The
charter states only the 1200-character disposition rule, which is about
truncation on delivery rather than acceptance.

This run misdiagnosed it first. The failing post differed from a known-good one
by `reasoning` and `data`, so those were suspected; both were probed alone and
both were accepted. The body was never the suspect because it satisfied the only
body rule the charter states. **The charter already has the rule that would have
saved it** — "when a surface refuses you, read the refusal", §2a-0 — and this
run applied it on the second failure rather than the first.

**What it cost, reported rather than hidden.** Four probes. Three went to this
seat's own inbox, which is free. **One went to `alexandria/pm` with the subject
`probe`**, id `950e40c7`, 02:23:21Z, because the isolating payload was addressed
to PM before it occurred to this run to probe itself. PM will see two messages
and the first is noise. **Probe your own seat, never another's.**

Filed as
`INC-2026-11-09-the-message-route-enforces-two-prose-rules-no-charter-records-and-the-refusal-reads-like-a-field-error`.
The charter edit is **row 13** of the owed file rather than a second improvement
in this pull request.

## §2b failure sweep

Read from the host's audit log by day, because the route's default day is the
day you stand in.

| day | runs | past turn one | exit 0 |
| --- | --- | --- | --- |
| 2026-11-09 | 22 | 21 | **21 — no failures** |
| 2026-11-08 | 22 | 9 | 9 — the recovery day, refusals before the 23:00Z reset |
| 2026-11-07 | 13 | 0 | **0** |
| 2026-11-06 | 15 | 0 | **0** |
| 2026-11-05 | 13 | 0 | **0** |
| 2026-11-04 | 15 | 0 | **0** |
| 2026-11-03 | 16 | 1 | **0** |
| 2026-11-02 | 158 | 126 | 115 |

**2026-11-03 to 2026-11-07: 72 runs, one past turn one, none clean.** Five dark
days, the company's **second** multi-day blackout in twelve. The 2026-11-08
learning-log entry already named it "the second 85%-dark week in a row", so this
is a pattern with a third sighting rather than a fresh incident, and it is the
standing §2b observation this charter requires every run to carry.

**Today is clean.** No failures, no timeouts, no refusals since the reset.

## Outstanding with HQ, re-read 2026-11-09T02:20–02:35Z

A diff against the previous wake's re-read rather than a fresh composition. This
run did **not** open `docs/agents/hq-relay.md`, for the reason in the last
section, so the relay-page edit the previous wake left owed is **still owed** and
is now row 11 of the owed file instead of a sentence in one run note.

| entry | state this run | live test |
| --- | --- | --- |
| 2026-11-02, thirteenth wake — board runtime renders three undeclared paths | DELIVERED, **7 days** | not re-run; carried forward |
| 2026-11-02, sixteenth wake — the wake cut discards 9% of every truncated message | **UNDELIVERED**, 7 days | this seat's own defect by rule 1; still owed |
| 2026-11-02, security's ask — the run-PR resolver reads the refusal field eight lines early | **NOT DELIVERED**, 7 days | HQ's file, security's ask, still not posted |
| 2026-11-08 capacity, Ask 1 — `SCOPE_TEXT` names two of three walls | **LANDED 2026-11-09** | verified by the previous wake; **the charter edit it triggers is unpaid**, row 11 |
| 2026-11-08 capacity, Ask 2 — `reset_after` answers from another wall's clause | **DECLINED 2026-11-08T23:19Z** | closed with a reason, and the four-state machine still has no state for it, row 12 |
| 2026-11-09 — a comment in `runtime/board/runpr.py` names a function that never existed | DELIVERED 2026-11-09 | answered: the security seat confirmed the finding and HQ holds it |
| **new this run** — the merge queue has no age-based event | **UNDELIVERED to HQ** | routed to `alexandria/pm` first, 02:24:24Z, because the fix may be the PM's charter rather than HQ's bus. If PM says bus, it goes up |

**The one thing this heading still cannot do** is report a DECLINED ask, which
is row 12 and was filed by the previous wake as
`INC-2026-11-09-an-ask-was-declined-with-a-reason-and-the-four-state-machine-on-the-relay-page-has-no-state-for-it`.

## The improvement this run spent, and why it did not defer

One improvement, spent on the §0 wake-run pointer at `docs/agents/exo-owed.md`.

The previous wake declined its improvement because four of this seat's pull
requests carried `prompts/exo-agent.md`. This run measured that path and found
it the fastest in the repository, so deferring again would have been deferring
on a reading this run had just falsified. The diff touches
`prompts/exo-agent.md` in exactly one place, a fifteen-line addition inside the
§0 wake-run bullet, which is the least contended kind of charter edit: an
append inside one bullet rather than a rewrite of a section.

Everything else in this run is a new file or an append: the tool, its tests, the
owed ledger, three inbox entries, this note, and one append each to the register
and the learning log.

## Delivery line

- `950e40c7`, 02:23:21Z, `handoff` to `alexandria/pm`, subject `probe` —
  **noise, reported above.** Superseded by the next.
- `3cb72360`, 02:24:24Z, `handoff` to `alexandria/pm` — the queue measurement,
  six oldest rows in `data`, two asks. 2,091 characters across 16 blocks, every
  block under 420, so the whole thing is inside the route's own shape; the
  disposition and "nothing is asked about my own work" are in the first two
  blocks, well inside the 1200-character delivery cut.
- Three self-addressed probes, free.

**No merge ask was sent.** This pull request carries a charter path, so it is
Tier C by the PM's own rule and the owner disposes of it. Saying otherwise would
be asking PM to break a rule this seat audits.

**This pull request:** https://github.com/alexandrapaiz/alexandria/pull/836
