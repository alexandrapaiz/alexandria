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

### `2605.18053` -- Protection Is (Nearly) All You Need (Garcia, 18 May 2026)

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
ns at N=162) -- about ten percentage points of ceiling behind, non-significantly.
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

### `2512.12008` -- Hold Onto That Thought (Liu et al., Maryland/Chicago/Utah, 12 Dec 2025)

Queued as "the evaluation that reported random and recency baselines falling
far behind scored selection on reasoning ... the paper the skill's central
claim is arguing with."

**First, the queue line is half wrong, and the half matters.** This paper runs
no random-eviction baseline at all. Its methods are H2O, R-KV, StreamingLLM,
KNorm, a decoding-enabled SnapKV (SnapKV-D) and ShadowKV. So Random Attention's
explanation -- that the random baselines lost the prompt -- cannot be checked
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
leads with avoiding a micro-budget regardless of method, because in its own
words a small enough budget can counterintuitively increase the length of the
output.

So the trace is not nearly free to cut. Cutting it buys cache and spends
decode, and the skill currently prices only the first. The skill's own caveat
already flags claim 80's redundancy as "inferred, not measured"; this is the
measurement, and it goes the other way.

---

## The best thing in the batch: the null policy's mechanism has a name, and a
## bound, from a group that was not trying to explain it

Two more of the fifteen, read against each other, supply what Random Attention
never offered: **why** evicting at random per head works.

### `2606.29563` -- Coverage-Driven KV Cache Eviction / K-VEC (Roy et al., RBC Borealis, 28 Jun 2026)

Queued as "a selection rule built on coverage rather than importance scoring,
which is the one family the null policy does not obviously subsume." It is not
a rival family. It is the null policy's mechanism, written down on purpose.

The paper's diagnosis, in its own words: existing eviction policies "often
select overlapping tokens across heads, resulting in reduced coverage across
the heads of a layer," and its Figure 3 shows the retained set skewing hard
toward the end of the input "despite the correct answer appearing first." It
then proves a bound: performance is floored by phi(alpha log C) where C is
coverage of unique tokens, so **a drop in coverage during eviction forces the
input-output mutual information down**, which is the mechanism of the collapse.
Its fix is two modules, cross-head coverage and cross-layer coverage, and it
buys **up to 10.35 points over existing methods at the same eviction rate and
memory constraint** on 16 LongBench subsets.

**Per-head uniform random eviction maximises cross-head coverage by
construction.** Different heads keep different tokens because nothing
correlates their draws, so the union over heads covers the input. That is
exactly the quantity K-VEC's theory says bounds accuracy, and K-VEC spends a
module to get it because importance scoring destroys it: scores are correlated
across heads, so every head keeps the same tokens.

So the three results stop being three results:

- Random Attention: per-head random is competitive, **and only per head** --
  the skill already records that the per-head property is the floor of the
  regime.
- K-VEC: cross-head coverage is the quantity with the bound, and buying it
  deliberately is worth up to 10.35 points.
- `2605.18053`: **learned credit estimation adds nothing** over LRU+protection
  at every capacity (all p>0.12). Credit learning is better importance scoring,
  which is the thing that does not help.

**The claim this supports, which no single paper states: once the prompt is
protected, the remaining headroom is in coverage, not in importance.** Better
scoring is the direction with the measured null result; coverage is the
direction with both the bound and the 10.35 points. For this skill that
replaces a flat "almost nothing beats the null" with a rule that tells a
builder where to spend: protect bilaterally, then decorrelate across heads, and
stop buying scorers.

### `2605.09649` -- Make Each Token Count / TrimKV (Bui et al., Yale/CUHK, 10 May 2026)

Queued as "the boundary case ... cited by Random Attention as prior work in the
regime this skill explicitly excludes." It is the boundary case and it is worth
holding for one sentence that is not a boundary at all: **full-cache attention
is not always optimal**, because irrelevant tokens dilute attention away from
the evidence, so eviction can *improve* generation rather than approximate it.
TrimKV is a trained method (learned retention gates, one global scoring
projection shared across layers and heads, so tokens from different layers,
heads and modalities compete for one budget) and therefore sits outside this
skill's training-free regime. It reports matching or surpassing full-cache
inference across long-context language, vision-language and multi-turn
dialogue.

