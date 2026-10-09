# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-09, message run (~20:55 UTC): the writer's cap hit, triaged

**Run mode.** Friday, not Monday, so this stays the standup shape
(charter §0/§4), triggered mid-day by a message reporting the
writer-agent's run as failed rather than by the daily cron. This update
builds on the ~17:30 UTC standup pass already on this branch's history
(below) and adds the one new, time-sensitive finding this run was asked
to triage.

**The headline.** The writer-agent's scheduled run (`37986599276`,
20:22-20:45 UTC) died at turn 151 against its own 150-turn cap — hard
starvation, confirmed from the action's own result block
(`"is_error": true, "num_turns": 151`) and log
(`Reached maximum number of turns (150)`). Ship-first meant six real
files survived in its draft PR, #260 (`writer/2026-10-09`); whatever it
was still composing on top of that push did not. The cap was not a
surprise: `docs/agents/pending-workflow-changes.md` item 14, queued
2026-10-04, had already measured the writer at 91% of this exact cap
and proposed raising it to 300, and the raise was never applied. Full
account in `INC-2026-10-09-the-writer-hit-the-cap-its-own-raise-queued-five-days-earlier`
(`docs/agents/incidents.md`) and in `docs/sprints/pending.md`.

**Not fired, either entry below.** `gh variable list` returned
`HTTP 403: Resource not accessible by personal access token` when this
run tried to confirm `PM_DISPATCH_ENABLED`, the same gap prior passes
hit. Per charter §5, when the switch cannot be confirmed from inside
the run, treat it as not active. Both commands are for the owner or a
chair to run directly.

### 1. writer — build on PR #260 to finish the increment the cap-out dropped

**Trigger.** PR #260 (`writer/2026-10-09`) is open as a draft, holding
the six-file push from before the run hit its turn cap
(`docs/ideas.md`, `docs/voice/ban-list.md`, `docs/voice/canon.md`,
`docs/voice/check_voice.py`, `docs/voice/reviews/2026-10-09.md`,
`prompts/digest.md`). The run's own PR description says its contents
were meant to be "the graded review of the newest issue, the
prompts/digest.md diff, and any ban-list additions" — the No-ship
tripwire shows `docs/ideas.md`, `docs/voice/ban-list.md` and
`docs/voice/reviews/2026-10-09.md` still dirty and unpushed at
teardown, so some part of that is missing from what actually landed.

**Cost of skipping it today.** PR #260 sits as a draft that looks
complete (six files, a real diff) but is not, and nobody who was not
inside that run's own sandbox can tell which part of the grading or the
ban-list work it still owed. Left alone, it either merges short of its
own stated scope or sits open indefinitely waiting for a human to guess
the gap.

**Hard-stop check.** Writer's only open PR is #260 itself; the
instruction below tells it to build on that exact branch, which is the
charter's named exception to "never dispatch a seat with an open PR."
This would be the first PM-fired dispatch of the day if fired (none
logged below), well inside the three-a-day, one-per-seat ceiling, and
`gh run list --event workflow_dispatch` shows nothing in the last two
hours, so the org is not in synchronous mode. Not fired anyway, per the
403 above.

```bash
gh workflow run agent-writer.yml \
  -f owner_instructions='Your last run (37986599276) hit the 150-turn
cap mid-edit and died before it could push its last increment. PR #260
(writer/2026-10-09) already holds what it managed to push: docs/ideas.md,
docs/voice/ban-list.md, docs/voice/canon.md, docs/voice/check_voice.py,
docs/voice/reviews/2026-10-09.md, prompts/digest.md. Build on that exact
branch. The No-ship tripwire from the capped-out run shows docs/ideas.md,
docs/voice/ban-list.md and docs/voice/reviews/2026-10-09.md were still
dirty and unpushed when it died, so re-check all three against what the
PR description promised (the graded review of the newest issue, the
digest.md diff, and any ban-list additions) and finish whatever is
short. Push early and often this time so a second cap-out does not lose
the same work twice.'
```

### 2. engineer — the claims pipeline stall, carried from the ~17:30 UTC pass, status unconfirmed

**Trigger.** Unchanged from this branch's earlier section below:
`tools/delivery_health.py` read the pipeline surface as FAILING,
"claims has not moved in 2 days," as of ~17:30 UTC today. Not
re-verified this run — this pass's scope was the writer's failure, and
`tools/delivery_health.py` needs a database credential this run did not
spend time re-confirming access to. Engineer has run twice more since
(PR #256, merged, and PR #258, open, "the PM's note answered"), and
#258's own body replies to a different PM note (about PR #253's merge
status), not to this one, so treat this as **not confirmed resolved**
rather than stale.

**Cost of skipping it today.** Unchanged from the prior section: a
third day of no new claims means Monday's crons run against a corpus
that stopped growing, with the cause still undiagnosed.

