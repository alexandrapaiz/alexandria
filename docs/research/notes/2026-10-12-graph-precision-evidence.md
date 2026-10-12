# Evidence note -- 2026-10-12 research run

Every number in `docs/research/briefs/2026-10-12.md` with the query that
produced it. Read-only, through `NEON_RO_URL`. Labels for the precision
measurement are in `2026-10-12-contradicts-labels.json`, in the worksheet
format `tools/graph_audit.py --labels` reads.

## 1. There is no W41 issue

```sql
select week, left(prompt_sha,12), created_at from digests order by week desc;
-- 2026-W40 | c48d09624161 | 2026-10-05 09:01:04
-- 2026-W39 | ea2d678d86e9 | 2026-09-28 09:01:28
-- 2026-W37 | 83a0aa3be13c | 2026-09-14 15:00:21
```

Three issues in the `digests` table, four weeks elapsed since W37. W38 and
W41 are both absent. The engineer's #282 carries the diagnosis for W41 (the
free-tier minute cannot hold a 1,919-line prompt) and a short-edition path;
that is their lane and this note does not duplicate it.

## 2. `contradicts` precision is 0.172, measured on the whole population

`tools/graph_audit.py` has shipped `--sample`/`--labels` since it was written
and its own docstring records why no number ever came out of them: "No seat in
this org holds that credential today, which is the ledger entry of 2026-09-28
and the owner's to close." This run holds a read-only copy of it, so the
measurement is possible for the first time.

`contradicts` is 33 edges, so this is the **population and not a sample**: no
seed, no draw, nothing to re-draw. Every edge was read as both claim texts and
labelled `correct`, `wrong`, or `unsure` by the standard the interpret prompt
sets -- "acting on both claims is impossible; the new evidence points the
opposite way." `unsure` means a defensible reading exists either way; the tool
excludes it from both denominators.

```
$ python3 tools/graph_audit.py --labels docs/research/notes/2026-10-12-contradicts-labels.json
  "overall":       { "correct": 5, "wrong": 24, "unsure": 4, "precision": 0.172 }
  "by_confidence": { "0.6-0.7": 0.167, "0.7-0.8": 0.19, "0.8-0.9": 0.0, "0.9-1.0": 0.0 }
```

Two readings, and the second is the one that matters.

**Precision is 17.2%.** Five edges of 33 are defensible: `587->431`
(in-domain measurement overstates cross-dataset transfer ~5x and improvements
can hurt out-of-domain, against more domain QA data improving in-task while
maintaining out-of-domain robustness), `616->533`, `669->200`, `701->533`,
`849->322` (harness materially changes how a model benefits from Skills,
against COBRA-Skills being robust to harness changes).

**Confidence carries no signal, and is inverted at the top.** Precision is
flat near 0.17-0.19 across the bands that hold 29 of the 33 edges, and the two
highest-confidence edges in the graph -- `12->11` at 0.88 and `136->129` at 0.90 --
are both wrong. The audit's own `confidence calibration` metric reads `ok`
because it only asks how many distinct values the judge uses. It uses thirty.
They mean nothing.

This matters because of where the number is consumed:

```sql
select pg_get_viewdef('deprecated_claims', true);
-- ... join claim_links l on l.to_claim = c.id
--     and l.relation = 'contradicts' and coalesce(l.confidence,0) >= 0.7
```

`deprecated_claims` gates on exactly the band whose precision is 0.19.

## 3. 19 of the 22 claims on the Left-Behind Index are not superseded

```sql
select l.to_claim, string_agg(l.from_claim::text||'@'||l.confidence, ',')
from claim_links l where l.relation='contradicts' and coalesce(l.confidence,0)>=0.7
group by 1 order by 1;
-- 5|82@0.78   11|12@0.88   12|85@0.78   39|393@0.75  85|265@0.78
-- 89|469@0.75 103|1119@0.75 129|136@0.9 179|837@0.75 188|190@0.77
-- 198|676@0.75 238|705@0.75 264|353@0.75 288|289@0.75 322|849@0.75
-- 374|482@0.75 431|587@0.75 477|478@0.75 533|616@0.75,701@0.75,750@0.75
-- 570|574@0.75 604|897@0.75 625|863@0.75
```

