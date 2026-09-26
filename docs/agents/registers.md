# The register map — where every rule is actually enforced

Written by the ExO agent on 2026-09-19, on the owner's order after
incident 20. It answers one question for every register the org keeps:
when a rule in that file is about to be broken, what stops it?

**Enforced at:** prompts/exo-agent.md §3d, every run.

## The pattern this file exists to kill

Incident 20 in [incidents.md](incidents.md) is the whole argument. The
owner ruled that section headings must be written fresh from the day's
news. The ruling was recorded in `docs/voice/taste.md` inside the hour,
correctly and permanently. The next artifact to reach her printed
"Gaining traction" and "Trailblazing" anyway, so she had to give the
same ruling a second time, in capitals.

Nothing failed at the archive. The ruling was written down, in the right
file, by the right seat, immediately. What was missing is that no step
between the ruling and the artifact ever opened that file. **Recording
is not enforcing.** A rule written down but not checked at the point of
production is documentation, and documentation does not stop anything.

So every register has two gates, and they are different gates.

- The **archive-side gate** decides that something gets written down.
  Who appends, when, and under what standing rule.
- The **artifact-side gate** decides that something gets checked before
  it ships. Which seat, at which step of which run, opens the file and
  compares its output against it.

An org can have a perfect archive-side gate on every register and still
break every rule it keeps. That is the state incident 20 found us in.

## The map

State after this run's charter edits. "was GAP" means no charter told
any seat to check an artifact against the file before 2026-09-19.

A cadence column was added on 2026-09-21, which is the debt the 2026-09-20
sweep left for this run. It compares how fast the thing a register governs
actually changes against how often its artifact-side gate fires. Where the
gate is slower, the register can be perfectly gated and still lie, and
model-routing.md is the proof: the gate fired exactly on schedule and the
file spent a day describing a policy the org had abandoned.

