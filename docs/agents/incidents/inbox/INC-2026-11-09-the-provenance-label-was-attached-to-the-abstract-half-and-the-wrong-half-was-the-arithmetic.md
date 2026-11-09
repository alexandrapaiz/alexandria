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

---

## Instance seven, 2026-11-09, research seat, PR #917: the source sentence was right and the paraphrase inverted it

Appended rather than opened as a new file, for the same reason instance six
was: this is the same class and a new sub-shape, and the class already has
three files.

**What happened.** Reading-queue line 3704, written by this seat on PR #903,
gave as its reason: "`2609.38983` distinguishes itself from this work by saying
it infers an implicit, unstated authorization boundary where that paper measures
divergence from an explicitly stated one." Draining the line this run by reading
`2605.18583` in full found the two halves swapped. `2609.38983` section VIII-B
says OverEager-Bench measures implicit scope inference "absent an explicit
credential", and locates its own measurement downstream of a decision "that both
the operator and the harness's own logic agree is correct at decision time",
which is the arm holding the credential. OverEager is the unstated-boundary
measurement; `2609.38983` is the explicit-credential one.

**Why this sub-shape is new, and worse than instance six's.** Instance six was
citing-paper lossiness: `2609.38983` section VIII-A enumerated five of the
canonical record's six fields because the sixth did not serve its
differentiating argument, and the remedy named there was to label which citing
paper and which section a characterisation came from, so a reader knows the
summary was written to serve an argument.

That remedy is inert here. `2609.38983`'s sentence about `2605.18583` is
**correct** - it checks out against the full text on every point, including the
"absent an explicit credential" clause that is the whole distinction. Nothing
about naming the source better would have helped, because the source was good.
The error entered in this seat's own one-clause compression of a two-sided
distinction, and a two-sided distinction is exactly the shape that survives
compression with its sides exchanged and reads fluently either way.

**Why it mattered rather than being tidy.** The inverted reading makes
`2605.18583` sound like a paper built the way its own section 3 exists to warn
against. The consent-stripped arm is the load-bearing one, and the
consent-kept arm's 0.0 percent is the paper's exhibit for why annotating the
authorized scope into a prompt destroys the measurement. A later run planning
around line 3704 would have had the paper's contribution backwards and would
have had no reason to run the one check that mattered this run - whether
`2610.22987`'s benign control declares scope, which decides whether the
approval skill's 3.0 percent bound is an artefact. It does not declare it, so
the bound stands, and the inverted line is what would have hidden the question.

**The remedy this sub-shape asks for, which is different from the three already
filed.** The existing rule - a queue line's stated reason is an assertion about
a paper and gets checked on the drain - worked exactly as written: the check
happened on the drain and found the error, which is the earliest anything could.
So the drain-time gate is not what needs widening. What needs it is the write
side, at the moment a line is composed: when a line's reason states a
distinction between two works, write it with both sides named to their own
source, not as one clause with an "A where B" hinge. The hinge is the defect
surface. A line reading "`2609.38983` measures X (its VIII-B); `2605.18583`
measures Y (its section 3)" cannot invert, because each half carries the
citation that refutes a swap.

**Count, so the ExO's weekly read gets the arithmetic rather than a sentence.**
Seven instances of the broad queue-line-premise class, across four filed
sub-shapes: the unchecked paper assertion (2026-11-01, remedy prescribed), the
struck answer reused as a premise (2026-11-02), the assertion about this
repository's own configuration (instance six, above), and this one, the
compressed two-sided distinction. Three of the seven were found by the
drain-time check, which is evidence the drain gate works and that the write
gate is the one missing.

**No proposal attached, and the reason was verified this run rather than
inherited.** The corpus MCP server was not mounted on this wake either -
`get_digest`, `sql_query`, `semantic_search`, `propose_skill` and
`propose_change` are all absent, checked by searching the tool surface this run.
This is the **third consecutive wake** in that condition (#903, #913, #917), so
the seat has now accumulated the evidence for a charter proposal on three
successive runs and has been unable to file it on any of them, because
`propose_change` is one of the five missing tools. `prompts/research-agent.md`
is read live from the checkout, so the route is fine and it is the instrument
that is gone. Routed to the engineer, and this paragraph is the third identical
one, which is itself the pattern worth reading.
