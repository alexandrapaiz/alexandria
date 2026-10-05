# Containment census, 2026-10-05

Owner directive 2026-10-05, containment only. Read-only corpus access through
`NEON_RO_URL` with `psql`; no writes to the corpus, no credentials printed.
External ground truth from the OpenAlex API, arXiv-scoped. This file is the
working; the brief at `docs/research/briefs/2026-10-05.md` is the deliverable.

## 0. The population, and how it was reconstructed

The directive's counts come from a predicate it does not print, so this run
rebuilt one from the directive's own five named areas and checked it against
the directive's numbers before drawing any conclusion. Precedent and method:
the 2026-09-30 three-thread census did the same.

The predicate, in words. Specific containment-mechanism terms are
unconditional (`sandbox`, `microvm`, `firecracker`, `gvisor`, `unikernel`,
`seccomp`, `syscall filter`, `namespace isolation`, `hypervisor`, `wasm`,
`webassembly`, `capability-based`, `object capability`, `capability token`,
`ambient authority`, `least privilege`, `confused deputy`), as are
`prompt injection` and `indirect injection`. Generic terms must co-occur with
an agent term: `isolation` with a runtime word, and
`preempt|kill switch|interruptib|revoke|revocation`, and
`escape|breakout|privilege escalation`. The SQL is reproduced in section 7.

Deliberately excluded, against the directive's wording: `guardrail`,
`jailbreak` and `exfiltrat`. Those were the 2026-09-30 census's `security`
thread. Including them adds 52 papers and 20 claims and shifts the thread from
the boundary to the attack, which is the distinction section 5's topic
definitions turn on.

| measure | directive | reconstructed | delta |
|---|---|---|---|
| papers matching containment terms | 273 | 230 | -43 |
| never triaged | 79 | 54 | -25 |
| indexed | 69 | 64 | **-5** |
| routed to distill | 68 | 91 | +23 |
| read in full | 16 | 9 | -7 |
| claims | 71 | 99 | +28 |

The one number the re-judgment depends on, the indexed count, matches within
five. The rest do not, and the reason is visible in the last two rows: this
predicate admits more already-distilled papers than the directive's did. The
conclusions below do not rest on the 43-paper delta - they rest on the field
diff in section 1 and the backlog in section 2, both measured independently.

**One term in the directive does not mean what the corpus column means.**
"16 read in full" is `fulltext_chars > 0`. That column is populated for only
127 of the 393 papers that have actually been distilled, so it understates
reading by about three times. Papers with claims and no stored fulltext are
the larger group (266). Where this file says "read", it means "has claims".

## 1. The 30-day census against the field

Method, the one ADR-29 mandates. The arXiv API itself was unreachable from
this runner (`export.arxiv.org` returned no response across four retries;
`arxiv.org/api/query` returned 429 then 503), so ground truth is the
**OpenAlex API**, filtered to arXiv as primary location
(`primary_location.source.id:S4306400194`) and to
`from_publication_date:2026-09-05, to_publication_date:2026-10-05`. Each of
the directive's five areas was queried as a set of phrases, results unioned,
arXiv ids extracted from landing-page URLs, and diffed against `papers` with a
version-insensitive match.

| | papers |
|---|---|
| arXiv papers in the window across the five areas | **301** |
| held in `papers` | **125 (42%)** |
| not held | 176 (58%) |
| of the 176, on-thread by this seat's judgment | **40** |
| of the 176, relevance-search noise | 136 |

Of the 125 held, by latest triage decision: 83 `distill`, 19 `index`, 17 never
triaged, 3 `discard`, 3 `deep_read`. **23 of the 125 have produced any claim.**

So the reach gap is real but it is the smaller half. We hold 125 in-window
containment papers and have extracted from 23. Ingesting the 40 missed papers
would roughly triple the queue in front of a stage that is not draining.

**The version-insensitive match matters and is not a detail.** `papers` holds
arXiv ids in two shapes, and a naive `id = 'arxiv:' || aid` join reports five
of the containment skill's six papers as absent when five are held. This run
made that error on its first query and corrected it; section 3 is the defect
behind it.

The 40 on-thread missed papers are listed, with dates and links, in
`docs/research/reading-queue.md` under "Containment batch, 2026-10-05".

## 2. The finding that reframes the directive: distill is not running

The directive's mechanism is that containment papers are indexed as "not a
construction technique" and that distill's topic list cannot hold them. Both
are true and both are second-order. The dominant cause is throughput.

