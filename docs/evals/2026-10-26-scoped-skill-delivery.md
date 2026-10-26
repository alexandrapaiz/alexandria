# Scoped skill delivery, measured on this library: 2026-10-26

The question. A skill library puts every skill's description in the agent's
context and lets the agent choose. The ledger proposal of 2026-09-18 asked
whether it should instead put only the skills a task needs there. Five
independent measurements later, the market brief of 2026-10-16 is the
controlled one: loaded-skill recall for the correct skill falls from 73.6%
to 27.4% once a thousand irrelevant skills join the library, while the rate
of loading no skill at all rises from 9.3% to 51.6%. Explicit
pre-selection from the same library holds recall at 73.9%.

This is that measurement run on this repository instead of on a paper's
synthetic library, with the instrument and the result bundle on file next
to it.

## What was measured

`tools/skill_scope.py` ships the mechanism in two stages. The first ranks
the whole catalogue by BM25 over each skill's own body and keeps at most
three, dropping anything scoring under half the top score. The second is
the trigger router this library already publishes, `lexical/2.1`, running
over whatever the first stage handed it plus the unchanged eight-decoy null
panel, so a skill still has to outrank the null to fire and silence is
still a decision rather than a score falling off a cliff.

The queries are the 67 cases in `skills/*/triggers.json`, the same set the
published trigger receipts are scored on. The measurement does not get to
write its own exam. 49 of them name a golden skill and 18 must produce
silence.

The irrelevant skills are the 20 Clerk skills already vendored in this
checkout under `.agents/skills/`. They are real skills with real bodies,
written by somebody else for authentication work this library does not
serve. Generating a thousand fake ones would have produced a bigger number
and a weaker one, because a distractor pool written by the run that
measures against it is a pool tuned to lose.

`scope/desc` is the control. It runs the same first stage over descriptions
alone, the text the baseline already sees, so it can add no information and
can only narrow the pool.

## The numbers

```
scoped skill delivery: scope/1, selector lexical/2.1
  9 library skills, 20 real distractors from .agents/skills, 8 decoys in the null panel
  67 cases: 49 with a golden skill, 18 that must stay silent
  policy: at most 3 skills loaded, cutoff at 50% of the top score

  bodies: library averages 2310 words, distractors 1292, a 1.79x gap

  distractors  arm          recall   wrong  no skill  silence  loaded  ctx words  scope miss
  ------------------------------------------------------------------------------------------
            0  unscoped      83.7%   14.3%    2.0%   77.8%       9       1172    0.0%
            0  scope/body    85.7%   12.2%    2.0%   83.3%     2.6        349   10.2%
            0  scope/desc    83.7%   14.3%    2.0%   77.8%    1.79        234   10.2%

            5  unscoped      83.7%   14.3%    2.0%   77.8%      14       1240    0.0%
            5  scope/body    87.8%   10.2%    2.0%   83.3%    2.73        353    8.2%
            5  scope/desc    83.7%   14.3%    2.0%   77.8%     1.9        228   10.2%

           10  unscoped      83.7%   14.3%    2.0%   77.8%      19       1277    0.0%
           10  scope/body    87.8%   10.2%    2.0%   83.3%    2.85        358    8.2%
           10  scope/desc    83.7%   14.3%    2.0%   77.8%    1.99        235   10.2%

           20  unscoped      83.7%   14.3%    2.0%   77.8%      29       1380    0.0%
           20  scope/body    87.8%   10.2%    2.0%   83.3%    2.87        361    8.2%
           20  scope/desc    83.7%   14.3%    2.0%   77.8%       2        235   10.2%

  at 20 distractors, scope/body moves recall +4.1% against no scoping (83.7% to 87.8%), loads 2.87 skills instead of 29, and spends 74% fewer words on descriptions
  at 20 distractors, scope/desc moves recall +0.0% against no scoping (83.7% to 83.7%), loads 2 skills instead of 29, and spends 83% fewer words on descriptions

  the unscoped baseline did not move between 0 and 20 distractors (83.7% both times), so this pool does not reproduce the recall collapse the market brief cites. Twenty real skills from one adjacent domain are not a thousand near-neighbours. What scoping buys here is the context cost and the confusion cases, not a rescue from a collapse this checkout cannot stage.
  verdict: scoping wins
```

## The baseline is the published instrument and not a new one

`python3 skills/_validation/trigger_test.py` prints 55 of 67 on this tree,
reliability 0.82. The unscoped arm at zero distractors prints a suite pass of
0.8209, which is 55 of 67 to four places. The baseline is the router this
library already publishes, running on the cases it already publishes, so the
difference between the two arms below is the scoping and nothing else.

## What they say

**Scoping is free and then some.** At the full pool, loading at most three
skills instead of 29 raises recall from 83.7% to 87.8%, raises the share of
silence cases held from 77.8% to 83.3%, and spends 74% fewer words on skill
descriptions. The product claim the proposal was built on holds here: a
reader does not pay for the library to get the skill.

**The collapse the paper measures did not happen here, and that matters
more than the win.** The unscoped baseline sat at 83.7% at zero distractors
and at 83.7% at twenty. Twenty real skills from one adjacent domain are not
a thousand near neighbours, and this checkout cannot stage the regime the
brief describes. So the honest reading is that scoping buys the context cost
and four confusion cases today, and that it is insurance against a trend
line rather than a repair of a live break.

**The gain is the body index, not the narrowing.** The control arm moved
recall by exactly nothing, 83.7% to 83.7%, at every distractor count. A
stage that narrows the pool using the same text the selector already reads
changes which skills are present and never which one wins. What changed the
answer was reading each skill's whole body, which a scoping stage can afford
and an in-context description cannot.

**Scoping has its own failure mode and it is in the table.** Four of the 49
golden cases had their correct skill scoped away, an 8.2% miss rate. Three
of those four were cases the unscoped selector also got wrong, so they cost
nothing. The fourth, `ams-pos-2`, is a real regression: a question about
whether to add a reranker between retrieval and the prompt went to
`skill-library-engineering` after scoping and to `agent-memory-selection`
before it. One case gained three and lost one, and both halves are counted.

## How to reproduce

```
python3 tools/skill_scope.py --measure
python3 tools/skill_scope.py --smoke
python3 -m pytest tests/test_skill_scope.py -q
```

The bundle beside this file is the frozen evidence, with per-case detail
for the full pool. `--all-cases` writes the detail for every count.

## What is not built yet

The mechanism exists and is measured. It is not yet what the plugin does on
install, because the two places it would have to live are not this seat's to
write. A router entry in the library is skill content, which belongs to the
reviewer panel, and a scoping hook in the plugin manifest is not something
the host exposes today. The remaining step is named in the ledger rather
than left for a reader to notice.
