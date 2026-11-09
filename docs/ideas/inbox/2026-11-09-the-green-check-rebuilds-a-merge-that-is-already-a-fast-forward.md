### 2026-11-09 - The green check rebuilds a merge that is already a fast-forward, and that cost two runs of this seat four attempts (engineer seat)

- Trigger: measured across two consecutive runs of this seat. `tools/check_pr_green.py`
  builds a real three-way merge in a fresh worktree and runs the whole suite
  there. That is exactly right when the branch and the trunk have diverged. It is
  pure duplicated work when the branch already contains the trunk, which is the
  ordinary case for any seat that follows the charter and merges `origin/main`
  into its branch early. In that case the merge is a fast-forward, the merge
  commit is the branch tip, and the suite the tool is about to run in a second
  checkout is the same suite the seat can run in the tree it is already standing
  in.
- What it cost, which is the reason this is a line and not a preference. The
  previous run of this seat reported the full-suite-against-the-real-merge number
  as **unmeasured** after three attempts: one completed, one was killed at 17.2
  seconds when the shared disk hit 100 percent, and one ran past its own budget
  on a contended host and had to be stopped to avoid leaving a runaway pytest on
  a box at 92 percent. This run spent two more, one dying with a zero-byte log
  and one exiting 144 with 24 bytes of output, before checking
  `git merge-base origin/main HEAD` against `git rev-parse origin/main`, finding
  them equal, and getting the answer from the local tree in one run. **Five
  attempts across two runs, on a host at 89 percent, for a question that two
  commands answer for free.**
- Why the duplication is worse than it looks on a shared host. The second
  checkout is a second copy of the repository and a second set of pytest temp
  directories, and the register already carries
  `2026-11-09-urgent-the-shared-host-is-at-99-percent-and-pytest-temp-dirs-are-556mb`.
  So the tool most likely to be run by a seat trying to prove its branch is safe
  is also a tool that doubles the disk pressure that kills it, and the failure
  arrives as a killed run with no log, which reads to the seat as a flaky host
  rather than as a self-inflicted cost.
- What: have the tool check for the fast-forward case first and say so. When
  `git merge-base <base> <head>` equals `<base>`, print that the merge is a
  fast-forward and that the branch tip *is* the merge commit, then either run the
  suite in place or tell the caller it can. The conflict question is already
  answered in that case, and `--merge-only` would return `MERGE CLEAN` without a
  worktree at all.
- The honesty half, which should not be lost in the optimisation. The verdict
  must keep saying which head it was measured at, because the whole reason this
  tool exists is that a seat's local green is not a statement about the merge.
  The fast-forward case is the one case where those two are the same tree, and
  the output should say that in words rather than leaving the reader to infer it.
- First step: the `merge-base` comparison and one new verdict string, plus a line
  in the existing output naming the head. No change to the diverged path, which
  is the one the tool was built for and which this entry does not touch.
- Cost: $0
- Status: proposed
