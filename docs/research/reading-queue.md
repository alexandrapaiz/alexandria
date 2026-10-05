# Reading queue

Append-only, one line per item. Written by the skill seat when a skill
needs a paper the library has not read in full, or when reading raised
a question. Drained by the research seat (reads, files, strikes the
line with date and PR) and by the engineer, who feeds queued arXiv ids
to distill ahead of the daily intake (ADR-35).

Format: `- [ ] arxiv:<id> — why — asked by skills/<slug> — YYYY-MM-DD`

## Queued 2026-09-26 by skills/skill-library-engineering

Every paper below is cited by one of the five papers this run read in full,
and none of the twelve is in the `papers` table at all, so the corpus holds
the skill-library cluster's 2026 results without the work they are measured
against. The first six are the load-bearing ones.

- [x] ~~arxiv:2602.12670 — SkillsBench, the source of "an ill-suited skill leaves the task worse off than no skill at all," which is the premise three of the five read papers build on and which alexandria currently asserts on their say-so — asked by skills/skill-library-engineering — 2026-09-26~~ - held and distilled; claims in the corpus, verified 2026-10-05, research seat, PR #210
- [x] ~~arxiv:2603.22455 — SkillRouter, the ~80K-skill routing benchmark and the finding that full skill bodies carry routing signal beyond names and descriptions; it is the baseline in two read papers and the reason the description-versus-body question has an answer — asked by skills/skill-library-engineering — 2026-09-26~~ - held and distilled; claims in the corpus, verified 2026-10-05, research seat, PR #210
- [x] ~~arxiv:2608.04828 — Skill-Use, the 177-task executable benchmark behind the trigger-rate table; the frontier-model numbers this skill quotes are quoted from this paper rather than measured by the paper that reports them — asked by skills/skill-library-engineering — 2026-09-26~~ - held and distilled; claims in the corpus, verified 2026-10-05, research seat, PR #210
- [x] ~~arxiv:2605.23904 — SkillOpt, the optimizing baseline both skill-evolution papers measure against, so every "+4.01 percent over SkillOpt" in the corpus is relative to a method the library has never read — asked by skills/skill-library-engineering — 2026-09-26~~ - held and distilled; claims in the corpus, verified 2026-10-05, research seat, PR #210
- [x] ~~arxiv:2602.12430 — Agent skills for large language models: architecture, acquisition, security, and the path forward; the survey all five read papers cite for what a skill is, and the only one of the twelve that covers skill security — asked by skills/skill-library-engineering — 2026-09-26~~ - held and distilled; claims in the corpus, verified 2026-10-05, research seat, PR #210
- [x] ~~arxiv:2603.25158 — Trace2Skill, distilling trajectory-local lessons into transferable skills; the direct prior for this skill's central claim that skills must be written from recorded runs — asked by skills/skill-library-engineering — 2026-09-26~~ - held and distilled; claims in the corpus, verified 2026-10-05, research seat, PR #210
- [ ] arxiv:2605.05726 — SkillRet, the skill-retrieval benchmark whose training split is what the native router's two projections were trained on — asked by skills/skill-library-engineering — 2026-09-26
- [ ] arxiv:2604.24594 — Skill retrieval augmentation for agentic AI (SRA-Bench), the out-of-domain library where metadata menus collapsed and dense retrievers fell below BM25 — asked by skills/skill-library-engineering — 2026-09-26
- [ ] arxiv:2604.01687 — CoEvoSkills, self-evolving skills via co-evolutionary verification; the code-centric sibling of the GUI evolution loop, and the nearest thing in this literature to alexandria's own review-panel design — asked by skills/skill-library-engineering — 2026-09-26
- [ ] arxiv:2606.03056 — SkillDAG, self-evolving typed skill graphs for skill selection at scale; tests whether the graph representation that helps execution also helps selection — asked by skills/skill-library-engineering — 2026-09-26
- [ ] arxiv:2607.25853 — HiSkill, hierarchical skill graphs; the second structured-representation line, needed before the library commits to a file shape — asked by skills/skill-library-engineering — 2026-09-26
- [ ] arxiv:2603.02766 — EvoSkill, automated skill discovery for multi-agent systems; the discovery half of the problem, which none of the five read papers covers — asked by skills/skill-library-engineering — 2026-09-26

Questions the reading raised, for the research seat rather than a single paper.

- [ ] Does the trigger-rate collapse reproduce on alexandria's own skills? A live harness loaded the correct skill on 1.1 percent of 177 tasks under progressive disclosure with a 32B backbone, against 90.9 percent with a native router. Our trigger test is a lexical stand-in for the retrieval half only, so it cannot see this failure mode at all — asked by skills/skill-library-engineering — 2026-09-26
- [ ] Is anything in the corpus measuring skills at the size a paying library actually ships, between five and fifty? Every read paper works at either one skill per benchmark or tens of thousands from a public registry, and alexandria sits in the untested middle — asked by skills/skill-library-engineering — 2026-09-26
- [ ] Nothing in this cluster measures a skill whose content is research findings rather than a task procedure. The evidence for grounding a skill in recorded runs does not obviously transfer to a skill whose grounding is a paper, and that gap sits directly under the product's differentiator — asked by skills/skill-library-engineering — 2026-09-26


## Queued 2026-09-29 by skills/context-window-engineering

Same shape as the 2026-09-26 batch, second run running. Every arXiv id below
is cited by one of the papers this run read in full, and not one of them is in
the `papers` table, so the corpus again holds a cluster's 2026 results without
the work those results are measured against. The first five are load-bearing:
two of them are the independent check on this skill's central finding, and the
library currently cannot run that check.

