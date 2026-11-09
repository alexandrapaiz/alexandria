### 2026-11-09 - `skill_length.py --check` has exited 1 since the day it was written, into a terminal nobody was standing in (engineer seat, for the owner through the PM)

- Trigger: arming the instruments under `skills/_validation/` for the skill
  seat's second ask meant running all seven of them for the first time in one
  place. Six exit 0. `skill_length.py --check` exits 1, and its last line says
  why: "rule 4 is measured in `wc -l`, under which every one of these passes.
  This exit code is the unit rule 4 meant, not the unit it names, and changing
  the rule is the owner's."
- What: 0 of 10 skills are under ADR-38 rule 4's cap of 120 lines when the cap
  is read as rendered lines at 100 columns, and 10 of 10 pass when it is read as
  `wc -l`. The instrument argues, in its own output, that the rendered reading
  is the one the rule meant, because a skill is loaded into a context window and
  a 5,597-character line costs what it costs however few newlines it holds.
  `skill-library-engineering` is 119 lines to `wc -l` and 414 rendered.
  So the number the rule names and the number the rule is about differ by a
  factor of three and a half on the library's worst file, and the instrument
  that measured it has been saying so to nobody. This is not a new finding about
  the skills. It is a finding about who heard it: the instrument was correct,
  it was committed, and no chain in this repository ran it, so its exit code
  reached no pull request and no register.
- What arming it changes, which is the part worth deciding: now that
  `tests/test_validation_instruments.py` runs the seven,
  `skill_length.py` is the one whose non-zero exit is pinned in `STANDING` with
  this entry's reasoning, and that pin is the only thing keeping the suite green.
  A pin is a decision deferred rather than a decision made. Leaving it there for
  a month is how a standing finding becomes furniture, which is exactly what the
  last fourteen months of `UNCOVERED` in `tests/test_ci_coverage.py` record.
- First step: the PM posts this as a section 22 `ask` with its own recommendation,
  because this is a rule's unit rather than money, an account, a secret or a
  seat's authority, so it proceeds as recommended after forty-eight hours of
  silence. Two outcomes, both one line. Either rule 4 says rendered lines at 100
  columns, and the skill seat gets a real backlog of ten files with a measured
  number against each. Or rule 4 says `wc -l`, and `skill_length.py` stops
  exiting 1, the pin in `STANDING` is deleted, and the rendered number becomes a
  note the instrument prints rather than a verdict it returns.
- Cost: $0
- Status: proposed
