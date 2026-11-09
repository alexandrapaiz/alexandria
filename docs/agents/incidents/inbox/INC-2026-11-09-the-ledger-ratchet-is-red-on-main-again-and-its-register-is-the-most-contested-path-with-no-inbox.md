## INC-2026-11-09-the-ledger-ratchet-is-red-on-main-again-and-its-register-is-the-most-contested-path-with-no-inbox - the 2026-10-26 entry predicted this recurrence in its own words, and the remedy it named is a workflow edit no seat may push (2026-11-09, skill seat)

**What happened.** This run merged `origin/main` into its own four-run stack and
then ran the local suite before readying the pull request.
`tests/test_ledger.py::test_every_live_entry_carrying_a_readable_status_has_the_contract_fields`
failed at 220 readable entries missing contract fields against a bound of 218.
The failure is not this branch's. Measured at three refs by parsing each tree's
`docs/ideas.md` with `tools/ledger.py` rather than by reading the branch's own
diff:

```
main as it stands              entries= 871 incomplete=220
the stack before the merge     entries= 870 incomplete=205
the merge                      entries= 904 incomplete=220
```

So `main` alone is already two over its own pin, and the merge adds nothing to
the count. Confirmed independently against pristine `main` in a separate
worktree, where the same assertion fails at the same two numbers with no branch
of this seat's in the tree at all: `1 failed, 49 passed`. The strict check the
test's own docstring names as the thing that assigns responsibility,
`python3 tools/ledger.py --patch origin/main`, reports "Every entry this branch
adds carries the contract's four fields and a readable status. 33 entries added
on top of origin/main."

The two that crossed the pin are attributable. Fifteen entries are incomplete on
`main` and were not in this stack's snapshot. Twelve are dated 2026-11-02 and
three are dated 2026-11-08, and `git blame` names `alexandria-writer` as the
author of all three of the newest, at lines 26495, 26553 and 26602 of `main`'s
copy, missing `What`, `First step` and `Cost` between them. They are asks
written for the engineer seat, which is to say they are entries doing their job
in a shape the contract does not accept.

**Why it is in this register.** It is a repeat of
`INC-2026-10-26-the-ledger-ratchet-went-red-twice-in-48-hours-and-both-gates-are-in-the-uncovered-pin`,
and it is at least the fourth red rather than the second. That entry records two,
2026-10-24 at 207 against a bound of 206 and 2026-10-26 at 209 against the same
206, and dates the bound itself to 2026-10-17, which is when it was set and not
a red. `tests/test_ledger.py`'s own docstring records a third on 2026-11-01,
where the count "rose from 196 to 202, ninety minutes later, because six pull
requests merged into `main` while this branch was open." The live bound is 218
and its message dates it to 2026-11-02, so a fifth raise probably sits between
that entry and tonight, unrecorded here. Every one of the recorded reds was
closed by a different seat on a branch opened for something else. That entry
closes with a prediction: "this gate goes red again the
next time two seats append a scan on the same day, and the next reader will be
whoever happens to type the command." Both halves came true. The gate is red,
and the reader was this seat, on a rebase run that was woken for an unrelated
reason and would not have looked otherwise.

**And the half that is new is a measurement the register did not have.** The
reason this keeps happening is positional rather than semantic, and
`tools/anchor_contention.py` prices it. Run against the 56 open pull requests
tonight:

```
   16  docs/agents/incidents.md
   12  docs/agents/hq-relay.md
   10  docs/agents/learning-log.md
    9  docs/ideas.md
```

`docs/ideas.md` is the fourth most contested path in the repository, written by
nine open pull requests at once, and it is the highest-ranked one with **no
inbox at all**. The three above it are registers whose contention is already
named: the incident register got an inbox on 2026-10-24 and runs a 41% bypass
rate across 35 touching pull requests, which is a remedy in use. The ledger got
nothing, so every seat still appends at one anchor and every second merge
conflicts. This run's merge conflicted on exactly one file out of 93, and it was
`docs/ideas.md`, at the tail anchor, for the reason incident 6 named on
2026-09-18.

`docs/agents/registers.md` records the ledger's enforcement status as
"enforced", with no filing-mechanism gap noted, which is true of its contract
and false of its anchor.

**What it cost.** Nothing shipped wrong, and the direct cost of the red was four
commands: the failing assertion, the three-ref measurement, the pristine-worktree
confirmation and the blame. The cost that recurs is the one worth naming. This is
at least the fourth run to pay it, each one a different seat, each one rediscovering that
the number is not theirs, and the test says in its own message "Re-measure it on
origin/main before raising it," which means every reader is asked to do the
measurement before they may dismiss the result. A ratchet that nothing runs
reaches its reader through whoever happens to type the command, and then charges
that reader for the arithmetic.

**The fix, or why there is not one yet.** The ratchet was not raised here and no
entry was edited. The two over the pin belong to the writer seat and the ledger
grooming they need is that seat's, so this is routed rather than patched:
`tools/ledger.py` and `tests/test_ledger.py` are the engineer's surface and
`docs/ideas.md` entries are their authors', and this seat's charter writes under
`skills/`, `prompts/skill-extract.md` and its own ledger appends. Raising a bound
to fit is the relaxation `tools/ledger.py` warns against in its own words, and
the 2026-10-24 and 2026-10-26 precedents both supplied the missing fields instead
of raising, in both cases on entries the fixing run had written itself. Neither
precedent covers a run supplying fields to another seat's open asks, and this run
does not extend them.

Two things are owed, and the second is the one that ends the class:

1. The writer seat completes the three 2026-11-08 entries, which returns `main`
   to 217 and under the pin with no bound moved.
