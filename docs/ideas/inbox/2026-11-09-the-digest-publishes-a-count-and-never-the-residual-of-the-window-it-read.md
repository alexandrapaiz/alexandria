### 2026-11-09 - The digest publishes a count and never the residual of the window it read

- Trigger: two things on the same morning. alexandria's ExO seat's rule, that
  a composition claim must publish its residual, filed after a register entry
  put `18G + 6.9G` under the word `measured` against a 43G total. Then the
  craft scan of Undermind, which publishes a discovery curve and a stopping
  criterion beside its result count, so a reader is told what the marginal
  return looked like when the search stopped.
- What: the weekly digest tells a reader how many papers it carries. It does
  not tell them how many the window held, how many each gate dropped, or what
  is left over after the named parts are subtracted. A reader therefore cannot
  tell a quiet week from a stalled cron, and neither can a seat. That is the
  same shape as the disk entry: a total, some named parts, and a remainder
  nobody publishes. `tools/sentinel.py --compose` already holds the rule and
  the refusal, so the work is to feed it the digest's own composition rather
  than to invent anything. The refusal matters more than the print: a digest
  whose unexplained remainder is larger than its largest named gate is a
  digest that does not know what it dropped.
- First step: one call in the digest composer that passes the window's total
  and each gate's drop count to `sentinel.Composition`, and one line in the
  issue footer that prints the residual. The gate comes after the print, so
  the first week only reports.
- Cost: $0
- Status: proposed
