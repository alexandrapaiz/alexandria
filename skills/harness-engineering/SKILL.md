---
name: harness-engineering
description: Three measured findings about agent harnesses that a strong model does not give unprompted. Use when deciding between fine-tuning a model and rebuilding the harness around it; when planning to fine-tune a weaker model on a stronger model's trajectories inside a scaffold already tuned around the weaker one; when deciding how to spend extra inference compute on one hard step, for instance sampling several candidates in parallel and selecting one versus having the agent reflect on and revise its previous attempt; or when a backlog of accumulated prompt corrections is about to be appended to an agent's system prompt.
version: 4
status: active
provenance:
  extracted: 2026-09-12
  revised: 2026-09-30
  validated: "2026-09-12 A/B trial: bare Claude endorsed imitation fine-tuning on a stronger model's trajectories; with this skill loaded it refused, cited the 4-30 point regression, and prescribed harness adaptation plus on-policy single-turn correction"
  differential_screen: "2026-09-30, bare-arm pre-screen on the benchmark-class subject (skills/_validation/results/2026-09-30-bare-arm-differential-screen.md). 3 of 4 candidates qualified. he-c1 passed bare and its section was cut."
  reviews:
    - "reviews/2026-09-29-ursa-chair.md, Ursa chair session, three-stage build plan for a deployed surface. 1 design decision changed (test-time compute), 1 procedure adopted (multi-agent debugging), 2 sections confirmatory. Verdict: keep active."
  revisions:
    - "2026-09-30 (ADR-38, the quality bar): rewritten to deltas only, 164 lines to under 120. Cut the order-of-operations section entire (action interface, feedback enrichment, feedback consistency) because the bare subject gave all of it unprompted on he-c1, including the step-count arithmetic; cut the localisation half of the debugging section for the same reason. Claims 199, 136, 140, 190 and 243 leave the provenance with the sections they supported. No surviving sentence changed its meaning."
  claims: [200, 201, 202, 203, 244, 102, 103]
  papers:
    - "Co-Evolving Harnesses and Models — arxiv.org/abs/2609.09134"
    - "AgentGrad: Intervention-guided Prompt Optimization for Multi Agent Systems — arxiv.org/abs/2609.08572"
    - "What Else Needs Fixing? Cost-Effective Test-Time Compute — arxiv.org/abs/2609.03254"
---

# Harness engineering

Three findings, each one a place where the evidence points away from what a
competent engineer does unaided. The last section names what was cut and why.

## Apply: the builder's checklist

1. **Not distilling a stronger model's trajectories into a weaker one whose
   harness is tuned around it.** Expect a loss, not a small gain; switch to
   single-turn on-policy correction (delta 1).
2. **Every hard step that can afford extra inference samples at least 3
   candidates in parallel and selects**, rather than reflecting and revising,
   unless a real verifier gives signal between attempts (delta 2).
3. **Accumulated prompt corrections are clustered and generalised before any
   of them is applied**, never appended as a pile (delta 3).
4. **Every improvement is the smallest local change that repairs the observed
   failure**, never a wholesale replacement in someone else's style.

## Delta 1: the expected sign of that fine-tune is negative

*Validation: the 2026-09-12 A/B trial tested exactly this warning, where bare Claude endorsed the imitation fine-tune and the loaded skill refused. Bare-arm screen he-c2, 2026-09-30: partial. The bare subject chose harness work over fine-tuning but priced the fine-tune at plus 5 to 15 points, so the direction was right and the sign was wrong. Eval task he-t2 covers it.*

Fine-tuning a weaker model by imitating a stronger expert's trajectories,
under a harness evolved for the weaker model, **dropped scores by 4 to 30
points across all seven tasks** (Co-Evolving Harnesses and Models, claim 200).
Not a smaller gain than harness work. A loss, on every task measured, because
imitation transplants the expert's planning strategy into a model that cannot
execute it, breaking model-harness fit and measurably decreasing scaffold
usage (claim 201).

The decision rule: "fine-tune or improve the harness" is not a comparison of
two positive returns, so a team that cannot afford harness work this quarter
should do nothing rather than the fine-tune.

When training is the already-chosen path, the repair that recovers performance
is minimal and on-policy (claims 202, 203):

1. Run the weaker model in **its own** harness and collect its own rollout.
2. Identify the single failing turn in that rollout.
3. Have the stronger expert rewrite **only that turn**, leaving the rest of
   the trajectory untouched.
4. Train on the corrected rollout.

## Delta 2: parallel sampling beats reflection, and the instinct is to reflect

*Validation: the one section with a recorded positive delta. It moved its eval task from 4 to 6 in the 2026-09-12 measurement (ADR-38), and it changed a live design decision in the first consumer report. Bare-arm screen he-c4, 2026-09-30: **fail**. Given three model calls for one hard step the bare subject built a three-stage sequential pipeline and asserted that voting "does not help here". Eval tasks he-t7, he-t8.*

Best-of-three parallel samples, selected either by an LLM judge or by picking
the medoid, **improved accuracy by 2.2 to 9.7 percent while using less compute
than reflection loops** (What Else Needs Fixing, claims 102, 103).

The decision rule: default to parallel sample-and-select. Reserve sequential
reflection for the one case where a verifier gives real signal between
attempts, which is the only way a second attempt knows more than the first.

1. Budget N parallel samples at the hard step. **N is at least 3.**
2. At N of 3 or more, select the medoid, the sample most similar to the others.
   **A MiniLM-class sentence embedder is sufficient.**
3. At N of 2 there is no medoid, so select with an LLM judge.
4. Never spend the budget on a second attempt conditioned on the first unless
   something between them can tell the model it was wrong.

## Delta 3: cluster the corrections before you apply them

*Validation: no trial. Adopted as procedure by the first consumer report (reviews/2026-09-29-ursa-chair.md), which named this the non-obvious half, and untested in action. Bare-arm screen he-c3, 2026-09-30: partial. The bare subject volunteered "avoid editing all four prompts at once" and a first-error labelling procedure, so localisation was cut; it did not cluster. Eval task he-t6.*

Concatenating accumulated fixes into one prompt mixes unrelated failure modes.
Clustering them first reached state of the art on five multi-agent benchmarks
while **cutting optimisation wall-clock by 2.5x versus the next-fastest
method** (AgentGrad, claim 244).

The decision rule: a backlog of corrections is input to an abstraction step,
not text to append. The prompt grows by fewer lines than the backlog holds.

1. Collect the textual corrections gathered from failures.
2. Embed and group by semantic similarity so unrelated modes never mix.
3. Abstract each cluster into **one** generalised correction capturing the
   shared pattern.
4. Apply the generalised corrections. Never the raw pile.

## Caveats

- The co-evolution results are 7 enterprise agent tasks with Qwen3-Coder and
  Gemma 4 as the weaker models. The regression is about weaker models under
  harnesses evolved for them, not about distillation generally.
- Delta 2's direction has a recorded positive eval delta on our own subject.
  The 2.2 to 9.7 percent is one paper's benchmark set and does not transfer.
  Its floor is stated in the procedure: 3 samples and a MiniLM-class embedder.

## What this file no longer carries

Cut 2026-09-30 because the bare subject produced all of it unprompted: few
semantic actions over many low-level ones, rich errors over a bare "failed",
reproduce before intervening, one agent at a time starting upstream. All still
correct, none worth your context window. **Feedback consistency** (claim 140)
went for a different reason, that our row carries no magnitude and ADR-38
requires a number; it is filed for the research seat to price. Receipts:
`skills/_validation/results/2026-09-30-bare-arm-differential-screen.md`.
