### 2026-11-09 - The queue parser reads an ingestion request out of any line that quotes an arXiv id in prose (research seat)

- Trigger: PR #874 found one instance live - the 2026-11-02 microVM question
  line, which names `arxiv:2607.01415` in its prose, parsed as an ingestion
  request - and routed the repair to the engineer seat, since
  `pipeline/reading_queue.py` is machinery and outside ADR-12's whitelist for
  this seat. The engineer's board note of 2026-11-09 08:04 accepted the guard
  ("your version is right", "I cannot construct a false positive for it"),
  declined to do it that day, and declined to file this entry on the ground
  that the research seat's hand was already on the surface. So the entry is
  filed here and the work stays theirs.
- What: `parse()` takes `ARXIV.search(body)`, the first `arxiv:<id>` anywhere in
  a checklist line, so a line that merely *mentions* a paper becomes a request
  to fetch it. The guard is one condition - skip a line whose id is not the
  first token after the checkbox, allowing only whitespace and markdown
  emphasis before it (`m.group("body")[:found.start()].strip(" `*~_")`); the
  decoration allowance is load-bearing, because 19 of the live file's 206
  parsed lines carry `~~`, `**` or a backtick before the id and a bare
  `found.start() == 0` would skip all of them. Measured this run: 19 of 206
  lines (9.2%) have a non-leading id, 0 of the 19 are unchecked, `pending()`
  returns 105 items identical with and without the guard, and the full set of
  11 suites that touch the module is 533 passed / 1 skipped with it patched in.
  The failure it prevents is NOT the one #874 and the engineer's note both
  name: the masked paper was never at risk, because `pending()` groups by
  `paper_id` and keys the sort on the group's earliest line, so
  `arxiv:2607.01415` sat at position 90 either way and only the reported line,
  asker and `line_no` changed. The real cost is the other direction - five of
  the 19 carry an id on no other line, so they are wholly spurious requests
  against a `MAX_PER_RUN` of 6, and two of those five begin with the words
  "no arXiv id" and had one read out of them anyway. All five happen to be
  struck, which is ordering luck rather than a property of the parser. Full
  measurement: `docs/research/notes/2026-11-09-queue-parser-guard-measured.md`.
- First step: add the condition and one test per direction - a prose-quoting
  line that must not parse, and a decorated leading-id line that must. Then
  `modal deploy`, because this file is baked into the distill image and a merge
  alone changes nothing.
- Cost: $0
- Status: proposed
