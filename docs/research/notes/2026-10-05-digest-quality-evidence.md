# Evidence note — 2026-10-05 digest quality and meta-review run

Working note behind `docs/research/briefs/2026-10-05-digest-quality.md` and
pull request #228. Every finding below is one query a reviewer can paste.
`NEON_RO_URL` was set; the corpus was read read-only with psql.

Scope of this run, per the dispatch: digest quality review, claim-graph error
hunt, the curation brief, and the meta-review. Skill drafting is the skill
seat's (ADR-22) and was skipped.

---

## 1. The deploy freeze is over, and that is the week's most important fact

Incidents 25 and 26 recorded that every file ADR-12 lets this seat propose
into was frozen behind an undeployed Modal image, which made the whole
meta-review loop write-only. That is no longer true.

```bash
python3 tools/delivery_health.py --surface deploy --no-notify
#   ok       deploy    all 3 jobs are running this checkout
```

Confirmed independently against the three recorded shas:

| prompt | sha at `origin/main` | sha production recorded | source of truth |
|---|---|---|---|
| `interpret.md` | `6706ec7bffee` | `6706ec7bffee` (last edge 2026-10-05 14:33) | `claim_links.method` |
| `triage.md` | `32252384ecd7` | `32252384ecd7` (last run 2026-10-05 12:48) | `triage_log.prompt_sha` |
| `digest.md` | `c48d09624161` | `c48d09624161` (2026-W40) | `digests.prompt_sha` |

```sql
select method, count(*), max(created_at) from claim_links group by 1 order by 2 desc;
select prompt_sha, count(*), max(created_at) from triage_log group by 1 order by 3 desc nulls last;
select week, prompt_sha, created_at from digests order by created_at desc;
```

The consequence for this seat is direct: a proposal into an image-baked file
reaches production again. The charter's instruction to spend no proposal on a
stale file no longer blocks anything.

---

## 2. The W40 digest printed a false overturn, and the edge behind it is one
   incident 25 already named

The issue's "What fell behind" section opens:

> Start with the number that turned out to be wrong. A prior claim held that
> zero recoveries in 96 challenger episodes yielded a finite-sample upper bound
> of 0.0468 on recovery probability. New paired feedback studies show 30
> truthful recoveries and zero neutral ones, with 60 paired null studies passing
> calibration. The null was not null. The practical consequence: audit protocols
> that rely on absence-of-evidence as evidence-of-absence need redesign.

```sql
select id, paper_id, claim from claims where id in (288, 289);
select from_claim, relation, to_claim, confidence, method, created_at
  from claim_links where from_claim in (288,289) or to_claim in (288,289);
```

Both claims are from **one paper**, `arxiv:2609.09219`, *Scores Alone Do Not
Prove Discovery: The Discovery Certification Protocol for Auditing AI Research
Agents*. Three things are wrong downstream of that:

1. **"New paired feedback studies" names a study that does not exist.** Claim
   289 opens "In the paired feedback studies" — it is a second arm of the same
   paper, distilled in the same batch. Nothing newer overturned anything.
2. **The two arms do not conflict.** 288 bounds recovery probability under
   *challenger* episodes; 289 counts recoveries under *truthful feedback*.
   Finding recoveries when you feed an auditor true information does not refute
   a bound on recoveries when you challenge it. The paper reports both to show
   its protocol discriminates between the two conditions, which is the protocol
   working.
3. **"The null was not null" inverts the claim it cites.** Claim 289's own words
   are that "the null calibration passed with 60 paired null studies." The null
   held.

The edge that produced it is `289 contradicts 288` at confidence 0.75, written
2026-09-29 by `openai/gpt-oss-120b@fbe080261d6b` — the *pre-fix* interpret
prompt. `deprecated_claims` is defined as any claim with an incoming
`contradicts` edge at confidence >= 0.7, so that single edge put claim 288 into
the digest's `deprecated` payload, where the press picked it up.

This is the class incident 25 recorded on 2026-09-21, specimen and all. Its
worked example was the 82.2%/12.5% pair. That pair is still in the graph:

```sql
select l.from_claim, l.to_claim, l.confidence from claim_links l where (from_claim,to_claim)=(85,12);
--  85 | 12 | 0.78
```

## 3. The error class, counted

