# Quality claims, and the machinery under each one

**Enforced at:** prompts/exo-agent.md §3g, every run. Artifact-side, at
prompts/writer-agent.md before any reader-facing copy ships, and at
prompts/frontend-agent.md before any copy reaches the live site.

Maintained by the ExO agent. Created 2026-09-30 on the owner's order, after
the first skill measurement.

## Why this register exists

ADR-36 was written because the site said a skill is revised when the research
moves and nothing in the organization did that. The site sentence shipped on
2026-09-18 (commit 7c714c6). The decision to build the machine came eleven
days later, on 2026-09-29, and the code for it is still on an unmerged
branch. For those eleven days the sentence was simply untrue in public, and
it is untrue today. That is not a copy defect. The writer had approval,
the frontend shipped what was approved, and the claim was plausible to
everyone who read it, because the thing it described was the thing the org
intended to build.

So the pattern has a name and it is the same shape as `recording is not
enforcing` in docs/agents/registers.md, pointed outward instead of inward:
**a public claim is a promise with a mechanism, or it is a promise with
nothing.** The org has no shortage of seats that check copy against taste,
voice, canon and the ban list. Until this file, no seat checked a claim
against the machine that would have to be true for it to hold.

One reason it went unnoticed for so long is that the claims are all true of
the *research*, which is real and cited, while what a reader buys is a claim
about *our artifact*. "The research has shown this technique to work" and
"this skill makes your agent better" are different sentences with different
evidence, and the second one is the one the product is sold on. Every row
below that is red is red on the second sentence.

## How to read the table

One row per claim a public surface makes about the quality of what we ship.
Not marketing adjectives and not mission statements. A claim is in scope when
a reasonable reader could ask "how do you know that" and expect an answer.

- **Mechanism** is the specific code, job, test or file that would have to
  run for the claim to be true. Prose in a charter is not a mechanism. A
  charter clause telling a seat to do it by hand is a mechanism only if the
  seat can actually reach the evidence, which is the capability test in
  docs/agents/unowned-duties.md.
- **State** is one of: `held` (mechanism exists, runs, and its result
  supports the claim), `unproven` (mechanism exists and has produced no
  result yet), `contradicted` (mechanism exists and its result does not
  support the claim), `not built` (no mechanism anywhere), `queued`
  (mechanism written and not merged or not deployed).
- **Measured** is the number, with the date it was measured. Empty is a
  finding on its own.

## Where the numbers come from, and the one this register could not read

Added 2026-10-11, because the register spent its first eleven days believing
a constraint that had already been lifted.

Every rate-shaped and cadence-shaped claim in the table below is measurable
from one unauthenticated request, from any seat's sandbox:

```bash
curl -s https://libraryofalexandria.dev/api/delivery
```

The site reads Neon from its own environment and publishes the facts, which
is the design recorded in [delivery-health.md](delivery-health.md) and
shipped 2026-09-28 for precisely this reason: so that a seat with no
database credential can still read the state of the product. The fields that
answer claims on this page:

| Claim shape | Receipt field |
| --- | --- |
| the corpus grows, is current, is up to date today | `pipeline.claims_newest`, `pipeline.papers_newest` |
| an issue ships every week | `press.newest_week`, `press.created_at` |
| a stage is keeping up rather than backlogged | `queues.triage_pending`, `queues.distill_pending`, `queues.interpret_pending` |
| the deployed code is the committed code | the `deploy[]` array's `runtime_sha` and `first_seen_at` |

**Read `observed_at` as the measurement date** and put it in the Measured
column, because it is the receipt's own timestamp rather than the time you
happened to call it.

The cost of not having tried this earlier is one row. The ExO charter's §3g
told three consecutive runs that this seat has no `NEON_RO_URL` and must
therefore quote a corpus number from whichever run last measured it. That
is true of the database and false of the facts. "The library grows every
day" sat at `held` on a count taken 2026-09-29 while the claims table went
four days without a row, and the number that falsifies it was published
hourly on the org's own public endpoint the whole time. **The register that
holds the claim and the register that holds the number are both this seat's,
and nothing had ever read one against the other.**

So the standing rule for this page: a row whose claim is about a rate is
re-measured from the receipt every run, and a row that cannot be measured
from the receipt says which run measured it. Never both.

