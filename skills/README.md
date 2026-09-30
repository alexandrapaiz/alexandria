# Gold layer

Human-approved skills and pattern notes distilled from the research pipeline.
Files land here only through the promotion flow (see ADR-7): the weekly brief
proposes, a human approves, and the approved claims are written up as a skill
or pattern. Since ADR-35 a skill is written from the papers read in full, not
from claim rows.

Six skills as of 2026-09-30, all drafted and none yet passed by the ADR-13
panel, so every `provenance.validated` field except harness-engineering's is
still empty.

Two instruments, and they measure different things. Both have to pass.

- **Does the skill fire?** `_validation/trigger_test.py` over each skill's
  `triggers.json`, with the dated bundles in `_validation/results/`. It runs on
  the pre-registered `lexical/2.1` engine by default; `--engine lexical/3`
  selects the candidate-normalised experiment, which is recorded and not
  adopted. A skill can win its eval and never load, which is the market's
  69-percent problem.
- **Does the skill help?** Each skill's `evals/evals.json`, added 2026-09-30
  under ADR-36: tasks the skill is meant to change, run with and without it
  loaded on the same subject model, plus control tasks it must not change. The
  contract is `_validation/evals/README.md`. The harness that runs them is the
  engineer's build, so the task files are here and the measured deltas are not
  yet. A skill can fire perfectly and teach nothing.

Under ADR-36 a skill with no eval is `status: draft` and never `active`, and a
skill whose eval shows no gain is retired with the numbers rather than quietly
kept. Under ADR-37 a skill is revised when a claim it cites is deprecated or
refined, when a cited paper's citations move sharply, or when its own eval
regresses; each skill's `provenance.revisions` records what fired and what
changed.

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