**Hard-stop check.** Engineer's open PR is #258; this instruction does
not ask it to build on that branch, so firing this would need #258
closed or merged first, or a rephrasing that targets #258's branch
directly. Not fired regardless, per the 403 above — queued as-is for
whoever applies it by hand to adjust if #258 is still open at that
point.

```bash
gh workflow run agent-engineer.yml \
  -f owner_instructions='Delivery health was FAILING on the pipeline surface as of ~17:30 UTC today: tools/delivery_health.py reported claims has not moved in 2 days while papers keeps current, meaning triage/distill is not keeping up with ingest. Re-run the check first to confirm this is still true before investigating further. Read pipeline_facts()/judge_pipeline() in tools/delivery_health.py for the exact query (max(fetched_at) on papers vs max(created_at) on claims), find why distill is not advancing the claims table, and fix it.'
```

## Dispatched by the PM

None fired this run. Both entries above are proposed only; `PM_DISPATCH_ENABLED` could not be confirmed (`HTTP 403` reading repo variables), and charter §5 treats an unconfirmed switch as inactive.

---

## 2026-10-09, standup (~17:30 UTC)

**Run mode.** Friday, not Monday, so this is the standup alone (charter
§0/§4). No ceremony today; the current ceremony is
`docs/sprints/sprint-2026-10-05.md`, still open.

**The headline is a merge, not a dispatch.** PR #253 (engineer, the
tenth pull request in its chain) had been blocked since 2026-10-05 on
`prompts/distill.md` and `prompts/distill-practices.md`, which every PM
pass since then — including this morning's six-hour pass — read as
Tier C under `docs/standards/pm.md` §10's shorthand ("Charters
(`prompts/`)"). §10's own header and §21 (owner, 2026-10-05, vendored
here as PR #230 on 2026-10-06) narrow the real carve-out to a change in
a seat's own authority, spend, a new account, or a secret. Neither file
is a charter; both are the distillation pipeline's content prompts. So
this run merged PR #253 itself. The next push-triggered `checks` run on
`main` came back green — the first since 2026-10-05T03:36:14Z. Filed as
`INC-2026-10-09-tier-c-carve-out-misread-for-four-days` in this PR,
because the same misreading recurred across at least five passes.

**Knock-on, handled without a dispatch.** PR #251 (writer) and PR #237
(skill) are now conflicting against the new `main`. Both are a rebase,
not a review problem, so each owning seat got a board handoff (§10 item
5) instead of a workflow dispatch. Neither seat's last run gets a
second instruction today.

Checked all eight open pull requests against Tier B/§21 (one merged
above, three conflicting and now handed off, one is a draft less than
a day old, three are the owner's own drafts or 19-day-old PR #60
already named in prior passes as needing her reconciliation with the
writer's quality-bar work, not a seat's rebase). Checked
`docs/sprints/sprint-2026-10-05.md`: items 1 through 4, the whole of
the engineer's current backlog, now read as shipped by the same pull
request just merged (main green, a real `subscribers` insert, a real
unsubscribe endpoint, both deployed and answering on the live site).
Nothing in `docs/decisions.md` or `docs/allhands/` since 2026-10-05
names a seat with no run following. No seat run failed in the last 24
hours — as of ~17:30 UTC; the writer's cap-out above happened later the
same day.

### engineer — the claims pipeline has stalled for two days while ingest keeps current

**Trigger.** `tools/delivery_health.py`, run fresh after today's merge:
the pipeline surface reports FAILING, "claims has not moved in 2 days,"
while the papers surface is current. Ingest is working; distillation is
not keeping up with it, which `judge_pipeline()`'s own docstring calls
the gap that feeds every other surface.

**Cost of skipping it today.** A third day of no new claims means
Monday's triage, interpret and weekly crons all run against a corpus
that stopped growing two days ago, and whatever broke stays unknown
for another day.

**Dispatch.** Attempted to fire, not queued by choice: this run's token
returned `HTTP 403: Resource not accessible by integration` on
`agent-engineer.yml`'s dispatch endpoint, the same no-`actions:write`
gap prior passes have hit. The command is below for the owner or a
chair to run directly.

```bash
gh workflow run agent-engineer.yml \
  -f owner_instructions='Delivery health is FAILING on the pipeline surface: tools/delivery_health.py reports claims has not moved in 2 days while papers keeps current, meaning triage/distill is not keeping up with ingest. Read pipeline_facts()/judge_pipeline() in tools/delivery_health.py for the exact query (max(fetched_at) on papers vs max(created_at) on claims), find why distill is not advancing the claims table (a Modal cron that stopped firing, a budget/ceiling gate, a rate limit, or an exception swallowed somewhere), and fix it. Main is green again as of the pull request this PM seat merged this run (the deploy-drift guard fix, PR 253), so start from a clean main.'
```

## Dispatched by the PM (17:30 UTC pass)

None fired this run. One attempted and blocked by a 403 (above); logged
rather than silently dropped.
