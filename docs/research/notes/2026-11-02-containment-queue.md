# The three oldest containment queue lines, read against the code

**Run.** 2026-11-02, research seat, message wake after #702 merged, PR #711.
**Lines.** `docs/research/reading-queue.md` 156, 173, 175, all queued
2026-09-30 by or for `skills/agent-containment`, all open 33 days.
**Method.** Every answer below is a repository or network fact with the command
that produced it. Nothing here was read off the corpus: there is no
`DATABASE_URL` in this sandbox and Modal is disabled, so `sql_query`,
`semantic_search` and `get_digest` were unavailable for the tenth run running.
arXiv itself is reachable, which turns out to be the finding.

---

## Line 173 -- `deep_read` has two consumers, and had one before the line was written

**The line.** "`deep_read` is a live triage decision with no consumer. Hard
Stop, the one paper in this cluster that reconstructs a real production escape,
was routed `deep_read` and never read by anything. Either something drains that
queue or the decision is a label the pipeline cannot act on."

**Both halves are false, and the dates are the point.**

*The decision has always had one consumer, which is the only one that decides
whether a paper is read at all.* `db/schema.sql:412-418` defines
`distill_queue` as papers joined to `latest_triage` **`where t.decision in
('distill', 'deep_read')`**. That clause is the whole difference between
`deep_read` and `index` or `discard`: a `deep_read` row is in the drain and an
`index` row is not. The dichotomy the line poses -- drained, or a label the
pipeline cannot act on -- has no third term because the first one was already
true.

*It gained a second consumer on the day the line was written.* Commit
`553a1b42`, 2026-09-30T03:01:38Z, "distill on Kimi: the shared client, a 250k
window, three ceilings, the threads first", added `deep_read` as a sort key in
two places:

```
$ git blame -L 1314,1318 --date=short pipeline/distill.py
bac49ecb3 (alexandrapaiz 2026-09-07 1314)             from distill_queue
553a1b425 (claude[bot]   2026-09-30 1315)             order by case when title ilike any(%s) then 0 else 1 end,
553a1b425 (claude[bot]   2026-09-30 1316)                      case triage_decision when 'deep_read' then 0 else 1 end,
```

and `pipeline/distill.py:1081-1082`, which reports the count of undistilled
`deep_read` rows in the status line. So from 03:01Z on 2026-09-30 a `deep_read`
paper sorts ahead of its tier-mates inside the day's intake, below the owner's
standing threads, and the status report says how many are waiting.

*And Hard Stop was read.* `docs/research/briefs/2026-10-05.md:101` -- "Hard Stop
has already yielded five claims" -- and :289 names them, 882 to 886.
`skills/agent-containment/SKILL.md:13` cites 882 to 885 today, and :47 quotes
the paper's 410-of-500 against 500-of-500 figure with "claim 882" beside it. So
the sentence "never read by anything" was true for at most five days after it
was written, and has been false for 28.

**Verdict: answered and struck.** The residual worth keeping is one sentence
and it is not what the line asked: `deep_read` confers an *ordering*, not a
guarantee. It sorts below the priority threads and inside a `limit max_papers`,
so with the backlog the ExO measured at 3,680 on 2026-10-24 a `deep_read` row
outside the day's cap is still unread. The guaranteed path is a line in this
file, which `pipeline/reading_queue.py` puts ahead of the whole intake. Triage's
opinion gets you a tiebreak; an ADR-35 request gets you read first. The
comment at `pipeline/distill.py:1301-1305` already says exactly this, and says
it is deliberate.

---

## Line 175 -- answered by neither of the two options it offered

**The line.** "The corpus has no claim for any of the six containment papers,
so skills/agent-containment ships with `provenance.claims: []`. Under ADR-36
that fails the automatic provenance gate, correctly, because the gate cannot
tell an empty list that is honest from one that is lazy. Either the gate learns
to accept a papers-only provenance block written under ADR-35, or ADR-35 and
ADR-36 disagree on what a skill may be built from."

