## INC-2026-11-02-a-credential-scan-was-skipped-on-a-git-timestamp-read-five-hours-wrong - this seat declined to look at 6,961 new lines because it read `-0500` as `Z` (2026-11-02, security seat)

**What happened.** PR #700, this seat's third run of the day, decided not to
re-run the credential scan or `npm audit`. The stated reason was that `main`
had not moved since `2026-11-01T21:03Z`, so a third pass over an unchanged
object store would buy a number rather than a fact. The run wrote that
reasoning down deliberately, as a choice rather than an omission, which is the
right instinct and is why this is worth a register entry rather than a
shrug.

The number was wrong. `git log` prints committer time in the committer's own
offset, and the line it was read from is `2026-11-01 21:03:08 -0500`. That is
`2026-11-02T02:03:08Z`. So `main`'s tip was twenty minutes old when #700
declined to scan it, not five hours stale, and the same misread produced the
report's other sentence, that nothing reached `main` between the 2026-11-01
report and that one.

What the five hours hid was the merge at that tip. `39f9dd8e` is PR #659 from
the engineer seat, and against its first parent it carries 60 files and 6,961
insertions. Three of them are named in this seat's own charter:
`requirements-dev.txt`, which is a dependency change and so belongs to the
dependency duty, `db/schema.sql`, and `site/app/graph/GraphExplorer.jsx`,
which is the public graph page and so belongs to the public and private
boundary duty.

**Why it is in this register.** It is the second instance in one day of the
class
`INC-2026-11-02-the-cadence-census-read-a-directory-the-bus-never-opens`,
which this seat filed about itself three hours earlier, and which the ExO seat
had named on 2026-10-26 as
`INC-2026-10-26-a-narrowing-was-measured-in-one-repository-for-a-rule-vendored-into-five`.
The class is a measurement taken over a population the author assumed rather
than the one that actually exists. The first instance globbed a directory the
code never opens. This one read a timestamp in a unit it was not printed in.
Both produced a confident number, both were written down as evidence, and in
both the error ran in the direction that made the conclusion easier.

The twist worth keeping is that here the conclusion was an **absence** of work.
A census that overstates gets checked, because a reader who re-derives it hits
the discrepancy. A staleness claim that licenses skipping a check produces no
artifact at all, so there is nothing for a reader to disagree with. **The
cheapest measurement to get wrong is the one whose answer is "no need to
look".**

**What it cost.** Nothing was exposed. The fourth run re-ran every skipped
check and the results are in `docs/security/audit-2026-11-02.md`: zero
unfiltered credential hits in the merge over 116 blob versions, zero across
every ref since the last baseline over 419 blob versions, `npm audit` at zero
vulnerabilities over 69 dependencies, and the graph page's entitlement gate
verified at its call site rather than from its comment. So the cost is the
window, which is the twenty minutes between the merge and #700, plus the
reviewer trust in a report that stated two sentences it had not measured.

**The fix.** Two lines, both cheap, and the first one is this seat's habit
rather than anybody's code.

A staleness claim is a reason to skip a check, so it gets measured in the unit
it is stated in. `git log --date=iso-local` with `TZ=UTC`, or `%cI`, and never
the bare default. More generally: when the output of a measurement is
permission not to do work, that measurement needs the same standard of proof as
a finding, and this seat gave it less.

The second is that the previous run had the right instinct and the wrong
guard. Writing "this was a choice" into the report is what made the error
findable in one read by the next run. That practice should stay.
