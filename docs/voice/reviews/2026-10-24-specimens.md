# Graded review, 2026-10-24 — the safe form that broke its own rule

**Writer run 47.** The writer lane on the board held nothing queued: thirteen
items in Done, one in Review that pull request 419 had just merged, and the
backlog, the sprint and the in-progress columns all empty for this seat. So
this run opened the item it took, which is what `docs/standards/pm.md` §14
requires rather than permits.

The item is ban list entry 93's unenforced half, open since 2026-10-05 and
declined by three runs on the same stated ground, the last of them writing
"cannot be scored, and that is the honest verdict." That was true, and it is
why the count had to stop being a run's reading.

## The single biggest weakness, plainly

The generator offered the model a sentence as the safe form, at the position
where the greeting gets written, and that sentence is the shape the hard rule
four lines below it bans and the gate at the end of the file was written to
catch.

```
The safe form, written out so that following this rule is copying rather
than composing, in a subject no payload will ever hand you: "If you run
anything overnight, you have written the same retry logic three times. This
week two results made it unnecessary."
```

Subject "you", verb "have written", which is present perfect. The rule: never
a past-tense verb with "you" as its subject, no material earns an exception.
The gate: "Past simple, present perfect, past continuous, all of them."

**One commit added all three.** `6f3a492`, 2026-09-26. `git log -S` over the
rule's text, over the gate's list of tenses, and over the specimen's text each
return that one commit and no other. The run that wrote the prohibition wrote
the gate for it and wrote a violation of it in the same diff, and it put the
violation where writing happens and the gate where reading happens.

That is the whole argument of this review, and the rest of it is the evidence
and the count.

## What was graded, and it is not an issue

`NEON_RO_URL` is unset in this runtime and the newest published issue has not
changed in twenty-six days. Thirty-seven of the fifty reviews in this directory
already name it. Run 46 made the case for not producing a thirty-eighth verdict
on an unchanged artifact and that case still holds, so what this run graded is
the generator, which the charter calls this seat's lasting output and which
changed on most of the last forty days.

Grading the generator is not a substitute for grading an issue. It is the thing
step 3 of the charter exists for, and today it is also the only artifact in
reach that has moved.

## The count, which three runs declined and which is now a command

```
python3 docs/voice/check_voice.py specimens
```

| what it counts | before | after |
|---|---|---|
| quoted spans in `prompts/digest.md` | 257 | 252 |
| of those at a writing position | 196 | 191 |
| of those long enough to lift as a sentence | 77 | 73 |
| specimens the file's own tense check fails | **1** | **0** |
| specimens printing the machine's own words | 2 | 1 |
| specimens that are not the owner's own words | 66 | 62 |
| of those written about the payload's subject | 28 | 27 |

Three things about this table, because a count whose limits are not stated is
worse than no count.

**The regions are found by marker and not by line number.** The file is edited
on most runs, and a hardcoded span starts reading the wrong region in silence.

**The gates region is excluded from every finding, on the file's own
reasoning.** A banned specimen is safe where you read finished output and
unsafe where you write, which the file says in its own words, so the passes at
the end of it are out of scope by the doctrine they belong to.

**The owner's specimens are exempted by reaching into her register, not by
anyone's judgment here.** `hers()` reads `docs/voice/taste.md` and matches on
seven words of overlap. This matters more than it looks: "Context beats
architecture this week" and "you can steer a model toward the answers people
prefer without the usual calculus of training" are both on the payload's own
subject and both sitting at writing positions, and both are HER repaired forms,
recorded in her register on 2026-09-19. A sweep run without that exemption
would have reported her craft as the defect and asked a run to delete it, which
is the one thing canon law 9 and this charter forbid in the same words. The
inversion is the one the taste gate already uses, and the reason is the same:
this seat may not edit her register, so the quote lives on the checker's side
and reaches across.

**And the on-subject figure is a ceiling rather than a verdict.** Entry 93 rules
banned specimens out of this class in its own words, because a model copying a
banned specimen is caught by the ban, and no command can tell a banned specimen
from an offered one. Roughly a third of that list is banned text. The command
says so where it prints the number.

## The grade, law by law, against the generator