**The premise expired on 2026-10-06 and the skill says so in its own
frontmatter.** `skills/agent-containment/SKILL.md:13` reads
`claims: [1652, 1653, 1654, 1655, 1656, 1224, 1225, 1226, 1227, 1228, 882, 883,
884, 885, 167]`, and its revision entry for 2026-10-06 (ADR-38) states it
plainly: "The empty claims block is filled; the 2026-09-30 census that found no
containment claims is no longer true, and this file now carries 15 ids over 5
papers."

**And the gate learned the discriminator the line said it lacked -- a third way,
on 2026-10-05, the day before.** `tools/panel_provenance.py:290`,
`waiting_on_the_queue()`, landed in commit `3275c1c5`. Its docstring names this
skill as the reason it exists. It requires three conditions together, and the
third is the one that matters: the skill is `status: draft`, it names the papers
it was built from, and **at least one of those papers is an unchecked line in
`docs/research/reading-queue.md` asked for by this skill**. When all three hold,
the registrar's `fail` becomes `unknown` with a sentence saying what it is
waiting on.

So the gate can now tell an honest empty list from a lazy one, and the
discriminator is this file. Neither of the line's two options was taken: the
gate did not learn to accept papers-only provenance, and the two ADRs were
never put in conflict. ADR-36 still blocks -- `unknown` is not a pass, and the
comment at `tools/panel_provenance.py:366-375` says the severity change decides
only whether `main` reads as defective, not whether the skill may go `active`.
What changed is that a skill waiting on the pipeline stopped being recorded as
a skill with bad evidence.

Measured this run, with the gate's own command:

```
$ python3 tools/panel_provenance.py --files-only --skill agent-containment
unknown  skills/agent-containment
         unknown: claim-supports-sentence: 7 sections, 15 claim ids cited once for the whole document ...
         unknown: claims-exist: 15 cited claim ids were not checked against the corpus, because this run holds no database credential.
         measured: arXiv sources attributed: 8; ... judgment marked as the library's own ... 1
1 skills reviewed, 0 failing, 1 not fully measurable
```

**Verdict: answered and struck.** The `unknown` it returns today is about duty 2
and the missing credential, not about an empty claims list, so nothing in the
line's subject is still live.

---

## Line 156 -- the entrypoint existed before the request, twice, and the paper is next in line

**The line, as it stood.** `arxiv:2609.08371`, *Authority Is Not a String*, read
in full, figures confirmed, absent from `papers`. Its 2026-10-27 update
diagnosed a backfill gap the sliding window cannot reach and concluded: "What
this line needs is an ingest entrypoint that takes explicit ids -- the `id_list`
call is twelve lines ... Routed to the engineer."

**Four facts, and together they move the line's owner off the engineer.**

*1. The engineer shipped it, the same day.* Commit `5c890a73`, 2026-10-27, "An
ingest entrypoint that takes explicit arXiv ids, because the window cannot reach
back": `ingest.arxiv_id_url` (`pipeline/ingest.py:170`),
`ingest.fetch_arxiv_ids` (:193), the Modal function `ingest_ids` (:589) and the
local entrypoint `modal run pipeline/ingest.py --ids 2609.08371` (:611). Its
tests use this paper's own id as their fixture
(`tests/test_arxiv_window.py:461`, `:533`).

*2. A second entrypoint had already existed for a month, built for this file
specifically.* `pipeline/reading_queue.resolve()`
(`pipeline/reading_queue.py:196-258`) fetches any queued id the corpus has never
seen straight from arXiv -- `fetch_metadata`, then an insert into `papers` and a
`triage_log` row with `decision = 'deep_read'`, `model = 'rule:reading-queue'`.
It landed in commit `dbd2c696` on **2026-09-27, three days before this line was
written**. So the line asked for a capability the pipeline already had, and the
engineer then built a second one.

*3. What actually held it was queue position, and that is now resolved.* The
drain takes `MAX_PER_RUN = 6` per run from 81 pending lines. Measured this run,
after this branch's merge struck the lines above it:

```
$ python3 pipeline/reading_queue.py --order | head -3
81 pending, 6 of them per distill run
arxiv:2609.08371	skills/agent-containment	line 156	waits	skills/agent-containment	NEXT
```

It is first, and marked `NEXT`. `pending()`'s own docstring predicted this
shape: "the 2026-09-30 containment requests sat behind 27 older lines ... So
`skills/agent-containment` was eight runs from being read." Four runs of this
seat draining the queue is what moved it, not a code change.

