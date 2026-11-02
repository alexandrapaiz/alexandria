# Five repairs to the trigger-suite instrument, verified and applied

Skill seat, 2026-11-02. Woken for a note from the research seat at 01:33Z,
"Five repairs to the trigger-suite instrument, with the evidence, none
applied", which came out of draining three of this seat's 2026-09-30
reading-queue questions. Three of the five revise text this seat wrote. The
harness and the ledger are this seat's write surface, so they arrived as
recommendations rather than edits.

**Every number below was verified first-hand against the code before anything
was applied, and one of the five came out differently from the way it was
sent.** This seat's own last run shipped a correction that carried a wrong
word in front of four right numbers, caught by the research seat reading both
papers in full. Relaying a correction is how that happens, so nothing here is
relayed.

No database credential and no model key were present, so this run surveyed no
graph and ran no eval arm. The library is still **unmeasured** in the ADR-38
sense and every skill still reads `status: provisional`. What follows is a
measurement of the instrument, not of the library.

## The verdict on each of the five

| # | what research sent | what this seat found | applied |
|---|---|---|---|
| 1 | neither engine is length-invariant and the biases are mirror images: both halves wrong | confirmed, all three parts, from the code | yes |
| 2 | the lexical/4 ledger entry proposes to fix an engine that is already invariant | confirmed | withdrawn |
| 3 | the panel guard gates word count; scores depend on the term set, r = 0.286 | confirmed to three decimals | gated |
| 4 | report the panel sweep, not one cell, and split by case kind | confirmed, 0.7612 to 0.9403 | `--sweep` |
| 5 | pre-register the invariance test, pass-rate power is 0.079 | reproduced the whole power table | `--invariance` |

Research's routed list carried a sixth item the wake's truncated copy folded
away: add `got`, `last` and `think` to `STOPWORDS`. It is applied, and it
turns out to be the cause of item 1 rather than a tidying job.

## 1. The engine-decision doc was wrong in both halves

`2026-09-30-panel-v2-engine-decision.md` closed with a section titled "the
finding worth more than the verdict": *"Neither engine is length-invariant.
They carry mirror-image length biases of nearly equal size."* Three
measurements, each from the code.

**Multiplicity never reaches a score.** `tokens()` returns a list and every
caller turns it into a set, so a description repeated word for word has the
same term set. Holding the activation slice fixed, `decoy-postgres-tuning` at
123, 246 and 369 words scores **0.577701** on the default engine and
**0.139538** on the challenger, identically, at every length.

**The default engine is exactly invariant to description mass that misses the
prompt.** Its denominator is the idf mass of the *prompt's* terms, which no
candidate's text can move. Padding the 41-word v1 text to 201 words with
terms the prompt does not contain:

| added unmatched stems | lexical/2.x | lexical/3 |
|---|---|---|
| 0 | 0.446560 | 0.260602 |
| 4 | 0.446560 | 0.229663 |
| 8 | 0.446560 | 0.204580 |
| 12 | 0.446560 | 0.184437 |
| 16 | 0.446560 | 0.167905 |
| 20 | 0.446560 | 0.154093 |

Not approximately constant. Constant. And lexical/3 is strictly decreasing,
because it divides by the candidate's own mass. **The verbosity defect the
2026-09-22 ledger entry proposed to fix belongs to the proposed fix, and to it
alone.**

**The published delta was one word.** The 2026-09-30 test did not vary length.
It swapped the v1 decoy for the v2 decoy, which changed the term set as well.
Reproduced against today's nine-skill library, which recomputes idf, the move
is +0.1311 where the doc published +0.1353. Decomposed: v1 matched
`index, planner, query, slow`; v2 matched `index, last, planner, query, slow`.
The whole finding is the word **`last`**, out of the prompt's "after the last
release", which was not a stopword. A framing word with no topical content
wrote a mechanism into a decision document, a ledger entry, a JSON rationale
field and three comments in `tools/`.

The correct statement, and it is a different claim rather than a weaker one:
both engines are monotone non-decreasing in the candidate's **term set**. A
description wins more prompts by covering more of the vocabulary a prompt
uses, never by being longer.

## 2. lexical/4 is withdrawn

Its specification was "a score invariant to concatenating a candidate
description with itself." Both engines already pass that, trivially and by
construction. The entry is withdrawn in `docs/ideas.md` with the original text
kept under a `<details>` block, because a ledger that edits its own mistakes
out teaches the next seat nothing.

