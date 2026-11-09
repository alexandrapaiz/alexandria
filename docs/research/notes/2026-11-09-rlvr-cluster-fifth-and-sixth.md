# The RLVR cluster finished: papers five and six read in full, and the opponent the cluster was missing

Research seat, 2026-11-09, PR #854. Closes the read-first cluster that PR #760
measured out of the chair's RLVR batch of 2026-10-05 in
`docs/research/reading-queue.md`. #760 ranked the batch and read papers one and
two; PR #796 read three and four and corrected the cluster's question; this run
reads **five and six**, which is the last of the six, and then checks the
finished cluster against the live field.

Both read with `python3 tools/read_paper.py`, exit 0, full text off
`arxiv.org/html`. Every number below carries the table or section it came from.

| # | id | read by | citations at #760's measurement |
|---|---|---|---|
| 1 | `2609.04108` Sequential Beats Joint | #760 | 12 |
| 2 | `2609.04565` Extremely Sparse Supervision | #760 | 6 |
| 3 | `2609.35259` On-Policy or Off-Policy Learning? | #796 | 1 |
| 4 | `2609.28385` When and Where to Trust the Teacher | #796 | 1 |
| 5 | `2609.37868` GRAFT | **this run** | 0 |
| 6 | `2609.16639` ReDraft | **this run** | 1 |

## `arxiv:2609.37868` -- Learning Beyond What You Sample (GRAFT)

https://arxiv.org/abs/2609.37868 -- Jang, Park, Chu, Park, Yang (KAIST,
AITRICS), v1 of 2026-09-29, arXiv perpetual non-exclusive license. Full text,
88,962 characters.

GRPO learns only from reward variation inside a rollout group, so a group where
all eight samples fail carries no gradient. GRAFT replaces such a group with a
peer model's group on the same prompt, keeping the peer's own advantages, and
controls the mismatch with a sequence-level compatibility gate and token-level
ratio clipping. No designated teacher: the two models are peers and exchange in
both directions.

1. **The headline reproduces, and the averages reproduce from their own
   cells.** Table 1, six model blocks over MATH500, AIME2024, AIME2025, AMC23
   and Minerva. SmolLM3-3B in Pair 1: 76.86, 14.42, 14.50, 50.87, 28.68, which
   averages to 37.066 against the printed 37.06, over GRPO (n=8) at 32.60, a
   lead of 4.46. The six block deltas are 4.46, 0.66, 2.24, 1.58, 2.29 and
   1.42, which average 2.108 against the abstract's "2.1 points on average".
   Checked by arithmetic, not taken.
2. **Three independent training runs exist and the main table is not them.**
   Appendix C repeats GRPO (n=8) and GRAFT three times per pair and reports
   sample standard deviations; Table 1 reports the **first** run of each
   setting. The three-run means are lower: SmolLM3 Pair 1 GRAFT 36.12 +/- 0.85
   against GRPO 32.15 +/- 1.48, so the +4.46 of the headline is +3.97 as a mean.
   A reader who quotes 4.46 is quoting one run.
3. **The boundary the paper states softly and the table states sharply.** The
   prose says only that gains are "largest on Pair 1 and the smallest on Pair
   3". The table says more than that. On Pair 3, SmolLM3's GRAFT average is
   33.26 against **33.38 for plain GRPO at n=16** and 35.71 at n=32 -- so on
   that pair the model would do better doubling its own rollout budget than
   exchanging with a peer, and better still quadrupling it, while GRAFT also
   pays for a second model's training. Of the six blocks, GRAFT clears GRPO
   (n=32) in four; the two it does not are **both** Pair 3 blocks, and Pair 3
   is the only pair that does not contain Qwen3-1.7B-Base. Per Appendix C the
   Pair 3 SmolLM3 delta is +0.91 against a baseline whose own run-to-run
   standard deviation is 1.48, so it is not separated from training noise.
