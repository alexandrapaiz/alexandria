### 2026-11-09 - The retention policy covers `tmp_path` and not the factory, and eight call sites use the factory (engineer seat)

- Trigger: this run shipped `tmp_path_retention_policy = failed` in a new
  `pytest.ini`, measured it at 98 directories a run down to 0 on one test file,
  and then measured what it does not reach. Two passing tests in one file, one
  taking `tmp_path` and one calling `tmp_path_factory.mktemp()`: the first
  test's tree is removed and the second's survives. The policy is a property of
  the `tmp_path` fixture rather than of the base directory, so a session-scoped
  factory directory is outside it.
- What: `tests/` has eight `tmp_path_factory` call sites across
  `test_shortlist.py`, `test_latest_links.py`, `test_cron_firing.py` and
  `test_rejudge_queue.py`. Those are the suite's remaining footprint on a
  volume twelve seats share, and they are the ones a reader of the new
  `pytest.ini` would assume are covered, which is the worse half: a policy that
  is believed to cover everything stops anybody looking. The work is to measure
  what those eight actually leave behind per run, then either move the ones
  that do not need session scope onto `tmp_path`, or wrap the rest in a
  finalizer that removes the tree when the test passed.
- Why not simply do it in the same run: the eight are session-scoped for a
  reason in at least some cases, a fixture built once and read by many tests,
  and converting one of those to `tmp_path` silently multiplies the work it
  does. That is a per-call-site judgment and it is a day's work rather than a
  line.
- First step: the measurement. Run the four files with their own basetemp and
  print the surviving bytes per call site, which is the number that decides
  whether any of this is worth doing at all. It may be kilobytes.
- Cost: $0
- Status: proposed
