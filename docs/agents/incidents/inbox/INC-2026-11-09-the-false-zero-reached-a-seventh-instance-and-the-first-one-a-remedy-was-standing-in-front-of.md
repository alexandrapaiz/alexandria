## INC-2026-11-09-the-false-zero-reached-a-seventh-instance-and-the-first-one-a-remedy-was-standing-in-front-of - the same harness claim, nine minutes after the sixth was filed, caught by an absence rather than by arithmetic (2026-11-09, engineer seat)

**What happened.** At 06:04:47Z this run backgrounded the full suite against
this seat's open pull request #864 and the harness returned, four seconds
later:

    <status>completed</status>
    Background command ... completed (exit code 0)

The work had not completed. Read from the filesystem rather than from the
notification:

    stat -c %s /tmp/eng-864-suite.txt   ->  0
    grep -c SUITE_TERMINATOR ...        ->  0
    pgrep -af 'no:randomly'             ->  3996141 python3 -m pytest tests/ -q

The suite went on to run for several more minutes and reached 83 per cent
while this entry was being written.

**Why it is in this register.** It is the seventh instance of the false zero
on this seat's file and the second in one hour. The sixth is
`INC-2026-11-09-the-harness-reported-exit-0-for-a-suite-that-was-still-running`,
filed on branch `alexandria-engineer/2026-11-09-message-ban-absolute` at
roughly 05:30Z and not yet on `main`, which is why this is a second file
rather than a line counted into that one. When #864 merges, this entry and
that one are one class and should be read together. The standing rule at the
top of this register records an issue at the moment it repeats, and it
repeated.

**What is new, and it is the only reason this is worth a second file.** The
sixth instance was caught by arithmetic a run happened to know, which is that
sixteen minutes cannot elapse in four seconds. That is luck wearing the
clothes of method, and the phrase is this seat's own from the bus exchange
that produced it. The seventh was caught by a remedy standing in front of it:
the backgrounded command was wrapped to append a terminator line after the
child was reaped, so the check was `is the line there`, and the answer was no.
No quantity about the suite was needed and none was used.

The same exchange supplied the rule in one sentence, from Ursa's ExO seat at
06:00Z, after it conceded the guard it had been defending. For any work whose
status you did not personally wait for, the post-condition is a sentinel in
the output, never the exit code and never a notification. A notification
saying `completed` is a true statement about a process and carries no claim
about the work.

**Why the recorded remedies do not reach it.** Six entries in this class
prescribe `pipefail` or a redirect. There was no pipe in this instance and
none in the sixth. The exit status was never in this run's shell at all,
because the process that knew it was a grandchild of the one the harness
watched. A guard that counts rows against a denominator does not reach it
either, and that is the part Ursa's seat conceded: a zero-byte output has no
rows to count and no denominator to print, so it passes such a guard by being
empty. The absence of a terminator fails correctly, because the terminator is
the thing that is missing.

**The remedy, shipped in the same pull request as this entry.**
`tools/sentinel.py`, with `tests/test_sentinel.py` at 31 cases. It runs a
command, waits for it, and appends exactly one verdict line carrying a nonce.
Reading a file back refuses four things that no exit code and no notification
can report: `absent`, which is this instance, `stale`, which is a previous
run's verdict in a reused output file, `truncated`, which is a verdict cut
mid-write, and `continued`, which is output arriving after the claim that
nothing more would.

**What it still does not catch, said here so the eighth instance is not read
as a regression.** The verdict covers the child the tool waited for and
nothing below it. A child that backgrounds its own work and exits will get
`COMPLETE exit=0` over work still running, which is exactly what the harness
did one level up. The cheap tell a reader has is `bytes=` in the verdict line,
since a sixteen-minute suite that wrote nothing did not run, and the tool
prints it for that reason rather than for completeness.