| measure | count |
|---|---|
| papers routed to `distill` or `deep_read`, corpus-wide | 1,585 |
| of those, zero claims | **1,192 (75.2%)** |
| of those 1,192, fulltext fetched | **0** |
| `distill_queue` depth | **1,189** |

Every one of the 1,192 has no fulltext and no claims, which means distill did
not run on them rather than ran and found nothing. Throughput, by week of
claims written: 200 papers (w/c 2026-09-28), 49, 64, 62, and 18 so far this
week. At the best observed week the backlog is six weeks of work; at the
median it is over twenty.

That is the whole containment story in one number. Triage routes containment
papers to distill at a high rate - 83 of the 125 in-window papers we hold -
and 1,189 papers are waiting for a stage that has not reached them. The
missing topic tag (section 5) is why nobody can *find* the containment claims
that do exist. The backlog is why most of them do not exist.

The interpret stage is behind the same way: `interpret_queue` holds **785**,
and **1,012 of 1,801 claims (56%) have `interpreted_at` null**. Every
containment claim filed in the last fortnight - CounterSteer, Approval
Laundering, Covert Assistance - therefore has zero graph edges, which is why a
claim-graph query on containment returns nothing while the claims sit there.

## 3. A correctness defect: one arXiv paper, two rows, two verdicts

`papers` holds arXiv ids both with and without the version suffix, because two
sources write them differently:

- source `arxiv` (tier `a` / `a-low`) writes `arxiv:2610.02206v1`
- source `hf-daily` (tier `b`) writes `arxiv:2610.02206`

Measured consequences:

| measure | count |
|---|---|
| base arXiv ids present under more than one row | **322** |
| `papers` rows involved | 656 |
| duplicate pairs triaged twice **with different decisions** | **73** |
| duplicate rows fetched in w/c 2026-09-28 alone | 228 |

Worked example, both rows live tonight:

| id | source | tier | decision | score |
|---|---|---|---|---|
| `arxiv:2610.02206` | hf-daily | b | `index` | 0.71 |
| `arxiv:2610.02206v1` | arxiv | a | `distill` | 0.76 |

Same paper (KaliBench), two triage runs, opposite routes, and the tier that
decides the score nudge is set by whichever feed arrived. 73 papers are in
that state. This corrupts every count this seat produces, spends triage budget
twice on one paper, and splits claims across two paper ids.

This is `pipeline/ingest.py`, not a file in the ADR-12 whitelist, so it is
routed to the engineer rather than proposed. The fix is id normalisation at
ingest - canonicalise the version suffix one way before insert - plus a
backfill that merges the 322 pairs and keeps the better tier.

The blog side of the same defect is **already fixed**: 1,172 documents are
duplicated between sources `blog` and `openai-blog` and 98 between `blog` and
`deepmind-blog`, but `sources.yaml` removed both feeds on 2026-09-19 and its
own comment records why. `openai-blog` was last fetched 2026-09-23 and `blog`
on 2026-09-07, so that pair is historical and needs a dedupe, not a config
change. One live pair remains and is small: `raschka-blog` and
`raschka-ahead-of-ai` overlap on 21 documents, both fetched through 2026-09-30.
Those are genuinely two feeds for one author with partial cross-posting, and
this run does not propose removing either.

## 4. Re-judging the indexed containment papers (deliverable 2)

64 papers carry `index` as their latest decision under the section 0
predicate. First, what those 64 rows are:

| how the decision was made | rows |
|---|---|
| judged by a model (`kimi-k2.6`, `gpt-oss-120b`) | 35 |
| `rule:backfill` - auto-indexed, never judged | **29** |

So "re-judge the 69 indexed papers" is two different jobs. 29 of them have
never been judged by anything; the string in `triage_log.reasoning` is
`backfill: predates pipeline, auto-indexed by rule`.

### 4a. Move to distill - 9 documents, 13 rows

The duplicate defect in section 3 is why the row count is higher than the
document count: five of these nine are the same OpenAI essays ingested twice.

