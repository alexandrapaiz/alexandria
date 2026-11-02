# The first reader `pass_condition` ever had, and the seven rows it found

Run 2026-11-02 by the skill seat. Raw output in
`2026-11-02-pass-condition-gate.txt`, both arms.

## What was measured, and why the earlier repair did not hold

`pass_condition` is a field in every eval suite that describes what the harness
does with the task. It had no reader. `tools/skill_eval.py` never mentions the
string and `normalize` does not carry it, so it was a documentation sentence
inside a machine-readable file with nothing checking it.

Measured rather than asserted: `python3 tools/skill_eval.py --check` prints the
identical 114 findings against this branch with the seven corrections and
against the same branch without them. The field moves nothing in the harness.

That is why declaring the measured `fixture_leak.stub_score` was not enough.
Declaring the number closes the number and cannot close the sentence. `ac-t12`
declared 2 of 5, measured 2 of 5, and passed `--check` at exit 0 with
"the harness reports the passing count in both arms, so a partial improvement
is visible" intact, which `tests_pass` cannot do: it returns 1.0 on exit 0 and
0.0 on anything else.

## The rule the gate checks

A `tests_pass` row's `pass_condition` may not assert a per-probe count. That is
false by construction rather than by measurement, so the gate needs no run of
the harness to decide it. A row that quotes the refuted sentence in order to
withdraw it still passes, because keeping a withdrawn number beside its
retraction is the house practice and must not be a failure.

## The seven rows, on the first run

| row | what it said | kind |
| --- | --- | --- |
| `agent-containment/ac-t12` | the harness reports the passing count in both arms, so a partial improvement is visible | the third copy of the sentence two register entries recorded as repaired |
| `context-window-engineering/cwe-c1` | passed when the with-skill arm's pass count is not below the without-skill arm's | a criterion over a count the harness does not emit |
| `evaluation-integrity/ei-c1` | same | same |
| `harness-engineering/he-c1` | pass rate rather than pass count | same |
| `recursive-harness-self-improvement/rhsi-c1` | same, with the binary caveat beside the false noun | same |
| `self-improving-post-training-loops/sipt-c1` | same | same |
| `skill-library-engineering/sle-c1` | same | same |

Seven rows, not one. The six control rows are the same absent number under a
different noun, and their criterion is sound read as a comparison of the two
scores `tests_pass` does produce, so the noun is what changed.

## What the gate still cannot see

Six of the fourteen project rows with a hard check declare no `fixture_leak`,
and the gate reads a declared number rather than deriving one, so those rows can
still carry any count they like in prose that the pattern does not match. The
pattern is drawn from sentences that actually shipped, which means the next
wording nobody has written yet goes through. That limit is the honest reading of
this gate and it is recorded here rather than claimed away.
