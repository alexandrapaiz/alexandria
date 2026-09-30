# The decoy panel at the library's word budget, and what it says about the engine

Skill seat, 2026-09-30. Sprint item 4, carried from this seat's own
recommendation in PR #83 and missed on two scheduled runs. No database
credential was present in this run, so no skill was extracted and the
whole run went to the instrument.

## The question as it was asked

Rewrite the decoy panel to the library's own word budget, add the
length-warning check from incident 31 to the runner, then re-measure
lexical/2.1 against lexical/3 on the same cases and say which engine
wins now that the confound is removed.

## The confound, measured

The panel's eight decoys averaged **40.8 words**. The library's eight
descriptions averaged **127.1**. That is a **3.11x** gap.

It matters because of how the default engine scores. `LexicalEngine.score`
divides the idf-weighted overlap by the idf mass of the prompt's terms and
never by the candidate's own. A longer description therefore covers more of
any prompt without paying for the coverage, so it strictly dominates a
terser one on every prompt both address. The null model was weaker than
the thing it was built to null, which means every negative case the
library passed was passed partly on length rather than on topic.

## The panel, rewritten

All eight decoys now sit at **122.2 words on average, range 117 to 129**,
inside the 100 to 150 budget the library itself occupies. The ratio is
**1.04x**.

Two disciplines held while rewriting, both recorded in `decoys.json`:

- **Domain coverage is fixed from v1.** Only length changed. Each decoy
  was rewritten as an expert in that same domain would write it at the
  library's length.
- **Vocabulary was not scrubbed.** Removing terms the library also uses
  would weaken the null and inflate the library's pass rate, in the
  other direction from the length gap. Natural overlap stays and is
  measured instead: 20.3 percent of decoy stems were shared with the
  library at v1 and 21.1 percent at v2, so widening the decoys did not
  quietly import the library's vocabulary.

One coverage regression was caught before shipping. The first v2 draft of
`decoy-product-copy` dropped v1's explicit "a chatbot persona and its
system prompt", and case `he-neg-2`, a request for a support chatbot's
system prompt, failed under both engines because the null no longer
covered it. The clause was restored. Restoring coverage v1 already had is
fidelity to the instrument. Adding coverage v1 did not have, to turn a
case green, would be tuning, and was not done.

## The four cells

All four runs use the same library, so each row varies one thing. The
retired panel is kept at `decoys-v1-retired.json` so the table
re-runs.

| panel | engine | result | reliability | 95% CI | panel ratio |
|---|---|---|---|---|---|
| v1 | lexical/2.1 | 45/57 | 0.79 | [0.66, 0.89] | 3.11x |
| v1 | lexical/3 | 49/57 | 0.86 | [0.74, 0.94] | 3.11x |
| v2 | lexical/2.1 | 48/57 | 0.84 | [0.72, 0.93] | 1.04x |
| v2 | lexical/3 | 48/57 | 0.84 | [0.72, 0.93] | 1.04x |

The mechanism predicted the direction and the prediction held. Fixing the
panel gained lexical/2.1 exactly three cases, and all three are
negatives: `asm-neg-2`, `ei-neg-2`, `cwe-neg-1`. Those are cases where a
library skill had been beating the null on a prompt it should have stayed
silent on, which is what a systematically shorter null produces.

## Which engine wins

Neither. They tie at 48 of 57, and the question turns out to have been
malformed.

The four-case gap at panel v1 was not a measurement of engine quality. It
was lexical/3 partially compensating for a defect in the decoy panel. Fix
the panel at its source and the compensation buys nothing, because there
is nothing left to compensate for.

The engines are not even agreeing case by case. They disagree on exactly
two, in a one-for-one trade: lexical/2.1 fails `rhsi-conf-1` and passes
`cwe-neg-1`, and lexical/3 does the reverse. A tie on totals with two
cases traded is a different result from two engines behaving alike, and
it is reported that way rather than as agreement.

**So lexical/2.1 stays the default.** Not because it won, but because it
is the pre-registered policy and an engine change needs evidence to
justify it. After this run there is none. That reasoning would have gone
the other way on the v1 numbers, which is the point of removing the
confound before deciding rather than after.

## The finding worth more than the verdict

Neither engine is length-invariant. They carry mirror-image length biases
of nearly equal size.

The test holds candidate, prompt and topic fixed and varies only length.
Scoring `decoy-postgres-tuning` against "Our Postgres query got slow
after the last release and I think the planner stopped using the index":

| engine | decoy at 41 words | decoy at 123 words | change |
|---|---|---|---|
| lexical/2.1 | 0.4499 | 0.5852 | +0.1353 |
| lexical/3 | 0.2651 | 0.1424 | -0.1227 |

lexical/2.1 pays a candidate for length. lexical/3 fines it, because its
precision term divides by the description's own idf mass, so a longer
description dilutes itself against a narrow prompt. The magnitudes are
close enough that at a length-matched panel the two biases land on the
same score, which is exactly what the table shows.

Three consequences.

1. **The panel's relative length decides negative cases under either
   engine.** Adopting lexical/3 would not have made the instrument
   length-invariant. It would have reversed the direction of the bias and
   left the validity of every negative case resting on how long the
   decoys happen to be.
2. **The panel-symmetry check is load-bearing, not hygiene.** It is the
   only thing standing between the suite and a silent return of this
   confound, in either direction, the next time anyone edits a
   description.
3. **A length-invariant engine is the real fix**, and it is now a
   specific proposal rather than a preference. Filed in `docs/ideas.md`
   as lexical/4.

## The guard, and the evidence it works

Incident 31 said what would catch this: a length check inside
`trigger_test.py`, because the runner is the one thing every skill run
executes before shipping. The rule already existed in
`prompts/skill-extract.md` and had failed twice, because a rule in a
prompt is checked when someone reads the prompt. That is L-A22 in
`docs/standards/lessons.md`, the gate goes in the command.

Two checks now run on every invocation, and both write their numbers into
every bundle under `length_audit`, so a result describes its own
instrument:

- a per-description warning past the 150-word budget, and
- a panel-level warning when the library to decoy mean-length ratio
  leaves the 1.35x tolerance.

L-A21 says a gate is trusted only after it is tested against an artifact
known to fail it. Pointed at the retired v1 panel, the guard fires:

```
warning: decoys-v1-retired.json: decoy panel averages 41 words against
the library's 127, a 3.12x gap past the 1.35x tolerance; negative cases
are partly decided by length rather than topic
```

It also caught something real on its first run against the live library.
`evaluation-integrity` stood at **151 words**, one word past a budget
stated on 2026-09-24 that nothing had measured since. Cut to 148, wording
only, no coverage change, and the skill is now version 4. A budget that
nothing measures is a budget that drifts one word at a time, and this is
what that looks like six days in.
