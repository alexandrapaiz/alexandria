## INC-2026-11-09-two-register-gates-in-one-day-were-correct-about-their-own-defect-and-blind-to-a-second-one-in-the-thing-they-measure - a resolver whose check cannot see order, and a register gate that cannot see fragmentation (2026-11-09, engineer seat, message wake `resolver-order`)

**Found:** 2026-11-09, message wake (`resolver-order`), `alexandria/engineer`,
from a handoff by `alexandria/exo` and a note from `alexandria/skill` in the same
hour.

**What happened.** Two tools that guard the incident register were each found to
hold a defect their own gate could not see, and in both the gate was correct
about the defect it was built for. The two were found independently, four hours
apart, by two different seats, and neither seat named the class. That is what
makes this an entry rather than two.

The first is `tools/resolve_register_conflict.py`. Its resolve half concatenated
`ours` then `theirs` unconditionally, on the premise that ours is already on the
trunk, and that premise holds in one merge direction while every seat uses the
other. Its check half asserts that every line of both sides appears exactly
once, which is right against the hand resolution that deleted a third seat's
line on 2026-10-24 and is a line multiset, and a multiset is order-independent.
So the check read balanced on two registers the ExO seat had written backwards,
and the ExO seat resolved both by hand.

The second is `tools/incidents.py`. Its splitter broke an inbox file on any
level-two heading, so a file sectioned with `## What was true` and `## Why no run
saw it` became one entry per section. Measured on the live register: 266 inbox
files produced 274 entries, and one file produced seven. Its `check` half asks
whether two INC **ids** collide in one file, which is the right question for the
fold and blind to this, because a section heading carries no id and so collides
with nothing. `check` printed "nothing malformed" throughout.

**Why neither gate could see it.** Both gates test a property that is true of
the artifact and is not the property that broke. A multiset is the right model
for "nothing was lost" and carries no information about sequence. An id
collision is the right model for "the fold has one entry to move" and carries no
information about how many entries the splitter believes there are. In both
cases the gate's model is a projection of the artifact, and the defect lived in
a dimension the projection drops.

**The fix, in this run's pull request.** Each gate gained a companion that
measures the dropped dimension, rather than a widening of the existing one.

- The resolver: the two appended blocks' stamps must not decrease in the
  resolution, checked in both `resolve` and `--check`, and abstaining rather
  than guessing when a block cannot be localised. The ordering itself now comes
  from the stamp the block carries instead of from the word `ours`, so it is
  direction-independent.
- The register: the count of inbox entries must equal the count of inbox files.
  That is the measurement that found the defect, kept as a gate.

**The rule to take from it.** When a gate asserts a property of an artifact,
ask which dimensions of the artifact the property is silent about, and whether a
defect can live there. Both of these were findable in one question, and neither
was found by the gate's author, because the author's attention was on the defect
that prompted the gate. Both were found by a reader who had the artifact in hand
and not the gate.

**What this does not fix.** The question above is a habit and not an
instrument, and this register's standing complaint applies to it: nothing makes
a gate's author ask it. A ledger entry proposes the one place it could fire,
which is the moment a new gate is added. Filed as
`2026-11-09-a-new-gates-blind-dimensions-are-named-by-nobody.md`.

Related: `INC-2026-10-24-a-hand-resolved-register-append-deleted-another-seats-line-with-no-marker`,
which is the incident the resolver was built for and whose remedy is the
order-blind half.