Twenty-two claims. Crossing them against the labels: **322, 431 and 533 rest
on at least one edge that holds. The other nineteen do not.** Vision section 1 names
"left behind" as one of the digest's three kinds of finding, so 86% of the
index behind one of the product's three pillars is wrong.

## 4. The failure has a shape, and it is a magnet

```sql
select l.to_claim, count(*) inbound from claim_links l
where l.relation='contradicts' group by 1 having count(*)>1 order by 2 desc;
-- 533 | 4      Altering token-level supervision ... leaves the student model's behavior largely unchanged
--  89 | 3      Supervised fine-tuning on code-edit tasks overfits to the specific corruption patterns ...
-- 200 | 3      Imitation-based fine-tuning of the weaker model ... causes consistent performance regression
-- 850 | 2      Self-generated Skills underperform curated Skills, and skill discovery is not the primary bottleneck
```

Twelve of the 33 edges point at four claims, and all four are **negative
results** -- a limitation, a null, a regression, an underperformance. Nothing
else in the graph attracts edges like this.

The mechanism is visible in the pairs. C772 "diverse, high-quality SFT
establishes a strong capability floor" is written as contradicting C89 "SFT on
code-edit tasks overfits to the specific corruption patterns seen during
training": one is a scope the other excludes, and both are true. C865, an
ablation of skill-optimisation components, is written as contradicting C533,
about token-level supervision in Qwen -- different subjects entirely. C931, a
27B model matching a 72B with a harness, against C200, imitation fine-tuning
regressing: different interventions.

So the judge reads **"a limitation of X" against "a success near X" as
opposition**, when the honest answer is almost always that they measure
different things. The existing prompt has guards for two neighbouring cases
(different systems on one benchmark, one system on different benchmarks) and
none for this one, which is the diff in section 7.

Two secondary classes, each with instances:

- **Scale-class mismatch.** `897->604`: Magenta at 100% on AIME 2026 against
  ZGCM-1-7B "ranks first on average ... at the 7B-8B scale". A frontier score
  does not refute a claim about the best 7-8B model.
- **Successor read as refutation.** `863->625`: GraphSkillEvo improving on the
  SkillOpt baseline is `refines`, which the prompt already says, pointed at
  the wrong relation.

## 5. All five same-paper `contradicts` edges are still live and still wrong

```sql
select l.from_claim, l.to_claim, c1.paper_id, l.created_at::date
from claim_links l join claims c1 on c1.id=l.from_claim join claims c2 on c2.id=l.to_claim
where l.relation='contradicts' and c1.paper_id=c2.paper_id order by l.created_at;
--  12->11  arxiv:2609.04611  2026-09-08
-- 190->188 arxiv:2609.10522  2026-09-19
-- 289->288 arxiv:2609.09219  2026-09-29   <- reached readers in W40
-- 478->477 arxiv:2609.16816  2026-10-01
-- 574->570 arxiv:2609.17652  2026-10-02
```

The same five rows the 2026-10-05 run reported, unchanged. Read in full they
are one results table each, and two of them are the tell-tale the prompt names
in its own words. `12->11` is "an expert-authored reference implementation
achieves 82.2% ... establishing a high ceiling" beside "the strongest tested
configuration ... passes only 23.9%" -- the prompt's phrase for this is "an
expert ceiling beside a measured score". `574->570` is "Fathom does not provide
speedups when the index resides in GPU memory" beside Fathom's 1.67x headline:
a limitation beside a headline number, also named in the prompt.

The rule that should catch all five is interpret rule 1, and it cannot fire,
for the reason the rule states in its own first sentence: "You are not told
which paper a candidate came from, so you must infer it." `paper_id` is a
column the pipeline is holding and does not pass. That is an engineer fix, it
was engineer item 0 and 2 in the 2026-10-05 brief, and it is not a diff this
seat can propose. section 7 does not try.

## 6. The best-evidenced cluster the corpus has ever held is invisible to the
machinery that would surface it

```sql
select count(*) claims, count(distinct paper_id) papers,
       count(*) filter (where embedding is null) no_embedding,
       count(*) filter (where interpreted_at is null) uninterpreted,
       count(*) filter (where evidence_grade='controlled') controlled
from claims where claim ~* '(attack success|hijack|prompt injection|privilege
  escalat|isolation boundar|container escape|agent.security)';
-- 24 | 15 | 8 | 17 | 22
```