| Register | Owner | Archive-side gate | Artifact-side gate | Change rate vs gate rate | State |
| --- | --- | --- | --- | --- | --- |
| `docs/agents/incidents.md` | ExO | standing rule, any seat appends the moment an issue repeats | every charter's ship check, plus PM §1f and ExO §2 | changes daily, gated per PR by every seat |  was GAP, closed |
| `docs/voice/taste.md` | chair and PM record | chair or PM records the ruling | writer's first grading gate, line by line | she rules in hours, writer gates daily |  was GAP, closed, this is incident 20 |
| `docs/voice/ban-list.md` | writer | writer appends new tells | writer §2, plus sales for launch copy | writer appends, writer gates, same seat daily |  closed for copy outside the digest |
| `docs/voice/canon.md` | writer | writer proposes, owner rules | writer §2, plus market and sales | rarely, gated daily |  enforced |
| the House voice rules | writer | live in `ban-list.md` | nine charters held a frozen four-rule copy | as the ban list grows, gated per run |  was GAP, now the file wins |
| `docs/design/taste.md` | chair and PM record | chair or PM records the ruling | frontend, compare step added | she rules in hours, frontend gates **weekly** |  was GAP, closed |
| `docs/design/ban-list.md` | frontend | frontend appends new tells | frontend, check every change before shipping | frontend appends and gates, weekly |  enforced, and the model for the rest |
| `docs/design/canon.md` | frontend | owner's rulings and the references | frontend, off-system values need a ledger entry | rarely, gated weekly |  enforced |
| `docs/design/motion.md` | frontend | distilled from the sources | named by no charter until this run | rarely, gated weekly |  was GAP, closed |
| `docs/agents/runtime-changes.md` | ExO | ExO writes the law | engineer §0 daily over `.github/` **and `pipeline/`**, plus frontend, security and ExO before their own edits, plus the deploy command's `&&` chain for the press | machinery changed twice in a week, gated daily |  reopened and reclosed 2026-09-24: the gate fired on the right files and the law's scope excluded provider changes |
| `docs/agents/press-rehearsal.md` | ExO writes, engineer builds | ExO specifies | `runtime-changes.md` ladder gate 3, **code since 2026-09-24**, in the press's deploy chain and in triage, interpret and distill | provider changes are rare and catastrophic |  closed 2026-09-26, see the note below this table |
| `docs/agents/turn-caps.md` | ExO | ExO re-derives monthly | ExO | monthly, gated weekly, ample |  enforced, same seat writes and reads |
| `docs/agents/unowned-duties.md` | ExO | ExO files, owner assigns | ExO §3b | charters change weekly, gated weekly |  enforced |
| `docs/agents/model-routing.md` | ExO | nobody from 2026-09-17 to 2026-09-20 | ExO read list, and the read found it stale on arrival | routing changed in **18 hours**, gated weekly |  closed, and see the 2026-09-20 sweep |
| `docs/agents/pending-workflow-changes.md` | ExO | ExO queues, owner applies | ExO §5, every queued diff re-verified against the live file each run (strengthened 2026-09-20) | workflows changed 3 times in 4 days, gated weekly |  enforced |
| `docs/agents/registers.md` | ExO | this file | ExO §3d, the register-gate sweep | as registers are added, gated weekly |  enforced |
| `docs/agents/org-chart.md` | PM | PM maintains | PM §1b | as seats change, gated weekly |  enforced |
| `docs/agents/frameworks.md` | PM | PM §1e | PM §1e | rarely, gated weekly |  enforced |
| `docs/decisions.md` (ADRs) | chair | chair records | engineer, PM and ExO read, nine seats do not | several ADRs a week, gated unevenly |  partial, and mostly fine |
| `docs/ideas.md` (the ledger) | all seats | append-only, owner decides status | the ledger contract in most charters | daily, gated per run |  enforced |
| `docs/agents/learning-log.md` | ExO | ExO appends every run | ExO §2, read first | weekly by construction, gated weekly |  enforced |
| `docs/sprints/dispatch-queue.md` | PM | PM rewrites it every standup, PM §4 | ExO §2c counts dispatches against the log, because the actor never audits the act | daily once it exists, gated weekly |  new 2026-09-19, and the file does not exist until the first standup runs |
| `docs/voice/value.md` | writer | writer drafts, owner approves | writer's copy step 1 refuses to draft copy without it | she rules once, gated per copy round | **new 2026-09-21, and the file does not exist yet.** This is the positive artifact incident 25 says was missing |
| `docs/voice/preferences/` | chair records | chair appends per verdict, live in the session | writer's copy step and ship check, frontend before setting a word | she rules in hours, chair is present when she does | new 2026-09-21, schema in preference-data.md |
| `docs/agents/copy-pipeline.md` | ExO | ExO writes the process | writer once before its first copy round, frontend run step 0, ExO §3e | the process changes rarely, gated per copy round | new 2026-09-21 |
| `docs/agents/preference-data.md` | ExO | ExO writes the schema | PM's ruling-capture check, ExO §3e | rarely, gated per ruling | new 2026-09-21 |
| `docs/standards/lessons.md` | HQ, vendored here | the exo centralizer syncs it, no seat here appends | **one charter in twelve named it until 2026-09-24**, now all twelve in the ship check | HQ appends continuously, gated per run from today | **was the largest GAP on this page**, closed 2026-09-24 |
| `docs/standards/pm.md` | HQ, vendored here | HQ ADRs, synced as a copy | PM charter | changes by HQ ADR, gated daily | enforced |
| `docs/agents/cross-repo-law.md` | ExO | ExO writes the rule | ExO §3f, plus every charter's ship check clause 3 | HQ decided twice in a week, gated weekly here and per run in the seats | new 2026-09-24, incident 23 |
| `docs/agents/hq-relay.md` | ExO | ExO writes entries, chair marks delivered | ExO §3f | as incidents implicate HQ, gated weekly | new 2026-09-24. The delivery column is the part that can rot, since no seat controls the chair |
| `docs/agents/delivery-health.md` | ExO | ExO writes the guardrails | PM §1f delivery half, daily | the product ships weekly and daily, gated daily | new 2026-09-24, incident 24 |
| `docs/agents/durable-execution.md` | ExO | ExO, on the owner's question | none, and correctly none | a decision note rather than a rule | new 2026-09-24, not a register and listed so nobody gates it |

## What this run changed

Every charter, all twelve, now ends with a section called "Check the
register before you ship". It does two things. It names, per seat, the
registers that seat's output is bound by, and it puts the incident
register's standing rule inside every charter instead of only inside the
register it governs.

The specific gaps that closes.

1. **The voice taste register**, incident 20 itself. The writer's first
   gate is now a taste-compliance pass, line by line against the
   artifact, before the canon laws are scored at all.
2. **The writer charter's own contradiction**, which is the sharper half
   of incident 20. The charter told the seat to protect "her section
   names (Trailblazing, Gaining traction, Left behind, Read these
   yourself)" while canon law 12 said those names never print. An agent
   reading its charter was being told to preserve the violation. The
   framework and the printed heading are now stated apart.
3. **The design taste register**, the same shape and not yet fired. It
   now carries the compare step the design ban list always had.
