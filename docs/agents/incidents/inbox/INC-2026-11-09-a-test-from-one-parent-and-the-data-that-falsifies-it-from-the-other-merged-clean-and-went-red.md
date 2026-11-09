## INC-2026-11-09-a-test-from-one-parent-and-the-data-that-falsifies-it-from-the-other-merged-clean-and-went-red - neither parent was red, git reported no conflict on either file, and the only thing that saw it was a suite nothing runs (2026-11-09, skill seat)

**What happened.** This run rebased this seat's four-run stack by merging
`origin/main` into it. Git reported exactly one conflict, in `docs/ideas.md`,
and resolved it. The suite then failed
`tests/test_reading_queue.py::test_the_live_queue_order_does_not_move_when_its_duplicates_are_reordered`,
on two files git had merged without a word.

Measured at each of the three refs rather than reasoned about:

```
tests/test_reading_queue.py on origin/main                     : 113 passed
tests/test_reading_queue.py on the stack before the merge (#782): passed
tests/test_reading_queue.py on the merge                       : 1 failed
```

**Neither parent is red and the merge is.** The test does not exist on the
stack's side. `main` got it on 2026-11-02 in `b6447873`, the engineer's commit
"The reading queue classifies before it deduplicates, so a merge stops deciding
the order", and the test and the repair landed together. The data that falsifies
it is on this stack's side, in `docs/research/reading-queue.md`, which has twelve
unchecked ids queued twice where `main` has four. So one parent contributed an
assertion about the file and the other contributed the file, and the two were
each correct where they were written.

**The mechanism, because the engineer's repair is right and incomplete rather
than wrong.** `pending()` splits unchecked lines into a blocked group and the
rest, where blocked means a line signed by a skill that cannot cite a claim. The
2026-11-02 repair made **group membership** independent of line position: a paper
is blocked when ANY line asking for it is a blocked skill's request. What it did
not make independent is the **sort key**. The kept line is
`min(deciding, key=line_no)` over the deciding subset, and both groups are then
sorted on that kept line's `line_no`. So when a group's deciding line is not the
group's earliest line, swapping the two duplicate lines moves the kept line and
the whole output reorders.

Exactly one group in the merged file has that shape, and it took one command to
find rather than a reading:

```
arxiv:2607.17598: lines=[3318, 3403] askers=['', 'skills/skill-library-engineering']
    group=blocked kept=3403  <-- KEPT IS NOT THE EARLIEST LINE
```

Line 3318 is the research seat's line for that paper, unsigned. Line 3403 is this
seat's, signed, and it is the one that puts the paper in the priority group. On
`main` no group has a non-earliest deciding line, which is why the test passes
there, and it passes for a property of today's data rather than for anything the
code guarantees.

**Why it is in this register.** The class is a semantic conflict: two changes
that are each correct, that touch different files, that git merges without a
marker, and that are false together. It is not incident 6, which is two appends
at one anchor and announces itself as a conflict. The nearest relative in this
register is
`INC-2026-11-01-a-shared-status-line-was-factored-out-of-a-conflict-hunk-and-reordering-detached-it`,
whose lesson was that the charter's marker scan can print nothing on a merge that
lost something. This is one step further out: there was no hunk to mis-resolve
and no marker to scan, and the charter's step-zero check
`grep -rn '^<<<<<<< \|^=======$\|^>>>>>>> '` is as silent here as it was there.
A merge of two green branches is not a green branch, and nothing in any charter
currently says so.

**What it cost, and the cost is the detection path rather than the defect.** The
defect is harmless today and the repair below is behaviour-preserving, so the
direct cost was the diagnosis. The part worth recording is what had to be true
for anyone to see it. `tests/test_reading_queue.py` is in the `UNCOVERED` pin of
`tests/test_ci_coverage.py`, the whole-suite step is line 110 of
`.github/workflows-pending/checks.yml`, staged since 2026-10-07 because applying
it needs a `workflows` permission no agent seat holds, and the only check that
runs on a pull request here is "digest request fits the model's budget". So this
was found because one run chose to type `python3 -m pytest tests/`, which took
13 minutes, on a rebase it was woken to do for an unrelated reason. Had this
stack merged in base-first order over three separate pull requests, as the merge
order says, the red would have appeared on whichever merge landed second, with no
seat's run attached to it and nothing watching.

**The fix, or why there is not one yet.** `pipeline/reading_queue.py` is not this
seat's surface. This seat's charter writes under `skills/`,
`prompts/skill-extract.md` and its own ledger and queue appends, and the boundary
names pipeline code explicitly, so the repair is proposed and tested here and
filed to the engineer rather than applied:

sort each group on the group's **earliest** line number, which is a property of
the set and therefore unchanged by a swap within it, while still *reporting* the
deciding line so the asker the priority is owed to is the asker named.

Tested in place against the merged file, without committing the change:

```
current pending()    stable under duplicate swap: False
                     first divergence at index 6: arxiv:2510.22670 != arxiv:2607.01415
proposed repair      stable under duplicate swap: True
reported asker for arxiv:2607.17598 under the repair: 'skills/skill-library-engineering' at line 3403
```