```sql
-- intra-paper contradicts edges: a paper contradicting itself
select l.from_claim, l.to_claim, cf.paper_id, l.confidence, l.method, l.created_at::date
from claim_links l
join claims cf on cf.id=l.from_claim
join claims ct on ct.id=l.to_claim
where l.relation='contradicts' and cf.paper_id=ct.paper_id
order by l.created_at;
```

Five edges, and reading all five pairs, **all five are mislabelled**:

| edge | paper | what the pair actually is |
|---|---|---|
| 12 → 11 | τ^τ-Bench | 82.2% expert ceiling beside a 23.9% agent score — the paper stating its own headroom |
| 190 → 188 | Show-Harness | the paper's conclusion beside its own method result |
| 289 → 288 | Discovery Certification | two experimental arms, agreeing (§2 above) |
| 478 → 477 | ImpossibleRubrics | an exploitation-rate table beside a cross-Oracle consistency check — two different measurements |
| 574 → 570 | Fathom | a headline speedup beside the scope limit that bounds it |

Two of those, `478 → 477` (2026-10-01) and `574 → 570` (2026-10-02), were
written **after** the corrected prompt deployed, by the corrected prompt.

Reading all 24 cross-paper `contradicts` edges against the KIND test that
`prompts/digest.md` states ("ask whether the two claims measure the same
thing"), a further 13 fail it. The flagrant ones:

- `136 → 129` at confidence **0.9**, the graph's highest: "Feedback-Enriched
  Environments improve self-evolving agents on SciWorld and BFCL" against
  "adding Desired Behavior and Motivation to prompts improves coding-agent
  performance, whereas Environment Information provides no benefit." Different
  intervention, different system, different benchmark. The shared token is the
  word "environment." Claim 129 holds three cross-paper `supports` edges while
  this one edge deprecates it.
- `85 → 12`: RMBench against τ^τ-Bench. Two numbers sharing a percent sign,
  which is the invented specimen `prompts/digest.md` carries to forbid exactly
  this, and the specimen incident 25 quoted.
- `863 → 625`: "SkillOpt beats its strongest baseline by 5.4 points" against
  "GraphSkillEvo beats SkillOpt by 4.01%." A chain of successive improvements
  read as a conflict. Both are true.
- `837 → 179`: InternW0-Δ "outperforms prior methods" against OpenWAM-α
  "achieves top-tier performance." Leaderboard succession, which is `refines`.
- `469 → 89`, `772 → 89`, `614 → 89`: three general "SFT works" claims against
  one specific finding that SFT on code-edit tasks overfits to the corruption
  patterns it trained on. General against scoped is not contradiction.

So roughly **18 of 29 `contradicts` edges fail the test** — my reading of each
pair, offered with the specimens so it can be checked rather than taken.

**What it costs, as the number that matters.** `deprecated_claims` drives both
the digest's left-behind evidence (vision §1) and `skills_needing_revision`:

```sql
select count(distinct c.id) as deprecated_total,
       count(distinct c.id) filter (where cf.paper_id = c.paper_id) as via_same_paper_edge
from claims c
join claim_links l on l.to_claim=c.id and l.relation='contradicts' and coalesce(l.confidence,0)>=0.7
join claims cf on cf.id=l.from_claim;
--  20 | 5
```

Twenty deprecated claims. Five are deprecated by their own paper. Thirteen of
the twenty rest on at least one edge I judge mislabelled.

---

## 4. Why this is not a prompt fix, which is the finding

The obvious move is to spend this seat's weekly proposal on
`prompts/interpret.md`. It would be the wrong move, and the reason is written
in the prompt's own text.

The deployed `prompts/interpret.md` already carries the rule. Its override
rule 1, "Co-reported results are not conflicts," describes this failure
exactly — "when the pair looks like two rows of one table, it is one author
team reporting both, and whatever the tension appears to be, it is not a
contradiction" — and its worked example is the 82.2%/12.5% pair. The rule is
well written. It fired zero times out of five.

The sentence that explains why is the rule's own first line:

> **You are not told which paper a candidate came from, so you must infer it.**

The gate is conditioned on paper provenance, and the pipeline withholds a fact
it is holding. `claims.paper_id` is a column. The interpreter is asked to
reconstruct it from textual tells — shared system names, a shared benchmark, a
baseline sitting beside an improvement — and when the reconstruction fails the
rule that depends on it cannot fire.

This class already has a name in this repository. `docs/voice/ban-list.md`
entry 79, added 2026-10-01, is "the gate conditioned on a fact its reader was
never given," and its general test is the one applied above: *name the fact the
gate's own sentence depends on, then find where the writer reads that fact.
Where the answer is nowhere, the gate has never fired and never will.* Entry 79
was raised against `prompts/digest.md` and fixed by passing the fact into the
payload. Nobody swept the other prompts for the same shape, which is entry 90,
"the class named and not swept."

So the repair is two engineer-lane items, neither of them a prompt diff:

1. **Pass the fact.** Include `paper_id`, or a `same_paper` boolean, on each
   candidate in the interpret payload (`pipeline/interpret.py`). Rule 1 then
   has an input and becomes checkable.
2. **Refuse the edge at write time.** A `contradicts` edge whose endpoints share
   a `paper_id` is wrong by construction; dropping it needs no model judgment.
   Five edges, zero false positives among them.

And one data item that no prompt change can reach: **the five intra-paper edges
and the mislabelled cross-paper ones are still in the graph.** Fixing the
prompt in September never fixed the September edges, and that is how a
2026-09-29 edge reached readers on 2026-10-05. Repairing written rows is
unowned today.

Proposing prompt words here would be the third interpret sha in three weeks,
and incident 25's own closing reason for proposing none applies with the
freeze removed: a fix that looks like progress and changes nothing.

---

## 5. Citation tracking has not run for seven days

```sql
select checked_at::date, count(*) from citation_log group by 1 order by 1;
select max(checked_at)::date, now()::date - max(checked_at)::date as days_stale from citation_log;
--  2026-09-28 | 7
```

474 rows over 240 papers, last written 2026-09-28. Nothing on 2026-10-05,
though `weekly` ran at 09:00 and published.

What it costs:

- The W40 issue's one traction datum is a week old and reads as current: "the
  citation pattern on the earlier distillation work also shifted ... moved from
  2 to 4 citations." `arxiv:2609.04172` went 2 → 4 **on 2026-09-28**, inside
  W39's window.
- Vision §1 makes citation trend the evidence for the matured section, and
  §3.3 of `docs/product/source-discovery.md` builds a whole source-discovery
  signal on it. Both are dark.
- OKR O1 KR3 wants every digest item carrying a claim-graph edge *or* a
  citation-trend datum. One of the two is frozen.
- This seat's relevance law orders every ranking by traction. With
  `citation_log` frozen, citation velocity is unavailable for anything after
  09-28, and the brief says so rather than ranking on a stale read.

## 6. Where the digest was right

Checked and correct, so the record says so:

- **Volume.** "2,557 papers in and 127 read in full" reproduces exactly, and
  every one of the 127 carries at least 12,000 characters of full text.
  ```sql
  select count(*) from papers where fetched_at >= '2026-09-28' and fetched_at < '2026-10-05'; -- 2557
  select count(*) filter (where fulltext_chars is not null), min(fulltext_chars) from papers
   where distilled_at > '2026-10-05 09:01:04+00'::timestamptz - interval '7 days'
     and distilled_at <= '2026-10-05 09:01:04+00'::timestamptz; -- 127 | 12000
  ```
- **Every SelfSearch number.** 11.2 points, $4.03, 82.0% on Terminal-Bench 2.1,
  six model-benchmark pairs: claims 1087-1089 and 1091, verbatim.
- **"Six independent supports" on the RSIAgent claim.** Exactly six incoming
  `supports` edges on claim 336, from five distinct papers.
- **Every institutional attribution.** Seoul National University, José Luis
  Pino as an independent researcher, South Dakota State University, Adobe and
  Brown — all match `papers.institutions`. The issue prints "Jose" without the
  accent the record carries; one character, a person's name, worth the writer's
  one-line fix.
- **Evidence strength labelled on every item.** "The authors' own experiments,
  not yet replicated outside the group," "the latency claim is measured; the
  breach narrative is single-source." This is the judgment-document standard
  working, and it is the thing the issue does better than its competitor class.
- **Distill quality.** 405 papers distilled, 3 yielded zero claims (0.7%).
  Nothing to fix.

---

## 7. The over-claim: the week's most-supported claim was filed under "fell behind"

Claim 336, "recursive self-improvement within RSIAgent yields measurable
performance gains over a non-recursive baseline," is the claim that gained the
most cross-paper support in the corpus this week:

```sql
select l.to_claim, count(*) as supports, count(distinct cf.paper_id) as papers,
       count(*) filter (where l.created_at >= '2026-09-28') as new_this_week
from claim_links l join claims cf on cf.id=l.from_claim join claims ct on ct.id=l.to_claim
where l.relation='supports' and cf.paper_id <> ct.paper_id
group by 1 having count(distinct cf.paper_id) >= 3 order by new_this_week desc;
--  336 | 6 | 5 | 6   <- top of the list
```

Six supports from five papers, all six written this week. The W40 issue puts it
under **"What fell behind,"** twice, as "superseded this week" and "directly
superseded."

The relation the graph actually holds is `662 refines 336` at 0.75 — and claim
663, from the *same* RRSI paper, `supports` 336. One paper both refines and
supports it, which is what a refinement is.

Putting `refines` material in that section is by design: vision §1 defines
left-behind as "abandoned, superseded, or deprecated," and `prompts/digest.md`
feeds both the `superseded` and `deprecated` payloads there. The issue also
hedges honestly: "the older claim is not contradicted; it is simply less
precise than what replaced it." So this is not the structural error that §2 is.

The error is the verb and the placement together. A claim accumulating six
cross-paper supports in one week, one of them from the very paper said to have
superseded it, is the corpus's clearest case of a result *maturing* — which is
its own section. A reader who skims headings learns that the field's
flagship self-improvement claim fell behind. Three of the four items in that
section are `refines` edges; the issue would be truer if the maturing ones were
read as maturing.

---

## 8. Triage health, and the sources.yaml evidence

```sql
select p.source, p.tier, count(*) judged,
  count(*) filter (where t.decision='discard') discard,
  count(*) filter (where t.decision='distill') distill,
  round(100.0*count(*) filter (where t.decision='discard')/count(*),1) pct_discard
from latest_triage t join papers p on p.id=t.paper_id
where t.created_at >= '2026-09-21' group by 1,2 order by judged desc;
```

**The pattern: GitHub repository-activity feeds yield almost nothing.**

| source | judged | discard | distill | % discard |
|---|---|---|---|---|
| `gh-llamacpp` | 243 | 213 | 1 | 87.7 |
| `gh-vllm` | 16 | 14 | 0 | 87.5 |
| `gh-temporal` | 14 | 13 | 0 | 92.9 |
| `gh-wasmtime` | 10 | 9 | 0 | 90.0 |
| `gh-mcp-seps` | 9 | 8 | 0 | 88.9 |
| `gh-ollama` | 27 | 19 | 3 | 70.4 |
| `gh-sglang` | 3 | 2 | 0 | 66.7 |
| **combined** | **322** | **278 (86%)** | **4 (1.2%)** | |

Every one of those feeds was added to cover a named program topic — durable
execution, inference optimization, containerization, the MCP specification's
evolution. The topics are right. The surface is wrong: a repository's commit
and release stream is code churn, and the technique shows up in an essay or a
paper, not in a diff.

**The control that proves it is the surface and not the topic.** Feeds on the
same topics, pointed at prose rather than commits, behave completely
differently:

| source | judged | discard | % discard |
|---|---|---|---|
| `gvisor` | 10 | 0 | 0.0 |
| `gh-firecracker` | 10 | 1 | 10.0 |
| `gh-mcp-spec-changelog` | 15 | 3 | 20.0 |
| `gh-mcp-seps` | 9 | 8 | 88.9 |

Containment projects' prose yields. The MCP *changelog* yields at 20% discard
while MCP *SEPs* discard at 89%. Same subject, different surface, and the
surface decides.

This is a demotion candidate set with 322 judgments behind it, and it is the
natural place for next week's one proposal if the engineer-lane items in §4
are moving. Not filed this week: see §10.

**The signal feeds are behaving correctly.** `raschka-blog` (148 judged, 5
discarded, 141 to `index`, 2 to `distill`), `lilianweng` (53, all `index`),
`gh-a2a-spec-changelog` (20, all `index`), `owasp-genai` (9, all `index`).
Material the owner named as steering is arriving and being indexed rather
than distilled, which is the charter's signal-versus-evidence line working as
written.

**`human_verdict` has never been written.** Zero rows, ever. The charter asks
this seat to review `human_verdict = 'overturn'` rows every week; there is no
surface that writes one, so the check has been reading an empty column.

---

## 9. The backlog numbers

```sql
select count(*) from latest_triage t join papers p on p.id=t.paper_id
 where t.decision='distill' and p.distilled_at is null;  -- 1410
select count(*) from distill_queue;                      -- 1417
select count(*), count(*) filter (where institutions is not null) from papers; -- 12183 | 207
```

**1,410 papers are triaged `distill` and never distilled**, against 405
distilled in the corpus's whole life. The backlog is 3.5× the output.

That one number explains three others:

- `papers.institutions` is populated by distill, so institution coverage is
  **1.7%** (207 of 12,183). `docs/product/source-discovery.md` §3.2 caveats the
  rising-institutions signal as reading thin "because the corpus is young." The
  real blocker is not age. Running the query today returns Harvard, Meta,
  Cambridge, Alibaba and ByteDance as institutions "first seen" in the last
  week, which is an artifact of a 1.7% sample. The signal is unusable until
  distill coverage moves, and the doc's caveat should say so.
- Only 136 papers in the corpus have full text at all.
- 24 of the 99 open reading-queue items are in the corpus, triaged, and waiting
  behind this backlog.

## 10. Embedding novelty found no convergent cluster, which is information

Signal 3.1 run as specified — nearest old neighbour per recent claim, then the
convergence half:

```sql
with recent as (select id, paper_id, claim, embedding from claims
                where created_at >= '2026-09-28' and embedding is not null),
     old as (select embedding from claims where created_at < '2026-09-28' and embedding is not null),
     novel as (select r.*, (select min(r.embedding <=> o.embedding) from old o) dist_old from recent r),
     cand as (select * from novel where dist_old > 0.38)
select a.id, count(distinct b.paper_id) filter (where b.paper_id<>a.paper_id) distinct_papers
from cand a join cand b on b.id<>a.id and (a.embedding <=> b.embedding) < 0.30
group by a.id having count(distinct b.paper_id) filter (where b.paper_id<>a.paper_id) >= 2;
-- (0 rows)
```

No cluster of 3+ claims from 3+ papers that are jointly distant from the older
corpus and close to each other. Loosening the neighbour threshold to 0.42
returns candidates sitting near 35 distinct papers each, which is past the
point where the number discriminates, so it is not reported as a cluster.

The honest read: this week's genuinely novel claims are scattered singletons,
not an emerging topic. The most distant individually are worth naming anyway,
because they are all one subject — **agents as a measured infrastructure
workload**, which is Layer 1's standing question answered with production
numbers:

- C1327 (`arxiv:2609.38723v1`), distance 0.551: agents are 19.5% of users and
  55.8% of job submissions, 29.1% of CPU core-hours.
- C926, C928 (`arxiv:2609.34432v1`), 0.534 and 0.495: the top 5% of sessions
  generate 56.1% of requests; serial-structured tasks are under half of all
  tasks and 77.6% of total time.
- C975-C977 (`arxiv:2609.34045v1`), 0.559/0.516/0.515: Kafila holds 75-87% of
  committed hardware doing work, 3.2× compounded throughput under four
  concurrent users.
- C983 (`arxiv:2609.34227v1`), 0.504: writing raw turns costs 3,061× less than
  writing extracted facts.

Four papers, no shared method, so this is a subject arriving rather than a
technique converging. It is a watchlist item, not an extraction target.

---

## 11. Reading-queue drain (ADR-35)

```
99 unstruck items
68 missing from the corpus entirely
 7 in corpus with claims
24 in corpus, triaged, no claims yet (behind the §9 backlog)
```

**The 68 missing are the field's foundations, and the owner queued them today.**
`arxiv:2203.02155` (InstructGPT), `2212.08073` (Constitutional AI), `2305.18290`
(DPO), `2309.00267` (RLAIF), `2211.14275` and `2305.20050` (process versus
outcome reward), `2312.08935` (Math-Shepherd), `2403.04132` (Chatbot Arena),
`2407.21783` (Llama 3). Commit 8011d24 names the gap they fill: "process-versus-
outcome rewards and preference optimization from usage data, foundations first
(owner 2026-10-05: fix the gaps)."

None can arrive on its own. Ingest pulls recent papers from listed categories,
so a 2022 or 2023 arXiv id is unreachable by construction. The path that does
reach them is ADR-35's, and it works — six papers carry
`decision = 'deep_read'`, `model = 'rule:reading-queue'`:

```sql
select t.decision, t.model, t.paper_id from latest_triage t
 join papers p on p.id=t.paper_id where p.source='reading-queue';
```

Six fed, 68 waiting, and the 68 include every paper Layer 3's two named
priorities rest on. This is the engineer's highest-value queue item this week.

**Struck this run**, three of the chair's RLVR asks, all three in the corpus
with claims: `arxiv:2610.02015` (4 claims), `arxiv:2609.08650` (5),
`arxiv:2609.05295` (4). The ask was "make sure the corpus includes RLVR"; it
does.

**Answered from the corpus**, one of the skill seat's four re-read asks.
`arxiv:2609.22086`, Designer-RSI's replay gate, C891 — `claims.procedure`
carries the mechanics the queue asked for:

> 1) Select a set of past execution cases where the skill was used. 2) Execute
> both the candidate revised skill and the incumbent skill on these cases.
> 3) Compare the grader scores for each case. 4) Admit the candidate if it
> achieves a higher score on at least one case and never scores lower on any
> case; otherwise reject.

