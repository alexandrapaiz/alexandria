---
name: recursive-harness-self-improvement
description: Evidence-backed method for loops where an agent reads its own failed runs, rewrites its own scaffold unattended, then keeps or reverts each edit on measured evidence. The editor is the agent, not a person, and no weights are trained. Use when an automated loop edits its own prompts, tool code or memory and keeps what measures better, when unattended self-edits raise the score on the tasks the loop evolves against while real work does not, when choosing the gate that accepts or reverts a proposed edit, when bounding how much one edit may touch, when attributing a failure to one function inside a long execution log, when the loop's own diagnosis costs more than its edits gain, when several automated workers rewrite one shared repository and converge on a single idea, or when an unattended run reports a win you have to judge.
version: 1
status: active
provenance:
  extracted: 2026-09-22
  validated: ""
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

This skill covers the loop where the agent is the one doing the editing. It
reads its own failed runs, decides which part of its own scaffold caused the
failure, writes a change to that part, measures the change, and keeps or
discards it. The model weights never move.

That is a different job from designing a harness well, which a competent
engineer already does by hand and which harness-engineering covers. It is
also a different job from post-training, where the thing that updates is the
weights. What is specific here is that the artifact being changed and the
thing proposing the change are the same system, so every safeguard a human
reviewer would have supplied has to be built into the loop instead.

This skill adds to standard engineering practice, it does not replace it.
Keep version control on the scaffold, keep a held-out evaluation set, and
keep full trajectory logs, because none of the procedures below work without
them. The sections are the deltas: what a self-editing loop needs that an
ordinary refactor does not.

## 1. Write the freeze list before the first cycle

A self-improving loop that changes several things at once produces no signal
about any of them. Every working design in this cluster splits the system
into a part that moves and a part held still, and alternates.

ScienceBuddy runs two nested loops with opposite freezes. In the inner loop
the task model's parameters are fixed and a separate, fixed auxiliary model
diagnoses trajectories and proposes bounded harness edits. In the outer loop
the harness and the scoring rubrics are fixed while the model is trained with
rubric rewards (ScienceBuddy). The auxiliary diagnostician being fixed
matters as much as the task model being fixed: if the thing judging the edits
also changes, an apparent improvement can be a drifting judge.

RSIAgent freezes on a schedule instead. Its memory accumulates during an
exploration phase, is marked frozen when the curriculum agent signals that no
informative tasks remain, and is then served read-only to every downstream
task (RSIAgent). SoL-Pi freezes further out still, pinning mechanism source
code, configuration, capability tolerances and acceptance rules before the
evaluation run begins (SoL-Pi).

