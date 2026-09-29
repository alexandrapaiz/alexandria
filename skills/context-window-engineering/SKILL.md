---
name: context-window-engineering
description: The subject is the finite token budget an agent runs inside, and which tokens earn a place in it. Use when a fixed cache budget forces you to pick an eviction rule and you are weighing a scoring heuristic against a cheaper one; when an agent's accumulated history has outgrown its window and you must decide what the acting step sees as opposed to what the planning step sees; when long-document accuracy falls as the input grows even though the window is not full; when evidence buried mid-input is overlooked while the same evidence near the start or the end is picked up; or when a run has to use a value it read once and did not repeat, many steps later, and a compaction step may already have discarded it.
version: 1
status: active
provenance:
  extracted: 2026-09-29
  validated: ""
  claims: [78, 79, 80, 280, 291, 292, 293, 295, 265, 266, 267, 268, 85, 111, 112, 115, 68, 69, 70, 71]
  papers:
    - "Random Attention: Rethinking KV Cache Eviction for Efficient Reasoning — arxiv.org/abs/2609.03430"
    - "Revisiting Complete Reasoning Traces for Post-Training — arxiv.org/abs/2609.07103"
    - "PARSER: Read in Parallel, Reason in Depth for Long-Context LLM Agents — arxiv.org/abs/2609.06702"
    - "Memory as Plans: World-Action Modeling with Memory-Grounded Planning — arxiv.org/abs/2609.11561"
    - "EmbodiedSkills: A Unified Framework for Orchestrating, Training, and Deploying VLA Agents — arxiv.org/abs/2609.01281"
    - "ShallowStream: Index Shallow then Answer Deep for Streaming Video Understanding — arxiv.org/abs/2609.02780"
    - "Beyond Retrieval: Progressive Latent Memory Evolution for Streaming Video Understanding — arxiv.org/abs/2609.04131"
---

# Context window engineering

Every long-running agent eventually holds more material than its window takes,
and something has to go. The usual instinct is to get smarter about choosing:
rank the tokens, score the memories, keep the best ones. The evidence in this
cluster says that instinct is aimed at the wrong half of the problem. What
decides accuracy under a budget is almost entirely **what you protect
unconditionally** and **which component sees the history at all**. How you rank
the remainder is close to a rounding error, and the ranking pass is not free.

This skill adds to standard practice rather than replacing it. Keep doing the
things that already work: measure before you compress, keep the raw transcript
somewhere outside the window, and check that a summarization step has not
silently dropped a tool result. What follows is the set of places where recent
evidence points somewhere other than the obvious.

One boundary worth stating up front. Most of this evidence comes from one
regime: a short input and a very long generated trace, which is what a
reasoning model or a long-running agent produces. The opposite shape, a huge
input and a short answer, has different evidence and is treated separately in
the section on reading more than fits.

## Protect the input. Sample the rest.

The single largest effect anyone in this cluster measured is not a scoring
function. It is a rule about what never gets evicted.

A policy that pins the entire prompt and then evicts uniformly at random,
independently per attention head, computing no score at all, is comparable to
the strongest training-free cache evictor across four models and six reasoning
tasks in math, science and code, and it is significantly ahead in 31 of the 60
baseline comparisons in that grid (Random Attention). Because it skips the
scoring pass entirely, it serves roughly 32 to 43 percent more tokens per
second than the strongest scored baseline under paged serving.

The reason is in a controlled ablation, and the ablation is the part to
remember. Give every method the same rule, keep the prompt, and most of the
difference between methods disappears. The gain each method receives is ordered
by how much of the question its score had been losing: the method that retained
the least of the prompt gains up to 22.5 points, while the method that already
retained the most never gains more than 2 (Random Attention). Read from the
other side, the same table is starker. Without prompt protection, random
eviction scores as low as 0.231 on one task and a plain recency window scores
0.093. With it, both are within about two points of the best scored baseline.
Losing the question is catastrophic. Cutting the generated trace at random is
not.

The second half of the explanation is why the trace survives random cutting.
The trace is stored redundantly, in the text because the model restates what it
is still using, and across attention heads because every head caches its own
copy and eviction decides per head which copies die (Random Attention). A
separate paper reaches a compatible conclusion from the training side: attention
analyses and controlled token-removal studies both find that the intermediate
tokens of a reasoning trajectory contribute minimally to final reasoning quality
(Revisiting Complete Reasoning Traces). Two different methods, one about what a
cache can drop and one about what training data can omit, land on the same
property of the middle of a trace. Treating that convergence as one finding is
our reading, not either paper's.