## The table, 2026-09-30

| Claim | Where | Mechanism | State | Measured |
| --- | --- | --- | --- | --- |
| "proven against the same tasks with and without it" (skills) | `site/app/mission/page.jsx:30` | `tools/skill_eval.py`, per-skill `evals/evals.json` | **contradicted** | 1 of 6 skills measured, 2026-09-30: 5.4 without against 5.3 with. The harness and five of the six suites are on unmerged branches |
| "revised when the research sharpens it" | `site/app/mission/page.jsx:31`, `site/app/llms.txt/route.js:30`, `site/app/pricing/page.jsx:35` | `pipeline/skill_revision.py` and the `skills_needing_revision` view | **queued** | 0 revisions ever fired. The view has never returned a row because `promotions` is empty. This is the precedent claim, ADR-36 |
| "retired with an explanation when it is overturned" (skills) | `site/app/mission/page.jsx:31`, `site/app/llms.txt/route.js:30` | none for the trigger. `SkillLibrary.jsx:111` renders a non-active status word | **not built** | 0 skills retired. There is no field for the explanation and nothing sets the status |
| "keeps every skill current at the pace of the research" | `site/app/skills/page.jsx:31` | same as revision, plus a freshness number that does not exist | **not built** | no skill freshness metric is computed or published anywhere. The staleness flag on the page is about the trigger-test bundle, not about the research |
| "agents that work from the current state of the evidence today and still will next month" | `site/app/skills/page.jsx:31` | a forward guarantee, so it needs the revision job deployed and a published lag | **not built** | five of six skills are at `version: 1` and none has ever been revised by a mechanism. The "today" half also fails on the corpus as of 2026-10-11: see the growth row |
| "every finding is linked to the findings that support, refine, or contradict it" | `site/app/mission/page.jsx:21` | `pipeline/interpret.py`, `claim_links`, bounded by `docs/product/graph-quality.md`, audited by `tools/graph_audit.py` | **contradicted on "every"** | last measured 2026-09-29: 545 of 846 claims waiting on interpret, edged frontier at claim id 301. The mechanism is real and it covers a minority |
| "the graph shows what confirmed it, what narrowed it, and what has contradicted it" | `site/app/graph/page.jsx:28` | same as above | **contradicted on the universal reading** | same numbers. True of an edged claim and false of most claims |
| "every finding in it carries its evidence" | `site/app/page.jsx:40` | the `claims`-to-`papers` foreign key, and the provenance block on every skill | **held** | every claim row has a paper. This one is sound and worth saying plainly |
| "replaced when newer work overturns it" (findings) | `site/app/page.jsx:40` | `pipeline/weekly.py` computes a `deprecated` section per issue from `contradicts` edges | **reports, does not replace** | 7 deprecated claims known. The issue tells the reader. Nothing changes the finding in the corpus |
| "the last trigger test that judged it", "when it was last checked" | `site/app/components/SkillLibrary.jsx`, `site/lib/skill-provenance.js` | `skills/_validation/trigger_test.py`, bundles sha256-matched to the skill text | **held** | 27 of 27 cases, 2026-09-30 bundle. The strongest receipt on the site, and the one that is easiest to mistake for evidence of value |
| "the library grows every day" | `site/app/page.jsx:40` | the daily distill cron | **contradicted**, moved from `held` 2026-10-11, and the mechanism is a **stopped job rather than a widening gap** | re-measured 2026-10-25T23:32:50Z: `claims_newest` still 2026-10-22T15:15:02Z, so **3.35 days** with no new claim, against 1.35 days two days ago. `distill_pending` is **3,680, the same integer as the 2026-10-23 reading**, and `papers_newest` is 2026-10-23T11:02:42Z at 2.52 days, so ingest stopped too. A backlog that grows means a job that cannot keep up; a backlog frozen to the digit beside a frozen newest means **a job that is not running**. The engineer seat has the cause and it is not a pipeline defect: the Modal workspace has been off since 2026-10-23, recorded in `docs/agents/engineer-run-note-2026-10-25-message.md`. Prior readings: 0.87 days and 2,559 pending on 2026-10-18, 1.35 days and 3,680 on 2026-10-23 |
| **"Each week the library becomes an issue"** | `site/app/page.jsx:40`, `site/app/library/page.jsx:29`, `site/app/llms.txt/route.js:10`, `site/app/pricing/page.jsx:29` and `:39` | `pipeline/weekly.py` on its Modal schedule | **contradicted on the record, cadence resumed** | re-measured 2026-10-23T23:44:17Z: `press.newest_week` is `2026-W42`, `created_at` 2026-10-19T09:02:52Z, which is two minutes after its schedule. The press fired on time for the first week since `INC-2026-10-12-the-press-had-no-degraded-path-and-the-week-got-no-issue`, and 4.6 days have passed since that issue with the next due 2026-10-26 09:00Z. The row stays contradicted because 2026-W41 was missed and was never made up, so the claim is false about the record even though it is currently true about the clock. First measured 2026-10-18T12:07:22Z at 13.1 days. **Re-measured 2026-10-25T23:32:50Z and unchanged**: still `2026-W42` created 2026-10-19T09:02:52Z, now 6.60 days old with the next due 2026-10-26T09:00Z, about nine hours after this reading. So the clock has not yet missed and the row's verdict is unchanged, but the press is the one stage whose input the stalled workspace feeds, which makes the 2026-10-26 slot the thing to read first |
| **"N papers read this week"**, the home page metric line | `site/app/page.jsx:43`, number from `site/lib/metrics.js` | `weeklyIngestCount()` over `INGEST_COUNT_URL`, whose `papers_ingested` field is `count(*) from papers where fetched_at > now() - interval '7 days'`, the same statement `pipeline/weekly.py` `gather()` uses | **contradicted on the verb, and dark on the live site** | measured 2026-10-23T23:44Z against the deployed page, not against the source: `curl -s https://libraryofalexandria.dev/` returns 200 with the paragraph directly above the metric present and **no `metric-line` element at all**, so `weeklyIngestCount()` is returning null in production and no reader is being shown this claim. The last reading with a number is 2026-09-26: 4,243 papers arrived in seven days against 55 read in full. The repair has been drafted since that day in `docs/voice/home-metric-line-2026-09-26.md` and is 27 days unset, which is `INC-2026-10-18-a-drafted-copy-repair-sat-unset-for-twenty-two-days` |

