# Gold layer

Human-approved skills and pattern notes distilled from the research pipeline. Files
land here only through the promotion flow (see ADR-7) — the weekly brief proposes,
a human approves, and the approved claims are written up as a skill or pattern.

Four skills as of 2026-09-24, all drafted and none yet passed by the ADR-13
panel, so every `provenance.validated` field except harness-engineering's is
still empty. `_validation/` holds the trigger test that decides whether a skill
fires, and `_validation/results/` the dated bundles it has produced. The test
runs on the pre-registered `lexical/2.1` engine by default; `--engine
lexical/3` selects the candidate-normalised experiment, which is recorded but
not adopted.

## Consumer reports (ADR-38, 2026-09-29)

Each skill directory may hold a `reviews/` lane:
`reviews/YYYY-MM-DD-<consumer>.md`, filed by any session or seat that
used the skill on real work. A report records who the consumer was,
the task, which sections changed a decision, which only confirmed one,
and what the skill should add. The skill agent reads new reports first
on every run (maintenance before creation, ADR-37), feeds
decision-change findings into per-section *Validation:* tags, and
treats several zero-decision-change reports as a deprecation signal.
The format additions of the same ADR: every skill carries a one-line
*Validation:* tag under each section heading and an "Apply" checklist
before its caveats, and caveats name the floor of any requirement they
state. The first report is
`harness-engineering/reviews/2026-09-29-ursa-chair.md`, whose consumer
derived all three additions the hard way.
