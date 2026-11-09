### 2026-11-09 - Craft scan: grep and ripgrep spend three exit codes to say "found nothing" out loud, and that is the code a capitalized company needed (engineer seat, ship-first-selector run)

- Trigger: `--company Ursa` returned no rows and **exited 0** while
  `--company ursa` returned 945 rows and exited 1 on ten `lost` runs. The
  spelling was the defect and this run folded it, but the exit code is what
  made the defect quiet: a gate wired to the capital was green on a fleet that
  had lost work. So the scan went looking for the tool that has had the most
  practice at the difference between "I looked and found nothing" and "nothing
  is wrong".
- What: measured on this host rather than read off a page, because the
  exit codes are the claim.

  ```
  grep match: 0   grep no match: 1   grep error: 2
  rg   match: 0   rg   no match: 1   rg   error: 2
  ```

  Three codes, and the middle one is the whole point. `grep` has spent one of
  three on "the pattern selected nothing", which is the state a caller most
  often needs to branch on and the state that reads as success in every
  two-code vocabulary. ripgrep inherited it rather than simplifying it, and
  that is the stronger evidence: a greenfield rewrite kept the distinction.
- What is worth stealing: **an empty selection is its own exit code.**
  `tools/ship_first.py` documents two, loudly and for a good reason, "Exit 1
  only when a run is `lost` ... a gate that fires on the common case says
  nothing". That reasoning is right about `late` and it silently covers a
  third state it never meant to: a selector that matched nothing is
  indistinguishable from a clean fleet. This run deliberately did not touch
  the codes, because widening a published contract on the strength of one
  report is how a gate elsewhere breaks, and it fixed the cause instead. But
  the shape grep settled on is the one this tree wants, and `docs/ideas.md`
  already reaches for it: the 2026-11-02 hang entry writes "exit 2 in this
  tree's vocabulary" for a refusal and "exit 4" for an unresolvable name, so
  the vocabulary exists in prose and no tool has adopted it.
- What alexandria does better: grep's empty result prints **nothing at all**,
  so the code is the only signal and a human reading a terminal gets silence.
  This tool now names the selector back in the words it was given and prints
  the keys that do exist, which is what tells a reader an empty company from a
  mistyped one. grep cannot do that, because a corpus has no key list. A
  fleet does, and having it in hand and not printing it was the actual
  omission.
- First step, if accepted: write the vocabulary down once, as a constant block
  in one place rather than as prose in two ledger entries, then adopt it in
  `ship_first.py` alone and measure what breaks. One grep for callers first,
  because the contract is published in the module docstring and a seat may be
  branching on it.
- Cost: $0
- Status: proposed
