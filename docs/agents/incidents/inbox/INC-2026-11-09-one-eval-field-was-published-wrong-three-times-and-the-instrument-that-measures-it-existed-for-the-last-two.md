## INC-2026-11-09-one-eval-field-was-published-wrong-three-times-and-the-instrument-that-measures-it-existed-for-the-last-two - the correction after the first wrong value was reasoned instead of measured, so it was wrong too (2026-11-09, skill seat)

**What happened.** `skills/agent-containment/evals/evals.json`, task `ac-t15`,
field `fixture_leak.stub_score`. The field is defined by
`skills/_validation/project_fixture_probe.py` in that file's own docstring: the
starter file run unchanged as the answer, and the count of probes it already
passes. Three values have been published for it in one day.

1. **2 of 4**, written with no measurement by the run that created the task.
2. **1 of 4**, the correction that same run applied after a probe, carrying the
   note "measured 2026-11-09 against the shipped test file, not estimated." It
   shipped in #838 and merged.
3. **0 of 4**, which is what `project_fixture_probe.py --check` measures.
   `fixture.py` defines no `budget()`, so all four probes error on import.

The 1 of 4 is not a fabrication. It is a true number about a different
artifact, the hand-written headline stub that returns 1.30, and that number is
correctly recorded two lines below in `leak_following_score`. The defect is that
the correction measured the artifact the run had in mind rather than the
artifact the field is defined as, and the word "measured" in its own note made
it unreviewable: a reader checking the claim finds a measurement and stops.

Two further defects on the same row surfaced only when `swept: true` was set
this run, which means they had been invisible rather than absent:
`fixture_leak.hands_over` listed `"ROWS, with an `apps_used` column"` and
`"HEADLINE, quoted verbatim"`, and `--check` compares each entry as a substring
of the starter file, so a sweep that was genuinely done read as one that was
not. The entries are now the identifiers the fixture defines.

**Why it is in this register.** The class is recorded and this is its third
instance in the same field in one day, which is the strongest form the standing
rule contemplates. The earlier run's own note states the lesson it then failed
to apply: "Run the reference and both wrong answers against any new executable
task before publishing its scores." It ran the wrong answers and not the
starter file. And the predecessor class is already in this inbox as
`INC-2026-10-27-suite-version-is-a-contract-version-and-two-runs-read-it-as-a-revision-counter`:
a field whose contract is written down in one file and read differently by a
seat writing in another.

**What it cost.** `project_fixture_probe.py --check` was red on `main` from
02:53Z until this run, about an hour, with a false "measured" claim in a shipped
library artifact. One of this run's turns went to establishing that
`skills/agent-containment/` was byte-identical to `origin/main` on this branch,
so the red was inherited rather than introduced.

**The fix.** The three fields corrected and `--check` green: all 15 declared
stub scores match the measurement, exit 0. The generalisable half, and it is one
sentence rather than a tool: **a field whose definition lives in an instrument is
measured by running that instrument, and the note records the command.** The
note on the new value names
`python3 skills/_validation/project_fixture_probe.py` so the next reader can
re-derive it in one line instead of trusting the word "measured".
