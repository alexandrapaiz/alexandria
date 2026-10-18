# Relay to HQ — what alexandria owes Alexandra Systems upward

**Enforced at:** prompts/exo-agent.md §3f, which also carries every
undelivered entry into that seat's pull request description. The ExO seat
writes entries.
The chair carries them, because no automated channel exists yet.

Seats never message each other, so evidence that matters to the parent stops
here unless something moves it. This file is the outbox. Each entry is
written to be copied into an HQ issue or a chair message with no editing, per
the standard the PM's dispatch queue already uses: if the carrier has to
compose anything, the note did not work.

**The second sentence of this file used to read "and no seat in this
repository can write to `alexandrapaiz/alexandra-systems`." It is false and
it was never re-tested** (corrected 2026-10-18,
`INC-2026-10-18-the-host-runs-every-seat-as-the-owner`). The host provides a
`GH_TOKEN` that authenticates as `alexandrapaiz` with `admin: true` on every
repository in the account, which three `GET` calls established in one turn.
Twenty-four days of hand-carried backlog rested on a sentence nobody spent a
command on.

**That does not make this file a channel, and the reason is worth keeping.**
The remedy for an outbox nobody empties is not for a seat to start writing to
the parent with the owner's own credentials because the credential happens to
allow it. A token's scopes are not a grant. The correct remedy is the pair of
asks in the 2026-10-18 entry below: scope the seats down to something
narrower than the owner's account, and then grant the one narrow permission
this file needs, which is issue creation on the parent. Until she rules, the
carrier is still the chair, and the entries below still stay until she marks
them delivered.

An entry stays until the chair marks it delivered with a date.

---

## 2026-09-24 — Kimi routing failed alexandria's PM seat twice, and the same class hit HQ's own seats

**Status: undelivered.**

**For:** whoever owns HQ ADR-015.

**The short version.** ADR-015's open routing has now produced four
failed runs across two repositories and zero successful ones. Alexandria
has removed the secrets and fallen back to Sonnet. The rollout also
skipped a safety gate that alexandria's own routing law requires, and
nobody here knew the model had changed until three days later. The
direction is not in question. The rollout shape is.

**The evidence, alexandria side.** Commit 609d7cc, merged 2026-09-19
18:49 UTC, gave `agent-pm.yml`, `agent-market.yml`, `agent-okr.yml` and
`agent-finance.yml` a preferred run step on `kimi-k2.7-code`.

- Run 35493791740, 2026-09-20: `is_error: true` at `num_turns: 1`,
  empty `modelUsage`, `total_cost_usd: 0`. The endpoint did not serve
  the request at all. This is plumbing, not quality.
- Run 35626266985, 2026-09-21: the model answered, worked twelve
  minutes, then `is_error: true` at `num_turns: 30` against a cap of
  300. The no-ship tripwire fired, so the run had made commits it never
  pushed. This one is quality, and specifically it is tool-calling
  reliability on a long agentic run.

Read those two apart. They are different failures and only the second is
evidence about the model.

**The evidence, HQ side, as reported to alexandria's owner.** pm 2/2
failed, finance 1/3, okr 1/2. Same week, same routing, same seats by
role. Two products producing the same failure distribution independently
is a stronger result than either one alone, and neither of us had the
other's numbers until the owner carried them by hand.

**Three things alexandria asks HQ to consider.**

1. **The rollout order is backwards.** ADR-015 routed the PM first in
   both repositories. The PM is the fleet-health seat, it is the seat
   that reports run failures to the owner, and under company ADR-033 it
   is now the only seat with dispatch authority. So the experiment was
   run on the seat whose absence makes every other failure harder to
   see. Route the seat whose failure costs least. In alexandria that is
   finance, which is dormant, or okr, which runs monthly.

2. **The either/or shape turns a routing experiment into a lost run.**
   Both workflows' Claude step is guarded by `if: env.OPENROUTE == ''`,
   so it is unreachable by construction while the key exists. A failed
   open-model attempt should cost three minutes, not the run. The two
   line fix is written out in full in
   `docs/agents/pending-workflow-changes.md` item 1b in this repository,
   and it applies verbatim to HQ's copies. Alexandria's position is that
   the secrets do not come back here until that is applied, because
   re-adding the key today re-arms the identical failure on the identical
   seat.

3. **The gate that was skipped.** `docs/agents/model-routing.md` in this
   repository requires a golden-set comparison before any seat leaves
   its explicit model. It was written on 2026-09-17 and it names the
   exact hazard that then occurred, in these words: "open-model
   tool-calling reliability on long agentic runs." The gate was not
   overruled, it was not seen. Alexandria is not claiming HQ meant to
   drop it.

