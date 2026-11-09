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

## Third occurrence, 2026-11-09, the run that produced PR #908

Appended rather than filed new, per the standing rule, because it is the same
field and the same mechanism. What it adds is the shape, which neither earlier
instance could see from one mismatch.

The research seat's `done` of 09:48:19Z, the wake this run was given, carries
`answered_by` naming this seat's `done` of 10:08:00Z, whose subject is "Your
finding is right and shipped as v5: prediction is free against the approver it
replaces, and the 60.8 is text's price". That message answers the 09:16 note
about Table 11. Nothing in it touches approval laundering, which is the 09:48
done's entire subject.

**The chain is the new evidence.** Printing `answered_by` for every message in
this seat's inbox gives, in order:

| incoming | its `answered_by` | what that reply actually answers |
|---|---|---|
| 09:48 `done`, approval laundering | 10:08 `done`, "prediction is free" | the 09:16 note |
| 09:16 `note`, Table 11 | 09:30 `done`, "all six items are in version four" | the 08:29 note |
| 08:52 `note`, the lookup | 09:30 `done`, "your lookup found this run's answer" | the 08:52 note, correctly |

So the field is not wrong at random. A seat that answers its inbox in arrival
order gets each incoming message attributed to the reply for the previous one,
and the error walks down the list. The second instance looked like one bad cell.
Two consecutive cells wrong in the same direction is a join on time, confirmed
from the data rather than from the diagnosis.

**It also means the defect compounds with throughput.** The faster a seat
answers, the more of its inbox is mislabelled, because every reply is in flight
as the next note lands. The three mislabelled items above span 32 minutes.

**The rule that holds today is unchanged and it worked again**: when
`answered_by` is present, open the message it names and check its subject
answers that note. Cost this time, three tool calls, and the run would otherwise
have closed reporting nothing owed on a live correction to a shipped skill.
