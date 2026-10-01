# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-01 (Thursday standup)

**Queue is empty.** Every dispatchable seat already holds an open pull
request from its last run, which is a hard stop under charter §5 with no
exception for actually firing (unlike the queue rule in §4, §5's version
has none): engineer (#170), research (#162), market (#163), writer
(#169), frontend (#168), skill (#159, #152, #151), security (#157), okr
(#171). That is all eight dispatchable seats. There is nothing left to
propose and nothing to fire today.

## Run health

**Fleet health.** No non-success among the twelve scheduled agent
workflows since the last PM run (PR #167, 2026-09-30T16:50 UTC):
`okr-agent` ran today at 16:56 UTC and succeeded; `engineer-agent` and
this `pm-agent` run are both `in_progress` as of this run, started in the
same minute, both `schedule`-triggered rather than `workflow_dispatch`,
so this is the daily cron overlap, not a synchronous-owner-present
condition. No `workflow_dispatch` run appears anywhere in the last two
hours either.

Two things that look like failures are already accounted for, not new:
- **`checks.yml` on `main` has been red for five straight runs**
  (2026-09-30T01:43Z through 02:37Z, all `failure`), already diagnosed as
  `INC-2026-09-30-two-checks-steps-red-on-main-for-days`. The fix is
  sitting in engineer's own open PR #170, which says merging it also
  turns `main` green again. A repeat by that PR's own count; nothing new
  to register.
- **PR #169's own CI check failed** ("digest request fits the model's
  budget"). That PR's own title is about exactly this kind of budget/gate
  defect, so this reads as the writer seat's self-diagnosis in progress,
  not an unexplained new failure.

**Delivery health.**
- **The press.** Still `unknown`: no database credential in this
  sandbox (guardrail 5, unresolved since 2026-09-27). Proxy:
  `https://libraryofalexandria.dev/library` lists `2026-W39` as newest,
  consistent with no issue being due until Monday 2026-10-05. **New this
  run:** engineer's open PR #170 builds exactly the credential-free fix
  this gap has been waiting for, a public `GET /api/delivery` endpoint
  on the site that answers the press/pipeline/deploy questions with no
  secret and no Neon role. It is not merged yet, so today's check still
  falls back to the library-page proxy. Worth prioritizing this merge:
  once it lands, guardrail 4/5 stops being `unknown` by construction
  instead of by someone remembering to check again.
- **The site.** `https://libraryofalexandria.dev/` returns 200.
- **The MCP server.** `https://ap4509--alexandria-mcp-serve.modal.run/`
  returns 404 on a bare unauthenticated GET, which is the expected,
  healthy shape (refusing rather than serving), same as every prior
  check since incident 21.

## Pending items past their date

Not reconciled this run (standup mode writes this file alone; full
`pending.md` reconciliation is ceremony-only, charter §1d). Two items
worth naming here rather than waiting for Monday:
- **The Polar Merchant-of-Record account (ADR-30)** — due 2026-09-26,
  now **5 days overdue**. Still the single launch-critical blocker: no
  live keys anywhere in the codebase, and checkout wiring cannot start
  without it. 12 days to the 2026-10-13 launch date.
- **PR #60** (pre-send quality checklist) — now **11 days open**, still
  the oldest open pull request in the repository.

## New finding this run: a duplicate ADR number

`docs/decisions.md` has two separate headers both titled exactly
`## ADR-38`: "Skills close the loop with their consumers" (2026-09-29)
and "The skill quality bar. A skill is its deltas, proven on tasks the
bare model fails" (accepted 2026-09-30). This is the same shape as the
ADR-32 duplicate the owner resolved on 2026-09-24, and that precedent's
own rule applies again: don't renumber silently, since every citing file
would need a matching fix. `docs/ideas.md` already cites "ADR-38" at
least once, so a silent renumber would break that reference too. This is
a `docs/decisions.md` edit, Tier B, outside this seat's writable
surface, same as the 2026-09-24 case — flagging for your one-line call
(which entry becomes ADR-39) and for the ExO to apply with a grep-fix of
every citing file in the same pull request. Not registered in
`docs/agents/incidents.md` by this seat for the same reason: that file
is also outside this seat's writable surface.

## GitHub Projects board

`PROJECTS_TOKEN` reachable this run via direct GraphQL
(`user(login: "alexandrapaiz").projectV2(number: 4)`, id
`PVT_kwHOBqunQs4Bj3sN`). Read the item list; nothing addressed to `pm`
specifically. Not dug into further, per charter §4's "spend few turns on
it."

## Linear trial

Not checked this run, no new signal. Still on trial per the 2026-09-19
ruling; no verdict recorded since.

## Dispatched by the PM

None. Every candidate seat is excluded by the open-PR hard stop above.
