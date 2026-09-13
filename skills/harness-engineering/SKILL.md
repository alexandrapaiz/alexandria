---
name: harness-engineering
description: Evidence-backed practices for designing, improving, and debugging agent harnesses (the scaffold around a model - tools, prompts, loop structure, feedback). Use when building an agent or multi-agent system, when an agent underperforms and the cause is unclear, when debugging a multi-agent pipeline, when the user plans to fine-tune or distill a smaller model on a stronger model's trajectories, when deciding between improving the harness and training the model, or when allocating test-time compute.
version: 1
status: active
provenance:
  extracted: 2026-09-12
  validated: "2026-09-12 A/B trial: bare Claude endorsed imitation fine-tuning on a stronger model's trajectories; with this skill loaded it refused, cited the 4-30 point regression, and prescribed harness adaptation plus on-policy single-turn correction"
  claims: [199, 200, 201, 202, 203, 243, 244, 102, 103, 136, 140, 190]
  papers:
    - "Co-Evolving Harnesses and Models — arxiv.org/abs/2609.09134"
    - "AgentGrad: Intervention-guided Prompt Optimization for Multi Agent Systems — arxiv.org/abs/2609.08572"
    - "What Else Needs Fixing? Cost-Effective Test-Time Compute — arxiv.org/abs/2609.03254"
    - "Environments as Scaffold: Feedback-Enriched Environments — arxiv.org/abs/2609.08404"
    - "Show-Harness: Just a VLM Agent Can Play Robots — arxiv.org/abs/2609.10522"
---

# Harness engineering

The harness is everything around the model: the tools it can call, the prompts
that frame each turn, the loop that decides what happens next, and the feedback
the environment returns. Recent evidence says the harness is usually the
higher-leverage place to work than the model weights, and that harness and
model must be treated as one coupled system, not two independent parts.

This skill adds to standard engineering practice, it does not replace it.
Keep giving the advice you would give anyway where it still holds: full
trajectory logging with per-turn spans, per-agent contracts and metrics, and
questioning whether the multi-agent decomposition itself is too fine-grained.
The findings below are the deltas: the places where recent evidence is
counterintuitive or not yet common knowledge. Lead with these where they
apply, and let them override generic advice only where they directly
conflict (the fine-tuning warning below is the main such conflict).

## Order of operations: harness before weights

When an agent underperforms, exhaust harness improvements before reaching for
fine-tuning. Evolving the harness alone, with the same weaker model, produced
substantial gains on seven enterprise agent tasks before any training was done
(Co-Evolving Harnesses and Models). Interface design alone can unlock
capability that looks like it would require a bigger model: a compact,
well-designed action interface let unmodified frontier VLMs control robots
zero-shot, outperforming trained task-specific baselines (Show-Harness).

Concretely, before proposing training:

1. Tighten the action interface. Fewer, more semantic actions beat many
   low-level ones. Ask whether the model can state its intent in one unit of
   your interface, or whether it must compose several fragile steps.
2. Enrich the feedback the environment returns. Richer error messages and
   intermediate signals measurably improve long-horizon agents (Environments
   as Scaffold). A bare "failed" is the worst feedback a harness can give.
3. Keep feedback consistent. If the same action in similar states returns
   differently shaped or differently graded feedback, agents destabilize.
   Feedback consistency is a hard boundary, not a nicety.

## Never break model-harness fit

A harness evolved around one model's behavior becomes part of that model's
extended body. The clearest negative result in this cluster: fine-tuning a
weaker model by imitating a stronger expert's trajectories, under a harness
evolved for the weaker model, made things consistently worse, dropping scores
by 4 to 30 points across all seven tasks. The imitation transplanted the
expert's planning style into a model that could not execute it, which broke
the fit between model and scaffold (Co-Evolving Harnesses and Models).

The repair that works is minimal, on-policy correction:

1. Run the weaker model in its own harness and collect its own rollout.
2. Identify the single failing turn in that rollout.
3. Have the stronger expert rewrite only that turn, leaving the rest of the
   trajectory untouched.
4. Train on the corrected rollout. The model keeps its native planning style
   and its harness fit, and performance recovers instead of regressing.

Apply the general principle even outside training: when improving any part of
a coupled agent system, prefer the smallest local change that fixes the
observed failure over wholesale replacement with someone else's style.

## Debugging a multi-agent harness: intervene one agent at a time

When a system of multiple agents fails, do not guess which agent is at fault
and do not change several things at once. Localize by sequential intervention
(AgentGrad):

1. Make the failure reproducible first. Pin the inputs, any retrieval corpus
   or environment snapshot, and seeds where the stack allows. This
   presupposes full trajectory logging; if the system lacks it, add it
   before intervening, since an intervention you cannot replay tells you
   nothing.
2. Pick one agent, replace its prompt with a candidate fix, and rerun the
   whole system with everything else unchanged. A practical ordering (ours,
   not the paper's): start upstream, with the planner, because upstream
   errors masquerade as downstream ones.
3. If the failure persists, revert and move to the next agent.
4. The first agent whose change makes the failure disappear is the
   responsible one. Record its corrected output.
5. Use that corrected output as the supervision signal for a precise prompt
   update, rather than rewriting prompts by intuition.

When many such fixes accumulate, do not concatenate them into one bloated
prompt. Cluster them first:

1. Collect the textual corrections gathered from failures.
2. Embed them and group by semantic similarity, so unrelated failure modes
   never mix.
3. Abstract each cluster into one generalized correction that captures the
   shared pattern.
4. Apply the generalized corrections, not the raw pile.

This kept prompt updates targeted and generalizable, and reached
state-of-the-art on five multi-agent benchmarks while cutting optimization
wall-clock by 2.5x versus the next-fastest method.

## Spending test-time compute: sample in parallel, then select

When the harness can afford extra inference for a hard step, parallel sampling
with a cheap selection step beats asking the model to sequentially reflect on
and revise its own answer. Best-of-three parallel samples, selected either by
an LLM judge or by picking the medoid (the answer most similar to the others),
improved accuracy by 2.2 to 9.7 percent while using less compute than
reflection loops (What Else Needs Fixing). Default to parallel
sample-and-select in harness design; reserve sequential reflection for cases
where a verifier gives real signal between attempts.

## Caveats

- The co-evolution results are from 7 enterprise tasks with Qwen3-Coder and
  Gemma 4 as the weaker models; the imitation-regression finding is about
  weaker models under evolved harnesses, not about distillation generally.
- Medoid selection needs at least 3 samples and an embedding model; with 2
  samples use an LLM judge.
- These findings are from 2026 papers and carry alexandria claim provenance;
  if a source claim is later contradicted, this skill will be revised or
  deprecated.
