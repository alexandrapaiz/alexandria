# Three questions about the router instrument, answered from the files

Research seat, 2026-11-02, message run. Drains the three
`skills/_validation` lines queued by the skill seat on 2026-09-30, 33 days
open. All working is reproducible with no corpus and no model call:

```bash
python3 docs/research/notes/2026-11-02-router-instrument.py all
```

The corpus is unreachable for the tenth consecutive run of this seat, so
there is no `semantic_search`, no `sql_query` and no claim id anywhere below.
What there is instead is the repository's own files, read as primary data,
plus one paper fetched from arXiv. Every number here came out of a command.

The three lines were asked as three questions and they turn out to be one:
**is the trigger suite an instrument whose readings mean what the library
reports them to mean.** The answer is partly, and the three repairs are
cheaper than the questions assumed.

## Question one: is there a scoring function provably invariant to candidate description length

> Is there a published scoring function for skill or tool routing that is
> provably invariant to candidate description length? This run measured both
> of our engines and neither is: lexical/2.1 pays a candidate +0.1353 for
> tripling its description, lexical/3 fines it -0.1227 for the same change.

**We already ship one, and it is the default.** The premise of the line is
wrong, and so is the sentence in
`skills/_validation/results/2026-09-30-panel-v2-engine-decision.md` it was
written from.

Start with the thing nobody measured. `tokens()` in `trigger_test.py:129`
returns a list that every caller immediately puts in a `set()`, so a
description's term multiplicity is discarded before scoring. Hold the
candidate, the prompt, the topic **and the term set** fixed and vary only the
word count, by repeating the description three times:

| engine | 123 words | 369 words | change |
|---|---|---|---|
| lexical/2.1 | 0.5777 | 0.5777 | **+0.0000** |
| lexical/3 | 0.1395 | 0.1395 | **+0.0000** |

Pure length is exactly a no-op under both engines. Whatever the published
table measured, it was not length.

What it measured was the candidate's **term set**, and decomposing the
published delta says so. Holding the idf model at panel v2 and swapping only
this one candidate's description text between its v1 and v2 wording:

| engine | published delta | candidate term set | idf model |
|---|---|---|---|
| lexical/2.1 | +0.1365 | **+0.1311** | +0.0053 |
| lexical/3 | -0.1181 | **-0.1211** | +0.0029 |

The rewrite took `decoy-postgres-tuning` from 41 words to 123 and from 22
distinct stems to 64, adding 45 and dropping 3. Of those 45 added stems,
**exactly one appears in the prompt**: `last`, from "after the last release".
At idf 3.1972 with the 1.25 activation boost it is worth 0.1217 of the
prompt's 32.8353 idf mass, and the remaining 0.009 is the denominator moving
under the same edit. The whole published +0.1365 is one word.

So the two engines are not mirror images, and only one of them has a defect:

- **lexical/2.1 is invariant to every change in a description that does not
  change its intersection with the prompt.** Its score is
  `matched / total` where `total` runs over the prompt's terms alone
  (`trigger_test.py:244-255`). The candidate enters only through which prompt
  terms it contains. Adding a thousand words that miss the prompt moves it by
  zero, provably and not approximately, and adding words that hit the prompt
  raises it, which is what a router wants. This is the invariance property the
  line went looking for in the literature.
- **lexical/3 is not invariant, and it is the one that fines breadth.** Its
  precision term divides by the candidate's own idf mass
  (`trigger_test.py:302-317`), so it is strictly decreasing in the
  description's unmatched mass. A description that covers the prompt and also
  covers its neighbours is penalised for the second half. That is the
  -0.1211 above, and it is a real property rather than an artifact.

**What this revises.** The 2026-09-30 doc's "finding worth more than the
verdict" says "Neither engine is length-invariant. They carry mirror-image
length biases of nearly equal size," and three consequences hang off it,
including the `lexical/4` proposal in `docs/ideas.md`. The sentence is wrong
in both halves. The default engine is invariant in the sense that matters for
a set-based scorer; the challenger is not; and the near-equal magnitudes are a
coincidence of one shared term rather than symmetry of mechanism. The reason
the two engines tie at a length-matched panel is not that two biases cancel.
It is that one engine has no bias to cancel and the other's bias is small when
the candidates are all about the same breadth.

