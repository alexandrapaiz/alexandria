# The file that bans the heading wrote the heading, and the issue printed it

**Writer run 54, 2026-10-26, hook, capacity returned.** Graded against
`2026-W40`, which went to readers on 2026-10-05 and which no run of this seat
and no command in this repository had ever read. Fetched from the live page,
un-rendered to the markdown the press stored, and the un-renderer proved
against `2026-W39` before a single figure below was taken off it.

## The single biggest weakness, plainly

`prompts/digest.md` bans a heading shape in two consecutive paragraphs and then
writes that shape three times in its own prose, and `2026-W40` printed it:

> ## What is gaining ground: recursive self-improvement with fewer guardrails
> ## What is genuinely new: where memory lives and who can pull the plug
> ## What fell behind: the assumptions that let agents run unchecked

That is canon law 12. It is the one ruling the owner has given twice, the
second time in the word "AGAIN", and it is incident 20 in this repository's own
register. The issue carrying it was sent twenty-one days ago.

The generator forbids it before the model reaches a heading slot. Line 349
names "what is new" and "what fell behind" as "that failure in its commonest
dress". Line 351 bans the colon that launders it, in the exact shape "What fell
behind: the thing yesterday's consensus got wrong", which is the third heading
above with one noun changed.

And then the same file wrote them. Line 44 listed the day's four slots as "what
gained ground, what is genuinely new, what fell behind, what to read yourself",
which is two of the three printed headings word for word and the third one
inflection away. Line 1525 wrote "what is new tests it, what fell behind is the
position it replaces", two of the five banned phrasings verbatim, inside the
rule that teaches the weekly to argue rather than list.

The diagnosis was already in the file, in its own bold: "The ban is on the
slot's IDEA and not on four strings, **and the words that beat it came out of
this file**." A run wrote that sentence, enumerated five phrasings under it,
and swept nothing. That is ban list 143 and the patch is in this diff.

## This run is a grade because a command said so, and the command is new

The run before this one could not have graded `2026-W40`, and it said so. The
fourth sighting of the artifact-scope class closes with the sentence that
`measure`, `devices`, `standalone` and `firstuse` all read
`site/content/issues/*.md`, that they therefore "describe a product two
editions stale unless a path is passed by hand", and that this is "the
engineer's surface and it is reported rather than filed here, because this run
cannot tell whether the directory is meant to be a mirror of the record or a
build input."

Three of those clauses are right and the conclusion does not follow. The
commands do not need the directory to change and they do not need that
question answered. They need a source, and the product publishes one with no
credential on it.

```
python3 docs/voice/check_voice.py editions
  served by the product     3: 2026-W39, 2026-W40, 2026-W42
  held in the repository    2: 2026-W37, 2026-W39
  round trip verified on     1 edition(s) held both ways
    OK      2026-W39  the served page un-renders to the file
  served and unreadable here 2: 2026-W40, 2026-W42
```

The round trip is the part that makes the rest usable. For every served week
the repository also holds as a file, the gate un-renders the public page and
diffs it against the file. `2026-W39` matches on every line that carries a
character, and `marks` finds the same single semicolon in both copies, at line
35 of the page and line 36 of the file, which is the one blank line between
them. A figure taken off a served page belongs to the document the press wrote,
and that sentence is now a command rather than a hope.

## The grade of 2026-W40, twenty-one days late

Read cold, start to finish, as a stranger who might pay $20. It is a better
issue than its headings suggest and the headings are what a reader meets first.

**Law 1, plain sentences and no semicolon joins. FAIL, eight times.**
```
python3 docs/voice/check_voice.py marks --live
  2026-W40 (served, un-rendered)   marks outside a quotation  8
```
Every one is the construction the generator names: "The field is not merely
accepting recursive improvement; it is making it cheaper and more stable." The
generator says of this mark that "the target is zero and there is no budget",
twice, and the second statement names the shape in its own words, "two finished
sentences in a balanced contrast". Eight in one issue is where that sentence's
number came from. It is a rule stated with no budget and nothing between it and
a reader, which is the ledger filing in this diff.

