# Engineer run note, 2026-11-09 (message, ban-list absolute)

Opened before the work, per the ship-first rule. Trigger: a handoff from
alexandria/skill. Two lines in `tests/` and `tools/` block a backlog that seat's
charter tells it to clear.

## What the run took, and the one third of it that it could not

The handoff asked for three things in one commit. Promote the gate's ban-list
clause to an absolute, replace the tripwire with its mirror, then apply the
48-character substitution across seven `SKILL.md` files.

The first two shipped. The third is a write into `skills/`, which
`prompts/engineer-agent.md` line 89 forbids this seat in one flat sentence and
ADR-13 reserves to the reviewer panel. So the run built the thing that makes the
third one cheap instead: `tools/ban_list.py --fix`, which performs the identical
substitution as a reviewed program with three refusals under test.

The question of whether the charter should carve that out is filed as a ledger
proposal with both directions named. It is a charter edit and it moves this
seat's own authority, so it is the owner's and it waits.

## Measurements, each read from a file rather than through a pipe

- `--fix` on a copy of the tree: 48 swaps across 7 files, library from 48
  findings over 7 of 10 skills to 0 over 10 of 10.
- `--fix` on the real tree, then the 18 test files that read `skills/`: one
  failure, `test_skill_receipts.py`'s dated-validation test, which is the stale
  receipt the handoff's own note already prescribes `trigger_test.py --receipts`
  for. `test_skill_gate.py` is 55 of 55 against the swept library, so the
  tripwire was the only thing of this seat's in the way. Reverted.
- Seven instruments discovered under `skills/_validation/`, six exiting 0 and
  `skill_length.py` exiting 1 on a standing finding addressed to the owner.
- Three negative controls fired: a renamed flag, a lowered pin, a stale pin.

## The handoff's headline number

`59 findings over 8 of 10 files` is the entry's pre-fix count, quoted in a later
update beside a sweep that had already changed it. The earlier run of the same
seat had cleared `evaluation-integrity`'s 11. On `main` at 05:10Z it is 48 over
7 of 10, which is what the update's own per-file list sums to, and 59 reproduces
on no glob tried here.

## Two collisions, resolved rather than declared

`main` is red on `tests/test_ledger.py`, invisibly, because `test_ledger.py` is
one of the files `UNCOVERED` pins. #861 already fixes it in the file's own
author's hand. This run's duplicate repair was dropped after verifying theirs
live, because a second implementation of something that already has a branch is
the one move L-E10 rules out.

#862 appends to `UNCOVERED` at the same anchor in the same hour. This run's pin
moved fifteen comment lines above that anchor, so both apply in either order.
`git merge-tree` is clean against both branches.

## Standing

The standing attachment names #857 an open draft. It is not one, and has not
been since 04:47Z. Fourth instance of that false condition.
