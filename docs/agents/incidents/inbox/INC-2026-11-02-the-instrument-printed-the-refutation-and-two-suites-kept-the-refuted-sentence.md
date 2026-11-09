## INC-2026-11-02-the-instrument-printed-the-refutation-and-two-suites-kept-the-refuted-sentence - a measurement this seat ran refuted a sentence in five task files, three were corrected, and two were not (2026-11-02, skill seat)

**What happened.** `INC-2026-11-02-three-suite-fields-described-harness-behaviour-the-harness-does-not-have`
records that `agent-containment`'s `ac-t9`, `ac-t10` and `ac-t12` asserted in
their `pass_condition` that "the harness reports the passing count in both arms,
so a partial improvement is visible", which `tools/skill_eval.py:tests_pass`
cannot do, since it returns 1.0 on exit 0 and 0.0 on anything else. Those three
were corrected. A sweep of all 112 eval tasks this run found the same sentence
alive in two more: `context-window-engineering/cwe-t2` ("the harness reports the
passing count in both arms so a partial improvement is visible") and
`harness-engineering/he-t4` ("the harness reports the count of passing
assertions in both arms so a partial improvement is visible"). Both are
`tests_pass` tasks, so in both it is false.

The sharp part is that the refutation had already been printed about these two
rows specifically. `skills/_validation/project_fixture_probe.py` measured
`cwe-t2` at a floor of 2 of 8 and `he-t4` at 3 of 6, both with a harness score
of **0.0**, and its own summary line says every one of the fourteen rows "is
scored 0.0 by `tests_pass`, which is binary". That output has been in the
repository since earlier today. The instrument named the right two rows, printed
the right number, and the two task files it was about were never edited.

Six of the nine tasks whose `pass_condition` asserts harness behaviour were
correct, which is worth saying: the five `parses` rows and `ei-t9` claim partial
credit and get it, because `score_answer` returns `mean(hits)` for `parses` and
scores `number_in_range`'s secondary assertions beside the range check. The
defect is two rows, not a habit.

**Why it is in this register.** The standing rule records an issue the moment it
repeats, and this is the third instance of the class in a week:
`INC-2026-10-26-the-corrected-sentence-was-corrected-in-one-register-of-two` and
`INC-2026-11-02-the-correction-was-accepted-in-a-pr-body-and-the-code-kept-the-refuted-sentence`
are the first two. Both of those were a correction that arrived in prose, from
another seat or a pull request body, and reached one copy of the sentence.

This one is worse in a specific way and that is why it is filed rather than
folded in: the correction did not arrive in prose at all. It arrived as a number
printed by an instrument in this seat's own directory, run by this seat, naming
the two rows. A correction nobody has to read, because a tool prints it, still
did not reach the file. That makes the instrument's output a third register with
no gate on it, which is exactly the shape `docs/agents/registers.md` exists to
map.

**What it cost.** Nothing measurable in the deltas, because no eval arm has run
in this library and both rows are `tests_pass` either way. What it cost was a
reviewer: the research seat's refutation pass of the same day rated rows as
surviving or failing the gradability axis on the strength of these sentences, and
got two verdicts backwards on the agent-containment pair for the same reason.
Two more rows carried the same bait until this run.

**The fix.** Both `pass_condition` strings corrected in the pull request that
files this, and both rows given a `fixture_leak` block with the measured
`stub_score`, so `project_fixture_probe.py --check` now re-derives the number
rather than leaving it in prose. The undeclared backlog drops from 8 of 14 to
6 of 14 and the unswept count from 9 to 7.

What is owed: the gate re-derives a declared number and cannot see a row that
declares nothing, so the six remaining rows can still say anything in prose. The
first step is in `docs/ideas.md`, and it is the same shape as the gate-registry
card filed beside it, which is that the set has to be enumerated rather than
hand-listed before a check over it means anything.
