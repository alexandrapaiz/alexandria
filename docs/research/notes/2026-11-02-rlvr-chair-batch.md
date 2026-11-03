# The chair's RLVR reading-queue batch, measured and ranked

Research seat, 2026-11-02, PR #760. Working note behind the drain of
`docs/research/reading-queue.md` lines 285-308, the batch the chair queued on
2026-10-05 under "make sure the corpus includes RLVR", 28 days open.

## Why this batch and not another

The lane had nothing to continue. Zero research cards in Backlog, This sprint
and In progress; the two in Review were PR #746 and PR #742, both merged and
both verified on the trunk before being moved to Done. So the charter's
standing first duty applies, which is to drain the reading queue oldest-first.

`python3 pipeline/reading_queue.py --order` prints the queue's own ordering. It
puts `arxiv:2609.08371` first, which four consecutive runs of this seat have
re-derived as blocked on a compute workspace no seat can switch on, and then
the five `NEXT` lines after it are this batch's first five.

## The measurement nobody had taken

The batch is 24 open lines and 3 struck ones. In 28 days no run recorded a
single number about any of them beyond the arXiv id and the title the chair
typed. The relevance law says every ranking this seat produces orders by
evidenced impact and uses recency only as a tiebreak, and a batch with no
impact measurement cannot be ordered that way, so it was ordered by the one
field it had, which is the id.

Citation counts, Semantic Scholar graph API, batch endpoint, fetched
2026-11-02 and re-performable:

```bash
python3 - <<'PY'
import urllib.request, json
ids = "2609.04108 2609.04565 2609.12191 2609.09075 2609.06107".split()
body = json.dumps({"ids": [f"arXiv:{i}" for i in ids]}).encode()
url = ("https://api.semanticscholar.org/graph/v1/paper/batch"
       "?fields=title,citationCount,publicationDate")
req = urllib.request.Request(url, data=body, headers={
    "User-Agent": "alexandria-research/1.0", "Content-Type": "application/json"})
print(urllib.request.urlopen(req, timeout=60).read().decode())
PY
```

The endpoint answers 429 on the single-paper route under load and 200 on the
batch route, so the batch route is the one to use. All 24 ids resolve and all
24 titles match the queue line, so nothing in this batch is mis-queued.

| cites | id | published | title |
|------:|----|-----------|-------|
| 12 | 2609.04108 | 2026-09-03 | Sequential Beats Joint: On-Policy Distillation and RLVR |
| 6 | 2609.04565 | 2026-09-03 | Extremely Sparse Supervision Incentivizes Reasoning Ability |
| 3 | 2609.12191 | 2026-09-10 | GAUGE: When Not to Trust LLM-as-a-Judge |
| 3 | 2609.09075 | 2026-09-08 | ThinkPrior: Zero-Rollout Difficulty Priors |
| 2 | 2609.06107 | 2026-09-05 | DataFlex-RL: An Evaluation Platform for RLVR Data Policies |
| 1 | 2609.40115 | 2026-09-30 | Unlearnable, or Unmeasured? Difficulty Labels in RLVR |
| 1 | 2609.35677 | 2026-09-28 | Verifier Errors in RLVR |
| 1 | 2609.35259 | 2026-09-28 | On-Policy or Off-Policy Learning? Distillation Dynamics |
| 1 | 2609.34857 | 2026-09-28 | Beyond Verbalized Confidence |
| 1 | 2609.28385 | 2026-09-23 | When and Where to Trust the Teacher |
| 1 | 2609.16639 | 2026-09-15 | ReDraft, Don't Just Distill |
| 0 | 2609.40360 | 2026-09-30 | Semifactual Credit-Augmented Policy Optimization |
| 0 | 2609.39533 | 2026-09-30 | CATCH: Reward Hacking in Coding RL |
| 0 | 2609.37868 | 2026-09-29 | Learning Beyond What You Sample (GRAFT) |
| 0 | 2609.37825 | 2026-09-29 | Privy to the Foil |
| 0 | 2609.28765 | 2026-09-23 | RLVR for Small Search Agents |
| 0 | 2609.24380 | 2026-09-21 | Information-Time Proximal Policy Optimization |
| 0 | 2609.23053 | 2026-09-19 | Attributable Post-Rationalization in RAG Citations |
| 0 | 2609.15987 | 2026-09-14 | Bellman Policy Optimization |
| 0 | 2609.10315 | 2026-09-09 | TRACE: Causal Exploration with Synthesized Rewards |
| 0 | 2609.05111 | 2026-09-04 | Unifying ICL, SFT and KL-Regularized RL |
| 0 | 2609.00444 | 2026-08-31 | Group Adaptive Clipping Policy Optimization |
| 0 | 2608.29188 | 2026-08-29 | Locked at the Entrance, Open Inside |
| 0 | 2608.27046 | 2026-08-27 | Parallel and Distributed Reasoning Language Models |

