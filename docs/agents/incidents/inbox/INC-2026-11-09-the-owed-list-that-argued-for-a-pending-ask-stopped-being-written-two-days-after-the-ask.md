## INC-2026-11-09-the-owed-list-that-argued-for-a-pending-ask-stopped-being-written-two-days-after-the-ask - a proposal waiting on a decision had its own evidence destroyed while it waited (2026-11-09, exo seat, message wake)

**What happened.** The duty-classes card's class B has been with the owner since
2026-10-24T22:15Z, sixteen days, asking that a wake run of this seat be allowed
to take one owed sweep per wake in addition to its one improvement. The card's
entire case is the depth of the owed list, which it cited as "fourteen
consecutive wake runs" deep. That list was carried by re-copying a paragraph
into each new entry of `docs/agents/learning-log.md`. It was last written on
**2026-10-26**, six items long. It has not been written since.

**The measurement.** From the last entry that carried it to this run:

| reading | value |
| --- | --- |
| learning-log entries of this seat after the last writing | **22** |
| host-recorded runs of this seat in the same span | **58** |
| of those, `exit=0` | 36 |
| of those, cron runs | **0** — all 58 were wake runs |
| days | 13 |
| the list's length when last written | 6 items, one of which was class B itself |

So the ask has sat with the owner for sixteen days while the number it is
arguing from was frozen on day two, and frozen in the direction that weakens
it: the real depth grew, and the page the owner would check to verify the claim
is silent.

**The sharper half, which is about the remedy and not the evidence.** Class B's
proposed remedy is "a wake run takes **one** item from the owed list, oldest
first". Had the owner granted it on any day after 2026-10-26, a run reading the
charter would have found no list to take an item from. **The proposal's own
input had been destroyed while the proposal waited.** A granted ask would have
produced a run looking for a surface that no longer existed, which is the exact
shape of
`INC-2026-10-24-the-receipt-we-asked-for-was-built-and-no-charter-was-pointed-at-it`
with the two halves reversed: there, a surface was built and no charter pointed
at it; here, a charter pointed at a surface that quietly stopped being written.

**The mechanism, which is the part worth keeping.** An append-only log is the
wrong home for standing state, for a reason that belongs to the medium rather
than to anybody's care. A list that survives only by being re-copied has exactly
one failure mode and it is silent: **an entry that omits the list is
indistinguishable from an entry written on a day when nothing was owed.** No
diff shows a deletion, because nothing was deleted. No check can fire, because
there is no declared place for the row to be missing from. The list survived 21
entries on diligence and died on the 22nd leaving no trace. Nothing noticed for
thirteen days, including eight runs of this seat that took a board lane item and
three whose run notes are titled "the lane item".

In a file with one row per item, the same loss is a deletion with an author, a
commit and a date.

**Fixed in this run.** `docs/agents/exo-owed.md` holds the twelve rows,
restored from the list's last two writings, each marked `unverified` with the
date it was last confirmed rather than asserted as owed today — because thirteen
days passed in which some may have been discharged, and a date is not an
observation. §0's wake-run bullet now points at the file.

**The general rule this register should carry.** When an ask is posted whose
case rests on a measurement, the measurement's surface is part of the ask. An
ask that is pending is a reason to keep measuring, not a reason to stop: the
decision will be taken against whatever the surface says on the day it is read.
