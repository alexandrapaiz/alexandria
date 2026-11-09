### 2026-11-09 - A register has a direction, and no file in this repository declares it (engineer seat)

- Trigger: answering the precedence question the ExO seat routed to this seat
  from owed row 17. The question was which order this repository's registers
  want, and the only way to answer it was to measure: count the stamps on the
  entry headings of all 16 registers and compare each consecutive pair. Every
  register that carries stamps is ascending-dominant, `docs/ideas.md` 81 ascents
  to 32 descents, `docs/agents/incidents.md` 63 to 24,
  `docs/agents/learning-log.md` 18 to 3, `docs/agents/hq-relay.md` 18 to 6,
  `docs/research/reading-queue.md` 12 to 1. So the answer is clear and it was
  nowhere written down, and two tools could disagree about it for a whole
  morning because neither had anything to read.
- What: `tools/check_registers.py` owns the register list. Give each register a
  declared direction beside its path, then ratchet the inversions rather than
  forbidding them: the existing descents are backdated entries and real history,
  so the gate pins today's count per register and fails when a count goes up. A
  new inversion in an append-only file is almost always one specific event, which
  is a merge resolution that wrote the register backwards, and that is the exact
  defect `tools/resolve_register_conflict.py` was rebuilt this morning to stop.
  The ratchet catches the instances the resolver never saw, because a hand
  resolution is most of them.
- First step: publish the per-register table above as a pinned baseline in the
  register checker, with the counting done by the resolver's own `stamp()` so
  one reader of a heading serves both tools. One file, one test, no new
  dependency, and the baseline is already measured.
- Cost: $0
- Status: proposed
