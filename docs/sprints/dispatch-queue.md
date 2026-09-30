# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-09-30, ~03:55 UTC (Wednesday, synchronous — second pass this window)

This is a second standup inside the same synchronous session as
[#150](https://github.com/alexandrapaiz/alexandria/pull/150), opened
about an hour earlier (~02:55 UTC). This run supersedes it: the branch
this file lives on merged #150's branch first (fast-forward, no
conflict), so nothing in that run's diagnosis is lost, only refreshed
against the last hour. Close #150 without merging once this lands.

**What changed in the hour between the two runs.** Eight more pull
requests opened, one from almost every seat this org runs
(#154 frontend, #155 writer, #156 sales, #157 security, #158 engineer,
#159 skill, #160 exo, #161 okr, #162 research, #163 market, #164
finance), each a `window`-triggered run same as this one, not something
this seat fired. The practical effect: the one dispatch candidate #150
found (frontend, blocked only by a 403 in the dispatch API itself) now
has an open PR of its own (#154), so it drops out of today's queue for
an ordinary reason instead of the 403.

## Failures, refreshed against #150's diagnosis

#150 classified the last 24 hours into three causes; nothing new
happened to reclassify, so this section states what moved, not the
whole read again (full detail stays in #150's description, GitHub's
copy of this file at that commit).

1. **Main's own checks were red** (`tests/test_press_resilience.py`
   over ADR-32's cost budget, `tests/test_run_report.py` breaking on an
   unset `GH_TOKEN` polluting `gh`'s JSON output). #150 hand off this to
   engineer. **It is now in flight**: PR #158 ("break-fix on main's red
   checks") is open, built on top of #153, and its own `checks` run
   alternates failure/success in the last ten minutes
   (36665897438 success, 36665565812 through 36665107... failure,
   36665989667 queued as of this writing) — consistent with the fix
   being actively iterated on right now rather than stuck. Nothing to
   hand off again; this is the seat's own open PR doing the job.
2. **The `chair/langfuse-traces` branch (PR #139) still fails
   `pm-agent`/`okr-agent`/`market-agent`/`finance-agent` before any job
   starts.** Same four run IDs as #150 found
   (36659107421/36659106719/36659105929/36659105241,
   all 2026-09-29T02:16 UTC) — no new occurrence since, because nothing
   has pushed to that branch again. Still asked of HQ per the board's
   own note that workflow files are HQ's surface, not this repo's.
3. **`checks` noise inherited from item 1** kept accumulating while the
   fix was in flight — roughly 45 failed `checks` runs in the trailing
   24 hours by direct count (`gh run list --limit 200`, filtered), up
   from #150's ~28, all the same regression, no separate handoff.
   Expect this count to stop climbing once PR #158 merges to main.

No new failure class. Nothing here needs a fresh incident entry; item 1
already reads as a repeat of a diagnosed defect with a fix underway, and
item 2 is an unchanged repeat already handed to HQ.

**Classified per standards/pm.md §11.7, for the record.** All three
items above are *real defect* (1, already incident-handled, handoff to
engineer, in flight) or *configuration* (2, asked of HQ) or *tripwire
false alarm* (3, the PR exists, no action). None is *transient*, so
`gh run rerun` was not called on anything this run — a second identical
failure on unchanged inputs would just fail identically again. The
repeating `engineer-agent` failures noted in the last 24 hours
(`36600800512`, `36513112021`, `36466106318`, and earlier) are the same
already-registered `INC-2026-09-26-run-report-dash-echo` family — real
defect, already handed to the ExO (outside every other seat's writable
surface), ship-first held in every case (a PR exists for each failed
run). No new entry.

## Run health

**Fleet.** As of 03:55 UTC: one `checks` run queued
([36665989667+](https://github.com/alexandrapaiz/alexandria/actions/runs/36665989667)
family, on PR #152's branch), and the last fifteen `checks` runs show a
mix of failure and success consistent with item 1 above being fixed
live. No `workflow_dispatch` or `schedule` run is failing right now that
isn't already covered in Failures. All of tonight's dispatches
(`engineer-agent`, `skill-agent`, and the eleven `window`-triggered PRs)
were fired by the owner or the chair, not by this seat — confirmed by
the actor field and by the two-hour rule itself: multiple dispatches
inside the last two hours is what puts this session in synchronous mode
in the first place.

**Delivery — corrected mid-run.** An earlier draft of this section used
`site/content/issues/`'s newest filename as a proxy for the press and
called the still-unconfirmed W40 file a red finding. That proxy is
wrong and PR #130 (merged, engineer, sprint item 1) already says so in
its own words: "nothing in this repository publishes a digest to the
site... the check that looked for one was reading a signal with no
connection to the question." Re-checked properly this pass, with the
tool PR #130 built for exactly this:

```
$ python3 tools/delivery_health.py
  unknown  press     no DATABASE_URL in this environment...
  unknown  pipeline  no DATABASE_URL in this environment...
  ok       site      1 issue(s) published, newest 2026-W39
  ok       mcp       up, and refusing unauthenticated calls
exit: 2 (nothing failing, something unanswerable from here)
```

- **The press.** `unknown`, not red. This sandbox has no `DATABASE_URL`
  (filed `urgent` in the ledger per PR #130, already carried in Pending
  below), so guardrail 4's own artifact cannot be read from here — the
  tool says so honestly rather than guessing from the site. Separately,
  a research seat entry in `docs/agents/incidents.md`
  (`INC-2026-09-28-kind-test-quoted-and-violated`, which has its own
  `NEON_RO_URL`) states as an aside that **the `digests` row for
  2026-W39 was written 2026-09-28 at 09:01 UTC** — Monday, on schedule.
  That is one seat's byproduct evidence answering another seat's "not
  meetable by any seat" verdict in PR #130, never connected until this
  run. Read together: **Monday's send did fire.** Sprint item 1's own
  acceptance criteria (a definitive answer, any code fix merged, this
  week's issue confirmed live in `digests`) all read as met once these
  two PRs are read side by side, which is exactly the kind of gap a
  standup exists to close. Site: today's expected newest label is still
  `2026-W39` (the press labels an issue by the week that just ended, and
  the week that ends today, W40, isn't over) — `2026-W39` being newest
  is the healthy, on-schedule state, not a gap.
- **The site.** `ok`. Reachable, 1 issue published, newest 2026-W39,
  confirmed by both the tool and a direct probe (`200`).
- **The MCP server.** `ok`, per the tool — up and refusing
  unauthenticated calls. This corrects the prior draft's "could not be
  checked": the probe just needed the tool's own client, not a guessed
  path on the main domain.

## Dispatch

**No entries.** Every seat charter §5 allows this seat to dispatch —
engineer, research, market, writer, frontend, skill, security, okr —
already holds at least one open pull request as of this run:

| seat | open PR(s) |
| --- | --- |
| engineer | #60, #141, #142, #149, #153, #158 |
| research | #138, #145, #162 |
| market | #163 |
| writer | #155 |
| frontend | #154 |
| skill | #140, #146, #151, #152, #159 |
| security | #157 |
| okr | #161 |

The hard stop ("never dispatch a seat that already has an open pull
request from its last run") excludes all eight without exception. This
is a plain consequence of the window wave documented above, not a gap
in coverage: nothing this run found needs a ninth actor added tonight.

## Sprint as milestone (owner's live instruction, tonight)

The owner said, live, to run sprints as milestones from now on: close
one when its goal ships, name the next. Reading that as an instruction
for how this run treats the open sprint, not as licence to rewrite
`docs/sprints/README.md`'s format on a standup's own authority with no
written ruling to cite — that edit, if it is meant to be durable, is
the ExO's or the chair's to make in the standard.

**Sprint 2026-09-28's goal:** "Close the gap between merged and running,
and let the skill library show its receipts," five items. Checked
against what has actually merged, not against open PR titles:

1. Diagnose the Monday press send — **done**, per the correction above:
   PR #130 merged, all three acceptance clauses read as met once read
   beside the research seat's incident entry.
2. Deploy-drift guard for the pipeline crons — **not done**. Confirmed
   by `docs/agents/incidents.md`'s own line: "the guard itself does not
   exist yet." No PR since claims it either.
3. Skill validation receipts on the skill library pages — **done**. PR
   #133 (merged, engineer run 10, "the skill library shows its receipts,
   and the field that had not rendered since 2026-09-18").
4. Rewrite the trigger-test decoy panel — **in flight, not merged**. PR
   #159 (draft, this window) reads as this item; not done yet.
5. Ship the Left-Behind Index as a public page — **in flight, not
   merged**. PR #154 (draft, this window, frontend) is open; not
   confirmed done yet.

**Verdict: the goal has not shipped.** Two of five items are genuinely
open (2 has no PR at all; 4 and 5 are draft PRs from tonight, not yet
ready). The sprint is not closed this run. Once #159 and #154 land and
item 2 gets a PR, the goal is a same-day close under the owner's new
rule rather than waiting for next Monday — worth naming so the next run
does not treat Monday as a hard boundary out of habit.

## Tier B — what this run would merge, and why nothing was

**PR #147 ("PMs own merges and failed-run triage") is still open, not
merged** (`gh pr view 147` shows `OPEN`, mergeable). The owner's
instruction tonight was to merge under Tier B only if that authority
has landed on this repo — it has not, so nothing below was merged. This
is the list against `docs/standards/pm.md` §10's six conditions from
PR #147's own diff, checked as a dry run.

**Would merge, all six conditions hold:**

- **#140** (skill) — `skills/`, `docs/agents/incidents.md`,
  `docs/ideas.md`, `docs/research/reading-queue.md`. No Tier C path, no
  checks defined, mergeable, 2 hours old, not draft.
- **#161** (okr) — touches only `docs/okrs/okrs-2026-Q4.md`. Clean,
  mergeable, 8 minutes old.
- **#144** (exo) — all twelve `.github/workflows/agent-*.yml` files,
  which §10's rewrite moves from Tier C to Tier B ("workflows... that HQ
  syncs into a product repo"). Technically clears all six conditions,
  and named separately because it is the riskiest of the three: a
  fleet-wide workflow change with zero checks run against it yet
  (`checks=set()`, not merely green). Worth the owner's own look once
  the authority lands, not a run-it-and-see.

**Would not merge:**

- **#141, #142** (engineer) — each superseded by a later PR from the
  same seat (#153, then #158; #149), by that PR's own title. Merging
  the superseded branch now ships work its own author has already
  moved past.
- **#138** (research), **#149** (engineer) — each touches a path under
  `prompts/`, which stays Tier C without exception regardless of what
  else is in the diff.
- **#146, #151** (skill) — checks red (condition 3), the same
  main-checks regression PR #158 is fixing; expect these to clear once
  #158 merges.
- **#145** (research) — `mergeable: CONFLICTING` (condition 5).
- **#60** (engineer) — 229 hours old, over the seven-day line in
  condition 6, with no evidence of recent activity this run could find.
  Reads as a *close* candidate under §11.6 ("older and idle: close it
  with a one-line note"), not a merge one — flagging rather than acting,
  since it is also the PR `pending.md` has named "waiting only on your
  merge" for over a week, and closing it needs the owner's eyes given
  that history.
- **#164** (finance) — a month-end close report from a seat this
  charter (§5) names as dormant. Financial reporting content plus a
  dormant seat's output is a judgment call this seat should ask for
  rather than guess at, per the relay rule.

## Pending items past their date

Not reconciled in full this run (standup mode writes this file alone,
per charter §4; full `pending.md` reconciliation is ceremony-only, next
due Monday 2026-10-05). Two items are worth naming rather than waiting
for that date:

- **The Polar Merchant-of-Record account (ADR-30) was due 2026-09-26
  and is now four days overdue.** No live keys appear anywhere in the
  codebase as of this checkout. O1 KR1 needs the $20 spine purchasable
  by 2026-10-13, 13 days out, and checkout wiring cannot start until
  this account exists. Owner-only action, unchanged from the last three
  standups.
- **PR #147** ("PMs own merges and failed-run triage") is still open.
  It is Tier C, the chair named it owner-merge, and it is what would
  authorize this seat to start merging other seats' Tier B pull
  requests. Until it merges, this run (like #150) does the failed-run
  triage duty but merges nothing beyond its own knowledge surface.

`docs/sprints/pending.md` itself was last updated 2026-09-28 (the last
ceremony) and is not stale enough yet to flag on its own — two days old,
next full pass due in five more days.

## The company board — could not read the inbox or reply there

The owner, live, asked this run to read `pm`'s inbox on
`board.libraryofalexandria.dev` (`GET /api/messages?to_seat=pm&...`,
bearer `BOARD_RUNTIME_TOKEN`) and reply there in first person once the
work was done. This sandbox has neither `BOARD_API_URL` nor
`BOARD_RUNTIME_TOKEN` set — confirmed by `env`, and confirmed again by
probing the board directly: even `GET /api/health`, which
`docs/board.md` documents as requiring nothing, answers `401` with no
token from here. `docs/board.md`'s own table says a GitHub-runner seat
gets these two as Actions secrets synced from Infisical; this run is
not executing as that runner, so it never received them.

**This is the one thing this run genuinely could not do tonight.** No
inbox message addressed to `pm` was read, and no reply was posted to
the board — not because nothing was owed, but because there is no door
open to it from here. The GitHub Projects board mirror has the same
gap for an unrelated reason: `gh project list --owner alexandrapaiz`
returns `403 Resource not accessible by personal access token`.

If the owner has something specific addressed to `pm` on the board
right now, relaying it directly in this conversation is the fastest
path — this session stays live for the rest of the work window. The
standing fix is giving this run's environment the same two board
secrets the `agent-pm.yml` workflow already carries.

## Linear trial

Not checked this run (no new signal surfaced, standup budget). Still on
trial per the 2026-09-19 ruling; last confirmed active 2026-09-28.

## Dispatched by the PM

1. **frontend**, 2026-09-30, ~02:55 UTC (from #150). Attempted, not
   fired. `HTTP 403: Resource not accessible by integration`, the same
   shape as `INC-2026-09-24-dispatch-403` and
   `INC-2026-09-29-dispatch-403-repeat`, a third occurrence. No run URL
   exists because no run was created.
2. **This run (~03:55 UTC): nothing fired or attempted.** No seat
   cleared the hard stop (see Dispatch above), so there was nothing to
   try.
