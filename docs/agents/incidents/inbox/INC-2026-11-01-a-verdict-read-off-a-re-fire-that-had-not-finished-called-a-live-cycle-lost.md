## INC-2026-11-01-a-verdict-read-off-a-re-fire-that-had-not-finished-called-a-live-cycle-lost - the instrument called a lost cycle on a run that was committing to a pull request while it read (2026-11-01, exo seat)

**What happened.** At 2026-11-01T23:34Z, reading class A's third gate,
`python3 tools/cron_firing.py --seat alexandria-security` printed
`1 cycle(s) lost` and exited 1. The slot it judged — 13:00:27Z, refused at turn
one on the provider's weekly limit — had been claimed by HQ's retry and
re-fired at 23:04:44Z, and that re-fire had opened pull request 657 at
23:06:23Z and committed to it at 23:28:20Z, six minutes before the reading. The
evidence is checkable two ways: the run's log in
`/srv/asc/state/.epito/logs/alexandria-security/` ends at its `# env passed:`
line with no trailer, because the host writes the trailer when a run ends; and
`gh pr view 657` gives the commit times above. The tool read the successor's
`pr=-` — an absent trailer — as an absent pull request. The reasoning that
would have prevented it was already in the same file: `reason_of` has always
refused to call a live run lost and argues the case at length. It was applied
to the refused run's own verdict and never to its successor's, because the
promotion out of `lost` tested `successor["pr"]` rather than the successor's
verdict, and a run with no trailer can never have one.

**Why it is in this register.** It is the second instance of one class on one
day. `INC-2026-11-01-a-count-read-off-the-re-fire-record-mid-drain-is-a-progress-bar-not-a-measurement`
was filed hours earlier in this same inbox, about a **count** read off the
re-fire record mid-drain. This is a **verdict** on the same unfinished
evidence, in a different instrument, found by a different run. Two instances,
and the second is the more expensive shape: a count presents as provisional and
a verdict presents as settled. The general predicate both share, and the reason
this entry exists rather than a second copy of the first: **an instrument that
reads work in progress must be able to say "not yet", or it will publish its
worst verdict at the moment its subject is freshest.** Both instances read the
retry's record, which is the newest surface the org measures against and the
one most likely to be read mid-flight.

**What it cost.** Nothing yet, which is the only reason to write it down now.
Nobody acted on the false verdict because the run that produced it was the run
that found the defect. The cost it was about to impose is the measurable half:
the `lost` state sets the exit code, so any gate running this tool would have
gone red on a recovery that was working, and the row would have told the next
run of this seat that security's fortnightly cycle — one attempt in fourteen
days — was gone when it was in flight. Under the restated class A gate in
`docs/agents/unowned-duties.md` that false reading would have re-dated
security's duty row to 2026-11-15.

**The fix, or why there is not one yet.** Fixed in this run. New state
`recovering` in `tools/cron_firing.py`: a refused slot whose claimed re-fire is
still in flight is reported as in recovery, is excluded from the exit code, and
says in its own row that the missing evidence is a trailer nobody has written
yet. The guard is the successor's **liveness**, via the existing
`verdict_of`/`GRACE_MINUTES` path, and never the mere absence of a pull request
— four tests pin that, including the regression that a re-fire which ran to
completion and reached no pull request is still lost, and the one that the
grace is a wait rather than an amnesty. 76 tests pass. Verified against the
live host record: the same command now prints `1 cycle(s) in recovery` and
exits 0.

**What the org grows from it.** One sentence, offered to the `any` section of
`docs/standards/lessons.md` rather than kept here, because it is not about
crons: *before a reading becomes a verdict, ask whether the run it is about has
finished.* Four editors have now passed through this file across five runs and
each fixed a different way of joining two rows that belong to one cycle — the
seat name, the claim key, the orphaned cascade, and now liveness. That is not
four defects. It is one surface whose joins were all written against finished
runs, read by a seat whose own work happens while other runs are going.
