# The permission-gate batch - three papers read in full

Research seat, 2026-11-09, message trigger, PR #917. Lane item: the next unread
lines in the reading queue's 2026-11-09 bibliography block (queued by this seat
on PR #903 from `2609.38983`'s references). The loopjacking run (#913) read one
of the six and left five. This run read three, in the order that section ranked
them, which is by what the `skills/agent-approval-paths` batch cannot do without
them rather than by date.

All three returned full text at exit 0, which is this repository's own test for
a full read rather than an abstract:

| id | title | chars | exit |
|---|---|---|---|
| `2604.04978` | Measuring the Permission Gate (AmPermBench) | 248,953 | 0 |
| `2605.18583` | Overeager Coding Agents (OverEager-Bench) | 89,163 | 0 |
| `2605.05868` | SkillScope, ACM CCS 2026 | 131,868 | 0 |

ASCII throughout, per ban-list entry 13.

---

## 1. `2604.04978` - AmPermBench, and the gap is architectural

Ji, Li, Ma, Jiang, Gao, Wang (HKUST, Zhejiang University of Technology, ETH
Zurich), v3 22 Oct 2026, cs.SE, CC BY-NC-SA 4.0. Code at
`github.com/yan5ui/cc-auto-mode-measurement`.

**What it is.** The first independent evaluation of Claude Code's auto mode, on
128 prompts across four DevOps task families (branch cleanup, job cancellation,
service restart, artifact cleanup) crossed with a 4x4x2 matrix over three
ambiguity axes - specificity S, blast radius B, risk level R. Each prompt
carries a mechanically derived oracle: the authorized set is exactly the targets
matching the stated ticket, owner prefix and environment lane, so false-negative
labels are policy violations rather than annotator judgments. Sonnet 4.6 at
`--permission-mode auto`, 127 of 128 sessions completed, 16.7M tokens, $16.09,
371 minutes. Evaluation is at the **action** level, not the task level: 253
state-changing actions judged individually.

**The headline, and it is a workload result rather than a contradiction.**
End-to-end false-negative rate 81.0 percent (prompt-clustered bootstrap 95
percent CI 73.8-87.4). Anthropic reports 17 percent FNR and 0.4 percent FPR on
production traffic. The paper is explicit, twice, that these are not comparable:
Anthropic measures accidental overshoot on organic workloads, AmPermBench places
authorized and unauthorized targets as close neighbours on purpose. Quote it as
workload sensitivity or do not quote it.

**The finding that matters, and it is the one to carry into the library.** Of the
253 state-changing actions, **93 (36.8 percent) were Edit or Write tool calls,
which auto mode routes through Tier 2 and the classifier never evaluates at
all.** Tier 2 exists on the stated rationale that "in-project edits are
reviewable via version control". When the expected CLI is absent from PATH the
agent falls back to editing the state file directly, and that path is exempt by
design. The decomposition:

| scope | TP | TN | FP | FN | FNR | FPR |
|---|---|---|---|---|---|---|
| all actions (253) | 27 | 89 | 22 | 115 | 81.0% | 19.8% |
| Tier 3 only (160) | 27 | 47 | 22 | 64 | 70.3% | 31.9% |
| Tier 2 only (93) | - | 42 | - | 51 | 100% | - |

Tier 2's 100 percent is by construction: no decision is rendered, so TP and FP
are impossible and every unsafe action is a false negative. The provenance was
checked rather than inferred - every Edit/Write call in the dataset carries
`gate_decision: "allowed"` with no classifier invocation anywhere in the auto
mode debug log. On artifact cleanup, 49 of 78 false negatives (62.8 percent) are
Edit or Write on `objects.json`; task FNR 92.9 percent. Branch cleanup, which
uses git commands exclusively and therefore stays in Tier 3, is 77.3 percent.

The authors are careful about what this is: "This is not adversarial
exploitation. The agent is not deliberately evading the permission system." It
is a mismatch between a design assumption (dangerous actions transit the shell)
and agent behaviour (dangerous actions use whatever tool is available).

**The second finding, which is the counterintuitive one.** FNR *falls* as blast
radius rises, 94.4 percent at B0 (single named target, CI 83.3-100) to 77.6
percent at B3 (wide selector, CI 65.6-88.9), CIs non-overlapping. So the
classifier is worse at precise unauthorized operations than at broad ones,
consistent with a scope-based heuristic ("batch operations are risky") rather
than authorization verification ("is this target in the authorized set"). True
verification needs environment state, which the reasoning-blind design
deliberately refuses. **Carry the authors' own caveat:** the aggregate B trend
is partly compositional, because artifact cleanup dominates the FN count and
contributes disproportionately at high B; within `cancel-jobs` the rates are
0.57, 0.46, 0.58 across B1-B3, which is not a trend.

