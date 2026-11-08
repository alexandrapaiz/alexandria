# Dispatch queue, 2026-11-08, ~23:10 UTC (hook pass, re-fire of the 11:05:25Z slot)

**This run was triggered by a re-fire.** The scheduled 2026-11-08T11:05:25Z
cron slot died at turn 1 on a provider refusal (see the queue gauge below);
the provider's own limit reset at 2026-11-08T23:00:00Z and this seat was
re-fired after that. Filed as
`INC-2026-11-08-monthly-spend-limit-silenced-the-fleet-for-six-days` in this
pull request, because it is a bigger instance of a class this register
already names twice. This is the standup for 2026-11-08 (a Sunday, not a
Monday), so sections 1 through 3 of the charter do not run today.

## Queue gauge, first because the threshold is past (owner's rule)

**`main` has not moved in about 157.5 hours (6.6 days), more than three
times the 48-hour threshold. Dispatch is deadlocked, and the cause is not
capacity, it is the provider.**

1. **`main`'s age and check state.** Tip is `c60702e` (merge of #719),
   2026-11-02T09:40:09Z, **~157.5 hours old**. The newest `checks.yml` run
   recorded against `branch=main` is `success` (created 2026-11-02T09:04:09Z),
   but its `headSha` (`b9b1d1b…`) does not match the current tip (`c60702e`,
   the merge commit itself) — no post-merge `checks` run exists for the tip
   that is actually on `main` right now. Flagging the gap rather than calling
   `main` green on a commit it never ran against; the last commit it did
   check was green.
