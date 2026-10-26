# The second generator, graded

**Writer seat, 2026-10-24, run 48. The artifact is `prompts/digest-short.md`,
the generator the press prints from when no model can take the full issue.**

## The single biggest weakness

**A short edition written in exact obedience to this prompt is held by the
pre-send gate, and the short edition is not offered a retry, so the week gets
no issue at all.** That is the outage the short edition was built to prevent.

The proof is measured rather than argued. I wrote a 400-word body that obeys
every rule the prompt carried this morning, ran the press's own pre-send gate
over it, and the gate blocked it twice.

```
/tmp/spec/short-obedient.md: 2 blocking, 2 warnings.
  [block] internal-vocabulary (2x, ban list 14)
      line 5: '2026-W38' is the ISO week code, which no subscriber can decode
      line 11: 'Supported twice' is a raw supports count, which no subscriber can decode
The send stops here.
```

Both blocks come out of the payload the prompt tells the model to write from.
`budget.smallest_payload()` carries `week` as `'2026-W38'` and a `traction`
block holding support counts. The prompt said "Everything you write comes out
of that payload", listed neither key in its own account of what it was given,
and carried no rule against printing either. `prompts/digest.md` carries a
rule for both.

The consequence is not a worse issue, and that is the part worth stating
plainly. `pipeline/weekly.py:1727` hands this edition to `hold_for_quality`
with `rewrite=None`, with a comment saying the degraded print is not offered
the retry. The full edition gets a second draft on a blocking finding. This
one is held, nobody is emailed, and the owner gets the held alarm. So every
rule the pre-send gate blocks on and this prompt does not teach is a path from
"the primary did not answer" to "there was no issue", which is
`INC-2026-10-12` exactly.

## Why no gate caught it

`pipeline/budget.py` says, in a comment at `SHORT_ISSUE_PROMPT`, that the
prompt "is the writer seat's surface and not this one's". The incident that
shipped the file says the same thing in its own closing paragraph:

> The short prompt carries a handful of the 103 entries in
> `docs/voice/ban-list.md`, because the rest do not fit in a 6,800-token
> request. The short edition is therefore the lesser issue by construction, and
> which rules survive is an editorial judgment that belongs to the writer seat
> rather than to the arithmetic in this diff.

That handoff was written on 2026-10-12 and this is the first writer run to
read it, twelve days later. Nothing carried it to this seat: it is a paragraph
in an incident entry, not a row on a board or a line in a register this seat
opens every run. `docs/voice/check_voice.py` named `prompts/digest.md` and no
other generator, and no file in `tests/` mentions `digest-short` at all.

Run 47 closed on the finding that no gate had ever read the generator. The
remainder was a whole second generator, and this is it.

## The budget, measured before anything was added

The incident's reasoning was that the ban list does not fit. The ceiling is
real and the file was nowhere near it.

| | tokens |
|---|---|
| the prompt as it stood | 844 |
| the largest prompt that still prints on every off-primary model | 3,731 |
| headroom | 2,887 |
| the prompt after this run's patch | 1,796 |
| headroom remaining | 1,935 |

Measured by binary search over `budget.short_issue_printers`, which is the
guard that fails the deploy, so the figure is the gate's own answer rather than
my arithmetic. The file was using 23 percent of its budget. "Which rules
survive" was a narrower question than the arithmetic forced, and three quarters
of the room was never spent.

## The taste gate, first, ruling by ruling

Run line by line against the artifact, which is what incident 20 says was
missing.

- **2026-09-19, the fine-tuned instruction is the base layer "for every
  cadence", refinements layer on top and never beside it. FAILED, and this is
  the ruling the whole grade turns on.** The short edition is a cadence. Its
  opening instruction read "Your first sentence is also the inbox preview, so
  it has to carry a finding on its own", which is the inverse of her
  context-first invariant. `prompts/digest.md` says "The greeting comes first,
  before any finding" and then "**It is ONE SENTENCE, and the sentence is about
  the reader's work in the PRESENT TENSE.**" Two generators, opposite
  instructions, in the slot she fine-tuned herself.
- **2026-09-19, the dual-audience close, as amended 2026-09-30 to "Accelerate
  every builder and agent to frontier speed." FAILED.** The prompt's part 4 was
  "One closing line that says what to watch next, drawn from the payload", with
  no standing close anywhere in the file.
- **2026-09-19, "You didn't show me the paper": links reach the full text,
  arxiv.org/html when it exists. FAILED.** The prompt said only "names the
  paper in italics with its link".
- **2026-09-19, the outsider test, every term of art given its plain-words
  clause at first use. FAILED.** The prompt carried no term-of-art rule at all.
  This is the strictest duty in the opening and the file's opening slot had
  nothing about it.
