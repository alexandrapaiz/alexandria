### 2026-11-09 - Rule 3's 0 of 10 counted the frontmatter, and the remedy the number named cannot move the number that matters (skill seat, for the owner)

- Trigger: this seat's own 2026-11-09 ledger entry, `ADR-38 rule 4 is measured
  in a unit the content cannot be held to`, carries a second finding: **0 of 10
  skills reach their checklist within twenty rendered lines**, median 103, worst
  182, cause named as the YAML provenance block in all ten. The same run acted
  on it and moved 1,837 words of revision history out of `agent-containment`.
  This run re-measured before moving a second skill's history for the same
  stated reason.
- What: the 0 of 10 was measured from byte zero of the file, which counts the
  frontmatter. The frontmatter is 93 of `agent-containment`'s 101 and 131 of
  `agent-security-measurement`'s 143, so the metric was mostly measuring a YAML
  block that no consumer renders as prose. Rule 3's own wording is
  "immediately after the opening paragraph", which describes document structure,
  and document structure starts after the frontmatter.
- The measurement, and it is in `skills/_validation/checklist_position.py` with
  a `--check` mode, rendered at 100 columns so it is comparable with
  `skill_length.py`:

  | reading | result | median | worst |
  |---|---|---|---|
  | from byte zero, frontmatter counted | 0 of 10 within 20 | 104 | 143 |
  | from the body, which rule 3's first sentence describes | **10 of 10** within 20 | 11 | 14 |
  | to the END of the checklist, which its second sentence describes | **2 of 10** within 20 | 30 | 41 |

- So the library passes rule 3 on one honest reading, fails it 2 of 10 on
  another honest reading, and the 0 of 10 belongs to neither. On the reading
  that does fail, **the cause is checklist length and not the frontmatter**:
  `agent-containment`'s checklist alone renders 33 lines. Moving its history out
  moved its from-byte-zero number from 101 to 101 by this instrument, because
  the papers list is what remains, and it could not have moved the other two at
  all.
- Why this is the owner's and not this seat's: rule 3 says "the first twenty
  lines" and does not say twenty lines of what. All three readings are
  defensible and they disagree 0, 10 and 2. Picking one is a charter edit, which
  is the same conclusion the rule-4 entry reached about its own unit, and the
  same reason `--check` here is wired into no gate.
- First step: one sentence in `prompts/skill-agent.md` rule 3 naming the region
  and the column, the way the rule-4 decision will have to name a unit. If the
  answer is the whole-procedure reading, 8 of 10 skills are over and the work is
  shortening checklists, which is a smaller programme than the rule-4 one.
- What this run did NOT do on the strength of the corrected number: move the
  remaining nine skills' `provenance.revisions` blocks out. `evaluation-integrity`'s
  moved this run for its own reasons, which are that the history had reached 643
  words and the site renders none of it, and that the new delta needed the lines.
  Those reasons stand. The rule-3 reason does not, and it was the stated one.
- Cost: $0
- Status: proposed
