# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-09-30 (Wednesday standup, scheduled cron, second standup of the day)

**Queue: empty.** Every dispatchable seat (engineer, research, market,
writer, frontend, skill, security, okr) already holds at least one open
pull request from last night's synchronous window session (PRs #145-#164,
opened 2026-09-30T02:00-03:54 UTC while the owner was live). That is the
hard stop under charter §5 and company standard §11.4 for all eight seats
at once, unconditionally — no instruction here would tell any of them to
build on the open branch, because none of today's evidence points at a
gap any of those seats' own open work doesn't already cover. Same
finding as the window session's own last standup (PR #165, 03:54 UTC):
nothing has changed since, because nothing has merged since (last merge
was PR #143 at 02:08 UTC; `gh pr list --state merged` confirms no PR has
landed in the ~13 hours between that window ending and this run).

## Run health

**Fleet health.** Quiet since the last PM run (PR #165, which accounted
for everything through 04:02:35 UTC). `gh run list --limit 50` shows
nothing between 04:02:35 UTC and this run's own start: the only two runs
in that gap are `engineer-agent` and this `pm-agent` run, both
`schedule`-triggered and both still `in_progress` as this is written. No
non-success to account for. The prior run's own open item (main's red
"digest request fits the model's budget" check, cost/backoff and
GH_TOKEN-JSON causes, handed to engineer) is unchanged: engineer's own
break-fix PR (#158, "break-fix on main's red checks") is already open
against it, so it needs no new dispatch, only the owner's merge.

**Delivery health**, via `tools/delivery_health.py` (exit 2, not clean,
and that is the honest answer rather than a false green):

- **The press.** `unknown` — no `DATABASE_URL` in this sandbox, so the
  `digests` table itself cannot be read here, same as every standup
  since incident 24. Not due again until Monday 2026-10-05's cron, so
  this is not a staleness finding, only an unanswered one.
- **The site.** `ok` — `libraryofalexandria.dev/library` serves, newest
  issue still 2026-W39, consistent with no new issue being due yet.
- **The MCP server.** `ok` — up, and correctly refusing an
  unauthenticated call.
- **The pipeline.** `unknown`, same cause as the press.

**The company board**, now readable from this sandbox (`BOARD_API_URL`
and `BOARD_RUNTIME_TOKEN` are present this run, where the last PM run
reported neither). Read in full (`tools/board.py show`). Nothing is
addressed to the `pm` seat specifically; the owner's live request from
last night's session (read `pm`'s inbox, reply in first person) was
scoped to that synchronous window and there is no standing inbox
mechanism beyond items and comments, which this run checked and found
empty for this seat. The open-sprint board ("Launch-ready newsletter,"
2026-09-21 to 2026-09-27) is 3 days past its own `ends_on` date with
work still in its "This sprint" column — worth a ceremony-run look at
whether the board's sprint record needs closing alongside
`docs/sprints/sprint-2026-09-28.md`, not something this standup
reconciles on its own per charter §4's scope.

## Pending items past their date

Full reconciliation is ceremony-only (§1d); two items in
`docs/sprints/pending.md` are now far enough past their date to name
here rather than wait for Monday:

- **The Polar Merchant-of-Record account (ADR-30)**, due 2026-09-26, is
  now 4 days overdue. No live Polar keys appear anywhere in the
  codebase as of this run. O1 KR1 needs the $20 spine purchasable by
  2026-10-13 (13 days out), and checkout wiring cannot start until this
  account and its keys exist. This has been the single most
  launch-critical open item in the tracker since the 2026-09-28
  ceremony and nothing in last night's window session changed that
  (`docs/finance/` was not checked this run for a status update beyond
  PR #164, still open).
- **PR #60**, the pre-send quality checklist, is now 10 days open, the
  oldest open PR in the repository. The 2026-09-30 window session's own
  standup (PR #165) already flagged it as a close candidate rather than
  a merge one, past the seven-day line; repeating here only because a
  PR this old with no new action owed from any seat is exactly what
  this section exists to surface.

## GitHub Projects board

Not checked this run to keep it cheap (charter §4): the company board
above is the fuller, live answer to the same question and was already
read in full.

## Linear trial

Still on. No verdict change since 2026-09-19; unchanged from the last
several standups.

## Dispatched by the PM

None this run. Queue was empty; nothing fired.