4. **The load-bearing component is mismatch control, not the exchange.**
   Table 2(a): removing the compatibility gate costs SmolLM3 8.36 points,
   larger than the whole method's gain, and removing the compatibility floor
   costs Qwen3 3.56. Random prompt selection costs 2.40 and 1.58. So the
   result is not "peer data helps"; it is "peer data helps when it is weighted
   by how close it is to you."
5. **Transferring only the peer's successes is worse than not transferring at
   all.** Table 2(b), "success-only": 29.22 for SmolLM3 against full GRAFT's
   37.06 and against **plain GRPO's 32.60**. The naive reading of cross-model
   learning -- hand the learner the correct solutions -- is 3.4 points below
   doing nothing, on this pair. The failed peer responses are what make the
   group's advantages mean anything, because the advantages are computed
   within the peer group and a success-only group has nothing to be relative
   to.
6. **The compute claim, and what it is charged against.** Section 6.1:
   GRAFT reaches a pair-mean 35.25 at 40.9 GPU-hours, 1.18 points over GRPO
   (n=32) at 0.45x its compute. Appendix D's conservative rule charges each
   cross-model run the **full joint cost of both models**, which is the right
   accounting and is the one the figure uses. Section 6.2: the peer need not be
   live -- replaying a partner's **stored** GRPO logs keeps 1.78 of the 2.11
   average points, 84% of the online gain, at 27-76% less compute, in all six
   blocks. That is the version a builder can actually run.

Scope, so nothing above is over-read: base models at most 3B, two-model pairs
only, mathematics only, verifiable rewards only, and the authors name all four
as limits. The compatibility score is a proxy rather than a density ratio
across tokenizers, which they also say.

## `arxiv:2609.16639` -- ReDraft, Don't Just Distill

https://arxiv.org/abs/2609.16639 -- Zhang, Wu, Dong et al. (Fudan, Shanghai AI
Laboratory), v3 of 2026-09-22. Full text, 137,990 characters. The batch's only
multi-modal line, so it is also the cluster's only Layer 3 multi-modal
contribution.

The problem is continual post-training: learn a task the model cannot do while
keeping what it could. SFT supplies explicit targets and forgets; on-policy
methods stay close to the policy and supply almost no signal when nothing
sampled is correct. ReDraft samples a rollout, has the model **revise its own
wrong rollout** against an expert reference, keeps the revision only if a
verifier accepts it, and fine-tunes on the survivors.

1. **The two-axis result.** Section 5.1, Qwen2.5-VL-3B and 7B over Counting,
   Jigsaw and Clock Reading, retention macro-averaged over eight prior
   benchmarks: target gain 56.9 points against SFT's 52.9, prior-task loss
   1.5 against 16.6, which is the 11.3x less forgetting of the abstract. On the
   two genuine cold-start tasks (base accuracy at most 5.25%) it gains 79.4
   against SFT's 73.8 and OPSD's 26.0.
2. **On-policy self-distillation's plateau is the objective, not the budget,
   and the paper tested that rather than asserting it.** Table 2: 70% more
   steps buy OPSD 4.1 points (19.3 to 23.4 mean gain) and it stays 31.7 behind
   ReDraft on Clock Reading, with ReDraft reaching its number in fewer steps
   (367 against 762). This is the cleanest available answer to "is the
   on-policy arm merely under-trained."
3. **Verifier-only methods need a success to exist first.** GRPO improved only
   7B Jigsaw, where correct orderings are occasionally sampled; elsewhere
   reward rose on the format term rather than accuracy (Appendix B.2).
   Rejection sampling on Counting, where base accuracy is 44.0/52.3%, gained
   1.0/1.3 against ReDraft's 12.8/11.4. Revision converts a failure into a
   positive target; rejection sampling can only keep successes.
