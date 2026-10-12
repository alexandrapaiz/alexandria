# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-11, standup (~16:45 UTC), completing a stalled six-hour pass

**Run mode.** Sunday, not Monday, so this is the standup alone (charter
§0/§4). The current sprint is still `docs/sprints/sprint-2026-10-05.md`;
Monday's ceremony (retro, grooming, new sprint) is 2026-10-12, not today.

**This seat's own open pull request.** `alexandria-pm/2026-10-11-message`
(#269) was already open when this run started: a six-hour pass, ten
hours earlier, that pushed one commit saying triage was starting and got
no further. Continued on that exact branch rather than opening a sixth
pull request in this seat's own recent chain — merged `main` into it
first (it was a full day stale, missing PR #268), then did both the
six-hour pass's own triage and this standup's reading on the same
branch. No new branch, no new supersession link.

**The headline is delivery health, not the queue gauge.** The distill
stage has not produced a claim in four days. Full account in
`docs/sprints/pending.md`'s matching entry; the short form: `claims_newest`
and `distilled_newest` on the live receipt (`GET /api/delivery`) are both
frozen at `2026-10-07T15:15:25Z` while `papers_newest` is today, the
backlog (`distill_pending`) is 2132 and climbing roughly 20 a day, and
this is already `urgent` in `docs/ideas.md` (2026-10-11 entry, which
narrows the cause to the environment rather than the code: the same
images have run since 2026-10-05 and produced claims exactly once, on
10-07). An engineer run is already in flight against it (PR #270,
started 16:37 UTC) — not touched here, per the standing rule against
editing a live run's own branch. What that run cannot reach is Modal's
own logs, which is the owner's access, named in full under "owed to
you" below.

**Run health.** Zero failures in the last 24 hours
(`gh run list --status failure --created ">=2026-10-10T16:39Z"` returns
nothing). Two runs in progress as this is written (this pm-agent run,
and engineer-agent's PR #270) are not yet measurable.

**Delivery health, the other half** (green on what evidence, and did
anything reach a reader).

- **The press.** Newest issue 2026-W40, printed 2026-10-05. Next due
  2026-10-12 (Monday), not yet in its window — `pending`, not `FAILING`,
  per the guardrail that only holds a week to account once its own
  deadline has passed.
- **The pipeline.** Ingest, triage and interpret all current (newest
  rows today or yesterday). Distill is the one stalled stage, above.
- **The site.** Reachable, 200, serving 2026-W40 at `/library`.
- **The MCP server.** **Could not be checked this run** — no record in
  this sandbox of its deployed `modal.run` endpoint. Named as unchecked
  rather than silently skipped.

## The queue gauge (four numbers, charter §4)

1. **`main`'s age and check state.** Last merge: 2026-10-11 06:25:33 UTC
   (PR #268), about 10h20m ago at this snapshot. The newest `checks.yml`
   run *on* `main` is still 2026-10-10 16:19:15 UTC (`success`) — stale
   rather than red: at least two merges since then, including #268,
   fell entirely outside the workflow's `paths` filter, the same gap
   `docs/agents/incidents.md` already tracks as item 17
   (`INC-2026-10-10-a-whole-pull-request-fired-no-merge-check`, third
   occurrence recorded yesterday by the engineer seat itself against
   this exact PR). A staged, verified fix exists
   (`git mv .github/workflows-pending/checks.yml
   .github/workflows/checks.yml`) and no seat may apply it.
2. **Open pull requests: 6** (#270, #269, #267, #205, #203, #60), **1
   opened since the last merge** (#270, 16:39:17 UTC — a live run's own
   pull request, not a backlog).
3. **Conversion, trailing 7 days: 67 merged / 83 opened** (≈0.81).
   Healthy.
4. **Deepest open supersession chain: #267**, depth 2 (supersedes #260,
   which is already closed). Not a blocker at that depth.

**Threshold check.** ~10h20m since the last merge, well under the 48h
line. Not the headline — delivery health is, above.

## The cap ratio

Two runs completed since the last standup pass (2026-10-10 ~16:10 UTC)
crossed 70% of their own `--max-turns`:

- **engineer-agent** (`38066706694`, 2026-10-10 16:12 UTC) —
  **158/200 (79%)**.
- **writer-agent** (`38080446679`, 2026-10-10 19:36 UTC) —
  **139/150 (92.7%)**, the second time in three days this seat has come
  within single digits of its cap, after actually hitting 151/150 on
  2026-10-09 (`INC-2026-10-09-the-writer-hit-the-cap-its-own-raise-queued-five-days-earlier`).
  `docs/agents/pending-workflow-changes.md` item 14 (raise to 300,
  writer included) is confirmed still unapplied — `agent-writer.yml`
  still reads `--max-turns 150` — seven days after it was queued and
  two near-misses later.

The third completed run in the window, engineer-agent
(`38102988830`, 2026-10-11 01:47 UTC), was 135/200 (67.5%), under the
line.

Ceilings, for reference (`grep -HoE '\-\-max-turns [0-9]+'
.github/workflows/agent-*.yml`): engineer 200, exo 200, frontend 600,
market/okr 160, finance 120, sales 160, research 180, pm 300, writer
150, security 250, skill 180.

## Failures, last 24h (charter §11.7)

`gh run list --status failure --created ">=2026-10-10T16:39Z"` returns
nothing. Nothing to triage or rerun this pass.

## Tier B merge check (`docs/standards/pm.md` §10/§21)

Every pull request open at the start of this run, checked fresh:

- **#270** (engineer) — a live run's own pull request, in flight as
  this standup writes. Not evaluated, not touched.
- **#269** (this seat's own) — excluded by Tier B's own first rule (a
  PM's own pull request waits for another merger).
- **#267** (writer, "editorial run 31") — clean, green, not a draft.
  **Disqualified anyway**: its diff touches `prompts/digest.md`, a
  Tier C path (charters). This seat cannot merge it under Tier B
  regardless of how clean it is. Waits on the owner.
- **#205** (finance, September close) — disqualified on conditions 2
  and 5 (draft, conflicting). Finance is dormant; nobody to dispatch to
  finish it.
- **#203** (okr, fifth cadence check-in) — disqualified on condition 2
  (draft), despite being substantively complete (1223 lines). Not this
  seat's call to mark another seat's work ready.
- **#60** (engineer, the pre-send quality checklist, 21 days old) —
  disqualified on conditions 4 and 5 (Tier C path `prompts/daily.md`,
  conflicting), same as every prior pass.

**No merges performed this run.** Nothing qualified.

## Pending items past their date

1. **The distill stall's next step is the owner's**: `modal app logs
   alexandria-distill`. 4 days stalled, growing ~20 items a day, cause
   narrowed to the environment (the Moonshot account's balance, tier,
   or secret), not the code.
2. **Merge PR #60**, the pre-send quality checklist — **21 days** open,
   Tier C, conflicting, waiting only on the owner.
3. **The Polar Merchant-of-Record account (ADR-30)** — overdue since
   2026-09-26 (now 15 days), and O1 KR1's $20 spine needs it
   purchasable by 2026-10-13, **2 days away**.
4. Also still open, named rather than repeated in full: the `sql_query`
   scope decision (10 days, fix shape is the owner's to pick); the
   writer's cap raise (above, now a second near-miss); the staged
   `checks.yml` replacement (above, one command, HQ's side of
   `.github/workflows` to apply).

## The board

Read via `BOARD_API_URL` before `gh pr list`, per `docs/standards/pm.md`
§15. Nothing addressed to `pm`/`alexandria` since 2026-10-10 18:27 UTC
(a `done` note from HQ's pm confirming this seat's own prior standup
pull request was already merged by someone else — needed no further
answer). The other entries in the shared feed are broadcast notes from
other companies' PM seats (`to_seat`/`to_company` both null); none name
alexandria. No unanswered ask or handoff.

## Linear trial

Not checked this run; no new signal since the last pass noted it was
still on.

## Dispatched by the PM

None fired this run. Checked every dispatchable seat against
`docs/standards/pm.md` §11.3's criteria table:

- **engineer** and **writer** are both hard-stopped by their own open
  pull requests (#270, #267) — neither instruction here tells either
  seat to build on that branch, so the stop holds.
- **finance** is dormant; never a dispatch target.
- **research, market, skill, security, frontend, okr** — each has no
  open pull request, but also no observed trigger this run: no failed
  run in the last 24h, no ADR or ruling since 2026-10-05 naming any of
  them with no run following, and no sprint item due this week that one
  of them owns and has not touched. Nothing invented to fill the queue.

`PM_DISPATCH_ENABLED` is confirmed `true` (read directly from this job's
own environment). The org is not in synchronous mode (no
`workflow_dispatch` event in the last two hours; the newest on record is
2026-10-05). Neither the switch nor the two-hour guard is holding
anything back — there is simply nothing to propose today, beyond the
in-flight engineer run already working the one real finding.
