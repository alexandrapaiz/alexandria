# Unowned duties

**Enforced at:** prompts/exo-agent.md §3b, the unowned-duty audit, every
run.

Maintained by the ExO agent (charter §3b). Created 2026-09-19 after
incident 19, the Hugging Face incident that no seat captured.

This page exists because of one discovery. Twelve charters each say what
a seat must produce, and not one of them said the org must know what the
world knows. Every seat did its job correctly and the org was blind
anyway. A duty that no charter names is invisible to every audit we run,
because every other audit checks performance against a charter. This is
the only page that checks the charters against reality.

## How to read the table

One row per duty the org's behavior assumes somebody performs. The owner
column says which seat's charter names the duty in words, not which seat
would probably do it if asked. "None" is the finding. A duty split across
three seats with no named owner is also a finding, because shared
custody of awareness is how incident 19 happened.

### The second test, added 2026-09-19: cadence

Naming an owner is necessary and it is not sufficient, and this register
had that bug for its first day of life. A duty is only owned when the
naming seat is **awake often enough to perform it**, which means the
seat's cadence has to be shorter than the rate at which the duty's
trigger arrives. A weekly seat cannot own a daily duty. Writing the duty
into its charter anyway produces the worst available outcome, which is a
duty that is documented as owned, audited as owned, and in practice
performed by whoever happens to be present. Here that was always the
owner.

The evidence is on this page. "Runs that fail get reported to the owner"
was assigned to the PM on 2026-09-19 and marked assigned the same day.
Runs fail on the day they fail, and the PM's cron fired once a week, so
the row was false within hours of being written. The owner discovered
two failed frontend runs herself, which is precisely the outcome that
row exists to prevent. The fix is in prompts/pm-agent.md sections 0 and
4 and in item 2 of pending-workflow-changes.md, and until that cron
changes the row below stays honest about being unenforceable.

So every row now carries two more columns. **Trigger rate** is how often
the duty's occasion actually arrives, measured rather than assumed.
**Cadence** is how often the owning seat runs. When cadence is slower
than trigger rate, the state is `cadence gap`, and a cadence gap is a
finding of the same weight as an unowned row.

| Duty | Owner | Trigger rate | Cadence | State |
|---|---|---|---|---|
| The org knows what the world knows | market (§5, named 2026-09-19) | weekly | weekly Fri | assigned |
| Ecosystem events steer what we ingest | research (signal read) | weekly | weekly Mon | consuming |
| Upstream compromise is in the threat model | security (incident 19 item 2) | continuous, acted on in sweeps | biweekly | assigned, accepted lag |
| Legal and compliance posture | **none** | once, before launch | n/a | owner decision |
| Free-tier and quota headroom | finance, dormant | monthly | dormant | owner decision |
| The corpus survives losing its database | **none** | continuous | n/a | owner decision |
| The repo describes the system it is | exo (§5b) | weekly | weekly Sun | assigned |
| Runs that fail get diagnosed | exo (§2b) | daily, 25 runs on 2026-09-19 | weekly Sun | **cadence gap** |
| Runs that fail get reported to the owner | pm (§1f) | daily | weekly Mon, daily once queued | **cadence gap, fix queued** |
| The org decides what to do next between Mondays | **none, and the owner did it** | hourly | n/a | **fix queued, see below** |

## The three open gaps, with the check each one needs

None of these is being proposed as a charter edit by this run. Each one
either costs money, touches the owner's personal exposure, or activates
a dormant seat, and all three of those are hers to decide. What follows
is the finding, the proposed check, and the seat that could carry it.

### 1. Legal and compliance posture

No charter in `prompts/` contains the words legal, privacy, GDPR,
CAN-SPAM, copyright, or robots.txt. That was verified by grep on
2026-09-19 across all twelve. Meanwhile three things are already true.
The site collects email addresses today and stores them in
`site/lib/waitlist.js`. The pricing page tells a visitor "We send one
email, and it carries an unsubscribe link" at `site/app/pricing/page.jsx`
line 49, while the unsubscribe endpoint is still a Phase-2 build item in
`docs/roadmap.md`. The digest redistributes other people's paper content
under licenses nobody has read in writing. Launch is Oct 13.