**The general point, which is the reason this note exists at all.** A
parent decision changed a subsidiary's machinery with no record inside
the subsidiary except a commit subject, and overrode a local safety
clause without either party noticing there was one. That is a mechanism
rather than a mistake, and it will recur on the next ADR unless the
shape changes. Alexandria's proposed rule is in
`docs/agents/cross-repo-law.md` and it is short: parent decisions govern
and they do not take effect silently, which means one entry in the
subsidiary's decisions file, one line in the local law that is being
overridden, and the affected seats told in a file their charters
already read. It is not a veto and it adds no approval step. Alexandria
offers it as a candidate for the standards set, since every product HQ
bootstraps will have the same exposure the moment it writes its first
local law.

**One thing HQ may already have and alexandria does not.** Whether
ADR-015 was accompanied anywhere by a measurement of what open routing
was expected to save. Alexandria's routing register has the lever
analysis but no number. If the saving is large the calculus on retrying
changes, and if it is small the four failed runs already cost more than
the experiment can return.

---

## 2026-09-27 — An HQ incident number reached alexandria as a commit subject, and its decision was recorded nowhere here

**Status: undelivered.**

**For:** whoever numbers HQ incidents, and whoever owns the bootstrap
that gives a product its `docs/standards/` copies.

**The short version.** HQ Incident 5 changed how alexandria deploys to
production. The change is good and the reasoning behind it is sound. It
arrived here as a commit subject and nine lines of comment inside the
workflow file it added, and nowhere else. `grep -rn "HQ Incident 5"
docs/` in this repository returns nothing. So the subsidiary now runs a
deploy path whose justification lives only in the artifact that
implements it, and the local file that holds the guardrails for scheduled
delivery went on describing the path that had been replaced.

This is the same interface defect as the ADR-015 entry above, in its
cheaper form. That one was a parent decision silently overriding a local
law. This one is a parent decision with no local law to override, and
therefore nothing to catch it.

**The evidence.** Commit `1baeb7f`, pushed straight to main on
2026-09-25 by the owner, subject "Production deploys via a deploy hook on
main; seat branches no longer create Vercel deployments (HQ Incident 5:
the 100/day limit)". It adds `.github/workflows/deploy-main.yml` and
sets `git.deploymentEnabled=false` in `site/vercel.json`. No pull
request explains it (`gh api .../commits/1baeb7f/pulls` is empty) and no
smoke run precedes it. The first execution of the new workflow is a
production push. That half is registered locally as
`INC-2026-09-26-deploy-workflow-no-smoke-run` by the engineer seat.

What the engineer's entry does not cover, and what this note is about, is
that four days later no file a seat reads knew the change existed:
not `docs/decisions.md`, not `docs/agents/runtime-changes.md`, and not
`docs/agents/delivery-health.md`, which is the ExO seat's own file and
whose table still read "The site | deploy on merge". Fixed here on
2026-09-27, four days after the fact, by a weekly audit.

**What alexandria is asking for, and it is small.** An HQ incident number
is a parent record. When one of them changes a subsidiary's runtime, the
subsidiary needs the number to resolve to something inside its own
repository, because that is where its seats look and they cannot read
HQ's register. One line in the product's `docs/decisions.md` naming the
HQ incident and what it changed locally is enough. That is the same
obligation `docs/agents/cross-repo-law.md` already proposes for a parent
ADR, and this week is the evidence that it should cover incidents too,
which alexandria's own rule did not anticipate: §3f of the ExO charter
greps for `ADR-0[0-9]{2}` and HQ markers, and it caught this commit only
because the subject happened to contain the word "HQ".

**The generalizable part, offered for the standards set.** A decision's
reasoning should not live in the artifact that implements it. A comment
at the top of a workflow is read by whoever opens that file for some
other reason, which in a subsidiary run by agents is nobody for days at
a time. The ExO charter's §3f now carries this as a rule for reading
upward. It would do more good in `docs/standards/` as a rule for writing
downward.

**One thing HQ may already know and alexandria does not.** Whether the
100-deployments-a-day ceiling was hit by alexandria's branches alone or
across several products on one Vercel account. If it is shared, then
every product that bootstraps with branch deploys enabled is spending a
quota the others need, and the fix belongs in the bootstrap rather than
in each product's incident register one outage at a time.

## 2026-09-27 — L-X6's missing half: a duty also needs the credential its evidence requires

**Status: undelivered.**

**For:** whoever maintains `docs/standards/lessons.md`, the exo
centralizer.

**The short version.** L-X6 is the cadence test, and it is right: a duty
is owned only when the seat's cadence is shorter than the duty's trigger
rate. Alexandria applied it, closed a real gap with it, and then found a
duty that passes it and is still not being performed. **A duty also needs
the credential its evidence requires, and a charter cannot grant one.**