**Law 4, the headline is a finding. PASS.** "Reward-free search and
kernel-level kill switches redraw the agent stack" states something a builder
can act on and could not be yesterday's title. `firstuse` reports zero title
terms a reader cannot define, which is better than `2026-W39` managed at two.

**Law 6, evidence grades in-line. PASS.** "The authors' own experiments, not
yet replicated outside the group." Present on every item, in the body rather
than in a footnote, and the kernel item grades its two claims apart: "The
latency numbers are reproducible; the breach narrative is not independently
verified." That is the right judgment inside the wrong punctuation, and it is
one of the eight above.

**Law 8, links reach the full text. PASS on form, FAIL on coverage.** Three of
three are `arxiv.org/html/`, which is the form. Coverage is the failure and it
needs a count rather than a reading, which is ban list 74. The issue names
SelfSearch, RSIAgent, RRSI, Rethinking On-Policy Distillation II, Latent
Interface Training, Dynin-Robotics and Movement Trend Guidance in its first
three sections and links none of them. Every link in the issue is in the
reading list. The generator's own words are "Every item in every section
carries its own link, and the traction section and the fell-behind section are
items just as much as the reading list is."

**Law 11, length follows the news. PASS on length, FAIL on density.** 1,350
words across 26 paragraphs is an honest size for the week. Four paragraphs run
past 100 words and the longest is 140, which is the kernel-preemption item, and
her ruling is that "avoiding density is important" with "one idea per sentence
as the default". That paragraph carries a latency, a confidence interval, a
benchmarking protocol, a prototype, an integration, a breach, five figures
about the breach, three named defences and two grades. Every clause is good and
the reader meets them as a wall.

**Law 12, framework names never print. FAIL, three times, and it is the
finding at the top of this review.** The verdict is not the grep, per ban list
entry 97: the four internal strings appear nowhere in the issue and the idea
appears in three of its five headings.

**Law 13, every issue stands alone. PASS.** "You ship agents that improve
themselves or you ship agents that stay safe, and until this week those two
pipelines barely spoke." Present tense, a condition rather than a claim about
what the reader has done, and `standalone` reports zero hits on this edition
against one on `2026-W39`. That is a merged repair of this seat's own working in
a print, confirmed by command for the second time.

**Law 14, the issue is enjoyable and formatting is how. FAIL on the two named
devices.** `devices` reports no list and no written turn. `measure` reports
`shapes 2`, which is paragraphs and one standalone line, and the generator's own
count calls one kind of block a failing issue. What the issue does have is four
bold leads in its middle section, which is formatting she asked for and is not
either of the two devices law 14 names. The rule for the list half was patched
into the generator on 2026-10-26 by the run before this one, so this verdict is
recorded and not re-patched.

**Law 15, never "read" for ingested. PASS.** "The week ending October 4 brought
2,557 papers in and 127 read in full." The arriving count takes "brought in"
and only the read-in-full count takes a verb of reading, which is exactly the
distinction the law draws.

**Law 16, a title the library has used is not a title. PASS.** No earlier issue
carries it.

**The outsider test. FAIL, and it is the standing failure rather than this
edition's.** `firstuse` counts 35 terms of art against the generator's cap of
five, 33 of them never glossed. `2026-W42` is 38 against the same cap, so this
is not a regression and not an improvement. The cap is a rule in the prompt
with no gate before the send, which is the fifth row of the ledger filing.

## The current edition, by command rather than by a second reading

`2026-W42` was graded in full four hours ago by run 51 and a second opinion on
one edition is not a better generator. What this run adds is that the verdicts
are now commands. Run 51 measured law 8 link by link with `curl` and filed the
pipeline change. `check_voice.py links` now asks arXiv per identifier and
prints the violations apart from the fallback:

```
python3 docs/voice/check_voice.py links --live
  2026-W42   arXiv links 10   abs 9  html 1
    of those, full text exists  7   no full text 2   unreached 0
      FAIL    abs/2604.24594 and arxiv serves html/2604.24594
      OK      abs/2609.37312v1, no html version, which is the rule's own fallback
```

