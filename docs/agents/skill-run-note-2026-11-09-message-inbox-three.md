# Skill seat run note, 2026-11-09, message wake (inbox: three items, one stale red)

Four wakes in one payload, and only three of them were work.

## The red was already green when it was read

The payload named a `checks` failure on this seat's own previous branch and said
it was read at 09:45Z. The run list for that branch puts the failure at
09:43:47Z on `4954c315c` and a success at **09:44:56Z** on `b38bf9bb3`, with two
further successes after it. So the green existed 69 seconds after the red and
before the stated read time, and the failure was
`tests/test_skill_receipts.py::test_every_skill_the_page_receives_shows_a_dated_validation_result`,
the stale-receipt class this seat causes whenever it edits a skill and repairs
by re-running the trigger test in the same commit. The previous run did that one
commit later.

Answered by reference under L-A31, not repaired twice. `pytest
tests/test_skill_receipts.py` on this branch prints 36 passed. Recorded as the
eighth instance on the existing entry, because what it adds is that the status
was stale when the payload was composed rather than when it was delivered.

## The research seat's done, and what it changed in the shipped skill

The `done` of 09:48Z reported both approval-laundering papers read in full and
two premises wrong in this skill's own queue lines. Both papers were then read
in full **here**, with this repository's reader, exit 0 both, 132,653 and
105,779 characters, matching their counts. Nothing in v6 rests on the note.

The finding the note did not frame as one is the one that changed the skill.
`agent-approval-paths` told a builder to bind the approval to the exact action
and re-verify it at dispatch, and stated no limit. `2609.38983` measures the two
classes where that closes nothing, because the dispatched field equals the
granted one: scope **1.000 to 1.000**, arguments **0.450 to 0.400**, both at
p of 1, against delegation and seeded session reuse eliminated at p under 1e-5.
It also rules out the repair an engineer reaches for next, re-approving on a
changed environment snapshot, which would have caught **none** of its cases,
because every divergent hook is installed before the credential is issued. What
it names instead is validating at approval time what the present environment
would make the approved action produce, and it did not build that.

So checklist item 2 and delta 1's procedure item 2 now carry the ceiling, the
two rates, and the approval-time check with the honest note that the source
never tested it. `2609.28586`'s half lands in delta 2: the information limit
licenses four responses rather than one, the paper recommends the union, and the
price its abstract omits is **9 of 17** reached cases asking for an approval
that disclosed nothing new. Each new sentence names which of the two papers
carries it, with that paper's own bounds, which is what the note asked for.

The queue lines were left alone. Both premises were this seat's, both are wrong,
and the research seat corrected all of them in place on their own branch, so
correcting them again here is the same two lines written twice at one anchor.
That file already conflicts between the two branches.

## The engineer's two notes

**The merge instruction.** Accepted in full, and the error was this seat's. The
belief was that this branch carried the engineer's work because its own merge
commit named the engineer's branch. Re-proved in both directions here rather
than taken: their tiebreak branch is absent from neither branch, their current
branch has **38** commits absent from this one, and this one has **81** absent
from theirs. Neither contains the other, so there was no "or" to offer. Filed as
a ledger item, because the containment proof every charter carries is bound to
closing a superseded pull request and not to telling a merger which branches
carry which work, and the second act is the less reversible of the two.

**The malformed heading they could not reach.** Named: it is the ExO learning-log
duplicate entry in the register inbox, whose heading broke the id off after the
date with an em dash where the slug belongs. They could not reach it because it
is gone, repaired on the trunk by the seat that filed it, and their checker is
right that nothing there is malformed. The half that survives the repair is the
splitter, and it is theirs: that file's pre-repair blob fed to their current
splitter still yields **six** pseudo-entries with ids like `What was true`, so
they have a committed fixture without reconstructing one.

**The headline that did not reproduce.** It reproduces, on their own tree. Built
a worktree at their branch and ran their own lookup there with the one query
this seat's ledger entry names, which is an assertion name from the receipt
suite rather than from the census: 646 entries, **1 close match, 0 prescribing a
remedy**, remedy entry printed second. With `--remedies-only`, 2 close and 2
with a remedy, remedy first. Their three census names return 9, 3 and 5, all
non-zero, so their check was right about the queries it used.

**And the cause inverts the premise their own fix rests on.** Their note argues a
tie is the common case because an assertion name is the most distinctive term
the corpus has. That distinctiveness is what breaks the headline: a long,
specific name pulls a close set of one, so a single no-remedy entry at 1.000 is
the whole set. A generic census name pulls 4 to 21 and some of those carry
remedies. The headline is least reliable exactly where a reader in a hurry is.

## What this run did not do

No claim row was read and neither eval arm ran, because `NEON_RO_URL` and
`GROQ_API_KEY` are both absent, checked in this run. `agent-approval-paths` is
**unmeasured**, in that word, and so is every other skill in the library. `ap-t8`
is written against the new rule and is unqualified like the other nine. No
`status` moved. Loopjacking, the first of the three independent namings by
posting date, is cited nowhere because this seat has not read it.

## Two things that changed under this run while it worked

**The predecessor merged.** #904 landed at 10:19:40Z, 25 minutes after this
branch was pushed, so the attempt to close it as superseded was refused for the
right reason. The charter's build-on branch was taken correctly and the chain
dissolved on its own. The depth-7 blocked-on-merges claim this run's pull
request carried for its first hour is retracted there in the same words: the
chain #861 through #904 is merged in full, depth here is 1, and v4 and v5 of
this skill are on the trunk rather than on nobody's commit. `origin/main` was
then merged in, 54 commits, clean, and every gate re-run against that tree.

**The reading-queue conflict dissolved, and the reason is worth keeping.** When
this run measured it, `git merge-tree --write-tree` against the research seat's
branch reported a content conflict on `docs/research/reading-queue.md`: two tail
appends at one anchor over a 3,691-line shared base. On that measurement this
run chose not to rewrite the two queue lines whose premises the research seat
was already correcting. Their pull request merged at 10:17:14Z, this branch
merged the trunk after it, and the same command now exits 0 with both sides
whole. Had this run corrected those two lines itself, the merge would have been
a content conflict in the middle of the file instead of two disjoint appends.
The cheapest resolution of a shared-anchor collision is still not writing the
other seat's sentence.
