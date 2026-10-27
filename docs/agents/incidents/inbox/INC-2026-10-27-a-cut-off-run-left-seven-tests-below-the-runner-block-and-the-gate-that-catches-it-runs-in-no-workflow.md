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

**And the repair found the larger half.** Moving the block restores a path, so
the next question is whether the path runs, and for this file it did not.
`tests/conftest.py` installs the Modal stub for the whole suite and only pytest
loads a conftest, while `modal` is declared in `requirements.txt`, which
`checks.yml` never installs: it installs `tiktoken` and `requirements-dev.txt`
and nothing else. So any test file whose module-level code imports a `pipeline/`
module reaches `import modal` with nothing standing in for it. The repository's
answer is the in-file guarded stub that `conftest.py`'s own docstring says is
left in place on purpose, because a file documenting a direct run "still has to
work with no conftest involved". Nothing checked that it did. Thirteen files
carry a runner block and two could not execute it: `test_arxiv_window.py` had no
stub at all, so the seven tests freed above were freed into a traceback, and
`test_triage_planner.py` had one spelled as nested namespaces exactly as deep as
`pipeline/triage.py` chained on the day it was written, so a later
`add_local_file` in that pipeline broke a test file that never changed. Both
failed at import, which means a direct run printed a traceback rather than a
wrong pass, and the suite stayed green throughout because pytest never takes
that path.

**The fix, or why there is not one yet.** The runner block in
`tests/test_arxiv_window.py` moved to the end of the file, which is the same
repair the 2026-10-14 entry applied to the two files it found, and
`test_ci_coverage.py` is green again. Both stubs are now spelled as the
self-returning image idiom `conftest.py` and `test_email_template.py` already
use, so a longer builder chain in `pipeline/` cannot break them again, and both
direct runs pass at 31 tests and 9. A new assertion,
`test_every_file_with_a_runner_block_can_run_without_the_conftest`, imports each
such module under its own name in a clean subprocess, so module-level code runs
and the runner block does not fire; thirteen files in eight seconds. It was
proved by reverting the triage stub, where it names the file and the
`AttributeError` and goes green again on restore. The half that is not fixed is the reach of
the gate, and it is not fixable from this seat: it needs the staged replacement
in `.github/workflows-pending/checks.yml` applied, whose own first comment says
the fourteen named pytest steps become one step that runs the suite, and that is
a `git mv` plus a `workflows` permission. Recorded here
rather than attempted, per the charter's rule that a seat cannot push a workflow
file and should file what it finds instead.
