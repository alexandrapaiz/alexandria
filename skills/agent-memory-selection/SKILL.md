---
name: agent-memory-selection
description: Three measured findings about what a long-horizon agent writes down about a conversation and what it reads back for one question. The subject is the write-versus-read split in what an assistant remembers between sessions, which is a store and a retrieval path rather than anything inside one model call. Use when choosing between extracting facts at ingestion and storing raw turns; when an LLM extraction or knowledge-graph build sits on the write path of every message; when deciding whether a reranker is worth its call on a retrieval path; when a memory system's accuracy is being compared against another at a different context size; when a memory graph is traversed with several model calls per query; or when an assistant with memory starts answering questions it should have said were never discussed.
version: 1
status: provisional
provenance:
  extracted: 2026-10-13
  validated: ""
  differential_screen: "not run. This seat has no route to either eval arm (no GROQ_API_KEY in .github/workflows/agent-skill.yml, no benchmark provider in pipeline/budget.py), both queued in docs/agents/pending-workflow-changes.md. Every section below is unscreened, and each Validation tag names what this run expects a bare subject to already supply."
  reviews:
    - "none filed yet. The lane is open at reviews/ (ADR-38); see reviews/README.md for what this skill most wants reported."
  claims: [982, 983, 984, 985, 986, 721, 722, 723, 724]
  papers:
    - "When Does Selection Replace Extraction? A Pre-Registered Test of Agent Memory with a Typed Decision Model — arxiv.org/abs/2609.34227"
    - "Jev-Mem: System-One-Controlled Agentic Memory for Efficient AI Agents — arxiv.org/abs/2609.23986"
---

# Agent memory selection

Three findings about conversational memory, each a place the default costs orders
of magnitude more than the measured alternative, or buys a number nobody scored.

## Apply: the builder's checklist

1. **The keep ratio is computed first**: candidates returned over candidates
   read (delta 2).
2. **At a tight ratio the store is raw turns with their dates** and one bounded
   call is the read path, not extraction on the write path, and no two systems
   are compared except at matched tokens (delta 1).
3. **At a generous ratio the spend moves to compactness**, extraction's ground,
   and ranking is close to free of effect (delta 2).
4. **Correct abstention is scored apart from accuracy** before a reranker ships
   (delta 3).

## Delta 1: write raw, select at read, and know what the premium costs

*Validation: none yet, claim provenance only. Unscreened: no bare-arm screen has run (see `differential_screen`). Recorded before measurement, this seat expects a bare subject to reach for an extraction or graph memory, because that is what the deployed systems do, and not to supply the 3-point bound or the cost ratio. Eval tasks ams-t1, ams-t4.*

On held-out conversations at a tight budget, storing raw turns and spending one
selection call at read time was **non-inferior to an LLM-extraction memory, one
sided 95 percent bound of 3.0 points against a pre-registered 5-point margin, at
3,061 times less write cost** (When Does Selection Replace Extraction): 77.0
against 77.5 percent at matched context, $1.865 per 1,000 turns against $0.00061.
Blind human grading moved the difference to 1.7 to 2.6 points and the bound to
4.7, so the result survives its own sensitivity analysis. Extraction is a
purchase whose tight-budget price is now known, and under 3 points for three
orders of magnitude of write cost is a bad trade unless those are the product.

1. Store each turn verbatim **with its session date**, the field temporal
   questions are answered from and the cheapest one here.
2. Shortlist by embedding similarity. **30 candidates is the measured setting**
   and 11.5 percent of answerable questions are lost here, so widen it first.
3. Select with **one bounded call per query** returning a score over fixed
   options, not generated text: 273ms p50 against 816ms for a generative
   listwise reranker, at accuracy the study could not separate (bound 2.0).
4. **Never compare two memory systems at their own default k.** Every number
   here holds at matched tokens, and these systems reorder without it.

## Delta 2: whether ranking matters is a property of the budget, not of your pipeline

*Validation: none yet, claim provenance only. Unscreened. This seat expects a bare subject to argue either direction with no threshold, because the literature it learned from disagrees with itself here, which is what this section resolves. Eval tasks ams-t2, ams-t3.*

One reranker in one pipeline was worth **+17.4 points when 3 of 30 candidates
were kept and +1.5 points when 20 of 30 were kept**, and on a second benchmark
+9.1 against +1.1 (When Does Selection Replace Extraction). At the generous end
the field reorders: extraction reached 82.4 percent on 1,238 tokens, above the
raw-turn path's 77.6 percent ceiling. The authors read the published disagreement
over whether ranking is the bottleneck as two groups measuring at two keep
ratios, which they offer as interpretation and not as a tested claim.

1. Measure candidates returned and candidates read. **The ratio is the input.**
2. **Keeping under roughly a quarter: buy selection**, because ordering decides
   what survives truncation. Double-digit gains at 3 of 30, on both benchmarks.
3. **Keeping most of them: stop paying for ranking** and spend on meaning per
   token. 1.1 to 1.5 points does not pay for a call per query.
4. Re-measure when the budget moves: the ratio belongs to the deployment.

## Delta 3: the arm that scores better abstains worse

*Validation: none yet, claim provenance only. Unscreened, and the section this seat most expects a bare subject to miss, because the cost appears only when abstention is scored apart from accuracy. Eval task ams-t5.*

On adversarial questions, whose correct answer is that the thing was never
discussed, **plain similarity search abstained correctly 63.6 percent of the
time, with a typed selector 54.1 percent, and with a generative reranker 48.8
percent** (When Does Selection Replace Extraction). The ranking that raised
accuracy by 17.4 points lowered correct abstention by about 9, and it held on a
second conversation set (54.2 against 65.3) and on the other benchmark at a
generous budget (63.3 against 70.0). Relevant-looking context makes an answer
model less willing to say nothing relevant exists, so a reranker trades recall
of the right evidence for confidence in the wrong kind.

1. Hold out questions **whose correct answer is that the memory has nothing**,
   which is a benchmark's adversarial split, and a product can mine its own.
2. Score **accuracy and correct abstention separately**: one blended number
   hides this, and abstention is a shipping gate wherever the assistant must be
   able to say "you never told me that".
3. If abstention regresses past what the product carries, keep the selector and
   **give it an explicit nothing-relevant option** (ours, not the paper's).

## Caveats

- Two benchmark families, LoCoMo and LongMemEval, gpt-4o-mini answering and
  judging, 778 questions over five held-out conversations, LoCoMo's dialogues
  model-generated. A claim later contradicted gets this file revised or retired
  with its numbers (ADR-37). The selector measured is one closed model
  (jev-1.13.0) and the procedure's floor is lower: any ranker returning a
  bounded score in one request, a MiniLM-class cross-encoder at the cheap end.
- The raw-turn ceiling is a read-path limit and not a storage one: 11.5 percent
  of questions lose evidence at the shortlist, 9.2 percent at selection,
  temporal worst at 22.7 percent, and a 150-turn shortlist recovered most of it
  post-hoc. Raw turns also reach the selector as user-written text, so selection
  is reachable by injected content, which the study did not test and says so.
- Cut to hold the three-module cap (ADR-40 item 4): **the typed control plane**,
  the write path behind Jev-Mem's 158-second build (6.6x) and 0.93-second query
  latency, including the split of candidate discovery from relation judgment
  that stops controller cost tracking memory size. Queued as its own skill in
  `docs/research/reading-queue.md`. Read it knowing Jev-Mem's 11.0 percent gain
  is against its own comparator set: the pre-registered test put it at 70.6
  against 77.0 percent at matched context. Filed in docs/ideas.md.
