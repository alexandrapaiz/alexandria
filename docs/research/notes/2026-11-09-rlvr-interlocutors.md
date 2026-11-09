# The two interlocutors read, and the cluster's central claim is a tie in its own significance table

Research seat, 2026-11-09. Continues the chair's RLVR batch of 2026-10-05
(`docs/research/reading-queue.md`, board card `251ae14a`). PR #760 measured the
batch and read papers one and two of a six-paper read-first cluster; #796 read
three and four; #854 read five and six and, on its live check, found two papers
the cluster lacked and **queued them rather than reading them** -- lines 3652 and
3654 of the queue. This run reads those two in full, which is the head of this
seat's own published ranking, and then re-opens the paper they were queued to
argue with.

| id | title | read by | status before this run |
|---|---|---|---|
| `2608.24696` | On-policy Distillation with Verifiable Reward (OPDVR) | **this run** | queued #854, abstract only |
| `2605.12652` | Multi-Rollout On-Policy Distillation (MOPD) | **this run** | queued #854, abstract only |
| `2609.04108` | Sequential Beats Joint | #760 | read, and **re-read this run** |

All three read with `python3 tools/read_paper.py`, exit 0, full text off
`arxiv.org/html`: 80,471 chars (`2608.24696`), 89,971 (`2605.12652`), 82,275
(`2609.04108`). Every number below names the table it came from.

## The headline: three runs have hunted a counterparty to an effect that is
## already a tie in the domain every candidate works in

Three runs of this seat have now named a counterparty to `2609.04108`'s title:

- **#760** named `2609.28385`. #796 read it and found the word "stage" does not
  occur in the paper.
- **#854** named `2608.24696` (OPDVR) as "the joint design done well, which
  makes it the counterparty `2609.04108`'s title is arguing with".
- **#854** also named `2605.12652` (MOPD) as the earlier single-model case of
  GRAFT's finding.

Read in full, neither of the second two is a counterparty either, by the same
test #796 applied:

```
grep -oic 'sequential|two-stage|two stage|cold start|cold-start|stage|staged' on each full text
  2608.24696  sequential 0   two-stage 0   cold start 0   stage 0   staged 0
  2605.12652  sequential 1   two-stage 0   cold start 0   stage 6   staged 0
```

