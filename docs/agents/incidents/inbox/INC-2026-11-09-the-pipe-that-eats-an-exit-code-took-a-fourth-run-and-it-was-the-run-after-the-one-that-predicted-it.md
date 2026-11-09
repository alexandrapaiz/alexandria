## INC-2026-11-09-the-pipe-that-eats-an-exit-code-took-a-fourth-run-and-it-was-the-run-after-the-one-that-predicted-it - the previous entry named the next instance as its own measurement, and the next instance was the next run of the same seat (2026-11-09, engineer seat)

**What happened.** This run measured the exit code of a repaired selector as
`timeout 400 python3 tools/ship_first.py --company alexandra-systems 2>&1 | head -3; echo "exit=$?"`
and read `exit=0`. That zero is `head`'s. The tool had exited 1, which is the
whole point of the measurement: the selector now finds 11 `lost` runs where it
used to find none, and 1 rather than 0 is the entire finding about the gate. Run
again with the output redirected to a file instead of piped, the same command
reports `HQ exit=1`.

Caught inside the run rather than published, because the number was the claim
being tested and a 0 contradicted the 11 `lost` rows printed two lines above it.
The pull request carries the corrected measurement with the redirect shown.

**Why it is in this register.** It is the fourth instance of the class and the
third filing. `INC-2026-11-02-a-probe-of-an-exit-code-piped-it-into-tail-and-read-the-pipes-exit-instead`
recorded the first two, four hours apart, one in alexandria/skill and one in
this seat. `INC-2026-11-09-the-pipe-that-eats-an-exit-code-took-a-third-seat-run-and-it-was-the-seat-that-filed-the-first`
recorded the third, and that entry closes with "the next seat that pipes a gate
into `tail` is the measurement of whether that was enough."

**This is that measurement, and the answer is no.** The third instance was the
immediately previous run of this seat, merged as part of #843 about forty
minutes before this one started. So the entry was filed, merged to `main`,
present in the fresh clone this run reads, and the same seat made the same
mistake in the next run. Two details sharpen it rather than soften it. It was
`head` rather than `tail`, so a reader grepping the register for `tail` would
not have matched it, and the previous entry's own title and remedy both say
`tail`. And this run had already read that entry's sibling ledger file during
the same session, which is as close to "the warning was open in front of me" as
the evidence gets.

**What it cost.** One command, repeated, so roughly four minutes of wall clock
on a tool that parses 2.7 GB per invocation. Nothing durable, for the same
reason as last time: the surrounding output disagreed with the exit code loudly
enough to be noticed. That is twice in a row that the save was the reader rather
than the gate, which is the thing worth not relying on a third time.

**The fix, and this entry does not propose a new one.** The remedy has been
correct and recorded since 2026-11-02: `set -o pipefail`, or read
`${PIPESTATUS[0]}`, or do not pipe a command whose exit code is the answer. The
third entry's conclusion is also right, that what would fire is a line in the
charter every seat reads before it works rather than a sentence in a register
opened weekly, and that a charter edit is the owner's merge and cannot ride a
seat's daily pull request. Both of those stand. The only thing this instance
adds to the proposal is its own frequency: four instances in eight days, three
in this seat, one of them in the run immediately after the run that filed the
previous one. The ledger entry carrying the charter-line proposal is
`docs/ideas/inbox/2026-11-09-a-pipefail-line-belongs-in-the-charter-not-in-a-register.md`,
filed by the previous run, and this entry is the evidence for it rather than a
second copy of it.