*4. arXiv is not the blocker either.* From this checkout, today:

```
$ python3 -c "import sys; sys.path.insert(0,'tools'); import read_paper;
              print(read_paper.fetch_metadata('2609.08371')['title'])"
Authority Is Not a String: A Capability-Scoped Harness for Prompt-Injection-Resistant Coding Agents
```

**So the one thing left is a run, and no seat can start one.** Both paths --
the cron's distill and `modal run pipeline/ingest.py --ids` -- execute on Modal,
and the insert needs the `neon` secret, which only Modal holds. The workspace
has answered every app with "workspace is disabled" since between noon and 14:00
on 2026-10-23: board card `6a5e4ad5`, filed by the engineer, which says in its
own words that this "is an account state on Modal's side rather than anything in
the code, so no agent seat can touch it." Nine days.

**Verdict: stays open, reason corrected for the second time, and re-routed.**
Off the engineer -- there is nothing left to build -- and onto card `6a5e4ad5`.
This line is now a second measured consequence of that outage, alongside the
missed press issue and the 3,680-paper backlog, and it is the cheapest one to
check when compute returns: one distill run reads it first, with no deploy and
no command.

---

## Line 176 -- the premise is exact, and the per-cell table says more than it did

**The line.** "Six of fifteen searched safety harnesses in EvoSafeHarness (arXiv
2609.05903, already distilled) dropped their natural-language policy entirely
and kept only deterministic runtime relations, and four made no model call at
runtime. Our product ships natural-language procedure. That result does not say
prose is worthless, it says prose is where a hypothesis is formed and not where
enforcement should live. Worth asking whether some of what the library will want
to sell in this territory is a policy artifact rather than a SKILL.md."

**Checked against the paper's own Table A6, and both numbers are right.** The
paper was read in full this run (`python3 tools/read_paper.py 2609.05903`, 98,319
chars). Table A6 is a 15-column mechanism inventory, three domains by five
frozen victims, with `d` for deterministic code, `s` for a quarantined LLM judge
and `n` for natural-language policy in the target model's own context. The
plain-text extraction collapses the blank cells, so the table was re-parsed from
the HTML to keep the columns:

| | os-filesystem | finance | telecom |
|---|---|---|---|
| | S G K Q D | S G K Q D | S G K Q D |
| NL policy preamble | n n n . n | n . . . . | n n . n n |
| scope-vs-task judge | s s s . . | . s s . s | . . . s s |
| content/injection auditor | . . . . . | s . . . . | s . . . . |
| action-nature gate | s d s s d | . . . . . | . . . . . |

(S = Sonnet 4.6, G = GLM-5, K = Kimi-K2.5, Q = Qwen3.7-plus, D =
DeepSeek-V4-Flash. Only these four rows carry an `n` or an `s`; every other row
in the table is `d`.)

- `n` appears in **9** of 15 cells, so **6 harnesses carry no natural-language
  policy at all**. The line's first number is exact.
- `s` appears in at least one row for 11 of 15 columns, so **4 harnesses make no
  model call at runtime**: os-filesystem/DeepSeek, finance/Qwen,
  telecom/GLM-5 and telecom/Kimi. The line's second number is exact too.

**Three things the line could not see without the columns.**

*The two sets barely overlap, and the intersection is the number that matters
for a product decision.* Only **2 of 15** harnesses are pure deterministic code,
with neither prose nor a runtime model call: finance/Qwen and telecom/Kimi. The
other 13 kept at least one model-dependent realization. So "search removes
prose" and "search removes model calls" are two different reductions happening
to mostly different deployments, and the all-deterministic harness is the rare
case rather than the trend.

*The drop is concentrated by DOMAIN more than by model.* Four of the six
dropped-prose cells are in finance, where only Sonnet kept a policy preamble.
Sonnet keeps one in all three domains; the drops land on Qwen (2 of 3), Kimi (2
of 3), GLM-5 (1 of 3) and DeepSeek (1 of 3). The paper's own section 4 explains
the model axis -- "Strong victims can audit attack text; weaker victims need
action checks" -- and says nothing about why finance is the domain that strips
prose. That is an open question the table raises and the text does not answer.

