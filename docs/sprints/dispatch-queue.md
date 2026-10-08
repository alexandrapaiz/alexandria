# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-08, standup (~17:50 UTC)

**Run mode.** Today is Thursday, not Monday, so this is the standup alone
(charter §0: the date decides when no dispatch carries other instructions,
and the invocation for this run explicitly named "standup" too, so both
signals agree). No sprint opened, no retro rewritten, no ledger groomed.

**A concurrent writer on these same files.** PR #248
(`alexandria-pm/2026-10-08-message-second-pass`, author `alexandrapaiz`, the
host-window six-hour-pass cadence of this same seat, not this run) is open
and draft, and its diff touches `docs/sprints/dispatch-queue.md`,
`docs/sprints/pending.md`, `docs/sprints/sprint-2026-10-05.md` and
`docs/agents/incidents.md` — the same four files this run writes. It builds
on #247, itself built on #243 (a chain of 3, by its own account "my own
chain hits five" counting back further). **Expected merge order: this PR
first** (it is finished and ready; #248 is still a running draft saying
"filling in as this pass continues"). Whoever merges #248 next should rebase
it past this one rather than the reverse, since replacing
`dispatch-queue.md` in full is exactly the collision shape incident 6 named.
Not touching #248 itself — it is a different cadence's in-flight work, not
this run's own prior PR.

## The most important finding this run: delivery health, not fleet health, carries the one red line

`python3 -I tools/delivery_health.py`, the guardrail-4 reader, run fresh this
standup:

```
ok       press     2026-W40 is written, by kimi-k2.6
ok       pipeline  ingesting and distilling within 2 days
FAILING  deploy    the deployed code is not this code: triage is 3.6 days behind.
                    not mailed: these rows came from the public API, which cannot
                    write the once-a-day cooldown
ok       site      2 issue(s) published, newest 2026-W40
ok       archive   the record and the archive both end at 2026-W40
ok       mcp       up, and refusing unauthenticated calls
```

Every agent-seat workflow is green (below). The product is not fully green:
**the live deploy is running code roughly 3.6 days older than what is on
`main`**, per the drift guard in `tools/delivery_health.py`. This is exactly
the shape `docs/agents/delivery-health.md`'s 2026-10-04 addition describes —
a change-triggered deploy whose last fire date does not match the newest
change it was supposed to carry — and the guard's own alarm cannot mail
itself because this run reads it through the public API rather than a
database connection, so it has no cooldown-writing credential. **Nobody is
being paged for this.** It is not an owner-only blocker (no spend, no
secret), so it does not belong in "pending items past their date" below; it
belongs here, named, because the standing rule in this file is to answer
"green on what evidence" rather than report the fleet and stop.

## The queue gauge (four numbers, charter §4)

```
gh pr list --state all --limit 200 --json number,state,createdAt,mergedAt
gh run list --workflow=checks.yml --branch=main --limit 1 --json conclusion,createdAt
```

1. **`main`'s age and check state.** Newest merge: PR #244, 2026-10-08
   06:28:41 UTC, about **11.5 hours old** at this snapshot. The exact
   command the charter names returns a `checks.yml` run against `main` from
   2026-10-05 03:36:14 UTC (`failure`) — stale attribution, because
   `checks.yml`'s trigger is `pull_request` on specific `pipeline/**` and
   `prompts/{digest,daily}.md` paths only (confirmed by reading the
   workflow file this run), not `push` to `main`, so no run has targeted
   `main` directly since that date regardless of what has merged since.
   The real evidence of `main`'s health this run is the delivery-health
   finding above, not this stale number.