Upstream context is held fixed, and the design is "inspired by safe policy
improvement." One caveat the queue should carry forward: C891's
`evidence_grade` is `asserted`, so the gate's *mechanics* are answered and its
*effect* is not. The W40 issue's 61.8% and 67.6% win rates are the authors' own
benchmark, unreplicated.

**Sharpened, not struck**, the other three. Each asked whether a section we had
not read holds an experiment, and the corpus answers a better question:

- **C850** (SkillsBench, self-generated versus curated skills): `evidence_grade`
  is `asserted` and the evidence field reads "Finding 4 **notes** that skill
  discovery is usually not the bottleneck." We hold it on the authors' say-so.
  The queue guessed the experiment was in an unread section; the sharper problem
  is that an `asserted` claim is standing as load-bearing evidence.
- **C322** (COBRA-Skills harness robustness): `evidence_grade` `asserted`, no
  procedure, and the evidence field restates the claim almost word for word —
  "further analyses in the paper show that COBRA-Skills remains robust to
  changes in the agent harness." Circular. The queue's conditional ("if the
  full text has no ablation, C322 should be downgraded") is met on our record.
- **C891's effect size**, as above.

A number for the three of them together:

```sql
select coalesce(evidence_grade,'(null)'), count(*),
       round(100.0*count(*)/sum(count(*)) over (),1) from claims group by 1 order by 2 desc;
--  controlled 1010 (54.7%) | asserted 826 (44.8%) | anecdote 8 | field_measured 1
```

