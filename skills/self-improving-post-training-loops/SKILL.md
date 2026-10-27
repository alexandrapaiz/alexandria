---
name: self-improving-post-training-loops
description: Evidence-backed decision rules for post-training loops where the model's own rollouts, or a teacher extrapolated from them, become the supervision for its next update. Use when you are about to distil from a larger teacher model and need to know whether that teacher's answers are actually right on the prompts you care about, when a self-distillation or on-policy-distillation run destabilizes or collapses, when turning an agent harness's own logs into a training mixture, when designing a reward for long-horizon agent training with no ground truth, or when a closed loop's second iteration is worse than its first. Covers per-prompt teacher gating and its fallback, teacher refresh rate, what to screen out of recorded interactions, gating guidance on the verifier's advantage sign, and per-step credit with no verifier. Distinct from harness-engineering, the inference-time scaffold around frozen weights, and from recursive-harness-self-improvement, where the agent edits its own scaffold and no weights move.
version: 4
status: provisional
provenance:
  extracted: 2026-09-18
  revised: 2026-10-27
  validated: ""
  differential_screen: "not run. This seat has no route to either eval arm: no GROQ_API_KEY reaches the run, and pipeline/budget.py knows no provider that serves the benchmark subject. Both are queued in docs/agents/pending-workflow-changes.md. Every delta below is unscreened, and each Validation tag names what this run expects a bare subject to supply already and what it does not."
  reviews:
    - "none filed yet. The lane is open at reviews/ (ADR-38); see reviews/README.md for what this skill most wants reported."
  revisions:
    - "2026-10-27 (ADR-37 maintenance, ADR-35 the paper wins): the research seat drained the 2026-09-30 reading-queue batch and routed one correction to this file (docs/research/briefs/2026-10-26.md section 9). Both halves were re-verified here against full text before being applied. (1) Delta 5's +15.9 is on AppWorld test-normal, and the split is load-bearing rather than a detail: AppWorld's own paper puts its best agent at 48.8 on test-normal against 30.2 on test-challenge, and test-challenge is the larger split at 417 of 585 test tasks and requires an API from an app the agent never saw (arxiv.org/abs/2407.18901 sections 1 and 3.4). The number now carries that, so nobody reads it as a whole-benchmark result. (2) The caveat said the self-judged variant needed no frontier judge and no verifier. True of the training signal and false of the evaluation, which is programmatic in both benchmark families: AppWorld scores with state-based unit tests, and tau-bench compares the final database state against an annotated goal state (arxiv.org/abs/2406.12045 abstract). DRACO's 97-task banking benchmark is not named in this skill as tau-bench and this run could not verify that it is one, so the caveat says tau-bench grades this family rather than saying this skill rests on tau-bench, and the question is queued for the research seat. The caveat now says which of the two it means, because a reader planning a loop on an unverifiable task would have taken the old wording as a licence. No number changed and no claim is deprecated."
    - "2026-10-26 (ADR-38, the quality bar): 185 lines to 112, five prose sections to five deltas each ending in a numbered procedure with its thresholds named, the checklist moved first, and every number in the file re-read against its paper. `status` moved from `active` to `provisional`: ADR-38 rule 7 earns `active` on a positive differential delta on the benchmark subject, no such delta exists for this skill, and `active` had been standing in for a measurement nobody ran."
    - "2026-10-26 (ADR-35, the paper wins, four corrections): all five papers were re-read in full this run and four statements did not survive. (1) The previous version said the gated teacher 'beat vanilla on-policy distillation across all six single-domain settings'. The paper reports the best distillation score on nine of fourteen benchmark-scale pairs, ties included, which is a weaker result and is now what delta 2 says. (2) NeoHorse-1's macro-average is over ten benchmarks, not eleven. (3) The validation stack before recorded interactions become training data has deduplication and evaluation-overlap screening as its first gate, which the previous version omitted entirely while naming a 'subscene-level labeling' step the read text does not carry. (4) RISE's gain was stated as consistent across four task families; the results read here are mathematical reasoning plus an out-of-domain average, so delta 1 now carries those and no more. All four filed for claim revision in docs/ideas.md; this run had no database and could not identify which claim ids carry them."
    - "2026-09-30 (ADR-38 retrofit, owner directive): per-section Validation tags, an Apply checklist, and caveats that name their floor. No claim, number or prescription changed."
  claims: [30, 31, 32, 33, 116, 117, 118, 119, 120, 141, 142, 143, 144, 96, 97, 98, 99, 39, 40, 41, 42]
  papers:
    - "RISE: Recursive Improvement via Self-Extrapolating Policy Distillation — arxiv.org/abs/2609.05295"
    - "Verify Before You Distill: Prompt-Level Teacher Gating for On-Policy Distillation — arxiv.org/abs/2609.02998"
    - "NeoHorse-1: Towards Recursive Self-Improvement via Agentic Post-Training with Routing Harness — arxiv.org/abs/2609.08183"
    - "FlowBalance: Verifier-Grounded Self-Improvement from On-Policy Reasoning Experience — arxiv.org/abs/2609.03241"
    - "AppWorld: A Controllable World of Apps and People for Benchmarking Interactive Coding Agents (read 2026-10-27 for the test-normal and test-challenge split behind DRACO's numbers) — arxiv.org/abs/2407.18901"
    - "tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains (read 2026-10-27 for what its evaluation actually verifies) — arxiv.org/abs/2406.12045"
    - "DRACO: Fine-Grained Credit Assignment with Dynamic Rubrics for Long-Horizon Agent Training — arxiv.org/abs/2609.04094"
