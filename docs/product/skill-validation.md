# The skill validation system

Drafted 2026-09-18 by the skill agent (ADR-22) against the board card "Design
the skill validation system". This is a design proposal plus one built slice,
not an accepted decision. It feeds ADR-13's validator reviewer and O2 KR3
(docs/okrs/okrs-2026-Q4.md), and it is the machinery behind the product
thesis the owner chose at the first all-hands: skills with receipts.

Provenance for the evidence review in section 2. Claims:
[4, 86, 87, 131, 132, 135, 150, 234, 239, 240, 260, 261, 286, 288, 289, 290,
321, 322, 328, 329, 369, 392, 396, 399, 400, 415]. Every id here is cited by
paper title somewhere below, which is the check the ADR-13 provenance
reviewer will run on this file.

Papers:

- Scores Alone Do Not Prove Discovery: The Discovery Certification Protocol
  for Auditing AI Research Agents, arxiv.org/abs/2609.09219
- The Router Within: Eliciting Native Skill Routing from a Frozen LLM,
  arxiv.org/abs/2609.15982
- Beyond Top-k Skill Retrieval: Diversity-Aware Skill Routing for LLM Agents,
  arxiv.org/abs/2609.05824
- COBRA-Skills: Contextual Bandit-Guided Evolution for Agent Skill
  Optimization, arxiv.org/abs/2609.11682
- ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement,
  arxiv.org/abs/2609.14857
- Procedural Graphs: Self-Evolving Execution Structures for LLM Agents,
  arxiv.org/abs/2609.09153
- ScienceBuddy: Recursive-in-Recursive Self-Improvement for Interactive
  Scientific Agents, arxiv.org/abs/2609.17523
- When Models Edit Too Much: On the Fidelity of Minimal Code Edits,
  arxiv.org/abs/2609.04061
- Beyond Solver Verdicts: Generative Reward Models for Autoformalization,
  arxiv.org/abs/2609.11085
- Using Grounded Theory for Agent Behavior Analysis at Scale,
  arxiv.org/abs/2608.30391
- SWE-Bench Pro Verified: A Reliable Benchmark for Software Engineering
  Agents, arxiv.org/abs/2609.08149
- MetroLLM-Bench: Evaluating Language Models as Transit Kiosk Runtimes,
  arxiv.org/abs/2609.10016
- Enabling Creative Exploration for Vibe Design Agents,
  arxiv.org/abs/2609.15078
- Iris: Climbing to the Search Frontier, arxiv.org/abs/2609.04304

## 1. What we have today, and why it is not enough

The library holds two skills. One carries a recorded A/B result: bare Claude
endorsed imitation fine-tuning on a stronger model's trajectories, and the
same model with the skill loaded refused, cited the regression, and
prescribed the on-policy repair instead. That is a real result and it is the
single most valuable sentence on the skill's page, because no marketplace
entry anywhere carries its equivalent.

It is also, on its own, a thin instrument. Stated plainly, that A/B shows one
model, on one prompt, in one session, answering differently. It does not show
that the skill loads when a user actually needs it, that the change in
behavior survives on prompts nobody wrote with the skill in mind, that the
next revision of the skill keeps the gain, or that the difference is larger
than the noise between two runs of the same model. Four of those five
questions are unanswered, and the fifth is answered at n of 1.

The gap matters commercially, not just academically. The verification badge
the market agent proposed (docs/market/opportunities-2026-09-18.md) promises
a prospect "verified against N sources, confidence X" and a trigger
reliability score. The moment that badge renders, every number in it is a
claim alexandria is making about itself, judged by the same standard this
system applies to papers. A badge we cannot defend is worse than no badge,
because the differentiator is honesty about evidence and nothing else.

## 2. What the research says about validating an agent artifact

This section is the requested research pass. The corpus is alexandria's own,
queried read-only this run, which is the point: the validation system should
be built out of the same evidence the skills are.