In practice (ours, not the papers'): write the freeze list as a file in the
repository, name the diagnostician's version in it, and treat a change to the
list as a new experiment rather than a continuation of the old one.

## 2. The whole gain can come from the scaffold

The reason to run this loop at all is that the scaffold carries more headroom
than it looks like it does.

RSIAgent lifted two open-source models past frontier closed-source models on
OSWorld-v2 and Agents' Last Exam without updating a single parameter
(RSIAgent). Its recursive phase is what bought the difference: the same
system without recursion scored 71.97 percent partial and 37.80 percent
binary on OSWorld, and with recursion 78.98 and 42.68 (RSIAgent). The
downstream gain then comes from frozen memory handed to the same base model
as context, with no training step anywhere (RSIAgent).

Two findings say the starting scaffold matters less than the loop. Beginning
from a minimal skeleton, self-evolving Procedural Graphs matched or surpassed
hand-designed graphs, and the same refinement process repaired a deliberately
flawed expert prior rather than inheriting it (Procedural Graphs).

The practical reading (ours, not the papers'): do not spend a week
hand-perfecting the seed scaffold before turning the loop on. Spend it on the
gates in section 5 instead, because a thin seed with good gates converges and
a good seed with no gates decays.

## 3. Localize the failure before proposing an edit

The signal an outcome gives you is one bit for a whole trajectory, and one
bit cannot say which function to change. Two papers attack that gap from
different ends.

ModularRSI converts task-level outcomes into function-level evidence by
contrast. It rolls the agent out K times per task, labels each trajectory by
binary reward, sorts tasks into all-success, mixed and all-failure groups,
and for the mixed group pairs a successful and a failed trajectory of the
same task and compares them. For an all-failure task it pairs a past success
from memory when one exists, and falls back to single-sided diagnosis when
none does. The output is a structured finding naming the module, the
evidence, the rationale and the proposed change (ModularRSI).

When the failure has to be found inside one long log rather than across a
pair, treat attribution as search rather than as a single judgment. Four
turns of continual search over an execution log raised attribution F1 from
0.349 to 0.498 for one model and from 0.478 to 0.620 for another, against
0.401 and 0.559 for passively continuing to read (Root-Cause Attribution).
The same work found that search substitutes for scale: with continual search,
lower-tier judges matched or surpassed higher-tier ones (Root-Cause
Attribution). Spend the budget on more search turns before spending it on a
more expensive diagnostician.

There is a stop rule attached. On short trajectories the extra turns did not
help and sometimes hurt, because the first pass had already covered the
evidence and further turns pressured the judge into flipping correct labels
(Root-Cause Attribution). Gate the turn count on log length, not on a
constant.

## 4. Bound what one edit is allowed to touch

An unbounded edit cannot be attributed, cannot be reviewed, and cannot be
reverted cleanly.

ModularRSI decomposes the harness into five functional modules, Agent Loop,
Tool Use, Observation Management, Context Management and Task Completion
Detection, and evolves each independently and in parallel with modifications
restricted to that module's scope, integrating and resolving conflicts only
after all modules have evolved (ModularRSI). ScienceBuddy bounds by size
instead of by module: one proposed edit adds, removes or revises exactly one
scoped skill, instruction or context setting, and a schema check enforces the
edit budget before the candidate is ever evaluated (ScienceBuddy).

Either bound works, and the two compose. What does not work is a diff that
spans the loop and the tools at once, because section 5's gates can then only
accept or reject the pair.

## 5. Gate every edit, and roll back by default

This is the section that separates a loop that improves from one that drifts.

ModularRSI puts three gates in series after every function update. A static
program check comes first, covering AST validity, imports and protocol
compliance. A diff review by a separate code-modifying agent comes second,
and its specific job is to reject changes that encode task-specific
heuristics rather than general improvements. Execution validation on two
randomly sampled tasks comes third. Failing any gate rolls the function back,
and only a modification that clears all three is retained (ModularRSI).

The acceptance criterion itself should be held-out performance, not the
diagnosis that motivated the edit. Procedural Graphs accepts a graph edit
only if it preserves or improves held-out validation performance, and it
keeps the rejected edits on file as negative signal so the loop stops
re-proposing them (Procedural Graphs). ScienceBuddy accepts a candidate
harness only when its mean normalized rubric score on the development tasks
beats the parent harness, and otherwise retains the parent (ScienceBuddy).

Two things worth copying that are easy to skip (ours, not the papers'). The
diff reviewer needs its own adversarial instruction, because "does this look
like a good change" and "is this change secretly a hard-coded answer to the
evolution task" are different questions and only the second catches the
failure mode the gate exists for. And retaining rejected edits costs almost
nothing and is the cheapest defense against a loop that spends its budget
rediscovering the same bad idea.

## 6. Evolve on tasks the benchmark never sees

A self-improving loop optimizes whatever it is scored on, so the tasks it
evolves against are a training set and have to be treated as one.

ModularRSI curates 2,000 executable evolution tasks from external sources
that are disjoint from the downstream benchmarks, applying instance-level
similarity filtering and a domain analysis to hold the overlap down
(ModularRSI). That discipline is what licenses its headline result: the
evolved harness improved unseen in-domain and out-of-domain tasks and
transferred across foundation models, which is a claim about generalization
that a contaminated evolution set could not support (ModularRSI).

The test to apply to your own loop (ours, not the paper's): if you cannot
name the filtering step that keeps your evolution tasks away from your
evaluation tasks, your improvement curve is measuring memorization and you
have no way to tell.

## 7. Make feedback cheap, and score tokens as well as accuracy

Both costs in this loop, the cost of evaluating a candidate and the cost of
running the resulting agent, are load-bearing, because a loop whose feedback
is expensive runs too few cycles to converge.

Dream-RSI attacks the first by recording the discovery history as a tree,
building a replay simulator that can replay any node of it, and evaluating
candidate exploration policies inside that simulator before any of them touch
an online evaluation. Only the surviving policy is deployed online, and what
it discovers is folded back into the tree (Dream-RSI).

SoL-Pi attacks the second by making token traffic part of what the loop
optimizes, cutting recorded token traffic by 44.7 to 49.0 percent and API
cost by about a third on a 51-task benchmark while holding performance
comparable to the native harness (SoL-Pi). Three of its mechanisms are worth
lifting directly:

1. Fuse an action with its follow-up. Letting the file-mutation tool accept
   an optional follow-up command removes an entire model round trip and takes
   the call count from three to two, with separate handling preserved for
   commands that must read the mutation's output first (SoL-Pi).
2. Gate compaction on arithmetic, not on a threshold. At each subtask
   boundary, estimate the tokens compaction would save and the rewrite cost
   from the current context size and the cache write-to-read price ratio, and
   compact only when the saving wins, requiring a larger margin as the
   context approaches the window limit (SoL-Pi).
3. Send a large observation in full twice, then by handle. Outputs above 10
   KiB go out whole for the first two provider requests, and from the third
   are replaced by a stable handle, the original byte size and a 1 KB excerpt,
   with the full output kept locally for exact retrieval (SoL-Pi).

## 8. When several agents evolve one shared artifact

A population of self-editing agents on one codebase behaves differently from
one agent on its own, and the difference is worth planning for.

Agora ran 13 coding-agent workers against a shared Git repository for about
12 days. They published 1,703 contributions and drove the evaluation metric
from 3.39 to 1.899 bits per byte, closing 62 percent of the gap to a trained
GPT-2 124M model, with no central planner (Agora). Two design details carried
that. Contributions are ranked by an evidence score computed as the weighted
count of downstream builds by other accounts, so credit accrues to work
others actually built on rather than to work that merely scored well (Agora).
And every harness and environment version is retained after each cycle, which
is what makes cross-cycle reuse and re-evaluation of an old configuration
possible at all (ScienceBuddy).

The failure to expect is monoculture. The Agora run spent five days with the
community collapsed onto a single branch, and a single human-published map of
where the work was concentrated broke it within one day by steering the
agents' next frontier reads toward under-explored branches (Agora). Budget
for a diversity signal, and note that in the one recorded case the
intervention was human.

## 9. Certify the gain before you believe it

An automated loop reporting its own improvement is the weakest evidence in
this whole cluster, and there is now a protocol for hardening it. The
Discovery Certification Protocol audits an agent's claimed outcome through
three gates: a statistically significant improvement over baseline by a
lower-confidence bound, zero recoveries of the same result by a matched
challenger agent within a finite-sample bound, and a measured positive effect
of truthful feedback over a calibrated neutral policy (Discovery
Certification Protocol).

The middle gate is the one most builders have no analogue for, and it is the
one worth adding first (ours, not the paper's). It asks whether a comparable
agent handed the same task reaches the same result without your loop. If it
does, the loop is not what produced the gain.

Pre-register the analysis before the run, not after, which is the discipline
the whole protocol rests on (Discovery Certification Protocol).

## Caveats

- The cost and mechanism results are single-system measurements on single
  benchmarks. SoL-Pi's savings are from one 51-task benchmark with a specific
  cache pricing ratio, and the compaction gate has to be recomputed against
  your provider's prices before its arithmetic means anything.
- ModularRSI's transfer claim is reported without numeric scores in the
  evidence alexandria holds, so treat "improves and transfers" as directional
  and check the paper before quoting a figure.
- The Agora population findings are one 12-day run with 13 workers and one
  target model, and the monoculture break is a single observed event with a
  human in the loop. It is a design warning, not a measured effect size.
- Dream-RSI's replay result covers algorithm engineering, mathematical
  optimization and GPU kernel engineering, all domains where a discovery can
  be re-executed cheaply (Dream-RSI). A domain where replay is not faithful
  loses the mechanism entirely.
- The root-cause attribution numbers come from LLM judges reading execution
  logs with a median size of hundreds of thousands of tokens, and the stop
  rule for short trajectories was observed on two benchmarks.
- These findings are from 2026 papers and carry alexandria claim provenance.
  If a source claim is later contradicted, this skill will be revised or
  deprecated.
