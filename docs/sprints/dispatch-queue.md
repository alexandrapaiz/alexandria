# Dispatch queue — 2026-10-26, ~00:50 UTC (message, Monday ceremony)

`PM_DISPATCH_ENABLED` is empty in this run's environment, so section 5 of
`prompts/pm-agent.md` stays dormant regardless of what follows: nothing
below is fired, only proposed.

## The queue gauge

1. **`main`'s age and check state.** Last merge to `main`: this pass's own
   merge of #529, 2026-10-26T00:32:44Z (minutes old at this writing). The
   newest *relevant* `checks` run on `main` is still success at
   2026-10-25T23:58:15Z (PR #516's merge); #529 touched only
   `docs/agents/` and `prompts/exo-agent.md`, none of which are in
   `checks.yml`'s path filter, so it correctly did not re-trigger. Green,
   on the evidence that exists.
2. **Open pull requests.** 29 total, 3 opened since the last merge before
   this pass's own (#530, #531, and one more in that window).
3. **Conversion.** 53 merged in the last 7 days over 136 opened in the
   last 7 days: 53/136.
4. **Deepest open chain.** #483 (PM's own), supersedes #480, **depth 13**
   — the deepest this register has recorded; the prior high was depth 5
   (2026-09-30). **This seat is blocked on merges at this depth.** #483 is
   mine, so I cannot merge it myself (Tier B condition 1); it is one of
   the 22 PM pull requests named below and in `docs/sprints/pending.md`.

Queue is not deadlocked: `main` moved under an hour ago and conversion is
0.39, not the 48-hour-no-merge state that would make the queue gauge the
headline. It is reported first anyway because of finding 4.

## Cap ratio (24h window)

`writer` ran at 145 turns against its live manifest cap of 150 (**96.7%**)
on its 23:02 hook wake (PR #517). Third-plus consecutive over-70% reading
for this seat (`docs/agents/turn-caps.md`'s 2026-10-25 sweep already had
it at 99.3%); an ask to raise the cap to 225 is already with HQ via the
relay and unresolved. `exo` (101/200, 50.5%) and `engineer` (129/200,
64.5%) are both under the 70% line. Not re-escalating past what the relay
already carries; naming it again so it is not re-discovered from scratch.

## Run health

Board run records, last six hours (2026-10-25T18:33Z to now): one
non-zero exit, `pm` at 18:20:00, **refused** ("You've hit your weekly
limit"), not a run that executed and failed — already a known, registered
pattern this week (`docs/agents/incidents.md`, the weekly-budget-window
incidents of 2026-10-25). Zero runs in this window ran to completion and
failed. `gh run list --limit 30` for `checks`/`deploy-main`: all green,
oldest in the visible window 2026-10-24T21:29:52Z.

**Delivery health, the half fleet-green cannot see.** The press has not
sent a new issue since `2026-W42` (2026-10-19, 7 days ago); `2026-W43` is
due today at 09:00 UTC, into a Modal workspace that has been disabled
since 2026-10-23 and is confirmed still off as of the last two engineer
runs (2026-10-25). The same outage takes the MCP server down with it
(distribution's handoff this pass; an ask is now with the owner). The site
deploy and the till/checkout watcher were not independently re-checked
this pass beyond what the above already covers; not claiming green on
either without fresher evidence than a day old.

## Merge-queue triage this pass (Tier B)

- **Merged**, #529 (exo): `tools/check_authority.py` returned `clear`.
- **Held**, #473 (distribution's HQ re-vendor of `docs/standards/pm.md`):
  `check_authority.py` returns `reserved` — one hunk sits inside §21
  itself. Asked of the owner on the board this pass, with a recommendation
  to merge.
- **Handed to the owning seat to rebase** (Tier B condition 5, conflict):
  #517 (writer), #466 (skill), #435 (frontend, also still draft at 42+
  hours). All three have since pushed new commits post-handoff; writer and
  skill within the hour.
- **22 of the PM's own pull requests** sit open and unmergeable by the PM
  itself (Tier B condition 1). Filed this pass as
  `INC-2026-10-26-pm-own-tier-b-prs-piled-up-to-twenty-two-and-one-chain-reached-depth-thirteen`,
  the second occurrence of this class. No fix is this seat's to ship;
  named in `docs/sprints/pending.md` as waiting on the owner or a chair.

## Proposed dispatches

None. Every seat with a live blocker (writer, skill, frontend) was already
reached directly on the board this pass and has started moving on its own
without needing a workflow dispatch; firing one on top of a seat already
acting would race it. Nothing else cleared the bar for a dispatch entry:
an observed trigger, evidence in one line, and a diff the owner has
already ruled on.

## Dispatched by the PM

None this pass.