Fifteen laws, and the honest form is one verdict each with the evidence quoted.
Where a law cannot be scored against this artifact, the review says so rather
than scoring it anyway.

**Law 1, plain sentences and no semicolon joins. PASS.** The file's own
punctuation bullet now reads the mark with a question rather than a list, and
the semicolon count is in the shape gate with a target of zero and no budget.

**Law 2, no buzzwords. PASS.** The stock-word count is in the mechanical-tells
pass, the target is zero, and the bullet says the named words are "the evidence
that the question is worth asking and never the test".

**Law 3, sell the product and never the recipe. PASS, and it is enforced three
ways**: the internal-vocabulary rule, the payload-field-name rule, and the
clause saying the names of the rules in this file are on that list too.

**Law 4, the headline is a finding. CANNOT BE SCORED against the generator and
it is not a pass.** The title slot holds the rule and the test. Whether the
line a reader gets states a finding is a fact about a print, and the press has
sent nothing in twenty days.

**Law 5, relevance is impact. PASS.** The traction slot leads at every cadence,
the ranking key is required to be visible, and the daily's substitute signal is
the corpus rather than the citation movers.

**Law 6, evidence grades in-line. PASS on the rule and FAIL on its history**,
which the file now records honestly: the grade's position is fixed because a
rule about the grade's words lost to the grade's position seven items out of
seven, and the gate reads frames rather than stems because naming a stem only
moved the stem.

**Law 7, honesty serves items and never the method. PASS.**

**Law 8, links reach the full text. PASS.** The identifier is copied character
for character and the coverage half is a count over named works rather than
items.

**Law 9, the fine-tuned instruction is the foundation. PASS, and this run is
where that law did work rather than sat there.** Two of the specimens the sweep
surfaced are hers. Deleting them would have been this seat refining beside her
fine-tuning instead of on top of it, which canon law 9 names and which the
charter says has already been done once and rejected. The exemption is in the
command so the next run cannot make that mistake by reading the list too
quickly.

**Law 10, the standing close. PASS.** "Accelerate every builder and agent to
frontier speed." is the last line of the template, declared always last and
never reworded.

**Law 11, length follows the news. PASS.**

**Law 12, framework names never print. PASS.** The four names are held only at
the heading gate, the tripwire runs after the question rather than in place of
it, and the prose search for the four ideas is there because a slot name does
not need a heading to print.

**Law 12a, the outsider test and density. FAIL, and run 46's filing is the
reason this run adds nothing to it.** The word `harness` is bare in all three
prints the library has made, across two generators and five prompt rules, four
of which were in force for the newest print. That is well past the charter's
"twice", the fix is filed in `docs/ideas.md` for the engineer as a blocking
rule in the one reader that sees an issue before a reader does, and a sixth
sentence here would be the third mistake the charter names.

**Law 13, every issue stands alone. FAIL, and this is the run's finding.** The
law's own grammar half was violated by the file that carries it, in the sentence
offered for copying, for twenty-eight days. Evidence is the block at the top of
this review. The repair is in this diff.

**Law 14, the issue is enjoyable and formatting is a tool. PASS on the rules.**
Nine counts, each with one fix, and the shape count's failing state is one kind
of block.

**Law 15, the issue's claims about its own reading. PASS.** The verb is bound to
`papers_read_in_full`, the zero case does not print at all, and the span is the
seven days rather than a calendar week.

**Pass 6, the standing defects, which has no failing state of its own. FAIL,
and the newest entry is this run's.**

- **Entry 92. FAIL, and the filing is twenty-one days open.** Nothing calls
  `docs/voice/check_voice.py`. Re-checked rather than restated:
  `grep -rn "check_voice" --include=* . | grep -v "^./docs/" | grep -v "^./.git/"`
  returns nothing, and `.github/workflows/checks.yml` names each test file by
  hand. The file now holds ten passes rather than the three it was filed with,
  so the filing's value has more than tripled while it sat.
- **Entry 93. Closed today, and it took a command rather than a run.** Its
  unenforced half said the file still teaches by worked example at other
  writing positions and nobody had inventoried them. The inventory is the table
  above and the entry now carries the command.
- **Entry 134, added yesterday. FAIL**, which is the expected state for an
  entry whose ending is a filing. Unchanged by this run and re-confirmed above
  under law 12a.
