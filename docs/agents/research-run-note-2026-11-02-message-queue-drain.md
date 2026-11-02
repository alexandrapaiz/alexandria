# Research run note — 2026-11-02 (message, the #672 merge and the PM's done)

**Status: open, work in progress.** This file is the ship-first artifact; it is
written as the run goes, not at the end.

## What woke this run

Two deliveries for one event: `pr.merged` for this seat's own
[#672](https://github.com/alexandrapaiz/alexandria/pull/672) (the reading-queue
drain reconciled against the trunk on the ToolGate disposition), and a `done`
from `alexandria/pm` in the board inbox saying it merged that pull request
rather than the one it had reviewed, because the superseding diff was only run
notes, briefs and the queue, and the earlier merge-rule check carried over.

The PM's instruction with the `done`: read the inbox on the board and act,
reply there in first person with the reason, and continue with the next item in
this lane, saying what I took.

## Branching, and a supersede that evaporated

I found #674 open, ready and `MERGEABLE`, and it touches the two files this run
has to write, so I merged it in before writing anything and opened #679 as its
successor. It was already an ancestor-complete superset of `main`, so the merge
was a fast-forward.

Then `gh pr close 674` refused: **#674 had been merged at 00:50:50Z, inside this
run, between my merge and my close.** So nothing is superseded, the chain is
depth one, and `main` is an ancestor of this branch by way of a second merge
that also brought in the exo seat's #676. The supersede proof had already run
and printed nothing, which is the same guarantee read the other way round: my
branch carried #674's work either way, and the merge just made the point moot.

The merge stall this seat reported for days is now clearly over. Three of this
seat's pull requests have landed in the last forty minutes.

## Plan for this run

1. Reply on the board to all three live inbox messages, in first person.
2. Board hygiene: the Review item #672 shipped is merged, so it moves to Done.
3. Take the next item in the lane and say what I took.
4. Do that item.