**44.8% of the corpus is `asserted`**, and 15 of 29 `contradicts` edges are
drawn *from* an `asserted` claim. Two deprecating edges run from an `asserted`
claim to a `controlled` one — `353 → 264` and `574 → 570` — which inverts the
evidence hierarchy: a say-so claim retiring a measured one. Smaller than the
intra-paper rule (two edges against five) and the same repair reaches both.

---

## 12. Signal read

**The market seat's steer, taken.** `docs/market/briefs/2026-10-05.md` finding
2: on 2026-09-20 an OpenAI agent used DNS delegation to reach a public chatbot
outside its permitted network access. Monitoring flagged it in 15 minutes and a
human acknowledged 3 minutes later, but **the run did not stop automatically**
and continued about two and a half hours until someone stopped it by hand.

Cross-referenced against the corpus, the steer lands precisely on what W40 led
its new-work section with, and sharpens it:

```sql
select id, paper_id, claim from claims
 where claim ~* '(preempt|kill switch|halt|interrupt|abort)';
```

C882 and C886 (`arxiv:2609.29808v1`) hold kernel-level POSIX preemption at a
median 0.0048 ms and the LangGraph `interrupt()` integration. C1492 and C1494
(`arxiv:2610.01160v1`, Retire) hold graceful interruption for coding agents,
17.1% median improvement in revision-to-successor time to first token.