- [ ] arxiv:2605.18053 — Protection is (nearly) all you need, which finds that structural protection dominates scoring for long-context question answering under a global cache cap; Random Attention says its own decode-phase result agrees with this one, and the library has read neither the agreement nor this paper — asked by skills/context-window-engineering — 2026-09-29
- [ ] arxiv:2512.12008 — Hold onto that thought, the evaluation that reported random and recency baselines falling far behind scored selection on reasoning; Random Attention's explanation is that those random baselines lost the prompt, so this is the paper the skill's central claim is arguing with and the one it never read — asked by skills/context-window-engineering — 2026-09-29
- [ ] arxiv:2608.26070 — Prefix Sliding, concurrent work that keeps the prompt plus a recency window, which is the nearest signal-free alternative to the policy this skill recommends and the one comparison Random Attention ran only in diagnostic settings — asked by skills/context-window-engineering — 2026-09-29
- [ ] arxiv:2604.17935 — How much cache does reasoning need, on depth-cache tradeoffs in compressed transformers; this skill can say what to protect and cannot say how large a budget should be, and this is the paper that addresses the gap — asked by skills/context-window-engineering — 2026-09-29
- [ ] arxiv:2605.09490 — Not all thoughts need HBM, a semantics-aware memory hierarchy for reasoning; the tiering evidence this skill cites is two video systems, so the section's honest caveat is that no text-agent tiering result was read, and this is it — asked by skills/context-window-engineering — 2026-09-29
- [ ] arxiv:2603.01229 — RMBench, the memory-dependent manipulation benchmark underneath the contradiction this skill resolves; both sides of that comparison are read and the benchmark defining the task split is not — asked by skills/context-window-engineering — 2026-09-29
- [ ] arxiv:2606.29563 — Coverage-driven KV cache eviction, a selection rule built on coverage rather than importance scoring, which is the one family the null policy does not obviously subsume — asked by skills/context-window-engineering — 2026-09-29
- [ ] arxiv:2605.09649 — Make each token count, on improving long-context performance through the cache; cited by Random Attention as prior work in the regime this skill explicitly excludes, so it is the boundary case — asked by skills/context-window-engineering — 2026-09-29
- [ ] arxiv:2602.10560 — When to memorize and when to stop, gated recurrent memory with early exit; one of the two sequential-memory baselines PARSER beats, and the more recent of them — asked by skills/context-window-engineering — 2026-09-29
- [ ] arxiv:2404.06654 — RULER, the long-context benchmark PARSER reports ten additional tasks on in its appendix; the skill cites the multi-hop QA result and cannot say what happens on the non-QA half — asked by skills/context-window-engineering — 2026-09-29
- [ ] arxiv:2506.16411 — When does divide and conquer work for long context LLMs, a noise decomposition framework; the skill recommends chunked parallel reading and this is the paper that says when chunking fails — asked by skills/context-window-engineering — 2026-09-29
- [ ] arxiv:2505.20625 — Long context scaling through multi-agent question-driven collaboration, the untrained predecessor of PARSER's lead-agent design, needed to separate the architecture's contribution from the reinforcement learning's — asked by skills/context-window-engineering — 2026-09-29
- [ ] arxiv:2605.15184 — Is grep all you need, on how agent harnesses reshape agentic search; PARSER runs shell-tool subagents as a drop-in variant, and this skill's suggestion that subagents return a checkable span leans on that line of work — asked by skills/context-window-engineering — 2026-09-29
- [ ] arxiv:2605.29307 — GrepSeek, training search agents for direct corpus interaction, the trained half of the same question — asked by skills/context-window-engineering — 2026-09-29
- [ ] arxiv:2603.09835 — Chow-Liu ordering for long-context reasoning in chain-of-agents, on whether the order chunks are visited can be chosen rather than inherited, which is the assumption PARSER removes by reading all chunks every round — asked by skills/context-window-engineering — 2026-09-29

Four works this cluster depends on carry no arXiv id in the reference lists
that cite them, so they need a different route into the corpus than the
distill path. Recorded here rather than dropped.

- [ ] no arXiv id — MemAgent (Yu et al., ICLR 2026), the sequential-memory agent PARSER's whole argument is against, cited as a conference paper with an external link only — asked by skills/context-window-engineering — 2026-09-29
- [ ] no arXiv id — ReMemR1 (Shi et al., 2026), the callback-module follow-up to MemAgent and the second baseline in every PARSER table — asked by skills/context-window-engineering — 2026-09-29
- [ ] no arXiv id — Context rot: how increasing input tokens impacts LLM performance (Hong et al., 2025), a Chroma technical report; it is the named source for the premise that accuracy degrades before the window is full, which this skill states in its description — asked by skills/context-window-engineering — 2026-09-29
- [ ] no arXiv id — Lost in the middle (Liu et al., TACL 2024), the positional-bias result the buried-evidence activation condition rests on — asked by skills/context-window-engineering — 2026-09-29

Questions the reading raised, for the research seat.

- [ ] question — How often do real agent traces contain a fact stated once and needed more than a budget later? Random Attention names this as the case a signal-free policy loses, says plainly that it never measured the frequency, and calls an agent reading state once and consulting it later the workload where its own method is the wrong default. That frequency decides whether this skill's central recommendation applies to agents at all — asked by skills/context-window-engineering — 2026-09-29
- [ ] question — Does the protect-the-input finding survive on architectures without per-head independence, such as multi-head latent attention or multi-query attention? Random Attention tested four models that all use grouped-query attention and says the transfer is an inference rather than a measurement — asked by skills/context-window-engineering — 2026-09-29
- [ ] question — Is there a text-agent equivalent of the shallow-layer index, where a cheap partial forward pass builds the retrieval structure and the full model only runs at answer time? ShallowStream shows it for video and the corpus holds no text result either way — asked by skills/context-window-engineering — 2026-09-29


## Queued 2026-09-30 by the skill seat, from the eval run (ADR-36)

This batch is a different shape from the two above it. Those queued the
papers a new skill needed. This run wrote no new skill; it wrote the eval
task sets for the six skills already on main, and what the reading turned up
is that the benchmarks the skills' headline numbers are measured on are
largely absent from the corpus. Every eval task is the situation a paper
studied, so a missing benchmark is now missing from the product twice: once
from the claim and once from the task that tests it.

Every id below was read out of a reference list in this run rather than
recalled, per L-A12. Where the citing paper gives no arXiv id, the line says
so instead of guessing one.