## The row this register promised itself and did not have, added 2026-10-18

The field map above has said "an issue ships every week → `press.newest_week`"
since 2026-10-11. **There was no such row in the table.** The register named
the claim shape, named the field that measures it, and had no row to put the
number in, for seven days.

That is this page's own founding pattern turned inward. The whole argument
for the register is that the org had seats checking copy against taste and no
seat checking a claim against a mechanism. Here the mechanism was named, the
measurement was free, and the claim was on **five** public surfaces including
the pricing page, which is the one page where a reader is being asked for
money. `grep -rniE 'every week|weekly' site/app/ site/emails/` finds them in
one second and no run had ever run it.

So the sweep in `prompts/exo-agent.md` §3g gains a fourth step, and it is the
cheapest of the four. **Read the field map against the table.** Every claim
shape the map can measure needs a row, or the map is describing a capability
the register does not use. The two halves are both on this page and nothing
had ever read one against the other, which is word for word the sentence this
page already used about itself on 2026-10-11 regarding the growth row. Twice
in eight days is a pattern rather than an oversight, and the pattern is that
**a register with a method section and a data section grows a gap between
them**, because a run reading for claims reads the table and a run reading for
numbers reads the map.

## The claim nobody can see, added 2026-10-23

The home page's metric line came to this register as a handoff from the PM
seat, which found it while checking the writer's taste-gate pull request and
could not fill the row because this file is not its surface. That part worked
exactly as the org intends. The seat that saw the gap wrote it on the board,
named the mechanism it had checked, named the one thing it could not check,
and handed it here.

The one thing it could not check is the whole finding. Its words were that
`INGEST_COUNT_URL` might not be configured in the live deploy, and that this
is runtime state outside the checkout. It is, and it costs one command to
read:

```bash
curl -s https://libraryofalexandria.dev/ | grep -c 'metric-line'
```

It returns `0`. The page is served, the paragraph immediately above the metric
renders, and the metric does not, which means `weeklyIngestCount()` is
returning null in production and has been doing so for as long as anyone has
looked. The claim is in the repository and it is not on the internet.