4. **`docs/design/motion.md`**, named by no charter at all until now.
5. **The runtime-changes law**, which binds every seat and the chair and
   was named in one charter. Engineer, frontend and security now carry
   it at the point where they would break it.
6. **Reader-facing copy outside the newsletter.** The sales seat writes
   launch posts, outreach emails and landing lines, and no voice
   register governed any of it.
7. **The incident register's standing rule.** "Any issue that occurs
   more than once is always recorded at the moment it repeats, no
   exceptions" binds every seat. Before this run, eleven of twelve
   charters mentioned the file only inside the ship-first boilerplate,
   citing incident 3 as evidence for a different rule, and no seat was
   told to open it or append to it. The most-cited register in the org
   was enforced at one seat, once a week, after the fact.
8. **The House voice snapshots.** Nine charters restate four ban-list
   entries inline. When the writer appends a new tell, those nine keep
   enforcing the 2026-09-18 copy. Each now says the file wins.
9. **`docs/agents/model-routing.md`**, which names this seat as its
   owner and which no run had opened since it was written. It is in the
   ExO read list now, so the next run either uses it or retires it.

## The 2026-09-24 sweep, second pass

One row changed and one row is new, both from
INC-2026-09-24-press-provider-migration.

The finding worth carrying forward is not about a missing register. It
is about what "closed" means in the State column. `runtime-changes.md`
was marked closed on 2026-09-20 and the mark was accurate: the gate
existed, it fired daily, and the engineer ran it. Then the org made a
runtime change that the law's own definition did not cover, in a
directory the gate did not read, and produced four production failures.
Every cell in that row was green while the thing the row exists to
prevent happened twice that evening.

So this table has a failure mode it did not name. **A register can be
perfectly gated and still miss, when its scope is narrower than its
subject.** The cadence column was added for the case where the gate is
too slow. This is the case where the gate is pointed in the wrong
direction, and it is harder to see, because a narrow gate that fires
reliably looks exactly like a correct one from inside this file.

The check that catches it, for whoever runs the next sweep: for each
row, name one change that would break the thing the register governs,
and then ask whether the artifact-side gate would have seen that change.
Not whether it would have fired. Whether it would have seen it. For the
runtime law on 2026-09-23 the answer was no, and no grep in this file
would have told you.

The second finding is the one the ExO seat has now written in three
places, which is a sign it is the real one. Nine rows in this table are
enforced by a sentence in a charter telling a model to read a file.
**One row is enforced by a shell.** The press's budget guard and
availability check sit in an `&&` chain and cannot be forgotten, which
is why neither has failed since it was added, and the rehearsal belongs
in that same chain rather than in a tenth charter sentence. Where a
command already exists, the gate goes in the command.

## Still open, and honestly

- **`docs/agents/org-chart.md` and `docs/agents/frameworks.md`** are the
  PM's and are enforced at the PM's own steps, which is fine, but
  neither carries an `Enforced at:` line yet because neither file is
  this seat's to edit. Filed in the ledger.
- **`docs/voice/*` and `docs/design/*`** are the writer's and the
  frontend's surfaces for the same reason. The enforcement now exists in
  the charters, which is where enforcement belongs. The marker line in
  the register files themselves is a ledger request to those two seats.
- **Nothing verifies that a seat actually ran its check.** A charter
  line is still an instruction to a model, not a gate a runner enforces.
  The honest position is that this run moved the rules from a file
  nobody opens to a file every seat opens, which is a real improvement
  and is not the same as enforcement. A mechanical gate would be a CI
  job, and a CI job is a runtime change, so it goes through
  docs/agents/runtime-changes.md and the owner.

## The rule this file establishes

Every register the org keeps carries an **Enforced at:** line near its
top, naming the charter and the step that checks artifacts against it.
A register that cannot name one is documentation, and it says so.

One reading note for whoever runs the grep. Not every file under
docs/agents/ is a register. `app-identity-handover.md` is a plan,
`pending-workflow-changes.md` is a queue, and plans and queues are
finished rather than enforced. The grep will list the plan and that is
correct output, not a gap.

This is a cheap invariant on purpose. It is one grep, it needs no
tooling, and it makes the failure visible in the file itself rather than
in a postmortem written after the owner repeats herself.


## The 2026-09-20 sweep

Both detection commands were run. Every file under `docs/agents/` now
carries an `Enforced at:` line. The eight files without one are all
under `docs/voice/` and `docs/design/`, which is the state this page
recorded on 2026-09-19 and explained then: those are the writer's and
the frontend's surfaces, the enforcement lives in their charters where
enforcement belongs, and the marker line is a ledger request rather than
an edit this seat may make. That request is still open after a day. It
is cosmetic and it stays a request.

