## INC-2026-10-26-a-sibling-run-read-this-seats-mail-and-acted-on-half-of-it-without-replying - the duplicate-wake class with the duplicate arriving as an in-flight sibling rather than as a second wake (2026-10-26, writer seat)

**What happened.** The PM seat sent this seat a note on the board at 20:45:45Z,
`9ac58062-9bf8-486d-8f07-107c48c88546`, saying it agreed with the W42 overturn
ruling, had merged it, had posted the correction-notice question to the owner as
a formal ask, and was holding the site edit as an owed item because the frontend
seat's own pull request is open. That note is the event this run was woken for.

A previous run of this same seat was already running when it arrived. Run 58
started at about 20:44, ran to 20:58:58, and its pull request #612 was created at
20:47:53Z. It read the seat's inbox mid-run, took the note's two factual halves
into `docs/voice/awaiting-her-word.md`, and shipped them: the question row it
added says the PM posted the ask and carries the silence rule's deadline. It
then sent the PM a `done` about its own topic at 20:58. It never replied to the
note.

So this run was woken by a message whose consequences were already in its own
register, written by its own seat, thirteen minutes earlier, and with no record
anywhere of who had done it.

**Why it is in this register.** Fifth instance of the class the charter already
names, `INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`,
after the fourth was filed this morning as
`INC-2026-10-26-the-red-check-was-already-green-when-both-wakes-fired`. The
shape is new again and worth separating for the same reason that one was. The
first three instances were one event waking two runs, detectable by looking for
the seat's own open pull request. The fourth was a second seat writing
instructions against stale state. This one is neither: the note was read by a
run it did not wake, which acted on the half that was bookkeeping and left the
half that was a conversation, so the note was simultaneously answered in the
register and unanswered on the bus.

**What it cost.** Little, and the charter's clause is why. #612 was found in the
first three commands and read rather than worked around, so this run built on
its branch instead of racing it. The verification was not wasted either, because
the standing instruction is to verify rather than trust the predecessor's
report: the ask was read at its source, board message
`065eda95-92e7-4f94-8625-906c10691b81` named in the PM's #609, and the live page
was re-read and still serves the pulled section. The real cost is the one that
did not land. A run that had trusted its own register would have replied to the
PM that the work was done without having verified any of it, and the register's
two new rows were the only evidence, written by a run that never said it had
read the note.

**The fix, or why there is not one yet.** No code is owed and the gate that
would catch it does not belong in this seat's instrument. The cheap rule is
one sentence in whatever governs a run's report: a run that acts on a message
addressed to its seat either replies to that message or says in its report that
it read it and did not. Run 58's report named its own topic and its own pull
request, both accurately, and said nothing about the note it had consumed. The
board already holds the fact that no reply was sent, and nothing reads it.
