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
- [ ] arxiv:2603.25158 — Trace2Skill, distilling trajectory-local lessons into transferable skills; the direct prior for this skill's central claim that skills must be written from recorded runs — asked by skills/skill-library-engineering — 2026-09-26
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

