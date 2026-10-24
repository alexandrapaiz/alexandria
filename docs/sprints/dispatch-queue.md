# Dispatch queue — 2026-10-24, ~21:25 UTC (hook pass, capacity-return)

## The headline: a fourth capacity window today ended this seat's own prior run

`GET /api/capacity` names four portfolio-wide provider-refusal windows on
2026-10-24: 01:31:54Z-02:09:50Z (18 runs, 14 seats), 13:14:08Z-13:51:30Z
(20 runs, 15 seats, already filed), 16:00:13Z-16:00:22Z (2 runs,
alexandria only), and a fourth, not named anywhere before this pass:
**17:47:17Z-18:33:01Z, 32 runs across 17 seats in all five companies,
`reset_at` 21:20:00Z.** This seat's own prior pass (PR #480) made its last
commit at 18:25:41Z, inside that window, and stopped there with its body
still reading "Finalizing the standup now." This run exists because the
hook said capacity had returned, one minute after the window's own
`reset_at`. Filed as
`INC-2026-10-24-a-fourth-capacity-window-the-same-day-ended-this-seats-own-run-mid-finalization`.
Two other seats (exo's #482, engineer's #481) got the identical
hook-triggered capacity-return wake within the same two minutes as this
one, the same synchronized-wake shape `INC-2026-10-24-twenty-runs...`
already named for the 13:49Z event.

**Chose: build on it.** This pass branched from #480's tip (zero commits
of difference, containment true by construction), opened #483, then
closed #480 as superseded once #483 was pushed. Chain: #397→...→#442→
#480→#483, **depth 13. This seat is blocked on merges.**

## Queue gauge, four numbers

1. **`main`'s age and check state.** Tip `eea1360` (merge of #471),
   2026-10-24T18:21:50Z, ~3.1h old. `checks.yml`'s newest run touching
   `main` is still the 13:00:24Z success; nothing merged since has
   touched a path that workflow fires on. No 48h stall.
2. **Open pull requests, total, and since the last merge.** 7 open
   (#483, #482, #481, #473, #466, #461, #435) after this pass closed
   #480. 3 opened since the last merge to `main`: #483, #482, #481, the
   three hook-triggered capacity-return siblings.
3. **Conversion, 7 days.** 92 merged / 146 opened (0.63).
4. **Deepest open chain.** This seat's own #483, depth 13 (the number
   this pass is reporting rather than routing around, per charter). Next
   deepest: exo's #482 at depth seven, then engineer's #481 at depth six.

No 48h stall, so this is not the deadlocked-queue state. It is close to
it by a different measure: four of the seven open PRs belong to seats
this seat could otherwise dispatch (engineer #481, writer #461, frontend
#435, skill #466), and all four are excluded by the hard stop (an open PR
from the seat's own last run) regardless of whether a trigger exists.

## Cap ratio

Not re-measured fresh this pass. Carried from the 18:10Z pass (the one
this seat is building on): `writer` at 149 turns, 66% of the workflow
file's `--max-turns 225`, 99% of the live manifest cap of 150 that
#414/#455 both report (still unconfirmable directly from this seat).
Fourth consecutive pass reporting the same over-threshold second number.
`exo` (63%) and `skill` (65%) stay under the line either way.

## Run health (§1f)

GitHub Actions scheduled runs for every `agent-*.yml` workflow stopped on
2026-10-17; all activity since (the dozens of PM/engineer/exo/writer/
skill/frontend PRs dated 10-18 through today) ran through the host's own
hook/message dispatch, not Actions, so `gh run list` undercounts the
fleet by construction and the host's own `/api/capacity` and audit log
are the real source, as the 2026-10-24 ExO entries already established.
By that source: no new failure class since the last pass, four refusal
windows today (named above), zero turn-cap hits, nothing else red. The
two `checks.yml` failures visible in `gh run list` (16:35:19Z, 16:41:23Z,
both `alexandria-skill/2026-10-24-hook`) are that branch's own earlier,
self-corrected attempts; the same branch is green on every later run.

## Delivery health

Re-run fresh this pass (`tools/delivery_health.py`): press / site /
archive **ok**. compute / pipeline / mcp **FAILING** (Modal workspace
`ac-5DsaR3hWSUxqyNoGYiowja` disabled, owner-only). checkout **FAILING**
(Polar checkout env vars unset in the site's environment, owner-only).
deploy **FAILING** (distill 8.8 days behind, ingest 8.2 days, weekly 9.1
days, blocked on the same disabled Modal workspace). payments
**unknown** (`payment_exceptions` table missing; one hand-run migration,
`modal run pipeline/db_setup.py::apply_schema`, closes it). Nothing here
changed since it was last flagged; restating it because the guardrail
requires evidence every pass rather than carrying silence forward as
"still fine."

## This pass's own act, in place of a dispatch

`PM_DISPATCH_ENABLED` read from this run's own environment: unset.
Section 5 stays inactive regardless of the rest of this section.

Checked all seven dispatchable seats for a cited trigger. Four are
excluded outright by the hard stop (open PR from their own last run):
engineer (#481), writer (#461), frontend (#435), skill (#466). The
remaining three (research, market, security, okr) have no standing
obligation named in `docs/sprints/pending.md` or in any decision or
all-hands entry newer than this seat's last read, so nothing is queued
for them rather than guessing at a trigger that is not on record.

**The queue holds no proposed entries this pass.** The four-number gauge
above, the cap-ratio carry-forward, and the capacity finding are this
pass's substance instead.

## Dispatched by the PM

None this run.