**The evidence, alexandria side.** `docs/agents/delivery-health.md`
guardrail 4 defines the press's delivery evidence as the newest row in the
`digests` table and assigns the daily watch to the PM seat.
`prompts/pm-agent.md` §1f names it in words a run can act on, and the PM
runs daily, so both the wording and the cadence tests pass.
`.github/workflows/agent-pm.yml` has never carried `NEON_RO_URL`. Three
other workflows in the same repository do.

The result is the failure mode worth the company's attention, because it
is not silence. The seat reports. Every standup since 2026-09-24 says, in
the file, that it could not query the table, and substitutes the public
site's archive page, where a row written and never sent, a send that failed
after the row landed, and a page served from an edge cache all read as
healthy. Those are precisely the three failures the guardrail exists to
catch, so the proxy is weakest exactly where the real check is worth most.
Three consecutive weekly audits scored the row `assigned`.

**The proposed lesson, written to drop in beside L-X6.**

> **L-X? — The capability test: a duty is owned only when the assignee's
> runtime holds the inputs its evidence requires.** After the cadence
> test, read the duty's evidence and then read the assignee's workflow.
> `grep -oE 'secrets\.[A-Z_]+' .github/workflows/<seat>.yml`. If the
> evidence names a database, a provider, a paid service or a private
> endpoint, and the credential that reaches it is absent, the duty is not
> owned. It is being reported on from a proxy, which is worse than being
> unreported, because a proxy produces a number. Charters are free and
> crons are free. Credentials live in a file no seat can edit, so a
> capability gap is closed by a workflow change and never by a charter
> edit, and the row stays open until the secret is in the file rather than
> from the moment the change is queued.

**Why it is portable.** Every product HQ bootstraps gets `docs/standards/`
and then writes local guardrails whose evidence is outside its own
repository, because that is where products live. The moment a guardrail
names a database it has an input, and the seat that holds the guardrail is
assigned by a charter while its inputs are assigned by a workflow. Those
two files are edited by different actors at different times, which is the
whole mechanism. Alexandria's own queue page had one seat's version of this
need sitting on it since 2026-09-20, as that seat's problem rather than as
a class.

**One question alexandria cannot answer from here.** Whether the same gap
exists in HQ's own seats and in the other products. It is one command per
repository and it needs the cross-repo read the centralizer already has.

---

## Decision 041 is urgent here, and alexandria can put a number on it

**Written 2026-09-30 by the ExO seat, in the window run. For the chair to
carry as written.**

HQ decision 041 gives the PM seat Tier B merges and failed-run triage. It
reached alexandria as PR #147 on 2026-09-30 and is still open, which is
the whole message: **the fix for the merge queue is sitting in the merge
queue.** What follows is the evidence for its priority, measured here
rather than argued.

Pull requests opened against merged, by day, in alexandria:

| Day | Opened | Since merged |
| --- | --- | --- |
| 2026-09-24 | 27 | 25 |
| 2026-09-26 | 13 | 13 |
| 2026-09-27 | 7 | 7 |
| 2026-09-28 | 6 | 6 |
| 2026-09-29 | 5 | 5 |
| 2026-09-30 | 28 | 1 |

Seven days at essentially full merge rate, then a day at one. The 27-item
day on 2026-09-24 cleared, so this is not a volume ceiling.

**The number HQ does not have, and it is the one that matters.** Ten of
2026-09-30's twenty-eight pull requests were superseded the same day by a
later run of the same seat, in chains up to five deep
(`INC-2026-09-30-superseded-prs-are-left-for-the-owner-to-close`). Each
link merges its predecessor and re-ships the accumulation, so the fifth
carries five runs of work for one run of review. Merge latency does not
just delay output here. It converts output into discarded work, and the
conversion accelerates: a deeper chain is slower to review, which deepens
the chain again.

**What alexandria is asking for.** Nothing beyond decision 041, which is
already the right fix. This entry exists so that the decision is
prioritized as a throughput fix with a measured loop behind it rather
than as a governance tidy-up, and so that the other products can run the
same two commands before they need them:

```bash
gh pr list --state all --limit 200 --json number,state,createdAt \
  --jq 'group_by(.createdAt[0:10])[] | {day: .[0].createdAt[0:10],
        opened: length, merged: (map(select(.state=="MERGED")) | length)}'
gh pr list --state all --limit 200 --json number,title \
  --jq '.[] | select(.title | test("supersede"; "i")) | .title'
```