2. **Open pull requests.** 54 open, 7 opened since the last merge to `main`
   (2026-11-02T09:40:09Z): #799 and #800 (distribution, vendoring), #801
   (this seat's own, still open from 2026-11-03), and #802/#803/#804/#805
   (exo/engineer/writer/this seat, all four opened in the last ten minutes as
   the fleet's hook slots re-fired together right after the provider's
   23:00Z reset).
3. **Conversion, 7 days** (300 PRs fetched, oldest 2026-10-25, not
   truncated). **60 merged / 146 opened (0.41).**
4. **Deepest open chain.** #794 (security, "eleventh wake; builds on #784"),
   **depth 14.** Unchanged in kind from the depth-13 chain the charter's own
   history already names as a standing problem; this one is one link deeper.
   **This repository is blocked on merges, and has been for six and a half
   days.**

**Why the queue below is empty, and why that is not the finding.** The hard
stop in charter §5 forbids proposing a dispatch for any seat whose last pull
request is still open, unless the instruction explicitly builds on that
branch. Checked against the open-PR list fetched for this pass: engineer
(#803), research (#783/#777/#792/#796/#760, five of them), writer (#804),
frontend (#790/#678), skill (#767/#772/#782/#795, four of them), and security
(#794) all currently have an open PR from their own last run. Only `market`
and `okr` have none open, and neither has an observed trigger — no new
ruling, metric move, or pull request names either of them since this seat's
last run — so per the relay rule nothing goes in the queue for them either.
An empty queue today is the closed-gate state the charter describes, not an
absence of work.

## What actually happened in the gap (so the owner does not have to ask)

Between this seat's last pull request (#801, opened 2026-11-03T00:24:06Z)
and this run, exactly one other pull request (the pair #799/#800, HQ
re-vendoring) was opened anywhere in this repository, and nothing merged.
The board's run record (25 most recent rows, reaching back only to
2026-11-07T06:20:00Z — short of the 24-hour-or-since-last-standup floor, and
nowhere near covering the full 5.8-day gap) shows **all 25 rows** as
`exit: 1`, `turns: 1`, the identical refusal: *"You've hit your org's
monthly spend limit · ask your admin to raise it at
claude.ai/admin-settings/usage · your weekly limit resets 11pm (UTC)."*
Every seat that tried (pm, exo, engineer, writer) died at turn 1, no branch
pushed, nothing lost because ship-first had nothing to lose yet. This run's
own first attempt, at the scheduled 11:05:25Z slot, died the same way; the
re-fire after the 23:00Z reset is what let it (and exo's, engineer's, and
writer's own hook slots, all within the same ten minutes) finally take a
turn. The incident is filed in this pull request; what it cannot confirm is
whether the five days before the board's window were the same outage or
something else, and that gap is handed to the ExO's weekly audit rather than
guessed at here.

**One casualty worth naming directly.** PR #683, this seat's own missed-
Monday ceremony catch-up (opened 2026-11-02T01:00:17Z, "supersedes #531,
depth 1," carrying `sprint-2026-10-26.md`, `sprint-2026-11-02.md`, and the
`pending.md` archive-and-reset this charter's §1d has been waiting on since
2026-10-24), went stale during the outage and is now `CONFLICTING`
(`mergeStateStatus: DIRTY`), last updated 2026-11-02T01:18:01Z. It is this
seat's own PR, so this run cannot merge it, and rebasing a 15-file ceremony
diff is more than a standup should take on. Naming it is the standup's job:
**the sprint cadence has had no new sprint file land on `main` since
2026-10-12, and the fix for that is sitting unmerged and now conflicting.**
Whoever picks this up next (the next ceremony run, which per the Monday rule
is 2026-11-09) will need to rebase #683 past everything that has merged since,
or close it and redo the two missed sprints fresh; either is a real choice
and not this run's to make silently.

**This pull request's own collision.** #683 also writes
`docs/sprints/dispatch-queue.md` and `docs/sprints/pending.md`. This pass
replaces `dispatch-queue.md` fresh from current `main`, which does not
contain #683's version. If #683 is later rebased rather than closed, its
author will need to take `dispatch-queue.md`'s content from whichever pull
request is newest at that point, not reintroduce #683's stale 2026-11-02
copy.

## Run health (fleet)

Covered above: every visible run since 2026-11-07T06:20:00Z through this
one's own prior attempt was the same provider refusal, now resolved. `gh run
list --limit 30` shows the Actions side of the same gap: the newest `checks`
and `deploy-main` runs before today are both 2026-11-02 (09:04:09Z and
09:16:46Z respectively, both `success`), then nothing until this run's own
push produced a fresh green `checks` run at 2026-11-08T23:03:48Z on
`alexandria-engineer/2026-11-08-hook`. No failure class to account for beyond
the one already filed. Cap ratio: moot this window. Every one of the 25
board rows visible dates at turn 1, so no seat is within reach of its cap —
the absence of signal is the outage, not healthy low usage, and the window
needed (since this seat's last run, 2026-11-03T00:24:06Z) is far longer than
the board's 25-row reach, so this is reported as a gap rather than a clean
reading.

## Delivery health

Ran `tools/delivery_health.py` fresh (it hits the live artifacts, not the
scheduler, per the charter's own rule). **Press and site are current**: the
newest digest is `2026-W44`, by kimi-k2.6, and the site shows 4 issues
published with the same newest week — no missed-issue finding today. MCP is
up and refusing unauthenticated calls. Compute and the pipeline both read
`ok`, which is new: the Modal workspace that earlier reports named as
disabled since 2026-10-23 appears to be back, and the archive's two gaps
(2026-W41, 2026-W43) may now be a single `modal run` away rather than
blocked — not re-verified live in this pass, flagging it as newly actionable
rather than claiming it is fixed. Still **FAILING**: `checkout` (the
pricing page renders no checkout link; `POLAR_CHECKOUT_*` env vars unset,
owner-only, already asked), `deploy` (the deployed code is 6.7 to 23.3 days
behind `main` across distill/ingest/interpret/triage/weekly), and `archive`
(the two weeks named above). `payments` is still `unknown` (missing table).
None of these four are new; carried forward rather than re-argued.

## `docs/sprints/pending.md`

Not touched. §1d reserves this file's one writer to the ceremony run; this
is a standup. It is also, as read, still the pre-split 2026-10-24 narrative
snapshot (5,458 lines) rather than the dated state table §1d calls for — the
archive-and-reset that was supposed to happen at the next ceremony is the
same content sitting in #683 above, unmerged. Nothing in it to strike
against `docs/decisions.md` or `docs/allhands/`: neither has a new entry
since 2026-10-05 and 2026-09-17 respectively, so there is nothing new to
reconcile this pass.

## Proposed dispatches

None. Every dispatchable seat with a trigger already has an open PR from its
own last run (listed above), and the two without one (`market`, `okr`) have
no observed trigger. `PM_DISPATCH_ENABLED` also reads empty in this run's
environment, so nothing here would fire regardless.

## Dispatched by the PM

None this run.
