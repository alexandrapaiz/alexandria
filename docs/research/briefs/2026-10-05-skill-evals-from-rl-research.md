# Brief — testing and refining skills, from the RL feedback research

Owner directive 2026-10-05: "look at all the RL feedback / evaluation /
refinement methods and use that research to develop testing and refinements
for the skills." Research seat, PR #220. The chair's decision record is
ADR-40 in docs/decisions.md; this is the full brief under it, with the papers
read in full per ADR-35.

`NEON_RO_URL` was set. The corpus was read read-only with psql; no writes, no
credentials printed, `digests/` and `skills/` untouched. Papers were read as
arXiv full HTML where it exists and at the abstract where it does not; which
one is said for each paper below, because the difference changed three
findings.

The week's curation brief is `docs/research/briefs/2026-10-05.md`, written by
this seat's containment dispatch (PR #210, now carried by #220). This file
does not restate it. Section 8 below is the curation addendum for the
skills-and-evals lane only.

## 0. Four corrections to ADR-40, found by reading the papers

ADR-40 is sound in its structure, and its seven testing items are the right
seven. Reading its seventeen cited claims against the papers they come from
changed four things, and all four change what the engineer should build.

**C934 does not say what item 6 cites it for.** Item 6 ends "length and style
effects are checked by scoring the same content at two lengths (C934)." C934
reads: "Auditing the physical nature of evaluation inputs (e.g., OCR quality)
should precede architectural changes, and the leaderboard's bimodal
performance distribution is explained by reading quality rather than
reasoning ability." That is input-quality auditing, not judge length bias.
The practice in item 6 is worth keeping — it is standard — but the corpus
does not currently evidence it, and the citation should be struck rather than
carried. C934 belongs in item 6 under its own meaning: audit the inputs a
task hands the subject before concluding anything about the subject.

**ScienceBuddy is an example of the gate item 2 warns against, not an
example of the gate it prescribes.** Item 2 pairs SkillOpt (C865) and
ScienceBuddy (C392) as though both gate on held-out tasks. They differ on
exactly the point that matters. SkillOpt accepts an edit "only when it
strictly improves a held-out validation score" (read in full,
arxiv.org/abs/2605.23904). C392 says ScienceBuddy accepts bounded edits
"only if they improve mean normalized rubric scores **on development
tasks**" — the tasks the edit was written against. ScienceBuddy's abstract
page does not mention a held-out set or discuss overfitting to dev tasks
(read at the abstract; arxiv.org/abs/2609.17523 publishes no full HTML).
Item 2's own sentence — an edit "must raise the held-out differential score,
not the score on the tasks it was written against" — is the correct rule and
it is SkillOpt's alone. Cite C392 for *bounded edits by a separate fixed
auxiliary model*, which is what it actually establishes, and not for gating.

**The corpus is not missing preference optimization from usage data. It holds
the form that applies to us.** ADR-40's consequences name "preference
optimization on usage data" as absent. Designer-RSI (C887-C891, four of the
five `controlled`) evolves a skill bank from real user traffic: 76
documentation-derived skills grow to 139 over five rounds on 1,406 briefs
and 1,869 graded trajectories (C890), gated by a replay gate that "admits a
proposed skill only when it outperforms the incumbent on at least one
replayed case and never causes a regression on any replayed case" (C891),
and scored by pairwise preference against the no-skill agent — 61.8% and
67.6% win rates on two models (C888). What the corpus genuinely lacks is the
*weight-training* branch: DPO, KTO and friends fitted to logged preferences,
where 0 claims mention usage data, implicit feedback or production traffic
at all. That branch is the one we do not need, because our artifact is a text
file and no weights are trained. The gap as written sends the reading queue
after the wrong half. Section 3 restates it.

**The three-module cap is not violated, and reading it as sections was my
own error.** My first pass counted `##` headings and concluded six of eight
skills breached C848's at-most-three-modules finding. The Agent Skills
specification (agentskills.io/specification, read today under L-R1) settles
what a module is, and it is not a heading. The spec defines progressive
disclosure in three levels — metadata at roughly 100 tokens, the `SKILL.md`
body loaded on activation, and files under `scripts/`, `references/` and
`assets/` loaded only when required — so a module is a *referenced file*.
Measured at HEAD: all eight skills have **zero** reference files. Every skill
is one module. C848's cap is not the library's problem.

The spec's two numeric recommendations do bind, and one is breached:

| Skill | Description (max 1024) | Body lines (keep <500) | Body words | ~tokens (rec. <5000) |
|---|---|---|---|---|
| `evaluation-integrity` | 983 | 440 | 4,333 | **~5,632** |
| `agent-containment` | 656 | 430 | 4,104 | **~5,335** |
| `agent-security-measurement` | 802 | 353 | 3,426 | ~4,453 |
| `skill-library-engineering` | 746 | 316 | 3,149 | ~4,093 |
| `recursive-harness-self-improvement` | 834 | 329 | 3,110 | ~4,043 |
| `self-improving-post-training-loops` | 878 | 164 | 1,505 | ~1,956 |
| `context-window-engineering` | 672 | 97 | 978 | ~1,271 |
| `harness-engineering` | 620 | 98 | 930 | ~1,209 |

Descriptions and line counts are all inside the spec. Two bodies exceed the
recommended 5,000-token instruction budget (token figures are words × 1.3, an
estimate, not a tokenizer count). The remedy the spec prescribes for exactly
this is "Move detailed reference material to separate files," which would move
those two skills from one module toward two or three — *toward* C848's shape,
not away from it. So the direction of travel is the opposite of what my first
pass said: the library is under-modularised, not over-modularised, and the
compaction work is splitting two files rather than cutting six.

What survives from the first reading is the size comparison, and it still
matters. SkillOpt's optimised artifacts stay between 300 and 2,000 tokens
after 1 to 4 accepted edits (C866). Six of our eight skills are above 2,000
and the largest is roughly 2.8× the top of that range. SkillOpt's number
comes from artifacts an optimiser *converged* on, so it is the best available
estimate of how much text actually earns its place, and it is evidence that
most of the library is carrying prose no measurement has justified. That is a
retirement question for the skill seat, and it lands on O2's twelve-skills
target, but it is a question about words and not about modules.