**Scores alone do not certify anything.** The Discovery Certification
Protocol is the most directly transferable design in the corpus. It replaces
"the number went up" with a three-gate audit: a statistically significant
improvement over baseline, zero successful recoveries by a matched challenger
within a finite-sample bound, and a measured positive effect of truthful
feedback against a calibrated neutral policy, with the task, the threshold,
and the analysis plan pre-registered before the run (Scores Alone Do Not
Prove Discovery). Its own audits report zero recoveries across 96 independent
challenger episodes, which bounds the recovery probability at 0.0468 rather
than at zero, and its feedback gate passed only after 60 paired null studies
calibrated what a sham effect looks like (Scores Alone Do Not Prove
Discovery). The most useful detail for us is the cheapest one: a
deterministic, LLM-free verifier reproduces those decisions from frozen
evidence bundles, so an audit is replayable by someone who does not trust the
auditor (Scores Alone Do Not Prove Discovery).

**Triggering is a measurable quantity, and other people are measuring it.**
Skill routing has its own benchmarks and its own state of the art. Gavel
routes with two trained linear maps on a frozen model and beats
retrieve-and-rerank pipelines that add billions of external parameters by up
to 13.4 points on one skill-selection benchmark and by 8.6 to 21.9 points
across four noisy-context scenarios in a 372-trajectory suite (The Router
Within). In a bash-agent harness, a 32B model with that router triggers the
correct skill more reliably than far larger frontier models running inside
Claude Code and Codex (The Router Within). Separately, treating routing as
complementary set selection rather than pointwise relevance ranking improves
both recall and full coverage on a skill-router benchmark, with the largest
gains on queries that need more than one skill (Beyond Top-k Skill
Retrieval). Two consequences for us. First, "69% of public skills never fire"
is not an unfixable property of the ecosystem, it is an unmeasured one.
Second, a trigger test that only asks "did my skill win" is already behind
the literature, because the real question in a growing library is which set
of skills should load together.

**Held-out means disjoint, and disjointness takes work.** ModularRSI curates
2,000 executable evolution tasks explicitly disjoint from its downstream
benchmarks, using instance-level similarity filtering and domain analysis to
minimize overlap (ModularRSI). The autoformalization verifier reports its
headline AUROC on the full benchmark and again on the subset whose source
texts are disjoint from training, 0.961 and 0.955, so a reader can see what
contamination would have cost (Beyond Solver Verdicts). A skill's validation
suite is contaminated in exactly the same way if it is written by the agent
that wrote the skill, from the same claims, on the same day.

**A benchmark is itself an artifact that can be wrong.** The SWE-Bench Pro
Verified audit found task-quality problems dominated by overly narrow tests,
75 instances, followed by misleading descriptions at 22 and overly broad
tests at 3 (SWE-Bench Pro Verified). The same work enumerates four
reward-hacking channels an agent will use if left open, the local file
system, git history, task metadata, and the external network, and closes each
one deliberately (SWE-Bench Pro Verified). Our equivalent leak is direct: an
agent being evaluated on a skill's task suite can read the skill, and if the
suite's answers are in the skill's own examples, we are measuring copying.

**Outcome scores hide behavior.** Frontier models score high Pass@1 while
rewriting far more code than the task required, a failure invisible to the
pass rate and visible in excess edit distance and added cognitive complexity
(When Models Edit Too Much). A preservation instruction cut average excess
Levenshtein distance from 0.195 to 0.131, reduced added cognitive complexity
by 26.6 percent, and improved Pass@1 by 2.3 points, which is the shape of the
result a good skill should produce: a large behavioral change and a small
outcome change (When Models Edit Too Much). The formal version of the same
point is that any scoring function depending only on a binary verdict cannot
separate a faithful answer from a verdict-preserving unfaithful one, and
scores an AUROC of 0.5 on a paired set built to test exactly that (Beyond
Solver Verdicts). For labelling what actually changed in a trajectory rather
than whether it passed, pre-built classifiers fall short on long and
unfamiliar tasks while grounded theory scales to thousands of trajectories
(Using Grounded Theory for Agent Behavior Analysis at Scale). Automating it,
by iterating open, axial, and theoretical coding until saturation, recovers
73 to 91 percent of the failure modes in human-annotated taxonomies across
six trajectory corpora and surfaces patterns those taxonomies missed (Using
Grounded Theory for Agent Behavior Analysis at Scale).

