# Engineer run note, 2026-11-02 (message): the by-id ask answered by the route that needs no credential

Woken by `message`. Three notes in the inbox, each delivered truncated at the
tail, which is where the sender's disposition lives, so the first act of the run
was to read all three in full on the board.

## What the three asked, and what each got

| From | Asked | Done |
|---|---|---|
| research, 02:49 | one `modal run pipeline/ingest.py --ids 2602.05366,2510.22670`, or the shape if a hand run is the wrong answer | the shape, and both ids queued on the route that needs no credential |
| writer, 03:20 | nothing; handed this seat one finding on its own card | the receipt widened, and two more columns found that were already being dropped |
| exo, 03:06 | nothing; withdrew its second option | answered with a live instance of the parked-suite cost |

## The research handoff, which was the day's work

The ask was impossible and that is a fact about this host rather than a
decision. There is no `modal` binary here and no Modal or Neon name in the
environment, which makes twelve consecutive runs of this seat without the
credential rather than the eleven the handoff counted.

Their tail asked for the shape over the one run, and the shape turned out to be
better than either seat had. **The by-id backfill is not the only route to the
corpus. It is the only one that needs a credential.** `pipeline/distill.py`
resolves every unchecked line of `docs/research/reading-queue.md` against
`papers` and ingests what the corpus has never seen, at tier `b`, with a
`deep_read` triage row the by-id path does not write, ahead of the day's intake.
Writing to that file is a commit. So the queue route holds the paper and reads
it, where the backfill only holds it, and it is the route that can be taken from
a sandbox with no secrets in it.

Why the asker reached for the blocked one is in this seat's own file.
`pipeline/ingest.py`'s local entrypoint docstring said `--ids` is "the entry
point the reading queue needs when a line names a paper the window cannot
reach". It is not, and `pipeline/distill.py` says in its own docstring that it
is. Two modules disagreeing about which one serves that file, and the
disagreement readable only by opening the module you were not already reading. A
seat working the ingest window reads `ingest.py`, finds a sentence addressed to
exactly its problem, and has no reason to open `distill.py` at all. Filed as
`INC-2026-11-02-the-handoff-asked-for-the-blocked-route-because-the-docstring-of-the-blocked-one-claimed-the-other-ones-job`.

Three things shipped for it, in increasing order of how long they outlive this
run.

1. The docstring names both routes and what each one is waiting for.
2. `python3 pipeline/reading_queue.py --add` is the writer that file had no
   version of. It refuses an id already in the file with every line it is on and
   whether each is struck or open, which is the grep rule from
   `INC-2026-10-27-a-paper-struck-as-read-was-requeued-as-the-highest-value-unread-paper-the-next-day`
   turned from a rule into a gate. It refuses a line the module's own parser
   would not read back as exactly one unchecked request for the id asked for,
   because `parse` skips what it cannot read and a malformed request is not a
   broken request, it is a request that silently does not exist. It appends and
   never inserts.
3. Both ids are on the queue, written by that command. 81 pending before, 83
   after.

**What is not fixed and is not this seat's to fix.** Neither route runs today.
The workspace has been off since 2026-10-23 and the deploy has been behind since
2026-10-17, and the queue's content is baked into distill's image at deploy time,
so these two lines reach the cron on the next `modal deploy`. The difference the
commit buys is not speed. A request for a hand run dies with the wake that
carried it and a commit waits.

**And no, this does not belong in a scheduled backfill**, which was the other
half of what the handoff asked. A new cron in `pipeline/ingest.py` needs a
`modal deploy` to exist at all, which is exactly what the queue route is already
waiting for, so it would buy a second blocked path rather than an unblocked one.
The queue route is already scheduled. It needed a writer and a corrected
signpost.

## The writer seat's finding, and the two columns nobody was looking for

`tools/delivery_health.py` is the only reader of `deploy_runtime` outside
`pipeline/`, so every instrument that asks what a scheduled job reported asks
through `deploy_facts`, and that function named five columns. The writer seat
found it while `invoked_by` was still only a card, which is the only point at
which it costs nothing.

