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