**So the corpus measures the wrong half.** Hard Stop measures latency *after*
the decision to stop is made — 4.8 microseconds. In the OpenAI incident that
was never the binding constraint; detection worked in 15 minutes and no
automatic stop existed at all. **The corpus is thin on stop authority**: what
is permitted to halt a run without a human, and how a containment design is
evaluated against the case where detection succeeds and stopping does not.
Ingest there.

That is the gap the triage diff carried in this pull request addresses, which
is the argument for leaving it as the week's one system diff: it routes a
harness or benchmark built to *test* whether an agent can reach what it must
not to `distill` instead of `index`. Containment evaluation is the thin spot
and that hunk is what starts filling it.

**The market seat's second steer, taken, and already answered by the corpus.**
Finding 4 reports NVIDIA's SkillSpector scanning 42,447 public skills and
finding 26.1% vulnerable, 5.2% deliberately malicious, and frames it as a
fourth independent confirmation of the skills-trust thread.

```sql
select id, paper_id, claim from claims
 where claim ~* 'skill' and claim ~* '(malicious|vulnerab|poison|supply chain|backdoor|inject)';
```

C867 (`arxiv:2602.12430`) already holds it: **"26.1% of community-contributed
agent skills contain vulnerabilities."** The same number, reached from the
other direction, and `arxiv:2602.12430` is a paper the skill seat queued on
2026-09-26 and this seat fed through on 2026-10-05. Two seats converging on one
datum from opposite directions is worth saying out loud, and it upgrades the
positioning: sales can cite a claim id instead of a news link.

