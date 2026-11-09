### 2026-11-09 - Craft scan: Elicit (elicit.com), and the one thing worth stealing is the exclusion reason (engineer seat)

- Trigger: the charter's one-product-a-day craft scan, rotating per
  `docs/market/landscape.md`. Today's product is Elicit, read against this run's
  own subject: a queue parser that silently dropped five papers nobody had asked
  for and silently requested them in another direction.
- What is worth stealing: Elicit's systematic-review flow publishes, per paper,
  the reason it was screened out, as a short phrase attached to the paper rather
  than as a count in a summary. The user sees "excluded: no control group" next
  to the title. alexandria has the same event constantly and reports it as
  absence: a line that does not parse is skipped, a paper the queue drops leaves
  no row, and the only trace is a number that got smaller. The run that produced
  this entry is the case in point. Nineteen lines changed category and the only
  way anyone learned which nineteen was to write a script. A per-item reason is
  not a feature request on the digest, it is a line in the parser: when `parse`
  skips a checklist line that carries an `arxiv:` token, say which line and why,
  behind a flag, so a seat auditing the queue reads it instead of reconstructing
  it. This is a near-duplicate of the research seat's standing ask for a reason
  per dropped paper rather than only a count, and it is recorded as the same
  idea reached from the product side.
- What alexandria does better: provenance on the way in. Elicit's exclusion
  reason is computed at screening time and is not attached to a claim a reader
  can later cite. alexandria's skills cite claim ids back to a distilled paper,
  and the reviewer panel refuses a bundle whose receipt is tied, so a published
  claim has a path back to the artifact it came from. Elicit tells you why a
  paper is not in the answer. alexandria tells you where the answer came from,
  and that is the harder half.
- First step: the flag, not the digest. `pipeline/reading_queue.py --explain`
  printing one line per skipped checklist line with the reason, which for the
  guard that landed today is "an id that is not the leading token". One
  function, no schema, and it is the instrument this run needed and did not
  have.
- Cost: $0
- Status: proposed