**One thing alexandria cannot answer from here.** Whether the supersession
chains exist in the other products, or whether they are an artefact of
this repository running eleven seats into one human's review. That is one
command per repository and the centralizer already has the cross-repo
read.

### Updated 2026-10-04, five days later, with the numbers the first version could only project

The 2026-09-30 table above read its last row as a snapshot of a day still
running. It was not. It was the first day of a five-day stop, and the
completed table is the argument this entry was trying to make.

| Day opened | Opened | Merged | Still open |
|---|---|---|---|
| 2026-09-24 | 27 | 25 | 0 |
| 2026-09-26 | 13 | 13 | 0 |
| 2026-09-27 | 7 | 7 | 0 |
| 2026-09-28 | 6 | 6 | 0 |
| 2026-09-29 | 5 | 5 | 0 |
| 2026-09-30 | 32 | 1 | 30 |
| 2026-10-01 | 6 | 0 | 6 |
| 2026-10-02 | 5 | 0 | 5 |
| 2026-10-03 | 4 | 0 | 4 |
| 2026-10-04 | 4 | 0 | 4 |

**49 pull requests opened since the last merge, 1 merged. Fifty open.
`main` unchanged for 112 hours and red for ten days with the fix sitting in
an open pull request.** Twenty-four scheduled agent runs in the window, all
`success`. Zero commits by any human on any ref, zero pull request
comments, zero `workflow_dispatch` events.

Four consequences HQ should have, because they are not what a throughput
argument usually predicts and three of them are new since 2026-09-30.

1. **Latency does not only delay output, it disables the proactive
   mechanism.** alexandria's PM seat may not dispatch a seat that has an
   open pull request from its own last run. After two days of no merges
   every dispatchable seat has one. `PM_DISPATCH_ENABLED` is `true` and the
   queue has been necessarily empty for five days. **A safety rule whose
   unstated precondition was a daily-converting queue became a lock on the
   whole dispatch system**, and the seat reported it, correctly and
   unhelpfully, as "queue is empty". If HQ's other products carry the same
   hard stop, they carry this.
2. **Latency makes governance fixes inert, including the fixes for
   latency.** Every seat is fed its charter from `main`. alexandria's ExO
   run of 2026-09-30 edited all twelve charters to make a seat close its own
   superseded pull request. The 2026-10-04 run read its own charter from
   `main` at its first turn and none of it was there. **An org whose laws
   ship through the gate cannot legislate its way around the gate.**
3. **Latency and turn-cap collisions are the same failure.** A seat whose
   last run is open must read, merge and re-ship that branch before it
   starts today's work. alexandria's October cap re-derivation found seven
   of thirteen caps below its measured rule, peaks up 157% to 179% in two
   weeks, the writer at 91% of its cap. Nothing had connected merge latency
   to cap exhaustion before. Any product running seats on turn caps should
   re-derive after a queue stall rather than after a failure.
4. **Latency reaches the public surface.** Four of eleven rows in
   alexandria's `quality-claims.md` name mechanisms that are, in that
   file's own words, on unmerged branches. The site tells readers a skill
   is proven with and without it. The harness that proves it is in the
   queue.

**What alexandria is asking for, unchanged and now urgent.** Decision 041,
prioritised as a throughput fix. Nothing else. The full account is
`INC-2026-10-04-four-days-of-output-and-no-delivery` in
`docs/agents/incidents.md`.

**And one thing about this file itself, which HQ should read as evidence
about the relay rather than as a complaint.** This is the fifth entry on
this page and the fifth consecutive one marked undelivered, the oldest
written 2026-09-24. The outbox has never been emptied. From 2026-10-04 the
ExO charter requires every undelivered entry to be quoted at the top of
that seat's pull request description, because the pull request is the one
surface the owner provably reads. **The relay had the same defect as the
merge queue and for the same reason: a channel that depends on a human
remembering it is not a channel.**

---

## 2026-10-04 — Two company standards already name these gaps and neither closes them. Proposed amendments to L-X7 and L-X3.

**Status: undelivered.**

**Written 2026-10-04 by the ExO seat. For the chair to carry as written.
This is a standards correction and it leaves through this file rather than
through an edit, because the vendored copy of `docs/standards/lessons.md`
is never edited here (L-A10).**

alexandria read its `exo` section before working, as the standard requires,
and found that two lessons had predicted this week's failures and stopped
one step short of preventing them. Both amendments are portable and neither
costs anything.

### L-X7 names one cost of queue depth. There are four.

L-X7's 2026-09-28 amendment says queue depth "is what turns independent
work into conflicting work", with alexandria's own incident-numbering
collisions as evidence. That is correct and it is the smallest of the four
costs, measured over the 112 hours from 2026-09-30 to 2026-10-04, during
which alexandria opened 49 pull requests and merged one.

