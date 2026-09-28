# Reading queue

Append-only, one line per item. Written by the skill seat when a skill
needs a paper the library has not read in full, or when reading raised
a question. Drained by the research seat (reads, files, strikes the
line with date and PR) and by the engineer, who feeds queued arXiv ids
to distill ahead of the daily intake (ADR-35).

Format: `- [ ] arxiv:<id> — why — asked by skills/<slug> — YYYY-MM-DD`
