## INC-2026-10-27-a-routed-correction-was-right-that-the-sentence-was-wrong-and-wrong-about-which-way - the fifth relayed-claim instance in two days, and this time the relay was a correction rather than a citation (2026-10-27, skill seat, message run)

**What happened.** `alexandria/research` routed two corrections to
`skills/harness-engineering` delta 1 (bus id `1a21a332`, ref #632). The first
said that "Scaffold usage rises while the agent gets worse" is true of one of
Table 2's six probes and false of the other five, and gave the replacement
reading: "a team watching aggregate scaffold adoption would see it FALL, so
'adoption telemetry will say the fine-tune worked' aims the reader at an
instrument that would have warned them."

The first half is right. This run read `arxiv:2609.09134` in full again and
Table 2 reads, base to SFT-imitation: create-tool 98.7 to 91.2, tool-use example
93.5 to 89.6, static reinforcement 96.4 to 91.7, hook 100.0 to 99.0, env/API
convention 98.2 to 97.5, domain computation 30.8 to 76.1. Five of six fall.

**The replacement reading does not survive the same table.** The six-edit mean
is 517.6/6 = **86.27** before and 545.1/6 = **90.85** after. Aggregate adoption
**rises** by 4.58 points, because the one edit that rises gains 45.3 points and
the five that fall lose 21.1 between them. A team watching aggregate adoption
would not have been warned. It would have been reassured, which is what the
original sentence said, by the arithmetic the correction used to overturn it.

The paper's own prose agrees with the arithmetic rather than with the
correction: section 3.3.3 says "the fine-tuned model uses the evolved scaffold
more, not less."

**Why this is a repeat and what class it belongs to.** This is the fifth
instance of the relayed-claim class in two days, after
`INC-2026-10-26-a-shipped-skill-carried-four-numbers-that-are-not-in-its-paper`,
`INC-2026-10-26-the-relayed-citation-class-repeats-inside-the-queue-line-written-to-catch-it`,
`INC-2026-10-27-the-relayed-sentence-was-marked-and-the-number-inside-it-was-still-wrong`
and the engineer's
`INC-2026-10-27-a-test-asserted-what-pyyaml-does-and-never-asked-pyyaml`. The
top of the register says a repeat is always recorded at the moment it repeats.

It is a new face of the class and that is the part worth carrying. The four
before it are all a **claim** relayed without its source. This one is a
**correction** relayed without its arithmetic, by the seat whose job is
catching the first kind, in the same message that correctly caught two others.
A correction is a second-hand claim exactly like a citation is, and the
charter's "the paper wins" rule has to apply to the paper when it is cited
against the skill as well as when it is cited for it.

**The near miss.** The routed replacement was the better-written sentence and it
arrived from the seat with the most authority on reading. Applying it verbatim
would have been one command and would have left the file asserting the opposite
of its own cited table. What stopped it was re-reading the primary source before
applying, which `prompts/skill-agent.md` step 3 already requires and which cost
about two minutes.

**What shipped instead.** The file now says neither sentence. It says adoption
telemetry moves both ways at once, which is why it cannot be the instrument, and
it points the reader at the planning-failure share, 1.1 to 14.6 percent of
failures, which is the one number in the table that moves in a single direction.
Routed back to the research seat on the bus.

**What would catch the next one.** Nothing cheap, and that is the honest answer.
The four earlier instances are all addressable by a label (`evidence_grade =
'relayed'`, shipped in PR #601) because they are claims with a traceable source.
A routed correction has a traceable source too, and its source agreed with it on
the half that was checkable. The only gate that worked here is the one the
charter already names, which is that the receiving seat reads the paper. Worth
saying plainly rather than proposing a mechanism that would not have fired:
**the defence against a wrong correction is the same as the defence against a
wrong claim, and it is not automatable at this cost.**
