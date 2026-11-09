### 2026-11-09 - The two-seat deadlock on `skills/` has a shape, and the carve-out is one charter line (engineer seat, for the owner)

- Trigger: the skill seat's handoff of 04:16Z asked this seat for a bundle
  commit: promote the gate's ban-list clause to an absolute, replace the
  tripwire, "then apply the substitution and commit the bundle in the same
  commit." The first two are this seat's files. The third is 48 characters
  across seven `SKILL.md` files, and `prompts/engineer-agent.md` line 89 says
  in one flat sentence that this seat does not write into `skills/`. So the run
  shipped two thirds of a change that was fully proven before it started, and
  the handoff's own closing line reads "second time today that work on my
  surface could only be finished in a file I may not open."
- What: the split ADR-13 draws is the right one and the deadlock is not an
  argument against it. ADR-13 reserves `skills/` to the reviewer panel because
  "autonomy applies to what the system knows, not to what the system is," and
  the engineer charter carries that as a path rule rather than as the test the
  decision actually states. A U+2014 swapped for a comma inside a
  `provenance.papers` list changes nothing the system knows: the skill seat
  hashed all ten `description` fields before and after and none moved, the site
  parser stayed 28 of 28, and the trigger suite returned 74 of 84 at 0.881 on
  both sides with zero of 84 cases changing verdict. Measured by ADR-13's own
  test that edit is machinery. Measured by the charter's path rule it is
  forbidden. Both readings are correct, which is what makes this the owner's
  line and not an argument either seat can win.
- Two carve-outs would each end the class, and they point opposite ways, so
  naming both is the useful part. **(a)** One sentence in
  `prompts/engineer-agent.md`: this seat may apply a repair under `skills/`
  when a gate in `tools/` both performs it and verifies it, and never otherwise.
  That is narrow enough to check, because the repair is a program rather than a
  judgement, and `tools/ban_list.py --fix` is the first instance.
  **(b)** The opposite sentence, which costs the engineer nothing and the skill
  seat one run: say plainly that a mechanical sweep is always the skill seat's,
  and that a gate promotion lands first with the library's debt ratcheted rather
  than cleared. This run built (b) without being able to authorize (a), because
  a seat does not widen its own authority.
- What shipped under (b), so the choice is between two live options rather than
  between a change and a plan: `tools/ban_list.py --fix` is the repair, measured
  at 48 swaps across 7 files taking the library to 0 findings over 10 of 10 on a
  copy of the tree. `ban_list_clause` is an absolute. The tripwire is a ratchet
  with a ceiling of 48 that names the command and the seat. So the skill seat's
  reverted sweep can now land green, in one command, on its own surface.
- First step: the owner reads the two sentences and picks one, or neither. section 21
  reserves a widening of a seat's own authority to her with no silence rule, so
  this waits rather than proceeding under section 22. If she picks neither, the status
  quo is (b) and it already works, which is the reason this entry is a proposal
  and not an `urgent`.
- Cost: $0
- Status: proposed
