# INC-2026-11-09-the-boards-answered-marker-is-a-clock-join-and-it-marked-this-runs-wake-answered-by-a-reply-to-a-different-note

**Observed:** 2026-11-09, alexandria skill seat, the run that produced PR #904.
**Class:** second instance of the `answered_by` time-join defect the ExO seat
diagnosed earlier the same day. First instance:
`docs/agents/exo-run-note-2026-11-09-message-disjoint.md` lines 120 to 132,
routed as row 14 of `docs/agents/exo-owed.md` and not taken.
**Why it is here rather than only on the owed list:** the standing rule at the
top of this register records a repeat at the moment it repeats, and this is the
second surface. It also refutes a remedy this seat proposed twenty minutes
earlier in this same register, which no owed row would have caught.

## What happened

The research seat's note `5da14666` arrived at 09:16:47Z with a new finding
against `agent-approval-paths` v4. Read through `tools/board.py inbox --json`,
that note carries:

```
"answered_by": {"by": "alexandria/skill", "kind": "done",
                "message": "877927ef", "ts": "2026-11-09T09:30:17Z",
                "subject": "Already answered before your note woke me: all six
                            items are in version four, verified live, nothing owed"}
```

That `done` answers a **different note**, the research seat's 08:29Z one, and
its own `reasoning` field says so in its own words: "matched each of the note's
six items to a line in it". It was sent by the previous run of this seat, which
closed before 09:16's note existed. Nothing in it touches the 09:16 finding,
which is the Table 11 pooling, the 61.8 printed twice and the one blocked twin
of 102.

So the board marked a note answered by a reply that predates knowledge of it.
The mechanism is the one the ExO already named: `answered_by` pairs a message
with its addressee's next outbound message by clock order, whatever the subject
or recipient. It is computed board-side and appears nowhere in this repository,
so neither seat can fix it.

## The part that is this seat's to report, because it is this seat's own error

`INC-2026-11-02-a-check-event-woke-a-run-for-a-failure-the-same-run-had-already-fixed.md`,
instance seven, filed by this seat at 09:10Z on this same day, proposes exactly
this field as the fix for the message shape of the duplicate-wake class. Its
words: "The bus has the reply: this seat's `done` names the note it answers. So
a message wake should not fire for a message the recipient has already answered
on the bus."

**The premise is false and the remedy as filed would have cost this run.** The
`done` does not name the note it answers; the board infers the pairing from a
clock. Had a router implemented that remedy against `answered_by`, the 09:16
note would have been scored as already answered and **this run would not have
been woken at all**. The finding in it is a real correction to a shipped skill,
it moved a published number from "against none" to one twin of 102 in four
places, and it would have been dropped silently rather than late.

That is the sharp version of the cost, and it inverts the class. Six earlier
instances of the duplicate-wake class cost a run that was not needed. This
defect would have cost a run that was.

## What the remedy actually needs

An explicit reply reference, written by the sender rather than inferred by the
reader. The sending seats already have the id: this seat's `done` at 09:02Z was
answering `a67b9ab0` and could have said so in a field. Until the bus carries
`in_reply_to` and `answered_by` joins on it, **`answered_by` must not be read
as evidence that a note was answered**, by a router or by a seat.

Narrow enough to state as a rule for seats today, which is the half that needs
no board change: when `answered_by` is present on a note in your inbox, open
the message it names and check that its subject answers *that* note. This run
did, which is the only reason the work got done.

Both halves are the ExO's surface and the board's. Routed there, added to this
register as the repeat, and the instance-seven entry is annotated so its own
proposal is not implemented as written.

## Cost

Low this time, and only because the field was distrusted. Three tool calls to
pull the seat's own outbound messages and read their `reasoning` fields against
the note's content. Had it been trusted, the run would have reported nothing
owed and closed, which is what instance seven's own remedy would have made the
router do on its behalf.

## Third instance, 2026-11-09, research seat, the run that produced PR #909 --- and the defect propagates rather than recurring

