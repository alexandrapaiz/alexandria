## INC-2026-10-27-a-cut-off-run-left-seven-tests-below-the-runner-block-and-the-gate-that-catches-it-runs-in-no-workflow — the stranded-test class recurred on this seat's own branch, and only a hand-run full suite could see it (2026-10-27, engineer seat)

**What happened.** The engineer seat's run of 2026-10-27T01:21:13Z was cut off
at turn 143. Its last commit, `5c890a73`, added `fetch_arxiv_ids` and seven
tests for it, and it appended all seven to the end of
`tests/test_arxiv_window.py`, which is below that file's
`if __name__ == "__main__"` block at line 392. The run never reached the full
suite, so it never saw that its own last commit had turned
`tests/test_ci_coverage.py::test_no_test_file_strands_a_test_below_its_runner`
red. The capacity-return run that continued the branch ran the suite and got
three failures; two reproduce on a clean `origin/main` worktree and are already
filed, and this third one does not. `test_ci_coverage.py` passes on `main` and
failed on the branch, which is the whole proof that the chain introduced it. The
seven tests pass under `pytest`, because pytest imports the module and collects
by name, so nothing about the failure is visible from the suite result of the
one file the work was in.

**Why it is in this register.** This is the second occurrence of the class. The
first was 2026-10-14, four tests across `tests/test_deploy_drift.py` and
`tests/test_delivery_receipt.py`, recorded inside
`INC-2026-10-14-the-two-apps-the-drift-guard-could-not-see`, and one of those
four asserted the wrong reading of the drift guard while nothing executed it.
That entry's own fix was the gate that caught today's. So the gate works, and
the thing worth recording is not the stranding. It is that the gate is
unreachable from any workflow: `tests/test_ci_coverage.py` is the first line of
its own `UNCOVERED` set, because adding a step to `checks.yml` needs a
`workflows` permission no seat holds, and `tests/test_arxiv_window.py` is not
named in `checks.yml` either. So a seat shipping a stranded test gets no red
tick on its pull request, and the only reader is a hand-run full suite. Today
that reader existed by accident, because a cut-off run happened to be continued
by a run that reruns everything. A run that merges cleanly is the ordinary case
and it would have carried this to `main` in silence, where a direct
`python3 tests/test_arxiv_window.py` would print a pass over seven tests it
never ran.

**What it cost.** Nothing in production, because the continuation caught it
inside six hours and before any merge. One commit to repair. The cost that is
worth the owner's attention is the same one item 17 of
`tests/test_ci_coverage.py` has been asking for since 2026-10-13. Sixty-four
files in `tests/` are pinned as run by no workflow, counted off `UNCOVERED`
rather than estimated, and two of the sixty-four are the gate against exactly
this and the file it just caught.

**The fix, or why there is not one yet.** The runner block in
`tests/test_arxiv_window.py` moved to the end of the file, which is the same
repair the 2026-10-14 entry applied to the two files it found, and
`test_ci_coverage.py` is green again. The half that is not fixed is the reach of
the gate, and it is not fixable from this seat: it needs the staged replacement
in `.github/workflows-pending/checks.yml` applied, whose own first comment says
the fourteen named pytest steps become one step that runs the suite, and that is
a `git mv` plus a `workflows` permission. Recorded here
rather than attempted, per the charter's rule that a seat cannot push a workflow
file and should file what it finds instead.
