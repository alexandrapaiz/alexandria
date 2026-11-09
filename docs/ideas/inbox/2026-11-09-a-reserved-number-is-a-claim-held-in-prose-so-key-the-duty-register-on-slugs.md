### 2026-11-09 - A reserved number is a claim held in prose, so key the duty register on slugs rather than on a sequence (exo seat)

- Trigger: this run performed the trunk merge the engineer seat handed back and
  its one conflict was `docs/agents/exo-owed.md`, where both sides had allocated
  row **16**. That is the third collision on this one file. The vendored
  `tools/resolve_register_conflict.py` refuses it, correctly: the file is not
  append-only, because its status column is edited in place, so "two appends" is
  the wrong model and there is nothing for the resolver to balance.
- What: the file's key is a sequence number, and a sequence number cannot be
  allocated by two parties that cannot see each other. Two wakes of one seat
  routinely compose appends in parallel against the same parent — that is the
  normal case here, not the exceptional one — and each correctly takes the next
  number.
- The attempted fix already failed in writing, which is the part worth keeping.
  An earlier run saw the collision coming, left row 16 **unallocated** for an
  unmerged branch, took 17 for itself, and wrote a paragraph explaining the
  hole. A later wake of the same seat took 16 anyway. It was not careless: a gap
  in a numbered column is unreadable as a reservation to a fresh context, and
  nothing but that paragraph said otherwise. **A reserved number is a claim held
  in prose, and a claim no instrument can read is not held.**
- First step: key each duty on its own slug, the way
  `docs/agents/incidents/inbox/` already keys incidents — `INC-<date>-<slug>`
  cannot collide and cannot be reserved, because there is no next one to take.
  The references to fix are the handful of "owed row N" mentions in
  `prompts/exo-agent.md`, the relay page and the run notes, and the mechanical
  half is that the renumbering then never has to happen again.
- Why not simply give the file a gate instead: a gate would catch the collision
  at merge time, which is where it is already caught, by hand, at the cost of
  one resolution each time. The number is the defect; a detector on it is a
  detector on a self-inflicted wound. This is also now a registered GAP —
  `docs/agents/registers.md` carries the row this run added, and the §3d sweep
  had never reached this file because the row did not exist.
- Cost: $0
- Status: proposed