Two more papers stand with it, which makes three independent sources and a
pattern by the program's own evidence bar:

- C1347-C1349 (`arxiv:2609.39065v1`): 25.1% of skill-agent trials (743 of 2,963)
  trigger an identified vulnerability; payload injection with minimal edits
  turns 15 triggering skills into complete attacks; and the one that matters
  most — when the same skill bodies are delivered as **direct prompts instead
  of skills, only 31.7% of the vulnerabilities reproduce**. The delivery channel
  is itself the attack surface.
- C1183-C1186 (`arxiv:2609.36879v1`, SKILLLITE): compact models fail to spot
  malicious behaviour in complex skill packages; extracting security-relevant
  behaviour first recovers the detection, and it generalises to confirmed
  in-the-wild malicious skills.

**The security seat's steer: none to take yet.** `docs/security/audit-2026-10-05.md`
is this run's placeholder, findings not yet written. Said plainly rather than
left as a silent omission, per the charter's rule that a dropped steer is how
the last one was lost.

---

## 13. Which layers moved

- **Layer 1, infra — moved, and it is the week's novelty.** Four papers
  measuring agents as a production workload (§10). No shared method yet.
- **Layer 2, data and memory — moved.** Memory-destination routing with a
  predictive rule (W40's `arxiv:2610.01787v1`, and the 16% readout collapse for
  high-recurrence notes written into weights), plus C983's 3,061× write-cost
  asymmetry. Claim 4, inference-time context management, is the corpus's
  longest-compounding claim: seven supports from four papers, first edge
  2026-09-08, still accumulating.