`2605.12652`'s single "sequential" is inside a bibliography entry for a
different paper's title, and all six of its "stage" hits are pipeline-timing
labels in an appendix (`timing_s/update_actor`, "the advantage-processing
stage"). Neither paper's baseline set contains a staged arm: OPDVR compares
against Sampled-Token OPD, Top-64 OPD, OPD+GRPO, RLSD, ExOPD, SG-OPD and
Distilled RL (section 5.1), all single-update; MOPD compares against the base
model, GRPO and SDPO (section 5). **Three candidates, three times the same
negative result.**

But the reason the hunt keeps failing is not that the field is silent. It is
that **`2609.04108` does not claim what the hunt assumed.**

Credit where it is owed, because this run did not discover that: #854 already
sharpened the queue line for `2609.04108` with the paper's bootstrap, writing
that the "beats all nine" half "holds on logic only" and that on math the lead
is "significant against six of the nine and a statistical tie with the three
strongest". That annotation is on queue line 360 and it is correct. What it does
not do is name the three, and the names are the whole decision. Table 7 is a
paired bootstrap over problems, 20,000 resamples, 95% confidence intervals for
the difference between OPD-then-RL and each competing method, macro-averaged
over MATH-500, AMC23, AIME24 and AIME25:

| OPD-then-RL vs. | pass@1 | pass@32 |
|---|---|---|
| OPD (pure) | [-0.47, +2.13] | [-1.58, +7.10] |
| SRPO (joint, weighted-additive) | [-0.81, +1.21] | [-2.09, +6.45] |
| KDRL-mask (joint) | [-0.06, +4.77] | [-3.10, +7.27] |
| TRRD (joint, teacher-modulated) | **[+0.54, +2.97]** | [-5.12, +4.26] |
| RLSD (joint, teacher-modulated) | **[+0.57, +3.01]** | [-0.70, +8.21] |
| HDPO (joint) | **[+0.74, +5.43]** | [-2.52, +9.08] |
| KDRL (joint) | **[+0.51, +5.25]** | [-5.75, +5.34] |
| GRPO | **[+1.06, +6.03]** | [-3.05, +8.94] |
| KDRL-Annealing (scheduling) | **[+0.81, +2.89]** | **[+0.19, +9.93]** |

Bold excludes zero. The three ties are SRPO, KDRL-mask and **pure OPD**, and
that last one is not a joint baseline at all -- it is stage one on its own. So
the accurate sentence is not "tied with the three strongest joint methods" but
**"on mathematical reasoning, running both stages is not distinguishable from
running only the first"**, which is a statement about whether to stage rather
than about which fusion to prefer. On pass@32 nothing separates from
OPD-then-RL in either direction except KDRL-Annealing. The paper's own summary,
which is accurate: "a large margin on logic and a tie on math."

Its Table 2 shows where the margin lives. Logic average pass@1 (K&K, Zebra,
Countdown): student 1.9, teacher 59.9, GRPO 49.4, pure OPD 53.9, best joint
KDRL 62.8, KDRL-Annealing 68.9, **OPD-then-RL 80.6**. Math average pass@1
(MATH-500, AMC23, AIME24, AIME25): GRPO 28.4, pure OPD 31.0, SRPO 31.6,
**OPD-then-RL 31.8** -- and on math pass@32 OPD-then-RL's 58.5 is *third*,
behind TRRD's 58.9 and KDRL's 58.7.

The paper names the moderator in its own setup, section 4.1: logic reasoning is
"where the teacher has limited prior exposure", mathematical reasoning is "where
the teacher has been heavily post-trained". It replicates the pattern on a
0.6B student (logic average pass@1 45.0 GRPO, 48.9 OPD, 70.4 OPD-then-RL) and
across model families on an OLMo-3.1-32B -> OLMo-3-7B pair, where it reports
"a large margin on logic and a tie on math" again.

**So the correction to this seat's record is this.** #854 attached the domain to
the staging claim and stopped there. The consequence it did not draw is that
every math-domain result in this cluster sits inside the regime where the
cluster's own staging paper reports a null. OPDVR, MOPD, GRAFT and UECR-GRPO are all evaluated on
mathematical reasoning. A counterparty to the staging claim found among them
would have been arguing about an effect that `2609.04108`'s own significance
table does not establish there. The question worth asking was never "who
disputes the staging result"; it is **"does the staging result exist outside
logic-style tasks the teacher has not been trained on"** -- and on the published
evidence the answer is no, by the original paper's own bootstrap.

That also retires the handoff #854 routed to the chair through the PM. The two
papers were queued as "the cluster's missing interlocutors". They are not
interlocutors. They are two more entries in the math regime, and they are worth
rows for their own findings below rather than for the role they were assigned.

## `arxiv:2608.24696` -- On-policy Distillation with Verifiable Reward (OPDVR)

https://arxiv.org/abs/2608.24696 -- Lin, Zhao, Jiang, Rao, Li, Wang, He, Huang
(LeapLab Tsinghua / Qiuzhen / Beihang / Peking / NLPLab), v4 of 2026-09-29,
arXiv perpetual non-exclusive license, code at github.com/LeapLabTHU/OPDVR.
Full text, 80,471 characters.

The mechanism, and it is the cleanest thing in the cluster. Match the
sampled-token OPD gradient against the RLVR gradient term by term (section 4.1)
and the OPD log-ratio *is* an implicit token-level reward,
`R_OPD(o_t) = log(pi_T/pi_theta)`. Its **sign is set by the teacher-student
confidence ratio and not by the verifier**, so a correct trajectory's tokens are
penalised wherever `pi_T < pi_theta` and an incorrect trajectory's tokens are
rewarded wherever `pi_T > pi_theta`. OPDVR applies a ReLU to each case so correct
trajectories get non-negative and incorrect ones non-positive reward. No new
hyperparameter. Section 4.3 reads the gate as a conditional token mask.

1. **The gate is a proximity instrument, and the cluster now has a fourth
   one.** Its decision variable is the pointwise log-ratio between teacher and
   student -- the same quantity `2609.35259` bounds with total variation,
   `2609.37868` approximates with a cross-tokenizer compatibility score, and
   `2609.16639` measures as answer-only perplexity. Section 5.5 reports the
   readout directly: the **zero-gated token ratio stays in a band around a half
   for the whole of training**, 0.48-0.50 for the 4B student and 0.40-0.44 for
   the 1.7B one, "never degenerating". The same section reports that student
   entropy and response length have *no* setting-independent trend -- entropy
   drifts 0.33->0.40 with length inflating 1.6k->6.7k in the same-architecture
   run, and entropy collapses from ~2.0 with length flat in the
   cross-architecture one. **So the one quantity stable across both settings is
   the proximity readout and not either of the usual training diagnostics.**
2. **The inverse-gated ablation is the strongest causal evidence in the cluster
   for the proximity axis.** Table 4, same-architecture: OPD 47.8, OPDVR 49.1,
   **Inverse-Gated 44.6**, with "the masking ratio and everything else
   unchanged". Same amount of masking, opposite selection, and the result falls
   below vanilla OPD **on all six benchmarks**. Holding the budget fixed and
   flipping only the sign of the selection is the test the rest of the cluster
   does not run. Note the authors' own careful reading: the inverse variant
   still improves on the initial model, so the teacher's distributional guidance
   survives a misaligned sign -- it is "substantially hindered", not destroyed.
3. **The margins are small, and the abstract's "consistently" is false in one
   cell.** Table 1, same-architecture (Qwen3-4B <- Qwen3-4B-RL), avg@16: student
   42.0, teacher 50.4, Sampled-Token OPD 47.8, Top-64 47.4, OPD+GRPO 47.7, RLSD
   44.8, ExOPD 47.9, SG-OPD 47.5, **OPDVR 49.1**. OPDVR leads on four of six
   benchmarks and trails on two, and on MATH500 it scores **84.7 against
   vanilla sampled-token OPD's 85.5** -- so "OPDVR consistently outperforms
   standard OPD", which is the abstract's claim and the conclusion's, does not
   hold per benchmark in the paper's own main table. On Minerva it is third
   (33.2 against ExOPD 35.9 and SG-OPD 35.2).
4. **It does not break the teacher ceiling, which is the problem the abstract
   opens with.** OPDVR's 49.1 is below the teacher's 50.4; GRPD's 49.4 is below
   it too. The single cell above the teacher is AIME24, 36.9 against 36.0. The
   abstract says OPD's performance is "limit[ed] to that of the teacher"; the
   paper moves the student from 42.0 to 49.1 against a teacher at 50.4 and
   leaves the limit in place.
5. **Every average reproduces from its own cells except the one the headline
   margin is measured against.** Recomputed from Table 1: student 42.000,
   teacher 50.433, OPD 47.817, Top-64 47.350, OPD+GRPO 47.717, RLSD 44.800,
   SG-OPD 47.450, OPDVR 49.117 -- all round to the printed value. **ExOPD
   computes to 48.000 and is printed 47.9.** The text says OPDVR outperforms
   "the next best method (ExOPD, 47.9) by 1.2 points"; from the cells the lead
   is 1.1. Tables 2 and 3 reproduce throughout.
6. **GRPD's "all six benchmarks" claim is false on two of six.** Table 3
   (Qwen3-4B <- Qwen3-4B-RL, DAPO-Math-17K, G=8): GRPO 44.8, OPD 48.4, Distilled
   RL 48.7, **GRPD 49.4**. The text says "GRPD consistently outperforms all
   baselines across all six benchmarks". On MATH500 GRPD scores 85.6 against
   Distilled RL's 86.3, and on AIME25 it **ties** vanilla OPD at 31.7. The
   aggregate claims in the same paragraph do check: +1.7 on AIME24 and +0.7 on
   average over Distilled RL, +6.5 and +10.9 over GRPO on AIME24 and AIME25.
7. **No dispersion anywhere.** Searched the full text: "seed" 0, "error bar" 0,
   "significan" 0, "confidence interval" 0, "95%" 0. The five hits for "std"
   and the one for "standard deviation" are all the GRPO advantage denominator
   in sections 3.1 and 4.4. Evaluation is avg@16 under one decoding setup, one
   training run per method per setting. **So a 1.1-point lead and a 0.7-point
   lead have nothing measured to be read against** -- which matters more here
   than usual, because the paper the cluster was comparing it to publishes a
   bootstrap that calls differences of exactly that size ties.

Scope, so nothing above is over-read: Qwen3 only, students 1.7B and 4B,
mathematics only, two teacher-student pairs, verifiable rewards only, one run
per condition.

## `arxiv:2605.12652` -- Multi-Rollout On-Policy Distillation (MOPD)

https://arxiv.org/abs/2605.12652 -- Yu, Li, Zhao, Liu, Zhang, Wang, Luo, Wu,
Mittal, Fredrikson, Hu (Carnegie Mellon / Microsoft / Purdue), v2 of
2026-06-01, code at github.com/viviable/mopd_code. Full text, 89,971
characters. The cluster's only paper outside mathematics and code-plus-QA
together, and the only one with a tool-use arm.

Standard OPD distils each rollout independently and throws away the other
attempts sampled for the same prompt. MOPD puts the student's own peer
rollouts -- two successes and one failure by default -- into the self-teacher's
context, so the teacher scores the target rollout while conditioned on both
what worked and what failed on the same prompt.

1. **The result that earned the queue line replicates in direction, on two
   tasks, and the ablation is internally clean.** Table 4, peer-context
   construction, mean@8: QA-Chemistry 51.90 (one success), 52.62 (two
   successes), **35.67 (one failure alone)**, 60.50 (one success + one
   failure), **74.29 (two successes + one failure)**; LiveCodeBench 49.49,
   55.62, 46.72, 58.90, **61.82**. Adding a single failed peer to a
   success-only context is worth **+21.67 on QA-Chemistry and +6.20 on LCB**,
   and a failure alone is the worst condition on both. The authors' own
   signal-quality analysis gives the mechanism: pairwise accuracy of the
   self-teacher rises from 0.13 with no peer to above 0.32 with any success,
   and **0.32 -> 0.40 when a failure is added to a success-only context**,
   "showing that negative evidence sharpens decision boundaries that positive
   evidence alone leaves blurred".
2. **But the sharper half of #854's claim does not replicate here, and the
   paper's tables cannot settle it.** GRAFT's result was that transferring only
   successes scores *below the no-transfer baseline* (29.22 against plain
   GRPO's 32.60). MOPD's equivalent comparison cannot be reconstructed: on LCB
   the Table 4 "1 successful solution" row is **numerically identical to Table
   5's SDPO Qwen3-8B row** (49.49 mean@8 / 64.34 pass@8), which reads as the
   no-peer baseline being the one-success condition, while on QA-Chemistry the
   "1 successful solution" row (51.90) matches no SDPO value anywhere in the
   paper. Taking the rows at face value, two successes is 55.62 against SDPO's
   49.49 on LCB (above the baseline) and 52.62 against SDPO's 62.91 on
   QA-Chemistry (below it). **So "the failures carry the signal" is a
   two-group pattern on direction and remains a one-table result on
   magnitude.** That is a narrower claim than the one #854 filed and it is the
   one the evidence supports.
3. **Two of the paper's own tables disagree about the baseline, on the one
   domain where it publishes dispersion, and the disagreement decides the
   result.** Table 2 (Science QA, Qwen3-8B) gives SDPO 50.60 / 62.91 / 67.36 /
   72.34 across Biology, Chemistry, Physics, Materials. Appendix Table 10 gives
   the same four SDPO cells with standard deviations over 3 runs: 50.60 +/- 2.1,
   **73.22 +/- 2.5**, 67.36 +/- 1.9, 72.34 +/- 2.6. Three of four match exactly;
   **Chemistry differs by 10.31 points.** Against Table 2's 62.91, MOPD's 74.29
   is a lead of 11.38. Against Table 10's 73.22 +/- 2.5, MOPD's 74.29 +/- 2.0 is a
   lead of **1.07, inside one standard deviation of either arm**. The authors
   say of Table 10 that "the standard deviations reveal moderate variance ...
   suggesting that training is not fully stabilized across runs." One of those
   two cells is wrong; the paper does not say which, and which one it is decides
   whether the Chemistry result is a win or a tie.
4. **"Consistently improves over standard on-policy baselines" fails on the
   math table.** Table 1 (Qwen3-4B, same generation budget): on AIME2025 MOPD
   scores **25.41 mean@8 against GRPO's 25.80** and 36.28 pass@8 against 36.66,
   and on HMMT25-Feb 19.58 pass@8 against GRPO's 20.94. Three of eight math
   cells go to GRPO. Where MOPD does win on math it wins large -- AIME2024
   28.54 against 17.09 -- so the aggregate is real and the word "consistently"
   is not. On LCBv6 (Table 5) the claim does hold at both scales: 4B 57.01
   against SDPO 48.84 and GRPO 40.75; 8B 61.82 against 49.49 and 43.65.
5. **One number worth taking on its own, because it prices the problem GRAFT
   exists to solve.** Section 5.3, finding 5: on LCBv6, **57% of prompts
   produce no successful rollout at all** for Qwen3-4B, which is why the
   no-peer self-teacher's pairwise accuracy is 0.13. GRAFT's whole construction
   is the all-fail group; this is an independent measurement of how often that
   group occurs, on a different benchmark, by a group that does not cite GRAFT.
6. **More peer context is not monotonically better, and the chosen
   configuration is not the best one.** Table 4's "8 solutions (4 hours)" row
   reaches **81.25 on QA-Chemistry against the headline configuration's
   74.29**, while on LCB it is 58.95 against 61.82. The paper states the second
   half ("providing all available rollouts yields no additional gains" on LCB)
   and not the first. Overhead for the headline configuration is +9.1% per step
   on LCB and +33.3% on QA-Chemistry (appendix Table 9).
7. **Dispersion exists and covers one of four task families.** "seed" 0,
   "error bar" 0, "significan" 0, "confidence interval" 0; Table 10 is three
   runs on Science QA only. Code, math and tool use are one run per condition.

Scope and the authors' own limits (appendix G): a verifier that can partition
rollouts into successes and failures is required; peer conditioning grows
context length and teacher-query cost, and which peers to pick under a context
budget is open; noisy or mislabelled verifiers inject misleading evidence.
Students are Qwen3-4B and Qwen3-8B.

## What the eight papers now are, as a body

**Mutual silence is total, and it now covers eight papers.** Checked pairwise
by grep across every full text in hand: `2608.24696` mentions none of
`2605.12652`, `2609.37868`, `2609.16639`, `2609.35259`, `2609.28385` or
`2609.04565`; `2605.12652` mentions neither `2608.24696` nor `2609.04108`;
`2609.04108` mentions neither MOPD nor GRAFT. #796 established that
`2609.28385` and `2609.04108` never meet. Eight papers on one question, and
not one citation between any pair of them.

**There is exactly one measurement bridge, and it holds.** `2608.24696` and
`2609.04108` share a baseline: RLSD. In `2609.04108`'s Table 2 RLSD's math
average pass@1 is 30.1 against pure OPD's 31.0; in `2608.24696`'s Table 1
RLSD is 44.8 against pure OPD's 47.8. Two independent reimplementations, two
different student-teacher pairs, and **both put RLSD below pure OPD on
mathematics**. That is the only cross-paper quantity in this cluster that two
groups measured without talking to each other, and the agreement is worth more
than either paper's headline because neither was trying to establish it.

**For the graph.** No `contradicts` edge belongs between any pair of these
eight -- an exchange has to exist before it can be a contradiction, and none
does. The edges that are true: `2608.24696` and `2609.04108` *compare* on
RLSD, in agreement. `2605.12652` and `2609.37868` *converge* on failures
carrying signal, by different routes, on direction only. `2609.04108`'s math
arm and `2609.35259`'s controlled study are both nulls about provenance, which
is agreement and not opposition.

**The proximity axis survives the two new readings and gains its best causal
test.** #854 named it from three instruments. OPDVR is the fourth, and unlike
the other three it manipulates the quantity experimentally rather than
measuring it: same mask budget, inverted selection, 4.5 points below OPDVR and
3.2 below vanilla OPD on all six benchmarks. The axis is now four independent
instruments and one controlled flip.

## What a builder should do differently, corrected

#796 and #854 left this seat's advice as: the distil-then-RLVR staging is
supported on logic reasoning, and the on-policy part of stage one is not
supported anywhere. **Both halves stand as written. What changes is what
follows from the first, and it is sharper than either run said.**

1. **Stage, if your teacher has not been trained on your task; otherwise do
   not bother.** `2609.04108`'s staging advantage is +11.7 average pass@1 over
   the best joint baseline on logic reasoning and **statistically
   indistinguishable from pure OPD on mathematics** (Table 7, [-0.47, +2.13],
   20,000-resample paired bootstrap). It replicates the same split at 0.6B and
   across model families. #854 had this as "the staging is supported, logic
   reasoning"; the operative half is the other one. If your task looks like the
   math case -- a teacher already heavily post-trained on it -- the published
   evidence does not support paying for a second stage at all, never mind
   choosing between fusions.
2. **Do not pay for on-policy rollouts in stage one until you have run the
   off-policy arm.** Unchanged from #796: `2609.35259` holds the pipeline fixed
   and finds KL direction and learning rate move accuracy while rollout policy
   does not, with three seeds and SEM bars.
3. **If you are gating or weighting a distillation signal, gate on correctness
   first and proximity second, and check the sign.** OPDVR's ReLU is one line
   and no hyperparameter, and the inverse-gated arm says the sign of that gate
   is worth 4.5 points at a fixed mask budget. Expect about half your tokens
   masked (0.40-0.50 across both of its settings).
4. **Put failed rollouts in front of whatever is producing your dense signal.**
   Two groups, two designs: +21.67 and +6.20 mean@8 from adding one failure to
   a success-only peer context (`2605.12652` Table 4), and success-only
   transfer below the no-transfer baseline in `2609.37868` Table 2(b). Direction
   is a pattern; the below-baseline magnitude is one table.
5. **Treat every margin in this cluster under about three points as unmeasured
   unless the paper published dispersion.** Of the eight papers, three publish
   any: `2609.35259` (three seeds, SEM, everywhere), `2609.04108` (paired
   bootstrap on math, and it converts its own headline into a tie),
   `2605.12652` (three runs, one of four task families, and its two tables
   disagree by 10.31 points on the cell that has them). `2608.24696`,
   `2609.37868` (main table), `2609.16639`, `2609.28385` and `2609.04565`
   publish none in their headline comparisons.

Everything above is bounded to students between 0.6B and 8B, traces at most
8,192 tokens, and tasks with automatic verifiers. No paper in the body tested a
frontier-scale student.

## Nothing here is a claim row

There is no corpus route from this host: `DATABASE_URL`, `NEON_RO_URL` and
`NEON_URL` are all unset, `import psycopg` raises `ModuleNotFoundError`,
`command -v modal` finds nothing and there is no `~/.modal.toml`. The chair's
ask on this batch is corpus presence, which one distill run meets and no
reading does. The extraction targets are listed on the queue lines and in the
run note; the shelf is training-loops.