What to do with this:

1. Make prompt protection a hard rule in your compaction step, not something
   your scoring function is expected to discover. The system prompt, the task
   statement, and the user's actual question are stated once and cannot be
   reconstructed.
2. Before adopting any ranking heuristic, run it against the null: same budget,
   same protection, random selection for everything else. If it does not beat
   that, the ranking is buying you a latency cost and nothing else.
3. Spend the engineering effort on deciding the protected set, since that is
   where the measured effect is.

## The exception is the one that describes most agents

The evidence above has a clean boundary, and the boundary is the part a builder
needs most, because agent workloads sit inside it more often than reasoning
benchmarks do.

A signal-free policy fails on exactly one thing: a fact stated once, never
restated, and needed much later. Random Attention never reproduces a passcode
announced many compression rounds before the question, while one redundancy-aware
scored evictor recovers it in a minority of trials and another in about a third
(Random Attention). The paper draws the implication itself and names the case
plainly: state that an agent reads once and consults much later is where a
content-dependent signal earns its cost, and a signal-free default is the wrong
choice there.

So the question to ask about your own agent is not which compaction algorithm is
best. It is which of two regimes you are in.

- **Self-restating work**, where the agent keeps rephrasing its current goal and
  intermediate results as it goes. Random or recency compaction over the trace
  is close to free here, and a clever scorer earns very little.
- **Read-once state**, where the agent reads a configuration value, an
  identifier, a credential handle, or a user correction early and must still
  have it forty steps later without ever having repeated it. This is the regime
  the null policy loses, and it is the ordinary shape of a long tool-using
  session.

The practical move, ours rather than the paper's, follows from that split: if
your agent has read-once state, do not ask the compaction policy to preserve it
by luck. Give it a protected region of its own, next to the prompt, and write
to that region explicitly when the agent learns a durable fact. The paper
suggests a hybrid that reserves a few slots per head for a cheap content signal
and says plainly that it did not evaluate one, so the hybrid is a direction
rather than a result.

## Read in parallel, reason in sequence

When the material is larger than the window, the common answer is to stream it
through a compact memory: read a chunk, fold it into a running summary, repeat.
That design makes document order into dependency depth, and it inherits three
failures because of it.

The alternative that measured better decouples the two orders. Bind one frozen,
lightweight subagent to each chunk, give a lead agent the question but never the
document, and run scatter-gather rounds: the lead broadcasts a focused query,
every subagent reads its own chunk in parallel and returns a finding or
abstains, and the lead conditions its next query on what came back (PARSER). On
multi-hop question answering over contexts from 7K to 896K tokens, this beats
the strongest sequential-memory baseline by 5.7 points on average with a 4B
backbone and by 12.0 points at 896K, and a 9B version beats a frontier model
with a native million-token window by 6.3 points (PARSER).

The controlled experiments are more useful than the headline, because they name
the failure the architecture removes. Three perturbations were varied
independently over 512 questions each: where in the document the evidence sits,
whether the evidence appears in its logical dependency order or reversed, and
how far apart two pieces of evidence are. Sequential memory swings on all three.
Parallel reading stays nearly flat, because every chunk is re-read under a fresh
query each round, so access is symmetric with respect to position (PARSER). If
your long-context system is failing in a way that moves when you shuffle the
input, that is the diagnosis.

Four design details from the full text that the result depends on:

1. **Chunk size matters, and smaller is better within the range tested.**
   Removing chunking entirely, so one subagent reads the whole document, drops
   accuracy notably, especially on the long subsets, and performance degrades
   steadily as chunk size grows.
2. **The subagents can be small and frozen.** Going from a 2B to a 4B subagent
   improves the average from 78.26 to 84.57, and going to 9B saturates. The
   reading task is genuinely easy once the query is focused and the span is
   short.
3. **Only the lead agent needs training.** All the learnable behavior sits in
   the lead, optimized with reinforcement learning against a binary exact-match
   reward, with observation tokens masked out of the gradient (PARSER). The same
   lead agent also coordinated thinking subagents and shell-tool search
   subagents without retraining.
