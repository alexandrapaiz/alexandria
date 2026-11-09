# Engineer run, 2026-11-09, message wake (red main, and the register's missing lookup)

Three events, and they resolve to one piece of work plus two answers.

## What the wake asked, and what each event turned out to be

alexandria/skill's 07:28Z note said `main` is red in five tests, named the pull
request that did it, and said neither of the two files involved is a surface
they may write. That is this seat's surface, so a break-fix outranks the lane.

A `checks` failure on this seat's own `#878`, read red at 07:47Z. **Already
answered by this seat's own later commit**, which is L-A31's case exactly, so it
is answered once by reference below and not repaired twice.

alexandria/skill's 08:06Z note cleared the blocker on `#878` and filed a third
thing for this seat: nothing answers "has this failure been filed before, and
did that entry prescribe a remedy?" over this register. That became the run's
build, because it is the one of the three that is not bookkeeping.

## Main's red, measured rather than taken on report

The full suite in a clean worktree at `origin/main`, `5c0b911a`, with nothing of
this seat's in the tree:

```
4 failed, 2980 passed, 7 skipped, 17 warnings in 677.30s

FAILED tests/test_target_census.py::test_every_flag_needing_a_judgment_has_one
FAILED tests/test_target_census.py::test_check_says_what_it_was_computed_over
FAILED tests/test_target_census.py::test_the_cli_agrees_with_the_functions
FAILED tests/test_target_census.py::test_the_listing_runs_and_classifies_every_row
```

**Four, not five, and the five was right when it was measured.** Both halves of
the report check out against the commits they belong to, which is why this is a
timing correction rather than a disagreement. At `1f51bf33`, the commit that
landed `tools/pr_backlog.py`, the two gate files together are **5 failed, 46
passed**, and the fifth is `test_the_uncovered_set_has_not_grown` naming
`tests/test_pr_backlog.py`. At its parent `027a7ddc` they are **51 passed**, so
the attribution to that pull request is exactly right and the trunk was green
before it.

What moved is `main`. #871 pinned both uncovered test files at **07:03:12Z**,
twenty five minutes before the note was written, so the coverage half of that
red was already repaired on live `main` when it was reported, and nothing was
owed on either file. The census half was still live and is fixed in this stack.

One number in the report does not reproduce and it is worth naming rather than
rounding off. The note said five fail and twenty four pass on the trunk, and
twenty eight pass one commit earlier. This run reads 46 and 51 over the two gate
files, and 2,980 over the suite. The counts are not recoverable without knowing
the selection they were taken over, which is the ledger entry this run filed.

## What shipped

`tools/incidents.py prior`. The question a seat actually holds is a failure and
not an id, and no instrument took one. `check` asks whether the register is well
formed and `fold` moves it. Neither answers this.

Two measured reasons this could not be a grep. 258 of the register's 632 entries
are not in `docs/agents/incidents.md` at all, so grepping the register file
reads 59% of the register, and the remedy missed this morning was in the inbox
half. And the unit of the answer is an entry with an id, a date, a seat and a
fix paragraph, not a line of prose with no boundaries.

Scoring is inverse document frequency over the entries, so a path appearing in
two entries outranks a word appearing in four hundred and there is no stopword
list to go stale. 632 entries in 2.4 seconds, no network. Each hit carries
`REMEDY`, `OPEN` when the fix section says the fix is owed, or `NONE` when there
is no fix section, and the fix paragraph is printed rather than cited.

The regression test is the case that produced it. The query that reproduces this
morning's receipt failure must keep returning
`INC-2026-10-26-the-library-shows-the-older-of-two-receipts-dated-the-same-day`
with a `REMEDY` verdict and the word `timestamp` in the paragraph.

## What using it found, including in itself

Running it rather than reading it is what found four defects, and three of them
were in this run's own new code.

`new` ranked the skeleton it had just written at 1.000 and pushed the real
precedent to second place. `new_entry(inbox=INBOX)` and
`report_prior(stream=sys.stdout)` were both default arguments bound at import:
the first wrote a test fixture into the real register's inbox before the line was
changed, and the second wrote past `capsys`, so a failing assertion pointed at
the ranking instead of at the harness. `tools/target_census.py` in the same
family already uses `stream=None` with `or sys.stdout` in the body, so the
convention existed and this code diverged from it inside one repository.

And the close-match threshold was a fixed floor, which means two different
things at two query lengths. A short query called 32 of 632 entries close and a
two-sentence one called 222, which makes the word useless in the case where a
seat pastes a failure verbatim. It is relative to the best hit now, and the same
two queries read 14 and 32.

The fourth is the gate catching this run. `tools/target_census.py --check` went
red on the two new flags within a minute of their being written, which is the
same gate that has `main` red right now, working on the diff in front of it.

## What it does not fix

Nothing makes a seat run it. The charter sentence still says "check the
register", and a sentence is what failed this morning. The wiring into `new`
catches the seat that files and misses the seat that reads, concludes there is
no precedent, and ships. Making it a gate was considered and rejected: a lookup
that can fail a run is a lookup a seat stops running. The charter line belongs
to the owner's merge, so it is an ask and not a diff.
