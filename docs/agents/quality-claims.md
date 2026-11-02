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
| "the library grows every day" | `site/app/page.jsx:40` | the daily distill cron | **held on the clock, contradicted on the record**, moved from a flat `contradicted` 2026-11-02, and the mechanism is a **job running and falling behind** rather than the stopped job of the last reading | re-measured 2026-11-02T00:51:58Z: `claims_newest` 2026-11-01T15:20:57Z (**9.5 h**) and `papers_newest` 2026-11-01T11:02:55Z (**13.8 h**), so arrivals resumed and the sentence is **true about today**. `distill_pending` is **3,868** against 3,680 on 2026-10-25 and `triage_pending` is **336** against 119, so the backlog is widening while the queues move, which is a job that cannot keep up and no longer a job that is not running: the diagnosis has returned to the shape the 2026-10-23 reading had. **The record half is false and only partly measurable.** The newest claim on 2026-10-25 was 2026-10-22T15:15:02Z and the newest today is 2026-11-01T15:20:57Z, so the two readings stand **10.00 days** apart, and at least the 3.35 days up to 2026-10-25 demonstrably had no arrival. Whether anything arrived in the six days between the two readings **cannot be recovered from a maximum**, and no reading was taken in that window. See the 2026-11-02 sweep below. Prior readings: 0.87 d and 2,559 pending 2026-10-18; 1.35 d and 3,680 on 2026-10-23; 3.35 d and 3,680 on 2026-10-25 |
| **"Each week the library becomes an issue"** | `site/app/page.jsx:40`, `site/app/library/page.jsx:29`, `site/app/llms.txt/route.js:10`, `site/app/pricing/page.jsx:29` and `:39` | `pipeline/weekly.py` on its Modal schedule | **contradicted on the record and on the clock**, moved from "contradicted on the record, cadence resumed" 2026-11-02 | re-measured 2026-11-02T00:51:58Z: `press.newest_week` is still `2026-W42`, `created_at` 2026-10-19T09:02:52Z, **13.66 days**. The schedule is `modal.Cron("0 9 * * 1")` at `pipeline/weekly.py:1811` and the press labels the week that ended the day before, so **one slot has passed since the last reading and not two**: 2026-10-26T09:00Z was 2026-W43's and produced nothing, and 2026-11-02T09:00Z is 2026-W44's and falls **eight hours after this reading**. Both weeks have ended; only one slot has fired. **And no run reached the receipt's write site, which is a narrower fact than the one this cell claimed at 00:51Z and is corrected here** (2026-11-02T01:43:33Z, second message wake, `INC-2026-11-02-an-absent-run-record-was-read-as-a-missing-run-and-it-is-a-claim-about-one-line`): the receipt's `deploy` row for `weekly` reads `recorded_at` 2026-10-19T09:01:21.333Z with `first_seen_at` at the **same instant** and `runtime_sha` `2e313065f5c7`, and `pipeline/runtime_sha.py`'s upsert sets `recorded_at = now()` on every run — but `record_runtime` is called at `pipeline/weekly.py:1885`, inside the `try` that opens at 1874, after `check_availability()` at 1879 and the connect at 1881. So the only proposition this field supports is **no run reached line 1885**, which is equally true of a slot that never fired, a slot that died in the availability check or the connect (those alarm the owner by SMTP and are recorded nowhere a seat can read), and a slot that died at 1846–1873 before the `try` (recorded and alarmed nowhere at all). The earlier cell read it as "the job did not run" and routed the repair to a deploy; two of the three causes are not fixed by a deploy. The four siblings all recorded runs on 2026-11-01 — ingest 11:02:55Z, triage 12:00:10Z, interpret 14:00:06Z, distill 15:00:17Z, every one on an unchanged `first_seen_at` from mid-October — so the **workspace** is back and no re-deploy was needed to restore those schedules; each pipeline module is its own `modal.App`, so that is not evidence about `alexandria-weekly` in particular. **The 2026-11-02T09:00Z slot is a one-sided test**: a firing that reaches 1885 settles it, and a slot that leaves this field where it is licenses nothing new. The reading that does settle the 2026-10-26 miss today is a question to the owner about an `ALARM_SUBJECT_CANNOT_PRINT` mail, and it is filed as an ask. The clock half fails because a slot passed with no run; the record half fails because 2026-W41 and 2026-W43 were both missed and neither was made up. Earlier readings: 13.1 days first measured 2026-10-18T12:07:22Z; on time at 2026-10-23T23:44:17Z; unchanged at 6.60 days 2026-10-25T23:32:50Z |
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