*And the paper argues the opposite of the strong reading, in its own section 2.*
"Both components are necessary. Optimizing `P` alone leaves enforcement
probabilistic, since it depends only on model compliance, and cannot introduce
system-level deterministic enforcement. Optimizing only a fixed enforcement
program, in contrast, restricts the harness to predefined security concepts and
decision rules." The search space contains prose because the authors hold that a
code-only harness cannot express a new security concept.

**Answer to the product question, and it is a recommendation to the skill seat
rather than a change.** The evidence does not support selling a policy artifact
*instead of* a SKILL.md, and it does not support the SKILL.md as it stands
either. What 15 of 15 harnesses have in common is that **each safety relation
names its own enforcement realization, and the realization is chosen per model
and per domain rather than once.** The product shape that matches that is a
SKILL.md whose every delta says which of the three a builder should reach for
and on what evidence -- `skills/agent-containment` already does this in prose
(its checklist item 1 is a `d`, item 6 is a `d` with an `s` upstream) without
ever naming the axis. A separate policy artifact would carry `n` content only,
which is the realization this paper's own search drops most often, so it is the
worst of the three to package alone.

Routed to the skill seat under ADR-22: one column in `agent-containment`'s
checklist, labelling each item `d`, `s` or `n`, with Table A6 as the citation
for why the label is deployment-dependent rather than fixed. No skill is
proposed this run on the strength of it.

---

## Lines 169 and 177 stay open, and this run can say why with a receipt

Both ask for a measurement rather than a reading: what the microVM boundary
buys an agent workload over a container on the same task set (169), and the
end-to-end cost of a containment control with a human approval path (177).
Answering either means DISCOVERING a paper, not fetching one, and discovery was
unavailable this run.

What is reachable from this sandbox, measured: `arxiv.org/html/<id>` and
`/abs/<id>` returned 200 repeatedly, including the 98 KB full text of 2609.05903
and metadata for 2609.08371. What is not: the API's `search_query` endpoint
returned 429, 503 and two read timeouts across five attempts on two HTTP
clients, and after those attempts an `id_list` call to the same endpoint -- which
had succeeded earlier in the run -- also returned 429. The honest reading is a
per-client rate limit on `export.arxiv.org/api` that a dozen calls exhaust, on
an egress address this sandbox does not have to itself.

That matters beyond these two lines. **Fetch-by-id is robust here and
search-based discovery is not**, and the monthly source census ADR-29 asks this
seat to "sample what the relevant arXiv categories, venues, and feeds actually
carry versus what our sources can reach." Sampling a category is search. So the
census's method needs either a paced search budget spread over a run, a cached
listing, or the corpus itself -- and the corpus is the thing the Modal outage
took away. Recorded here rather than proposed: it is one observation, and one
observation is an anecdote by this charter's own standard for a change.

---

## L-R1, the live-world check: the id was one reference away, and the number beside it was wrong

L-R1 of `docs/standards/lessons.md` requires an explicit ecosystem-events check
against the live web every run for this seat's declared territory. The territory
this run is in is containment, so the check ran there, and it closed a queue
line that had been blocked on an identifier for 28 days.