**Revision is where validated artifacts quietly die.** Two independent
systems land on the same rule. Self-evolving procedural graphs accept an edit
only if it preserves or improves held-out validation performance, and retain
the rejected edits as negative signal so the same bad idea is not proposed
twice (Procedural Graphs). ScienceBuddy holds the model fixed, lets a
separate auxiliary model propose one bounded, single-scope edit to the
harness, and accepts it only when the mean normalized rubric score on
identical development tasks improves (ScienceBuddy). Skill optimization work
adds the robustness dimension: its gains hold across changes to the agent
harness and when the target model itself generates the refinements
(COBRA-Skills). Our skills promise to revise when the evidence changes. That
promise is the thing most likely to break the validation, and nothing
currently re-runs anything when a claim's status moves.

**Small n, stated honestly.** The corpus is full of good practice here and it
costs almost nothing to copy. A finite-sample bound is reported instead of
zero when zero events are observed (Scores Alone Do Not Prove Discovery). A
scaling result is reported as three seeds all moving the same direction, with
the effect itself shrinking from plus 7.03 points at 2B to minus 0.91 at 27B,
which is a far more useful sentence than an average would have been
(MetroLLM-Bench). An online experiment with more than 300,000 tasks reports
its headline metric as statistically uncertain while reporting the secondary
effects it did establish (Enabling Creative Exploration for Vibe Design
Agents). And a skill optimizer reports that it reached its result using only
50 unique optimization examples per benchmark, which is the honest way to
present a small budget (COBRA-Skills).

**Control the confound.** On the benchmarks Iris evaluates, inference-time
context management, which limits the tool set and context length and fixes
the judge, is worth more than most reported differences between systems
(Iris). Our reading, not the paper's: an A/B that changes the skill and
anything else about the harness at the same time is measuring the harness. A
validation run has to pin the model, the tool set, the context budget, and
the judge, and vary only whether the skill is loaded.

## 3. The system

Five gates. Each one states its question, its instrument, its pass rule, and
the field it writes on the receipt. The ADR-13 validator reviewer runs them;
the provenance and adversary reviewers keep their existing jobs, and gate V2
below is the one they already implied.

### V1. Trigger reliability

*Question.* Does the skill fire when the user needs it, stay silent when they
do not, and route correctly against its nearest neighbour in the library?

*Instrument.* A case file per skill, `skills/<slug>/triggers.json`, holding
at minimum the three positives and two hard negatives the charter already
requires, plus one confusion case per neighbouring skill. Cases are scored
against the library and against a fixed panel of decoy skill descriptions
that stand in for domains the library does not serve. The decoys are the null
model, so silence is earned by something else fitting better rather than by a
score falling under an arbitrary cutoff.

*Pass rule.* Every case passes, and the report names every decision whose
margin over the null was under 0.02, because a coin-flip win is not a pass.
No skill promotes with a red suite, and a skill already in gold that goes red
becomes a revision item rather than a silent defect.

*Receipt field.* `trigger_reliability`, reported as a fraction with its exact
binomial interval and never as a bare percentage.

*Built.* Slice 1, in this PR. Section 5 says what it does not yet do.

### V2. Provenance and evidence fit

*Question.* Does every claim id exist, does the cited claim support the
sentence citing it, is unsupported judgment marked as ours, and does the
claim graph contain contradicting or refining claims the draft ignored?

*Instrument.* The provenance and adversary reviewers of ADR-13, unchanged.

*Pass rule.* Unanimous, as ADR-13 specifies.

*Receipt fields.* `claim_count`, `source_count`, and the contradiction sweep's
date, so the page can say when the evidence was last checked rather than only
what it said.

*Built.* No. Designed in ADR-13, zero engineer PRs so far.

### V3. Behavioral delta on a held-out suite

*Question.* With the harness pinned and only the skill varying, does behavior
move in the direction the evidence supports, on tasks written by someone
other than the skill's author?

