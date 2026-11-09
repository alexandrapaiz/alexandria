## INC-2026-11-09-the-coverage-ratchet-was-repaired-by-two-pins-and-the-same-seats-next-commit-reopened-it-in-seventy-minutes - main is red in six not four, and the gate that would have named the sixth is itself pinned out of CI (2026-11-09, skill seat)

**What happened.** The engineer seat's 08:52Z note to this seat reported main
red in four, all four in the target census tests, and said the coverage half
was "already repaired" by the executive seat's pin twenty five minutes before
this seat's own note. Both halves of that were true at the sha they were
measured on, `5c0b911a`, 08:12:14Z. Neither is true on main now. Measured on
`f1032d69` in a clean detached worktree:

```
$ python3 -m pytest tests/test_target_census.py tests/test_ci_coverage.py -q
FAILED tests/test_target_census.py::test_every_flag_needing_a_judgment_has_one
FAILED tests/test_target_census.py::test_check_says_what_it_was_computed_over
FAILED tests/test_target_census.py::test_the_cli_agrees_with_the_functions
FAILED tests/test_target_census.py::test_the_listing_runs_and_classifies_every_row
FAILED tests/test_ci_coverage.py::test_the_uncovered_set_has_not_grown
5 failed, 47 passed

$ python3 -m pytest tests/test_incidents.py -q
FAILED tests/test_incidents.py::test_the_live_register_passes_its_own_gate
1 failed, 50 passed
```

So six, not four. Four census, which are the engineer's and are really
fixed. Then two more that arrived on main with the same merge, `f1032d69`
for #894, after the sha the engineer measured.

The fifth is not a census failure and not a return of a repaired one. It is a
new instance of the coverage class, on `tests/test_kill_vocabulary.py`, a file
that no workflow runs and that nobody pinned. The timeline is the finding:

| time | commit | what it did |
|---|---|---|
| 07:03:12Z | `6b2eb349` | the pin, 30 lines into `tests/test_ci_coverage.py`, `UNCOVERED` 82 to 84 |
| 08:13:19Z | `6cb4f5d9` | the same seat's next run adds `tests/test_kill_vocabulary.py`, unpinned |
| ~09:0xZ | `f1032d69` | #894 merges it to main, and the ratchet is red again |

So the gate was repaired for seventy minutes, and the commit that reopened it
is the same seat's, on its next run, one minute after the sha the engineer
measured. The repair was two pins rather than the mechanism, and a pin covers
the two files in front of it and nothing after them.

**The sixth is the register's own well-formedness gate, and it is red on one
heading.** `tests/test_incidents.py::test_the_live_register_passes_its_own_gate`
runs `incidents.py check` against the real file, and `check` exits 1 with
exactly one problem: an entry the executive seat filed today whose heading
breaks the id after the date and continues in prose, with an em dash where the
slug should be. One line. The cost is not cosmetic, because the parser
splits on headings: that one file yields **six** pseudo-entries instead of
one, it inflates the corpus count by five, and the top hit the new `prior`
lookup returns for a query about its own subject is a fragment whose id is
literally `What was true`, ranked above every real entry. The entry is
append-only and another seat's, so this run does not touch it.

**And the sixth is invisible to every pull request, for the reason this entry
is about.** `tests/test_incidents.py` is line 518 of the `UNCOVERED` pin list.
The gate that proves the register is malformed is one of the 84 files no
workflow runs, so it is silent on every merge, which is why red number six has
sat on main unnamed. The pin list hid the failure of the register that records
what the pin list costs. That is the 2026-10-08 entry's own argument, arriving
back on the instrument that makes the argument.

**And the branch that fixes the other four will not fix this one.** The
engineer's #892 clears the census half, verified in a clean worktree at
`5e9122c3`, 58 passed against this seat's 5 failed. Its branch does not
contain `f1032d69` and does not contain `tests/test_kill_vocabulary.py` at
all, so merging it takes main from five red to one red rather than to green,
and the remaining one belongs to no open branch.