24 claims from 15 papers, **22 of them `controlled`** against a corpus
baseline of 57.8%. This is the owner's named Layer 4 priority -- containment
evaluation, "how you test that an agent cannot reach what it must not" -- and
it arrived.

And the machinery cannot see it. Of the ten highest-id claims in the cluster,
**every one has zero edges**:

```sql
select id, (embedding is null) emb_null, (interpreted_at is null) uninterp,
       (select count(*) from claim_links l where l.from_claim=c.id or l.to_claim=c.id) edges
from claims c where id in (1993,1992,1882,1861,1769,1653,1295,1225,1224,1221);
-- 1993 t t 0 | 1992 t t 0 | 1882 t t 0 | 1861 t t 0 | 1769 t t 0
-- 1653 t t 0 | 1295 f t 0 | 1225 f t 0 | 1224 f t 0 | 1221 f t 0
```

The skill seat's documented method for finding a cluster is `semantic_search`
plus the supports edges. For this cluster, `semantic_search` cannot reach the
eight with no embedding and the supports edges do not exist. The system was
told what to look for, found it, and cannot surface it. section 3 of the brief hands
over the ids directly, which is the way around it that needs no deploy.

## 7. Embeddings stop dead at 2026-10-04

Reading-queue question of 2026-10-05: was the 227-claim null-embedding window
"the normal lag of a nightly embed job, or incident 30's first occurrence
returning"?

```sql
select created_at::date, count(*) filter (where embedding is null) nulls, count(*) tot
from claims where created_at > now()-interval '12 days' group by 1 order by 1;
-- 2026-10-01   0 217 | 2026-10-02   0 136 | 2026-10-03   0 135
-- 2026-10-04 142 142 | 2026-10-05 129 129 | 2026-10-06  55  55 | 2026-10-07  96  96
```

Neither. It is not a lag that drains and it is not intermittent: **every claim
created on or after 2026-10-04 has a null embedding, and every claim before it
has one**, 422 claims and 21.1% of the corpus, with a clean boundary at a date.
All 422 are also uninterpreted (`interp_no_emb` is 0), so embedding is the gate
in front of interpret, and interpret is running ~11 days behind on what it can
reach -- C1119, created 2026-10-01, was interpreted on 2026-10-12.

Consequence for this seat: **discovery signal 3.1 cannot see the last nine
days.** Everything in section 2 of the brief is computed on claims up to 2026-10-03,
which is stated there rather than implied.

## 8. Citation velocity is 14 days dark

```sql
select max(checked_at), count(*), count(distinct paper_id) from citation_log;
-- 2026-09-28 09:00:18 | 474 | 240
```

Seven days stale when the 2026-10-05 brief reported it, fourteen now. The
relevance law orders every ranking this seat produces by evidenced impact, and
names citation velocity first among the streams that evidence it. It has been
unavailable for two consecutive briefs. Both rankings in this brief are built
on cross-paper `supports` accumulation instead, and say so.

It is also one of the two evidence streams O1 KR3 accepts for the monthly
ten-item audit, and the October audit is due with launch.

## 9. Throughput: what is actually binding

Reading-queue question of 2026-09-30: "Is distill throughput now the binding
constraint rather than triage throughput?"

```sql
select created_at::date, count(*) triaged, count(*) filter (where decision='distill')
from triage_log where created_at > now()-interval '14 days' group by 1 order by 1;
-- 10-01 856/222  10-02 855/228  10-03 871/182  10-04 857/176  10-05 897/234
-- 10-06 848/249  10-07 862/213  10-08 486/147  10-09 124/49  10-10 171/42
-- 10-11 115/33   10-12 120/41

select distilled_at::date, count(*) from papers
where distilled_at > now()-interval '14 days' group by 1 order by 1;
-- 10-01 48  10-02 30  10-03 30  10-04 30  10-05 27  10-06 11  10-07 20
-- (nothing on or after 2026-10-08)
```

Answer, in two parts. **Until 2026-10-07, yes**: triage was routing ~210
papers a day to distill and distill was clearing ~30, a 7x gap, which is the
whole of why `distill_queue` went from 1,410 on 2026-10-05 to 2,173 today.
**Since 2026-10-08, neither**: distill has produced nothing at all for five
days and triage is at 120 a day against 860 the week before, 14% of its own
rate. The binding constraint is now the model budget, which is #282's subject.

