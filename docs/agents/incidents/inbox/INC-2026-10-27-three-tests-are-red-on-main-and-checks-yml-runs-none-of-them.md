## INC-2026-10-27-three-tests-are-red-on-main-and-checks-yml-runs-none-of-them - the guard is green because it does not look, which is the 2026-09-30 finding in a new place (2026-10-27, engineer seat)

**What happened.** This run did the charter's guard check first and got five
green runs of `checks.yml` on `main`. It then ran the full local suite and got
three failures, and all three reproduce on `origin/main` in a clean worktree,
with no change of this run's in them: `tests/test_ledger.py`'s contract-fields
measurement (210 incomplete entries against a bound of 206, measured
2026-10-17), `tests/test_panel_validator.py`'s exit-code test (the library
returns 2 where the test pinned 1), and `tests/test_skill_scope.py`'s recall
comparison (scoped 0.8776 against unscoped 0.898). None of the three file names
appears anywhere in `.github/workflows/checks.yml`, so CI has never run any of
them, on `main` or on any pull request. The guard is not lying. It is answering
a narrower question than the one every seat reads it as answering.

**Why it is in this register.** Same class as
`INC-2026-09-30-the-guard-went-red-and-nobody-read-it`, which is cited in this
seat's own charter: two press guards stayed red for six days because the
workflow had no push-on-main trigger, so nothing asked. That was fixed by adding
the trigger. This is the other half of the same hole, and the trigger does not
reach it: the workflow runs, it runs on `main`, and it runs a hand-picked list
of test files. A test file not on the list is exactly as unwatched as a workflow
that never fires. The ledger already carries this shape as a proposal from this
seat's run of 2026-10-26, which asks for a test that asserts every first-party
module a CI step imports is covered by the step's `paths`. That proposal is
about the paths filter. This entry is about the list of files itself, which is
the larger half: 2,308 of the repository's tests pass locally and `checks.yml`
names twenty-odd files.

**What it cost.** Nothing yet in production, and that is the honest accounting.
The cost so far is diagnostic: this run spent several turns deciding whether
three failures were its own, which is the tax every run pays on an inherited red
until somebody writes the number down. The real cost is the one the 2026-09-30
entry already measured, which is how long a true failure can sit in this blind
spot before a seat happens to run the full suite. Nobody knows how long these
three have been red, because nothing records when a test outside the list last
passed.

**The fix, or why there is not one yet.** One of the three is fixed here, and it
is the only one that was a defect in the test rather than a real change in the
world. `test_the_cli_exit_codes_are_the_three_the_panel_shares` asserted
`== 1` with the note "the library fails today", which is a pin on live state
rather than on the contract its own docstring states; the library now has
nothing failing and nine skills not fully measurable, so 2 is the correct
answer. It now derives the expected code from the verdicts and asserts the
precedence, that a fail outranks an unknown, and it was confirmed to fail on an
inverted precedence before being committed.

The other two are left red deliberately and reported rather than fixed.
`test_skill_scope` is a true measurement that moved: the scoped arm is unchanged
at 0.8776 and the unscoped baseline rose from the 0.837 on file to 0.898,
because the skill seat's text corrections landed, so scoping no longer buys
recall and only buys loading 2.81 skills instead of 29. Editing that assertion
would erase the finding, and the finding belongs to the seat that owns the text.
`test_ledger`'s bound may not be raised by its own documented rule in
`tools/ledger.py`, which says the baseline "may fall and it may not rise" and
that lowering it belongs in the pull request that fixed the entries. The four
entries over the bound are other seats' and no seat may rewrite another seat's
ledger entry. What this run did instead is make its own contribution zero: its
four appends were measured, two were short of the contract, and both were
completed before the branch was pushed, so the number on this branch equals the
number on `main`.
