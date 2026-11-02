# Writer run 59, 2026-10-26 (message): the PM's merge note, read and answered

The wake is one board message, `9ac58062-9bf8-486d-8f07-107c48c88546`, from
alexandria/pm at 20:45:45Z, and it is an answer to this seat's W42 overturn
ruling rather than a request for work. Read in full on the board rather than
from the wake's excerpt, which is the thing the note itself says it did in the
other direction. It carries four statements, and three of them needed something
from this seat.

## What the note said, and what each half was worth checking

**It agreed with the pull and merged #600.** Nothing owed. The reasoning it
gives is also right on the point every seat here keeps getting wrong: the diff
touched `prompts/digest.md`, which is a content prompt the press runs rather
than a seat's charter, so the hold that hangs over `prompts/` did not apply.

**It posted the correction-notice question to her as a formal ask.** Verified
rather than taken on report, which is the standing instruction after three
duplicate wakes on 2026-10-24. The ask is board message
`065eda95-92e7-4f94-8625-906c10691b81`, named in the PM's own #609, and it
carries this seat's recommendation and the hour the silence rule expires. Both
are now in the register row with the message id beside them.

**It is holding the site edit as an owed item** because the frontend seat's own
pull request, #559, is still open, and neither seat sets site copy. Nothing to
argue. The consequence for the register is that the row's defect outlives the
ruling by a day or more, and the row now says so and says which seat owes the
diff.

**It left the quality-claims rows and the masthead's overturn promise with the
ExO seat.** Correct, and this seat's own ruling routed them there. The masthead
constant in `pipeline/weekly.py` still recites the framework slots on every
issue the press sends, which is canon law 12, and it stays filed where it is.

## The grade, and why there is not one

The newest issue is still `2026-W42`. It has been graded by runs 51 and 57,
audited against its own cited abstracts by the research seat, and its overturn
section is ruled pulled. A fourth reading of one issue produces a second opinion
rather than a patch, so there is no failed grade in this run and therefore no
diff to `prompts/digest.md`. The generator's live change is still run 57's third
test at the fell-behind slot, and it is undeployed, so the generator's next
measurable move belongs to a deploy and not to another prompt edit. No ban-list
addition: this run read no new reader-facing artifact prose. No new copy
candidate, because `docs/voice/value.md` still carries no recorded approval and
that is the charter's precondition for a copy round.

What this run produced instead is the half of run 57's ruling that was still
only a recommendation inside an argument.

## The finding: a decision that reads as made and is not set anywhere

Run 57 ruled on four edits and wrote the fifth, the notice, as a quoted
recommendation inside a section arguing for it. The PM then put that
recommendation to her. So the sentence exists, the question is asked, and the
clock is running, and nothing anywhere says where the sentence goes on the page
or what it looks like when it gets there.

That matters because of who the next reader is. The frontend seat sets it, that
seat's run is visual, and the words are this seat's lane. Handed the candidate
as it stood, that seat would have had to choose the anchor and the typography,
which is drafting. Three decisions were therefore made in
`w42-correction-2026-10-26.md` this run, each with its reason in the file:

- **The anchor.** A new paragraph directly under the masthead at line 3 of the
  corrected file, one blank line each side, lead paragraph after it.
- **The form.** Plain prose. No italic, because the masthead above it is italic
  and is furniture that appears on every issue, so a notice in italic under it
  reads as another clause of the furniture rather than a statement about this
  page. No bold and no label in front of it, because her 2026-09-29 ruling bans
  bold in body copy and colon-led devices, which rules out the shape a
  newspaper would reach for.
- **The date.** "October 26, 2026" is the only date form this product has ever
  printed to a reader. `pipeline/weekly.py` builds every issue's range as the
  month's name, the day, a comma and the year, so the notice borrows that rather
  than inventing a second.

And the sequencing, which is the part that could have cost a reader. The two
edits are independent and the pull is never held for the notice. A frontend run
that lands the corrected body and leaves the notice for a one-line second diff
has done the whole job available to it. A run that waits for both so they land
together keeps a section that is wrong three times out of three in front of
readers to save a seat one diff.

## One argument replaced with a better one

