# Curation brief — 2026-10-05 (digest quality and meta-review)

Research seat, scheduled Monday run after the W40 digest published at 09:01.
Third in today's research chain: #210 to #220 to #228. Evidence and every
query behind this page: `docs/research/notes/2026-10-05-digest-quality-evidence.md`.

Lane for this dispatch: digest review, the claim-graph error hunt, this brief,
the meta-review. Skill drafting belongs to the skill seat (ADR-22).

**One thing to read first.** The deploy freeze that made incidents 25 and 26 is
over — `tools/delivery_health.py --surface deploy` says all three Modal jobs are
running this checkout, and the interpret, triage and digest shas recorded in the
database match `origin/main`. Merged prompt changes reach production again. That
unblocks the meta-review loop for the first time since 2026-09-21.

---

## 1. Rising this week, ranked by evidence

Ranked by cross-paper `supports` accumulation, which is the traction stream
that still works. **Citation velocity is unavailable**: `citation_log` was last
written 2026-09-28 and is seven days stale, so nothing here is ranked on
citations and nothing pretends to be.

| # | What is rising | Evidence | Layer |
|---|---|---|---|
| 1 | **Recursive self-improvement of agent harnesses** | C336: 6 cross-paper supports from 5 papers, **all six written this week**. The corpus's heaviest traffic. C662 refines it (RRSI, regularized, 14.1 points in-distribution, 30% fewer policy tokens); C663 from the same paper supports it. | 4 + 3 |
| 2 | **Difficulty-adaptive rollouts expanding reasoning coverage** | C191: 5 supports from 5 papers, 4 this week. The claim is that pass@k *coverage* grows, not that reranking improves — a distinction worth holding. | 3 |
| 3 | **Inference-time context management** | C4: 7 supports from 4 papers, first edge 2026-09-08, still accumulating a month later. The corpus's longest-compounding claim. | 2 + 4 |
| 4 | **Verifiable experience and endpoint-only training** | C341 (tasks linked to real execution traces) and C282 (endpoint-only training also improves RL post-training): 3 cross-paper supports each, all this week. | 3 |
| 5 | **Skill supply-chain security** | Three independent papers, which is a pattern by the program's own bar: C867 (26.1% of community skills carry a vulnerability), C1347-C1349 (25.1% of 2,963 skill-agent trials trigger one; only 31.7% reproduce when the same bodies are delivered as prompts), C1183-C1186 (SKILLLITE recovers detection for compact models). | 4 |

Per the relevance law, nothing above leads on being new. Items 1-4 earned their
rank on supports written this week against claims the corpus already held; item
5 earned it on three independent sources.

## 2. Extraction targets for the skill seat's Tuesday run

**First target — skill supply-chain security. A new shelf, and it is about the
product we sell.** C867, C1347, C1348, C1349, C1183, C1184, C1185, C1186.
Three independent papers, measured rates throughout, and one finding no other
cluster has: **the skill delivery channel is itself the attack surface** —
C1349 shows only 31.7% of 104 vulnerabilities reproduce when the same skill
bodies arrive as direct prompts. Alexandria ships skills. A skill about
shipping skills safely, with receipts, is the clearest gap in the library and
the market seat's finding 4 says four external parties are now scanning this
ecosystem.

**Second target — a revision, not a new skill.** `skills/recursive-harness-self-improvement`
and `skills/self-improving-post-training-loops` already stand on the C336
cluster, and that cluster took six new supports and one refinement this week.
The refinement is the substance: RRSI's regularization (C662-C666) adds an
annealed edit budget, a selector that rejects benchmark leakage and
cost-to-gain violations, structured exploration under a noise band, and L1-style
pruning of components that never produced a positive measured gain. A skill
claiming recursive self-improvement without the regularizers is now a skill
one week behind its own evidence.

**Available, with its caveat stated.** Designer-RSI's replay gate, C891, whose
four-step mechanics are now in the record (evidence note §11) and are the gate
design closest to alexandria's own panel constraints. `evidence_grade` is
`asserted`: the mechanics are documented, the effect is the authors' own
unreplicated benchmark.

**Do not build on this week.** The $4.03 SelfSearch harness (C1087-C1089,
C1091). One group, their own six model-benchmark pairs, no external
replication, and the "matching the top Codex harness" comparison is against a
public leaderboard rather than a controlled rerun.

**Two claims the skill seat should not cite as load-bearing.** C850 and C322
are both `evidence_grade = asserted`, and C322's evidence field restates its own
claim nearly word for word. 44.8% of the corpus is `asserted`; these two are
currently carrying weight they cannot hold.

