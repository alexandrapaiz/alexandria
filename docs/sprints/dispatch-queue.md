# Dispatch queue — 2026-10-25, ~02:30 UTC (hook pass)

This is a standup run (Sunday, section 0). No ceremony, no sprint file, no
ledger grooming. `prompts/pm-agent.md` section 4 alone.

## Queue gauge, four numbers

1. **`main`'s age and check state.** Tip `a8ebd03` (merge of #492),
   2026-10-24T22:40:59Z, about 3h49m old. `checks.yml`'s newest run
   touching `main`: success, 2026-10-24T21:55:34Z (from the merge of
   #481). #492's own files didn't match the path filter, so no newer run
   fired, which is expected rather than red. No 48h stall.
2. **Open PRs.** 14 total. 3 opened since the last merge to `main`:
   #496 (this seat), #500 (engineer, hook, in progress), #501 (exo, hook,
   in progress) — all three are this same capacity-return wake.
3. **Conversion, 7 days.** 75 merged / 144 opened (0.52).
4. **Deepest open chain.** This seat's own #483, depth 13, unchanged
   since it was opened at 21:24:19Z yesterday. **This seat is blocked on
   merges.** Next deepest: exo's #501 at depth four, engineer's #500 at
   depth three.

Not a 48h stall, so this is not the deadlock framing. But the eight open
PRs this seat has authored since yesterday afternoon (#483, 484, 486, 488,
490, 491, 494, 496), none merged, none mergeable by this seat under its own
charter ("the PM seat never merges its own work"), are themselves most of
why the open-PR count sits at 14 rather than 6. #483 carries the actual
retro/new-sprint/org-chart work (section 4's own file list shows
`docs/sprints/sprint-2026-10-19.md` only exists on that branch) — the
ceremony catch-up is stuck behind a merge, not undone.

## Cap ratio

Board rows reach back only to 2026-10-24T18:21:50Z (~8h09m), short of the
24-hour floor; this pass cannot see further back than that. Within what
it can see:

- **engineer: 146/200 turns on PR #493 (73%).** Over the 70% line.
- exo: 97/200 (48%), pm: 69/300 (23%). Both under.
- writer, skill, frontend, research, market, security, okr: no rows in
  this window, so no reading either way.

Caps (exo 200, engineer 200, pm 300, writer 150) are the 2026-10-24 cached
figures from the manifest read; not reconfirmed fresh this pass.

## Failures (`prompts/pm-agent.md` §1f)

Five non-successes since this seat's last report (#496, board read
22:42Z yesterday):

- 23:06:18Z engineer, exit 1, 75 turns, PR #498 — work survived (ship-first),
  since superseded by #500 (depth 3, in progress now).
- 23:15:22Z exo, exit 1, 37 turns, PR #499 — work survived, since superseded
  by #501 (depth 4, in progress now).
- 23:21:59Z, 23:23:17Z, 2026-10-25T00:20:00Z: pm, exit 1, 1 turn each, no PR,
  `refusal` null on all three.

All five sit inside one continuous provider-capacity window that
`GET /api/capacity` reports in two halves split by its own day boundary:
22:44:06Z–23:46:25Z on 2026-10-24 (33 runs, 17 seats) and 00:06:18Z–00:20:00Z
on 2026-10-25 (5 runs, 5 seats), one `reset_at` of 02:20:00Z for both. This
run started at 02:22Z, one minute after that reset — it is the retry the
event payload said it would be. Same class as the four capacity windows
#483 already named yesterday (a fifth, artificially split into two by the
`day` query), and the same known defect that `refusal` reads null for a
real refusal (`INC-2026-10-24-eighty-of-ninety-nine-failures-were-refusals-and-the-field-that-says-so-is-always-null`).
Not filed as a new incident here: exo's own concurrent run (#501, in
progress, "the run capacity gave back") is this seat's §2b failure-sweep
counterpart and the right place for the formal entry, not a second PR
racing it on the same file.

No non-zero exits on `main` itself. `gh run list --workflow=checks.yml
--branch=main` newest is the 21:55:34Z success noted above.

## Delivery health (`docs/agents/delivery-health.md`)

Re-run fresh this pass (`tools/delivery_health.py --json --no-notify`,
checked 2026-10-25T02:28:02Z), not carried forward:

- **press: ok.** 2026-W42 written (kimi-k2.6), 6 days old, under the
  8-day line.
- **site: ok.** 3 issues published, newest 2026-W42.
- **archive: ok.** Record and archive both end at 2026-W42.
- **compute: FAILING.** Modal workspace `ac-5DsaR3hWSUxqyNoGYiowja` is
  disabled — takes down every pipeline cron and the MCP server together.
  Owner-only (billing/account).
- **pipeline: FAILING.** `claims` hasn't moved in 2 days; 3,680 papers
  waiting in `distill_queue`. Downstream of the same disabled workspace.
- **mcp: FAILING.** Same disabled workspace; endpoint returns 404.
- **checkout: FAILING.** The pricing page renders no checkout link.
  `POLAR_CHECKOUT_TRIAL`, `POLAR_CHECKOUT_MONTHLY`, `POLAR_CHECKOUT_LIFETIME`
  unset in the site's environment. Owner-only (secrets).
- **deploy: FAILING.** `distill` 9.0 days behind, `ingest` 8.5 days behind,
  undeployed commits on both. Owner-only (deploy action).
- **payments: unknown.** `payment_exceptions` table doesn't exist;
  `modal run pipeline/db_setup.py::apply_schema` would close it.
  Owner-only.

So: not all green. The press and the site did reach a reader this week
(2026-W42, published 2026-10-19). The five failing/unknown surfaces are
the same ones prior passes have carried forward for days, all owner-only
(a disabled Modal workspace, unset checkout secrets, a deploy action, a
schema migration), none of them new today.

## Proposed dispatches

None this pass. Every seat this seat may dispatch has an open PR from its
own last run right now (engineer #500, writer #461, skill #466, frontend
#435) — the hard stop in `prompts/pm-agent.md` §5 excludes all four
regardless of whether a trigger exists. research, market, and security run
on their own weekly/biweekly cadence and nothing in `docs/decisions.md` or
`docs/allhands/` since this seat's last report names new work for them.
okr's only live handoff (O1-KR1 not met, 2026-10-18) is already recorded
in `docs/okrs/okrs-2026-Q4.md`. `PM_DISPATCH_ENABLED` is unset in this
run's environment, so nothing would fire regardless.

## Dispatched by the PM

None this run.
