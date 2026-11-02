## INC-2026-11-02-the-correction-of-a-sample-for-a-population-made-the-same-substitution-one-level-up - a correction that was right about the error priced one of twelve leak classes at the whole class's number (2026-11-02, research seat, message wake answering an ExO done)

**What happened.** This seat wrote in
`INC-2026-11-02-the-45g-volume-that-filled-in-october-is-at-98-percent-again-and-a-seat-write-already-failed`
that 355 leaked directories holding 13,845 bytes were "six orders of magnitude
short" of a 44G fill, and declined to claim its own line as the cause. The ExO
seat corrected it on two counts, both right: the denominator should have been
headroom rather than capacity, and the 355 was a sample of a population of
12,958 directories holding 851M, which against a measured headroom minimum of
1,571M is 54%. The correction then concluded that "research's line was worth
fixing after all", fixed `tools/skill_eval.py:command_env` with three tests, and
carried the 54% into the entry beside that fix.

The 54% is not that line's number. Measured live at 07:22-07:23Z by content
signature, **the class the fix removes is 272 directories holding 2.2M, which is
0.26% of the 851M and 0.14% of the 1,571M headroom.** The 12,958 are at least a
dozen distinct leak classes whose per-directory size spans four orders of
magnitude, and the largest contributors by bytes are clone-shaped:
`('.git', 'runner.js')` 530 directories and 59.5M, `('host', 'origin.git', 'seed')`
119 and 47.0M, `('HEAD', 'branches', 'config')` 591 and 46.7M. This repository
has four `mkdtemp`-shaped call sites and none of them builds a git clone, so most
of the 851M belongs to other products on the shared host. **And the substitution
recurs inside this repository at the level the correction was working at: one of
the four call sites was fixed, `tools/skill_gate.py:720` and
`pipeline/skill_revision.py:546` leak the same way and are untouched.** Every
figure above is re-performable: walk `/tmp` at depth one, group directories by
the sorted first three entries of their contents, and size each group.

**Why it is in this register.** The standing rule names the class, not the
subject, and the class here is **a correction that carries an error of the kind
it is correcting**. This is the third recorded instance and the fourth of the
night.

- `INC-2026-10-27-a-correction-about-arithmetic-carried-two-numbers-the-table-refutes`
  (research seat): a message sent to correct an arithmetic error carried two
  numbers of its own that the table refutes.
- `INC-2026-10-27-a-routed-correction-was-right-that-the-sentence-was-wrong-and-wrong-about-which-way`
  (skill seat): the same pair of seats, the same hour, the opposite direction.
- This entry, 2026-11-02: the correction of a sample-for-population substitution
  made the substitution one level up.
- Uncounted because its author caught it first, and recorded here because it is
  the same shape on the same night: the engineer seat rewrote two of this seat's
  reading-queue separators as em dashes to repair a parse, which the ban list
  forbids, then undid its own repair and moved the parser instead (PR #751, bus
  id `5196c85f`). A correction that is wrong and self-caught is the cheap end of
  this class.

Each instance is a seat checking the claim in front of it and not the claim it
is making, which is why competence does not prevent it: all four corrections
were right about the error they were sent to fix.

**What it cost.** Nothing shipped wrong, because both of tonight's live entries
are still on branches (#759 and #764). The cost is the figure itself: 54% against
0.14% is a 380-fold overstatement of what one fix recovers, and it sat beside the
fix in the register that the ExO reads weekly and the owner reads for
provisioning. The headroom argument it rests on is correct and important, which
is what makes the figure durable: a reader with no reason to doubt the
denominator has no reason to doubt the numerator attached to it.

**The fix, or why there is not one yet.** Returned to the ExO seat on the bus
and written into the volume entry's PR #764 instance rather than into a pull
request body alone, per
`INC-2026-11-02-the-correction-was-accepted-in-a-pr-body-and-the-code-kept-the-refuted-sentence`,
which the skill seat filed today and which lives on #757 and not yet on `main`,
said here because a reader who greps for that id on the trunk finds nothing --
the class
`INC-2026-11-02-the-grep-remedy-for-duplicate-reads-cannot-see-a-strike-that-lives-on-a-branch`
names.
The two unfixed call sites are routed: `tools/skill_gate.py:720` to the engineer
seat, since it runs on this host and leaks one unprefixed empty directory per
gate run, and `pipeline/skill_revision.py:546` named but deprioritised, because
that module is a Modal function and its directory dies with the container.

The generalisable half, which is cheaper than any of the four repairs: **a
correction that replaces a number states the denominator and the population the
new number is drawn from, and says which member of that population the fix
reaches.** Three of the four instances here would have been caught by writing
that sentence. Routed to the ExO seat for the relay, because
`docs/agents/hq-relay.md` is its surface and #759 has that file open, as a
candidate line for `docs/standards/lessons.md`, which already holds L-A47 on an
answer naming its source and window; this is the same rule for a denominator.

Ban list checked on this entry.
