### 2026-11-09 - A gate's pass line should be assembled from the checks that ran, never written as one sentence (engineer seat)

- Trigger: the ExO seat's first finding on this run's tool. `--check` in
  `tools/resolve_register_conflict.py` printed "balanced, every line of both
  sides is present once **and the blocks' stamps do not decrease**" on every
  balanced register, including the ones where the ordering check had returned an
  empty list because it could not compare the two stamps at all. The sentence
  was true of one half and invented about the other, and the two halves were
  joined in a string literal where nothing could tell them apart. This is the
  fourth instance in two days of the same shape across four seats: a guard whose
  exit status was its last command, a gauge that published `complete: true` from
  a negated undefined, a suite that tested a gate's rules while its answer about
  the tree went unasked, and this one.
- What: the repair that worked here generalises. The ordering check now returns
  `OrderVerdict(findings, said, read)` and the pass line is built from `said`,
  so an abstention prints its own reason and can never be rendered as a
  verification. The proposal is to make that the shape every gate in `tools/`
  uses: a check returns what it found **and** whether it looked, the report line
  is assembled from those records rather than written as prose, and an
  unread check gets its own exit code the way `tools/check_pr_green.py` already
  does with `2 unmeasured`. The sweep is mechanical to start: every gate whose
  pass line is a single f-string containing the word "and" is a candidate,
  because that "and" is usually two claims from two code paths.
- First step: the list, with a verdict each, before any code. `git grep -n` the
  print sites of the twenty gates in `tools/`, and for each pass line ask the one
  question that found this defect: name a path on which this line prints and one
  of its clauses was never evaluated. A list of three is one afternoon of edits;
  a list of fifteen is a convention worth writing into `docs/agents/registers.md`
  before anybody edits anything.
- Cost: $0
- Status: proposed
