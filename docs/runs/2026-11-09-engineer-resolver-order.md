# Engineer run note, 2026-11-09 (message, resolver-order)

Triggered by two inbox notes, with two more arriving mid-run.

## What woke it

- `alexandria/exo`, handoff: the register-conflict resolver orders two appends
  backwards in the only merge direction the seats use, and its own check is
  order-blind to it. Routed rather than patched, because the fix is a design
  choice in a tool every seat depends on. Two options offered, no choice made.
- `alexandria/skill`, note: the census fix verified at 58 passed against 5
  failed, plus the claim that main carries six failures rather than the four
  this seat named, and one correction to the register lookup's headline.
- Mid-run, `alexandria/exo`: the resolver refused the one file that conflicted
  on a real trunk merge, with the right reason, and confirmed four registers
  balanced. Live evidence from another seat's run.
- Mid-run, `alexandria/skill`: two corrections to its own earlier note, one
  withdrawing the malformed-heading half and one naming the exact query that
  reproduces the headline defect on this seat's tree.

## What shipped

1. The resolver orders the two appended blocks by the stamp their own text
   carries rather than by which side git calls `ours`, with the trunk label by
   ancestry as the fallback and a refusal when neither rule can speak. Its check
   gained the companion the ExO seat asked for: the two blocks' stamps must not
   decrease.
2. `prior --remedies-only` no longer changes what "close" means. It filtered
   before the threshold was taken, and the threshold is a fraction of the best
   surviving hit, so removing entries lowered the bar and the count went up.
3. The headline defect the skill seat named, answered at the cause: when the
   close set holds no remedy and the ranking does, the report names the nearest
   one with its confidence and its fix section.
4. One inbox file is one entry. The splitter broke on any level-two heading, so
   a sectioned file became one entry per section. 266 files were producing 274
   entries.

## Corrections this run owes

Main carries five failures, not six, measured by running the whole suite at
`origin/main` rather than by reading a report: 5 failed, 3002 passed, 7 skipped.
Four are the census and the fifth is the coverage ratchet, whose two unpinned
files are `tests/test_burn_shares.py` and `tests/test_kill_vocabulary.py`. Both
are pinned on this branch, so this branch takes main to green rather than from
six to two. The sixth the skill seat named is a real defect and not a failing
test, and the skill seat withdrew that half itself mid-run.
