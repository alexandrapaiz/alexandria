# Run note: engineer, 2026-10-26, scoped skill delivery

Opened on the message run of 06:17Z, which was cut off at turn 34 with only
this file committed. Continued on the hook run that followed, which was woken
by the provider limit resetting. PR #556 carried the first state and is closed
as superseded by #558; this branch is #556's head plus the work below, so
nothing of it was lost.

Item taken: **sprint-2026-10-26 item 3, ship scoped skill delivery by
default.** Items 1 and 2 are merged as #542 and #549.

## What shipped

`tools/skill_scope.py`, the mechanism, in two stages. The first ranks the
whole catalogue by BM25 over each skill's own body and keeps at most three,
dropping anything under half the top score. The second is the trigger router
this library already publishes, `lexical/2.1`, imported rather than
reimplemented, over whatever the first stage handed it plus the unchanged
eight-decoy null panel.

`docs/evals/2026-10-26-scoped-skill-delivery.md` and its bundle, the
before and after. At the full distractor pool, loading at most three skills
instead of 29 moves recall from 83.7% to 87.8%, moves silence held from 77.8%
to 83.3%, and spends 74% fewer words on skill descriptions.

`tests/test_skill_scope.py`, nineteen tests, including a checkout built so
that scoping is the wrong move, which the verdict has to be able to say.

## Three findings worth more than the win

The unscoped baseline did not move between zero and twenty real distractors,
83.7% both times, where the market brief reports a fall to 27.4% at a
thousand. Twenty real skills from one adjacent domain are not a thousand near
neighbours, so this checkout cannot stage the collapse and the result is a
safety margin rather than a rescue.

The control arm moved recall by exactly nothing. Narrowing the pool using the
same text the selector already reads changes which skills are present and
never which one wins. What changed the answer was reading each skill's whole
body, which a scoping stage can afford and a description in context cannot.

The baseline reproduces the published instrument to four places: 0.8209
against `trigger_test.py`'s 55 of 67. So the difference between the arms is
the scoping and nothing else.

## What is not done

The default is still the whole library. The two places it would have to
change are a router skill, which is content and belongs to the ADR-13 panel,
and a plugin-manifest hook the host does not expose. Both are in the ledger.

`tests/test_skill_scope.py` is pinned in `test_ci_coverage.py`'s uncovered
set, because the step that would run it goes in a workflow file this seat
cannot write. That is the twelfth line on that list and it counts itself at
`INC-2026-10-17-the-pin-list-grew-for-the-seventh-time-in-nine-days`.
