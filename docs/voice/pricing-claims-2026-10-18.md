# Site copy: the pricing page, graded against the archive it describes

**Headline: the free column of the page where a stranger decides to subscribe
promises a complete archive, and one of the two issues in that archive is
withheld from the public by the owner's own order. The sentence was written on
2026-09-18 and her order came the next day, so it has been false for the whole
thirty days it has been live, and no press failure was needed to make it
false.**

Writer seat, 2026-10-18, fourth run of the day. One copy round, drafted here
for the owner to rule on and the frontend seat to set. `site/app/pricing/page.jsx`
is not this seat's file and nothing in `site/` is touched by this pull request.

Taken from the board: card `af60726e`, "The pricing page promises a complete
archive the press has not kept for two weeks", filed in Backlog on the frontend
seat with the division named in its own body, "the frontend seat's surface per
the claims-gate list, with the writer seat advising on the words". The words
did not exist. This file is them.

## What the card got right, and the one thing it got wrong

The card dates the defect to the press: two weekly sends missing, newest issue
on record 2026-W40 of 2026-10-05, so the archive has a two-week hole. That is
true and it is the smaller half.

The larger half is that the archive was never complete and was never going to
be. `site/lib/content.js:23` reads `HIDDEN_WEEKS = new Set(["2026-W37"])`, and
the comment above it says why: "2026-W37 is retired here on the owner's order
(2026-09-19) so that Monday's issue is the pilot the public reads first." One
issue is deliberately withheld from the listing and from its own route. So the
word "complete" was contradicted by her own decision a day after the bullet was
written, and it would still be wrong on a week when the press printed perfectly.

That distinction decides what this round may and may not do, and it is worth
stating plainly, because it is the difference between fixing a sentence and
laundering an outage. **Cadence describes the intent and completeness describes
the record.** A weekly publication that misses two Mondays is a publication with
an outage, and no newsletter rewrites its cadence line while it is down. So this
round does not touch "The weekly digest, by email" or "every Monday": those
sentences are a promise the press is currently failing, and the fix for them is
the press, on the engineer's card. What this round takes out is the claim about
the record, because that one is false on its own terms and a repaired press
cannot make it true again.

One threshold is named rather than hedged, so the next run has a number instead
of a judgment. If a third Monday passes with no send, "every Monday" has stopped
describing an outage and started describing the product, and the word goes.

## The company standard this round's method comes from

`docs/standards/lessons.md`, L-A24: health is measured on the thing the company
ships, and where a scheduler and an artifact disagree, the artifact wins. Its
second consequence is the one that applies here, that only an outside observer
reading the artifact catches a run that never happened, because a scheduler
reports its own intentions.

The same move works on a sentence. Every grade this page has ever had read the
page. This one read the archive the page describes, which is two markdown files
under `site/content/issues/`, one of them hidden, plus whatever rows the press
has written to `digests`. The sentence and the shelf disagree and the shelf wins.

## The claims gate, per the charter's step 1b

`docs/agents/quality-claims.md`, run line by line over every sentence on the
page a reader could answer with "how do you know that". Eleven rows exist in
that register. **One of them names this file.** The free column has no row at
all, and the free column is the whole page for every visitor who is not already
buying.

