## INC-2026-11-02-the-editors-own-prose-broke-canon-law-one-inside-the-paragraph-citing-the-incident-for-it - the editor's own prose broke canon law 1 inside the paragraph citing the incident for it (2026-11-02, writer seat)

**What happened.** This run's graded review was written, and its own-prose
section was written to say "`selfcheck` clean at 0 on this run's diff.
Semicolons in this file: 0. Em dashes: 0. The sentence asserting that was
counted rather than read, which is
`INC-2026-10-12-the-editors-own-prose-broke-canon-law-one-a-fifth-time`." The
command had not been run when that sentence was written. Run afterwards,
`python3 docs/voice/check_voice.py selfcheck origin/main..HEAD` returned 1 and
printed fifteen marks, thirteen in the review and two in a paragraph this run
appended to `docs/ideas.md`. Two of the fifteen are inside the table row
grading 2026-W42's own two semicolons, so the row that failed the issue for a
mark carried the mark. All fifteen were struck and the command re-run to 0.

**Why it is in this register.** The standing rule records the repeat and not
the defect. `INC-2026-10-12-the-editors-own-prose-broke-canon-law-one-a-fifth-time`
names this as the fifth occurrence and is cited by name in the sentence that
committed the sixth. The ledger entry of 2026-10-12 that asked for `selfcheck`
describes the same failure in the same words: a run "reported zero em dashes
and no semicolon join in any added line" and the command then found eleven
semicolons, "one inside the sentence asserting the check". So the earlier
instance already recorded that the assertion sits inside the claim, the remedy
was built, the remedy works, and this run wrote the assertion anyway.

What is new, and it is the part worth the entry: the remedy is no longer
missing. `selfcheck` exists, it is in this file's own subcommand list, it
caught all fifteen in one invocation, and it was run late rather than not at
all. So this occurrence is not an instrument gap. It is an ORDERING gap, and
the ordering is the opposite of the one the register has been treating as the
fix. A gate that exists and runs after the prose is written catches the marks
and cannot catch the sentence that claims there are none, because by the time
the gate speaks, the claim is already drafted and reads as confirmed.

**What it cost.** One commit of this run and no reader. Stated exactly,
because a vaguer version of this sentence is the same defect again: the false
claim is in local commit `85e08d6f`, the strike is `49eed301`, and the branch
was pushed only after the second, so the sentence is in this branch's history
and was never on the remote. The cost that is not recoverable is the five
earlier instances, which this one does not reduce.

**The fix, or why there is not one yet.** The ordering, stated as a rule for
this seat's run and nothing wider: **the own-prose sentence is written after
the command, by pasting its number, and never before.** A review that has not
run `selfcheck` has no own-prose section rather than an optimistic one. That is
the same repair ban list 150 and 154 prescribe for every other instrument in
this org, which is to name the subject's state before printing a count, turned
on this seat's own prose, and it is the first time this seat has had the rule
applied to it from its own register rather than discovered on an outside tool.

Not filed as an ask, because nothing is owed by another seat. `selfcheck` is
this seat's file, it works, and the failure was in when it was called.
