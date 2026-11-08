## INC-2026-11-08-the-sweep-for-ungated-rules-could-not-admit-the-rule-the-days-grade-turned-on (2026-11-08, writer seat, message run)

**Repeat of `INC-2026-11-02-the-twice-ruled-law-had-a-gate-on-the-generator-and-none-on-the-artifact`**,
which is itself a repeat of incident 20. That class is a rule stated
absolutely in `prompts/digest.md` with no command in this seat's instrument
able to return a verdict on an artifact breaking it. Recorded under the
standing rule at the top of this file.

**What happened.** The grade of 2026-11-08, six hours earlier on the same day
and in the same lane, named the figure dump as the single biggest weakness of
`2026-W44`, the newest edition the product serves. It counted it by hand,
because nothing in `docs/voice/check_voice.py` counted a number. The
generator's law 14 states four counts in one sentence group. Two of them,
"the longest paragraph: over about 100 words" and "sections running past four
paragraphs with no written turn", were rows in `axes` at a target of zero.
"Numbers in the heaviest paragraph: past three" had nothing. So on the
artifact whose figure density was the headline verdict, every count the file
could take passed, and `measure` printed `longest 87   over100 0`.

**Why this is the sharper instance of the class, and the reason it gets an
entry of its own.** The repair for the 2026-11-02 instance was a new gate on
the artifact, and the general repair the org keeps reaching for is a register
that sweeps for rules with no gate. That register exists here. `ungated` reads
`ABSOLUTE_RULES` and reports which of the generator's absolute rules the press
can refuse, and it was green on this one.

It was green because its admission test read "a row belongs here when the
generator gives it a target of zero, or says never, or the canon numbers it a
law and the owner has ruled on it twice." Law 14's fourth count has a target
of three. **The sweep built to find rules with nothing between them and a
reader was constitutionally unable to admit a rule whose target is a number
other than zero.** A gate's scope is part of its answer (L-A47) and this is
that defect one level up, in the register whose whole job is to find the
instances of it.

**Measured, so the entry is not an argument.** With the count built, all four
served editions fail the rule, at heaviest paragraphs of 8, 9, 10 and 16
against a target of 3, and three of the four fail it in more than a quarter of
their paragraphs. `2026-W39`, the edition the canon treats as the cleanest,
carries a 141-word paragraph with eight figures in it. The rule has never been
met by anything the press has published.

**Fixed in this pull request, on this seat's surface.**
`check_voice.py figures` is law 14's fourth count as a verdict, with four
pinned cases including the live specimen and the boundary that has to keep
passing, a row added to `axes` so `compare` holds it, and the readings that
decide what a figure is stated in the code beside it. `ABSOLUTE_RULES`'
criterion now reads "a target of zero, or a number with no budget attached to
it", which moves the denominator from 11 to 12 and the ungated count from 5 to
6. Ban list 158.

**What is not fixed and whose it is.** The new row is `UNGATED`, measured
rather than assumed: `tools/check_digest_quality.py` carries a `bare-number`
WARN, which is the generator's eighth count and a different rule, and nothing
there counts figures per paragraph. The press cannot refuse a figure dump
today. `tools/` is pipeline code and the writer charter's boundary says never
pipeline code, so the ask is in `docs/ideas.md` with `figures` named as the
reference implementation.

**No prompt diff, under step 3.** The rule is in the generator, deployed, with
its number in it, under a heading that calls the count a hard gate.

Ban list checked on this entry.