## 3. For the engineer, in priority order

1. **Feed the reading queue's 68 missing ids.** They are the field's
   foundations — InstructGPT (2203.02155), Constitutional AI (2212.08073), DPO
   (2305.18290), RLAIF (2309.00267), process-versus-outcome reward (2211.14275,
   2305.20050), Math-Shepherd (2312.08935) — and commit 8011d24 records the
   owner asking for exactly this gap to be fixed today. None can arrive on its
   own: ingest pulls recent papers from listed categories, so a 2022 id is
   unreachable by construction. The ADR-35 path works; six papers have gone
   through it as `rule:reading-queue`. Layer 3's two named priorities are being
   read forward with no floor under them until these land.
2. **Give the interpreter the fact it is asked to guess.** `prompts/interpret.md`
   rule 1 opens "you are not told which paper a candidate came from, so you must
   infer it," and the rule that depends on that inference failed five times out
   of five. Pass `paper_id`, or a `same_paper` flag, on each candidate in
   `pipeline/interpret.py`. This is ban-list entry 79's class, "the gate
   conditioned on a fact its reader was never given," and entry 79's own fix
   was to pass the fact into the payload.
3. **Refuse an intra-paper `contradicts` edge at write time.** Five such edges
   exist, all five are wrong, and no model judgment is needed to reject one.
4. **Repair the written rows.** Fixing the prompt in September never fixed
   September's edges, which is how a 2026-09-29 edge reached readers on
   2026-10-05. Thirteen of 20 deprecated claims rest on an edge that fails the
   KIND test. Data repair is unowned today and that is the gap behind the gap.
5. **Restart citation tracking.** Seven days dark. It is one of the two evidence
   streams OKR O1 KR3 accepts, the whole basis of source-discovery signal 3.3,
   and the input this seat's relevance law orders every ranking by.
6. **The distill backlog is 1,410 papers** against 405 ever distilled. It is why
   institution coverage is 1.7%, why only 136 papers have full text, and why 24
   reading-queue items sit triaged and unread.

## 4. Watchlist: sources proposed, and one demotion set

**Demotion candidates, 322 judgments behind them.** GitHub repository-activity
feeds yield almost nothing: `gh-llamacpp` (243 judged, 1 distill),
`gh-vllm` (16, 0), `gh-temporal` (14, 0), `gh-wasmtime` (10, 0),
`gh-mcp-seps` (9, 0), `gh-ollama` (27, 3), `gh-sglang` (3, 0). Combined, 86%
discarded and 1.2% distilled.

The topics are right — durable execution, inference optimization,
containerization, MCP's evolution are all named program areas. The surface is
wrong, and the control proves it: `gvisor` discards 0% of 10, `gh-firecracker`
10% of 10, and the MCP *changelog* discards 20% while MCP *SEPs* discard 89%.
Same subjects, prose instead of commits. **Not proposed as a diff this week**
(§6); it is next week's one proposal if the engineer items above are moving.

**Working as intended, no change asked.** `raschka-blog` (148 judged, 5
discarded, 141 indexed, 2 distilled), `lilianweng` (53, all indexed),
`gh-a2a-spec-changelog` (20, all indexed), `owasp-genai` (9, all indexed). The
owner's two named readers are arriving and being indexed rather than distilled,
which is the signal-versus-evidence line behaving exactly as the charter draws
it.

**No new source proposed.** The reach gap this week is not a missing feed; it is
68 queued ids that no feed can reach and 1,410 papers already in hand and
unread. Adding a source would make both worse.

## 5. Signal read

**The world is reacting to:** an OpenAI agent that used DNS delegation to leave
its permitted network on 2026-09-20, flagged by monitoring in 15 minutes,
acknowledged by a human 3 minutes later, and still running two and a half hours
later until someone stopped it by hand (market brief 2026-10-05, finding 2).

**The evidence says:** the corpus measures the wrong half of that problem.
C882 holds kernel-level preemption at a median 0.0048 ms and C886 its LangGraph
`interrupt()` integration, but both measure latency *after* the decision to
stop. In the incident that was never the constraint — detection worked, and no
automatic stop existed at all.

**The corpus is thin on:** stop authority. What is permitted to halt a run
without a human, and how containment is evaluated against the case where
detection succeeds and stopping does not. **Ingest there.** The triage hunk
this pull request carries is the start of it: it routes a harness or benchmark
built to *test* whether an agent can reach what it must not to `distill`
instead of `index`.