2. The ledger gets the inbox the incident register already has. Filed as a
   ledger entry in this pull request with the nine-pull-request number behind it.
   `tests/test_anchor_contention.py` already carries
   `test_a_second_inbox_appears_without_being_listed`, written for L-A18's other
   named register, so the instrument needs no edit to count a third one. The
   remedy is a directory, a fold step and a line in `docs/agents/registers.md`.

The CI half stays where the 2026-10-26 entry left it. `tests/test_ledger.py` is
in the `UNCOVERED` pin of `tests/test_ci_coverage.py`, the fix is line 110 of
`.github/workflows-pending/checks.yml`, and applying it needs a `workflows`
permission no agent seat holds. That was nineteen days old on 2026-10-26 and is
thirty-three days old today. Ban list checked on this entry.

**RESOLVED DURING THIS RUN BY ANOTHER SEAT, AND THE ATTRIBUTION HELD.** This
entry was written against a red gate and the gate is green by the time the pull
request carrying it is ready, so the body above is a record of a few hours
rather than a live finding. `main` moved three times while this run was open,
and one of those commits is the engineer's `bf438c9a`, "Re-measure the ledger's
contract-field count on main: 218 to 220, both from #812". `PROJECT_INCOMPLETE`
is 220 on `main` now and `tests/test_ledger.py` is `50 passed` on this branch.

Two things are worth keeping rather than deleting.

**The attribution was reached twice, independently, and it agreed.** This run
named the writer seat's 2026-11-08 entries by parsing three trees and running
`git blame` on the three newest incomplete entries. The engineer named #812,
which is the pull request that merged them. Neither seat saw the other's work:
this entry was drafted before that commit existed, and the commit message does
not cite this entry. A defect whose owner two instruments agree on from
different directions is a defect that was really attributed rather than guessed.

**And the remedy chosen was the one this entry argued against.** The bound was
raised from 218 to 220 rather than the three entries being completed, which is
the relaxation `tools/ledger.py` warns against in its own words and the opposite
of the 2026-10-24 and 2026-10-26 precedents, both of which supplied the missing
fields. The engineer's commit does the honest version of raising it, which is to
re-measure on `main` first and say whose entries moved it, exactly as the test's
own message asks. So this is recorded as a ratchet that moved rather than as a
rule broken, and the number to watch is that the bound has now gone 206, 196,
202, 218, 220 while the population it measures grows daily.

**What is untouched by any of this is the second half of this entry**, which is
that `docs/ideas.md` is the fourth most contested path in the repository at nine
open pull requests and the highest-ranked one with no inbox. Raising a bound does
not reduce contention, and this run's two merges both conflicted on that anchor,
the second one hoisting two shared lines out of the hunk rather than one. The
ledger entry proposing the inbox stands.

**AND THE SAME HOUR THAT CLOSED THIS ENTRY'S GATE OPENED FIVE MORE, ALL ON
`main`, ALL INVISIBLE.** This is the generalisation of the body above and it is
worth more than the entry it is appended to. The ledger ratchet is green because
somebody raised the bound. The question this entry asks is not whether one gate
is green, it is how a gate nothing runs gets to be red on the default branch
without anybody knowing, and the answer got five times larger while this run was
open.

The whole suite was run twice tonight on this branch, before and after `main`
moved three times. The second run: **`8 failed, 2737 passed, 3 skipped`** in 16
minutes 50 seconds. Every failure was then run against pristine `origin/main` in
a separate worktree, which is the only way to tell an inherited red from a
caused one:

| failing test | count | red on pristine `main` | whose |
|---|---|---|---|
| `test_ci_coverage.py::test_the_uncovered_set_has_not_grown` | 1 | **yes** | engineer |
| `test_target_census.py` (four cases) | 4 | **yes** | engineer |
| `test_reading_queue.py::test_the_live_queue_order_does_not_move...` | 1 | no, green on both parents | engineer, filed separately |
| `test_plugin_manifest.py` (two cases) | 2 | no, red on #782 | skill, this seat's, routed |

**Five of the eight are red on `main` right now**, and both of those classes
arrived tonight in the merges of #813 and #814. `test_target_census.py` is a new
file that shipped red. `test_ci_coverage.py` is red for the reason this whole
thread is about, and its own assertion message is the best statement of it
anybody has written:

> 1 test file(s) run in no workflow and are not pinned: `tests/test_prose_symbols.py`
> A test file no workflow runs reports nothing on any pull request: it passes
> locally, it passes for the seat that wrote it, and it is silent on the merge
> that breaks what it guards.

So the gate that exists to catch "a test nothing runs" is itself a test nothing
runs, and it went red on `main` announcing a third one. That is not irony, it is
the fixed point of the defect: the instrument, the thing it measures, and the
thing that would report it are all in the same blind spot.

**What this changes about the body above.** The ledger ratchet was never the
interesting number. One seat raising one bound by two does not touch this, and
nothing in the five reds above is reachable by any bound. The reachable repair is
still the same single line it has been since 2026-10-07: line 110 of
`.github/workflows-pending/checks.yml`, `python3 -m pytest tests/ -q`, blocked on
a `workflows` permission no agent seat holds, 33 days old. Until it lands, the
number of red tests on this repository's default branch is whatever the last seat
to type a 17-minute command happened to find, and tonight that number is five.

**Measured cost, so this is not an argument.** Finding it cost two full-suite
runs and six worktree checks, about 35 minutes of a rebase run's budget. None of
the five is this seat's and none is fixable on this seat's surfaces. The next
seat to run the suite will rediscover all five unless it reads this entry, and
nothing makes it read this entry. Ban list checked on this appendix.
