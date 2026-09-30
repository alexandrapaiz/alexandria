---
name: evaluation-integrity
description: Three measured findings about instruments a model produced, which a strong model does not give unprompted. The subject is the rubric, the judge and the verdict, not the system they score. Use when a model-written rubric is about to become a reward signal or a gate; when a pass-or-fail verdict from a checker, a compiler or a test suite stands in for correctness; when a single-turn evaluation is being read as a reliability result; or when reporting an exploit rate or a benchmark score you intend someone else to trust.
version: 4
status: active
provenance:
  extracted: 2026-09-24
  revised: 2026-09-30
  validated: ""
  differential_screen: "2026-09-30, bare-arm pre-screen on the benchmark-class subject, two rounds, 7 candidates for this skill (skills/_validation/results/2026-09-30-bare-arm-differential-screen.md). 3 qualified, all as partials. ei-c3, ei-c5 and ei-c7 passed bare and their sections were cut; ei-c6 was dropped for carrying no magnitude."
  reviews:
    - "none filed yet. The lane is open at reviews/ (ADR-38); see reviews/README.md for what this skill most wants reported."
  revisions:
    - "2026-09-30 (ADR-38, the quality bar): 467 lines to under 120, eleven sections to three. Cut on measurement: the noise band (ei-c3, where the bare subject supplied the five-to-ten repeat floor this file had claimed as ours), the four shortcut channels (same answer), judge-variance monitoring (same answer's grader-noise re-grading), the unanimous panel (ei-c5, where the bare subject required unanimity, named judge correlation as the dominant error term and failed malformed judgments closed), and the benchmark-defect profile (ei-c7, answered with gold-patch and empty-patch screens, leakage detection and rank inversion). Cut for carrying no magnitude, which ADR-38 requires: partial monitoring (claims 269, 272, 273) and the defect ordering (claims 237-240); both filed for the research seat to price. The certification protocol's challenger gate (claims 286, 288, 290) moved to recursive-harness-self-improvement, where the loop needing it lives, rather than being carried twice."
  claims: [476, 477, 478, 479, 480, 260, 261, 262, 263, 557, 559, 560, 561]
  papers:
    - "ImpossibleRubrics: Stress-Testing Generated Rubrics — arxiv.org/abs/2609.12534"
    - "Beyond Solver Verdicts: Generative Verification for Formalization — arxiv.org/abs/2609.13147"
    - "PACT: Pressure-Tested Compliance for Enterprise Assistants — arxiv.org/abs/2609.19442"
    - "Emergence World: Long-Horizon Multi-Agent Stress Testing — arxiv.org/abs/2609.20117"
---

# Evaluation integrity

Three findings about the instrument. A broken instrument does not throw; it returns a
number, and the number is higher than it should be.

## Apply: the builder's checklist

1. **An attacker model has been pointed at every generated rubric**, no instruction but to
   maximise its score, judged against an oracle the rubric cannot see.
2. **Every exploit rate names its oracle.** Only the direction survives swapping it.
3. **Nothing gates on a bare pass-or-fail verdict.** If something does, you have not seen
   the class of wrong answers it accepts.
4. **Your pressure suite scores recognition separately from outcome and publishes a
   realism measurement**, or its nulls cannot be read.
5. **Any unanimous judge panel is calibrated against an outside grader**, or unanimity
   measures agreement, which correlated judges manufacture.

## Delta 1: your exploit rate is a property of your oracle

*Validation: no trial and no consumer report. Bare-arm screen ei-c1, 2026-09-30: partial. The bare subject volunteered hand-written rubric-satisfying-but-wrong answers, so the attack idea is not a delta; it did not automate the attacker, did not name oracle independence as the step teams skip, and did not know the measured rate moves with the oracle. Eval task ei-t1.*

Eleven rubric generators, **every one exploitable**: an attacker optimising against the
rubric scored at or above the honest baseline while violating ground truth on **8 to 26
percent** of an unbiased 150-environment cut, and the best generator still hit **36
percent** on a 45-environment stress cut (claim 476). Rubrics tied to a machine-checkable
certificate were exploited **0 of 45** (claim 479). Then the reporting rule: swapping
**only the oracle** moved the rate across **33.3, 75.6 and 66.7 percent** (claim 477)
while the direction survived, all 15 attacks the primary oracle flagged being flagged by
both alternatives (claim 478).

