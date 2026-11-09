### 2026-11-09 - a status table restates a field on disk, and the count gate next to it cannot see a wrong word (engineer seat)

- Trigger: fixing the count surfaces in `docs/product/install.md` this run put
  the status table two lines below one of them in view. The table said `active`
  for six skills. Every `SKILL.md` on `main` says `provisional` for nine and
  `draft` for one, and `agent-approval-paths` had no row at all, so the page a
  buyer reads was wrong about six of ten grades and silent about a tenth skill.
  The count gate directly above it was green on that page, because a status is a
  word rather than a number and nothing connects a word in a table to a field in
  frontmatter.
- What: the census that shipped this run answers "does every file that names a
  count get judged". The same question with "status" in place of "count" has no
  instrument. A table that restates a frontmatter field is two implementations
  that agree only on the day somebody typed the second one, and this one had
  drifted on six rows plus a missing row. The proposal is a `--table` gate in
  `tools/check_plugin_manifest.py` or its own tool: find the markdown table in
  the install page whose first column is a backticked skill directory name,
  require one row per directory under `skills/`, and require the status column to
  equal the `status:` field that directory's `SKILL.md` declares. A table with a
  row for a skill that does not exist is the same finding from the other side.
- Why this one and not a generator: a generated table would end the drift and
  would also end the third column, which is a hand-written sentence about what
  each skill decides and is the best writing on the page. A gate keeps the prose
  and checks the two columns that are facts. That is the same split the install
  block already uses, where the sentence is human and the number is checked.
- First step: the gate for the two mechanical columns, against the table as it
  stands after this run's repair, plus one test that deletes a row and one that
  changes a word. Half a day, and it is the same file the census already reads.
- Cost: $0
- Status: proposed
