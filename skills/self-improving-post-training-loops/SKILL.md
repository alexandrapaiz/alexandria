---
name: self-improving-post-training-loops
description: Three measured findings about training loops where the model's own output becomes its next supervision signal, which a strong model does not give unprompted. Use when planning on-policy or dense distillation from a teacher whose reliability varies by prompt; when assigning credit on a long-horizon agent task that has no verifier and no ground-truth labels; or when a self-generated guidance signal such as a token-level log-probability gain is shaping the training target and training destabilises or response length collapses. Distinct from harness-engineering, which covers the inference-time scaffold around a frozen model.
version: 3
status: active
provenance:
  extracted: 2026-09-18
  revised: 2026-09-30
  differential_screen: "2026-09-30, bare-arm pre-screen on the benchmark-class subject (skills/_validation/results/2026-09-30-bare-arm-differential-screen.md). 3 of 4 candidates qualified, two of them outright bare failures, which makes this the strongest-scoring skill in the library on the screen. sipt-c2 passed bare and its section was cut."
  validated: ""
  reviews:
    - "none filed yet. The lane is open at reviews/ (ADR-38); see reviews/README.md for what this skill most wants reported."
  revisions:
    - "2026-09-30 (ADR-38, the quality bar): 185 lines to under 120, five sections to three. Cut on measurement: refresh-the-teacher-every-iteration (sipt-c2, where the bare subject volunteered the iterated RLVR-snapshot-distill-back loop, added a stop rule this file lacked, and diagnosed entropy collapse as the likely cause of the plateau). Cut as the narrowest evidence in the file, one production system: capability-guided data selection and the harness-log-to-training-data pipeline (claims 141-144). Claims 30-33 leave with the refresh section."
  claims: [116, 117, 118, 119, 120, 39, 40, 41, 42, 96, 97, 98, 99]
  papers:
    - "Verify Before You Distill: Prompt-Level Teacher Gating for On-Policy Distillation — arxiv.org/abs/2609.02998"
    - "DRACO: Fine-Grained Credit Assignment with Dynamic Rubrics for Long-Horizon Agent Training — arxiv.org/abs/2609.04094"
    - "FlowBalance: Verifier-Grounded Self-Improvement from On-Policy Reasoning Experience — arxiv.org/abs/2609.03241"
---

# Self-improving post-training loops

Three findings for the loop where supervision is self-referential, all three about not
trusting a signal uniformly.

## Apply: the builder's checklist

1. **Teacher reliability is estimated per prompt** from verifier-scored probes, and it
   decides which prompts get dense distillation at all (delta 1).
2. **When the gate says no, a different signal takes over**, verifier-grounded GRPO, not
   distilling anyway from a teacher that just failed its check (delta 1).
3. **Where no verifier exists, the rubrics regenerate during training** and each score is
   redistributed onto the steps responsible for it (delta 2).
4. **Any self-generated guidance signal is conditioned on the verifier-derived advantage
   sign**: kept where positive, **reversed** where negative, off where the rollout group
   shows no preference (delta 3).

## Delta 1: gate the teacher per prompt, and it pays in compute as well as accuracy

*Validation: no trial and no consumer report. Bare-arm screen sipt-c1, 2026-09-30: partial. The bare subject gave a strong distillation recipe and did filter prompts to the frontier by **student** pass rate, which is not this: the gate here is on the **teacher's** reliability, because a confidently wrong teacher on a given prompt is worse than no teacher on it. It also did not have the utilisation number. Eval tasks sipt-t2, sipt-t3.*

Estimate the teacher's reliability on each prompt from a small set of **verifier-scored
teacher probes**, and route each prompt on that estimate: dense distillation when the
check passes, **verifier-grounded GRPO when it does not**, since a confidently wrong
teacher gives misleading updates a fallback signal avoids (claims 119, 120).

The gate beat vanilla on-policy distillation in **all six single-domain settings** and on
multi-domain benchmarks, at **both 4B and 35B** scale (claims 116, 117). It is also a
compute win: deciding which prompts need the teacher raised teacher-node GPU utilisation
from **9.8 to 78.9 percent** in one 4B run, because idle teacher capacity in vanilla
asynchronous distillation gets used once the gate decides what is worth it (claim 118).

