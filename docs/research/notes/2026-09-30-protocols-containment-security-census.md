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

