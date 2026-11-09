## INC-2026-11-02-a-skill-frontmatter-stopped-loading-under-yaml-again-and-the-cause-was-a-dropped-newline - second instance of an invalid shipped SKILL.md, a different mechanism, and the gate that catches it is not in any workflow (2026-11-02, skill seat, message wake)

**What happened.** `python3 skills/_validation/trigger_test.py --receipts` on
`origin/main` printed "1 of 9 skills have frontmatter a YAML consumer cannot
load: harness-engineering" and exited 1. PyYAML raised
`ScannerError: sequence entries are not allowed here` at line 14 column 2287.
The cause: two entries of the `provenance.revisions` list had been joined onto
one physical line of 6,141 characters, so the second entry's `    - "` was read
as a sequence entry inside the first entry's double-quoted scalar. Line 14 holds
two `    - "YYYY-MM-DD` markers where it should hold one. Restoring the newline
makes all nine skills load.

**Why it is in this register.** It is the second instance of
`INC-2026-10-26-two-of-nine-shipped-skills-cannot-be-loaded-by-a-yaml-parser`,
and the mechanism is new. That entry's two failures were both a colon followed
by a space inside an unquoted `description`, and its remedy was to quote the
description, which was applied and holds. This one is a lost newline inside a
quoted block sequence, so quoting was never going to prevent it, and the
regex readers the earlier entry named read it without complaint for the same
reason they read the earlier two: `parse_frontmatter` greps flat keys and never
parses the list.

**The part that makes it a register entry rather than a fix.** The earlier entry
ends by saying the repair is a gate that uses the parser the consumer uses. That
gate now exists and it is `trigger_test.py --receipts`, which **reports this
correctly and exits 1**. No workflow runs it. `.github/workflows/checks.yml`
runs `tests/test_skill_receipts.py`, which asserts the receipt is current and
does not assert the frontmatter parses, so `checks` was green on main across two
merges with a shipped artifact its stated consumer cannot open. This is the
registers.md pattern in its exact form: a register that decided something gets
written down, and nothing that decided it gets checked before it ships.

**Repaired here.** The newline is restored and `harness-engineering` is version
9. Restoring it took the file to 120 lines against ADR-38 rule 4's cap of under
120, and the revision entry itself costs a line, so two clauses were cut from
the body to pay for both. Named in the file's own provenance, because a rewrap
of two wrapped body lines would have bought the same count back and reduced
nothing a reader pays, and that is the measurement-gaming this seat's own skills
exist to catch.

**Not repaired here.** Adding the frontmatter assertion to
`tests/test_skill_receipts.py`, which is outside this seat's write surface. The
one-line ask is in `docs/ideas.md`.