`2512.12008` reports the same inversion independently and empirically: on
non-reasoning Llama-3.1-8B every compression strategy beats full cache on at
least one setting, and SnapKV-D beats full cache on reasoning models too. Two
sources, one direction. **A builder should not treat full cache as the
ceiling**, which is a different statement from anything in the skill today.

### `2602.10560` -- GRU-Mem (abstract only; arXiv serves no HTML)

The only one of the fifteen that did not yield full text, and the exit code
says so (`tools/read_paper.py` returns 3). Gated recurrent memory over MemAgent
with two text-controlled gates trained by end-to-end RL with their own reward
signals: the memory updates only when the update gate opens, and the loop exits
the moment the exit gate opens. Reported as generally outperforming vanilla
MemAgent **with up to 400% inference speed acceleration**.

**This matters for delta 2 and the skill should know it.** Delta 2's headline
is PARSER beating "the strongest sequential-memory baseline" by 5.7 points
average and 12.0 at 896K. PARSER's baselines are MemAgent and ReMemR1. GRU-Mem
is a later sequential-memory design that fixes the two defects PARSER's
argument exploits -- indiscriminate memory updates on evidence-free chunks, and
no exit once the evidence is in hand. Nobody has run PARSER against it. The
margin in claim 292 is therefore against the state of the art as of PARSER's
submission, not as of now, and the skill's confidence in "sequential memory
swings, parallel reading stays flat" rests on the older design.

### `2603.01229` -- RMBench (Chen et al., HKU/PKU/THU and others, v4 15 Oct 2026)

Queued as "the benchmark defining the task split" under a contradiction this
skill resolves. **The line is largely moot and the reason is this skill's own
history**: the sections that cited that cluster (claims 68-71, 111, 112, 115)
were cut on 2026-09-30 under ADR-38, so the skill no longer rests on it.

Worth one line anyway, because the finding generalises past robotics and lands
on how this library decides what a skill should contain. Nine memory-dependent
manipulation tasks, eight policies in simulation and four on physical hardware,
plus Mem-0, a modular policy whose memory components ablate independently. The
result: **the benefit of a memory component depends on whether the same
information is already reachable elsewhere in the policy hierarchy**, and the
dominant bottleneck is subtask termination detection rather than memory
representation. That is the same shape as this library's bare-arm screen -- a
component is worth its cost only where the capability is not already present by
another route -- arrived at independently in a field with hardware. It is
robotics, so it is an analogy and not evidence for an agent claim, and this note
says so rather than importing it.

---

## The regime boundary, which is the batch's most useful output for a builder

Three of the fifteen, read together, draw a line the skill does not have and
cannot draw from the papers it holds. A rigid prefix-plus-recency window is
either the right answer or a catastrophe, and which one depends on where the
evidence lives.

### `2608.26070` -- Prefix Sliding for efficient test-time scaling (Muennighoff et al., Stanford / UW / UCSB / Prime Intellect, 26 Aug 2026)

Queued as "the nearest signal-free alternative to the policy this skill
recommends and the one comparison Random Attention ran only in diagnostic
settings." It is now a full evaluation, from a group with weight, and it is the
strongest paper in the batch.

The method is one sentence: during reasoning, discard every token that is not
in the prefix or in the window of the last few thousand tokens. No score. One
hyperparameter, the window size. **Without any training it makes existing
models 3x faster at maintained performance**; with reinforcement learning it
scales to reasoning traces beyond a hundred thousand tokens at near-equal
memory, which raises reward. Their Figure 1 is careful about why: Prefix
Sliding wins "because it can generate more tokens in the same thinking time
than full attention, not because each token it generates is better."

