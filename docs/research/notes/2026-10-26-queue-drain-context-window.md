# Draining the 2026-09-29 context-window-engineering reading-queue batch

Run of 2026-10-26, research seat, message trigger. The batch was queued by
`skills/context-window-engineering` on 2026-09-29: 15 arXiv ids, 4 works with
no arXiv id, 3 questions. It is the oldest undrained batch in
`docs/research/reading-queue.md`.

**The corpus is unreachable this run, as it was on 2026-10-26's weekly run
(PR #589): the Modal workspace is disabled, so there is no `sql_query`,
`semantic_search`, `get_digest`, `propose_skill` or `propose_change`.** Every
paper below was read off arXiv with `tools/read_paper.py`, which needs none of
them. What this run cannot do is write claims into the corpus. What it can do,
and does, is read the queued papers in full and record what they say against
the skill that queued them, so that the claims are a transcription job for
whoever has `distill` rather than a reading job.

Reading status, 15 ids: **14 full text, 1 abstract only** (`2602.10560`,
arXiv serves no HTML).

---

## The headline: the two independent checks agree, and they agree on something
## sharper than either paper claims

Two of the first five were queued as "the independent check on this skill's
central finding, and the library currently cannot run that check." Both are now
read, and together with the paper the skill already holds they resolve the
check in a way no one of the three states.

The skill's delta 1 says: pin the whole prompt, evict uniformly at random for
the rest, and you are competitive with the strongest trained-free scorer. Its
source is Random Attention (`2609.03430`, claims 78-80), decode-phase, per-head,
reasoning traces.

### `2605.18053` — Protection Is (Nearly) All You Need (Garcia, 18 May 2026)

Independent, different regime: globally capped decode-time harness, LongBench
QA, seven policies (LRU, H2O, SnapKV, StreamingLLM, Ada-KV, QUEST, Random), ten
models across five vendor families.

- **Without structural protection all seven policies collapse to F1 <= 0.064.**
  Not degraded: degenerate. The author audited the reference implementations of
  H2O, SnapKV, Ada-KV, QUEST and vLLM and found all four retain a recency
  window and **none protects the first-token sink by position**, so the
  vulnerability is in published code and not in his harness.
- **Reserving 10% of capacity at each boundary recovers 69-90% of the C=2048
  ceiling at C=256 (13% retention)** on the seven-model LongBench panel; a
  ten-model panel spans 68-98%.
- **The protection budget curve, which this skill does not have and its own
  caveats admit it needs.** LRU at C=256: 0% -> F1 0.011 (3.6% of ceiling);
  5% -> 0.247 (78.3%, p<0.001); 10% -> 0.282 (89.4%, p=0.016 vs 5%);
  15% -> 0.285 (ns); 20% -> 0.283 (ns). **Ten percent each side, and past that
  you are spending capacity that middle context wants.**
- **Protection is bilateral and it is structural, not a budget artifact.** At a
  matched 52 protected slots: both(10+10) 89.8% of ceiling, prefix-only(20%)
  55.6%, suffix-only(20%) 60.6%, both p<1e-7 against bilateral. Doubling either
  side alone buys nothing (prefix p=0.65, suffix p=0.13). Each boundary alone
  recovers ~55-58%; the pair recovers ~90%.
- **Negative result worth the corpus's shelf space: learned credit estimation
  adds nothing.** A 4-feature online counterfactual credit estimator is
  statistically indistinguishable from LRU+protection at every capacity tested
  (C in {64,96,128,256,512}, all p>0.12, Wilcoxon), and identical to three
  decimal places at C=64.

**And it corrects this skill's wording.** The skill says random eviction "is
the best policy in all four settings once protected." In this paper's regime
protected-random is a **floor, not a winner**: F1 0.250 at C=256 against
0.282-0.290 for all five scoring policies (Delta = -0.031 vs LRU+prot, p=0.14,
ns at N=162) — about ten percentage points of ceiling behind, non-significantly.
The gap then **nearly vanishes as capacity slack grows**: at C=512 random+prot
is 0.289 against LRU+prot's 0.285 (Delta = +0.004, p=0.67). Faithful per-head
Ada-KV and QUEST add a further ~0.03-0.04 F1 over simplified variants, against
a protection lift of ~0.11-0.14 F1. The author's own summary is the honest one:
"protection dominates; scoring differences are secondary once boundaries are
guarded; per-head allocation gives a further modest gain."

Read against the skill, the correction is small and the direction is the same:
run the null arm first, expect it to get you ~80% of the way, and expect the
scorer to buy single-digit percent that shrinks as the budget loosens. That is
a better decision rule than "almost nothing beats it," and it is the rule the
evidence supports.

### `2512.12008` — Hold Onto That Thought (Liu et al., Maryland/Chicago/Utah, 12 Dec 2025)

Queued as "the evaluation that reported random and recency baselines falling
far behind scored selection on reasoning ... the paper the skill's central
claim is arguing with."

**First, the queue line is half wrong, and the half matters.** This paper runs
no random-eviction baseline at all. Its methods are H2O, R-KV, StreamingLLM,
KNorm, a decoding-enabled SnapKV (SnapKV-D) and ShadowKV. So Random Attention's
explanation — that the random baselines lost the prompt — cannot be checked
against this paper, because there is no random baseline in it to check. The
recency half is right and it is brutal.

**Second, the disagreement is real and it is enormous.** On R1-Distill-Qwen-14B
at cache budget 128, GSM8K: SnapKV-D **0.80**, H2O 0.33, StreamingLLM 0.07,
R-KV 0.02, KNorm 0.00, against a full-cache 0.81. MATH500 at 128: SnapKV-D
0.43, H2O 0.20, StreamingLLM 0.02, R-KV 0.00, KNorm 0.00, full cache 0.47. The
spread between eviction methods here is not 0.03 F1. It is three quarters of
the entire metric, on reasoning, which is this skill's own regime.

**Third, the paper measures the mechanism that reconciles it, and reads its own
table the other way round.** Appendix A.4 defines a critical-token retention
rate: the fraction of the question's critical tokens (names, quantities, key
entities) still in cache at the final decoding step. Table 8 shows SnapKV-D and
H2O retain them at a higher rate than the others, and the paper's Figure 3
attention-loss ordering is the same ordering as the accuracy: SnapKV-D, H2O,
StreamingLLM, KNorm, least loss to most. The paper concludes that accumulated
attention is the best importance heuristic. The same table, read against the
other two papers, says that **the methods that win are the methods that still
hold the question at the end of decode**, and scoring is how they get there
rather than why it works.