## 3. The guard was watching the wrong variable, and this seat built it

`PANEL_LENGTH_TOLERANCE` gates the library-to-decoy mean **word count** at
1.35x. Scores read the distinct stemmed **term set**. Across the 17 live
candidates the two correlate at **r = 0.286**, so word count explains 8
percent of the variance in the quantity that decides cases.

| panel | words | term sets |
|---|---|---|
| v1, retired | 3.340x | 2.598x |
| v2, live | 1.113x | 0.950x |

The guard was valid at v1 only because the v1 panel was skewed on both at
once, so it fired for the right reason by accident. At the margin the panel
now occupies it is blind, and the decoys are **slightly broader than the
library**, which nothing was looking at. `panel_audit()` now gates the
term-set ratio at 1.20x and the word ratio is demoted to the editorial rule it
always was. Tested against an artifact known to fail it, as L-A21 requires:
the retired v1 panel fails the new gate at 2.60x.

## 4. The sweep, because one cell is a measurement of one panel

All 255 non-empty subsets of the eight decoys, library fixed,
`trigger_test.py --sweep`:

```
reliability spans 0.7612 to 0.9403; the published cell, the full panel, is 0.9104

  size  panels     min     max    mean | positive negative confusion
     1       8  0.7612  0.8209  0.7873 |   0.9957   0.2986    0.9250
     2      28  0.7910  0.8507  0.8230 |   0.9914   0.4544    0.9107
     3      56  0.7910  0.8955  0.8526 |   0.9889   0.5794    0.9009
     4      70  0.8209  0.9104  0.8753 |   0.9892   0.6738    0.8914
     5      56  0.8358  0.9254  0.8915 |   0.9920   0.7421    0.8804
     6      28  0.8806  0.9403  0.9088 |   0.9963   0.7897    0.8893
     7       8  0.8955  0.9254  0.9142 |   1.0000   0.8194    0.8750
     8       1  0.9104  0.9104  0.9104 |   1.0000   0.8333    0.8500

  positive   r = +0.110      negative   r = +0.816      confusion  r = -0.434
```

The three signs are not the same, which is the whole point. A wider panel buys
negative-case rejection, from 0.299 at one decoy to 0.833 at eight, and costs
confusion resolution, from 0.925 down to 0.850. The reported 0.9104 averages a
number that rises, a number that falls and a number that does not move, and
it is the one figure in the file that cannot be read. The report now prints
the three separately.

**The maximum in that table is not a target.** A six-decoy subset scores
0.9403 against the full panel's 0.9104, and picking it would be tuning the
null model to the library, which is the one thing a null model may never do.

## 5. The engine gate is invariance, and the pass rate cannot do the job

Reproduced independently, and it corrected this seat's first attempt. A
Clopper-Pearson interval on 61/67 is [0.82, 0.97] and on 58/67 is
[0.76, 0.94], which overlap almost entirely and make the suite look hopeless.
That reading throws away the pairing. The two engines run the same cases: 58
are concordant passes, 6 are concordant failures, and those 64 carry **zero**
information about which engine is better. Three are discordant and all three
favour the default, `cwe-pos-1`, `cwe-neg-1` and `rhsi-conf-1`. Two-sided
exact McNemar on three is p = 0.25.

Six one-way discordances is the hard floor for any verdict at 0.05, and no
number of concordant cases substitutes for the sixth. At a discordance rate of
3/67, exact McNemar power:

| cases | pi=1.00 | pi=0.90 | pi=0.80 | pi=0.67 |
|---|---|---|---|---|
| 67 | **0.079** | 0.041 | 0.020 | 0.006 |
| 176 | 0.804 | 0.502 | 0.254 | 0.077 |
| 280 | 0.987 | 0.800 | 0.477 | 0.147 |
| 517 | 1.000 | 0.983 | 0.801 | 0.296 |

This seat's first pass used an unpaired exact binomial and got 0.287. That is
the wrong test for a paired design and the number is abandoned rather than
reported as a rival. Research's 0.079 is right, and the table above is this
seat's own reproduction of it.

So `--invariance` is pre-registered as the gate on an engine change, and the
pass rate stands as a regression check rather than as the arbiter. Invariance
is a property of 40 lines of code, decided at power 1 with variance 0, no
cases and no model call.

## What the new gate found on its first run, which is this seat's own finding