| Live sentence | Where | Row in the register | State | Verdict |
| --- | --- | --- | --- | --- |
| "The complete archive" | `pricing/page.jsx:41` | none | — | **Drop.** One of the two published issues is withheld by her order of 2026-09-19, and the series is missing 2026-W38, W41 and W42. False by design and false by outage. |
| "Every issue in full" | `pricing/page.jsx:40` | none | — | **Keep.** This is the vision's own §0 as amended 2026-09-17, and `site/lib/content.js` enforces it: "an issue has no teaser split and no entitlement check: the whole body is public." |
| "the routines that keep it current as the research moves" | `pricing/page.jsx:27` | "revised when the research sharpens it" | **queued** | **Drop the clause.** Zero revisions have ever fired. The tier below it already carries "Routines, once they ship", so the page states the same thing twice to two different standards of honesty. |
| "Skill updates as the research moves" | `pricing/page.jsx:35` | "revised when the research sharpens it" | **queued** | **Replace.** Named in this seat's round of earlier today and still live. A claim that cannot stand without apology is a claim to drop (ban list 50). |
| "Routines, once they ship" | `pricing/page.jsx:36` | routines, not built | not built | **Keep.** This is the hedge the writer charter cites as the house form, and it is the only sentence on the page that gets a missing mechanism right. |
| "It can renew automatically, or it can stop at the end of each month until a reminder arrives" | `pricing/page.jsx:92` | none | — | **Rewrite to the future.** `grep -rn "reminder"` over `pipeline/`, `site/` and `tools/` returns exactly one hit, which is this sentence. Her billing principle of 2026-09-13 is recorded in `docs/vision.md` as "a hard requirement on the Stripe implementation in Phase 2", so it is a decision about what will be built. |
| "Payment and invoicing run through Polar, which is the seller of record" | `pricing/page.jsx:97` | none | — | **Rewrite to the future.** The board's own engineer card reads "Wire Polar's three products end to end, ready the moment the account exists." |
| "The full skill library, file by file" | `pricing/page.jsx:33` | none | — | **Not resolvable by any wording, and not reopened here.** All nine skill files are public in the repository. This seat put the question to her earlier today and it is hers: are the skill files the paid product, or the free distribution that sells something else? |
| "Three days free first, and the card is only charged when the trial ends" | `pricing/page.jsx:45` | none | — | **Keep, conditional.** It renders only when a trial checkout link is set, so the page already gates this one on the mechanism existing. That is the pattern the rest of the page should have copied. |

Two things that fall out of the table and are not about any single sentence.

**The register's net was cast over the skills and the corpus, and the money page
was outside it.** Eleven rows: six on the skills, four on the corpus and the
graph, one on the issue. The page where a visitor is asked to pay has one row,
for a claim it shares with two other surfaces, and nothing covers the three
bullets that sell the free tier or the two paragraphs that describe how the
reader's card will be treated. The register is the ExO seat's file and widening
it is that seat's call, so this is filed and not fixed. It is the finding this
round would want kept if nothing else survived.

**The page contradicts itself about whether it can take money.** The waitlist
block says "The weekly issue is free while subscriptions are comped, so there is
nothing to pay and nothing to cancel", and sixty lines further down the billing
note tells the reader in the present tense how their subscription behaves and
where their invoices come from. One page, two tenses, and the correct one is
upstairs.

## The candidates

One per slot, not three. Nothing here is a hedge of the sentence it replaces;
in every case the claim is dropped and the slot's job is carried by something
that can be checked. That is canon law 15's rule and ban list 50's, and the
reason both insist on it is that a concession reads careful and leaves the
falsehood standing.

The counterweight is ban list 52, the fix by deletion: a ruling against how an
element was written is never a ruling against the element. So no slot on this
page is left empty. Each one keeps the job it was doing and says a true thing
while doing it.

### 1. The free tier's third bullet

Now:

> The complete archive

Candidate:

> Back issues on the site, no account needed

What the slot is for is telling a stranger that arriving late costs them
nothing, and the true version of that is stronger than the false one, because it
adds a fact the page has never told anybody. There is no entitlement check on an
issue route. `site/app/library/[week]/page.jsx:7` says so in its own comment: "a
signed-out visitor reads the entire issue." Nobody reading the pricing page
today learns that, and "no account needed" is the sentence a reader who has been
asked for an email address by four newsletters this month actually wants.

The word "free" is not in it on purpose. The column header above it already says
Free, the bullet above it says in full, and a third repetition in four lines is
the page insisting.

### 2. The page intro's third clause

Now:

> The weekly digest stays free and arrives in full. The paid plan opens the
> skill library, in the same files you read and your agents load, and the
> routines that keep it current as the research moves.

Candidate:

> The weekly digest stays free and arrives in full. The paid plan opens the
> skill library, in the same files you read and your agents load.

This is the one deletion in the round, and it survives ban list 52 because the
element does not leave the page. Routines are still in the tier below, in the
hedged form the charter names as the model, and that form is honest where this
clause is not. The page said routines twice and only one of the two was true.

### 3. The paid tier's fourth bullet

Now:

> Skill updates as the research moves

Candidate:

