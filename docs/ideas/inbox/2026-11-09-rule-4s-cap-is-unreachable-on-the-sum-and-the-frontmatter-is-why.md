### 2026-11-09 - rule 4's cap is unreachable when the frontmatter is counted, and the cap has already deleted advice to pay for metadata (skill seat, to travel with the engineer's unit ask)

- Trigger: the engineer seat armed `skills/_validation/skill_length.py` in
  `tests/test_validation_instruments.py` on 2026-11-09, found it exits 1 with 0
  of 10 skills under the cap when the cap is read as rendered lines at 100
  columns, pinned it in a `STANDING` dict, and filed the rule's unit as a ledger
  entry for the PM to post as a section 22 ask. This entry is the half that ask
  is missing. The unit question cannot be answered without it, because the
  answer "rendered lines" is not reachable by any skill the format contract
  permits.
- What: ADR-38 rule 4 caps a skill at 120 lines "including frontmatter", and
  this seat split the count in two to find out which half was long. The
  frontmatter is 39 to 128 rendered lines across the library, median about 90,
  so between a third and the whole of the cap is spent before a word of advice.
  The irreducible part of it, with every revision narrative removed, is still 29
  to 59. The shortest body in the library is 104 rendered lines. **So the
  smallest frontmatter plus the shortest body is 143, and no skill this contract
  permits can reach 120 on the sum.** `--check` prints that floor in its own
  output as of this run.
- The harm is not hypothetical and it is recorded in the library's own words.
  Rule 4 counts `provenance.revisions`, which ADR-37 requires to grow by one
  narrative entry per maintenance run and which **nothing reads**:
  `site/lib/content.js` `parseSkill` returns `name`, `description`, `version`,
  `status`, `extracted`, `validated`, `claims`, `papers` and the body, and no
  test, no instrument under `skills/_validation/` and no tool under `tools/`
  reads the field. On `harness-engineering` the five entries had reached 8,651 of
  the file's 17,602 characters, 49 percent of this library's gold specimen. Three
  of those five entries say in their own words that they cut reader-facing
  advice to pay for the space a revision entry took: delta 3's closing clause,
  the itemised list inside the last caveat, a checklist item, and four prose
  lines. A gate that deletes advice to make room for metadata about having
  deleted advice is doing harm rather than work.
- What this run did about it without touching the rule: the narratives moved to
  `skills/harness-engineering/revisions.md`, the frontmatter keeps one dated line
  per revision naming the trigger and what changed, which is what ADR-37 asks the
  record to carry, and the file went from 229 rendered lines to 160 with no
  sentence of the body touched. `prompts/skill-extract.md` now carries that as
  the format contract, so it binds the next skill written rather than only this
  one. Nine skills still carry their narratives in the frontmatter.
- So the owner's ask has three options rather than two, and the third is the one
  the numbers point at. (a) Rule 4's unit stays `wc -l`, and the instrument is
  advisory. (b) The unit becomes rendered lines, which is unreachable today and
  would require either a cap near 400 or cutting roughly two thirds of the
  library's words. (c) **The cap governs the body and the provenance block is
  metered separately**, which is the only option under which a well-maintained
  skill does not grow its way into violation by obeying ADR-37.
- First step: the PM's section 22 ask carries (c) alongside the unit question,
  with the floor number in it, because the unit question answered alone produces
  a rule no file can satisfy. This seat recommends (c) and has already shipped
  the part of it that needs no ruling.
- Cost: $0
- Status: proposed
