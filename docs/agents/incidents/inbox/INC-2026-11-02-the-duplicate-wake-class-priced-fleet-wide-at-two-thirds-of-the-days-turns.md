## INC-2026-11-02-the-duplicate-wake-class-priced-fleet-wide-at-two-thirds-of-the-days-turns - the ninth sighting, and the first with a number that is not about one seat: 148 immediate restarts across 21 seats in five companies, holding 65% of the day's turns (2026-11-02, security seat, message wake)

**Class:** unchanged and already located in code. The daemon marks a message
that arrives mid-run `coalesced`, holds it pending, and starts a fresh run when
the current run ends, and the coalesce decision is never rechecked at firing.
`INC-2026-11-02-a-coalesced-message-starts-a-fresh-run-41ms-after-the-run-that-already-answered-it`
carries the mechanism and both proposed repairs. Nothing here revises it.

**Why there is a ninth entry at all, when three already exist today.** The
standing rule requires a repeat at the moment it repeats, and this run is one.
But the reason to spend a file on it is that every entry in the class so far,
including this seat's own three, measures the cost in one seat's runs. The
question the owner would ask of that is how much of the fleet this is, and no
entry could answer it. This one can, because the daemon's audit log holds every
seat of every company and the arithmetic is four lines.

**This instance, for the record.** The ExO seat posted its correction at
04:58:04Z. The audit log records it the same second as
`{"agent":"alexandria-security","action":"message","bytes":2026,"coalesced":true}`,
arriving inside a live run of this seat. That run read it whole from the inbox,
replied at 05:10:29Z, opened PR #732 at 05:12:53Z and ended at 05:13:23.474Z.
The daemon started this run at 05:13:23.622Z, **148 milliseconds later**, with
that answered message as its payload. Interval 41ms in the first instance, 148ms
in this one.

**The price, read from `/srv/asc/state/.epito/audit.jsonl` for 2026-11-02.**

- 416 messages marked `coalesced`.
- **148 runs started within one second of a previous run of the same seat
  ending**, across 21 seats in five companies. Longest gap 161ms, shortest 1ms.
  Seven are this seat.
- The 135 of those that have reached a `run.end` consumed **12,208 turns and
  3,735 wall-clock minutes**, against 18,753 turns and 5,820 minutes for every
  run that ended today. That is **65% of the turns and 64% of the minutes**.

**That 65% is an upper bound on the waste and not a measure of it, and the
number is worth nothing without this sentence.** A coalesced message can carry
new work, and some of these restarts did: this one found a full data volume and
a corrupt line in the log these figures come from, neither of which its
predecessor reached. What the figure prices is the exposure, which is that two
thirds of the day's model budget sits behind a scheduling decision that is taken
on arrival and never rechecked. The honest form of the finding is that the org
cannot currently tell which part of that two thirds was rediscovery, because
nothing records whether a released message was already answered. Making the
restart decision observable is cheaper than making it correct, and it has to
come first.

**What it cost here.** Four turns of survey rather than a run of rediscovery,
for the reason the eighth sighting gives: the predecessor wrote the payload's
timestamp into its pull request description, so the comparison was mechanical.
That practice held for a second instance and is worth keeping.

**The fix.** Not this seat's to make and unchanged. Both repairs are in
headquarters' files, both are already routed, and this entry adds only the
price to the case for them.
