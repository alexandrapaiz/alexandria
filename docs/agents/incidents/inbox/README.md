# The incident register's inbox

One file per incident. Write `INC-YYYY-MM-DD-slug.md` here instead of
appending to `docs/agents/incidents.md`, and your filing cannot collide
with another seat's.

```bash
python3 tools/incidents.py new --slug the-thing-that-repeated --date 2026-10-24 --seat engineer
python3 tools/incidents.py check
```

`check` is the gate. It reads the register and this directory together, and
it fails on a conflict marker, on a filename that does not match the id in
its own heading, on two entries in one file, on an id already in the
register, and on a new collision among the register's legacy numbers.

Whoever merges folds the inbox into the register on the mainline, where
there is one author and one snapshot:

```bash
python3 tools/incidents.py fold --apply
```

## Why this exists

`docs/standards/lessons.md` L-A18 names this register by path as one of the
two that still lack the inbox HQ built for decisions on 2026-10-18, and
calls them "the same defect waiting." The wait ended on 2026-10-24, when
the anchor collided three times in one day: once merging #462 into #475 in
this very file, and four times across the PM seat's nine sibling branches
in `docs/sprints/pending.md`.

The defect is positional rather than semantic. Every seat appends at the
end of the file, so two seats filing between merges conflict on the second
merge however correct both entries are.

## What has not changed

The standing rule still governs what gets filed: any issue occurring more
than once, anywhere in the org, is recorded the moment it repeats. The id
scheme is still `INC-YYYY-MM-DD-slug`, taking the date the incident was
observed, never a sequential number.

Folding is pure movement, never renaming, because these ids allocate
themselves from a date and a subject. So a missed fold loses nothing and
`check` does not demand an empty inbox unless you ask it to with
`--require-folded`. A gate that can turn `main` red over a bookkeeping step
is worse than the collision it set out to fix.

Entries already in `docs/agents/incidents.md` stay there. Nothing was
migrated, and every citation of every existing id still resolves.
