# Engineer run note, 2026-10-25 (message)

## Trigger

#500 merged. The event asked for the next item in this seat's lane on the
board, and for this run to say which one it took.

**Not a duplicate wake, and no open pull request from this seat.**
`gh pr list --state open` returned seventeen, none with an
`alexandria-engineer/` branch. #500 is on main at `edd22941`. So there is no
chain and nothing to supersede, which is the first run in several days that
can say that.

## What the lane held

Four cards, all in `This sprint`, and all four close with a hand this seat
does not have.

| card | what closes it |
|---|---|
| Compute: the Modal workspace is switched off | re-enabling the workspace, an account state on Modal's side |
| Deploy: weekly is not running main | `modal deploy`, a Modal token |
| Press: no issue for 2026-W41 | `modal run pipeline/weekly.py::resend`, a Modal token |
| Checkout: no offer on the pricing page can be bought | three `POLAR_CHECKOUT_*` values in the site's environment |

That table is the same table, card for card, that the run of 2026-10-24 wrote
at the top of its own note. Two runs in a row have paid to discover it, so it
is registered as
`INC-2026-10-25-the-engineer-lane-was-rediscovered-as-owner-blocked-for-the-second-run-running`
rather than written a third time into a surface nothing reads.

Two of the four also carry numbers that have moved. `Deploy` names
`0cbc51a0e248`, where production now records `2e313065f5c7` for weekly and
main computes to `8452336438d9`, so weekly is further behind than the card
says. `Press` says "the newest issue on record is 2026-W40", where
`/api/delivery` reads `2026-W42` written 2026-10-19, so the press is less
behind than the card reads: the 2026-W41 gap is real and still open, and
2026-W42 shipped. Both conclusions hold. Both numbers mislead, in opposite
directions.

So the day's work was taken under the charter's fallback, an `accepted` ledger
entry no sprint picked up, and the item it continued is the one the board
could not offer: the next correction to the slow loop this seat shipped
yesterday.

## Observe

- **Main's guard is green**, `success` at `edd22941`, 2026-10-25T02:55Z.
- **Machinery diff, 36 hours.** Three commits under `pipeline/`. `5c086ca5` is
  merged PR #443; `f8e02811` and `7cb9d838` are #498 and #500, both merged.
  No unexplained runtime change, so nothing to file under
  `docs/agents/runtime-changes.md`.
- **Pipeline health.** Skipped as a Modal read, because the workspace is
  disabled, so there are no cron runs and the CLI has nothing to authenticate
  against. Read from `https://libraryofalexandria.dev/api/delivery` instead,
  which is what produced the finding below.
- **Sprint.** `sprint-2026-10-12.md` is still the newest, now fourteen days
  old. Already filed in the ledger by the previous run.

## What the delivery receipt said that nobody had asked it

`interpret_pending: 0`.

Yesterday this seat shipped the slow loop's trigger and argued it was safe on
one sentence: the fresh queue is 2,000-odd deep, so `rejudge_budget` returns
nothing and the loop stays latent until the drain catches up. That sentence
was written into a docstring, into a test name, and into
`docs/product/graph-quality.md`.

The queue did not drain. It moved one stage upstream. `distill_pending` is
3,680 and no claim has been written since 2026-10-22, because distill is what
makes claims and the Modal workspace has been off since 2026-10-23. An empty
fresh queue and a deep one are indistinguishable to a rule that takes the
leftovers, so the sweep takes whole runs from the first one after deploy
rather than none.

Nothing about that is a defect in the trigger. It is bounded by the
`max_claims` and `CAP_USD` the job already had, so no run can cost more than
it could before the loop existed, and it terminates, because every pass writes
a row including the passes that find nothing. What was wrong is the claim that
it was free. And the reason that is worth more than the correction: **a safety
argument keyed to a queue depth is a reading with an expiry date, and this one
expired the day after it was written.**

## Work

Three changes, one unit.

**The sweep is ordered by what it buys.** `REJUDGE_QUEUE_SQL` ordered by
`c.id`, which was free when the sweep returned nothing. A claim carrying a
pass under a known older prompt sha is the slow loop's own case, because two
prompts read it and the second verdict is a changed mind or a confirmation. A
claim whose only pass is the backfill's `unknown` has no comparable prior
verdict and re-reading it mostly buys a row. Both are due and both terminate.
A run the cap cuts short should now be cut short at the cheap end.

The select became a `left join lateral` rather than an inner join, which is
not cosmetic. Every `interpreted_at` claim got a backfill row, so an inner
join looks safe, and it is not: a claim judged by an image older than
`claim_judgments` but running after the backfill has `interpreted_at` set and
no row at all, and an inner join would make it unreachable by the one job that
would ever give it one. That case has its own test against a real server.

**The sweep has a bill before it is spent.** `drain` priced the fresh backlog
in runs and dollars and gave re-judgment a bare count, so the one queue that
can take a whole run was the one with no cost attached. It now reports the
sweep's runs and dollars the same way, and splits the depth into the passes
under a known older prompt and the `unknown` rows, because depth alone cannot
say whether a sweep is worth its cap.

**The expired premise is named rather than replaced.** The `rejudge_budget`
docstring, the test that asserted latency, and the design doc all quote the
sentence that was wrong and say what read false and when. None of them
substitute a newer number, because a newer number is the same mistake.

## Evidence

`python3 -m pytest tests/test_rejudge_queue.py -q`: 40 passed, up from 31,
with nothing skipped. This host has PostgreSQL 16, so the DB-backed half ran
rather than skipping, which is the stronger evidence the suite's own docstring
asks for. The new tests include the ordering proved against a real corpus the
backfill recovered, the unreachable-claim case, and the libpg_query parse of
the rewritten query against `db/schema.sql`.

## Scope held

No change to the spend rule itself. `(0, 90, 90)` is an explicit decision the
previous run wrote down as a test parameter, and reversing a day-old decision
unilaterally is the thrash a retrospective should not have to find. The
ceiling it would need is also a judgment about a daily bill, which is the
owner's. It is a ledger entry, and the forecast built today is what it should
be decided against.
