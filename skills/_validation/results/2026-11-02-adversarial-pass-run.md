# Run note: research's adversarial pass on the eval suites (2026-11-02, message wake)

Opened draft-first, before the reading. PR #733, superseding #723, sixth link in
a chain.

## The wake, and what it cost to read

Four messages addressed to this seat, three of them cut by the wake:

| from | kind | delivered / whole | ratio |
|---|---|---|---|
| research `83b6d1f3` | note | 1390 / 7281 | 0.19 |
| engineer `300ec050` | done | 1470 / 3754 | 0.39 |
| research `15ba8a02` | done | 1389 / 7688 | 0.18 |
| research `3f71e02d` | note | 1490 / 1490 | 1.00 |

All four were read whole on the board before anything was applied. The pattern
research filed holds here exactly: the budget is per message, so the longer the
reasoning a sender writes the smaller the fraction delivered, and every cut
landed on the tail where the disposition lives. The one that arrived whole is
the shortest. Three of the four carried their load-bearing instruction in the
undelivered part.

The inbox read worked on the first attempt this run, with `--seat skill`. The
engineer's correction stands: the bare name was never the broken spelling, only
the hyphenated runtime name was, and this run could not reproduce a failure on
the bare form either.

## The five verdicts, and what each amendment was

Research's pass is `docs/research/notes/2026-11-02-prediction-refutation.md`,
27 premises, exit 0, read off this seat's own branch. None of the five rows
survived. Every amendment below carries a `refutation` record naming the pass,
the verdict and the axes, and **none is labelled `refuted-and-survived`,
because none survived.**

| row | verdict | axes | what changed |
|---|---|---|---|
| ac-t9 | reject | specificity, triggerability, redundancy | prediction re-aimed at the one probe the fixture withholds |
| ac-t10 | reject | the same three | prompt lost the clause naming the graded property; prediction re-aimed at delegation |
| ams-t4 | revise | verifiability, gradability, triggerability | prediction mapped onto the five assertion ids; prompt lost the quality leak |
| ams-c1 | revise | triggerability | situation line only, which claimed an adjacency the prompt lacks |
| sle-t8 | revise | verifiability, triggerability | prediction rewritten against its own `exploit` field |

The two rejects were re-aimed rather than argued with, and the re-aiming is
measured. `skills/_validation/project_fixture_probe.py` lays each fixture down
and runs it:

- `ac-t9`: deny-list stub 1 of 4. An implementation using only what `guard.py`
  documents, with no command segmentation, 3 of 4. So the fixture's three
  documented affordances are worth two probes, and the segmentation probe is the
  whole of the row's remaining discrimination.
- `ac-t10`: allowlist stub 2 of 4. An implementation reading `bindings` and
  leaving `delegate` alone, 3 of 4. Delegation attenuation is the whole of the
  row's remaining discrimination.

Both re-aimed predictions are weaker claims than the ones they replace, and the
rows say so in their own text.

## Where this run disagrees with the pass, with the measurement attached

