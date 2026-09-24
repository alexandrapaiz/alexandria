# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run. Holds at most three proposed dispatches, ordered, and is
allowed to hold none.

## 2026-09-24 (standup, dispatch-triggered)

**No dispatches fired this run.** The owner is present and working
synchronously right now (nine seats — engineer, exo, research, security,
market, writer, frontend, skill, finance — were all dispatched within
the same two minutes this morning, per `gh run list`). Charter §5's own
guardrail is explicit: "Never dispatch while the owner is present... a
second dispatcher is how two runs of one dispatch end up racing on one
branch. Queue instead." `PM_DISPATCH_ENABLED` being `true` is necessary
but not sufficient; this run treats the guardrail as binding and queues
rather than fires. See the PM's standup PR for the run-health line and
the pending-tracker catch-up.

Draft, being written now. Full content follows in this same PR.
