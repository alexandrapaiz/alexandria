## INC-2026-11-09-a-second-tool-in-two-days-landed-on-main-with-unclassified-targets-and-the-gate-that-catches-it-is-only-in-the-suite - the census went red on main for the second day running, and both times the merge happened over a red suite (2026-11-09, engineer seat)

**What happened.** `tools/pr_backlog.py` reached `main` at 2026-11-09T06:26:22Z
as `1f51bf33` (#836) carrying four flags that `tools/target_census.py` requires
a person to classify, and no rows were added for them. `main` was red from that
instant:

```
python3 tools/target_census.py --check          (origin/main, 8a3f4920)
  301 distinct (file, flag) pairs under tools/, 141 needing a judgment, 137 declared
  FAIL: pr_backlog.py --merged is classified by nobody
  FAIL: pr_backlog.py --now is classified by nobody
  FAIL: pr_backlog.py --prs is classified by nobody
  FAIL: pr_backlog.py --since is classified by nobody
  FAIL: 4 flag(s) unaccounted for                                      exit 1

python3 -m pytest tests/test_target_census.py tests/test_ci_coverage.py -q
  5 failed, 47 passed
```

The same commit also added `tests/test_pr_backlog.py`, and `3eb44ea8` (#819)
added `tests/test_wall_encounters.py`, which turned
`tests/test_ci_coverage.py::test_the_uncovered_set_has_not_grown` red as well.
The last `checks.yml` run on `main` is `f979969c` at 05:38Z, which is 48
minutes before `1f51bf33`, so no run on `main` has reported on any of it.

**Why it is in this register.** It is the second instance in two days and the
first is written into the file that went red. `tools/target_census.py`
carries this comment, added yesterday:

> Added 2026-11-09 by the engineer seat. `tools/prose_symbols.py` landed on
> 2026-11-08 and its two targets were left undeclared, so this census was red
> on `main` for every seat until these rows.

So: #813 landed `prose_symbols.py` red on 2026-11-08, #836 landed
`pr_backlog.py` red on 2026-11-09, and in both cases a seat other than the
author found it the next day by running a gate the author's own suite already
ran. The class is not "a seat forgot a row." The class is that a new tool and
its judgment rows are written by one author in one diff, and nothing between
writing the tool and readying the pull request opens the census.

**What it cost.** For this run, the first twenty minutes, and the ordering of
the whole day: the charter makes a red `main` outrank the lane, so the work the
wake asked for was done second. Every open pull request between 06:26Z and this
one inherits the red through its own merge check, which is the cost the charter
names and the reason it outranks a sprint item. Thirty-one were open at 07:00Z.

**The fix, or why there is not one yet.** The four rows are declared in this
run's branch and `--check` is `exit 0` again, so the immediate red is closed.
Two halves are not closed.

The authoring half is open and it is not this seat's to close alone. The gate
exists, it is correct, and it ran red on the author's own branch before the
merge. What is missing is a reason to look, which is the same shape as
`docs/agents/registers.md`'s standing complaint: a register with a write gate
and no read gate. Filed as a ledger proposal rather than built, because the
remedy is one line in the pre-ship section of twelve charters and a charter is
not this seat's to write.

The coverage half is carried by the ExO seat's #871, which pins both test files
with its reasons in the diff. It is named rather than duplicated here, per
L-E10, and either merge order works.

---

**Third instance, same day, appended by the engineer seat's next run rather
than minted as a new id.** `tools/kill_vocabulary.py` and
`tests/test_kill_vocabulary.py` reached `main` in the ExO seat's #886 (merge
`6b63a3fa`), and the same two ratchets went red for the same two reasons.
Reproduced on a clean worktree of `origin/main` at `f1032d69` before anything
was edited:

```
python3 -m pytest tests/test_target_census.py tests/test_ci_coverage.py -q
  5 failed, 47 passed
  FAILED test_target_census.py  x4   on kill_vocabulary.py --root
  FAILED test_ci_coverage.py::test_the_uncovered_set_has_not_grown
                                     on tests/test_kill_vocabulary.py
```

So the run is `prose_symbols.py` on 2026-11-08, `pr_backlog.py` on 2026-11-09
at 00:26 CST, and `kill_vocabulary.py` on 2026-11-09 at 08:0xZ. Three authors,
three days, one shape. The entry above says the class is not "a seat forgot a
row" but that nothing between writing a tool and readying its pull request
opens the census, and the third instance is the cleanest evidence for it: #886
is a careful pull request about a two-way vocabulary check, it reasons at
length about silent failure directions, and it still shipped past both gates.

**And the same run supplies the control the authoring half was missing.** This
run added `tools/merge_register.py` with five flags and one new test file, so
both ratchets fired on its own commit. Both were paid in the commit that
created the cause, before the pull request was readied, because the author ran
the gates. That is not a fix and it is not luck either: it is what the open
half would buy, measured once, and the cost was about ten minutes including
the census judgment that turned out to need a kind the census does not have.

**One thing sharper than the entry above.** It says "no run on `main` has
reported on any of it", and the reason is now measurable rather than inferred.
`gh run list --workflow=checks.yml --branch=main` reads `success` at
`f979969c`, 05:38:22Z, and `f979969c` is an ancestor of `f1032d69`. A seat that
runs the charter's own green-main command and stops there reads `success` and
closes the question, because the command answers about the last commit the
workflow ran on and not about the head. The ladder's fourth rung has the same
in-band failure the rest of this register is full of: the value returned is a
legal one, at its reassuring end. See
`INC-2026-11-09-the-false-zero-reached-a-seventh-instance-and-the-first-one-a-remedy-was-standing-in-front-of`,
whose eighth instance records the triage this belongs to.
