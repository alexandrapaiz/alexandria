# The ceiling held by 179 tokens, which is not holding it

Writer seat, eighth run of 2026-10-18. Triggered by a handoff from the PM
seat, not by the daily cadence. Today's graded review of the issue is
`docs/voice/reviews/2026-10-18.md` and this branch carries it. This file
grades the generator's weight, which is what the handoff asked for.

## What was asked

The PM read PR #366 against the merge rule and held it. Her two reasons, in
her words: a red check on the exact tokenizer at $0.1519 an issue against a
$0.15 ceiling, and a `prompts/` path, which is Tier C and not hers to merge
whatever the check says. The second reason stands either way and I am not
arguing with it.

#366 was merged at 07:09:30Z, after her hold and before this run opened, so
the branch she was holding is `main` now. Her ask is not closed by that. What
she asked for is headroom, and the merge put the 211-token margin into `main`
rather than removing it.

What she asked for is the part this run answers. Trim the prompt growth far
enough under the ceiling that there is real headroom, rather than a number
that just barely clears it.

## The state she read, and the state now

Every number below is `pipeline/budget.py`'s own, taken from each branch
head with the exact tokenizer installed, so they are costs rather than
estimates.

| | prompt tokens | cost an issue | headroom |
|---|---|---|---|
| main, before #366 merged | 36,582 | $0.149962 | 40 tokens |
| the sixth run, which went red | 38,634 | $0.151911 | over by 2,011 |
| the seventh run, now main | 36,411 | $0.149799 | 211 tokens |
| this run | 34,396 | $0.147885 | **2,226 tokens** |

The check was already green when this run opened: run 39106212077 passed on
`9da8410`, which is #366's head and is now main. Her reading was correct for
the commit she read and the branch moved under her. The three failed runs in
the event payload are all on commits two branches back, and nothing is red.

So the question this run actually had to answer is whether 211 tokens is
headroom. It is not. The file grew 2,056 tokens in one run three hours
earlier, so a 211-token margin is spent by the next run before it writes
anything. Before #366 merged, main's own margin was 40 tokens, which is one
sentence, and nothing in the repository was watching it.

## What was cut, under one principle

The generator gets the rule and the fix, never the argument for the rule.

The seventh run cut the case history: dates, tombstones, the account of which
print produced which clause. This run cut the layer under it, which is
persuasion. The file was written by an editor arguing with the next editor,
and the press pays to read that argument before every issue. The rule is what
the model acts on. Why the rule is right belongs in this directory, where it
already is.

Seventeen blocks were rewritten this way: the shape gate, the evidence grade, the
heading gate, the first-use pass, the stands-alone gate, the attribution gate,
the item spine, the headings rule, the links rule, the reading-list slot and
the close. 2,015 tokens of the file, 5.5% of it, with every operative
clause, every disambiguation and every counted target left standing.

Three things were explicitly not cut, and the boundary is worth writing down
because the next run will want to cross it.

- **Disambiguation is operative.** "A bold lead opening a paragraph is not a
  shape" looks like commentary and is the only thing standing between the
  count and a wrong answer.
- **A specimen the ban list records as enforcement stays.** I removed the
  words "Worth the hour if you are" from the reading-list slot, read entry 56
  of the ban list, found that naming that frame as spent IS the enforcement
  the entry records, and put it back. A trim that quietly disarms a ban-list
  entry is a worse defect than the tokens it saves.
- **An owner's ruling keeps its attribution.** The date on "(owner's ruling,
  2026-09-19)" costs almost nothing and tells the model which lines are not
  the editor's to soften.

## The defect this run introduced and caught

Compressing the count gate, I dropped the sentence that fixes what the count
counts, and left "The sentence's number is that count" pointing at nothing.
`docs/voice/check_voice.py` caught it, because ban-list entry 112 is anchored
on that exact sentence, and the anchor stopped resolving.

That is the gate working, and it is also the measure of what this kind of pass
risks. 44 anchors resolve against the file and the rest of the prompt has no
such tripwire, so the next compression run should read its own diff for
dropped imperatives before it trusts the anchor check. The grep that found it
here, once the anchor pointed at it:

```
git diff origin/main -- prompts/digest.md | grep '^-' | grep -E '^\-\s*(Count|Take|Strike|Put|Read|Write|Check|Drop|Run|Ask|Never|So )'
```

## The part that is still not fixed, and it is the same part

2,226 tokens is ten times the margin she was handed and it is not real
headroom either, and I would rather say that plainly than let the number
stand in for an answer.

| term | cost | whose |
|---|---|---|
| output reservation, 24,000 tokens | $0.0960 (65%) | the press, raised 4x on 2026-09-24 |
| the generator prompt | $0.0327 (22%) | this seat |
| worst-case payload | $0.0192 (13%) | the distill caps |

Deleting every word of the generator lands at $0.1152, which is 23% under the
ceiling and still more than double what ADR-32 books. Two full runs of
careful editing have now cut 4,238 tokens and bought back $0.0040. At that
rate the whole file is gone before the ceiling has real room in it.

So the measured answer to the handoff is: the writer seat can keep the press
under the ceiling and cannot give it headroom. Both of this run's structural
proposals are in `docs/ideas.md` for the engineer and neither is prose work.

## What stops the margin being spent again

`docs/voice/canon.md` now carries the gate, because the charter says this seat
reads that file every run and nothing else in the loop ever weighed the
prompt. Two rules. Run `python3 pipeline/budget.py` before committing a prompt
change rather than hearing about it from CI three red runs later. And a run
that adds tokens removes at least as many, or says in its pull request, with
the number, that it could not.

That second rule is the one that matters. The ceiling was never broken by a
bad commit. It was broken by forty days of good ones.

## Registers

- `docs/voice/taste.md`, first and line by line. No reader-facing copy and no
  heading this run, so the 2026-09-19 and 2026-09-29 rulings are not engaged.
  Her 2026-09-19 ruling that the fine-tuned instruction is the base layer is
  engaged by every line of the diff, and the test I ran against it is whether
  any operative clause she wrote is weaker now. None is.
- `docs/voice/canon.md`, `docs/voice/ban-list.md`: 44 anchors resolve, one
  failure found and repaired, no entry deleted and none weakened.
- `docs/voice/value.md`, `docs/voice/preferences/`: not engaged, no copy.
- `docs/agents/quality-claims.md`: not engaged, no claim about what we ship.
- `docs/agents/incidents.md`: the cost ceiling is already recorded as a repeat
  by the PM seat in #367, as `INC-2026-10-18-the-cost-ceiling-breached-a-third
  -time-this-one-caught-before-main`. Nothing from this run repeats it and
  nothing here is filed twice.
- `docs/standards/lessons.md`, the `any` section and the writer's: read.
  L-A22, measure before you promise, is the rule this run's canon addition
  implements.
