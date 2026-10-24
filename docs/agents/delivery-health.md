# Delivery health — the product shipped, not just the runs passed

**Enforced at:** prompts/pm-agent.md §1f, every standup, daily. The ExO
seat audits the duty in §3b and owns this file.

Written by the ExO agent on 2026-09-24, on the owner's order after
incident 24. It names the standing guardrails for anything this org
ships on a schedule, and it fixes the definition error that let a week
pass with a green fleet and no newsletter.

## The definition error

Every health check this org keeps reads `gh run list`. That covers
twelve agent workflows and none of the things the org actually ships.
The newsletter runs on a Modal cron. The site is a static deploy. The
MCP server is a long-running process. All three are outside GitHub
Actions, so all three were invisible to every seat's run-health duty,
including the PM's §1f, which is the duty that exists so the owner never
finds a failure herself.

On 2026-09-21 the press did not print. Every Actions run that week was
green, so every report the org produced was accurate and every one of
them was useless. The owner found out from her own inbox three days
later. That is not a seat missing something in its lane. The product was
in nobody's lane.

So the org keeps two health surfaces from today, and the second one is
the one that matters to a reader:

- **Fleet health.** Did the agents run. Twelve workflows, `gh run list`.
- **Delivery health.** Did the product reach anyone. The press, the
  site, the MCP server.

A report that covers the first and not the second is incomplete, and
saying "all green" while holding only fleet evidence is the specific
error this file bans.

## The four guardrails

These bind anything the org ships on a schedule. Three of the four are
shipped for the press in PR #75, which is what makes them law rather
than proposals. They are written generally on purpose, because the site
and the MCP server have the same exposure and neither has been checked.

**1. Availability check, before the work and before the deploy.** A
scheduled job verifies that everything it depends on still exists,
before it spends twenty minutes producing something it cannot deliver.
For the press that is `GET /models` against the provider, which costs
nothing against any rate limit, run both at deploy time and at the top
of every scheduled run. The general rule: a dependency that can be
withdrawn by someone else gets checked at run start, and a check that
fails loudly beats a run that fails late. Note the distinction PR #75
gets right and which is easy to get wrong: a network failure must raise
rather than return an empty set, because "the request failed" and
"everything is gone" are the same value and very different facts.

**2. An ordered fallback list, every entry verified.** One provider, one
model, one endpoint is one point of failure however good it is. The list
is ordered, and it is ordered by the property that actually fails. PR
#75's reasoning is the standard: a production model outranks a preview,
because previews are withdrawn without notice, and the list spreads
across families, because three models from one vendor are one point of
failure wearing three hats. Capacity is the worst reason to pick a
model, which is exactly the mistake that put the press on
`groq/compound`. Every entry in the list is checked by the same guard
that checks the one in use, because a fallback nothing has measured is a
fallback that fails at three in the morning.

**3. Notify on failure, on every path that ends without a delivery.**
Not on exceptions, on outcomes. Any exit from a scheduled job that
produces no artifact for a reader raises an alarm to the owner,
including the path where the artifact was produced and then failed to
send, because to a reader those two are identical. The notifier never
raises, so a failed alarm cannot swallow the original error. It uses a
channel the job already has, which for the press is the Gmail path
`send_newsletter` already used, so a guardrail costs no new secret and
no new service.

**4. A delivery-health line in the daily standup.** The other three
guardrails tell the owner when a run fails. None of them tells anyone
when a run never happened, and incident 24's second and more serious
failure is exactly that: the Modal weekly app shows no log output at all
for 2026-09-21, and a job that never starts cannot notify anybody. Only
an outside observer catches a missing run. That observer is the PM's
daily standup, and the evidence is the artifact rather than the job: the
newest row in `digests`, the newest commit to the live site, a probe of
the MCP endpoint. Read the artifact, not the scheduler.

Guardrail 4 is what makes the other three complete, and it is the one
that was missing in every version of this org's monitoring until today.

## Why the artifact and not the scheduler

Incident 24 is the argument. `modal app logs alexandria-weekly` showed
nothing for 2026-09-21. No output is the same value for "the schedule
never fired" and "it fired and died before its first print," and the
Modal CLI does not expose schedule history, so the scheduler could not
answer the only question that mattered. The `digests` table could, in
one query, with no ambiguity at all: the newest row was 2026-W37 and the
week was W38.

Anywhere a scheduler and an artifact disagree, the artifact is the
evidence. A scheduler reports its own intentions.

## Guardrail 5, added 2026-09-27: the evidence has to be reachable

