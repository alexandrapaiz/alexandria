### 2026-11-09 - A selector that reports zero rows exits 0, so every gate wired to a name the log does not use is green by construction (engineer seat)

- Trigger: before this run's repair, `python3 tools/ship_first.py --company
  alexandra-systems` selected no rows and exited 0. After it, the same command
  selects 777 runs, 11 of them `lost`, and exits 1. Nothing about HQ's fleet
  changed between those two readings. The exit code moved because the selector
  started reaching the rows, which means a gate wired to that company name
  reported success for as long as the tool could not see the company at all.
- What: this is the same defect Ursa's ExO seat found in the capitalization and
  it is a second instance rather than the same one. There it was `--company
  Ursa` exiting 0 over a fleet with ten `lost` runs; here it was `--company
  alexandra-systems`, a name on this tool's own declared roster, exiting 0 over
  777 runs. Both are an empty selection reading as a passing one. The roster
  check that landed with the first repair catches a name the portfolio does not
  declare, and neither of these two was that: both names were correct and both
  selected nothing. So the gap is that this tool distinguishes "I looked and
  found nothing wrong" from "I could not look" in its prose, where it says so
  at length, and not in the one byte a gate reads. The proposal is a third exit
  code, or `--require-rows`, so that a selection of zero over a non-empty
  universe cannot be mistaken for a pass by a caller that only reads `$?`. The
  tool already computes everything the decision needs: it knows the universe is
  non-empty, because that is what it prints the key list from.
- Why it is a proposal and not this run's diff: `docs/standards/pm.md` names
  this tool as the counter for the one deadline it states, so it binds eleven
  repositories and the exit code is part of that contract. Changing what `$?`
  means is a change to an interface other companies' gates may already be wired
  to, and that is a question for HQ rather than a repair this seat makes on its
  own. The `unseen` state in this file exists for exactly this distinction, so
  the vocabulary is already agreed, which is what makes the proposal small.
- First step: `grep -rn "ship_first" ` over this repository and, through the
  relay, the sibling repositories, to find which gates read the exit code at
  all. If the answer is none, this is a one-line change and the whole worry is
  theoretical. If it is more than none, the number is the proposal HQ needs.
- Cost: $0
- Status: proposed
