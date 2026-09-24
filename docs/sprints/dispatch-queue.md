# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run. Holds at most three proposed dispatches, ordered, and is
allowed to hold none.

## 2026-09-24 (Thursday, second standup this day)

**Context.** The prior standup (PR #91, 04:58 UTC) ran inside the
owner's synchronous session and queued nothing, correctly, since a
`workflow_dispatch` was in progress at that moment. This run starts at
15:47 UTC, ~10h40m after the last `workflow_dispatch` (writer-agent,
05:09:00Z). Charter §5's owner-present gate (any dispatch within the
last two hours) does not apply. `PM_DISPATCH_ENABLED` is `true`.
Dispatch authority is ACTIVE (ADR-033). Both required conditions hold,
so this run fires rather than only proposes. Checked before firing: no
PM-initiated dispatch has fired yet today (every prior dispatch-queue.md
version today logged "None this run"), so the daily ceiling (3/day, 1
per seat) starts at zero.

### 1. market — PR #93 has sat with only its ship-first stub for 10+ hours

**Trigger.** The owner dispatched this run herself last night ("run
while she sleeps") to rank issue 2026-W39 against newsletters builders
actually enjoy and rank alexandria against the $20/month competitive
set, landing both in one brief for the PM. The run's own workflow
entry shows `success` in 4m1s (35958636133, 05:08:31Z), but the branch
`market/2026-09-24-b` carries exactly one commit — the ship-first stub,
05:10:22Z — and the file itself still reads "Status: draft, in
progress... The full brief... land in this same file before the PR
comes out of draft." No further commit has landed since.

**Cost of skipping it today.** The ranking the owner asked for, and
that this seat's own PR promises to hand back to the PM, stays
undelivered. If the run is not resumed, there is no record of whether
it stalled (turn cap, timeout) or was simply never finished, and
tomorrow's standup re-discovers the same stale draft.

**Dispatch.**

```bash
gh workflow run agent-market.yml \
  -f owner_instructions='PR #93 (branch market/2026-09-24-b) is a draft
with only its ship-first stub commit from 05:10 UTC; the promised full
brief never landed. Build on that branch, do not start a new one.
Finish exactly what the PR body already commits to: rank issue 2026-W39
(site/content/issues/2026-W39.md) against newsletters builders actually
enjoy (Interconnects, Ahead of AI, Latent Space, The Batch, Import AI,
TLDR AI, Bens Bites, and comparable others), scored on enjoyability,
density, and whether a reader opens the next one; rank alexandria
against the $20/month competitive set as the live site stands now; land
both ranks plus a one-page priority-ordered decision brief for the PM
in docs/market/briefs/2026-09-24-b.md; then take the PR out of draft.
Note PR #60 (engineer) also touches docs/ideas.md if this run adds
ledger proposals, per this PRs own collision note.'
```

### 2. engineer — PR #60 is the oldest open PR and now conflicts with main

**Trigger.** PR #60 (`engineer/2026-09-20-digest-quality-gate`, sprint
2026-09-21 item 4, the pre-send quality checklist) opened 2026-09-20 and
is still open, the oldest PR in the repo by four days. Its own body
named the deadline as "tomorrow's 15:00 UTC cron" relative to
2026-09-20, so that deadline has already passed at least three times
over. `gh pr view 60 --json mergeable` now reports `CONFLICTING`, a
direct result of the roughly twenty PRs that merged today while this
one sat untouched. The current sprint file's own mid-week status
section still lists item 4 as "built, open, awaiting merge."

**Cost of skipping it today.** The conflict only grows as more work
lands on main, and Monday's retrospective would otherwise have to
report a committed sprint item as neither shipped nor explicitly
dropped, four days after its build finished.

**Dispatch.**

