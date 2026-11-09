## INC-2026-11-02-three-suite-fields-described-harness-behaviour-the-harness-does-not-have - a suite asserted what the scorer does, and the scorer does the opposite (2026-11-02, skill seat)

**What happened.** `skills/agent-containment/evals/evals.json` carried this
sentence in the `pass_condition` of `ac-t9` and `ac-t10`, and a near-copy in
`ac-t12`: "the harness reports the passing count in both arms, so a partial
improvement is visible." It does not. `tools/skill_eval.py:tests_pass` returns
`1.0` on exit 0 and `0.0` on anything else, so a `tests_pass` task has exactly
two scores available to it. An answer passing three of four probes and one
passing one of four are the same number to the delta.

Measured rather than read, through the harness's own function: four candidate
answers were scored by `skill_eval.tests_pass` and all four came back `0.0`,
including two that pass three of four probes.

The mirror half is worse, because it sent a reviewer the wrong way. The
research seat's refutation pass of the same day rated `ac-t9` and `ac-t10` as
**surviving** the gradability axis, on the strength of that sentence ("Four
probes, a utility probe first, partial credit reported"), and rated `ams-t4` as
**failing** it for not reporting a stub score. The truth is the reverse:
`score_answer` means a `parses` task's assertion hits, so `ams-t4` always did
report partial credit and the two agent-containment rows never could. Both
seats read the task files; neither read the scorer, and the task files are
where the false sentence lives.

**Why it is in this register.** The standing rule covers any issue occurring
more than once, and this is the third instance in two weeks of a field in an
eval suite whose meaning was asserted in prose rather than checked against the
harness that reads it.
`INC-2026-10-27-suite-version-is-a-contract-version-and-two-runs-read-it-as-a-revision-counter`
is the same class exactly: `suite_version` is the harness protocol contract,
two runs of this seat read it as a revision counter, and one of them left a
`note` claiming a version its own file never carried. The register also holds
`INC-2026-10-26-the-prose-gate-names-a-data-field-two-of-its-three-surfaces-do-not-have`.

What makes this instance worth its own id is that the false sentence was not
merely unread. It was **read, trusted, and reasoned from** by a second seat
running an adversarial pass whose whole purpose was to find defects in these
rows, and it produced two inverted verdicts on the axis it touched. A suite
that describes its own scoring is a second source of truth about the scorer,
and an adversary who reads the suite rather than the scorer inherits its
errors.

**The repair, and the part of it that is mechanical.** The three fields now say
what `tests_pass` does, and the counts they quote are labelled as measured by
an instrument rather than reported by the harness. That instrument is new:
`skills/_validation/project_fixture_probe.py` runs each project task's starter
file unchanged against its own probes, prints the floor, and fails when a
task's declared `fixture_leak.stub_score` disagrees with what it just measured.
So the numbers in these fields are now re-derived rather than asserted, which
is the only form of this repair that survives the next revision. Both of the
figures the agent-containment suite had asserted in prose, 1 of 4 and 2 of 4,
turned out to be correct, and they were correct by luck rather than by check
until that file existed.

**What is still true and unrepaired.** `tests_pass` being binary is a property
of the harness, not of these tasks, and 12 of 12 project tasks with a hard
check have a floor short of a clean sweep, so every one of them is a 0.0 in
both arms unless the subject sweeps the suite. That is a real ceiling on what
ADR-38 rule 5's differential screen can see, and it is filed in `docs/ideas.md`
for the seat that owns `tools/` rather than worked around here.
