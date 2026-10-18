# The generator outgrew its budget, and the gate was right

Writer seat, seventh run of 2026-10-18. Triggered by three failed workflow
runs on this seat's own branch, not by the daily cadence.

## The single biggest finding

The generator prompt has grown every day since it was written and has now
hit a hard cost ceiling. Nothing in this seat's loop ever looked at its size.

```
FAIL the cost is under the $0.15 ceiling ADR-32 implies: $0.1519 an issue against $0.15
```

That assertion is `tests/test_press_resilience.py`, it ran three times on
`alexandria-writer/2026-10-18-message-payload-audit`
(39104702728, 39104759569, 39104867224), and it failed identically each time.
The sixth run of 2026-10-18 added 2,056 tokens of field-map rules to
`prompts/digest.md`. Main was already at $0.149996. The prompt crossed the
line on this seat's own commit, and the gate caught it on the first push.

The gate is right and it is not raised. The test says so in its own words:
"Raising the ceiling is a finance decision and belongs to the owner: a
ceiling quietly raised to fit the current number is a ceiling that has
stopped being one."

## What the growth actually looks like

Measured by replaying every commit that touched the file.

| date | prompt tokens |
|---|---|
| 2026-09-08 | 680 |
| 2026-09-19 | 4,513 |
| 2026-09-26 | 19,432 |
| 2026-10-05 | 29,141 |
| 2026-10-17 | 36,689 |
| 2026-10-18, before this run | 38,745 |

101 commits have touched the file. Nine of them subtract anything at all, the
largest of those is a merge artifact rather than a deliberate cut, and the
file has never once been edited down on purpose. The charter is the reason,
and it is not a bug in any single run. Step 3 says to translate every failed
grade into the smallest prompt change that would have prevented it. There is
no step that removes one. A loop that only adds reaches a wall on a date
nobody picked, and today was the date.

## What this run did about it

Cut 2,227 tokens out of `prompts/digest.md` under one named principle: the
generator does not need the case history of its own rules.

The file had accumulated a running account of how each rule came to exist.
Dated references to past prints, tombstones reading "a specimen stood here
and is deleted", and narration of which gate failed on which issue. Those
sentences are notes this seat left for the next editor, and the press pays
$0.95 a million tokens to read them before writing anything. The rule is what
the generator acts on. The history belongs in this directory, where it
already is.

Every operative clause survived. Where a case was load-bearing, the failure
shape stayed and the date went: "an issue that opens on the citation pattern
shifting and makes 'moved from 2 to 4 citations' its main clause" says
everything "the print of 2026-10-05 carried a block whose subject was the
count" said, in a third of the words, and it says it about any issue rather
than about one Monday.

Two cuts are craft rather than budget and would be right at any price. The
no-specimen principle was written out five times in one file, three of them
inside 130 lines. The colon repair was written out three times. An editor who
fails an issue for the same connective used twice does not get to say one
thing five times in the prompt that writes it.

Net effect: the file is now 36,518 tokens, which is 171 tokens smaller than
main, and it carries the 2,056 tokens of field-map rules the sixth run added.
The checks are green.

## The part that is not fixed, stated plainly

The margin is 179 tokens.

That is not a fix, and the next writer run re-reds this branch. The median
writer run adds about 400 tokens and the big ones add two thousand. This
seat spent a full run cutting 2,227 tokens of genuine waste and bought back
179 tokens of headroom, which is the measurement that matters more than the
cut itself.

The arithmetic says why, and it says the prompt is the wrong place to balance
this budget.

| term | cost | whose |
|---|---|---|
| output reservation, 24,000 tokens | $0.0960 | the press, raised 4x on 2026-09-24 |
| the generator prompt | $0.0347 | this seat |
| worst-case payload | $0.0192 | the distill caps |

The reservation is 64% of the cost. Deleting the entire generator prompt, every
word of it, lands at $0.1152, still 2.3x the $0.05 ADR-32 booked. The writer
seat cannot hold this ceiling by writing less, and a seat that keeps trying
will cut gates to make a budget, which is the wrong trade for the product and
is not this seat's call to make.

So the structural work goes where it belongs. Two ledger entries, one
incident, and no further trimming of rules by this seat without the owner
saying which gates she is willing to lose.

## Against the registers

`docs/voice/taste.md`, first, line by line. This run produced no reader-facing
copy and printed no heading, so the 2026-09-19 framework ruling and the
2026-09-29 site-copy rulings are not engaged. The rulings this run could
break are the ones about the generator's own text, and the cuts were checked
against them: no framework name was introduced into a slot, no specimen was
added anywhere near a position where writing happens, and three specimens
were removed from such positions, which is L-A23 in the direction it wants.

`docs/voice/canon.md` and `docs/voice/ban-list.md`: this file was swept. No
em dash, no semicolon join, no entry from the list.

`docs/voice/value.md` and `docs/voice/preferences/`: not engaged, no copy
this run.

`docs/standards/lessons.md`, the `any` section. There is no writer section.
L-A22 is the finding of this run almost word for word, and it is quoted in
the ledger entry rather than here.

## The grade this run did not run

The charter's steps 1 and 2 grade the newest issue against the ten laws. The
sixth run of today already did that, in
`docs/voice/reviews/2026-10-18-payload-audit.md`, against the same issue.
Grading it twice in one day would be a second opinion from the same reader,
which is not evidence. This run graded the generator instead, which is what
the trigger asked for and what was actually broken.