**This is a third place a claim can fail, and the register only modelled two.**
A row until today could fail because the mechanism does not exist, or because
the mechanism exists and its result does not support the claim. Both of those
are properties of the repository, and every one of the twelve rows before this
one was scored by reading two halves of the repository against each other. A
claim can also fail because the surface that is supposed to carry it is dark,
and no amount of reading the repository detects that. `site/app/page.jsx`
contains the sentence. A reader does not receive it.

The lesson already has a number in the company standards and this register had
never applied it. **L-A16, configured is not in effect.** The sales seat's
`docs/sales/launch-gate.md` reached the edge of this on 2026-10-18 and stopped
in the right place, writing that if the variable is unset in production the
false verb is invisible, which is luck rather than a fix, and that a reading
taken from the repo cannot tell us which. It cannot. A reading taken from the
deployed page can, and nothing in this register told anyone to take one.

So §3g of `prompts/exo-agent.md` gains a fifth step, and like the fourth it is
the cheapest one on the list: **measure the live surface, not the source that
should produce it.** For every row whose Where column names a page, fetch that
page and confirm the claim is actually in the bytes a reader gets. Where it is
not, the row says so in the Measured column before it says anything else,
because the severity is different in both directions. A false claim nobody can
see is not urgent. A true claim nobody can see is a feature that is not
shipping, and the home page's one piece of telemetry is in the second category
once its verb is repaired.

**And the verb is still wrong, so the dark surface is currently load-bearing.**
The line says "read" over a count of papers that arrived, which is canon law
15, the owner's ruling of 2026-09-25. The repair was drafted the next day in
`docs/voice/home-metric-line-2026-09-26.md`, it is good, and it is 27 days
unset. If the variable were set tomorrow by someone fixing the metric, a false
sentence would go live on the first screen a stranger sees, and the person
setting the variable would reasonably believe they were turning on telemetry
rather than publishing a claim. That ordering is worth saying out loud in the
row and it is why this run did not simply file the finding as low severity.

Both halves belong to other seats. The words are the writer's to draft and the
frontend's to set, and the draft already exists. The variable is runtime
configuration and belongs to the engineer seat and the owner. This register
holds neither. What it holds is the sentence that says the two must land in
that order, and that sentence did not exist until today.

## 2026-10-24: the cause behind two contradicted rows is now known, it is on the owner's desk, and this register never named it

Every row in the table above is scored against a mechanism in this
repository, which is what this register was built to do. **Two of them are
currently failing for a reason that is not in this repository at all**, and
a reader of the table cannot see it.

**The reason, from the daily brief of 2026-10-24, in the owner's own
"Needs you" list:** "Modal has hit its spend limit, so alexandria's pipeline
and press cannot run until you raise it." The engineer seat put the same
finding on the company board on 2026-10-23 as "Compute: the Modal workspace
is switched off", and its pull request says every cron and the skills server
are down together.

**What that explains, and what it predicts.**

- *"the library grows every day"* is contradicted with `distill_pending` at
  3,680 and `claims_newest` 1.35 days old. The register has been recording
  the backlog widening for three measurements and attributing it to pace.
  It is not pace. The daily distill cron is a Modal schedule and Modal is
  off, so the number cannot improve by any amount of work inside this
  repository.
- *"Each week the library becomes an issue"* currently reads "contradicted
  on the record, cadence resumed", because 2026-W42 shipped on time on
  2026-10-19. **The next issue is due 2026-10-26 09:00Z and
  `pipeline/weekly.py` runs on the same disabled Modal schedule.** So this
  row is on track to fail a second time, in two days, for the same reason
  2026-W41 was missed, and the thing that would prevent it is a spend limit
  only the owner can raise.

**The register's own shape is the finding here.** Columns 3 and 4 are
*mechanism* and *state*, and a mechanism is scored as present or absent in
the codebase. There has never been a column for whether the platform the
mechanism runs on is switched on. A claim can therefore be marked
"contradicted" with a perfectly accurate number for three consecutive
measurements while the actual cause sits unnamed in a different company's
billing page. That is the 2026-10-23 lesson about the dark home-page metric,
one layer down: **the first reading was "is the claim in the repository", the
second was "is the claim on the internet", and the third is "is the machine
that produces it running".**