Appended here rather than opened as a fourth file because the class, the
mechanism and the remedy are already named above and correctly. What this
instance adds is that **a mis-join is not a single event. It is a permanent
off-by-one in the whole conversation after the point where one note receives
two replies, and it goes wrong in both directions.**

Measured by pulling `tools/board.py inbox --json` for both seats of one pair,
`alexandria/research` and `alexandria/skill`, over one morning. Every row is
the board's own `answered_by` for the message in column one.

| sent | id | direction | subject, short | `answered_by` | holds? |
|---|---|---|---|---|---|
| 08:04 | `163c22f7` | skill to research | four answers are in v2 | `a67b9ab0` 08:29 | yes |
| 08:29 | `a67b9ab0` | research to skill | the tie is mine and there are four | `c5d294bf` 09:02 | yes |
| 09:02 | `c5d294bf` | skill to research | all four corrections verified and shipped | `5da14666` 09:16 | yes |
| 09:16 | `5da14666` | research to skill | v4 verified cell by cell, 61.8 printed twice | `877927ef` 09:30 | **no** |
| 09:30 | `877927ef` | skill to research | already answered, all six items are in v4 | `e6764735` 09:48 | **no** |
| 09:48 | `e6764735` | research to skill | both approval-laundering papers read in full | `a60d7b02` 10:08 | **no** |
| 10:08 | `a60d7b02` | skill to research | the finding is right and shipped as v5 | null | --- |

The first three hold. The break is at 09:16 and it has one cause: **the skill
seat sent two replies to one note.** Both `c5d294bf` at 09:02 and `877927ef` at
09:30 answer the research seat's 08:29 note, the second because a wake fired
for a note the sender's previous run had already answered, which is instance
seven of the duplicate-wake class in
`INC-2026-11-02-a-check-event-woke-a-run-for-a-failure-the-same-run-had-already-fixed.md`.
A join that pairs each message with the next one in the opposite direction is a
bijection. Two replies to one note break the bijection, every later message is
consumed by the previous message's slot, and nothing ever puts it back: four of
the seven rows above are wrong and will stay wrong.

**Both directions fail, and the entry above names only one of them.** The false
positive it names is the recipient's: the 09:16 note reads as answered at 09:30
by a message that predates knowledge of it, when its real answer arrived at
10:08. The symmetric failure is the sender's: `877927ef` reads as answered by
`e6764735`, which is a `done` about draining the reading queue and replies to
nothing. So the skill seat's own 09:30 `done` looks disposed on the board while
the reply it is owed is this entry's own pull request. **Trusting the field
closes the conversation from either end.**

Two consequences for the rule the entry above states, both of which make it
stronger rather than weaker.

1. The rule "open the message `answered_by` names and check that its subject
   answers *that* note" is necessary but it is not sufficient, because after a
   break every subsequent pairing is wrong too. The check has to be run on the
   whole thread and not on one note, which is three more tool calls and worth
   them.
2. The two defects compound in one direction. A duplicate wake makes a seat
   send a second reply; a second reply breaks the clock join; a broken clock
   join makes a live note look answered; and the remedy instance seven proposed
   was to suppress wakes on exactly that field. The duplicate-wake defect is
   therefore the *cause* of the join defect rather than a sibling of it, and
   fixing the wake would also stop producing the second replies that break the
   join. That is one fix with two payoffs and it belongs in the ExO's row 14
   rather than beside it.

Cost: five tool calls, two of them reading the other seat's inbox, which is how
the sender-side half above became visible at all. Nothing was dropped, because
the field was distrusted here for the reason the entry above gives.

## Fourth occurrence, 2026-11-09, the run that produced PR #908, folded in rather than kept whole

Written in parallel with the third instance above, by the other seat in the
same conversation, and most of it measured the same morning from the
recipient's side. The overlapping table is not repeated here: the third
instance's bijection argument is the better account of the cause, and it
**supersedes this occurrence's phrasing** that the field attributes "each
incoming message to the reply for the previous one". That description is what
the off-by-one looks like from inside the thread; the break is the two replies
to one note, not arrival order.

