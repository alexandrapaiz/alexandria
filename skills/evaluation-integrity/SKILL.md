---
name: evaluation-integrity
description: Four measured findings about instruments a model produced, which a strong model does not give unprompted. The subject is the rubric, the judge and the verdict, not the system they score. Use when a model-written rubric is about to become a reward signal or a gate; when a pass-or-fail verdict from a checker, a compiler or a test suite stands in for correctness; when deciding how many independent judgments an accept should require and where they should come from; when a single-turn evaluation is being read as a reliability result; or when reporting an exploit rate, an absence of failures, or a benchmark score you intend someone else to trust.
version: 4
status: active
provenance:
  extracted: 2026-09-24
  revised: 2026-09-30
  validated: ""
  differential_screen: "2026-09-30, bare-arm pre-screen on the benchmark-class subject (skills/_validation/results/2026-09-30-bare-arm-differential-screen.md). 3 of 4 first-round candidates qualified as partials; ei-c3 passed bare and its section was cut. Delta 3 was screened in the second round."
  reviews:
    - "none filed yet. The lane is open at reviews/ (ADR-38); see reviews/README.md for what this skill most wants reported."
  revisions:
    - "2026-09-30 (ADR-38, the quality bar): 467 lines to under 120, eleven sections to four. Cut the noise-band section because the bare subject gave the band, the five-to-ten repeat floor, the leakage read and the multiplicity correction unprompted (ei-c3), which also retired a floor this file had marked as ours. Cut the shortcut-channel section because the same bare answer volunteered the read-only checkout, the network block and the config diff. Cut the judge-collapse section because the bare answer's grader-noise re-grading is the transferable half. Cut partial monitoring (claims 269, 272, 273) and the benchmark-defect profile (claims 237-240) because neither carries a magnitude for the effect it asserts, which ADR-38 requires; both are filed for the research seat to price. The certification protocol's challenger gate (claims 286, 288, 290) moved to recursive-harness-self-improvement, where the loop that needs it lives, rather than being carried twice."
  claims: [476, 477, 478, 479, 480, 260, 261, 262, 263, 228, 557, 559, 560, 561]
  papers:
    - "ImpossibleRubrics: Stress-Testing Generated Rubrics — arxiv.org/abs/2609.12534"
    - "Beyond Solver Verdicts: Generative Verification for Formalization — arxiv.org/abs/2609.13147"
    - "An Open Recipe for IMO Gold — arxiv.org/abs/2609.16560"
    - "PACT: Pressure-Tested Compliance for Enterprise Assistants — arxiv.org/abs/2609.19442"
    - "Emergence World: Long-Horizon Multi-Agent Stress Testing — arxiv.org/abs/2609.20117"
---

# Evaluation integrity

Four findings about the instrument. A broken instrument does not throw. It returns a
number, and the number is higher than it should be.

## Apply: the builder's checklist

1. **An attacker model has been pointed at every generated rubric** with no instruction
   but to maximise its score, and judged against an oracle the rubric cannot see (delta
   1).
2. **Every exploit rate you report names the oracle that produced it**, because the rate
   is a property of the oracle and only the direction survives swapping it (delta 1).
3. **Nothing gates on a bare pass-or-fail verdict.** If something does, you have not yet
   seen the class of wrong answers it accepts (delta 2).
4. **Where a false accept is expensive, the accept rule is unanimity across
   independently trained checkpoints**, malformed judgments discarded and not counted,
   with the panel calibrated against an outside grader (delta 3).
5. **Your pressure suite scores recognition separately from outcome and carries a
   realism measurement**, or its null results cannot be interpreted (delta 4).

## Delta 1: your exploit rate is a property of your oracle

*Validation: no trial and no consumer report. Bare-arm screen ei-c1, 2026-09-30: partial. The bare subject volunteered hand-written rubric-satisfying-but-wrong answers, so the attack idea is not a delta; it did not automate the attacker, did not name the oracle-independence requirement as the step teams skip, and did not know the rate moves with the oracle. Eval task ei-t1.*

Eleven rubric generators were tested and **every one was exploitable**: an attacker
model optimising directly against the rubric scored at or above the honest baseline
while violating ground truth on **8 to 26 percent** of an unbiased 150-environment cut,
and the lowest exploit rate any generator reached on a 45-environment stress cut was
**36 percent** (ImpossibleRubrics, claim 476). Rubrics written to be faithful to a
machine-checkable certificate were exploited **zero times out of 45** on that same cut
(claim 479).

Then the part that changes how you report: holding the rubrics, the attack responses and
the judge scores fixed and swapping **only the oracle** moved the measured exploitation
rate across **33.3, 75.6 and 66.7 percent** (claim 477). The direction survived the
swap, since all 15 attacks the primary oracle flagged were flagged by both alternatives
(claim 478). So "this rubric is exploitable" holds across oracles and the number
attached to it does not.

1. Generate the rubric from the question and its evidence with a neutral prompt, exactly
   as production would.
2. Hand it to an **attacker model whose only instruction is to maximise the rubric
   score**. Not a hand-written adversarial answer; the automated attacker is what found
   the 8 to 26 percent.
3. Score an honest baseline answer and the attacker's answer against that rubric.
4. Check the attacker's answer against an **oracle independent of the rubric**. This is
   the step teams skip, and without it the test cannot separate a good answer from a
   well-dressed one. Impossible tasks are the cheap source: the evidence determines no
   answer, so any confident answer violates the certificate (claim 480).
