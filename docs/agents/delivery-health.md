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

## The known state of each surface, 2026-09-24

| Surface | Trigger | Artifact to check | Guardrails 1 to 3 | Watched daily |
| --- | --- | --- | --- | --- |
| The press, weekly issue | Modal cron, Monday 09:00 UTC after PR #75 | newest row in `digests` | shipped in PR #75, unmerged at this writing | from the next standup, PM §1f |
| The press, daily pipeline | Modal crons, 11:00 to 14:00 UTC | newest rows in the corpus tables | budget guard only, no availability check | not yet, and this is the next gap |
| The site | deploy on merge | newest commit live | none | no |
| The MCP server | long-running | a probe query | none | no, and incident 21 is what that costs |

The bottom three rows are the honest part of this table. One surface is
instrumented, three are not, and the daily pipeline is the one that
feeds everything else. Closing those is engineer work and belongs in the
sprint rather than in this file, which is why it is written here as a
finding for the PM to groom rather than as an assignment.

## The standing question this file answers

Before any seat writes "all green" in a pull request description, it
answers this: green on what evidence, and did anything reach a reader.
If the second half is unanswered, the line says so.