4. **Three measurements of proximity, all pointing the same way.** Answer-only
   perplexity under the frozen base model: self-revisions 1.62 against expert
   trajectories 5.33 at 3B (70% lower) and 1.47 against 5.90 at 7B; the
   model's own rollout is 1.30, the floor. Weight displacement orders
   SFT > ReDraft > OPSD at (6.52, 5.59, 4.13)e-3. Update direction:
   cos(SFT, ReDraft) = +0.272 against +0.135 for cos(SFT, OPSD), concentrated
   in the vocabulary tensors (+0.76 against +0.39). The mechanism is measured
   in three spaces, which is the part worth borrowing.
5. **A scale threshold that is about revising, not about solving.** Section 7.
   The main experiments' revision instruction states the target answer, which
   makes repair easy -- the authors flag this as the STaR shortcut. Withhold the
   answer and the verifier accepts 0.6% and 2.5% of 3B revisions on Clock
   Reading and Jigsaw, 17.2% and 18.8% at 7B, and 99.5% and 96.8% at 32B.
   Across the same scales first-attempt accuracy moves only 0.0% to 0.9% and
   3.3% to 13.5%. **What scales is the ability to revise against a reference,
   not the ability to do the task** -- and at 3B the revision usually returns
   the original answer unchanged, so the method's own precondition fails there.
   ReDraft* moves the revision to the expert (edit the rollout, do not replace
   it) and recovers most of the advantage at 3B: Clock Reading 85.8 against
   SFT's 76.4 with retention 72.5 against 71.8.
6. **The boundary that has to travel with every number above: there is no
   dispersion anywhere in this paper.** Searched: "seed", "std", "standard
   deviation", "error bar", "variance", "significan", "confidence interval",
   "95%" -- **zero occurrences of each**. Evaluation is avg@8 at temperature
   0.7, one training run per condition. So the 4.0-point target-gain margin
   over SFT (56.9 against 52.9) has nothing measured to be read against, and in
   mixed training at 7B ReDraft actually ends behind SFT on target accuracy
   (68.6 against 69.5). The **forgetting** result is a different size of claim
   -- 1.5 against 16.6, and 78.4 against 31.6 retention at 7B mixed -- and is
   large enough to survive plausible run-to-run noise. Quote the retention
   number; do not quote the acquisition margin as a win.

Other limits the authors state: an automatic verifier is required, each failed
rollout costs an extra generation pass, the revised set is built once from the
starting policy so targets go stale as weights move, and the self-distillation
family is represented by OPSD without its pointwise clipping, with SDFT not
evaluated.

## What the finished cluster says

The six papers were assembled by subject, and read end to end they are not six
answers to one question. They are six positions on **one axis that none of them
names**: how far the thing you train on sits from what your policy would have
produced, and whether you control that distance deliberately or inherit it from
who generated the rollout.

Laid out on that axis:

- `2609.35259` holds the pipeline fixed and finds that **rollout policy is not
  the variable**. Forward KL holds 71-73% across every rollout policy and
  learning rate; reverse KL spans 35-72%. The forward-KL update difference
  between two rollout policies is bounded linearly by the total-variation
  distance between prefix distributions (appendix C proof), which says in so
  many words that proximity is the quantity and provenance is a proxy for it.
- `2609.16639` measures proximity directly as answer-only perplexity and
  constructs a target that is explicit **and** proximal, beating both the pure
  off-policy and the pure on-policy arm on both axes at once.
- `2609.37868` takes data from a different model entirely and makes it work by
  weighting it by a compatibility score -- and loses 8.36 points when that
  weighting is removed. Same quantity, third instrument.
- `2609.04565` pushes the same idea to its limit: supervise one or two tokens
  per trajectory, 0.05% of them, and match full-token distillation. Minimal
  displacement, maximal explicitness.
- `2609.04108` is the staging result, and staging is one way to get both
  properties sequentially rather than within one update.
- `2609.28385` is the one that measures the mechanism rigorously and the
  comparison loosely, which #796 established.

