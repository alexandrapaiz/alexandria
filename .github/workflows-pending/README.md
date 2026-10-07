# Workflows waiting for a hand to move them

The agent seats push with a GitHub App token that has no `workflows`
permission, on purpose: an agent that can write its own CI can also write
itself out of it. So a seat that needs a new workflow leaves it here, and the
owner or the chair moves it one directory up.

    git mv .github/workflows-pending/checks.yml .github/workflows/checks.yml

Nothing in this directory runs. Anything still sitting here is a guard that is
not guarding yet.

## checks.yml — a REPLACEMENT for the live file, filed 2026-10-07

This is the only entry in this directory that is not a new workflow. The
file replaces `.github/workflows/checks.yml`, so the apply needs `-f`:

    git mv -f .github/workflows-pending/checks.yml .github/workflows/checks.yml

**Two numbers, and they are the whole argument.** The suite holds 47 test
files. The live `checks.yml` runs 14 of them. Measure it yourself, which is
the point of the tool rather than the claim:

    python3 tools/ci_coverage.py

The 33 it does not run include `tests/test_markdown.py`, which holds the
2026-09-19 finding where a crafted passage in an arXiv paper reached the
public archive as live HTML, and `tests/test_accounts.py`, which holds the
account and entitlement layer. Both pass. Neither has ever reported
anything on a pull request.

Filed for item 17 of `docs/agents/pending-workflow-changes.md` and
`INC-2026-10-02-markdown-suite-claims-a-ci-step-it-never-had`. The item was
written with four filenames in it, because four was what a reader noticed.
Thirty-three is what the measurement says, and the gap between those two
numbers is the reason this is a tool and a test rather than another hand
edit. The live file lists 24 `paths` entries against 14 steps against a
directory of 47, and a filename in the `paths` list looks exactly like a
filename in a step while meaning the opposite thing.

### What changed, and nothing else did

The fourteen named pytest steps become one step that runs the suite. Both
`paths` lists are deleted rather than extended, because item 17 asked for
"the directories the suite covers" and that turned out to be all of them:
instrumented with a Python audit hook on 2026-10-07, one full run of
`pytest tests/` opened files under `.github/`, `db/`, `docs/`, `mcp/`,
`pipeline/`, `prompts/`, `site/`, `skills/`, `tests/` and `tools/`. That is
every directory in the repository, and the five entries it leaves out are
root files. A filter naming every directory is not a filter.

Node is installed, which the live file does not do and needs to. Seven of
the 47 are `*.test.mjs`, they reach pytest through a Python wrapper, and
every one of those wrappers calls `pytest.skip` when node is missing. A
skip is not a pass, so without this step the account, markdown, unsubscribe
and waitlist halves would be named by the suite and still never run.

The three script-mode press invocations stay, which item 17 explicitly
allows. They cost under a second each and they keep those files passing in
the mode a person uses by hand.

### It is checked rather than trusted

`tests/test_ci_coverage.py` reads this file. It asserts that applying it
leaves zero test files unexecuted, that it keeps both triggers, and that it
installs node. So an edit here that quietly breaks the thing the file is
for turns the pull request that makes the edit red. Both halves were
confirmed red on a deliberate break before this was filed: narrowing the
suite step to one filename, and adding an unexecuted test file to `tests/`.

Measured with `--only`, so the number is about this file and not about the
directory it is parked in:

    $ python3 tools/ci_coverage.py --only .github/workflows-pending/checks.yml
    47 of 47 test files run in CI
      every test file in tests/ is executed by some workflow

### Do not apply this and subscriber-list.yml both

`subscriber-list.yml`, below, runs `tests/test_waitlist.py` and
`tests/test_unsubscribe.py` and nothing else. This file runs both of them
inside the suite, so applying this one makes that one two duplicate steps
on every pull request. Both were filed by this seat, four days apart, and
the second one makes the first unnecessary rather than wrong.

Apply this file and `subscriber-list.yml` can be dropped. Apply
`subscriber-list.yml` alone if the one-step change is too large to take
today, and this file keeps waiting: it guards the signup path, which is the
one surface in this repository a stranger touches directly, and that is
worth a narrow guard today over a broad one later.

### What is still not guarded after this is applied

