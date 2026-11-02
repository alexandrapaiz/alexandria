# Engineer run note, 2026-11-02 (message, checks-red wake)

Three events on one wake, plus a standing block. The standing block named PR
#659. `GET /api/standing`, read at the start of this run, named #684 instead,
because #659 merged at 02:03:08Z and the block attached to the wake was read at
01:15Z. The payload's own instruction to confirm a standing condition live is
what produced that correction, in one call, and it is the only one of the four
conditions that carried such an instruction. The other three cost six tool calls
to establish the same kind of answer, which is this run's register entry.

## The predecessor: #684, read and then superseded

#684 is this seat's own run from 01:07Z, on the branch name this run was handed.
It is not a stub. 927 insertions across ten files: a second fetch route for the
paper reader with its first test file, the frontmatter detector's fix, two
incident entries, three ledger entries and a craft scan. Its branch head ran
green at 01:51:14Z.

So the charter's first move was the right one. This branch is #684's tip with
`main` merged into it, `git log --oneline origin/alexandria-engineer/2026-11-02-message ^HEAD`
printed nothing before #684 was closed, and the branch is kept. Second in a
chain: #659 to #684 to this one, and #659 is already on `main`, so the chain's
review burden is one run of work on top of one merged run rather than three.

## Both red checks: already green, verified rather than trusted

The two events name runs `41371440532` and `41372385293`. One cause for both:
`tests/test_skill_receipts.py` asserts the hand-written frontmatter parser and
PyYAML agree about every shipped skill, and `skills/harness-engineering/SKILL.md`
was a file the parser accepted and the loader refused. Commit `8fe6a858`, ten
minutes after the first failure, is the repair, and it is on this branch and on
`main`.

What was checked here rather than read off the reports:

```
$ python3 -m pytest tests/test_skill_receipts.py -q
27 passed

$ gh run list --workflow=checks.yml --branch=main --limit 5
success  02:03:12Z  39f9dd8e   (the merge of #659)
success  00:28:33Z  671b1eea
success  00:07:05Z  e1bbb198
success  23:55:03Z  bfd63c02
success  23:31:21Z  cdd8bd2e
```

`main` is green and was never red in this window, so the daily red-main duty
found nothing to fix ahead of the day's work. The machinery diff,
`git log --since="36 hours ago" -- .github/ pipeline/` against `origin/main`, is
empty, so there is no runtime change in the window to ask the two
runtime-changes questions about.

Nothing was left red and nothing needed fixing to get there. That is the finding
rather than a dodge of the instruction, and the register entry is where the cost
of establishing it is written down.

## The day's build: the press records that it was invoked

The ExO seat's handoff of 02:00:02Z, carded rather than asked. `record_runtime`
writes `deploy_runtime`, which is the only row in this system that says a
scheduled job ran at all, and in `pipeline/weekly.py` it sat after the
availability check, after the two prompt reads and after the connect. A death
above it left no row. `notify_owner` is inside the same `try`, so a death above
the `try` left no mail either, and a mail is a record a person reads rather than
one a seat can query.

**The choice the card left open, and why this one.** The card offered two: move
the first durable write ahead of the first thing that can fail, or give
`notify_owner` a row. The first is the one that closes the question, and the
reason is that the two options have different reach rather than different cost.
Every durable write here needs the database, so the connect is the floor: no
row of any kind survives a database that cannot be reached, whichever path
writes it. Moving the record to immediately after the connect makes the row
exist for every run that could write one at all, and moving the prompt reads
below it brings the one failure that previously reached nobody, a prompt file
missing from the image, which raised above the `try`, inside the handler that
mails. An alarm row would reach the strictly smaller set.

So `weekly` now opens its own short-lived connection at the top of its `try`,
writes the record, closes it, and then does everything else. Its own connection
rather than the run's, because the run's connection closes before the model call
on purpose: Neon terminates a connection left idle in a transaction, and that
cost the press a written issue on 2026-09-24. The availability check is a
network call, so holding the run's connection across it would have reintroduced
exactly that.