So a row whose mechanism is a scheduled job carries the platform's state
beside it from now on, and the check is one line of the receipt rather than
a new instrument: a `pipeline.*_newest` that has not moved in more than one
cron interval means the platform and not the pace. Where that is true, say
so in the Measured column and name who can fix it, because for a disabled
account that is never a seat.

**This is not a prediction this register gets to make quietly.** It goes in
the ExO pull request under the owner's heading, because the window to act is
two days and the act is hers.

## What this table says as a whole

Thirteen claims, recounted from the table 2026-10-23. **Two hold.** Four are
contradicted outright by our own measurement and two more are contradicted on
their universal reading. Three have no mechanism at all. One is waiting on
code that is written and not merged, and one reports a problem instead of
acting on it.

**This paragraph said "three hold" until 2026-10-18, and it had been wrong
since 2026-10-11**, because the run that moved the growth row out of `held`
updated the row and not the count. That was the third instance in eight days
of the same gap, after the growth row's stale number and the missing weekly
row, and all three are the same mechanism: this page has a method half and a
data half and a summary that counts the data half, so a run editing one of the
three does not see the other two. The fix is the fourth step added to §3g
above, and the fix for this specific sentence is to recount from the table
every run rather than to adjust it.

### The distribution sentence was the fourth instance of the same gap

Added 2026-10-23. Until today the paragraph below this one read, in bold,
**"every claim that holds is about the corpus, and every claim that fails is
about the skills."** It was written on 2026-10-18 and the table it claims to
summarise already falsified it on the day it was written. The growth row was
moved out of `held` on 2026-10-11 and the weekly-issue row was added as
`contradicted` on 2026-10-18 itself, and both of those claims are about the
corpus. The new row added today is about the corpus too, and it fails.

So the page has now produced the same defect four times in twelve days, and
the fourth time it was in the sentence the page itself calls the single most
useful one on it. That is worth stating as a property rather than as a lapse.
**A summary sentence is a measurement with no date on it.** Every number in
the table carries the moment it was taken, which is what lets a reader
discount a stale one. The prose underneath carries no date at all, so it reads
as current forever and it decays silently from the day it is written. The
three earlier instances were all read as bookkeeping slips. Four is the shape.

The fix is not another reminder to recount. It is that **every claim this page
makes about its own table is dated in the same sentence**, the way every row
in the Measured column is, so a reader can see the age of a conclusion without
re-deriving it. The counts above now say "recounted from the table
2026-10-23". The replacement for the distribution sentence says its date in
its own first line.

### What the distribution actually shows, 2026-10-23

The honest version is narrower and it is still worth having. **Every claim
that holds is about the corpus, and no claim about the skills holds.** The
reverse does not follow: three corpus claims fail as well, and the newest of
them fails at the surface rather than in the machinery. The skills half has no
claim in `held` and five of its six claims have either no mechanism or a
mechanism that contradicts them, which is the original finding and it survives.
What does not survive is the implication that the corpus half is sound. It is
measured, which is a different thing, and the measurements have been going the
wrong way for two weeks.

That is still a finding no seat could produce from inside its own lane,
because the writer sees copy, the skill seat sees skills, and only a pass over
the claims together shows which half of the product is carrying the other.

## The rule this register enforces

**A new quality claim does not ship before its mechanism is named in this
file.** Not built is an acceptable state to ship in, when the claim is
honestly hedged the way `routines/page.jsx` hedges "once they ship". What is
not acceptable is a flat present-tense claim with an empty mechanism column,
because that is the 2026-09-18 skills copy again.

Five things follow each ExO run. The authoritative list is §3g of
`prompts/exo-agent.md` and this is its summary, so when the two disagree the
charter wins and the run that noticed fixes this copy in the same pull
request. **It said "three things" until 2026-10-23**, by which date the
charter had four and this run made five, which is the method-half-and-data-half
gap this page keeps producing, this time across two files instead of within
one.

1. Re-read the surfaces for claims added since the last run. `site/app/`,
   `site/app/llms.txt/route.js`, the emails under `site/emails/`, and any
   launch copy the sales seat has drafted.
2. Re-measure the numbers in the Measured column from the delivery receipt,
   or say which one could not be re-measured and why. A number with no date
   is the beginning of the same failure.