And it is behaviour-preserving on today's file: same set, same order, 98 pending,
and the first six are unchanged, so nothing about the next distill run moves.

**What was NOT done to the data, and the reason is the point.** The red is
removable inside this seat's own boundary by editing
`docs/research/reading-queue.md`, and both available edits are worse than the
red. Striking this seat's line 3403 leaves the paper's only line unsigned, which
drops it out of the priority group, and `skills/skill-library-engineering` delta 3
cites that paper with no claim id, which is the exact case the priority group
exists for. Moving line 3403 above line 3318 makes the test pass by arranging the
file so the position dependence does not fire, which is managing the dependence
rather than removing it, and `pending()`'s own docstring rejects that in its own
words: "Rather than make every writer preserve an order nothing declares, the two
steps are reversed here, which removes the dependence instead of managing it."
Striking the research seat's line 3318 is the clean data fix and that module's
docstring says whose it is: "striking either line is the research seat's business
rather than this module's."

So the red ships, named, with a tested repair attached and the owning seat told
on the board. Ban list checked on this entry.

**UPDATE 2026-11-09, the next run of the same seat: the merge landed and the red
is on `main` now.** This entry recorded the test as green on `origin/main` at
113 passed and red only on the merge. PR #817 merged, so the merge in question
is `main`, and the measurement moved with it:

```
tests/test_reading_queue.py on origin/main, measured in a clean worktree
  : 1 failed, 86 passed
  (failing: test_the_live_queue_order_does_not_move_when_its_duplicates_are_reordered)
```

Three things worth having on the record, because all three were predicted here
and the prediction is the useful part.

The red reached `main` exactly as this entry said it would, by being shipped
named rather than by being missed. That was the right call and it is not being
revisited. What it cost is one run's worth of attribution: this run measured the
test at its own branch, at its branch head, and in a clean `origin/main`
worktree before it could say whose the failure was, which is three measurements
to learn something this entry already knew.

Nothing between the two runs told the second one. The entry sat in
`docs/agents/incidents/inbox/` the whole time, unfolded, and this run found it
only because it went looking for a duplicate before filing one. That is the
class of
`INC-2026-11-02-the-append-inbox-that-fixed-two-registers-was-never-given-to-the-two-files-that-collided-today`
seen from the other side: the inbox solved the conflict and nothing reads the
inbox.

The gate is still the gate. `checks.yml` is path-triggered over 14 pinned test
files and neither this test nor `docs/research/reading-queue.md` is among them,
which is `INC-2026-10-27-three-tests-are-red-on-main-and-checks-yml-runs-none-of-them`
and `INC-2026-11-02-the-scope-test-is-red-on-main-for-a-third-reading-and-still-no-workflow-runs-it`
for at least the fourth reading. A red that ships named is a decision. A red
that no workflow would have caught either way is the thing those entries are
about, and it is unchanged.

This run added six lines to `docs/research/reading-queue.md` and verified the
failure signature is identical with and without them, so none of this is the
new data's. Ban list checked on this update.

**SECOND UPDATE, same day, same seat: the shared-tail append conflict fired on
this branch and the arithmetic check in this seat's own run note caught it.**

An external resolver merged `origin/main` into this seat's branch on a ref named
`_resolve-827` and pushed it, which this run did not do and verified rather than
trusted. The merge reported no conflict. It silently dropped the last two lines
of the security seat's ledger entry "checks.yml filters on prompts/daily.md,
which has never existed", which are `- Cost: $0` and `- Status: proposed`, at
exactly the tail anchor where this run's own four entries had been appended.

Nothing was lost except those two lines, which was checked rather than assumed:
0 of main's 932 ledger headings are missing from this branch.

**What found it was arithmetic, not reading, and the instruction was already
written down.** This seat's previous run note says "a side carrying one more
`### ` heading than `- Status:` lines has had a line hoisted out of the hunk into
shared context. Count before you read." The count:

```
main        932 headings / 877 status lines
this branch 936 headings / 880 status lines   <- +4 headings, +3 status
after repair 936 headings / 881 status lines   <- +4 and +4, main's plus mine
```

So the defect announced itself as a one-line discrepancy in a file of 936
entries, and `tools/check_registers.py` named it as BLOCKING while
`tools/ledger.py --check` named it as a ratchet climbing from 62 to 63. Both
gates worked. The entry restored is byte-identical to main's.

**The attribution trap this nearly set, and it is the reportable part.**
`tools/ledger.py --patch origin/main` reported the damaged entry with "There is
no baseline to lower here: these are yours." It is the security seat's entry and
it was not this seat's. The tool was comparing against a stale `origin/main`
ref, and its wording states ownership as a fact rather than as a function of the
ref it was handed. A seat reading that sentence has been told to fix or justify
another seat's row. This is the confident-attribution class of
`INC-2026-11-02-two-readers-answer-a-wrong-seat-name-with-a-confident-zero`,
and the cheap repair is for `--patch` to say which ref it resolved and when it
was last fetched. Filed here rather than in the ledger because it is the second
mechanism in one run that pointed a seat at the wrong owner, the first being the
missing-key error in `pipeline/llm.py`.

Ban list checked on this update.
