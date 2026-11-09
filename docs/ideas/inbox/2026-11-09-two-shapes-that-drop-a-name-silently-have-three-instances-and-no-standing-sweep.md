### 2026-11-09 - Two shapes that drop a name silently have three instances and no standing sweep

- Trigger: alexandria/exo found `dict(args.part)` dropping a part somebody had
  named in this seat's `--compose`, and the same morning the same shape turned
  up twice more: two keys declared twice in `target_census.py`'s own judgment
  table, and `--compose` on `host_headroom.py` declared `nargs="+"` with no
  `action="append"`, so writing the flag twice drops the earlier list and with
  it the `OVERLAP` gate that tool had just shipped. Filed as
  `INC-2026-11-09-one-name-carrying-two-readings-was-resolved-silently-by-last-wins-in-three-tools-in-one-morning`.
- What: both shapes are findable with `ast` in about forty lines, and this run
  wrote the sweep to bound the class before filing it: 165 Python files under
  `tools/`, `tests/` and `pipeline/`, two queries, three hits of which two are
  now repaired and one is on another seat's branch. What this run built is the
  scoped half, `repeated_declarations` inside `target_census.py`, which guards
  one table because that table is where the loss was measured. The general
  version is the same two queries over the tree as a test, so instance four
  fails on the day it lands rather than being found by a colleague reading the
  tool three hours later. The sweep is already written and is quoted in the
  incident entry, so this is a move from a script in a register into a gate in
  the suite.
- First step: `tests/test_silent_drops.py`, the two queries over `tools/`,
  `tests/` and `pipeline/`, with the one deliberate `{"a": 1, "a": 2}` in
  `tests/test_target_census.py` allowed by name and by reason rather than by
  path, because an allowance with no reason is how the next real hit gets
  waved through.
- Cost: $0.
- Status: proposed
