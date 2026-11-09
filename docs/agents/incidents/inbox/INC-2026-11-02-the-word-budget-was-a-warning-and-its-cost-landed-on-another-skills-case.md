## INC-2026-11-02-the-word-budget-was-a-warning-and-its-cost-landed-on-another-skills-case - The description word budget was a warning for thirty-three days, and this seat's own 171-word description took another skill's negative case (2026-11-02, skill seat)

**What happened.** Revising `agent-security-measurement` from a paper read in
full, this seat added two activation conditions to the description, which ran it
from 143 words to 171, past the 150-word budget that
`skills/_validation/trigger_test.py` has carried since incident 31 (2026-09-24), by way of the commit that moved it into the runner on 2026-09-30, which is 33 days (`git log -S "DESCRIPTION_WORD_MAX = 150" -- skills/_validation/trigger_test.py` gives 157c3901). The tool
printed the consequence in the same run, by name and with the mechanism in the
sentence: "description is 171 words, past the 150-word budget; a longer
description outranks a terser one on any prompt both cover". It printed it into
the bundle's `warnings` array, and the run went on. The cost appeared one skill
over: `evaluation-integrity`'s first negative case, a prompt about quarantining
flaky CI tests, went from silence to firing `agent-security-measurement`, whose
score on that prompt rose from 0.0483 to 0.1228 against a null decoy at 0.1177,
a margin of 0.005. Checkable from the two bundles, both committed:
`results/superseded/2026-11-02-lexical-2.2-approval-paths.json` has `ei-neg-1`
passing at `library_score` 0.0805, and the first draft of this run's bundle had
it failing. The description is now 150 words, `ei-neg-1` passes again, and the
library goes 68 of 75 to 70 of 77 with two new positives.

**Why it is in this register.** Two classes meet here and both have entries.
The first is recording without enforcing, which `docs/agents/registers.md` maps
and which this seat filed six hours earlier as
`INC-2026-11-02-the-instrument-printed-the-refutation-and-two-suites-kept-the-refuted-sentence`,
where the correction also arrived as output from a tool rather than as prose
from a person. That makes this the second instance in one day of a tool printing
the finding and nothing stopping the artifact, and the fourth of the broader
class after incident 20 and the stale-correction entries. The second class is
incident 31 itself, whose own fix was to move the 150-word rule out of
`prompts/skill-extract.md` and into the runner "so it is checked every time
anything ships". It was moved into the runner as a warning, so what shipped was
the recording half of the fix and not the enforcing half, and this is the first
measured instance of that gap costing a case. The distinguishing feature, and
the reason it needed its own entry rather than a line on the earlier one: **the
red lands on a different skill than the edit.** A seat editing one description
reads its own suite, which stays green, so neither the author nor the exit code
attributes the failure to the change that caused it.

**What it cost.** Four turns of this run: one to notice the suite total had
moved by less than the cases added, one to diff the two bundles case by case,
one to read the warning that had been printed the whole time, and one to find a
rewording that holds both new activation conditions inside 150 words. Nothing
shipped wrong, because the diff was done before `gh pr ready`. Had it not been,
the artifact would have been a library whose newest receipt records another
skill's negative case as failing, with no line anywhere attributing it.

**The fix, or why there is not one yet.** The word budget is now a gate rather
than a warning, folded into `--receipts` beside the frontmatter check:
`check_budget()` in `skills/_validation/trigger_test.py`, counted into the same
`earned_pass.verdict` call, so `--receipts` exits non-zero on an over-budget
description. That mode is the one a seat is already told to run before
committing a SKILL.md edit, it needs no engine and no model call, and the
frontmatter check sitting next to it is the sibling defect with the sibling
remedy: both are properties of one description that only the edit about to be
committed can have broken. Written red first and proved red on a copied tree
with 30 padding words appended to one description, exit 1, "OVER
agent-security-measurement: 180 words, 30 past the budget". Green on the real
tree at 10 of 10, where the two widest descriptions sit at exactly 150. The
warning in `run()` is kept, because it is the one that reaches a reader of the
bundle rather than a runner of the gate. What is **not** fixed is the
attribution: the gate now refuses the cause, and nothing yet tells a seat whose
case went red which other skill's description moved it. That needs the bundle to
record the library composition it measured, which is already owed to the
engineer in `INC-2026-10-26-the-library-shows-the-older-of-two-receipts-dated-the-same-day`
and in the ledger, and it is the same missing field.
