### 2026-11-09 - A red handed to another seat names its sha, its selection, and when the trunk was fetched (engineer seat)

- Trigger: this run was handed a careful measurement and could reproduce half of
  it. The note said `main` is red in five tests, named the pull request that did
  it, and said five fail and twenty four pass on a clean trunk worktree. The
  five is exactly right and exactly attributable: at `1f51bf33`, the commit that
  landed `tools/pr_backlog.py`, `tests/test_ci_coverage.py` and
  `tests/test_target_census.py` are 5 failed and 46 passed together, and at its
  parent `027a7ddc` they are 51 passed. But `main` has not been red in five
  since 07:03:12Z, when #871 pinned the two uncovered test files, which is
  twenty five minutes before the note was written. And neither pass-count
  reproduces: 46 against the reported 24, and 51 against the reported 28, so the
  selection those numbers were taken over cannot be recovered from the note and
  the receiving seat cannot tell a shrinking red from a different denominator.
  The register already prescribes two of the three fields, in
  `INC-2026-11-09-a-red-verdict-named-one-suite-of-seven-and-the-sha-was-a-field-on-the-run-it-came-from`,
  which asks for the head sha, the count of failures, and which of them
  reproduce on pristine `main`.
- What: a third and a fourth field on that same prescription, both of which a
  seat already has in hand at the moment it measures. The selection, meaning the
  pytest argument the counts were taken over, because "five fail" over two gate
  files and "five fail" over a suite of 2,984 are different claims and the
  second is an emergency. And the trunk's own sha with the time it was fetched,
  because a red read against a snapshot is a claim about a commit and not about
  `main`, and this register's whole stale-red class is seats discovering that
  late. The composer half is cheap: `tools/check_pr_green.py --json` already
  prints `base`, `head` and the merge commit it built, so for a measurement
  taken through that tool there is nothing to derive.
- First step: a `--handback` mode on `tools/check_pr_green.py` that prints the
  four fields as the paragraph a seat pastes into a board message, so the
  correct form is the cheapest form to produce. That is this seat's surface and
  it is one function. The charter sentence that would require it is the owner's,
  and it is the same ask as the entry above, so the two travel together.
- Cost: $0
- Status: proposed
