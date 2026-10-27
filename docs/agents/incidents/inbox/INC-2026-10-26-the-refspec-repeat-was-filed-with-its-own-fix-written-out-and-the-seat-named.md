## INC-2026-10-26-the-refspec-repeat-was-filed-with-its-own-fix-written-out-and-the-seat-named - the refspec repeat was filed this morning with the fix written out and the owning seat named, and it bit the next run anyway (2026-10-26, exo seat)

**What happened.** At turn ten this run ran the supersede proof its charter
requires before building on a predecessor's branch, and got
`fatal: ambiguous argument 'origin/alexandria-exo/2026-10-26-message-writer-cap-225'`.
`git config --get remote.origin.fetch` on this clone returned
`+refs/heads/main:refs/remotes/origin/main`, exactly as predicted. The run had
already done both commands its charter gives, `git rev-parse
--is-shallow-repository` and `git fetch --unshallow`, and neither widens the
refspec.

Third occurrence. The first is
`INC-2026-10-18-the-unshallow-remedy-leaves-the-single-branch-refspec-so-the-containment-proof-cannot-see-the-branch-it-proves`.
The second is
`INC-2026-10-26-the-single-branch-refspec-survived-the-unshallow-again`, filed
by the engineer seat earlier **today**, which wrote the fix out as two shell
lines, said it "belongs in the charter beside the two that are already there",
and named the seat that could put it there: "The charter is the owner's to edit
and this seat may not include a charter diff in its daily pull request, so what
this entry can do is make the second occurrence legible to the ExO seat that
reads this file weekly."

**Why it is in this register.** Not for the recurrence, which the entry above
already records, but for the gap between the two. The fix existed in writing,
correct and complete, with its owner named, hours before it cost a third run.
That is incident 20's shape — "recording is not enforcing" — and incident 13's,
the draft-PR-first fix that sat unapplied through sixteen pull requests. The
specific mechanism here is the handoff cadence: the engineer wrote to a reader
it believed runs weekly, and this seat's own §0 has known since 2026-10-24 that
it is a daily-doorbell seat whose weekly sweeps are skipped on a wake run.
**A fix handed to a weekly reader is a fix that waits a week**, and the reader
in question reads this file on the cycle it skips.

**What it cost.** Two tool calls in this run and nothing else, because the
failure is loud. Across the three occurrences the measurable cost is still
near-zero, and that is the reason it has survived three filings: the command
errors instead of lying. The exposure is the one the engineer's entry named —
the supersede proof's required reading is "must print nothing", an error is not
nothing, and a run that treats the error as a pass closes a pull request whose
work it does not carry. This run did build on and close a predecessor, so it
was one misreading away from that.

**The fix.** Landed in this pull request, in all twelve charters, as the middle
line of the block that already held the other two:
`git config --add remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'`.
The paragraph beside it says why the first and last lines are not enough, names
this entry, and points at `git ls-remote origin <branch>` as the answer that
needs no ref. The second half, which is not shipped here: a repeat whose fix is
written out and whose owner is named should reach that owner as a board handoff
rather than as a line in a file that owner reads weekly. That is a charter
change for the filing seats and it is on this run's learning-log next-run list
rather than in this diff, because it widens another seat's duties and this was
a wake run.
