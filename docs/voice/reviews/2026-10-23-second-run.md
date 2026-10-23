# The generator was carrying four blocks of its own text twice, and one of them left a slot open to the end of the file

**Writer run, 2026-10-23, second run of the day. The artifact graded is
`prompts/digest.md` itself, and the issue it wrote,
`site/content/issues/2026-W39.md`, is graded against it.**

## The biggest weakness, stated first

The file this seat exists to evolve had four blocks of edit damage in it, on
main, and no gate in this repository could see any of them.

Two rule bullets, one slot instruction and one single line were each written
in beside the copy the file already held. Three of the four first copies end
in the middle of a sentence, which is what says how it happened: edits that
inserted replacement text and did not remove what it replaced.

One of the four matters far more than the other three. The duplicated slot
instruction opened a second curly brace, so the template's brace depth never
returned to zero after line 1145. **Every slot from the reading list to the
sign-off sat nested inside an instruction block that never closed**, in a file
whose own line 502 tells the model that text in braces is an instruction to it
and is replaced by its own words. The closing line law 10 requires, the one
that must print verbatim and last, was inside that unterminated block.

Nothing was red. No conflict marker, no failing test, no gate. The weighing
gate measured the file's cost and passed it. The taste gate found every one of
her rulings present in it. The enforcements command verified forty-six quoted
anchors inside it. All three were reading a file that disagreed with itself
about where its own instructions ended.

## How it stayed invisible, which is a fact about the gate and not the file

`tools/check_registers.py` exists for exactly this damage. It was built on
2026-09-24 after `docs/agents/incidents.md` was found carrying two verbatim
copies of two of its own entries, from, in that file's own words, "a merge that
appended entries the file already held."

Its list of files has grown to sixteen, and the criterion for being on it is
written in its own comment: not that a file is famous, but "that more than one
seat appends to it, because that is what produces the anchor contention
incidents 6, 25 and 29 are all made of."

`prompts/digest.md` is not on the list. It is the single most-appended file in
this seat's custody and the one the product's whole output passes through.

And the checker would not have caught this damage even with the file listed,
which is the sharper half. Its damage test is `CONFLICT`, seven characters of
git marker at the start of a line. The 2026-09-24 incident was not a conflict
marker either. It was clean duplicated text, and the gate built in response to
it catches the loud form of that failure and never the form that caused it.

So the repeat is filed, and it is filed against the gate rather than against
whoever made the edit.

## The four blocks, named with their lines as main carried them

| lines | what was doubled | state of the first copy |
|---|---|---|
| 1140 and 1145 | the reading-list slot's opening, five lines | complete, and it opens the brace that never closes |
| 1946 and 1949 | the count gate's worked case, three lines | cut at "Nothing there was a" |
| 1966 and 1967 | "just counted, which is the next paragraph." | complete |
| 2026 and 2036 | the attribution gate's bullet, ten lines | cut at "every one of those sentences is telling the" |

The pair at 1946 is the one that says which copy to keep. The first says "One
section of 2026-09-28 failed this three ways at once" and the second says "One
section failed this three ways at once", so the second is the trimmed version
from a run spending the weighing gate's own rule that dates are this seat's
notes to the next editor rather than instructions to the model. That trim
wrote the new sentence in and left the old one standing, truncated. The
repair keeps the trimmed copy, which is what the trimming run intended.

Nineteen lines removed, no operative clause among them. Brace depth returns to
zero. `enforcements` and `sweep` report byte-identical results before and
after, so no quoted enforcement anchor moved.

## What it cost per issue, which is the part with a number on it

The generator sits **$0.0021** under a per-issue ceiling that
`tests/test_press_resilience.py` fails the build over. That is the margin the
whole seat has to work in, and the duplicated text was being bought at the
primary model's input price on every single send.

**34,364 tokens to 34,043, and $0.1479 an issue to $0.1476 against the $0.15
ceiling.**

The headroom went from $0.0021 to $0.0024. The saving is small in money and it
is 14% of the only margin that exists, and none of it was ever buying a rule.

## The instrument: `python3 docs/voice/check_voice.py generator`

Three detectors, and the reason this is a command rather than a note is that
not one of them is a prose judgment. They are arithmetic on the file.

- **A run of lines the file carries twice in a row.** Not any repeated line.
  Two slots of this generator legitimately end on the same wrapped
  cross-reference three hundred and sixty-four lines apart, and a check that
  counted repeated lines would call that damage. What is damage is a run that
  appears twice with nothing between the copies, because the only way to write
  that deliberately is to mean it twice running.
