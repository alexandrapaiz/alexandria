# Model routing — using models intelligently across the org

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
| pm, market, okr seats | Claude Sonnet | strategy and writing over a repo, Sonnet-shaped |
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
