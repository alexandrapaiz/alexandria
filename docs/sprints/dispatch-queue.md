# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-09-30 (Wednesday, synchronous — the owner is on)

The owner is present live (~03:15 UTC) and told this seat directly to run
the standup now, read the board first, triage the last 24 hours of failed
runs, and dispatch per the criteria. Per standard §11.4, presence lifts the
two-hour dispatch wait, not the ceilings; per §11.5, `PM_DISPATCH_ENABLED`
is `true`.

**Board and messages, read first.** `alexandria`'s board and its messages
to `pm` were read before anything else. Two things worth naming:

1. **PMs owning merges and failed-run triage is a company decision
   (decision 041), and this repo's copy is not active yet.** PR #147
   vendors it into `docs/standards/pm.md` and `agent-pm.yml`: three
   autonomy tiers instead of two, the PM merging Tier B under six written
   conditions, and this run's own Failures section below. Chair
   `hq-langfuse` named it as owner-merged, Tier C, because it changes the
   tiers themselves — it is not this seat's to merge, and it has not
   merged yet (`gh pr view 147` still shows `OPEN`). Until it does, this
   run does the triage duty below but merges nothing beyond its own
   knowledge surface, because the standard that would authorize merging
   other seats' pull requests is itself still waiting on that same merge.
   Once #147 lands, the next standup starts merging eligible Tier B pull
   requests under the six conditions in `pm.md` §10.