The charter-count command produced one finding this run and it is the
kind this page warned would look healthy.

### `docs/agents/model-routing.md`, one charter, and one day too late

The count said 1, which is this seat's own charter, and 1 was the
correct and intended number. The file still failed. It was added to the
ExO read list on 2026-09-19 with the note that the next run would
"either use it or retire it", and the next run, this one, opened it and
found it describing a routing policy the org had already abandoned.
Four seats had been moved to a third-party endpoint eighteen hours
earlier and the register that owns routing said they ran on Sonnet.

So the artifact-side gate existed, it fired on schedule, and it still
let a day pass with the register lying. **A gate on a weekly seat has a
weekly blind spot**, which is the same sentence as the cadence test on
docs/agents/unowned-duties.md, arriving here from the other direction.
Recording is not enforcing, and enforcing weekly is not enforcing daily.
This page should carry a cadence column eventually. It does not yet,
because the honest fix for most rows is not a faster ExO but a different
owner, and picking those owners is a run's worth of work on its own.

**For the next run:** add a cadence column to the map above, comparing
each register's artifact-side gate against how fast the thing it governs
actually changes. Routing changed in 18 hours. The voice canon changes
when the owner rules, which is also fast. The turn-caps table changes
monthly, and a weekly gate is ample. The column will separate them.

### `docs/voice/prose-benchmark-2026-09-19.md`, named by zero charters

New since the last sweep, from the writer seat's PR #36, and it has no
`Enforced at:` line and no charter names it. Before filing it as a gap,
apply this page's own reading note: not every file under a register
directory is a register. A benchmark is a measurement taken on a date,
which makes it evidence rather than a rule, and evidence is finished in
the same way a plan is finished. **Classified as an artifact, not a
gap.**

One question goes to the writer seat as a ledger note rather than a
charter edit, because it is that seat's call to make. If the intent is
to re-score the digest against that benchmark periodically, then the
benchmark becomes a standard and needs a line in the writer charter
naming when it is re-run. If it was a one-time read of the competition,
it is done and correctly unnamed. Nobody outside that seat can tell
which from the file.


## The 2026-09-21 sweep

Both detection commands were run again. Every file under `docs/agents/`
carries its `Enforced at:` line, including the two added this run. The
eight files under `docs/voice/` and `docs/design/` still lack the marker
for the reason this page has given twice: those are the writer's and the
frontend's surfaces, the enforcement lives in their charters, and the
marker line is a ledger request rather than an edit this seat may make.
Two days open now. It is still cosmetic and it is still a request.

Three findings, and the first one is a new kind.

### The polarity finding: a gated, current register that cannot converge

`docs/voice/taste.md` passes every test this page has ever applied. It has
an owner, an archive-side gate that fires within the hour, and an
artifact-side gate at the writer's first grading step, checked daily.
Nothing about it is stale.

It still produced eight rejected rounds of site copy on 2026-09-20,
because roughly forty of its rulings say what the words must not be and
none of them says what the product is worth to a builder. That is
incident 25.

So the sweep gains a third question, beside "who writes it" and "who
checks it": **does the register say what good looks like, or only what bad
looks like?** A register of rejections cannot converge, and the reason is
arithmetic. Each "no" removes one candidate from an unbounded space, so a
hundred of them still leave the target unlocated, and the seat reading it
can avoid every recorded failure and miss every time.

Where the ratio is lopsided, the finding is not a missing gate. It is a
**missing positive artifact**, and the fix has three parts: name the file,
say which seat drafts it and which approval makes it law, and put the
precondition in that seat's charter so the work downstream of it cannot
start first. `docs/voice/value.md` is the first one and it is specified in
[copy-pipeline.md](copy-pipeline.md).

The rule, for the next register that grows this way: **a register of
rulings needs a companion that states the target.** The rulings tell a
seat when it has failed. Only the target tells it where to aim. The check
is now in prompts/exo-agent.md §3d.

### What the cadence column found on its first run

It was added this run as the debt the 2026-09-20 sweep left, and it paid
for itself once. **`docs/design/taste.md` is a cadence gap.** The owner
rules on pixels in the same hours she rules on words, and the only
artifact-side gate is the frontend seat's compare step, which fires
weekly on Wednesdays. The voice register has the same archive rate and a
daily gate, because the writer runs daily. The two registers look
identical in every other column and they are not equivalent.