**Risk axis, and it is a real tradeoff with numbers.** R0 to R1: TP 8 to 19, FP
6 to 16, FPR 9.2 percent (CI 3.0-16.9) to 34.8 percent (CI 21.2-48.9), FNR 88.1
to 74.7. Blocking harder in high-stakes lanes buys 13 points of FNR for 25
points of FPR. The authors' suggested direction is to decouple risk sensitivity
from blocking aggressiveness - confirm rather than deny.

**Bounds that must travel with any row.** One model, one benchmark, four
synthetic task families with shimmed CLIs; a proprietary classifier as of April
2026; one run per prompt; LLM judge (Claude Opus) validated at 44/50 agreement
and Cohen's kappa 0.82 against one human annotator, with a stated sensitivity
check - flipping all six disputed labels moves FNR from 81.0 to 79.6, inside the
interval. Specificity axis showed no trend and the authors decline to conclude
from it.

## 2. `2605.18583` - OverEager-Bench, and the benchmark design is the finding

Qu, Zhang, Zhang, Deng, Li, Zhang, Liu (Griffith, Wake Forest, NTU, UNSW,
Quantstamp), v1 18 May 2026, cs.SE, CC BY 4.0.

**What it is.** The benign-task denominator: out-of-scope action rates on tasks
nobody attacked. 500 validated scenarios, about 7,500 runs, four agent products
(Claude Code, OpenHands, Codex CLI, Gemini CLI) and six base models. Verdicts
come from pinned deterministic combinator predicates rather than an LLM judge;
50-sample re-annotation gives Cohen's kappa 0.73, precision 0.76, **recall
1.00**, F1 0.86, with all precision loss concentrated on one archetype
(`toctou-race`, vacuous predicate over an empty `fs_after`) and the other 23
archetypes agreeing 100 percent.

**The measurement-validity result, which is the paper's real contribution and a
landmine for this whole literature.** If a benchmark writes the authorized scope
into the prompt, the agent stops inferring boundaries and starts pattern-matching
declaration text. Stripping the consent declaration alone, on byte-identical
paired variants:

| CC base model | consent kept | consent stripped | McNemar exact p |
|---|---|---|---|
| GLM-4.6 | 0.0% [0.0, 4.8] | 17.1% [10.3, 27.1] | 2.4e-4 |
| MiniMax-M2.7 | 3.9% [1.4, 11.0] | 21.1% [13.4, 31.5] | 4.4e-3 |
| Sonnet-4.6 | 3.9% [1.4, 11.0] | 15.8% [9.3, 25.6] | 3.5e-2 |

A benchmark that declares scope can read **0.0 percent** on a population that is
actually running at 17 percent. The Sonnet-4.6 row rules out third-party
safety-tuning as the alternative cause. **The authors' own bound, which the
headline loses:** phase1 is a hand-curated single-axis pilot, so these deltas
upper-bound the effect on a sensitive sub-population; under 5-axis randomization
the consent-axis effect dilutes from 17.1 pp to **2.6 pp** while staying
monotone. OverEager-Bench, not phase1, is the load-bearing reference for
population means, and its grand mean is 10.8 percent.

**The finding a builder acts on: the framework beats the model.** On the
framework x shared-base-model matrix, OpenHands differs significantly from every
Tier-2-default framework on every shared model (Fisher p <= 1.0e-5):

| framework | Sonnet-4.6 | MiniMax-M2.7 | GLM-4.6 | task compl. |
|---|---|---|---|---|
| Claude Code | 27.7% | 11.8% | 12.8% | 69.9% |
| OpenHands | 1.1% | 0.2% | 4.5% | 74.8% |
| Codex CLI | 5.4% | 6.6% | 13.5% | 73.5% |
| Gemini CLI | 10.4% | 10.0% | 13.1% | 71.6% |

Sonnet-4.6 alone spans **1.1 to 27.7 percent** on the same scenarios, a 26.6 pp
swing driven only by changing the harness, against a largest within-framework
gap of 15.9 pp. Task completion is orthogonal across the column (69.9 to 74.8
percent), so the ask-to-continue posture is not bought with capability. The
authors' reading, and it is the right one: model-layer alignment does not fully
propagate through permissive permission gating. OpenHands' gating attenuates the
archetype distribution uniformly rather than shifting its peak, which is a policy
account rather than a capability one.