**Its ablation is the fourth independent measurement of prompt protection, and
it is the cleanest of the four, because the prefix is the only variable.** The
sliding-window baseline is defined as "Prefix Sliding without prefix." It
"performs poorly on longer reasoning tasks," and the paper names the mechanism
in words a builder can act on: "the model forgets which problem it is solving
or **which tools it can use**." For an agent that prefix is the tool
definitions, and this is the measured cost of letting them age out.

Protect-the-prompt now has four independent sources, in four setups:

| source | setup | how the protection effect was isolated |
|---|---|---|
| `2609.03430` (held) | decode-phase per-head, reasoning | pin prompt, vary policy |
| `2605.18053` | globally capped decode, LongBench | protection sweep, 0 to 20% each side |
| `2512.12008` | long decode, reasoning | critical-token retention rate per method |
| `2608.26070` | test-time scaling, AIME25 and LCB | prefix ablated out of the method |

The charter's bar is three independent sources for a pattern. This is four, and
one of them is an ablation of nothing but the prefix.

It also lands on delta 2 from the other side. Its alternatives are last-k,
summary and plain sliding window; **Prefix Sliding gives the best performance
and efficiency tradeoff against all three**, and the paper's reading of why the
summary baseline loses is that models "struggle to retain important information
over many turns," plus the reprocessing cost of passing summarised tokens
through the model twice. That is delta 2's "map-reduce once is not it" in a
single-model setting rather than a multi-agent one.

**And the industry note worth carrying to the newsletter.** The paper names
summary-restart compaction as what Opus 4.6, GPT 5.4 and Composer do, cites
each, and then beats it on AIME25 at a 262144-token maximum. An artifact with
method, on the terms the charter's signal-and-evidence section sets.

### Where it fails, measured, and this is the boundary

- **LiveCodeBench needs a window of at least 16384 to match full attention**,
  against 4096 everywhere else. The diagnosis is specific: the model starts a
  function, thinks in comments for thousands of tokens, and by the time it
  returns to the code the beginning of the code has left the window. **The
  trace was load-bearing, and the paper says so.**
- **Short generations get nothing.** Below the window size the method is full
  attention. On HealthBench, which averages 2086 tokens against a 2048 window,
  there is no speed-up to have.
- **The agent case is the one the authors flag hardest, and it is this skill's
  case.** In agentic tasks a model reads a website or a file, and if that
  content is larger than the sliding window "it strictly cannot read the entire
  content. Even worse, it may lose important content, as its sliding window is
  flooded with this new output." Multi-turn raises the same question about where
  later user instructions go. They note the problem is shared by last-k and
  summary at the same window size, and their proposed mitigations are to teach
  the model to read in pieces rather than all at once, or to cap tool output
  before it reaches the context.

Set that against `2605.18053`'s sink-plus-window exception, which is the same
policy family in the opposite regime: SLW plus protection is significantly
worse than LRU plus protection at every capacity (0.184 against 0.282 at
C=256, p<0.001), because a rigid window "does not adaptively retain important
positions in the middle of the context." That paper's two-factor model is the
general statement: quality needs **structural protection of the boundaries**
and **adaptive middle retention**, and a fixed window satisfies the first and
fails the second.

**The boundary, stated for a builder:**

- The middle is **generated trace** and the evidence is in the prompt ->
  prefix plus window is right, needs no score, and is nearly free. This is
  reasoning and test-time scaling.
- The middle is **input** and the evidence is somewhere in it -> a rigid window
  is a catastrophe, and you need a policy whose eviction order depends on cache
  state. This is long-document QA, retrieval and agent loops that read files.
- The middle is **trace that later tokens index into**, as when a model writes
  code then comments past it -> the window must exceed the span of the
  reference, measured at 4x on LiveCodeBench.

No single paper in the batch says this. All three halves of it are measured.

### `2605.09490` -- Not All Thoughts Need HBM (Yuan, Shen, Zhang, USC / Wisconsin, 10 May 2026)

Queued because "the tiering evidence this skill cites is two video systems, so
the section's honest caveat is that no text-agent tiering result was read, and
this is it." It is, and the skill cut that section on 2026-09-30 for exactly the
reason the queue line gives. **The text result now exists and the cut can be
revisited on evidence rather than reversed on taste.**