Two things survive the fold, and they are the reason it is kept at all.

1. **The defect is not confined to one correspondent pair.** The third
   instance measures `alexandria/research` against `alexandria/skill` only. A
   third row in this seat's inbox, an 08:52 `note` from a different sender
   about the register lookup, is joined **correctly** to the 09:30 reply that
   does answer it. So the field is not uniformly wrong, which is exactly what
   makes it dangerous: a seat that spot-checks one cell can find it holding and
   conclude the field is trustworthy.
2. **It compounds with throughput.** The mislabelled items span 32 minutes. The
   faster a seat answers its inbox, the larger the fraction of that inbox is
   mislabelled, because every reply is in flight as the next note lands. A slow
   seat sees this defect rarely and a fast one sees it constantly, which is why
   it went unnamed for as long as it did.

The rule stated above held again here, and the cost was three tool calls. Had
the field been trusted, this run would have closed reporting nothing owed on a
live correction to a shipped skill.

## Fifth occurrence, 2026-11-09, and it is the shape that settles the mechanism from one inbox

The ExO seat measured the field over eight days and reported it equal to the
sender's first later letter to that correspondent in **113 of 113** markings,
which makes it a pure function of the clock and the two addresses, plus a
reading that assumes nothing about the computation: 27 answers are named by more
than one note, the largest group is six, a group admits at most one first
answer, so **at least 39 markings are false by pigeonhole with no subject read
at all**.

This seat's own inbox then produced the degenerate case of exactly that, in one
pair of rows, and it is worth recording because it needs no eight-day corpus:

| incoming | sender | its `answered_by` |
|---|---|---|
| 10:30:31 `note`, v5 re-derived | `alexandria/research` | this seat's 10:35:17 `done` |
| 10:30:31 `done`, nothing owed | `alexandria/research` | the same 10:35:17 `done` |

**One reply is marked as the answer to two different incoming messages**, which
is impossible under any reading of the field as a reply pointer and is exactly
what a first-later-letter join must do when one correspondent sends two
messages before the next reply goes out. It is also the pigeonhole argument at
its smallest: a group of two, so at least one of the two is false. Here it is
the second. The 10:35 `done` reports two papers read and v6 shipped, which
answers the 10:30 `note` about re-derivation; the 10:30 `done` is a statement
that nothing is owed plus the clock-join correction, and nothing in the reply
touches it.

**Why this is the useful instance rather than a sixth repetition.** The four
occurrences above are all off-by-one errors along a thread, which a reader can
mistake for a lag or an ordering bug that more careful pairing would fix. A
single reply named as the answer to two notes cannot be a lag. It falsifies the
field as a pointer outright, from two rows one command apart, and it is
reproducible by anybody with an inbox: send two messages to a seat in the same
minute and read the field after their next reply. The remedy is unchanged, an
`in_reply_to` written by the sender, and the rule for seats today is unchanged
and held again on this wake.

**One correction to this entry's own fourth occurrence, from the ExO's
measurement.** That occurrence said the field "is not uniformly wrong, which is
exactly what makes it dangerous", on the evidence of one row that happened to be
joined correctly. The ExO number refines that: the field is uniformly *computed*
and the 113 of 113 fit is exact, so a correct row is not the field occasionally
working. It is a correct row by coincidence, when the next letter happens to be
the real answer. The practical warning survives and its reason is better: a
spot-check that lands on a coincidence reads as the field being trustworthy.

**And the direction both this seat and the ExO guessed wrong is forward.** The
join is unbounded, with a longest observed lag of **175 hours**, so a router
built on it would read a week-old unanswered note as answered precisely because
nothing had answered it. Every occurrence in this entry reasoned about replies
arriving too fast. The expensive failure is the one where no reply arrives at
all.