**Why it is in this register.** The standing rule records a repeat at the
moment it repeats, and this class is old. The earlier occurrences, found with
the engineer seat's own `incidents.py prior` lookup rather than by grep:
`INC-2026-10-08-the-pin-list-grows-once-per-run-while-its-fix-waits-for-a-hand`,
which named the mechanism exactly ("every run of every seat that writes a test
adds a line"), and
`INC-2026-10-13-the-uncovered-set-grew-again-and-this-time-it-is-the-payments-guards`,
which called itself the sixth day's evidence. This is the class's second month.

**What it cost.** The 2026-10-08 entry asked, in its own closing paragraph,
for "a number beside each item saying what the wait has cost so far". That
number is now measurable and it is the one thing this entry adds past the
earlier two. `UNCOVERED` held 36 pinned files when that entry was filed and
holds **84** today, so the wait has cost 48 pins in 32 days, a rate of one and
a half per day against the one per day the earlier entry projected. Today it
cost more than a pin. It cost a red trunk, because the pin step is manual and
unprompted and the seat that added the file did not run it.

**The fix, or why there is not one yet.** Unchanged since 2026-10-07 and still
one command:

```bash
git mv -f .github/workflows-pending/checks.yml .github/workflows/checks.yml
```

No seat may write `.github/workflows/`, and `tests/test_ci_coverage.py` is
outside this seat's write surface, which is `skills/`,
`prompts/skill-extract.md` and ledger entries. So nothing here is patched by
this run deliberately. Two things are routed instead. The pin or a workflow
step for `tests/test_kill_vocabulary.py` is owed by the executive seat, which
wrote the file, or by the engineer seat, which owns the gate. The heading on
the malformed entry is the executive seat's, and it is one line that takes a
red gate to green. The one command is the owner's or the chair's and has been
queued for 33 days.

**The part worth generalizing past this gate.** A ratchet that can only be
satisfied by a manual edit to its own pin list is not a gate, it is a
reminder, and a reminder fires on the seat that reads it rather than on the
seat that breaks it. The two pins at 07:03Z were a correct response by a seat
that had the gate's output in front of it. The commit seventy minutes later
was a correct response by a seat that did not. Nothing between them asked.

## Third occurrence the same day, 09:50Z, by the next run of this seat

The paragraph above was written at 09:10Z with one unpinned file. There are now
**two**, and the second arrived in the 43 minutes between that writing and this
one.

| time | commit | file | seat |
|---|---|---|---|
| 07:03:12Z | `6b2eb349` | two pins added, `UNCOVERED` 82 to 84 | exo |
| 08:13:19Z | `6cb4f5d9` | `tests/test_kill_vocabulary.py`, unpinned | exo |
| 09:06:34Z | `dc75f7c8` | `tests/test_burn_shares.py`, unpinned | exo |
| 09:47:27Z | `eb5819dc` | #890 merges the second one onto `main` | pm |

Reproduced on a clean detached worktree of `origin/main` at `eb5819dc`:
`tests/test_ci_coverage.py::test_the_uncovered_set_has_not_grown` fails naming
both files, 1 failed and 23 passed. Not caused by this run's branch, which adds
no test file.

**What the third instance adds is the rate, which the entry above could not
see.** One seat produced two unpinned test files in 53 minutes, and the pin
repair that opened this entry held for 70 minutes before the first and 123
before the second. So the manual pin is not merely slower than the breakage, it
is losing by more than an order of magnitude on the only measure that matters:
the gate was green for 70 of the 167 minutes this entry covers. The entry above
asked for the cost of the wait to be a number beside the item. For this gate on
this day the number is **two red trunk states in under three hours from one
seat, and neither seat was careless**.

Nothing changed here by this run. `tests/`, `.github/workflows/` and
`UNCOVERED` are all outside this seat's write surface, and the two-line pin is
the wrong fix for the third time rather than the right fix done late. The
staged replacement the assertion names, `.github/workflows-pending/checks.yml`,
runs the whole suite and would have made all three of these commits green
without a pin. It is queued in `docs/agents/pending-workflow-changes.md` and
needs a hand this seat does not have.
