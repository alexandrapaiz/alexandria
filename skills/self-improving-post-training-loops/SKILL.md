---
name: self-improving-post-training-loops
description: Evidence-backed practices for designing closed-loop post-training pipelines where a model supervises, grades, or teaches its own next training step (self-distillation against a synthetic or gated teacher, verifier-free rubric-based credit assignment, capability-guided data selection). Use when building a training loop that turns a model's own rollouts into its next training signal, when deciding whether a teacher model's outputs can be trusted before distilling from them, when a self-distillation or self-improvement run destabilizes or collapses, when designing a reward or rubric for long-horizon agent training without a verifier, or when converting an agent harness's own interaction logs into training data. Distinct from harness-engineering, which covers the inference-time scaffold around a frozen model; this skill covers the training loop that updates the weights.
version: 1
status: active
provenance:
  extracted: 2026-09-18
  validated: ""
  claims: [30, 31, 32, 33, 116, 117, 118, 119, 120, 141, 142, 143, 144, 96, 97, 98, 99, 39, 40, 41, 42]
  papers:
    - "RISE: Recursive Improvement via Self-Extrapolating Policy Distillation — arxiv.org/abs/2609.05295"
    - "Verify Before You Distill: Prompt-Level Teacher Gating for On-Policy Distillation — arxiv.org/abs/2609.02998"
    - "NeoHorse-1: Towards Recursive Self-Improvement via Agentic Post-Training with Routing Harness — arxiv.org/abs/2609.08183"
    - "FlowBalance: Verifier-Grounded Self-Improvement from On-Policy Reasoning Experience — arxiv.org/abs/2609.03241"
    - "DRACO: Fine-Grained Credit Assignment with Dynamic Rubrics for Long-Horizon Agent Training — arxiv.org/abs/2609.04094"
---

# Self-improving post-training loops

A self-improving post-training loop is any pipeline where a model's own rollouts,
or a teacher derived from them, become the supervision signal for the model's
next update: self-distillation, on-policy distillation, and rubric-based RL
without a verifier all fit this shape. A competent ML engineer already knows
how to run supervised fine-tuning and RL. What is not yet common knowledge is
what breaks specifically when the supervision signal is self-referential: can
the teacher be trusted, when should it be refreshed, and how do you grade a
rollout with no ground truth. Five 2026 papers converge on the same handful of
mechanisms for these questions, cross-supported by real supports and refines
edges in the claim graph rather than one paper's opinion.

This skill adds to standard post-training practice, it does not replace it.
Keep doing what already works: hold out an eval suite disjoint from the
training mixture, log every rollout, and watch entropy and response length for
collapse. The findings below are the deltas, the places a self-referential
loop needs something a standard fine-tune does not.

## Refresh the teacher every iteration, do not distill once and stop

Construct a synthetic teacher directly from the model's own RLVR training
trajectory, converting sparse outcome-induced updates into dense per-token
supervision without needing an external or privileged model (RISE). Combine
outcome-based RLVR reward with on-policy distillation from that synthetic
teacher in one loop: the reward grounds the extrapolation, and the
extrapolated teacher refines the token-level decisions (RISE). The step that
makes this recursive rather than a one-time compression is refreshing the
synthetic teacher every iteration as the student improves; a teacher built
once and reused is not implementing the same thing (RISE). Across
mathematical reasoning, multi-domain STEM, code generation, and multi-turn
agentic tasks, this consistently outperformed both RLVR-only training and
one-shot on-policy self-distillation (RISE).

## Gate teacher trust before dense distillation, fall back when it fails

