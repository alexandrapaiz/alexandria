# Gold layer

Human-approved skills and pattern notes distilled from the research pipeline.
Files land here only through the promotion flow (see ADR-7): the weekly brief
proposes, a human approves, and the approved claims are written up as a skill
or pattern. Since ADR-35 a skill is written from the papers read in full, not
from claim rows.

Eight skills as of 2026-09-30, none yet passed by the ADR-13 panel, so every
`provenance.validated` field except harness-engineering's is still empty. Six
carry `status: active` from before ADR-36. The two newest,
`agent-containment` and `agent-security-measurement`, carry `status: draft`
because their eval task sets exist and no harness has run them yet, which is
what ADR-36 says draft means.

All eight completed the ADR-38 retrofit on 2026-09-30 (owner directive), so
every skill now carries a per-section *Validation:* tag, an "Apply" checklist
of five to seven lines, caveats that name a floor where one exists, and a
standing `reviews/` lane referenced from its provenance block. Read the tags
before quoting a section: seven of the eight skills have no section validated
by anything stronger than claim provenance and an unrun eval task, and the
tags say so at each section head rather than leaving it to one empty field in
the frontmatter.

`agent-containment` is the library's first skill with an empty
`provenance.claims` list, and that is deliberate rather than a gap. The
2026-09-30 coverage census found that all 24 claims the corpus attributes to the
containment thread are keyword artefacts and that no claim in the graph concerns
an isolation boundary, so the skill is written from six papers read in full
under ADR-35 and its provenance is the `papers` list. A papers-only provenance
block cannot pass ADR-36's automatic gate, which is a real conflict between the
two ADRs and is filed in `docs/ideas.md` rather than worked around here.

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

Each skill directory holds a `reviews/` lane, whose shared contract is
`_validation/reviews/README.md` and whose per-skill `reviews/README.md` names
the sections that skill most wants a report on. The lane ships with the skill
rather than waiting for its first consumer, because a lane created after a
report arrives never receives one:
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

The retrofit pass that applied them on 2026-09-30 found something the reports
themselves would not have: two skills, `evaluation-integrity` and
`recursive-harness-self-improvement`, had a section whose claim ids were
attached to an eval task that tested none of it. Tagging every section forces
a reader to ask what covers each one, which is how the gap surfaced. Both
suites moved to version 2 with the missing task written rather than the tag
softened.
