# The Obsolescence Report — the launch-day artifact

Proposed 2026-09-30 by the sales seat, for the owner's yes or no by
2026-10-02. Nothing here has been published, shown, or sent.

## The bet, in one paragraph

Do not launch with an announcement. Launch with a verdict. Every product in
this class publishes what is new, which means the whole class competes on
being first to the same papers. Alexandria holds the one thing none of them
holds, which is a record of which claims stopped being true, and that record
cannot be assembled retroactively by anyone, no matter how good their writers
are, because it is made of edges accumulated over time. So the launch-day
artifact is a dated report on what the research stopped supporting, and the
announcement is a paragraph inside it rather than the thing itself.

**The move that makes it work, and the reason to run this rather than admire
it: alexandria goes first in its own report.** Section one is the claims
alexandria has published that its own record now contradicts, by issue, by
date, with the paper that overturned each one. We grade ourselves with the
instrument before we point it at anything else.

That single choice does four things at once. It makes the report unattackable,
because the obvious attack on a company publishing other people's errors is
that it would never publish its own. It is the only real proof that the
evidence trail is load-bearing rather than decorative, since a trail that
never returns a verdict against its owner is a marketing asset pretending to
be an instrument. It is the answer to the question this audience actually asks
about an agent-run company, which is whether anything checks the agents. And
nobody launches a product by leading with its errata, which is why it will
travel.

## Why it beats the announcement post it replaces

The 2026-09-18 Hacker News draft is a good announcement and it is still an
announcement, which means it competes on interestingness against every other
launch that day and gets read once. The report competes on a different axis.
It is a reference document, it earns a link rather than an upvote, it is the
kind of page that gets cited months later by someone settling an argument, and
citation is the channel that compounds while posts decay.

It is also the only launch artifact that makes the paid product obvious
without arguing for it. A reader who finds one belief of their own in the
contradicted section has just been shown, at their own expense, that keeping
up by reading summaries does not work. Nothing in the copy has to say so.

## What the report is made of

Four sections, in this order. The order is the argument.

**1. What we got wrong.** Alexandria's own published claims that the record
now contradicts, from the two archived issues and the six skills. Each entry
names the issue or the skill, the claim in plain words, the paper that
overturned it, and the date the record changed. If the query returns nothing,
the section says so and states what it searched, because a company claiming a
self-correcting record and reporting zero self-corrections has said something
about its search, not about its accuracy.

**2. What the record stopped supporting.** Claims in the covered subject areas
that carried support and now carry contradiction. Plain words, both links,
both dates.

**3. What held up.** Claims that accumulated independent support over the same
window. This section is not a courtesy. A report that only ever finds fault is
a hit piece, and the instrument's credibility rests on it returning both
verdicts from the same query.

**4. What this covers, and what it does not.** The subject areas, the count of
papers read in full, and the plain statement that a claim absent from this
report is a claim the library has not read closely rather than a claim in good
standing.

## The honesty rules, which are not negotiable and are the product

1. **Claims, never people.** No entry names an author as wrong. A claim is
   contradicted; a person is not. An entry that reads as a verdict on someone
   gets cut, however good it is.
2. **No entry without both edges cited, both reaching full text.** If the
   supporting paper or the contradicting paper cannot be linked to its full
   text, the entry does not run. Abstract landing pages are not links.
3. **A thin section runs thin.** Four honest entries beat twelve padded ones,
   and the padding is the only thing in this document that could actually
   damage us.
4. **Section one goes first, always.** Moving it below the others converts the
   whole artifact into the thing it was designed not to be. This is the rule
   most likely to be quietly broken on the morning of the send, when section
   one looks embarrassing and the launch feels fragile. It is the section the
   report is for.
5. **No superlatives anywhere in it.** The document's authority comes from
   being checkable. One adjective doing persuasive work invites the reader to
   audit the tone instead of the citations.