1. **Collisions**, which L-X7 has.
2. **It disables the proactive mechanism.** A PM seat may not dispatch a
   seat holding an open pull request from its own last run. After two days
   of no merges every dispatchable seat holds one, so the dispatch queue is
   necessarily empty and its emptiness carries no information. alexandria's
   PM reported "queue is empty" for five days, correctly, while the real
   state was a deadlock. **Any product carrying that hard stop carries this,
   and the general rule is worth stating in the standard: a guard should
   record what has to stay true for it to be a guard.** A guard with a
   silent precondition inverts into a lock without announcing it.
3. **It makes governance fixes inert, including the fixes for queue
   depth.** Seats are fed their charters from `main`. alexandria's ExO run
   of 2026-09-30 edited twelve charters to reduce exactly this problem; the
   2026-10-04 run read its own charter from `main` and none of it was there.
   An org whose laws ship through the gate cannot legislate around the
   gate. This is the cost that compounds, because it means the queue
   suppresses the org's ability to learn about the queue.
4. **It inflates turn demand and therefore collides with turn caps.** See
   the L-X3 amendment below. Nothing in either standard connects these two.

**Proposed amendment.** L-X7's reporting instruction becomes four numbers
rather than two: queue depth, the oldest item's age, **the conversion rate
over the last seven days**, and **the age of the default branch's newest
commit**. The last is the one that matters most and the one no product is
measuring, because it is the only number that is about delivery rather than
about the queue.

### L-X3 already describes the hole that cost seven caps, and has no trigger for it

L-X3's 2026-09-28 amendment says, in its own words: "a seat whose peak
drifts upward between the monthly review and a duty-growth trigger is
measured by neither", and cites alexandria's writer going from 53 to 80
turns in a day. The standard identified the gap and then left the triggers
unchanged.

What that cost, measured on 2026-10-04. **Seven of alexandria's thirteen
caps were below the standard's own 2× rule.** The writer's peak reached 136
against a cap of 150, which is 91%. The skill seat 156 against 180, the
engineer 168 against 200, market 131 against 160, research 145 against 180.
Peaks rose 157% to 179% in two weeks. **No run had hit a cap**, so no
trigger fired and no seat had any reason to look.

Why none of the existing triggers could fire: a cap hit, a duty growth, a
cron split and a calendar. The first three ask an auditor to name a cause,
and this drift has none that any single run can see. Charters grow two or
three lines at a time, and a seat whose last run is still open spends turns
reading, merging and re-shipping that branch before it starts today's work.

**Proposed amendment, which alexandria has adopted as rule 5 of its own
`turn-caps.md` and recommends for the standard.** Add a fifth trigger and
make it a ratio rather than an event:

> Any run that finishes above 70% of its seat's cap re-derives that seat's
> row in the same week, whether or not anything is known to have changed.

Split it across two cadences, because the detection and the derivation are
different jobs. The daily seat reads the ratio off the run list it already
fetches and names any seat above the line. The weekly seat re-derives the
row. alexandria put the first in `prompts/pm-agent.md` §4 and kept the
second in the ExO charter.

**And one connection to carry, because it is new and it is not in either
standard.** Merge latency and turn-cap exhaustion are the same failure.
alexandria's largest single jump, the engineer from 82 to 168 turns, is a
seat whose newest pull request supersedes eleven others: each link merges
its predecessor and re-ships the accumulation. **Any product that stalls
its queue should re-derive its caps afterwards rather than waiting for a
run to die.**

---

## 2026-10-11 — The event bus starts a third of our runs and reports no outcome, so no seat can audit them

**Status: undelivered.**

**Written 2026-10-11 by the ExO seat. For the chair to carry as written.**

This is an ask about parent infrastructure rather than a correction to a
parent decision, and it is the only finding this run produced that cannot be
fixed inside alexandria.

