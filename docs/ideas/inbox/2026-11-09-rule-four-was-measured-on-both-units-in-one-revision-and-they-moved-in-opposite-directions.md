### 2026-11-09 - rule 4 was measured on both units in one revision and they moved in opposite directions (skill seat, for the owner)

- Trigger: `agent-approval-paths` v7 had to add a precondition to delta 1 while
  v6 sat at 120 lines to `wc -l`, the governing metric, which is the one file in
  the library not under ADR-38 rule 4's cap. Paying for the new material surfaced
  the unit question that `skills/_validation/skill_length.py` already documents,
  this time with a before-and-after inside one revision rather than a snapshot
  across the library.
- What: rule 4 caps a skill at 120 lines "counted with `wc -l` including
  frontmatter". The library's files are one paragraph per physical line, so a
  paragraph costs one line however long it is. v7's measurement, same file, same
  run:

  | version | `wc -l` | frontmatter | body | rendered at 100 cols |
  |---|---|---|---|---|
  | v5 | 118 | 99 | 347 | 446 |
  | v6 | 120 | 118 | 402 | 520 |
  | v7 | 119 | 109 | 459 | 568 |

  The governing metric **improved** by one line while the file got **48 rendered
  lines longer to read**, and both facts are true of the same diff. v7 is also
  the honest version of the move: it paid by collapsing four superseded
  revision narratives in the frontmatter, which `REVISIONS.md` carries in full,
  rather than by cutting advice, and the frontmatter duly fell from 118 to 109.
  The body still grew and nothing saw it. For contrast, v6 paid by merging two
  cross-paper caveats, which is reader-facing prose, and the instrument's own
  docstring records three `harness-engineering` entries doing the same thing in
  their own words. So the metric does not merely fail to catch growth, it
  rewards the one payment method that costs the reader.
- First step: not a charter edit and not this seat's to make, which is why this
  is a ledger entry. The one thing a seat can do today, and v7 did it, is report
  both numbers in the pull request and refuse to describe `wc -l` alone as
  passing. What the owner is owed is the unit decision, and the instrument
  already states the constraint that decides it: the smallest frontmatter in the
  library is 45 rendered lines and the shortest body is 104, so no skill the
  format contract permits can meet 120 rendered lines including frontmatter. A
  cap on the sum is therefore a cap on the ADR-37 provenance record first and on
  the advice second. The two coherent options are a cap on the **body** in
  rendered lines with the frontmatter excluded, or `wc -l` retained and
  acknowledged as a formatting convention rather than a length bound. Either is
  one sentence in ADR-38 and either makes the gate mean something; the current
  pair means a seat can pass the rule while the skill doubles.
- Cost: $0
- Status: proposed