3. Move any row whose mechanism landed, and say in the learning log which
   way it moved. A row going from `queued` to `held` is the org paying a debt
   and it should be visible. Recount the summary paragraph from the table in
   the same edit.
4. Read the field map above against the table. Every claim shape the map can
   measure needs a row.
5. Fetch the live page for every row whose Where column names one, and
   confirm the claim is in the bytes a reader gets. L-A16, configured is not
   in effect.

## What is deliberately not here

Mission statements and positioning. "Accelerate every builder and agent to
frontier speed" is a purpose, not a claim about an artifact, and gating it
would make this file a copy review. The test is whether a reader could ask
"how do you know" and expect a number.

## The 2026-10-25 sweep, on the owed weekly cycle

Receipt read live and cache-busted twice at 2026-10-25T23:32:50Z and
2026-10-25T23:32:52Z. `observed_at` advanced between the two reads, so the
surface is live rather than cached and the frozen numbers below are the
pipeline's and not the receipt's.

**One row's state is unchanged and its diagnosis was wrong, which is the
finding.** The growth row has read `contradicted` since 2026-10-11 and every
sweep since has explained it as a backlog the distill job cannot keep up with.
The 2026-10-23 sweep put a number on that reading: 3,680 pending, "44% larger
than it was", "gap widening again". Two days later `distill_pending` is
**3,680 again, the same integer**, and `claims_newest` has not moved at all.

**A backlog depth read once cannot tell a job that is behind from a job that
is off, and the two have opposite fixes.** Behind is a capacity problem and
you tune the pacing, which this org has done three times. Off is an
availability problem and you turn something on. The discriminator is free and
it is a second reading: a number that grows is a job running too slowly, and a
number frozen to the digit beside a frozen `newest` is a job not running.

That is **precondition 6 of the ExO charter's §0** arriving in this register,
and it is the sharpest instance of it yet, because the misleading reading was
not a null or an absence. It was a real measurement, taken carefully, of a
real backlog, which happened to be the same number for two different reasons.
A single depth reading reads the same whether the news is "slower than we
hoped" or "stopped".

**The cause is known and it is not ours to re-derive.** The engineer seat
found it the same day: the Modal workspace has been off since 2026-10-23, and
its run note says so plainly. The ExO charter's §2 says to read that seat's
recent work for machinery findings before re-deriving them, so this sweep
cites it rather than repeating it. What this register adds is that the public
claim has been false for 3.35 days for a reason nobody reading this page would
have guessed from the page.

**The rule this adds to `docs/agents/registers.md`.** The existing rule is
that every sentence a register writes about its own data carries the date it
was written. That is necessary and it was obeyed here: the 2026-10-23 sentence
carried its date and was still misleading, because a dated conclusion can be
dated and wrong about the mechanism. So the companion rule, for any row whose
measured column is a **queue depth or a backlog**: record the previous reading
beside the new one in the same cell, because the delta is the evidence and a
single depth is not. The growth row above now carries all three readings and
any future sweep can see at a glance which of the two failure modes it is in.

**The other rate-shaped rows, re-measured against the same receipt.**

| Row | Reading at 2026-10-25T23:32:50Z | Moved |
|---|---|---|
| "the library grows every day" | `claims_newest` 2026-10-22T15:15:02Z, 3.35 d; `distill_pending` 3,680 | state unchanged, **diagnosis corrected** |
| "Each week the library becomes an issue" | `press.newest_week` 2026-W42, created 2026-10-19T09:02:52Z, 6.60 d, next due 2026-10-26T09:00Z | no, and the clock has not yet missed |
| a stage is keeping up rather than backlogged | `triage_pending` 119, `distill_pending` 3,680, `interpret_pending` 0 | the `interpret_pending: 0` the engineer seat acted on is still zero |
| the deployed code is the committed code | `deploy[]` present, `distill` `recorded_at` 2026-10-22T15:00:19Z | already failing per the engineer's 2026-10-24 note, unchanged |

**And one thing this sweep did not do, named rather than implied.** Step 5 of
§3g requires fetching each page whose claim is in the Where column and
confirming the claim is in the bytes a reader gets. That was not done this
run, which spent its budget on the refusal-class finding and the cadence test.
The last such pass was 2026-10-23 on the home page metric line, and it found
the metric rendering nowhere. So the live-surface half of this register is two
days stale and the next run owes it.
