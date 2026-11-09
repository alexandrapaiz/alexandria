---
name: harness-engineering
description: "Three measured findings about agent harnesses that a strong model does not give unprompted. Use when deciding between fine-tuning a model and rebuilding the harness around it; when planning to fine-tune a weaker model on a stronger model's trajectories inside a scaffold already tuned around the weaker one; when deciding how to spend extra inference compute on one hard step, sampling several candidates in parallel versus reflect-and-revise; when a reinforcement-learning run's parallel rollouts all score zero so there is no learning signal and the instinct is to buy a larger group size; or when a pile of one-line prompt fixes is about to be pasted onto the end of an agent's system prompt all at once."
version: 10
status: provisional
provenance:
  extracted: 2026-09-12
  revised: 2026-11-09
  validated: "2026-09-12 A/B trial: bare Claude endorsed imitation fine-tuning on a stronger model's trajectories; with this skill loaded it refused, cited the 4-30 point regression, and prescribed harness adaptation plus on-policy single-turn correction"
  differential_screen: "2026-09-30, bare-arm pre-screen on the benchmark-class subject (skills/_validation/results/2026-09-30-bare-arm-differential-screen.md). 3 of 4 candidates qualified. he-c1 passed bare and its section was cut."
  reviews:
    - "reviews/2026-09-29-ursa-chair.md, Ursa chair session, three-stage build plan for a deployed surface. 1 design decision changed (test-time compute), 1 procedure adopted (multi-agent debugging), 2 sections confirmatory. Verdict: keep active."
  revisions:
    - "2026-11-09 (ADR-38 rule 4, format repair, no finding changed): the five entries below were 8,651 of this file's 17,602 characters and nothing reads them, so their full text moved to REVISIONS.md and each entry here is now one line. No claim, number, paper, description or body sentence changed. Full text: REVISIONS.md."
    - "2026-11-02 (two revisions on one date, a frontmatter repair and an ADR-37 maintenance pass): no claim, number or finding changed. PyYAML had refused this file on main because two `revisions` entries were glued onto one physical line, and restoring the newline cost two reader-facing clauses. The description was then rewritten in a requester's vocabulary, 124 words to 116, four confusion cases were re-pointed, and the trigger suite moved 58 of 67 to 61 of 67. Both entries in full, separately: REVISIONS.md."
    - "2026-10-27 (ADR-37 maintenance, ADR-35 the paper wins): five corrections to delta 1 and delta 2 re-verified against arxiv.org/abs/2609.09134 in full, the Gemma 4 caveat narrowed to one task, the failure-mode census of arxiv.org/abs/2607.08938 added, and `status` moved from `active` to `provisional`. Claim 201 filed for correction. Full text: REVISIONS.md."
    - "2026-10-13 (ADR-37 trigger 1, claim contradicted): claim 1119's contradiction of claim 103 is a false edge and is filed for correction, and delta 2's exception clause now carries 1119's numbers. Full text: REVISIONS.md."
    - "2026-09-30 (ADR-38, the quality bar): rewritten to deltas only, 164 lines to under 120. Claims 199, 136, 140, 190 and 243 left the provenance with the sections they supported, and no surviving sentence changed its meaning. Full text: REVISIONS.md."
  claims: [200, 201, 202, 203, 244, 102, 103, 1119]
  papers:
    - "Co-Evolving Harnesses and Models, arxiv.org/abs/2609.09134"
    - "Better Harnesses, Smaller Models (read in full 2026-10-27, the suite every delta-1 number is measured on and the failure-mode census), arxiv.org/abs/2607.08938"
    - "AgentGrad: Intervention-guided Prompt Optimization for Multi Agent Systems, arxiv.org/abs/2609.08572"
    - "What Else Needs Fixing? Cost-Effective Test-Time Compute, arxiv.org/abs/2609.03254"
    - "RLTL;DR: Self-improvement by Internalizing Self-generated Feedback, arxiv.org/abs/2609.37633"
---

# Harness engineering

Three findings, each a place the evidence points away from what a good engineer does unaided.

## Apply: the builder's checklist

1. **Not distilling a stronger model's trajectories into a weaker one whose harness is
   tuned around it.** Expect a loss; switch to single-turn on-policy correction (delta 1).
2. **Every hard step that can afford extra inference samples at least 3 candidates in
   parallel and selects**, not reflect-and-revise, unless a real verifier gives signal
   between attempts, or the parallel arm is scoring zero (delta 2).
3. **Accumulated prompt corrections are clustered and generalised before any is
   applied**, never appended as a pile (delta 3).

## Delta 1: the expected sign of that fine-tune is negative

*Validation: the 2026-09-12 A/B trial tested exactly this warning, where bare Claude endorsed the imitation fine-tune and the loaded skill refused. Bare-arm screen he-c2, 2026-09-30: partial. The bare subject chose harness work over fine-tuning but priced the fine-tune at plus 5 to 15 points, so the direction was right and the sign was wrong. Eval task he-t2 covers it.*

