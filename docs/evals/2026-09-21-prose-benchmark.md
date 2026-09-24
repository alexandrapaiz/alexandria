# Blind prose benchmark: the digest against TLDR AI

Sprint 2026-09-21, item 2. Engineer seat, 2026-09-21.

**Status: the instrument is built and the packet is cut. The scores are
not in, because scoring is the comped friends' job and no agent session
can do it for them.** Everything below is ready to send. What is owed is
one round of reading by people, and then one command.

## Why this is not the benchmark we already have

`docs/voice/prose-benchmark-2026-09-19.md` is the writer seat's reading
of alexandria against five newsletters. It is a good document and it is
not this. It was written by the seat that owns the prose, with both
names visible, grading its own work. It gave 2026-W37 an F on voice,
which is probably right, and that is exactly the problem. A seat that
can hand itself an F can hand itself an A, and neither number came from
a reader.

This benchmark asks strangers which passage they would rather read,
without telling them who wrote either one. That is the only version of
the question whose answer we do not already control.

## The rubric

Three questions, each out of five, one line of reason required. The
three come from the sprint. They are deliberately about reading rather
than about craft, because a subscriber does not grade prose, they either
keep reading or they stop.

**1. Clarity.** Could you say what this passage claims, in your own
words, straight after reading it once? One means no. Three means you
got the gist and would have to go back for the specifics. Five means you
could restate it.

**2. Written by a person.** Does this read as written by someone with a
view, or as a form being filled in? One means a template with the blanks
filled. Three means competent but anonymous. Five means someone is
clearly talking to you.

**3. The point lands.** Did the point arrive without you going back over
a sentence? One means you reread more than once. Three means you went
back once. Five means it landed first time.

Then one forced choice. Of the two passages, which would you keep
subscribing to, and why in one line. Scores compress and a head to head
does not, so the preference count is the number we will act on. The
2026-09-07 distill bake-off worked the same way and its verdict held.

There is a fifth field, and it is the one that protects the result.
Graders are asked whether either passage looked familiar. Several of
the comped friends subscribe, so some of them may have read 2026-W37
when it went out. A grader who recognises our own issue is not scoring
blind, and a sheet that says so is worth more than a sheet that quietly
does not.

## How the specimens were cut

No hand chose the extract. `tools/blind_prose_benchmark.py` applies
these rules and `tests/test_prose_benchmark.py` pins them.

**Ours.** The issue's opening, then the first item of its first section,
whatever that item happens to be. That is 201 words from 2026-W37, the
only issue that has ever shipped.

**Theirs.** The comparison issue's second section, taking items in
publication order, skipping sponsored items, until the running word
count first reaches ours. That is 251 words from three items of TLDR
AI's "Deep Dives & Analysis" for 2026-09-21, read live this morning and
kept in `sources/` so the cut can be repeated without the network.

Second section rather than first, and the reason belongs here rather
than in a fresh judgement each run. A TLDR issue opens on product news,
alexandria publishes no product news at all, and a comparison against
that section would measure subject matter instead of writing. The
second section is where they put analysis, which is the nearest thing
they print to what we print.

## How they were blinded

Every rule below runs on both specimens. Where a rule only bites on one
of them, that is said, because a rule that touches one publication and
not the other is a thumb on the scale.

- **Typographic characters become ASCII.** Non-breaking hyphens, narrow
  no-break spaces, curly quotes, the multiplication sign, and em dashes,
  which become a spaced hyphen. **This one only bites us.** Our 201
  words carry sixteen non-breaking hyphens, two narrow spaces and three
  em dashes. Their prose carries none. Without this rule a grader could
  sort the two passages by searching for a character instead of reading
  either of them, and the whole exercise would be theatre.
- **Links go,** replaced by the word link. Only we cite, so only we are
  touched. An arXiv URL names us as surely as a masthead would.
- **Read-time tags, repository tags and sponsor blocks go.** Only they
  are touched.
- **Bold and italics go, on both sides.** Their issue reaches us as
  rendered text with its markup already lost, so leaving ours in place
  would hand the grader a typographic signature rather than a sentence.
- **Publisher names go,** matched on whole words, in both directions.
- **Mastheads, dates and the week code go.**

And what deliberately stays, because it is the thing under test:

- Section headings, including ours. "Trailblazing" is furniture that
  fits any issue we will ever publish, which the ban list has said twice.
  Question two exists to catch furniture, so removing it first would be
  removing the evidence.
- The item that ends on its citation, which ban-list entry 25 names.
- Sentence length, paragraph shape, sub-bullets, and every word choice.

## What this cannot tell us, said plainly

- **One issue, one week, one section.** We have shipped once, so the
  sample on our side is the whole archive and still only 201 words.
- **The passages are 25% apart in length.** The rule stops at the first
  item that reaches our word count, and the item it stopped on was a
  long one.
- **Ours opens with a framing paragraph and theirs does not,** because
  theirs has no opening. That asymmetry is in the sprint's own
  instruction and it is also a real difference between the products.
- **Subject matter still differs.** Ours is research findings, theirs is
  analysis of the field. Choosing their second section narrowed that gap
  and did not close it.
- **Normalising the punctuation removed real defects from our specimen.**
  Ban-list entry 13 is a genuine failure of 2026-W37 and this benchmark
  will not see it. That is the right split of work. The machine gate
  catches encoding, and people are being asked about reading.

## Running it

```
python3 tools/blind_prose_benchmark.py build     # cut and blind the packet
python3 tools/blind_prose_benchmark.py reveal    # the key, from the seed
python3 tools/blind_prose_benchmark.py tally --write docs/evals/2026-09-21-prose-benchmark.json
```

The packet is `specimens/`, and it holds two passages and a scoring
sheet. It holds no key. The key is not stored anywhere in the repository
and is recomputed from seed 20260921 when someone asks for it, so
handing a grader the folder gives nothing away.

To collect a round: send `specimens/` to each comped friend, ask for the
sheet back with the fields filled in, drop each one into `scores/` as
`<name>.md`, then run `tally`. It averages each criterion per passage,
counts the preferences, maps the letters back to the publications, and
writes the result beside this file in the shape the 2026-09-07 bake-off
used. It refuses a score outside one to five rather than averaging it,
and it says it has nothing rather than printing an empty result.

## What is owed

One round of human reading. Until it lands, this repository has an
instrument and no measurement, and nobody should quote a number from it.