Seven of ten links in the edition a buyer opens today stop at the abstract with
the full text one path segment away. Two are the rule working. The measurement
is run 51's and the gate is this run's, which is the difference the register
map calls the second gate, the one the org keeps forgetting.

## The patch, and why it is one line in three places rather than a paragraph

Every live defect above is a rule the generator already states in its most
explicit available form. Law 8's link rule is bolded, carries a worked
`abs` to `html` example with a version suffix on it, and warns about coverage in
the same bullet. Law 1's semicolon rule states its target twice and names the
construction. Law 14's list rule was patched this morning. The charter's
structure watch says a structural fix that has failed twice through prompt
changes goes to the engineer rather than into a third wording, and run 51
applied that to law 8 four hours ago and filed the entry.

So this run wrote a fourth wording of law 8's rule, at the three writing
positions where the file hands the model `[full text](url)` and says nothing
about the url, and then struck it. The revert is in the history on purpose. A
run that argues wording is not the lever and then adds a wording has graded
itself more kindly than it graded the generator.

What the generator did get is the sweep nobody ran. All three slot specimens now
use this file's internal names, which the tripwire at the end of the file
already reads, so a leak from any of them is a leak the existing gate catches.
Weight 33,953 tokens before and 33,947 after, six returned, because the internal
names are shorter than the dress.

## The standing defects, re-checked

- **The masthead recites three framework slots**, line 3 of every edition, 23
  days, third ledger filing, `pipeline/weekly.py:1002`. Still true. One thing
  this run can add and it is not a coincidence worth asserting: the masthead's
  "what's gaining acceptance" and `2026-W40`'s "What is gaining ground" share a
  frame, and the model never sees the masthead, because `add_masthead` splices
  it after generation. The common source is the prompt and not the masthead,
  which is ban list 143 and is fixed here. The masthead filing stands on its
  own reasons.
- **`check_voice.py reading`, four surfaces give the arriving count a verb of
  reading.** Still four, unchanged. The oldest is `site/app/page.jsx:44`, 30
  days, drafted since 2026-09-26.
- **The desk queue renders 524 rows oldest first.** Still open, drafted
  2026-10-24.
- **Nine captions on the skill library's shelf page.** Drafted by run 53 and in
  this pull request, awaiting her word.
- **`docs/voice/value.md` has read "awaiting her approval" for 56 days** and the
  charter's prescribed remedy was performed on 2026-09-21. Run 53 filed the
  deadlock and routed the §22 ask to the PM. Nothing in this run touches it.

## This run's own prose, measured

`selfcheck` is the gate this seat points at itself, and the charter says an
editor whose review contains a banned word resigns. The run's own figures are
in the checks table below rather than claimed here, because a review that
asserts its own cleanliness is the thing ban list 74 is about.

## Checks

| check | result |
| --- | --- |
| `editions` | FAIL on two served editions no gate could read, which is what it exists to say |
| `links --live` | FAIL, 7 of `2026-W42`'s 10 links stop at the abstract with the full text live, 2 are the fallback |
| `marks --live` | FAIL, 11 semicolons across the three served editions, 8 of them on `2026-W40` |
| `devices --live` | FAIL on all three served editions, no list and no written turn in any |
| `standalone --live` | clean on `2026-W40` and `2026-W42`, one hit on `2026-W39` |
| `slotwords` | green on this branch, FAIL on `origin/main` naming both standing specimens, 5 cases pass |
| `ungated` | FAIL, 5 of 11 absolute rules have no gate between them and a reader |
| `enforcements` | entry 143's LANDED line resolves, 58 checkable against 57 before |
| `routed` | clean, 10 ledger entries named, no finding routed that the ledger already holds unnamed |
| `candidates` | clean |
| `blockrules` | clean |
| `incidents.py check` | nothing malformed |
| `pipeline/budget.py` | 33,947 tokens, 6 returned |
| conflict markers | none in `docs/`, `prompts/`, `README.md` |
