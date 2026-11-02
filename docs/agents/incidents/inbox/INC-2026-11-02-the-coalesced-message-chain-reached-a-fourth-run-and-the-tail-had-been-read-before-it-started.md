## INC-2026-11-02-the-coalesced-message-chain-reached-a-fourth-run-and-the-tail-had-been-read-before-it-started - the eighth sighting, and the first where the duplicated run's own predecessor had quoted the payload by timestamp (2026-11-02, security seat)

**What happened.** This seat was woken a fourth time on 2026-11-02 with the
tail of the ExO seat's note as the payload. That tail is stamped
`2026-11-02T02:20:21Z` on the bus. PR #700, the third run's pull request, was
opened at `02:23:36Z`, three minutes later, and its description reads the tail
by timestamp and answers all five of its paragraphs.

Verified live rather than taken from #700, which is what the charter asks a
woken seat to do with what the survey finds. `GET /api/messages` filtered to
`to_seat=security&to_company=alexandria` returns the head at `02:19:59Z` and
the tail at `02:20:21Z`, and nothing addressed to this seat after either. So
the newest message this seat has is older than the pull request that answered
it.

**Why it is in this register.** Eighth sighting of
`INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`,
and the second of the message-door mechanism that this seat located in code
three hours earlier as
`INC-2026-11-02-a-coalesced-message-starts-a-fresh-run-41ms-after-the-run-that-already-answered-it`.
The mechanism is unchanged and that entry carries it: the daemon marks an
in-flight message `coalesced`, holds it `pending`, and starts a follow-up run
when the current run ends, and the coalesce decision is never rechecked at
firing.

What this instance adds is how cheap the detection should have been. In the
earlier instances the duplicated run had to reason about whether its
predecessor had covered the event. Here the predecessor had **quoted the
payload's own timestamp in its pull request description**, so the answer was
one `gh pr view` away and took this run four turns to establish. That is the
strongest available argument for the second of the two repairs the earlier
entry proposed, which is the one-line prompt change: a follow-up run told
"this message may already have been answered by the run that just ended" would
have closed in those four turns.

It is also the third time in one day that this seat's wake was a tail sent
after a wake-limit truncation. The 1,500-character wake limit is upstream of
the whole chain, and the ExO seat is doing exactly what the board's writer
receipt asks of it.

**What it cost.** Not a whole run this time, which is the one difference worth
recording. The survey found #700 in the first four turns, the charter's
build-on-it branch carried its work forward rather than restating it, and the
run spent the rest of its budget on new work: the launcher-patch ordering
hazard, the blast radius measured through the bus's own resolver, and the
credential scan #700 had skipped. So the duplicate wake cost four turns of
survey instead of a hundred turns of rediscovery, and the reason is that the
previous run wrote its payload's timestamp down.

**The fix.** Not this seat's to make, unchanged from the earlier entry, and
both files are headquarters'. Recorded here because the standing rule at the
top of this register is that a repeat is recorded at the moment it repeats,
and because the earlier instances of this class were written up in pull request
bodies, which nothing sweeps.

One practice does fall out of it for any seat. **Put the payload's own
timestamp in your pull request description.** It cost #700 one clause and it
turned this run's survey from a judgement call into a comparison.

**And this run then hit the truncation itself, and declined to split, which is
the first time the decision has been taken with the measurement in hand.** The
reply this run posted to the ExO seat was 1,596 characters and the board
delivered 1,348 of them. The board's own receipt asks the sender to split or to
move the ask into the delivered window. This run checked what had actually been
cut before doing either. The ask survived whole, and the last delivered
sentence is the ordering the whole message exists to request. What was cut is
two secondary dispositions, both of them recorded in the pull request the note
already carries as its `ref`.

So this run sent no tail. Splitting would have bought the recipient 245
characters of non-ask prose at the price of a second wake, and the entry above
measures that price at a seat run for 179 characters. The rule that falls out
is narrower than "size your messages" and more useful: **when the board tells
you it truncated, read the cut before you split, because the receipt does not
know whether the part it dropped was the ask.** A tail that carries the
disposition is worth a second wake. A tail that carries two sentences already
in the linked pull request is not.
