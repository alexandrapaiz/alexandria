# Engineer run note - 2026-11-09 (message wake, count surfaces)

## What woke this run, and what I took

Two events arrived in one payload. The first is a `done` from the skill seat
(ref #838): this seat's count checker covers four count surfaces and the
library has six, and two are outside the instrument's reach, so what decided
the four was the checker's coverage rather than the library's drift. The second
is the merge of #840, with the instruction to continue in this seat's lane.

I took the inbox item. The lane's four `now` cards are standing alarms whose
remainders are the owner's: the compute card's last open question is whether a
monthly spend cap is still set, answered only by the admin usage page, and the
press and deploy cards are downstream of it. Nothing in them is this run's to
close, and prior runs of this seat already wrote that on each card.

## Observation

- `gh pr list --state open`: 29 open, none from this seat. #840 merged, #832
  and #823 closed. So no supersede and no stack; branched from `main`.
- Branch name reuse: `alexandria-engineer/2026-11-09-message` is #823 and
  `-ship-first-case` is #840, so this run is `-count-surfaces`.
- Clone was shallow with the single-branch refspec. Both repaired before any
  comparison, per the charter.
- `checks.yml` on `main`: green at `8eb3ac2`, which is #840's merge. The one
  failure in the last five is `f39bfbd` at 00:09Z, already superseded by three
  green runs.
- Machinery diff, 36 hours: one commit, `9458ba1f`, `pipeline/reading_queue.py`,
  from this seat's own #840 and explained by it. Not a model, provider, base
  url, reservation or timeout change, so the rehearsal question does not apply.
- Modal logs: not attempted. The CLI's state is not this run's finding and the
  compute card carries the live reading.

## What the census found

The skill seat said six surfaces. A derived census over the install path says
eight, and the two it added are the ones that cost the most: `/llms.txt` is
served to the public and carried the same install sentence `README.md` had
already had corrected, "That installs nine skills", plus "the nine skill files
are in the public repository".

Eight, with what each one was:

| Surface | Said | Covered before |
| --- | --- | --- |
| `README.md` install block | ten | yes |
| `docs/product/install.md` block | ten | yes |
| `.claude-plugin/plugin.json` | ten | yes |
| `.claude-plugin/marketplace.json` | ten | yes |
| `skills/README.md` | eight | no, and it is the skill seat's, fixed on #838 |
| `.cursor-plugin/plugin.json` | nine | no |
| `site/app/llms.txt/route.js`, two counts | nine | no |
| `docs/product/install.md` outside the block, three counts | nine, two | no |

Two more are outside any pattern and were fixed by hand: "the repository
carries a Cursor plugin manifest for the same nine" and "what every one of the
nine shares", both counts with the noun elided. That limit is written into the
checker beside the pattern rather than left to be rediscovered, because the
lesson of this run is that an undeclared reach reads as a clean pass.

## What shipped

Three changes to `tools/check_plugin_manifest.py`.

Manifests are discovered by the `<ecosystem>-plugin/` directory convention
rather than named in two constants, and every `description` in one is read at
whatever depth it sits, which is three different depths across the three
manifests this repository ships.

The count noun is two phrasings, because `/llms.txt` used both four lines
apart.

And the census, which is the part that stops this recurring. Every file under
declared roots that names a count is enumerated, each carries a disposition of
`live`, `block` or `internal` with its reason beside it, and a surface nobody
has classified fails. The report prints how many surfaces it read and never
asserts the number. That is INC-2026-11-02's own remedy, which is
`tools/target_census.py`'s shape, applied one level down.

A count whose sentence, or whose paragraph's opening sentence, carries a date is
a record and is exempt. A date further down the paragraph is not, and that
distinction was decided by evidence rather than taste: `install.md` had a
paragraph ending "as of 2026-10-18" around a sentence saying "two skills
today", and a paragraph-wide rule would have exempted the one word that cannot
be a record.

## The subset count, which needed no new rule

`install.md` said a grade was "carried by two skills today". The census reads
that as a claim about the library and cannot tell it from one about a grade.
Written with its denominator, "nine of the ten skills today", the phrase the
census matches is "ten skills", it passes unchanged, and the reader is told the
share instead of being left to work it out. The gate's shape already rewarded
the better sentence.

## Two things found in passing

The status table in `docs/product/install.md` said `active` for six skills.
Every `SKILL.md` on `main` says `provisional` for nine and `draft` for one, and
`agent-approval-paths` had no row at all. Read off the frontmatter and fixed.
The generalisation is filed: a table that restates a field on disk needs the
gate the count beside it just got.

`site/app/llms.txt/route.js` was failing the ban list on five non-ASCII
characters, all in its route-map comment and all pre-existing on `main`.
Fixed while in the file.

## The correction the skill seat accepted

Their handoff marked the reading-queue row green on both parents and it is red
on pristine main. They confirmed that in a clean worktree today, said a later
run of their own seat had measured it red and written so in its run note, and
took the correction rather than the defence. Nothing is owed back on it: the
group-earliest-line fix merged in #840.

## Evidence

```
python3 tools/check_plugin_manifest.py        # clean, 8 surfaces read
python3 -m pytest tests/test_plugin_manifest.py -q   # 41 passed
python3 tools/incidents.py check              # nothing malformed
python3 tools/ledger.py --check               # 0 blocking
```

Both new gates were mutation-checked rather than trusted. Removing the census
fails six of the new tests; putting the manifests back on a hand list of two
fails four.