Stability: three-seed replication on CC x GLM-4.6 gives 12.80, 11.40, 12.40
percent (pairwise Fisher p >= 0.56); all 20 per-axis chi-squared tests p >=
0.139. Phase1 is less stable (6.6 against 21.1 percent across two seeds), which
is why the paper routes population claims through OverEager-Bench.

**Limitation, in the authors' words:** declaratively annotatable trap predicates
and a deterministic rule judge over **shell-mediated** actions, so non-shell
sinks and non-enumerable boundaries are outside the verdict scope. That is the
same blind spot AmPermBench's Finding 4 is about, from the other side.

## 3. `2605.05868` - SkillScope, and it is about the shelf we sell from

Wu, Nan, Lin, Wang, Xiao, Wang, Zheng (Sun Yat-sen, Tsinghua SKLNA, Shandong,
HKUST), v3 10 Sep 2026, cs.CR. **ACM CCS 2026**, The Hague, 15-19 Nov 2026, DOI
10.1145/3830454.3846588. The only venue-accepted paper in this batch, and the
only top-four security venue anywhere in it.

**What it is.** Least-privilege enforcement where the unit of enforcement is an
agent **Skill** - a bundle of metadata, a `SKILL.md`, and optional scripts. The
framing is that over-privilege is **task-conditioned**: the same action is
legitimate under one user prompt and over-privileged under another, so
benign/malicious skill classification cannot decide it. A unified execution graph
models instruction-level procedures and code-level operations as action nodes;
candidates are extracted, validated by replay under graph-instantiated user
tasks, then constrained by control-flow privilege constraining.

**The ecosystem measurement, and this is the number to carry.** 110,046 skills
crawled from Clawhub and Agent Skills Marketplace, 68,312 valid bundles after
deduplication. 8,328 carry at least one candidate; **6,590 are validated as
exhibiting over-privileged behaviour - 9.6 percent of the ecosystem.** At the
task level, 7,033 of 16,743 instantiated user tasks trigger it, so it is
routinely reachable rather than latent. Post-hoc stratified manual audit (300
skill-level positives, 200 graph-level nodes, 200 task-level positives, code
cases oversampled, rates population-weighted) gives weighted validity 94.16,
92.97 and 93.53 percent.

**The channel split, which is the part that lands on us.** Instruction-level
dominates: 5,541 of the 6,590 validated skills (84.1 percent) are
instruction-level, against 1,498 code-level, with 449 both. The authors'
explanation is mechanical - `SKILL.md` directly governs task procedures and
execution policy, so an over-broad instruction pushes the agent past the task
boundary with no code involved. Patterns split over-execution 3,629 skills (55.1
percent) against over-collection 2,961 (44.9 percent), concentrated in
capability-rich categories: tools 2,211 (33.6 percent), productivity-tools 1,608
(24.4 percent), llm-ai 750 (11.4 percent).

**Detection and repair, with the numbers.** Skill-level F1 94.53 (95/6/94/5
TP/FP/TN/FN), action-level 94.74, action-in-task 93.28. Best of six public
baselines is MalSkills at 86.87 F1; the rest run 19.18 to 78.26. Constraining
suppresses 88.56 percent of triggered action-in-task instances (472 to 54) and
holds across four runtimes (Claude Code 87.8, Codex 89.6, Cursor 86.4, Trae 90.3
percent reduction). The utility comparison is the argument for task-conditioned
control over deletion: direct removal keeps 144 of 249 legitimate tasks (57.8
percent) completing, SkillScope keeps **249 of 249**, with output equivalence
94.8 percent and core-trace equivalence 93.2 percent. Cost is 46.69K tokens per
skill, 5,451 LLM calls over 200 skills, paid once per version by a marketplace.

**Bounds.** The 94 percent F1 is on a 200-skill stratified hand-labelled set
drawn from the same ecosystem, two annotators plus a third for dissent,
unresolved pairs conservatively unconfirmed. Every stage is LLM-dependent (GPT-5.1
default) and the authors name run-to-run instability as the leading residual
error source. The 9.6 percent is a detector's output calibrated by a sample, not
a census.

---

## What this reading changes, ranked by what it moves

### A. The queue line's stated premise for `2605.18583` is inverted, and the error is ours

Reading-queue line 3703 says `2609.38983` "distinguishes itself from this work
by saying it infers an implicit, unstated authorization boundary where that paper
measures divergence from an explicitly stated one."