It is recorded rather than fixed, for the same reason as the frontend row
in unowned-duties.md. The honest answer is not a faster frontend cron,
since nothing else in that seat's week wants to run seven times, and the
chair can apply a design ruling in the session that produced it. Watch
it, and treat a design ruling that waited for a Wednesday as the evidence
that changes the answer.

### The two new registers, and one honest note about them

`copy-pipeline.md` and `preference-data.md` were written this run and both
carry `Enforced at:` lines naming charter steps that also shipped this
run, which is the arrangement this page asks for. The note worth keeping
is that neither has fired yet. A register whose gate has never executed is
in the same state `docs/agents/model-routing.md` was in on 2026-09-19,
which was named by exactly the right charter and wrong anyway. **For the
next run:** check whether the writer's first copy round after this merges
actually opened `value.md`, and whether the preference file it produced
uses the schema. If the next copy session is recorded as narrative again,
the schema failed and more words are not the fix.


## The 2026-09-24 sweep

Four rows added, one of them a gap larger than anything this page has
found before, and one new failure mode for the page itself.

**The gap: the company standards were enforced nowhere.**
`docs/standards/lessons.md` states in its own opening paragraph that
"every seat in every product reads its role's section before working."
It is the owner's own corrections, generalized into law, distributed by
HQ, and vendored into this repository on 2026-09-21. Running the §3d
grep against it, exactly one charter in twelve named the path, and that
one was the PM citing the other standard, `pm.md`. So the org has spent
three days holding a register that every seat is supposed to read and
that eleven seats had no instruction to open.

This is the same shape as incident 20 and it is worse in one specific
way. Incident 20's register was written here, by a seat that also reads
it. This one is written somewhere else, by a body with no visibility
into whether it is read, and it arrives as a file drop. **A vendored
register has no archive-side gate in this repository at all**, which
means the only gate it can have here is the artifact-side one, and there
was none. The fix shipped this run: clause 3 in every charter's ship
check, in all twelve.

**The new failure mode: a register whose gate depends on somebody
outside the org.** `docs/agents/hq-relay.md` has a delivery column that
no seat can advance. This seat writes an entry, and whether it reaches
HQ depends on the chair reading it. That is not a defect worth avoiding,
since the alternative is not relaying at all, but it is worth naming,
because the page will look enforced while entries sit undelivered. The
detection rule for a future run is one line: an entry in the relay whose
delivered column is still empty after two runs is a finding, and the
finding is about the channel rather than about the chair.

**A row that is deliberately not a register.**
`docs/agents/durable-execution.md` answers a question the owner asked
and holds no rule anyone can violate. It is listed with "gated by
nothing, correctly" so that the §3d grep does not flag it every week and
so that no future run invents an enforcement step for a document that
needs none. The org will accumulate more of these. A decision note is
not a register and gating it would be ceremony.

**Unchanged and still worth watching.** The three cosmetic marker lines
under `docs/voice/` and `docs/design/` are now four days an open ledger
request. Still not this seat's files, still not worth a second mention
to the owner.

## The gate-3 row, corrected (engineer seat, 2026-09-26)

The `press-rehearsal.md` row read "not yet code" and "GAP" until this run. It
had been out of date since 2026-09-24, which matters more than a stale cell
usually does, because this table is the thing a seat reads to find out what is
missing. A reader following it would have rebuilt a gate that already existed.

What is actually true now. `rehearse()` is in `pipeline/weekly.py` beside
`preflight` and `weekly`, with `press_rehearsals` in `db/schema.sql` and the
`&&` link in that module's deploy docstring, built 2026-09-24. `triage` and
`interpret` got `preflight` and `rehearse` on 2026-09-26 when they moved to
Kimi. `distill` got both on 2026-09-26, which closed the last model-calling
cron. `ingest` has neither and needs neither in this form, because it calls no
model.

One honest limit, carried from `press-rehearsal.md` rather than hidden here: no
rehearsal has ever run against a live provider, because no seat holds the keys.
Every one of them is proved as far as a test can prove it without a key, and the
first real execution of each is the chair's, on the next deploy.

**And the gate this table was right about is still open.** Row 59's own point
was that a register with no second gate gets violated by the next artifact.
Tonight is that, exactly: a runtime change reached twelve live workflows with no
pull request and no smoke run, and every seat's run has been recorded as a
failure since 01:14 UTC. It is INC-2026-09-26-run-report-dash-echo, the fix is
written and tested, and it is queued as item 10 in
`pending-workflow-changes.md`, because the one gate this org still cannot close
from inside a seat is the one that needs a `workflow`-scoped token.
