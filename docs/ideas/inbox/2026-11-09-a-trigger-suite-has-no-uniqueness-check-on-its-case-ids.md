### 2026-11-09 - a trigger suite has no uniqueness check on its case ids, and one collision made a case invisible for eight hours (skill seat, for the engineer)

- Trigger: this run built a before-and-after per-case comparison of the trigger
  suite, to prove a mechanical sweep across seven `SKILL.md` files moved no
  verdict. The comparison dict held **83 entries for a suite reporting 84
  cases**. The missing case was a second `ac-pos-5` in
  `skills/agent-containment/triggers.json`, added by this seat's own commit
  `a3349aff` eight hours earlier on an id the 2026-11-02 revision already held.
  One of the two passes and one fails. Filed as
  `INC-2026-11-09-a-trigger-case-id-was-reused-and-one-of-two-cases-was-invisible-to-every-per-case-record`.
- What: the defect is one case and the class is a missing assertion. Nothing in
  this repository checks that case ids are unique within a `triggers.json`:
  `grep` for a `set(` or `Counter` over case ids across `tests/`,
  `skills/_validation/` and `tools/skill_*.py` returns **zero** hits. The suite's
  totals count positionally, so 84 stayed 84 and no number moved, while every
  per-case consumer keys by id and silently holds 83. `by_kind.positive.failed`
  then read `['ac-pos-5', 'ac-pos-7']`, naming an id that two cases share, so
  the library's own published sentence "ac-pos-5 does not fire" was true of one
  case and false of the other. This is the same shape as the `duplicate-status`
  defect that turned `main` red this morning in a ledger entry of this seat's:
  one key, two values, the first wins and the second is absent rather than
  rejected. The repair pattern is also already proven here today, by the
  engineer's own ban-list work on #864: an absolute assertion that costs nothing
  to run makes a class impossible rather than clearing it once.
- Where it should live, and the file already proves the point:
  `tests/test_skill_scope.py:261`, inside
  `test_the_suite_is_the_published_one_and_not_a_new_exam`, already globs every
  `skills/*/triggers.json`. That test computes
  `published = sum(len(cases) for each suite)` and asserts the live measurement
  agrees with it. **It summed 84 and agreed with the collision in the tree**, verified in this run by restoring `a3349aff`'s version of the file (14 cases, 13 unique ids) and running that one test, which passed,
  because a length is positional and a collision changes no length. So the one
  test that reads every suite is blind to this by construction rather than by
  omission, and it is also the cheapest place to fix it: the files are already
  open and parsed.
- First step: four lines in that test. For each suite, collect
  `[c["id"] for c in cases] + [c["id"] for c in retired_cases]` and fail when
  `len(ids) != len(set(ids))`, keeping retired ids in the same namespace because
  a revived id collides the same way. Put the offending id and the two prompt
  prefixes in the assertion message, because the entire cost of this incident
  was not knowing which case the id meant. The library is clean as of this run,
  so the assertion lands green and needs no ratchet, which makes it strictly
  cheaper than the ban-list promotion it mirrors.
- Cost: $0
- Status: proposed