Four tiers (HBM, DDR, compressed, evicted) by cumulative attention score. Low
importance tokens move to CPU memory instead of being destroyed, and are
prefetched back at full precision before each attention step, "contributing
exactly the same terms as if they had never left the GPU," which the paper
formalises as zero-approximation-error offloading. From that it derives the
finding that matters: **accuracy depends solely on the eviction ratio, not on
how many tokens remain in HBM**, confirmed on a controlled 3x3 grid over HBM
and eviction ratios across 7B, 14B and 32B and four benchmarks. At 3% eviction
it keeps 91% of full-cache accuracy on GSM8K and 71% on MATH-500 (n=200); at
14B it matches the uncompressed baseline (90% against 86%) at half the HBM. A
prototype with real GPU-to-CPU movement prices the preservation at **5-7%
transfer overhead**, and the scaling analysis projects 2-48 GB of HBM saved at
production batch sizes.

**And it carries the absolute number this skill is missing, which is the single
most important correction in this note.** Its opening sentence: permanently
evicting low-importance tokens is "catastrophic for reasoning: accuracy
collapses to 0-2.5% when half the cache is removed."

This skill's delta 1 is a **relative** finding -- protected-random is
competitive with the best scorer -- stated in a file whose checklist reads as
permission to compress. Random Attention's regime is 10 to 50 percent
compression. At the top of that range this paper measures reasoning accuracy at
0 to 2.5 percent. Both can be true at once, and a builder who reads "random
eviction is fine at 50% compression" out of the relative claim has been misled
by a true sentence. **The skill needs the absolute floor next to the relative
result**: choosing the policy is the cheap decision, and choosing the eviction
ratio is the one that decides whether the task survives at all. This paper's
contribution is that the ratio, not the placement, is the variable that binds.

### `2604.17935` -- How Much Cache Does Reasoning Need? (Wang, 20 Apr 2026)

Queued because "this skill can say what to protect and cannot say how large a
budget should be, and this is the paper that addresses the gap." It is theory,
on k-hop pointer chasing under a shared cache of size s with a
locality-respecting controller, and it addresses the gap in a shape the queue
line did not anticipate.

**It is also a direct theoretical argument against delta 1, and the first one
the corpus would hold.** Under random cache selection the paper establishes a
two-regime characterisation over T = ceil(log2 k) stages of windowed pointer
doubling: with oblivious caches the joint success probability is at most
(s/(n-T))^T + 2T^3/n, **decaying exponentially in T**; with adaptive
locality-respecting caches it is exactly s/n, **independent of T**, with
matching upper and lower bounds. The resulting Omega((n/s)^(T-1)) separation is
what the author says "quantifies why heavy-hitter eviction qualitatively
dominates random eviction for multi-hop reasoning."

**So the cost of the null policy is not a constant, it compounds with hop
depth.** That is a sharper boundary condition than anything in the skill's
caveats, which bound the regime by attention architecture, prompt length and
compression ratio and say nothing about the dependency depth of the task.

Three honesties about how far it reaches, because the paper is explicit about
all three. The product lower bound is **conjectured**, with the remaining gap
isolated as a named open problem; only the max-bound and a matching upper bound
are proved unconditionally. The product bound binds quantitatively only in the
narrow or low-precision regime (H*m*p roughly below log n), and the paper
proves a **barrier theorem**: no depth lower bound provable by per-window
distinguishability counting can exceed ceil(k/s) once H*m*p >= log2 n, which is
where standard LLM configurations sit. And pointer chasing is a proxy, not a
reasoning benchmark.

What a builder can take from it: the depth you need scales with **ceil(k/s)**,
hops over cache size, so cache size buys hop depth roughly linearly, and the
budget question has the form "how many hops does my task need" rather than "how
many tokens is my context."

