---
name: skill-library-engineering
description: "Evidence-backed method for the written skill file and the library it sits in: what a SKILL.md has to contain to beat loading nothing, and how a router finds it. Use when a skill in your library never fires, when deciding what belongs in a skill's description because that text is the whole surface a router reads, when a skill loads on a request it should have lost and leaves the run worse off than an empty context, when setting the match score above which a stored skill file is reused, when two neighbouring skills in a library keep taking each other's requests, when turning recorded agent runs into an edit to one named part of a skill file, and when deciding how many revision rounds a skill file is worth. The subject is the written artifact and the library around it, not the agent that reads it."
version: 3
status: provisional
provenance:
  extracted: 2026-09-26
  revised: 2026-10-26
  validated: ""
  differential_screen: "not run. This seat has no route to either eval arm: no GROQ_API_KEY reaches the run, and pipeline/budget.py knows no provider that serves the benchmark subject. Both are queued in docs/agents/pending-workflow-changes.md. Every delta below is unscreened, and each Validation tag names what this run expects a bare subject to supply already and what it does not."
  reviews:
    - "none filed yet. The lane is open at reviews/ (ADR-38); see reviews/README.md for what this skill most wants reported."
  revisions:
    - "2026-10-26 (ADR-38, the quality bar): 337 lines to 113, nine prose sections to six deltas each ending in a numbered procedure with its thresholds named, the checklist moved first, and every number in the file re-read against its paper. `status` moved from `active` to `provisional`: ADR-38 rule 7 earns `active` on a positive differential delta on the benchmark subject, no such delta exists for this skill, and `active` had been standing in for a measurement nobody ran."
    - "2026-10-26 (ADR-35, the paper wins, two corrections): all five papers were re-read in full this run. (1) The previous version's headline, that a hand-written and a model-written skill 'both left an agent slightly worse off on average than no skill at all', holds in one of the three published model-harness configurations and not in the other two. Under the Codex harness on GPT-5.4 the two sources averaged 67.23 and 67.21 against 67.97 for no skill; with no harness the same two were net positive, +2.14 and +2.13 on GPT-5.4 and +7.39 and +8.42 on GPT-5.4-nano. The caveat that this covered 'two OpenAI models' was wrong in this skill's own favour on the finding it leans on hardest. Delta 1 now carries the configuration, and the replacement finding is sharper: on SpreadsheetBench a hand-written skill was net negative in all three configurations. (2) The threshold sweep was described as loose matching costing 'more than twice' what strict matching costs. It is 14.3 points against 2.8, five times, and delta 4 now says five. Both filed for claim revision in docs/ideas.md; this run had no database and could not identify which claim ids carry them."
    - "2026-09-30 (ADR-38 retrofit, owner directive): per-section Validation tags, an Apply checklist, and caveats that name their floor. No claim, number or prescription changed."
  claims: [320, 321, 322, 328, 329, 396, 397, 398, 399, 400, 565, 566, 567, 568, 569, 625, 626, 627, 628, 629]
  papers:
    - "Beyond Top-k Skill Retrieval: Diversity-Aware Skill Routing for LLM Agents — arxiv.org/abs/2609.05824"
    - "COBRA-Skills: Contextual Bandit-Guided Evolution for Agent Skill Optimization — arxiv.org/abs/2609.11682"
    - "The Router Within: Eliciting Native Skill Routing from a Frozen LLM — arxiv.org/abs/2609.15982"
    - "Reflect, Revise, Reuse: Training-Free Skill Evolution for GUI Agents — arxiv.org/abs/2609.17653"
    - "GraphSkillEvo: Evolutionary Optimization of Graph-Structured Agent Skills — arxiv.org/abs/2609.21749"
---

# Skill library engineering

Six findings about the written skill file and the library around it. A competent engineer already writes clearly, keeps the file short, prefers concrete examples and versions the artifact. None of that is repeated below. What is specific here is that a skill is an intervention rather than a document: it is chosen by a router that reads only its description, it can leave a run worse off than loading nothing at all, and the only baseline that says whether it is worth shipping is the same task with an empty context. Each delta ends in a procedure with its thresholds named.

## Apply: the builder's checklist

1. **Written from recorded runs of the task rather than from the task description or a runbook**, and the result read per task family rather than as an average (delta 1).
2. **About thirty grounded candidates, scored on about fifty held-out examples, best one kept, and no search loop built until that is exhausted** (delta 2).
3. **The description states the conditions in the vocabulary a requester would use**, because it is the whole surface the router reads and adding text does not repair a bad pick (delta 3).
4. **The reuse threshold is approached downward from 0.6 rather than upward from below**, and neighbours are separated by writing them distinguishably rather than by penalising their similarity (delta 4).
5. **Each class of failure has one file or one section that owns it**, and the library indexes that metadata rather than the body (delta 5).
6. **Three revision rounds, with the reader that diagnoses the failure blind to the skill text and to the runner's reasoning** (delta 6).
7. **Measured against no skill at all before it ships.** Every number below is a difference from an empty context, and a skill that has not been compared with one is unproven whatever its prose.