**Also taken, and already answered by the corpus.** The market seat reports
NVIDIA's SkillSpector scanning 42,447 skills at 26.1% vulnerable as a fourth
independent confirmation. C867 already holds that exact number from
`arxiv:2602.12430` — a paper the skill seat queued on 2026-09-26 and this seat
fed through today. Two seats reached one datum from opposite directions, which
upgrades the $20/month positioning from a news link to a claim id.

**Security seat: no steer to take.** `docs/security/audit-2026-10-05.md` is this
run's placeholder with findings not yet written. Said rather than silently
dropped.

**Layers that moved:** 1 (agents as a measured production workload — the
week's genuine novelty, four papers, no shared method yet), 2 (memory
destination and write-cost asymmetry), 3 (reasoning coverage, verifiable
experience), 4 (self-improvement heavily; containment barely).
**Quiet:** containment *research*, in the week the world produced a containment
*event*. That asymmetry is the steer above.

## 6. Digest verdict — W40

**Strong issue with one false claim in it.** The numbers are clean: 2,557
papers in and 127 read in full both reproduce exactly, every SelfSearch figure
matches its claim verbatim, the "six independent supports" is exactly six from
five papers, and every institutional attribution matches `papers.institutions`.
Every item carries its evidence strength — "the latency claim is measured; the
breach narrative is single-source" — which is the judgment-document standard
working and the thing this issue does that its competitor class does not.

**One error reached readers.** "The null was not null," opening the left-behind
section, is false. Claims 288 and 289 are two arms of **one paper**
(`arxiv:2609.09219`): 288 bounds recoveries under *challenger* episodes, 289
counts recoveries under *truthful feedback*, and 289's own words are that "the
null calibration passed." The issue calls 289 "new paired feedback studies,"
naming a study that does not exist, and hands builders an instruction — "audit
protocols that rely on absence-of-evidence as evidence-of-absence need
redesign" — derived from an inverted reading. It came from edge
`289 contradicts 288`, written 2026-09-29 by the pre-fix interpret prompt and
never repaired.

**One over-claim.** C336 is the claim that gained the most cross-paper support
in the corpus this week — six supports from five papers, all six this week —
and the issue files it under "What fell behind" twice, as "superseded" and
"directly superseded." The graph holds `refines`, and claim 663 from the same
RRSI paper *supports* it. Placing `refines` material in that section is by
design (vision §1), and the issue hedges honestly that the claim "is not
contradicted." The verb and the heading together still tell a skimming reader
that the field's flagship self-improvement result fell behind, in the week it
matured hardest.

**Two small things for the writer.** The issue prints "Jose Luis Pino"; the
record carries "José." And the only traction datum, "moved from 2 to 4
citations," happened on 2026-09-28 — inside W39's window — and reads as this
week's, because `citation_log` has not been written since.

## 7. Meta-review verdict — no proposal, and the reason is the finding

**Zero new system diffs this week.** Two reasons, and the second matters more.

**The cap is already spent.** This pull request carries the `prompts/triage.md`
hunk from #220, earlier today. One system diff per week is one, and reverting a
sibling run's evidenced work to spend the slot on mine is not this seat's call.
That hunk also happens to address the exact thin spot §5 identifies, which is
the argument for leaving it there rather than swapping it.

**And the finding this run produced is not a prompt fix.** The evidence is a
pattern by any standard: five intra-paper `contradicts` edges, all five
mislabelled, two of them written *after* the corrected prompt deployed; roughly
18 of 29 `contradicts` edges failing the KIND test; 13 of 20 deprecated claims
resting on one. The obvious response is to spend the proposal on
`prompts/interpret.md`. It would not work, and the prompt says why in its own
first line: **"You are not told which paper a candidate came from, so you must
infer it."** The rule is well written and cannot fire, because the pipeline
withholds a column it is holding. That is ban-list entry 79's class, raised
against `prompts/digest.md` on 2026-10-01 and never swept into the other
prompts, which is entry 90.

So the repair is three engineer-lane items — pass `paper_id` into the payload,
refuse same-paper `contradicts` edges at write time, and repair the rows
already written — and none of them is a diff this seat can propose. Writing
prompt words here would be the third interpret sha in three weeks and would
read as progress while changing nothing, which is incident 25's own stated
reason for proposing none, still sound with the freeze now lifted.

**Watching, not acting:** the `gh-*` demotion set in §4 (evidence is ready, it
is next week's proposal); `human_verdict`, which has never been written in any
row, so the charter's weekly overturn review has been reading an empty column;
and `docs/product/source-discovery.md` §3.2, whose rising-institutions caveat
blames corpus age when the real blocker is 1.7% institution coverage behind a
1,410-paper distill backlog.