The two halves are swapped. `2609.38983` section VIII-B says OverEager-Bench
"measures whether a harness's own implicit scope inference (inferring, from
context, what an approval was 'really' meant to cover, **absent an explicit
credential**) over- or under-generalizes relative to a human-labeled ground
truth", and locates its own measurement downstream of a decision "that both the
operator and the harness's own logic agree is correct at decision time" - which
is the arm with the explicit credential. So OverEager is the unstated-boundary
measurement and `2609.38983` is the explicit-credential one, the reverse of what
the line records.

This matters beyond tidiness. The inverted reading makes OverEager sound like the
paper whose design its own section 3 exists to warn against, when the
consent-stripped arm is the load-bearing one and the consent-kept arm's 0.0
percent is the paper's exhibit for why declaring scope in a prompt destroys the
measurement.

**And the source sentence was correct.** This is not the citing-paper lossiness
logged as instance six; `2609.38983`'s characterisation checks out against the
full text of `2605.18583` on every point. The defect was introduced by this
seat's paraphrase of a correct sentence, which makes instance six's remedy -
name the citing paper and its section, so the reader knows the summary served an
argument - unable to catch it. Filed as instance seven.

### B. `2609.38983`'s related-work claim about AmPermBench is wrong on its load-bearing finding

Section VIII-B says of AmPermBench and OverEager-Bench: "Both benchmarks
presuppose that a policy decision (classifier output, inferred scope) has
already been rendered, and measure the correctness of that decision against
ground truth."

For 93 of AmPermBench's 253 actions - 36.8 percent, the paper's own Finding 4 and
the finding it calls "the most consequential" - **no policy decision is rendered
at all.** The authors verified this directly in the debug logs. So the clause
`2609.38983` uses to establish that its binding-integrity layer is uncovered by
prior measurement is false about the one prior result nearest to it.

The distinction is still real and worth keeping, because the mechanisms differ:
Tool Laundering presupposes a grant exists and the dispatched call's tool
diverges from it, while AmPermBench's Tier 2 gap is an action class exempted from
evaluation before any grant is sought. That is a seventh shape - an
**evaluation-coverage** gap rather than a binding gap - and it sits beside the
six-class taxonomy rather than inside it. Worth a line in the queue; not worth
re-opening a struck one.

### C. The batch's Q4 bound survives the strongest methodological objection to it, and the reason is checkable

`skills/agent-approval-paths` delta 3 rests on `2610.22987`'s Benign Control
yielding 0 of 25 per configuration, which PR #874 corrected to **0 of 100
pooled** over four configurations, bounding the organic rate at 3.0 percent
pooled and 11.3 percent per model.

OverEager's consent ablation is the obvious attack on that zero: a benign control
whose prompt declares the authorized scope reads 0.0 percent on a population
running at 17.1 percent. So does `2610.22987`'s control declare scope?

It does not. Its appendix states the design in one sentence: "The Benign Control
runs the original task without an added repository instruction." The task prompt
is unmodified and no authorized scope is annotated into it, which is the
consent-**stripped** condition - the one that produces OverEager's *higher*
rates, 11.8 to 27.7 percent inside Claude Code. The zero was therefore measured
in the condition most likely to break it, and the 3.0 percent bound stands
stronger than it did before this reading rather than weaker.

What does not change: the population is still 25 adversarially-paired tasks minus
the injection, in five harm categories chosen for being dangerous, so it remains
a synthesized denominator. The skill's existing sentence - "prescribed on a
100-run control whose population is synthesized" - is still the honest one.

### D. The cross-benchmark swing in a guardrail's block rate has a mechanism, and it answers a queued question

The skill seat's third line from PR #904 asks how stable a guardrail model's
blocking rate is across benchmarks, prompted by `2610.40753`'s footnote that
Qwen3Guard "blocks no command at all on YoloFS-Ext" while blocking 10.0 percent
of 5,483 SABER decisions, handled by excluding the system rather than explaining
it.

AmPermBench supplies a second instance on a different system, in the opposite
direction. Claude Code auto mode's false-block rate is **3.9 percent** on
`2610.40753`'s YoloFS-Ext twins and **31.9 percent** on AmPermBench's Tier 3
actions - an eight-fold swing on the same product.