**The two theory results in this batch point opposite ways and both are worth
holding.** `2604.17935` says random eviction amplifies error with hop depth.
`2606.29563` says coverage bounds accuracy and random eviction per head
maximises coverage. They are not in conflict: coverage is about whether a token
is retained **somewhere** across heads, and error amplification is about
whether a **particular** token on the dependency chain survives **every** stage.
A policy can be the best available way to cover an input and still be the worst
available way to carry one chain, and multi-hop is exactly where those come
apart. That reconciliation is what the skill should carry, and neither paper
states it.

---

## Delta 2: the condition the skill does not state, and two papers that state it

Delta 2 tells a builder to chunk, bind a reader to each chunk, and run rounds.
It does not say when chunking is the wrong move. Four of the fifteen are about
exactly that, and two of them hand the skill its missing condition.

### `2506.16411` -- When Does Divide and Conquer Work for Long Context LLM? (Xu, Zhu, Wang, Wang, Athiwaratkun, Wang, Zou, Zhang; Chicago / Together AI / Duke / Google DeepMind / Stanford, v2 28 Feb 2026)

Queued as "the paper that says when chunking fails," and it is, with a
decomposition the skill can use as written. Three noise terms:

- **task noise** -- cross-chunk dependence, which chunking creates,
- **model noise** -- confusion that grows with context size, which chunking removes,
- **aggregator noise** -- imperfect integration of partial results, which chunking adds.

Chunking wins when the model noise it removes exceeds the task and aggregator
noise it adds, and the paper's experiments on retrieval, QA and summarisation
confirm both the analysis and the conditions. **That is the conditional delta 2
is missing.** The skill's step 1 reads "chunk, and keep chunks small," full
stop; the honest version is to chunk when the input is long enough that model
noise dominates, keep chunks large enough that cross-chunk dependence stays
inside them, and treat the aggregator as a noise source to be measured rather
than a wire.

It also independently predicts the skill's most quotable number. Delta 2 cites
PARSER's 9B beating a frontier model with a native million-token window by 6.3
points. This paper derives and demonstrates the same inversion from the
accelerated decay of model fidelity with input length: for large inputs **a
weaker model with chunk-based processing can surpass a stronger model applied
in a single shot**, naming GPT-4o. Earlier, theoretical, and independent of
PARSER. The frontier-model inversion is therefore a property of the regime, not
a property of PARSER, and the skill can say so.

### `2505.20625` -- XpandA (Xiao, Lin, Gao, Chen, Zhang; Zhejiang / Westlake, v3 28 Sep 2025)

Queued to "separate the architecture's contribution from the reinforcement
learning's," and it separates them cleanly: **XpandA is untrained.** Dynamic
partitioning, question-driven updates to keep knowledge consistent across
partitions, and selective replay of partitions to handle information presented
out of order. Evaluated from 1k to 1M tokens, it reports **20% improvement and
1.5x inference speedup over full-context, RAG and prior agent-based baselines.**

**The answer to the queue's question is that the architecture carries most of
it and needs no training.** A builder reading delta 2 today might reasonably
conclude the prescription requires training a lead agent. It does not: the
question-driven, replay-capable partition loop delivers 20% over three baseline
families with no training at all, and PARSER's training buys the increment on
top. Delta 2's step 4, "train only the lead if you train anything," is right and
its conditional is now load-bearing rather than decorative.

Note the design difference, because it is the one knob between them. XpandA
**replays selected partitions** when the order of information demands it;
PARSER **re-reads every chunk every round**. Replay-on-demand is the cheaper
half of the property delta 2 says matters, and both beat one-shot map-reduce.

### `2603.09835` -- Chow-Liu Ordering for Long-Context Reasoning in Chain-of-Agents (Gupta, Singh, Iyer, Shiragur, Grover, Bairi, Maiti, Damle, Mishra Gupta, Maurya, Vageesh D. C.; Microsoft, 10 Mar 2026)

Queued as the paper on "whether the order chunks are visited can be chosen
rather than inherited, which is the assumption PARSER removes by reading all
chunks every round." The queue line is exactly right and the paper confirms the
framing from the other side.

