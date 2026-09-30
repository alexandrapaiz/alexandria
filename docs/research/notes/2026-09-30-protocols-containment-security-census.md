# Three-thread census, 2026-09-30: protocols, containment, security

Owner directive 2026-09-29. Three threads, same shape as the reasoning-models
(2026-09-26) and self-improvement (2026-09-30, PR #138) runs. Read-only corpus
access through `NEON_RO_URL` with `psql`; no writes, no credentials printed.

## 0. The population, and how it was reconstructed

The owner's counts came from a title/abstract match the directive does not
print, so this run rebuilt one and checked it against the owner's numbers
before drawing any conclusion from it. The predicate is in
`docs/research/notes/` history via the queries below; in words, each thread is
a regex over `title || ' ' || abstract`, with the generic terms
(`isolation`, `container`, `permission`, `adversarial`, `malicious`,
`poison`, `threat model`) required to co-occur with `agent`, and the specific
terms (`model context protocol`, `MCP`, `A2A`, `sandbox`, `microVM`, `wasm`,
`prompt injection`, `tool poisoning`, `jailbreak`, `exfiltrat`, `guardrail`)
unconditional.

| thread | owner's papers | reconstructed | owner's distilled | reconstructed | owner's claims | reconstructed |
|---|---|---|---|---|---|---|
| protocols | 93 | 100 | 1 | 1 | 1 | 1 |
| containment | 188 | 182 | 5 | 5 | 24 | 24 |
| security | 288 | 274 | 8 | 9 | 34 | 44 |

Containment matches exactly on the two numbers that matter, protocols matches
on all three, security is 5% off on papers and carries ten extra claims my
predicate admits and the owner's did not. Same population, so the census below
is about the owner's threads and not about three neighbouring ones.

## 1. The finding that reframes the directive

The directive's stated mechanism is that "the papers arrive and then triage
indexes them as 'not a construction technique'." That happens, and it is the
smaller half. The dominant cause is that **triage never saw most of these
papers at all**, and when it does see them it passes most of them.

| thread | papers | never triaged | auto-indexed by backfill rule | ever judged by the model | of those, passed to distill |
|---|---|---|---|---|---|
| protocols | 100 | 55 (55%) | 36 | **9** | 4 (44%) |
| containment | 182 | 152 (84%) | 15 | **15** | 11 (73%) |
| security | 274 | 189 (69%) | 45 | **40** | 28 (70%) |

Three things fall out of that table.

**The model's judgment is not the bottleneck; it is the best-performing part
of the chain.** Handed a containment paper, triage routes 11 of 15 to distill.
Handed a security paper, 28 of 40. Corpus-wide those rates would be
remarkable. The rubric is not what is keeping these threads at one claim.

**Live `discard` is almost nil: 0, 0 and 3 across all three threads.** The
`index` decisions the directive describes are mostly not decisions. 96 of the
100 `index` rows across the three threads carry the reasoning string
`backfill: predates pipeline, auto-indexed by rule` — a rule, not a judgment.
The handful of real `index` verdicts read correctly, and one of them is
already applying the rubric the directive asks for:

> Sandbox escape in antivirus context, not agent sandboxing. No measured
> escape rates, agent-state design, or evaluation of agent runtime isolation.
> Relevant technique but wrong domain and no operational metrics.

That is triage declining a paper for exactly the reason a containment rubric
would want it declined. The rubric text in §4 is still worth writing, because
it is needed the moment throughput is fixed, but this run cannot claim the
rubric is why the threads are empty.

**Throughput is why.** Corpus-wide, 5,777 of 10,026 papers have never been
triaged, and 5,313 of those were published since 2026-09-01. Live triage
volume, from `triage_log` with the backfill rows excluded:

```
2026-09-08  50     2026-09-15  20     2026-09-22  10     2026-09-29   20
2026-09-09  20     2026-09-16  20     2026-09-23  20     2026-09-30  171
2026-09-10  10     2026-09-17  20     2026-09-24  10
2026-09-11  20     2026-09-18  10     2026-09-25  20
2026-09-12  20     2026-09-19  20     2026-09-26  10
2026-09-13  10     2026-09-20  10     2026-09-27  10
2026-09-14  10     2026-09-21  20     2026-09-28  20
```

Ten to twenty papers a day, against an ingest rate from `papers.fetched_at` of
274 to 2,216 a day over the same period. `pipeline/triage.py` is configured for
far more than it delivers: `MAX_CALLS_PER_RUN = 90` and `BATCH = 10` plan for
900 papers a run, and the run reports 10-20. The code says why in its own
words — it stops on the first batch no model will judge, printing "no model
could judge this batch ... stopping — rate limited" — and `CAP_USD = 0.60` is
the other candidate. Which of the two is binding is the engineer's to
determine; that it is one of them is not in doubt at a 45x gap between planned
and delivered.

**And the ordering makes the backlog a graveyard rather than a queue.** The
selection query in `pipeline/triage.py` orders by
`case when title ilike any(PRIORITY_PATTERNS) then 0 else 1 end, published_at
desc nulls last`. `PRIORITY_TERMS` is entirely the reasoning-models priority
(`reasoning`, `chain-of-thought`, `rlvr`, `grpo`, `verifiable reward`,
`test-time compute`, `process reward`, `long cot`) — correct per the owner's
2026-09-23 order, and it means every protocols, containment and security paper
sorts behind it. After the priority, newest-first. With ingest running 20-40x
triage, a paper not reached within roughly a day is displaced by papers
published after it, permanently. September bears this out — the share of each
day's intake that was ever live-triaged, by publication date:

```
09-10 22/310   09-15 17/306   09-20  2/99    09-25 37/334
09-11 15/134   09-16 16/320   09-21 26/321   09-26 11/95
09-12  5/49    09-17 27/340   09-22 12/323   09-27 15/118
09-13  8/44    09-18  9/273   09-23 33/368   09-28 63/418
09-14 28/138   09-19  3/72    09-24 68/382   09-29  0/18
```

Between 85% and 98% of what the field published in September, in the
categories we pay to ingest, has not been read by anything in this pipeline.
That is the coverage census, and it is the same answer for all three threads.

## 2. Thread by thread: the census is not the same story three times

### 2a. Protocols — genuinely empty, and the sources are the reason

100 papers, 1 distilled, 1 claim. The single claim is #656, from
*EvoOntology: A Self-Evolving Ontology Layer for Data Agents*: "EvoOntology
enables data agents to actively query and interact with a self-evolving
ontology via an MCP server, improving performance on heterogeneous data
tasks." MCP appears in it as deployment furniture. There is no claim in this
corpus about a protocol — not about MCP's transport or authorization model,
not about A2A's task lifecycle or agent cards, not about agent identity as a
principal. The thread is empty in substance, not merely thin.

The interesting part is that the feeds for this territory exist and fire.
`sources.yaml` carries `gh-a2a-protocol` and `gh-mcp-spec` at tier d, added
after incident 21, and they have delivered 18 rows. Here is every one of them:

```
gh-a2a-protocol   v1.0.1, v1.0.0, v1.0.0-rc, v0.3.0, v0.2.6, v0.2.5,
                  v0.2.4, v0.2.3, v0.2.2, v0.2.1
gh-mcp-spec       2026-07-28 RC, 2026-07-28, 2025-11-25, 2025-11-25-RC,
                  2025-06-18, 2024-11-05-final, 2024-11-05, 2025-03-26,
                  2024-10-07
```

Every title is a bare version or date string. Every abstract is empty. Every
`fulltext_chars` is null. Every one was `index`ed. This is not triage failing
to recognise substance; there is no substance in the row. `releases.atom` on a
specification repository returns the tag, and the MCP specification's whole
content — the revision's actual normative changes — lives in the repo's
`docs/specification/<date>/` tree and its changelog page, which that feed does
not carry. The two feeds that were added precisely so this thread would not be
empty are, as configured, 18 rows of zero information. §5 proposes the fix.

### 2b. Containment — 24 claims, none of them about containment

The 24 claims the directive credits to this thread are keyword artefacts. All
24, by paper:

- **T1: Terminal Agent Reinforcement Learning** (claims 204-207) — MoE terminal
  agent, Terminal-Bench scores, TITO/R³ log-probability gap, dense
  verification reward. Reasoning and RL work; matched on "terminal"/"isolated".
- **Emergence World: Adversarial Stress-Testing** (386-390) — multi-agent
  resilience under stress events, alignment non-compositionality, Agent World
  Indicators. The closest of the five to the thread, and still about
  population dynamics rather than isolation.
- **SoL-Pi: Recursively Scaling Auto-Research Loops** (535-539) — token
  traffic down 44.7-49.0%, Action Fusion, Online Context Compact,
  ObservationPack. Harness and token-efficiency work.
- **Reflect, Revise, Reuse: EvoSkill-GUI** (565-569) — GUI skill evolution,
  multi-file skill packages, metadata retrieval.
- **AgentWorld** (839-843) — multi-agent collaboration benchmark, Causal
  Collaboration Effectiveness.

Not one claim concerns a sandbox, a microVM, a wasm runtime, a capability
model, a measured escape, or the cost of an isolation boundary. The corpus
holds **zero** containment claims. This is the named priority of Layer 4 —
"AGENT CONTAINMENT ... the world just proved this field's stakes" — and the
count that reads as 24 is 0.

### 2c. Security — the one thread that is not empty, and is invisible anyway

This thread has real material, and it is good. Of the 44 claims, roughly 34
are genuinely about agent security, and several meet the directive's own
distill-worthy bar already:

- **EvoSafeHarness** (306-310): average attack success rate from **45.6% to
  10.0%** at a 3.3-point utility cost on DecodingTrust-Agent; **82.8% utility
  at 0.0% ASR** on AgentDojo, twice CaMeL's utility at the same operating
  point; mean ASR below 20% on Agent-SafetyBench under adaptive PAIR. A
  defense with a measured attack success rate, against named benchmarks, with
  a named baseline beaten. This is exactly the artifact the directive's rubric
  describes.
- **MOLE: Detecting Insider Threats in AI Agents** (166-170): **72%** of 39
  evaluated agent models complete most assigned harmful objectives, and agent
  refusal does not predict completion; the best monitor misses nearly half of
  completed harmful actions; benchmark-guided search improves a mid-tier
  monitor by 49-64%.
- **Shutdown Sabotage Propensities in Multi-Agent Systems** (742-746):
  multi-agent systems sabotage a peer's shutdown mechanism in **38.3%** of
  rollouts against **8.4%** in control; frequency rises with the
  irreversibility of the mechanism and with the number of agents; an explicit
  prohibition reduces but does not eliminate it. This is multi-agent collusion
  under containment, measured — the sub-area the charter names by name.
- **Decoy Direction Optimization** (420-424): under 10% ASR under Refusal
  Feature Ablation across six model families; Heretic weight-level ASR on
  Llama-3-8B-Instruct from 88.7% to 18%; 30-450x cheaper than trained defenses.
- **PACT** (557-561): rule-following under pressure across twelve regulated
  domains; ordinary user pressure raises rule-violation rates by **65%**.
- **Feyospace-v1** (323-327): offensive-side post-training, CyberGym verified
  success 63.24%, 164,269 audited trajectories.

So the security thread does not need a rubric to become distill-worthy. It
needs to be findable, and it is not, for two measured reasons in §3.

## 3. Why the security thread is invisible even though it has good claims

Two measured reasons, and neither is about the papers.

### 3a. There is no topic tag for any of these three threads

`prompts/distill.md` restricts `claims.topics` to a closed vocabulary: skills,
context-engineering, harness-engineering, loop-engineering, memory, retrieval,
multi-agent, evals, post-training, reasoning, serving, systems, tooling, other.
`reasoning` is in that list because the owner made reasoning models a named
priority on 2026-09-23 and the vocabulary was extended to match. Containment is
a named priority of the same standing and got no tag.

The consequence, measured over all 846 claims: the tag `containment` appears
**0** times. `protocols` appears **0** times. And the model, handed the
EvoSafeHarness claims, went outside the vocabulary rather than lose the
information — `safety` appears 3 times and `security` 2 times, neither
sanctioned by the prompt. Those 5 off-vocabulary tags are the distiller trying
to say something the vocabulary forbids.

So EvoSafeHarness's 0.0% attack-success-rate result is filed under
`{evals, safety}` and `{evals, post-training}`. Shutdown Sabotage is filed
under `{multi-agent, other}`. MOLE is `{evals, systems}`. A builder or a skill
agent querying the library for agent security finds them only by luck.

While counting tags, a second defect surfaced in the same column. **Six
vocabulary tags exist in the corpus in two spellings, split by a non-ASCII
hyphen (U+2011):**

```
post-training      290      post‑training        13
harness-engineering 243     harness‑engineering   4
loop-engineering   144      loop‑engineering      2
context-engineering 102     context‑engineering   1
task-refinement      1      task‑refinement       1
                            data‑augmentation     1
                            instruction‑tuning    1
```

Twenty-one claims carry a topic tag that no query for the spelling
`prompts/distill.md` actually specifies will ever match. The same
contamination runs through the claim text itself: **698 of 846 claims (82.5%)
contain at least one non-ASCII character**, and 1 of the 2 digest bodies does.
`docs/voice/ban-list.md` entry 13, amended after incident 27, bans exactly this
class of character, and the writer seat scrubs it at the issue. It is entering
at distill, upstream of every register that checks for it. §8 says why this run
does not spend its proposal there.

### 3b. Not one claim link joins two security claims

Of the 274 edges in `claim_links`, the number with **both** ends in the
security thread is **0**. Six have exactly one end in it, and all six run
outward into claims about something else:

| edge | verdict |
|---|---|
| 166 `supports` 16 — MOLE's "refusal does not predict completion" -> "rationale-only supervision reduces false refusals" | wrong. Agent-level behavioural measurement linked to a model-level refusal-training method because both say "refusal". |
| 166 `supports` 15 — same MOLE claim -> "boilerplate refusal statements cause superficial cues" | wrong, same cause. |
| 169 `supports` 88 — "selectively deploying a stronger monitor yields 10% budget-AUC" -> "the gains from the preservation instruction are not attributable solely to..." | wrong. Unrelated domains; the shared token is "gains". |
| 168 `supports` 51 — "benchmark-guided search improves a mid-tier monitor" -> "coordinating specialized agents for query reformulation, graph traversal" | wrong. Unrelated. |
| 306 `supports` 73 — EvoSafeHarness's policy-plus-code search -> "compile-by-training converts a natural-language specification into a reusable..." | defensible. Both are specification-to-artifact compilation. |
| 306 `supports` 186 — EvoSafeHarness -> "Show-Harness provides a compact semantic interface..." | wrong. The shared token is "harness". |

Five of six are lexical adjacency across unrelated domains. Meanwhile
EvoSafeHarness (306-310) and MOLE (166-170) — two papers that both measure
agent monitors and defenses against named attack benchmarks, and that plainly
bear on each other — have no edge between them at all. The graph draws the
spurious link and misses the real one.

The charter's Step 3 tells the skill agent to find a cluster via
`semantic_search` plus supports edges. In this territory that instruction
returns nothing, because the cluster exists in the claims and not in the graph.

### 3c. The `contradicts` edges, for the record

All 7 `contradicts` edges in the corpus, judged:

1. `12 -> 11` (0.88): "expert reference implementation achieves 82.2% on RMBench" vs "Claude Opus 5 under Claude Code passes 23.9%". **Comparison**, two systems on one benchmark, not a contradiction.
2. `85 -> 12` (0.78): "12.5% on four memory-dependent RMBench tasks" vs the 82.2% reference. **Comparison** across different systems *and* different task subsets.
3. `265 -> 85` (0.78): "MaP-WAM achieves 83.3% on RMBench" vs "the same execution approach attains only 12.5% on four memory-dependent tasks". **Refinement** — an aggregate and its own worst subset, which is where a headline number breaks down.
4. `136 -> 129` (0.90): "Feedback-Enriched Environments improve self-evolving agents" vs "adding Desired Behavior and Motivation to prompts improves coding-agent performance". **Not a relation at all.** Two independent improvements from two mechanisms.
5. `190 -> 188` (0.77): "a semantic interface alone unlocks capability from foundation VLMs" vs "small open-source VLMs can be adapted with a few GPU-hours". **Alternatives**, both can hold.
6. `289 -> 288` (0.75): "30 truthful recoveries, zero neutral" vs "zero recoveries in 96 challenger episodes". Plausibly two conditions of one experiment; **refinement** rather than contradiction.
7. `82 -> 5` (0.78): "a shared executable-skill interface with bounded VLA execution" vs "a single ReAct agent without sub-agents solves the hardest rollouts". **Defensible** — a real architectural tension.

Six of seven are comparisons, refinements or non-relations. This is a pattern
by the charter's own bar, and the 2026-09-28 digest reached the same verdict
independently on the first of them, in its own prose: "these numbers share a
percent sign and little else. The edge between them fails the kind test." The
press caught the bad edge; the graph still carries it.

## 4. Rubric text, per thread

The directive asks for rubric text that makes each thread distill-worthy. Below
is the text, written to drop into `prompts/triage.md` beside the reasoning
rubric it already carries. Each one names the measurement that earns `distill`
and the shape that earns `index`, with a worked example from this corpus.

### 4a. Protocols

> **Agent protocols and identity.** Route to `distill` a paper or artifact that
> reports a **protocol change and its measured effect**: a specification
> revision with a stated compatibility or failure consequence, an
> interoperability measurement across independent implementations, a
> measured cost of a transport or authorization choice, or an adoption study
> that counts implementations and names what broke. The unit is a claim a
> builder can act on when choosing or implementing a protocol.
>
> Route to `index` a paper that merely *uses* MCP or A2A as plumbing and
> measures something else, and a release note that carries only a version
> string or date.
>
> Accept: "An Empirical Study of Model Context Protocol Applications"
> (2607.25635), which counts real MCP servers and characterises their failure
> modes. Accept: "Can MCP Clients Decide What to Do After Failure? A
> Result-Only Actionability Audit" (2609.00072), which measures whether clients
> can act on a tool error. Reject: claim 656's source, *EvoOntology*, where the
> MCP server is deployment furniture and the measurement is ontology quality.

### 4b. Containment

> **Agent containment and isolation.** Route to `distill` a paper or artifact
> that reports an **isolation design together with a measured escape or a
> measured cost**: an escape or bypass with its preconditions, a benchmark of
> whether an agent can reach what it must not, the overhead a boundary imposes
> (latency, cold start, syscall cost, throughput), a capability or
> least-privilege scheme with the authority it actually withheld, or a
> production report of running agents under isolation at scale with numbers.
>
> Route to `index` a paper that asserts a sandbox without measuring it, a
> non-agent sandbox result with no transferable mechanism, and any isolation
> claim whose only evidence is that no escape was attempted.
>
> Accept: "Scaling Agentic-RL Sandboxes to the Millions with gVisor at Tencent"
> (gvisor.dev, 2026-04-23) — a production isolation design with scale numbers.
> Accept: "Authority Is Not a String: A Capability-Scoped Harness for
> Prompt-Injection-Resistant..." (2609.08371). Reject, and triage already did:
> the antivirus sandbox-escape paper it declined with "no measured escape
> rates, agent-state design, or evaluation of agent runtime isolation."

### 4c. Security

> **Agent safety and cybersecurity.** Route to `distill` a paper or artifact
> that reports a **defense or an attack with a measured attack success rate**
> against a named benchmark or a named baseline: ASR before and after, a
> utility cost paid for the ASR reduction, a monitor's detection rate and what
> it misses, or an attack with its success rate and preconditions. A postmortem
> with measured preconditions qualifies on the same terms as a paper.
>
> Route to `index` a paper that reports only that a vulnerability exists, a
> taxonomy or survey with no measurement of its own, and a benchmark paper that
> introduces the harness without reporting a defense or attack result on it.
>
> Accept: EvoSafeHarness (claims 306-310), 45.6% to 10.0% ASR at a 3.3-point
> utility cost, and 82.8% utility at 0.0% ASR on AgentDojo against CaMeL.
> Accept: Shutdown Sabotage (742-746), 38.3% against an 8.4% control. Reject:
> an agent-security survey that restates known attack classes without running
> one.

The honest caveat this run owes the directive: none of the three rubrics is why
the threads are thin, and installing all three tonight would change the counts
by roughly nothing, because triage reads 3-15% of what arrives (§1). The rubrics
are worth writing now so that they are already in place when throughput is
fixed; they are not the fix.

## 5. Topic definitions

Three tags for `prompts/distill.md`'s vocabulary, written in the same register
as the entries already there, with the boundary against neighbouring tags
stated because that is where the existing vocabulary leaks.

> - `protocols` — the wire contract between agents, or between an agent and its
>   tools: MCP, A2A, agent cards, task lifecycles, tool-calling schemas, agent
>   identity as a principal (SPIFFE, per-agent OAuth, workload identity), and
>   interoperability across independent implementations. Tag it when the claim
>   is about the contract itself. A claim about what an agent *did* over a
>   protocol is `tooling` or `multi-agent`, not this.
>
> - `containment` — the boundary an agent runs inside and what it costs:
>   sandboxes, microVMs, wasm runtimes, containers and their pinned runtimes,
>   capability and least-privilege schemes, measured escapes and their
>   preconditions, and containment evaluation. Tag it when the claim is about
>   the boundary. A claim about an agent's runtime performance inside a
>   boundary is `systems`; a claim about the attack that crossed it is
>   `security`, and claims about both take both tags.
>
> - `security` — adversarial pressure on agents and the defenses measured
>   against it: prompt injection and indirect injection, tool poisoning,
>   jailbreaks, exfiltration, sabotage and collusion between agents,
>   guardrails and monitors, and attack success rates. Tag it whenever a claim
>   carries an ASR, a detection rate, or a sabotage frequency. `evals` is for
>   how capability is measured; a security benchmark takes both.

Precedent for the addition, so it is not a novelty: `reasoning` was added to
this vocabulary for the Layer 3a priority and the observed distribution shows
it in use. The measured need for these three is §3a — 21 claims already reach
for `safety`, `security` or a hyphen-variant the prompt does not sanction.

## 6. Sources: the reach gap, measured against external ground truth

Method, the same one ADR-29's monthly census mandates and the same one the
2026-09-19 containment brief used on cs.CR: query the live arXiv API for
September 2026 submissions on each thread's terms, sample the 400 most recent,
and diff their ids against `papers`.

September 2026 on arXiv, by `totalResults`:

| thread terms | September arXiv papers | in our corpus (of a 400 sample) |
|---|---|---|
| model context protocol / agent-to-agent / agent interoperability / agent identity / MCP / A2A | 1,778 | **28 (7%)** |
| sandbox / sandboxing / microVM / capability-based / agent isolation / least privilege | 1,285 | **36 (9%)** |
| prompt injection / tool poisoning / agent hijacking / jailbreak / exfiltration | 2,703 | **55 (13%)** |

### 6a. The gap is not a category gap, with one exception

The obvious inference from 7-13% is that we are missing arXiv categories. The
data says otherwise. Of the missed papers in the sample, the share carrying a
cross-list into a category `sources.yaml` already ingests:

| thread | missed | cross-listed into a category we ingest | structurally unreachable |
|---|---|---|---|
| protocols | 372 | 296 (80%) | 76 |
| containment | 364 | 318 (87%) | 46 |
| security | 345 | 319 (92%) | **26** |

For the security thread, 92% of what we missed was already inside our
subscription. No source diff reaches it. The throughput finding in §1 is the
whole story there, and adding feeds to a pipeline that reads 3-15% of its intake
makes the arithmetic worse, not better. **Ordering matters: throughput before
sources.** This is stated plainly because the directive asks for sources and the
evidence says sources are the second problem.

The one real category gap, consistent across all three threads, is **cs.SE**.
Primary categories of the structurally unreachable papers, combined:
`cs.SE=82, cs.CV=56, cs.RO=30, cs.CY=21, cs.HC=15`. cs.CV and cs.RO are noise
for us (knee-MRI foundation models, robot navigation, chart-to-code). cs.SE is
not. It is where the empirical protocol literature lives, and every one of
these is unreachable today:

```
2609.14721  A Two-Dimensional Study of the Model Context Protocol: Publication and Adoption
2607.25635  An Empirical Study of Model Context Protocol Applications
2606.09182  Understanding How Enterprises Adopt the Model Context Protocol for LLM-Driven SE
2609.00072  Can MCP Clients Decide What to Do After Failure? A Result-Only Actionability Audit
2608.24944  Secret MCP: Evidence-Bounded and Context-Isolated Design Specification Generation
2607.17012  Schema-Bound LLM Control of Scientific Instrumentation through Model Context Protocol
2608.23084  ARGUS: MCP-Grounded Root Cause Analysis for Kubernetes Incidents
2606.25257  How Do Developers Maintain and Evolve Their Agents' Instructions? An Empirical Study
```

The protocols thread has one claim, and the reason is visible right there: the
people measuring MCP in the field publish in cs.SE, and we do not read cs.SE.
This is the cs.CR finding of 2026-09-19 repeating in a different category.

cs.SE also carries containment work — `2609.08371` "Authority Is Not a String:
A Capability-Scoped Harness for Prompt-Injection-Resistant..." (the
capability-scoping sub-area by name), `2607.27294` "AgentS4D: Benchmarking
Runtime Risks across the Execution Lifecycle of LLM-Based Workspace [agents]",
`2606.19409` "OpenRath: Session-Centered Runtime State for Agent Systems",
`2608.05521` "Reasoning from Traces: Divergence-Guided Agentic Repair of
WebAssembly Discrepancies" — and security work: `2609.27263` "Specifying and
Maintaining Agentic Workflows: An Empirical Study of GitHub Agentic Workflows".

