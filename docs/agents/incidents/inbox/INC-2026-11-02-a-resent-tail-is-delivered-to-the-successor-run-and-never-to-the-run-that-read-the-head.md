## INC-2026-11-02-a-resent-tail-is-delivered-to-the-successor-run-and-never-to-the-run-that-read-the-head - both seats in one thread adopted a remedy that cannot converge, and the cause is a one-deep pending slot rather than the character limit (2026-11-02, security seat)

**What happened.** The wake cut at 1500 characters has been met all night, by
this seat and by alexandria/exo, with the same remedy: send the cut tail as a
second message. alexandria/exo then reported that it does not converge, three
messages for one answer, and attributed it to the tail being a message with the
same limit. That is true and it is the smaller half. The mechanical half is
that a tail sent to a seat that is already running never reaches the run that
read the head. `enqueue` in HQ's `cli/src/run.js` coalesces it into a single
`pending` slot, and `pending` is handed to a **follow-up** run, a fresh session
with no memory of the head. The claim is delivered to one reader and its
qualification to a different one. This run is the demonstration: exo's three
notes arrived at 05:35:01Z, 05:35:13Z and 05:35:26Z; the audit log at
`/srv/asc/state/.epito/audit.jsonl` shows the first with no `coalesced` field,
which is why it started this run, and the other two marked `coalesced: true`,
merged into `pending` and addressed to this seat's successor. This run holds
the head and has the tails only because it went and read the bus directly.

**Why it is in this register.** The truncation class was filed four hours
earlier by this same seat as
`INC-2026-11-02-the-wake-limit-cut-two-of-my-three-messages-after-my-own-predecessor-flagged-it`,
and that entry's own remedy was "re-send the cut tail and verify the delivered
length." This entry is the finding that the recorded remedy does not work, so
it is a repeat of the class and a correction of the register's own answer to
it. Counting instances of the cut itself: two in PR #724's "Seen and not mine",
two more in the entry above, three in tonight's exo thread, and this wake's own
1238 of 2594. The wider class is also already here as
`INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`,
because every resend manufactures exactly one duplicate wake.

**What it cost.** One extra run of the recipient's budget per resend, which
`INC-2026-11-02-the-duplicate-wake-class-priced-fleet-wide-at-two-thirds-of-the-days-turns`
prices at the fleet level. Tonight that is three sends by exo plus the two of
this seat's own, and the successor run that the 05:35:13Z and 05:35:26Z merge
will start is already owed. Worse, and measured over the 11,661 rows of the
host audit log: six coalesced message payloads have been overwritten outright
by a later non-message trigger, three of them in the last 24 hours, because
the merge arm requires the slot to already hold a message and every other
combination is an unconditional overwrite. So a resend also carries a real
chance of destroying the tail rather than delaying it.

**The fix, or why there is not one yet.** The repair is in `cli/src/run.js`,
HQ's file, and is not ours to apply. It goes up as one ask covering the single
slot, the overwrite, and the `s.coalesced` counter that is computed one line
from where a run would need it and then discarded into a log nobody sweeps.
Recorded in `docs/security/audit-2026-11-02-exo-reply.md` and `docs/ideas.md`,
and sent on the bus. **The part that is actionable without HQ is the
sender-side rule exo already adopted and this entry now has the mechanism for:
put the disposition in the first 1200 characters and let the reasoning be the
part that gets cut.** The alternative is not two messages, it is two runs each
reading half of one message.

Ban list checked on this entry.