Fine-tuning a weaker model by imitating a stronger expert's trajectories, under a harness
evolved for the weaker model, **dropped scores by 4 to 30 points across all seven tasks**
(Co-Evolving Harnesses, claim 200), because imitation transplants planning the model
cannot execute (claim 201). **The sign is conditional on the evolved harness, and that
condition is the finding**: the identical recipe on the identical trajectories under the
un-evolved baseline harness *helps*, 29.2 to 35.5 percent mean, +6.3 (section 3.3.1).
What breaks is planning, which is also the one failure mode optimised harnesses never
address (81 percent address instruction-following, 81 knowledge, 62 tool-use, 33
long-context, planning none: Better Harnesses Smaller Models, IV-D), so neither arm
repairs a planning failure. **Adoption telemetry cannot see it, because it moves both ways
at once**: five of the six harness edits slip from near ceiling while the
domain-computation recipe rises 30.8 to 76.1 percent of rollouts, so the six-edit mean
rises. **Watch the planning-failure share instead, 1.1 to 14.6 percent of failures while
knowledge failures fall 46.2 to 44.5: it is the one instrument that moves one way**
(Tables 2 and 3).

The decision rule: the order decides the sign. A team that has already evolved its harness
does not run this fine-tune. A team that cannot afford harness work may, priced at about
+6 against the +48.8 the skipped harness work pays (29.2 to 78.0, claim 200). On top of an
evolved harness the repair is on-policy, minimal and **safe rather than large**: +1.7
mean, 78.0 to 79.7 percent, five of seven tasks up, two near ceiling (claims 202, 203):

1. Run the weaker model in **its own** harness and collect its own rollout.
2. Identify the single failing turn in that rollout.
3. Have the expert rewrite **only that turn**, leaving the rest untouched. **Sample 3
   candidate rewrites and keep the best under a quality judge.**
4. Train on about **500 rows**: roughly 400 corrections plus 50 of the model's own
   passing rollouts, chosen at its capability boundary.

## Delta 2: parallel sampling beats reflection, and the instinct is to reflect

*Validation: the one section with a recorded positive delta. It moved its eval task from 4 to 6 in the 2026-09-12 measurement (ADR-38), and it changed a live design decision in the first consumer report. Bare-arm screen he-c4, 2026-09-30: **fail**. Given three model calls for one hard step the bare subject built a three-stage sequential pipeline and asserted that voting "does not help here". Eval tasks he-t7, he-t8. The 2026-10-12 contradiction against claim 103 was read and resolved in this section's favour (see revisions); nothing about the delta changed.*

Best-of-three parallel samples, selected by an LLM judge or the medoid, **improved
accuracy 2.2 to 9.7 percent on less compute than reflection loops** (What Else Needs
Fixing, claims 102, 103).

The decision rule: default to parallel sample-and-select, and reserve sequential attempts
for the one measured exception. On tasks a policy failed 128 attempts straight, sequential
rollouts each conditioned on a one-sentence insight from the last failure's unit-test
output solved 14 to 59 percent where parallel i.i.d. rollouts solved none (RLTL;DR, claim
1119). A zero licenses the switch; on unfiltered mixes it neither helped nor hurt.

1. Budget N parallel samples at the hard step. **N is at least 3.**
2. At N of 3 or more, select the medoid, the sample most similar to the others. **A
   MiniLM-class sentence embedder is sufficient.**
3. At N of 2 there is no medoid, so select with an LLM judge.
4. Never spend the budget on a second attempt conditioned on the first unless something
   between them can tell the model it was wrong. **A parallel arm scoring zero is that
   exception**: feed the verifier's output into a one-sentence insight and condition on it.

## Delta 3: cluster the corrections before you apply them

*Validation: no trial. Adopted as procedure by the first consumer report (reviews/2026-09-29-ursa-chair.md), which named this the non-obvious half, and untested in action. Bare-arm screen he-c3, 2026-09-30: partial. The bare subject volunteered "avoid editing all four prompts at once" and a first-error labelling procedure, so localisation was cut; it did not cluster. Eval task he-t6.*

Concatenating accumulated fixes into one prompt mixes unrelated failure modes. Clustering
them first reached state of the art on five multi-agent benchmarks while **cutting
optimisation wall-clock 2.5x against the next-fastest method** (AgentGrad, claim 244). So
a backlog is input to an abstraction step, not text to append.

1. Embed the collected corrections and group them by semantic similarity.
2. Abstract each cluster into **one** generalised correction for the shared pattern.
3. Apply the generalised corrections. Never the raw pile.

## Caveats

- The co-evolution numbers are 7 enterprise agent tasks with Qwen3-Coder as the weaker
  model, and Gemma 4 is a one-task replication (Webarena, 55.6 to 41.1 percent) rather
  than a second seven-task arm. This is weaker models under harnesses evolved for them.
- Delta 2's direction has a recorded positive eval delta on our own subject. The 2.2 to
  9.7 percent is one paper's set; what transfers is the procedure's floor, 3 samples and
  a MiniLM-class embedder. Its exception is one model on three task sets.
- Cut and why: the 2026-09-30 bare-arm screen cut four sections the bare subject already
  gave unprompted. Receipt: `_validation/results/2026-09-30-bare-arm-differential-screen.md`.