- **2026-09-24, ISO week ids never reach a reader. FAILED, and it is the
  blocking one above.**
- **2026-09-19, framework names never print. PASSED, and inertly.** The prompt
  says "No other sections", so the slot labels have nowhere to appear. Worth
  recording as inert rather than as held, because the reason is the absence of
  headings and not a rule.
- **2026-10-04, a title the library has used is not a title. PASSED.**
  "`prior_titles` in the payload lists the titles already used. Yours is new."
- **2026-09-19, no meta-commentary, the issue never narrates its own method.
  PASSED.** "no note about yourself or about how the issue was produced."
- **2026-09-19, length follows the news. PARTIAL.** A word ceiling is a budget
  rather than a template, so this is not a violation, but the file said only
  "Stay under that ceiling" and nothing about a thin week being honestly
  shorter.
- **2026-09-24, density and short paragraphs. PASSED.** "One short paragraph
  each, three to five of them."

## The laws, one verdict each

1. **Plain sentences, no em dashes, no semicolon joins. PASSED.** "No em dashes
   and no semicolons. The target for both is zero."
2. **No buzzwords. PASSED, and well.** "The test is grammatical, not a list",
   and the file refuses to print a specimen of the vocabulary on the stated
   ground that "a banned word sitting where a word gets written is the nearest
   available draft." That reasoning is correct and it is the file's best line.
3. **Sell the product, never the recipe. PASSED.** Nothing in the prompt asks
   the issue to describe the pipeline.
4. **The headline is a finding, not a greeting. PASSED.** "It is a sentence
   about this week's strongest finding, not a label for the issue."
5. **Relevance is impact, and the ranking says what earned each slot.
   PARTIAL.** "three to five of them, strongest first" orders the claims and
   never says what earned the order. At this size I am letting it stand, because
   a ranking sentence on each of four claims inside 400 words is the density
   failure of law 14 arriving to fix law 5.
6. **Evidence grades in-line. PASSED, narrowly.** "says what was found, how it
   was shown" carries the grade without naming it.
7. **Honesty serves items, never the method. PASSED.**
8. **Links go to the full text. FAILED.** Graded above.
9. **The fine-tuned instruction is the foundation. FAILED.** Graded above, and
   it is the biggest of the prose failures.
10. **The dual audience appears in every issue's close. FAILED.** Graded above.
11. **Length follows the news. PARTIAL.** Graded above.
12. **Framework names never print. PASSED, inertly.** Graded above.
12a. **The outsider test and density. FAILED on the outsider half, PASSED on
   density.** Graded above.
13. **Every issue stands alone. FAILED, and this is the one with three shipped
   failures behind it.** The prompt carried no stands-alone rule, no rule
   against "last week", and no trace of the hard grammatical rule the canon
   says has "no material that earns an exception": never a past-tense verb with
   "you" as its subject. `prompts/digest.md` carries that rule at the writing
   position and a gate for it at the end. The short generator had neither, and
   it is the generator for the edition that prints under the word "week".
14. **Enjoyable, and formatting is how. PASSED at this size.** The file's ban on
   starting a line with bold or italic text does sit against law 14's bulleted
   lists with bold leads, and at 400 words with no sections I read the ban as
   right and the tension as real. Recorded, not patched.
15. **Never claims to have read what it only ingested. PASSED, and
   explicitly.** "Ingesting a title is not reading a paper."
16. **A title already used is not a title. PASSED.**

## The ban list

Two quoted specimens sat at writing positions, which is entry 93's class and
`L-A23`:

- `"This week in AI research" is not a first sentence.` in the opening slot.
- `as in "Strong evidence. The method works."` in the rules.

The file states the principle for one rule and does not apply it to these two.
Both are removed and the forms are described instead, the way
`prompts/digest.md` does it: "The form is described and never drafted."

`python3 docs/voice/check_voice.py specimens prompts/digest-short.md` read 2
liftable specimens at writing positions before the patch, neither of them hers,
and 1 after, which is her own approved standing close. Entry 136 is the new
tell and it is about the gate, not the file.

## What was patched, and which law each change serves

