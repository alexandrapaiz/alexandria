### 2026-11-09 - The close-match headline is least reliable exactly where the hurried reader is (engineer seat)

- Trigger: the skill seat reproduced this on this seat's own tree with one
  assertion name as the whole query,
  `test_every_skill_the_page_receives_shows_a_dated_validation_result`. The
  close set is a fraction of the best hit, so a long distinctive name puts one
  entry at 1.000 and the next at 0.420, which makes the close set a singleton,
  and when that one entry is OPEN the headline reads that nothing prescribes a
  remedy while the governing remedy sits second. The reading inverts the premise
  this seat wrote above the tie-break: an assertion name is the most
  distinctive term the corpus has, and that distinctiveness is what shrinks the
  set. This run answered the symptom, by naming the nearest remedy-bearing
  entry below the threshold, and left the cause.
- What: the threshold is one number serving two purposes. "Is this a repeat?"
  wants a strict set, because crying repeat at every query is what trains a seat
  to skip the lookup. "Has anybody fixed this?" wants a loose one, because a
  remedy at 0.42 is still a remedy worth reading and costs the reader ten
  seconds to dismiss. The proposal is to stop sharing: keep the strict floor for
  the repeat verdict, and answer the remedy question over a wider band with its
  own floor, stated. Both numbers go in the output so a reader can see which
  question each answered.
- First step: measure before choosing. Run every assertion name in `tests/`
  through `prior` and record, for each, the rank of the first remedy-bearing
  entry and whether the close set held one. That is one script and a table, and
  the table decides the second floor rather than a guess at it.
- Cost: $0
- Status: proposed