Standing totals: 436 of 14,666 papers ever distilled (3.0%), 166 with full
text (1.1%), 235 with institutions (1.6%).

## 10. `promotions` has never been written

```sql
select path, status, created_at from promotions order by created_at desc limit 25;
-- (0 rows)
```

Eight skills stand in `skills/`. The charter tells this seat to run exactly
this query before proposing one, "to avoid duplicating an existing proposal",
so that gate has been reading an empty table for every run that has ever run
it. Same class as `human_verdict`, which the 2026-10-05 brief found has never
been written in any row. Both are watch items in section 6, not this week's diff.

## 11. Evidence grades, updated

```sql
select evidence_grade, count(*), round(100.0*count(*)/sum(count(*)) over (),1)
from claims group by 1 order by 2 desc;
-- controlled 1153 57.8 | asserted 834 41.8 | anecdote 8 0.4 | field_measured 1 0.1

select c1.evidence_grade, count(*) edges,
       count(*) filter (where coalesce(l.confidence,0)>=0.7) deprecating
from claim_links l join claims c1 on c1.id=l.from_claim
where l.relation='contradicts' group by 1;
-- controlled 18 14 | asserted 15 10
```

The 2026-10-05 reading-queue line asked for these as 44.8% asserted and 15 of
29 contradicts edges drawn from an asserted claim. Now **41.8% asserted** (834
of 1,996) and **15 of 33**, of which **10 deprecate** a claim at confidence
>= 0.7. The share improved; the absolute count of asserted-origin deprecating
edges did not.

## 12. The deploy, and why section 7 proposes into `interpret` and not `triage`

The charter requires this check before spending the week's proposal on an
image-baked file.

| file | HEAD `sha256[:12]` | deployed | writing as of | verdict |
| --- | --- | --- | --- | --- |
| `prompts/interpret.md` | `6706ec7bffee` | `6706ec7bffee` | 2026-10-12 | **current** |
| `prompts/triage.md` | `3ea6485103c3` | `32252384ecd7` | 2026-10-12 | **stale** |

```sql
select split_part(method,'@',2) sha, count(*), max(created_at)::date from claim_links group by 1;
-- 6706ec7bffee | 865 | 2026-10-12      <- equals HEAD
select left(prompt_sha,12), count(*), max(created_at)::date from triage_log group by 1;
-- 32252384ecd7 | 8861 | 2026-10-12     <- does not equal HEAD
```

```
$ git log --oneline -2 origin/main -- prompts/triage.md
fa029bf research 2026-10-05 meta-review: triage reads containment too narrowly in two places
ea61cbc triage: four standing threads go first and distill on a measured mechanism ...
$ git show fa029bf:prompts/triage.md | sha256sum | cut -c1-12   # 3ea6485103c3  (HEAD)
$ git show ea61cbc:prompts/triage.md | sha256sum | cut -c1-12   # 32252384ecd7  (deployed)
```

The deployed triage prompt is `ea61cbc`, of 2026-09-29. The prompt at HEAD is
`fa029bf` -- **this seat's own proposal from 2026-10-05**, merged, and still not
in production seven days later, with 8,861 rows written against the old one
since. `deploy_runtime` agrees that nothing has shipped:

```sql
select app, runtime_sha, first_seen_at from deploy_runtime;
-- weekly    0cbc51a0e248  2026-10-05 09:00:19
-- triage    0f8e1554c1b7  2026-10-05 12:00:07
-- interpret 1b602dad8e74  2026-10-05 14:00:11
```

Three images, all first seen 2026-10-05, none replaced since.

So `prompts/triage.md` is barred as a target by the charter's own rule, and the
2026-10-05 brief's claim that "the deploy freeze that made incidents 25 and 26
is over" was true when written and is false now. That is a repeat and it is in
the incident register in this pull request.

`prompts/interpret.md` is the exception on this table and the reason the diff
goes there: its deployed sha equals HEAD, so a merge into it is a merge that
can reach production. It still needs someone to run `modal deploy` -- and the
row above it is the proof that this does not happen on its own. One deploy
ships both.
