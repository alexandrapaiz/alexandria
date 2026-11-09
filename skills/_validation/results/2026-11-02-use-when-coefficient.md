# USE_WHEN_BOOST against the two papers that measure the field

> **Corrected 2026-11-02, after this file was written.** Three things in the
> text below changed and the file is amended in place rather than reissued,
> because it is the citation receipt the coefficient decision rests on.
> (1) The two arXiv identifiers were transposed throughout, consistently, here
> and in `use_when_evidence.py` and in all three reading-queue lines. The claim
> content was right and only the ids moved. 2510.22670 is "Tools are
> under-documented" (the add-one/one-out ablation, Tool-DE, the 41.6 percent
> audit) and 2602.05366 is "Multi-Field Tool Retrieval" (Table 5, the learned
> field weights). Caught by the research seat, confirmed here by fetching both.
> (2) The 0.269x to 1.363x range is Table 5's `examples` row over its
> `description` row. That table has no when-to-use row at all, and whether
> `examples` is our field is now an open queue line rather than an assumption.
> (3) The idf-mass ratio was computed by rounding each candidate's share and
> then meaning the rounded values. It is now exact until print, which moves it
> by one in the fourth decimal.
>
> **Amended again, later on 2026-11-02, and this one withdraws a number rather
> than correcting one.** The open queue line in (2) was answered by the research
> seat from both papers' full text, and it resolved AGAINST this file.
> 05366's `examples` is 22670's `example_usage`, which holds query text, and not
> its `when_to_use`, which holds the activation clause: the per-field definition
> says "representative user intents", the query side aligns the field with "a
> concrete user utterance", and Table 4's cells hold strings like "clean up
> podcast recordings by removing background noise". So this is a wrong-FIELD
> citation and not a wrong number. **Presence survives, magnitude is withdrawn,
> and `USE_WHEN_BOOST`'s 1.25x rests on no published weight at all.** Every
> sentence below that compares 1.25 to 0.269-1.363, or that says central
> tendency runs the opposite way, is withdrawn and left standing so the
> withdrawal is legible next to what it withdraws. Two things survive it: the
> paper's own methodological conclusion that no constant is right, and this
> file's sweep, which is the actual reason the coefficient was not retuned. One
> cell both seats missed is added by the same note, Table 4 Gorilla on BM25,
> `examples` 42.3 against `description` 21.4 for 1.977x, not commensurable with
> Table 5 and adaptive per query. Reconciliation:
> `docs/research/notes/2026-11-02-field-identification.md`.

2026-11-02, skill seat. Instrument `skills/_validation/use_when_evidence.py`,
machine-readable bundle `2026-11-02-use-when-coefficient.json`, console form
`.txt`. No database and no model call: every number is derived from this
repository's own descriptions, decoy panel and 67 trigger cases.

## Why this exists

`USE_WHEN_BOOST` has multiplied a candidate's activation-clause terms by 1.25
since lexical/2, and nothing ever justified the number with evidence. It was a
reasonable editorial intuition promoted to a numeric coefficient. On 2026-11-02
this seat queued the question of whether any paper measures the field at all,
and recorded that it could not name a candidate id, which was itself the
finding: the one coefficient in our engine that no paper supported was also the
one nobody had gone looking for.

The research seat answered it with two ids and read both in full. The answer
runs against the coefficient rather than for it.

## What the literature says

`arXiv:2510.22670` ablates a when-to-use field add-one and one-out on a dense
and a sparse retriever over thirty-five unified datasets, and keeps it. The
field its authors drop is example-usage. So having the clause is supported.
Read its section 4.1 and not its 2.2, which carries a sentence naming the wrong
field that reverses the finding.

`arXiv:2602.05366` is the only source either seat can find that measures a
weight on the field rather than its presence. It learns per-field weights and
publishes them: the usage-scenario field runs 0.269x to 1.363x of the
description field's weight across six dataset and retriever cells, median
0.695x, and it sits below the description in five of the six.

Ours is a fixed 1.25x above it. So the literature supports the clause, rules
out a constant in either direction, and runs the opposite way on central
tendency.

## Everything the research seat sent, reproduced first

Nothing below was taken on the note's word. The asymmetry reproduces to the
digit under the shipped definition: library boosted share 0.7963 against panel
0.9441, ratio 0.8435x, past the 1.15x tolerance.

One gap found while reproducing it, and it is small. `panel_audit()` measures
the boosted share as a count of stems, while `score()` multiplies idf mass.
Measured on idf mass the same asymmetry is 0.8048 against 0.9426, a 0.8538x
ratio. Both trip the tolerance, so the finding stands either way, and the gap
is recorded rather than repaired.

The stopword decomposition reproduces, with one digit of difference the seat
reports rather than smooths: the research seat sent 0.1502 for the two
non-load-bearing arms and this instrument gets 0.1501.

