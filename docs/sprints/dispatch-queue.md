# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run. Holds at most three proposed dispatches, ordered, and is
allowed to hold none.

## 2026-09-24 (Thursday night standup, owner present)

**No dispatches fired or proposed.** The owner is driving this session
directly: an engineer run (wiring the press's send path to
`site/emails/digest.html`, per tonight's dispatch) and a writer run
(PR #89, "every issue stands alone, promoted to law") are both
`workflow_dispatch` runs in progress as this standup starts. Charter
§5's guardrail is unconditional here: any `workflow_dispatch` inside the
last two hours means synchronous mode, queue instead of fire, and two
are running right now, not two hours ago. `PM_DISPATCH_ENABLED` is
`true`, but that is one of two required conditions, not both.

This run's job was tracking, not proposing. The two owner items above
and tonight's reconciliation (the ADR-32 duplicate resolved, the ExO
chain merged, #69 merged, W39 printed/sent/published, the subscriber
roll updated) are recorded in `docs/sprints/pending.md` instead.

**Run health.** All green since the last PM run (04:25:27Z, success, PR
#88). `gh run list --limit 30` shows no new failure class since then;
nothing unregistered.

## Dispatched by the PM

None this run.