1. Generate the rubric from the question and its evidence with a neutral prompt.
2. Hand it to an **attacker model whose only instruction is to maximise the rubric
   score**, and score both its answer and an honest baseline. A hand-written adversarial
   answer is not this.
3. Check the attacker's answer against an **oracle independent of the rubric**, the step
   teams skip. Impossible tasks are the cheap oracle: the evidence determines no answer,
   so any confident answer violates the certificate (claim 480).
4. Report the rate **with its oracle**. Only the direction transfers (ours).

## Delta 2: a verdict gate is blind by construction, not by accident

*Validation: no trial and no consumer report. Bare-arm screen ei-c2, 2026-09-30: partial. The bare subject gave mutation testing, an immutable oracle and dense rewards, all of it good; it did not state that verdict-only scoring is provably uninformative on the population a reward signal actually meets, and it reached for a denser verdict rather than a continuous judge. Eval tasks ei-t2, ei-t3.*

A scoring function depending only on a binary verdict scores a faithful candidate and a
verdict-preserving unfaithful one identically, so on a verdict-matched paired set it
reaches an **AUROC of 0.5** (claim 260). A proof, not a measurement, and verdict-matched
pairs are the population a reward signal keeps meeting. Mutation testing says whether your
suite is strong, not what your gate cannot see. The repair is the **renormalised
probability the judge puts on yes against no** instead of its verdict: **0.961 AUROC**,
**0.955** on the 652 rows disjoint from training (claim 261).

1. Mutate each known-correct artifact: flip a relational operator, perturb a constant,
   reverse an implication. Keep only mutants the **checker still accepts** that are
   provably not equivalent, **732 cases at 57 to 43** in the source work (claim 263).
2. Replace the verdict with the judge's renormalised yes-probability as the score.
3. Spend extra attempts by verifier score rather than uniformly: **11.3 points** of
   end-to-end accuracy over the same system with no verifier (claim 262).

## Delta 3: how to score a pressure suite

*Validation: no trial and no consumer report. Bare-arm screen ei-c4, 2026-09-30: partial. The bare subject volunteered multi-turn pressure testing, severity taxonomies, per-slice power and grader validation, so "test under pressure" is not a delta; it did not separate recognition from outcome, did not require a realism measurement, and did not know a per-model safety result fails to compose. Eval task ei-t8.*

Across 22 models, **ordinary user pressure raised rule-violation rates by an average of 65
percent**, and the strongest assistants still misapplied a compliance rule on **6 to 10
percent** of items (claims 559, 560). Not jailbreaking: a persistent user, a hurried
manager, a shortcut. Three scoring rules follow, and these rather than the pressure
testing are the delta.

1. **Score recognition separately from outcome.** Recognising an attack did not imply
   restraint or recovery, so one collapsed number hides which failed (Emergence World).
2. **Measure and publish scenario realism**, 3.21 on a 4-point scale at 0.97 internal
   consistency in the reference suite (claim 561). Without it a null is unreadable: an
   implausible scenario explains one as well as a safe model does (ours). Floor: one
   model-judge realism pass over a sample, humans only where the two disagree.
3. **Never carry a per-model safety result to the system you assembled from those
   models.** The same model behaved differently in a mixed population (Emergence World).

## Caveats

- Rubric exploitation rates come from 169 impossible tasks plus 48 answerable controls,
  built so the oracle is cheap. Not a general failure rate for open-ended tasks.
- The generative-verifier numbers are one domain with a **27B open model and LoRA
  adapters, which is also the floor**: no frontier model is needed in the judge seat.
- Pressure results are 48 multi-turn scenarios across 12 regulated domains plus a few
  simulated worlds. The effects exist and are large; their size in your setting does not
  follow.

## What this file no longer carries

Eight sections cut 2026-09-30: five because the bare subject gave them unprompted, one of
those supplying a floor this file had claimed as its own; two for carrying no magnitude;
and the challenger gate, which moved to `recursive-harness-self-improvement`. Receipts,
with the bare answers and the section names, in
`skills/_validation/results/2026-09-30-bare-arm-differential-screen.md`.