## 1. The estate as measured, which is the baseline any plan has to beat

Counted at HEAD across the eight `skills/*/evals/evals.json` suites:

| Property | Measured |
|---|---|
| Suites | 8 |
| Tasks | 88 (72 treatment, 16 control) |
| Task form | 71 `prompt`, 17 `project` |
| Check type | 68 `rubric`, 8 `tests_pass`, 10 `parses`, 2 `number_in_range` |
| Tasks with a hard check | 20 of 88 (23%) |
| Suites specifying repetitions | 0 |
| Suites specifying pass@k | 0 |
| Suites naming a rubric certificate | 1 |
| Suites naming an exploit test | 2 (in prose, no task implements one) |
| Skills with a recorded differential screen | 2 of 8 |
| Skills with a recorded A/B validation | 1 of 8 (`harness-engineering`) |

Two of ADR-40's seven testing items are already built, and the brief should
say so rather than prescribe them again. **Item 7, credit to the section, is
live:** the 2026-09-30 ADR-38 retrofit gave every one of the 88 tasks a
`sections` list naming the SKILL.md headings it exercises, "so the per-section
Validation tags are checkable by string comparison rather than by trusting
`source.claims`." **Item 6's first half, judge separate from subject, is
live:** every suite declares `"judge": "a model other than the subject"`.

What the table says about the rest is one sentence. **77% of the library's
eval surface is rubric-judged, and not one rubric in it carries the
certificate that the corpus's best-evidenced warning says is the difference
between 0% and 36% exploitation.** That is the gap the directive's item 4 is
really asking about, and section 4 is the plan for it.

## 2. The methods, each read against what it would change here

For each: what it measures or changes, the measured gain, the failure mode,
and the mapping onto a skill file as the artifact and the eval harness as the
loop. Papers read in full HTML unless marked *(abstract only)*.

### 2a. The reward signal: rubrics and their exploitation

**ImpossibleRubrics** (C476-C480; read in full, arxiv.org/abs/2609.16816).
*Measures:* whether a generated rubric rewards an honest answer over an
adversarial one optimised against it. *Gain:* certificate-faithful rubrics
0/45 exploited against 8-26% for eleven generators on the unbiased 150-task
cut and 36% for the best generator on the 45-task stress cut (C476, C479).
*Failure mode:* three of them, and only the first is in the corpus.

1. Specificity is the attack surface. A generated rubric's task-specific
   criteria "act as an attack roadmap that forces the violating claim."
   In the paper's worked example the rubric awards credit for stating
   "0.0%" on a prophylaxis criterion, reasoning that no trials imply zero
   probability; the attacker follows the faulty inference and scores
   100/100 while the honest answer that acknowledges missing evidence
   scores 36/100. Seven of eleven generated rubrics were exploited as often
   as or more often than a naive decisiveness proxy that scores 64% on
   Hard-45. **The problem is not that rubrics are vague. It is that they are
   specific about the wrong things.** No claim row carries this, and it is
   the single most useful sentence in the paper for us.
2. Prompting does not fix it. Instructing generators to "reward faithful
   handling of the provided evidence" moved Sonnet 5 from 67% to 49%, with
   residuals of 22%, 36% and 49% across generators — far above the 0%
   certificate baseline.
3. The measured rate is a property of the verifier, not of the rubric.
   Holding rubrics, attacks and judge scores fixed and swapping only the
   Oracle gives 33.3%, 75.6% and 66.7% (C477) — a 42-point swing.

