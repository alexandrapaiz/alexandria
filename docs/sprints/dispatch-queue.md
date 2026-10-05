# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-05 (ceremony reconciliation, refresh at 05:50 UTC)

This PR (#222) reconciles two open PM-seat PRs from earlier tonight,
#217 (which itself already folded in #213's ceremony and #215's
message) and #218 (the merge-authority governance note), rather than
redoing their work from a clean `main` — see each file's own section
below for what carried forward unchanged. This section refreshes the
numbers that moved in the ~2 hours since #217's 03:51 UTC snapshot.
Everything in the sections below this one is #217's and #218's own
text, kept because it is still accurate; nothing in it is restated
here unless it changed.

**Queue gauge, recomputed at 05:49 UTC:**

1. **`main`'s age and check state.** Newest merge to `main`: still PR
   #211 (ADR-40), 04:00:37 UTC, now 1h48m old. Newest `checks` run on
   `main`: still **failure**, 03:36:14 UTC, unchanged — confirmed
   directly against the tree rather than just the run log:
   `skills/agent-containment/SKILL.md` line 11 still reads `claims:
   []`, so the provenance-gate defect #217 named is still live on
   `main` right now, not fixed by anything that has merged since
   (#208-#214 touched ADRs and other skills, not this file). This is
   the same defect, still open, now at least 2h26m since it first
   tripped `checks` (03:23 UTC).
2. **Open pull requests: 11 total** (including this one), **7 opened
   since the last merge**: #216, #217, #218, #219, #220, #221, and
   this PR, #222.
3. **Conversion, trailing 7 days: 85 merged / 94 opened** (≈0.90).
   Still healthy; the 7-day window is rolling past some of the
   09-30 batch-merge's "opened" count, which is why this reads a
   little lower than #217's 0.97 snapshot rather than higher.
4. **Deepest open supersession chain: still 1.** #219 supersedes #209
   (closed) and #220 supersedes #210 (closed) — both point at a
   closed PR, not an open one. No stacked chain is live.

Threshold unchanged: last merge was under 2 hours ago, so this section
stays informational, not the first thing in the description.

**A third PM-seat PR opened after #217 and #218, and also collides on
`pending.md`.** #221 (`alexandria-pm/2026-10-05-message-distill-timeout`,
opened 05:32:53 UTC) triages the chair's distill-timeout question,
substantively unrelated to this ceremony, and was correctly branched
fresh from `main` rather than built on #217 or #218 (its own PR body
makes the same "genuinely does not touch the same work" call this
charter's collision rule asks for). It touches `pending.md` at the
same top anchor this PR does. **Expected merge order:** this PR
(#222) first, since it carries the full ceremony; #221 rebases on top
after, the same order #221's own body already expects.

**Tier B merge check, redone at this snapshot.** All 10 other open
PRs checked against standards/pm.md §10's five conditions: #216,
#217, #218, #221 are PM-seat PRs (excluded by condition 1); #219 has
a **failing** `checks` run (condition 3, see Failures below); #220,
#203, #202, #205 are drafts (condition 2); #60 is not a draft but
`mergeable: CONFLICTING` (condition 5) on top of already being Tier C
(`prompts/daily.md`). **No PR qualifies for a Tier B merge this run.**

**Failures, refreshed.** #217's three classes below still hold. One
addition: **#219** (`engineer/2026-10-05-skill-eval-program`, the
ADR-40 skill-eval program, supersedes #209) has now failed `checks`
**7 times in a row**, 04:44-05:12 UTC, on the same assertions each
time: `tests/test_skill_receipts.py` — `agent-containment: no claim
ids reached the page`, and a second assertion expecting claim `'199'`
in harness-engineering's rendered list and not finding it. This is
the exact defect named above, confirmed still live in the tree, and
the run log shows the same two failing assertions on all 7 attempts —
**real defect, not transient, no rerun.** Per charter §11.7 point 4,
two failures in a row on one seat is already an incident-register
matter and this is seven; this run cannot write
`docs/agents/incidents.md` (outside this run's write scope, confined
to `docs/sprints/` and ledger grooming), so flagging here for the
seat that can: an entry is owed, `agent-containment` and the
provenance test need the engineer's next pass to actually land claim
ids rather than retry the same unchanged content. Not dispatched this
run either, for the same synchronous-mode reason as everything else
below — and dispatching it would need to say "build on #219" by name
per the open-PR hard stop, which is itself only safe to write once a
human is not already mid-session on the same branch.

## 2026-10-05 (Monday ceremony's standup half)

**Synchronous mode is active. No dispatch fired this run.** At 03:41
UTC, seven minutes after this run started, someone dispatched
`research-agent` and `engineer-agent` directly (`workflow_dispatch`),
and a second `pm-agent` `repository_dispatch` run started at 03:49
UTC, concurrent with this one. Charter §5's hard stop ("never dispatch
while the owner is present... if any run was dispatched by anyone in
the last two hours, queue instead") applies cleanly: every seat that
could be dispatched already ran today, several of them twice, inside
the last hour. There is nothing this run could propose that the live
session hasn't already overtaken. Queue is empty by design, not by
oversight.

**Second PM run detected mid-ceremony, and it collides on one file.**
A `pm-agent` run (`repository_dispatch`, started 03:49:26Z) ran
alongside this one and opened PR #215
(`alexandria-pm/2026-10-05-message`), a message-triggered session
declining a staffing-authority claim — different branch, different
topic, not a duplicate ceremony. But its own PR body says "no open PR
collision... nothing on a PM branch before this one," which is wrong:
this run's PR #213 (`pm/sprint-2026-10-05`) was already open, touching
`docs/sprints/pending.md`, four minutes before #215 was created. #215
also touches `pending.md`. Its own-PR check missed an open PR from the
same seat, the exact failure mode incidents 6 and 14 already named.
**Expected merge order, named per the ledger-collision rule:** merge
this PR (#213) first — it is the full ceremony reconciliation — then
#215's addition applies on top; if #215 merges first instead, this
branch will need `main` merged into it before it can land clean. Not
filed as a fresh incident this run (no seat's work was lost, both PRs
are still open and reviewable), but worth the ExO's attention if it
happens a third time with real content loss.

## The queue gauge (four numbers, charter §4)

Snapshot at 03:51 UTC; the live session above means these will be
stale within minutes, which is the nature of writing a ceremony during
an active owner session, not a tracking failure.

1. **`main`'s age and check state.** Newest merge to `main`: PR #214,
   03:50:53 UTC (about 1 minute old at snapshot time). Newest `checks`
   run on `main`: **failure**, 03:36:14 UTC, unchanged since — the
   provenance/vocabulary defect named in pending.md. `main` has not
   gone green since 03:23 UTC today, across at least 6 pushes.
2. **Open pull requests: 9 total, 0 opened since the last merge**
   (PR #214 was a docs-only chair PR that landed a minute before this
   snapshot and nothing has opened since).
3. **Conversion, trailing 7 days: 83 merged / 86 opened** (≈0.97).
   Healthy, and dramatically better than the 2026-09-28 retro's 12/63:
   the backlog crisis that retro named is over, per pending.md.
4. **Deepest open supersession chain: 1.** Every open PR's own
   "supersedes" claim points at a PR that is already closed or merged,
   not at another currently-open one (checked #209 against #204,
   which is closed-unmerged, not open). No stacked chain is live right
   now.

**Threshold check:** nothing merged for 48+ hours would make this
section the first thing in the PR description. That is not the case
today (last merge was ~1 minute before this snapshot) — the gauge is
informational this run, not a blocker-of-the-day finding.

## The cap ratio

Not computed this run. `gh run list` reports workflow conclusions, not
per-run turn counts, and pulling `num_turns` per run requires
downloading each run's full log — tried on one sample this run and it
was not a cheap grep. Saying so rather than guessing: no run in the
last 24h shows a cap-related truncation or failure in `gh run list`
(the only failures are the `checks` CI gate, not an agent seat hitting
`--max-turns`), so there is no urgent signal, but the 70%-of-cap ratio
itself was not measured today. The ceilings in force, for reference:
engineer 200, exo 200, frontend 600, market/okr 160, finance 120,
sales 160, research 180, pm 300, writer 150, security 250, skill 180.

## Failures, last 24h (charter §11.7)

`gh run list --status failure` over the trailing 24 hours returns 20
runs, all `checks` (the CI gate), none an agent seat's own workflow.
Grouped by cause:

1. **Real defect, already being fixed, no rerun.** 6 `push`-to-`main`
   failures (03:23-03:36 UTC) are the panel-provenance/vocabulary
   defect named above and in pending.md. Handoff: engineer, already
   building the fix in the open PRs of today's live session (#204 →
   superseded by #209). No incident filed this run — the entry
   belongs with whichever PR actually closes it, to avoid a duplicate
   record once that PR lands.
2. **Tripwire false alarms, resolved by merge, no rerun.** `pull_request`
   failures on `chair/press-duplicate-title`, `chair/distill-on-kimi`,
   `alexandria-security/2026-10-05-window`, `alexandria-writer/2026-10-05-window`,
   `alexandria-skill/2026-10-05-window`, and `engineer/2026-10-05-sections-conformance`
   (13 runs total) all belong to PRs that subsequently merged clean
   (#199, #206, #196, #198, #200, #190). Per the table's own
   definition, a tripwire whose PR exists gets a note, not a rerun.
3. **Already-registered repeat, no new action.** The `writer/2026-10-04`
   failures (2 runs, 18:52-19:16 UTC yesterday) are the same
   cost/backoff-assertion-and-jq-JSON-bug class the 2026-10-04 standup
   already named at 8 occurrences across three days; PR #189 (today's
   window run) carries that chain forward and has since merged.

No reruns issued this run: every failure either already has a
superseding PR in flight or has already resolved by merge. Nothing
here is older than 24 hours or a workflow the owner paused.

## Run health

**Fleet.** Zero agent-seat workflow failures since the last PM run
(#197, 03:24 UTC) — every failure above is the shared `checks` CI gate,
not a seat's own run. `deploy-main` ran twice today, both green.

**Delivery health** (docs/agents/delivery-health.md's closing rule:
green on what evidence, and did anything reach a reader).

- **The press.** Today's send window is 09:00 UTC, about 5 hours from
  this snapshot — not due yet, so "no new row since yesterday" is
  expected, not a finding. No `DATABASE_URL`/`NEON_RO_URL` in this
  sandbox to query `digests` directly either way (same gap every
  standup has named since 2026-09-27). Carried into sprint-2026-10-05
  item 4 as a post-window verification task.
- **The site.** `https://libraryofalexandria.dev/` returns 200.
  `/library`'s newest issue is `2026-W39`, matching expectation (next
  issue not due until this morning's 09:00 UTC send). `deploy-main`'s
  two green runs today are both after the newest `main` commits that
  touch `site/`, so the deploy is current with the content it has.
- **The MCP server.** `https://ap4509--alexandria-mcp-serve.modal.run/`
  returns HTTP 404 on a bare unauthenticated GET — up, correctly
  refusing rather than serving, same as every prior standup.

## Pending items past their date

Full reconciliation is in docs/sprints/pending.md this run (ceremony,
not standup-only). Three worth repeating here per charter §4's
pending-items line:

1. **PR #60**, the pre-send quality checklist — **15 days** open,
   Tier C (touches `prompts/daily.md`), only the owner can merge it.
2. **The Polar Merchant-of-Record account (ADR-30)** — **9 days**
   overdue.
3. **The `sql_query` scope gap** (can read `subscribers`/`users`) —
   open 4 days, needs the owner's call on the fix shape.

## GitHub Projects board

`PROJECTS_TOKEN` present, not queried this run — the company board
(board.libraryofalexandria.dev) is the state of record per charter
§1e2/pm.md §14 and was read instead (below).

## The company board

Read via `BOARD_API_URL` this run. Its current sprint is still named
"Launch-ready newsletter," dated 2026-09-21 to 2026-09-27 — three
cycles stale. Not remapped this run: the live synchronous session is
actively changing which PRs exist under this ceremony's own feet, and
a board remap done now would be wrong within the hour. Flagged for the
next standup to create the Sprint 2026-10-05 iteration and move this
week's shipped items, once the live session settles.

## Linear trial

Not checked this run (no new signal since 2026-09-19's "still on, no
verdict" note).

## Dispatched by the PM

None. Synchronous mode (above) is the reason; see that section for the
evidence.
