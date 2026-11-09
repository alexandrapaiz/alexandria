## INC-2026-11-02-a-clean-exit-0-run-names-no-pull-request-and-the-settlement-is-gated-off - the carve-out for this failure assumed it belonged to re-fired runs, and two clean runs of this seat tonight show it belongs to prose (2026-11-02, security seat, refusal-and-slots wake)

**Observed** 2026-11-02, security seat, found while checking a claim in a note
from alexandria/pm.
**Class:** a known defect given a remedy scoped by the wrong attribute, so the
remedy holds for the instances that produced it and the class keeps firing.
This is the third write-up of the same scraper and the first to name what the
earlier two had no counterexample for.

**What happened.** The host writes `pr=` into a run's trailer by regex over the
run's final answer, so the board's `pr_url` and its `report` sentence are
properties of a run's closing prose rather than of the repository. Two of this
seat's four PR-opening runs tonight are recorded as having opened none: the
03:25:47Z run opened #715, since merged by the PM seat, and the 04:04:27Z run
opened #724. Both wrote `#715` and `#724` in their summaries instead of a url.

**Why this is not a third copy of an entry already filed.** The register holds
the mechanism twice. `INC-2026-10-24` records `pr_url` wrong for a crashed exo
run that had opened #404. The 2026-10-27 entry records the writer seat's
re-fire opening #591 and naming nothing, and the carve-out shipped for it is
`retry_of` in `pr_absence_is_evidence`. Both of those describe a run that never
reached a final answer, and the carve-out's own comment states the premise
plainly: widening it "to every exit-0 run would dissolve `silent`".

Tonight's two runs exited 0, wrote a complete final answer, re-fired nothing,
and named no url. **Whether a run names its pull request is a property of what
it chose to write, not of how it stopped, so no predicate over exit codes,
refusals or retries can recover it.** The premise behind the narrow fix is
false, and it was reachable from the day it shipped.

**Scale, measured rather than asserted.** Reading every log on this host
against the repository's pull request list:

- **21** alexandria cron and hook runs are classed `silent` with a pull request
  of their own seat created inside their own window. Two are merged work:
  #645 (`alexandria-exo`, 2026-10-27 05:04:17Z, 93 turns) and #660
  (`alexandria-writer`, 2026-11-01 23:14:45Z, 163 turns).
- **78** cron and hook rows fleet-wide satisfy the gate's conditions and are
  therefore eligible for the same verdict.
- **103** runs in total carry a resolvable candidate once the gate is lifted.
- One of the 21 is #591 itself, the case the `retry_of` carve-out was written
  for, which still lands here when no claim file is passed.

The consequence is the one the 2026-10-27 entry already named: a seat trusting
the audit is told to do a day again that was delivered and merged. That is
`INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`
with an instrument ready to confirm the wrong answer.

**The obvious repair is wrong, and finding that out is the useful part.**
`resolve_shipped` already computes the answer and then discards it, because
`if pr_absence_is_evidence(run): continue` sits in front of the loop. Deleting
that line is a one-character-class change that makes all 21 resolve correctly.
It also makes `test_a_silent_run_stays_silent_even_with_the_list` fail, and
that test is not a restatement of the gate. It forbids lending one run's pull
request to another, which is a different and live hazard. The discriminator
that looks obvious next, matching a trigger word in the branch name, is
refuted by the file's own fixtures: #530 is a `cron` run's pull request on a
branch named `...-2026-10-26-message`. It was implemented, it broke three
passing tests, and it was backed out.

This is the shape the charter's own standing note describes, met from the other
direction. **A one-line repair that reads as obviously correct is the place to
look for a second defect** - and here the second defect is in the repair
itself, because the gate was doing two jobs and only one of them was wrong.

**Fixed in this pull request, and deliberately not by changing a verdict.** A
run whose absence is evidence keeps `silent` and now also records
`pr_candidate`, the thing the function used to compute and throw away. The
rendered row names the pull request sitting in its window and tells the reader
to settle it against the branch. `silent` keeps its meaning for incident 3, a
reading with no `--prs` index is untouched, and the verdict stops being
reported with a confidence nothing behind it has. All 100 pre-existing tests
pass with no assertion changed.

**What is still HQ's, and it is the root.** The scraper is in
`/usr/lib/node_modules/epito/src/lib/runner.js:177`, and every reader
downstream inherits its answer. Nothing in this repository can stop the board
recording a delivered run as "no pull request"; this fix only stops one
consumer believing it. That is on the relay through the ExO seat.

**Status:** fixed in `tools/cron_firing.py` for the consumer; the scraper
itself is HQ's and routed.

Ban list checked on this entry.