The four guardrails above say what to check. None of them asks whether
the seat that owns the check can get at the thing it is checking, and
that turned out to be the gap that mattered most, because it is the one
that produces an honest report of the wrong number.

**A guardrail is not in force until the seat that owns it holds the
credential its evidence requires.** Guardrail 4 names the newest row in
`digests` as the press's evidence and assigns the watch to the PM's
daily standup. `.github/workflows/agent-pm.yml` has never carried
`NEON_RO_URL`. Three seats do (research, writer, skill) and the seat
that owns the delivery check does not. The PM has said so in every
standup since: "No database credentials in this sandbox, so the
`digests` table itself was not queried," and then substituted the public
library page.

That substitution is not a small one, and the direction of its error is
the problem. The library page lists the issues the site has built. A
digest row written and never sent, a send that failed after the row
landed, and a page served from an edge cache all read as healthy on that
page, and those are exactly the three failures guardrail 3 exists to
catch. So the proxy is strongest precisely where the real check would
have been most useful.

The rule that follows, for whoever writes the next guardrail: **name the
evidence and the credential in the same sentence.** If the credential is
not in the owning seat's workflow, the guardrail ships as a queued
workflow change first and as a charter line second, and the surface
stays marked unwatched until the secret lands. A guardrail whose input
is missing is worse than an absent one, because it reports.

## The known state of each surface, 2026-09-27

| Surface | Trigger | Artifact to check | Guardrails 1 to 3 | Watched daily |
| --- | --- | --- | --- | --- |
| The press, weekly issue | Modal cron, Monday 09:00 UTC after PR #75 | newest row in `digests` | shipped in PR #75, unmerged at this writing | **named, not performed**: PM §1f watches it daily and has no `NEON_RO_URL`, so the site is read instead (guardrail 5) |
| The press, daily pipeline | Modal crons, 11:00 to 14:00 UTC, windows now checked by `budget.check_kimi_windows()` | newest rows in the corpus tables | budget guard only, no availability check | no, and this is still the next gap |
| The site | **the `deploy-main` hook, only when `site/**` changes on main** (HQ Incident 5, 2026-09-25) | newest commit live | **guardrail 3 unmet, see below** | no. **And the trigger has not fired since 2026-09-30 02:37 UTC**, see the 2026-10-04 note |
| The MCP server | long-running | a probe query | none | no, and incident 21 is what that costs |

### What changed under the site row, and why it is now the weakest

Until 2026-09-25 the site deployed on every merge, through Vercel's Git
integration. HQ Incident 5 took that away: seat branches were spending
the Hobby plan's 100 deployments a day and production builds were
refused for 24 hours. `site/vercel.json` now sets
`git.deploymentEnabled=false`, and `.github/workflows/deploy-main.yml`
fires the project's deploy hook on pushes to main under `site/**`.

That is the right fix for the quota and it introduced two silent paths,
neither of them recorded anywhere before this run.

**The hook's acceptance is not a build.** The workflow's only assertion
is that the POST returned 200 or 201. A deploy hook returns as soon as
the job is queued, so a build that fails afterwards leaves the workflow
green, `gh run list` clean, and production serving the previous commit.
This is the definition error at the top of this file, reproduced exactly,
in the runtime added the day after the file was written to prevent it.
Guardrail 3 wants an alarm on every path that ends without a delivery,
and this runtime has no notifier at all.

**The path filter decides what counts as a change to the site.** A merge
that changes what the site renders from without touching `site/**` does
not fire the hook. That is correct for the quota and it means the set of
files the site depends on is now load-bearing and written in one place
only, as a glob in a workflow the seats cannot edit.

Neither of these is an outage today and neither is the engineer seat's
to fix from where it sits. Both belong in the sprint, and the honest
statement until they are closed is that the site is the one surface
whose deploy reports success without evidence that anything deployed.

The rest of the table is the honest part. One surface is instrumented,
three are not, and the daily pipeline is the one that feeds everything
else. Closing those is engineer work and belongs in the sprint rather
than in this file, which is why it is written here as a finding for the
PM to groom rather than as an assignment.

## The standing question this file answers

Before any seat writes "all green" in a pull request description, it
answers this: green on what evidence, and did anything reach a reader.
If the second half is unanswered, the line says so.

## Guardrail 4 has a reader, 2026-10-01 (engineer seat)

The four guardrails above were written as law on 2026-09-24 and the fourth one
had no reader for a week. Its evidence is named exactly, "the newest row in
`digests`", and no agent seat holds a credential for that table, so every seat
ever asked whether the press printed reached for a proxy or answered `unknown`.
`tools/delivery_health.py` shipped on 2026-09-28 and made the gap legible rather
than closing it: two surfaces green, two `unknown`, exit status 2, and a message
naming the missing variable.

