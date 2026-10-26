---
name: recursive-harness-self-improvement
description: Evidence-backed method for loops where an agent reads its own failed runs, rewrites its own scaffold unattended, then keeps or reverts each edit on measured evidence. The editor is the agent, not a person, and no weights are trained. Use when choosing the seed the unattended loop starts from, when choosing what is frozen each cycle and whether the diagnosing model is part of it, when attributing a failure to one function inside a long execution log, when unattended self-edits raise the score on the tasks the loop evolves against while real work does not, when the loop's own feedback costs more per cycle than its edits gain, or when several automated workers rewrite one shared repository and converge on a single idea.
version: 4
status: provisional
provenance:
  extracted: 2026-09-22
  revised: 2026-10-26
  validated: ""
  differential_screen: "not run. This seat has no route to either eval arm (no GROQ_API_KEY in agent-skill.yml, no benchmark provider in pipeline/budget.py), both queued in docs/agents/pending-workflow-changes.md. Every delta below is unscreened, and each Validation tag names what this run expects a bare subject to supply already and what it does not."
  reviews:
    - "none filed yet. The lane is open at reviews/ (ADR-38); see reviews/README.md for what this skill most wants reported."
  revisions:
    - "2026-10-26 (ADR-38, the quality bar): 355 lines to 114, body 3,119 words to 2,572, checklist first, nine sections to six deltas. Nothing was deleted outright: the evolution-set contamination section and the certification-protocol section fold into delta 4, the first keeping its whole decision rule and the second only the matched-challenger gate, because evaluation-integrity v5 delta 5 now carries the gate arithmetic in more depth and two skills were teaching it. Eval task rhsi-t10 retired with that fold and rhsi-t11 written for the surviving prescription. `status` moved from `active` to `provisional`: ADR-38 rule 7 earns `active` on a positive differential delta on the benchmark subject, no such delta exists here, and `active` had been standing in for a measurement nobody ran."
    - "2026-10-26 (ADR-35, the paper wins, a numeric correction): the previous version's section 3 reported attribution F1 rising from 0.349 to 0.498 for one model and 0.478 to 0.620 for another against 0.401 and 0.559 for passive continuation. Four of those six numbers appear nowhere in arxiv.org/abs/2609.13463, read in full this run, and the two that do appear belong to different tables than the sentence claimed. Delta 3 now carries the paper's actual Table 2 and Table 3, which are a stronger result than the invented one because Table 3 shows the method losing on short logs and so supplies the threshold the old section asked for and could not name. Filed for claim revision in docs/ideas.md; this run had no database and could not identify which claim ids carry the bad numbers."
    - "2026-09-30 (ADR-38 retrofit, owner directive): per-section Validation tags, an Apply checklist, and caveats that name their floor. The tagging pass found section 9 uncovered by the ADR-36 suite, so eval task rhsi-t10 was written and the suite moved to version 2."
    - "2026-09-30 (ADR-35, the paper wins): re-read arxiv.org/abs/2609.09219 in full while revising evaluation-integrity, and narrowed section 9. The third gate is optional in the protocol and returned Inconclusive on both of its real-data audits, which the section had presented as a gate to adopt alongside the other two. No claim this skill cites is deprecated."
  claims: [411, 412, 413, 414, 415, 335, 336, 337, 338, 392, 393, 395, 535, 537, 538, 539, 354, 355, 147, 148, 150, 593, 594, 597, 462, 465, 466, 286]
  papers:
    - "ModularRSI: Modular and Generalizable Recursive Harness Self-Improvement — arxiv.org/abs/2609.14857"
    - "RSIAgent: Autonomous Exploration for Recursive Self-improvement in New Environments — arxiv.org/abs/2609.15364"
    - "ScienceBuddy: Recursive-in-Recursive Self-Improvement for Interactive Scientific Agents — arxiv.org/abs/2609.17523"
    - "SoL-Pi: Recursively Scaling Auto-Research Loops for Efficient Agent Harness — arxiv.org/abs/2609.20519"
    - "Dream-RSI: Recursive Self-Improvement through Evolving Worlds — arxiv.org/abs/2609.14858"
    - "Procedural Graphs: Self-Evolving Execution Structures for LLM Agents — arxiv.org/abs/2609.09153"
    - "Root-Cause Attribution Is a Search Problem: Continual Search for Long-Horizon Agent Failures — arxiv.org/abs/2609.13463"
    - "Agora: Git as Shared Memory for Collective AutoResearch — arxiv.org/abs/2609.18094"
    - "Scores Alone Do Not Prove Discovery: The Discovery Certification Protocol for Auditing AI Research Agents — arxiv.org/abs/2609.09219"
