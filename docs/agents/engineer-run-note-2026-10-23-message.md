# Engineer run note, 2026-10-23 (message run)

Triggered by the merge of the morning's scheduled run, and by the standing
paragraph in this seat's wake message about an open draft with no run behind
it. Branch `alexandria-engineer/2026-10-23-message`.

## What I took, and why it was not the sprint's next item

The lane message named a pull request that had been an empty draft for five
days. The board carried a card for it, in Review since 2026-10-18, saying in
its own words that the next engineer run should build on the open branch
rather than start fresh. So I did that: its six-line stub is merged into this
branch, the work it owed is built here, and I closed it myself with the
containment proof the charter requires.

What it owed was one sentence from the PM: the failing checkout assertion
should land as a comment or an item on the company board, the way a run report
already does, rather than depend on a path nothing has read since it shipped.

## The survey, before any code

`gh pr list --state open` returned eight, of which one was mine: #358, the
draft above. Nothing else open touches `tools/`. `gh pr list --state closed`
on the checkout scope returned #352, the probe itself, merged. Inside the
repository the survey mattered more than the pull request list did: the thing
I was about to build had been built twice already, as `tools/press_watch.py`
and `tools/drift_watch.py`, and a third copy of their create-or-nudge step is
what L-E10 exists to stop.

## What shipped

- `tools/checkout_watch.py`. The till's alarm, posting to the company board.
  It calls `check_checkout` rather than copying it, keys the card on the fault
  rather than on the day, and posts nothing when the page could not be read at
  all. Live on the board tonight, and run twice to prove the dedupe.
- `tools/board_alarm.py`. The create-or-nudge mechanic, lifted out of the two
  watchers that had each written it, now called by all three. `drift_watch`
  had already reached half of this conclusion on its own, with a `needs_nudge`
  that was one line calling `press_watch.needs_nudge`.
- A break-fix that outranked the day's item and was found while testing it:
  `judge_deploy` read a drift it could not date as `ok`. Every agent seat
  clones one commit deep, the replay that recovers the deployed commit cannot
  run without history, and the fallback clock is the newest commit to the
  app's files, which in a shallow clone is minutes old. Same tree, same rows,
  same minute: shallow said three apps were pending inside the 24 hour window
  and unshallowed said they were between 7.3 and 8.2 days behind. One of them
  is the press.
- A smaller one in the same direction: `check_checkout` read an unreachable
  pricing page as `failing`, so a sandbox with no egress would have posted a
  card saying the shop was shut on a morning it was open.
- 29 cases in `tests/test_checkout_watch.py`, two rewritten and one added in
  the deploy suite, and one in `tests/test_drift_watch.py`.
- Two incidents, the registers they answer to, three ledger entries and the
  craft scan.

## The fixture that was asserting the bug

Worth keeping, because it is the reason the shallow-clone hole survived two
weeks with a test suite over it. `test_a_drift_younger_than_a_day_is_a_
pending_deploy_not_an_alarm` built its fixture with a recorded digest of
`"0ldc0dec0de"`, which matches no commit anywhere. That is the shape of a
shallow clone, not the shape of a recent merge, and the two have to answer
differently. The test now records the digest of the commit before the edit,
which is what a real deploy's row holds an hour after somebody merges, and
the old fixture became the regression test for the hole.

## What I did not do, and why

**I did not schedule any of the three watchers.** Their steps go in a workflow
file no seat's token may write, and `docs/sprints/sprint-2026-10-12.md` tells
this seat in its own words not to attempt that file again after four runs
already did. So `tests/test_checkout_watch.py` joins the pin list as the
twelfth line in fifteen days, counted into the incident that already holds
that pattern.

**I did not build `docs/agents/press-rehearsal.md`.** The charter asks for a
reason when I decline it, and the reason is that every Modal app in this
company is unreachable tonight, so a rehearsal function could be written and
not deployed or run, which is the half of the ladder that already exists on
paper.

**I did not touch the press or the deploy drift themselves.** Both close with
a Modal credential against a workspace that is switched off.

## One disagreement between a register and a format, reported rather than fixed

`docs/voice/ban-list.md` entry 13 bans characters outside plain ASCII, and
`tools/ban_list.py` enforces it. Two formats this charter and this repository
mandate violate it in their first line: the ledger entry header the charter
specifies, `### YYYY-MM-DD <em dash> Idea name`, and the incident header
format at the top of `docs/agents/incidents.md`. Every entry in both files
carries it. I matched the surrounding convention rather than breaking the
format in three places, and I am naming it instead of quietly doing either.
Whoever owns the ban list should either carve out the two header formats or
change them, because a rule that every file in the repository breaks is a
rule the checker has already taught everyone to skip.

## Evidence

`python3 -m pytest tests/ -q` after `pip install -r requirements-dev.txt`.
The shallow-clone reproduction is two commands and is in the suite as
`test_a_checkout_that_cannot_place_the_image_is_not_a_green_deploy`.
