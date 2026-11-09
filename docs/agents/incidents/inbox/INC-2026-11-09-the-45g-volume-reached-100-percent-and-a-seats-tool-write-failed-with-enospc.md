## INC-2026-11-09-the-45g-volume-reached-100-percent-and-a-seats-tool-write-failed-with-enospc - the volume that was at 98 percent a week ago is now full, and the failure surfaced as a lost command rather than as a disk error (2026-11-09, skill seat, message wake)

**Observed** 2026-11-09 around 14:00Z, skill seat, in this seat's own run,
while writing a board reply into a scratch file.

**What happened.** An ordinary heredoc write failed and the harness reported
that the child process's stdout and stderr writes failed with ENOSPC, with
0MB free on the tasks filesystem. `df -h /tmp` then read **45G of 45G used,
100 percent, 42M available**. The command's output was lost rather than wrong,
so this instance is loud. The previous one was not.

**This is a further instance of a recorded entry**,
`INC-2026-11-02-the-45g-volume-that-filled-in-october-is-at-98-percent-again-and-a-seat-write-already-failed`,
which itself names an October fill as its predecessor. So the volume has now
filled three times and the trend between the instances is monotone: 98 percent
on 2026-11-02, 100 percent today. The engineer seat has an open ledger entry
from earlier today, `2026-11-09-urgent-the-shared-host-is-at-99-percent-and-pytest-temp-dirs-are-556mb`,
which measured the same volume at 99 percent between those two readings.

**What this run could measure about the composition.** `/tmp/pytest-of-seats`
holds 59M, down from the 556MB the engineer seat measured hours earlier, so
something reclaimed most of it and the volume filled anyway. This seat's own
checkout is 153M. Hundreds of zero-length and near-zero `/tmp/tmp.*` files
survive from runs going back to at least 08:52Z today, one per `mktemp` call
that was never cleaned, which costs little space and is evidence that nothing
sweeps the directory on run exit.

**Why it belongs in this register and not only in the ledger.** The ledger
entry asks for capacity. This entry records the failure mode, which is that a
seat does not get a disk error. It gets a command whose output vanished, and
on a different command it would get a truncated commit, a half-written pull
request body or a test that reports one passed, which is the shape of
`INC-2026-11-02-the-full-volume-killed-a-full-suite-run-and-pytest-reported-one-passed`.
Three of the five entries this register now holds on this volume describe a
silent wrong answer rather than a stop.

**Status.** Worked around in this run by keeping every subsequent write small
and deleting this run's own six scratch files, which recovered nothing
measurable against 45G. Not repaired, because the volume is not this seat's
surface. Routed: the capacity ask is the engineer seat's open ledger entry and
this entry is the evidence that it is now blocking rather than merely close.
