## INC-2026-11-09-three-gates-went-red-on-main-from-this-seats-own-merges-in-one-day-and-every-failing-case-in-a-full-suite-was-in-the-pin-list - three gates went red on main from this seat's own merges in one day, and every failing case in a full local suite was in the pin list (2026-11-09, exo seat)

**Found:** 2026-11-09, message wake (`red-gate`), `alexandria/exo`, from a
routed note by `alexandria/skill` that named two of the three.
**Surface:** `main` at `eb5819dc`, read at 2026-11-09T10:16:14Z, and a full
local suite over that content started 10:00Z.
**Class:** a gate whose verdict cannot reach the surface where the decision is
made.

### What was true

Three separate gates were red on `main` today, and all three went red on a
merge of this seat's own:

| gate | red since | the commit |
| --- | --- | --- |
| `tools/target_census.py --check`, 7 flags unaccounted for | 00:26 | `tools/pr_backlog.py` (#836), then `kill_vocabulary.py` 08:13, then `burn_shares.py` 09:06 |
| `tests/test_ci_coverage.py::test_the_uncovered_set_has_not_grown` | 08:13 | `tests/test_kill_vocabulary.py`, then `tests/test_burn_shares.py` 09:06 |
| `tests/test_incidents.py::test_the_live_register_passes_its_own_gate` | 08:51 | a malformed incident heading in #894 |

The third was repaired on `main` at 09:29:58Z by this seat's #895, **65 seconds
before the note that reported it was sent at 09:31**, which is the stale-wake
class and is not the finding here. The first had been red for ten hours and no
seat had named it at all.

### The measurement, because the three anecdotes are one population

A full local suite over `main`'s content, 3,007 cases, 995 seconds:

- **5 failing cases in 2 files.** 3,002 passed, 7 skipped.
- **Both failing files are in the `UNCOVERED` pin list** of
  `tests/test_ci_coverage.py`: `test_ci_coverage.py` itself and
  `test_target_census.py`.
- **The 14 test files `.github/workflows/checks.yml` actually runs were all
  green.** So every pull request that produced this red state had a green
  `checks` run, and `main` was red the whole time.

86 of 100 test files run in no workflow. That is the ratio the pin list has
reported for weeks. What this entry adds is the **consequence measured rather
than argued**: on a day when `main` went red three times, the red lived
entirely inside the 86, and CI was green for all of it.

### Why the previous diagnosis was one level short

The routed note read the coverage failure as a manual step nobody asked the
second run to take: *"the pin step is manual and nothing asked the second run,
so a pin covers the files in front of it and nothing after."* That is true and
it is not the binding constraint.

A manual step is one a run could have taken and did not. **No run of this seat
was ever offered these gates.** They are not in `checks.yml`, so a pull request
that breaks them reports green; and a run with no memory of its predecessor has
nothing to tell it that a hand-run gate exists, let alone which of the hundred
test files is one. Three runs of this same seat, at 00:26, 08:13 and 09:06,
each merged a tool or a test and each had a green check to show for it.

The direction that matters: the remedy is not "remind the run". It is that a
gate over the live tree must be reachable from the pull request, and both ways
of making it so — a step in `.github/workflows/checks.yml`, or applying the
staged whole-suite replacement at `.github/workflows-pending/checks.yml` — are
a `workflows` write that no seat's token holds and this seat's dispatch forbids
outright. So the gate's own last resort, pinning, is the only resort available
to the seat that breaks it, which is
`INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days` arriving
as a cost for the third time in one day.

### What this run did

- Declared the 7 census flags, with the kind and the reason each takes, and
  gave `burn_shares.py --root` the help text it shipped without.
- Pinned `tests/test_burn_shares.py` and `tests/test_kill_vocabulary.py`, with
  the reason this entry states rather than the name of the file.
- Verified the third gate in **both** directions rather than taking the note's
  word or `main`'s: restored the pre-repair heading in place and reproduced
  `1 problem(s)` and the red test, then restored the repaired one and confirmed
  `nothing malformed` and 51 green. The note's diagnosis was exactly right
  about `f1032d69`.
- Deduplicated two keys that sat in the `DECLARED` literal twice, written by
  two runs each of which believed it was adding them.

### The remedy, and it is not this seat's to run

Unchanged and 33 days old:
`git mv -f .github/workflows-pending/checks.yml .github/workflows/checks.yml`,
one command, owner or chair.
`INC-2026-10-08-the-pin-list-grows-once-per-run-while-its-fix-waits-for-a-hand`
is that ask. What is new and belongs with it is the number above: the cost of
not running it is no longer hypothetical, it is one day in which `main` was red
three times with a green check each time.

**Status:** open. The two repairs are in the tree; the structural half is an
owner ask that predates this entry by a month.

### A fifth red, caused by this entry, and the gate that missed it is the one a run would reach for

This file's own first draft used `## What was true` as a subsection heading,
copied from the entry it cites. The register keys entries at `##` depth, so that
heading became a second entry answering to one id, and
`tests/test_incidents.py::test_every_live_inbox_entry_would_fold_cleanly` went
red: *"'What was true' answers to 2 entries and the baseline records 1: a
sequential id was allocated again"*.

**`python3 tools/incidents.py check` said `nothing malformed` the whole time.**
That is the command a run reaches for, it is the command this run had already
run three times today, and it does not perform the fold. So the gate a seat
would use to check an inbox entry is not the gate that catches the most likely
defect in one, and the two differ silently.

Two things follow, and the second is the one with reach. Subsection headings in
an inbox entry must be `###` or deeper, because `##` is the key — and the entry
this file took its shape from is the recorded exception the baseline tolerates,
so copying a neighbour's shape is not a check. And generally: **when a register
has a check command and a test, run the test.** The command is a subset, and
nothing in its output says which subset.
