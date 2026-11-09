## INC-2026-11-09-step-0b-read-from-a-shared-name-and-the-measurement-it-produced-was-handed-to-another-seat - the shared-tmp class in the read direction, where the failure is a confident wrong number rather than a lost artifact (2026-11-09, engineer seat, message wake)

**Observed** 2026-11-09, this seat's own run, while writing the board reply that
corrected another seat's measurement of `main`.

**What happened.** This run obeyed step 0b where the rule's own example points.
Every commit message, the pull request body and the board reply were written
into a `mktemp -d` directory. Then the same run redirected four measurements to
fixed names in `/tmp`: `trunk-suite.log` for the full suite against pristine
`main`, `green892.json` and `green892b.json` for the three-way merge verdicts,
and `mainsuite-pid`. The clone's own worktree went to a fixed `/tmp` path too.

**Why it is in this register.** Third instance of the class, and the standing
rule records a repeat at the moment it repeats. The first is
`INC-2026-10-18-twelve-seats-now-share-one-tmp-and-one-overwrote-another-seats-artifact`,
where a pull request description was overwritten between the write and the
publish. The second is
`INC-2026-11-02-a-mktemp-directory-addressed-by-a-glob-is-a-shared-name-again`,
where the rule was obeyed and then undone one command later by a glob, and 25
live `body.md` files were measured under `/tmp/tmp.*` at that moment, all owned
by the same uid and all mode 0644.

**And the direction is new, which is why this is not just a third tally mark.**
Both prior instances are writes: this seat's artifact is overwritten by another
seat and reaches GitHub wrong. Step 0b's own paragraph is written entirely in
that direction, and its named failure is "the content belongs to somebody else"
at publication time. This run's exposure was the read. The four fixed names
hold measurements, and the measurement was the deliverable: the whole board
reply this run sent is a correction of another seat's numbers, built by reading
`/tmp/trunk-suite.log` back. Had a concurrent seat been running the same suite
to the same name, this run would have read another seat's pass count, published
it as its own against another seat's report, and been wrong with a sha and a
timestamp attached.

**What it cost.** Nothing, and the reason is luck rather than a guard. No
concurrent seat happened to choose those names in the window. That is the same
"nothing was overwritten and the reason is luck" finding the 2026-11-02 entry
made about its own near miss, which is the second time in eight days this class
has been caught by chance rather than by a check.

**Why the rule did not reach it.** Step 0b names "scratch file" and gives
`cat > "$scratch/body.md"` as its one example, so the reader applies it to the
artifact about to be published. A log you redirect and a verdict you parse do
not read as scratch, they read as output, and nothing in the paragraph says
that a measurement read back from a shared name is the same defect with a worse
failure mode. The prior entries could not have taught this either, because both
are writes.

**The fix, or why there is not one yet.** Not fixed in code, because the
repair is a sentence in step 0b of every charter and charters are edited only
by the owner's merge. What the sentence would say, offered rather than applied:
step 0b covers everything a run writes under `/tmp` and reads back, not only
what it publishes, and the read direction is the dangerous one because an
overwritten artifact is caught by whoever reviews the publication while a
misread measurement is published with evidence attached. Filed as a ledger
entry in this pull request alongside the incident.

What this run did do, immediately and in its own tree: the remaining scratch in
this run went through `mktemp -d`, and `tools/root_scratch.py` already guards
the checkout root for the sibling half of this class, so the gap is `/tmp`
specifically and it is one paragraph wide.

**Blameless note.** The run that filed this is the run that committed it, in the
same hour it built an instrument whose whole purpose is finding a prior entry
with a remedy. It found both prior entries in 2.4 seconds when it finally asked.
It did not ask until after the measurements were taken, which is the honest
shape of the gap named in the entry beside this one: the lookup fires when a
seat files and not when a seat acts.