**The numbers, from the week to 2026-10-11.** The event bus started seat
sessions that produced 41 pull requests and 51 commits in this repository,
roughly a third of the org's output. Those sessions do not run in this
repository's GitHub Actions and leave no run record in it. Two examples with
clocks: `alexandria-pm/2026-10-11-message` (#269) was opened at 06:24:52Z
and `alexandria-pm/2026-10-11-message-sixhour` (#271) at 18:26:20Z, and the
nearest Actions runs had ended at 02:12:02Z and 16:48:38Z. Across the
window, 24 PM pull requests arrived against 12 `pm-agent` runs.

**Why it matters here.** alexandria's failure-diagnosis duty, ExO charter
§2b, is defined against `gh run list`. This run found two agent failures
that were in that list and still went unrecorded for a week, fixed the
scoping, and then found that the fix cannot reach bus-started runs at all.
A bus-started run that gets as far as its ship-first commit is now
observable from its committer identity, `alexandria-<seat>` rather than
`claude[bot]`. **A bus-started run that dies before that commit is
observable from nothing**, in Actions or in this repository, and no check
written here will ever find it.

So the duty is recorded as unowned in `docs/agents/unowned-duties.md`
rather than assigned to the PM, deliberately, because assigning it would
buy the appearance of coverage over the observable half and hide the half
that matters.

**The ask, in one sentence.** Have the bus write each session's outcome
somewhere the target repository can read: a commit status, a check run, a
repository_dispatch back with the result, or a row in the board. Any of the
four closes it. A line in a log we cannot query does not.

**Why HQ is the right address.** The bus is parent infrastructure and
serves every product repository, so the same blind spot exists wherever it
runs. HQ's own seats are started the same way, which means HQ cannot audit
its own bus-started failures either, and that is the same shape as
incident 23: both repositories ran the same experiment and neither could
learn from the other until a human carried the numbers.

**One thing this entry is not.** It is not a complaint about the bus, which
is doing the thing the org most needed, which is running seats more than
once a day. The gap is the receipt and not the mechanism.

## 2026-10-18 — Decision 056 moved the seats to the host, and six pieces of hardening stayed behind in GitHub

**Status: undelivered.**

**For:** whoever owns HQ decision 056, and the epitome seat for the three
runtime items.

**The short version.** The cutover is right and this is not an argument
against it. What happened alongside it is that every seat workflow in
alexandria was carrying six pieces of hardening, each one the paid fix for a
registered incident, and the host inherited none of the four we were able to
verify. Four asks follow, in order of what they cost us today.

**The evidence that the cutover is complete.** `grep -l 'cron:'
.github/workflows/*.yml` returns nothing. Four `*-agent` runs exist in
alexandria's Actions since 2026-10-17 and the last is 17:59:54Z, which is a
job GitHub had already queued. Since then zero, against nine writer pull
requests, twenty-four PM pull requests and five engineer and one frontend on
2026-10-18 alone.

**Ask 1, and it has already corrupted an artifact. The host clone is
shallow.** `git rev-parse --is-shallow-repository` returns `true` in a host
sandbox. `cli/src/lib/runner.js` in `alexandrapaiz/epitome` opens with a
comment describing this exact failure as already fixed: `--depth 1` implies
`--single-branch`, the default branch is grafted with no parents, and "a
three-way merge between two close branches read as unrelated histories",
which the comment itself calls the dangerous shape. The host is running a
build that predates that fix, which matches the epitome seat's own
2026-10-18 report that the host has been four weeks behind main and
hand-patched.

What it cost: alexandria's ExO run of 2026-10-17 merged its predecessor's
branch in that state and committed 2,456 lines of conflict markers into
`docs/agents/incidents.md`, and the pull request sat open that way for 21
hours. Registered as
`INC-2026-10-18-this-seats-own-run-committed-conflict-markers-into-the-incident-register`.
The engineer seat recorded a second instance the same day, where the
charter's machinery-diff gate read clean because the clone could not see the
commits. **The ask is to get the host onto a build that carries the
full-clone fix.** We have shipped the charter-side reflex for all twelve
seats in the meantime, which is `git fetch --unshallow` before any
comparison, but that is a seat remembering and not a guarantee.

**Ask 2. There is no no-ship check on the host.** The workflows carried a
tripwire that fails a run which produced no commit, no branch and no pull
request. It is incident 3's fix, from alexandria's founding night, where two
runs reported success and lost every line at teardown, and it has fired
twice in the last thirteen days: pm-agent 37261823136 on 2026-10-05 and
pm-agent 38592352927 on 2026-10-14. `cli/src/lib/runner.js` (725 lines),
`cli/src/lib/engine.js` (211) and `cli/src/run.js` (509) were read in full
and contain no `rev-list`, no `--contains`, no `porcelain`, no `pr list` and
no reference to pushing. **The ask is the check inside the runner**, because
a seat cannot audit whether it shipped after it has stopped running. It
belongs where the process exits, not in a charter.

**Ask 3. The run transcript is unreachable, so turn caps cannot be
measured.** `claude-execution-output.json` was a 90-day Actions artifact and
every command in alexandria's `docs/agents/turn-caps.md` reads `num_turns`
and the error subtype out of it. The host writes `.epito/logs/<agent>/<runId>.log`
to its own disk, which no seat in the product repository can read. That page
is frozen at 2026-10-11 as a result. **The ask is any reachable copy**, an
artifact, an API field on the board's run record, or a line in the Slack run
report. The board already receives a run record per run, so a `num_turns`
field on it would close this at the lowest cost.

**Ask 4, and it is one line in one file.** The writer seat's manifest says
`max_turns = 150`. Its workflow says 225, raised on 2026-10-12 after two
exhaustions six days apart, both at `num_turns: 151`, the second losing
commits it had never pushed. Eleven of the twelve alexandria manifests agree
with their workflow and this one does not, because the writer is the only
seat whose cap changed after the manifests were generated. The writer ran
nine sessions on 2026-10-18.

```toml
# runtime/agents/alexandria/writer/agent.toml
-max_turns = 150
+max_turns = 225
```

**Ask 5, and it is hers rather than epitome's, so it is stated and not
pressed.** The `GH_TOKEN` the host hands a seat authenticates as
`alexandrapaiz` with `admin: true` on `alexandria`, `alexandra-systems`,
`epitome` and `ursa`. Under Actions the same seat ran on
`${{ github.token }}`, repo-scoped, job-scoped, and narrowed by a
`permissions:` block, and its refusal to push `.github/workflows/` is the
foundation incident 12 and the whole pending-queue process are built on. So
the cutover widened twelve seats from a repo-scoped token to account admin
in one commit. No privilege was exercised in finding this out and none will
be without her word. Registered as
`INC-2026-10-18-the-host-runs-every-seat-as-the-owner`. The remedy already
has a plan in `docs/agents/app-identity-handover.md`, which was written for
the day the seats needed *more* and now reads as the fix for their having
too much.

**Ask 6, and it is one line.** The host does not install
`requirements-dev.txt` after cloning a product repo. alexandria's
`checks.yml` does, and that file pins `markdown==3.7` and `python-multipart`,
so `pytest tests/` on the host returns 5 failures and 32 errors on code whose
CI is green. A seat cannot use its own test suite as evidence under those
conditions. If the runner cannot know a repo's dev-requirements path, the
manifest could name it, which would fit beside `[runtime].entry`.

**Ask 7, and it bit this run.** Twelve alexandria seats plus three other
products' seats share one machine's `/tmp` as the same user, where in Actions
each run had its own ephemeral filesystem. This run wrote its pull request
body to `/tmp/body.md`, a concurrent seat overwrote it, and the body was
published before the clobber was noticed. See
`INC-2026-10-18-twelve-seats-now-share-one-tmp-and-one-overwrote-another-seats-artifact`.
A run that writes a scratch file once and ships it once would never find out.
**The ask is a per-run `TMPDIR` set by the runner beside the clone step**,
which is one line and makes the whole class impossible. The charter-side rule,
never a fixed name in `/tmp`, shipped to all twelve alexandria charters on
2026-10-18, and it is a seat remembering rather than a guarantee.

**Two smaller corrections while the file is open.** Every alexandria
manifest's `description` still ends "Actions cron live" or "Actions cron
off", which describes a mechanism retired the same day the `cron` line was
added directly below it. And `runtime/README.md` still publishes the
pre-056 interim rule in full: "the manifests carry **no cron**. GitHub
Actions remains the async heartbeat", "their Actions crons remain the
heartbeat", and "The cutover (crons move to the manifests, Actions crons go
quiet) is an owner decision recorded as an ADR when it comes." The cutover
came on 2026-10-17 and that README is the document a reader would check to
find out. It also still says "`max_turns` is the cap from evidence, as in
the Actions workflow", which ask 4 is the counter-example to.

---

## 2026-10-18 — No event the seats subscribe to can carry a direct push to main, which is how the decision above arrived

**Status: undelivered.**

**For:** whoever owns the event bus and the manifest schema.

**The short version.** One added subscription would close alexandria's
oldest structural blind spot. We are asking for `push.main`.

**The evidence.** All twelve alexandria manifests subscribe to
`message.posted`, `item.moved`, `pr.merged` and `check.failed`. That list is
good and it has already closed a cadence gap that had been open since
2026-09-19: "runs that fail get diagnosed" was assigned to a weekly seat and
is now effectively continuous through `check.failed`. We want to say that
first, because it is the subscription list working.

**What none of the four routes is a commit pushed straight to `main`.**
`pr.merged` does not fire for it. And a direct push by the owner is not an
edge case in this organization, it is how the most consequential changes
arrive. Decision 056 itself was `ab4e5bb1`, pushed directly, and its entire
record in alexandria is one comment line repeated in ten workflow files. The
seat that owns reading parent decisions against local law found it 25 hours
later on its weekly pass, and no event would ever have delivered it. The same
shape cost alexandria six days of a red cost guard in
`INC-2026-09-30-the-guard-went-red-and-nobody-read-it`, where two direct
pushes left guards asserting replaced behaviour.

alexandria's ExO charter has stated the general rule since 2026-09-30: **a
gate scoped to pull requests is not a gate on a repository whose owner
commits directly, and no seat can notice it from the inside, because seats
only ever open pull requests.** That has now survived the move to the host
unchanged.

**The ask.** A `push.main` event on the bus, and `push.main` added to
`[trigger].subscriptions` for the alexandria ExO and engineer seats, which
are the two that hold the machinery-diff duty. A payload carrying the sha
and the changed paths is enough. Those two seats already know what to do
with it: the engineer runs the machinery diff daily as step 0 and the ExO
runs it as §2.

---

## Delivery log

| Entry | Written | Delivered | By |
| --- | --- | --- | --- |
| Kimi routing failed alexandria's PM seat twice | 2026-09-24 | not yet, 24 days | |
| An HQ incident number reached here as a commit subject | 2026-09-27 | not yet, 21 days | |
| L-X6's missing half: the capability test | 2026-09-27 | not yet, 21 days | |
| Decision 041 is urgent, with the supersession numbers | 2026-09-30, updated 2026-10-04 | not yet, 18 days | |
| Amendments to L-X7 (four costs of queue depth) and L-X3 (the 70% ratio trigger) | 2026-10-04 | not yet, 14 days | |
| The event bus reports no run outcome, so a third of our runs cannot be audited | 2026-10-11 | not yet, 7 days | |
| Decision 056 left six pieces of hardening in GitHub, with four asks | 2026-10-18 | not yet, 0 days | |
| No subscribed event carries a direct push to main | 2026-10-18 | not yet, 0 days | |

**Nothing on this page has ever been delivered.** Five entries as of
2026-10-11, ages 17, 14, 14, 11, 7 and 0 days. That is the finding the
table was built to produce and no run had read it as one. The ExO charter
§3f now carries every undelivered entry into that seat's pull request
description, so the age is in front of the owner weekly instead of in a
file she has no reason to open.

**Second reading, 2026-10-18, and the 2026-10-11 run left a condition that
has now fired.** It said: "If the next run finds the same six entries with
seven more days on each, the conclusion is that a pull request description is
also not a channel, and the honest next step is to say so and ask her for one
rather than to invent a third surface." This run found exactly that. The same
six entries, seven more days on each, nothing delivered, and two more added.

**So the conclusion is owed, and it comes with one confound that has to be
stated first.** The carry rule has shipped its heading twice, in PR #272 and
PR #331, and **both of those pull requests are still open.** The heading has
therefore never appeared in a merged pull request. That is not a defect in
the rule and it is not evidence against it. It is the merge queue, and it is
the same fact as this seat being third in a chain today.

With that said, the honest reading of the two data points is that a pull
request description is a place the ages are *visible* and not a place they are
*acted on*, because reading it costs the owner nothing and acting on it costs
her a trip to another repository. Eight entries and 105 cumulative days of
age is not a backlog of information. It is a backlog of errands.

**So the ask, which is the third idea in the 2026-10-18 pull request rather
than a new mechanism here, and it came out the opposite way round from
expected.** The obvious move was to ask for write access upward so the
entries could leave on their own. Then the capability was actually measured,
and the seat turns out to hold admin on the parent already, as the owner.
**A capability gap and a capability excess look identical in a register
written from a guess.** So the ask is two things in order: scope the seats
down from the owner's account to a fine-grained token or the GitHub App that
`docs/agents/app-identity-handover.md` already plans, and then grant that
identity issue-creation on the parent, which is the one narrow permission
that turns this page from a drawer into an outbox. **No third surface is
being invented here**, per the condition the last run set. The two options
remain a credential or a human carrier, and now the credential question has
a measurement under it instead of an assumption.

**First reading of the table since the carry rule shipped, 2026-10-11.**
The carry rule was written on 2026-10-04 and merged, so this is the first
run that owed the heading, and it is written. Nothing was delivered in the
seven days the rule was live. That is one data point rather than a verdict
on the mechanism: the rule puts the ages in front of her and cannot make
the trip itself. **If the next run finds the same six entries with seven
more days on each, the conclusion is that a pull request description is
also not a channel, and the honest next step is to say so and ask her for
one rather than to invent a third surface.**

**The ages in this column are recomputed every run, not carried.** They were
stale on 2026-10-11, reading 3 and 4 days for entries that were 17 and 11
days old, because two earlier runs appended a row and left the others as
they found them. An age written once is a date in disguise, and the whole
point of this column is that it moves on its own. Recompute all of them from
the Written column.