---

# Recursive harness self-improvement

Six findings about the loop where the agent does the editing: it reads its own failed runs, decides which part of its own scaffold caused the failure, changes that part, measures, and keeps or discards. The weights never move. Designing a harness by hand is `harness-engineering`, and updating weights is post-training. What is specific here is that the artifact being changed and the thing proposing the change are one system, so every safeguard a human reviewer would have supplied has to be built into the loop. Version control on the scaffold, a held-out set and full trajectory logs are assumed.

## Apply: the builder's checklist

1. **The week before launch went into the gates, not into the seed scaffold** (delta 1).
2. **A freeze-list file exists, it names the diagnosing model's version and not only the task model's, and changing it restarts the score series** (delta 2).
3. **No edit is proposed from a bare outcome**: either a paired success and failure of the same task, or continual search over the log with the turn count gated on the log's median token size (delta 3).
4. **One edit touches one module or one scoped item, a schema check rejects oversized candidates before evaluation, three gates run in series with rollback as the default, acceptance is decided on held-out performance rather than on the motivating diagnosis, rejected edits are kept, the evolution set has a named filtering step, and a matched challenger has failed before the gain is published** (delta 4).
5. **Candidate evaluation is cheap enough for many cycles, and compaction fires on a cost calculation rather than on a context percentage** (delta 5).
6. **Above two or three workers on one repository, credit is ranked by downstream builds by other accounts and a diversity signal is budgeted** (delta 6).

## Delta 1: the scaffold carries the headroom, so the seed is the wrong place to spend the week

*Validation: no trial, no consumer report, no bare-arm screen. Eval task rhsi-t2. A bare subject will say "iterate rather than over-engineer the first version". It is unlikely to supply that the recursive phase alone was worth seven points with no parameter update, or that a deliberately flawed prior was repaired rather than inherited.*

RSIAgent lifted two open-source models past frontier closed-source models on OSWorld-v2 and Agents' Last Exam without updating a parameter, and the recursive phase is the whole difference: without recursion **71.97** partial and **37.80** binary on OSWorld-v2, with recursion **78.98** and **42.68** (RSIAgent). The gain arrives as frozen memory handed to the same base model as context, with no training step anywhere (RSIAgent). From a minimal skeleton, self-evolving Procedural Graphs matched or surpassed hand-designed graphs, and the same process repaired a deliberately flawed expert prior rather than inheriting it (Procedural Graphs).