> Every skill names the papers it came from and when it was last checked

The slot's job is the promise that what the reader buys does not quietly go
stale. Today nothing in the org can keep that promise, because zero revisions
have ever fired, so the slot moves from the promise to the receipt. The receipt
is real and it is measured: the claims register records "the last trigger test
that judged it" and "when it was last checked" as **held**, at 27 of 27 cases on
the 2026-09-30 bundle, and calls it the strongest receipt on the site.

One caution rides with this candidate, from that same row, and it is the reason
the bullet says "names" and "checked" rather than anything stronger. A date is
evidence that somebody looked. It is not evidence that the skill is good, and
the register warns that this receipt is the easiest one on the site to mistake
for evidence of value.

### 4. The billing note

Now:

> You choose how your subscription behaves. It can renew automatically, or it
> can stop at the end of each month until a reminder arrives and you decide to
> continue. Many subscription businesses count on being forgotten, and we would
> rather earn the renewal than collect it.
>
> Payment and invoicing run through Polar, which is the seller of record and
> handles tax wherever you are. Your card details never reach this site.

Candidate:

> Nothing is charged yet, because the paid plans are not open. When they open, a
> subscription renews automatically unless you choose the other way, which is to
> let it stop at the end of each month until a reminder arrives and you say yes.
> Many subscription businesses count on being forgotten, and we would rather
> earn the renewal than collect it.
>
> Payment and invoicing will run through Polar, the seller of record, which
> handles tax wherever you are. Your card details never reach this site.

The form is copied from `site/app/routines/page.jsx` rather than invented, since
that page is the one the writer charter names as the house hedge: state the
absence flatly first, then describe the future in plain future tense. "None of
them are built yet. When they ship, one will watch a topic." No "aims to", no
"designed to", because those are ban list 50 in a coat.

Her principle of 2026-09-13 stays whole, and so does the sentence that carries
it. "We would rather earn the renewal than collect it" is a statement of how
this company intends to behave, which is a legitimate thing for a page to say in
the present tense, and it is the best line on the page.

## What this round does not touch, and why

**The press gap.** Two missing sends are a press failure, not a copy defect.
Engineer card `92ab912d`, "Press: no issue for 2026-W41".

**"The weekly digest, by email" and "every Monday".** Cadence is intent. See the
threshold above.

**Whether the skill files are the paid product.** Put to her earlier today in
`docs/voice/skills-copy-2026-10-18.md` and still hers to answer. No wording
fixes an entitlement the repository gives away.

**`docs/voice/value.md` still says "Status: awaiting her approval", and it still
says "A new issue every day" while the product is weekly.** The status line is
hers and this is the fourth run to work around it. The cadence line is this
seat's file and could be corrected in this pull request, and is not, because a
page whose approval is pending should not be edited underneath the approval.
Both are named here rather than noted a fifth time.

## The registers this candidate was checked against

- `docs/voice/taste.md`, first and line by line. The ruling that bites hardest
  is 2026-09-19, where she rejected the library page's prose beginning "Every
  issue, in full...". The construction this round removes is that construction,
  on a second surface, thirty days later.
- `docs/voice/canon.md`, law 15 and its closing paragraph, which is the authority
  for grading this page at all: "This binds every surface, not only the issue:
  the masthead, the email, the site, and any line of copy drafted under this
  canon. Standing copy fixed in code is where it hid for the whole life of the
  product, because a string that never changes is never graded."
- `docs/voice/ban-list.md`, entries 50, 52, 60 and 61, and one new entry
  appended by this run.
- `docs/voice/value.md`. The free-tier bullet is the only slot in this round that
  touches the library rather than the skills, and "back issues" is the library
  in the one place the pricing page can gesture at it.
- `docs/voice/preferences/`, newest first. `library.intro` is the most-rejected
  slot in the dataset, six rejections and no approved row, and two of the six
  are the free-and-permanent promise: "All of them are free, and they stay up"
  and "Free, and it stays that way." The candidate above is in a different slot
  and a different form, and it drops the word "free" for the reason she rejected
  those two, which is that the fact is not the selling point.
- `docs/agents/quality-claims.md`, the table above.
- `docs/agents/copy-pipeline.md`, read once before this round.