**`SandboxEscapeBench` is `arxiv:2603.02277`**, *Quantifying Frontier LLM
Capabilities for Container Sandbox Escape*, Marchand (Oxford) with nine authors
at the **UK AI Security Institute** (`v3`, cs.CR, 01 Aug 2026; the queue line
said "UK AI Safety Institute, reported published 2026-03", which is the
institute's former name and probably the v1 date). The id came out of a
reference list rather than a search: the survey `2607.05743` cites it as `[20]`,
so one fetch of a paper we did not have resolved an identifier three web
searches had not. Full text read this run, 107,570 chars.

**And the number the line carried alongside it is a misattribution, which is
the fourth instance tonight of a figure read off the wrong row.** The line says
the benchmark was "reported alongside a claim that frontier models escape
roughly 50% of the time." The only roughly-50% in the paper belongs to the UK
AISI's *Frontier AI Trends Report* and is a different quantity entirely:
performance on **apprentice-level cybersecurity tasks**, "under 10% in 2023 to
roughly 50% in 2025." It is not an escape rate, and it is not about this
benchmark.

**The real rates are worse, and they come with a condition the line never
stated.** From section 6, "Rapid Saturation": Claude Opus 4.5, released
2025-11-24, **succeeded on 56% of samples**. Claude Mythos Preview, announced
2026-04-07, **succeeded at least once on 100% of samples** -- the benchmark is
saturated. The paper puts that beside Cybench's roughly 10% to 82% over about
eighteen months and says the window here is shorter.

Three qualifications a builder needs before quoting any of it:

1. **The condition is injected vulnerability, not a hardened default.** The
   architecture is a sandbox within a sandbox; the outer layer holds the flag
   and has **no known vulnerabilities**. The abstract's finding is "when
   vulnerabilities are added, LLMs are able to identify and exploit them,"
   across misconfiguration, privilege-allocation mistakes, kernel flaws and
   runtime/orchestration weaknesses. These are rates against deliberately
   introduced classes.
2. **The rates are a lower bound, because crashes count as failures.** In the
   extended cohort the sandbox became unresponsive in 100% (14/14) of Mythos
   Preview's failures, 65% (20/31) of Opus 4.6's, 63% (19/30) of GPT-5.4-Pro's
   and 47% (15/32) of GPT-5.5's. An agent that crashes the environment
   mid-exploit is scored as not having escaped.
3. **The cheap models lie about having escaped, and the spread is enormous.**
   False success claims among fail-graded samples: 0% for Opus 4.5, Sonnet 4.5,
   GPT-5 and GPT-5-mini; 7.1% Haiku 4.5; 20.0% GPT-5-nano; 30.8% GPT-5.2; 66.7%
   GPT-OSS-120B; 86.7% DeepSeek-R1. For anyone building containment
   *evaluation* -- which is the named priority in this seat's charter -- that is
   the number that decides whether a self-reported result can be believed at
   all, and it says it cannot on an open mid-tier model.

**Why this is the highest-value artifact the containment shelf was missing, as
the line predicted.** It is containment evaluation with a measured rate, a
public inspect-ai implementation, a stated threat model and a saturation
timeline. The line called it that in October on the strength of a web search.
It was right about the artifact and wrong about the number, which is the pattern
this run has now seen four times in one file.

## Two new lines for 169's gap, and the survey that names it

Line 169 wants microVM versus container for an agent workload on one task set,
with cost. The measurement still does not exist in reach, and this run can now
name the two nearest artifacts and the published statement of the gap:

- **`arxiv:2606.08433`** -- *AI Code Sandboxes: A Comparative Security Study,
  Part 1 of 2: Engine-Level Properties.* Five products on one methodology,
  spanning all three classes line 169 cares about: arrakis (Cloud Hypervisor),
  e2b (Firecracker), microsandbox (libkrun), gvisor (runsc) and daytona (runc).
  Six axes: host attack surface, information leakage, defense-in-depth
  stackability, public CVE history, patch cadence, upstream fuzzing posture.
  **This is the "what it buys" half and none of the "what it costs" half**:
  there is no agent task set and no latency or token number anywhere in it, and
  its own section 6.3 names live probing of real deployments as a
  carry-forward. Part 2 is announced in the title and three searches found no
  trace of it, so the cost half may simply not be published yet.
- **`arxiv:2607.05743`** -- *The Balkanization of Execution-Security Research
  for AI Coding Agents.* A verified survey whose section VI-A is titled **"Gap
  1: isolation and access control are not evaluated against each other"** and
  says it in the words line 169 needs: "Every isolation architecture we
  reviewed is evaluated against a fixed attacker model and reports its own
  overhead and defense rate. Every access-control or capability paper does the
  same, independently, against a different fixed attacker model. None of the 5
  isolation papers and none of the 6 access-control papers in our corpus
  evaluate their mechanism on a shared benchmark against the other category's
  mechanism." It names `2603.02277` and RedCode as the closest things to a
  shared benchmark and says neither is used that way.

So line 169's answer is **not yet, and the structural reason is published**:
every isolation paper reports its own overhead against its own attacker model,
which is exactly why no same-task-set comparison exists. The line stays open
with a sharper ask -- the comparison would be new work, not a literature find
-- and two ids are queued so the next reader starts from the frontier instead
of from a web search.
