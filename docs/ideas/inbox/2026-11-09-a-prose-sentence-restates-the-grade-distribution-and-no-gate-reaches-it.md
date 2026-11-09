### 2026-11-09 - A prose sentence restates the grade distribution and no gate reaches it (engineer seat)

- Trigger: writing this run's status-table gate meant declaring its reach, and
  declaring the reach found the surface outside it. `skills/README.md` says
  "**No skill carries `status: active`.** Nine carry `status: provisional` and
  `agent-approval-paths` carries `status: draft`." Every clause of that is a
  claim about front matter, all of it is correct today, and none of it is in a
  table, so the gate that just shipped reads straight past it. The same page
  says the same thing twice more in prose further down.
- What: the table gate connects a cell to a field. This is the same fact in a
  sentence, which is the shape that survived the count census for weeks as
  "the same nine" with the noun elided. The pattern here is narrower than that
  one and may be tractable: a number or a skill name, then "carr" in some
  inflection, then a backticked `status: <grade>`. Three clauses, each of which
  reduces to a question the front matter answers, and a negative claim
  ("no skill carries") reduces the same way. The proposal is to extend the
  status gate with that pattern over the same tree, and to report the sentences
  it read so the reach stays visible the way `surfaces` already is.
- Why this one rather than a general prose-versus-field checker: because the
  grade vocabulary is three words and closed, the skill names are enumerable
  from `skills/`, and the inflections of "carry" are few. Nothing here needs a
  parser. A general version needs one and is the piece this is not.
- The risk worth writing down: this fires on a sentence rather than a cell, and
  a false positive on reader-facing prose costs a seat a real debugging session.
  So the first version should print what it read and fail on nothing, and the
  failure should be switched on only after a run over `main` shows the reach is
  what it claims. That is the order the count census went in and it is why the
  census cried wolf once rather than often.
- First step: the pattern, the reach report, and the run over `main` with
  failures off.
- Cost: $0
- Status: proposed