**The second half of the card falls out of the same line.** `first_seen_at` is
written by the same upsert, so the drift guard could not date a deploy of
`weekly` until a run reached the old line. It can now.

**The class is five wide and four of it is not in this diff.**
`tests/test_deploy_drift.py` gains a measurement over every app in
`runtime_sha.APPS`: how many statements of the scheduled entry point run before
the first durable write. Pinned so it can shrink and cannot grow, which is the
shape `tools/ci_coverage.py` already uses.

```
weekly     7   docstring, two imports, the week-label parse, the try, the connect
triage     9   llm(), load_prompt(), usable_models() over the network
interpret  10  the same three, plus maintenance_step()
distill    13  the same three, plus a SentenceTransformer import and the windows
ingest     9   every feed fetched and judged, and judge_sources raises by design
```

`ingest` is the one worth reading twice. `judge_sources` raises
`NothingToIngest` on a bad feed day, deliberately, and that happens before the
record. So the single day ingest has a real failure to report is the day it
leaves no evidence that it ran. The four are a ledger entry rather than this
diff because a reorder inside a model-calling job is a runtime change under
`docs/agents/runtime-changes.md` and wants a rehearsal per app, and four
rehearsals is not one day. `ingest` is first in that entry because it calls no
model, so its chain is a bare deploy.

**Both gates were rehearsed red before they were trusted.** The pin, against a
statement added above the record inside the `try`: red, and it named the
statement. The press's source-order claim, against the record moved back below
the prompt reads: red on both markers. The first draft of the pin counted only
the entry point's top-level statements, so the repair's own `try` hid everything
inside it and the deliberate break passed. That is written into the test's
docstring, because a gate that cannot see the edit it exists to catch is this
register's recurring defect rather than a detail of this one.

## The card's third item: `tools/ci_coverage.py`

The ExO seat reported it exits 1 at 14 of 78 test files, and that no workflow
runs it, and that nobody has it. Two of those three are right and the third is
not, which is the useful answer.

It is owned. `.github/workflows-pending/checks.yml` is a replacement for the
live `checks.yml`, filed by this seat on 2026-10-07 for item 17 of
`docs/agents/pending-workflow-changes.md`, and it replaces the fourteen named
pytest steps with one step that runs the suite. A seat's token has no
`workflows` permission, by design, so the whole change is one command and it is
the chair's:

    git mv -f .github/workflows-pending/checks.yml .github/workflows/checks.yml

Re-measured here rather than taken from the file's own argument:

```
$ python3 tools/ci_coverage.py --only .github/workflows-pending/checks.yml
81 of 81 test files run in CI
$ python3 -m pytest tests/test_ci_coverage.py -q
24 passed
```

What is new and worth the chair's attention is the drift. That README argues
from "the suite holds 49 test files, the live workflow runs 14." The suite is 81
now and the live workflow still runs 14, so the gap went from 35 to 67 while the
file sat parked for 26 days. One of the 67 is `tests/test_ci_coverage.py`
itself, the gate that pins the uncovered set so it can shrink and cannot grow.
A gate no workflow runs cannot stop the set from growing, and the set grew by
32. The README is re-measured in this diff with that sentence in it.

## Ledger and the craft scan

Three entries and one scan note, all dated 2026-11-02. The four jobs that can
still die without a record, with `ingest` named as the first step. A
`finished_at` to pair with the start signal the repair above creates, so
"started and never finished" is a query rather than an inference. And the
receiver-side half of the resolved-condition remedy, which is a charter sentence
and therefore a proposal rather than an edit.

The craft scan went to Healthchecks.io, read live on 2026-11-02, because this
run's build was an invocation record and that product's whole job is the same
question. The stealable thing is two signals rather than one: `/start` and the
bare ping, with run time measured as the gap between them, `Started` as its own
state, and the alerting rule that a start with no success inside the grace time
is a failure. That is precisely the state this run's repair creates and does not
yet read. What alexandria does better is that nothing here holds a second copy
of the schedule: Healthchecks asks you to type the cron into its UI, where
`runtime_sha.schedule_of` parses it out of the job's own source and refuses
rather than guesses when a module carries two.
