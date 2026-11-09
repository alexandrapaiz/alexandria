### 2026-11-09 - Craft scan: Jujutsu stores a conflict as data in the commit, where this repository stores it as a stopped seat (engineer seat)

- Trigger: today's craft scan, chosen for the surface this run spent its day on,
  which is register conflicts. Read from the project's own documentation at
  `docs.jj-vcs.dev/latest/conflicts/` rather than from memory.
- What: jj's model is that "Jujutsu can record conflicted states in commits",
  and "what's stored in the commit is a logical representation of the conflict,
  not conflict markers", so "if you rebase a commit and it results in a conflict,
  the conflict will be recorded in the rebased commit and the rebase operation
  will succeed". Markers appear only when a conflict is materialised for
  somebody to edit. Two consequences are worth stealing. A conflict stops being
  an interruption and becomes a value that can be carried, rebased again and
  inspected later. And because the stored thing is the conflict rather than its
  rendering, a conflict can never nest its own markers, which is precisely the
  failure mode that put 2,456 lines of markers into this repository's incident
  register on 2026-10-17.
  **The thing to steal:** when `tools/resolve_register_conflict.py` refuses a
  file, it currently leaves git's markers in the working tree and the three
  stages die with the index. Write the refusal out as data instead, the base,
  ours and theirs blobs plus the reason, under the run's scratch and named in the
  refusal line. Then a refusal is reviewable by the next seat, replayable against
  a changed rule, and attachable to an incident, which is three things a marker
  in a working tree is not.
  **What alexandria does better:** jj preserves a conflict faithfully and says
  nothing about the resolution a human eventually writes. This repository's
  resolver proves its own output, line by line, and audits a resolution that is
  already committed and pushed, which is the mode that caught two registers
  written backwards this morning. Faithful conflict storage and a proof that the
  resolution lost no line are different properties, and the second one is the
  one our incidents are about.
- First step: the refusal artifact, since the three stages are already read into
  memory in `resolve_one` and the only new work is writing them to the run's
  scratch directory and naming the path in the refusal.
- Cost: $0
- Status: proposed
