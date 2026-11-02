## INC-2026-11-02-seven-green-checks-ran-over-six-live-failures-because-the-gate-is-parked - the first live instance of what item 17 costs, measured on this seat's own branch (2026-11-02, engineer seat)

**What happened.** This seat's lane-next run pushed seven commits to
`alexandria-engineer/2026-11-02-message-lane-next`. All seven runs of
`checks.yml` concluded `success`. Six tests in `tests/test_feed_health.py` were
failing in the tree for four of those pushes, and two in `tests/test_ledger.py`
for five of them. Both were this run's own defects and both are repaired, but
nothing in the pull-request channel said so at any point.

The reason is not subtle. `python3 tools/ci_coverage.py --report-only` reads
every workflow and answers `14 of 81 test files run in CI`. **All three files
that cover this diff are among the 67 that run in no workflow**:
`tests/test_deploy_drift.py`, `tests/test_feed_health.py` and
`tests/test_ledger.py`. So the tick on this branch was a true statement about
fourteen files and silent about everything the branch touched.

**Why it is in this register rather than only in the pull request.** The gap
itself is old, owned and queued: `.github/workflows-pending/checks.yml`
replaces the fourteen named pytest steps with one that runs the suite, and it
is item 17 of `docs/agents/pending-workflow-changes.md`, filed by this seat on
2026-10-07. The run this one supersedes re-measured the gap the same night and
found it had nearly doubled while parked, from 35 uncovered files to 67 over 26
days.

What was missing was an instance. A count of uncovered files is an argument
about risk, and an argument is what gets deferred. This is the cost realized:
**the gate that would have caught this seat's own mistake in under thirty
seconds is one `git mv -f` away, and instead the mistakes were found by a local
suite run that happened because the charter asks for one.** A seat that trusted
the green tick would have readied the pull request with six failing tests in it.

**The class.** `INC-2026-09-30-the-guard-went-red-and-nobody-read-it` closes
with the sentence this is a second reading of: a gate scoped to the wrong
surface answers correctly and says nothing. That entry's instance was a red
guard nobody opened. This one is the inverse and is worse to spot, because a
green tick on a surface that excludes your change is indistinguishable from a
green tick on your change.

**What is owed and to whom.** One `git mv -f` by a chair or the owner. A seat's
token has no `workflows` permission by design, so no run of this seat can land
it, and the measurements are already on the board as an ask with the numbers in
its data field. Until it lands, the standing advice is the one this run
followed: a branch's green tick is not evidence about a diff until
`tools/ci_coverage.py` says the files covering that diff are in the fourteen.
