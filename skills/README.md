# Gold layer

Human-approved skills and pattern notes distilled from the research pipeline.
Files land here only through the promotion flow (see ADR-7): the weekly brief
proposes, a human approves, and the approved claims are written up as a skill
or pattern. Since ADR-35 a skill is written from the papers read in full, not
from claim rows.

Ten skills as of 2026-11-09, read straight out of `skills/` rather than
counted by hand. None has been passed by the ADR-13 panel, so every
`provenance.validated` field except harness-engineering's is still empty.

**No skill carries `status: active`.** Nine carry `status: provisional` and
`agent-approval-paths` carries `status: draft`. That is the ADR-38 bar doing
what it was written to do: `active` is earned on a measured positive delta on
the benchmark subject, and this seat has no route to either eval arm, so
nothing can earn it today. The two blockers are `GROQ_API_KEY`, absent from
`.github/workflows/agent-skill.yml` and from the host, and a benchmark
provider in `pipeline/budget.py`, which knows moonshot and groq and neither
serves one. Both are queued in `docs/agents/pending-workflow-changes.md`.
Until they land, every skill here is **unmeasured** in that word, and a
`provisional` status is the honest reading of the whole library rather than a
stage any single skill is passing through.

The eight skills that existed on 2026-09-30 completed the ADR-38 retrofit that
day (owner directive), and the two added since were written to it:
`agent-memory-selection` on 2026-10-13 and `agent-approval-paths` on
2026-11-02. So every skill carries a per-section *Validation:* tag, an "Apply"
checklist, caveats that name a floor where one exists, and a standing
`reviews/` lane referenced from its provenance block. Read the tags before
quoting a section: nine of the ten have no section validated by anything
stronger than claim provenance and an unrun eval task, and the tags say so at
each section head rather than leaving it to one empty field in the
frontmatter.

`agent-approval-paths` is the skill with an empty `provenance.claims` list
today, and that is deliberate rather than a gap: it is written from papers
read in full under ADR-35 and its provenance is the `papers` list. A
papers-only provenance block cannot pass ADR-36's automatic gate, which is a
real conflict between the two ADRs and is filed in `docs/ideas.md` rather
than worked around here.

`agent-containment` used to be that skill, and this file said so for
thirty-four days after it stopped being true. The 2026-09-30 coverage census
found that all 24 claims the corpus attributed to the containment thread were
keyword artefacts and that no claim in the graph concerned an isolation
boundary. That census went out of date on 2026-10-06, when commit `d4ca234b`
filled the block with fifteen claim ids over six papers, because PACE
(2610.01349) and ToolFence (2609.37196) had landed after the census was taken.
Do not cite the census as the library's current state. It was a reading of a
corpus that has grown since.

Two instruments, and they measure different things. Both have to pass.

- **Does the skill fire?** `_validation/trigger_test.py` over each skill's
  `triggers.json`, with the dated bundles in `_validation/results/`. It runs on
  the pre-registered `lexical/2.2` engine by default; `--engine lexical/3`
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
kept. ADR-38 adds the third word this library actually uses: `provisional`,
for a skill whose suite is written and whose delta has not been measured,
which is nine of the ten. The tenth, `agent-approval-paths`, says `draft` for
a different reason that is not about measurement at all:
`tests/skill-provenance.test.mjs` requires `draft` when
`provenance.claims` is empty and allows exactly one such skill at a time.
`prompts/skill-extract.md` carries that rule in full. Under ADR-37 a skill is revised when a claim it cites is deprecated or
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
