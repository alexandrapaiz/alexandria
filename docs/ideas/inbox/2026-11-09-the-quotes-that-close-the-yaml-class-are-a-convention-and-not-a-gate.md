# The quotes that close the YAML class are a convention and not a gate

**Filed by** the skill seat, 2026-11-09, from the run woken by the red that the
class produced.

**What landed today.** Every `description` in `skills/*/SKILL.md` is now a
double-quoted YAML scalar, which makes the unquoted-colon break impossible to
write. That class had two occurrences, 2026-10-26 on two skills and 2026-11-09
on `agent-approval-paths` v7, and the second one cost a red CI run and the wake
that produced this file. The full account, including three false claims the
register held about the second occurrence, is in
`docs/agents/incidents/inbox/INC-2026-10-26-two-of-nine-shipped-skills-cannot-be-loaded-by-a-yaml-parser.md`.

**What is still open, and it is one assertion.** Nothing requires the quotes.
`--receipts` checks that the frontmatter loads, that the receipt is current and
that the description is inside 150 words. It does not check that the description
is quoted. So the library conforms today by the act of one run, and the next
skill written here can reintroduce the hazard by typing an unquoted value, at
which point the class is live again on that one file and the only thing standing
between it and a red is whether the author happens to use a colon.

**The ask.** One assertion in `check_frontmatter` in
`skills/_validation/trigger_test.py`: a `description` whose raw value does not
begin and end with a double quote fails `--receipts`. It is a two-line check, it
has no false positives, and it converts today's ten-file convention into an
invariant. The reason it is filed rather than applied is that the same run moved
all ten files, and a change that makes the library conform wants to be
reviewable separately from the gate that holds it there.

**Why it is worth the two lines, in the terms this seat is measured in.** The
charter's own market figure is that 69 percent of public skills never fire. A
skill whose frontmatter no loader will open fires zero percent of the time, and
the three readers in this repository are all regex readers that cannot tell,
which is the first occurrence's finding. The gate the first occurrence asked for
exists and works, so this is not a missing gate. It is the difference between a
gate that catches the defect after a commit and a rule that makes the defect
unwritable, and the second occurrence is the measurement of what the first costs:
one red run and one seat run, for a defect of one character.

**Surface.** `skills/_validation/trigger_test.py`, which is this seat's own, so
this is a note to the next run of this seat rather than a request to the
engineer.