- [ ] arxiv:2607.08938 — Better harnesses, smaller models, Yang et al. 2026, the seven-task enterprise agentic suite and the six-category adaptation-failure ontology. This is the load-bearing gap in the library: harness-engineering's two flagship numbers, the harness-alone gain and the 4-to-30-point imitation regression, are both measured on this suite, and the failure ontology is what the source paper uses to explain the regression as a planning-fit loss. Read before anything else here — asked by skills/harness-engineering — 2026-09-30
- [ ] arxiv:2507.19457 — GEPA, reflective prompt evolution, the harness search actually used to produce the evolved harnesses in that result, so "evolving the harness alone" names a specific method the corpus has never read — asked by skills/harness-engineering — 2026-09-30
- [ ] arxiv:2509.16941 — SWE-bench Pro, Deng et al. 2025, the 731-instance benchmark whose re-audit the library has read. evaluation-integrity's defect profile, 75 narrow tests against 22 misleading descriptions, is a statement about this dataset, and the four shortcut channels are properties of its environment — asked by skills/evaluation-integrity — 2026-09-30
- [ ] arxiv:2406.12045 — Tau-bench, Yao et al. 2024, the out-of-domain benchmark DRACO generalises to without a verifier; the generalisation claim in self-improving-post-training-loops rests on a benchmark the corpus does not hold — asked by skills/self-improving-post-training-loops — 2026-09-30
- [ ] arxiv:2404.07972 — OSWorld, Xie et al. 2024, the environment behind the recursion ablation recursive-harness-self-improvement quotes, 71.97 to 78.98 partial and 37.80 to 42.68 binary — asked by skills/recursive-harness-self-improvement — 2026-09-30
- [ ] no arXiv id — AppWorld, Trivedi et al., ACL 2024, cited without an id by the paper that reports a 15.9-point gain on it. The largest single number in self-improving-post-training-loops is measured here — asked by skills/self-improving-post-training-loops — 2026-09-30
- [ ] no arXiv id in the citing paper — SciWorld and BFCL-V3, the two benchmarks the feedback-enrichment result is measured on, cited by arxiv:2609.08404 without ids in its visible reference list. Needed because harness-engineering states feedback consistency as a hard boundary and that is where it was measured — asked by skills/harness-engineering — 2026-09-30

Questions the reading raised, for the research seat.

- [ ] question — Claim 289 is a misreading, and the question is how many others are. It says arxiv.org/abs/2609.09219 observed "30 truthful recoveries and zero neutral recoveries" establishing "a statistically significant positive feedback effect". The paper reports 9 of 30 and 16 of 30 truthful against 0 of 30 neutral, and records both Evidence decisions as Inconclusive. The row merged two numbers and inverted the verdict. It then contradicted the accurate claim 288 at 0.75 confidence, which put a true claim into deprecated_claims. The general defect: interpret has no way to tell two registered experiments inside one paper apart when the paper reuses a word for both, and a same-paper contradicts edge is exactly the signature. Worth a corpus-wide pass over same-paper contradicts edges — asked by skills/evaluation-integrity — 2026-09-30
- [ ] question — Is a with-versus-without eval written by the seat that wrote the skill measuring the skill, or the author's model of the skill? The tasks in this run were written from the papers, but by the same seat, in the same week, with the skill text in context. evaluation-integrity's own first section says a generated instrument is an attack surface and that the honest test needs an oracle independent of the rubric. This library now has 66 tasks with no such independence. The cheapest available check is whether the unaided arm behaves as each task's `without_skill` field predicts, which was written before any run — asked by the skill seat, for all six skills — 2026-09-30
- [ ] question — Does any published work measure with-versus-without for a skill whose content is research findings rather than a task procedure? The 2026-09-26 batch queued this once for skills/skill-library-engineering. Re-raised because it is now the premise of the whole eval programme rather than one skill's caveat, and every measurement the library cites is on task-procedure skills — asked by the skill seat — 2026-09-30
- [ ] question — arxiv:2609.07103, Revisiting Complete Reasoning Traces for Post-Training, publishes no full HTML and was read at the abstract only, for the second run running. It is one of the two independent lines behind context-window-engineering's claim that the middle of a trace is droppable. Either get the PDF into the corpus or mark the convergence in that skill as resting on one paper — asked by skills/context-window-engineering — 2026-09-30


## Queued 2026-09-30 by skills/agent-containment and skills/agent-security-measurement

Two skills, ten papers read in full, and the first thing the reading found is
about the pipeline rather than the literature. **Five of the ten were routed to
`distill` or `deep_read` by triage and never distilled. Three were never
triaged at all, and they include the three strongest containment papers in the
corpus. Every claim that does exist from the other four was written with
`fulltext_chars` null, which means from the abstract.** So the containment
thread is not empty because the papers are missing or because the rubric
rejected them. They are here, routed correctly, unread.

| paper | triage decision | distilled | claims |
|---|---|---|---|
| arxiv:2609.29808 Hard Stop | deep_read | never | 0 |
| arxiv:2609.22978 DSec | distill | never | 0 |
| arxiv:2609.26761 A2M | distill | never | 0 |
| arxiv:2609.29647 AgentKernel | distill | never | 0 |
| arxiv:2609.06500 capmas | never triaged | never | 0 |
| arxiv:2609.35366 Planarian | never triaged | never | 0 |
| arxiv:2609.35557 The Compiler May Read It | never triaged | never | 0 |
| arxiv:2609.05903 EvoSafeHarness | distill | 2026-09-14 | 5, abstract-only |
| arxiv:2609.06966 Mole | distill | 2026-09-10 | 5, abstract-only |
| arxiv:2609.28274 Shutdown Sabotage | distill | 2026-09-25 | 5, abstract-only |

Every arXiv id below was read out of a reference list or a corpus row during
this run rather than recalled, per L-A12. The first four are load-bearing: they
are the baselines the two new skills' headline numbers are measured against,
and not one of them is in the `papers` table.

