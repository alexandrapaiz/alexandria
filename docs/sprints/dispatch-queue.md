# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-09, six-hour pass (~06:25 UTC)

**Run mode.** Today is Friday, not Monday, so this is the six-hour pass
alone: no sprint opened, no retro rewritten, no ledger groomed. The
sprint file gets a dated progress line instead, same as every pass this
week.

**Continuing this seat's own running branch.** This pass builds on the
branch opened at 00:29 UTC today, which itself closed two earlier pull
requests in the same day's chain (the message-session branch and the
standup that merged into it). Nothing from either is lost: both are
already closed with a pointer forward. Counting from the first pull
request in today's chain to this one: **seven deep. This seat is
blocked on merges**, the same shape the charter asks to be named in bold
rather than quietly worked around.

## The most important finding this run: one pull request now closes four things at once, and it is still one Tier C file short

The engineer's newest pull request (opened about three hours ago, the
tenth in its own chain) is green and clean against `main`. Past the red
test suite, the real subscriber row, and the real unsubscribe endpoint
its predecessors already carried, this one also found and fixed a real
bug in the delivery-health reader: the deploy check compared production
against whichever branch happened to run it rather than against the
trunk, so a seat's own recent commit could make a four-day-old
production deploy read as fresh. It ships the regression tests for that
fix too. The only thing between this and `main` is the same single
condition that has held every pull request in this chain for four days:
two files under `prompts/` that this seat's own authority does not
reach.

## Delivery health, read fresh this pass

```
ok       press     2026-W40 is written, by kimi-k2.6
ok       pipeline  ingesting and distilling within 2 days
FAILING  deploy    the deployed code is not this code: triage is 4.1 days behind.
                    not mailed: these rows came from the public API, which cannot
                    write the once-a-day cooldown
ok       site      2 issue(s) published, newest 2026-W40
ok       archive   the record and the archive both end at 2026-W40
ok       mcp       up, and refusing unauthenticated calls
```

Every agent-seat workflow is green (below). The one red surface is the
same gap a prior pass already named and filed: deploy drift on triage,
grown by about half a day since the last check, consistent with nobody
having deployed in between rather than a new problem. Nobody is paged
for it; it stays here rather than in "pending items past their date"
because it is not owner-only (no spend, no secret), and the standing
rule in this file is to answer "green on what evidence" rather than
report the fleet and stop.

## The queue gauge (four numbers, charter §4)

```
gh pr list --state all --limit 200 --json number,state,createdAt,mergedAt
gh run list --workflow=checks.yml --branch=main --limit 1 --json conclusion,createdAt
```

1. **`main`'s age and check state.** Newest merge: the frontend's weekly
   visual review, 2026-10-08 06:28:40 UTC, about **24 hours old** at
   this snapshot. The exact command the charter names still returns a
   stale `checks.yml` run from 2026-10-05 (failure), because that
   workflow triggers on specific paths in a pull request, not on a push
   to `main`, so no run has targeted `main` directly since that date
   regardless of what has merged since. The delivery-health reading
   above is the real evidence of `main`'s health, not this number.
2. **Open pull requests: 7 total, 3 opened since the last merge** (the
   engineer's newest, this seat's own, and the writer's newest; the
   other four predate the last merge).
3. **Conversion, trailing 7 days: 59 merged / 77 opened** (≈0.77).
4. **Deepest open supersession chain: 10** — the engineer's main-fix
   line, unbroken since 2026-10-05 (ten pull requests, the open one
   named above). This seat's own chain is 7, named above, and is not
   counted here since it is this seat's own backlog file, not the
   org's main-line work.

**Threshold check.** 24 hours since the last merge is well under the
48-hour line. Org-wide throughput is not blocked; chain depth and the
deploy drift above are the two things actually wrong today.

## The cap ratio

Measured against the four seat runs completed since the last standup
(2026-10-08 ~17:49 UTC), `num_turns` read from each run's own log,
caps read fresh from `.github/workflows/agent-*.yml`:

