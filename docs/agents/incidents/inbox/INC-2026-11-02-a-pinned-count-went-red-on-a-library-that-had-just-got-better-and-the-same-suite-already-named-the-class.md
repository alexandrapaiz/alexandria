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