It is closed now, and not by distributing a credential. The site already reads
Neon from its own environment, so the site publishes the facts and every seat
reads them at `GET /api/delivery`, with no token and no secret anywhere in a
workflow. `site/lib/delivery-core.js` has the field-by-field rule that keeps the
issue body and the claim text out of it.

Three things a reader of this file should carry away rather than infer.

**The receipt carries facts and never verdicts.** It says the newest week is
2026-W39. It never says the press is broken. The judgement stays in
`tools/delivery_health.py`, in one copy, taking rows from either reader, because
two readers of one question is the shape that grows two answers. That is also
why a bad week reads as a date to a passer-by rather than as an alarm.

**Second-hand evidence says so.** Every surface reports `read_via` in its
evidence: `DATABASE_URL` when a connection answered, the receipt's URL when it
did not. A report that hides which one it had is the kind of report incident 24
was full of.

**A reader with no credential cannot write, and one guardrail needs to.** The
deploy-drift alarm keeps a once-a-day cooldown in `deploy_runtime.notified_at`.
Read through the receipt, a drift is reported in full and nobody is mailed, and
the surface says that in its own evidence. Mailing without a cooldown would be
one mail every time the standup runs.

What this does not close is the paragraph above about the site's own deploy. The
hook still returns 200 when a build is merely queued, and the receipt is now one
more thing that reaches production through it. The receipt could publish the
site's own build commit and make that measurable, which is in the ledger as a
proposal rather than here as a fact.

## Guardrail 6, added 2026-10-01 (engineer seat): the record and the page have to agree

The archive used to be files committed by hand. `site/lib/issues-live.js` makes
`/library` and every issue route read the `digests` table instead, so a Monday
send is public on Monday. It falls back to the committed markdown when it cannot
reach the database, which is the right way to fail and is exactly why the
failure needed a guardrail of its own.

**The rule.** When the site's environment cannot read `digests`, the archive
keeps serving the committed files and every surface in this file stays green.
The record path would be dead and nothing would say so. That is L-A16 in
`docs/standards/lessons.md` in its own words: the gap between intent and effect
is silent by construction, because a well-built fallback makes the run succeed
anyway. So the two answers are compared rather than trusted separately. The
press surface knows the newest week in `digests`. The site surface knows the
newest week a reader can open. Agreement between them is the only evidence that
the connection between them exists.

**The reader.** `python3 tools/delivery_health.py --surface archive`, a sixth
surface beside the five above. It derives its answer from the press and site
surfaces rather than from a read of its own, so it needs no credential the other
two do not already have, and it fetches both of them even when only `archive` is
asked for.

**What it will not call a failure.** A week the owner retired is not a gap:
`HIDDEN_WEEKS` is read out of `site/lib/content.js` rather than copied here, so
her veto over the archive lives in one place. And a week published by hand that
the record does not hold reads as the old path still working, with both weeks
named, because that is informative and not broken.

**What it costs to ignore.** The press can print perfectly and the archive can
show last month, and until this surface existed the org had no way to tell those
two apart from the outside.


## An amendment, 2026-10-08 (engineer seat): a guardrail that is wrong on a schedule

Both the press surface and the site surface judged the newest issue against the
week that had ended. That is the right question to ask the press, which prints
the week that ended, and the wrong question to ask a health check, which also
has to know whether the press has had its turn yet.

The press cron is `0 9 * * 1`. A week ends on Sunday night, so from Monday
00:00 UTC until the cron fires at 09:00 the week that has just ended correctly
has no row, and for those nine hours both surfaces reported a missing issue
every single week. Sprint 2026-10-05's item 4 is where it was first written
down: the press surface "reads FAILING on any Monday before the cron fires".

**The rule now.** `press_due_week` answers which issue the press is obliged to
have printed by a given instant, and that is what the verdict turns on. A week
inside its own window is `pending`, the surface names the issue it is waiting
for and the time it is waiting until, and the week that has ended stays in the
evidence as `expected` because it is still the honest answer to a different
question. The grace is two hours past the cron, because the scheduled run opens
a connection, calls a provider under a 1800-second timeout and then mails every
subscriber, so a run still going at 09:40 is a working press.

**What it does not forgive.** Only the one week whose deadline has not arrived.
An issue two weeks old is still a failure at 03:00 on a Monday, and so is an
empty `digests` table, because neither has a deadline the clock can excuse.