| stopword arm | 41-word decoy | 123-word decoy | delta |
|---|---|---|---|
| none of the three (lexical/2.1) | 0.4466 | 0.5777 | +0.1311 |
| all three (lexical/2.2) | 0.6850 | 0.6850 | 0.0000 |
| `last` only | 0.5052 | 0.5052 | 0.0000 |
| `got` only | 0.5052 | 0.6553 | +0.1501 |
| `think` only | 0.5052 | 0.6553 | +0.1501 |

Only `last` was load-bearing. Stripping either of the other two alone grows the
delta, because both sit in the prompt and in neither description, so removing
one shrinks the denominator and leaves the numerator untouched. The case for
`got` and `think` is that they are framing, which is an editorial argument, and
not that they carried the length bias, which they did not.

## The three arms, on every field the verdict reads

This is the shape of the defect this seat reported to the research seat and
then committed itself. A uniform boost is a no-op on the ranking and not on the
verdict, because `route()` also reads `library_score >= FLOOR` and
`abs(null_margin) < NARROW_MARGIN`, both against absolute numbers, and a
uniform boost scales both.

| arm | fired | passed | narrow flags | under floor |
|---|---|---|---|---|
| boost off | 52 | 60 | 7 | 1 |
| boost 1.25 live | 50 | 61 | 6 | 1 |
| boost 1.25 uniform | 52 | 60 | 6 | 1 |

Off and uniform agree on all 67 fired decisions and disagree on one narrow
flag, `he-conf-2` at +0.0179 against +0.0224, across the 0.02 threshold.

The floor is untested rather than satisfied. `sle-neg-1` is the one case under
it at 0.0492, and it also trails its closest decoy by 0.0629, so the ranking
clause silences it before the floor is ever consulted.

## The composition, which a net of plus one hides

The boost moves three of 67 cases, and the three are +2 and -1 rather than a
net of one. It wins `cwe-neg-1` and `rhsi-conf-1`, and it loses `he-conf-2` at
-0.0034. `he-conf-2` passes at boost off and passes under a uniform boost, and
fails only live.

So today's 61 of 67 is five library failures and one instrument artifact, and
that is now confirmed by two independent counterfactuals rather than inferred
from a margin. The five are `ams-neg-1`, `ei-neg-2`, `pt-neg-1`, `ac-conf-2`
and `cwe-conf-1`. The artifact is `he-conf-2`.

## The measurement this run adds, and the one that decides the coefficient

The coefficient swept twice over the range the literature publishes, once
through `activation_clause()`'s positional slice as shipped, and once applied
uniformly to every candidate's whole term set, which is what a unified schema
would do.

| boost | in published range | live passed | live under floor | uniform passed | uniform under floor |
|---|---|---|---|---|---|
| 0.269 | yes | 48 | 11 | 56 | 25 |
| 0.5 | yes | 56 | 1 | 60 | 10 |
| 0.695 | yes | 59 | 1 | 60 | 6 |
| 1.0 | yes | 60 | 1 | 60 | 1 |
| 1.25 | yes | 61 | 1 | 60 | 1 |
| 1.363 | yes | 61 | 0 | 60 | 0 |
| 1.5 | no | 61 | 0 | 60 | 0 |

Through the positional slice the pass rate runs 48 to 61. Applied uniformly,
every arm at 0.5x and above scores exactly 60, and the only movement below that
is the floor collapsing rather than the clause earning anything.

So all of this suite's apparent preference for a high coefficient is the 0.84x
asymmetry. Tuning 1.25 on the pass rate would be tuning on a confound.

## What is therefore not done, and why

The coefficient is not retuned. Three reasons, and none of them is caution.

The literature rules out a constant in either direction, so moving 1.25 to
0.695 would replace one unsupported constant with a better-sourced unsupported
constant.

Our own suite cannot choose the number, because the only arm in which it
responds is the arm carrying the confound.

And `arXiv:2602.05366` lands the same warning independently. The variant in
that paper which applies field weights to raw unstandardized documentation is
the one that fluctuates, and its conclusion is that a unified schema is the
prerequisite. A positional slice of free prose is that variant, and the 0.84x
measured here is what it costs. So the repair is a declared field rather than a
tuned coefficient, filed in `docs/ideas.md`, and the panel rewrite already
queued as decoy panel v3 comes before either.

## Status of the engine

Unchanged. Every edit to `trigger_test.py` in this run is a comment, so
`ENGINE_VERSION` stays at lexical/2.2 and the suite scores 61 of 67 with the
same six failures before and after. `--invariance` holds 3 of 3 properties,
`tools/skill_eval.py --check` exits 0 at 9 of 9 conformant eval files, and
`tests/test_skill_receipts.py` passes 26 of 26.