- [ ] arxiv:2503.18813 — Defeating Prompt Injections by Design (CaMeL), the capability-based defence that both new skills are positioned against: "82.8 percent utility at 0.0 percent attack success, twice the utility of CaMeL at the same operating point" is the strongest number in agent-security-measurement, and CapScope defines itself by the contrast. The library has never read the thing it is twice as good as — asked by skills/agent-security-measurement — 2026-09-30
- [ ] arxiv:2505.23643 — Securing AI Agents with Information-Flow Control (Fides), the defence agent-security-measurement recommends in section 4. What the library has read is one attack paper's reimplementation of it, described in that paper's own words as "FIDES-style" precisely because it is not the original — asked by skills/agent-security-measurement — 2026-09-30
- [ ] arxiv:2609.08371 — Authority Is Not a String, the capability-scoped harness paper. Read in full by this run and absent from the `papers` table entirely, because it is cs.SE, which is the category gap the 2026-09-30 research census measured. Two of agent-containment's seven sections rest on it and it carries no claim ids as a result — asked by skills/agent-containment — 2026-09-30
- [ ] arxiv:2509.22040 — "Your AI, My Shell": prompt injection on agentic coding editors, the source of the 84 percent attack success in production editors that the capability-scoping literature opens with. It is the premise sentence of this whole territory and the corpus does not hold it — asked by skills/agent-containment — 2026-09-30
- [ ] arxiv:2609.29647 — AgentKernel, a trust-native agent operating system, fetched in full by this run and not read within the run's budget. It is the fourth independent argument that governance sharing the agent's process trust boundary is not a boundary, and confirming or breaking that convergence is worth one read — asked by skills/agent-containment — 2026-09-30
- [ ] arxiv:2510.05244 — Indirect Prompt Injections: Are Firewalls All You Need, or Stronger Benchmarks? The nearest rival to agent-security-measurement's section 4, since it reports that simple firewalls solve many cases in several benchmarks. If that holds, the section's ordering is wrong and the skill needs revising — asked by skills/agent-security-measurement — 2026-09-30
- [ ] arxiv:2504.11703 — Progent, privilege control for AI agents, one of the three fixed expert defences the searched harness beats. A "beats the fixed baselines" claim is only as good as the baselines — asked by skills/agent-security-measurement — 2026-09-30
- [ ] arxiv:2412.14470 — Agent-SafetyBench, where the "mean attack success below 20 percent under adaptive attacks" result is measured — asked by skills/agent-security-measurement — 2026-09-30
- [ ] arxiv:2508.01780 — LiveMCPBench, the benchmark every tool-hijacking number in agent-security-measurement sits on, including the perplexity table this skill leans on hardest — asked by skills/agent-security-measurement — 2026-09-30
- [ ] arxiv:2604.13630 — SafeHarness, lifecycle-integrated security architecture for agent deployment, the closest published relative of the harness-level enforcement both new skills recommend — asked by skills/agent-containment — 2026-09-30
- [ ] arxiv:2601.04688 — ToolGate, contract-grounded and verified tool execution, the contract-based alternative to capability scoping that neither new skill can currently compare against — asked by skills/agent-containment — 2026-09-30
- [ ] arxiv:2412.04984 — Frontier Models are Capable of In-context Scheming, the prior that the shutdown-sabotage study extends by removing the incentive. Needed to say whether the no-incentive result is new or a replication — asked by skills/agent-security-measurement — 2026-09-30
- [x] ~~arxiv:2609.16204 — Decoy Direction Optimization, a post-hoc weight-editing defence against abliteration, already in the corpus with five claims. Deliberately left out of agent-security-measurement because it defends a model release rather than an agent deployment. It is the seed of a different skill and should not sit unused — asked by skills/agent-security-measurement — 2026-09-30~~ - held and distilled; claims in the corpus, verified 2026-10-05, research seat, PR #210
- [ ] no arXiv id — Anatomy of a Frontier Lab Agent Intrusion, Hugging Face Security Team, 2026, and the METR independent investigation of the same incident. These are the external ground truth for the July 2026 escape that agent-containment's section 6 narrates, and the library has read only a single-author monograph's retelling of them — asked by skills/agent-containment — 2026-09-30
- [ ] no arXiv id — Firecracker (Agache et al., NSDI 2020) and EROFS (Gao et al. 2019), the two systems the production sandbox platform's boundary and image path are built from. Not urgent for a skill, but the corpus holds no systems substrate at all for this thread — asked by skills/agent-containment — 2026-09-30

Questions the reading raised, for the research seat and the engineer.

- [ ] question — `deep_read` is a live triage decision with no consumer. Hard Stop, the one paper in this cluster that reconstructs a real production escape, was routed `deep_read` and never read by anything. Either something drains that queue or the decision is a label the pipeline cannot act on, which is the same shape as the 96 `index` rows that were really a backfill rule — asked by skills/agent-containment — 2026-09-30
- [ ] question — Is distill throughput now the binding constraint rather than triage throughput? The 2026-09-30 research census measured triage reading 3 to 15 percent of intake. This run found four papers routed to distill weeks ago and still undistilled, and zero of the ten papers it read carrying a non-null `fulltext_chars`. Both constraints are real and the ordering between them decides which one the engineer fixes first — asked by the skill seat — 2026-09-30
- [ ] question — The corpus has no claim for any of the six containment papers, so skills/agent-containment ships with `provenance.claims: []`. Under ADR-36 that fails the automatic provenance gate, correctly, because the gate cannot tell an empty list that is honest from one that is lazy. Either the gate learns to accept a papers-only provenance block written under ADR-35, or ADR-35 and ADR-36 disagree on what a skill may be built from — asked by skills/agent-containment — 2026-09-30
- [ ] question — Six of fifteen searched safety harnesses in EvoSafeHarness (arXiv 2609.05903, already distilled) dropped their natural-language policy entirely and kept only deterministic runtime relations, and four made no model call at runtime. Our product ships natural-language procedure. That result does not say prose is worthless, it says prose is where a hypothesis is formed and not where enforcement should live. Worth asking whether some of what the library will want to sell in this territory is a policy artifact rather than a SKILL.md — asked by the skill seat — 2026-09-30
- [ ] question — Nothing in either cluster measures the cost of a containment control end to end in a real deployment except one paper's 145 to 316 second mean, and that figure is dominated by a fully autonomous loop retrying refused actions with no human approval path. A number for the same control with an approval path is the single most useful missing measurement for anyone deciding whether to adopt this — asked by skills/agent-containment — 2026-09-30
- [ ] question — Is there a published scoring function for skill or tool routing that is provably invariant to candidate description length? This run measured both of our engines and neither is: lexical/2.1 pays a candidate +0.1353 for tripling its description, lexical/3 fines it -0.1227 for the same change, and the two biases are close enough in size that they cancel at a length-matched decoy panel. The retrieval literature has known length-normalisation problems since BM25's `b` parameter, and we are rediscovering them by hand. A single reference that states the invariance property and its cost would be worth more than another engine version — asked by the skill seat for skills/_validation — 2026-09-30
- [ ] question — What is the right null model size for a router benchmark, and does anyone publish one? Our decoy panel is eight candidates against eight skills. This run showed the panel's word length decides negative cases, so the panel is an instrument with its own parameters, and we have no external calibration for any of them: how many decoys, how close to the library's domains, how long. Every negative-case number the library reports rests on choices this seat made by eye — asked by the skill seat for skills/_validation — 2026-09-30
- [ ] question — 57 trigger cases give a 95 percent interval of roughly [0.72, 0.93] at 48 passes, which is too wide to detect the two-case difference between our engines. How many cases would the suite need before an engine change is decidable at all? Worth knowing before anyone writes lexical/4, because the answer may be that the suite cannot judge it and the honest gate is the invariance unit test rather than the pass rate — asked by the skill seat for skills/_validation — 2026-09-30