2. **A new working rule for every seat, posted tonight:** inbox (the
   board's messages) first, claim before a shared edit, done with the PR
   link. Followed in this run: read messages before touching anything,
   this file is the one shared surface touched, and the PR link is
   posted back as a board note per the closing section below.

## Failures (last 24 hours)

28 failed runs since 2026-09-29T02:45 UTC (`gh run list --status failure
--created ">=2026-09-29T02:45:36Z"`). They reduce to three distinct causes,
not 28 distinct problems; each is read and classified below rather than
listed 28 times.

**1. Real defect — main's own checks are red on two tests, and every open
PR inherits it.** Five direct pushes to `main` failed identically tonight:
[36656467732](https://github.com/alexandrapaiz/alexandria/actions/runs/36656467732),
[36658539877](https://github.com/alexandrapaiz/alexandria/actions/runs/36658539877),
[36659811322](https://github.com/alexandrapaiz/alexandria/actions/runs/36659811322),
[36660234129](https://github.com/alexandrapaiz/alexandria/actions/runs/36660234129),
[36660717986](https://github.com/alexandrapaiz/alexandria/actions/runs/36660717986).
Same job, `digest request fits the model's budget`, same two failing steps
every time:

   - *"the press survives a provider that changed under it"*
     (`tests/test_press_resilience.py`) fails two checks. `report.cost <
     0.15` now reads `$0.1628 an issue` against ADR-32's roughly-$0.05
     budget, more than triple. And the retry-after backoff check
     (`slept == [1.0, 1.0]`, honouring the provider's own `retry-after: 1`
     header) now sees a longer, schedule-driven sleep instead — the code
     and the test disagree on whether a live 429 header or a fixed backoff
     schedule wins. Tonight's Kimi K2 migration of triage/interpret is the
     likeliest cause of both, but that is a hypothesis for the engineer to
     confirm, not a diagnosis this run made.
   - *"the run report survives the container's shell"*
     (`tests/test_run_report.py`) fails with a `JSONDecodeError`:
     `tools/run_report.py` shells out to `gh pr list`, and without a
     `GH_TOKEN` in the test's shell, `gh` prints a warning to stdout ahead
     of the JSON the script emits, and the test's parser chokes on the
     warning line.

   Confirmed to be the same defect everywhere, not per-branch flakiness:
   the identical two steps fail on `main` and on the open draft PR #146
   (`gh pr view 146` shows the same job red), and on every `checks` run
   this session inspected on `skill/2026-09-30-skill-evals`,
   `skill/2026-09-30-containment-and-security`,
   `engineer/2026-09-30-skill-registrar-and-evals`, and
   `engineer/2026-09-30-evidence-grade-and-practices` — `pull_request`
   checks build against `main`, so every branch inherits `main`'s own
   regression. **Not transient**: identical failure five times running on
   `main` alone, and a deterministic test does not change on a rerun, so
   none were rerun. **Handoff:** the engineer seat, next run, with the two
   file names and the two failing check names above. Not dispatched this
   run — engineer already holds two open pull requests (#141, #142) and a
   run in progress as this standup was written
   ([36661171059](https://github.com/alexandrapaiz/alexandria/actions/runs/36661171059)),
   which is the hard stop in standard §11.4. A board item carries it so it
   is not lost before engineer's next run (see below).

**2. Configuration, asked of HQ — four agent workflows fail before any job
starts, on an unmerged branch.**
[36659107421](https://github.com/alexandrapaiz/alexandria/actions/runs/36659107421) (pm-agent),
[36659106719](https://github.com/alexandrapaiz/alexandria/actions/runs/36659106719) (okr-agent),
[36659105929](https://github.com/alexandrapaiz/alexandria/actions/runs/36659105929) (market-agent),
[36659105241](https://github.com/alexandrapaiz/alexandria/actions/runs/36659105241) (finance-agent),
all `push` events on `chair/langfuse-traces` (PR #139, open), each with
zero jobs and GitHub's own "this run likely failed because of a workflow
file issue." A plain YAML parse of all four files off that branch comes
back clean, so the fault is in GitHub's stricter Actions schema, not a
typo this run could find by inspection. Per tonight's own board note from
`chair:hq-langfuse` ("workflow files and runtime machinery belong to HQ;
product seats hand fixes to alexandra-systems/exo-centralizer instead of
editing them"), this is asked of HQ rather than diagnosed further or
edited here. No rerun — a schema problem repeats identically. It also
means PR #139 cannot merge as written, which is its own gate.

**3. False alarms — the same defect from item 1, repeating on every open
PR's own checks run.** Roughly nineteen more `checks` runs tonight on
`skill/2026-09-30-skill-evals`, `skill/2026-09-30-containment-and-security`,
`engineer/2026-09-30-skill-registrar-and-evals`, and
`engineer/2026-09-30-evidence-grade-and-practices` — each PR still exists
and its author is iterating, and each failure is item 1's regression
inherited from `main`, confirmed at the job/step level on three of them,
not a new problem in that PR's own diff. No separate handoff. Two of the
skill branches additionally fail a third, branch-local step ("the skill
library shows its receipts, and they describe today's text") that did not
appear on the engineer branches — left to the skill seat as its own, since
both PRs are still open and unmerged.

## Run health

**Fleet health.** Covered in full above (Failures). Beyond those: an
`engineer-agent` run is in progress
([36661171059](https://github.com/alexandrapaiz/alexandria/actions/runs/36661171059)),
an `exo-agent` run is in progress
([36660858251](https://github.com/alexandrapaiz/alexandria/actions/runs/36660858251)),
and a `skill-agent` run is in progress
([36660409051](https://github.com/alexandrapaiz/alexandria/actions/runs/36660409051))
as this standup was written — all three `workflow_dispatch`, triggered
directly by the owner tonight (`alexandrapaiz`, confirmed via the runs'
own actor field), consistent with the synchronous session, not a
PM-fired dispatch.

**Delivery health.** Not rechecked this run beyond the Failures section
above — the last confirmed reading (2026-09-29 standup) had the site and
MCP server both up and the press unconfirmed for lack of a database
credential in this sandbox; nothing since then changes that picture
enough to redo the check inside a standup's turn budget.

## Dispatch

One candidate this run carries fresh, named evidence and clears every
hard stop in standard §11.3/§11.4.

### 1. frontend — sprint item 5 is due this week and the seat has not run since before the sprint opened

**Trigger.** `docs/sprints/sprint-2026-09-28.md` item 5 assigns "Ship the
Left-Behind Index as a public page" to frontend, in the sprint that opened
2026-09-28 and runs through 2026-10-04. `gh run list --workflow=agent-
frontend.yml` shows frontend's last run was 2026-09-26T00:47:57Z, two days
before this sprint even started — no run at all this sprint, and no open
pull request from a `frontend/*` branch.

**Cost of skipping it today.** The item is the most direct lever the
sprint file names on the OKR benchmark's weakest axis (product surface,
1.3 at baseline, 2.0 at the 2026-09-24 check-in), and it closes two
10-day-old accepted ledger entries at once. Every day it sits unstarted
is a day closer to the 2026-10-13 launch date with the weakest axis
untouched.

**No open PR blocks this**, and this is not a Tier-B-merge situation —
it is a plain dispatch under the criteria, which stands regardless of
PR #147's status.

**Attempted this run, not fired.** Both standard §11.4/§11.5 conditions
held (`PM_DISPATCH_ENABLED` true, synchronous mode named by the owner's
own dispatch), so this run tried to fire it for real. The attempt 403'd:

```
could not create workflow dispatch event: HTTP 403: Resource not
accessible by integration
(https://api.github.com/repos/alexandrapaiz/alexandria/actions/workflows/361059087/dispatches)
```

This is the same failure shape as `INC-2026-09-24-dispatch-403` and
`INC-2026-09-29-dispatch-403-repeat` — a third occurrence of one unfixed
defect in how this workflow's own token calls the dispatch API, now
against a third seat's workflow. Filing the incident entry itself is
outside this run's writable surface (`docs/agents/incidents.md` is not
`docs/sprints/` or `docs/ideas.md`); naming the repeat here is this run's
half of "check the register before you ship," and the other half —
actually appending it — is owed to whichever seat writes there next. The
command below is unchanged and ready for the owner or chair to run by
hand with their own token, same as the last two times.

```
gh workflow run agent-frontend.yml \
  -f owner_instructions='Sprint item 5, docs/sprints/sprint-2026-09-28.md
(on main): "Ship the Left-Behind Index as a public page — closes two
accepted, unbuilt ledger entries at once (sales'\'' Left-Behind Index page,
market'\''s make left behind the public flagship), both 10 days old, over
the existing deprecated_claims view with no new backend needed. Also the
most direct lever on the OKR benchmark'\''s weakest axis by far: product
surface scored 1.3 at baseline and 2.0 at the 2026-09-24 check-in, still
the lowest of the five axes. Done means: a page rendering the current
deprecated-claims list with dates and citations, linked from the site
nav, screenshotted at the frontend seat'\''s usual viewports." This is
the full item verbatim; no new scope is added. Your seat has not run
since 2026-09-26, before this sprint opened, so this closes that gap.'
```

**Result:** 403, no run created. See above.

**Not proposed for any other seat.** engineer, research, and skill each
already hold open pull requests or in-progress runs (the hard stop).
market and security have no fresh, evidenced trigger beyond their normal
cadence — security's monthly automatic-merge audit (ADR-37 guardrail 6)
falls on the 1st, which is tomorrow, not today. okr's own monthly
check-in is scheduled for 2026-10-01 on its own cron; nothing suggests
that cron will not fire. writer ran as recently as 2026-09-29T20:17 and
has no gap to close.

## Pending items past their date

Not reconciled this run (standup mode writes this file alone, per charter
§4; full `pending.md` reconciliation is ceremony-only, §1d, next due
Monday 2026-10-05). Worth naming here rather than waiting: PR #147 itself
(above) and the `DATABASE_URL` read-only credential, both still open,
owner-only asks carried in `pending.md` already.

## Linear trial

Not checked this run (no new signal, standup budget). Still on trial per
the 2026-09-19 ruling.

## Dispatched by the PM

1. **frontend**, 2026-09-30, attempted, not fired. `HTTP 403: Resource
   not accessible by integration`, the same shape as
   `INC-2026-09-24-dispatch-403` and `INC-2026-09-29-dispatch-403-repeat`,
   now a third occurrence. Full instruction: see entry 1 above. No run URL
   exists because no run was created.