- **Entry 135, added today. PASS on the day it was written**, which is rare in
  this register and is worth saying plainly: its ending is an anchor and not a
  filing, both anchors are verified against the live generator by the
  `enforcements` gate, and the command that found the defect reports zero.

## What this diff changed in the machine

Four specimens and three restatements, and the file got smaller.

**The greeting specimen is deleted and the form is described.** This is the
finding above. The slot had already done the hard part, moving both BANNED
sentences to the gate on the stated ground that a banned sentence at a writing
position is the nearest available draft whatever the paragraph around it says.
It left the OFFERED sentence standing four lines above the rule, carrying the
same grammar the two it had just removed carried. The warning was moved away
from the writing position and the model was left there.

**The claim above the template is corrected, because it was false of the file
it describes.** It read: every example in this file is drawn from a subject the
payload cannot contain. Twenty-seven spans say otherwise, and the reading-list
slot had already refuted the defence in prose, saying a specimen "defended as
uncopyable" is still a draft because "the subject is the one thing a payload
controls". Two doctrines in one file, the stricter one confined to one slot.

The test that reconciles them is in the file now, and it is the review's one
piece of new craft rather than a restatement. An off-subject example cannot be
lifted for its CONTENT. It can still be lifted for its SHAPE, because a shape
survives having its subject swapped. So a position whose reusable part is a
shape carries no example at all and is described instead: every heading, every
line opener, every grade, every attributive phrase. The evidence that this is
the right cut rather than a tidy one is the print of 2026-10-05, which lifted a
heading frame with nothing but its tail changed, and the night-shift specimens,
which have never been reported lifted and which the file reaches for whenever
it needs a number.

**The thin-evidence rule stops naming a payload stream at the reader.** It
offered "only one deprecation this week" as the plain form, and `deprecated` is
a payload key, which the internal-vocabulary rule forbids in its own words two
hundred lines earlier.

**The attribution rule stops naming people.** It offered three attributive
phrases with researchers' names in them at the position where an attribution
gets written, under a rule whose own absolute is never-invent. This is the
highest-consequence lift on the list and not the most likely one: a template
costs a reader's interest and an invented attribution costs the claim.

**Three restatements of one principle collapse, and that is how the run pays
for itself.** Now that the doctrine is governing law above the template, the
reading-list slot's argument for it and the heading rule's argument for it are
the same principle stated a second and third time, which canon law's trimming
rule names as this seat's notes to the next editor. The operative clauses stay.
The third was a sentence that had become false and is deleted rather than
trimmed.

**The weight, measured and not estimated.** `python3 pipeline/budget.py` with
tiktoken installed, so the figure is exact rather than the pessimistic estimate
the canon says not to believe: 146,685 characters and 34,018 tokens against
146,795 and 34,043 before, so **-110 characters and -25 tokens**. The canon's
rule is that a run which adds tokens removes at least as many, and this one
removes more than it adds.

The cost per issue is $0.1476 worst case both before and after, against a
ceiling of $0.15. The saving is real and it is smaller than the printed
precision, which is the honest way to say it: a first draft of this paragraph
read the before-figure off a budget run taken midway through the patch, when
the file was 375 characters heavier than it started, and reported a saving four
times the true one. The before-figure here is measured against the parent of
this run's own commit.

**And the taste gate caught my own edit before this was shipped**, which is the
cheapest possible demonstration that the gate is worth its line. The rewording
of the invariant paragraph broke the anchor `taste.md` holds for her ruling on
the four slot names, because the sentence that carried it gained a capital
letter. `check_voice.py taste` went from one pre-existing failure to two. The
sentence was restructured to carry the anchor verbatim and the count went back
to one.

## The new pass, and the idea in it

The pass is small and the idea behind it is not, so it is stated here rather
than left in a docstring.

**Every hard gate in `prompts/digest.md` reads finished output, and not one of
them has ever read that file.** There are eleven of them. A specimen sitting at
a writing position IS a draft of that output, which is the whole of ban list
entries 53, 88 and 93 and of `L-A23`. It follows that the gates apply to the
file's own specimens, and nobody had ever pointed one of them there.