---

# Self-improving post-training loops

Five findings about the loop where the supervision signal comes from the model being supervised. A competent ML engineer already runs supervised fine-tuning and reinforcement learning, already holds out an eval suite disjoint from the mixture, already logs rollouts, and already watches entropy and response length for collapse. None of that is repeated below. What is specific here is that the signal and the thing being trained on it are one system, so the question a standard fine-tune never has to ask is whether this particular supervision can be trusted on this particular prompt, and what runs instead when it cannot. Each delta ends in a procedure with its thresholds named.

## Apply: the builder's checklist

1. **The teacher is rebuilt every iteration and the distillation phase is actually in the loop**, because adopting the extrapolated checkpoint without it recovers about a tenth of the gain (delta 1).
2. **Each prompt is routed on three verifier-scored teacher probes with the gate opening at two of three**, and a different signal trains the prompts the gate rejects (delta 2).
3. **Deduplication and evaluation-overlap screening run before the structural and semantic gates**, because a closed loop feeds its own eval set back into its mixture, and the published loop ran one pass (delta 3).
4. **Self-generated guidance is multiplied by the sign of the verifier's group advantage and switched off when that advantage is zero**, never applied uniformly (delta 4).
5. **Where no verifier exists, rubric criteria are regenerated per group of rollouts, criteria nobody in the group failed are dropped, and each score is redistributed over steps with a length normalisation** (delta 5).
6. **The harness was exhausted first.** These are mechanisms for a loop whose training path is already chosen, and the cheaper fix is usually upstream of the weights.

## Delta 1: the extrapolated teacher is not the gain, the distillation against it is

*Validation: no trial, no consumer report, no bare-arm screen. Eval task sipt-t1. A bare subject will say "distil the RL checkpoint into dense supervision", which is the plan this delta rejects. It is unlikely to supply the ablation number, which is the whole argument.*

RISE builds a teacher out of the model's own reinforcement-learning trajectory rather than out of a privileged external model, extrapolating in weight space or logit space with a coefficient above one, and converts sparse outcome rewards into dense per-token supervision (RISE). The paper's own ablation is the reason to care, and it points the opposite way from intuition: adopting the extrapolated checkpoint directly, with no distillation phase, moves Math Avg from **60.0 to 60.3** on Qwen3-8B and **45.4 to 45.6** on Qwen3-1.7B, against **+2.7** and **+4.8** for the full loop (RISE). The extrapolation is a direction, not a model. Out-of-domain average held at 70.6 to **72.0** on the 8B, so the loop did not buy its gain by narrowing.

1. Refresh the teacher every iteration as the student improves. A teacher built once and reused is one-time compression wearing a loop's name, and the ablation above is roughly what it is worth.
2. Keep the outcome reward in the loop beside the distillation loss. The reward grounds the extrapolation and the extrapolated teacher refines the token-level decisions.
3. Decay the extrapolation coefficient on a schedule and hold an exponential-moving-average anchor. The paper offers these as empirical robustness and states plainly that principled detection of when extrapolation stops being meaningful is open (RISE).
4. Do not run this on a reward you have not audited for hacking. Extrapolation amplifies whatever direction the reward points, including a spurious one (RISE).

## Delta 2: gate the teacher per prompt at two probes of three, and bank the utilisation before the accuracy

*Validation: no trial, no consumer report, no bare-arm screen. Eval tasks sipt-t2, sipt-t3 and sipt-t7. Best-evidenced delta here, and the one this run corrected downward. A bare subject will say "check teacher quality". It is unlikely to supply per-prompt routing rather than per-corpus filtering, the fallback arm, or that the compute win is the larger and more certain half.*

