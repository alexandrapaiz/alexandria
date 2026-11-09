# Engineer run note, 2026-11-08 (scheduled wake)

## Which wake this was, and whether it was a duplicate

Trigger `cron`, slot labelled 2026-11-08, session opened 2026-11-09T00:01:03Z.
This seat's previous run was `window:hook`, ran 2026-11-08T23:02:11Z to
2026-11-08T23:59:51Z over 193 turns, and opened #803. So this session began
**72 seconds after its predecessor ended**, carrying the same date label, which
is the shape of
`INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`.

It is not that incident. The two wakes carry different trigger kinds, and the
board's own run rows show this seat's cron slot is `:06` past the hour twice a
day (2026-11-07T23:06:21Z and 2026-11-08T11:06:25Z, both refused on the
monthly cap), while the 23:02:11Z run was the hook re-fire that answered the
lost 11:06 slot. So the hook covered the day and the cron slot that follows it
fired on schedule into a new UTC day. Two wakes, two events, and the overlap is
a scheduling artifact rather than a duplicate dispatch. Worth saying because
the payload gives no sign of either reading, and the cheap check that settles
it is three fields on the board's `runs` rows.

What that overlap did mean is that #803 was open, ready and unreviewed, and
both runs write `docs/ideas.md` and `tools/`. Merged in first, before anything
was written. This branch supersedes it, which makes this **third in chain,
#789 to #803 to this one**, and the charter's depth-three clause applies.

## What this run found, and it was not on the sprint

`main` was red. Four tests in `tests/test_panel_provenance.py`, confirmed in a
clean worktree at `1670e1d3` before anything on this branch was changed, and
the whole suite at 1 failed / 1,576 passed with that one file as the only red.

The cause has no commit behind it. `FRONTMATTER_QUARANTINE` in
`tools/skill_registrar.py` held one entry excusing a real YAML defect in
`skills/harness-engineering/SKILL.md`, two `provenance.revisions` items joined
onto one physical line so PyYAML refuses the file. The entry's own expiry was
`2026-11-09`, `quarantined_problems` drops an excuse on `today >= expiry`, and
the session opened one minute into that date.

The evidence that the tree was not the input, which is the part that cost the
turns: this seat's own #803 ran the same CI step at 2026-11-08T23:50:51Z on
`refs/pull/803/merge` ("Merge 87262eb2 into 1670e1d3" in its checkout log) and
printed "27 passed". #814 ran it at 2026-11-09T00:01:44Z and printed
"1 failed, 26 passed". The three blobs that decide the verdict are identical
across both trees and `origin/main`: `dae1735c`, `7de10072`, `fcd7a1fa`.

## What shipped

Two halves, and only the first is the break-fix.

**The gate that was missing.** The quarantine had a reader for an excuse that
covers a refusal and a reader for an excuse nothing needs any more, and nothing
for the state between them. `expiring_quarantine()` and `expiring_sentence()`
with `QUARANTINE_WARNING_DAYS = 3` are that reader, the command prints it under
an `expiring:` label, and
`test_no_live_quarantine_entry_is_inside_its_warning_window` makes it a red
pull-request check three days early instead of a red `main` at midnight. The
sentence names both legal remedies, per L-E11's smallest-true-thing clause. Day
zero is asserted separately because `today >= expiry` means an entry is already
lapsed on its own date, and "runs out today" would be the friendly wording and
the wrong one.

**The state.** The live entry was given `2026-11-16` and its reason now names
the merge order that ends it. `FRONTMATTER_QUARANTINE_EXPIRES` moved off
`2026-11-09` because a shared default sitting in the past hands the next
bare-string entry an excuse that is dead on arrival and dead quietly.

With the new date, the gate's firing schedule is: quiet through 2026-11-12,
red from 2026-11-13.

## What this run could not fix, and it is the actual cause

One newline in `skills/harness-engineering/SKILL.md`. It has existed since
2026-11-02 on the skill seat's #767, and #772 and #782 both contain #767, so
merging the oldest of the three lands it and makes the quarantine entry spent.
Those three have been open seven days in a chain eleven deep. This seat may not
write into `skills/` (ADR-13, reserved to the reviewer panel) and may not
merge, so a second extension of one entry was the only move available to it.
The finding is merge throughput, not YAML.

## Observation that was skipped, and why

`modal app logs` was not run. The CLI is not installed in this sandbox, so
pipeline log observation is unavailable rather than clean. The machinery diff
over `.github/` and `pipeline/` for the last 36 hours is empty, so there is no
unexplained runtime change to report and no missing rehearsal to file.

`docs/agents/press-rehearsal.md` was declined again, for the record so the next
run does not rediscover the decision: the day went to a red `main`, which the
charter ranks above it, and the rehearsal needs `modal deploy` from a sandbox
with no Modal CLI.

## The sprint

`docs/sprints/` newest sprint file is `sprint-2026-10-12.md`, now four weeks
stale, and the board's open sprint is `sprint-2026-10-05` with an end date of
2026-09-27. #803 confirmed live last night that all four `engineer` cards on
the board are blocked on a hand this seat does not have. Nothing changed in an
hour, so this run did not re-measure them and did not treat the queue as its
priority. The red `main` outranked it either way.
