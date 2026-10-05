# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-04 (Sunday standup)

Today is Sunday, not Monday, so this is a standup run (charter §4 alone):
no retro, no grooming, no new sprint file. The sprint ends tonight;
tomorrow's Monday run does the ceremony.

**Branch note.** This seat's last five runs (#150, #167, #173, #179,
#183, 2026-09-30 through 2026-10-03) are still open, and none has merged
since the 2026-09-29 standup landed on main. Branched from main rather
than building on #183, for the same reason #183 gave against #179:
`dispatch-queue.md` is replaced in full every run, so there is nothing
in any of the five to carry forward. This PR supersedes #183, which
transitively supersedes #179, #173, #167, and #150. Close all five
without merging once this lands. (`alexandria-pm/2026-09-30-window`,
#165, is the chair's own synchronous-session PR on a different branch
naming scheme, not part of this chain, and is left alone.)

## Queue is empty

Checked all eight dispatchable seats against the open pull requests.
Every one already holds an open pull request from its own last run,
the hard stop under charter §5 with no exception for firing:

- **engineer** — #185 (2026-10-04, today's scheduled run, supersedes #182)
- **writer** — #184 (2026-10-03, run 23, supersedes #180, #175, #169)
- **market** — #177 (2026-10-02, weekly ceremony)
- **security** — #174 (2026-10-01, run 6, supersedes #157)
- **okr** — #171 (2026-10-01, builds on #161)
- **research** — #145 (2026-09-30), open 4 days
- **frontend** — #168 (2026-09-30, supersedes #154), open 4 days
- **skill** — #152 (2026-09-30, draft, supersedes #151), open 4 days

`PM_DISPATCH_ENABLED` is `true` and no `workflow_dispatch` or
`repository_dispatch` event appears anywhere in the last 50 Actions
runs, so the owner-present guard is not what is blocking today's queue.
The open-pull-request hard stop is the whole reason, same as the last
several days: eight seats, eight open PRs, nothing left to propose.

## Run health

**Fleet.** One pattern to account for since the last PM run (#183,
2026-10-03 ~15:11 UTC): the `checks` workflow on the writer's newest
pull request, #184 (opened 18:52:19Z, after this seat's last run),
failed eight consecutive times between 18:52 and 19:14 UTC on
2026-10-03. Per #183's and #179's own run-health notes this is an
already-registered class, not new (a cost/backoff assertion and a
`gh pr list`-warning-breaks-JSON bug in the run-report test), but the
count is climbing across three calendar days with no fix landed yet
(2 on 10-01, 3 on 10-02, 8 on 10-03). Worth a line rather than silence,
since "already registered" has covered three days running now.
Everything else is green: today's scheduled `engineer-agent` run and
all seven of its `checks` re-runs on PR #185 completed clean.

**Delivery health.**

- **The press.** No database credential in this sandbox, so the
  `digests` table could not be queried; reported `unknown` per
  guardrail 4, not green. This is the same gap every standup has named
  since 2026-09-27 (`DATABASE_URL` still missing from this seat's
  workflow).
- **The site.** `https://libraryofalexandria.dev/` returns 200.
  `/library`'s newest issue is still `2026-W39`, which matches
  expectation: the next weekly issue is due tomorrow, Monday
  2026-10-05 at 09:00 UTC. Not a staleness finding.
- **The MCP server.** `https://ap4509--alexandria-mcp-serve.modal.run/`
  returns HTTP 404 on a bare unauthenticated GET — up, and correctly
  refusing rather than serving.

## Pending items past their date

Not reconciled this run (standup mode writes this file alone, per
charter §4; full `pending.md` reconciliation is ceremony-only, §1d,
and happens tomorrow). Two items from the ceremony's last pass
(2026-09-28) are worth naming here rather than waiting another day:

1. **PR #60**, the pre-send quality checklist, is still open. It was
   the oldest open PR in the repository at 8 days on 2026-09-28; it is
   now **14 days** open and still waiting only on the owner's merge.
   Nothing further is owed from any seat.
2. **The Polar Merchant-of-Record account (ADR-30)** was due
   2026-09-26 and, as far as this seat's sandbox can see, still has no
   live keys anywhere in the codebase. It is now **8 days overdue**,
   and O1 KR1 needs the $20 spine purchasable end-to-end by 2026-10-13,
   now 9 days out.

## GitHub Projects board

`PROJECTS_TOKEN` is present and reachable this run: the GraphQL query
against `user(login: "alexandrapaiz").projectV2(number: 4)` ("alexandria
scrum") returned its item list cleanly. Not dug into further to keep
this run cheap, per charter §4's "spend few turns on it."

## Linear trial

Not checked this run (no new signal). Still on trial per the 2026-09-19
ruling; no verdict recorded since.

## Dispatched by the PM

None. The queue was empty this run (every dispatchable seat already
holds an open pull request), so nothing was fired.