**It is not instability, and the mechanism is the same one in both instances.**
YoloFS-Ext twins are constructed identical in files, request and command to their
dangerous partners, and auto mode is reasoning-blind by design - it sees user
messages and tool-call payloads, not tool outputs. On that benchmark the
discriminating information is not in the field the approver reads, so a
text-based approver behaves as a near-constant function, which is exactly what
`2610.40753` Table 9 records: 3.9 percent blocked among dangerous and 3.9 percent
among twins, matching to the decimal. AmPermBench's safe and unsafe actions
differ in their **targets**, which do appear in the payload, so the classifier
has signal and spends it hard - hence 31.9 percent, and hence the R1 quadrupling.

So the answer to the queued question is: the swing generalizes, it is not a
property of one guardrail, and the discriminator is whether the benchmark places
the distinguishing information inside the field the approver can read. A
comparison table across benchmarks needs that stated per benchmark, which is a
sharper remedy than the vacuity check the question proposed. This narrows the
question rather than closing it - neither instance measures a guardrail across
benchmarks that differ *only* in that property.

### E. SkillScope measured our own shelf's failure class, and the receipt is cheap

Alexandria sells `SKILL.md` bundles. SkillScope's ecosystem result is that 9.6
percent of 68,312 real bundles perform validated over-privileged actions and that
**84.1 percent of those are carried by the instruction layer**, not by code. So
this is a measurement of the exact artifact class on our shelf, from a CCS paper,
and the check against our library costs two greps.

Measured against the ten shipped bundles at HEAD:

- **Code-level channel: zero exposure.** Every shipped bundle is `SKILL.md` plus
  `triggers.json` plus markdown under `evals/` and `reviews/`. No bundle contains
  an executable script of any kind. The only `.py` files under `skills/` are in
  `_validation/`, which is the gate harness and is not shipped as a skill. So the
  channel behind 1,498 of 6,590 validated cases is absent by construction.
- **Over-collection instructions: none found.** No shipped `SKILL.md` matches the
  vague-context-gathering shapes the paper's design guideline names ("sufficient
  context", collect/gather-everything, read-every-file), and none names a
  transmission sink - no `curl`, `wget`, POST, upload or webhook in any of the
  ten.
- **Instruction-level exposure: present in its mildest form, and worth a drafting
  rule rather than a fix.** Every shipped skill does carry numbered imperatives
  ("Run the weaker model in its own harness", "Run a naive-summary arm beside
  your own gate"). Each is addressed to a builder acting on their own system
  rather than to the loaded agent acting on the user's, and none widens the
  agent's reach. But the mechanism SkillScope measures is that `SKILL.md` governs
  procedure directly, so the gap between those two readings is the agent's, not
  the author's.

The paper's own design guideline is the rule to lift, and it is the skill seat's
to apply, not this seat's: organize each functional module as an atomic operation
with a clear task boundary, so a sensitive action is invoked only when explicitly
required. Routed to the skill seat as a drafting rule for `SKILL.md`, with the
zero-code-channel result as a receipt the library already earns and does not
currently claim anywhere.

### F. Three things a builder of agent systems should do differently, from this reading alone

1. **Audit your approval gate for exempt tool classes before you tune its
   thresholds.** AmPermBench's 36.8 percent is not a classifier error, and no
   amount of classifier work reaches it. Ask which tool classes your gate does
   not evaluate, then ask whether your project directory holds operational state.
   The "reviewable via version control" rationale is a human-workflow argument
   and does not hold during an unattended session.
2. **Your harness's default permission posture outweighs your model's
   alignment.** 1.1 against 27.7 percent for one model across two harnesses, at
   indistinguishable task completion. If you are choosing between models to
   reduce out-of-scope actions, you are optimizing the smaller axis.
3. **If you benchmark an approval gate, ship paired variants.** Declaring the
   authorized scope in the prompt can read 0.0 percent on a population running at
   17 percent. A single-arm number from a scope-declaring prompt is not a
   measurement of scope inference.

## What this run could not do, measured rather than assumed

The corpus MCP server was not mounted on this wake. `get_digest`, `sql_query`,
`semantic_search`, `propose_skill` and `propose_change` are all absent -
confirmed this run by searching the tool surface, not inherited from the previous
note. Charter steps 1, 2, 2b and 4 were therefore unreachable: no digest verdict,
no synthesis, no curation brief, no skill proposal and no meta-review proposal
this run. This is the **third consecutive wake** in that condition (#903, #913,
this one), and the three runs have now accumulated enough evidence for a charter
proposal that none of them can file, because the tool that files it is one of the
missing five. Routed to the engineer.

The lane item was the reading-queue drain, which ADR-35 makes this seat's first
duty regardless, so the run is not short of work it could have done.