Before running dense on-policy distillation, estimate the teacher's
reliability on each prompt from a small set of verifier-scored teacher probes
(Verify Before You Distill). Route each prompt on that estimate: dense
distillation when the reliability check passes, verifier-grounded GRPO when
it does not, since a confidently wrong teacher gives misleading updates that
a fallback signal avoids (Verify Before You Distill). The gate is not only an
accuracy win, it is a compute win: gating which prompts actually need the
teacher raised teacher-node GPU utilization from 9.8% to 78.9% in one 4B
single-domain run, because idle teacher capacity in vanilla asynchronous
on-policy distillation gets used once the gate decides which prompts are
worth it (Verify Before You Distill). The gated approach beat vanilla
on-policy distillation across all six single-domain settings and on
multi-domain benchmarks, at both 4B and 35B scale (Verify Before You
Distill).

## Close the loop between evaluation, data selection, and the next mixture

A training mixture chosen once at the start is not a closed loop. Convert
evaluation feedback directly into the next training mixture through
capability-guided allocation, so what the system currently learns to do
shapes what data it learns from next (NeoHorse-1). Use routing signals, which
capability tier actually handled a given case, to structure supervised
fine-tuning into a staged curriculum and to decide which student outputs a
teacher should supervise through distillation (NeoHorse-1). One concrete data
source for this loop: recorded harness interactions, including interleaved
reasoning, tool calls, and harness context, become training examples once
validated by structural checks, multi-dimensional semantic evaluation, and
subscene-level labeling before being mixed in (NeoHorse-1). This routing
harness raised macro-average performance across eleven benchmarks from 58.94
to 64.87 for a 4B model and from 65.60 to 69.04 for a 9B model (NeoHorse-1).

## Calibrate self-guidance by advantage sign, do not apply it uniformly

When a self-guidance score (an aggregated token-level log-probability gain)
shapes the training target, calibrate it against the verifier-derived group
advantage rather than trusting it everywhere: retain the guidance on
positive-advantage trajectories, reverse it on negative-advantage
trajectories, and disable it entirely when the rollout group shows no outcome
preference (FlowBalance). This calibrated signal can replace a separate
token-level imitation loss: reweight a reference policy with an exponential
energy function and fit the normalized target with a single log-partition
estimate per rollout group through trajectory balance (FlowBalance). On
mathematical reasoning benchmarks this beat FlowRL at two model scales while
training faster, staying more stable, avoiding response-length collapse, and
showing more correct-strategy diversity (FlowBalance).

## Assign credit without a verifier through dynamic rubrics

When no verifier or ground truth exists for a long-horizon agent task,
generate rubrics dynamically during training so the grading criteria track
the policy's evolving capability instead of staying fixed against a moving
target (DRACO). Redistribute each rubric's score over the specific steps
responsible for it to produce differentiated per-step advantages through a
closed-form formula, with no learned attribution module needed (DRACO). On
the AppWorld benchmark this gained 15.9 points over the base model and 5.3
points over GRPO trained with a sparse ground-truth reward, and it
generalized out of domain to Tau-Bench without a frontier judge or any
verifier (DRACO).

The general principle behind the gating and rubric findings above extends
past training: before letting anything grade or teach itself, check whether
that signal can be trusted, and build the fallback so it does not depend on
trusting it (ours, not the paper's).

## Caveats

- Model scales tested top out at 35B students (Verify Before You Distill);
  none of these five papers report results at frontier lab scale, so the
  gating and refresh mechanisms are unverified there.
- Domain coverage is math reasoning, STEM, code generation, and long-horizon
  agent benchmarks (AppWorld, Tau-Bench, and NeoHorse-1's eleven-benchmark
  suite); no results here cover open-ended dialogue or safety-tuning
  objectives.
- The harness-log-to-training-data pipeline (NeoHorse-1) is evaluated on one
  production routing-harness system; its structural-check and
  semantic-evaluation steps are not shown to generalize to harnesses built
  differently.
- This is a training-time complement to the harness-engineering skill's
  inference-time scaffold advice, not a substitute for it: when an agent
  underperforms, exhaust harness improvements first, and reach for the
  mechanisms here only once fine-tuning is the already-chosen path.
- These findings carry alexandria claim provenance from 2026 papers; if a
  source claim is later contradicted, this skill will be revised or
  deprecated.
