# The RLVR cluster, papers three and four: read in full, and the cluster's question is not the one it was ranked on

Research seat, 2026-11-02. Continues the drain that PR #760 started in
`docs/research/reading-queue.md` lines 285-326, the chair's RLVR batch of
2026-10-05. #760 measured the batch, found a six-paper cluster carrying 21 of
its 32 citations, and read the first two of the six in full. This note reads
the third and the fourth, which are the two #760 named as the ones that would
settle the cluster's question, and records what settling it actually did.

Both read with `python3 tools/read_paper.py`, exit 0, full text off
`arxiv.org/html` in both cases. Section and table numbers are given against
every number below so each can be checked rather than taken.

## Why these two and not the lane's other options

The research lane on the board had nothing to continue: zero cards in Backlog,
This sprint and In progress, and the single card in Review is #760's own, which
is awaiting a merge rather than more work. So the charter's standing first duty
applies, which is the reading queue, and inside the queue #760 had already
ranked the lines and published the reading order. Papers three and four in that
order are `2609.28385` and `2609.35259`. Taking the next two in a published
ranking is the cheapest honest thing a second run can do, and it is also the
only way the ranking gets tested.

## `arxiv:2609.28385` -- When and Where to Trust the Teacher (UECR-GRPO)

https://arxiv.org/abs/2609.28385 -- Zhang, Yang, Huang, Liu, Huang (Shanghai
Jiao Tong, Zhejiang), v1 of 2026-09-23, arXiv perpetual non-exclusive license.
Read as full text, 78,084 characters.

#760 queued this one as the strongest counterparty to `2609.04108`'s
sequential result, "so the sequential result is read against its strongest
counterparty rather than against the weakest." **It is not a counterparty. The
two papers never met**, and that is the first thing the reading establishes:

```bash
grep -c "2609.04108\|Sequential Beats" 28385.txt    # 0
grep -ci "sequential\|two-stage\|stage\|cold start" 28385.txt    # 0
```

The words "sequential", "two-stage", "stage" and "cold start" do not occur in
the paper at all. Its baselines are Vanilla GRPO, Vanilla PG-OPD, a naive sum
of the two losses, Distilled RL and an aligned ATOD (section 5.1) -- five
single-update methods and no staged one. The newest work in its bibliography is
`arXiv:2607.17247`, so its literature cutoff precedes both of the batch's
most-cited papers, which are from 2026-09-03. **A cluster assembled by subject
match produced an opposition that does not exist in either text.**

What the paper does establish, with where it is measured:

1. **The method's margin over the best existing method is under one point, at
   both scales.** Table 2, Avg@12 over five contests (AIME 2024 and 2025, AMC
   2023, HMMT February and November 2025). Qwen3-1.7B student: UECR-GRPO 17.21
   against ATOD-aligned 16.32, a lead of 0.89. Qwen3-4B student: 65.09 against
   Distilled RL 64.53, a lead of 0.56. Both averages reproduce from the
   published per-benchmark cells to the second decimal.
2. **The aggregate win is not a win everywhere, and the paper says so
   itself.** At 4B it trails the best baseline on three of the five benchmarks
   (AIME25 by 0.56, AMC23 by 0.14, HMMT25-Nov by 0.56) and leads on two, and
   section 5.2 states plainly that "the aggregate gain does not imply uniform
   improvement." At 1.7B it leads on four and loses HMMT25-Nov by 0.84.
3. **No uncertainty is attached to any of it.** Searched for and absent:
   "seed" appears five times and every one is inside an offline diagnostic, not
   the training comparison; "significan" appears once, in an appendix sentence
   explaining that a reported quantity is "rather than a token-level
   significance test"; "error bar" does not appear. Table 2 is one training run
   per method per scale, evaluated under one fixed decoding setup. **So the
   sub-point margins have no measured dispersion to be read against.**
4. **The ablation gaps are large and are on a different scale than the
   headline.** Table 3: trajectory construction alone moves the three-benchmark
   average from 17.22 (verifier reward only) to 20.28 (joint normalisation),
   and the full method reaches 25.62. That is an 8.4-point internal gap against
   its own no-teacher arm, next to a 0.89-point external gap against the best
   published method. The two numbers are not comparable -- Table 3 averages
   three benchmarks and Table 2 averages five -- and the paper does not invite
   the comparison, but a reader who takes 25.62 as the headline has taken a
   three-benchmark ablation average for a result.