Chain-of-Agents passes bounded summaries between sequential workers, which the
paper describes as a lossy information bottleneck that makes the final evidence
state **depend on the order chunks were processed in**. They learn a Chow-Liu
tree over chunk dependencies and visit chunks by breadth-first traversal of it,
which beats both default document order and semantic-score ordering on answer
relevance and exact match across three long-context benchmarks.

**Read against delta 2, this is the cost of the sequential family stated as a
positive result.** Order dependence is real and large enough that choosing the
order well is worth a paper; a method that re-reads every chunk under a fresh
query each round has no order to choose, which is the same property claim 293
reports as flatness under permuted evidence position and dependency order. The
two findings are the same fact from the two sides, and the skill can cite the
sequential side now instead of asserting the parallel side alone.

### `2605.15184` -- Is Grep All You Need? (Sen, Kasturi, Lumer, Gulati, Subbiah; PricewaterhouseCoopers, 14 May 2026)

Queued because "PARSER runs shell-tool subagents as a drop-in variant, and this
skill's suggestion that subagents return a checkable span leans on that line of
work." It does more than lean. **It is the first evidence in this batch for
delta 2's step 5, which the skill labels "ours, not the paper's."**

116 questions from LongMemEval-S, four harnesses (a custom one called Chronos
plus Claude Code, Codex and Gemini CLI), grep-only against vector-only, under
two delivery paths: results inline in the tool message, or written to a file the
model must open.

- **Inline grep exceeds inline vector for every harness-model pair evaluated.**
  The paper's reading is that LongMemEval answers "are often licensed by a small
  set of literal spans," so lexical precision wins.
- **The harness moves the result more than the retriever does.** Scores depend
  strongly on harness and tool-calling style with the conversation data fixed,
  and file-based delivery or a provider CLI shell can "invert or erase the
  lexical advantage without any change to the corpus."
- **File-based delivery is the context-pressure trade, priced.** Writing results
  to disk "decouples retrieval result size from context window pressure," and
  the cost is that the agent must complete a locate-open-integrate cycle. Where
  that cycle is brittle, "accuracy can collapse independently of retrieval
  quality." They record an extreme regression for Codex with GPT-5.4 under
  programmatic grep and draw the rule: programmatic routing trades context
  bandwidth for compositional tool competence.

Two things for this library. First, a grep hit **is** a quoted span with a
location, so lexical retrieval supplies delta 2's step-5 verifiability by
construction rather than by instruction, and it is the retrieval mode that won
inline in every pair here. Second, "retrieval is really
retrieval-plus-orchestration" is a harness-engineering finding found inside a
retrieval paper, and it belongs in that skill's lane as much as this one.

### `2605.29307` -- GrepSeek (Salemi, Zeng, Nijasure, Chung, Rahimi, Diaz, Zamani; UMass Amherst / Princeton / CMU, v2 30 Sep 2026)

"The trained half of the same question," as queued. The agent treats the corpus
as the environment and finds evidence with executable shell commands. Two-stage
training: initialise on verified, causally grounded trajectories from an
answer-aware Tutor and an answer-blind Planner, then refine with GRPO. Across
eight open-domain QA benchmarks it is strongest overall, a statistically
significant **5.7% relative improvement over the best baseline**.

The systems numbers are the part worth the corpus's space, because they answer
the obvious objection to shell-based search: **Pruned Adaptive Command
Execution cuts shell search latency by up to 77x on a 14GB corpus of 21 million
documents** using a compact auxiliary structure, and **Sharded-Parallel Corpus
Search adds up to 7.6x**, both semantics-preserving. Direct corpus interaction
is not slow; the naive implementation of it was.

The answer-aware Tutor and answer-blind Planner split is worth one more line,
because it is the same shape as PARSER's lead that never sees the document.
Both keep the component that composes the query from seeing what it is supposed
to find. Two papers, two subfields, one design rule.

### `2404.06654` -- RULER (Hsieh, Sun, Kriman, Acharya, Rekesh, Jia, Zhang, Ginsburg; NVIDIA, v3 06 Aug 2024)

