# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-09-27 (Sunday standup)

**Builds on and supersedes #117** (`pm/standup-2026-09-26`, still open):
this run started from its two commits rather than from main, since both
touch this file and `docs/agents/incidents.md`. Close #117 once this PR
merges rather than reviewing both; nothing in it is lost, it is all on
this branch.

**Today is Sunday, not Monday.** The current sprint file
(`sprint-2026-09-21.md`) covers through today; tomorrow's run is the
ceremony (retro, grooming, the new sprint file), per charter §0. This
run is §4 alone.

### 1. frontend — the board's read-only view, re-attempted, still 403s

**Trigger.** Unchanged from yesterday: HQ ADR-037 priority 1 (relayed in
PR #113). Engineer's open PR #115 ships `docs/board.md` as the spec and
already queued item `board-ui` on the board ref (`status: next,
assignee: frontend`, unchanged since 2026-09-26). Frontend's own last PR
(#108) is merged, so the hard stop against dispatching a seat with an
open PR does not apply.

**Status: attempted again, not fired.** Same command as yesterday
(building on `engineer/2026-09-26-board-store` per PR #115 still being
open), same result:

```bash
gh workflow run agent-frontend.yml -f owner_instructions='Build the read-only board view on the site. Trigger: HQ ADR-037 priority 1 (relayed live in PR #113, "PM sync session 2026-09-26"), which the engineer seat then built in open PR #115 ("the board'"'"'s own store, and every run reports onto it"). PR #115 ships docs/board.md as your spec and already queued item `board-ui` on the board ref (status: next, assignee: frontend, note: "queued by the PM in #113; reads the board ref, see docs/board.md"). PR #115 is still open, so branch from engineer/2026-09-26-board-store, not main: tools/board.py, board/views.json, and docs/board.md only exist on that branch today. Per docs/board.md'"'"'s own "Reading it from the site" section: fetch the whole board with one request, GET https://codeload.github.com/alexandrapaiz/alexandria/tar.gz/refs/heads/board, untar server-side, keep files under board/events/, and fold them with the same rules tools/board.py fold uses. Do not use the GitHub trees API plus one request per file. Read the view columns from board/views.json rather than inventing your own. This slice is read-only: no view-creation UI, no workflow step, no item dependencies/labels/comments/due-date alarms. Move item board-ui to doing via `python3 tools/board.py item --id board-ui --status doing --assignee frontend` when you start, and to review when your PR is open.'
```

```
could not create workflow dispatch event: HTTP 403: Resource not
accessible by integration
(https://api.github.com/repos/alexandrapaiz/alexandria/actions/workflows/361059087/dispatches)
```

**This is the third occurrence** (2026-09-24, 2026-09-26, 2026-09-27),
all from this seat's scheduled run, all the same `ghs_` app-installation
token. Escalated to the ExO in `docs/agents/incidents.md`
(`INC-2026-09-24-dispatch-403`, third-occurrence note appended this
run), because a third identical failure with an unanswered diagnosis is
past the point where re-filing helps. The command above is exact and
ready for the owner or chair to run by hand.

### Why nothing else is in the queue

**engineer, writer, research, skill, and okr are all disqualified** by
the hard rule (last PR still open): engineer has #60, #110, #115, #116,
#118, #120; writer has #107, #112, #119; research has #109; skill has
#111; okr has #114.

**market and security have no fresh, evidenced trigger.** Market's last
PR (#103) is merged and its newest brief (2026-09-25) has nothing new
since the last standup read it. Security has had no run since
2026-09-24 and nothing in the newest decisions, market/research briefs,
or `pending.md` names undone security work today.

One entry, not three: the queue holds evidenced triggers, not a quota.

## Run health

**Fleet health, since the last PM run (2026-09-26T14:56:35Z, schedule,
success, produced PR #117).**

- **Two more occurrences of an already-open incident, work survived
  both times.** `engineer-agent` runs `36250253554` (schedule,
  2026-09-26T14:57:18Z, became PR #118) and `36285149176` (schedule,
  2026-09-27T01:18:48Z, became PR #120) both finished their real work
  (both PRs exist, complete, open) and then failed the job at the same
  Slack-notify `jq` parse error as `INC-2026-09-26-slack-notify-jq-control-chars`
  already named. Third and fourth occurrences of that class now,
  appended to the same entry rather than re-filed, and escalated
  alongside the dispatch-403 finding since a week of recurrences with no
  attempted fix has exhausted "wait for the weekly ExO read."
- **This run's own dispatch attempt 403'd again.** Third occurrence,
  see the queue entry above and the incident update.
- **Everything else since the last PM run is a plain success or
  already-registered**: `writer-agent` schedule (18:46:28Z, success),
  and the two engineer runs above (failed only at notify, not at work).
  Two runs are `in_progress` as this PR opens (`engineer-agent`
  `36330209631` and this seat's own `pm-agent` `36330174329`) — both
  started in the same minute as this run; their results are not yet
  known.

**Delivery health.**

- **The press.** No database credentials in this sandbox, so `digests`
  was not queried directly (same limitation every standup since
  2026-09-24 has noted). No new weekly issue is expected before Monday
  2026-09-28 09:00 UTC, so this is not a staleness finding on its own;
  reported as unchecked, not as green.
- **The site.** Not independently re-probed this run; last confirmed
  200 with current content on 2026-09-26's standup, nothing since has
  named a deploy failure.
- **The MCP server.** Not independently re-probed this run (checked
  deeper on 2026-09-26: `/mcp` answered 401 as expected and the OAuth
  discovery endpoint returned a well-formed body). Reported as carried
  from yesterday's check, not re-verified today.
- **The GitHub Projects board** (`PROJECTS_TOKEN` available): reachable
  via GraphQL against project 4 this run; a light read of the newest
  items showed `Done` statuses consistent with recent merges. Not a
  full board audit, which is a ceremony-run task.

## Pending items past their date

Read in full this run (`docs/sprints/pending.md`, last substantively
updated 2026-09-24; not rewritten today, reconciliation is a
ceremony-run job per charter §0/§1d). Two items worth naming a day past
their date, with the seat or party named:

- **PR #60** (engineer, "the pre-send quality gate") — open since
  2026-09-20, now a full week, the oldest open PR in the repo. `pending.md`
  has asked for "rebase or retirement" since 2026-09-24 with no action
  either way.
- **The Polar account setup** (owner-only action) was due 2026-09-26,
  yesterday. This run has no secrets access to confirm whether it
  happened.

The current sprint file (`sprint-2026-09-21.md`) itself reads stale
against the week's actual activity (accounts, Clerk, the board rebuild,
HQ's ADR-037 reorder) — worth flagging for tomorrow's retro rather than
fixing today, since rewriting sprint status is a ceremony-run task, not
a standup one.

## Linear trial

Not checked this run (no new signal since the 2026-09-19 ruling; PR
#113 notes HQ's priority 1 as direction to build the replacement, not
yet a recorded verdict to abandon Linear). Still on trial.

## Dispatched by the PM

None fired. One attempted (frontend, above), third identical 403,
escalated to the ExO in the incident register this run. The instruction
is recorded above for the owner or chair to run by hand.
