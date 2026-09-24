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
| Upstream compromise is in the threat model | security (§2, words added 2026-09-20) | continuous, acted on in sweeps | biweekly | assigned, accepted lag. **Was false from 2026-09-19 to 2026-09-20**, see below |
| Legal and compliance posture | **none** | once, before launch | n/a | owner decision |
| Free-tier and quota headroom | finance, dormant | monthly | dormant | owner decision |
| The corpus survives losing its database | **none** | continuous | n/a | owner decision |
| The repo describes the system it is | exo (§5b) | weekly | weekly Sun | assigned |
| Runs that fail get diagnosed | exo (§2b) | daily, 25 runs on 2026-09-19 | weekly Sun | **cadence gap** |
| Runs that fail get reported to the owner | pm (§1f) | daily | weekly Mon, daily once queued | **cadence gap, fix queued** |
| The org decides what to do next between Mondays | **none, and the owner did it** | hourly | n/a | **fix queued, see below** |
| A runtime change is smoke-tested before the next cron fires | engineer (§0, added 2026-09-20), exo (§2) as backstop | twice in the week of 2026-09-14 | daily | assigned 2026-09-20, was a cadence gap |
| Reader-facing site copy gets drafted | writer (§"Site copy is yours to draft", added 2026-09-21) | per copy session, 8 rounds in one day on 2026-09-20 | daily 16:00 UTC | assigned 2026-09-21. **Was worse than unowned from 2026-09-19 to 2026-09-21**, see below |
| Approved copy reaches the live site | frontend (sets only, §added 2026-09-21) | per approval | weekly Wed | assigned, lag accepted, see below |
| The owner's rulings become reusable preference data | chair records (pm-agent.md ship check, added 2026-09-21) | whenever she rules in chat | present whenever she is | assigned 2026-09-21, and the chair is the correct owner here, see below |
| **The product reached its readers** | pm (§1f delivery half, added 2026-09-24) | daily and weekly, whenever the press or the site ships | daily standup | assigned 2026-09-24. **Was unowned from the first issue until now**, see below |
| **An HQ decision is read against local law** | exo (§3f, added 2026-09-24) | two HQ decisions in the week of 2026-09-21 | weekly Sun | assigned 2026-09-24, and it is a cadence gap on its face, see below |
| **Evidence from here reaches HQ** | exo writes, chair carries (hq-relay.md) | as incidents implicate a parent decision | weekly to write, unbounded to deliver | assigned 2026-09-24, with the delivery half outside any seat's control |
| The daily pipeline's providers stay available | **none** | continuous, three failures in five days | n/a | **unowned**, see below |

## The 2026-09-21 rows, and the state that is worse than unowned

Three rows arrived this run out of incident 25, and the first one
demonstrates a state this register did not previously have a name for.

### Assigned to a seat that was forbidden

"Reader-facing site copy gets drafted" was not unowned on 2026-09-20. It
was worse. The owner's ruling of 2026-09-19 named the writer seat, and
that seat's own charter said "never site copy (frontend's lane)", while
the frontend charter's run steps are entirely visual and never write a
word. So the duty read as owned from both directions, would have passed
any grep for the vocabulary, and was performed by neither seat.

The state deserves its own name because it defeats this register's own
method. Grepping the charters for "site copy" on 2026-09-20 returned a
hit, in the writer charter, in a sentence that forbade it. **A grep finds
vocabulary, not polarity.** So the method gains one step: when the grep
hits, read the sentence and check whether it assigns the duty or refuses
it. Absence of the vocabulary is a finding, and so is its presence in the
negative.

The cadence test passes comfortably once the row is real. The writer runs
daily at 16:00 UTC and copy rounds arrive when the owner asks for them,
so the owning seat is awake more often than the trigger.

### The lag that is accepted rather than fixed

"Approved copy reaches the live site" sits with the frontend seat, which
runs weekly on Wednesdays, and approvals can arrive any day. That is a
gap by this register's own test and it is recorded as accepted rather
than fixed, for two reasons. The chair can set an approved line in the
session it was approved in, so the seat's cron is a floor and not a
ceiling. And the honest fix is not a faster frontend cron, because
nothing else in that seat's week wants to run seven times. Revisit it if
a copy change is ever blocked waiting for a Wednesday, and revisit it
before the Oct 13 launch regardless.