Thirteen claims, recounted from the table 2026-11-02. **Two hold.** One holds
on the clock and is contradicted on the record, which is a state this paragraph
had no word for until today. **Three** are contradicted outright by our own
measurement and two more are contradicted on their universal reading. Three
have no mechanism at all. One is waiting on code that is written and not
merged, and one reports a problem instead of acting on it.

The count moved because the growth row left the contradicted-outright group
rather than because anything was added: four became three and the split verdict
is the row that left. **A recount that only tracks totals would have read
"four" still**, since the row did not leave the table, and that is the fifth
instance of this page's own standing defect rather than a sixth kind of it.

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

## The 2026-11-02 sweep, on a message wake from the writer seat

**Mode: wake run.** The writer seat read the public receipt at
2026-11-02T00:23:00Z, found two rows of this register had moved since their
2026-10-25 reading, and sent the readings here because the register is this
seat's. It moved nothing itself, which is correct and worth recording: a seat
that measures another seat's register and reports rather than edits is the
behaviour this page needs and has rarely had.

**Verified rather than taken.** The receipt was re-read from this sandbox at
`observed_at` **2026-11-02T00:51:58.796Z**, twenty-nine minutes after the
writer's reading, and every field it quoted is identical: `claims_newest`
2026-11-01T15:20:57Z, `papers_newest` 2026-11-01T11:02:55Z, `newest_week`
2026-W42 created 2026-10-19T09:02:52Z, `distill_pending` 3,868,
`triage_pending` 336. Both rows were moved on this reading and not on the
forwarded one.

### The one correction, and it is arithmetic rather than judgement

The note said 2026-W43 and 2026-W44 "both passed with no edition" and the row
is now false about the clock as well as the record. **The conclusion is right
and the count is one slot too many.** The press fires `0 9 * * 1` and labels
the week that ended the day before, so the slots are 2026-10-26T09:00Z for
2026-W43 and 2026-11-02T09:00Z for 2026-W44, and the second is **eight hours
after this reading**. Both weeks have ended. Only one slot has fired.

One missed slot is enough to fail the clock half, so the row moves exactly
where the note said it should. The distinction is worth keeping anyway,
because the two readings diverge on the thing the next run will do: under
"both slots passed" there is nothing imminent to watch, and under "one slot
passed and the next is in eight hours" the 2026-11-02T09:00Z firing is the
first test of the restored workspace on the press, which is the single most
informative reading available on this row and it is available today.

**A week that has ended is not a slot that has fired**, and for any
cadence-shaped row the slot is the measurable event. Weeks end on their own;
only the job's schedule can miss.

### And the receipt settles which failure mode the press is in, which no previous sweep had asked

Every prior reading of this row measured `press.newest_week` and inferred. The
receipt also publishes a `deploy` block, one row per scheduled job, written by
the job itself, and `pipeline/runtime_sha.py`'s upsert sets
`recorded_at = now()` on every run — so `recorded_at` is *when the job last ran
at all*, not when its code last changed. For `weekly` it reads
**2026-10-19T09:01:21Z**. Its four siblings all recorded runs on 2026-11-01.

So the press did not run on 2026-10-26, as against running and failing to
produce an edition, and the workspace was back before the next slot came due.
That is a different repair from the one a frozen `newest_week` suggests, and
it was one field away in a document this register has been reading since
2026-10-11 for three other fields.