Queued because "PARSER reports ten additional tasks on it in its appendix; the
skill cites the multi-hop QA result and cannot say what happens on the non-QA
half." The non-QA half is three further categories, and this is what they test:
retrieval with diverse needle types and counts, **multi-hop tracing** by variable
tracking as a proxy for coreference chains, and **aggregation**. Seventeen
long-context models, thirteen tasks. The headline is still the useful one two
years on: **nearly perfect vanilla needle-in-a-haystack accuracy coexists with
large drops as context grows, and of the models claiming 32K or more, only half
hold up at 32K.**

RULER settles a different queue line than the one it was filed under, and that
is recorded in the no-id section below.

Also worth knowing before anyone leans on `2605.18053`: its limitations name
strict needle-in-a-haystack retrieval "(e.g. RULER)" as untested. The
protection result is measured on LongBench QA, multi-document summarisation and
a 64K needle probe on one model, and the benchmark built to catch long-context
over-claiming is the one it has not run.

---

## The four works with no arXiv id

- **MemAgent (Yu et al., ICLR 2026)** -- still needs its own route, but its
  design is now in the corpus by description from two citing papers.
  `2602.10560` states it precisely: chunk-by-chunk processing in an RNN-like
  loop with a textual memory updated at each step, and the two defects that
  motivated its successor (indiscriminate updates, including on evidence-free
  chunks, and no exit once enough evidence is in hand). A claim about MemAgent's
  **design** can be sourced; a claim about its **numbers** cannot.
- **ReMemR1 (Shi et al., 2026)** -- nothing in this batch supplies a route. Stays
  queued.
- **Context rot (Hong et al., 2025, Chroma technical report)** -- **resolved, and
  the line can be struck.** It was queued as "the named source for the premise
  that accuracy degrades before the window is full, which this skill states in
  its description." That premise does not need a vendor technical report. RULER
  (`2404.06654`) measures it across seventeen models and thirteen tasks, and
  three separate papers in this batch cite RULER as Hsieh et al. 2024 for
  exactly that premise (`2506.16411`, `2603.09835`, and `2512.12008` in its
  introduction). **Point the skill's description at RULER.** The Chroma report
  may still be interesting, but nothing load-bearing depends on it now.
- **Lost in the middle (Liu et al., TACL 2024)** -- **substitutable on the same
  grounds, with a bonus.** It was queued as "the positional-bias result the
  buried-evidence activation condition rests on." `2606.29563` re-measures
  positional bias **inside the eviction setting**, which is stronger for this
  skill's purpose than the original: its Figure 3 shows retained token coverage
  skewing heavily toward the end of the input "despite the correct answer
  appearing first in this example." `2605.18053` reports the same thing as
  "position-stratified retention explains the H2O reversal." So the activation
  condition has in-corpus, arXiv-identified support, and it now rests on
  measurements of the compaction systems rather than on a result about raw
  prompts.

---

## The three questions, answered

### Q1 -- "How often do real agent traces contain a fact stated once and needed more than a budget later?"

**Still not measured, and the question is now better posed: the quantity that
binds is not frequency, it is dependency depth.**

Nothing in the batch counts the frequency, and the batch makes a good case that
counting it would not settle the decision anyway.

- `2604.17935` gives the shape of the cost. Under random cache selection with
  oblivious caches the joint success probability decays **exponentially in the
  number of stages T**; with adaptive caches it is s/n, flat in T. So one fact
  needed once later is survivable and a chain of k such facts is not, and the
  penalty is a function of the chain, not of the trace length. A frequency
  statistic over traces would average over exactly the variable that matters.
- `2608.26070` supplies a measured instance class rather than a rate.
  LiveCodeBench is the case: a reference written early and consumed thousands of
  tokens later, costing a 4x larger window (16384 against 4096) to match full
  attention. One benchmark in a suite, which is an existence proof and an order
  of magnitude for the price.
