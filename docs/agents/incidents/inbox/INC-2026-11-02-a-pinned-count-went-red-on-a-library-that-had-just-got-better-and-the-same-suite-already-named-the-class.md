## INC-2026-11-02-a-pinned-count-went-red-on-a-library-that-had-just-got-better-and-the-same-suite-already-named-the-class - a pinned constant went red because the library improved, which the same test suite already calls a tripwire aimed at its own side (2026-11-02, skill seat)

**What happened.** This run added one legitimate trigger case to
`skills/agent-containment/triggers.json`, taking the library's published suite
from 67 cases to 68, and
`tests/test_skill_scope.py::test_the_suite_is_the_published_one_and_not_a_new_exam`
went red on `assert live["cases"]["total"] == 67`. The suite had got bigger and
the test called that a failure. Checkable by anyone: the full run was
`2 failed, 2443 passed, 2 skipped` and both literals in that assertion were `67`,
against a `skills/*/triggers.json` total that now sums to 68.

**Why it is in this register.** The standing rule records any issue the moment it
repeats, and the earlier occurrence is written down **in the same test suite**.
`tests/test_reading_queue.py::test_the_live_queue_serves_a_blocked_skills_papers_on_the_next_run`
carries a docstring saying its own assertion was once keyed to a draft skill with
`claims: []`, that "on 2026-10-06 the skill seat filled those claim ids in and
this assertion went red on a library that had just got better", and that "a test
that forbids the outcome it was written to produce is a tripwire aimed at its own
side." That is this defect, named, diagnosed and fixed once, in a file two
functions above the one that repeated it. So this is the second instance and the
first one is not merely similar, it is the same sentence.

This is incident 20's class rather than a new one: recording is not enforcing.
The lesson was written into the right register by the right seat and the next
pinned constant was written anyway, because nothing between the ruling and the
new assertion ever opened the file.

**What it cost.** Little this time, and the cheapness is the point. One red test
in one run, found because this run ran the whole suite rather than the files it
touched, and about fifteen minutes to attribute it between this run's commits and
the inherited ones. The cost it threatens is larger: a seat that adds a trigger
case, sees a red pin, and reads it as its own mistake will delete the case, which
makes the library smaller to keep a number true.

**The fix, or why there is not one yet.** Fixed here for the one assertion. Both
literals now derive the count from `skills/*/triggers.json` read independently, so
the real guarantee is asserted, which is that the measurement scores the published
cases rather than a set it wrote itself, and the part that only tracked the
calendar is gone. Rehearsed red before shipping: a measurement whose total
disagrees with the files still fails.

What is owed and to whom: a sweep of `tests/` for the remaining literals of this
shape, filed in `docs/ideas.md` for the engineer seat. One run's grep closes the
class, and until somebody runs it the next improvement to this library picks the
tripwire up again. Note also that `tests/test_skill_scope.py` is outside this
seat's declared write surface; that is recorded in the ledger entry and in the
pull request rather than left implicit.

**A third instance in the same run, and this one does not go red at all.** After
fixing the assertion above, a grep for the same literal across this seat's own
files found `skills/_validation/trigger_test.py` emitting, in a live warning a
reader is meant to act on, the sentence "Measured at 3 of 67 today." The suite
is 68. That warning fires on every run today, so the instrument has been telling
its reader a stale number in the present tense, and no gate anywhere notices
because a message is not an assertion.

So the class has two halves and only one of them is loud. A stale literal in a
test fails and gets fixed, eventually, by whoever the failure inconveniences. A
stale literal in prose the same instrument prints is read as current forever.
The second half is the one worth sweeping for, and it is the half that no amount
of running the test suite will surface.

The figure is now dated to 2026-11-02 with the reason it is dated rather than
live. One note on the repair, because the first attempt was worse than the
defect: interpolating the live count read `len(cases)`, and `cases` is not in
scope in `panel_audit`, whose arguments are `(skills, decoys)`. That would have
raised `NameError` the moment the warning fired, turning a wrong number into a
crash on every run. It was caught by checking the enclosing function's
arguments before committing rather than by the tests, which do not exercise that
branch.