Standard on-policy distillation applies the teacher uniformly, so a confidently wrong teacher supplies a confidently wrong update. Estimate reliability per prompt from a small set of verifier-scored teacher probes and route on it, dense distillation when the check passes and verifier-grounded reinforcement learning when it does not (Verify Before You Distill). The accuracy result is real and it is narrower than this skill previously claimed: the gated method took the best distillation score on **nine of fourteen** benchmark-scale pairs, ties included, across two scales and three domains (Verify Before You Distill). The compute result is cleaner. Teacher-node GPU utilisation went from **9.8 percent to 78.9 percent** in the 4B single-domain run, because idle teacher capacity gets spent once the gate decides which prompts are worth it (Verify Before You Distill).

1. Run **three** probes per prompt and open the gate at **two**, which is the paper's main-experiment setting of three probes at a two-thirds threshold (Verify Before You Distill).
2. Build the fallback arm before the gate, not after. A gate with nothing on its closed branch distils anyway from a teacher it has just failed, which is worse than not gating.
3. Judge the gate on teacher utilisation first. That number moved by a factor of eight and the accuracy numbers moved by a benchmark or two, so utilisation is where the gate pays reliably (ours, not the paper's).
4. Stop at the method's edge: it needs an automatic verifier and routes binarily, so an open-ended task has no gate here (Verify Before You Distill).

## Delta 3: screen the eval set out of the mixture before anything else, and treat one loop pass as one loop pass

*Validation: no trial, no consumer report, no bare-arm screen. Eval task sipt-t4. One production system, the narrowest evidence in this file. A bare subject will say "clean your training data". It is unlikely to supply that decontamination is gate one specifically because the loop is closed, or that the published result is a single iteration.*

Converting evaluation feedback into the next training mixture is what makes a mixture a loop: results are aggregated into a model-deficiency profile and that profile shifts the next mixture toward the underperforming regions (NeoHorse-1). Recorded harness interactions, with interleaved reasoning, tool calls and harness context, become training examples once they clear three gates in order (NeoHorse-1). Macro-average across **ten** benchmarks rose **58.94 to 64.87** at 4B and **65.60 to 69.04** at 9B (NeoHorse-1).

1. **Deduplicate and decontaminate first**: exact and near-duplicate removal, then evaluation-overlap screening. This gate is first because the loop writes its own next mixture, so an eval item that leaks in is scored by the same system that then trains on it.
2. **Structural validation**: rule-based checks for request and response presence, causal event order, and closure of every tool-call and result pair, each record landing as internally complete, partially recoverable, or quarantined.
3. **Semantic evaluation on six dimensions**: goal attainment, instruction adherence, tool use, evidence consistency, error recovery, termination, each rated pass, warn, fail or not evaluated. No numeric acceptance threshold is published, so set yours and record it.
4. Read the headline as one pass. The paper evaluates **a single pass** of the evaluate, select and update loop, so sustained multi-iteration gain is unvalidated, and a second iteration that regresses is inside rather than outside the published evidence (NeoHorse-1).

## Delta 4: multiply self-guidance by the advantage sign, and switch it off at zero

*Validation: no trial, no consumer report, no bare-arm screen. Eval task sipt-t5. A bare subject will say "weight by advantage". It is unlikely to supply the third branch at zero advantage, which is the one that stops a no-preference group from training on confidence alone.*

A self-guidance score, meaning an aggregated token-level log-probability gain, is a measure of the model's own confidence, so applying it uniformly rewards a trajectory for being confidently wrong. FlowBalance gates it on the sign of the verifier-derived group advantage instead: positive advantage retains the guidance, negative advantage reverses it so a confidently scored failure cannot become self-reinforcing supervision, and zero advantage disables the dense branch entirely (FlowBalance). There is no tunable threshold here, only the sign. The calibrated signal then replaces a separate token-level imitation loss through an energy reweighting fitted with one log-partition estimate per rollout group (FlowBalance).

1. Compute the group advantage from the verifier first, then apply guidance, never the other way round.
2. Implement all three branches. Two branches and no zero case is the common partial implementation and it trains on confidence wherever the group shows no outcome preference.
3. Expect the gain to be small and the stability to be the point: **+1.67** average at Qwen3-4B and **+1.98** at Qwen3-8B over FlowRL on four mathematics benchmarks, 0.5 validation accuracy on AIME24 in about **100** steps against roughly **143** for standard group-relative policy optimisation, and near-peak accuracy held through **400** steps where the baseline degrades after about **180** (FlowBalance).
4. Watch response length as a symptom and not as a cause. The paper is explicit that the length comparison diagnoses a correlated failure without establishing causation (FlowBalance).

## Delta 5: regenerate the rubric per group, drop what nobody failed, and normalise credit by step length

*Validation: no trial, no consumer report, no bare-arm screen. Eval tasks sipt-t6 and sipt-t9. A bare subject will say "write a rubric and have a strong model grade the steps". It is unlikely to supply regeneration per group, discriminative dropout, the length normalisation, or that the cheap self-judge was the best out-of-domain arm.*

A fixed rubric grades a moving policy against a standard it has already passed. DRACO generates criteria during training instead: a judge proposes them from the task instruction, extends them once per sampled rollout with the sub-goals that rollout reveals, and merges the proposals with duplicates removed (DRACO). Each rubric's score is then redistributed over the steps responsible for it by a closed-form formula with no learned attribution module, and the formula divides by the step's token count so a step's credit depends on its quality weight rather than on its length (DRACO). On AppWorld test-normal this took task-goal completion **69.4 to 85.3** percent, which is **+15.9** over the base model and **+5.3** over an outcome-reward baseline, with scenario-goal completion **41.1 to 70.6** (DRACO). **Read that against the split and not against AppWorld.** Test-normal is the easier of the two test sets and the smaller one, 168 tasks against test-challenge's 417, and AppWorld's own best agent scores 48.8 on normal against 30.2 on challenge, so a gain measured on normal is not a gain on the benchmark (AppWorld, arxiv.org/abs/2407.18901).

1. Regenerate per group, at **G = 6** rollouts per task per training step, not per run and not per epoch.
2. Apply discriminative dropout: delete any criterion no member of the group failed. It carries no signal and it inflates every score equally. Expect about **5.1** surviving criteria per rollout with a frontier judge and **3.8** with the model judging itself (DRACO).
3. Redistribute with the length normalisation in place. Without it the longest step absorbs the credit, which is the failure a per-step scheme exists to avoid.
4. Try the self-judge before buying a frontier one. Out of domain on a 97-task banking benchmark the base model scored **15.8** percent, the frontier-judged variant **20.4**, and the self-judged variant **21.1**, which was the best arm (DRACO).
5. Do not read end-task gain as proof the credit landed correctly. The paper says in its own words that a judge which is internally consistent can still be systematically wrong, and that end-task validation does not establish that credit reached the right steps (DRACO).

The principle under deltas 2 and 5 generalises past training, and it is the one sentence worth carrying out of this file: before letting anything grade or teach itself, measure whether that signal can be trusted on this case, and build the branch that runs when it cannot (ours, not the papers').

## Caveats

- **This skill is unmeasured.** No delta carries a differential number and no bare-arm screen has run, because this seat has no route to either eval arm. `status: provisional` says exactly that, and it replaced `status: active` on 2026-10-26 for this reason.
- **Scales top out at 35B students** (Verify Before You Distill), and nothing here is verified at frontier scale. The floor is the useful half: the gate was measured at 4B, and the 4B single-domain run is where the utilisation gain from 9.8 to 78.9 percent was recorded, so one small student is enough to see whether the gate pays.
- **Domains are mathematics, code, instruction following and long-horizon agent benchmarks** (AppWorld, a 97-task banking benchmark, NeoHorse-1's ten-benchmark suite). FlowBalance's authors state that generalisation beyond mathematical reasoning is open. Nothing here covers open-ended dialogue or safety tuning.
- **The harness-log pipeline is one production routing-harness system over one loop pass** (NeoHorse-1), and its gates are not shown to transfer to a harness built differently. The floor it does establish is the order of the gates, which costs nothing to copy: decontaminate, then validate structure, then evaluate semantics, and mix nothing in that has not cleared all three.
- **DRACO's primary numbers come from one frozen judge** (GPT-5.4 at temperature 0.1), with no independent signal that the generated criteria describe the task faithfully. The floor is cheap and it is the finding: the self-judged variant needed no frontier judge and no verifier and was the best out-of-domain arm. "No verifier" is about the training signal only, and not about the task. AppWorld scores with state-based unit tests, and the tool-agent benchmarks of this family grade by comparing the final database state against an annotated goal state (tau-bench, arxiv.org/abs/2406.12045). So nothing in this delta says a loop can be trained on a task whose outcome nobody can check.
- **This is a training-time complement to `harness-engineering`, not a substitute.** When an agent underperforms, exhaust the inference-time scaffold first, and reach here only once fine-tuning is the chosen path.
- Every delta is revised or withdrawn if the claim behind it is contradicted. The claim ids in the provenance block are the addresses a contradiction lands on, and four statements in the previous version are already known wrong: they are listed in the 2026-10-26 revision note and filed in `docs/ideas.md`.