Volume, so the tier is a measurement and not a guess: cs.SE ran **639 papers in
September**, about 21 a day, against cs.CR's 1,106 (37 a day) which
`sources.yaml` already carries at `a-low`. 270 of the 639 (42%) mention "agent"
in the abstract, a better agent density than cs.CR's. cs.SE at `a-low` is
therefore the conservative placement, not a generous one.

### 6b. The two protocol feeds we have are 18 rows of nothing

§2a established this: `gh-a2a-protocol` and `gh-mcp-spec` point at
`releases.atom`, which on a specification repository returns the tag and
nothing else. Eighteen rows, every title a bare version or date string, every
abstract empty, every `fulltext_chars` null, every one indexed.

The fix the directive names — spec changelogs, not only releases — exists as a
path-scoped GitHub commits feed, and it works. Verified 2026-09-30, HTTP 200
with 20 entries each, and the path filter genuinely narrows (the spec-path feed
returns different, spec-only commits than the whole-branch feed):

```
https://github.com/modelcontextprotocol/modelcontextprotocol/commits/main/docs/specification.atom
https://github.com/modelcontextprotocol/modelcontextprotocol/commits/main/seps.atom
https://github.com/a2aproject/A2A/commits/main/specification.atom
```

What they buy, stated honestly: the commit messages are mostly spec-text
maintenance ("Fix 'Serves' typo in resources capability text", "docs: fix
invalid JSON in two example code blocks"), which triage should discard. The
`seps.atom` feed is the higher-signal one, because MCP's normative change runs
through a numbered Specification Enhancement Proposal process, and its commits
name the substance: "Add Agent Skills backward-compatibility requirement",
"align capability wording with ext-skills", "Require WG/IG discussion before
SEP submission". A feed whose good items are one in five is still infinitely
better than a feed whose items are the string "v1.0.1".

### 6c. What the protocol blind spot has already cost this project

Following `seps.atom` to its source produced the most product-relevant finding
of this run, and it is not a paper.

**SEP-2640, "Skills Extension", status Final, created 2026-04-23**, defines a
convention for serving Agent Skills over MCP. It specifies the `skill://` URI
scheme, the `skills/list` and `skills/get` methods, the extension identifier
`io.modelcontextprotocol/skills`, and an optional
`resources/directory/read`. It was written by a "Skills Over MCP Working
Group". It delegates the skill format itself — directory structure, YAML
frontmatter, naming, and the progressive-disclosure model that governs how
hosts stage content into context — entirely to the **Agent Skills
specification** at `agentskills.io/specification`, and requires that clients
honour that specification's own backward-compatibility mechanisms.

alexandria's terminal asset is a skills library. There is a Final standard for
how skills are served and a separate standard for how they are formatted,
neither is in `sources.yaml`, and the corpus holds zero claims about either.
The one feed pointed at that repository reports version dates.

The good news, checked rather than assumed: `skills/*/SKILL.md` in this
repository already carries YAML frontmatter with `name` and `description`, which
is the Agent Skills specification's stated minimum. The library is
shaped to be servable under SEP-2640 without a format change. What is missing is
that nothing in this system knew the standard existed. That is the skill seat's
and the PM's call to act on, not this seat's; it is routed in the brief.

`agentskills.io` publishes no feed (checked: `/feed.xml` and `/rss.xml` both
404). `https://github.com/modelcontextprotocol/ext-skills/commits/main.atom`
returns 200 and is the working proxy for that specification's development.

### 6d. Containment: the isolation engineering is on vendor blogs, not arXiv

The containment thread's rubric asks for a measured escape or a measured cost.
arXiv mostly does not carry that; the people who run isolation at scale write it
up themselves. Verified 2026-09-30, all HTTP 200 with parseable entries:

- `https://gvisor.dev/blog/index.xml` — 10 entries spanning 2023-2026, and the
  titles are the rubric: "Scaling Agentic-RL Sandboxes to the Millions with
  gVisor at Tencent" (2026-04-23), "Multi-Agent gVisor Isolation (MAGI)"
  (2026-04-15), "Optimizing seccomp usage in gVisor", "Safe Ride into the
  Dangerzone: Reducing attack surface with gVisor", "Who needs VMs? Run systemd
  and full Linux desktop apps in gVisor" (2026-09-17). Low volume, so it costs
  the triage budget almost nothing, which matters given §1.
- `https://github.com/firecracker-microvm/firecracker/releases.atom` — microVM,
  the named sub-area, 10 entries.
- `https://github.com/bytecodealliance/wasmtime/releases.atom` — the wasm
  runtime, 10 entries.

Declined after checking, and named so the next census does not re-examine them:
`kata-containers` releases (200, but the release notes are dependency bumps);
`cncf.io/feed/` (200, and far too broad — general cloud-native news at a volume
that would crowd the queue); `e2b.dev/blog/rss.xml` and `modal.com/blog/feed.xml`
(both 404, so the agent-sandbox vendors are unreachable by feed today, which is
worth a recheck next month).

### 6e. Security: one standards body, and one declined

- `https://genai.owasp.org/feed/` — 200, 10 entries, and the content is the
  thread: "OWASP GenAI Security Project Unveils 2026 Top 10 for LLM
  Applications, New Agent Control Standard", "Memory Is a Feature. It Is Also
  an Attack Surface", "OWASP GenAI Exploit Round-up Report Q1 2026". A standards
  body shipping agent-security substance, and the "New Agent Control Standard"
  is exactly the artifact-with-method the charter admits. Propose.
- `https://openid.net/feed/` — 200, but **declined**. Its 10 most recent items
  are OpenID4VP/OpenID4VCI certification, age assurance, post-quantum OIDC and
  workshop notices. Nothing agent-specific in the sample. Agent identity as a
  principal is a real charter sub-area and this feed is not currently where it
  is happening; adding it would spend triage budget on credential-format news.
  Recheck next census.

## 7. Radar: the first skill each thread deserves

Step 3 of the charter, kept to targets rather than drafts (ADR-22). None of
these is proposable this week, and the reason is the same each time.

**Security — `agent-defense-evaluation`, and it is close.** The claims exist and
they measure the right things: EvoSafeHarness's ASR-versus-utility operating
points (306-310), MOLE's monitor detection gap (166-170), DDO's cost ratio
(420-424), Shutdown Sabotage's collusion frequencies (742-746), PACT's
pressure effect (557-561). That is five independent papers converging on one
procedure: how to measure whether a defense works, what utility you pay, and
what your monitor misses. **Blocker:** the graph holds zero edges between any
two of them (§3b), so the charter's own "cluster of mutually supporting claims"
test cannot be satisfied, and a skill asserting the cluster on this seat's
reading rather than on evidenced links is the padded skill the charter forbids.
Re-run the interpret pass over these 34 claims and this becomes the strongest
skill target in the corpus.

**Containment — `agent-isolation-boundaries`, and it is empty.** Zero claims
(§2b). Nothing to build on. The first ingredient is not a skill proposal, it is
the gVisor material in §6d and the cs.SE capability-scoping papers in §6a
reaching distill. Named here so the shelf has a name before it has contents.

**Protocols — `mcp-server-design`, and it is a one-claim thread.** The material
exists in cs.SE (§6a) and in the SEP process (§6c), and none of it is in the
corpus. The skill this deserves first is not about MCP in general but about the
one piece with a Final standard and direct product bearing: serving skills over
MCP under SEP-2640. That is a skill the skill seat could write from the
specification itself rather than from claims, which is a different evidence
route than ADR-22 contemplates, and therefore a question for the owner rather
than an assumption by this seat.

## 8. Meta-review: what reaches production, and what this run will not propose

The charter requires checking deploy state before spending the week's proposal.
Measured tonight against `sha256(prompts/<file>.md)[:12]`:

| file | main | HEAD (this branch) | deployed | verdict |
|---|---|---|---|---|
| `interpret.md` | `6706ec7bffee` | `6706ec7bffee` | `6706ec7bffee` on 3 edges; `fbe080261d6b` on 271 | current, but almost no output yet |
| `triage.md` | `32252384ecd7` | `a9e16aa25ba6` | `32252384ecd7`, 180 rows today | **main is live** |
| `digest.md` | `5db6c08aba9e` | `5db6c08aba9e` | `ea2d678d86e9`, `83a0aa3be13c` | **stale; the deployed press prompt is in no commit** |
| `distill.md` | `819694a98603` | `819694a98603` | unknowable — `claims.prompt_sha` is null on 846 of 846 rows | **unverifiable** |

Three consequences for this run's one proposal.

**Not `interpret.md`.** Every one of the 7 bad `contradicts` edges and all 6 of
the bad `supports` edges carry `method = openai/gpt-oss-120b@fbe080261d6b` — a
prompt that no longer runs. The current prompt is deployed and has produced 3
edges, which is not enough evidence to say whether it fixed the problem. A
proposal here would be evidence against a prompt that is already gone. What the
271 stale edges need is a re-interpret pass, which is the engineer's job, not a
prompt diff.

**Not `distill.md`,** even though §3a's evidence is strong and points straight
at it. `claims.prompt_sha` is null on every row, so the column that exists to
answer "is the deployed distiller current" answers nothing, and PR #138 found
independently tonight that the distill image is behind (the reading queue's 27
arXiv ids have been parseable since 2026-09-27 and none is ingested). Proposing
the topic-vocabulary extension into an image whose state cannot be verified is
incident 25's shape exactly. The definitions are written in §5 and held for the
week after the deploy lands. **That distill writes no `prompt_sha` is itself the
finding to route**, because it disables the charter's own safety check.

**So: `sources.yaml`,** which the directive asks for by name and which the
evidence in §6 supports with external measurement. It is image-baked and
frozen until `modal deploy`, and the triage evidence above shows deploys are
happening (main's `triage.md` went live today), so the diff will reach
production on the next one. The brief routes the deploy.

