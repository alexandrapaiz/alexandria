---
name: skill-library-engineering
description: Evidence-backed method for the loadable skill file itself and the library it sits in: what a SKILL.md has to contain to beat loading nothing, and how it gets picked. The subject is the artifact and its selection. Use when a written skill sits in a library and is never picked up, when deciding what belongs in a skill's description because that text is the whole surface a router reads, when a skill loads on the wrong request and leaves the run worse than an empty context, when setting the match score above which a stored skill is reused, when one request needs several complementary entries at once, when turning recorded failures into an edit to one named section of a skill, and when deciding how many revision rounds a skill file is worth.
version: 1
status: active
provenance:
  extracted: 2026-09-26
  validated: ""
  claims: [320, 321, 322, 328, 329, 396, 397, 398, 399, 400, 565, 566, 567, 568, 569, 625, 626, 627, 628, 629]
  papers:
    - "Beyond Top-k Skill Retrieval: Diversity-Aware Skill Routing for LLM Agents — arxiv.org/abs/2609.05824"
    - "COBRA-Skills: Contextual Bandit-Guided Evolution for Agent Skill Optimization — arxiv.org/abs/2609.11682"
    - "The Router Within: Eliciting Native Skill Routing from a Frozen LLM — arxiv.org/abs/2609.15982"
    - "Reflect, Revise, Reuse: Training-Free Skill Evolution for GUI Agents — arxiv.org/abs/2609.17653"
    - "GraphSkillEvo: Evolutionary Optimization of Graph-Structured Agent Skills — arxiv.org/abs/2609.21749"
---

# Skill library engineering

A skill is a file an agent loads into its context when a task calls for it.
This skill is about that file and about the library it lives in: what the file
has to contain to be worth loading, how the file gets chosen, and how it gets
better after it ships. It is not about the agent that reads it.

The delta from ordinary practice is uncomfortable. Writing a good skill by
hand, in the shape the format documents describe, is measurably not enough.
In the strongest evidence here, an expert-written skill and a model-written
skill both left an agent slightly worse off on average than no skill at all,
and only skills built from recorded runs of the task beat the empty baseline.
The sections below are the places where the evidence contradicts what a
careful author would otherwise do.

This skill adds to normal documentation practice, it does not replace it.
Keep writing clearly, keep the file short, keep examples concrete. What
follows is what that discipline alone does not buy you.

## Write the skill from recorded runs, not from the task description

The most direct measurement in this cluster is a baseline table. Under the
Codex harness with GPT-5.4 across four benchmarks, a skill written by a human
expert averaged 67.23 against 67.97 for running with no skill at all, and a
skill an LLM wrote from the task description averaged 67.21. Both were net
negative, and on the spreadsheet benchmark the expert's skill cost 7.5 points.
The same table's skills built and refined against actual execution
trajectories averaged 8 to 10 points above the no-skill baseline in the same
setting (GraphSkillEvo). A second paper reports the same shape: its plain
evidence-grounded skill, generated from no-skill rollouts and never optimized
further, already improved over the no-skill baseline on every target model it
tried (COBRA-Skills).

So the procedure is: run the task without a skill first, keep the
trajectories, and write the skill from what actually went wrong. A skill
written from a description of the task is a plausible document and an
unreliable intervention.

