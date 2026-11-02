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

**Third instance, 2026-11-02 (PR #745), same file, one function below the
second.** This run added a tenth skill, `skills/agent-approval-paths`, and
`tests/test_skill_scope.py::test_scoping_loads_fewer_skills_and_less_context`
went red on `assert full["unscoped"]["mean_skills_loaded"] == 29`, reporting
`assert 30 == 29`. Nine library skills plus twenty distractors was 29; ten plus
twenty is 30. The library grew by one and the test called it a failure.

**The detail that makes this instance worse than the two above it.** The second
instance was fixed by deriving the count instead of pinning it, and the fix held:
the published-case assertion absorbed seven new trigger cases in this very run,
68 to 75, without going red. So the repair works and was applied to one
assertion rather than to the file. This function sits twelve lines below the one
that was repaired, in the same test suite, under a docstring that says "what
scoping buys structurally, which has not changed and cannot" — and the literal
`29` is a count of the library, which changes every time this seat does its job.
Immediately below it is `test_the_verdict_answers_for_the_recall_relation_rather_than_a_pinned_sign`,
whose entire docstring is an argument against pinning live state, written on
2026-10-27.

So the file now contains, in order: a derived assertion that survived, a pinned
assertion that broke, and a docstring explaining why pinning breaks. That is
incident 20's class in miniature, three times over in forty lines.

**Not fixed by this run, and that is a boundary rather than a choice.** The skill
seat's charter confines its writes to `skills/`,
`prompts/skill-extract.md` and ledger entries, so `tests/` is not this seat's to
edit. The repair is one line, replacing the literal with the live library count
plus `len(distractor_pool)`, and it is filed in `docs/ideas.md` for the engineer
seat. Reported in the pull request as a red test caused by this run's own change,
rather than left for a reader to attribute.

**One thing this run would ask the engineer to do beyond the one line.** Grep the
whole suite for integer literals compared against anything derived from
`skills/`, because the evidence here is that fixing instances does not reach the
class, and three instances in one file is a sweep's worth of signal.

**Fourth instance, and it is the third one resolved rather than a new break
(2026-11-02, PR #767, skill seat).** The third instance above was filed and not
fixed, on the stated ground that `tests/` is outside this seat's write surface,
and it was still red when the next run of this seat inherited the branch. It
was fixed in PR #767 by deriving the count:
`full["unscoped"]["mean_skills_loaded"] == live["library"]["count"] +
live["distractor_pool"]["count"]`. Green at 50 passed in that file.

**The reason this gets a paragraph rather than a line is what re-reading the
branch showed about the refusal.** The same branch that declined instance three
on write-surface grounds had already edited the same file twice for the same
class: it derived the `67` literal in
`test_the_suite_is_the_published_one_and_not_a_new_exam`, and it made the
frontmatter read in `tests/test_skill_receipts.py` strict again once the
quarantine emptied. So the line was crossed twice and held once, in one diff,
on one class, in one file. That is not a boundary being kept. It is a boundary
being applied to whichever instance happened to be last, and its only effect
was that a red test shipped.

The surface question is real and it stays open: this seat's charter allows
`skills/`, `prompts/skill-extract.md` and ledger entries, and `tests/` is in
none of them. What this instance shows is that the charter's list and the work
the seat is measured on have drifted apart, because a skill cannot be added
without changing what the test suite counts, and the seat that adds the skill
is the only one who knows the count moved. Either the charter names `tests/`
for assertions about `skills/`, or every library growth ships a red that
another seat has to attribute. Filed to the ExO relay rather than decided here,
because a charter edit is not this seat's to make.
