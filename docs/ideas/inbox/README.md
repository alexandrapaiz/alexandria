# The ledger's inbox

One file per entry. Write `YYYY-MM-DD-slug.md` here instead of appending to
`docs/ideas.md`, and your filing cannot collide with another seat's.

```bash
python3 tools/ledger.py --inbox-new the-thing-you-observed --title "what it is" --seat engineer
python3 tools/ledger.py --inbox
```

`--inbox` is the gate, and `--check` runs it too, so a seat that only ever runs
the register's own check still gets it. It fails on a conflict marker, on a
filename that is not `YYYY-MM-DD-slug.md`, on a heading and a filename that
disagree about the date, on two entries in one file, on an entry already in the
register, and on an unfilled `<...>` placeholder left over from the skeleton.

Whoever merges folds the inbox into the register on the mainline, where there is
one author and one snapshot:

```bash
python3 tools/ledger.py --fold            # what would move, and the invariant
python3 tools/ledger.py --fold --apply    # move it
```

A fold opens its own `## Folded from the ledger inbox, YYYY-MM-DD` section. That
is not decoration. This register nests an entry as a `### ` inside a `## ` run
section, so an entry appended bare at the tail joins whichever seat's run
section happens to be last, and a register that files one seat's entry under
another seat's run is worse than one that is hard to merge.

## Why this exists

`docs/standards/lessons.md` L-A18, amended 2026-10-18, named the registers that
still appended at a shared anchor and called them "the same defect waiting." The
incident register stopped waiting on 2026-10-24 and got
`docs/agents/incidents/inbox/`. This one did not, and the law never named it,
because "this file" in that sentence is HQ's lessons register rather than ours.

So the ledger was named by measurement instead. `python3
tools/anchor_contention.py --fetch` on 2026-11-09 read `docs/ideas.md` as the
highest-contended path on the engineer seat's own surfaces with no inbox beside
it, and the merge that opened the run which built this conflicted here, at this
anchor, for the second time in two days. That report finds this directory
without being told about it: a `<path>/inbox/` implies the register `<path>.md`
beside it, so the pair appeared in the measurement the day it existed.

## What has not changed

The entry contract is the one printed at the bottom of every charter: a
`### YYYY-MM-DD - name` heading, then `Trigger`, `What`, `First step`, `Cost`
and `Status`. The statuses are still the owner's. Only `proposed` and `urgent`
can be the status of an entry arriving for the first time, because `accepted`
and `rejected` are hers and `built` is a move on an entry that already exists.

Folding is pure movement and never renaming, because an entry's identifier is
its own date and name rather than a count. So a missed fold loses nothing, and
`--check` does not demand an empty inbox unless you ask it to with
`--require-folded`. A gate that can turn `main` red over a bookkeeping step
nobody promised to run is worse than the collision it set out to fix.

Entries already in `docs/ideas.md` stay there. Nothing was migrated, and every
citation of every existing entry still resolves.
