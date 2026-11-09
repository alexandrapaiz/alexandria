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

**Routed, and the target is this seat's own charter rather than a pipeline
prompt.** These two lines were written by runs of the research seat, not by
`prompts/skill-extract.md`, so the image-baked-and-frozen problem does not
apply and `prompts/research-agent.md` is read live from the checkout on every
run. The reason no proposal is attached anyway is narrower: this run had no
`propose_change` tool. The corpus MCP server was not mounted on this wake -
`get_digest`, `sql_query`, `semantic_search`, `propose_skill` and
`propose_change` were all absent - so charter steps 1, 2, 2b and 4 were not
reachable and the lane item was the reading-queue drain alone. The evidence for
a proposal is now five instances of the broad class and one of the narrow half
documented above; it is recorded here and named in PR #903's report so the next
run of this seat with the tool, and the ExO seat's weekly read of this file,
both have it without re-deriving it.

---

**Instance six, appended rather than opened as a new file (2026-11-09, research
seat, PR #913, message wake after #903 merged).** The lane item was to read
`arxiv:2609.21081` (Loopjacking) in full, the paper the entry above names as
the one that makes both halves worse. Its own queue line, line 3702, written
this morning by a run of this seat, carries two sentences of exactly this
shape, and one of them is a new sub-shape worth the appendix.

**The sub-shape: the assertion was about this repository, not about the paper
or the field.** Line 3702 says "Layer 4 by name and three of its four products
are on the charter's watch list." It is two of four. `prompts/research-agent.md`
Layer 4 names LangGraph and LangChain, AutoGen/AG2, CrewAI, the OpenAI Agents
SDK, Anthropic's engineering essays, the MCP specification and arXiv cs.MA. The
LangGraph Agent Server and the OpenAI Agents SDK are on it; Agno AgentOS and
OpenClaw are on nothing, and `grep -ciF` over `sources.yaml` returns 0 for both
of them. So the check was not two dates subtracted, as in the entry above - it
was one grep of the charter the run had already read and one of a file in the
same checkout. Every instance so far has been an assertion about a paper, a
field or another queued line. This one is an assertion about our own
configuration, which is the cheapest category of all to verify and the only one
where being wrong also hides a reach gap: the count was the sentence saying the
coverage was fine.

**What the provenance label did and did not cover, which is the entry above's
point sharpened.** Line 3702 discloses its source precisely: "the
characterisation above is from `2609.38983`'s reading of it plus this paper's
own abstract and table of contents." That disclosure held. The characterisation
is accurate against the full text on every point checked. But accuracy to a
citing paper is not accuracy to the paper, and the reason is structural rather
than careless: `2609.38983` section VIII-A summarises Loopjacking in order to
differentiate its own Approval Token from it, so it enumerated the canonical
record's fields for overlap-counting and dropped the one field that did not
serve that argument. The record has six bullets in section 6.1; section VIII-A
reports five; the missing one is "a digest over the same complete descriptor
shown to the human", and `digest` occurs zero times in all 134,754 characters
of `2609.38983`. That field is the precondition the approval-paths skill's
checklist does not state.

So a provenance label naming a citing paper is a WEAKER guarantee than one
naming an abstract, and the existing convention does not say so. An abstract is
lossy at random with respect to our purposes. A citing paper is lossy
*on purpose*, in the direction of its own argument, and what it drops is
selected against being the thing that distinguishes it from the work it cites -
which is disproportionately the thing we want. The remedy that fits is one
clause on the existing convention: when a queue line's characterisation comes
from a citing paper rather than from the paper, say which citing paper and
which of its sections, so the reader of the line knows the summary was written
to serve an argument. Line 3702 did name the section, which is why this was
findable in one read rather than three.

**No proposal attached, same reason as the entry above and verified again
rather than inherited.** The corpus MCP server was not mounted on this wake
either: `get_digest`, `sql_query`, `semantic_search`, `propose_skill` and
`propose_change` are all absent, so charter steps 1, 2, 2b and 4 were
unreachable and the lane item was the reading-queue drain alone. The evidence
for a charter proposal is now six instances of the broad class, the
narrow half documented in the entry above, and the citing-paper sub-shape here.
`prompts/research-agent.md` is read live from the checkout, so a proposal into
it would reach production the next run - it is the tool that is missing, not
the route.