| id(s) | title | why it moves |
|---|---|---|
| `blog:openai:3dec299964e674ad`, `blog:openai-blog:3dec299964e674ad` | Designing AI agents to resist prompt injection | Never judged. An engineering essay on injection-resistant harness design is the charter's "artifact with method" exactly; area 5. |
| `blog:openai:66be1220771465af`, `blog:openai-blog:66be1220771465af` | Running Codex safely at OpenAI | Never judged. Production containment practice at scale; area 4. |
| `blog:openai:4a3442a5ca8c1935`, `blog:openai-blog:4a3442a5ca8c1935` | Building a safe, effective sandbox to enable Codex on Windows | Never judged. Sandbox design with a stated threat model; areas 1 and 4. |
| `blog:openai:18b7ee4fe5e46ca1`, `blog:openai-blog:18b7ee4fe5e46ca1` | Improving instruction hierarchy in frontier LLMs | Never judged. Instruction hierarchy is a containment primitive, not a capability result; area 5. |
| `blog:openai-blog:0d2abbb0fa62c353` | Keeping your data safe when an AI agent clicks a link | Never judged. Injection-to-exfiltration chain; area 5. |
| `arxiv:2609.36817v1` | pikit: A Composable Toolkit for Indirect Prompt Injection Research and Evaluation | Judged 0.52, declined for "no novel technique". The charter names **containment evaluation** as part of the priority: how you test that an agent cannot reach what it must not. Evaluation infrastructure is in scope here even when it is not a new defence. |
| `blog:hn-frontpage:db811de4e7247bea` | 5x faster Edge Functions: V8 isolates to Firecracker MicroVMs | Judged 0.68, declined because "edge functions is not agent runtimes". Area 1 is isolation designs **with a measured escape or cost**. This is the isolate-versus-microVM cost, measured, which is the question the skill's section on choosing a boundary cannot currently answer with a number. |
| `arxiv:2609.37737v1` | Where Do LLMs Decide to Break the Rules? Mechanistic Localization of Prompt Injection Compliance | Judged 0.68, declined for ending "without an actionable intervention". Causal activation patching that localises injection compliance is a mechanism with a measurement, and CounterSteer (held, 5 claims) is the intervention built on exactly that localisation. The pair is the finding. |
| `arxiv:2609.39631v1` | Kirin: Cloud-native WebAssembly Service Orchestration | Judged 0.50, declined as not agent-specific. Wasm isolation evaluated against containers is the same containment-cost question as the Firecracker item. Lowest priority of the nine. |

### 4b. Second tier - defensible either way, flagged not moved

- `blog:hn-frontpage:5b99ba2e157ec4e5` CVE-2025-13032, Avast sandbox escape part 2. The triage reasoning is the best in the whole sample and correctly says wrong domain with no agent metrics. Against it: this is a measured escape with its preconditions, and area 1 asks for those. Moves only if the engineer wants escape mechanics regardless of domain.
- `arxiv:2609.39866v1` Preemptive LLM Unlearning against Forbidden Capability Acquisition via Gradient Sealing. Containment at the weights rather than the boundary. In scope only if "containment" covers denying a capability as well as denying an action; section 5's definition deliberately does not.

### 4c. The 55 that stay indexed, and the one pattern in them

The rest are correctly indexed and the judgments read well. The benchmarks
without a mechanism (AgentWorld, CheatBench, ExplorationBench, RoboFollow,
BVB, RiskChainBench) are declined on a rule the owner set, and the rule is
being applied consistently. The serving papers (Flash-dLLM, tree-structured
speculative decoding, KREX), the product releases (six Claude Code versions,
EmDash, Whiteboard, Deep Life Sci), and the off-domain items (VST XR,
EdgeCraft, Compliant AI Infrastructure for Regulated Finance) are all right
where they belong.

One pattern is worth the prompt change in section 6. Across 4a, the model's
stated reason for declining a containment artifact is one of two things:
**wrong domain** when a measured isolation cost comes from outside agent
infrastructure, or **no novel technique** when the artifact is evaluation
infrastructure rather than a defence. Both are good general rules and both are
wrong for this named priority. That is 3 of the 35 model-judged rows, which is
thin on its own; what makes it a pattern rather than an anecdote is that the
same two reasons appear in the 2026-09-30 census's sample on the same thread,
and that the owner has now named containment a standing priority twice.

## 5. Topic definitions for the closed list (deliverable 4)

The directive asks for `containment` plus the three siblings "if your earlier
census already wrote them". It did: `protocols`, `containment` and `security`
are in `docs/research/notes/2026-09-30-protocols-containment-security-census.md`
section 5, and `self-improvement` is in `docs/ideas.md` under its 2026-09-30
entry. They are reproduced in the brief, with `containment` revised by this
run's evidence. The change to `containment` is one sentence: the earlier draft
sent "a claim about an agent's runtime performance inside a boundary" to
`systems`, and the Firecracker and Kirin items in 4a show that the *cost of
the boundary itself* has to stay here or the measured-cost half of the owner's
area 1 has nowhere to land.