### The sharpened claim, and it now clears the three-source bar

| paper | regime | prompt protected? | spread between methods |
|---|---|---|---|
| `2512.12008` | long decode, short prompt, reasoning | no | catastrophic: 0.07 to 0.80 |
| `2605.18053` | globally capped decode, LongBench QA | no | all collapse, F1 <= 0.064 |
| `2605.18053` | same, protected | yes | Delta 0.031, p=0.14, ns |
| `2609.03430` (held) | decode-phase per-head, reasoning | yes | random competitive, ahead in 31 of 60 |

**The spread between KV eviction methods is largely a measure of how much
protection each one accidentally provides.** Three papers, two regimes, two
protection conditions, one pattern, and no one of the three says it. The
charter's bar is three independent sources for a pattern and this is three.
It is the strongest extraction target to come out of this batch.

The one cell nobody has filled: **protected-random on long-decode reasoning at
a micro-budget**, where `2512.12008` measured the 0.07-to-0.80 spread. Random
Attention is protected and in that regime, but at 10-50% compression rather
than at a 128-token absolute cap. Whether explicit bilateral protection closes
a gap that large is unmeasured.

### And `2512.12008` contradicts the skill's fourth checklist item outright

The skill says to "expect the question to be unrecoverable and the trace nearly
free to cut; the trace restates itself (claims 80, 280)." This paper measures
the opposite cost on the trace half: **cutting the cache makes reasoning models
generate longer traces.** Lower budgets trigger elongation, worst for the
worst-performing policy (KNorm), and Appendix A.2 exhibits a DeepSeek-R1-Distill-
Llama-8B run that babbles in circles and never answers. Its practical guidance
leads with "regardless of method, avoid a micro-budget ... very small budgets
can counterintuitively increase the length of the output."

So the trace is not nearly free to cut. Cutting it buys cache and spends
decode, and the skill currently prices only the first. The skill's own caveat
already flags claim 80's redundancy as "inferred, not measured"; this is the
measurement, and it goes the other way.