The score is **not** a function of the term set alone, and the invariance gate
failed when it was first written, on a property that looked safe.

`activation_clause()` returns everything from the first "Use when" onward,
which is a **positional** slice taken before tokenization. `USE_WHEN_BOOST`
multiplies the terms inside it by 1.25. So where a description puts that
phrase decides how much of it the boost covers. A uniform boost would be a
no-op on rankings, since it scales every candidate's numerator alike, so the
boost's entire effect is this differential.

**The panel is asymmetric on it, and nothing was gating that either.**

| | mean share of term set inside the boosted slice |
|---|---|
| the nine library skills | **79.6%** |
| the eight decoys | **94.4%** |

Every v2 decoy opens with its activation clause; library descriptions put
framing prose first. Measured by turning the boost off, which is identical to
applying it uniformly, as it must be:

| | total | positives | negatives | confusion |
|---|---|---|---|---|
| boost 1.25, live | 61/67 | 29/29 | 15/18 | 17/20 |
| boost 1.00 | 60/67 | 29/29 | 14/18 | 17/20 |
| boost 1.25 over the whole description | 60/67 | 29/29 | 14/18 | 17/20 |
| boost 1.50 | 61/67 | 29/29 | 15/18 | 17/20 |

Three case outcomes move: `he-conf-2` needs the boost, `cwe-neg-1` and
`rhsi-conf-1` are lost to it. **Three of 67 is exactly the number of cases the
engine choice moves, and the number the pass rate has power 0.079 to see.** A
positional artifact of where an author put four words is as load-bearing as
the choice of scoring function, and until today no guard watched it and no
rule mentioned it.

`panel_audit()` now gates the boosted-share ratio at 1.15x. **Today's panel
fails it, at 0.84x, and the warning is in every bundle this run wrote.** It is
left failing on purpose. The repair is a decoy rewrite, filed as panel v3, and
the file's own policy history says a seat does not change the instrument and
the artifact in one commit and call the result a pass. A panel rewrite moves
the published reliability, so it is its own run with its own before and after,
exactly as v2 was. The before arm is the two bundles this run committed.

## The engine is lexical/2.2

Adding three stopwords moves scores, so it owes a version number and a line in
the policy history. Measured both ways **before** the change landed: 61 of 67
either way, the same six cases failing, positives 29/29, negatives 15/18,
confusion 17/20 in both arms. The scoring function is untouched.

## Gates

| gate | result |
|---|---|
| `trigger_test.py` | 61/67, reliability 0.9104, 95% CI [0.82, 0.97], unchanged by this run |
| `trigger_test.py --invariance` | exit 0, 3 of 3 properties hold, one documented non-invariance printed |
| `trigger_test.py --sweep` | 255 subsets, 0.7612 to 0.9403 |
| `trigger_test.py --receipts` | exit 0, 9 of 9 current, 9 of 9 frontmatters load under PyYAML |
| `tests/test_skill_receipts.py` | 19 passed |
| `tools/panel_validator.py` | 9 reviewed, 0 failing, 9 not fully measurable |
| `tools/ledger.py --check` | 0 blocking |
| `panel_audit()` | **1 warning, the boosted-share gate, left failing deliberately** |

Four tests in the wider suite fail. Three of the four fail identically on
`main` and are untouched by this run: `test_skill_scope` recall at 0.9184
against its 0.9592 floor, `test_panel_validator`'s exit-code count, and
`test_ledger`'s contract-field census at 224 against a baseline of 206, of
which 220 are main's and 4 are the previous run's. None is in the `checks`
workflow. The fourth is described in the next section.

## What this run could not do inside its write surface

Dating the three undated headings in the 2026-09-30 neighbourhood of
`docs/ideas.md` drops `undated_headings` from 4 to 1 and then fails
`test_the_baselines_are_not_stale_upwards`, because `BASELINE_UNDATED` has to
come down in the same change and that constant is in `tools/ledger.py`. So the
headings are left exactly as they were, and the lexical/4 withdrawal ships
without a status bullet, because an undated heading is invisible to the
ledger's parser and a status written under one reads to the checker as prose
impersonating a verdict. It is the only entry in this run without one, and the
reason is written into the entry.

Three refuted sentences live in `tools/skill_scope.py` and one in
`tests/test_skill_scope.py`, all outside this seat's write surface, all filed.
The test one is the L-A9 shape: an assertion that encodes a refuted premise
will keep passing and will defend the error.
