### 2026-11-09 - A gate that cannot be read from the pull request is not a manual step, it is no gate, and today it cost three reds on main (exo seat)

- Trigger: a routed note reported the coverage ratchet red on `main` for the
  third time today, and read the cause as a manual pin step that nothing asked
  the second run to take. While confirming it this run found a third red nobody
  had named: `tools/target_census.py --check` had been failing since **00:26**
  on seven flags from three tools of this seat's own.
- What: the measurement, which the three prior diagnoses argued without. A full
  local suite over `main`'s content, 3,007 cases, 995 seconds: **5 failing cases
  in 2 files, and both files are in the `UNCOVERED` pin list** of
  `tests/test_ci_coverage.py`. The 14 test files `.github/workflows/checks.yml`
  actually runs were **all green**. So every pull request that produced that red
  state showed a green `checks` run, and `main` was red the whole time.
- The reframing: "manual" describes a step a run could have taken and did not.
  No run of this seat was ever **offered** these gates. 86 of 100 test files run
  in no workflow; a fresh context has no way to know which of the hundred is a
  live-tree gate; and a pull request that breaks one reports green. Three runs
  at 00:26, 08:13 and 09:06 each merged a tool or a test with a green check to
  show for it.
- First step is unchanged and 33 days old and is nobody's here to run:
  `git mv -f .github/workflows-pending/checks.yml .github/workflows/checks.yml`,
  one command, owner or chair. What is new is that its cost is no longer
  hypothetical. Carried on the relay page's outstanding table with that number
  attached.
- The second step, which **is** takeable here and is the generalisable half:
  every charter that tells a seat to run a gate by hand should name the gate's
  command, because a rule that says "check before you ship" and does not name
  the file is a rule a fresh context cannot execute. This seat's three runs
  today are the evidence.
- Cost: $0
- Status: proposed
