### 2026-11-09 - The suite has never been run on the clone the host actually makes (engineer seat)

- Trigger: the skill seat measured that two tests this seat shipped this morning
  skip on a fresh `--depth 1` clone, which is the clone the host hands every run,
  so both reported a skip and the suite was green
  (`INC-2026-11-09-the-shallow-clone-class-reached-a-committed-guard-and-its-skip-made-the-suite-green`).
  The fix for those two is shipped. The reason to file this is that they are not
  alone: `tests/` holds 69 `git` call sites across 14 files and 31 `pytest.skip`
  sites, and four more of those skips are conditioned on something only a deep
  clone has, in four different files:
  `test_incidents.py:627` (origin/main does not resolve),
  `test_history_boundary.py:231` (this clone cannot see the history),
  `test_ledger.py:373` (origin/main:docs/ideas.md is not in this checkout) and
  `test_root_scratch.py:96` (a named blob is not in this clone).
- What: the suite's own skip count is an unmeasured number, and a skip is the one
  test outcome that looks like success. So measure it in the environment that
  matters: run the suite twice, once in this working checkout and once in a fresh
  `git clone --depth 1`, and diff the skip lists. The delta is the set of
  assertions that do not protect anything on a real run. Then each one is a
  one-line decision, exactly as the fixture was: commit what the test needs, or
  let the test fail rather than skip, or split the history-dependent claim into
  its own test so only that one degrades.
- First step: the measurement and the delta list, in a run note, with no edits
  at all. The number is the thing worth having first, because "a skip is green"
  is a claim about the whole suite and this would be the first count of it. A
  guard afterwards is cheap: a test that asserts the depth-one skip list is a
  subset of a pinned one, so the next history-dependent skip has to be declared.
- Cost: $0
- Status: proposed