**The confound, stated before the claim that rests on it.** At one to two
months out, a raw citation count is mostly a measure of how long the paper has
been available, and in this table the count does correlate with publication
date. So the ranking is normalized by days since publication before anything is
concluded from it:

| id | days | cites | per day |
|----|-----:|------:|--------:|
| 2609.04108 | 60 | 12 | 0.200 |
| 2609.04565 | 60 | 6 | 0.100 |
| 2609.12191 | 53 | 3 | 0.057 |
| 2609.09075 | 55 | 3 | 0.055 |
| 2609.06107 | 58 | 2 | 0.034 |
| 2609.40115 | 33 | 1 | 0.030 |

The leader survives the normalization: `2609.04108` is 2.0x the runner-up on
rate as well as on count, and 3.5x the third. That is thin evidence in absolute
terms and it is stated as thin, but it is the only evidence anybody has
gathered about this batch, and it points the same way twice.

## The finding: the queue serves this batch in the one order the law forbids

The queue's order for these 24 lines is the order the chair typed them, which
is newest-first by arXiv id. Lines 285-289, the five the queue marks `NEXT` and
therefore the five a returning distill run would read first, hold **1, 0, 0, 0
and 0 citations**. The paper with 12 sits at line 305, twenty-first of
twenty-four.

So the next six papers this system would read are six of the least-cited in the
batch, and the most-cited one is last. The charter calls a ranking that reads
as a release-date feed a violation of the relevance law, and this one is a
release-date feed in both directions at once: newest-first by construction, and
therefore least-traction-first by consequence.

Nothing in `pipeline/reading_queue.py` is at fault for the content of the
order. `pending()` groups by blocked skill and otherwise preserves file order,
which is the correct behaviour for a file whose contract is append-only. The
defect is that no stage between "the chair types 27 ids" and "a distill run
takes the first six" has any impact signal to sort on. Routed to the engineer
as one field rather than as a rewrite: a queue line that carries a traction
number can be sorted by it, and the number is one batch API call for the whole
file.

## The cluster, which is the extraction target

Six of the 24 lines are one subject: how teacher supervision and verifiable
reward combine, and whether the rollout policy should be the student's or the
teacher's. Confirmed by reading each abstract first-hand rather than by
matching titles.

- `2609.04108` Sequential Beats Joint (12 cites)
- `2609.04565` Extremely Sparse Supervision (6)
- `2609.35259` On-Policy or Off-Policy Learning? (1)
- `2609.28385` When and Where to Trust the Teacher, UECR-GRPO (1)
- `2609.16639` ReDraft, for continual multimodal post-training (1)
- `2609.37868` GRAFT, cross-model trajectory exchange (0)

Those six lines are 25% of the batch and hold **21 of its 32 citations**, which
is 66%. The other eighteen lines are eighteen separate policy-optimization
variants holding 11 citations between them, and nine of those eighteen hold
zero.

That is the shape of the batch, and it is not what the batch's own ordering
says it is. On the evidence available, the month's live question in this layer
is not which clipping or credit-assignment variant wins. It is **on-policy
distillation and what happens when you put it next to RLVR**, which is a
question about staging a post-training pipeline and therefore a question a
builder acts on.

## Read in full this run

### `arxiv:2609.04108` -- Sequential Beats Joint

https://arxiv.org/abs/2609.04108 -- Li, Chen, Yang, Nie, Zhao, Ye (NYU, Chicago,
Waterloo, NYU Shanghai, Alberta/Amii), v2 of 2026-09-04, CC BY 4.0. Read as
full text, 82,275 characters, `python3 tools/read_paper.py 2609.04108`, exit 0.

Claim-grade findings, each with where it is measured:

1. **Two-stage beats every single-step fusion.** Running on-policy distillation
   to step 60 and then switching to GRPO reaches the best average pass@1 on
   both task families, 80.6 on logic and 31.8 on math, and leads the other
   combination methods by 11.7 to 26.7 points on logic (section 4.2, Table 2). On
   math the lead is significant against six of nine competitors and a
   statistical tie with the strongest three, by paired problem-level bootstrap.
   On pass@32 no method is significantly ahead of it on either family.
2. **The two signals interfere, and the interference is visible in the
   weights.** Sign-conflict rate against the distillation update, over the
   top-K% of parameters by distillation-update magnitude (section 5.3, Table 3): pure
   RL conflicts on 20.36% of K&K parameters at top-100%, the weighted-additive
   joint method on 15.02%, the teacher-modulated one on 6.58%, and the
   sequential recipe on 3.38%, near zero at top-10%. The sequential recipe's
   conflicts sit in the low-magnitude tail, so the distillation directions that
   matter survive the RL stage intact.
3. **The division of labour is measured, not asserted.** Distillation lifts the
   whole pass@k curve and widens the pass@128 minus pass@1 gap; RL narrows that
   gap by moving probability mass to pass@1 (section 5.1). Expansion then sharpening,
   in that order, and the order is the whole result.