## Delta 1: write from recorded runs, and read the per-family number rather than the average

*Validation: no trial, no consumer report, no bare-arm screen. Eval task sle-t1. A bare subject will say "write it from your runbook, keep it specific, iterate", and may well say "ground it in real examples". It is unlikely to supply that hand-written skills measured net negative in a published configuration, and less likely still to supply that one benchmark went negative in all three.*

The baseline table this delta rests on is narrower than this skill claimed before 2026-10-26, and the correction is the point. Under the **Codex harness with GPT-5.4** across four benchmarks, a human-written skill averaged **67.23** and a model-written-from-description skill **67.21**, against **67.97** for no skill at all (GraphSkillEvo). With no harness the same two sources were net positive, **+2.14** and **+2.13** on GPT-5.4 and **+7.39** and **+8.42** on GPT-5.4-nano (GraphSkillEvo). Two things hold in every configuration. The gap to skills built and refined against execution trajectories is large and one-directional, **+8.98** to **+10.31** in the Codex row and **+17.85** to **+21.86** on the small model (GraphSkillEvo). And the harm is task-shaped rather than model-shaped: on SpreadsheetBench a hand-written skill was negative in **all three** configurations, **-1.31**, **-0.48** and **-7.50**, and a described-from-the-task skill too, **-3.57**, **-2.39** and **-9.28** (GraphSkillEvo). Grounding alone is most of it: a skill generated from no-skill rollouts and never optimized further improved over the no-skill baseline on **all three** target models it was tried on (COBRA-Skills).