5. **The honest half, which is the part worth borrowing.** Every offline
   diagnostic in the paper carries real statistics: 95% prompt-cluster
   bootstrap intervals with 2,000 and 10,000 replicates, 100 within-response
   entropy shuffles as a control that the signal beats, 451 mixed groups and
   22,811 response pairs in the ordering audit. And the paper labels its own
   limits in its own voice: the localisation result "establishes the intended
   localization behavior rather than a causal accuracy gain", and the sweep
   finding is "an empirical observation on held-out rollouts, not a guarantee."
   **The rigour is on the mechanism and not on the comparison**, which is the
   opposite of the usual failure and is worth naming as such.
6. **One result the paper reports and does not read.** On HMMT25-Nov at 1.7B,
   every teacher-assisted method scores below plain GRPO: 5.28 for Vanilla
   GRPO against 4.72, 3.89, 4.17, 3.33 and 4.44 for PG-OPD, the naive sum,
   Distilled RL, ATOD and UECR-GRPO. Five methods, one direction. The paper
   mentions only that vanilla GRPO "leads on HMMT25-Nov by 0.84 points." At 4B
   the inversion does not appear. A benchmark on which the whole family of
   teacher-assisted methods is worse than the method they improve on is the
   kind of fact a builder wants, and it is one sentence away from being made.

Scope, so nothing above is over-read: Qwen3 only, both scales, non-thinking
mode, DeepMath-103K prompts, frozen teachers one size up, `G = 8` responses per
prompt, 515 and 160 training steps.

## `arxiv:2609.35259` -- On-Policy or Off-Policy Learning? A Systematic Study of Distillation Dynamics

https://arxiv.org/abs/2609.35259 -- Piskorz, Berthon, van der Schaar
(Cambridge), v1 of 2026-09-28, CC BY 4.0. Read as full text, 164,422
characters.

This is the controlled study, and it is the paper that changes what a builder
should do. It holds the pipeline fixed and varies three things independently
that the literature usually varies together: rollout policy (student-generated
or teacher-generated), token-level KL direction (forward or reverse), and
learning rate. Llama-3.1-8B into Llama-3.2-1B on medical, scientific and
arithmetic reasoning, with Qwen2.5-7B into Qwen2.5-1.5B replicated in an
appendix. **Three seeds per configuration, SEM error bars on every figure**
(section 4.1).

1. **On-policy rollouts have no consistent advantage on any of the three
   benefits claimed for them.** Section 4.2: best mean held-out accuracy 72%
   on-policy against 73% off-policy. Out-of-distribution performance moves by
   at most 1.3 points between learning rates at the low rate and drops 11.2 to
   14.0 points at the high one, so forgetting tracks the learning rate and not
   the rollout policy. Update sparsity is 85.3-89.6% at the low rate against
   51.9-60.0% at the high one, and off-policy produces updates at least as
   sparse as on-policy **in every matched comparison**.
2. **KL direction is the variable that moves task accuracy.** Forward KL holds
   71-73% across every rollout policy and learning rate; reverse KL spans 35%
   to 72% and is the sensitive one. Sections 5.1 and 5.2 explain it rather than
   reporting it: the forward-KL logit gradient is `pi_S(v) - pi_T(v)`, bounded
   in `[-1, 1]`, so its update difference between two rollout policies is
   bounded linearly by the total-variation distance between the prefix
   distributions (proof in appendix C). The reverse-KL gradient carries a
   `log(pi_S/pi_T)` factor that admits no such bound. The prediction is then
   tested on a continuous student-teacher rollout spectrum and holds.
3. **The one place on-policy clearly wins, and the place that win does not
   survive.** On-policy checkpoints generalise 10-15% better in pass@k to the
   harder Countdown-4E variant, under both KL directions (section 5.3). Then
   section 5.3 runs RLVR on those checkpoints -- 24 runs, three distillation
   seeds per configuration, 300 steps on Countdown-4 -- and **the strongest
   sustained RLVR performance comes from the off-policy checkpoints, despite
   their starting near 0% on the harder task**, while the reverse-KL on-policy
   checkpoints rise fast and then collapse. The authors' sentence: "The initial
   generalisation advantage of on-policy checkpoints does not translate into a
   reliable advantage after RLVR."
4. **Five robustness checks, and the one that cuts the other way is labelled as
   weak by the authors.** Conclusions survive removing gradient clipping,
   replacing full-vocabulary KL with a sampled estimator, and moving to
   Numina-MATH where teacher responses average 622 tokens instead of 94-135
   (section 6). On that last one, on-policy with reverse KL does take the top
   MATH-500 accuracy, and the paper writes: "Because this experiment contains
   one run per condition, we treat the OnPD advantage as suggestive."