Two of them need no judgment at all. The tense check, which the file itself
calls grammar rather than judgment and which it says has "a yes or a no". And
the internal-vocabulary rule, which is a word list.

Only the first one fails the check, and the asymmetry is the file's own rather
than a convenience. The file holds all three shipped past-tense greetings at
the gate and says they are "deliberately absent from the opening slot where the
line gets written", so a specimen of that shape at a writing position cannot be
a banned one and needs no reading. The internal-vocabulary list makes no such
promise: the file quotes the machine's own words at writing positions both as
the failure and as the form, and the two hits it reports are one of each. A
gate that failed on a correct line is a gate the next run routes around, so
that finding is inventory and says so.

## The repeat, recorded

`INC-2026-10-24-the-safe-form-broke-the-rule-it-illustrated`, appended in this
pull request. It is the fourth occurrence in the greeting chain and the first
one found in the generator rather than in a print. The standing rule at the top
of the incident register binds this seat and not only the ExO's weekly read.

The company-standard half of it is filed in `docs/ideas.md` for the ExO to
relay, because it is not this seat's edit to make. `L-A14` tells every seat in
every product to ship the safe form beside a prohibition, "so following the
rule is copying rather than composing", and the commit that produced today's
defect quoted that phrase while producing it. `L-A23` tells every seat not to
quote the banned specimen where the work is written, and the generator obeyed
that too. Neither standard says the safe form has to pass the rule it
illustrates. L-A14's own worked case is a shell snippet, where that question
answers itself. Where a rule governs prose, the safe form is a sentence and the
question is a reading nobody ran.

## The registers, checked rather than read

- **`docs/voice/taste.md`, first and line by line.** Two rulings bind this
  artifact directly. Her outsider ruling of 2026-09-19, whose recorded repaired
  form is one of the specimens this sweep surfaced and therefore one of the two
  it must not touch. And her stands-alone ruling of 2026-09-24, "dont assume
  readers read each issue", whose grammar half is the rule the deleted specimen
  broke. The gate reports one failure and it is the pre-existing one, verdict 6
  of her 2026-09-29 ruling, which is a live site defect with an open row rather
  than anything this run touched.
- **`docs/voice/canon.md` and `docs/voice/ban-list.md`.** Fifteen laws graded
  above. Entry 135 added with two verified anchors, entry 93 closed with the
  command that closes it.
- **`docs/voice/value.md` and `docs/voice/preferences/`.** Not applicable, and
  that is a statement rather than a skip: this run produced no reader-facing
  copy, drafted no line for any surface, and added no row to
  `docs/voice/awaiting-her-word.md`.
- **`docs/voice/awaiting-her-word.md`, and `candidates` passes this time.** The
  gate reads every file a diff adds under `docs/voice/`, and the one this run
  adds is this review. It quotes the generator rather than an issue, so it
  redrafts no surface with an open row and the gate says so. Run 46 left a note
  for the next run that the gate will trip on any review quoting an issue with
  an open row. That note is still right and this run did not need it.
- **`docs/agents/quality-claims.md`.** No copy round, so no claim to place.
  Every figure above was produced by a command named beside it.
- **`docs/agents/copy-pipeline.md`.** Read on a prior run, no copy round here.
- **`docs/standards/lessons.md`, the `any` section and the writer's.** `L-A14`
  and `L-A23` are the two this run turns on and both are quoted rather than
  paraphrased. `L-A22` is why the finding became a command. `L-A21` is why the
  command was probed on both exit codes and on both branches before being
  trusted, and the probe is the before-and-after table above. `L-A47` is why
  the pass states its scope and its exclusions before it prints a number.

## The gate summary after the diff

`enforcements`, `sweep`, `stale`, `measure`, `links`, `candidates`, `generator`
and `specimens` exit 0. `taste`, `claims`, `reading`, `delivery`, `ledger` and
`firstuse` exit 1, and every one of those is a live site or press defect already
carrying an open row in `docs/voice/awaiting-her-word.md` or an open filing in
`docs/ideas.md`. `ledger` moved by one in each column because this run filed one
proposed entry, so the gap of one it reports is unchanged and is still run 45's
finding.

## The board

The item names the measurement rather than the law, so a reader of the board
sees what was counted without opening a file.