**Three independent groups measuring the same quantity with three different
instruments** -- a TV-distance bound on prefix distributions, a compatibility
score across tokenizers, and answer-only perplexity under the frozen base
model -- is the charter's bar for a pattern rather than a finding. The pattern:
*post-training methods in this cluster succeed to the degree they control the
distance between the training target and the current policy, and the on-policy
versus off-policy framing is a crude proxy for that distance that the
controlled evidence does not support.*

**And the cluster is not a conversation.** Checked pairwise by grep across all
five full texts in hand: `2609.04108` cites neither GRAFT nor ReDraft nor the
two papers found below; GRAFT cites neither ReDraft nor `2609.04108`; ReDraft
cites neither. #796 already found that `2609.28385` and `2609.04108` never
meet. Six papers, one question, mutual silence. That is a fact about the
cluster that matters to the graph: an edge marked `contradicts` between any
pair of these would assert an exchange that does not exist in either text. The
right edge is unreconciled comparison.

## The opponent the cluster was missing, found by the live check

L-R1 requires an ecosystem check against the live web every run. This run's
check was on the cluster's own question and it returned two papers the queue
does not hold and, on the ask's own terms, the corpus probably does not either.

**`arxiv:2608.24696` -- On-policy Distillation with Verifiable Reward (OPDVR).**
Lin, Zhao, Jiang et al., LeapLab Tsinghua / Qiuzhen / Beihang / Peking /
NLPLab, v4 of 2026-09-29, code at github.com/LeapLabTHU/OPDVR. It reformulates
sampled-token OPD's implicit reward on trajectory correctness and applies a
ReLU gate so correct trajectories get non-negative and incorrect ones
non-positive reward, turning OPD into a proper RLVR method combinable with any
policy-gradient algorithm, **with no added hyperparameters**, and reports
consistent gains over standard OPD on six reasoning benchmarks. This is the
joint design done well, which makes it **the counterparty `2609.04108`'s title
is arguing with** -- the role #760 assigned to `2609.28385` and #796 showed it
cannot fill. Its v1 id puts it in August 2026, before `2609.04108` of
2026-09-03, and `2609.04108` does not cite it.

**`arxiv:2605.12652` -- Multi-Rollout On-Policy Distillation via Peer Successes
and Failures (MOPD).** Yu, Li, Zhao et al., Carnegie Mellon / Microsoft /
Purdue, v2 of 2026-06-01, code at github.com/viviable/mopd_code. It conditions
the teacher on the student's own successful **and failed** peer rollouts,
contrasting the two, over competitive programming, mathematics, science QA and
tool use, and finds mixed success-failure contexts align teacher scores with
verifier rewards better than successes alone. That is GRAFT's finding 5 arrived
at four months earlier in the single-model case, and GRAFT does not cite it.
Two independent groups, two designs, same result: **the failures carry the
signal.** This is now a pattern rather than one table.

Neither is a correction to the cluster. Both are the cluster's missing
interlocutors, and both are queued below rather than claimed here.

## What a builder should do differently, bounded

If you are staging post-training as distil-then-RLVR: the staging is supported
(`2609.04108`, logic reasoning) and the on-policy part of stage one is not
(`2609.35259`, under control), so run the off-policy arm as a baseline before
paying for generation throughout training. #796 established that line and
nothing read this run moves it.

Added this run. First, if your target task is one the model cannot do at all,
neither arm is the answer: verifier-only methods have no success to learn from
(`2609.16639` section 5.1) and plain SFT buys the task at 11x the forgetting,
so revise a failed rollout into a verified target instead -- and check your
model is large enough to revise against a reference before you rely on it doing
so, because that capability breaks below roughly 7B independently of task
competence (section 7). Second, if you are sharing trajectories between models
or between rollouts, transfer the failures too; success-only transfer scored
**below the no-transfer baseline** in GRAFT's Table 2(b) and MOPD reaches the
same conclusion by a different route. Third, treat "on-policy" as a proxy for
"close to the current policy" and measure the thing itself -- answer-only
perplexity under the frozen base model is the cheapest of the three instruments
in this cluster and needs no training run to compute.

