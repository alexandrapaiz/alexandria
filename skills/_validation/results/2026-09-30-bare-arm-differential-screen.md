# Bare-arm differential screen, 2026-09-30

ADR-38 clause 4: an eval task counts only if the bare subject fails it or
scores partial on it, measured **before** the with-arm runs. This file is that
measurement for the six non-fixture skills, and it is the evidence for every
cut in the same pull request.

## What was measured, and what was not

- **Subject.** The benchmark-class model (Claude Opus 5, the model running the
  skill seat), in a **fresh context with no skill text**, instructed to answer
  from its own knowledge and to read no file in this repository and use no
  tools. Four candidate prompts per skill, one context per skill, answers
  capped at 250 words each.
- **Arm.** Bare only. This is the pre-screen, not the with-versus-without
  delta. No with-arm was run and no delta is reported here.
- **Grading.** By the skill seat against a check written **before** the prompt
  was sent, naming the specific finding, number and decision rule the section
  claims. `pass` = the bare answer states the rule and its threshold.
  `partial` = states the direction, omits the number or the load-bearing half.
  `fail` = omits it, or recommends against it.

## Three limits, stated because they bound every conclusion below

1. **The cheap open-model arm is unmeasured.** `tools/skill_eval.py` (ADR-36)
   has not landed on `main`, and neither `MOONSHOT_API_KEY` nor `GROQ_API_KEY`
   exists in this sandbox, so `pipeline/llm.py`'s provider walk has nowhere to
   go. The 2026-09-12 qwen-27B numbers in ADR-38 remain the only open-model
   measurement. A section cut here as non-differential on a frontier subject
   may still be a real delta on a 27B one, and ADR-38 clause 6 makes the
   frontier subject the one that decides `status: active`, which is why the
   cuts follow it.
2. **Subject and grader are the same model family, and the grader wrote the
   skills.** That biases the screen toward *over*-crediting the bare arm: a
   grader who knows the intended answer reads it into a near miss. The bias
   therefore shrinks the differential set and makes a delta harder to earn,
   which is the conservative direction, but it is not no bias.
3. **Four prompts per skill share one context**, so a later answer in a skill
   can be primed by an earlier one. Same direction: priming inflates the bare
   arm and drops tasks from the differential set.

## Two rounds

Round 1 screened four candidates per skill, chosen as the sections the seat
expected to keep. Round 2 screened the seven sections round 1 had left
unmeasured, and it cut three more after the first drafts were written. Both
rounds are below; the round column says which.

## Results

| candidate | section under test | bare verdict | kept as |
|---|---|---|---|
| he-c1 | harness before weights, action interface, feedback | **pass** | control |
| he-c2 | imitation under an evolved harness regresses | partial | differential |
| he-c3 | localise one agent at a time / cluster corrections | partial | differential (clustering half only) |
| he-c4 | parallel sample-and-select over reflection | **fail** | differential |
| cwe-c1 | protect the prompt, run the ranker against a null | partial | differential (null arm only) |
| cwe-c2 | read-once state needs an explicit protected region | **pass** | control |
| cwe-c3 | parallel reading, order-sensitivity diagnosis | partial | differential (scatter-gather half only) |
| cwe-c4 | history to the planner, not the executor | **pass** | control |
| ei-c1 | attacker model against a generated rubric | partial | differential (oracle property only) |
| ei-c2 | verdict-only scoring is blind by construction | partial | differential |
| ei-c3 | noise band, leakage screen, cost ceiling | **pass** | control |
| ei-c4 | evaluate under multi-turn pressure | partial | differential (scoring rules only) |
| rhsi-c1 | freeze list, bounded edits, gates, rollback | **pass** | control |
| rhsi-c2 | evolution set disjoint from the eval set | **pass** | control |
| rhsi-c3 | search turns substitute for judge scale | partial | differential (stop rule and F1 only) |
| rhsi-c4 | matched-challenger recovery gate | **fail** | differential |
| sipt-c1 | per-prompt teacher reliability gate | partial | differential |
| sipt-c2 | refresh the synthetic teacher every iteration | **pass** | control |
| sipt-c3 | rubrics regenerated during training | **fail** | differential |
| sipt-c4 | calibrate self-guidance by advantage sign | **fail** | differential |
| sle-c1 | write the skill from recorded runs | **pass** | control |
| sle-c2 | the description is the whole routing surface | **pass** | control |
| sle-c3 | tune the reuse threshold from the strict side | **pass** | control |
| sle-c4 | grounding before an optimizer | **pass** | control |
| ei-c5 (r2) | unanimity across independent judgments | **pass** | control |
| ei-c6 (r2) | partial monitoring is an intervention | partial | dropped, no magnitude |
| ei-c7 (r2) | benchmark defect profile and repair loop | **pass** | control |
| sle-c5 (r2) | select a complementary set, not top-k | partial | differential |
| sle-c6 (r2) | revise in rounds, isolate the reader, stop at three | **pass** | control |
| sle-c7 (r2) | skills transfer across models | **fail** | differential |
| rhsi-c5 (r2) | gate compaction on arithmetic, not a threshold | **pass** | control |

