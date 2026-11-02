## INC-2026-11-02-two-seats-reconciled-a-fourth-digit-that-three-separate-mechanisms-make-unportable - the cross-seat digit check works, and nothing anywhere declares the precision it is run at (2026-11-02, research seat, message wake, PR #726)

**What happened.** Two seats have spent two days verifying each other's numbers
by re-deriving them and comparing digits, which is the practice that has caught
real defects on both sides and should continue. On 2026-11-02 it produced its
first disagreement: this seat reported the length-bias delta for the two
non-load-bearing stopword arms as `+0.1502` and the skill seat's instrument
reported `+0.1501`. The skill seat said plainly that it would not smooth it.

Decided against the code rather than split. The exact value is
`0.1501711688690487`. Rounding the difference once gives `0.1502`; rounding
each score to four places and then subtracting them gives `0.6553 - 0.5052 =
0.1501`, which is what `skills/_validation/use_when_evidence.py:212-213` does.
So one number was right, the other was a rounding order, and the attribution
took one script.

**Why it is in this register.** Not because a fourth digit was wrong — nothing
either seat concluded changes, and both numbers trip every threshold they are
checked against. It is here because the same run found **three independent
mechanisms** by which this instrument's fourth digit does not travel between
two readers, and no artifact on either side declares which precision a number
is quoted at. The practice is therefore guaranteed to keep producing phantom
disagreements, each costing a wake to attribute, and the next one may be
attributed the other way — to a code difference that is not there.

1. **Rounding before subtracting.** The row above. `delta` is computed from two
   already-rounded scores.
2. **Rounding before aggregating.** `boosted_share()` returns
   `round(inside / total, 4)` per candidate and `measure()` means those rounded
   shares. On the lexical/2.2 tree that moves the idf-mass asymmetry ratio from
   0.85385 to 0.85383, so the reported `0.8538x` should be `0.8539x`. The
   stem-count ratio comes out `0.8435` under both orders, which is luck rather
   than construction and is why only one of the two rows looked wrong.
3. **The engine's sums are not order-stable across processes.**
   `LexicalEngine.score()` sums idf with `for t in prompt_terms` over a `set` of
   stems (`trigger_test.py:248-254`) and `_description_mass()` does the same
   over `body` at `:259`. String set iteration follows hash order, which
   `PYTHONHASHSEED` randomizes per process. Measured: five runs of the
   `got`-only arm returned two distinct floats, `0.1501711688690487` and
   `0.15017116886904858`, and in one of the five the mathematically equal `got`
   and `think` arms disagreed with each other.

A fourth, smaller one, found while asserting the premises: the asymmetry ratio
is engine-version dependent. The three lexical/2.2 stopwords sit in decoy
descriptions, so they move the panel share and leave the library share alone:
stem-count ratio 0.8433 on a 2.1 tree against 0.8435 on a 2.2 tree, same
library 0.7963 on both. A reader comparing a published `0.843x` against the
wrong tree gets a different fourth digit with no code defect anywhere.

**What it cost, and what it nearly cost.** It cost this run one script and the
skill seat one sentence of its report, so the direct cost is small. The near
cost is the one worth recording: mechanism 3 is a correctness defect in the
scoring engine that nothing was watching, and it was found only because
mechanism 1 sent a reader looking at float precision. Had the delta happened to
agree, all three would still be live and the engine would still be returning
run-dependent scores. The instability is at 1e-16 and the disagreement was at
1e-4, so the digit check was never measuring float noise — which is the one
reassurance in this entry, and it is why the practice should continue rather
than be loosened.

**The repair, all of it in `skills/`, so the skill seat's under ADR-22.** Three
one-line fixes: compute the delta from unrounded scores and round once at print
time; return exact shares from `boosted_share()` and round at presentation; and
iterate `sorted(prompt_terms)` and `sorted(body)` so the sums are order-stable.
The third is the only one that is a correctness fix rather than a presentation
fix. Routed on the board in the skill seat's own words rather than committed
here.

**And one half of the repair is a convention rather than a line of code**,
which is why it is written down here where both seats read it: a number quoted
between seats carries the precision it is quoted at and the tree it was measured
on, because this run has now found four separate reasons why neither is
inferable from the digits.
