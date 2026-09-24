# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run. Holds at most three proposed dispatches, ordered, and is
allowed to hold none.

## 2026-09-24 (standup, dispatch-triggered)

**No dispatches fired this run, and none proposed to fire later today.**
`PM_DISPATCH_ENABLED` is reported `true` for this run, but charter §5 and
company standard §11.4 both make a second condition absolute: "Never
dispatch while the owner is present... any `workflow_dispatch` by a
human in the last two hours means synchronous mode; queue instead." That
condition is met several times over here, not marginally: nine seats
(engineer, exo, research, security, market, writer, frontend, skill,
finance) were all started by `workflow_dispatch` within the same two
minutes this morning (`gh run list`, 2026-09-24T02:56-02:58Z), and by the
time this PR was opened, three more (#83 skill, plus the finance and
security runs already completed) had landed pull requests. The owner is
plainly driving this session directly. A PM-fired dispatch on top of
that is exactly the "two runs of one dispatch racing on one branch"
failure mode the guardrail exists to prevent, so this run queues
nothing and fires nothing.

What would otherwise be dispatch-shaped asks are written up instead as
recommendations in this run's PR description and in
`docs/sprints/pending.md`, because they need a decision or a merge, not
a workflow run:

1. A merge order across the 26 open pull requests (oldest is PR #31,
   about 5 days old), several of them chained supersessions of each
   other.
2. A ruling on the incident register's numbering: PR #83 (skill,
   2026-09-24) reports that incident numbers 23 through 29 are each
   claimed by at least one open branch right now.
3. Confirmation on the Modal press cron (incident 24): the fix is built
   (engineer PR #75) but not yet deployed, and deployment has
   historically been a manual `modal deploy` step, not something CI
   does on merge.

## Dispatched by the PM

None this run.
