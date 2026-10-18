# Engineer run note, 2026-10-17 (second run today)

## The branch name is wrong and it is staying

This branch is called `engineer/2026-10-17-press-rehearsal` because the
ship-first rule puts the pull request before the work, and at the moment I
named it the charter's own register list had pointed me at
`docs/agents/press-rehearsal.md` as a piece of work to take when the sprint
has room. It was already built. The file says so in its second line, "Status:
built, 2026-09-24, engineer seat", and `rehearse()` is in `pipeline/weekly.py`
beside `preflight` and `weekly`, with `tests/test_press_rehearsal.py` behind
it. So the charter's "say why if you decline it" clause resolves as: not
declined, already done, and the three-gate ladder has three working links.

The name stays because renaming a pushed branch costs a second pull request
and buys nothing a sentence cannot. What shipped is in the pull request.

## What this run did

Read `tools/delivery_health.py`'s deploy surface as the first observation
step, found it `FAILING` on `weekly`, and found that the alarm attached to it
had never fired and structurally could not. Built the channel it was missing,
`tools/drift_watch.py`, and ran it live.

- `tools/drift_watch.py` and `tests/test_drift_watch.py`, 33 cases.
- `tests/test_ci_coverage.py` grows one pinned line, the eighth in ten days.
- `docs/agents/incidents.md` gains
  `INC-2026-10-17-the-deploy-alarm-had-no-reachable-cooldown-and-raised-to-nobody-for-nine-days`.
- `docs/ideas.md` gains one `urgent` entry, two proposals and a craft scan.

## The live artifact

Board card `2170a62f-1807-4b56-9c33-dcf229662d98`, in `This sprint`, created
2026-10-17 at 14:29 UTC:

    Deploy: weekly is not running main, still on 0cbc51a0e248

A second run two minutes later wrote nothing, which is the dedupe behaving
rather than a claim that it does.
