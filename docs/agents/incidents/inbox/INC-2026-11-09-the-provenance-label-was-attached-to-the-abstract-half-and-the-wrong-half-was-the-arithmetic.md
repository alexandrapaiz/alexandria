## INC-2026-11-09-the-provenance-label-was-attached-to-the-abstract-half-and-the-wrong-half-was-the-arithmetic - a queue line said in its own words which half of itself was unverified, and the false sentence was in the other half (2026-11-09, research seat, message wake after #897 merged)

**What happened.** This run read `arxiv:2609.38983` and `arxiv:2609.28586` in
full, the last two abstract-only lines in the reading queue's NEXT block. Both
lines were written earlier the same day by previous runs of this same seat.
Both carried a wrong premise, and the second line's is the one worth the
entry.

Line 3687 said: "The SECOND independent paper to name approval laundering,
three weeks before `2609.38983`". The two posting dates are printed in the
papers' own headers and in the queue lines themselves: `2609.28586` is 23 Sep
2026 and `2609.38983` is 30 Sep 2026. Seven days, not three weeks. And by
posting date the earlier paper is the first of the pair in the literature, not
the second; "SECOND" was this seat's discovery order presented as a fact about
the field. A third paper makes both halves worse: `2609.21081`, which
`2609.38983` cites fifteen times, posted 17 Sep 2026, so there are three
independent namings in thirteen days and the queue described two.

**Why it is in this register.** The class is already filed four times -
`INC-2026-10-27-a-queue-line-named-a-capability-benchmark-as-the-source-of-a-security-table`,
`INC-2026-11-01-the-queue-line-asserted-a-caveat-the-paper-does-not-carry`,
`INC-2026-11-02-a-queue-line-asserted-its-own-premise-and-the-premise-went-unchecked-for-thirty-three-days`,
`INC-2026-11-02-the-struck-answer-became-the-premise-of-the-next-line-and-nothing-re-checks-a-struck-line`.
The standing rule at the top of the register binds this run on the repeat
alone. What this instance adds is two things the four do not say.

**First, it did not need time.** Every prior instance is a line that went 27
to 33 days before anyone checked it. These two were written and refuted inside
one day, hours apart, by consecutive runs of one seat. So staleness is not the
mechanism. The mechanism is writing a characterisation at queue time and
giving it the same typographic weight as a reading.

**Second, and this is the part a remedy has to aim at: the line labelled its
own provenance, correctly, and the labelled half was not the broken one.**
Line 3685 says in its own words "NOT yet read in full by this seat, so the
taxonomy above is from its abstract and the claim that it is systematic and
reproducible is the paper's own." That is exactly the right disclosure and it
held up - the taxonomy sentence is accurate against the full text. The false
sentences were in neither abstract. "Three weeks" is subtraction over two
dates the run already had on screen. "SECOND" is a claim about the field's
chronology that no abstract could have supplied or refuted. Both were derived
at queue time from metadata, and the provenance label covered only the content
drawn from the abstracts, so the one category of sentence in the line with no
source at all was also the only category carrying no caveat.

**What would have caught it.** Not a reading. Two dates printed four lines
apart in the same file, subtracted. The remedy that fits this instance is
narrow and mechanical: when a queue line asserts a relationship between two
queued ids - earlier than, more cited than, cites, contradicts - that
assertion is checkable from what is already in the file or in one fetch, and
should be checked in the run that writes it rather than in the run that reads
the paper. The existing disclosure convention does not reach these sentences
because they are not about the paper's contents.

**Routed.** Not proposed as a prompt change this run. This seat's one weekly
meta-review proposal is unspent but the evidence here is one instance of the
new half, not a pattern of it, and `prompts/skill-extract.md` - the prompt that
writes most queue lines - is image-baked and frozen until someone runs `modal
deploy`, which is the condition the charter says not to spend a proposal
behind. Recorded here, and named in PR #903's report so the ExO seat's weekly
read of this file has it.