**Why it was worth a day.** Nothing here was broken in the press. The check was
wrong, on a schedule, in the quiet direction that costs the most: a surface that
cries wolf at a predictable hour teaches the seats reading it to discount what
it says, and guardrail 4 exists precisely so that a seat and not the owner is
the first reader of a failure. A false alarm every Monday is how that gets
unlearned. `PRESS_CRON` is the one copy of the press's schedule this file keeps,
so a test reads the decorator out of `pipeline/weekly.py` and pins it.

## 2026-10-04: the trigger that cannot fire, and the reason "all green" was true all week

**Added by the ExO seat, because this file's standing claim is that "all
green" is a statement about the product and not only about the runs, and
this week produced the cleanest example of the gap it was written for.**

The site's deploy trigger is `site/**` changing on `main`. The newest
commit touching `site/` is `5a90fb3`, pushed at **2026-09-30 02:37 UTC**,
and `deploy-main`'s newest run is a `success` at **2026-09-30 02:37 UTC**
for exactly that commit. **Both numbers are correct and the surface is five
days stale**, because nothing has merged to `main` since 2026-09-30 02:08
UTC and so the trigger's precondition has not occurred since. The
mechanism is not broken. It has had nothing to carry.

The PM's standup of 2026-10-04 reported `Site: ok, newest issue 2026-W39,
matches expectation`. That is accurate and it is not a contradiction, and
the reason is worth writing into this file because it is the shape every
future reader will hit. **The issue is data and the page is code.** The
weekly issue is written to the database by a Modal cron and rendered
dynamically, so a new issue appears on a five-day-old build. A check that
reads the newest issue is a check on the pipeline, and it reports healthy
while every editorial fix, every copy ruling and every frontend change of
the last five days is undeployed.

**The guardrail this adds, and it generalises past the site.** For any
surface whose deploy fires on a change rather than on a clock, the check is
two questions and not one.

1. Is the artifact current? The existing guardrails ask this.
2. **When did the deploy mechanism last fire, and is that the same date as
   the newest change it was supposed to carry?** A change-triggered deploy
   is indistinguishable, from the artifact side, between "nothing needed
   deploying" and "everything needs deploying and nothing can".

```bash
gh run list --workflow=deploy-main.yml --limit 3 --json conclusion,createdAt
git log origin/main -1 --format='%ci %h' -- site/
```

Same dates means current. The deploy older than the commit means a failed
deploy, which is loud. **The commit older than the queue is the quiet one**,
and it is the state this week was in: every pending change to the surface
sitting in a pull request, so the trigger is correct, the deploy is correct,
the artifact is stale, and no check in the org returns anything but ok. The
full account is `INC-2026-10-04-four-days-of-output-and-no-delivery`.

## 2026-10-09: a guard that answers to where you are standing answers green

**Added by the engineer seat, on the day this file's own deploy surface was
caught giving two different verdicts about one production image.**

`tools/delivery_health.py`'s deploy surface compared `deploy_runtime` against
the working tree and dated the drift from `HEAD`. Every seat in this org runs
on its own branch and commits inside the hour, so the question it was really
answering was "has this seat committed recently", and the answer was yes every
single time. Measured this morning, off one row, within the same minute:

```
on engineer/2026-10-09-...   ok       a deploy is pending and still inside
                                      the 24h window: triage (8.9h, 6 undeployed
                                      commits since c7ab0c8 ...)
in a clean main worktree     FAILING  the deployed code is not this code:
                                      triage is 3.9 days behind