6. **We do not claim the report is comprehensive.** Section four exists to
   refuse that claim before a reader makes it for us.

## The floor, so this is committable at T-13 rather than a hope

The report depends on a query nobody has run, against a graph whose coverage
this seat cannot measure from the repository. So it ships in one of two forms,
and the choice is made on 2026-10-02 from the query's actual return.

**Full form.** All four sections. Needs the contradicted-claims query to
return enough cited pairs in the covered areas to fill sections two and three.

**Floor form, and it is genuinely good on its own.** Section one and section
four only, titled for what it is: alexandria's own errata, at launch, before
anyone asked. Two archived issues and six skills against the current record,
which needs no new backend, no coverage assumptions, and no one else's claims.
It is one page instead of five, it keeps the entire surprise, and it is the
half of the idea that cannot fail to be true.

Decide by reading the query's output, not by preference. If the full form's
sections two and three would need padding to look substantial, ship the floor
form and say nothing about the other two sections.

## The schedule, with owners

Sales owns none of the building. Every row below is an ask, and the ask is
named so the owner can grant or refuse it in one pass rather than discover it
on 2026-10-12.

| When | Who | What | Blocks |
|---|---|---|---|
| 10-01 | owner | Yes or no on the idea, and yes or no to the self-errata section leading it. A no on the second is a no on the whole campaign, and the fallback is the 2026-09-18 announcement drafts as rewritten in this pull request. | everything |
| 10-02 | engineer | Run the contradicted-claims query over the covered areas and paste the raw return into this folder. The view already exists at `db/schema.sql:265`; the join onto cited claims is at line 281. No new backend. | form choice |
| 10-02 | sales | Read the return, choose full or floor, and say which in this folder with the count that decided it. | prose |
| 10-03 | sales | Run the same query against alexandria's own two issues and six skills for section one. | section 1 |
| 10-06 | writer | Prose pass on all sections under the canon, the reading verbs of law 15, and the 2026-09-29 sentence rulings. Sales drafts facts; the writer owns the sentences that ship. | page |
| 10-08 | frontend | The page, at a permanent path, with its own title, linkable per entry. An entry that cannot be linked to on its own cannot be cited, and citation is the entire distribution plan. | send |
| 10-09 | owner | Read it whole. Every line reaches her before it is set, which is her standing rule and not a courtesy. | send |
| 10-12 | sales | Final pass against the pre-send gate in `../../claim-ledger.md`, plus the ban list and the canon. | send |
| 10-13 | owner | Publish with the launch. The venue drafts in `../../launch/` carry the report as their subject rather than the product. | — |

## What the launch posts become if this runs

They get shorter and they stop arguing. The Hacker News post becomes the
report's title and two sentences, because a link to a document that grades its
own author needs no pitch underneath it. The launch email leads with section
one, since the free list is people who read this before it was a business and
are exactly the audience for which claims we got wrong. Every rewritten draft
in `../../launch/` carries a marked block showing what its opening becomes in
that case, so no draft has to be rewritten on the morning of the send.

## The risk, stated plainly

Section one can find something genuinely embarrassing, and the honest response
to that is to publish it and fix the claim, which is the whole premise. The
real risk is smaller and more likely: section one finds nothing, because the
library has read 174 papers in full and published two issues, and two issues
is not much surface to have been wrong on. In that case the section says what
it searched and returns nothing, and that sentence is weaker than a finding
but still true and still unusual. It is not a reason to skip the search, and
inventing an error to fill the section would be the single worst thing this
campaign could do.

Second risk, worth naming because it is the one a reader raises in the
comments rather than in private: a record that grades itself is not
independent. The answer is not to deny it. The answer is that every edge in
the report cites two papers a reader can open, so the grading is checkable
even when the grader is not disinterested. That answer is honest and it is
also incomplete, and the honest form of the incomplete part is to say that
outside verification is a thing the library does not have yet.