- **A curly brace that never pairs.** Reported with the line that opened it.
- **A line ending mid-clause with a new block on the line under it.** This is
  the tell of the first copy whose tail was replaced, and it is the only one of
  the three that would have caught the pair at 1946, because those two copies
  are not identical and the duplicate detector correctly says nothing about
  them.

### Proved by breaking it, and the fixtures are named

The ledger entry this seat filed this morning asks for a charter line
requiring exactly this, so this run follows it before anyone has ruled on it.

| artifact | what it holds | exit |
|---|---|---|
| `prompts/digest.md`, repaired | nothing | **0** |
| `/tmp/gfx/clean.md` | a slot, a bullet, a heading, no damage | **0** |
| `prompts/digest.md` as main carried it | all four blocks | **1**, and it names all four with line numbers |
| `/tmp/gfx/dup.md` | two lines written twice in a row | **1**, duplicate detector alone |
| `/tmp/gfx/brace.md` | one slot opened and never closed | **1**, brace detector alone |
| `/tmp/gfx/damaged.md` | one bullet cut mid-clause before the next bullet | **1**, truncation detector alone |

Green is reachable, the real artifact's real damage is caught, and each
detector is proved on a fixture holding only its own defect, so a pass on one
cannot be standing in for the others.

### Four false positives, found by building it, and they are the whole craft of it

The first cut of the truncation detector treated any line starting with `{` or
a capital letter as a new block. It reported four findings on the repaired
file, and all four were ordinary prose wrapping across a line:

- Line 501 ends "Everything in" and line 502 begins "{curly braces} is an
  instruction to you". A `{` at the start of a line can continue a sentence,
  which this file proves in the sentence that explains what braces mean.
- Two lines wrap before an emphasised run of capitals: "every heading that
  reaches the reader is / WRITTEN FRESH", and "the sentence is about the
  reader's work in the / PRESENT TENSE".
- One wraps inside an open quotation: `attributed by INSTITUTION first
  ("researchers at / Tsinghua and Moonshot AI"`.

So three exclusions, and the detector is worth nothing without them. A run of
capitals on the next line is emphasis and therefore a continuation. An
unbalanced parenthesis or an odd number of quotation marks means the sentence
is mid-quotation. And `{` comes out of the restart pattern entirely, because
the duplicate and brace detectors already catch a doubled slot and the
truncation detector cannot tell a slot from a sentence.

This is the third run in a row where the defect worth writing down was in the
gate rather than in the artifact, and the general shape is the same each time:
**a check that asks whether the right kind of thing is nearby will pass on the
artifact that has it nearby and means something else.** Entry 129 wrote that
sentence yesterday about a defining clause. Entry 130 writes it today about a
line break.

## The ten laws, one verdict each, against `site/content/issues/2026-W39.md`

The press has printed nothing since 2026-10-05, so this is the same artifact
the grade of eighteen hours ago read, and the honest thing is to say which
verdicts are re-measured by command and which are carried. Figures from
`check_voice.py measure site/content/issues/2026-W39.md`, re-run today: 1,105
words, 27 paragraphs, longest 141, four over 100, em dashes 0, semicolons 1,
non-ASCII 0, shapes 2, links 4.

1. **Plain sentences, no em dashes, no semicolon joins.** FAIL, one count,
   re-measured. Zero em dashes and one mark joining two finished sentences:
   "RMBench measures end-to-end agent construction on software tasks; the
   air-combat result measures win rate in a physics simulator."
2. **No buzzwords, every line targeted.** PASS, carried.
3. **Sell the product, never the recipe.** FAIL on the standing line, carried:
   the masthead reads "read in full and distilled weekly", which is law 15's
   own specimen, and it is filed as the owner's call because the line is
   spliced in before storage.
4. **The headline is a finding.** FAIL, carried. "Harness distillation without
   the harness at runtime" is a finding stated in two words the reader cannot
   define, so law 4 passes and law 12a fails on one line.
5. **Relevance is impact, and every ranking says what earned its slot.** FAIL,
   carried: "The strongest compounding evidence this week sits on the boundary
   between training and deployment" is a slot name used as an adjective.
6. **Evidence grades in-line.** FAIL by count, carried: three of six named
   works graded, and two of the three ungraded print a number each.
7. **Honesty serves items, never the method.** PASS, carried. The grades it
   does carry are about the work.
8. **Links reach the full text.** PASS, re-measured. `check_voice.py links`
   reports six of six on `arxiv.org/html/` with no version suffix.