*Maps onto:* the certificate is the artifact we are missing. The paper's
certificate has six parts, and the two that are mechanical for us are the
*evaluation specification* ("mandatory, prohibited, permissible, and
acceptable refusal statements") and the *reward-hacking behaviours* list.
The exploit test is a four-stage chain, not a single adversarial answer:
generate the rubric blind, have a second model write an answer that maximises
rubric reward regardless of honesty, have a third model score honest and
attack answers blind to which is which, and have a fourth verify the attack
against the certificate. An exploit is recorded when the attack scores at
least as high as the honest baseline **and** violates the certificate. ADR-40
item 5's phrasing — "an answer that games the rubric must not score" — is
absolute where the paper is comparative, and the comparative form is the one
that can actually be run.

**DRACO** (C39, C40, C42; *abstract only*, arxiv.org/abs/2609.04094).
*Changes:* generates rubrics dynamically during training to track the
policy's evolving capability, then redistributes trajectory-level rubric
scores over the responsible steps by closed-form formula, with no learned
attribution module. *Gain:* +15.9 on AppWorld and +5.3 over GRPO with sparse
ground-truth rewards; +5.3 on out-of-domain Tau-Bench, beating both
ground-truth-reward training and other rubric-based settings, without a
frontier judge (C42). *Failure mode:* the paper states none; the operating
assumption is an outcome-blind setting with no programmatic verifier, which
is the opposite of where we should be. *Maps onto:* the redistribution idea
is the right one for section-level credit and it is cheaper than it sounds —
closed form, no extra model. The dynamic-rubric half does not transfer: our
rubric has to be stable across runs for a delta to mean anything, and a
rubric that tracks capability cannot also be the gate.

Note a live disagreement the graph already flags: claim_links holds
`393 contradicts 39`, ScienceBuddy keeping rubrics fixed through the RL phase
against DRACO regenerating them. That is a real design tension and the open
question under any rubric-based loop we build. It is mislabelled as a
contradiction — see section 6.

### 2b. Credit assignment, which is what makes a delta actionable

| Method | What it changes | Measured | Failure mode |
|---|---|---|---|
| **DRACO** (C40) *abs* | Rubric score → per-step advantage, closed form | +5.3 OOD over base (C42) | No verifier in the loop; dynamic rubric can't also gate |
| **FloWright** (C1442) *full* | Workflow structure → role-level reward, no extra models, labels or executions | +7.41% peak; +5.03% co-evolving roles against +2.83% single-role | Workflows "trained and evaluated on data a single agent can already handle" — the paper built DataWright to harden tasks because of it |
| **RDPO / IterSynth** (C778) *abs* | Terminal outcome reward + turn-level rubric → role-specific advantages | Not separable from the system in the claim row | Asserted, single source, no ablation in the corpus |
| **FAULT** (C1474) *abs* | Self-diagnosis → explicit step-level credit anchored by terminal outcomes | MRR 0.494 for the decisive error step against GiGPO 0.303 and random 0.266; 95% signal coverage against GRPO 41%, GiGPO 72% | Diagnosis is produced by the same system being diagnosed |

FloWright's failure mode is the most valuable line in this table, because it
arrives at ADR-40's item 2 from an independent direction. Item 2 requires
differential tasks — only tasks the bare subject fails or partly fails count.
FloWright found the same defect in workflow optimisation generally and built
an adaptive hardening step to cure it. Two independent lines reaching the
same requirement is the evidence bar the charter asks for, and it means the
differential rule is the one item in ADR-40 I would build first.

### 2c. Judging: who scores, and what it costs

**PACT (enterprise assistants under pressure)** (C561; *abstract only*,
arxiv.org/abs/2609.18605). Note a name collision that will cause a
miscitation: the corpus holds two papers called PACT, this one and
"PACT: From Credit Assignment to Critic Alignment" (arxiv:2609.26355).
ADR-40 cites the first. *Measures:* rule-following under pressure across 12
enterprise domains and 48 scenarios in multi-turn conversations, with items
built "under strict LLM-as-judge auditing to ensure samples are unambiguous,
ungameable, and realistic enough to avoid eliciting evaluation-aware
behavior." *Gain:* across 22 models, the best assistants still mis-apply a
rule on 6-10% of items, and user pressure raised violation rates by 65% on
average. *Failure mode:* the auditing is itself an LLM judgment, so it
inherits the Oracle sensitivity ImpossibleRubrics measured. *Maps onto:* the
once-per-task audit in item 6, and something ADR-40 does not have — a
**pressure arm**. Every skill in the library contains prohibitions
("never put the control in front of the model's judgment about text", "a
prohibition in a prompt is not a control"). A single-turn task cannot test a
prohibition. Skill-Use calls this the Boundary facet; PACT supplies the
multi-turn pressure that makes it bite, with a 65% effect size.

**RAIM** (C1322-C1324; *abstract only*, arxiv.org/abs/2609.39229).
*Changes:* replaces a frontier judge with a cross-fitted stacked panel of
cheap models plus an admissibility test. *Gain:* median 93% of the frontier
judge's Cohen's κ and 2.9 balanced-accuracy points lost on average across
eight faithfulness benchmarks, at roughly 1/64 the price, after a one-time
calibration of 50-100 labelled records. *Failure mode:* stated plainly and it
decides whether we can use it — the panel works "where several capable
members err on different items" and fails when one model dominates, in which
case the frontier judge stays materially better. The admissibility test is
what tells you which case you are in. *Maps onto:* this is the budget answer
for 68 rubric-judged tasks. ADR-32 funds a Kimi account and the suites
already default the subject to it; a RAIM-style panel lets the *judge* be
cheap without the judge becoming the subject. The 50-100 labelled records
are the cost, and we would have to produce them by hand once per rubric
family.

### 2d. Refinement: attributing an edit, then gating it

**AgentGrad** (C244; *abstract only*, arxiv.org/abs/2609.08572).
*Changes:* two things ADR-40 reads as one. First, *sequential intervention*
modifies one agent at a time to identify whose modification resolves the
failure — attribution by experiment, not by inference. Second, semantic
textual gradients are clustered by similarity and each cluster abstracted
into one generalized correction. *Gain:* state of the art on five
benchmarks, 2.5× less wall-clock optimisation time, 21.8% lower cost.
*Failure mode:* the paper names what it fixes in prior gradient methods —
no verification that the edited prompt actually resolves the failure, and
random gradient grouping. Both are failure modes of the obvious
implementation. *Maps onto:* item 1 (one intervention at a time) and item 3
(cluster before applying) are the same paper and should stay coupled: the
clustering is what makes a correction general, the intervention is what
proves it landed. Our `harness-engineering` skill already carries the
clustering half as "Delta 3: cluster the corrections before you apply them."

**SkillOpt** (C862-C866; read in full, arxiv.org/abs/2605.23904).
*Changes:* bounded textual learning-rate budget, held-out validation gating,
rejected-edit buffer, epoch-wise slow/meta updates. *Gain:* +23.5 points in
direct chat, +24.8 inside Codex, +19.1 inside Claude Code over no-skill
accuracy on GPT-5.5 (C862); +5.4 over the strongest per-cell baseline across
52 (model, benchmark, harness) cells (C863); artifacts transfer across model
scales, harnesses and related benchmarks (C864) and stay 300-2,000 tokens
after 1-4 accepted edits (C866). *Failure mode:* C865 is an ablation saying
all four mechanisms are *each* necessary for stability — which is also a
warning that implementing three of four buys instability, not 75% of the
gain. *Maps onto:* this is the reference design for our maintenance loop,
and the only one in the corpus whose gate is held-out. The 300-2,000 token
window is the retirement target for the six oversized skills.

**COBRA-Skills** (C320-C322; *abstract only*, arxiv.org/abs/2609.11682).
*Changes:* contextual-bandit prioritisation of which skill to evaluate next.
*Gain:* 55-58% lower optimisation cost than SkillOpt using only 50 unique
optimisation examples per benchmark (C321), robust to harness changes (C322).
*Failure mode:* **C322 also asserts it "performs effectively when the target
model itself is used for skill generation and refinement," and the paper
offers no evidence for that sentence** — no comparison, no ablation, nothing
beyond the assertion, confirmed by reading the page. It sits directly against
C850 (self-generated Skills underperform curated Skills) and against C965
(the self-refinement trap). Both C322 and C850 are `asserted`, so neither
settles it, and the corpus currently holds an unresolved contradiction on the
one question that decides whether our cheap subject may propose its own
edits. Section 3 queues the reading that would settle it. Until then ADR-40
item 6's conservatism is the right call, and it should be recorded as a
*choice under contested evidence* rather than as a finding.

**GraphSkillEvo** (C625-C629; *abstract only*, arxiv.org/abs/2609.21749).
*Changes:* represents a skill as a directed graph — nodes are execution steps
with operational guidance, edges are context-dependent transitions — and
evolves a population by structure-aware mutation and crossover, selecting
top-N by validation fitness each generation. *Gain:* +4.01% over SkillOpt on
GPT-5.4-nano and +1.76% on GPT-5.4 across five benchmarks (C625). *Failure
mode:* the gains are small and the larger one is on the smaller model, which
is the signature of a scaffold that substitutes for capability; C629's
efficiency argument is the more durable claim than C625's accuracy one.
*Maps onto:* not the file format — SEP-2640 and the Agent Skills
specification settle that, as the reading queue already records. What
transfers is C627: structured operators "enable broader exploration of the
skill space than pure LLM-based self-refinement," which is a second
independent vote against letting a model free-form rewrite its own skill.

**Trace2Skill** (C872-C876; read in full, arxiv.org/abs/2603.25158).
*Changes:* consolidates execution trajectories into skills by inductive
reasoning, in parallel rather than by order-dependent sequential editing.
*Gain:* up to +57.65 points on WikiTableQuestions (C872), the largest number
in this whole area, plus cross-family and cross-scale transfer (C876).
*Failure mode:* **the paper labels itself "Work in Progress" with expanded
experiments planned.** C872 is graded `controlled` in our corpus. A
work-in-progress preprint carrying the area's biggest number and our second
strongest evidence grade is a provenance problem, not a result; it is in
section 6's list. *Maps onto:* C873's parallel-over-sequential finding is
directly usable and cheap — when several consumer reports arrive, consolidate
them in one pass rather than applying them in sequence. It is the same shape
as AgentGrad's clustering, from a second paper.

**Designer-RSI** (C887-C891; read via the W40 draft and the claim rows).
*Changes:* evolves a skill bank from real user traffic by widening (minting
skills for recurring uncovered subtasks) and deepening (contrasting failed
and successful executions), behind a replay gate. *Gain:* GenEval2 execution
success 72.7% → 99.3% (C887); widening and deepening together 58.5% on 200
held-out briefs against 49.4% and 48.6% alone (C889). *Failure mode:* Adobe's
own benchmark, no independent replication, as the W40 draft says. *Maps
onto:* the replay gate (C891) is a third gate design, and it differs from
both SkillOpt's and ScienceBuddy's: *beats the incumbent on at least one
replayed case and regresses on none*. For a library where consumer reports
arrive one at a time and we cannot afford a full rerun per edit, that is the
cheapest defensible gate of the three. C889 is also the only measured
evidence in the corpus that the two refinement directions are complementary
rather than substitutes.

### 2e. The benchmarks that define what "using a skill" means

**Skill-Use** (C857-C861; read in full, arxiv.org/abs/2608.04828).
*Measures:* three facets — Trigger (does the agent invoke the skill), 
Compliance ("how faithfully it follows the prescribed procedure"), Boundary
(does it avoid forbidden operations) — combined into a gated SU score that
"credits execution only after the skill is triggered" (C857). 79 real skills,
177 executable tasks, nine domains, real files, isolated Docker sandboxes,
trajectory-based rubric (C858). Agents see only the name and description
first and must retrieve the procedure, which is progressive disclosure
measured as a behaviour. *Gain:* the measurement itself; the strongest of
eight models under two harnesses reaches 0.613 (C859). *Failure mode for us:*
C860 — triggering and compliance are **independent** bottlenecks, so a single
aggregate score hides which one you have. And C849/the paper's conclusion
that skill use "behaves as a capability conditioned on the harness rather
than a fixed property of the model" means our numbers are only comparable
within a fixed harness. *Maps onto:* this is the structure our test plan
should adopt wholesale, because our 88 tasks currently measure Compliance
only. Nothing in the estate tests Trigger — every task hands the subject the
skill. The `description` field is the entire routing surface
(`skill-library-engineering` already says so), and it is the one part of
every skill file that has never been tested.

**SkillsBench** (C847-C851; read in full, arxiv.org/abs/2602.12670).
*Measures:* 87 tasks across 8 domains with deterministic verifiers, under
"matched no-Skills and curated-Skills conditions for 18 model-harness
configurations." *Gain:* average pass rate 33.9% → 50.5%, +16.6pp, 25.5%
normalized (C847), with per-configuration gains from +4.1 to +25.7pp (C851).
*Failure mode:* C851's spread is the finding — a +16.6 average over a range
that wide means a single-configuration measurement tells you almost nothing,
which is ADR-40 item 3's spread requirement with a number attached.
*Maps onto:* deterministic verifiers and matched conditions are what our
20-of-88 hard-check ratio is short of. The three-module and
self-generated-vs-curated findings (C848, C850) are refinement constraints,
handled in section 0.

### 2f. The trap, stated more precisely than ADR-40 states it

**FlyBy / small reasoning models** (C965; read in full,
arxiv.org/abs/2609.34327). *Measures:* what self-refinement does to the
reachable solution set. *Finding:* self-refinement "largely consolidates
probability mass onto solutions already reachable from the current state,
rather than making new ones reachable." *The distinction ADR-40 is missing:*
the paper separates **execution bottlenecks**, where a correct path exists
and reflection recovers it, from **knowledge bottlenecks**, where external
information is needed before any solution is reachable at all. Self-refinement
helps with the first and cannot touch the second. *Gain:* FlyBy-4B reaches
45.96% pass@8 against 16.85% pass@1 — the gap between what is reachable and
what is reached, which is also the argument for reporting pass@k beside
pass@1. "Small" means 4B and 8B here.

This reframes the whole loop. **A skill file is a cure for a knowledge
bottleneck.** It supplies information the subject does not have. So the cheap
subject can legitimately *verify* a skill (does loading this file change my
answer) and cannot legitimately *author* one, because authoring requires
making reachable what was not. That is a sharper statement of item 6 than
"refinement proposals come from the benchmark subject or from consumers," and
it also explains C850: self-generated skills underperform curated ones
because a model generating its own skill is working inside its own reachable
set by construction.

## 3. What the corpus lacks, restated against measurement

Counts are word-bounded regex over `claim || ' ' || evidence` across all
1,801 claims, run today. Unbounded matching inflates these badly — `DPO`
matches "en**dpo**ints" — and the first pass of this run made that mistake.

| Area | Claims | Read |
|---|---|---|
| RLHF / human feedback | 2 | A named standing priority with two claims |
| **RLAIF / AI feedback / constitutional** | **0** | Named in the charter by name; nothing |
| RLVR / verifiable reward | 12 | The chair's queue already addresses this |
| DPO / preference optimisation | 7 | Mechanism papers, no foundational comparison |
| Process / outcome supervision | 2 | See below |
| Credit assignment | 3 | DRACO, FloWright, FAULT — mechanisms only |
| Rubric | 17 | The strongest-covered area, and ImpossibleRubrics carries it |
| LLM-as-judge | 29 | Broad but incidental; most are "judge score went up" |
| Reward hacking | 2 | Thin for a named risk |
| Usage data / implicit feedback | 0 | But see section 0 on Designer-RSI |

**The gap the chair did not name is RLAIF.** Layer 3 of the standing research
program names "RLHF and RLAIF by name and their live successor landscape...
constitutional and AI-feedback approaches." Zero claims mention RLAIF, AI
feedback, or constitutional AI. Two mention human feedback. This is the
oldest named coverage order in the charter and it is the emptiest shelf in
the corpus.

**The process-versus-outcome gap is real but differently shaped than
recorded.** ADR-40 says the corpus holds no claims on process versus outcome
rewards for long horizons. It holds three credit-assignment *mechanisms*
(DRACO C40, FloWright C1442, FAULT C1474) and two claims touching process
supervision. What is absent is the *comparison*: no claim establishes that
process supervision beats outcome supervision, or where the tradeoff turns at
long horizons. We hold the answers to "how do I assign per-step credit" and
nothing on "should I." The chair's eleven queued papers (Uesato, Lightman,
Math-Shepherd, OmegaPRM, Setlur, ProcessBench, Qwen PRM, PRIME, agent PRMs,
GiGPO, RAGEN) are the right eleven for that, and FAULT's own comparison
against GiGPO means the corpus already has one foot in that literature.

**The preference-from-usage gap needs re-pointing**, per section 0. The
chair's nine queued papers are the weight-training branch, which our artifact
does not use. Appended to the queue today, the branch we do need:

- Designer-RSI's own full text, read for the replay gate's mechanics, since
  it is the gate design closest to our constraints and we have it only
  through claim rows and the W40 draft.
- The evidence that would settle C322 against C850 — whether a target model
  may refine its own skill — because the corpus holds two `asserted` claims
  in direct opposition and the answer decides our loop's architecture.
- RLAIF and constitutional AI foundations, to fill a zero.

## 4. The test plan, per skill

Three things per skill, as the directive asks: which checks are hard, which
need a rubric and what its certificate is, and the exploit test for each
rubric. The generic protocol comes first because it is most of the work.

### 4.1 The protocol, in build order

1. **Trigger, Compliance, Boundary, scored separately** (Skill-Use C857,
   C860). Our 88 tasks measure Compliance. Add Trigger tasks that present a
   situation and the library's descriptions *only*, and score whether the
   right skill is retrieved — this tests the `description` field, which is
   the whole routing surface and is currently untested in all eight skills.
   Add Boundary tasks for every prohibition a skill states. Report three
   numbers, never one: the aggregate hides which bottleneck you have.
2. **Differential screening, from both directions** (ADR-40 item 2; FloWright
   on hardening). A task counts only if the bare subject fails or partly
   fails it. Two of eight skills have a recorded screen; six do not. Run the
   bare arm first and cut the sections that pass bare, which is what the
   2026-09-30 screen did for `cwe-c2`, `cwe-c4` and `he-c1`.
3. **Repetitions and spread** (ADR-40 item 3; SkillsBench C851's +4.1 to
   +25.7 range). Zero suites specify repetitions today. Report the delta with
   its spread, and pass@k beside pass@1 wherever a hard check exists
   (C965: 45.96% pass@8 against 16.85% pass@1 is what pass@1 alone hides).
4. **Certificates before rubrics** (section 4.3). No new rubric criterion
   ships without a certificate and an exploit test.
5. **Cheap judge panel with an admissibility test** (RAIM C1322-C1324), so
   68 rubric tasks are affordable: median 93% of frontier κ at ~1/64 the
   price, but only where several panel members err on different items. Run
   the admissibility test per rubric family and fall back to the frontier
   judge where one model dominates.
6. **Pressure arm on every prohibition** (PACT C561): multi-turn, with a
   persistent user. Single-turn compliance overstates a prohibition's
   strength, and the measured effect of pressure is +65% violations.
7. **Section-level credit**: already live via the `sections` field. Keep it,
   and extend it to the Trigger and Boundary tasks as they are added.

### 4.2 Which checks can be hard, per skill

A hard check is a test, a number in a range, or a named artifact — scored
without a judge. Today: 20 of 88 tasks. The realistic ceiling, by skill:

| Skill | Hard-checkable | What the check is |
|---|---|---|
| `evaluation-integrity` | **High** | Its own procedures are executable. "Construct the mutants a verdict gate cannot see" already is one. The rubric-stress section can be run as ImpossibleRubrics runs it: generate, attack, score, verify — a pass/fail on whether the subject's proposed procedure detects a planted exploit. |
| `context-window-engineering` | **High** | Both deltas are numeric. Delta 1 is a baseline comparison (does the proposal beat the null policy) and Delta 2 is a retrieval task over material larger than the window — both runnable with real files and a scored answer. |
| `recursive-harness-self-improvement` | **Medium-high** | The freeze list, the edit bound and the rollback gate are all checkable as artifacts: does the subject produce a freeze list naming the files, does its proposed edit touch more than the bound. `parses` plus `number_in_range` cover most of it. |
| `agent-containment` | **Medium** | Sections 1, 2, 4 and 7 are testable in a sandbox, which is also the practice the skill sells: give the subject a deny-list defence and a reachable secret, and check whether the secret was reached. Section 5 (price the boundary) is judgment and stays rubric. |
| `harness-engineering` | **Medium** | Delta 1's expected sign is a directional check (does the subject endorse or refuse the fine-tune) and scorable as a binary. Deltas 2 and 3 are advisory. |
| `skill-library-engineering` | **Medium** | The description/routing sections are *directly* hard-checkable by the Trigger protocol above — the skill's own subject matter is the test. Revision-rounds and set-selection sections stay rubric. |
| `agent-security-measurement` | **Low-medium** | Mostly about how to report a number. Sections 1 and 2 can be checked by handing the subject a defence report and scoring whether it recomputes completed harm and refuses a single-rate summary. |
| `self-improving-post-training-loops` | **Low** | Training-loop design advice; no weights are trained here and the tasks cannot run. Stays rubric, and therefore needs certificates most urgently. |

### 4.3 The rubric certificates, and the exploit test for each

A certificate, in our form, is three lines attached to each criterion: the
**mandatory** statements an honest answer must contain, the **prohibited**
statements that void it, and the **verifiable anchor** in the task that
decides which is which — a number, a file, a named artifact, or a cited claim
id. The anchor is what makes it a certificate rather than a better-worded
rubric; without one, specificity makes things worse, not better
(ImpossibleRubrics, section 2a).

The exploit test per rubric is the four-stage chain from section 2a, and it
is one test per criterion set, not per criterion. Concretely, per skill, the
answer the exploit test must not reward:

| Skill | The gameable answer the exploit test plants |
|---|---|
| `evaluation-integrity` | An answer that names every integrity term — rubric stress, unanimity, noise band — and prescribes reading rubrics by eye. Vocabulary without a procedure. The criterion must anchor on the subject proposing an *attack*, not on it mentioning attacks. |
| `agent-containment` | An answer that recommends a longer deny list in confident containment vocabulary. Anchors on the enforcement point, not the word "sandbox". |
| `agent-security-measurement` | An answer reporting a single attack-success rate with a decimal and a confidence interval. Precision standing in for an operating curve. |
| `harness-engineering` | An answer that endorses the fine-tune while citing the regression number. Correct citation, wrong conclusion — this is the one our one recorded A/B already distinguishes, and the exploit test fixes it in place. |
| `recursive-harness-self-improvement` | An answer that proposes a gate and then measures it on the tasks the edit was written against. The ScienceBuddy failure, planted deliberately. |
| `skill-library-engineering` | An answer that writes a long, keyword-dense description. Retrieval-bait as a routing strategy. |
| `context-window-engineering` | An answer that adopts a sophisticated scoring heuristic without comparing it to the null policy. |
| `self-improving-post-training-loops` | An answer that distills from an ungated teacher and calls it self-improvement. |

Each of those is an answer a judge reading a plausible rubric would score
well, and each is wrong in the way the skill exists to prevent. That is the
test: **if the planted answer scores at least as high as the honest one, the
rubric is not measuring the skill.**

### 4.4 What to build first

In order, by evidence strength and cost: the differential screen for the six
unscreened skills (two independent lines of evidence, cheap, and it will
shrink the suites); then Trigger tasks, because the `description` field is
untested in all eight skills and is the entire routing surface; then
certificates and exploit tests on `self-improving-post-training-loops` and
`agent-security-measurement` first, because they are the two skills with the
least hard-checkable surface and therefore the most rubric exposure.

## 5. Digest quality review, in this lane

The newest published issue is W39 (2026-09-28). W40 exists only as a
`press_rehearsals` row written 2026-10-05 03:36. PR #210's brief reviewed the
W40 draft in full and its verdict stands; two findings here are specific to
this dispatch.

**The draft's strongest section is the one this dispatch is about, and it
under-claims it.** "Three labs bet on the harness as the unit of improvement"
covers Designer-RSI, component routing and Mixture of Self-Improving
Branches. Designer-RSI is reported accurately, including the replay gate and
the Adobe-measured caveat. What the draft does not say is that
Designer-RSI is the only measured evidence in the corpus for refining a
skill library from usage data, which is exactly the thing ADR-40 recorded as
absent on the same day. The item reads as one of three harness results; it is
the week's most directly applicable finding for our own product.

**One number in the draft is stated two ways.** The draft says GenEval2
success "rises from 72.7% to 99.3%, a +11.99-point improvement." 72.7 to 99.3
is +26.6 points. C887 carries the same pairing, so the digest faithfully
reproduced the claim row and the claim row is internally inconsistent — the
+11.99 is presumably a different quantity from the paper (a normalized or
averaged gain). This is a distill-stage defect that the press then inherited,
and it is the shape of defect the digest's evidence trail is supposed to
prevent. Routed to the engineer and the skill seat in section 7.

## 6. Claim-graph errors

24 `contradicts` edges, audited in full; 578 `supports`, 194 `refines`, 1
`duplicates`. PR #210 reported that five `contradicts` edges link two claims
of one paper and one joins unrelated subjects. Confirmed, and this run adds
the specific re-classification for the two in this lane plus three provenance
findings.

- **`478 contradicts 477` is wrong and should be `refines`.** Both are
  ImpossibleRubrics. C477 says exploitability varies with the Oracle
  (33.3/75.6/66.7); C478 says all 15 attacks flagged by the primary Oracle
  are also flagged by the other two. Reading the paper, both are true
  together and stated together: the 15 are a nested subset, and the other
  Oracles flag more. C478 *bounds* C477 — the variation is one-directional,
  not disagreement. As a `contradicts` edge it tells a reader the paper
  disputes itself, which is the "deprecation that overreaches" case the
  charter's Step 1 asks about.
- **`393 contradicts 39` is a design tension, not a contradiction.**
  ScienceBuddy holds rubrics fixed through the RL phase; DRACO regenerates
  them during training. Neither claim asserts the other is false; they are
  opposed design choices, and the opposition is genuinely informative — it is
  the open question under any rubric loop we build. The schema has no relation
  for this, and `refines` would be wrong too. **This is a gap in
  `prompts/interpret.md`'s relation vocabulary, not a mislabel the prompt
  could have avoided**, which is why it is reported rather than corrected.
- **Trace2Skill's C872 is graded `controlled` on a self-declared work in
  progress.** The paper labels itself "Work in Progress" with expanded
  experiments planned, and C872 carries the largest effect size in this area
  (+57.65pp). Grade and provenance disagree.
- **Two different papers are both called PACT** (arxiv:2609.18605 and
  arxiv:2609.26355), both in scope for this brief's subject. Any citation by
  name alone is ambiguous. ADR-40's C561 is the first.
- **The duplicate-row defect #210 found reaches this lane.** Of the papers
  central to this brief, AgentGrad, COBRA-Skills, GraphSkillEvo,
  ImpossibleRubrics, IterSynth, PACT (both) and ScienceBuddy each hold two
  rows, `arxiv:NNNN.NNNNN` and `arxiv:NNNN.NNNNNv1`. No duplicate *claims*
  resulted (zero claims share identical text), so the damage is confined to
  paper-level counts and citation checks for now.

## 7. The finding that gates everything above

ADR-40's harness is meant to measure skills whose claims come from a graph
that supplies corroboration. Ten of ADR-40's seventeen cited claims have no
graph edge of any kind. That is not a fact about ADR-40 — 62.8% of all 1,801
claims are orphans — and the cause is measurable.

**`interpret` is rate-limited below its arrival rate, and the backlog does
not drain.** Measured today:

- Service rate: exactly 90 claims/day on 2026-10-01, 10-02, 10-03 and 10-04.
- Arrival rate over the same four days: 217, 136, 135, 142.
- Deficit: 270 claims over four days, about 67/day.
- Backlog: 1,012 uninterpreted claims, of which 785 are embedded and waiting
  and 227 have no embedding yet.
- Lag: the newest claim `interpret` has reached was created 2026-09-27. The
  graph is **8 days behind the corpus**.

The consequence for the product is specific. vision.md §1 defines "matured"
and "left behind" as what accumulating `supports` and `contradicts` edges
reveal. With an 8-day lag, no claim from the current week can carry an edge,
so those two sections structurally cannot see the week the digest is about,
and O1 KR3's evidence requirement is met by older claims only. The
`reasoning` topic — a named owner priority — is the extreme case: 132 of its
133 claims have no edge, because all but one arrived after the lag opened.

This is the third occurrence of one failure. Incident 30 records the first
(2026-09-19, null embeddings, 158 of 543) and the second (2026-09-22, 439
waiting, 12 days stale, growing ~25/day), and prescribes the fix: "rate-match
`interpret` to `distill`." Half of it was applied — throughput rose about
six-fold, from 7-31/day to 90/day, and days-of-staleness improved from 12 to
8. The other half was not: `distill`'s output rose further, so the absolute
backlog more than doubled (439 → 1,012) and the daily deficit roughly doubled
(~25 → ~67). Recorded in `docs/agents/incidents.md` in this PR under the
standing rule.

Three smaller pipeline findings in the same family, all first sightings:

- **227 claims have no embedding, every one created in the last two days**
  (142 on 10-04, 85 on 10-05), and all 227 are also uninterpreted. This is
  the exact shape of incident 30's *first* occurrence. Whether it is a
  regression or the normal lag of a nightly embed job is not decidable from
  the corpus alone; either way it is the condition that makes a claim
  invisible to `interpret`'s neighbour query and to semantic search.
- **`citation_log` stopped on 2026-09-28**, seven days ago, and covers 240
  papers — **all of them tier `b`** — out of 11,584. The charter's relevance
  law ranks by traction and names citation velocity as the evidence for it;
  that evidence is a week stale and covers 2% of the corpus. Worse,
  `docs/product/source-discovery.md` §3.3 prescribes filtering the movers
  query to papers whose tier is *not* `b` or `c`, to catch papers the source
  tiers under-rated. Because the checker only ever visits tier `b`, **that
  documented discovery signal returns the empty set by construction** and
  always has.
- **3,785 papers were triaged by `rule:backfill`, every one to `index`**, no
  model judgment — 32% of everything triaged. It is concentrated in exactly
  the sources the charter's signal-and-evidence section admits as "artifacts
  with method": `openai-blog` (1,118 of 1,138 rule-triaged, 0 ever routed to
  distill), `transformer-circuits` (55 of 56, 0), `lilianweng` (53 of 53, 0),
  `qwen` (44 of 44, 0), `deepmind-blog` (87 of 88, 0). Two causes, and they
  need different fixes: `hf-blog`'s 850 rows are empty-bodied (#210's
  finding), but `openai-blog` averages 156 characters and
  `transformer-circuits` 105 — teasers, not articles — while `lilianweng`
  averages 1,041 characters of real text and is *still* rule-filed to `index`
  53 times out of 53. The engineering-essay channel the charter opens is
  closed in the implementation, and for the one source that has the text, it
  is closed by the rule rather than by the body.