It was dropping two columns that already exist. `entrypoint` and `file_count`
have been in `db/schema.sql` since the table was created, the schema's own
comment calls `entrypoint` the value "for the deploy command", and neither has
ever reached a reader through that function.

**The reason nothing caught it cost twenty-five red tests to find.**
`tests/test_deploy_drift.py` has sixty-two cases against that table and its
`FakeConn` answered every query with anonymous tuples and no `description`. A
reader that names five columns and a reader that names all seven are
indistinguishable from inside that suite, by construction, so the column list
was unobservable to the one suite that exists to watch the column. The fake now
carries `RECEIPT_COLUMNS` and asserts every row's width against it. Sixty-two
pass.

## The runtime question, asked and answered rather than skipped

Nothing in this diff is a runtime change by `docs/agents/runtime-changes.md`'s
list. No workflow, no image definition, no base, no cron, no timeout, no secret,
no model, no provider, no reservation. `pipeline/ingest.py` changed by one
docstring. `tools/delivery_health.py` is a hand and standup tool and is not
scheduled.

One consequence worth stating rather than leaving to be discovered.
`pipeline/reading_queue.py` is a file distill's image adds, so changing it moves
distill's `runtime_sha` and the drift guard will report distill as drifted. It
already does: the deploy has been behind since 2026-10-17. The added code is
module-level pure functions and a CLI branch that the scheduled path never
reaches, so a deploy of it changes no behaviour of a distill run except that the
queue file it bakes in has two more lines.

## Gates, and every one rehearsed red against its own break

Nine on the queue writer, seven of them with a rehearsed break: the duplicate
check blinded, the version suffix kept, the section guard removed, the written
line struck, the route sentence stripped of its command, a dry run that writes,
and an append that also strikes an unrelated line. That last one is the one
worth naming, because the gate that caught it was "append, never insert" and not
the count: the test fixture carries the same id on two lines, so striking one
leaves the pending count correct. The CLI's own count gate has no rehearsed
break and is defence in depth rather than a measured guard, which is said here
rather than left to be inferred from a list of nine.

Four on the receipt, all four rehearsed against the fixed-five source. The first
draft of the fake connection ignored the statement it was handed, so the break
failed with `ValueError: too many values to unpack` from inside the code under
test, naming no column and reading like a bug in the test. The fake projects now,
and the same break prints `entrypoint is in deploy_runtime and no consumer can
see it`. The column list the gate asserts is read out of `db/schema.sql` at test
time, so the day `invoked_by` lands it is asked for with nobody editing the test.

## Numbers from this run

- `tests/test_delivery_health.py tests/test_feed_health.py tests/test_ledger.py
  tests/test_reading_queue.py`: 229 passed.
- `tests/test_deploy_drift.py`: 62 passed, after 25 red that this run caused and
  fixed.
- `tools/ci_coverage.py --report-only`: 14 of 81 test files run in any workflow.
  **All four of the test files covering this diff are in the 67 that do not.**
- `python3 tools/check_registers.py`: 0 blocking, 71 warnings, every one
  pre-existing.
- `python3 tools/check_authority.py`: no changed line answers yes to any of the
  four questions.
- `python3 tools/incidents.py check`: nothing malformed.
- `gh run list --workflow=checks.yml --branch=main --limit 5`: five successes.
  `main` is green, so there was nothing to fix ahead of the day's work.
- `git log --since="36 hours ago" -- .github/ pipeline/` on `origin/main`:
  empty. No runtime change landed in the window.

## One thing checked and deliberately not filed

`python3 tools/ban_list.py docs/research/reading-queue.md` reports 823 findings,
818 of them already on `main`. Almost all are U+2014, and the em dash is that
file's documented field separator: `- [ ] arxiv:<id> — why — asked by <who> —
date`, which three readers in `pipeline/` parse. So the ban list and the file's
machine format disagree by construction. It is not filed as an incident, because
the ban list governs "anything the owner will read" and this file is a
machine-read request log rather than prose. The two lines this run appended carry
six of those findings between them and they are the format, not a choice. Said
here so the next run does not re-measure it.
