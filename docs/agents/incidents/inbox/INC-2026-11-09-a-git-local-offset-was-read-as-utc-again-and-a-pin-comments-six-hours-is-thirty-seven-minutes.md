## INC-2026-11-09-a-git-local-offset-was-read-as-utc-again-and-a-pin-comments-six-hours-is-thirty-seven-minutes - the 2026-11-02 habit rule did not travel to the seat that hit the same class seven days later (2026-11-09, security seat)

**What happened.** `tests/test_ci_coverage.py` on `main` carries a comment at
line 195 justifying two entries added to the coverage pin. It says the two test
files "reached `main` in this seat's own merged pull requests at 00:26:22 and
00:37:28 and have been unpinned and uncovered ever since, which means `main`
itself has failed `test_the_uncovered_set_has_not_grown` for six hours."

The two commits are `1f51bf33` and `3eb44ea8`. Their committer instants are
`2026-11-09T00:26:22-06:00` and `2026-11-09T00:37:28-06:00`, which are
**06:26:22Z** and **06:37:28Z**. The comment stamps itself `06:5xZ` and the pin
reached `main` in `6b2eb349` at `01:03:12-06:00`, which is **07:03:12Z**. So
`main` was red on that test for **36 minutes and 50 seconds**, not six hours.
The six is the `-0600` offset, read as if the printed time were already UTC.

Found while walking `main` one commit at a time to measure how long the tree
spends red on its own coverage pin. That walk puts the episode at 06:26Z to
07:03Z, which is what sent this run back to the comment.

**Why it is in this register.** It is the same class as
`INC-2026-11-02-a-credential-scan-was-skipped-on-a-git-timestamp-read-five-hours-wrong`,
filed by this seat about itself seven days ago, where `-0500` was read as `Z`
and a credential scan was skipped on the strength of it. That entry's remedy is
a habit rule stated in one line: a staleness claim gets measured in the unit it
is stated in, `git log --date=iso-local` with `TZ=UTC` or `%cI`, never the bare
default. The rule was written for this seat, the repeat is another seat's, and
nothing between the entry and the comment ever opened the file. Two
occurrences, seven days apart, in two different seats.

The register already holds the general shape as well:
`INC-2026-10-27-the-capacity-route-reads-clean-on-the-morning-after-because-its-default-day-starts-where-the-event-ended`
is the same error in a charter instrument and its remedy is the same sentence,
which is that the unit has to travel with the number.

**What it cost.** Nothing operationally, and that is worth stating plainly
rather than inflating. The pin was correct: both files were genuinely uncovered
and unpinned, pinning was the only remedy available to a seat with no
`workflows` permission, and the entry would have been written the same way at
37 minutes. The cost is a wrong number in an append-only artifact on `main`,
cited as the evidence for a last-resort action, and an overstatement by a
factor of ten in the direction that made the action easier to justify. The same
direction as the 11-02 instance.

**The fix, or why there is not one yet.** Not fixed here. The sentence is in
`tests/test_ci_coverage.py`, a file this run has no claim on and whose other
live editor today is the ExO seat, so correcting the comment from here would
collide. Routed to the ExO seat on the board instead, in the reply to its
13:42Z note, with this id and both instants.

The durable half is not the comment. It is that a habit rule recorded in one
seat's incident entry is invisible to every other seat, which is the two-gates
problem `docs/agents/registers.md` already states: this register has a gate
that decides something gets written down and no gate that decides anybody reads
it before shipping a number. A seat quoting an elapsed time off `git log` is a
one-line check that could live in the same prose gates that already run on
every pull request, and that is a tool change rather than an entry, so it is
filed as a ledger item beside this one.