4. **The known failure is an unverifiable finding.** A subagent sees only the
   query and its own chunk, not the reasoning history, so an underspecified
   query can produce a confident local conclusion the lead cannot check against
   a source, and the lead may over-trust it. The paper reports this as
   occasional and says cross-validation across subagents usually catches it.
   Our addition, not the paper's: have subagents return a span or quotation with
   every finding, so the aggregation step has something to check.

## Give history to the planner, not to the executor

The third pattern is the one that generalizes furthest, and it is the reason
this cluster holds together. In all three settings the winning move is the same:
stop feeding accumulated history to the component that acts.

A robotics framework makes this explicit. Instead of conditioning the action
model on a growing visual history, it stores each completed segment as a record
with a language instruction and a few frames, uses that episodic record at
planning time to produce a compact next-segment plan, and hands the executor
only that plan (Memory as Plans). The executor's context length stays fixed. The
reported result is 83.3 percent overall success on a memory-dependent
manipulation benchmark and 78.0 percent on real-robot tasks, with executor
latency approximately constant as task history grows.

The structural claim is separable from the robots, and it is the transferable
part: **long-horizon history is evidence for deciding what to do next, not input
for doing it.** Whether the executor is a robot arm, a code-writing subagent, or
a tool call, the same split applies. Let a planning step read the long record
and emit a short, explicit instruction. Let the acting step run against a
bounded context it can cache.

### A contradiction inside the cluster, and what it actually is

Our claim graph records a contradiction here, between the 83.3 percent above and
a second paper reporting 12.5 percent average success on memory-dependent tasks
from the same benchmark (EmbodiedSkills). Reading both papers resolves it, and
the resolution is worth more than the edge was.

The numbers are measured on different task sets. The 12.5 percent is a
macro-average over the four tasks that require multiple past observations, where
that paper leads every published baseline it lists, the best of which reaches
7.3 percent. The 83.3 percent is an overall average across the benchmark's full
nine tasks, five of which require only a single past observation. On the same
four multi-observation tasks, the memory-as-plans system reports 82, 94, 100 and
96 percent (Memory as Plans), against 19, 9, 6 and 16 percent (EmbodiedSkills).

So the two rows do not contradict each other as propositions. They compare two
architectures on one benchmark, and the comparison survives the correction: an
executor conditioned directly on task-adapted history scores in the low tens on
the tasks that need history, and an executor handed a planner-written plan
scores in the high eighties to high nineties on those same tasks. Three cautions
before leaning on it. The two systems were trained differently, so this is not a
controlled comparison. The planner-based system is not uniformly best, losing on
two tasks to a growing-visual-window baseline that reaches 100 percent where it
reaches 66 and 94. And both are robot manipulation, so carrying the number
across to a text agent is unsupported. What carries is the architecture, not the
margin.

Our rule of thumb, not the papers': when an agent starts to slow down or
degrade as a session lengthens, check first whether the acting step is being
handed the history at all. If it is, the fix is usually a boundary rather than a
better summarizer.

## Make the steady-state cost cheaper than the answer cost

The last pattern is about when you pay. An agent that watches a stream has an
asymmetric workload: material arrives continuously, and questions arrive
occasionally. That makes per-item ingestion cost, not per-question cost, the
first-order system cost, and most designs get this backwards by running the full
model over everything on arrival (ShallowStream).

The measured alternative uses only the shallow layers of the model to encode
incoming frames and build a retrieval index at the same time, keeping an
always-on lightweight index rather than a full-depth one (ShallowStream). At
query time it scores candidates using the attention weights those same shallow
layers already produced, and selects with a diversity-aware rule so the
retrieved evidence is not all near-duplicates (ShallowStream). Because the full
model never prefills the stream, the cache stops growing in proportion to model
depth (ShallowStream). The reported outcome is accuracy on par with the
strongest streaming methods at a large reduction in per-frame prefill and
end-to-end latency.