The decision rule (ours, not the papers'): do not spend a week hand-perfecting the seed. Spend it on delta 4, because a thin seed with those gates converges and a good seed without them decays.

## Delta 2: freeze the diagnostician too, or the improvement you measure is a drifting judge

*Validation: no trial, no consumer report, no bare-arm screen. Eval task rhsi-t1. A bare subject will say "change one thing at a time". It is unlikely to name the diagnosing model as one of the frozen things, which is the half that makes an apparent gain unfalsifiable rather than merely noisy.*

Every working design here splits the system into a part that moves and a part held still, and alternates. ScienceBuddy runs two nested loops with opposite freezes: inner, the task model's parameters are fixed and a separate **fixed** auxiliary model diagnoses trajectories and proposes bounded edits; outer, the harness and the rubrics are fixed while the model trains on rubric rewards (ScienceBuddy). RSIAgent freezes on a schedule, marking memory frozen when the curriculum agent signals no informative tasks remain and serving it read-only downstream (RSIAgent). SoL-Pi pins mechanism source, configuration, capability tolerances and acceptance rules before the evaluation run begins (SoL-Pi).

The procedure (ours, not the papers'):

1. Write the freeze list as a file in the repository before cycle one.
2. Name the diagnostician's version in it, not only the task model's. If the thing judging the edits also moves, an apparent improvement can be the judge drifting, and no gate in delta 4 can tell you which it was.
3. Treat a change to that file as a new experiment, with the score series restarted rather than continued.

## Delta 3: one bit per trajectory cannot name a function, and above a log-size threshold the fix is more search turns on a cheaper judge

*Validation: no trial, no consumer report, no bare-arm screen. Eval tasks rhsi-t3 and rhsi-t4. Best-evidenced delta here, and the one this run corrected: four of the six numbers the previous version quoted appear nowhere in the paper. A bare subject may describe contrastive pairing. It is unlikely to supply that search substitutes for judge scale, or that the method reverses on short logs.*

ModularRSI turns task-level outcomes into function-level evidence by contrast: roll out K times per task, label each trajectory by binary reward, sort tasks into all-success, mixed and all-failure, and for the mixed group pair a successful and a failed trajectory **of the same task**. An all-failure task pairs a past success from memory when one exists and falls back to single-sided diagnosis otherwise. The output names the module, the evidence, the rationale and the proposed change (ModularRSI).

Inside one long log, treat attribution as search. Four continuation turns beat both a single pass and passive re-reading on the three benchmarks with the largest records: on MegaRCA-Mix (median **286K** tokens) Opus-4.8 went **0.471** single-turn to **0.608** against **0.479** passive, and TRAIL (100K) and TELBench (39K) moved the same way (Root-Cause Attribution). Search substitutes for scale: Sonnet-5 reached a turn-4 weighted F1 of **0.505** against Fable-5's 0.498 at about **64 percent** of the cost. Buy search turns before buying a more expensive diagnostician.

The stop rule has a number because the method loses on short logs. The same four turns took GPT-5.5 from 0.310 down to **0.241** on AgentRx (median **7.2K**) and from 0.516 down to **0.437** on Who&When (median **2.4K**), the published reading being that one pass had already covered the evidence and further turns pressured the judge into flipping correct labels (Root-Cause Attribution). Gate the turn count on the log's median token size, not on a constant, and run one pass below roughly **10K** tokens (ours, not the paper's: the helped benchmarks sit at 39K and above, the hurt ones at 7.2K and below, and nothing is measured between them).

## Delta 4: bound the edit, gate in series, accept on held-out, roll back by default

*Validation: no trial, no consumer report, no bare-arm screen. Eval tasks rhsi-t5, rhsi-t6, rhsi-t7 and rhsi-t11. A bare subject will say "small diffs, test before merging, be able to roll back", and will probably say "keep the evolution tasks separate from the benchmark", which is why that is a sentence here rather than a section. It is unlikely to supply the diff reviewer's adversarial instruction, acceptance on held-out performance rather than on the motivating diagnosis, or keeping rejected edits.*

An unbounded edit cannot be attributed, reviewed or reverted cleanly. ModularRSI bounds by module, decomposing the harness into Agent Loop, Tool Use, Observation Management, Context Management and Task Completion Detection, evolving each in parallel with modifications restricted to its own scope and integrating only after all have evolved (ModularRSI). ScienceBuddy bounds by size: one edit adds, removes or revises exactly **one** scoped skill, instruction or context setting, and a schema check enforces the budget **before** the candidate is evaluated (ScienceBuddy). Either works and the two compose. A diff spanning the loop and the tools at once does not, because the gates can then only accept or reject the pair.

1. **Static program check**: AST validity, imports, protocol compliance (ModularRSI).
2. **Diff review by a separate code-modifying agent**, whose stated job is rejecting changes that encode task-specific heuristics rather than general improvements (ModularRSI). Give it its own adversarial instruction: "does this look like a good change" and "is this change secretly a hard-coded answer to the evolution task" are different questions, and only the second catches the failure the gate exists for (ours, not the paper's).
3. **Execution validation on two randomly sampled tasks** (ModularRSI). Failing any gate rolls the function back, and only a modification clearing all three is retained.
4. **Accept on held-out performance, never on the diagnosis that motivated the edit.** Procedural Graphs accepts an edit only if it preserves or improves held-out validation performance, and ScienceBuddy only when the candidate's mean normalized rubric score on development tasks beats the parent, otherwise retaining the parent (Procedural Graphs; ScienceBuddy).
5. **Keep rejected edits on file** as negative signal so the loop stops re-proposing them (Procedural Graphs). It costs almost nothing and is the cheapest defence against a loop rediscovering one bad idea (ours, not the paper's).

Two conditions sit outside the chain. The evolution tasks are a training set and need a **named filtering step**: ModularRSI curated 2,000 executable tasks from sources disjoint from the downstream benchmarks, with instance-level similarity filtering and a domain analysis, and that discipline is what licenses its transfer claim (ModularRSI). If you cannot name your filtering step, the improvement curve is measuring memorisation (ours, not the paper's). And before publishing a gain, check that a **matched challenger** given the same starting knowledge and observations but not the answer fails to reach the same result (Discovery Certification Protocol). That is the gate an ordinary review lacks. The arithmetic for reporting an absence of recoveries honestly is in `evaluation-integrity`, which carries the protocol's three gates in full.

## Delta 5: feedback cost is a design parameter, and compaction is arithmetic rather than a percentage

*Validation: no trial, no consumer report, no bare-arm screen. Eval task rhsi-t8 scores the compaction arithmetic as a number rather than as advice. A bare subject will say "cache aggressively and trim the context". It is unlikely to supply the gate's two inputs, or the send-twice-then-handle rule with its byte thresholds.*

A loop whose feedback is expensive runs too few cycles to converge, and both costs are load-bearing: evaluating a candidate, and running the agent the candidate produces. Dream-RSI attacks the first by recording the discovery history as a tree and building a replay simulator over it, so candidate exploration policies are scored offline and only the survivor is deployed online, with what it discovers folded back into the tree (Dream-RSI). SoL-Pi attacks the second by making token traffic part of what the loop optimizes, cutting recorded token traffic **44.7 to 49.0 percent** and API cost by about **one third** on the 51-task EdgeBench evaluation at performance comparable to the harness it evolved from (SoL-Pi). Three of its four mechanisms lift directly:

1. **Fuse an action with its follow-up.** An optional follow-up command on the file-mutation tool removes a round trip and takes the call count from **three to two**, with separate handling kept for commands that must read the mutation's output first (SoL-Pi).
2. **Gate compaction on arithmetic, not on a percentage of the window.** At each subtask boundary, estimate the input tokens compaction would save and the cache-rewrite cost from the current context size and the cache write-to-read price ratio, and compact only when the saving wins. Later compactions carry unrecovered rewrite cost forward and demand a larger margin (SoL-Pi).
3. **Send a large observation in full twice, then by handle.** Outputs above **10 KiB** go out whole for two provider requests, and from the third are replaced by a stable handle, the original size and a **1 KB** head-and-tail excerpt, the full output kept locally for exact retrieval (SoL-Pi).

## Delta 6: a population of self-editing workers collapses onto one branch, and the credit rule is what pulls it apart

*Validation: no trial, no consumer report, no bare-arm screen, and the weakest evidence in this file: one 12-day run with one human intervention inside it. Eval task rhsi-t9. A bare subject will say "coordinate the workers". It is unlikely to supply monoculture as the expected failure, or crediting by downstream builds rather than by score.*

Agora ran **13** coding-agent workers against one shared Git repository for about **12 days**, publishing **1,703** contributions and driving the metric from **3.39 to 1.899** bits per byte, **62 percent** of the gap to a trained GPT-2 124M, with no central planner (Agora). Two details carried it: contributions are ranked by an evidence score computed as the weighted count of downstream builds **by other accounts**, so credit follows work others built on rather than work that merely scored well (Agora), and every harness and environment version is retained after each cycle, which is what makes re-evaluating an old configuration possible (ScienceBuddy).

Expect monoculture. That run spent **five days** collapsed onto a single branch, and one human-published map of where the work was concentrated broke it within **one day** by steering the agents' next frontier reads toward under-explored branches (Agora). Budget a diversity signal, and note that in the one recorded case the intervention was human.

## Caveats

- **This skill is unmeasured.** No delta has a differential number and no bare-arm screen has run, because this seat has no route to either eval arm. `status: provisional` says that and nothing weaker, and it replaced `status: active` on 2026-10-26 for that reason.
- **The attribution numbers are LLM judges reading execution records**, tool-enabled and reading artifacts on demand under read-only access rather than having the log inlined, which is the configuration the numbers belong to. The floor is the useful part: four turns of continual search let a lower-tier judge match a higher-tier one at about two thirds of the cost. The 10K-token gate is interpolated, and nothing is measured between 7.2K and 39K.
- **ModularRSI's transfer claim carries no numeric scores in the evidence alexandria holds**, so treat "improves and transfers" as directional and check the paper before quoting a figure. Two of its gates name cheap floors: execution validation ran on **two** randomly sampled tasks, and the load-bearing part of the 2,000-task evolution set is the named filtering step rather than the count.
- **SoL-Pi's savings are one 51-task benchmark at one provider's cache pricing**, so recompute the compaction gate against your own prices before its arithmetic means anything. Its input floor is small and that is the point: current context size and the cache write-to-read price ratio are the two numbers the decision needs. **Dream-RSI's replay result covers algorithm engineering, mathematical optimization and GPU kernel engineering**, where a discovery re-executes cheaply, and a domain where replay is not faithful loses the mechanism entirely.
- **The Agora findings are one 12-day run, 13 workers, one target model**, and the monoculture break is a single observed event with a human in the loop. It is a design warning rather than an effect size, and its floor is a population: at one or two workers there is no monoculture to break and delta 6 does not apply.
- Every delta above is revised or withdrawn if the claim behind it is contradicted. The claim ids in the provenance block are the addresses a contradiction lands on, and one of them is already wrong: the attribution numbers this run corrected came from a claim row no reading of the paper supports.