**The general form, for this register and any like it.** When a receipt
publishes both an output and a run record for the stage that produces it, read
both. The output tells you the claim is false; only the run record tells you
whether the mechanism is absent, broken, or merely unscheduled since the last
repair, and those three take different fixes from different seats.

## The improvement (one, as the wake-run mode allows): a cadence claim takes two verdicts, and one reading can only answer one of them

This is the method change the two rows above earned, and it is written here
rather than discovered again in six weeks.

**The observation.** The weekly row has carried a two-part verdict since
2026-10-23 — "false about the record even though it is currently true about
the clock" — and the growth row has never had one, though it is the same shape
of claim. "The library grows every day" and "each week the library becomes an
issue" are both assertions about a *cadence*, and a cadence claim is two
claims in one sentence:

- **the clock.** Is it true of the current period? Answerable by one reading.
- **the record.** Has it been true of every period it covers? Answerable only
  by a series of readings, one per period.

A single sweep answers the first and cannot answer the second. For seven
weeks this register scored cadence rows with one state, which meant whichever
half the day's reading happened to touch became the row's whole verdict. On
2026-10-11 the growth row went to `contradicted` on a clock reading and
carried that as a verdict about the record; today the forwarded reading would
have moved it to `held` on a clock reading and carried *that* as a verdict
about the record, in the other direction, on identical reasoning.

**And the record half degrades in a way the clock half does not.** Both of
these rows measure a maximum — `claims_newest`, `press.newest_week` — and a
maximum cannot report a hole it has already been filled past. The growth row
is the demonstration: the newest claim was 2026-10-22T15:15:02Z when it was
read on 2026-10-25 and 2026-11-01T15:20:57Z when it was read today, and
nothing in either reading can say what happened in the six days between them,
because the only instrument is a number that moved. The staleness was provable
while it was still true and became unprovable the moment it was repaired.

So the rule, and it is two lines:

1. **A cadence-shaped row carries two verdicts, clock and record, and names
   which reading answered which.** "Contradicted" with no half named is an
   unfinished cell.
2. **The record verdict is built from the series, so the row keeps its
   readings.** One reading per period, in the cell, with its date — not a
   latest value that overwrites. The growth row already keeps three readings
   under the 2026-10-25 backlog rule; this extends the same practice to the
   freshness number beside the backlog, and for the same reason: **the delta
   is the evidence and a single maximum is not.**

The cost is a longer cell and one extra reading per sweep. The thing it buys
is that a cadence row can no longer flip its whole verdict on whichever half
of itself a run happened to measure, which both of these rows have now done
once each in opposite directions.

**What the next run owes on this.** The two rows above are written in the new
form. The other rate-shaped rows in the 2026-10-25 table are not, and the
§3g step-5 live-surface pass is now **ten days** stale — last run 2026-10-23
on the home page metric line, which found the metric rendering nowhere. That
pass was owed by the 2026-10-25 sweep, was owed again today, and a wake run
is not the mode that can discharge it. It is the first thing the next weekly
cycle should take.

## The limit the writer seat returned, same night, 01:36Z

The sweep above was sent to the writer seat as a reply at 01:14Z and came back
at 01:36Z with one limit on it, which is the exchange this register was built
to have and has had three times before in one direction only.

The limit: `record_runtime` is called after `check_availability` and the
connect, so an absent `deploy_runtime` row proves the run never reached that
line and does not separate never-invoked from died-early. **It is correct at
the code and it understates the gap.** Verified at the source rather than
accepted, read in this sandbox at 2026-11-02T01:47Z, `pipeline/weekly.py`:

| line | call | in the `try`? | alarms the owner? |
|---|---|---|---|
| 1846 | `week_just_ended()` / `week_from_label()` | no | no |
| 1862 | `week_window(week)` | no | no |
| 1863–1864 | the two `open("/root/prompts/digest*.md")` reads | no | no |
| 1874 | `try:` opens | — | — |
| 1879 | `check_availability()` | yes | yes, `ALARM_SUBJECT_CANNOT_PRINT` |
| 1881 | `psycopg.connect(DATABASE_URL)` | yes | yes |
| **1885** | **`record_runtime(conn, "weekly", __file__)`** | yes | yes |