1. Run the task with no skill first and keep the trajectories. They are the input. The research is not, and a plausible document is not an intervention.
2. Report the delta **per task family**, never as an average. The average hid a 7.5-point loss on the one benchmark where a hand-written file was harmful in every configuration.
3. Measure in the harness you ship. The same two skill sources were worth **+8.71** in one configuration and **-7.50** in another, so the sign is a property of the file and its harness together rather than of the file (ours, not the paper's).
4. Treat a net-positive average as unproven until the family breakdown is in front of you.

## Delta 2: stop at grounding, because the search built on top of it is worth about two points

*Validation: no trial, no consumer report, no bare-arm screen. Eval task sle-t2. The ordering advice is ours, read off these papers' ablations against their own arguments. A bare subject will say "iterate on the skill against an eval set". It is unlikely to supply the size of the optimizer's own contribution against the distance from no skill, or that the target model can author its own skills at half the cost.*

Two of these papers build elaborate optimizers over skill text, and both report what the machinery adds beyond a grounded skill. Removing the bandit that allocates evaluations cost **2.2** points and removing the population evolution **2.4**, against **13.1 to 26.9** points over no-skill for the method as a whole, and a Best-of-30 baseline that generated thirty grounded candidates and kept the best observed one came within **2.5** points of the full system (COBRA-Skills). The other optimizer beat its strongest optimizing baseline by **4.01** points on a small model, **1.76** on a large one and **1.33** under the Codex harness (GraphSkillEvo). The economics point the same way twice. Optimization cost is dominated by the model that rewrites the skill rather than the one that runs it, cut **55 to 58 percent** against the baseline while using only **50** unique optimization examples per benchmark, and using the target model itself to write and refine its own skills lost **one** point, 73.5 to 72.5, at roughly half the cost (COBRA-Skills). The artifact also outlives the model it was written for: **34 of 36** cross-model transfers improved on the receiving model's no-skill baseline (COBRA-Skills), a skill optimized on a small model and run on a large one beat the skill optimized directly on that large model, **71.78 against 69.40** (GraphSkillEvo), and the same skills held their lead under two external harnesses, 68.2 under Claude Code and 72.4 under Codex (COBRA-Skills).

1. Generate about **30** grounded candidates, score each on about **50** held-out examples, keep the best. That is the Best-of-30 configuration and it lands within 2.5 points of a full bandit-and-evolution search.
2. Let the target model write and refine its own skills before paying for a stronger author. The measured cost of that choice is one point.
3. Build a search loop only once delta 1's per-family numbers are positive and the last two points are worth a pipeline.
4. Amortize the grounding over models rather than repeating it. Transfer is the cheap direction, and it ran small-to-large in the one test that compared them.

## Delta 3: the description is the entire routing surface, and more text does not repair a bad pick

*Validation: the one delta here with standing evidence outside its papers. The library's own trigger suite (skills/_validation/) has re-run every description on every change since 2026-09-18 and the recorded bundles are the receipts, which is adoption of the procedure and not a measurement of its effect. Eval task sle-t3. A bare subject will say "write a clear, specific description with keywords". It is unlikely to supply the 1.1 percent floor, the metadata cap, or that showing the picker the full body left 29 percent of picks wrong at twenty times the context.*

Deployed harnesses route by progressive disclosure: every installed skill's name and description is preloaded into the system prompt and the model picks from that menu, which is why one deployed harness caps all skill metadata at **2 percent** of the context window and trims the rest (The Router Within). How much rides on that one paragraph: on a benchmark of **177** executable tasks over a library of **79** skills, Qwen3-32B under progressive disclosure loaded the correct skill on **1.1 percent** of them, while the same frozen model with a native router loaded it on **90.9 percent** (The Router Within). The menu came closest on a curated library whose descriptions summarize their skills well, and fell far behind on a library of procedural pages with uninformative titles, where telling the right entry apart takes detail no description carries (The Router Within). The obvious repair does not work. Placing the twenty shortlisted **full bodies** in the menu did not close the gap: the correct skill's complete body was in the prompt for **92 percent** of queries and the picker chose another skill on **29 percent** of them, while the median prompt grew from **1.3K** tokens to **28K to 52K** and a single pick took **26 to 124 seconds** of prefill (The Router Within).

1. Write the conditions under which the skill applies, in the vocabulary a requester would use, and treat the body as unread by the router.
2. Find out whether your harness routes on descriptions alone or reads candidate bodies, and spend the writing effort on whichever it is.
3. Never answer a routing failure by adding text. The measured price of the full-body menu was twenty times the context and seconds of prefill for a pick still wrong on 29 percent of queries.
4. Budget the description against a ceiling rather than a floor. Metadata is capped per library, so a description that is merely long takes room that belongs to its neighbour.

## Delta 4: approach the reuse threshold from the strict side, and separate neighbours by writing rather than by a similarity penalty

*Validation: no trial and no consumer report, though the confusion cases in every triggers.json in this library exist because of this delta. Eval tasks sle-t4 and sle-t5. A bare subject will say "tune the threshold empirically" and "deduplicate near-identical skills". It is unlikely to supply the five-to-one asymmetry of the sweep, and unlikely to supply that penalising inter-skill similarity scored below the baseline it was built to beat.*

An ill-suited skill leaves a task worse off than no skill at all (The Router Within), and the retrieval sweep sizes it. Lowering the reuse threshold from **0.6 to 0.4**, so more stored skills matched, dropped success from **69.5 to 55.2 percent**; raising it to **0.8**, so fewer did, dropped it only to **66.7** (Reflect, Revise, Reuse). Loose matching cost **14.3** points against strict matching's **2.8**, five times as much, and this skill said "more than twice" until 2026-10-26. The same paper's error analysis found skill guidance adding unnecessary steps on tasks that had a direct solution (Reflect, Revise, Reuse). The neighbour problem carries its own trap. Treating routing as complementary set selection rather than relevance ranking does help compositional requests, but penalising raw similarity between candidates scored **0.534** recall against the pointwise baseline's **0.705** and cut multi-skill full coverage from **0.424 to 0.254**, because skills needed by the same request are similar to each other for a good reason; only after removing the query-aligned component of each skill's representation did set selection beat the baseline, **0.711** (Beyond Top-k Skill Retrieval).

1. Start at **0.6** and move up, not up from below. The sweep is asymmetric five to one, so a tie goes to the strict side.
2. Write the boundary as deliberately as the claim. Name the requests this skill should lose and keep them as confusion cases in its test suite.
3. Write neighbouring skills so they are distinguishable on the axis the requester varies, and accept that two skills covering different steps of one workflow are supposed to look alike (ours, not the paper's).
4. Do not thin a library by similarity alone. The one published attempt to do it by penalising similarity landed below the baseline it replaced.

## Delta 5: one failure, one file, and index on that metadata rather than on the body

*Validation: no trial, no consumer report, no bare-arm screen. The smallest direct effect in this file, which the delta says of itself, and the metadata result rests on twelve cases. Eval tasks sle-t7 and sle-t8. A bare subject will say "organise the skill into sections" and "add good metadata for retrieval". It is unlikely to supply the repair rates by owning file, or 12 of 12 against 1 of 12.*

Splitting a skill into a multi-file package, with retrieval metadata, executable plan, backup localization, recovery rules and failure cases in separate files, raised success from **66.67 to 69.52 percent** against a single monolithic file, the smallest of the three ablations that paper ran (Reflect, Revise, Reuse). The payoff is in revision rather than execution: which failures the loop could actually repair depended on which file owned them, plan-level errors **16 of 23** by editing the plan file, grounding errors **6 of 12** by editing the backup localization file, missing contingencies only **1 of 4** by editing the recovery file (Reflect, Revise, Reuse). Structure also carries the index. Matching a query against structured metadata, an intent line, an application, keywords and reusable argument slots, recovered the correct skill in **12 of 12** reuse cases at threshold 0.6 against **1 of 12** for matching the full procedural text, mean score **0.88 against 0.41**, because long procedural files share surface tokens across genuinely different tasks (Reflect, Revise, Reuse). Stripping an explicit graph of execution steps back out of already-optimized skills, while keeping every instruction, cost **0.75 to 4.52** points across five benchmarks (GraphSkillEvo).

1. Give each failure class one owner: plan, localization, recovery, failure cases. A monolithic file gives the revision step nowhere specific to aim, and the repair rates above are what aim buys.
2. Index on the metadata, not the body, unless your router reads bodies. The finding inverts with the router design (delta 3), so settle that question before you write either.
3. Adopt the structure because it makes delta 6 possible, not for its direct **2.85** points, which is the smallest effect in this file.

## Delta 6: three rounds, and the reader that diagnoses the failure never sees the skill

*Validation: no trial, no consumer report, no bare-arm screen. The two largest ablations its source paper ran, which makes it the best-evidenced procedure here. Eval task sle-t6. A bare subject will say "iterate with a critic model on failed runs". It is unlikely to supply that the critic's isolation was the single largest effect measured, or the three-round stop with its fourth-and-fifth-round number.*

The loop these results come from is: run the skill, let the runner amend it in place when the environment contradicts it, then have a separate reader diagnose the failed run and drive an edit to one named file. Both halves are load-bearing. Removing the in-run amendment cost **6.66** points and removing the reader's isolation cost **8.57**, the two largest effects the paper measured (Reflect, Revise, Reuse). Isolation means the reader sees only the instruction and the trajectory, not the skill text and not the runner's reasoning, so its diagnosis cannot inherit the mistaken plan it is supposed to find. Rounds saturate fast: three rounds bought **12.4** points on one model and a fourth and fifth together added **0.9** (Reflect, Revise, Reuse). Three rounds also beat three independent retries of the same task, **69.5 against 62.8 percent**, on a slightly smaller token budget, 94.75M against 103.00M, which is the evidence that the gain comes from accumulated edits rather than from extra attempts (Reflect, Revise, Reuse). Where a population is worth keeping, keep it for recombination: removing crossover cost **4.93** points and removing trajectory-driven mutation **17.02** (GraphSkillEvo).

1. Two writers and one of them blind. The runner amends in place during the run; the reader diagnoses afterwards with the skill text withheld.
2. Stop at **three** rounds. The fourth and fifth are worth 0.9 points between them.
3. Compare the loop against the same budget spent on retries rather than against one attempt. That comparison is what rules out "more samples" as the explanation.
4. If you keep a population, spend it on recombination. Trajectory-driven mutation is the larger half at 17 points, and crossover is worth about 5.

## Caveats

- **This skill is unmeasured.** No delta carries a differential number and no bare-arm screen has run, because this seat has no route to either eval arm. `status: provisional` says exactly that, and it replaced `status: active` on 2026-10-26 for this reason.
- **The strongest execution numbers here come from GUI agents** on MobileWorld, AndroidWorld and OSWorld (Reflect, Revise, Reuse). Screen interfaces are non-stationary in ways a file-and-shell environment is not, so the revision loop's magnitudes are indicative outside that setting even where the shape carries.
- **The thin samples are thin.** The metadata-retrieval result rests on 12 reuse cases and the routing-set result on 75 expert-verified queries, 24 single-skill and 51 multi-skill. Both are directionally strong and statistically small.
- **Every routing number measures whether the right skill was selected, not whether the task then succeeded.** One paper says outright that an agent can still fail with every required skill retrieved, including from conflicts among the loaded skills' instructions (Beyond Top-k Skill Retrieval).
- **Two floors make this cheap to act on.** The rewriting model need not be stronger than the target: the target model writing and refining its own skills lost one point, 73.5 to 72.5, at roughly half the cost. And the grounded-candidates path this skill prefers over an optimizer needs about 30 candidates on about 50 examples per benchmark to come within 2.5 points of the full search.
- **The headline finding is narrower than this skill once said**, and the 2026-10-26 revision note in the frontmatter carries both corrections with their numbers. It is also the finding most worth re-testing on your own tasks, because the published sign flipped between harnesses.
- Every delta is revised or withdrawn if the claim behind it is contradicted. The claim ids in the provenance block are the addresses a contradiction lands on.
