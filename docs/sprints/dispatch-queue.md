# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run. Holds at most three proposed dispatches, ordered, and is
allowed to hold none.

## 2026-09-24 (ceremony-lite sync, third pass this session)

**Refreshed again (04:30 UTC), ceremony-lite run, not the standup that
wrote the rest of this file.** One thing changed since the 04:13 UTC
refresh: PR #87 opened (exo, second run today). No PR merged, no run
failed, no new `workflow_dispatch` since then — still well inside
synchronous mode. Ask 2 below (the incident-numbering ruling) now has
a second dimension: a duplicate "## ADR-32" heading in
`docs/decisions.md`, the same failure class PR #57 already fixed once
for ADR-30. Full detail in `docs/sprints/pending.md`'s new top
section. Nothing else below changed; re-verified rather than
rewritten.

**No dispatches fired this pass either, same reasoning as the standup
below**, reinforced: a second human-triggered run (exo, PR #87,
04:22:40Z) landed since the original queue was written, which is
further evidence of synchronous mode, not less.

## 2026-09-24 (standup, dispatch-triggered)

**Refreshed later the same session (04:13 UTC).** One item below moved:
PR #75 merged at 03:37:34Z (ADR-32, the Kimi K2 press fix), so ask 3 is
now a narrower deployment question, not a merge-status one. No new run
started since this queue was first written and no other PR opened,
merged, or closed (`gh run list` and `gh pr list --state open` both
checked again and unchanged otherwise). The synchronous-mode gate still
holds: the newest `workflow_dispatch` (engineer, 03:17:07Z) is under two
hours old.

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

1. A merge order across the 28 open pull requests (oldest is PR #31,
   about 5 days old; PR #86 and #87 opened after this queue was first
   written), several of them chained supersessions of each other. Full
   breakdown in `docs/sprints/pending.md`.
2. A ruling on the incident register's numbering: PR #83 (skill,
   2026-09-24) reports that incident numbers 23 through 29 are each
   claimed by at least one open branch right now. Now joined by a
   second, related numbering collision: two "## ADR-32" headers in
   `docs/decisions.md` (this pass's finding, `docs/sprints/pending.md`
   has the detail).
3. Confirmation on the Modal press cron (incident 24): the fix merged
   (PR #75, ADR-32) at 03:37:34Z, but deployment is still unconfirmed.
   Deployment has historically been a manual `modal deploy` step, not
   something CI does on merge, so the question is now narrower: has
   anyone run it, or does something already deploy on merge to main?

## Dispatched by the PM

None this run.
