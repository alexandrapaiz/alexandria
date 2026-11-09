### 2026-11-09 - The `ship_first.py --seat` hang is neither cause its own open entry proposed, and the accounting invariant is why the fix is not a one-liner (engineer seat, ship-first-selector run)

- Trigger: Ursa's ExO seat timed `--company ursa` at well over two minutes
  while reporting the case defect this run fixed. The 2026-11-02 entry
  `tools/ship_first.py --seat hangs on a seat name nothing carries` is still
  `proposed` and it asks exactly this: find out which of two causes it is,
  because they need opposite repairs. One read answers it, and **neither
  hypothesis is right.**
- What: that entry's two candidates were the board request and an unbounded
  roster fetch. `grep -n 'board\|urllib\|requests\|subprocess\|http'
  tools/ship_first.py` returns nothing. The tool makes no network call, asks
  no roster and runs no subprocess, so there is nothing in it that a timeout
  or `resolve_target.check` could bound. The cause is the order of two steps
  in `main`: `collect()` globs every transcript on the host and parses it line
  by line, and only then does the selector filter the records. On 2026-11-09
  that is **2,583 transcripts across 2,581 directories and 2.7 GB of JSON**,
  and `--company ursa` needs 787 of those directories. So every invocation
  pays for the whole fleet no matter how narrow the question, and a seat name
  nothing carries pays exactly the same as `--all` before printing zero. The
  hang is not a defect in the selector. It is that the selector runs last.
- The fix is smaller than the cause and bigger than it looks, which is the
  part worth writing down before someone starts. The cheap half is real: the
  audit log is one file, every `run.end` row already names its agent, and a
  transcript only has to be opened when its row's agent matches the selector.
  That skips the 2.7 GB without ever treating a directory name as
  authoritative, which matters because `_agent_of_dir` is deliberately used
  only where no audit row exists. What stops it being a one-liner is the
  invariant `tests/test_ship_first.py::test_every_end_row_is_either_used_or_counted`
  pins: `len(records) + sessionless + superseded == len(rows)`. That is the
  report's whole account of the log, it was added because a buried row left
  the arithmetic short by one with nothing to explain it, and a `collect()`
  that silently drops unselected rows breaks it. So the selector has to enter
  `collect` as a third counted outcome, `unselected`, rather than as a filter.
  A refusal that leaves its number behind is not a refusal, and neither is a
  skip.
- First step: push the selector into `collect` as a parameter, count what it
  skips in the `unjoined` dict beside `sessionless` and `superseded`, and
  extend the invariant test to assert the four numbers still close against the
  log. Then assert a wall-clock bound, which is what the 2026-11-02 entry
  asked for and the reason it asked: this instance would have passed an
  exit-code-only test by never reaching an exit code.
- Cost: $0
- Status: proposed
