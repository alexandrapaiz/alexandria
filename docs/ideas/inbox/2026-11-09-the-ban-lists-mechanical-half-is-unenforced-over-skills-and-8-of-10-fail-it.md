### 2026-11-09 - The ban list's mechanical half is unenforced over `skills/`, and 8 of 10 skills fail it (skill seat, for the writer and the engineer)

- Trigger: the skill charter's pre-ship check names `docs/voice/ban-list.md`
  "for skill descriptions, which readers see". This run ran it, which is the
  second gate the charter asks for, and the file it was revising failed with 11
  findings. The 11 were pre-existing on `main`, identical in count.
- What: `python3 tools/ban_list.py skills/*/SKILL.md` returns **59 findings
  across 8 of 10 skills**. Every one of the 59 is entry 13, U+2014, and every
  one sits on a `provenance.papers` line, where this seat has been writing
  `Title (U+2014) arxiv.org/abs/NNNN` as the separator since the library started. Per
  skill: context-window-engineering 13, evaluation-integrity 11,
  recursive-harness-self-improvement 10, self-improving-post-training-loops 7,
  skill-library-engineering 7, harness-engineering 5,
  agent-security-measurement 4, agent-memory-selection 2. The two that pass are
  `agent-approval-paths` and `agent-containment`, the two most recently written,
  which already use `Title (arxiv.org/abs/NNNN)`.
- It is reader-facing, which is what makes it an entry rather than a taste
  note: `site/lib/skill-provenance.js` returns `papers` verbatim to the page, so
  the character reaches a reader, and entry 13's own argument is that a search
  box and an agent loading the text both match on ASCII and neither matches on
  this.
- `docs/agents/registers.md` row `docs/voice/ban-list.md` reads
  "closed for copy outside the digest", with the gate named as "writer appends,
  writer gates, same seat daily". Nothing in that row reaches `skills/`, and the
  one charter sentence that does is a prose instruction to a seat rather than a
  check anything runs. This is incident 20's class, measured: the register has
  the gate that decides something gets written down and not the gate that
  decides something gets checked before it ships.
- First step, and it is two small ones in different seats. (1) Engineer:
  `tests/test_skill_receipts.py` already opens every `SKILL.md`; add
  `tools/ban_list.py`'s mechanical six to it, which makes this class impossible
  to reintroduce. (2) This seat: 48 separators across 7 skills, one character
  each. This run fixed only `evaluation-integrity`'s 11, because the other seven
  are seven revisions and the charter allows one skill per run, and because a
  reader-facing edit to a skill invalidates its trigger receipt and should be
  measured rather than swept.
- Cost: $0
- Status: proposed
