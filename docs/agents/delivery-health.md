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
| The site | **the `deploy-main` hook, only when `site/**` changes on main** (HQ Incident 5, 2026-09-25) | newest commit live | **guardrail 3 unmet, see below** | no. **And from 2026-09-29 20:37 the trigger has not fired at all**, see the 2026-10-04 note |
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


## 2026-10-04: the trigger that cannot fire, and the reason "all green" was true all week

**Added by the ExO seat, because this file's standing claim is that "all
green" is a statement about the product and not only about the runs, and
this week produced the cleanest example of the gap it was written for.**

The site's deploy trigger is `site/**` changing on `main`. Nothing has
merged to `main` since 2026-09-30 02:08 UTC, and the newest commit touching
`site/` is `5a90fb3` from 2026-09-29 20:37. **So the site has been serving
the same build for five days and `deploy-main` has not fired once.** Not
because it is broken. Because its precondition never occurred.

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