All of it is bounded to students between 0.6B and 7B, short-to-medium traces,
and tasks with automatic verifiers. No paper in the cluster tested a
frontier-scale student.

## The ranking, measured against what actually reads this file

#760 routed a traction field to the engineer. #796 added that a citation count
cannot resolve a tie inside this cluster, because the two papers at one citation
turned out to be the weakest and the strongest of the four then read. This run
adds the third constraint, and it is the one that decides the design.

`pipeline/reading_queue.py --order` on this branch, today:

```
arxiv:2609.18411  skills/agent-approval-paths  line 3482  blocked  NEXT
arxiv:2606.02668  skills/agent-approval-paths  line 3483  blocked  NEXT
arxiv:2610.22987  skills/agent-approval-paths  line 3484  blocked  NEXT
arxiv:2609.08371  skills/agent-containment     line 220   waits    NEXT
arxiv:2609.40115  the chair                    line 338   waits    NEXT
arxiv:2609.40360  the chair                    line 339   waits    NEXT
```

`MAX_PER_RUN` is 6 of 97 pending. Two of the six slots reach the chair's batch
and **both go to lines measured at zero citations**, while `2609.04108` -- 12
citations, and published at Findings of EMNLP 2026, pages 13252-13270,
Budapest, confirmed live this run at aclanthology.org/2026.findings-emnlp.631 --
sits at file line 360, twenty-two lines down. #760's annotations are prose, and
`pending()` orders by file position, so **the re-rank is invisible to the only
consumer that acts on this file.** Filed as a register entry this run.

The repair is not to move the lines. `pending()`'s own docstring argues against
that in writing: it reversed classification and deduplication in order to
remove its dependence on line position precisely because "line position in this
file is decided by whichever merge landed last", and it records two merges of
identical content giving different reading orders. Re-sorting a 24-line batch by
hand would be betting on the property that module deliberately stopped trusting.

So the field the engineer was handed is still the right fix, and it now has a
specification:

1. **Declared in the line and parsed**, not written in prose above the batch. A
   human-readable ranking has now failed to reach `pending()` once, which is one
   more time than a guess.
2. **Used as a sort key within a group**, after the blocked-skill grouping that
   `pending()` already does correctly and must keep.
3. **Not citation count alone.** Three signals this seat can gather without
   waiting five weeks for the field to cite anything: venue acceptance (one
   fetch; it is what separates `2609.04108` from every other line in its batch
   and a citation count would not have found it for another month), the
   evidence markers the reading itself records (#796's "3 seeds, SEM" against
   nothing), and recency as the last tiebreak rather than the only key.

Nothing in this note is asserted as a claim row. There is no corpus route from
this host -- `DATABASE_URL`, `NEON_RO_URL` and `NEON_URL` all unset, `import
psycopg` raises `ModuleNotFoundError`, `command -v modal` finds nothing, no
`~/.modal.toml` -- so the chair's ask, which is corpus presence, is met by one
distill run and not by any reading. It waits on board card `6a5e4ad5`.

## Routed, not applied

- **To the skill seat:** findings 1-6 on GRAFT and 1-6 on ReDraft. The
  extraction target is the proximity axis above, and it is now a six-paper
  cluster with three independent instruments rather than the two-paper
  disagreement #796 left. The shelf is training-loops, where
  `self-improving-post-training-loops` already stands gold; ReDraft's section 7
  threshold also belongs wherever a skill advises choosing a model size for a
  self-correction loop.
- **To the engineer:** the three-point specification above, and the measured
  fact that two of six distill slots currently go to zero-citation lines.
- **To the chair, through the PM:** `2608.24696` and `2605.12652` are queued as
  additions to the RLVR batch rather than silently folded into it, because the
  batch is the chair's and this seat does not extend another's ask without
  saying so.
