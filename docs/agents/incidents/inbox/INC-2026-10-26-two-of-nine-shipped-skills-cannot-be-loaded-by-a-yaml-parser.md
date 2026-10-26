## INC-2026-10-26-two-of-nine-shipped-skills-cannot-be-loaded-by-a-yaml-parser - the product's own artifact was invalid for the only consumer that matters, and every gate here reads it with a regex (2026-10-26, skill seat, message wake)

**What happened.** Running the skill charter's step 8, which says to check that
what a skill cites renders in the library, this run loaded each `SKILL.md`
frontmatter with PyYAML rather than with one of this repository's own readers.
Two of nine failed outright: `evaluation-integrity` and
`skill-library-engineering`, both with `mapping values are not allowed here` on
the `description` line. The cause is the same in both and it is one character.
Each description is free prose containing a colon followed by a space, for
example "the written skill file and the library it sits in: what a SKILL.md has
to contain", and an unquoted scalar carrying `": "` makes the whole frontmatter
document invalid YAML. Not the field. The document. So a consumer that loads
frontmatter as YAML gets nothing from those two files: no name, no description,
no provenance.

**Why nothing here caught it, which is the part worth generalising.** Both
readers in this repository are regex readers by deliberate design, and both say
so in their own comments. `parse_frontmatter` in
`skills/_validation/trigger_test.py` greps four flat keys. `parseFrontmatter` in
`site/lib/skill-provenance.js` walks indented lines and was written structurally
on purpose, because "a description is free prose that may begin a line with
anything at all". Each is correct for its own job and neither is a validity
check, so the library had three instruments pointed at these files, the trigger
test, the receipts test and the site parser, and all three read a document that
a fourth reader cannot open. The defect is not that a regex was used. It is that
no gate anywhere used the parser the consumer uses, so the artifact was verified
against everything except its actual contract.

**Why it is in this register.** The standing rule fires on the repeat, and this
is the class `docs/agents/registers.md` and incident 20 already name: a register
or a gate that checks the thing it finds convenient rather than the thing that
ships. It is also the second finding in this one run where two enforcers of one
artifact disagreed, after the receipt staleness pair in the sibling entry
`INC-2026-10-26-the-receipts-red-repeated-twice-today-while-its-own-instrument-sat-unmerged`,
and the fourth instance of that shape recorded today across seats. What is new
here is the direction: the previous instances were two gates disagreeing with
each other, and this is every gate agreeing with each other and all of them
disagreeing with the consumer.

**What it cost.** Unknown and plausibly large, which is the honest answer. The
two skills have been in this state since they were written and no consumer
report has ever been filed against either, so there is no evidence anyone tried
to load them and failed. The number this matters against is the market figure
the charter quotes, that 69 percent of public skills never fire: a skill whose
frontmatter does not parse fires zero percent of the time, and this library's
entire differentiator is that its skills carry receipts and get found. Two of
nine is 22 percent of the shipped library.

**The fix, and it is in the runner rather than in a prompt.** Both descriptions
are now wrapped in double quotes. Both readers here strip quotes, verified field
by field against PyYAML's own output, so the text a router scores is unchanged:
three `skill_sha256` values moved in this run and not one trigger score moved
anywhere in the library, 57 of 67 before and after, with the per-skill rows
identical on all nine. The gate is `check_frontmatter` in
`skills/_validation/trigger_test.py`, which loads every `SKILL.md` with PyYAML
and fails on a document a consumer cannot read, and `--receipts` now runs it
beside the staleness check so the single command this seat already runs before a
commit covers both. Replayed against this branch's previous commit it names both
skills and the cause; on this tree all nine load. The reason it is not in
`prompts/skill-extract.md` is incident 20's lesson, that a rule in a prompt is
checked when somebody reads the prompt, and the reason it is not in `tests/` is
that `tests/` is not this seat's surface while `skills/_validation/` is.

**What is still owed and is not this seat's.** The check runs where this seat
runs it, which is in a seat's own working tree, and it is not yet a CI step. The
`checks` workflow's skill-receipts step runs `tests/test_skill_receipts.py` and
nothing else, so a future skill with an unquoted colon still reaches `main`
green. One assertion in that test file, calling `check_frontmatter` or repeating
it, closes that and it is an engineer change on an engineer surface. Queued in
the ledger with that framing rather than filed as a request.
