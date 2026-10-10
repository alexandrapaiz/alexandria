# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-10, standup (~16:10 UTC)

**Run mode.** Saturday, not Monday, so this is the standup alone
(charter §0/§4). The current ceremony is still
`docs/sprints/sprint-2026-10-05.md`; Monday's ceremony (retro, grooming,
new sprint) is 2026-10-12, not today.

**This seat's own open pull request.** `alexandria-pm/2026-10-10-message-pass2`
(#264) was already open when this run started, a draft left mid-triage
by a six-hour-pass session about 3h45m earlier. Rather than stack a
sixth pull request onto an already five-deep same-day chain, this run
checked out that exact branch and finished the pass on it; this is the
pull request this standup ships as. No new branch, no new supersession
link.

**The headline is two merges, not a dispatch.** Both open PRs that were
not drafts and were not conflicting checked out clean against Tier B
(`docs/standards/pm.md` §10/§21):

1. **#263** (engineer, "the stalled stage names its own cause") — no
   checks at all on its branch, and its own body explains why and files
   it as `INC-2026-10-10-a-whole-pull-request-fired-no-merge-check`:
   `checks.yml`'s `paths` filter (`prompts/digest.md`, `prompts/daily.md`,
   `pipeline/**`) does not cover this diff (`site/`, `tools/`, `tests/`),
   confirmed directly against the workflow file rather than taken on the
   PR's word. Verified locally in place of CI before merging:
   `tests/test_delivery_receipt.py` (24 passed, 1 skipped) and
   `tests/delivery.test.mjs` (13/13 passed). Merged 16:14:43 UTC.
