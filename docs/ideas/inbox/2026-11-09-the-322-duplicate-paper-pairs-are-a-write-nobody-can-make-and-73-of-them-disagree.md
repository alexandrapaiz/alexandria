### 2026-11-09 - The 322 duplicate paper pairs are a write nobody can make, and 73 of them disagree with themselves (engineer seat)

- Trigger: answering the research seat's board ask meant reading the two code
  paths that resolve a paper against `papers`, and both were joining on
  equality against a key space with two shapes. That is fixed on this branch.
  What is not fixed is the data the broken joins produced, measured by the
  research seat on 2026-10-05 and unchanged since: **322 arXiv papers held
  twice, 656 rows, and 73 of those pairs triaged twice and given different
  decisions.**
- What: the repair has two halves and only one of them is engineering. The
  mechanical half is collapsing each pair onto one row and repointing `claims`,
  `claim_links`, `promotions` and `citation_log` at the survivor, which is an
  ordinary migration. The other half is the 73 pairs where triage looked at the
  same paper twice and said different things, and there is no rule that picks a
  winner: the newer decision is not automatically better, because the two rows
  can carry different `prompt_sha` values and one of them may be the prompt the
  owner has since rejected. Picking is a judgement about which judge to trust,
  which is the owner's and not a migration's. So this card asks for a decision
  before it asks for code.
- First step: the measurement, not the write, and it is one command away now.
  `tools/corpus_row.py` already prints every shape a paper is held under; the
  census is the same query without an id, which is twenty lines on top of what
  landed today. It needs `NEON_RO_URL`, which is an owner secret pending in
  `docs/backlog.md` since 2026-09-26, so the ordering is: the credential, then
  the census, then the owner's rule for the 73, then the migration. Nothing
  before the credential is worth building, because a migration written against
  a count from five weeks ago is a migration written against a guess.
- Cost: $0 in services. It costs one secret the owner already has.
- Status: proposed
