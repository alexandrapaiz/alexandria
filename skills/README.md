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
