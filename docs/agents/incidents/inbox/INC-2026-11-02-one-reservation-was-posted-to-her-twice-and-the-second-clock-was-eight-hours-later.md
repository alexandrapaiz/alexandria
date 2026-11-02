## INC-2026-11-02-one-reservation-was-posted-to-her-twice-and-the-second-clock-was-eight-hours-later - One reservation was posted to her twice and the second clock was eight hours later (2026-11-02, writer seat)

**What happened.** Both open questions in `docs/voice/awaiting-her-word.md` were
posted to the owner as section 22 asks twice in one day. The first pair went out
at 00:32:58Z and 00:33:05Z as `2cfc0df6` and `8eff5507`, on this seat's board
handoff `9574b0d1`, and this seat recorded both ids and their
`deadline 2026-11-04T00:32Z` in the register the same run. The second pair went
out at 08:28Z as `46c63f93` and `cbdb86a5` with `deadline 2026-11-04T08:28:00Z`,
and the PM's note naming them said "I will not re-post these; the clock runs
from the timestamps above", which is only true if the 00:32Z pair
does not exist. All four are live on the bus, read at the source with
`board.py inbox --seat owner`, and none was withdrawn. The two postings are
distinguishable by their `data` fields: the first pair carries
`asked_by: writer handoff` and the `row` it answers, the second carries `source`
and `standard` and no row.

**Why it is in this register.** Two counts, and the second is the repeat.

The duplication itself is the first instance of its class in this register, and
it is filed on the harm rather than the count, because the harm is silent and
arithmetical: section 22's forty-eight hours run from the posting of the
reservation, so recording the newer id as the row's clock moves the row back
eight hours. On rows that have been open fifteen days that is invisible in the
reading and material in the resolution, and a reservation re-posted every eight
hours never resolves at all. Nothing on either side was trying to delay
anything.

The repeat is the pairing. The PM's note names two ids and does not say which id
answers which question, and both new asks reworded the question rather than
quoting it, so this seat had to pair them from each message's `data` field.
That is the **third** time a row in this register was confirmed from the message
rather than from a seat's report of it: the value-statement row needed a
two-source reconstruction on 2026-11-01, run 64 paired the 00:32Z asks the same
way on 2026-11-02, and this is the third. The register already wrote the second
one down as "the second time", which is what made the third one countable.

**What it cost.** Nothing yet, because the register was read before it was
written to. Had this run trusted the note, both clocks would read
2026-11-04T08:28Z and the resolution of two fifteen-day-old reservations would
have slipped eight hours with no record of why. The cost actually paid is one
read of the bus at the source, about four tool calls.

**The fix, or why there is not one yet.** Half shipped, half is not this seat's.

Shipped: `check_voice.py deadlines` has a fourth code, `duplicated`, for a row
naming more than one ask, and it now reads `expired` against the **earliest**
deadline rather than against any of them. The case that earns the code is an
expired earlier clock beside a live later one, where a row read on its newest id
looks live while the reservation has already resolved under the standard.
`DEADLINE_CASES` is 9 of 9 and the gate is red on both live rows, deliberately,
until one ask of each pair is withdrawn.

Not shipped, and owed to the PM seat: withdrawing one of each pair, and whatever
makes that seat's own record of a posted ask survive into its next pass. This
seat can only decline to let the duplicate move its clock. It cannot unpost a
message. Named to that seat on the board in this run's reply.

**The thing worth generalising.** A gate that reads a register for a missing
clock will not notice a surplus one. `deadlines` was written to catch a row with
no ask and a row with an unreadable hour, and both of those are absences. This
is the same register's failure mode inverted, and it was invisible for the same
reason the absences were: the check counted rows that named an ask and never
asked how many asks a row named.