2. **Open pull requests: 7 total, 1 opened since the last merge** (#248,
   opened 12:29 UTC today; the other six — #246, #245, #237, #205, #203,
   #60 — all predate PR #244's 06:28 UTC merge).
3. **Conversion, trailing 7 days: 59 merged / 75 opened** (≈0.79).
4. **Deepest open supersession chain: 8** — the engineer's main-fix line
   (#204 → #209 → #219 → #226 → #233 → #240 → #242 → #246, the last link
   open now as #246, "supersedes #242," whose own body said "seventh in a
   chain" before this one extended it to eight). This seat's own chain
   (#239 → #241 → #243 → #247 → #248) is 5, named in #248's own title, and
   is not this run's to carry further since #248 is a different cadence's
   PR.

**Threshold check.** 11.5 hours since the last merge is well under the
48-hour line. Org-wide throughput is not blocked; main-chain depth and the
deploy drift above are the two things actually wrong today.

## The cap ratio

Measured against the five most recently completed seat runs since the last
standup (2026-10-07 ~17:45 UTC), `num_turns` pulled from each run's log tail,
caps read fresh from `.github/workflows/agent-*.yml`:

| Seat | Run | `num_turns` | Cap | Ratio |
|---|---|---|---|---|
| writer | 37685229081 (2026-10-07 20:51) | 108 | 150 | **72%** |
| engineer | 37718849374 (2026-10-08 02:38) | 104 | 200 | 52% |
| frontend | 37667164895 (2026-10-07 18:28) | 188 | 600 | 31% |
| pm | 37661479016 (2026-10-07 17:45, last standup) | 52 | 300 | 17% |

**Writer is the one over 70%: 108/150.** No run has hit its cap, so this is
not yet a tripwire, but it is the seat to watch — per `docs/agents/
turn-caps.md`'s own history, a seat that runs daily and drifts upward
between measurement triggers is the exact failure mode that under-capped the
writer seat twice before (80→200 on 2026-09-21, and again implicitly since).
Not proposing a number; reporting the ratio and naming the seat, per rule 5.

## Failures, last 24h (charter §11.7)

`gh run list --status failure --created ">=...-24 hours"` returns 4 runs, all
the shared `checks` gate on `writer/2026-10-07` (PR #245), none an
agent-seat's own run:

1. **Stale base, no rerun warranted.** All 4
   (37685533800, 37687005926, 37687775814, 37688259693, 20:54–21:16 UTC
   2026-10-07) fail the same job, "digest request fits the model's budget."
   `main` already carries the fix for exactly this test — commits `7718cf5`
   ("The press cost check carries its tokenizer's confidence") and `b8ec4b0`
   ("break-fix: the two tests main's CI has been failing on") — and PR #245
   was cut before either landed. Rerunning without a rebase would fail
   identically. This is the trigger for the writer dispatch below, not a
   rerun.

No agent-seat workflow (engineer-agent, writer-agent, pm-agent, etc.) failed
in this window; both writer-agent and engineer-agent's own runs in this
period completed successfully (they produced the now-stale-based PRs, they
did not fail).

## Tier B merge check (`docs/standards/pm.md` §10)

All six other open pull requests checked against the six conditions. **Zero
qualify for a Tier B merge this run** — the common disqualifier is new since
the last pass: three of the live, non-draft PRs are blocked on Tier C paths,
not on review.

- **#246** (engineer, "the press guardrail… supersedes #242") — draft: no.
  Checks: green. **Disqualified on conditions 4 and 5**: `mergeable:
  CONFLICTING`, and the diff includes `prompts/distill.md` and
  `prompts/distill-practices.md` — Tier C. Waits for the owner regardless of
  the conflict.
- **#245** (writer, "two grades cleared three links…") — **disqualified on
  conditions 3, 4 and 5**: checks failing (above), diff includes
  `prompts/digest.md` — Tier C — and `CONFLICTING`. Dispatched below instead
  of merged.
- **#237** (skill, "agent-containment retrofit…") — **disqualified on
  conditions 3, 4 and 5**: checks failing (same budget test, same stale-base
  cause), diff includes `prompts/skill-extract.md` — Tier C — and
  `CONFLICTING`. Dispatched below instead of merged.
- **#205** (finance) — **disqualified on conditions 2 and 5**: draft, and
  `mergeable: CONFLICTING`. The owner's own in-progress work.
- **#203** (okr) — **disqualified on condition 2**: draft, despite being
  otherwise clean and mergeable (`MERGEABLE`/`CLEAN`). The owner's own
  in-progress work.
- **#60** (engineer, 18 days old) — **disqualified on conditions 4 and 5**:
  touches a Tier C prompt and is `CONFLICTING`. Oldest open PR in the repo;
  named again below.

## Run health

**Fleet.** No agent-seat workflow failed in the last 24 hours; the only
failures are the shared `checks` gate on a stale-based branch (above). One
`engineer-agent` run and this `pm-agent` run are both `schedule`-triggered
and in progress as this is written, started within 41 seconds of each other
(17:49:17 and 17:49:58 UTC) — not a dispatch collision, both are independent
cron firings, confirmed via `gh run list --json event` showing `schedule` on
both.

**Delivery health.** See the finding above — this is the one surface that is
not green, and it leads this description rather than sitting in a list.

## Pending items past their date

1. **PR #60**, the pre-send quality checklist — now **18 days** open, Tier
   C, conflicting, waiting only on the owner. Unchanged since the last
   several passes.
2. **The Polar Merchant-of-Record account (ADR-30)** — overdue since
   2026-09-26, no live keys visible in the tree as of this run.
3. **PR #246**, the press-guardrail fix — Tier C (`prompts/distill.md`,
   `prompts/distill-practices.md`), green and would otherwise be ready; waits
   only on the owner.
4. **The dispatch-403 permission gap** — four occurrences in fifteen days,
   now `INC-2026-10-08-dispatch-403-fourth-occurrence`, escalated to the ExO
   by name in that entry. Not owner-only, but unanswered across four PM
   runs.

## The board

Read via `BOARD_API_URL` this run, before `gh pr list`, per `docs/standards/
pm.md` §15. The inbox query (`to_seat=pm&to_company=alexandria`) returns 47
messages, but `to_company` does not appear to filter server-side — the same
gap a prior pass already flagged for the ExO. Of the 47, none is actually
addressed to `alexandria`'s `pm` by another seat asking something unanswered;
they are broadcast `note`s from other companies' PM six-hour passes (`Ursa`,
`epitome`, `alexandra-systems`) and `done`/`ask` traffic between those other
companies' seats. **No unanswered ask or handoff addressed to this seat this
pass.** The board item for the press-resilience cost/backoff defect (created
2026-09-30, `c69113d9`) can move: `main` carries the fix now (commits
`7718cf5`, `b8ec4b0`), the remaining work is the three stale-based open PRs
named above, not a fresh defect — noting this here rather than writing to the
board, since this run's token has no `BOARD_RUNTIME_TOKEN` write path
confirmed and the read-only query above is what succeeded.

## Linear trial

Not checked this run (no new signal since 2026-09-19's "still on, no
verdict" note).

## Proposed, not fired: this session's token cannot dispatch (`INC-2026-10-08-dispatch-403-fourth-occurrence`)

Both entries below have cleared every hard stop in charter §5 / `docs/
standards/pm.md` §11.4: `PM_DISPATCH_ENABLED` is `true`, this section is
ACTIVE, no `workflow_dispatch` fired in the prior two hours (the org is not
in synchronous mode), zero PM dispatches today (well under the ceiling), one
per seat, and neither seat has a run in progress. The first was attempted
for real and 403'd exactly as the three prior occurrences did; the second is
queued unfired rather than attempted a second time against the same
confirmed wall.

### 1. writer — build on the open branch for PR #245

**Trigger.** PR #245 (`writer/2026-10-07`) has failed `checks` 4 times in
the last 24 hours on "digest request fits the model's budget" and is
`CONFLICTING` against `main`. `main` already carries the fix for that exact
test (commits `7718cf5`, `b8ec4b0`); #245 was cut before they landed.

**Cost of skipping it today.** The prose-grading work on #245 stays
unmergeable behind a defect that already has a fix elsewhere, and every day
it waits the conflict against `main` gets harder to resolve by hand.

```bash
gh workflow run agent-writer.yml \
  -f owner_instructions='Build on the open branch for PR #245
(writer/2026-10-07). Its checks have failed 4 times in the last 24h on
"digest request fits the model'"'"'s budget" and the PR is CONFLICTING
against main. Main already carries the fix for that exact test (commits
7718cf5 "The press cost check carries its tokenizer'"'"'s confidence" and
b8ec4b0 "break-fix: the two tests main'"'"'s CI has been failing on"); PR
#245 predates both. Rebase or merge main into the branch, resolve the
conflict, confirm checks pass, then continue the grading work already on
the branch.'
```

**Attempted, not fired.**

```
could not create workflow dispatch event: HTTP 403: Resource not
accessible by integration
(https://api.github.com/repos/alexandrapaiz/alexandria/actions/workflows/361826898/dispatches)
```

Copy the command above and run it directly, or confirm this workflow's
`actions: write` permission actually resolves inside a run (the standing
question in `INC-2026-10-08-dispatch-403-fourth-occurrence`).

### 2. skill — build on the open branch for PR #237

**Trigger.** PR #237 (`skill/2026-10-06-agent-containment-retrofit`) fails
the same "digest request fits the model's budget" check and is
`CONFLICTING` against `main`, for the identical reason as #245: it predates
commits `7718cf5` and `b8ec4b0`.

**Cost of skipping it today.** The containment retrofit (449 lines to 100,
by its own title) stays unmergeable behind the same already-fixed defect.

**Hard-stop check.** Skill's only open PR is #237 itself; the instruction
below tells it to build on that exact branch. This would be the second PM
dispatch today, one per seat, inside the three-a-day ceiling, spaced after
the writer attempt above.

```bash
gh workflow run agent-skill.yml \
  -f owner_instructions='Build on the open branch for PR #237
(skill/2026-10-06-agent-containment-retrofit). Its checks fail on "digest
request fits the model'"'"'s budget," the same test PR #245 fails, and the
PR is CONFLICTING against main for the same reason: it predates main'"'"'s
fix (commits 7718cf5 and b8ec4b0). Rebase or merge main into the branch,
resolve the conflict, confirm checks pass, then continue the containment
retrofit already on the branch.'
```

**Not fired, per the section above** (the first attempt already confirmed
the 403; not spending a second identical failed call on the same confirmed
wall). Copy the command above and run it directly.
