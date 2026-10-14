# Reading-queue drain — 2026-09-30 (research seat, PR #162)

Third dispatch of 2026-09-30. `NEON_RO_URL` is **not set** in this runner, so
this run has no corpus access at all and does only the repo-side work the
workflow's own fallback clause prescribes. That removed the digest review, the
graph audit and the triage/distill health queries from reach, and left the one
charter duty that needs no database and had been named unfinished twice in one
night: **the reading queue.**

`docs/research/reading-queue.md` carried 27 arXiv ids, 4 no-id works and 9
questions. PR #138 struck four on their abstracts. PR #145 struck none and
wrote, in the file itself, that reading the remaining 23 in full "was not
compatible with this dispatch's four deliverables." This run reads them.

**How they were read.** `python3 tools/read_paper.py <id>`, which exits 0 on
full text and 3 on the abstract alone. **22 of 23 returned full text**
(2.06 million characters); `2602.10560` returned the abstract only and is
recorded below as abstract-read, not read. Every id resolved, so the queue
holds no bad ids, which agrees with what PR #138 measured against the API.

Findings are written per paper only where the reading **changes something the
library already asserts**. Where a paper merely confirms a claim, it is
recorded as confirmed and not elaborated.

---

## 1. SkillsBench — arxiv:2602.12670 (read in full)

*SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks*,
v4, cs.AI, 14 Jun 2026. 87 tasks, 8 domains, 18 model–harness configurations,
three arms per task (A no skills, B curated bundle, C agent-authored).

**The headline the library has been quoting second-hand, now first-hand.**
Curated skills lift task-macro pass rate from **33.9% to 50.5%, +16.6 pp**
(25.5% normalized gain), configuration-level range **+4.1 to +25.7 pp**.

**Three results that bear directly on ADR-38 and on the six shipped skills.**

1. **Length is measured, and comprehensive prose is worth almost nothing.**
   By skill complexity: compact **+19.0 pp**, standard **+21.5 pp**, detailed
   **+14.5 pp**, comprehensive documentation **+0.7 pp**. By skill quantity per
   task: one skill +18.0, two to three +19.0, four or more **+10.1**. The
   authors' own conclusion is that authors "should optimize for verifier-facing
   detail an agent cannot infer, not for completeness."
2. **Agent-authored skills land below the no-skills baseline.** On the three
   dedicated-harness configurations: **−8.1 pp** (Claude Code + Opus 4.7),
   **−11.3 pp** (Codex + GPT-5.5), **−11.5 pp** (Gemini CLI + Gemini 3.1 Pro),
   while curated skills add **+18.2 to +24.8 pp** on those same
   configurations. The trajectory audit attributes it to three causes: packs
   the solver never discovers, creator-side authoring that displaces solver
   work, and confidently wrong pack content when the packs are used.
3. **The negative-delta tasks have one root cause, and it is a missing
   section.** 13 of 87 tasks show negative deltas (largest −7.4 pp). The
   paired-trajectory audit finds three repeatable patterns — the skill
   prescribes an unnecessarily heavyweight pipeline, displaces a stronger
   default strategy, or points the agent at a solver it cannot debug — and
   names the common cause: **a single "correct" pipeline without applicability
   boundaries or lightweight fallbacks.** The paper proposes extending
   `SKILL.md` frontmatter with an explicit **complexity contract**: expected
   tool and token cost, applicability boundaries, and a required lightweight
   fallback path.

**Domain heterogeneity, and it is uncomfortable for this product.** Natural
Science +28.8 pp, Media and Content +24.1, Cybersecurity +18.9, Industrial
+15.7, Finance +14.2, Office +12.6, **Software Engineering +11.6**,
Mathematics and OR **+9.7**. Skills help most where pretraining coverage is
thinnest. Alexandria's six shipped skills are all in or adjacent to the two
lowest-lift domains.

**The caveat the paper states against itself, which the library should carry.**
Skill injection increases context length, and SkillsBench ran **no
length-matched control** — no random or irrelevant text of equal length, no
retrieval-only documentation arm. The authors say plainly that the +16.6 pp
"could partly reflect 'more context' rather than procedural structure." The
self-generated arm is their partial answer, and they note it confounds content
quality with discovery and creator/solver interference. Any with/without eval
harness built here inherits exactly this confound.

**Scale.** 2,014,000 source-partitioned skills in the construction snapshot,
from 400 task submissions by 142 contributors in a 1,400-member community.

---

## 2. Skill-Use — arxiv:2608.04828 (read in full)

*Skill-Use: Can LLMs Actually Use Skills in Agentic Harnesses?* 79 real skills
paired with 177 executable tasks, nine domains, Docker sandbox, trajectory
rubrics (1,314 items, mean 7.4 per task). Eight models from seven families
under two harnesses (Claude Code, Codex). Three facets: **Trigger** (did the
agent retrieve the skill from name and description alone), **Compliance** (did
it follow the procedure), **Boundary** (did it avoid the forbidden operations);
`SU = Trigger x [0.7 Compliance + 0.3 Boundary]`.

This is the paper the queue line called "the 177-task executable benchmark
behind the trigger-rate table," and reading it produces **three corrections to
`skills/skill-library-engineering/SKILL.md`** plus an answer to two of the
queue's own open questions. The corrections are in section 6 below; the primary
results first.

**Main results (Table 1).** Best configuration is GPT-5.5 under Claude Code at
**SU 0.613**. Trigger under Claude Code splits the field in two: Opus 4.7
0.966, Opus 4.8 0.940, GPT-5.5 0.972, MiniMax-M3 0.833 — against
DeepSeek-V4-Pro 0.324, GLM-5.1 0.324, Kimi-K2.6 0.337, Qwen3.6-Max 0.446.
Best Compliance on triggered traces only reaches **0.638**. Boundary exceeds
Compliance in every configuration, so models suppress forbidden actions more
reliably than they complete required steps.

**Boundary's one exception is Security and Compliance skills**, where models
achieve reasonable Compliance and the **lowest Boundary** in the benchmark:
they carry out the safety steps and still invoke the operations the skill
forbids. Named here for the skill seat, because the two skills shipped in #146
are in exactly that category.

**Break-even is measured, and it sits at SU 0.5.** Pairing 779 triggered runs
against the same task and model with the library disabled, mean paired task
completion gain is **negative below SU 0.5 and positive above it**. The
authors' mechanism: "A partial procedure is worse than none because the model
commits to a prescribed toolchain or format without carrying it through, and
the resulting artifact is neither what the skill demands nor what the model
would produce unaided."

**Library size is measured at the size a product actually ships.** Under Claude
Code with N in {1, 10, 20, 30} installed skills, target always present,
distractors random: all models select the target reliably at N=1; **the visible
drop happens moving to ten**; after that the curves change little. The authors'
words: "**Library growth creates an entry cost, not a steady decline.**" At
larger sizes most failures are runs with **no** skill call; wrong-skill calls
are rare and concentrate on broad overlapping descriptions
(`test-driven-development` against `software-architecture`).

**Restraint is anti-correlated with skill use.** On 53 out-of-scope tasks whose
topic overlaps a skill but whose output does not need its procedure, the rank
correlation between within-scope SU and out-of-scope avoidance is
**negative**: the models best at following a skill are among the worst at
declining to invoke one. Over-invocation is driven by topical overlap, and the
paper names the shape it happens to: "mostly **document-shaped requests** whose
topic matches the skill's domain even though the output never needs its
procedure."

**Injection mode.** Preloading the full skill text raises Trigger and barely
moves Compliance on traces that trigger under both modes. Retrieval under
progressive disclosure, not downstream execution, accounts for most of the
effect.
