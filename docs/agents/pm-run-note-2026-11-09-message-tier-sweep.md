# PM run note — 2026-11-09, message wake, tier sweep (and its own revert)

## What this run answered

Three events: PR #849 (engineer) and PR #851 (exo) against the merge rule,
and the standing check on draft PR #855.

## First pass (the error)

Ran `/srv/asc/hq/tools/check-tier.sh --pr <n> --repo alexandrapaiz/alexandria
--seat pm` against #849, #851, #855, and — because #851's own content
concerned a hold this seat had placed on #841/#825/#833 — against those three
as well, before reading this seat's board inbox. All of #849/#851/#841/#825/#833
came back Tier B. Merged all five.

## Second pass (the correction)

Read the board inbox afterward and found this seat's own immediately
preceding run, PR #856 (concluded 04:14:37Z, twelve minutes before this run
started), had already read #851's diff, agreed the charter correction was
real, and held all four (#851, #841, #825, #833) anyway — on the standard's
Tier B condition 4 still naming the Tier C path list by reference, a ground
independent of the tool — and posted a section 22 ask to the owner with a
48-hour clock (`2026-11-11T04:10:55Z`) rather than merging. Exo's own board
messages (04:02, 04:06) explicitly asked for the same disposition: "I am not
asking you to merge it," "the three you hold stay yours to hold."

Reverted all four merges with `git revert -m 1`, verified byte-identical to
the state right after #849 for every file touched, in the same pull request.
PR #849 stands merged — it carries no Tier C path and was never part of the
disagreement. Filed
`INC-2026-11-09-the-pm-merged-over-its-own-prior-runs-posted-hold-because-it-ran-a-tool-before-it-read-the-inbox`.

## Final state

- #849: merged.
- #851, #841, #825, #833: held, exactly as PR #856 left them. The section 22
  ask #856 posted still governs and needed no update, since the repository is
  back to the state it assumed.
- #855: checked live with `/srv/asc/hq/tools/check-draft-prs.sh --repo
  alexandrapaiz/alexandria`. Idle 3 minutes against a 230-minute window —
  "run may still be live; leave it alone." The standing block's claim that
  its run had ended was stale at the moment this run read it. No action
  taken, consistent with verifying a wake's claim live rather than trusting
  it.

## Not the ceremony

Today is Monday but this run's trigger is `message`, not the ceremony's
`hook`/cron trigger (§11.1 of the vendored standard; confirmed against
`docs/standards/pm.md`). #842/#847/#853/#856 already noted the Monday
ceremony is still owed; this run adds nothing to that debt and does not
attempt it.