This reframes what an author is doing (ours, not the paper's). You are not
documenting a procedure you believe in. You are recording the corrections that
a run needed, which is why the trajectories are the input and not the
research.

## Most of the value is in the grounding, not in the search on top of it

Two of these papers build elaborate optimizers over skill text, and both
report how much that machinery adds beyond a grounded skill. Removing the
bandit that allocates evaluations cost 2.2 points and removing the population
evolution cost 2.4, against gains of 13.1 to 26.9 points over no-skill for the
method as a whole. A Best-of-30 baseline that simply generated thirty grounded
candidates and kept the best observed one came within 2.5 points of the full
system (COBRA-Skills). The other paper's optimizer beat its strongest
optimizing baseline by 4.01 percent on a small model and 1.76 percent on a
large one (GraphSkillEvo), again small next to the distance from no skill.

The practical reading for a small library (ours, not the paper's): write a few
grounded candidates, measure them on a held-out set, keep the best, and do not
build a search loop until you have exhausted the grounding. The ordering is
what the numbers support. The papers themselves are arguing for their
optimizers.

Two details are worth taking even at small scale. Optimization cost is
dominated by the model that rewrites the skill, not by the one that runs it:
one method cut total cost 55 to 58 percent against its baseline while using
only 50 unique optimization examples per benchmark (COBRA-Skills). And the
rewriting model does not have to be stronger than the target: using the target
model itself to write and refine its own skills lost only one point, 73.5 to
72.5, at roughly half the cost (COBRA-Skills).

## Structure the file so one failure maps to one section

Both structural results point the same way and neither is large on its own.
Splitting a skill into a multi-file package, with retrieval metadata,
executable plan, backup localization, recovery rules and failure cases in
separate files, raised success from 66.67 to 69.52 percent against a single
monolithic file (Reflect, Revise, Reuse). Representing a skill as an explicit
graph of execution steps with condition-dependent transitions, rather than a
flat instruction list, gave clearer workflow guidance and less duplication
(GraphSkillEvo). Stripping that structure back out of already-optimized
skills, while keeping every instruction, cost 0.75 to 4.52 points across five
benchmarks (GraphSkillEvo). It also shrank the search space enough to make
later optimization more efficient (GraphSkillEvo).

The bigger payoff is in revision, not execution. When one paper traced which
failures its loop could actually repair, the answer depended on which file
owned the failure: plan-level errors were repaired 16 times out of 23 by
editing the plan file, grounding errors 6 of 12 by editing the backup
localization file, and missing contingencies only 1 of 4 by editing the
recovery file (Reflect, Revise, Reuse). A monolithic file gives a revision
step nowhere specific to aim.

Ranking these honestly (ours, not the paper's): structure is the smallest of
the three effects the same paper measured, behind in-run revision and reader
isolation below. Adopt it because it makes the other two possible, not because
the direct 2.85-point gain justifies the rewrite.

## The description is the entire routing surface, and it is read alone

Deployed agent harnesses, Claude Code and Codex among them, route by
progressive disclosure: every installed skill's name and description is
preloaded into the system prompt, and the model picks from that menu. The
metadata crowds the context in proportion to library size, which is why Codex
caps skill metadata at 2 percent of the context window, and routing accuracy
decays as the library grows (The Router Within). Your description is competing
inside that budget, against every other skill, with none of your body text
visible.

Two measurements show how much rides on it. Where a menu of names and
descriptions was compared against a method that reads the full skill body, the
menu held up on curated libraries whose descriptions summarize their skills
well, and collapsed on a library of procedural documents where telling the
right skill apart takes detail that no description carries (The Router
Within). And in a live bash-agent harness on 177 executable tasks, Qwen3-32B
under progressive disclosure loaded the correct skill on 1.1 percent of them,
while the same frozen model with a native router loaded it on 90.9 percent
(The Router Within).

That 1.1 percent is the mechanism behind the market fact that most public
skills never fire. The description is not a summary of the skill. It is the
only evidence a router gets, so it has to state the conditions under which the
skill applies, in the vocabulary a requester would actually use.

## A wrong load costs more than a missed one

An ill-suited skill leaves a task worse off than no skill at all (The Router
Within), and the retrieval-threshold sweep puts a number on it. Lowering the
reuse threshold from 0.6 to 0.4, so that more stored skills matched, dropped
success from 69.5 to 55.2 percent. Raising it to 0.8, so that fewer did,
dropped it only to 66.7 (Reflect, Revise, Reuse). Loose matching was more than
twice as costly as strict matching. The same paper's error analysis found
skill guidance adding unnecessary steps on tasks that had a direct solution
(Reflect, Revise, Reuse).

Two consequences. Tune a reuse threshold from the strict side. And when you
write the boundary of a skill, you are protecting the requests it should lose,
not only claiming the ones it should win.

## Index on metadata, not on the body

Retrieval that matched a query against structured metadata, an intent line, an
application, keywords and reusable argument slots, recovered the correct skill
in 12 of 12 reuse cases at threshold 0.6, against 1 of 12 for matching the
full procedural text, with mean scores of 0.88 against 0.41 (Reflect, Revise,
Reuse). Long procedural files share surface tokens across genuinely different
tasks, which is what drags full-text matching down.

If your router reads whole bodies instead, the finding inverts: a method that
read each candidate's full body under the model's own attention beat the
metadata menu by the widest margin exactly where bodies differ and
descriptions do not (The Router Within). Know which of the two your harness
does before you decide where to spend your writing.

## When one request needs several skills, select a set

Scoring each candidate independently and taking the top k is the wrong
objective once tasks are compositional, because several near-duplicate skills
can all score highly and crowd out a complementary one the workflow also
needs. Skill routing is better treated as complementary set selection than as
relevance ranking alone (Beyond Top-k Skill Retrieval). Selecting the shortlist
as a set, balancing per-skill relevance against redundancy, improved recall
and full coverage over a strong pointwise reranker, with the larger gains on
multi-skill queries (Beyond Top-k Skill Retrieval).

The caution matters more than the method. Penalizing raw similarity between
candidates made things sharply worse than the pointwise baseline it was meant
to improve, 0.534 against 0.705 recall, because skills needed by the same
request are similar to each other for a good reason. Only after removing the
query-aligned component of each skill's representation, so that the penalty
measured redundancy rather than shared relevance, did set selection beat the
baseline, 0.711 (Beyond Top-k Skill Retrieval).

For a library author (ours, not the paper's), the operational form of this is
to write neighbouring skills so they are distinguishable on the axis the
requester varies, and to accept that two skills covering different steps of
one workflow are supposed to look alike.

## Revise in rounds, keep the reader separate, stop at three

The revision loop that these results come from is: run the skill, let the
runner amend it in place when the environment contradicts it, then have a
separate reader diagnose the failed run and drive an edit to a named file.
Both halves are load-bearing. Removing the in-run amendment cost 6.66 points
and removing the reader's isolation cost 8.57 points, the two largest effects
the paper measured (Reflect, Revise, Reuse). Isolation here means the reader
sees only the instruction and the trajectory, not the skill text and not the
runner's reasoning, so its diagnosis cannot inherit the mistaken plan it is
supposed to find.

Rounds saturate fast. Three rounds bought 12.4 points on one model. A fourth
and fifth together added 0.9 (Reflect, Revise, Reuse). Three rounds also beat
three independent retries of the same task, 69.5 percent against 62.8, on a
slightly smaller token budget, which is the evidence that the gain comes from
the accumulated edits rather than from extra attempts (Reflect, Revise,
Reuse).

Where a population is worth keeping, keep it for recombination rather than
for retries: recombining components across separately-refined candidates was
worth 4.9 points over running the same refinements in parallel without
exchange, and selecting the top few candidates by validation fitness each
generation is what preserves the diversity that makes recombination possible
(GraphSkillEvo). Trajectory-driven refinement is still the larger half, worth
17 points when removed entirely (GraphSkillEvo).

## Skills outlive the model they were written for

Skills optimized against one model transferred to others: 34 of 36 cross-model
transfers improved on the receiving model's no-skill baseline (COBRA-Skills),
and a skill optimized on a small model and deployed on a large one beat that
large model's no-skill baseline on all three benchmarks tested, in one case
beating the skill optimized directly on the large model, 71.78 against 69.40
(GraphSkillEvo). Skills also survived a change of surrounding harness, holding
their lead under two external agent harnesses (COBRA-Skills).

This is the argument for the artifact being the thing you maintain (ours, not
the paper's): the file is portable across models in a way that tuned weights
and harness-specific prompts are not, so the cost of grounding it is amortized
over every model you later run it under.

## Where the full text narrows what our claim rows say

Four rows in the claim graph read stronger than the papers behind them, and
the paper wins.

- The multi-file result (Reflect, Revise, Reuse) is real but small, 2.85
  points, and is the least of the three ablations that paper ran. The row
  states it without the magnitude.
- The set-selection gains (Beyond Top-k Skill Retrieval) are 1.4 recall points
  and 1.3 coverage points at the cutoff where both systems were actually
  compared. The large gains at cutoff 50 are measured against a baseline whose
  released output stops at 20, which the paper states plainly. On single-skill
  queries, set selection tied plain embedding retrieval exactly.
- The native router's win over frontier models (The Router Within) is against
  open models running in Codex, with their numbers quoted from the benchmark's
  own paper, and the router itself runs in a different harness. Our row names
  Claude Code as a compared system. The paper's table does not.
- The bandit optimizer's first-place finish (COBRA-Skills) is a 2.2 to 2.5
  point margin over its own ablations, inside a method whose total gain over
  no-skill is 13 to 27 points. Reading the row alone attributes the gain to
  the search.

## Caveats

- The strongest execution numbers here (Reflect, Revise, Reuse) come from GUI
  agents on three benchmarks, MobileWorld, AndroidWorld and OSWorld. Screen
  interfaces are non-stationary in ways a file-and-shell environment is not,
  so the revision loop's magnitudes should be read as indicative outside that
  setting even where the shape carries.
- The metadata-retrieval result rests on 12 reuse cases, and the routing-set
  result on 75 queries. Both are directionally strong and statistically thin.
- Every routing number is measured as whether the right skill was selected,
  not whether the task then succeeded. One paper says outright that an agent
  can still fail with every required skill retrieved, including from conflicts
  among the loaded skills' instructions (Beyond Top-k Skill Retrieval).
- The baseline table showing hand-written skills going net negative covers
  four to five benchmarks on two OpenAI models. It is the finding this skill
  leans on hardest and the one most worth re-testing on your own tasks.
- These findings are from 2026 papers and carry alexandria claim provenance;
  if a source claim is later contradicted, this skill will be revised or
  deprecated.