2. **#237** (skill, the agent-containment ADR-38 retrofit, open since
   2026-10-06) — clean, green, not a draft, but `CONFLICTING` against
   `main`. The only conflict was a docs-only append collision at the end
   of `docs/agents/incidents.md` and `docs/ideas.md` (both sides added
   new entries at the same anchor — the exact shape this seat's own
   `INC-2026-10-09-same-anchor-conflict-on-a-rebase-and-a-resolver-that-staged-its-own-markers`
   already named), which §10 condition 5 lets the PM resolve directly.
   Kept `main`'s appended entries first, then the branch's own appended
   entries, verified `python3 tools/check_registers.py` after (0
   blocking, the same 5 pre-existing warnings #263 already named), and
   waited for the branch's own `checks` run to go green post-push before
   merging. Merged 16:19:12 UTC. `main`'s own next `checks.yml` run came
   back green afterward too, confirmed directly rather than assumed.

**Two abandoned ship-first placeholders, closed rather than left to
rot.** Per the queue-moving duty in `docs/standards/pm.md` §18 line 4
(every open PR is merged, closed with a reason, or named as waiting on
the owner):

- **#258** (engineer, "the PM's note answered") — held nothing but its
  placeholder file for 23 hours, body still said "more to follow," none
  followed, and no live run is building on the branch. Closed.
- **#255** (market, weekly ceremony) — held nothing but a 5-line stub
  ("draft in progress") for 23 hours, none of the four promised
  ceremonies landed, no live run is building on the branch. Closed.

Both closes are reversible and said so in the closing comment.

**Left open, each named rather than acted on:**

- **#260** (writer, editorial run 30) — not a placeholder, checks green,
  clean, but still a draft; the writer's own call when it's ready, not
  this seat's to force ready.
- **#203** (okr, fifth cadence check-in, 5 days old) — a real, 1223-line
  check-in, still a draft. Reads as substantively complete, not a stub,
  but marking another seat's own work ready is outside what a merge
  mechanic should decide; named as waiting on either the owner's answer
  to its own two questions or the okr seat calling `gh pr ready` itself.
- **#205** (finance, September close, 5 days old, conflicting) — real
  partial content (107 lines) but the close's own core numbers were
  never filled in ("filling in below as the run proceeds," then
  nothing). Under the 7-day idle-close threshold, finance is dormant
  (no seat to dispatch to finish it), so this is named as waiting rather
  than closed today.
- **#60** (engineer, the pre-send quality checklist) — unchanged, 20
  days open, Tier C (`prompts/daily.md`), conflicting. Still the oldest
  open PR in the repository, still waiting only on the owner.
- **#265** (engineer, "the receipt has no distill row at all") — opened
  by a live, in-progress, schedule-triggered engineer-agent run during
  this standup (not a human dispatch: `gh run list --event
  workflow_dispatch` shows nothing newer than 2026-10-05, so the org is
  not in synchronous mode). Its own body says it supersedes #263, which
  this run merged minutes before #265 opened; the live session will find
  that for itself when it finishes. Not this seat's to touch mid-run.

## The queue gauge (four numbers, charter §4)

1. **`main`'s age and check state.** Newest merge: this run's own #237,
   2026-10-10 16:19:12 UTC, about 10 minutes old at this snapshot. The
   next `checks.yml` run on `main` after that merge came back `success`
   (confirmed by polling `gh run list --branch main --workflow=checks.yml`
   directly, not read stale).
2. **Open pull requests: 6 total** (#60, #203, #205, #260, #264, #265),
   **1 opened since the last merge** (#265, opened 16:15:08, four minutes
   before #237 merged at 16:19:12 — so technically before this run's own
   last merge, but after #263's 16:14:43 merge; either reading leaves the
   count at 0-1, not a backlog).
3. **Conversion, trailing 7 days: 64 merged / 82 opened** (≈0.78).
   Healthy, and this run added two more merges to the numerator without
   adding to the denominator.
4. **Deepest open supersession chain: this seat's own**, continuing
   count from the 2026-10-09 pass4 entry (fifth stacked pass since then,
   itself fourth in its own prior chain) — unchanged in kind by
   continuing the same branch rather than opening a sixth link. #265's
   chain (supersedes #263) is depth one once #263's merge is accounted
   for, since #263 itself was not a superseding PR.

**Threshold check.** 10 minutes since the last merge, far under the
48-hour line. Not the headline.

## The cap ratio

Only one agent-seat run completed between this run and the last standup
pass (2026-10-09 ~20:55 UTC): engineer-agent at 2026-10-10T02:14:53Z,
**117/200 turns (58.5%)** — under the 70% line, nothing to report. The
writer's cap hit (151/150, the prior pass's own finding) is unchanged
and already filed; not re-reported as new. The two runs in progress as
this is written (this pm-agent run, and engineer-agent's #265) have not
completed and cannot be measured yet.

Ceilings, for reference (`grep -HoE '\-\-max-turns [0-9]+'
.github/workflows/agent-*.yml`): engineer 200, exo 200, frontend 600,
market/okr 160, finance 120, sales 160, research 180, pm 300, writer
150, security 250, skill 180.

## Failures, last 24h (charter §11.7)

`gh run list --status failure --created ">=2026-10-09T16:13Z"` returns
exactly one: the writer-agent cap hit at 2026-10-09T20:22:56Z, already
triaged in full by the prior pass on this branch
(`INC-2026-10-09-the-writer-hit-the-cap-its-own-raise-queued-five-days-earlier`),
real defect, no rerun (the same input would hit the same cap), handed to
the writer which already produced the follow-up push (checks green on
`writer/2026-10-09` since 2026-10-09T20:40:36Z). Nothing new to do here
this pass.

## Tier B merge check (`docs/standards/pm.md` §10/§21)

Every pull request open at the start of this run, checked:

- **#263** (engineer) — qualified, merged. Account above.
- **#237** (skill) — qualified after a docs-only conflict resolution,
  merged. Account above.
- **#258** (engineer) — disqualified (draft) and abandoned; closed
  rather than left open.
- **#255** (market) — disqualified (draft) and abandoned; closed rather
  than left open.
- **#260** (writer) — disqualified on condition 2 (draft).
- **#205** (finance) — disqualified on conditions 2 and 5 (draft,
  conflicting).
- **#203** (okr) — disqualified on condition 2 (draft).
- **#60** (engineer, 20 days old) — disqualified on conditions 4 and 5
  (Tier C path `prompts/daily.md`, conflicting).
- **#265** (engineer) — opened mid-run by a live session; not evaluated,
  per the rule against touching a run still in flight.

## Run health

**Fleet.** One failure in the last 24h (the writer's cap hit, already
triaged above). Two schedule-triggered runs are in progress as this is
written (this pm-agent run, and an engineer-agent run that has already
opened #265): expected, not a finding. Every other run since the last
standup pass was green.

**Delivery health** (green on what evidence, and did anything reach a
reader).

- **The press.** Not re-checked this run beyond what #263 already
  measured: `claims_newest` frozen at 2026-10-07T15:15:25Z while
  `papers_newest` is current — the live engineer run (#265) is actively
  investigating this right now, which is the reason not to duplicate the
  check mid-investigation. The last confirmed send (`/library` listing
  `2026-W40`) is unchanged and not stale by the weekly-issue measure.
- **The site.** `deploy-main` ran successfully at 2026-10-10T16:14:46Z,
  right after #263 merged, confirming the deploy pipeline is still firing
  on every `main` push.
- **The MCP server.** Not probed fresh this run; no signal since the
  last standup that it changed state.

## Pending items past their date

1. **The `sql_query` scope decision** — confirmed still unfixed this
   run by reading `mcp/server.py` directly: no table allowlist, only a
   single-statement/SELECT-only check. Open since 2026-10-01, now 9
   days, needs the owner's call on the fix shape.
2. **PR #60**, the pre-send quality checklist — **20 days** open, Tier
   C, conflicting, waiting only on the owner.
3. **The Polar Merchant-of-Record account (ADR-30)** — overdue since
   2026-09-26, not checked fresh for live keys this run (no new signal
   since the last pass that found none).

## The board

Read via `BOARD_API_URL` before `gh pr list`, per `docs/standards/pm.md`
§15. Exactly one message addressed to `alexandria`/`pm` since the last
pass: a `done` note from the writer (2026-10-09T17:48:12Z, "rebased onto
the new main and re-pushed"), already acted on before this run started.
No unanswered ask or handoff.

**Found, not fixed this run: the board is materially stale.** Its sprint
record still reads "The press runs itself," `starts_on 2026-09-21,
ends_on 2026-09-27` — three weeks behind `docs/sprints/sprint-2026-10-05.md`,
the file this repo's PM ceremony actually maintains. Its 20 items are
almost entirely 2026-09-27/09-30-dated owner and Linear-sourced cards;
none mentions the claims-stall work, the waitlist/unsubscribe work
(both already shipped, confirmed by #263's own survey), or either merge
this run made. Full reconciliation (closing shipped items to Done,
opening cards for current work, fixing the sprint record) is a ceremony-
sized lift, not a standup one; flagging it here so Monday's ceremony
inherits it as a named item rather than a surprise. Posted a short note
to the board this run instead of attempting the full resync (see commit
history / board Messages).

## Linear trial

Not checked this run; no new signal since the last pass noted it was
still on.

## Dispatched by the PM

None fired this run. No candidate in `docs/standards/pm.md` §11.3's
criteria table had an observed trigger: the one live defect (the claims
stall) already has a run in flight against it (#265, schedule-triggered,
not a dispatch); engineer's own open PR (#265) is a hard stop on
dispatching that seat regardless; no new ADR or ruling since 2026-10-05
names a seat with no run following; no draft PR has failing CI; finance
and okr's stale drafts are incompleteness, not failure, and neither fits
the criteria table's rows. `PM_DISPATCH_ENABLED` is confirmed `true`
(read directly from this job's own environment), and the org is not in
synchronous mode (no `workflow_dispatch` in the last two hours), so
nothing here is being held back by the switch or by the two-hour guard —
there is simply nothing to propose today.
