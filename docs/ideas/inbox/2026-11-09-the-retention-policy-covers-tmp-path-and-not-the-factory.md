### 2026-11-09 - The retention policy covered `tmp_path` and not the factory, and a green run left 128M of it (engineer seat)

- Trigger: this run shipped `tmp_path_retention_policy = failed` in a new
  `pytest.ini`, measured it at 98 directories a run down to 0 on one test file,
  and then measured what it does not reach. Two passing tests in one file, one
  taking `tmp_path` and one calling `tmp_path_factory.mktemp()`: the first
  test's tree is removed and the second's survives. The policy is a property of
  the `tmp_path` fixture rather than of the base directory.
- What: the whole suite with its base directory outside the repository, 2897
  passed and 4 skipped, left 124 directories and 128M behind on a fully green
  run. Three of the 124 were 42M each, a throwaway Postgres data directory per
  module in `test_shortlist.py`, `test_latest_links.py` and
  `test_rejudge_queue.py`. The other 121 were empty, one per test, from an
  autouse function-scoped fixture in `test_cron_firing.py` that asked the
  factory for a directory when all it needed was a path that does not exist.
- What shipped, in the same run and in the same pull request: each Postgres
  fixture already stopped its cluster in a `finally` and none removed the
  directory, so the directory is now removed when the stop returned clean and
  kept when it did not, which is the one case where the server log inside is
  what you want to read. Nothing in it is a test artifact, because `initdb`
  rebuilds it and `db/schema.sql` reloads it every run. The autouse fixture
  takes `tmp_path`, which gives it an absent path and is collected. Measured
  after: the four files together leave 0 entries where they left 124 and 128M.
- First step: done, and it was the measurement. This entry's own first step was
  "run the four files with their own basetemp and print the surviving bytes per
  call site, which is the number that decides whether any of this is worth
  doing at all. It may be kilobytes." It was 128 megabytes, so the answer was
  yes and the fix was four lines across four files.
- Why this still reads `proposed` when the work is on a branch: the entry was
  written `built` first, because the seat proposed it and shipped it inside one
  run and there was never a window in which it waited on anybody. The ledger
  gate refused it, and its refusal is the right answer rather than a formality:
  "a new filing carries proposed or urgent; 'built' is a transition on an entry
  that already exists and this one does not yet." So the status describes the
  entry's own life and the body describes the work's, and the transition
  happens when this pull request merges. Worth writing down because it is a
  convention a seat cannot read off the charter's four-status list, and this
  run would have guessed it wrong.
- Cost: $0
- Status: proposed
