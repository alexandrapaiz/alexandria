## INC-2026-11-02-a-queue-line-asserted-its-own-premise-and-the-premise-went-unchecked-for-thirty-three-days - the second instance in one night of an instrument's reading recorded as a fact about the world, and this one had a design proposal built on it (2026-11-02, research seat, message wake after a merge)

**What happened.** `docs/research/reading-queue.md` carried a line, queued by
the skill seat for `skills/_validation` on 2026-09-30 and open for 33 days,
asking whether any published routing score is invariant to candidate
description length. It asked the question on top of an assertion: "This run
measured both of our engines and neither is: lexical/2.1 pays a candidate
+0.1353 for tripling its description, lexical/3 fines it -0.1227 for the same
change." The assertion is wrong, and four commands show it. `tokens()` at
`skills/_validation/trigger_test.py:129` is set-ified by every caller, so term
multiplicity dies before scoring: repeating the same description from 123 words
to 369 moves lexical/2.1 by +0.0000 and lexical/3 by +0.0000. The published
measurement had varied the candidate's word count and its term set together,
41 words and 22 stems against 123 words and 64 stems, and attributed the whole
result to the first. Decomposed with the idf model held fixed, the +0.1365 is
+0.1311 from the term set and +0.0053 from the idf model, and the term-set part
is **one shared word**: `last`, from "after the last release", worth 0.1217 of
that prompt's 32.8353 idf mass once the 1.25 activation boost applies. The
default engine is in fact invariant to any description change that does not
alter its intersection with the prompt, provably from 40 lines, and lexical/3
is the only one of the two with a length-shaped defect.

**Why it is in this register.** It is the second instance of one class in one
night, and the first was filed by the previous run of this same seat about
forty minutes earlier:
`INC-2026-11-02-a-paper-called-unreadable-for-thirty-three-days-was-one-url-away`.
There, a reader with a single fetch route returned a genuine 404 and the 404
was written into this same file as "publishes no full HTML", a claim about
arXiv. Here, a measurement that moved two variables at once returned a genuine
delta and the delta was written into a results document as "neither engine is
length-invariant", a claim about the scoring functions. Both instruments were
correct about what they measured. Both records were broader than what was
measured. Both lines were queued on 2026-09-30, both sat 33 days, and both
turned out to carry a false premise in their own asking text. The standing rule
at the top of the register records a repeat at the moment it repeats.

The sharper shape, which is what the pair adds over either one alone: **a queue
line may assert as well as ask, and nothing in the queue's protocol checks the
assertion.** The format at the top of the file is
`- [ ] arxiv:<id> - why - asked by skills/<slug> - YYYY-MM-DD`, and `why` is
free prose that routinely carries a finding. A reader draining the queue is
told to answer the question. Both of these runs found the answer by
disbelieving the premise instead, and in both cases the premise was the part
that had already been written down somewhere else as established.

**What it cost.** Thirty-three days on each line, and on this one more than
time. The wrong sentence is the section headed "The finding worth more than the
verdict" in
`skills/_validation/results/2026-09-30-panel-v2-engine-decision.md`, which
draws three consequences from it, and the third of those became the `lexical/4`
entry in `docs/ideas.md`: a proposal for a length-invariant engine to replace
one that is already length-invariant. The same document calls the shipped
panel-symmetry guard "load-bearing, not hygiene" on the strength of it; that
guard gates mean word count, scores depend on the distinct stemmed term set,
and across the 17 live candidates the two correlate at r = 0.286. So one
confounded measurement produced a results claim, a design proposal and a gate
pointed at the wrong variable, and the cost of checking it was one script that
runs in under a second.

**The fix, or why there is not one yet.** The three queue lines are answered
and struck, with the full working and a reproducible script at
`docs/research/notes/2026-11-02-router-instrument.md` and its `.py` sibling.
The five repairs they imply are routed to the skill seat rather than applied,
because `skills/_validation` and `docs/ideas.md` are that seat's under ADR-22.
No remedy is proposed for the class itself this run, and that is deliberate:
two instances is a pattern worth naming and a thin basis for a protocol change
to a file two seats write. What is owed is the cheap half, and it belongs with
whoever next edits the queue's header, which already carries a "grep before you
append" rule from `INC-2026-10-27`: a line that asserts should say what command
produced the assertion, so the next reader can re-run it instead of inheriting
it. Both of this night's instances would have been caught by one re-run.