Run 57 defended the notice by reading the scope of her 2026-09-19 ban on
meta-commentary, which is a defence from what the ban does not cover. Canon law
7 covers it positively. Its first clause asks for a limitation disclosed in one
plain sentence when it materially affects that day's content, and its second
bans the issue narrating its own methodology, ranking logic or virtues. A
section removed for being wrong is the clearest case of material the first
clause describes, and the sentence narrates none of the three things the second
clause names. The register row carries that ground now, because the row is what
she or a later seat reads, not the candidate's argument section.

## The gate: a clock nobody could read

Run 58 added the question row thirteen minutes before this run started, wrote
the deadline into it as "at about 20:44 UTC on 2026-10-28", and wrote beside it
that a reservation with a clock on it and no row anywhere is a clock nobody can
read. Both halves of that sentence were true of the sentence itself. Prose is
exactly the form no command can read, and this register's own closing paragraph
says what that is worth: nothing fires when a row here goes stale.

It is also the first row here that needs a command rather than a reading,
because it is the only kind of row whose answer arrives without anybody acting.
Every other row waits on her or on a seat's diff and simply stays open. This one
becomes law at a stated hour under the company standard's silence rule, whether
or not a run is looking.

So `check_voice.py deadlines` asks the two questions the prose cannot:

```
python3 -I docs/voice/check_voice.py deadlines
  DEADLINE_CASES                             4 of 4
  questions awaiting her word                4
  carrying a readable deadline               1
  read at                                    2026-10-26T21:07Z
    every clock here is readable and none of them has run out
```

A row that argues the silence rule and names no `deadline YYYY-MM-DDTHH:MMZ`
fails, which is run 58's row as written and is the second of the four pinned
cases. A deadline that has passed with the row still in the questions table
fails too. The cases run before the register is opened and are read against a
fixed clock, so a case here means the same thing on every day this file runs.

Two scope decisions. It reads the questions table only, because the surface rows
above it wait on a seat's diff and nothing about them expires, which the
register already says in plain words about its own oldest row. And nine of the
ten questions have no clock at all and must stay silent, which is why the first
pinned case is a bare question with no standard attached: a check that failed
those would be unusable by the register it reads.

The second question is a time bomb and that is deliberate. The inbox README
argues the other side of this well, that a gate which can turn `main` red over a
bookkeeping step is worse than the collision it set out to fix. This one cannot
reach `main`. No workflow runs this file. It runs inside a writer seat's run,
which is the only place where the right thing to do about an expired reservation
is decidable, and what goes red is a run in front of the seat that can record
the resolution and move the row.

What it does not do is decide the answer. Resolving a reservation by silence is
the standard's mechanism and the PM's to apply. This reports that the hour has
passed.

## The two repeats, filed

`INC-2026-10-26-the-supersede-proof-errored-on-the-first-run-that-actually-had-a-predecessor`.
Third occurrence of the single-branch refspec surviving `--unshallow`, and the
first time a run with a real predecessor reached the step the earlier entries
predicted would hurt. The charter's supersede proof passes on empty output, and
on this clone it produced empty output and a fatal error at once. A seat reading
"must print nothing" literally closes a pull request whose work it does not
carry. The entry names the form of the same proof that cannot fail quietly,
`git merge-base --is-ancestor`.

`INC-2026-10-26-a-sibling-run-read-this-seats-mail-and-acted-on-half-of-it-without-replying`.
Fifth instance of the duplicate-wake class and a new shape again. Run 58 was
in flight when the note arrived, read it, shipped the two register rows it
implied, and never replied, so the note was answered in the register and
unanswered on the bus with no record of who had done which. The cost was small
because the charter's clause found #612 in the first three commands.

## Gates

`deadlines` 4 of 4 cases and clean. `candidates` clean: this run adds no
candidate file, and the two files it changes are a candidate with a row and a
review. `selfcheck` 0 unexcused over the whole branch against `origin/main`.
`tools/incidents.py check` reads 346 entries and 19 inbox files with nothing
malformed. `tools/check_registers.py` 0 blocking. The conflict-marker grep over
`docs/`, `prompts/` and `README.md` prints nothing.

`provenance --live` reports the same two findings on `2026-W42` at 21:04Z that
run 58 read at 20:49Z, which is the live confirmation that the defect this run's
register rows describe is still in front of readers. Every other red gate on
this branch was red on `main` before it, is somebody else's register, or is one
of the two issues that reached readers and are not files in this repository.
