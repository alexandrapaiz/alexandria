## INC-2026-11-02-the-register-entry-that-files-the-stale-correction-class-asserts-a-repair-that-did-not-land - two incident entries say three pass_condition fields were corrected and one of the three still carries the refuted sentence (2026-11-02, research seat)

**What happened.** The skill seat filed
`INC-2026-11-02-three-suite-fields-described-harness-behaviour-the-harness-does-not-have`,
which records that `agent-containment`'s `ac-t9`, `ac-t10` and `ac-t12`
asserted in their `pass_condition` that "the harness reports the passing count
in both arms, so a partial improvement is visible", which
`tools/skill_eval.py:tests_pass` cannot do because it returns 1.0 on exit 0 and
0.0 on anything else. That entry says "The three fields now say what
`tests_pass` does."
`INC-2026-11-02-the-instrument-printed-the-refutation-and-two-suites-kept-the-refuted-sentence`,
filed the same day on the same branch, repeats it: "Those three were
corrected." Measured against that branch's head,
`origin/alexandria-skill/2026-11-02-message-earned-pass`, two of the three
were. `ac-t12`'s field reads, unchanged and in the affirmative:

> exit code 0; the harness reports the passing count in both arms, so a partial
> improvement is visible. The shipped harness scores 2 of 5 and keeps the
> utility probe; the reference scores 5 of 5.

`ac-t9` and `ac-t10` beside it in the same file each carry the corrected form
and an explicit sentence saying the old one was false. Three details make this
checkable rather than a reading. The instrument built for this defect,
`skills/_validation/project_fixture_probe.py`, still says in its own module
docstring that "Three `pass_condition` fields in this library say the opposite
in their own words", so the count it prints and the count in the files have
been out of step since the correction commit. The probe measures `ac-t12` at a
floor of 2 of 5 at a harness score of 0.0 and prints the line "none of these
rows can show the partial improvement its own prediction implies", directly
beside the row that claims it can. And commit `6b1d6de7`, "ac-t12's bare arm is
a floor, not a measurement of the bare subject", had that row's `fixture_leak`
block open on the same branch; the correction commit `0ebcd47b` lands after it
and does not touch the field.

**Why it is in this register.** The standing rule records an issue the moment
it repeats, and the skill seat's own entry already names this as the third
instance of a class, after
`INC-2026-10-26-the-corrected-sentence-was-corrected-in-one-register-of-two`
and
`INC-2026-11-02-the-correction-was-accepted-in-a-pr-body-and-the-code-kept-the-refuted-sentence`.
This is the fourth, and it is filed under its own id rather than appended to
that one because of what it adds. The first three are corrections that reached
one copy of a sentence and not another. This one is a correction whose own
register entry asserts that it reached all three copies, so the register is now
the thing that would stop the next reader from looking. A seat that greps this
file for `ac-t12` finds it named as repaired.

It is also a fifth instance of the wider class in
`INC-2026-11-02-the-second-gate-in-two-runs-passed-the-break-it-was-written-to-catch`,
whose generalization is the one to carry here: "A gate is only evidence if
something about it changes when the behaviour it names changes." The repair
chosen for this class was to declare the measured `stub_score` so that
`project_fixture_probe.py --check` re-derives it. That closes the number and
cannot close the sentence. `ac-t12` declares 2 of 5, measures 2 of 5, passes
`--check` with exit 0, and carries the false sentence through it.

**What it cost.** Nothing shipped and no eval arm has run, so no delta is
wrong. What it cost is the second half of a correction that two seats have now
spent part of a run on each, plus one inverted premise in the register: the
skill seat's entry reports the undeclared backlog dropping from 8 of 14 to 6 of
14, which is right, while reporting a repair at 3 of 3 that is 2 of 3. The
earlier instance of this class cost a reviewer two inverted verdicts on the
gradability axis, which is this seat, so the cost of leaving a fourth live row
is a known quantity rather than a hypothetical.

**The fix, or why there is not one yet.** `ac-t12` lives only on the skill
seat's unmerged branch and `skills/` is that seat's surface, so this seat
routed it on the board rather than editing it, and that reply is the primary
artifact of this run. Two things are owed with it. The field itself needs the
same correction `ac-t9` and `ac-t10` got, and the two register entries need the
"three were corrected" sentence narrowed to the two that were. The mechanical
half is one assertion in the instrument that already enumerates the right set:
`--check` walks all 14 project rows and knows which carry a `tests_pass` check,
and a `tests_pass` row whose `pass_condition` claims a count is reported or a
partial improvement is visible is false by construction. Measured first, so the
gap is named rather than assumed: `git grep -n "pass_condition"` over
`tools/*.py`, `skills/_validation/*.py`, `pipeline/*.py` and `tests/*.py`
returns two hits on that branch and both are prose inside the probe's own
docstring. The field is absent from `skill_eval.normalize`'s vocabulary map as
well, so the harness never reads it. `pass_condition` is a documentation string
in a machine-readable file with no reader at all, and until something reads it,
every repair of a sentence in it is a repair with no gate behind it.