*Instrument.* A held-out task suite per skill, ten to twenty tasks, authored
against the topic rather than against the skill text, with the skill's own
examples excluded by similarity filtering (the disjointness discipline of
ModularRSI and Beyond Solver Verdicts). Each task is scored on two axes, not
one: the outcome, and a behavioral rubric naming the specific moves the skill
teaches, for instance "proposed harness change before training", "localized
by single-agent intervention", "gated the teacher before distilling". Scoring
both axes is what the over-editing and verdict-only results above say a
single pass rate will miss. Anti-hacking: the evaluated agent never sees the
skill file in the bare arm, and the judge never sees which arm it is scoring.

*Pass rule.* The behavioral rubric improves with a lower confidence bound
above zero, and the outcome score does not regress. A skill that changes
outcomes without changing the taught behavior is suspect, because it means
something other than the skill did the work.

*Receipt field.* `validated`, the one field that turns "pending validation"
into a verified badge, carrying the rubric delta, the n, and the interval.

*Built.* No. This is the upgrade of the existing A/B, and the natural second
slice.

### V4. Regression on revision

*Question.* When the skill is edited or one of its claims changes status,
does everything that passed before still pass?

*Instrument.* Re-run V1 and V3 against the previous recorded bundle. A skill
edit is accepted only if it preserves or improves the prior scores, the
acceptance rule both Procedural Graphs and ScienceBuddy converge on, and
rejected edits are retained in the ledger so the same revision is not
proposed again. The trigger for a re-run is not only a human edit: a
`contradicts` edge landing on any claim in the skill's provenance block
should schedule one, which is the mechanism behind our claim that skills
revise when evidence changes.

*Pass rule.* No metric below its previous recorded value outside its
interval. A regression blocks the edit, it does not merely annotate it.

*Receipt field.* `last_revalidated`, plus the version the numbers belong to.

*Built.* No. Cheap once V1 and V3 exist, since it is those two plus a
comparison against the stored bundle.

### V5. Statistical honesty

*Question.* Is what the badge says defensible at the sample size we actually
ran?

*Instrument.* Three rules, all of them cheap. Pre-register the thresholds and
the decision policy before the run and print them in the bundle, so nobody
tunes until green. Report exact binomial intervals rather than point
estimates, because at n of 6 a normal approximation is simply wrong. Report a
finite-sample bound rather than zero when zero failures are observed, in the
manner of the DCP recovery bound.

*Pass rule.* This gate does not pass or fail a skill. It governs what the
other four gates are allowed to print, and it is the gate the owner should
check first when reading any number this system produces.

*Receipt field.* Every numeric field carries its n and its interval, or it
does not render.

*Built.* Slice 1, in this PR, for V1 only.

## 4. From a validation run to the receipts and the badge

A validation run writes one bundle. The bundle, not the skill's frontmatter,
is the source of truth for every number the library shows, for the reason the
DCP verifier exists: a receipt has to be replayable by someone who does not
trust the agent that produced it (Scores Alone Do Not Prove Discovery). The
bundle records the engine version, the pre-registered policy, the sha256 of
every `SKILL.md` it judged, every case with its score, and the intervals.
Bundles land in `skills/_validation/results/` and, once ADR-13's panel is
live, as a `promotions` row so the audit trail stays in the database that
already holds every other verdict.

The badge reads four fields, extending the schema this agent proposed in the
ledger on 2026-09-18 with the two the design above now makes computable:

| Badge field | Source | Rendered when | Says |
|---|---|---|---|
| `source_count` | `provenance.papers.length` | always | "5 papers" |
| `claim_count` | `provenance.claims.length` | needs the parser fix | "12 claims" |
| `trigger_reliability` | V1 bundle | bundle exists | "11 of 12 trigger cases, 95% CI 0.62 to 1.00" |
| `validated` | V3 bundle | bundle exists and passed | the behavioral delta with its n |
| `last_revalidated` | V4 bundle | bundle exists | "re-checked 2026-11-04, no regression" |

Three rules on rendering, which matter more than the fields themselves.

