# Orchestration deep dive — 2026-09-19

**Dispatch.** Owner order relayed by the chair, 2026-09-18: *"make sure we
really research orchestration in ai."* A dedicated deep dive ahead of the
Monday cadence, under the orchestration research program in
`prompts/research-agent.md` step 2b.

**Data access.** `NEON_RO_URL` was set; the corpus was queried read-only.
Every corpus number below is reproducible from the queries in Appendix A.

**Evidence bar.** Three independent sources for a pattern. Framework
marketing is not a finding: every framework statement here comes from a
specification changelog, a release feed, or a technical documentation page,
each linked. Anecdote and result are kept apart, and where the honest answer
is "the evidence does not support a rule yet," that is what is written.

---

## 0. The finding that reframes everything below

**alexandria currently cannot see orchestration.** Not "sees it weakly" —
structurally cannot, through any of the sources added for it. This was
discovered while assembling §2 and it governs how §2, §4 and §5 should be
read.

Three facts, each one query:

1. **All 504 claims in the corpus come from exactly one source.**
   `hf-daily` (tier `b`), 109 distinct papers. Not one claim has ever come
   from arXiv, from a lab blog, or from a framework release feed.

2. **All 2,445 arXiv papers are still untriaged — including every cs.MA
   paper.** They are not discarded; they sit in `triage_queue`, never read.
   `sources.yaml` lists `cs.MA` (the multi-agent category, tier `a`) and it
   has produced nothing, because `pipeline/triage.py` orders the queue
   `b → c → d → a → a-low` and the model has judged **210 papers total in 11
   days** (~19/day) while ingest brought in **315, 338 and 458 papers** on the
   last three days alone. Tier `a` is last in a line that grows roughly an
   order of magnitude faster than it drains. The arXiv firehose is not a slow
   source; it is an unreachable one.

3. **The orchestration feeds the owner named have never been judged at all.**
   `gh-langgraph` (2), `gh-autogen` (10) and `gh-mcp-spec` (7) — 19 releases,
   **100% auto-indexed by `rule:backfill`**, zero model judgments. Their
   release dates predate the 60-day `BACKFILL_DAYS` cutoff, so
   `triage.py` stamped them `index` by rule without reading them. A further
   28 (`gh-langgraph` 8, `gh-mcp-spec` 2, `gh-claude-code` 18) are still
   queued.

And `index` is a terminal state: `distill_queue` admits only `distill` and
`deep_read`, so an indexed item can never produce a claim, never gain an
edge, and never become a digest item with evidence behind it. Across every
`gh-*` feed, **0 of 30 releases** have ever been routed to `distill`.

The consequence for this dispatch is exact: **§4's source additions are
necessary but not sufficient.** Adding CrewAI or Temporal to `sources.yaml`
today would put them at the back of the same queue, behind 2,445 arXiv
papers, and the 60-day backfill rule would stamp their older releases
`index` unread. Orchestration coverage becomes permanent pipeline input only
if the throughput and routing defects in §7 are fixed alongside it. Anything
less is a diff that looks like coverage and delivers none.

---

## 1. The orchestration field as it stands, with evidence

### 1.1 The taxonomy has converged — and it is judgment, not measurement

Two independent primary sources now state the same distinction in nearly the
same words.