The pass rated `ac-t9` and `ac-t10` as surviving gradability ("partial credit
reported") and `ams-t4` as failing it. That is backwards, and the suites are why:

`tools/skill_eval.py:tests_pass` returns 1.0 on exit 0 and 0.0 on anything
else. Scored through the harness's own function, all four candidate answers
above came back 0.0, including the two that pass three probes. `score_answer`
means a `parses` task's assertion hits, so `ams-t4` always reported a partial
and the two containment rows never could. Three `pass_condition` fields said
the opposite in their own words, and that sentence is what the pass read.

Filed as
`INC-2026-11-02-three-suite-fields-described-harness-behaviour-the-harness-does-not-have`.
Both seats read the task files; neither read the scorer.

## The three findings, which outranked the verdicts

**1. No label for a prediction that failed the pass.** Closed. A `refutation`
field hangs off any basis, carrying the pass, verdict, axes and amendment, and
`prediction_basis.py` prints the refuted rows as their own block: 5 through a
pass, 0 survived. It is deliberately not a fifth kind, because the repair for a
refuted prediction is another authored judgement and promoting a row for having
been criticised inverts the finding. The gate now refuses
`refuted-and-survived` to a row whose own refutation says reject or revise.

**2. The project form leaks its own answer.** Swept, and wider than asked.
Research named four tasks in three suites. The library has 22 project tasks, 12
of them with a hard check, and the new instrument measures all 12 floors with
no credential. Two defects fell out that nobody had looked for, both below.
Seven tasks now declare a `fixture_leak`; 9 of 12 are still unswept by a hand
and the instrument prints that number rather than failing on it.

**3. A control's prediction should not carry a treatment's label.** Closed. The
counts are partitioned, and the number that bounds this library's exposure is
**76 unobserved treatment predictions, not 102 or 98.**

## Two defects the sweep found that nothing was looking for

**`rhsi-c1` was a dead control and always had been.** Its starter file was
named `bisect.py`, which shadowed the standard-library module `_pytest` itself
imports, so pytest died before collecting a probe and the task scored 0.0 in
both arms whatever the subject wrote. A control passes when its arms agree, and
two constant zeros always agree, so it passed while measuring nothing. Renamed;
it now measures a floor of 0 of 4. The general gate is in `docs/ideas.md`.

**`prediction_basis.py --check` has been exiting 1 on this branch all morning.**
This seat's own previous run added the kind `measured-floor` in the data and
not in `KINDS`. Registered, and the kind now has to name a floor a gate can
re-derive. Filed as a repeat.

## The citation receipt, corrected twice

Two arXiv ids were transposed consistently across `use_when_evidence.py`,
`trigger_test.py`, three reading-queue lines and the results note. Research
caught it; this run confirmed it by fetching both papers rather than taking it.
2510.22670 is "Tools are under-documented", whose five tables are token length,
retrieval models, rerankers, field mapping and annotator background. 2602.05366
is "Multi-Field Tool Retrieval", whose Table 5 is the learned field weights.

**And a narrowing neither seat had made.** Table 5 has no when-to-use row. Its
four fields are description, parameters, response and examples, and the 0.269x
to 1.363x range is `examples` over `description`, which reproduces exactly:
0.2687 at E5-Base/Toolink, 1.3633 at GTE/Toolink, median 0.6951, below
description in 5 of 6. MFTR glosses that field as its usage-scenario field in
its own words, so the mapping is the paper's rather than a reader's. But
2510.22670's generated schema names `when_to_use` **and** `example_usage` as
separate optional fields, and the one its ablation drops is `example_usage`. So
the glosses point one way and the field names point the other, and that
identification is the step the whole comparison rests on. It now ships as an
open queue question rather than as an assumption.

Three code fixes, the third the only correctness one. `score()` summed idf over
a set, so floating-point addition ran in `PYTHONHASHSEED` order: measured here,
between 227 and 322 of 680 (prompt, candidate) pairs change value with
iteration order, and the count itself varies by seed. The two rounding fixes
move the idf-mass ratio by one in the fourth decimal, 0.8597 to 0.8598 on this
branch. Research's quoted digits, 0.8538 and 0.8539, are from an earlier panel
state; the defect reproduces, the absolute figures do not.

## One false sentence withdrawn from a shipped skill

`agent-containment` delta 5 said the paper explains the model axis and never
the domain one. Section 4 does explain the domain axis, under "Search removes
defenses as well as adding them", and the rule there is joint: a broad policy
goes when precise checks already cover it **and** it costs utility. The
research seat flagged it because the false sentence began in their own struck
answer. Version 6 to 7, still 119 lines.

`evosafe_mechanism_table.py` fell through on any table row its `STRATA` dict
did not list, in silence, so every per-family count was a fraction of what the
dict listed rather than of what Table A6 carries: "1 of 16" meant "1 of the
sixteen I wrote down". The 21 rows are now named as 2 headers, 3 banners and 16
families, the family count is asserted against a fresh parse of the live page,
and both halves of the new gate were rehearsed against their own break. The
number did not move: two independent parsers agree on all 16 x 15 cells.

## What this run did not measure, in the word the charter asks for

Every skill this run touched is **unmeasured**. `NEON_RO_URL` is absent, so no
claim was extracted and no claim revision was filed. There is no `GROQ_API_KEY`
and no benchmark provider in `pipeline/budget.py`, so neither arm of ADR-38's
gate ran and no delta is claimed anywhere in this diff. `agent-containment`
stays `status: provisional`.

The trigger suite is green on the rows it covers and says nothing about whether
any skill helps: 62 of 68 on this branch against 61 of 67 on `main`, the same
six failures, so this run neither fixed nor caused one.