### The one duty the chair should own

"The owner's rulings become reusable preference data" is assigned to the
chair, and that is not the compromise it looks like. Every other row on
this page prefers a seat with a cron over the chair, because a cron is
what makes a duty independent of the owner's presence. This duty is the
exception, because its trigger is her presence. A ruling only exists when
she gives one, in chat, to whoever is in the room, and the seat in the
room is the chair. A cron cannot capture a conversation it was not in.

What follows from that, and it is the part worth checking next run: a
duty owned by the chair has no workflow enforcing it, so it needs a
written rule instead. The rule is in prompts/pm-agent.md's shipping check
and the schema is docs/agents/preference-data.md. The ExO seat audits
that the record exists, in §3e, which is the same arrangement as every
other row where the actor cannot audit the act.

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


## The 2026-09-20 audit

Three results, and the first one is about this register rather than
about the org.

### 5. A row that said assigned and was not

The re-verification in charter §3b exists because a row can go false
after it is written. It went false on the day it was written, again.

"Upstream compromise is in the threat model" was moved to **assigned**
on 2026-09-19 on the strength of incident 19's second recommendation.
The audit of 2026-09-20 grepped `prompts/security-agent.md` for the
vocabulary that duty would have to use, which is the same method that
found the first three rows, and found nothing. Not `upstream`, not
`supply chain`, not `Hugging Face`, not `dependency`, not `third
party`. The charter's only mention of incident 19 sits inside the "Seen
and not mine" boilerplate, which is the exact reading error
docs/agents/registers.md warns about: a file named in boilerplate as
evidence for some other rule looks like coverage to a grep and is not
coverage.

So for one day the register asserted that the org's supply-chain
exposure was somebody's job, and the security seat would have run its
next sweep on the 1st with no instruction to look. The words are in the
charter now, naming the artifacts the org actually consumes and asking
for the blast radius in writing.

**The lesson, and it is this page's second self-inflicted one.** Moving
a row to assigned on the strength of a *recommendation* is the same
mistake as moving it on the strength of a feeling. A row moves when the
charter edit is merged, not when the incident that proposes it is
written, and the two happen in different pull requests more often than
not. The rule at the bottom of this page said this already. It now has
a second instance to point at.

### 6. The new row: runtime changes and the six-day blind spot

Found by grepping the charters for who checks that a change to the
machinery was tested before a seat met it. The answer was one seat, this
one, in §2, on Sundays.

The trigger rate is not weekly. In the week of 2026-09-14 the machinery
changed twice, once for containerization and once for open routing, and
the second landed at 18:49 UTC on a Friday, 35 minutes after the
previous ExO run began. A seat met it at 06:16 on Saturday and failed
completely. The audit that would have caught it was 35 hours away, and
had the change landed on a Monday it would have been six days away.

That is a cadence gap of the purest kind, and unlike the PM's it did not
need a cron change to close, because the org already has a seat that
runs every day. The engineer charter's new step 0 runs the machinery
diff daily and reports what it finds to the incident register and to the
owner. This seat keeps the weekly pass as the backstop and as the
pattern-finder, which is what a weekly cadence is actually good for.

**Check next run:** whether the engineer seat's PRs carry a machinery
line. A duty assigned to a charter is not a duty performed, which is the
whole thesis of this page.

### 7. What the cadence table still says, honestly

Two rows remain in cadence gap, and one of them is worse than it was.

"Runs that fail get reported to the owner" is still owned by a seat
whose cron fires weekly, because item 2 of pending-workflow-changes.md
is still unapplied. The 2026-09-20 evidence: the PM run failed at 06:16
UTC and nothing in the org mentioned it for eleven hours, until the
ExO's scheduled Sunday run opened `gh run list`. That the gap was
eleven hours rather than six days is an accident of which day it was.