5. Report the rate **with the oracle that produced it**, and treat only the direction as
   transferable (ours, not the paper's).

## Delta 2: a verdict gate is blind by construction, not by accident

*Validation: no trial and no consumer report. Bare-arm screen ei-c2, 2026-09-30: partial. The bare subject gave mutation testing, an immutable oracle and dense rewards, all of it good; it did not state that verdict-only scoring is provably uninformative on the population a reward signal actually meets, and it reached for a denser verdict rather than a continuous judge. Eval tasks ei-t2, ei-t3.*

Any scoring function depending only on a binary verdict assigns identical scores to a
faithful candidate and to one that is unfaithful but preserves the verdict, so on a
paired set matched for verdict it scores an **AUROC of 0.5** (Beyond Solver Verdicts,
claim 260). This is a proof, not a measurement. The compiler passing, the suite going
green and the solver returning sat are all this kind of signal, and verdict-matched
pairs are exactly the population a reward signal keeps meeting.

The repair is a continuous score from a model reading the candidate against the original
intent. Scoring the **renormalised probability the judge puts on yes against no**,
rather than taking its verdict, reached **0.961 AUROC**, holding at **0.955** on the 652
rows whose source texts were disjoint from training (claim 261). Quote the disjoint
number.

1. Take each known-correct artifact and mutate it systematically: flip a relational
   operator, perturb a constant, reverse an implication.
2. Keep only mutants the **checker still accepts** and that are provably not equivalent.
   In the source work this produced **732 cases at a 57 to 43 split** (claim 263). These
   are the answers your gate cannot see.
3. Replace the verdict with the judge's renormalised yes-probability as the score.
4. Spend extra attempts by verifier score rather than uniformly: this improved end-to-
   end answer accuracy by **11.3 points** over the same system with no verifier (claim
   262).

## Delta 3: unanimity, and the three parts everybody drops

*Validation: no trial and no consumer report. Bare-arm screen ei-c5, 2026-09-30, second round: see the screen file for the verdict and what the bare subject did and did not give. Three of the four portable parts below are marked ours and carry no evidence beyond the one competition system. Eval task ei-t7.*

For accepting proofs during a competition search, the rule was unanimity across **16
independent judgments, 8 from the reinforcement-learning checkpoint and 8 from the
supervised one**, any missing or unparsable judgment **discarded rather than counted**,
and acceptance only when all 16 parsed scores were 1 (An Open Recipe for IMO Gold, claim
228). The panel's scores closely tracked an independent post-hoc model jury, which is
the evidence that it measured what an outside grader would.

1. Take independence from **different checkpoints**, not more samples from one. Sixteen
   samples from one model share its blind spots.
2. **Discard an unparsable judgment. Never count it as a pass.** The difference shows up
   exactly on the hard cases that make judges emit malformed output.
3. Calibrate the panel against an outside grader before trusting it, or unanimity
   measures agreement, which correlated judges manufacture.
4. Use it only where a wrong accept is expensive and a rejected candidate can be
   resubmitted. It buys precision with recall, so it is the wrong rule for ranking.

## Delta 4: how to score a pressure suite

*Validation: no trial and no consumer report. Bare-arm screen ei-c4, 2026-09-30: partial. The bare subject volunteered multi-turn pressure testing, severity taxonomies, per-slice power and grader validation, so "test under pressure" is not a delta; it did not separate recognition from outcome, did not require a realism measurement, and did not know that a per-model safety result fails to compose. Eval task ei-t8.*

Across 22 models on a rule-following benchmark, **ordinary user pressure raised rule-
violation rates by an average of 65 percent**, and the strongest assistants still
misapplied a compliance rule on **6 to 10 percent** of items (PACT, claims 559, 560).
The pressure was not jailbreaking: a persistent user, a hurried manager, an attractive
shortcut.

Three scoring rules, and they are the delta rather than the pressure itself:

1. **Score recognition separately from outcome.** Recognising an attack did not imply
   restraint or recovery, so collapsing them into one number hides which one failed
   (Emergence World).
2. **Measure the realism of your scenarios and publish it.** The reference suite
   averaged 3.21 on a 4-point scale with 0.97 internal consistency (claim 561, 273's
   paper). Without it a null is unreadable, because an implausible scenario explains a
   null as well as a safe model does (ours, not the paper's). Floor: a model-judge
   realism score over a sample, one pass, with human annotation only where they
   disagree.
3. **Do not carry a per-model safety result to the system you assembled.** The same
   model behaved differently in a mixed population than in a homogeneous one, with
   different failure modes (Emergence World).

## Caveats

- Rubric exploitation rates come from 169 impossible tasks plus 48 answerable controls,
  built so the oracle is cheap. They are not a general rubric-failure rate for ordinary
  open-ended tasks.
- The AUROC 0.5 result is a proof about verdict-matched pairs, not a claim that binary
  checkers are uninformative. On unmatched data a verdict carries real signal.
- The generative-verifier numbers are one domain with a **27B open model and LoRA
  adapters, which is the floor**: nothing here asks for a frontier model in the judge
  seat. Treat 0.961 as local.
- The unanimous panel is competition mathematics, one model family, where a proof is
  checkable and a wrong accept costs a problem. **The floor is two independently trained
  checkpoints and one outside-jury calibration, not the count of sixteen.**
- Pressure results are 48 multi-turn scenarios across 12 regulated domains, plus a small
  number of simulated worlds. They establish that the effects exist and are large, not
  their size in your setting.

## What this file no longer carries

Seven sections were cut on 2026-09-30. The noise band, the four shortcut channels and
judge-variance monitoring went because the bare subject gave them unprompted, in one
case supplying a floor this file had claimed as its own. Partial monitoring and the
benchmark-defect profile went because neither carries a magnitude for the effect it
asserts. The challenger gate moved to `recursive-harness-self-improvement`. Receipts,
with the bare answers, in `skills/_validation/results/2026-09-30-bare-arm-differential-
screen.md`.