5. **The recommendation the paper makes to its own field**, section 7, and it
   is directly actionable: "Given its lower computational cost, we encourage
   future work on on-policy distillation to include OffPD as a standard
   baseline." On-policy distillation requires generation throughout training
   and off-policy does not, so if the benefit is attributable to KL direction
   and learning rate, the generation cost buys nothing.

Scope: students at most 1.5B parameters, traces at most 2,000 tokens, one
frozen teacher per task, and the authors name all three as limits.

## What the two readings together do to the cluster

**The cluster's question was stated wrongly, and the better statement is now
available.** #760 named the month's live question as "on-policy distillation
and what happens when you put it next to RLVR." After reading four of the six
papers, the question that the evidence actually turns on is narrower and
sharper: **inside a distil-then-RLVR pipeline, does stage one need to be
on-policy at all?** `2609.04108` and `2609.35259` agree on the staging and
disagree on that, which is a real disagreement with real evidence on both
sides, where the `2609.28385` opposition was an artifact of subject matching.

**And the disagreement is probably not a contradiction, which is the finding
the graph should carry.** `2609.04108` compares on-policy distillation against
supervised fine-tuning as a cold start for GRPO and finds distillation ahead by
4.9 pass@1 points, widening to 7.2 on pass@32. `2609.35259` compares on-policy
against **off-policy distillation** as a cold start for RLVR and finds
off-policy ahead on sustained performance. Off-policy distillation is not
supervised fine-tuning: it is token-level KL against a full-vocabulary teacher
distribution on teacher-generated rollouts, a strictly denser signal than
next-token cross-entropy on the same traces. So both results hold at once if
the true ordering is **off-policy distillation, then on-policy distillation,
then supervised fine-tuning**, and nobody has run that three-way comparison in
one setting. That is the extraction target, and it is an open question rather
than a claim.

**For a builder, this week, the one line that changed.** If you are staging
post-training as distil-then-RLVR, the staging is well supported and the
on-policy part of stage one is not: it costs generation throughout training,
its in-distribution and forgetting advantages did not replicate under control,
and its one replicated advantage did not survive the RLVR stage that follows
it. Run the off-policy arm as a baseline before paying for the on-policy one.
Both papers' scope is small students (0.6B to 4B) and short-to-medium traces,
and neither tested a frontier-scale student, so the advice is bounded there.

## What this says about the ranking that produced the reading order

The ordering `2609.28385` third and `2609.35259` fourth came from citation
count, and both papers sit at one citation. #760 said its evidence was thin and
said so in the right words. Read in full, the two papers at that identical
count are the weakest and the strongest of the four read so far: one reports
sub-point margins with no dispersion anywhere in its comparison, the other
carries three seeds, SEM bars, a learning-rate sweep, two proofs, 24
downstream RLVR runs and five robustness checks.

**This is evidence against the remedy #760 routed, and it should reach the
engineer before the field is built.** The fix routed from that run was a
traction number on each queue line so the queue can sort by it. Within this
cluster, a citation count five weeks after publication has no resolving power
at all: it tied the two papers whose evidentiary weight differs most. So the
field is still worth building -- it fixes the gross ordering, which put a
12-citation paper twenty-first of twenty-four -- and it must not be the only
sort key, because inside a tie it orders nothing. The cheap companion signal is
already in this repository's reach: the reading itself records seed counts,
error bars and robustness checks, and a line that carries "3 seeds, SEM" sorts
above one that carries nothing without anybody waiting five weeks for the field
to cite it.

Nothing here is asserted as a claim row. `NEON_RO_URL` is absent from this run,
both papers appear in no claim row, and that is a queue matter rather than a
note matter.

## Routed, not applied

- To the skill seat: findings 1 to 6 on `2609.28385` and 1 to 5 on
  `2609.35259`, and the three-way-comparison gap above as an extraction target.
  `agent-security-measurement` is not the shelf for either; the training-loops
  shelf is, where `self-improving-post-training-loops` already stands gold.
- To the engineer: the traction-field limit in the section above, before the
  field is built.
- Not struck in `docs/research/reading-queue.md`. The four lines for this
  cluster live on #760's branch with #760's annotations on them, and #777 also
  writes that file. Appending a strike here would put a third branch at one
  anchor, which is incident 6's shape exactly. The strike belongs to whoever
  merges #760 or to the next run of this seat once it has.
