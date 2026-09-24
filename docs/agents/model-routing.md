# Model routing — using models intelligently across the org

**Enforced at:** prompts/exo-agent.md, "Check the register before you
ship". Unread between 2026-09-17 and 2026-09-19, which is why the line
exists.

Owner's directive (2026-09-17): route work to open-source models where
they suffice, and design our own routing so the orchestration layer
uses models intelligently. This is ADR-5's right-size rule extended
from the pipeline to the agents. The ExO agent owns tuning this policy;
changes ship through its weekly PR.

## What already runs on open models (the base we build from)

- The entire daily pipeline: triage, distill, interpret on
  gpt-oss-120b via Groq's free tier (ADR-5), embeddings on self-hosted
  Qwen3-0.6B. $0.
- The ADR-13 reviewer panel is designed to run the same way, inside
  the weekly Modal cron on Groq. Judgment steps that are small, stable,
  and verifiable are exactly where open models shine.

So the token spend to optimize is the org: seven Claude Code seats on
the owner's subscription.

## The routing table (current policy)

| Work | Model | Why |
|---|---|---|
| Pipeline judgment (triage, distill, interpret) | gpt-oss-120b (Groq, $0) | proven by bake-off, golden set guards upgrades |
| Embeddings | Qwen3-0.6B self-hosted | married, never rented |
| Reviewer panel (provenance, adversary, validator) | gpt-oss-120b (Groq, $0) | small verifiable steps, fresh contexts |
| engineer, security, exo, skill, weekly, frontend seats | Opus (set explicitly; the action DEFAULTS to Sonnet when unset, incident learned 2026-09-18) | agentic coding, gold drafting, audits, visual judgment: errors cost most here |
| pm, market, okr, finance seats | **Sonnet, since 2026-09-23.** Open routing to `kimi-k2.7-code` (chair, 2026-09-19, HQ ADR-015) is PAUSED: the secrets were removed, so the fallback step is live. The routed step is still in all four workflows | the seats judged Sonnet-shaped were the ones sent open first, and the PM failed twice. Conditions for resuming are in the 2026-09-24 addendum |
| sales seat | Opus (moved up 2026-09-18, incident 11: creative breadth under open briefs is premium-tier work) | campaigns and creative strategy |
| Mechanical subtasks inside any seat's run | Haiku via `.claude/agents/sweeper` | log parsing, link checks, inventory sweeps |

## The three levers, cheapest first

1. **Right-size within Claude (implemented now).** Per-seat `--model`
   in the workflow `claude_args`, and a repo-level `.claude/agents/`
   worker (`sweeper`, Haiku) that any seat's run can spawn for grunt
   work so premium tokens never read logs. Zero new infrastructure.
