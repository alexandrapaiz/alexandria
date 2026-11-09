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
