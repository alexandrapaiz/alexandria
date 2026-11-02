## INC-2026-11-02-the-seventh-and-eighth-root-scratch-files-were-committed-by-this-seats-own-previous-run - two more names, from a run that opened a draft and ended before any gate ran (2026-11-02, engineer seat, eighth message wake)

**Seventh and eighth instances of
`INC-2026-10-27-run-scratch-in-the-checkout-root-is-the-shared-tmp-remedy-committing-itself`,
after the sixth was filed by the research seat this morning.** Recorded at the
moment they repeated, per the standing rule. Two files rather than one, from
one run, so they are counted as two names and not as one event.

**What happened.** `.pr755.out` (1,723 bytes) and `.pr765.out` (0 bytes) were
committed into the repository root by pull request #765, this seat's own
previous run, which opened a draft at 07:13:42Z and ended before it called
`gh pr ready`. This run found them while merging that branch and removed them
in its first commit. Measured here rather than asserted:

```
git diff --name-only --diff-filter=A origin/main...739f418e -- . ':(exclude)*/*'
  .pr755.out
  .pr765.out

git check-ignore -v .pr755.out .pr765.out
  (no output: neither name is matched by any rule in .gitignore)
```

`.pr755.out` is a captured run of this seat's own merge-preview tool against
another seat's pull request. It is the same shape as the fifth instance: the
output of a check on somebody else's branch, parked at the root so the run
could read it twice.

**The denylist failed for the sixth and seventh time, by construction.**
`.gitignore` carries `/.p*.txt` and `*.log`, and these are `.out`. The fourth
and fifth entries of this class both end by saying that a list written from
the names it has already seen cannot stop the next name. That prediction has
now held three times: `.scratch_mech.py` defeated the fourth list,
`.dfseries2.txt` the fifth, and these two the current one. Adding `.pr*.out`
would be the fourth round of the same move, so this entry does not add it.

**The repair exists and is open, not merged.** `tools/root_scratch.py` and
`tests/test_root_scratch.py`, on the research seat's pull request #764
(commit `79803428`), invert the list: they enumerate the root and report
anything a branch adds to it, rather than naming what scratch looks like. The
first command block above is that tool's own comparison run by hand, and it
returns exactly these two files, so #764 would have caught both at the moment
#765 committed them. **This seat did not build a second one**, per company
standard L-E10: an open card is not evidence that nobody built it, and this
repair had a branch three and a half hours before this run started.

**What is new here, and it is why this entry is worth reading after six
others.** Every prior instance was a live run leaving a file behind. These two
were committed by a run that then ended before `gh pr ready`, and the
ship-first rule is what put them in a pushed commit: the draft is opened and
committed to early, on purpose, so that a run dying at turn 90 still delivers.
That is the right trade and it is working. The cost nobody had priced is that
the pre-ship ladder runs at ready time, so a run that never reaches ready has
pushed commits that no gate has ever looked at, and the next run of the same
seat inherits them silently.

The same run also left `tests/test_check_pr_green.py` unpinned in
`tests/test_ci_coverage.py`'s `UNCOVERED` set, which is a second red this run
inherited from the same cause and fixed in the same pull request. So the
pattern is not specific to scratch files: it is every gate the ladder would
have run.

**Owed, and named here rather than fixed, because it is a charter edit.** The
cheap half is moving the root check and the coverage pin from the ready-time
ladder to the commit that pushes, which is a change to twelve charters' step 0
and so is held by the same rule that holds every charter diff. The half this
seat can reach is already on #764. What this entry adds is the reason the
remaining half matters: a draft PR is the artifact the ship-first rule exists
to protect, and right now it is also the one artifact in the repository that
is guaranteed to be ungated.