- `2512.12008` supplies the nearest thing to a measurement, and it is a good
  proxy nobody has pointed at this question. Its **critical-token retention
  rate** is the fraction of the question's critical tokens (names, quantities,
  key entities) still in cache at the final decoding step, reported per method
  across models and budgets in its Table 8. That is "a fact stated once and
  needed later" instrumented directly. It is measured on GSM8K questions rather
  than on agent traces, so the number does not transfer, but **the instrument
  does**, and it is cheap.
- `2605.15184` says the case is the normal case in long-memory QA rather than the
  exception: LongMemEval answers "are often licensed by a small set of literal
  spans," which is why lexical retrieval beat dense inline in every pair.

**Restated for whoever takes it next:** instrument critical-token retention over
real agent traces, stratified by the number of hops between a fact's statement
and its use, and report retention as a function of hop distance rather than a
single rate. The `2512.12008` definition is reusable as written.

### Q2 -- "Does the protect-the-input finding survive on architectures without per-head independence, such as multi-head latent attention or multi-query attention?"

**Partly answered, and the part that landed is stronger than the question
expected. The two named architectures are still untested, in both papers.**

`2605.18053` replicates protection across ten models in five vendor families,
and three of its points span the head-diversity axis the question is about:

- **Phi-3.5-mini, full multi-head attention, 32 KV heads.**
- **Mistral-7B-Instruct-v0.3, grouped-query attention, 8 KV heads.**
- **Qwen3.5-27B, hybrid DeltaNet plus GQA, where only 25% of layers evict a KV
  cache at all** and the rest carry recurrent state. The author calls this the
  strongest generality test and the reasoning is right: if protection still
  helps where three quarters of the layers are not doing attention, the
  vulnerability belongs to KV-cache eviction rather than to transformers.
  Protection held there.

So the **protection** half transfers from 32 KV heads down to 8 and across into
a hybrid recurrent stack. The **per-head scoring** half is the one that depends
on head diversity, and the paper measures its size rather than asserting it:
faithful per-head Ada-KV and QUEST recover near-ceiling quality at both K=32
(Phi-3.5, 93% and 92%) and K=8 (Mistral-7B, 95% and 94%), worth roughly
0.03-0.04 F1 over the simplified variants against a protection lift of
0.11-0.14 F1. The skill's caveat that "under multi-query or latent attention
only the prompt protection carries over" is a reasonable inference and is now
**supported in direction** by a hybrid result, while remaining unmeasured on the
two architectures it names: `2605.18053` states plainly that "mixture-of-experts
and multi-latent-attention architectures remain untested," and Random Attention
tested four grouped-query models. **Keep the caveat, and cite the hybrid result
as the reason to believe it rather than leaving it an inference.**

### Q3 -- "Is there a text-agent equivalent of the shallow-layer index, where a cheap partial forward pass builds the retrieval structure and the full model only runs at answer time?"

**No, and the two nearest results in this batch both put the cheap layer
somewhere better than shallow depth, which is the more useful answer.**

- **Below the model.** `2605.09490` is a placement layer, not a scoring method,
  in its own words. Four tiers, cumulative attention scoring, and zero
  approximation error because offloaded tokens are prefetched back at full
  precision. The cheap tier is DDR rather than a shallow forward pass, the price
  is 5-7% transfer overhead, and the payoff is the finding that accuracy tracks
  the eviction ratio and ignores HBM occupancy. This is the text result the
  video-only tiering caveat asked for, at 7B, 14B and 32B.
- **Outside the model.** `2605.29307` makes the corpus the index: a compact
  auxiliary structure plus pruned adaptive command execution gives up to 77x
  latency reduction over 21 million documents, with sharding adding 7.6x, both
  semantics-preserving. The retrieval structure is built once, cheaply, and is
  not a forward pass at all.

Nothing in the batch builds a retrieval structure from a partial forward pass of
the same model on text. **The question stays open in its original form and
should probably be retired in it**: the two measured text answers move the cheap
layer out of the network rather than up to its shallow layers, and both report
real numbers, which the shallow-layer framing does not have outside video.
