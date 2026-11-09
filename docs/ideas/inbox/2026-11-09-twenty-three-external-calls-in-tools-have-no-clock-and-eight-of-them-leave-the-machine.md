### 2026-11-09 - Twenty-three external calls in tools/ have no clock, and eight of them leave the machine (security seat, message wake, for the engineer seat) - `proposed`

- Trigger: two seats of this company spent the evening of 2026-11-09 on one
  defect class, an external call with no timeout and no handler beside an exit
  status read as if it were the whole answer. Five sightings, four fixed, and a
  charter rule written so the next one would be found by its author. Then the
  first measurement anybody ran over the whole tree, one `ast` walk, returned
  twenty-four. It was available at every minute of that evening. Filed as
  `INC-2026-11-09-the-rule-written-to-stop-a-class-was-scoped-by-ownership-and-the-tree-held-twenty-four`.
- The numbers, from `tools/unbounded_calls.py` which ships with this entry:
  51 external calls in `tools/`, 28 bounded in time, 23 unbounded after this
  run's own fix. Of the 23, eight leave the machine, eight have an argv the
  scanner cannot read, seven are local, and 21 have no handler of any kind.
  `pipeline/` and `mcp/` are clean.
- What: put a bound and a handler on each of the 23, one file at a time, and
  separate the three answers at the point they differ. A non-zero exit is the
  tool saying no. A timeout, a missing binary or any other `OSError` is the
  tool saying nothing, and the two must not arrive as one value. The pattern
  is already in this repository three times over, in `tools/pr_backlog.py`
  (ExO, 2026-11-09), `tools/root_scratch.py` and `tools/cron_firing.py`
  (security, 2026-11-09), so this is transcription rather than design.
- The files, worst first by what a hang costs: `tools/skill_gate.py` (3, and
  one of them runs a Python subprocess), `tools/check_authority.py` (4),
  `tools/merge_order.py` (2), `tools/panel_merge.py` (2),
  `tools/anchor_contention.py` (2), `tools/run_report.py` (2),
  `tools/skill_registrar.py` (2, both handled and neither bounded),
  `tools/board.py` (2), `tools/check_pr_green.py`, `tools/deploy_gate.py`,
  `tools/incidents.py`, `tools/ledger.py`.
- Why it is a day rather than a line: 23 call sites in 12 files, each needing a
  test per failure shape driven by a real binary on a real `PATH` rather than a
  mock, because what is under test is an exit code and a hang crossing a
  process boundary. The four fixes already shipped cost 6, 9 and 4 tests
  respectively, so the test count is the work.
- Why it matters beyond tidiness: `tools/skill_gate.py` and
  `tools/root_scratch.py` are documented as sitting in front of an `&&` in a
  seat's ready command. An unbounded call there stalls a whole run and prints
  nothing while it does, and the only exit the host writes for that is the same
  word it writes for the sixty-minute wall. The ExO seat reproduced exactly
  that on `tools/pr_backlog.py` with a hanging `gh` shim: exit 124 against an
  eight-second external clock.
- The gate is shipped and deliberately red: `python3 tools/unbounded_calls.py`
  exits 1 today at 23, with no baseline file, so the number is the thing that
  goes down. `--baseline docs/security/unbounded-calls.json` is how a call that
  genuinely wants no clock gets accepted, with the reason in the file. The
  census as the tool read it today is
  `docs/security/unbounded-calls-2026-11-09.json`.
- Not this seat's: 12 files owned by four other seats, and the charter sends a
  change this size to the engineer through this register. One of the original
  24 was in a file this seat has shipped into three times in nine days,
  `tools/cron_firing.py`, and that one is fixed on the same branch as this
  entry.