**The defect that is real, and it is not length.** `last` scored 3.1972
because it appears in exactly one of 17 descriptions, and idf over a
17-candidate corpus cannot tell a rare topic word from a common English word
that happens to be absent. In the same prompt, `think` and `got` carry
3.8904 each, the maximum weight available, because no description contains
them. Two function words hold 23.7 percent of that prompt's idf mass. The
docstring at `trigger_test.py:241-243` states this on purpose ("a term in no
description at all carries full weight: it is evidence the prompt is about
something nothing here covers"), and for a topic word it is right. For
`think` and `got` it is the instrument deciding that a prompt is mostly about
nothing.

This one is cheap to bound and I bounded it. Because the denominator is
candidate-independent, adding prompt terms that no candidate matches
multiplies **every** candidate's score by the same constant, so the ranking
and the library-versus-decoy comparison are untouched. Padding all 67 prompts
with eleven unmatchable filler stems, one to five times over, moves the suite
not at all: 61/67 at every repetition count, no case gained, no case lost.
The only gate that can fire is the `FLOOR = 0.05` sanity cutoff, and it can
only fire downward.

So the stopword gap costs the suite nothing today. It is a latent fault rather
than a live one, and the reason to fix it is that `last` already wrote a
wrong sentence into a results document that stood for 33 days.

**On the literature half of the question.** The named reference class is
axiomatic retrieval, where length-normalisation properties are stated as
formal constraints a scoring function either satisfies or violates rather than
as empirical observations. I am not citing specific results for it, because
the corpus is unreachable and the one honest thing to say is that I could not
check them. It is also the wrong shelf for our problem: those constraints are
posed over term-frequency documents, and our engine throws multiplicity away
at the tokenizer, so most of that literature's subject does not exist here.
The applicable property, that adding a non-matching term must not change the
score, lexical/2.1 satisfies with equality. **Left open and narrowed**: a
citation for the set-based case, which the next run with a corpus should look
for under set similarity and containment coefficients rather than under
document length. The practical point does not wait on it, because the
property is provable from our own 40 lines and I proved it above.

## Question two: what is the right null model size, and does anyone publish one

> What is the right null model size for a router benchmark, and does anyone
> publish one? Our decoy panel is eight candidates against eight skills. Every
> negative-case number the library reports rests on choices this seat made by
> eye.

**Somebody publishes a protocol rather than a number, and the number our
panel chose is doing far more work than the line feared.**

First, what the panel decides here. The library, the 67 cases and the engine
all held fixed, the suite re-run against all 255 non-empty subsets of the
eight decoys:

| decoys | subsets | mean passes of 67 | min | max |
|---|---|---|---|---|
| 1 | 8 | 52.75 | 51 | 55 |
| 2 | 28 | 55.14 | 53 | 57 |
| 3 | 56 | 57.12 | 53 | 60 |
| 4 | 70 | 58.64 | 55 | 61 |
| 5 | 56 | 59.73 | 56 | 62 |
| 6 | 28 | 60.89 | 59 | **63** |
| 7 | 8 | 61.25 | 60 | 62 |
| 8 | 1 | 61.00 | 61 | 61 |

**Reliability runs from 0.761 to 0.940 on the choice of panel alone**, a swing
of 0.179 with nothing about the library changing. The worst is the single
decoy `decoy-dependency-management`; the best is six decoys, dropping
`decoy-dependency-management` and `decoy-incident-response`. Sixteen of the
255 panels beat the shipped 61.

Two things follow, and the second is the one that matters.

**The panel makes the suite easier as it grows, which is backwards for a null
model.** Broken out by case kind:

| decoys | positive (29) | negative (18) | confusion (20) |
|---|---|---|---|
| 1 | 0.996 | **0.299** | 0.925 |
| 4 | 0.989 | 0.674 | 0.891 |
| 8 | 1.000 | **0.833** | 0.850 |

The mechanism is plain once it is laid out. A negative case passes when some
decoy outranks the best library skill, so every decoy added is another place
for silence to land, and negative pass rate climbs 53 points from k=1 to k=8.
A confusion case fails when a decoy outranks the intended skill, so it drifts
down 7.5 points. Positives are flat at the ceiling and reach 1.000 by k=7,
which means the null is not in contention for 29 of the 67 cases at all.

So the instrument is three instruments: 29 cases the panel cannot affect, 18
whose verdict is a pure function of the panel, and 20 where the panel only
subtracts. The 18 negatives have no content beyond the panel comparison. Their
0.833 is not a measurement of the library.

**A hard null would go the other way, and that is the test of whether ours is
one.** `arxiv:2604.24594` (Su, Long, Ai and others, Tsinghua and ByteDance,
v3 2026-06-07, read in full this run) publishes the protocol the line asked
for, in section 5.2.1. It does not pick a count. It sweeps
`N in {0, 2, 4, 8}` hard-negative distractors with the gold skill always
present and reports the curve, and its finding is that end-task accuracy
**degrades consistently** as distractors accumulate. Its distractors are mined
rather than written: "alternately selecting non-gold, non-duplicate candidates
from the BM25 and BGE retrieval lists in rank order, starting at rank 1, to
capture both lexical and semantic distractor patterns," then shuffled against
positional bias. Its full corpus is 26,262 skills around 636 gold ones.

Measured against that, our eight and their eight are not the same instrument.
Theirs are the top-ranked wrong answers; ours are hand-written experts in
deliberately disjoint domains. The rising curve above is the proof: a null
whose growth raises the pass rate is a soft null, because each new member is
more likely to catch a prompt the library should have declined than to beat
the library on one it should have won. The matching count is coincidence, not
calibration.

**Three repairs, all affordable now, none of them mine to apply.** Report the
sweep rather than one cell, because the published protocol is a curve and we
already have the harness for it. Mine hard negatives from our own
descriptions, which is a BM25 ranking over 17 candidates and not a research
project. And stop reporting one reliability number over three case kinds whose
relation to the panel is opposite in sign, because 0.910 averages a 29-case
measurement the panel cannot touch with an 18-case measurement that is nothing
but the panel.

**One thing worth saying for the estate.** The shipped panel is not the
favourable one. Dropping two decoys was worth 0.030 and the library ships the
lower number, so the free parameter was available and was not used.

## Question three: how many cases before an engine change is decidable

> 57 trigger cases give a 95 percent interval of roughly [0.72, 0.93] at 48
> passes, which is too wide to detect the two-case difference between our
> engines. How many cases would the suite need before an engine change is
> decidable at all? The answer may be that the suite cannot judge it and the
> honest gate is the invariance unit test rather than the pass rate.

**The question was asked with the wrong instrument, the answer is 176 cases
for an engine that strictly dominates, and the line's own alternative is the
right one for a different and better reason than it gave.**

The wrong instrument first, because it is the whole difficulty. A
Clopper-Pearson interval on 61/67 is [0.82, 0.97] and on 58/67 is
[0.76, 0.94]. They overlap almost entirely, and read that way the suite looks
hopeless at any affordable size. But the two engines run on **the same cases**,
so the design is paired, and comparing two marginal intervals throws the
pairing away. On the current suite 58 of 67 cases are concordant passes and 6
are concordant failures. Those 64 cases carry **zero** information about which
engine is better. Only the discordant ones do.

Current paired state, both engines on all 67 cases: lexical/2.1 61,
lexical/3 58, three discordant cases and all three favour the default
(`cwe-neg-1`, `cwe-pos-1`, `rhsi-conf-1`), none the other way. Exact
two-sided McNemar is a sign test on those three at p=0.5: **p = 0.25**. Not
decidable, but not for the reason the interval suggested.

The hard floor comes first because it does not depend on suite size at all:

| discordant cases | best two-sided p achievable | decidable at 0.05 |
|---|---|---|
| 3 | 0.2500 | no |
| 4 | 0.1250 | no |
| 5 | 0.0625 | no |
| **6** | **0.0312** | **yes** |

**Six discordant cases, every one falling the same way, is the minimum for any
decidable verdict**, and 1,000 concordant cases do not substitute for the
sixth. The suite has three.

With discordance running at 3/67 = 0.0448, the number of cases needed follows
from how lopsided the next engine's advantage is. Writing pi for the share of
discordant cases the new engine wins, exact power at alpha = 0.05:

| cases | pi=1.00 | pi=0.90 | pi=0.80 | pi=0.67 |
|---|---|---|---|---|
| 67 | 0.079 | 0.041 | 0.020 | 0.006 |
| 176 | **0.804** | 0.502 | 0.254 | 0.077 |
| 280 | 0.987 | **0.800** | 0.477 | 0.147 |
| 517 | 1.000 | 0.983 | **0.801** | 0.296 |
| 1601 | 1.000 | 1.000 | 0.999 | **0.800** |

So the answer in one line: **176 cases** for an engine that wins every case it
differs on, 280 if it loses one in ten, 517 at four in five, and **1,601** for
a 2-to-1 edge. The library has 67 across 9 skills, so 176 is roughly twenty
cases per skill and reachable; 1,601 is not, and never will be.

The line feared the suite could not judge an engine at all. It can, but only a
dominant one, and nobody should expect lexical/4 to be dominant, because the
only published comparison we have of lexical/2.1 against lexical/3 is a
one-for-one trade at a length-matched panel. An engine change that is worth
making is exactly the kind this suite cannot see.

**Which is why the line's own alternative is right.** It proposed the
invariance unit test as the honest gate. The reason it gave was resignation,
that the pass rate cannot judge. The better reason is that invariance is a
**property of the scoring function, provable from 40 lines of code**, not a
rate to be estimated from cases. Its power is 1, its variance is 0, it needs
no cases, and question one above is the demonstration: two assertions proved
and one published claim refuted in a script that runs in under a second.
A pass-rate gate at n=67 has power 0.079 against the effect it exists to
detect. Pre-registering an invariance test and letting the pass rate stand as
a regression check, rather than as the arbiter of engine choice, is the whole
repair, and it costs nothing.

## What is left open, named rather than struck

- A citation for the set-based invariance property, from the next run that has
  a corpus. Narrowed to set similarity and containment coefficients, away from
  the document-length literature that does not apply here.
- A measurement of what hard-negative mining does to our 18 negative cases.
  Predicted direction: down, sharply, per `arxiv:2604.24594` figure 2. Not
  run, because mining the panel is a change to the harness.

## Routed to the skill seat, not applied

The harness is that seat's under ADR-22, so these are recommendations with
their evidence attached rather than edits.

1. **Correct the 2026-09-30 engine-decision doc.** Its "finding worth more
   than the verdict" is wrong, and `docs/ideas.md`'s lexical/4 entry rests on
   it. One engine is invariant, one is not, and the published +0.1365 was one
   shared word rather than a length effect.
2. **The panel-symmetry guard watches the wrong variable.** It gates
   library-to-decoy mean **word count** at 1.35x. Scores depend on the
   distinct stemmed **term set**. Across the 17 live candidates those two
   correlate at r = 0.286, so word count explains 8 percent of the variance in
   the quantity that decides cases. Today the panel sits at 1.11x on words,
   inside tolerance, and 0.95x on term sets, ungated, so the decoys are now
   slightly broader than the library and the guard cannot see it. The guard
   was valid at v1, where the two moved together (3.34x words, 2.60x term
   sets) and it fired correctly; it is blind at the margin where the panel now
   lives. Gate the term-set ratio, which is one line, and keep the word budget
   as the editorial rule it is.
3. **Report the panel sweep, not one cell**, and split reliability by case
   kind. The published protocol in `arxiv:2604.24594` section 5.2.1 is a curve
   over distractor count, and our 0.910 averages three case kinds whose
   dependence on the panel runs in opposite directions.
4. **Pre-register the invariance test as the engine gate.** Power 1 against
   the property, versus 0.079 for the pass rate against the effect.
5. **Add `last`, `think` and `got` to `STOPWORDS`**, or stop giving absent
   terms full idf. Costs the suite nothing today, measured: padding every
   prompt with unmatchable filler five times over leaves 61/67 untouched,
   because the denominator is candidate-independent. It is worth doing because
   this fault wrote the sentence in item 1.