<!-- skill seat, run opened 2026-10-05 (window, synchronous). Additions below. -->
- [x] ~~arxiv:2603.25158 — Trace2Skill, distilling trajectory-local lessons into transferable skills; the direct prior for this skill's central claim that skills must be written from recorded runs — asked by skills/skill-library-engineering — 2026-09-26~~ — read from the arXiv abstract 2026-09-30, research seat, PR #138
- [x] ~~arxiv:2604.01687 — CoEvoSkills, self-evolving skills via co-evolutionary verification; the code-centric sibling of the GUI evolution loop, and the nearest thing in this literature to alexandria's own review-panel design — asked by skills/skill-library-engineering — 2026-09-26~~ — read from the arXiv abstract 2026-09-30, research seat, PR #138
- [x] ~~arxiv:2606.03056 — SkillDAG, self-evolving typed skill graphs for skill selection at scale; tests whether the graph representation that helps execution also helps selection — asked by skills/skill-library-engineering — 2026-09-26~~ — read from the arXiv abstract 2026-09-30, research seat, PR #138
- [x] ~~arxiv:2603.02766 — EvoSkill, automated skill discovery for multi-agent systems; the discovery half of the problem, which none of the five read papers covers — asked by skills/skill-library-engineering — 2026-09-26~~ — read from the arXiv abstract 2026-09-30, research seat, PR #138
## Drain record, 2026-09-30 (research seat, PR #138)
**The blocker first, because it governs the rest.** All 27 arXiv ids in this
file are still absent from `papers`. Each one resolves against the live arXiv
API, so none is a bad id. ADR-35 and the registers table both record that
`pipeline/distill.py` has parsed the unchecked lines and ingested what the
corpus lacks on every daily run since 2026-09-27. Measured tonight it has
ingested none of them, which agrees with the finding that the distill image is
not current (`docs/research/briefs/2026-09-30.md` section 4, and the deploy
entry filed in `docs/ideas.md`). Until that deploy lands, this queue cannot be
drained through the corpus by any seat.
**Struck: four, and on an abstract rather than a full read.** The four bearing
directly on the 2026-09-29 directive on self-improving systems were read from
their arXiv abstracts and are written up as a cluster in the brief's section 8:
`2604.01687` CoEvoSkills, `2606.03056` SkillDAG, `2603.02766` EvoSkill,
`2603.25158` Trace2Skill. The strike notes say "from the arXiv abstract" and
mean it. All four remain worth a full read when they are ingested, and the
brief's recommendation to the skill seat is explicitly **not** to build a skill
on this cluster yet, because a skill resting on four abstracts is the padded
skill the charter forbids.
**Not struck: 23 ids, 4 no-id works, and 6 questions.** Reading 23 papers in
full was not compatible with this dispatch's four deliverables, and striking a
line without reading it is worse than leaving it standing. Named here rather
than left as a silent omission.
**Two questions answered without a strike.** The skill seat asked whether
anything in the corpus measures self-evolving skill libraries, and whether
anything measures a library at the size a paying product ships. On the first:
no. The four papers that do are the four above and none is in `papers`, so the
corpus holds nothing on the product's own territory. On the second: the census
found nothing between five and fifty skills either, which leaves the seat's
original reading of that gap intact rather than resolved.
## Drain record addendum, 2026-09-30 (research seat, PR #145)
Second dispatch the same night, on protocols, containment and security. The
blocker recorded above is unchanged and was re-measured rather than assumed:
**all 27 arXiv ids in this file are still absent from `papers`.** No further
strikes, because striking a line without reading it is worse than leaving it.
**One open question is answered, from outside the corpus.** The
`skills/skill-library-engineering` batch queued `arxiv:2607.25853` (HiSkill,
hierarchical skill graphs) with the reason "the second structured-representation
line, needed before the library commits to a file shape", and the same batch's
third standing question asks what a skill's file shape should be when its
content is research findings rather than a task procedure.
The file-shape half of that question now has an external answer that no paper in
this queue will give. **SEP-2640 "Skills Extension" (status Final, created
2026-04-23)** standardizes serving Agent Skills over MCP and delegates the
format - directory structure, YAML frontmatter, naming, progressive disclosure -
entirely to the **Agent Skills specification** at `agentskills.io/specification`.
Checked against this repository: `skills/*/SKILL.md` already carries YAML
frontmatter with `name` and `description`, that specification's stated minimum,
so the library is already shaped to be servable under SEP-2640 without a format
change. The library does not need to choose a file shape from the research
literature; there is a standard, it is Final, and we already broadly conform.
What the research literature is still needed for is the part the standard does
not cover: whether a hierarchical or graph representation helps *selection*, which
is what HiSkill and SkillDAG measure and what no standard will answer. That line
stays queued and unstruck. Full working in
`docs/research/notes/2026-09-30-protocols-containment-security-census.md`
section 6c.
- [ ] arxiv:2610.02015 — RLVR: On Language Drift during RLVR Post-Training — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.40115 — RLVR: Unlearnable, or Unmeasured? On the Reliability of Difficulty Labels in RLVR — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.40360 — RLVR: Semifactual Credit-Augmented Policy Optimization — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.39533 — RLVR: CATCH: A Controllable Analysis Testbed for Reward Hacking in Coding RL — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.37825 — RLVR: Privy to the Foil: a self-privileged critic for RLVR — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.37868 — RLVR: Learning Beyond What You Sample: cross-model trajectory exchange for RLVR — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.35259 — RLVR: On-Policy or Off-Policy Learning? distillation dynamics — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.35677 — RLVR: Verifier Errors in RLVR: Reward Hacking, Limits of Feedback, and Selective Control — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.34857 — RLVR: Beyond Verbalized Confidence: Calibrating Reasoners with Differentiable Readouts — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.28765 — RLVR: Reinforcement Learning with Verifiable Rewards for Small Search Agents — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.28385 — RLVR: When and Where to Trust the Teacher: on-policy distillation and GRPO through entropy — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.24380 — RLVR: Information-Time Proximal Policy Optimization — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.23053 — RLVR: Attributable Post-Rationalization in RAG Citations: an RLVR fix — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.16639 — RLVR: ReDraft, Don't Just Distill: reference-driven revision for continual post-training — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.15987 — RLVR: Bellman Policy Optimization — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.12191 — RLVR: GAUGE: When Not to Trust LLM-as-a-Judge in user-simulated evaluation — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.10315 — RLVR: TRACE: Training Reasoning Agents for Causal Exploration with Synthesized Rewards — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.08650 — RLVR: Difficulty-Adaptive Tree-Structured Policy Optimization — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.09075 — RLVR: ThinkPrior: Zero-Rollout Difficulty Priors for Cold-Start Prompt Selection in RLVR — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.06107 — RLVR: DataFlex-RL: An Evaluation Platform for RLVR Data Policies — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.05111 — RLVR: Unifying ICL, SFT, KL-Regularized RL Through a Bayesian Lens — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.05295 — RLVR: RISE: Recursive Improvement via Self-Extrapolating Policy Distillation — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.04565 — RLVR: Extremely Sparse Supervision Incentivizes Reasoning Ability — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.04108 — RLVR: Sequential Beats Joint: On-Policy Distillation and RLVR — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2609.00444 — RLVR: Group Adaptive Clipping Policy Optimization — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2608.29188 — RLVR: Locked at the Entrance, Open Inside: Where RLVR Narrows the Solution Space — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2608.27046 — RLVR: Performance Foundations of Parallel and Distributed Reasoning Language Models — asked by the chair (owner: make sure the corpus includes RLVR) — 2026-10-05
- [ ] arxiv:2211.14275 — gap: process versus outcome rewards over long horizons: Uesato et al., process- and outcome-based feedback for math word problems (the original comparison) — asked by the chair (owner: fix the gaps) — 2026-10-05
- [ ] arxiv:2305.20050 — gap: process versus outcome rewards over long horizons: Lightman et al., Let's Verify Step by Step (PRM800K, process supervision beats outcome) — asked by the chair (owner: fix the gaps) — 2026-10-05
- [ ] arxiv:2312.08935 — gap: process versus outcome rewards over long horizons: Math-Shepherd, automatic process supervision without human labels — asked by the chair (owner: fix the gaps) — 2026-10-05
- [ ] arxiv:2406.06592 — gap: process versus outcome rewards over long horizons: OmegaPRM, automated process supervision by MCTS — asked by the chair (owner: fix the gaps) — 2026-10-05
- [ ] arxiv:2410.08146 — gap: process versus outcome rewards over long horizons: Setlur et al., Rewarding Progress: scaling automated process verifiers — asked by the chair (owner: fix the gaps) — 2026-10-05
- [ ] arxiv:2412.06559 — gap: process versus outcome rewards over long horizons: ProcessBench, where process reward models fail — asked by the chair (owner: fix the gaps) — 2026-10-05
- [ ] arxiv:2501.07301 — gap: process versus outcome rewards over long horizons: Qwen, the lessons of developing process reward models in mathematical reasoning — asked by the chair (owner: fix the gaps) — 2026-10-05
- [ ] arxiv:2502.01456 — gap: process versus outcome rewards over long horizons: PRIME, process reinforcement through implicit rewards — asked by the chair (owner: fix the gaps) — 2026-10-05
- [ ] arxiv:2502.10325 — gap: process versus outcome rewards over long horizons: Process reward models for LLM agents, framework and directions (long-horizon credit) — asked by the chair (owner: fix the gaps) — 2026-10-05
- [ ] arxiv:2505.10978 — gap: process versus outcome rewards over long horizons: GiGPO, group-in-group policy optimization for long-horizon agent credit assignment — asked by the chair (owner: fix the gaps) — 2026-10-05
- [ ] arxiv:2504.20073 — gap: process versus outcome rewards over long horizons: RAGEN, training agents by multi-turn RL and where it collapses — asked by the chair (owner: fix the gaps) — 2026-10-05
- [ ] arxiv:2203.02155 — gap: preference optimization from usage data: InstructGPT, RLHF from human preference comparisons (the reference pipeline) — asked by the chair (owner: fix the gaps) — 2026-10-05
- [ ] arxiv:2305.18290 — gap: preference optimization from usage data: DPO, direct preference optimization without a reward model — asked by the chair (owner: fix the gaps) — 2026-10-05
- [ ] arxiv:2402.01306 — gap: preference optimization from usage data: KTO, alignment from binary good-or-bad feedback, the shape usage data actually has — asked by the chair (owner: fix the gaps) — 2026-10-05
- [ ] arxiv:2401.10020 — gap: preference optimization from usage data: Self-rewarding language models, the model judging its own preferences — asked by the chair (owner: fix the gaps) — 2026-10-05
- [ ] arxiv:2404.19733 — gap: preference optimization from usage data: Iterative reasoning preference optimization, online preference loops — asked by the chair (owner: fix the gaps) — 2026-10-05
- [ ] arxiv:2404.03715 — gap: preference optimization from usage data: Direct Nash optimization, general preferences beyond reward models — asked by the chair (owner: fix the gaps) — 2026-10-05
- [ ] arxiv:2403.04132 — gap: preference optimization from usage data: Chatbot Arena, preference data from live usage at scale — asked by the chair (owner: fix the gaps) — 2026-10-05
- [ ] arxiv:2411.15124 — gap: preference optimization from usage data: Tulu 3, the open post-training recipe where RLVR was named — asked by the chair (owner: fix the gaps) — 2026-10-05
- [ ] arxiv:2407.21783 — gap: preference optimization from usage data: The Llama 3 herd of models, the preference-data pipeline in production — asked by the chair (owner: fix the gaps) — 2026-10-05

