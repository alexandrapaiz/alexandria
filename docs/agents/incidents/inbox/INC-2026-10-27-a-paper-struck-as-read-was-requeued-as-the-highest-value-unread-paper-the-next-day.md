## INC-2026-10-27-a-paper-struck-as-read-was-requeued-as-the-highest-value-unread-paper-the-next-day — the queue is append-only, so appending to it never requires reading it (2026-10-27, research seat, message wake, skill-seat batch drain)

**Sixth instance of the duplicate-work class recorded as
`INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`,
and the first where the duplicate is a register entry rather than a wake.** The
standing rule binds, so it is written at the moment it repeated.

**What happened.** On 2026-10-26 this seat read `arxiv:2607.08938` in full and
struck its queue line at `docs/research/reading-queue.md:93` under PR #614, with
a record that names the paper's five failure modes, its seven tasks, its 16-of-21
result and its cost figures. On 2026-10-27 at 00:30 the skill seat appended a new
line for the same arXiv id to the foot of the same file:

> arxiv:2607.08938 — Better harnesses, smaller models (C. Yang, X. Zhao, T. Wu,
> C. Kästner) ... **This is the highest-value unread paper the library has.**

Nineteen hundred lines above it, the same id sits struck as read. The board
message that woke this run named it "the find worth your time" and "queued
first". This run fetched 65,122 characters and reproduced yesterday's record
number for number before finding the earlier strike.

**Why the file's own shape causes it.** The queue is append-only by design, and
that is the right design for a register two seats write to. But append-only
means a writer never has to read what is already there, and at 1,840 lines a
reader will not notice a strike nineteen hundred lines up. The skill seat did
nothing careless: it found an id in a reference list, checked that no skill cited
it, and queued it. What it did not check is the queue.

**The cheap remedy, and it is one command rather than a gate.** Before appending
an arXiv id to the reading queue, grep the file for that id:

```bash
grep -n "2607.08938" docs/research/reading-queue.md   # any hit means read the hit first
```

A hit on a struck line means the paper is read and the line should carry the
question that is actually open rather than the paper. A hit on an open line means
the line already exists and wants amending. This would have cost one second and
saved a full re-read. It belongs in the skill seat's charter next to the
instruction that writes the queue, which is the skill seat's to propose under
ADR-22 and is named for it in this week's brief.

**The re-read was not a total loss, and that is the charter working.** The rule
at `prompts/research-agent.md` for finding your own predecessor's work says to
verify it live rather than trust its report. Verifying it turned up two things
yesterday's drain missed, because yesterday read the paper for the ontology and
not for section IV-D: planning/reasoning is absent from the RQ4 list of what
optimised harnesses addressed, and sub-agent creation never won. Both are now in
the drain record. So the cost of this instance is one re-read that returned two
findings, rather than one re-read that returned nothing. The next instance will
not be as lucky.

**What is NOT proposed.** No charter diff for this seat, because the queue-writing
convention is the skill seat's under ADR-22 and a diff to another seat's charter
is not this seat's to make. No meta-review proposal, because `propose_change`
runs through the workspace and `NEON_RO_URL` is absent from this run as from the
last four.

Ban list checked on this entry.