9. **The fine-tuned instruction is the foundation.** FAIL, and this is the
   verdict this run changes. Every previous grade read this law against the
   issue's structure and passed it, and the structure does hold: context
   first, institution-first attribution, her four sections in her order. This
   run read it against the instruction instead, which is what the law is
   actually about, and the instruction was carrying her own text twice with a
   slot left open to the end of the file. A base layer that disagrees with
   itself about where its instructions end is not a foundation, however well
   the issue it produced came out.
10. **"Accelerate every builder and agent to frontier speed."** PASS, carried,
    verbatim and last.
11. **Length follows the news.** PASS, re-measured. 1,105 words on three
    findings.
12. **Framework names never print.** PASS on the strings, re-verified by grep,
    FAIL on the idea through law 5's specimens.
12a. **The outsider test and the density rule.** FAIL, re-measured by command:
    `check_voice.py firstuse` reports 24 terms of art against the generator's
    cap of five, 22 of them bare, two of them in the title. Density passes on
    the paragraph figures and fails on the shape count, which is 2.
13. **Every issue stands alone.** FAIL, carried. "You have spent the week
    watching agents get faster by thinking less at test time" is her rejected
    sentence of 2026-09-24 reworded.
14. **The issue is enjoyable, and formatting is how it gets there.** FAIL,
    re-measured. Shape count 2 in 1,105 words, no list anywhere, which is the
    formatting she asked for by name.
15. **The library never claims to have read what it only ingested.** FAIL on
    the masthead, same filing as law 3.
16. **A used title is not a title.** PASS, carried.

## The registers, checked before shipping and not after

**`docs/voice/taste.md` first, ruling by ruling.** `check_voice.py taste`
reports 31 rulings, 27 enforced and quoted, three unenforceable by any file,
one replaced, and one FAIL. The FAIL is verdict 6 of her 2026-09-29 site
ruling, never "read" for ingested, red because `reading` is red on four live
surfaces, unchanged and blocked on candidates that have been open for five
days and twenty-seven days.

Her ruling of 2026-09-27 binds this run's own output and was checked against
it: codes are never owner-facing, so nothing in this file's pull request
description names a decision or an incident by its number.

**`docs/voice/ban-list.md`.** Entry 130 is appended in this pull request. No
entry is deleted, which needs her word.

**No reader-facing copy in this run**, so `value.md`, the newest preference
file and `quality-claims.md` have no artifact of this run's to gate. Checked
rather than assumed: `check_voice.py candidates` counts the one file this
branch adds under `docs/voice/`, which is this review, and reports that it
redrafts none of the seven surfaces awaiting her word. The nine rows in
`docs/voice/awaiting-her-word.md` are untouched. The surfaces that need her
ruling needed it before this run, and drafting a tenth candidate for a surface
that already has an open row is the mistake that register was created to
stop.

**`docs/standards/lessons.md`** has no `writer` section, so `any` binds.
`L-A21`'s last clause, every gate tested against an artifact known to fail it
before the gate is trusted, is the table of six fixtures above. `L-A39`, a
check that tests for presence answers a different question, is the class all
four false positives fell into, and it is why they are in this review by name
rather than fixed quietly.

**The repeat is registered.** `INC-2026-10-23-the-generator-is-not-on-the-list-of-files-checked-for-edit-damage`
is appended in this pull request, against the standing rule that an issue
occurring more than once is recorded at the moment it repeats.

## What this run did not fix, and what it is handing on

**The checker's list is not this seat's surface.** Adding `prompts/digest.md`
to `REGISTERS` in `tools/check_registers.py`, and widening its damage test
past the git marker to the duplicated block, are the engineer's edit. Filed in
the ledger with the measured finding rather than argued for.

**The wiring, for the fifth time.** `generator` joins `enforcements`, `sweep`,
`taste`, `candidates` and `firstuse` as a command that reads a register
against a file and is called by nothing. The difference is worth naming: this
one is green today on a repaired file, so unlike `firstuse` it can go into
CI immediately without reddening a build over a file nobody can edit. That
makes it the cheapest of the six to wire and it is in the ledger as such.

**The ban list already knew.** Entry 61's own sentence is that a string which
never changes is never graded. The same sentence is true of a prompt. The
generator is read by a model every send and by a person roughly never, and the
canon's own count of this file is 101 commits in forty days with nine of them
subtracting anything, which is exactly the condition entry 61 describes. What
was missing was not the idea. It was a command.

**The press is still silent.** Nothing has printed since 2026-10-05, which is
eighteen days. This seat can improve the generator and cannot observe it, and
the repair in this pull request is the first change in weeks whose effect does
not need an issue to be visible, because the damage was in the file rather than
in the prose.
