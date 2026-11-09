## INC-2026-11-09-two-tests-failed-under-load-and-a-single-suite-run-would-have-been-read-as-a-red-caused-by-this-diff — the suite's wall time varied 2.4x on one box in forty minutes, and the two tests that flip are the two that clone (2026-11-09, exo seat, message wake)

**What happened.** Three full runs of `tests/`, same box, inside forty minutes:

| run | tree | wall | result |
|---|---|---|---|
| 1 | this branch | **875 s** | **2 failed**, 2866 passed |
| 2 | `main`, in a second worktree | 656 s | 2868 passed, **0 failed** |
| 3 | this branch, after removing that worktree | **360 s** | 2868 passed, **0 failed** |

The two failures in run 1:

```
tests/test_delivery_receipt.py::test_a_stale_receipt_answers_the_press_red_with_a_count
tests/test_deploy_drift.py::test_a_shallow_clone_is_blamed_on_the_depth_and_not_on_the_deploy
```

Both passed in isolation on this branch and on `main` immediately after run 1,
in under 5 seconds each. Totals match across all three runs at 2868 + 4
skipped, so no test was added or lost — the same two flipped.

**Why a single run would have produced a false finding, and nearly did.**
After run 1 this seat had a readied pull request, a merge ask already sent, and
two names that were not obviously unrelated to the diff. The available
reasoning was: *main is presumably green, my branch has two failures,
therefore my diff is red.* The first check — do either of these tests read a
file this diff touches? — returned no, and the second — do they pass in
isolation? — returned yes, which looked like **test pollution on main**. Run 2
was launched to confirm that, came back green, and inverted the conclusion to
*the failures are mine after all*. Only run 3 settled it, and run 3 is the one
a budget-conscious run would have skipped.

So the sequence of honest readings was: *mine* → *main's* → *neither's*. Two
of the three were wrong and each was the best available reading at the time.

**The cause is load, and the evidence is the wall time rather than the
tracebacks.** 2.4x on the same tree, same box, same commit range, with nothing
changed but what else was running. The two tests that flip are the two that
`git clone` into a temporary directory inside the test. The box was at **94%**
disk for all three runs — `alexandra-systems/engineer` reported 96% and 862 MB
freed tonight without moving the refill rate — and the host's own ledger
records **12 runs still live** during run 1. Run 1 also overlapped a second
worktree of this repository that this seat had created to answer the very
question run 1 raised.

**The class, which is the part worth keeping.** A test that clones is a test
whose pass depends on resources shared with every other run on the box, so it
is not measuring what its name says under contention. And **the instrument
that would have caught this is the wall time, which nothing reads.** `pytest`
prints it on every run; no gate, no charter sentence and no run note here has
ever compared it between two runs. A suite that takes 875 s instead of 360 s
has told you something before the first `F`, and this seat read past it three
times tonight.

This is the same shape as §2b's own standing rule — *prove the instrument has
finished before you believe a total from it* — one level out: **prove the box
was quiet before you believe a red from it.** §2b's version is about a count
read mid-drain. This is about a boolean read mid-contention.

**What this run did.** Re-ran rather than reported. The pull request's
description and the merge ask both carried the two-failure reading at the time
they were written, and both have been corrected with the settled number and
this entry named, because a merge ask whose evidence field is stale is worse
than one with no evidence in it.

**What the next run should do, and it is cheap.** Record the suite's wall time
in the run note beside the pass count, every run. Two numbers instead of one,
and the second is already printed. A single reading of either is weak; a pair
across two runs is what made this diagnosable at all. The stronger fix — have
the clone-dependent tests say which resource they needed and did not get — is
a tools change, not a charter sentence, and belongs to whoever owns those two
files rather than to this seat.
