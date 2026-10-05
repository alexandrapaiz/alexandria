---
name: context-window-engineering
description: Two measured findings about spending a finite token budget that a strong model does not give unprompted. Use when a fixed KV cache budget forces a choice of eviction rule and you are weighing a scoring heuristic against a cheaper one; when you are about to adopt a ranking or scoring function for compaction and need to know what baseline it has to beat; when long-document accuracy falls as the input grows even though the window is not full; when evidence buried mid-input is overlooked while the same evidence near the start or the end is picked up; or when a multi-hop question over material larger than the window is answered by folding chunks into a running summary.
version: 4
status: active
provenance:
  extracted: 2026-09-29
  revised: 2026-09-30
  validated: ""
  differential_screen: "2026-09-30, bare-arm pre-screen on the benchmark-class subject (skills/_validation/results/2026-09-30-bare-arm-differential-screen.md). 2 of 4 candidates qualified, both as partials. cwe-c2 and cwe-c4 passed bare and their sections were cut."
  reviews:
    - "none filed yet. The lane is open at reviews/ (ADR-38); see reviews/README.md for what this skill most wants reported."
  revisions:
    - "2026-09-30 (ADR-38, the quality bar): 403 lines to under 120. Cut the read-once-state section and the planner-executor section because the bare subject gave both unprompted and in more useful form (cwe-c2, cwe-c4); cut the streaming-ingestion section because both its papers are multimodal video and nothing in it has ever been measured on a text agent. Claims 85, 265-268, 111, 112, 115 and 68-71 leave the provenance with those sections. Claim 85 is in deprecated_claims and this skill no longer cites it, which resolves the ADR-37 trigger by removing the citation and not by accepting the deprecation: the resolution stands in docs/ideas.md and the two rows still do not contradict each other."
  claims: [78, 79, 80, 280, 291, 292, 293, 295]
  papers:
    - "Random Attention: Rethinking KV Cache Eviction for Efficient Reasoning — arxiv.org/abs/2609.03430"
    - "Revisiting Complete Reasoning Traces for Post-Training — arxiv.org/abs/2609.07103"
    - "PARSER: Read in Parallel, Reason in Depth for Long-Context LLM Agents — arxiv.org/abs/2609.06702"
---

# Context window engineering

Two findings, both about a baseline you are probably not running.

## Apply: the builder's checklist

1. **Your ranking heuristic has beaten protected-random at the same budget.** Until it
   has, you do not know the scorer does anything (delta 1).
2. **Compaction protects the whole prompt outside the score's reach**, where the
   measured effect lives (delta 1).
3. **A multi-hop reader re-queries its chunks each round from a lead that never sees the
   document**, rather than folding chunks into a summary once (delta 2).
4. **You have shuffled the input and reversed the evidence order.** If accuracy moves,
   document order has become dependency depth (delta 2).

## Delta 1: the null policy is the baseline, and almost nothing beats it

*Validation: no trial and no consumer report. Bare-arm screen cwe-c1, 2026-09-30: partial. Asked to choose an eviction policy, the bare subject recommended keeping the prompt plus sinks plus a recency window, so the prescription itself is not a delta; it never proposed a random-eviction control and never priced the protected set against the scorer. What qualified is the null arm and the magnitudes. Eval tasks cwe-t1, cwe-t2.*

Pinning the entire prompt and then evicting **uniformly at random, per attention head,
computing no score at all** is comparable to the strongest training-free cache evictor
across four models and six reasoning tasks, and significantly ahead in 31 of 60 baseline
comparisons (Random Attention, claim 78), while serving **32 to 43 percent more tokens
per second** for skipping the scoring pass.

The ablation is the part to keep. Give every method the same rule, keep the prompt, and
most of the difference between methods disappears: the method retaining the least of the
question **gains up to 22.5 points**, the one already retaining the most **never gains
more than 2** (claim 79). Random eviction scores as low as 0.231 unprotected and is the
best policy in all four settings once protected.

The decision rule: a compaction scorer is an optimisation with a control, and the
control is protected-random at the same budget. Run it first.

1. Pin the system prompt, task statement and user question unconditionally, not as a
   scoring bonus. Outside the score.
2. Build the null arm: same budget, same protection, uniform random eviction per head
   for the rest.
3. Adopt the scorer only if it beats the null by more than the **32 to 43 percent
   throughput** the null hands you free.
4. Expect the question to be unrecoverable and the trace nearly free to cut; the trace
   restates itself (claims 80, 280).

## Delta 2: for multi-hop, re-query in parallel rounds; map-reduce once is not it

*Validation: no trial and no consumer report. Bare-arm screen cwe-c3, 2026-09-30: partial. The bare subject diagnosed the serial recurrence and volunteered the shuffle-and-reverse test, so the diagnostic is not a delta; it then prescribed one-shot parallel extraction into a retrieval index, losing the iterative conditioning that carries multi-hop. Eval tasks cwe-t4, cwe-t5.*

Bind one frozen lightweight subagent to each chunk, give a lead agent the question but
**never the document**, and run scatter-gather rounds: the lead broadcasts a focused
query, each subagent reads its own chunk in parallel and returns a finding or abstains,
and the lead conditions its next query on what came back (PARSER, claim 291). On multi-
hop QA from 7K to 896K tokens this beat the strongest sequential-memory baseline by
**5.7 points on average with a 4B backbone, 12.0 at 896K**, and a 9B version beat a
frontier model with a native million-token window by **6.3 points** (claim 292).

Varying evidence position, dependency order and distance independently over 512
questions each, sequential memory swings on all three and parallel reading stays flat,
because every chunk is re-read under a fresh query each round (claim 293).

The decision rule: one-shot map-reduce into an index gives up the property that matters.
The lead's second query must be able to depend on the first round.

1. Chunk, and keep chunks small. One reader over the whole document loses accuracy,
   worst on the long subsets.
2. Put a frozen reader on each chunk. **Floor is 4B**: 2B costs six points of average
   accuracy, 9B saturates, a frontier model here is wasted spend.
3. Run rounds, not one pass; the lead never sees the document.
4. Train only the lead if you train anything (claim 295).
5. Require a quoted span with every finding (ours, not the paper's): a subagent sees
   only its chunk, so an underspecified query yields an unverifiable finding the lead
   may over-trust.

## Caveats

- Cache-eviction evidence is decode-phase eviction, short prompts, traces of several
  thousand to 32K tokens at 10 to 50 percent compression, four models, three of one
  family, all grouped-query attention with 8 or 10 KV heads per layer. **That is the
  floor for the per-head half**: under multi-query or latent attention only the prompt
  protection carries over, and workloads where the input itself fills the cache are
  outside the regime.
- Claim 79 reads flatter than its paper, which establishes that random eviction is
  *competitive*, not that scores carry no information. Four comparisons in its tables
  favour a baseline significantly, code reasoning is the systematic exception on the two
  larger models, the throughput figure inverts at short generations, and claim 80's
  text-level redundancy is inferred, not measured.
- Parallel-reading evidence is multi-hop QA on two datasets, 4B and 9B backbones from
  one family, and says nothing about tasks where no chunk can be judged in isolation.
  Claim 280's paper was read in abstract only, arXiv serving no HTML.

## What this file no longer carries

Read-once protected regions and the planner-executor boundary were cut 2026-09-30
because the bare subject gave both unprompted and better; streaming ingestion was cut
because its papers are video and nobody measured the transfer. Still do the first two.
Receipts, with the bare answers, in `skills/_validation/results/2026-09-30-bare-arm-
differential-screen.md`.