| change | law |
|---|---|
| the opening rewritten to the context-first form, one present-tense sentence about the reader's work, then the news | 9, taste 2026-09-19 |
| the hard rule against a past-tense verb with "you" as its subject | 13 |
| the ninety-character preview constraint | 9 |
| nothing refers to a previous issue or to what the reader has seen | 13 |
| `week` never reaches a reader, name the month and the days | 14, taste 2026-09-24 |
| `traction` counts are facts about our database, said in plain words or left out | 14 |
| `dates` carries a separator that is not a hyphen, retype it, and the issue is plain ASCII | 13 |
| the title carries no date | taste 2026-09-19 |
| every term of art gets a plain-words clause at first use | 12a |
| the link reaches the full text, arxiv.org/html when the payload has it | 8, taste 2026-09-19 |
| the standing close, verbatim | 10, taste 2026-09-30 |
| a thin week is honestly shorter | 11 |
| a figure lands beside the thing it is measured against | ban list 24 |
| the two drafted specimens removed and the forms described | 93, L-A23 |
| the slop test extended past adjectives and adverbs to a verb or noun chosen for size | 2 |
| `week` and `dates` added to the account of what the payload holds | the blocking defect |

The repaired body, obeying the patched prompt, passes:

```
/tmp/spec/short-repaired.md: 0 blocking, 3 warnings.
```

## The gate, so this file is never unread again

Two changes in `docs/voice/check_voice.py`, which is this seat's surface.

**`specimens` and `generator` default to both generators.** They defaulted to
`[DIGEST]`. A default naming one of two generators reports a clean file and a
silent one under the same verdict, which is how a 66-line live prompt went
twelve days without a reader.

**A new gate, `blockrules`, which is the editorial judgment made mechanical.**
The engineer's question was which of 103 ban list entries survive into a
6,800-token request. The answer this run gives is a rule rather than a list:
**a rule survives if the pre-send gate blocks on it, because the short edition
gets no retry and a block is a week with no issue.** The gate reads the BLOCK
rule names out of `tools/check_digest_quality.py` and checks each against a
maintained row saying how the short prompt answers it, or why it cannot fire.

```
  rules the pre-send gate blocks on             8
  of those this seat has never ruled on         0
  of those that cannot fire on this edition     2
  of those the short prompt no longer answers   0
```

The two inert rules are `skeleton-heading`, which needs a section heading to
appear in, and `daily-too-short`, which is guarded by `kind == "daily"`.

**The artifacts it was built to fail**, per the rule from run 42 that a run
shipping a gate names them. Both were probes, neither is committed.

- The phrase answering `typesetter-punctuation` removed from the short prompt:
  `DROPPED typesetter-punctuation expected 'plain ASCII' in digest-short.md`,
  exit 1.
- A new BLOCK rule added to the pre-send gate:
  `UNRULED second-person-past (block on the short edition holds the issue)`,
  exit 1.

The second is the one that matters. A rule the engineer adds to the pre-send
gate now fails this check until this seat rules on whether the degraded edition
needs to be taught it. That is the loop whose absence cost twelve days.

## Two findings in the engineer's file, routed rather than patched

`tools/check_digest_quality.py` is not this seat's surface, so both go to the
ledger.

**The pre-send gate warns on the owner's own standing close, in every issue.**
`INTENSIFIERS` holds `"very "` and the test is `if word in low`, a substring
match with no word boundary. "every builder" contains "very ". So law 10's
close, which appears in every issue by law, raises `empty-intensifier` forever.

```
/tmp/spec/close.md: 0 blocking, 1 warnings.
  [warn] empty-intensifier (1x, ban list 5)
      line 5: 'very'
```

Under `--strict` it exits 1. It is a warning today, so no issue is held by it,
and the cost is that every quality report this seat and the owner read carries
one finding that is not real.

**`TYPESETTER` enforces four characters where ban list 13 is a class.** The
entry was amended on 2026-09-21 by incident 27, and the amendment's own words
are that "the three characters named above are examples and the entry is the
class, which is every character outside plain ASCII", and that "a check written
from the words above passes all five". The check is written from the words
above. It holds the non-breaking hyphen, the narrow no-break space, the thin
space and the multiplication sign, and it passes the en dash, the curly
apostrophe and the bullet separator.

The en dash is the one that matters, because `pipeline/weekly.py:1469` builds
the payload's `dates` with one, every week, by construction, and feeds it to
both editions. `check_voice.py` does census every character above 127, so a
shipped issue is caught, but that census reads `site/content/issues` after the
fact and is not the pre-send gate. Thirty-three days after the amendment
predicted this exact miss, the gate still passes the character the payload
supplies.

## Honest limits of this grade

The press has never printed a short edition. `site/content/issues` holds
2026-W37 and 2026-W39 and neither is one, and `NEON_RO_URL` is unset in this
run, so the digests table is unreachable. So this grade reads a generator and
not an issue, the specimens above are mine rather than the model's, and what
they prove is what the prompt permits rather than what a model did. That is the
weaker evidence and I would rather say so than imply a print. It is also why
reading the file is the only gate available for this edition: the usual
instrument, grading the output, has never had an artifact.
