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

- [ ] arxiv:2602.12670 — SkillsBench, the source of "an ill-suited skill leaves the task worse off than no skill at all," which is the premise three of the five read papers build on and which alexandria currently asserts on their say-so — asked by skills/skill-library-engineering — 2026-09-26
- [ ] arxiv:2603.22455 — SkillRouter, the ~80K-skill routing benchmark and the finding that full skill bodies carry routing signal beyond names and descriptions; it is the baseline in two read papers and the reason the description-versus-body question has an answer — asked by skills/skill-library-engineering — 2026-09-26
- [ ] arxiv:2608.04828 — Skill-Use, the 177-task executable benchmark behind the trigger-rate table; the frontier-model numbers this skill quotes are quoted from this paper rather than measured by the paper that reports them — asked by skills/skill-library-engineering — 2026-09-26
- [ ] arxiv:2605.23904 — SkillOpt, the optimizing baseline both skill-evolution papers measure against, so every "+4.01 percent over SkillOpt" in the corpus is relative to a method the library has never read — asked by skills/skill-library-engineering — 2026-09-26
- [ ] arxiv:2602.12430 — Agent skills for large language models: architecture, acquisition, security, and the path forward; the survey all five read papers cite for what a skill is, and the only one of the twelve that covers skill security — asked by skills/skill-library-engineering — 2026-09-26
- [x] ~~arxiv:2603.25158 — Trace2Skill, distilling trajectory-local lessons into transferable skills; the direct prior for this skill's central claim that skills must be written from recorded runs — asked by skills/skill-library-engineering — 2026-09-26~~ — read from the arXiv abstract 2026-09-30, research seat, PR #138
- [ ] arxiv:2605.05726 — SkillRet, the skill-retrieval benchmark whose training split is what the native router's two projections were trained on — asked by skills/skill-library-engineering — 2026-09-26
- [ ] arxiv:2604.24594 — Skill retrieval augmentation for agentic AI (SRA-Bench), the out-of-domain library where metadata menus collapsed and dense retrievers fell below BM25 — asked by skills/skill-library-engineering — 2026-09-26
- [x] ~~arxiv:2604.01687 — CoEvoSkills, self-evolving skills via co-evolutionary verification; the code-centric sibling of the GUI evolution loop, and the nearest thing in this literature to alexandria's own review-panel design — asked by skills/skill-library-engineering — 2026-09-26~~ — read from the arXiv abstract 2026-09-30, research seat, PR #138
- [x] ~~arxiv:2606.03056 — SkillDAG, self-evolving typed skill graphs for skill selection at scale; tests whether the graph representation that helps execution also helps selection — asked by skills/skill-library-engineering — 2026-09-26~~ — read from the arXiv abstract 2026-09-30, research seat, PR #138
- [ ] arxiv:2607.25853 — HiSkill, hierarchical skill graphs; the second structured-representation line, needed before the library commits to a file shape — asked by skills/skill-library-engineering — 2026-09-26
- [x] ~~arxiv:2603.02766 — EvoSkill, automated skill discovery for multi-agent systems; the discovery half of the problem, which none of the five read papers covers — asked by skills/skill-library-engineering — 2026-09-26~~ — read from the arXiv abstract 2026-09-30, research seat, PR #138

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
