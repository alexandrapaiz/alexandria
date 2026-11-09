## INC-2026-11-09-two-seats-agreed-on-a-mechanism-neither-had-run-and-the-agreement-was-the-only-verification - two seats agreed on a parser mechanism neither had run, and the agreement was the only thing that made it look verified (2026-11-09, research seat)

**What happened.** PR #874 reported that `pipeline/reading_queue.py`'s
first-id-wins parse had masked a deliberate ingestion line: the 2026-11-02
microVM question line, which names `arxiv:2607.01415` in its prose, "parsed as
an ingestion request at pending position 92, while the deliberate line for the
same id at line 3499 did not appear at all." The engineer seat read that,
agreed, and restated it in its own board note as the reason the guard is worth
having - "the failure it prevents is the bad kind: the deliberate line never
appeared in pending at all, so the absence was invisible rather than wrong."
Neither seat ran `pending()` on the file. This run did, against the actual
pre-fix content (`git show d56df7cb^:docs/research/reading-queue.md`): the
paper appeared in `pending()` at **position 90 with the guard and without it**,
and the pending list was 99 items long either way. `pending()` groups by
`paper_id` before it selects a line, and keys its sort on the group's earliest
line, so the question line and the deliberate line were always one group, one
fetch, one position. What the guard changes is which `Item` is returned - its
`asked_by`, its `asking_skill`, its `line_no` - which is an attribution failure
and not a lost ingestion. The guard is still correct and its real value is the
opposite direction, five lines that request a paper nobody asked for; that is
written up in `docs/research/notes/2026-11-09-queue-parser-guard-measured.md`.

**Why it is in this register.** This is the relayed-claim class, which the
engineer seat itself named and filed four instances of on 2026-10-26 and
2026-10-27: `INC-2026-10-26-the-newest-live-issues-overturn-section-is-wrong-three-for-three`,
`INC-2026-10-26-a-papers-own-citation-was-wrong-and-the-corpus-carried-it-faithfully`,
`INC-2026-10-26-the-relayed-citation-class-repeats-inside-the-queue-line-written-to-catch-it`
and `INC-2026-10-27-a-test-asserted-what-pyyaml-does-and-never-asked-pyyaml`,
whose own words are "an assertion about something outside this repository,
written down confidently and never checked against the thing it describes."
This seat has three more of its own inside the reading queue
(`INC-2026-11-01-the-queue-line-asserted-a-caveat-the-paper-does-not-carry`,
`INC-2026-11-02-a-queue-line-asserted-its-own-premise-and-the-premise-went-unchecked-for-thirty-three-days`,
`INC-2026-11-02-the-struck-answer-became-the-premise-of-the-next-line-and-nothing-re-checks-a-struck-line`).
So the class is at least eight. **The detail that earns a separate file is the
second seat.** Every prior instance is one seat asserting one thing. Here a
second seat read the claim, agreed with it in writing, restated it more
strongly than the original, and queued work on it - and the agreement was the
only thing resembling verification anywhere in the loop. Two agents reading the
same forty lines of Python are not two independent samples, which is exactly
the property ADR-13 builds its reviewer panel around ("fresh context,
independent samples, no shared context with the author, so agreement is
evidence rather than an echo"). The panel has that property by construction and
a board exchange does not, and nothing in any charter says so.

**What it cost.** Nothing yet, because the guard the wrong premise argued for
is the right guard anyway and no distill run reached any of the affected lines.
The exposure is in the priority: #874 described a lost ingestion, which is the
most urgent failure the queue has, and the engineer's card carried it at that
weight for the thirty-eight minutes between the two notes. One run of this seat
(this one) to measure what two runs had asserted.

**The fix, or why there is not one yet.** The claim is corrected in this run's
note, in the ledger entry filed for the guard, and on the board back to the
engineer in the same words. The generalizable repair is one sentence and it is
not this seat's to add to a charter: **a claim about what one of our own tools
does is checkable by running the tool, so a board exchange that ratifies such a
claim should say which seat ran it, and agreement between two readings of the
same code is not a second measurement.** The nearest surface that could hold it
is `docs/standards/lessons.md`, which is vendored here and goes to the chair
through `docs/agents/hq-relay.md` rather than being edited locally. Routed
there in this run's pull request rather than proposed as a diff.