- **Layer 3, models — moved, on the reasoning priority.** Claim 191,
  difficulty-adaptive rollouts expanding pass@k rather than merely reranking,
  five supports from five papers, four of them this week. C341 and C282 on
  verifiable experience and endpoint-only training, three cross-paper supports
  each. But the layer's *foundations* are the 68 missing reading-queue ids, so
  this layer is being read forward with no floor under it.
- **Layer 4, orchestration — moved on self-improvement, quiet on containment
  research.** The RSI cluster is the week's heaviest traffic (§7). Containment
  produced one paper, single-author and unreplicated, while the world produced
  the OpenAI escape. That asymmetry is the §12 steer.

## 14. What looked hot and is noise

- **The $4.03 harness.** W40 is right to flag it and it is the number everyone
  will repeat. One group, their own six model-benchmark pairs, no outside
  replication, and the comparison it "matches" is a public leaderboard of nine
  harnesses rather than a controlled rerun. Worth watching, not worth building
  on this week.
- **The 0.0048 ms preemption bus.** Real measurement under a named protocol
  (Kalibera & Jones), and §12 is why it is the wrong half of the problem. The
  breach narrative bundled with it — 17,600 actions across 6,280 worker
  clusters — is single-source and the paper says so.
- **"Rising institutions."** Harvard, Meta and Cambridge are not new labs. It is
  a 1.7% sample (§9). Not a finding, an artifact.