2. **Route whole seats to open models through a proxy (adopt when a
   seat's shape is proven).** The mature options found on GitHub
   (2026-09): musistudio/claude-code-router (37k stars, a local
   control plane that points Claude Code at any model),
   lm-sys/RouteLLM (5.5k, the research framework for
   quality-preserving cost routing), katanemo/plano (7k, AI-native
   proxy with routing and guardrails), NadirClaw (drop-in
   cheap-vs-premium router for Claude Code). Pattern for us: start
   claude-code-router in the Actions runner, point the seat at Groq's
   gpt-oss-120b, $0. Risk: open-model tool-calling reliability on
   long agentic runs. Rule: a seat migrates only after its run shape
   is stable and a golden-set comparison passes, the same bake-off
   discipline that chose the distill model.
3. **Our own router in the orchestration layer (the destination).**
   A policy the ExO agent tunes from evidence: task-class table plus
   an escalation rule, open model first, escalate to Claude when a
   verifier rejects or the run stalls. RouteLLM is the reference
   design. Note the product angle: a research-tuned router is itself
   a sellable orchestration artifact, squarely inside the owner's
   differentiation (directly applicable orchestration tools), and the
   claim graph already ingests the routing literature that would tune
   it.

## Guardrails

- The north star is product quality benchmarked against competitors.
  A routing change that saves tokens and dents quality reverts; the
  monthly benchmark is the detector.
- Model changes are evidence changes: golden sets before and after,
  archived in docs/evals/, per the ADR-5 habit.

## Addendum 2026-09-19: the writer seat

The writer agent (ADR-28, editor-in-chief) runs on **Opus**, explicit
`--model opus` in agent-writer.yml, because editorial judgment on
prose quality is exactly where the premium tier earns its cost. Cap
150 turns, timeout 75 minutes, daily after the digest publishes.
Verify from run logs' modelUsage as with every seat.

## Addendum 2026-09-20: open routing is live, and it has never worked

This is the first ExO run to open this file since it was written, which
was the point of putting it in the charter's read list on 2026-09-19.
It was stale on arrival, and the thing it had missed is large.

### What changed under the register

On 2026-09-19 at 18:49 UTC the chair merged PR #49, commit 609d7cc, and
four workflows gained a second, preferred run step. Whenever
`OPENROUTE_API_KEY` is set, `agent-pm.yml`, `agent-market.yml`,
`agent-okr.yml` and `agent-finance.yml` point `ANTHROPIC_BASE_URL` and
`ANTHROPIC_AUTH_TOKEN` at a third-party endpoint and pass
`--model ${{ vars.OPENROUTE_MODEL || 'kimi-k2.7-code' }}`. The Sonnet
step is still in each file, guarded by `if: env.OPENROUTE == ''`, so it
runs only when the secret is absent. The secret is present. Four of the
org's twelve seats are therefore open-routed today, and the Sonnet
fallback is unreachable while the key exists.

That is lever 2 of this page, adopted in one commit. The owner's
directive of 2026-09-17 is exactly this, so the direction is hers and
this seat's lane is the evidence rather than the decision.

### What happened on the first run

It failed. Incident 23 in [incidents.md](incidents.md) has the full
diagnosis. The PM dispatch of 2026-09-20 06:16 UTC, run 35493791740, was
the first execution of the open-routed path by any seat, and it returned
`is_error: true` at `num_turns: 1` after 190 seconds, with
`total_cost_usd: 0` and an empty `modelUsage`. No model answered. The
seat shipped nothing, and ship-first could not help it, because the run
never reached a second turn.

Read that number carefully before drawing a conclusion about open
models. Nothing here is evidence that `kimi-k2.7-code` writes a bad
sprint plan. It is evidence that the endpoint did not serve the request
at all, which is a plumbing result and not a quality result. The
distinction matters because the wrong lesson is cheap to learn here.

### The clause this page already had, and what it now requires

This register's own rule for lever 2 reads: "a seat migrates only after
its run shape is stable and a golden-set comparison passes, the same
bake-off discipline that chose the distill model." Four seats migrated
without either. So the rule was not wrong and it was not enforced, which
is the pattern docs/agents/registers.md exists to kill. It is recorded
there as a gap against this file, and the honest reading is that a
register owned by a seat that runs weekly cannot gate a change that
lands on a Friday evening.

From here, three things decide whether the four seats stay open, and
all three are cheap.

1. **The path serves a request at all.** One hand dispatch of one routed
   seat, with the action in debug mode so the endpoint's actual error is
   visible. Until this passes, quality is not a question yet.
2. **The seat completes its real work.** One full run that ships a
   branch and a pull request, judged by its artifacts as incident 8
   requires, never by its conclusion.
3. **The output holds up beside the Claude run it replaced.** For the PM
   that is a sprint file and a retro, and the comparison set already
   exists in `docs/sprints/`. This is the golden-set clause, applied to
   a seat rather than to a pipeline step, and it is the one that decides.

Verify the model from run logs and never from this table. The command is
in incident 9's lesson and it is one line:

```bash
gh run view <id> --log | grep -E '"model"|modelUsage'
```

### The risk this page named in advance

"Risk: open-model tool-calling reliability on long agentic runs." That
sentence was written on 2026-09-17 and it named the right hazard, so the
next routing decision should weight it. The four routed seats include
the PM, which is the seat the org most needs present, and the okr and
finance seats, which run monthly and dormant respectively. If the owner
wants the experiment to continue while the risk is unmeasured, the
cheapest shape is to route the seats whose failure costs least first,
which is the reverse of what landed. The PM is the worst seat to
experiment on this week, because its Monday ceremony is the one run the
whole sprint depends on.

That is a recommendation and not a decision. Routing is the owner's
call and the fallback queued in
[pending-workflow-changes.md](pending-workflow-changes.md) makes the
experiment survivable either way.


## Addendum 2026-09-24: the trial is paused, and here is what turns it back on

The chair removed the OPENROUTE secrets from this repository on
2026-09-23, so all four seats fall back to Sonnet and nothing is
currently routed anywhere. This addendum records the two runs' full
result and the conditions for resuming, so that no future run has to
reconstruct either.

**The second run, which the 2026-09-20 addendum could not have seen.**
Run 35626266985, 2026-09-21 16:32 UTC. The log shows
`"model": "kimi-k2.7-code"` answering, so the endpoint served this one.
The run worked for twelve minutes and returned `is_error: true` at
`num_turns: 30` against a cap of 300, and the no-ship tripwire fired,
meaning it had made commits it never pushed.

Read the two runs apart, because they are different results and the
distinction is the whole value of this page.

| Run | Result | What it is evidence about |
|---|---|---|
| 35493791740 | `is_error` at turn 1, empty `modelUsage` | the endpoint. Plumbing. Says nothing about the model |
| 35626266985 | `is_error` at turn 30, model answered, work unshipped | the model. Tool-calling reliability on a long agentic run |

Only the second is evidence about `kimi-k2.7-code`, and it is one data
point, on one seat, on the org's most demanding non-coding charter. It
is not proof that open routing cannot work here. It is proof that this
seat is the wrong place to find out.

**What this page predicted, in its own words, on 2026-09-17.** "Risk:
open-model tool-calling reliability on long agentic runs." That is
exactly what run two did. The register named the hazard eight days
before it occurred and could not stop it, because the register is read
weekly and the change shipped in eighteen hours. That failure of
enforcement is registers.md's problem and it is recorded there. What
belongs here is the narrower lesson: **a risk this page names in advance
is a precondition, not a caveat.** If the next routing change does not
address the risk the table already lists, the change is not ready.

**The four conditions for turning routing back on.** All four, not a
majority.

1. **The either/or becomes a fallback.** Queued item 1b in
   pending-workflow-changes.md, two lines per file. Until it is applied,
   re-adding the key means a failed model call costs the whole run
   again. This is now a hard precondition and it is stated as one in the
   queue.
2. **The first seat routed is the one whose failure costs least.** That
   is finance, which is dormant, or okr, which runs monthly. Never the
   PM. The PM is the fleet-health seat, it now carries delivery health
   too, and under ADR-033 it is the only seat with dispatch authority,
   so routing it first makes every other failure harder to see. The
   rollout did the reverse in both repositories.
3. **The golden-set comparison this page already requires.** For a seat
   rather than a pipeline step, the comparison set is the seat's own
   prior output. For the PM that is the sprint files and retros in
   docs/sprints/, and it is the condition that actually decides quality.
4. **A number for what routing saves.** Nobody has written one down.
   The org has the lever analysis and no estimate of the saving, and
   four failed runs have already cost more attention than a small saving
   can return. This is asked of HQ in the relay note.

**And one thing this page is now clear about.** The owner's directive of
2026-09-17 stands and this addendum does not touch it. Route work to
open models where they suffice. What the last week established is that
"where they suffice" is a measurement, the measurement has an order, and
the order starts with the seat the org can most afford to lose.
