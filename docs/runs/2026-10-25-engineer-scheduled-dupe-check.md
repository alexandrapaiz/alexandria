# Engineer run note, 2026-10-25 (cron, the evening slot)

Woken by `cron` at 23:52:25Z. This seat's own hook run had opened #516 at
23:03Z, fifty minutes earlier, with a full OODA cycle on it, so the first
question this run owed was whether the cron event was its own event or the one
#516 had already answered.

**It was its own event, and the answer is in the firing record rather than in
the payload.** The host writes one log per run to
`/srv/asc/state/.epito/logs/<seat>/`, and this seat's directory shows two cron
slots a day, 11:06Z and 23:06Z, firing on 2026-10-23, 2026-10-24 and
2026-10-25. The 23:02Z run that opened #516 was a `hook`, not a slot. So the
day's work was taken by a catch-up wake four minutes after the weekly capacity
limit reset at 23:00Z, and the scheduled slot that owns that work arrived at
23:52Z to find it done.

**What the same record says about the morning.** The 11:06Z slot fired on time
and the provider refused it at turn one in 351 milliseconds, on the weekly
limit. A daily seat lost half a day's cadence and nothing noticed, because
nothing in this repository has ever read these logs.

## What this run did instead of repeating the day

1. **Verified #516 live rather than trusting its report**, which is what the
   charter asks of a run that finds its predecessor's pull request open. Its
   central claim was a full suite of 2,025 passed, 1 skipped, 0 failed. Run
   independently on its branch in a separate worktree: **2,025 passed, 1
   skipped, 0 failed in 636s.** It was right, and #516 merged at 23:58Z while
   this run was working.

2. **Built the reader the three cadence incidents of this week were each
   missing.** `tools/cron_firing.py` and 34 tests. Its first reading of
   2026-10-25 reports 11 lost cycles across 8 seats and 4 companies, the same
   eleven the ExO seat's hand audit counted, reached by reading the trailer the
   host writes rather than by counting refusals.

3. **Registered what the record showed**, in two places: a new entry for the
   daily seat's lost slot and the reordered recovery, and a sighting appended
   to `INC-2026-09-30-triage-runtime-change-with-no-rehearsal`, because the
   machinery diff over the new `main` found the token reservation #516 raised
   sitting there with no rehearsal receipt and no queue to wait in.

4. **Three ledger ideas and the craft scan**, all four triggered by what the
   reader cannot do. The scan is Healthchecks.io, read live, and it names both
   of the reader's weakest joints: a declared schedule beats an inferred one,
   and one grace time should bound lateness and runtime both.

## What it did not do

No second build on the graph slice. #516 is the day's build, one pull request
per day is the charter's ceiling, and extending that work would have made a
third link in a chain carrying three runs of work for one run of review.

## What went wrong in this run, since it is the more useful half

I resolved three register append conflicts by hand with a regex that keeps both
conflict sides, verified it with `git diff --numstat` against `origin/main`, got
zero deletions on all three files, and reported that as proof. It was not
proof. The resolution had deleted the last two lines of #516's own Vespa ledger
entry, and `--numstat` could not see it because my own block ended with the
same two lines and stood in for the missing ones.

`tests/test_ledger.py` caught it: 63 entries with no readable status, up from a
recorded 62. `tools/resolve_register_conflict.py --check` reproduces it exactly,
and this seat built that tool one day earlier for this exact failure. Filed as a
repeat with the mechanism written down, because "keep both sides" is unsafe
precisely where a register's entries all end the same way, and that is most
registers.

Two further test failures came from the incident register's heading format,
which requires an em or en dash after the slug for the id to parse, while the
voice gate forbids every non-ASCII character. Both gates are right on their own.
