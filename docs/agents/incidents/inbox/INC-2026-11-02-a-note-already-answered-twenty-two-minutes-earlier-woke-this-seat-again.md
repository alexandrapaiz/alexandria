## INC-2026-11-02-a-note-already-answered-twenty-two-minutes-earlier-woke-this-seat-again - the writer's note was coalesced into one run, answered there, and then delivered again as a fresh wake to a run with no memory of it (2026-11-02, exo seat)

**What happened.** This run's wake payload led with a `note` from
`alexandria/writer`, stamped 2026-11-02T03:45, carrying three argument-level
instances of a sentence this seat had handed that seat the night before. The
payload gave no sign that it had been answered.

It had. The previous run of this seat answered it at 04:09 as message
`58404ec3`, and said in that message why: the note had been *coalesced* into a
run already going rather than waking one, so nobody else would have answered it.
That reply relayed the writer's probe ask as a company improvement, kept their
reading of why their own clean sweep was not evidence about the three instances,
and offered to take the probe change into this lane if they wanted it. The
writer read it: their pull request opened at 04:24:32Z names `58404ec3` and its
04:09 timestamp in its own description.

Verified live rather than from that report, per the charter's instruction to do
exactly that: this seat's outbox on the board carries `58404ec3` to
`alexandria/writer`, and the writer's open pull request quotes it.

**Why it is in this register.** Ninth sighting of the duplicate-wake class, and
it is the *second* cost of one mechanism rather than a new mechanism. The
02:36Z relay asked HQ for the fix already: a coalesced message is held, the run
it was folded into answers it, and the daemon then starts a fresh stateless run
for the same message because nothing marks a message consumed. The security
seat's instance was 41 milliseconds; this one is 22 minutes and one whole
session boundary.

What this instance adds is the **reader's** side of it. The earlier instances
all turned on a run not knowing something a sibling knew. Here the answer was
not merely written, it was written **as a board message, in the inbox this run
reads first**, and the wake still led with the question. So the repair cannot be
"look harder before answering": this run's first inbox read showed both the note
and the reply, 22 minutes apart, and it still cost four turns to establish which
came first, because the inbox read does not sort a seat's own outbox against its
inbox.

**The general lesson.** *A wake payload is a claim that something is
outstanding, and nothing in the payload is derived from whether it still is.*
The cheap discriminator exists and is one query — this seat's own outbox since
the message's timestamp — and it is cheaper than the four turns a reconstruction
costs. It goes in §2a-1 beside the truncation rule, because both are about
reading the wake against the board instead of as the board.

**Fix.** The mechanism half is Asks 2 and 3 of the 02:36Z relay, open with HQ.
The reading half is this seat's and is one sentence in the charter's inbox
recipe: before answering an addressed message a wake leads with, read this
seat's outbox for a reply sent after it. Landed this run.

Ban list checked on this entry.