"Runs that fail get diagnosed" is still this seat's, still weekly, and
this run does not propose a fix for it. The machinery half moved to the
engineer above, which is the part that was mechanically checkable. The
diagnosing half needs judgment against the incident register, and
splitting it further would produce shared custody, which is the defect
this page was created to name. The honest options are a second ExO run
midweek or nothing, and that is the owner's call rather than this
seat's, because it spends her tokens.


## The 2026-09-24 rows

Four rows this run. Three of them come out of incidents 23 and 24 and one
is the new hunt required by §3b.

### The product reached its readers, which was owned by nobody

This is the row that should embarrass the register, and it is the
clearest instance yet of the class this page exists for. The org runs
twelve seats, keeps a run-health duty, and assigns it to the PM daily.
Every one of those checks reads `gh run list`. The newsletter is the
product. It runs on a Modal cron, which is not GitHub Actions, so it was
outside every health duty the org has ever written. On 2026-09-21 no
issue was written, every Actions run that week was green, and the owner
found out from her own inbox three days later.

Nothing failed an audit. The fleet-health duty was owned, it was
performed, and it was performed correctly on a definition of "health"
that excluded the product. That is the same shape as incident 19 and it
deserves naming as its own detection heuristic, because the §3b method
did not find it: **grep the charters for the vocabulary of the thing the
org sells, not only for the vocabulary of the duty.** Grepping for
"run health" found an owner. Grepping for "digest," "issue," or "reader"
in a monitoring context found nobody.

Assigned to the PM, in §1f's new delivery half, with the artifact rather
than the scheduler as the evidence. The cadence fits: the press ships
weekly, the pipeline daily, and the standup now runs daily, so the
detection lag is a day rather than a week.

### An HQ decision is read against local law, and this one is a cadence gap on arrival

Assigned to this seat in §3f, and honestly marked as a cadence gap in
the same breath. HQ decided twice in the week of 2026-09-21, ADR-015 and
ADR-033, and this seat runs weekly. So the worst case is that a parent
decision governs alexandria for six days before any seat here compares
it against local law, which is very close to what happened: ADR-015
landed on a Friday evening and was first read on a Sunday, after it had
already failed two PM runs.

The register's own rule says a cadence gap is fixed with a cron change
rather than another sentence in a charter. This one is not, and the
reason is worth writing down so the next run does not re-open it. The
trigger is not the calendar, it is a merge, so the correct detector is
an event rather than a schedule: a check that fires when a commit
touching this repository carries an HQ marker. That is a workflow
change, the lane is still closed, and it is queued in
pending-workflow-changes.md rather than argued about here. Until then
the weekly pass is the backstop and it is marked honestly as a gap.

### Evidence from here reaches HQ, with half the duty outside the org

The writing half is this seat's and is assigned. The delivering half
belongs to the chair, who is a human session and not a seat, so no cron
covers it and no audit can. The row is here rather than absent because
an unowned half that is visible beats one that is not. The detection
rule is in registers.md: an entry still undelivered after two ExO runs
is a finding about the channel.

### The new unowned row: the daily pipeline's providers

Found by the §3b hunt, and found by taking the delivery-health table
seriously rather than by a grep. The weekly press now gets an
availability check, a fallback list, and an alarm, all shipped in PR
#75. The daily pipeline, which is triage, distill and interpret, and
which feeds everything the weekly issue is made of, gets none of the
three. It has a budget guard and nothing else. It runs on the same free
tier, on the same account, against the same rate limits, and on models
from the same provider that withdrew `groq/compound` without notice.

So the org has hardened the visible surface and left the one underneath
it exposed, which is the more expensive of the two, because a silent
daily pipeline degrades the corpus rather than announcing itself with a
missing email. Three provider failures in five days is the trigger rate,
and no charter names the duty.

Marked unowned rather than assigned, and deliberately. The fix is
engineer work in the pipeline, which is not this seat's surface, and the
sizing is the PM's to groom. What this seat can say is that the duty
exists, that it has a known trigger rate, and that the fix is already
written once in PR #75 and only needs applying a second time.
