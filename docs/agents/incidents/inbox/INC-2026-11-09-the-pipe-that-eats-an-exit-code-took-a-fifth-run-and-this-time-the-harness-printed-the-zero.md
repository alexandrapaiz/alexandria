## INC-2026-11-09-the-pipe-that-eats-an-exit-code-took-a-fifth-run-and-this-time-the-harness-printed-the-zero - the class reached a shape no pipefail line reaches, because the zero came from the tool wrapper rather than from a shell variable (2026-11-09, engineer seat)

**What happened.** This run put the full suite in the background as
`python3 -m pytest tests/ -q -x --basetemp=... 2>&1 | tail -15`. It came back
with `1 failed, 2349 passed` in the body and `[exited with code 0]` on the last
line, printed by the tool wrapper rather than by any `echo $?` this run wrote.
Nothing in the command read an exit code, so no `set -o pipefail` in the
command text would have changed the line that lied.

**Why it is in this register, and it is the fifth instance.**
`INC-2026-11-02-a-probe-of-an-exit-code-piped-it-into-tail-and-read-the-pipes-exit-instead`
recorded the first two, four hours apart.
`INC-2026-11-09-the-pipe-that-eats-an-exit-code-took-a-third-seat-run-and-it-was-the-seat-that-filed-the-first`
recorded the third, and
`INC-2026-11-09-the-pipe-that-eats-an-exit-code-took-a-fourth-run-and-it-was-the-run-after-the-one-that-predicted-it`
recorded the fourth, which was this seat's immediately previous run with the
third entry already merged to `main` and readable in the clone.

**What this instance adds, and it is why the recorded remedy does not cover
it.** The four earlier instances are all a seat writing a command that reads
`$?` after a pipe, and the fix for all four is one line the seat types:
`set -o pipefail`, or `PIPESTATUS[0]`, or a redirect instead of a pipe. This
one has no such line, because the exit code was reported by the harness that
ran the command, which sees the pipeline's status and has no way to know the
seat cared about the first stage. A seat reading `[exited with code 0]` has no
local edit available. The only remedy is not to pipe a gate at all when the
harness is the thing reporting its result, which is a different instruction
from the one on record.

**What it cost, and the save was again the reader rather than the gate.** The
body said `1 failed` three lines above the zero, so the contradiction was
visible. That is three instances in a row where the output disagreed with the
exit code loudly enough to be noticed, and the fourth entry already named
relying on that as the thing to stop doing.

**What the failure actually was, since it matters for the remedy.** The red
test was `tests/test_root_scratch.py::test_this_repository_is_clean_at_the_root`,
and it was correct: this run had put its measurement base directories at the
repository root. So a run that had believed the zero would have shipped scratch
directories into a pull request, which is the class
`tools/root_scratch.py` exists for. One lying exit code nearly defeated the
gate for a different class entirely.

**The remedy this entry proposes, narrow and additive.** The recorded fix
stands for a seat reading `$?`. Add one sentence to it: when the harness
reports the exit code rather than the shell, redirect the output to a file and
read the file, because there is no pipefail available at the boundary where the
report is made. Written here rather than in a charter because every charter in
this repository is held by a rule it corrects, and the ledger already carries
the proposal to move the general version into a charter as
`2026-11-09-a-pipefail-line-belongs-in-the-charter-not-in-a-register`.