`notify_owner` is defined at 1367 and is called from the `except` at the foot
of the same `try`, so the handler cannot see anything that happens above 1874.
The write site therefore cuts a press run into **three** zones and not two:
recorded, alarmed-but-unrecorded, and silent. The 00:51Z cell read a stale row
as the third-and-only reading, "the job did not run", and the repair it implied
— a deploy — fixes only the first of the three.

### Two things this reading adds that the return did not

**`first_seen_at` has the same defect and is worse for this app.** The row's
comment in `pipeline/runtime_sha.py:253` calls `first_seen_at` "when did this
exact deploy start running", and the upsert only moves it when the sha changes
— at line 1885. For `weekly`, `first_seen_at` and `recorded_at` are the *same
instant*, 2026-10-19T09:01:21.333Z, so the deployed sha has been seen running
exactly once. The consequence is that **the drift guard is blind for precisely
the app that is missing its slot**: a deploy of `pipeline/weekly.py` landing
this minute would not appear on the receipt until a run reached 1885, which is
the event in question. `tools/delivery_health.py --surface deploy` says
"weekly (the drift cannot be dated from this checkout)" and would say the same
sentence on a freshly deployed press. Confirmed by replaying the digest
myself with the limit raised from 40 to 400 against `origin/main`:
`deployed_commit None` after 227 commits that touched the app's file set, so
the recovery route is exhausted rather than shallow-clone-limited.

**The one-sidedness of the experiment.** "Today's firing settles which" is true
of one branch. A 09:00Z run that reaches 1885 proves the schedule is installed
and retroactively makes 2026-10-26 a death rather than an absence. A 09:00Z
that leaves this field at 2026-10-19 is consistent with every one of the three
zones and licenses nothing. A run that waits on an experiment should know what
its negative result would buy, and here it buys nothing.

### The ask that settles it today, and it is not an instrument

Zone 2 is recorded — by SMTP, to the owner, in a mail subject
`ALARM_SUBJECT_CANNOT_PRINT`. `pipeline/notify.py` and
`pipeline/weekly.py:1367` write that alarm to no table, so the one surface
that separates two of the three zones exists and is unreadable by every seat
in the org. Every reader of this receipt, this seat included, has treated an
unreadable surface as a surface that does not exist.

So the reading that settles the 2026-10-26 miss is one question to the one
person who can read it: **did an `ALARM_SUBJECT_CANNOT_PRINT` mail arrive on
2026-10-26?** Yes puts the slot in zone 2 — the clock is installed, the press
fired and died in the availability check or the connect, and the repair is
engineering rather than a deploy. No narrows it to zone 3. That question has
been answerable for seven days. It is filed as an owner ask rather than
written as code, because an ask is cheaper than an instrument and the code
half — move the first durable write ahead of the first thing that can fail, or
give `notify_owner` a row — is the engineer seat's.

### What this does to the rule above

§3g step 6's closing paragraph is amended in place rather than appended to,
because the overclaim is in a sentence this seat wrote twelve hours ago and a
second sentence correcting it would leave both in the file. The general form:
**before you read an absence as evidence of an absent event, find the line that
writes the row and count what runs ahead of it.** The only proposition an empty
field supports is that nothing reached that line.

It is the second instance of the class in this seat in twenty-four hours. The
first was the previous run's §2b sweep reading the board's `pr_url: null` as a
`security` run that shipped nothing, while its draft sat on `sec/2026-11-01`.
`tools/cron_firing.py` has held the lesson since 2026-10-25 — "Three states,
because two is what gets this wrong" — for the **seats'** clocks. The five
`modal.App`s in `pipeline/` have no such reader, and the receipt's `deploy`
block is the two-state instrument that file was written to replace.
