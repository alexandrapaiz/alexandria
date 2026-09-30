# Workflows waiting for a hand to move them

The agent seats push with a GitHub App token that has no `workflows`
permission, on purpose: an agent that can write its own CI can also write
itself out of it. So a seat that needs a new workflow leaves it here, and the
owner or the chair moves it one directory up.

    git mv .github/workflows-pending/checks.yml .github/workflows/checks.yml

Nothing in this directory runs. Anything still sitting here is a guard that is
not guarding yet.

## checks.yml — does the digest request fit the model's budget?

Filed by the engineer seat 2026-09-19 for incident 22. Runs
`python3 pipeline/budget.py` on every pull request that touches a generator
prompt or the pipeline, and fails the build with the arithmetic printed when
the prompt plus the worst-case payload plus the output reservation no longer
fits the model's per-request ceiling.

Until it is moved, the same check still runs in two places, so the press is
not unguarded in the meantime: `modal run pipeline/weekly.py` runs it locally
before it spends anything, and the digest run itself refuses to call Groq when
the sums do not work. What is missing without the workflow is the early
warning, at the moment an editorial merge is proposed rather than the next
time the press tries to print.

The same workflow has since grown three more steps, each `always()` so a
red budget step cannot hide them: the press's bad-day paths
(`tests/test_press_resilience.py`, incident 24), the designed email
(`tests/test_email_template.py`, the owner's 2026-09-24 ruling), and the
rehearsal print (`tests/test_press_rehearsal.py`,
INC-2026-09-24-press-provider-migration). None of them needs a key, a
network or a database.

A fifth step joined them on 2026-09-29: the skill library's receipts
(`tests/test_skill_receipts.py`). It is the odd one out, because it guards a
customer-facing page rather than the press, and it is here for the same reason
as the rest. Every receipt on `/skills` is pinned by sha to the exact `SKILL.md`
text the page shows, so editing a skill without re-running
`python3 skills/_validation/trigger_test.py` publishes a pass rate for a
document the reader cannot see. That step turns red on the pull request that
does it. It needs no key, no network and no database.

A sixth joined them on 2026-09-29: the claim graph's audit
(`tests/test_graph_audit.py`). `tools/graph_audit.py` holds ten SELECTs against
the corpus database, and no CI job in this org can execute one, because the only
Postgres that matters is the production one. So the step parses every query with
libpg_query and resolves every relation and column it names against
`db/schema.sql`. A migration that renames a column turns the pull request red
rather than turning the audit red the first time somebody points it at Neon. No
key, no network and no database.

The same commit fixed the fifth step's triggers. The receipts step was added on
2026-09-29 without adding anything it guards to this workflow's `paths`, so
editing a `SKILL.md` would not have run it and the guard would have been a guard
in name. `skills/**`, `site/lib/skill-provenance.js` and both new test files are
in the list now. It is worth saying plainly what that near miss was, because it
is the shape this whole directory exists to catch: a check can be written
correctly, reviewed, merged, and still never fire, and nothing about reading it
tells you which.

The rehearsal step is worth one sentence of its own, because it is the
only one that guards a gate CI cannot run. The gate itself is `modal run
pipeline/weekly.py::rehearse`, a real call with a real key that costs
real money, and it belongs to the chair's deploy command
(docs/agents/runtime-changes.md). What CI holds is that the gate still
has teeth: that a rehearsal cannot write to `digests`, cannot mount a
mail credential, and cannot pass on a receipt naming a different model.

## Still pending as of 2026-09-26, and the cost is now larger

Filed by the engineer seat 2026-09-19. Seven days later it is still here,
which means the repository's 279 Python tests and 66 Node tests run in
exactly one place: a seat's own session, on the honour system. Every
sentence above about what CI holds is written in the future tense.

That mattered less when the only thing at stake was whether an editorial
merge broke the press, because the press refuses the call itself when the
sums do not work. It matters more as of today. `python3 pipeline/budget.py`
now also fails when a per-run spend cap is raised past the ceiling in
docs/finance/opex.md, and when two jobs that share Moonshot's
single-concurrency slot are scheduled into overlapping windows. Those two
guards exist to stop a change nobody is watching, and until this file moves
one directory up they stop it only for whoever remembers to run the command.

    git mv .github/workflows-pending/checks.yml .github/workflows/checks.yml

One command, and it is the owner's or the chair's: a seat's token has no
`workflows` permission, for the reason the top of this file gives.

## skill-gate.yml — does this revision merge on its own?

Filed by the engineer seat 2026-09-30 for ADR-37, amended the day before when
the owner confirmed no human in the loop for skill maintenance. It runs
`python3 tools/skill_gate.py` on every pull request that touches `skills/**`,
labels the pull request `skill-gate/passed` or `skill-gate/failed`, and comments
with the state of all seven clauses and the reason behind each one. One comment
that it edits on each push, never a new one.

**It does not merge anything, and that is deliberate.** ADR-37 allows a measured
revision of an existing skill onto main without the owner, and the step that
would act on this verdict is not queued here yet. The gate has to be seen to be
right on real revisions first, and a label is reversible in a way a merge is not.
When it is queued it will be a separate workflow with its own permissions, so
that the thing which judges and the thing which acts are never one file.

A pull request that edits a skill alongside code gets no label at all. The
`paths:` filter can only say `skills/**`, and the question ADR-37 actually asks is
whether the diff touches nothing else; the tool answers that one and reports the
pull request as not applicable, because a red label on every engineer pull request
that happens to edit a skill is how a label stops being read.

`fetch-depth: 0` is load-bearing. Three clauses compare the revision against the
base branch: the eval against the previous version's own lower bound, the ban list
against what the revision adds, and the trigger test against which cases were
already failing. On a shallow checkout those clauses report `unknown`, and an
unmeasured clause is never a pass, so the gate would fail closed. That is the
right direction to fail, and it is still worth not failing.

Until it is moved, nothing enforces the gate on a pull request. The same clauses
can be run by hand from a checkout, which is how the seven refusals were
rehearsed on 2026-09-30 (a deprecated cited claim, a month-old claim-status
snapshot, a SKILL.md edited after its eval, a delta below the previous version's
lower bound, a version with no trigger, the kill switch set, and a revision that
introduces a ban-list tell). No key, no network, no database: the graph clause
reads `docs/research/claim-status.json`, which the daily Modal job writes.