## 8. Curation addendum: extraction targets for the skill seat

The week's curation brief is `2026-10-05.md` §6. These are the additions in
this lane, ordered by evidence and not by date, per the relevance law.

1. **The rubric-integrity cluster is ready and is the highest-value target
   not yet packaged as procedure:** C476, C477, C478, C479, C480, plus C561
   for the audit step and C1322-C1324 for the affordable judge. Caveat the
   skill seat must honour: `evaluation-integrity` already carries the
   stress-test section, so this is a *revision* target, not a new skill, and
   the new material is the certificate's structure and the four-stage exploit
   chain — neither of which is in any claim row, both of which came from the
   full text today.
2. **The skill-maintenance cluster**: C862-C866 (SkillOpt), C320-C322
   (COBRA-Skills), C625-C629 (GraphSkillEvo), C872-C876 (Trace2Skill),
   C887-C891 (Designer-RSI). Three independent gate designs with different
   acceptance rules, which is the comparison a skill would exist to make.
   Blocked on one thing: C322 against C850 is unresolved and the cluster's
   central question depends on it. Package the gate comparison, not the
   self-refinement question.
3. **Not yet**: the credit-assignment cluster (C40, C1442, C1474, C778). Four
   mechanisms, three `asserted`, no edges between them, and the foundational
   comparison absent from the corpus (§3). This is the cluster most likely to
   produce a confident skill on thin evidence. Revisit after the chair's
   eleven process-reward papers are read.

