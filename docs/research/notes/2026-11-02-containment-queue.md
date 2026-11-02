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
