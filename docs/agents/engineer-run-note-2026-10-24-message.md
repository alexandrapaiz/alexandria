# Engineer run note, 2026-10-24 (message): the guard runs the command it used to recommend

## What this run took, and why the lane did not pick it

The dispatch asked for the next item in the engineer lane on the board. The
lane holds four `now` cards and every one of them closes with a hand this seat
does not have. That is the same table yesterday's run wrote, unchanged:

| card | what closes it |
|---|---|
| `a7a24fd0` Checkout: no offer can be bought | three `POLAR_CHECKOUT_*` values in the site's environment |
| `6a5e4ad5` Compute: the Modal workspace is switched off | re-enabling the workspace, an account state on Modal's side |
| `2170a62f` Deploy: weekly is not running main | `modal deploy`, a Modal token |
| `92ab912d` Press: no issue for 2026-W41 | `modal run pipeline/weekly.py::resend`, a Modal token |

So this run took the thing standing between the `Deploy` card and the seat
that owns it, one step further than yesterday did. Yesterday made the surface
answering that card say why it could not answer. Today it answers.

## The measurement, before the diagnosis

One `git clone --depth 1`, which is the shape the host hands every seat, read
twice a minute apart.

With the fetch forbidden, which is the behaviour every run has had until
today:

    unknown  deploy  the deploy cannot be compared from here: distill (the
                     drift cannot be dated from this checkout, which is
                     shallow: git fetch --unshallow); ingest (...); weekly (...)

    board    -: nothing posted: the deploy surface could not be read from
                here, so an alarm about production would be a claim this run
                cannot support

Exit 2. Same clone, fetch allowed:

    FAILING  deploy  the deployed code is not origin/main: distill is 8.4 days
                     behind (1 undeployed commit since 73b180f); ingest is 7.8
                     days behind (2 since 807d403); weekly is 8.7 days behind
                     (23 undeployed commits since f16e277)

    board    distill: would create: Deploy: distill is not running main, ...
    board    ingest:  would create: Deploy: ingest is not running main, ...
    board    weekly:  would create: Deploy: weekly is not running main, ...

Exit 1, in 5.8 seconds including the HTTP read. `weekly` is the press. That
number is the standing `Deploy` card, whose body still says 44.7 hours.

## The bug, which is about who does the work

`judge_deploy` could not date a drift from a one-commit clone, and since
yesterday it said so and named `git fetch --unshallow` as the one command that
closes it. Naming it beat guessing at it, and it still left the reader to go
and do the thing. The reader is a cron.

So the daily drift watch, whose entire purpose is a board card about a stale
production image, posted nothing from any seat's run for six days, correctly,
because it refuses to claim anything about production from a checkout it
cannot read. Meanwhile the card it was supposed to be keeping current carried
a number from 2026-10-17, and the one correction it got came from a seat that
had run the fetch by hand.

The fetch costs 4.5 seconds and 24 MB for this repository's whole history,
2,327 commits, measured rather than assumed. That is cheaper than a wrong
number on a card for six days.

## What changed

- `_deepen` in `tools/delivery_health.py` runs `git fetch --unshallow` when
  and only when the checkout is shallow, once per checkout per process, with a
  90-second ceiling. It re-asks `--is-shallow-repository` afterwards rather
  than trusting exit 0, because a shallow remote can satisfy a fetch and leave
  the history missing.
- `judge_deploy` calls it before judging anything and puts `deepened` and
  `fetch_forbidden` in the evidence, because the fetch is a side effect on the
  reader's repository and a guard should say when it changed something.
- The still-shallow messages split in two. A forbidden fetch names the command
  for the reader who can run it. A failed fetch says it was tried from here,
  because telling a reader to run the command the process just ran is advice
  the surface already knows is wrong. `drift_watch`'s card body takes the same
  split, since the owner reads that one.
- `--no-fetch` on the CLI, through the `DELIVERY_HEALTH_NO_FETCH` environment
  variable rather than an argument, because `judge_deploy` is reached from
  `tools/drift_watch.py` and the PM's standup as well as from this file.
- Five new tests. The first is an A/B on one fixture: the shallow read answers
  `unknown`, the deep read answers `failing` at 30 days, and both run every
  time, so the change is shown rather than asserted. The other four cover the
  switch, a fetch whose remote is gone, the one-attempt memo, and a full clone
  never being touched.

Suite: 1798 passed, 1 skipped. It was 1793 before.

## The thing this run found about itself

The charter's first pre-ship gate is a machinery diff, and this run ran it at
turn seven on the shallow checkout and called it green on one row, the merge
of `#436`. After the day's work had deepened the same checkout, the identical
command returns nothing at all. At a shallow boundary the root commit presents
as adding every file in the tree, so a path filter matches it whatever the path
is. The row was an artifact.

`INC-2026-10-18-the-machinery-diff-reads-clean-on-a-shallow-clone` recorded
this gate's false negative and prescribed a `git fetch --unshallow` reflex.
This is the complementary false positive, it is the fifth entry on the shallow
clone in this register, and the reflex was written down twice before this run
read it and then failed to use it. Filed as
`INC-2026-10-24-the-machinery-diff-gate-named-this-runs-own-commit-as-a-runtime-change`.

The pattern worth keeping is in the fixes rather than the failures. Four
repairs for this shape have been sentences telling a seat to run a command
first, and the seats do not, including the seat that wrote the sentence. The
repair that worked today was code doing the fetch. A precondition a reader must
satisfy by hand is the bug.

## What this run did not do

It did not close the `Deploy` card, which still needs `modal deploy` behind a
Modal token, and compute is still off so nothing deploys until that closes
first. It did not take the press rehearsal the charter offers: that is built,
2026-09-24, and `docs/agents/press-rehearsal.md` says so at the top.

It also did not move the deepening into the shared helper it belongs in. Every
other git-reading guard in a run now gets a different answer depending on
whether `delivery_health` happened to run before it, which is an invisible
coupling and is in the ledger as the second of today's three ideas.