First, absence renders as "pending validation", never as a blank and never as
a silent false. A drafted skill awaiting the panel must not be mistakable for
a proven one, which is the same rule this agent recorded in the ledger for
`validated` and which now applies to all five fields.

Second, no field renders without its n and its interval. "11 of 12 cases,
95% CI 0.62 to 1.00" is a receipt. "92% trigger reliability" is marketing,
and it is the exact kind of claim this company exists to catch other people
making.

Third, the bundle is linkable. The strongest version of the receipt is the
prospect clicking through from the badge to the recorded run, seeing the
prompts, and seeing the case we failed. Our read, not the papers': showing
the failure is what makes the passes credible, and it is cheap for us because
the failures are genuinely small.

## 5. Slices, and who owns them

1. **V1 trigger test, executable.** This PR. Skill agent. Ships the runner,
   the null panel, cases for both gold skills, and the recorded bundles.
2. **Parser fix and badge fields.** Engineer, already in the ledger. The
   site's `parseSkill` is a flat-line regex that cannot see anything nested
   under `provenance:`, so no receipt reaches the page today.
3. **V3 held-out suites and the blinded judge.** Engineer plus skill agent,
   and the natural home of the ADR-13 validator reviewer. Needs the suites
   authored against topics rather than against the skill text.
4. **V4 regression on revision.** Engineer. Needs 1 and 3, plus a hook on
   `contradicts` edges landing in a promoted skill's provenance block.
5. **Model-in-the-loop trigger engine.** Engineer. Replaces the lexical
   screen with a real router, which is the only way `trigger_reliability`
   stops being a floor. The literature offers a cheap version, scoring each
   shortlisted skill by the model's own mean log-likelihood of the task given
   the skill plus a yes-or-no relevance log-odds, with no extra parameters
   trained (The Router Within).
6. **Multi-skill routing.** Later, and only once the library is past roughly
   six skills, since set selection is the failure mode that appears when
   several skills are plausibly relevant at once (Beyond Top-k Skill
   Retrieval).

## 6. Limitations of what is built, stated before anyone asks

- The lexical engine is a stand-in for the retrieval half of a router, not a
  router. Everything it reports is a lower bound.
- Both the cases and the decoy panel were written by the same agent that
  wrote the skills, in the same session. That is the contamination the
  disjointness results above warn about, and the honest mitigation is that
  the ADR-13 adversary, not the author, should own the decoy panel and at
  least half the negatives.
- Six cases per skill is a very small n. A perfect 6 of 6 bounds true
  reliability at 0.54 from below at 95 percent confidence, which is worth
  saying out loud before anyone reads a clean sweep as proof.
- The suites test only trigger behavior. Nothing here yet tests whether the
  skill is any good once loaded, which is V3's job and is not built.
- One gold skill currently fails its own suite. That is reported rather than
  fixed in this PR, for the reason in section 7.

## 7. For the owner

Three things need your call rather than an agent's.

**The failing case should stay failing until you decide.** The trigger test
finds that `harness-engineering` does not fire on a natural-language version
of the test-time-compute question its own description claims, because the
description says "when allocating test-time compute" and the user says
"should we sample three candidates in parallel or have it revise its own
answer". The fix is one clause in the description. It is also an edit to the
only skill in the library carrying a recorded validation, so this run
proposed it in the ledger rather than making it. Ordinarily, once V4 exists,
this is exactly the class of change that should be automatic.

**Is the badge allowed to show a floor?** The honest `trigger_reliability`
before slice 5 is "11 of 12 on a lexical screen, which is a lower bound". The
alternative is not showing the field until the model-in-the-loop engine
exists. Our recommendation is to show it with the qualifier, because a
qualified number that clicks through to the run is still stronger than every
competitor's zero, but that is a positioning decision.

**The validator reviewer is currently the whole bottleneck.** O2 KR3 asks for
a recorded validation on every skill promoted this quarter, and the
instrument that would produce it is gates V2 and V3, neither of which is
built and neither of which is this agent's surface to build. The ledger
entries exist. They need a sprint slot.
