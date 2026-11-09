### 2026-11-09 - the quotes that close the YAML colon class are a convention and not a gate (skill seat, own surface)

- Trigger: this run was woken by a red that the unquoted-colon class produced on
  `agent-approval-paths` v7, which is the second occurrence of that class. The
  first was 2026-10-26 on two skills. Both are recorded in
  `docs/agents/incidents/inbox/INC-2026-10-26-two-of-nine-shipped-skills-cannot-be-loaded-by-a-yaml-parser.md`,
  together with three claims that entry made about the second occurrence that
  this run checked against the forge and found false.
- What landed today: every `description` in `skills/*/SKILL.md` is a
  double-quoted YAML scalar, so the break is no longer writable. The first
  occurrence quoted only the two files that were broken at the time and left
  eight unquoted, which is why the class stayed live and recurred fifteen days
  later on one of the eight.
- Proved inert rather than assumed, because a router reads this field: PyYAML
  parses a byte-identical description on all 10 before against after,
  `parse_frontmatter` in `skills/_validation/trigger_test.py` agrees with PyYAML
  on all 10, `parseFrontmatter` in `site/lib/skill-provenance.js` leaks a quote
  on 0 of 10, and the trigger test is 76/86 at reliability 0.88 before and
  after with 0 of 86 verdicts moved, diffed case by case rather than read off
  the total.
- What is still open, and it is one assertion: nothing requires the quotes.
  `--receipts` checks that the frontmatter loads, that the receipt is current,
  and that the description is inside 150 words. It does not check that the
  value is quoted. So the library conforms today by the act of one run, and the
  next skill written here can reintroduce the hazard, at which point the only
  thing between it and a red is whether the author happens to type a colon.
- First step: one check in `check_frontmatter` in
  `skills/_validation/trigger_test.py` failing `--receipts` on a `description`
  whose raw value does not begin and end with a double quote. Two lines, no
  false positives, and it turns today's ten-file convention into an invariant.
- Why it is filed rather than applied: the same run moved all ten files, and the
  change that makes the library conform should be reviewable apart from the gate
  that holds it there.
- Why it is worth the two lines, in this seat's own terms: the charter's market
  figure is that 69 percent of public skills never fire, and a skill whose
  frontmatter no loader will open fires zero percent of the time. All three
  readers here are regex readers that cannot tell, which is the first
  occurrence's finding. This is not a missing gate, because the gate the first
  occurrence asked for shipped on 2026-10-27 in `12389a5a` and did fire. It is
  the difference between catching the defect after a commit and making it
  unwritable, and the second occurrence measures what the first costs: one red
  run and one seat run, for one character.
- Surface: `skills/_validation/trigger_test.py`, which is this seat's own, so
  this is a note to the next run of this seat rather than a request to the
  engineer.
- Cost: $0
- Status: proposed
