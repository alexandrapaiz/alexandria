# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-09-28 (Monday ceremony)

**Own-seat PRs reconciled.** This ceremony's branch (pm/sprint-2026-09-28)
merges in four of this seat's own open PRs (#125, #121, #117, #113) rather
than leaving them to collide with this run's writes to the same files.
See this PR's description and docs/sprints/pending.md for detail. #117's
own entry below (2026-09-26 standup) is carried forward rather than
repeated.

**Nothing proposed and nothing fired this run.** Checked in order per
charter §4: `gh run list` (three already-registered engineer-agent
notify-step failures, no new class — see pending.md's run-health
section), `gh pr list --state open` (every dispatchable seat with an
open PR — engineer #127, writer #126, okr #114 — is excluded by the
hard stop against dispatching a seat whose last PR is still open), the
board (the one standing candidate from the last three days, the
board-ui item, has moved from `assignee: frontend` to being built by
`engineer` directly across PRs #115/#122/#127 and is now `In progress`
there, so that trigger no longer applies to frontend), and
docs/decisions.md/allhands (no new ADR or ruling since 2026-09-25's
ADR-35 names a seat with no run following it — skill and research have
both already run under it).

That leaves research, market, frontend, skill, and security as
eligible seats with no open PR, and none of them carries an observed
trigger this run: each is inside its normal weekly cadence with no
failed run, no stale draft, no due milestone, and no un-acted-on ruling
naming it. Per charter §4's own rule, an entry with no observed trigger
does not go in the queue, so the queue holds none today rather than
inventing one to fill it.

**Two items worth the owner's attention that are not dispatch
candidates, because they wait on her, not on a seat's run:** the Polar
Merchant-of-Record account (ADR-30, now overdue) and PR #60's merge
(8 days open, the oldest in the repository). Both are in
docs/sprints/pending.md's top three, not here, because no
`gh workflow run` command would move either one forward.

## Dispatched by the PM

None fired this run. See "Nothing proposed and nothing fired this run"
above for why. The standing, already-escalated defect
(INC-2026-09-24-dispatch-403, INC-2026-09-26-dispatch-403-repeat) that
has 403'd every dispatch this seat's own scheduled run has attempted so
far was not re-tested this run, since no candidate reached the point of
attempting a command.

## 2026-09-27 (Sunday standup, superseded above)

Reconciled into this run rather than repeated in full; see this
ceremony's own entry above. The prior day's frontend dispatch was
attempted and 403'd a third time (INC-2026-09-26-dispatch-403-repeat);
that trigger no longer applies as of this run, per the board note
above.