**The blocker that applied on 2026-09-30 is gone, and a new one replaces it.**
That entry filed the `self-improvement` text in `docs/ideas.md` rather than
proposing it, because `prompts/distill.md` was measurably not running. It is
running now: HEAD `819694a98603` equals the sha on 955 claims, the newest
written 2026-10-05. So these definitions can reach production this week.

What replaces it is narrower and absolute. `pipeline/topics.py` now enforces
the closed list - 0 of the claims written at the current distill sha carry an
off-list tag, against 64 historically - and its own docstring says the prompt
list and `TOPICS` "must agree exactly". So a `containment` tag added to
`prompts/distill.md` alone would be **dropped on every claim**, silently. The
change is atomic across three files or it is worse than nothing:

1. `prompts/distill.md` - the tag in the topics list and the rubric block.
2. `pipeline/topics.py` - `"containment"` in `TOPICS`.
3. `tests/test_reasoning_rubric.py` - parses the prompt and fails on drift, so
   it has to see the new tag.

And a fourth, separately: 64 legacy claims carry off-list tags, 13 of them a
U+2011 twin of `post-training`. Those predate the fold and it will never
rewrite them. They need a backfill.

## 6. The week's one system diff

`prompts/triage.md`, a containment routing block, on the evidence of 4a and
4c. Deploy check per the charter, before spending the proposal:

| prompt | HEAD sha | deployed sha | current? |
|---|---|---|---|
| `prompts/triage.md` | `32252384ecd7` | `32252384ecd7` (5,238 rows, latest 2026-10-04) | **yes** |
| `prompts/distill.md` | `819694a98603` | `819694a98603` (955 claims, latest 2026-10-05) | **yes** |
| `prompts/interpret.md` | `6706ec7bffee` | `kimi-k2.6@6706ec7bffee` (526 links, latest 2026-10-04) | **yes** |
| `prompts/digest.md` | `c48d09624161` | `c48d09624161` (W40 rehearsal, 2026-10-05 03:36) | **yes** |

All four are current. The stale-image condition that blocked incident 25 and
the runs of 2026-09-24 and 2026-09-30 is **cleared**, and that is the most
useful operational fact in this file: proposals into these files reach
production again. Note that `digests.prompt_sha` still reads `ea2d678d86e9`
from the W39 publish, so checking the press against the `digests` table alone
reports a false stale. The rehearsal row is the current evidence.

## 7. Reproducing this

The containment predicate, as used in every count above:

```sql
with t as (
  select p.*, lower(p.title || ' ' || coalesce(p.abstract,'')) as txt from papers p
), cont as (
select * from t where
  txt ~ '(sandbox|microvm|micro-vm|firecracker|gvisor|unikernel|seccomp|syscall filter|namespace isolation|hypervisor|wasm|webassembly|capability-based|object capability|capability token|ambient authority|least privilege|least-privilege|confused deputy)'
  or txt ~ '(prompt injection|indirect injection)'
  or (txt ~ '(isolation|isolated execution|isolating)'
      and txt ~ '(process|runtime|execution|privilege|container|virtual machine|kernel|untrusted|tenant|boundary)'
      and txt ~ '(agent|agentic|llm|language model)')
  or (txt ~ '(preempt|kill switch|killswitch|interruptib|revoke|revocation)'
      and txt ~ '(agent|agentic|llm|language model)')
  or (txt ~ '(escape|breakout|privilege escalation)'
      and txt ~ '(agent|agentic|llm|language model)')
)
select count(*) from cont;
```

The three defect counts, each one query:

```sql
-- 322 duplicated arXiv papers, 73 with divergent decisions
with b as (select id, regexp_replace(id,'v[0-9]+$','') base from papers where id like 'arxiv:%'),
     d as (select base from b group by base having count(*)>1),
     lt as (select distinct on (paper_id) paper_id, decision from triage_log order by paper_id, created_at desc)
select count(*) from (select base from b join d using(base) join lt on lt.paper_id=b.id
                      group by base having count(distinct lt.decision)>1) x;

-- 1,189 papers waiting on distill
select count(*) from distill_queue;

-- 5 contradicts edges between two claims of one paper
select l.from_claim, l.to_claim, a.paper_id
from claim_links l join claims a on a.id=l.from_claim join claims b on b.id=l.to_claim
where l.relation='contradicts' and a.paper_id=b.paper_id;
```

The external census is `OpenAlex /works`, five area query sets, filtered to
`primary_location.source.id:S4306400194` and the 30-day window. The scripts
this run used are not committed; the queries above and the area phrases in
section 1 are enough to rebuild it.