| Seat | Run (UTC) | `num_turns` | Cap | Ratio |
|---|---|---|---|---|
| engineer | 2026-10-08 17:49 | 135 | 200 | 67% |
| writer | 2026-10-08 20:53 | 106 | 150 | **71%** |
| engineer | 2026-10-09 02:54 | 111 | 200 | 56% |
| pm | 2026-10-08 17:49 | 45 | 300 | 15% |

**Writer is still the one over 70%.** No run has hit its cap. Same seat
flagged last pass, same ratio within a point. Not proposing a number;
reporting the ratio and naming the seat, per rule 5.

## Failures, last six hours

Zero. `gh run list --status failure --created ">=2026-10-08T18:00:00Z"`
(wider than the six-hour window) returns nothing, and no agent-seat
workflow has failed since the last pass. Nothing to triage, rerun, or
file.

## Tier B merge check (`docs/standards/pm.md` §10, §21)

All six other open pull requests checked against the six conditions.
**Zero qualify for a Tier B merge this run**, the same finding as every
pass since 2026-10-06.

- **The engineer's newest** (supersedes the ninth link in its own
  chain) — draft: no. Checks: green. Merge state: clean, no conflicts.
  **Disqualified on condition 4 only**: the diff carries
  `prompts/distill.md` and `prompts/distill-practices.md`, Tier C. The
  single best candidate in the queue, unchanged in kind from the last
  four passes, better in substance (see above).
- **The writer's newest** (supersedes its own prior link) —
  **disqualified on conditions 4 and 5**: `prompts/digest.md` in the
  diff, and conflicting against `main`.
- **The skill seat's agent-containment retrofit** (open since
  2026-10-06, unchanged) — **disqualified on conditions 3, 4 and 5**:
  checks still fail the same stale-base assertion, `prompts/
  skill-extract.md` in the diff, and conflicting.
- **The finance draft** — **disqualified on condition 2** (draft), also
  conflicting. The owner's own in-progress work.
- **The OKR draft** — **disqualified on condition 2** (draft) despite
  being otherwise clean and mergeable. The chair's own in-progress work.
- **The pre-send quality checklist**, 18 days old — **disqualified on
  conditions 3, 4 and 5**: a failed deploy check, `prompts/daily.md` in
  the diff, and conflicting. Oldest open pull request in the repository,
  named again below.

## Run health

**Fleet.** No agent-seat workflow has failed since the last standup.
Four seat runs completed in the window (engineer twice, writer once, this
seat's own last standup), all successful. All other Actions runs in the
window are the shared `checks` gate on pull requests, all green.

**Delivery health.** See the finding above, which leads this description
rather than sitting in a list.

## Pending items past their date

1. **The pre-send quality checklist** — now **18 days** open, Tier C,
   conflicting, waiting only on the owner. Unchanged since the last
   several passes.
2. **The Polar Merchant-of-Record account** — overdue since 2026-09-26,
   now **13 days**, no live keys visible in the tree.
3. **The engineer's newest pull request** — green, clean, Tier C
   (two prompt files); would otherwise be ready; waits only on the
   owner, and closes the most of anything in the queue if it lands.
4. **The dispatch permission gap**, four occurrences across fifteen
   days, already escalated to the ExO by name — not owner-only, but
   still unanswered.

## The board

Read via the board's message feed this run, before `gh pr list`, per
`docs/standards/pm.md` §15. The feed returned for "addressed to pm" is
not scoped to this company, so this run read every entry back to the
last pass and kept the ones naming alexandria. None is new, and none is
an unanswered ask or handoff addressed to this seat. The traffic between
sibling companies' own PM seats (merges, renewed asks, six-hour-pass
notes) is informational, not addressed here, and needs no reply from
this seat.

## Linear trial

Not checked this run (no new signal since it was last noted).

## Proposed, not fired

Nothing this pass. The engineer, the writer, and the skill seat each
already hold an open pull request of their own, which is the hard stop
on dispatching any of them, and none of their own further work would
clear the one condition actually blocking them — only the owner's merge
does. The remaining dispatchable seats (research, market, security,
frontend, okr, sales) have nothing evidenced this window beyond their
normal cadence, so no entry meets the trigger bar this run.

## Dispatched by the PM

None this run.
