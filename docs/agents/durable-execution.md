# Temporal, and what durable execution would actually have bought us

**Enforced at:** nothing, deliberately. This is a decision note and not
a register. It holds no rule anyone can violate, so gating it would be
ceremony. The §3d sweep lists it with that verdict so no future run
invents an enforcement step for it.

Written by the ExO agent on 2026-09-24, answering a question the owner
asked directly: should scheduling move to Temporal instead of GitHub
cron. This is a recommendation and not a decision. Temporal Cloud is a
paid service and this seat holds no authority over money, so the call is
hers.

## The answer, in one paragraph

Temporal would have fixed the half of our failures that were about
visibility and retries, and it would not have fixed the half that
actually broke the press. Durable execution gives you a workflow that
survives a crashed worker, retries with real backoff, and a history you
can open and see. Against incident 24 that means the Modal run which
left no log for 2026-09-21 would have been an unambiguous entry saying
started-and-failed or never-scheduled, instead of three days of an empty
inbox and a question the CLI could not answer. That is a genuine gain
and it is the gain worth wanting. What it would not have touched is
everything downstream of the scheduler. A 404 from a model that no
longer exists is a permanent error, and durable execution retries
permanent errors faithfully until it gives up, which is slower failure
rather than no failure. A saturated free-tier key is the same: Temporal
would retry into the same 8,000 tokens per minute ceiling, and the
ceiling is the constraint. The actual fixes were an availability check,
an ordered fallback list, and an email when nothing printed, and all
three are ordinary code that runs anywhere, which is why PR #75 could
ship them on the existing stack this week for nothing. So my
recommendation is post-launch, alongside the router evaluation in
docs/agents/model-routing.md, because that is the point where we have
several long multi-step jobs whose partial progress is expensive to lose
and where a $0 ceiling is no longer the binding constraint. Adopting it
now would add a service, a worker to host, and a second scheduling
system to reason about, in exchange for better visibility into a
pipeline whose real problem is that its provider keeps withdrawing
models underneath it.

## The detail behind that, for when the question comes back

**What durable execution is, mechanically.** A Temporal workflow is code
whose execution state is persisted at every step by the server. If the
worker process dies mid-run, the workflow resumes from its last
completed step on another worker rather than starting over. Retries,
timeouts, and backoff are declared per activity instead of hand-written.
Every run has an inspectable history. The things it is genuinely good at
are long-running multi-step jobs, partial failure with expensive
progress, and anything where "did this run, and how far did it get" has
to be answerable months later.

**Scored against our actual failures.** Five press and seat failures in
the last week.

| Failure | Temporal helps | Why |
| --- | --- | --- |
| Modal cron left no log for 2026-09-21 | **yes** | workflow history distinguishes never-started from started-and-died, which is the exact question the Modal CLI could not answer |
| `groq/compound` returns 404 | no | permanent error, retries cannot bring a withdrawn model back |
| 429 rate limit on a shared free-tier key | no | the org-level ceiling is the constraint, retrying re-enters it |
| 413 request too large | no | arithmetic, caught by the budget guard before the call |
| PM run died at turn 30 on Kimi | no | Claude Code runs inside Actions, a different execution model entirely |

One yes out of five, and the one yes is real. Note what the table
implies: our failures have been about the correctness of what we call,
not the durability of the calling. That ratio is what makes this a
post-launch decision rather than a now decision. It would change if we
started losing expensive partial work, and the corpus-expansion spike is
the first thing on the horizon that could do that.

**What it costs.** Temporal Cloud is usage-priced with a monthly
minimum, so it is not $0, and the org's standing constraint is $0.
Self-hosting is free in licence and not free in attention: a server, a
database, and a worker process we would own. Either way it is a second
scheduling system living beside GitHub Actions for the twelve seats,
which stay where they are because claude-code-action is an Actions
action. So the realistic scope is the pipeline only, which means the org
would run two schedulers and a reader would have to know which jobs live
where.

**The cheaper thing that captures most of the value now.** Guardrail 4
in docs/agents/delivery-health.md, which is the PM reading the newest
row in `digests` every morning. Most of what Temporal would have bought
us on 2026-09-21 is the knowledge that nothing shipped. An outside
observer checking the artifact gets that for the cost of one query, and
it works against any scheduler, including ones whose history we cannot
read. It does not give us resumable partial progress, which is the part
that genuinely needs a durable engine, and we do not need that part yet.

**Where it belongs on the roadmap.** Post-launch runtime work, evaluated
together with the router in docs/agents/model-routing.md. Those two
belong together because they are the same decision from two directions:
the router decides what to call, durable execution decides how calls
survive. Both become worth their overhead at the same moment, which is
when the pipeline runs long multi-step jobs across several providers
with real money behind them. The trigger to revisit, stated concretely
so a future run can test it rather than re-argue it: the first time we
lose more than an hour of completed work to a mid-run failure, or the
first time a pipeline job legitimately needs to run longer than an
Actions job may.

An entry belongs in docs/ideas.md so it is groomed rather than
remembered, and this seat does not write the ledger's statuses.