**Across both rounds, 31 candidates: 15 qualified as differential (5 bare
failures, 10 partials), 15 passed outright and become controls, and 1 was
dropped for carrying no magnitude.** The five bare failures are the strongest
tasks in the library, because on each of them the bare model recommended
*against* the finding rather than merely omitting it: he-c4, rhsi-c4, sipt-c3,
sipt-c4, sle-c7. The last of those is the sharpest result in the file. Asked
whether a skill optimised on a small model should be re-optimised for a large
one, the bare subject said yes and warned that the existing file would be
"actively harmful"; the measured evidence says 34 of 36 cross-model transfers
improved on the receiving model's no-skill baseline, and in one case the
transferred skill beat the one optimised directly on the large model, 71.78 to
69.40. A confident answer in the wrong direction is worth more to a skill than
ten the model already has.

## The finding the table is really reporting

The bare subject did not merely match the skills on the eleven passes. On
seven of those eleven it gave a **better** answer than the skill did, in the
same shape the skill was aiming for. One partial belongs in this list too, and
it is the sharpest case.

- sle-c1: unprompted, it said to run the task 10 to 20 times with no skill,
  classify the failures, write only what removes an observed failure mode, and
  "delete what the model already knows". That is this library's own ADR-38
  thesis, produced by a model that had not read it.
- ei-c3: it gave the noise floor, the repeat count, the paired statistics, the
  multiplicity correction and the leakage read. `evaluation-integrity`'s noise
  band carried a floor of five repeat runs marked as ours because no source set
  one. The bare model set it at five to ten.
- ei-c5: unprompted, it required unanimity rather than a majority, named
  inter-judge correlation as the dominant error term rather than per-judge
  accuracy, insisted independence come from different model families, and said
  a malformed judgment must fail closed as an abstain that cannot satisfy the
  gate. Three of the four portable parts `evaluation-integrity` carried, two of
  them marked as ours.
- rhsi-c5: derived that a percentage threshold is the wrong compaction trigger,
  replaced it with absolute headroom against a projected worst case, and priced
  it against prompt-cache invalidation at roughly ten times cached-read cost.
  That is the argument SoL-Pi's compaction gate rests on, reached without it.
- rhsi-c3 (a partial, not a pass): offered delta debugging by oracle substitution over the replayed
  run, about six replays for forty candidates and correct by construction,
  which is a better method than the text-search procedure the skill carries.
- cwe-c2: gave the pinned-facts block, the structural guarantee that compaction
  cannot touch it, re-derivability so recall is not the only path, and a
  needle-across-compaction CI test.

Two readings. The obvious one is that a large fraction of the library was
paying rent on advice its reader already has. The less obvious one is that the
bare model's answers are a **source of deltas**, not only a filter: three of
them name a mechanism no cited paper in this library covers, and those are now
queued for the research seat rather than quietly absorbed.