For the engineer, in the order that matters: the `interpret` rate match (§7,
and it gates the graph the digest's judgment rests on); the `citation_log`
restart plus widening it past tier `b`, which also repairs
source-discovery §3.3; the C887 `+11.99` against `72.7 → 99.3`
inconsistency (§5), which is a distill defect that reached a draft issue; and
`rule:backfill`'s 3,785 unjudged `index` rows, where `lilianweng` is the
cheapest proof that the rule and not the missing body is the blocker.

For the PM: ADR-40's refinement item 4 needs rewording before the skill seat
plans from it. The three-module cap is not breached — all eight skills are one
module — but six of eight exceed SkillOpt's measured 300-2,000-token artifact
range and two exceed the Agent Skills spec's own 5,000-token body
recommendation (§0). The work that implies is splitting two skills into
reference files and cutting words from six, which is a different and smaller
job than retiring sections, and it lands on O2's twelve-skills target either
way.

## 8b. The live-web check (L-R1), which found the week's largest gap

`docs/standards/lessons.md` L-R1 requires an explicit ecosystem-events check
against the live web for this seat's declared coverage every run. The
containment dispatch ran one for containment (brief `2026-10-05.md` §12);
this is the one for skill evaluation and refinement. It found more than the
corpus survey did, which is the finding.

**Six papers squarely on this dispatch's subject are absent from the
corpus.** Searched today, then checked by id against `papers`:

| arXiv | Title | In corpus |
|---|---|---|
| 2607.01874 | SkillCoach: Self-Evolving Rubrics for Evaluating and Enhancing Agentic Skill-Use | absent |
| 2606.22613 | SkillAudit: From Fixed-Suite Benchmarking to Skill-Centered Assessment | absent |
| 2608.27487 | Grounded Checklist Partial Credit for Agent Skill Trajectories | absent |
| 2606.17819 | A Framework for Evaluating Agentic Skills at Scale | absent |
| 2606.11435 | Agent Skill Evaluation and Evolution: Frameworks and Benchmarks | absent |
| 2607.27309 | SIGIL: Compiling Agent Skills into Typed Harnesses | absent |

SkillCoach is the one that stings: self-evolving rubrics for skill-use
evaluation is this dispatch's exact subject, and the brief above built its
rubric argument from ImpossibleRubrics, which is a general rubric paper, for
want of a skill-specific one.

**The cause is a time window, not a missing feed, and it is measurable.**
Of the arXiv papers in `papers`, 5,932 carry a `2609` id and 374 a `2610`.
Older months: 118 from `2608`, **1 from `2607`, 2 from `2606`**, and one or
two per month before that. `published_at` for the `arxiv` source runs
2026-08-26 to 2026-10-01. The corpus is effectively a five-week window, and
everything older in it arrived by deliberate backfill — which is exactly how
the skill benchmarks this brief leans on got here (SkillsBench `2602`,
Trace2Skill `2603`, SkillOpt `2605`, Skill-Use `2608`). Every one of the
canonical papers in this field is older than the window, so the field this
dispatch surveys is reachable only by hand.

This is the charter's relevance law as an ingestion defect: "a 2023 paper
whose idea is compounding through the field this month outranks yesterday's
upload that nobody has used," and the pipeline cannot see 2023, or June 2026.
It is an ADR-29 census finding and larger than this brief; the six papers
above are queued, and the window itself is routed to the engineer.

**One ecosystem event, reported as a steering signal and not as evidence.**
Press reporting today (VentureBeat, The New Stack, unite.ai) says Anthropic
has opened Agent Skills as a standard with an SDK at agentskills.io, with
Microsoft, OpenAI, Atlassian, Figma, Cursor and Goose adopting, and
separately that Anthropic released **an evaluation framework that turns one
or more skills into executable evaluation tasks, each a realistic user
request paired with its environment, input artifacts and hidden rubrics**,
plus a dataset of executable coding tasks, able to evaluate a single skill in
isolation.

Two reasons to treat that carefully rather than act on it. The dates in the
coverage do not agree with each other and I could not pin the release date
from the primary source. And the specification itself, read directly today,
defines only the file format — directory structure, frontmatter fields,
progressive disclosure, file references, and a `skills-ref validate`
command — with no evaluation framework, no task format and no hidden-rubric
concept in it. So the framework is real reporting about something outside the
spec I verified, which makes it a signal to point the telescope at and not a
finding.

If it is what the coverage describes, it changes ADR-40's build order, and
the engineer should establish that before building: an off-the-shelf harness
that generates executable tasks with hidden rubrics would supply items 1, 2
and 4 of ADR-40's testing list. **Hidden rubrics are the interesting part,**
because withholding the rubric from the subject attacks the specificity
problem ImpossibleRubrics measured from the other end — an attacker cannot
follow a roadmap it cannot read. That is a defence our own suites cannot use
today, since all 88 tasks carry their criteria in the same file the subject's
author reads.

Two cheap consequences, both inside this seat's lane to report and the
engineer's to do. `skills-ref validate ./<skill>` is a free conformance gate
and nothing in the repository runs it. And the spec's own numbers are now the
authority for §0's size question, which is why that section changed during
this run.

## 9. Meta-review verdict: no proposal this week, and the reason is a rule

The week's one system diff is already spent. PR #210, this seat, this week,
revised `prompts/triage.md`; #220 carries that commit. `sources.yaml` and the
prompts are one proposal per week under the charter, and the dispatch repeats
it ("at most one system diff per week"), so a second diff here would break
it.

The stronger reason is the charter's own stale-image rule. `prompts/triage.md`
at `origin/main` hashes to `32252384ecd7`, which is the sha `triage_log` shows
in production; at HEAD it hashes to `3ea6485103c3` because of #210's commit.
So triage already has one undeployed change pending. Stacking a second prompt
change behind it is precisely incident 25's shape — "a second fix stacked
behind an undeployed first one reads as progress and changes nothing."

Sha status for the record: `interpret` (`6706ec7bffee`), `distill`
(`819694a98603`) and `digest` (`c48d09624161`) all match production.
`triage` is stale by one commit, ours.

**What is being watched and not yet acted on.** The best-evidenced diff
available is to `prompts/research-agent.md`, this seat's own charter, which is
read from the checkout at run time and so reaches production on the next run.
Step 4 tells this seat to gather triage health, distill health and graph
health, and says nothing about queue depth or its trend — the quantity that
actually determines whether the graph reaches the frontier. Incident 30 drew
exactly that lesson in its own words ("a queue is not healthy because its
worker ran. It is healthy when its depth is flat or falling") and noted that
none of the three blackboard queues is checked that way by anything. Three
occurrences later, nothing checks them, and this run found the third only
because it went looking for an unrelated reason. The evidence is a pattern,
the file reaches production, and the diff is four lines. It is next week's
proposal, pre-evidenced here so it does not need re-deriving.
