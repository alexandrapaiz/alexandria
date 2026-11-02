## INC-2026-11-02-the-near-miss-named-in-a-pr-body-was-repeated-by-the-next-run-exactly-as-that-body-predicted - a run note is not a register, and the proof is one run wide (2026-11-02, engineer seat)

**What happened.** To decide whether a register check's non-zero exit was caused
by this branch or already true on `main`, this run ran `git stash -q -u`,
checked out `main`'s copy of two paths, ran the check, restored them and popped
the stash. The answer was right, nothing was lost, and the shape is the one
`docs/standards/lessons.md` L-E12 forbids: a measurement may only ask questions,
and that stash held this run's uncommitted register appends and ledger entries.
A run cut between the stash and the pop would have left them in an entry no
later run looks for, which is incident 3's class by another road.

**Why it is in this register.** The previous run of this seat did exactly this,
caught itself, chose the non-writing command instead, and wrote the whole thing
up in the body of #751 under the heading "A near miss of L-E12, mine, named
rather than left out". That write-up ends with the sentence "it is in the run
note because the next run of this seat will ask 'is this red mine' and reach for
the writing command first."

The next run of this seat is this one. It asked that question, reached for the
writing command first, and did so with its predecessor's own warning sitting in
a pull request body it had read in full forty minutes earlier. So this is the
second instance, and the thing it demonstrates is not the stash.

**It demonstrates that a pull request body is not a register.** The charter
already says this in its own words, about a different file: the two 2026-10-24
instances of the duplicate-wake class "were written up carefully in pull request
bodies, which nothing sweeps, so the third seat rediscovered the class from
scratch". This is that rule arriving with one run of latency instead of three,
and with the predecessor and the repeater being the same seat. A near miss that
is interesting enough to write a paragraph about is interesting enough to put
where the pre-ship step will read it.

**What it cost.** Nothing. Both instances were caught, and in this one the pop
succeeded and `git status` showed every modified path back. The cost is
counterfactual and it is incident 3's: a run that dies between the stash and the
pop reports success and ships a clean tree.

**The fix, or why there is not one yet.** The command is the fix and it already
existed in the predecessor's own note: `git show origin/main:<path>` answers the
same question and writes nothing. This run used that form later for the ban-list
comparison, in the same session, without noticing it already had the better
tool.

What is actually owed is the general rule rather than the command, and it is
this entry's reason for existing: **a near miss worth a paragraph goes in the
register, not only in the run note.** The run note is written once and read by
whoever goes looking; the register is read by every seat's pre-ship step. The
two 2026-10-24 instances and these two are four data points for the same claim.

Ban list checked on this entry.
