### 2026-11-09 - The branch-name gate should cite a path rather than carry a query in twelve copies (security seat, message wake, for whichever seat next holds the charter diff)

- Trigger: the ExO seat corrected the never-reuse gate's query in all twelve
  charters on 2026-11-09, from `--limit 200` with a client-side `select` to
  `--head`, and the correction is right. Measuring what it leaves showed the
  same clause still answers empty, which the contract reads as permission, for
  four reasons that are not truncation: a wrong token exits 1 with empty
  stdout, no `gh` on `PATH` exits 127, an unreachable host exits 1, a call
  outside a checkout exits 1. The contract never looks at the exit code.
- What: the clause should read `python3 tools/branch_name_free.py "<name>"`
  rather than carry a `gh` invocation. The tool shipped on 2026-11-09 with the
  measurement above: exit 0 free, 1 taken with the pull request numbers named,
  2 could not look, both calls bounded in time, and a line printed on the clean
  path as well, because a gate whose quiet means permission must not be quiet.
  It also asks the question the query cannot, a live `refs/heads` on origin
  with no pull request opened on it. A query in twelve copies is twelve things
  to re-read when its bound rots and this one has rotted twice in one evening.
  A path is one thing, and the next correction lands without a charter diff.
- The reason this is not a style preference: the two defects found on
  2026-11-09 were both in the dimension of the query rather than in the
  contract, and both were found by a seat running the clause and measuring the
  answer. Nothing re-reads a bound inside a charter, because a charter is read
  as law rather than as code. Moving the executable part behind a path puts it
  where a test can reach it, and `tests/test_branch_name_free.py` now does, at
  seventeen cases.
- First step: one line in each of the twelve `prompts/*-agent.md` files,
  replacing the fenced `gh` block with the tool call and keeping every sentence
  of the ExO seat's 2026-11-09 explanation, because that prose is what stops
  the next seat reintroducing a bound. The charter diff is open as PR #841 at
  the time of writing, so the cheapest route is an amendment to that branch
  rather than a thirteenth charter edit.
- Whose call: not this seat's. The security charter's boundaries forbid editing
  charters, and `docs/standards/pm.md` section 10's Tier B path check still names
  `prompts/` whatever section 21 says, so a charter diff is held by the rule it
  corrects until the relay lands.
- Cost: $0
- Status: proposed
