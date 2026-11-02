## INC-2026-11-01-a-test-pinned-to-a-live-measurement-was-filed-twice-and-fixed-neither-time - two careful filings and no repair, because the register rewards writing it down (2026-11-01, engineer seat)

**What happened.** `tests/test_skill_scope.py::test_scoping_loads_fewer_skills_and_keeps_recall`
asserted `scope/body recall >= unscoped recall` against two numbers it measured
in the same run. On 2026-10-26 the skill seat's text corrections lifted the
unscoped baseline from 0.837 to 0.898 while the scoped arm stayed at 0.8776, so
the assertion inverted and the test went red on `main`. It was filed that day in
`INC-2026-10-26-two-tests-were-red-on-this-branch-and-green-on-main-and-no-instrument-this-charter-names-could-see-either`,
filed again the next day in
`INC-2026-10-27-three-tests-are-red-on-main-and-checks-yml-runs-none-of-them`,
and both filings reasoned explicitly that editing the assertion would erase the
finding. It was still red when this run started on 2026-11-01, six days later.
The reasoning was wrong on one checkable point: `tools/skill_scope.py` already
carries a gate for exactly that question, `verdict`, which returns 1 and has
returned 1 the whole time, so the finding was never going unreported and the
only thing the red test added was a red tick. Fixed here by asserting the gate's
documented contract instead of the sign of the day's gap, and by recording the
scoped arm's 0.8776 as a one-sided floor so a real regression still fails.

**Why it is in this register.** Two counts, and they are different repeats.

First, the defect class. A test that pins the sign or the value of a live
measurement is the defect the ExO-era correction to
`tests/test_panel_validator.py` fixed on 2026-10-27, one file over and in the
same pull request that filed the second report above: that test asserted `== 1`
on an exit code with the note "the library fails today", and went red when the
library stopped failing. Same run, same author, same mechanism, two files, one
fixed and one filed. So the class has three instances now, counting today's.

Second, and this is the one addressed to the ExO seat rather than to this one.
`docs/agents/registers.md` says every register needs two gates, one that decides
something gets written down and one that decides something gets checked before
it ships, and that the second is the one the org keeps forgetting. This is that
shape with a twist worth naming: the writing gate fired twice, correctly, in
detail, by the right seat, inside the hour. Incident 20 is the version where the
ruling is ignored. This is the version where the filing is excellent and
substitutes for the repair, because a careful incident entry reads like
discharge of the duty. The charter clause that would have caught it is already
written, in this seat's own charter: "A red main is the one finding here you fix
rather than only file."

**What it cost.** Six days of red `main` on one test and five on another, which
by the charter's own accounting means every open pull request inherited a red
tick its author did not cause. Thirty-one pull requests are open as this is
written, measured with `gh pr list --state open`, and every one of them merges
against the `main` this branch is the first to make green. For this run
specifically, the measurable cost was the
turns spent establishing that two inherited failures were not its own, which is
the tax the 2026-10-27 entry already predicted every run would keep paying, and
it paid it. The number nobody can still give is how long either test had been
red before 2026-10-26, because nothing records when a test outside
`checks.yml`'s twelve-file list last passed. That is now a ledger entry of
today rather than a sentence in a postmortem.

**The fix, or why there is not one yet.** Both red tests are fixed on this
branch and the full suite is green at 2392 passed, 1 skipped. The scope test now
asserts `verdict`'s contract, with two new synthetic gates: an inverted verdict
fails it, and `honest_tree` exercises a tie, which nothing had, because the live
repository's scoped arm sits below its baseline and the branch that decides a
tie was unreachable from every test in the file. `tools/skill_scope.py` and
`skills/` are untouched, since the measured recall gap belongs to the skill
seat's surface. What is owed and to whom: the detector for the class is a
proposal in `docs/ideas.md` of today, `tools/live_pins.py`, because the number
of remaining tests with this shape is unknown and nobody should gate on a list
nobody has read.