4. **Where the joint methods look fine, and why that is the trap.** On logic
   tasks, where the teacher has little prior exposure, every combination beats
   both pure baselines. On math, where the teacher is heavily post-trained,
   most joint methods fall below pure distillation on pass@1 (avg -1.2 for
   weighted-additive), and the weighted-additive family buys +4.8 pass@1 on
   logic at a cost of -2.0 pass@32. A builder who evaluates a fusion on one
   task family gets the opposite answer from one who evaluates on the other.
5. **The switch point has a readable signal.** The distillation validation
   score at the switch is what propagates: on K&K and Zebra, where that score
   keeps rising to step 100, a later switch wins; on Countdown, where it
   saturates by step 20, all three switch points converge (section 6, Figure 10).
   So the rule is switch at saturation, and switching early caps the ceiling.
6. **Distillation is a better cold start for RL than supervised fine-tuning.**
   Same teacher, GRPO on DeepMath: 30.3 against 25.4 pass@1 before RL, a 4.9
   point gap, which widens after RL to +7.2 average pass@32, 51.3 to 58.5.
   Supervised-fine-tuning-then-RL gains marginal pass@1 and consistently
   degrades pass@32 (section 6, Appendix C.2, Table 8).

Scope, so the claims are not over-read: Qwen3-8B teacher in non-thinking mode,
Qwen3-1.7B-Base student with Qwen3-0.6B-Base replicated in Appendix B, three
ReasoningGym logic tasks and DeepMath-103K for math, pass@1 as avg@32. All
methods trained under one total step budget. Code at
`github.com/StringNLPLAB/opd-rlvr`.

### `arxiv:2609.04565` -- Extremely Sparse Supervision Incentivizes Reasoning Ability

https://arxiv.org/abs/2609.04565 -- read as full text, 113,007 characters,
`python3 tools/read_paper.py 2609.04565`, exit 0.

1. **One or two tokens per trajectory is enough.** In the on-policy
   distillation setting, supervising as few as one or two generated tokens per
   reasoning trajectory, about **0.05% of all tokens**, in most cases matches
   or surpasses full-token training on reasoning ability. Held across nine
   teacher-student configurations on mathematical reasoning, and separately
   validated on coding reasoning, on Llama models, and under PPO-based RLVR.
2. **Even the random single token works.** Three single-token variants are
   compared: `maxtok` and `mintok` pick the most positively and most negatively
   rewarded token, `rand1tok` picks at random (Figure 1, AIME 2025, Qwen3-8B
   student from a Qwen3-4B-Instruct-2507 teacher). `maxtok` beats both plain
   distillation and the teacher; `mintok` matches plain distillation; and
   `rand1tok` still substantially improves on the base student. The selection
   rule is worth something, and most of the effect does not depend on it.
3. **The measured boundary, which is the half an abstract loses.** Extending to
   Gemma 3, Gemma 4 and Mistral 3, **plain sampled-token distillation did not
   improve the students at all**, and the authors name the likely cause as not
   having run supervised fine-tuning on the student first (section 7). The sparse
   result is built on successful distillation, so it inherits that
   precondition. Any advice drawn from this paper holds for Qwen3 and,
   less strongly, Llama, and is unevidenced for Gemma and Mistral.

### What the two together say that neither says alone

Both are from 2026-09-03, both are the batch's two most-cited papers by a
factor of two over everything else, and both land on the same place: in
post-training, the **density and the staging** of teacher supervision are now
the variables that move the number, not the policy-optimization objective.
One says do not mix the two signals in a single update; the other says the
dense signal did not need to be dense. Eighteen of the other lines in this
batch are new objectives.

Both also share a scope limit that the corpus should carry with the claims:
the Qwen3 family is the testbed, and one of the two papers reports that the
phenomenon fails to appear on two other model families.

## What is still owed, and by whom

The chair's ask is **corpus presence**, and this run cannot meet it. The three
lines struck in PR #228 were struck on a `papers` query, and there is no route
from this host to that database. Checked live rather than carried forward:

```bash
echo "${DATABASE_URL:-absent}"      # absent
python3 -c "import psycopg"         # ModuleNotFoundError
command -v modal                    # nothing
ls ~/.modal.toml                    # No such file or directory
```

`mcp/server.py:303` makes `sql_query` read-only besides, so even a credential
would not insert these papers; the only `insert into claims` outside `tests/`
is in `pipeline/distill.py` and it runs on Modal. The workspace has answered
"workspace is disabled" since 2026-10-23 and the board card for it is
`6a5e4ad5`, in This sprint, owner-blocked.

So what this run delivers against the chair's ask is not corpus presence. It is
the ordering for the one distill run that will meet it, so that the first six
papers read when the workspace returns are the six that carry two thirds of the
batch's citations instead of the six the chair happened to type first, plus two
of those six read in full here so the evidence exists in the repository in the
meantime.

**Ingestion order for the engineer, when the workspace returns:**
`2609.04108`, `2609.04565`, `2609.35259`, `2609.28385`, `2609.37868`,
`2609.16639`, then `2609.12191`, `2609.09075`, `2609.06107`, then the rest in
any order.
