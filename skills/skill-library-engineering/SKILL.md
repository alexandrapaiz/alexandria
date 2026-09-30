---
name: skill-library-engineering
description: Three measured findings about the loadable skill file and how it gets picked, which a strong model does not give unprompted. Use when deciding whether a skill optimised against one model has to be re-optimised before deploying on a stronger one; when one request needs several complementary skills at once and a diversity or redundancy penalty is about to be added to the retrieval score; or when a decision about a skill library needs a magnitude rather than a direction, such as how far to move a reuse threshold, how many revision rounds to buy, or whether an optimizer is worth building.
version: 3
status: active
provenance:
  extracted: 2026-09-26
  revised: 2026-09-30
  validated: ""
  differential_screen: "2026-09-30, bare-arm pre-screen on the benchmark-class subject, two rounds, 7 candidates for this skill (skills/_validation/results/2026-09-30-bare-arm-differential-screen.md). Only 2 qualified, which is the weakest result in the library and is stated plainly in the pull request: 5 of 7 prescriptions this skill carried are things the bare subject says unprompted, several of them better. Under ADR-38 clause 7 this file is the library's first retirement candidate if its differential eval does not move."
  reviews:
    - "none filed yet. The lane is open at reviews/ (ADR-38); see reviews/README.md for what this skill most wants reported."
  revisions:
    - "2026-09-30 (ADR-38, the quality bar): 337 lines to under 120, ten sections to three. Cut on measurement: write-from-recorded-runs (sle-c1, where the bare subject independently produced this library's own ADR-38 thesis, including 'delete what the model already knows'), the description-as-routing-surface section (sle-c2, answered with instrumentation, mechanical-cause triage, situation-plus-vocabulary rewriting and replay validation to an 80 percent hit rate), the reuse threshold (sle-c3, which it refused with a 3-to-5x asymmetry weighting), grounding-before-an-optimizer (sle-c4, refused with a minimum-detectable-effect calculation), and revise-in-rounds (sle-c6, answered with a cap of three, held-out gating, reader separation and a not-a-skill-problem label this file lacked). What survives of all five is their magnitudes, collected in delta 3."
  claims: [320, 321, 322, 328, 329, 400, 565, 567, 568, 569, 625]
  papers:
    - "Beyond Top-k Skill Retrieval: Diversity-Aware Skill Routing for LLM Agents — arxiv.org/abs/2609.05824"
    - "COBRA-Skills: Contextual Bandit-Guided Evolution for Agent Skill Optimization — arxiv.org/abs/2609.11682"
    - "The Router Within: Eliciting Native Skill Routing from a Frozen LLM — arxiv.org/abs/2609.15982"
    - "Reflect, Revise, Reuse: Training-Free Skill Evolution for GUI Agents — arxiv.org/abs/2609.17653"
    - "GraphSkillEvo: Evolutionary Optimization of Graph-Structured Agent Skills — arxiv.org/abs/2609.21749"
---
# Skill library engineering

One finding that contradicts a strong model, one trap the obvious method walks into, and a
price list, because here the directions are free and the magnitudes are not.

## Apply: the builder's checklist

1. **Do not re-optimise a skill for a stronger model before measuring it there.** Optimised
   skills transfer upward, sometimes beating one optimised directly on the larger model.
2. **Adding a redundancy penalty to set selection? Project out the query-aligned component
   first.** Penalising raw similarity measured **worse than the pointwise baseline**.
3. **Three magnitudes from delta 3, because a direction without one is a guess.** Move a
   reuse threshold from the strict side only, 0.6 to 0.4 costing 14.3 points against 2.8 for
   0.6 to 0.8. Stop revising at three rounds and isolate the diagnosing reader, worth 8.57.
   Do not build an optimizer for the 2.2 to 2.5 points it adds to grounding's 13 to 27.

## Delta 1: skills transfer upward, and the instinct is to re-optimise

*Validation: no trial and no consumer report. Bare-arm screen sle-c7, 2026-09-30: **fail**. Asked whether a skill optimised on a small model must be re-optimised before deploying on a much larger one, the bare subject said yes, predicted part of the file would be "actively harmful" on the larger model, and told the builder to expect to cut 30 to 60 percent of it. The measured evidence points the other way. Eval task sle-t9.*

**34 of 36 cross-model transfers improved on the receiving model's no-skill baseline**
(COBRA-Skills), and a skill optimised on a small model and deployed on a large one beat that
large model's no-skill baseline on all three benchmarks, **in one case beating the skill
optimised directly on the large model, 71.78 against 69.40** (GraphSkillEvo). Skills held
their lead under two external harnesses too (claim 322).

