# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-09-30, ~03:55 UTC (Wednesday, synchronous — second pass this window)

This is a second standup inside the same synchronous session as
[#150](https://github.com/alexandrapaiz/alexandria/pull/150), opened
about an hour earlier (~02:55 UTC). This run supersedes it: the branch
this file lives on merged #150's branch first (fast-forward, no
conflict), so nothing in that run's diagnosis is lost, only refreshed
against the last hour. Close #150 without merging once this lands.

**What changed in the hour between the two runs.** Eight more pull
requests opened, one from almost every seat this org runs
(#154 frontend, #155 writer, #156 sales, #157 security, #158 engineer,
#159 skill, #160 exo, #161 okr, #162 research, #163 market, #164
finance), each a `window`-triggered run same as this one, not something
this seat fired. The practical effect: the one dispatch candidate #150
found (frontend, blocked only by a 403 in the dispatch API itself) now
has an open PR of its own (#154), so it drops out of today's queue for
an ordinary reason instead of the 403.

## Failures, refreshed against #150's diagnosis

#150 classified the last 24 hours into three causes; nothing new
happened to reclassify, so this section states what moved, not the
whole read again (full detail stays in #150's description, GitHub's
copy of this file at that commit).

1. **Main's own checks were red** (`tests/test_press_resilience.py`
   over ADR-32's cost budget, `tests/test_run_report.py` breaking on an
   unset `GH_TOKEN` polluting `gh`'s JSON output). #150 hand off this to
   engineer. **It is now in flight**: PR #158 ("break-fix on main's red
   checks") is open, built on top of #153, and its own `checks` run
   alternates failure/success in the last ten minutes
   (36665897438 success, 36665565812 through 36665107... failure,
   36665989667 queued as of this writing) — consistent with the fix
   being actively iterated on right now rather than stuck. Nothing to
   hand off again; this is the seat's own open PR doing the job.
2. **The `chair/langfuse-traces` branch (PR #139) still fails
   `pm-agent`/`okr-agent`/`market-agent`/`finance-agent` before any job
   starts.** Same four run IDs as #150 found
   (36659107421/36659106719/36659105929/36659105241,
   all 2026-09-29T02:16 UTC) — no new occurrence since, because nothing
   has pushed to that branch again. Still asked of HQ per the board's
   own note that workflow files are HQ's surface, not this repo's.
3. **`checks` noise inherited from item 1** kept accumulating while the
   fix was in flight — roughly 45 failed `checks` runs in the trailing
   24 hours by direct count (`gh run list --limit 200`, filtered), up
   from #150's ~28, all the same regression, no separate handoff.
   Expect this count to stop climbing once PR #158 merges to main.

No new failure class. Nothing here needs a fresh incident entry; item 1
already reads as a repeat of a diagnosed defect with a fix underway, and
item 2 is an unchanged repeat already handed to HQ.

## Run health

**Fleet.** As of 03:55 UTC: one `checks` run queued
([36665989667+](https://github.com/alexandrapaiz/alexandria/actions/runs/36665989667)
family, on PR #152's branch), and the last fifteen `checks` runs show a
mix of failure and success consistent with item 1 above being fixed
live. No `workflow_dispatch` or `schedule` run is failing right now that
isn't already covered in Failures. All of tonight's dispatches
(`engineer-agent`, `skill-agent`, and the eleven `window`-triggered PRs)
were fired by the owner or the chair, not by this seat — confirmed by
the actor field and by the two-hour rule itself: multiple dispatches
inside the last two hours is what puts this session in synchronous mode
in the first place.

**Delivery.**

- **The press.** Cannot query the `digests` table directly — no
  `NEON_RO_URL`/`DATABASE_URL` credential in this sandbox, the same gap
  delivery-health.md's guardrail 5 already names against this seat's own
  workflow. Proxy: `site/content/issues/` still holds only `2026-W37.md`
  and `2026-W39.md` (newest published 2026-09-24, per #150's and the
  2026-09-28 ceremony's own reading). No new issue file exists as of
  this checkout. Monday 2026-09-28's send — the one sprint item 1 of the
  current sprint exists to diagnose — is still unconfirmed two days
  later: no engineer PR opened today claims to have resolved it, and
  none of today's eleven `window` PR titles name the press. **Flagging
  this as the run's one red delivery finding**: it is not new tonight,
  but it is not fixed either, and it is now two days past the send date
  with no recorded answer.
- **The site.** Reachable: `https://libraryofalexandria.dev/` returns
  200 (probed directly this run).
- **The MCP server.** Could not be checked this run. The prior standup's
  probe used a path this seat could not rediscover (`/mcp` now 404s on
  the main domain, and no `mcp.*` subdomain resolves from this
  sandbox); delivery-health.md's own surface table already marks this
  one "no" for daily watch, so this is a known gap, not a new one.
  Saying so rather than reporting silence, per the file's own rule.

## Dispatch

**No entries.** Every seat charter §5 allows this seat to dispatch —
engineer, research, market, writer, frontend, skill, security, okr —
already holds at least one open pull request as of this run:

| seat | open PR(s) |
| --- | --- |
| engineer | #60, #141, #142, #149, #153, #158 |
| research | #138, #145, #162 |
| market | #163 |
| writer | #155 |
| frontend | #154 |
| skill | #140, #146, #151, #152, #159 |
| security | #157 |
| okr | #161 |

The hard stop ("never dispatch a seat that already has an open pull
request from its last run") excludes all eight without exception. This
is a plain consequence of the window wave documented above, not a gap
in coverage: nothing this run found needs a ninth actor added tonight.

## Pending items past their date

Not reconciled in full this run (standup mode writes this file alone,
per charter §4; full `pending.md` reconciliation is ceremony-only, next
due Monday 2026-10-05). Two items are worth naming rather than waiting
for that date:

- **The Polar Merchant-of-Record account (ADR-30) was due 2026-09-26
  and is now four days overdue.** No live keys appear anywhere in the
  codebase as of this checkout. O1 KR1 needs the $20 spine purchasable
  by 2026-10-13, 13 days out, and checkout wiring cannot start until
  this account exists. Owner-only action, unchanged from the last three
  standups.
- **PR #147** ("PMs own merges and failed-run triage") is still open.
  It is Tier C, the chair named it owner-merge, and it is what would
  authorize this seat to start merging other seats' Tier B pull
  requests. Until it merges, this run (like #150) does the failed-run
  triage duty but merges nothing beyond its own knowledge surface.

`docs/sprints/pending.md` itself was last updated 2026-09-28 (the last
ceremony) and is not stale enough yet to flag on its own — two days old,
next full pass due in five more days.

## GitHub Projects board

Could not be checked this run: `gh project list --owner alexandrapaiz`
returns `403 Resource not accessible by personal access token` in this
sandbox, and `PM_DISPATCH_ENABLED`/board reads that need the same scope
returned the same 403. Unlike the prior standup, which read the board
directly, this run's token does not carry that access. Naming the gap
rather than reporting silence on it, same principle as the MCP probe
above.

## Linear trial

Not checked this run (no new signal surfaced, standup budget). Still on
trial per the 2026-09-19 ruling; last confirmed active 2026-09-28.

## Dispatched by the PM

1. **frontend**, 2026-09-30, ~02:55 UTC (from #150). Attempted, not
   fired. `HTTP 403: Resource not accessible by integration`, the same
   shape as `INC-2026-09-24-dispatch-403` and
   `INC-2026-09-29-dispatch-403-repeat`, a third occurrence. No run URL
   exists because no run was created.
2. **This run (~03:55 UTC): nothing fired or attempted.** No seat
   cleared the hard stop (see Dispatch above), so there was nothing to
   try.