1. Probe the teacher on a small verifier-scored sample per prompt cluster.
2. Route dense distillation only to prompts that clear the check.
3. Send the rest to verifier-grounded GRPO. Never to the teacher anyway.
4. Watch teacher-node utilisation as the cheap confirmation. **Floor is 4B**: the gain was
   measured there, so a small student is enough to see whether the gate pays.

## Delta 2: without a verifier, the rubric has to move while the policy moves

*Validation: no trial and no consumer report. Bare-arm screen sipt-c3, 2026-09-30: **fail**. Asked how to assign credit with no verifier and no labels, the bare subject built a fixed rubric calibrated against human labels and reached for branching value estimates for per-step credit. A fixed rubric against a moving policy is the specific failure this delta names, and it recommended one. Eval task sipt-t6.*

Generate rubrics **dynamically during training** so the criteria track the policy's
evolving capability instead of standing still against a moving target (claim 39), then
redistribute each rubric's score over the steps responsible for it through a
**closed-form formula with no learned attribution module** (claim 40). On AppWorld this
gained **15.9 points over the base model and 5.3 over GRPO trained with a sparse
ground-truth reward**, and generalised out of domain to Tau-Bench **without a frontier
judge and without any verifier** (claims 41, 42).

1. Regenerate the rubric on a schedule tied to policy updates, not once at the start.
2. Score the trajectory against the current rubric.
3. Redistribute each criterion's score onto the steps responsible for it by closed form.
   **Do not train an attribution module**; the measured result does not need one.
4. **Floor: no frontier judge and no verifier.** The out-of-domain transfer was obtained
   without either, so this is the cheap option, not the expensive one.

## Delta 3: calibrate self-guidance by advantage sign, and reverse it when negative

*Validation: no trial and no consumer report. Bare-arm screen sipt-c4, 2026-09-30: **fail**. Given an unstable log-probability-gain signal and collapsing length, the bare subject fixed the aggregator, winsorised, normalised within group, stratified by length and mixed roughly 0.7 verifiable reward with 0.3 self-guidance. All reasonable, and the mix applies the guidance **uniformly**, which is what this delta says not to do. Eval task sipt-t5.*

Calibrate a self-guidance score against the verifier-derived group advantage rather than
trusting it everywhere: **retain the guidance on positive-advantage trajectories, reverse
it on negative-advantage trajectories, and disable it entirely when the rollout group
shows no outcome preference** (claim 97). The reversal is the counterintuitive part and
the part a uniform mixing weight cannot express.

It can also replace a separate token-level imitation loss, by reweighting a reference
policy with an exponential energy function and fitting the normalised target with one
log-partition estimate per rollout group through trajectory balance (claims 96, 98). On
mathematical reasoning it beat FlowRL at two scales while training faster, staying more
stable, **avoiding response-length collapse**, and showing more strategy diversity (99).

1. Compute the group advantage from the verifier over the rollout group.
2. Advantage positive: keep the guidance as is.
3. Advantage negative: **reverse its sign**. Not downweight.
4. Group shows no outcome preference: switch the guidance off for that group.
5. Log entropy, response length and correct-strategy diversity every iteration, on a
   held-out set disjoint from the mixture. And exhaust the harness first: this file is
   for a loop whose training path is already chosen.

## Caveats

- Scales top out at 35B students and no paper here reports frontier-lab scale, so the gate
  and the calibration are unverified there. The **floor is low, which is the useful half**:
  the gate was measured at 4B as well as 35B.
- Domain coverage is math reasoning, STEM, code generation and long-horizon agent
  benchmarks. Nothing covers open-ended dialogue or safety tuning.
- Delta 3's numbers are against one named baseline at two scales on mathematical reasoning.
  The sign rule transfers; the margin does not.

## What this file no longer carries

Two sections cut 2026-09-30. Refresh-the-teacher went because the bare subject volunteered
the iterated snapshot-and-distill-back loop, added a stop rule this file lacked, and named
entropy collapse as the likely plateau cause. The capability-guided data mixture went as
the narrowest evidence here, one production system. Receipts, with the bare answers, in
`skills/_validation/results/2026-09-30-bare-arm-differential-screen.md`.