```

Both ran the same command against the same database row. Six of those named
commits had never merged and never could be deployed; the real count is one.
The guard had been in this state since the day it shipped, and the only run
that ever saw past it was the one that re-measured by hand in a scratch
worktree and wrote the workaround into a ledger entry.

**The rule, and it is the general one.** A guard on production compares the
artifact against the trunk, never against the checkout it happens to be
running in. The deployable code is the code a hand can deploy, which is
`origin/main` and nothing else; a commit that has not merged has never been
inside an image, so including it in the comparison is not strictness, it is
noise that moves the verdict. The surface resolves `origin/main`, then `main`,
then `HEAD` for a repository with no trunk, and it prints which one it judged
in its headline and its evidence.

**Why this one is worth a section rather than a line.** The hazard was already
written down. The two questions above, added 2026-10-04, name `origin/main`
explicitly in their own shell snippet. `tests/test_deploy_drift.py`'s module
docstring listed "a branch carries commits that never merged" as one of three
cry-wolf cases and claimed each had a test; that one had neither a test nor a
line of code. The register was right, the test file said it was covered, and
nothing between either sentence and the artifact ever checked. That is
incident 20's shape, and the full account is
`INC-2026-10-09-the-deploy-guard-judged-the-branch-it-ran-from`.

The regression test is `test_a_branch_commit_does_not_reset_the_drift_clock`:
a trunk four days ahead of the deployed image, a branch commit a minute old,
and the two verdicts must match to the character.

## 2026-10-09, later the same day: a guard is only as wide as its list

The morning's section above is about a guard comparing the wrong two things.
This is the other way the same surface goes wrong, found hours later by
following the PM's dispatch on a real break, and it is the cheaper failure to
make and the harder one to see.

**What happened.** The pipeline surface read `FAILING`, "claims has not moved
in 2 days," while the papers surface stayed current through 11:01 UTC. So
ingest was working and the stage that turns papers into claims was not. The
deploy surface, asked in the same run, read `ok`.

Both were telling the truth. `pipeline/runtime_sha.py`'s `APPS` held three
entries, triage, interpret and weekly, and there are five scheduled jobs in
`pipeline/`. The two it omitted were `ingest` and `distill`: the stage that
fills `papers` and the stage that fills `claims`, which are the two columns
the pipeline surface judges. The guard watched the three jobs whose output no
other surface grades and was blind to both jobs whose output it grades itself.

The cost was a diagnosis rather than an outage. Six surfaces could see that
claims had stopped. None could see `distill`, because it was the only
scheduled job in the pipeline that left no trace of a run, so no seat could
distinguish a cron that stopped firing from a run against an empty queue from
a run that raised. That distinction is the whole of the next step, and
answering it needed Modal logs or a database credential, which no seat holds.

**The general rule. A job that runs unattended is watched, and the list of
what is watched is derived rather than kept.** The second clause is the one
that matters, because the first was never in dispute: nobody decided not to
watch `distill`. The list was written when three jobs existed and two more
were added beside it over the following weeks, and a hand-kept list of what to
watch has no moment at which it is wrong. `tests/test_deploy_drift.py` now
parses `pipeline/` for `modal.Cron` and `modal.Period` and fails when a
scheduled job is not in `APPS`, and fails in the other direction too, so the
guard cannot demand a deploy for a job that no longer has a schedule to be
behind on.

**And "never recorded" is a third state, not a stale one.** An app with no row
has told the guard nothing, so dating its drift from its last commit answers a
question nobody asked: it reports the age of the code as the age of the
deploy. `ingest` is the case that proves it, because it delivered papers this
morning and has never recorded a runtime in its life, and the old path would
have called a working job days behind. An app with no row now reads `unknown`,
says it is unmeasured rather than behind, and carries the `modal deploy` line
that fixes it. An empty table keeps reading as a failure, because that is a
recorder that has never worked rather than one app without coverage.

The three regression tests are `test_every_scheduled_app_is_watched_by_the_
drift_guard`, `test_every_watched_app_records_its_own_runtime`, and
`test_an_app_that_never_recorded_is_unmeasured_while_the_others_are_judged`.

## 2026-10-14 (engineer seat): "never recorded" was the wrong half of the right idea, and it cost two issues

The section above ends with a rule that is half correct, so this section
replaces that half rather than arguing with it. The correct half is that
dating an app's drift from its last commit reports the age of the code as the
age of the deploy. The wrong half is the conclusion, which was that an app
with no row is therefore unmeasured. No row has two causes and they are
opposites.

**The question is not whether a row exists. It is whether the code at the
trunk asks for one.** An app whose module calls `record_runtime` writes its
row on the first run of any deploy built from that commit. So no row means the
running image predates that commit, and the age of that commit is a lower
bound on the age of the image. That is drift, and it is datable without
guessing. An app whose module does not call `record_runtime` can never write a
row from any deploy, so the absence of one says nothing at all, and `unknown`
is the honest answer for that case alone.

`ingest` was the example the old rule was written around and it was the second
case by accident and the first case in fact. It had never recorded because the
deploy that would have recorded had not happened. Neither had `distill`'s. The
cost was seven days of no claims and two issues that did not print, because
the three merged fixes to the pacing that had stopped `distill` all landed
inside the window where this surface was saying `unknown` about it. The full
account is
`INC-2026-10-14-the-two-apps-the-drift-guard-could-not-see`.

**The general rule, and it is not about deploys.** A pending action parked in
a state that nothing escalates is indistinguishable from a pending action
nobody took. The 2026-10-09 entry closed with a section called "The part that
is still open" that named the two commands and was read by at least two seats,
and five days passed, because `unknown` gets quieter as it ages rather than
louder. A guard state that cannot grow into an alarm is a note, so put the
note in the register and leave the state to the thing that escalates.

What this surface does now: an app that has never recorded while its code asks
it to reads `failing`, dated from the commit that asked, with the `modal
deploy` line in its evidence and the commits inside the gap named in the
headline. An app whose code does not ask reads `unknown`. An app whose asking
commit is inside the grace window reads as a pending deploy, which keeps the
cry-wolf case the old rule was right about. The mail is withheld for the
failing case with its reason in the evidence, because the alarm's cooldown is
a column on the row these apps do not have, and that is worth closing: see
the ledger entry of 2026-10-14 for the schema change it needs.

The regression tests are `test_an_app_that_has_never_recorded_since_its_code_
asked_to_is_behind`, `test_an_app_added_to_the_guard_today_is_a_pending_
deploy_not_an_alarm`, `test_an_app_whose_code_never_asks_to_record_is_
unmeasured`, and `test_an_unrecorded_image_names_what_it_is_missing`. The
three the section above names are still there, under their own names, and one
of them was rewritten rather than kept: it asserted the reading this section
replaces, and it had never run, because it sat below its own file's
`__main__` block. `tests/test_ci_coverage.py` now fails when any test file
strands a test below that block.

## 2026-10-14 (engineer seat, second run): the press surface has a reader on the hour it matters

The amendment of 2026-10-08, four sections up, fixed the press surface's
clock. It gave the surface the press's own deadline, which is `PRESS_CRON`
plus `PRESS_GRACE`, so the nine hours of every Monday between midnight and
the cron stopped reading as a missing issue. The section that wrote it named
what it had not closed in its own words: "with nothing standing that
re-checks after the window closes".

That sentence was the whole cost of the next week. On Monday 2026-10-12 the
press cron started at 09:00 UTC, recorded its own runtime fingerprint, and
wrote no row to `digests`. The surface was correct about it from 11:00
onwards. Nothing asked. The gap sat undetected for eleven hours, until the
PM's weekly ceremony opened the receipt at 20:00 and found 2026-W40 still the
newest issue. Two days later, at 15:51 on 2026-10-14, the same week was still
missing, 52.9 hours past its deadline, and the company board carried nothing
about it.

**The schedule was the defect, not the judgement.** The only scheduled reader
of this file is the PM's daily standup, and on a Monday the PM runs the weekly
ceremony instead. The press is weekly, it can only fail on a Monday, and
Monday is the one day of the seven that nothing read whether it had.

**So guardrail 4 now has a second reader, and it writes.**
`tools/press_watch.py` calls `judge_press` rather than copying it, and when
the window has closed on an issue that was never written it posts a card to
the company board, which is the surface `docs/standards/pm.md` §14 makes the
state of the work. Its schedule is
`.github/workflows-pending/press-watch.yml`, daily at 11:00 UTC, waiting on a
`git mv` as item 21 of
[pending-workflow-changes.md](pending-workflow-changes.md).

Three properties of it are worth keeping if anyone rewrites it.

**The card is its own cooldown.** The due week is in the title, so a second
run on the same week finds its own card and writes nothing. That is what
makes a daily schedule post one card a week instead of seven, and a daily
schedule is the point: a Monday run GitHub skips under load is then caught on
Tuesday rather than next week. The deploy alarm in this file keeps its
cooldown in a column of the row it alarms about and this one has no row, so
the artifact it writes is the memory. A week that stays missing gets one
comment a day, dated from the newest comment the card already carries.

**A blind run posts nothing and still goes red.** When the receipt cannot be
read the tool exits 2 and creates no card, because an alarm it cannot support
is worse than silence, and a red scheduled run is the second channel. The
failure this is written against is the one directly above: a gate that saw
nothing reading as a quiet pass, which is company standard L-A21 and
`INC-2026-10-14-the-two-apps-the-drift-guard-could-not-see`.

**It reads the artifact, so it does not care whether the cron started.** The
press cron on 2026-10-12 did start and did record its fingerprint, which is
exactly the case guardrail 4's own opening section is about. A reader of the
scheduler would have called that Monday green.

**What is still open.** Nothing closes the card. The tool creates and
comments, and `pm.md` §14 lets a seat move an item, so a later run could move
a week's card to Done once the issue lands. It does not today, because the
first version of a guardrail that writes should do one thing and the thing
worth doing first is saying so out loud. Until then the card is closed by the
hand that sends the issue.

## 2026-10-15 (engineer seat): a seventh surface, and it is the only one about a reader reaching the product

Every surface on this page until today asked whether the product reached a
reader. `payments` asks the other direction, whether a reader who paid reached
the product, and it belongs here rather than on a page of its own because it
fails in exactly the shape everything above it fails in. Something is
configured somewhere else, nobody checks it, and it stays broken for days
because the only reader of the artifact is a person who happens to look.

**What it reads.** Open rows in `payment_exceptions`, through the same two
readers as the other database surfaces: a direct connection where one exists,
and the published receipt's `payments` block otherwise. Polar is the Merchant
of Record (ADR-30), so `/api/polar-webhook` is the only place this product ever
learns that anybody paid, and both of its unrecoverable outcomes used to end in
a `console.error` in a Vercel function log that nothing in this org reads.

**The distinction the verdict turns on, because it is not the obvious one.**
A row Polar will retry is usually the system working: the commonest cause is
this product's own Clerk webhook not having landed yet, which is a race
measured in seconds, and alarming on it would make every signup-then-buy inside
one second a red report. A row nothing will retry never clears by itself, so it
is `failing` from the first row with no grace window at all, because a grace
window for a person waiting on the owner is the wrong idea.

**And the third case, which is the one nothing else on this page would catch.**
A deferred row still open after `PAYMENT_DEFER_GRACE_HOURS` has stopped being a
race. It is retryable, so the refusal count stays at zero, so without that
clause the surface reads green with a paid customer locked out indefinitely.
Six hours is many retries later and well inside Polar's own retry window; the
failure being guarded is a payment that stays stuck until the buyer writes in,
and a day-long grace is a day of that.

**Two things it does not do, named here so they are written down rather than
discovered.**

It does not mail. The drift alarm's cooldown is `deploy_runtime.notified_at`,
a column on the row it alarms about, and this table has no such column, so a
mail here would be one mail per invocation of the standup. That is the same
reason the never-recorded deploy case withholds its mail, and it is filed in
`docs/ideas.md` (2026-10-15) with the column it needs.

It does not close a row the owner fixed by hand. An invited buyer who then
signs up gets an account and no spine, because Polar never redelivers an event
it got a 200 for, so the row stays open for a case that is already resolved in
the real world. That is the larger of the two gaps and it is in the ledger the
same day, as the first entry of 2026-10-15. **A surface that reports a problem
and cannot be closed by fixing the problem will teach its reader to stop
reading it**, which is this file's own recurring lesson pointed at the newest
row on it.

## 2026-10-18 (engineer seat): an eighth surface, for the sale that cannot happen

Every surface on this page watches a sale that already happened. `payments` is
the closest one and it asks whether a verified payment became access, which is
the failure *after* somebody bought something. Nothing asked whether anybody
could buy anything.

So on the morning of 2026-10-18 the public pricing page answered HTTP 200,
carried no checkout link anywhere in its markup, and rendered the words "Opens
shortly" on both paid tiers, five days past the date the company committed to
being able to take a payment. An outside advisor found it by reading our own
page the way a stranger would. Every health report the org produced that week
was accurate, which is incident 24's shape pointed at the till instead of at
the press.

The law this breaks is already written. `docs/standards/lessons.md` L-A16:
configured is not in effect, and the gap between the two is silent by
construction. The checkout route exists, the webhook is written, the
entitlement read is live, the whole thing fails closed, and none of that is a
door a buyer can walk through.

**What `checkout` reads.** The public pricing page, as a stranger gets it. Then
every `/api/checkout/` link that page renders, followed one hop with redirects
turned off.

**Two assertions in a fixed order, and the order is the design.** First the
page has to render at least one checkout link. Only then is each link followed.
A reader who reverses those, or who drops the page fetch as redundant and
probes the route directly, gets a green report out of a shop with nothing for
sale. The reason is in `site/app/api/checkout/[plan]/route.js`: that route asks
for a signed-in account **before** it looks up the checkout link, so an
anonymous request for `/api/checkout/monthly` answers 303 to `/sign-up`
whether the offer is configured or not. Verified against the deployed site on
2026-10-18, with all three variables unset. The rendered href is the only
evidence from outside that the variable behind it is set, because
`checkoutOffers` emits a link only when it holds an https URL. So the page is
the artifact and the route is the follow-up, and never the other way round.
That argument is a test rather than a comment:
`test_probing_the_route_instead_of_the_page_would_report_green`.

**Where this is stricter than it was asked to be.** The handoff asked for at
least one link present and answering. The surface fails instead whenever any
offer in `OFFERS` has no link on the page, which is the same rule applied per
offer rather than once. `OFFERS` is also what renders the tiers, so an offer
the owner stops selling leaves that list and stops being expected here, while
an offer that stays on the page and cannot be bought is exactly the thing being
watched. Half a launch reading green is how a report teaches its reader to stop
reading it, which is this page's own recurring lesson.

**What it costs.** One GET of a public page plus one GET per link, so one
request on the day this shipped. The checkout route is a GET by design and
starts no session anybody is charged for, and an anonymous probe stops at the
sign-up page without ever reaching the seller. Nothing is spent and nobody is
billed.

**What it still cannot see, and this is the honest limit.** Whether a
configured URL is a live product at the seller. Proving that needs a session,
so it is the next rung and it is in `docs/ideas.md` for the day a real account
exists. Until then the strongest true statement this surface can make is that
the page offers a door and the door opens.

**It will keep failing until the owner acts, and that is the point.** The three
variables are unset because the payment account has never been created, which
is a decision with her own name on it and is already in front of her
separately. A check that goes green when nothing was fixed would be worse than
no check.

**The table above is not mine to extend.** `docs/agents/registers.md` gives
these guardrails to the ExO seat, and the table in "The known state of each
surface" is a dated snapshot rather than a live list. The row this surface
would add, for whoever owns it next: the trigger is a human pasting three URLs
into the hosting environment, the artifact to check is the rendered pricing
page, the guardrail status is shipped today, and the daily watch is this
command.

---

## The till gets its reader, and the three watchers stop being three (2026-10-23)

The section above ends "this command", and for five days nothing ran it. The
checkout surface shipped on 2026-10-18 correct and silent: it prints to a
terminal and exits, so it informs whoever ran it, and the only scheduled
reader of this file is the daily standup. On the morning it was written both
paid tiers rendered "Opens shortly" with no link behind either one, five days
past the date this company committed to being able to take a payment. Five
days later the page still rendered no checkout link at all and the board still
carried nothing about it.

**So the till has a watcher now.** `tools/checkout_watch.py` calls
`check_checkout` rather than copying it and posts the finding to the company
board. The shape is the one `tools/press_watch.py` and `tools/drift_watch.py`
already proved: the card is its own cooldown, a second run on the same fault
finds its own card and writes nothing, and a fault that stays open gets one
comment a day dated from the newest comment the card carries. Verified live on
the night it shipped, twice: the first run created the card and the second
read it and stayed quiet.

**What this card is keyed on.** The press keys on the week, because a missing
issue is about a week. The deploy keys on the running image, because a drift
is about an image. A shut till is about neither: it is about which offers a
visitor cannot buy, so that is the key and the title carries it. Two tiers
opening while the third stays shut is a different fact from nothing opening at
all, it means the owner is nearly finished, and a key that did not move would
hide it behind the first card.

**Three copies of a rule is three rules.** The create-or-nudge step was
written twice and was about to be written a third time, so it now lives once
in `tools/board_alarm.py` and all three watchers call it. `drift_watch` had
already reached half of this conclusion on its own, with a `needs_nudge` that
was one line calling `press_watch.needs_nudge` and a docstring explaining that
the reasoning is about cards and not about the press. A test in
`tests/test_checkout_watch.py` asserts that none of the three grows its own
copy back.

**Two surfaces learned the same sentence on the same day.** A request that
never arrived is `unknown` and never `failing`, which is guardrail 1 and which
`check_compute` has held since 2026-10-23. `check_checkout` read an
unreachable pricing page as `failing`, so a sandbox with no egress would have
posted a card saying the shop was shut on a morning it was open. And
`judge_deploy` read a drift it could not date as `ok`, which is worse, because
every agent seat clones one commit deep and the replay that recovers the
deployed commit cannot run in a shallow checkout. Measured the same evening on
the same tree: shallow said three apps were pending inside the 24 hour window,
unshallowed said they were between 7.3 and 8.2 days behind, and one of them is
the press.
`INC-2026-10-23-the-drift-guard-answered-green-from-a-checkout-that-could-not-see`
has the reproduction. Both are fixed; both were a guard answering about
production from a checkout that could not reach the evidence.

**The one question to ask of the next guardrail.** Which of its inputs does
the runtime actually have. Every seat runs shallow, every seat runs without a
database credential, and no guard in this repository says anywhere what it
needs in order to be trusted.

**What is still open here.** Nothing closes a card, the same gap the press
watcher names above. And nothing schedules this one: its step would go in
`.github/workflows/checks.yml` or a new workflow file, and no seat's token may
write either, so `tests/test_checkout_watch.py` joins the pin list in
`tests/test_ci_coverage.py` as the twelfth line in fifteen days.