## Containment batch, 2026-10-05 (research seat, PR #210)

Owner directive 2026-10-05, containment only. Appended so distill reads these
first. Two groups: the papers the containment skill rests on, and the papers
the 30-day census found in the field and not in our corpus.

### Group 1 — the papers `skills/agent-containment` rests on

The directive names four. The draft's front matter names **six**, and the two
it does not name carry load in the skill's body (the five-week deny-list
revision count, and the statepoint mechanism). All six are listed. Their state
was measured tonight, and it corrects the directive on two points: five of the
six **are** in `papers`, and one of them has already yielded claims.

- `arxiv:2609.08371` **Authority Is Not a String: A Capability-Scoped Harness for
  Prompt-Injection-Resistant Coding Agents** — arxiv.org/abs/2609.08371 —
  **ABSENT from `papers` entirely.** Ingest first. This is the load-bearing
  paper of the skill: every factorial number in skill sections 1 and 2 (46/75,
  47/75, 33/75, 3/75) comes from it, and the corpus cannot check one of them.
- `arxiv:2609.06500v1` **CAPMAS: Capability-Based Delegation of Privileges in
  Multi-Agent Systems** — arxiv.org/abs/2609.06500 — held, **never triaged**.
  Needs a triage decision before it can reach distill.
- `arxiv:2609.22978v1` **DeepSeek Elastic Compute (DSec): A Sandbox
  Infrastructure for Effective Agentic Training at Scale** —
  arxiv.org/abs/2609.22978 — held, routed to `distill`, **no fulltext, 0
  claims**. In the distill backlog.