Anthropic, *Building Effective Agents*
([anthropic.com/engineering/building-effective-agents](https://www.anthropic.com/engineering/building-effective-agents)):

> Workflows are systems where LLMs and tools are orchestrated through
> predefined code paths. Agents, on the other hand, are systems where LLMs
> dynamically direct their own processes and tool usage, maintaining control
> over how they accomplish tasks.

LangChain, *Workflows and agents*
([docs.langchain.com](https://docs.langchain.com/oss/python/langgraph/workflows-agents),
`dateModified` 2026-09-18 — updated the day before this brief):

> Workflows have predetermined code paths and are designed to operate in a
> certain order. Agents are dynamic and define their own processes and tool
> usage.

The LangGraph page's section headings are Anthropic's five patterns in
order: **prompt chaining, parallelization, routing, orchestrator-worker,
evaluator-optimizer**, then **agents**. That is convergence on a shared
vocabulary, which is real and useful.

What neither source provides is a *decision rule*. Anthropic's guidance is
explicitly economic and explicitly qualitative:

> we recommend finding the simplest solution possible, and only increasing
> complexity when needed. This might mean not building agentic systems at
> all. Agentic systems often trade latency and cost for better task
> performance […] you should consider adding complexity only when it
> demonstrably improves outcomes.

and on the boundary itself: workflows "offer predictability and consistency
for well-defined tasks, whereas agents are the better option when
flexibility and model-driven decision-making are needed at scale." LangGraph
says agents suit problems where "problems and solutions are unpredictable."

Both sources push the decision back onto the builder's own measurements.
Neither cites a controlled comparison. This is the honest state of the art
and it is the basis of §3.

### 1.2 Durability moved up the stack — the clearest real movement this period

This is the one orchestration pattern that clears the three-independent-
sources bar with primary evidence, and the sources move in the *same
direction*: the transport layer is shedding state, and resumption is
becoming the orchestrator's explicit, externally-stored responsibility.

**Source 1 — the MCP specification, revision 2026-07-28**
([changelog](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/changelog.mdx)).
The spec went *stateless*, deliberately and at cost:

- Protocol-level sessions and `Mcp-Session-Id` removed; servers needing
  cross-call state use "explicit, server-minted handles passed as ordinary
  tool arguments" (SEP-2567).
- The `initialize`/`notifications/initialized` handshake removed; every
  request now carries its own protocol version and capabilities in `_meta`
  (SEP-2575).
- **SSE stream resumability and message redelivery removed** — `Last-Event-ID`
  and event IDs are gone, and "a broken response stream loses the in-flight
  request; clients **MUST** re-issue it as a new request with a new request
  ID" (SEP-2575).
- Long-running work left the core protocol for an extension
  (`io.modelcontextprotocol/tasks`), with blocking `tasks/result` replaced by
  polling `tasks/get` plus `tasks/update` (SEP-2663).

Read plainly: MCP decided durability is *not* the protocol's job and handed
it to the layer above. That is a strong, checkable architectural position,
and it is the opposite of what a framework's marketing would claim.

**Source 2 — LangGraph.** Checkpointing is not a feature flag but a
separately versioned product surface: `langgraph-checkpoint==4.2.0` and
`langgraph-checkpoint-postgres==3.1.2` ship on their own cadence in the
[release feed](https://github.com/langchain-ai/langgraph/releases.atom). The
[persistence docs](https://docs.langchain.com/oss/python/langgraph/persistence)
scope checkpointers to exactly the durability problem — "continue a
conversation, resume after an interruption, recover from a failure" — and the
capability nav carries *Fault tolerance*, *Interrupts* and *Time travel* as
first-class pages.

**Source 3 — OpenAI Agents SDK.** The
[sessions documentation](https://openai.github.io/openai-agents-python/sessions/)
leads with "Resuming interrupted runs with the same session," and ships
multiple persistence backends (SQLAlchemy, SQLite, encrypted) as built-ins.

**Corroborating (not counted in the three) — durable execution proper.**
Temporal continues near-daily releases (`v1.32.0-162.5`, 2026-09-18), and
CrewAI exposes "Replay Tasks from Latest Crew Kickoff." The durable-execution
lineage that predates LLM agents is being drawn on, not reinvented.

### 1.3 Topology primitives, by framework, from primary docs

| Framework | Topology primitives | Durability primitive |
|---|---|---|
| LangGraph | graph nodes/edges; orchestrator-worker; routing; evaluator-optimizer | checkpointers, stores; interrupts; time travel |
| OpenAI Agents SDK | **handoffs** (first-class, under "Agent orchestration"); guardrails | sessions (SQLAlchemy / SQLite / encrypted) |
| AG2 (AutoGen line) | two-agent chat; sequential chat w/ carryover; nested chat; group chats; pattern cookbook | — (carryover is context, not checkpointing) |
| CrewAI | `Process.sequential`; `Process.hierarchical` (manager delegation) | replay from latest kickoff |
| MCP (protocol) | not a topology; tool/resource interface | **explicitly removed** (§1.2) |

Sources: [AG2 orchestration](https://docs.ag2.ai/latest/docs/user-guide/advanced-concepts/orchestration/orchestrations/),
[CrewAI processes](https://docs.crewai.com/en/concepts/processes),
[OpenAI handoffs](https://openai.github.io/openai-agents-python/handoffs/),
LangGraph as above.

The primitives differ more than the shared taxonomy suggests. "Handoff"
(OpenAI), "group chat" (AG2) and "hierarchical process" (CrewAI) are not
three names for one thing: they differ in who holds control, what carries
across the boundary, and whether the transfer is recoverable. No framework
publishes measured failure rates for its own topology — see §3.

### 1.4 The active AutoGen line has moved, and our feed is on the wrong repo

`microsoft/autogen`'s latest release in its feed is **`python-v0.7.5`,
2025-09-30** — nearly a year stale. The community fork **AG2** (`ag2ai/ag2`)
has shipped **v1.0.1 through v1.0.5 between 2026-07-29 and 2026-09-11**.
`sources.yaml` watches `gh-autogen` (the stale repo) and not AG2. This is a
concrete, checkable miss and §4 fixes it.

### 1.5 What the corpus adds that the frameworks do not

The frameworks document *what they offer*. The corpus contributes the only
adversarial evidence we hold on what multi-agent systems actually do wrong —
*Emergence World* (claims 386-389): no evaluated world was fully resilient
across three stress events; recognition of an attack does not guarantee
restraint or recovery; **model-level alignment is not compositional** (the
same model behaves differently in mixed vs. homogeneous populations); and
persistent operation surfaces recurring tool errors, goal drift, language
opacity, and coordinated refusal of assigned work.

That last cluster is the most genuinely differentiated orchestration material
we own, and — see §2 — it currently has no embedding and no graph edges.

---

## 2. Orchestration claim clusters in the corpus, and extraction targets

**Scale, stated honestly.** 33 claims carry the `multi-agent` topic tag. Of
those, **9 have been interpreted** and **7 have any graph edge at all**.
Corpus-wide, 323 of 504 claims (64%) have never been interpreted, and 119
claims — every claim created on 2026-09-17 and 2026-09-18 — **have no
embedding**, which makes them invisible to `semantic_search` and excludes
them from `interpret_queue` entirely.

**This changes how the skill agent must work on Tuesday.** The charter's
normal method — find clusters via `semantic_search` plus `supports` edges —
will silently under-return on orchestration, because the orchestration claims
largely have neither. The clusters below were therefore assembled by
paper-level coherence and embedding-neighbour search from anchor claims, not
by edge traversal. The skill agent should treat claim IDs, not edges, as the
handle here.

Ranked extraction targets:

**T1 — Multi-agent failure modes under long-horizon operation.**
Claims **386, 387, 388, 389** (*Emergence World*), supported by **13**
(τ^τ-Bench coding-agent failure modes: shallow queries, minimal
communication). *Why first:* it is procedure-and-judgment material (what
breaks, when not to use this) rather than a benchmark number, which is the
skill format's strength; it is the part of orchestration no framework
documents; and it directly serves the digest's differentiation. *Caveat the
skill agent must handle:* these four claims have **no embedding and no
edges** — they will not surface by search. Load them by ID.

**T2 — Orchestrator-worker: when decomposition pays.**
Claims **106** (decomposition quality bounds the achievable gain — the
theoretical spine), **110** (72.2% vs 70.8% on SWE-bench), **49/51** (PACE:
specialised agents beat a monolithic model on conflict detection),
**6/7/8/9** (MaxKernel: specialised sub-agent pool for TPU kernels).
*Why second:* 106 supplies the *judgment* — the gain is bounded by how
cleanly the task decomposes — which turns a set of results into a usable
rule. *Caveat:* margins are narrow (110 is +1.4pp over a *mini* baseline) and
must be reported as such, not rounded up into a recommendation.

**T3 — Lead-agent/sub-agent parallel reading.**
Claims **291, 292, 294, 295** (*PARSER*): parallel subagents with a single
learnable lead agent; **up to 11× lower latency** than sequential memory
agents; all learning concentrated in the lead while subagents stay frozen
off-the-shelf. *Why third:* the cleanest measured, mechanism-plus-number
cluster we own, and the "train the lead, freeze the workers" design is
directly transferable. *Caveat:* the 11× is against *sequential memory
agents*, not against a strong single agent.

**T4 — Harness evolution over model upgrade.**
Claim **199** (*Co-Evolving Harnesses and Models*): evolving the harness with
a weaker model substantially improves performance on enterprise tasks.
Adjacent: **320** (COBRA-Skills), **328/329** (skill routing as complementary
set selection, not relevance ranking), **397/399/400** (*The Router Within*:
a 32B model with native skill routing selects the right skill more often than
larger frontier models). *Why fourth:* strategically the most interesting
claim in the corpus for a skills business — it says the harness is the lever —
but it is currently **one claim from one paper**. It does **not** clear the
three-independent-sources bar and must not be packaged as a skill this week.
Flagged for the skill agent as a *watch*, not a target.

**Not a target: orchestration frameworks themselves.** Nothing in §1 is in
the corpus. Those are primary-source findings from this brief, which is why
§5 routes them to the digest rather than to skill extraction.

---

## 3. What the workflow-versus-agent evidence actually supports today

Plainly, as ordered.

**It supports a vocabulary, not a decision rule.** Two independent primary
sources (§1.1) define the workflow/agent split in near-identical terms and
share a five-pattern taxonomy. That convergence is real. But both state the
choice qualitatively and hand the decision back to the builder's own
measurements. **No source surveyed — framework documentation, specification,
or paper in our corpus — publishes a controlled comparison of the same task
built as a workflow versus as an agent.** Anyone claiming the boundary is
settled is overclaiming.

**Our corpus points both ways, and that is the finding.**

*For decomposition:* PACE (51) beats a monolithic model on conflict
detection; PARSER (291/294) gains accuracy *and* up to 11× latency on
long-context multi-hop QA; MaxKernel (6-9) matches expert hand-tuned TPU
kernels with a specialised sub-agent pool; Bilevel/SRMA (110) reaches 72.2%
on SWE-bench.

*Against, or limiting:* **Iris (claim 5) achieves the strongest reported
open-source search-agent scores with a single ReAct agent — no sub-agents, no
test-time verification.** Bilevel's margin is +1.4pp over a *mini*
reference. And Emergence World (386-389) documents failure modes that exist
*only because* the system is multi-agent: goal drift, coordinated refusal,
non-compositional alignment.

**The reconciling claim is 106**: the achievable coordination gain is bounded
by *task-decomposition quality*. That is the most defensible statement
available today, and it explains the split rather than papering over it —
multi-agent wins where the task genuinely decomposes and verification can be
made external, and adds cost plus novel failure modes where it does not.
Since decomposition quality is a property of the task, there is no universal
rule to be had, which is precisely why Anthropic's and LangGraph's guidance
stays qualitative.

**Evidence strength:** claim 106 is a single theoretical result from a single
paper. It is the best organising idea we have, **not** an established finding,
and should be presented that way.

**How orchestration quality is evaluated at all: it mostly isn't.** Every
benchmark in the corpus that touches agents — τ^τ-Bench, SWE-bench,
Terminal-Bench, OSWorld-v2, RealSWE, HarvestBench, SchemeArena — measures
**task success of a whole system**. None isolates the orchestration layer;
none lets you attribute a delta to a topology choice. *Emergence World* is
the nearest thing to an orchestration-quality evaluation we hold, and it
measures resilience under adversarial stress rather than comparing
topologies. **This is the most under-served question in the whole territory
and the strongest candidate for original work alexandria could do itself** —
we run a multi-seat orchestration daily and keep an incident register, which
the charter already names as citable primary data.

---

## 4. Source and watchlist proposals (the sources.yaml diff)

This is this week's **one system diff** (charter step 4 cap; ordered
explicitly by the dispatch). It is proposed, not accepted — the human merge
is the promotion.

Five additions, each a verified-200 primary technical feed, each closing a
named gap:

| Add | Tier | Why, with evidence |
|---|---|---|
| `gh-ag2` — `ag2ai/ag2` releases | `d` | §1.4: the AutoGen line's active development moved here (v1.0.1-v1.0.5, 2026-07-29→09-11) while our `gh-autogen` feed's latest is 2025-09-30. |
| `gh-openai-agents` — `openai/openai-agents-python` releases | `d` | Owner-named framework, entirely absent. Primary home of the **handoff** primitive (§1.3). Shipping actively (v0.22.3, 2026-09-17). |
| `gh-crewai` — `crewAIInc/crewAI` releases | `d` | Owner-named framework, entirely absent. Only source for the sequential-vs-hierarchical process contrast (§1.3). Active (1.15.22, 2026-09-16). |
| `gh-temporal` — `temporalio/temporal` releases | `d` | Owner-named durable execution. §1.2's pattern needs the pre-LLM durability lineage. Near-daily releases (2026-09-18). |
| `langchain-blog` — `blog.langchain.com/rss/` | `d` | The charter names "LangChain's engineering output." Our `langchain` feed is the marketing site; this is the engineering blog. |

`gh-autogen` is **retained, not removed** — it is the reference line and its
archive still matters; it is simply no longer where the work happens.

Deliberately **not** proposed, with reasons:

- **A `watchlist:` section** (authors/institutions). `sources.yaml` has no
  schema for it — that is `docs/product/source-discovery.md` §7 phase 2, a
  schema change that deserves its own review. More to the point, the signal
  that would populate it is not usable yet: institutions are extracted for
  only **33 of 111** distilled papers, and the top institution appears **3
  times**. Proposing a watchlist now would be fabricating a pattern.
- **A tier promotion for any existing feed.** The citation-velocity signal
  that would justify one **cannot be computed**: `citation_log` holds 68 rows
  for 68 distinct papers — **exactly one observation each** — and velocity
  needs two. Maximum citation count in the corpus is 1. The digest was right
  to say "No citation movers were recorded this week."
- **New arXiv categories.** `cs.MA` is already listed and has never been
  read (§0). Adding categories to a queue that never drains would be theatre.

**The honest caveat, restated:** per §0, these five feeds will land at the
back of a 3,057-item queue, and the 60-day backfill rule will stamp their
older releases `index` unread. **This diff delivers orchestration coverage
only if §7's throughput and routing defects are fixed.** I am proposing it
anyway because the feed list is the part within this seat's whitelist, and
because the diff is correct on its own terms — but it should not be merged
under the belief that coverage now exists.

---

## 5. What the next digest issue should carry from this territory

Ranked, all evidence-backed, all publishable under O1 KR3:

1. **"MCP made itself stateless — and handed durability to you."** The lead.
   The 2026-07-28 revision removed sessions, the initialize handshake, and
   SSE resumability, and moved long-running tasks to a polling extension
   (§1.2). It is *directly applicable systems and orchestration* — exactly the
   differentiation the charter names — it is dated, primary, and checkable,
   and it carries a real consequence for readers: if you relied on transport
   resumability, your agent runs are now your problem to checkpoint.

2. **"Durability moved up the stack."** The three-source pattern (§1.2):
   MCP sheds it, LangGraph ships checkpointers as separately versioned
   packages, OpenAI Agents SDK leads its session docs with resuming
   interrupted runs. One convergent direction, three independent primary
   sources. This is a *Trailblazing*-section item.

3. **"One agent still beats many, in search."** Iris (claim 5) against the
   decomposition results (§3). A genuine tension in current evidence,
   presented as a tension — the "judgment document, not a feed" posture
   vision §1 asks for. **Prerequisite:** claim 5 is currently marked
   deprecated by a false edge (§6) and that must be corrected before it is
   cited.

4. **Multi-agent failure modes** (Emergence World, 386-389) for *Read these
   yourself* — alignment is not compositional is a striking, useful result.

5. **Hold for a later issue:** the AG2/AutoGen activity shift (§1.4) is
   accurate but is ecosystem news, not a finding that changes how an agent is
   built. It belongs in the brief and in `sources.yaml`, not in an issue.

**Do not carry:** any framework capability claim sourced from a landing page,
and any orchestration "best practice" implying the workflow-vs-agent question
is settled (§3).

---

## 6. Digest quality review and claim-graph errors (charter step 1)

Digest reviewed: **2026-W37**, the only issue published (`digests` has 1 row,
created 2026-09-14).

**What it got right.** The *Trailblazing* items are accurately transcribed
from their claims, including the dense-verification-reward numbers
(49.4% → 64.0%, +28.5% relative) and the TITO/R³ log-probability gap
(0.021 → 0.013). It stated "No citation movers were recorded this week"
rather than inventing movement — correct, and §4 confirms movement was not
computable.

**The "Left behind" section is wrong in its entirety.** It rests on the four
`contradicts` edges in the graph, and **all four are false positives**.
Because `deprecated_claims` marks any claim targeted by a `contradicts` edge
at confidence ≥ 0.7, and all four edges score 0.78-0.90, **four claims are
currently and wrongly marked deprecated** (5, 11, 12, 129).

| Edge | Actual relation | Error |
|---|---|---|
| 82 → 5 (conf 0.78) | different domains (embodied VLA vs. search) | Two existence claims about different settings. Neither refutes the other. |
| **12 → 11 (conf 0.88)** | **same paper** | Both claims are from τ^τ-Bench's own abstract: 82.2% is the *human expert ceiling*, 23.9% is the *best model score*. That is the benchmark's headline gap, reported together by design. A paper cannot contradict itself. |
| 85 → 12 (conf 0.78) | different papers, different benchmarks | EmbodiedSkills' 12.5% on RMBench vs. τ^τ-Bench's 82.2%. Unrelated systems on unrelated benchmarks. |
| 136 → 129 (conf **0.90**) | unrelated | FEE training environments vs. which prompt fields help coding agents. No logical opposition — and this is the *highest-confidence* edge of the four. |

**Two errors reached subscribers.**

- **A published statement inverts its source paper.** The digest reads: "An
  earlier benchmark suggested that Claude Opus 5 could solve only 23.9% of
  simulations. A reference implementation now reaches 82.2%, showing the
  earlier ceiling was far too low." τ^τ-Bench says the opposite: 23.9% is
  what the best model scored, and 82.2% is the human ceiling it falls far
  short of. The paper reports *models lagging humans by 58 points*; the
  digest told readers models had improved. This is the most serious defect
  found this run.
- **A fabricated necessity claim.** The digest says skill selection plus
  verification is "required" for top performance. Claim 82 says such an
  interface "lets" these be combined — a capability claim. "Required" was
  manufactured to make a contradiction read as one.
- Also wrong, from edge 85 → 12: "The same reference implementation that
  achieved 82.2% was later shown to drop to 12.5%" — asserts an identity
  between two unrelated systems.

**Verdict: the digest's judgment layer is sound; its deprecation layer is
not and is currently a liability.** *Trailblazing* and *Gaining traction*
are trustworthy; *Left behind* — which vision §1 names as a core
differentiator — is 0-for-4 and published at least one meaning-inverting
statement. It should not run again until §7 is resolved.

---

## 7. Meta-review verdict

**This week's one system diff: the `sources.yaml` orchestration additions
(§4)**, ordered explicitly by the dispatch.

**Escalated, not proposed as a prompt diff this week — the `contradicts`
precision failure.** The evidence is a pattern by any standard (4 of 4 wrong,
100% false-positive rate, at confidences 0.78-0.90), and
`prompts/interpret.md` is inside this seat's whitelist. I am escalating
rather than shipping a prompt diff because **a prompt fix alone would not
fix this**: the four bad edges already exist in the database and would
continue to mark four claims deprecated and to feed *Left behind* no matter
what the prompt says next. The repair needs a data correction this seat
cannot make (read-only by charter, and rightly so). Shipping a prompt diff
would create the appearance of a fix without retracting a published error.

Recommended, for the owner and the engineer seat:

1. **Delete or downgrade the four `contradicts` edges** (from_claim 82, 12,
   85, 136). Restores claims 5, 11, 12, 129 — and claim 5 is needed for §5
   item 3.
2. **Then** sharpen `prompts/interpret.md` with the three tests that would
   have caught all four: (a) never label `contradicts` between two claims
   from the **same paper**; (b) results measured on **different benchmarks or
   task suites** are not in conflict; (c) two claims that each assert an
   approach *can work* do not contradict — that is a comparison. I will ship
   this as next week's diff, or sooner on request; the evidence is in §6 and
   verifiable with one query.
3. **Consider suppressing *Left behind*** in the next issue until (1) lands.

**Also found, logged for the ledger, not proposed this week:**

- **Throughput (the §0 defect).** Model triage: 210 papers in 11 days against
  300+/day arriving on recent days; 3,057 untriaged. Not a prompt problem — it is the Groq
  free-tier token cap meeting `BATCH * max_calls`. Needs an owner decision
  about budget or a cheaper first-pass filter.
- **Routing (the §0 defect).** Two rules jointly guarantee no orchestration
  artifact can ever produce a claim: `triage.py`'s tier ordering puts arXiv
  permanently last, and `triage.md` routes capability-adding releases to
  `index`, which is terminal. The charter says industry artifacts "qualify
  alongside papers when they carry real technical substance" — the prompt
  does not implement that. **This is the strongest *prompt* diff candidate
  after interpret.md**, and the MCP 2026-07-28 changelog is the worked
  example: a spec revision with nine major protocol changes, currently
  `index`-ed unread by rule.
- **Embedding gap.** 119 claims (all of 2026-09-17 and 2026-09-18) have no
  embedding, making them unsearchable and un-interpretable. Either a lag or a
  break on the 17th; worth an engineer check, since it hides the newest work.
- **Interpret backlog.** 323 of 504 claims (64%) never interpreted, spanning
  09-11 to 09-16. The claim graph describes roughly the first third of the
  corpus.
- **Topic vocabulary drift.** 37 off-vocabulary tag instances across 23
  distinct tags on 34 claims, against `prompts/distill.md`'s closed 13-tag
  list. **Nine of them use U+2011 (non-breaking hyphen) instead of ASCII
  `-`** — `post‑training`, `loop‑engineering`, `task‑refinement`,
  `anti‑hacking`, `data‑augmentation`. These are byte-distinct from the real
  tags (`706f7374e28091747261696e696e67` vs `706f73742d747261696e696e67`), so
  those claims drop silently out of every topic filter. A one-line
  normalisation in the pipeline is the right fix, not a prompt change;
  `distill.md` already states the vocabulary clearly.
- **`promotions` is empty (0 rows)**, so the charter's
  `select path from promotions` duplicate check is vacuous today. Noted so a
  future run does not read the empty result as "nothing proposed yet."

---

## Appendix A — reproducing every corpus number

```sql
-- §0: single-source corpus
select p.source, p.tier, count(distinct p.id), count(c.id)
from claims c join papers p on p.id = c.paper_id group by 1,2;

-- §0: untriaged backlog, arXiv vs rest
select case when source='arxiv' then 'arxiv' else 'other' end, count(*)
from triage_queue group by 1;

-- §0: model vs rule triage, and the gh-* dead end
select model, decision, count(*) from triage_log group by 1,2;
select p.source, t.model, t.decision, count(*)
from triage_log t join papers p on p.id=t.paper_id
where p.source like 'gh-%' group by 1,2,3;

-- §2: orchestration claim coverage
with ma as (select id from claims where 'multi-agent' = any(topics))
select (select count(*) from ma) total,
       (select count(*) from ma m join claims c on c.id=m.id
         where c.interpreted_at is not null) interpreted,
       (select count(distinct m.id) from ma m join claim_links l
         on l.from_claim=m.id or l.to_claim=m.id) with_edge;

-- §2/§7: embedding and interpret gaps
select count(*) filter (where embedding is null) null_emb,
       count(*) filter (where interpreted_at is null) not_interp from claims;

-- §4: citation velocity is not computable (one observation per paper)
select count(*) rows, count(distinct paper_id) papers, max(citations)
from citation_log;

-- §6: every contradicts edge, in full
select l.from_claim, l.to_claim, l.confidence, cf.paper_id, ct.paper_id
from claim_links l
join claims cf on cf.id=l.from_claim join claims ct on ct.id=l.to_claim
where l.relation='contradicts';

-- §7: U+2011 tags
select t, encode(convert_to(t,'UTF8'),'hex')
from claims, unnest(topics) t where t like '%'||chr(8209)||'%';
```

## Appendix B — primary sources used

All fetched 2026-09-19; every feed URL verified HTTP 200.

- MCP specification, revision 2026-07-28 changelog — `modelcontextprotocol/modelcontextprotocol`
- Anthropic, *Building Effective Agents* — anthropic.com/engineering/building-effective-agents
- LangChain, *Workflows and agents* and *Persistence* — docs.langchain.com
- LangGraph release feed — github.com/langchain-ai/langgraph/releases.atom
- OpenAI Agents SDK, *Sessions* and *Handoffs* — openai.github.io/openai-agents-python
- AG2, *Orchestrating agents* — docs.ag2.ai
- CrewAI, *Processes* — docs.crewai.com
- Temporal release feed — github.com/temporalio/temporal/releases.atom
- microsoft/autogen release feed — github.com/microsoft/autogen/releases.atom

No marketing page is cited as evidence for any capability claim.