```bash
gh workflow run agent-engineer.yml \
  -f owner_instructions='PR #60 (branch
engineer/2026-09-20-digest-quality-gate, sprint item 4, the pre-send
quality checklist) is four days old, its own stated deadline has
passed, and gh pr view 60 now reports mergeable: CONFLICTING against
main. Rebase that branch onto main and resolve the conflicts; do not
start a new branch or redesign the checklist from scratch. Before
resolving, check whether anything that merged today already covers
part of what this PR does (the email-template send path in PR #90, the
evidence-grade work in PR #72, or anything else now on main) and would
make part of this PR redundant. If the checklist this PR adds is still
needed as designed, land it clean. If it is now partly or fully
redundant, say so plainly in the PR rather than merging duplicate
logic, and state clearly whether you recommend closing PR #60 unmerged
so the owner can act on a stated recommendation rather than a bare
conflict.'
```

Two candidates this run, both evidenced against a specific stalled or
conflicting PR. No third: nothing else found today clears the bar of a
named trigger with a stated cost of skipping (the MCP-server daily-watch
gap in docs/agents/delivery-health.md is real but is sprint-planning
material for Monday's ceremony, not a today-dispatch — it has no PR, no
run, and no date attached to skipping it one more day).

## Run health

**Fleet.** `gh run list --limit 60` shows one non-success since the last
PM run (PR #91, which itself reported all-green as of 04:25:27Z): a
`writer-agent` run cancelled at 05:08:33Z after 1m36s
(35958638663). Read alongside the timeline, this looks like a duplicate
`workflow_dispatch` cancelled in favor of the writer run that started 27
seconds later (35958671490, 05:09:00Z, success, 16m35s) and produced PR
#89/#92's line of work — not a new failure class, and nothing was lost:
the following run completed and shipped. No unregistered failure
pattern found. Two `pm-agent` runs are `in_progress` as this file is
written (this run, and an `engineer-agent` scheduled run that started 31
seconds earlier) — both scheduled, not dispatched, not a synchronous-
session signal.

**Delivery.**
- **The press.** The live site's `/library` page shows 2026-W39 as the
  newest issue, matching `docs/sprints/pending.md`'s note that it
  printed and sent today (2026-09-24, recovery send). Not stale. This
  run had no database credentials available to query the `digests`
  table directly (no `NEON_RO_URL` or equivalent in this workflow's
  env); the site is used as a cross-check instead, per
  docs/agents/delivery-health.md's own rule to read the artifact, not
  the scheduler, wherever a direct check is unavailable.
- **The site.** Live: `https://libraryofalexandria.dev/` returns 200 as
  of 15:49 UTC and serves 2026-W39 as the newest issue, consistent with
  today's deploy.
- **The MCP server.** Could not be checked this run: no public endpoint
  is documented in the repo and no credentials for probing it are
  available in this workflow's environment. This matches
  docs/agents/delivery-health.md's own table, which already marks the
  MCP server as "not watched daily" and names that gap as the next
  thing to close, engineer work for a future sprint rather than
  something this standup can instrument on the spot.

**Board.** `PROJECTS_TOKEN` is available. Project 4 still shows the
2026-09-18 split (43 Backlog, 15 Done, nothing In Progress or In
Review) despite roughly twenty PRs merging since. The board is stale
against real state; a full remap is ceremony-run work (per the
2026-09-18 reorg note in pending.md, which already flagged this as
"Monday's job, not a mid-week mirror's"), not fixed in this standup.

**Pending tracker.** `docs/sprints/pending.md` was last updated inside
last night's session (~05:10 UTC) and is not re-reconciled in this run
per charter §4 ("full reconciliation stays in the ceremony run"). One
line past its date, seat named: **engineer**, PR #60 above — its own
2026-09-20 deadline text ("tomorrow's 15:00 UTC cron") is now three
cron cycles overdue.

## Dispatched by the PM

1. **market**, 2026-09-24, dispatched to finish PR #93 on
   `market/2026-09-24-b`. Instruction in full: see entry 1 above. Run:
   *(URL added after firing)*
2. **engineer**, 2026-09-24, dispatched to rebase/resolve PR #60 on
   `engineer/2026-09-20-digest-quality-gate`. Instruction in full: see
   entry 2 above. Run: *(URL added after firing)*