Proposed check: one line on the PM's launch-readiness gate that says
legal and compliance readiness is answered in writing before send, with
the content of that answer being the owner's call. This is the smallest
thing that makes the gap visible on a date rather than after it.

Proposed owner: the owner decides the substance, the PM owns the gate
line, because the PM already owns the launch runway.

### 2. Free-tier and quota headroom

The only charter that watches metered usage is the finance seat's, and
the finance seat is dormant. So today nothing in the org would notice
Groq's free tier, Neon's row limits, or GitHub Actions minutes
approaching a ceiling until a job started failing. The org's standing
rule that cost stays at zero is enforced by nobody counting.

Proposed check: until finance is activated, the engineer's daily run
names any quota error or rate-limit response seen in the pipeline logs,
in one line, even when the run otherwise succeeded.

Proposed owner: activate finance monthly, which is a one-line schedule
change, or give the interim line to the engineer. Owner's call.

### 3. The corpus survives losing its database

Nothing in `prompts/`, `docs/`, `pipeline/`, or `.github/workflows/`
mentions a backup, a dump, or a restore. That was verified by grep on
2026-09-19. One Postgres database on a free tier holds the papers, the
claims, the embeddings, the claim graph, and the subscriber list. The
vision calls this a library. A library with no second copy is a rumor.

Proposed check: the security seat's biweekly sweep answers once, in
writing, "if this database were lost tonight, what survives and how long
would rebuilding take." An answer of "nothing, and weeks" is a finding
for the owner rather than a fix for the seat, because a backup target
may cost money.

Proposed owner: security writes the assessment, the owner decides what
to spend on it.

## The rule that keeps this page honest

A duty only leaves this page by being written into a charter in words a
run can act on. Moving a row to "assigned" because it feels covered is
the exact mistake that made incident 19 possible.


### 4. The org decides what to do next between Mondays

Found 2026-09-19 by the owner, in her own words: "right now i feel like
im doing the PMs job, i want the pm to be proactive." This is the fourth
row, it is the largest one on the page, and unlike the three above it is
not an owner decision, so it is being fixed rather than proposed.

The duty is deciding what the org does next, hour by hour, between
planning ceremonies. Every charter in `prompts/` was grepped for the
vocabulary this duty would have to use, and the result is stark. No
charter contains `gh workflow run`, `workflow_dispatch`, or any
instruction to start another seat's run. The PM charter contains the
word dispatch twice, and both times it refers to a dispatch that
happened TO the seat. Twelve charters describe what each seat produces
when it is woken, and not one of them describes who decides that a seat
should be woken.

So that duty went to the only always-present actor, which was the owner.
That is not a delegation failure, it is the absence of any seat capable
of receiving the delegation, for two separate reasons stacked on top of
each other. The PM's cadence was weekly, so it could not notice. And no
seat holds dispatch authority at all, because `GITHUB_TOKEN` cannot
trigger a workflow, so even a seat that noticed had no actuator.

The fix ships in two versions, both in this run. Version 1 is inside the
current constraints: the PM runs daily and publishes a proposed dispatch
queue with the `owner_instructions` already drafted, which moves her job
from authoring dispatches to approving them. Version 2 is written and
dormant, waiting on `APP_PRIVATE_KEY`, and it lets the PM fire the queue
itself inside ceilings she controls. Both are in prompts/pm-agent.md
sections 4 and 5, and the cron they depend on is item 2 of
pending-workflow-changes.md.

The general lesson, which is the reason this section is longer than the
row deserves: **duties accrete to whoever is present.** The full
argument is in docs/agents/learning-log.md under the presence gradient,
and its operational form is the cadence test above.