- `arxiv:2609.35557v1` **The Compiler May Read It, the Agent May Not** —
  arxiv.org/abs/2609.35557 — held, routed to `distill`, 0 claims. In the backlog.
- `arxiv:2609.35366v1` **Planarian: Managing Agent State with Statepoints** —
  arxiv.org/abs/2609.35366 — held, routed to `distill`, 0 claims. In the backlog.
- `arxiv:2609.29808v1` **Hard Stop: Kernel-Level Preemption and Containment for
  Rogue Agentic Execution** — arxiv.org/abs/2609.29808 — held, `deep_read`,
  12,000 fulltext chars, **5 claims already filed (882-886)**. Not a reading
  gap. It is a *provenance* gap: the skill says `claims: []` while five claims
  from its own paper sit in the corpus. Claim 883 also carries the wrong
  evidence grade (see the brief's graph-error section). Routed to the skill seat
  rather than queued for reading.

### Group 2 — missed by the census (40 papers, external ground truth)

Method and full tables in
`docs/research/notes/2026-10-05-containment-census.md`. OpenAlex, arXiv-scoped,
2026-09-05 to 2026-10-05, the owner's five named containment areas; 301 arXiv
papers in the field, 125 held, 176 not held, of which these 40 are on-thread by
this seat's judgment and 136 are relevance-search noise. Every id below was
returned by the external query and checked against `papers`; none is inferred.

**Tier A - the boundary itself (read first)**

- `arxiv:2609.08062` (2026-09-08) ResidualAuth: What Authorization State Must Language Agents Preserve under Revocable Delegation? — arxiv.org/abs/2609.08062
- `arxiv:2609.11596` (2026-09-10) From Intent to Execution Grant: An Execution-Boundary Conformance Profile for High-Risk AI Actions — arxiv.org/abs/2609.11596
- `arxiv:2609.12001` (2026-09-10) Scan the Skill, Govern the Action: Composing Registry Verdicts with Runtime Consequence Control — arxiv.org/abs/2609.12001
- `arxiv:2609.14003` (2026-09-12) Confuse the Model, Control the Flow: Understanding and Mitigating Privacy Leakage from LLM Agents with Information Flow Control — arxiv.org/abs/2609.14003
- `arxiv:2609.13672` (2026-09-12) Recoverability as a System Primitive for Long-Horizon AI Agents — arxiv.org/abs/2609.13672
- `arxiv:2609.14780` (2026-09-13) The Stochastic Deputy: Structural Tenant Isolation for Tool-Using LLM Agents — arxiv.org/abs/2609.14780
- `arxiv:2609.14631` (2026-09-13) LLM Agent Capabilities Should Follow Task Intent and Context Source — arxiv.org/abs/2609.14631
- `arxiv:2609.15906` (2026-09-14) Authorization Architectures for Tool-Using AI Agents — arxiv.org/abs/2609.15906
- `arxiv:2609.14987` (2026-09-14) ActGuard: Pre-execution Action Auditing against Indirect Prompt Injection in LLM Agents — arxiv.org/abs/2609.14987
- `arxiv:2609.17648` (2026-09-15) Trust propagation and structural containment in Multi-agent LLM pipelines — arxiv.org/abs/2609.17648
- `arxiv:2609.21088` (2026-09-17) Origin Is All You Need: Provenance-Aware Transformers for Structural Trust-Boundary Separation — arxiv.org/abs/2609.21088
- `arxiv:2609.22573` (2026-09-18) Zero-Trust Authorization and Discovery for Enterprise MCP — arxiv.org/abs/2609.22573
- `arxiv:2609.22882` (2026-09-19) The Law of Stop: Interruptibility, Injunctions, and the Governance of Agentic AI — arxiv.org/abs/2609.22882
- `arxiv:2609.23498` (2026-09-20) Runtime Authorization Consistency Checking for MCP-based Agentic Workflows — arxiv.org/abs/2609.23498
- `arxiv:2609.24077` (2026-09-21) LeaseGuard: Incumbent-Preserving Admission Control for Privileged LLM Agents — arxiv.org/abs/2609.24077
- `arxiv:2609.32378` (2026-09-26) AuthorityLens: Rethinking LLM-Based Agent Systems Through the Lens of Authority — arxiv.org/abs/2609.32378
- `arxiv:2609.32750` (2026-09-26) CUA-Sandbox: Efficient Environments for Computer-Use Agent Reinforcement Learning — arxiv.org/abs/2609.32750
- `arxiv:2609.32390` (2026-09-26) Reward Hacking and Agent Containment Failure: A Monte Carlo Study Based on the 2026 Hugging Face Incident — arxiv.org/abs/2609.32390
- `arxiv:2609.33658` (2026-09-27) AgentBoundary: Counterfactual Evaluation of Safety in Tool-Using LLM Agents — arxiv.org/abs/2609.33658
- `arxiv:2609.40082` (2026-09-30) Tide: Reclaiming Phased Memory in Agent MicroVMs — arxiv.org/abs/2609.40082

**Tier B - attack side and harness exposure**

- `arxiv:2609.06835` (2026-09-06) Skynet: Workflow-Level Anomaly Detection for Agentic AI via Semantic and Structural Modeling — arxiv.org/abs/2609.06835
- `arxiv:2609.07529` (2026-09-07) CoER: Defending against Adaptive Indirect Prompt Injection via Adversarial Co-Evolution and Refinement — arxiv.org/abs/2609.07529
- `arxiv:2609.06972` (2026-09-07) AgentDrift: A Step-Labeled Benchmark of Injection-Hijacked LLM Agent Trajectories — arxiv.org/abs/2609.06972
- `arxiv:2609.07360` (2026-09-07) Scanning the Harness: Configuration Exposures in AI Coding-Agent Supply Chains — arxiv.org/abs/2609.07360
- `arxiv:2609.10892` (2026-09-09) DriftNet: A Dual-Head Trajectory Transformer for Detecting and Localizing Prompt Injection in LLM Agents — arxiv.org/abs/2609.10892
- `arxiv:2609.10854` (2026-09-09) No-Box Vulnerability Analysis: Description-only Detection of Indirect Prompt Injection Vulnerabilities in MCP Servers — arxiv.org/abs/2609.10854
- `arxiv:2609.10871` (2026-09-09) A2ABreak: Systematic Security Analysis of the A2A Protocol — arxiv.org/abs/2609.10871
- `arxiv:2609.12216` (2026-09-10) Guardrailed Meta-Agent Loops: Stress-Testing Policy Pinning, Budget Bounds, and Crash Recovery — arxiv.org/abs/2609.12216
- `arxiv:2609.13889` (2026-09-12) When Malicious Instructions Persist: Persistent Memory Poisoning Attack on Harness-Based Agents — arxiv.org/abs/2609.13889
- `arxiv:2609.16098` (2026-09-14) Universal Defenses for Tool-Integrated LLM Agents Against Adversarial Attacks — arxiv.org/abs/2609.16098
- `arxiv:2609.15516` (2026-09-14) Misleading the Planner through Deceptive Resumes: Registration-Time Injection in Centralized Multi-Agent Systems — arxiv.org/abs/2609.15516
- `arxiv:2609.18217` (2026-09-16) Measuring and Exploiting Implicit Trust in LLM Tool-Calling Pipelines — arxiv.org/abs/2609.18217
- `arxiv:2609.18411` (2026-09-16) The Verifiable Action Card: Trustworthy Human-in-the-Loop Control for Secure Autonomous Agents — arxiv.org/abs/2609.18411
- `arxiv:2609.22510` (2026-09-18) Defusing Explosive Prompts: Understanding and Preventing Trigger-Based Prompt Injections in LLM Agents — arxiv.org/abs/2609.22510
- `arxiv:2609.30383` (2026-09-24) Stealth Apart, Harm Together: Skill Cascading Attacks on Skill-Based Agent Systems — arxiv.org/abs/2609.30383
- `arxiv:2609.32021` (2026-09-25) SilentCall: Hidden Tool-Call Backdoors in Open-Weight Agents, and How to Catch Them — arxiv.org/abs/2609.32021
- `arxiv:2609.36576` (2026-09-29) Divide and Inject: Can Agents Reconstruct an Indirect Prompt Injection from Fragments? — arxiv.org/abs/2609.36576
- `arxiv:2610.00430` (2026-09-30) Memetic Trojans: Social Contagions as Carriers of Adversarial Payloads in Agent Networks — arxiv.org/abs/2610.00430

**Tier C - surveys, orientation only**

- `arxiv:2609.13731` (2026-09-12) Trustworthy Agentic AI: A Comprehensive Cybersecurity and Systems Survey on Threat Landscapes, Defense Architectures, and Open Challenges — arxiv.org/abs/2609.13731
- `arxiv:2609.22712` (2026-09-19) Trustworthy Agentic AI: Failure Modes, Mitigation Strategies, and a Lifecycle Framework for Autonomous LLM Systems — arxiv.org/abs/2609.22712
**Not struck, and why.** Nothing in this batch is struck. This seat read
titles and abstracts, not full texts, and the directive's four deliverables
were not compatible with 40 full readings. The charter's standing rule holds:
striking a line without reading it is worse than leaving it standing.

**One standing question for whoever reads Tier A.** Three of these papers put
the enforcement point in three different places — the dispatch interceptor
(ActGuard), the authorization-state machine across a delegation chain
(ResidualAuth), and the kernel (held: Agent-Warden, ContractWarden). The skill
currently orders these by "how much privilege the deployment has". Nothing in
the corpus measures them against each other on one workload. If one of these
papers does, that comparison is the skill's missing section.

## Correction to this file's standing blocker, 2026-10-05 (research seat, PR #210)

**The blocker recorded on 2026-09-30 and re-confirmed the same night is false,
and it should stop being planned around.** That record says every arXiv id in
this file is absent from `papers`. Measured tonight against the 56 ids this
file held before this run: **19 distinct papers are held, and 13 of them have
claims in the corpus.** Recorded as
`INC-2026-10-05-absence-asserted-from-an-unnormalised-id-join`.

Seven unchecked lines above are struck accordingly, each one a paper that is
held and distilled. Six more are held with claims but are recorded in tables
or question lines rather than as checkbox items, so they are named here instead
of struck: `arxiv:2609.05903` (EvoSafeHarness, 5 claims), `arxiv:2609.06966`
(MOLE, 5), `arxiv:2609.07103` (Revisiting Complete Reasoning Traces, 4),
`arxiv:2609.08404` (Environments as Scaffold, 5), `arxiv:2609.28274` (Shutdown
Sabotage Propensities, 5), `arxiv:2609.29808` (Hard Stop, 5). The table row
above that records Hard Stop as `0` claims is wrong; it has five, 882-886.

Six are held and genuinely unread, so their lines stand: `arxiv:2609.06500`
(CAPMAS, never triaged), `arxiv:2609.22978` (DSec), `arxiv:2609.26761` (A2M),
`arxiv:2609.29647` (AgentKernel), `arxiv:2609.35366` (Planarian),
`arxiv:2609.35557` (The Compiler May Read It). All but CAPMAS are routed to
`distill` and waiting in a 1,189-paper queue.

**Use this join, not an equality test.** `papers` holds arXiv ids in two
shapes because source `arxiv` writes `arxiv:2610.02206v1` and source
`hf-daily` writes `arxiv:2610.02206`, so an equality join silently misses
every paper that arrived through the `arxiv` feed:

```sql
from f left join papers p on p.id like 'arxiv:' || f.aid || '%'   -- correct
from f left join papers p on p.id = 'arxiv:' || f.aid             -- wrong
```

That is also why the first query of this run reported five of the containment
skill's six papers as missing when five are held.
