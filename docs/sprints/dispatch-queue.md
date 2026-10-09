# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

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
hours.

### 1. engineer — the claims pipeline has stalled for two days while ingest keeps current

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

## Dispatched by the PM

None fired this run. One attempted and blocked by a 403 (above); logged
rather than silently dropped.