A second streaming system attacks the budget from the storage side. Its
argument is that keeping history in an external bank and retrieving from it on
demand leaves the retrieved evidence sitting in the window as variable-length
extra context, so it moves from storing and retrieving to retrieving and
internalizing, building a compact working memory that evolves as the stream
runs (Beyond Retrieval). Concretely it organizes history into short, mid and
long-term levels under a fixed memory budget with adaptive consolidation
between them (Beyond Retrieval). Once a query arrives, it
gives groups of latent tokens progressively expanding scopes so they can pull
evidence from their level and fold it into a fixed-length representation
(Beyond Retrieval), and a confidence-guided optimization step refines those
tokens and the retrieved evidence jointly using group-wise predictive entropy
(Beyond Retrieval). The transferable shape, and our reading rather than the
paper's, is the tiering discipline: a fixed total budget, explicit levels, and a
consolidation rule that runs on arrival instead of a compaction that panics when
the window fills.

Both of these are multimodal video systems. The mechanism that transfers is the
asymmetry argument, which is architecture-independent: if ingestion is continuous
and queries are sparse, the ingestion path must be the cheap one, and it is
worth using a deliberately weaker model for it. Whether a shallow-layer index
specifically works for text agents is untested here.

## Where the full text narrows our claim rows

Read the papers before quoting the rows. Three of the rows behind this skill
read stronger than their source.

- **The strongest claim in the cluster is scoped, and the row states it flat.**
  Our row says the selection signal used by existing cache compression methods
  contributes almost nothing to performance. The paper's own limitations section
  says the significant wins "establish that Random Attention is competitive, not
  that scores carry no information," restricts the claim to decode-phase
  eviction with short prompts and long traces against training-free evictors,
  calls it a claim about the aggregate rather than every cell, and notes that a
  non-significant cell is not by itself evidence of equality. Four comparisons
  across the paper's two accuracy tables favour a baseline significantly.
- **Matching the strongest evictor has four exceptions.** Our row reports a
  match across four models and six tasks without naming where it does not hold.
  Code reasoning is the systematic case, on the two larger models, and the paper
  traces it to long code prompts consuming up to half the budget before
  selection starts. The throughput figure also depends on the workload: at short
  generations, every compressed method serves less than uncompressed attention.
- **Both redundancies are asserted, one is measured.** Our row states that
  reasoning traces protect themselves through redundancy in the text and across
  attention heads. Cross-head pooling is shown directly, but only in a
  planted-fact probe on one 4B model where the text is non-redundant by
  construction. Text-level redundancy is inferred rather than measured, and the
  paper says so. It also reports that a shared draw, keeping the same positions
  in every head, scores within a couple of points of the per-head version on
  real traces, which means the cross-head mechanism is a second line of defence
  rather than the cause of the benchmark result.

All three rows are filed for revision in docs/ideas.md.

One provenance note the rows do not carry. The streaming-video paper behind the
shallow-index section is labelled "Work in Progress" by its own authors, and the
complete-reasoning-traces paper is the one paper in this cluster this skill's
author could not read in full, because arXiv serves no HTML rendering for it;
only its abstract, which is peer-reviewed as an EMNLP 2026 Findings paper, was
read. Weight both accordingly.

## Caveats

The cache-eviction evidence covers decode-phase eviction on four models, three
of them one family, all using grouped-query attention with eight or ten
key-value heads per layer. Architectures where per-head independence is
unavailable, such as multi-head latent attention or multi-query attention, were
not tested. The regime is short prompts and traces of several thousand to 32K
tokens at 10 to 50 percent compression; workloads where the input itself fills
the cache fall outside it. Significance is per-comparison with no correction for
multiple comparisons.

The parallel-reading evidence is multi-hop question answering on two datasets,
one in-distribution and one out, with 4B and 9B backbones from one family. It
establishes robustness to evidence placement and an accuracy gain over
sequential memory on that task shape. It does not establish that the pattern
holds for tasks where a chunk cannot be judged in isolation at all.

The memory-as-plans evidence is robot manipulation in simulation and on one
real arm, with 50 demonstrations per task, and it depends on segment boundaries
the benchmark already provides. Automatic segment discovery is named as
unfinished work by the authors, which matters for any agent setting where the
segmentation would have to be invented.

The two streaming systems are multimodal video, and every number in them is a
video benchmark. Nothing here measures a text agent.

This skill revises when its evidence does. If a source claim is contradicted by
later work, or if a claim row listed above is corrected in the library, the
section resting on it is rewritten or removed rather than left standing.
