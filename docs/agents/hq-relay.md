# Relay to HQ — what alexandria owes Alexandra Systems upward

**Enforced at:** prompts/exo-agent.md §3f, which also carries every
undelivered entry into that seat's pull request description. The ExO seat
writes entries.
The chair carries them, because no automated channel exists yet.

Seats never message each other and no seat in this repository can write
to `alexandrapaiz/alexandra-systems`. So evidence that matters to the
parent stops here unless a human moves it. This file is the outbox. Each
entry is written to be copied into an HQ issue or a chair message with
no editing, per the standard the PM's dispatch queue already uses: if
the carrier has to compose anything, the note did not work.

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

## Delivery log

| Entry | Written | Delivered | By |
| --- | --- | --- | --- |
| Kimi routing failed alexandria's PM seat twice | 2026-09-24 | not yet, 3 days | |
| An HQ incident number reached here as a commit subject | 2026-09-27 | not yet | |
| L-X6's missing half: the capability test | 2026-09-27 | not yet | |
| Decision 041 is urgent, with the supersession numbers | 2026-09-30, updated 2026-10-04 | not yet, 4 days | |

**Nothing on this page has ever been delivered.** Four entries, ages 10,
7, 7 and 4 days as of 2026-10-04. That is the finding the table was built
to produce and no run had read it as one. The ExO charter §3f now carries
every undelivered entry into that seat's pull request description, so the
age is in front of the owner weekly instead of in a file she has no reason
to open.