1. Deploy the existing skill on the new model and measure against that model's **no-skill**
   baseline. The bare instinct is right on one point: never compare against the small model
   with a skill.
2. Re-optimise only if that comparison is flat or negative. Expect it not to be, and where
   you do, the rewriting model need not be stronger than the target: **the target writing
   its own skills lost one point, 73.5 to 72.5, at about half the cost** (claim 322).

## Delta 2: the redundancy penalty everyone reaches for scores below the baseline

*Validation: no trial and no consumer report. Bare-arm screen sle-c5, 2026-09-30: partial. The bare subject switched to set selection unprompted and then prescribed MMR at lambda about 0.7, which is a penalty on raw similarity between candidates. That is the exact configuration measured below the pointwise baseline. The prescription is not the delta; the trap is. Eval task sle-t5.*

Treating routing as complementary **set** selection rather than pointwise ranking improved
recall and coverage over a strong reranker (claims 328, 329), which a strong model tells you
itself. The trap is the implementation. **Penalising raw similarity between candidates made
things sharply worse than the pointwise baseline it was meant to improve, 0.534 against
0.705 recall**, because skills needed by one request are similar for a good reason. Only
after removing the query-aligned component of each representation did set selection win, at
**0.711**.

1. Decompose the request and select a **set**, not a ranked list.
2. Project out the query-aligned component before penalising similarity; a plain MMR-style
   penalty on raw similarity is the failing arm.
3. Verify against the **pointwise baseline**, not only against no selection. The failing arm
   loses to it by 17 recall points, so a missing baseline hides the defect entirely.
4. Write neighbouring skills to differ on the axis the requester varies, and accept that two
   skills covering different steps of one workflow are meant to look alike (ours).

## Delta 3: the price list

*Validation: this section exists because of the screen rather than in spite of it. Every line is the magnitude behind a prescription the bare subject gave unprompted and without a number (sle-c1, c2, c3, c4, c6, all passes). Adopting a direction is free; these are what it costs to get it wrong. Eval tasks sle-t1, sle-t3, sle-t4, sle-t6.*

- **An ungrounded skill is net negative, not merely weak.** A human expert's skill averaged
  **67.23 against 67.97 for no skill at all** and cost **7.5 points** on one benchmark; a
  model's, written from the task description, 67.21. Skills refined against execution
  trajectories averaged **8 to 10 points above** no-skill.
- **Routing fails silently.** Qwen3-32B under progressive disclosure loaded the correct skill
  on **1.1 percent** of 177 executable tasks; the same frozen model with a native router,
  **90.9 percent** (claim 400). One deployed harness caps all skill metadata at **2 percent
  of the context window**, so each description's room shrinks as the library grows.
- **Loose matching costs more than twice what strict matching costs.** 0.6 to 0.4 dropped
  success from **69.5 to 55.2 percent**, 0.6 to 0.8 only to **66.7**. Metadata retrieval
  recovered the right skill in **12 of 12** reuse cases against **1 of 12** for full text
  (claim 568).
- **Revision saturates at three rounds**, worth **12.4 points**, a fourth and fifth adding
  **0.9** (claim 569). Three rounds beat three independent retries **69.5 to 62.8** on a
  smaller budget. Removing the reader's isolation cost **8.57 points**, in-run amendment
  **6.66** (claim 567).
- **The optimizer is the cheap part.** Removing the bandit cost **2.2 points**, removing
  population evolution **2.4**, against a total gain of **13.1 to 26.9** over no skill; a
  Best-of-30 grounded baseline came within **2.5 points** of the full system on **50 unique
  optimization examples** (claims 320, 321).

## Caveats

- The strongest execution numbers are GUI agents on MobileWorld, AndroidWorld and OSWorld
  (claim 565), and screen interfaces are non-stationary in ways a file-and-shell environment
  is not. The metadata-retrieval result rests on 12 reuse cases and the routing-set result on
  75 queries: directionally strong, statistically thin.
- Every routing number measures whether the right skill was selected, not whether the task
  then succeeded. An agent can fail with every required skill retrieved, including from
  conflicts among the loaded skills' own instructions (Beyond Top-k).
- Delta 1's transfer numbers come from reading both papers in full and are carried by **no
  claim row in our own graph**, filed for the research seat. Delta 3's first line covers four
  to five benchmarks on two OpenAI models and is the finding most worth re-testing yourself.

## What this file no longer carries

Seven sections cut 2026-09-30, five because the bare subject gave them unprompted and often
better. Their magnitudes are delta 3; the frontmatter's revision note names each one.
Receipts, with the bare answers, in
`skills/_validation/results/2026-09-30-bare-arm-differential-screen.md`.