The job installs no `node_modules`, so `tests/test_markdown.py`'s one
`marked` comparison stays skipped. That is the only skip in the suite that
a package would resolve, and it is the renderer's own library rather than
the rule under test.

## checks.yml — APPLIED 2026-09-29, and this section is history

**Moved to `.github/workflows/checks.yml` by the chair in `4ef55df` on
2026-09-29** ("checks.yml goes live (queued by engineer, applied by
chair)"), ten days after it was filed. The file is no longer in this
directory. Everything below is kept because it is the record of what the
guard is for, and because the near miss in it is the best example this
directory has. Read it in the past tense.

One thing the move taught, and it belongs at the top of this file rather
than buried here: the applied version runs on `push: branches: [main]` as
well as on pull requests. It did not have that trigger while it sat here,
and two runtime changes were pushed directly to main in the gap and left
two guards red for six days
(`INC-2026-09-30-the-guard-went-red-and-nobody-read-it`). **A guard
scoped to pull requests is not a guard on a repository whose owner
commits directly.** Any workflow filed here that is meant to protect main
gets both triggers before it is filed.

### What it was filed for

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

### It was pending for ten days, and this was the cost while it was

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

## adr-numbers.yml — every ADR number names one decision

Filed by the ExO seat 2026-09-30. Fails a pull request, or a push to main,
when `docs/decisions.md` contains two `## ADR-N:` headings with the same
number, printing both line numbers and the next free number.

**It will fail on its first run, and that is the point.** ADR-38 is
currently two different decisions on main: "Skills close the loop with
their consumers" at line 1337 and "The skill quality bar" at line 1384,
written eight minutes apart on 2026-09-29. Renumbering the second to
ADR-39 and updating its references is the chair's edit, because
`docs/decisions.md` is not a seat's surface.

**Why a check and not a convention.** The incident register hit the same
defect four times with its own sequential numbers and fixed it by
convention, moving to `INC-YYYY-MM-DD-slug`. The story it tells about
itself is that seats write on branches and read different snapshots. That
story is not what happened to ADR-38: one author, one branch, eight
minutes, two consecutive direct commits to main. The allocator is "read
the file, add one", and the file was read once. A convention would not
have helped, and `docs/agents/registers.md` already names the general
form of this: **recording is not enforcing.**

It reads one file, needs no key, no network and no database, and runs in
about a second. All three of its paths were exercised before it was
filed: the duplicate (exit 1, both lines named), a fixture with the
second heading renumbered to ADR-39 (exit 0, "39 ADRs, every number
unique"), and a `decisions.md` with no ADR headings at all, which exits 1
rather than passing silently, because a heading-format change would
otherwise turn this check into a guard in name.

    git mv .github/workflows-pending/adr-numbers.yml .github/workflows/adr-numbers.yml

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

## subscriber-list.yml — the signup and the unsubscribe are guarded

Filed by the engineer seat 2026-10-06 with sprint 2026-10-05 items 2 and 3.
Runs `tests/test_waitlist.py` and `tests/test_unsubscribe.py` on any change to
the signup path, the unsubscribe path or `db/schema.sql`.

**Why a new file rather than two more steps in `checks.yml`.** A seat's token
has no `workflows` permission, so `checks.yml` cannot be edited from a seat's
run at all, and this directory is the lane that exists instead. The paths and
both triggers are already right, per the rule at the top of this file.

What it holds is the half CI can hold without a database. Every SQL statement
in `site/lib/waitlist.js` and `site/lib/unsubscribe.js` is parsed with
libpg_query and every relation and column it names is resolved against
`db/schema.sql`, which is why that file is in the paths. The signup's row is
asserted to be `status = 'active'` and comped, because `pipeline/weekly.py`
sends to active rows only and anything else is a row waiting on a human, which
clause 1 of the sprint's definition of done rules out. The unsubscribe route is
asserted to export POST and no GET, because mail scanners fetch every link in a
message before a person reads it.

Four deliberate breaks were confirmed red before it was filed: a `'waitlist'`
status, a `statuss` column, a GET handler on the unsubscribe route, and an
update scoped by email address rather than by token.

Until it moves, those 44 assertions run in exactly one place, which is whichever
seat remembers `python3 -m pytest tests/ -q`. The signup path is the one surface
in this repository a stranger touches directly.

    git mv .github/workflows-pending/subscriber-list.yml .github/workflows/
