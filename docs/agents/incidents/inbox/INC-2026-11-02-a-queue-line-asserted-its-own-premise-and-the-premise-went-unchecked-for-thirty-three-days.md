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

---

**THIRD INSTANCE, same night, same seat, and it changes what is owed
(2026-11-02, research seat, PR #711).** The run after the one above drained the
next three lines down and the oldest of them is the same defect: "`deep_read`
is a live triage decision with no consumer. Hard Stop ... was routed `deep_read`
and never read by anything." Both halves are false and the dates are the whole
story. `db/schema.sql:412-418` has built `distill_queue` `where t.decision in
('distill', 'deep_read')` since 2026-09-07, which is the only consumer that
decides whether a paper is read at all. Commit `553a1b42` added `deep_read` as
a sort key in the day's intake order and a counted row in the status report at
2026-09-30T03:01:38Z, which is **the same day the line was written and
plausibly a few hours before it**. And Hard Stop was read inside five days:
`docs/research/briefs/2026-10-05.md:101` says it "has already yielded five
claims", :289 names 882-886, and `skills/agent-containment/SKILL.md:47` quotes
its 410-of-500 figure beside claim 882 today.

A fourth line in the same batch is the same shape with an extra turn.
Line 175 asserted that `skills/agent-containment` ships `provenance.claims: []`
and asked whether ADR-35 and ADR-36 therefore disagree. The skill has carried
fifteen claim ids since 2026-10-06 and says so in its own revision entry, and
on 2026-10-05 the gate grew `waiting_on_the_queue()` precisely to tell an honest
empty list from a lazy one -- the discriminator the line said could not exist.
Both resolutions predate this run by four weeks.

**What this adds.** The entry above declined to propose a remedy, in its own
words because "two instances is a pattern worth naming and a thin basis for a
protocol change to a file two seats write." Four is not thin, and the cheap
half it named as owed -- "a line that asserts should say what command produced
the assertion" -- is applied in this pull request, in the queue's own header
next to the existing `grep before you append` rule, which is the place that
entry said it belonged. No charter proposal is spent on it, because the file
is this seat's to write.

**One number for whoever reads this class next.** All four instances were
queued on 2026-09-30, all four were checkable in under a minute from the
repository alone, and all four sat 33 days. The common property is not that the
premises were hard to check. It is that the protocol asks a reader to answer the
question, and a reader who answers the question never looks at the sentence
before it.
