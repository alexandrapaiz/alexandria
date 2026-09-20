# The voice canon

Where the newsletter's words come from. The owner was frequently
dissatisfied with the writing and structure because nobody owned the
words as a craft; this canon and the writer seat (ADR-28) fix that the
same way the design canon fixed the pixels. The writer seat reads this
file every run and evolves prompts/digest.md toward it. Adopted
2026-09-19, consolidating guidance that previously lived scattered
across charters and the voice-overhaul PR.

## The register

Morning Brew discipline with technical substance: simple language
carrying real technical weight, why-it-matters framing on every item,
and a reader who finishes smarter, not just informed. The reader is a
builder deciding what to do this week, and their agents load the same
findings, so precision is not optional.

## Scope: the issues and the site both

Her ruling of 2026-09-19, recorded in docs/voice/taste.md: this canon
governs SITE COPY as well as the newsletter. She rejected the library
page's prose and ordered the mission page rewritten under these laws,
with the outsider test binding hardest of all, because a page is where
a stranger decides what alexandria is before a single issue is read.

The division of work is the same one the design canon uses in reverse.
The writer seat drafts the words and the frontend seat sets them, so a
copy change arrives as a draft in docs/voice/ and lands in the site
through the frontend seat's own pull request. Three laws bite hardest
on a page: law 3, sell the product and never the recipe, because a
visitor meeting a description of the machinery has been handed the
blueprint instead of the building; law 12a, the outsider test; and the
design register's own rule that a heading never carries an explanatory
subtitle.

## References, and what to take from each

Study decisions, never copy sentences.

- **Morning Brew**: the register. Short sentences that move. An item
  earns its length; nothing pads.
- **Matt Levine (Money Stuff)**: how a distinctive voice carries dense
  technical material without drying out, and how honesty about
  uncertainty becomes charm instead of hedging.
- **The Economist**: compression. Say it in half the words, and let
  one concrete number do the work of three adjectives.
- **Stratechery**: structure that builds an argument across sections
  instead of listing items. The daily may list; the weekly must argue.
- **Import AI's "why this matters" line**: the named consequence per
  item, already adopted as the craft-scan finding from PR #23.

## The laws (owner's standing rules)

1. Plain sentences, transition words, no stylistic em dashes, no
   semicolon joins.
2. No buzzwords, ever. Every line targeted and actionable.
3. Sell the product, never the recipe.
4. The headline is a finding, not a greeting: a builder should know
   from one line whether to open the issue.
5. Relevance is impact, not recency: traction leads, and every
   ranking says what earned each slot (the relevance law).
6. Evidence grades in-line: "authors' own experiments, not yet
   replicated" is product, not weakness.
7. Honesty serves items, never the method: grade an item's evidence
   in-line, and disclose a bias or limitation only when it materially
   affects that day's content, in one plain sentence. The issue NEVER
   narrates its own methodology, ranking logic, or virtues (owner's
   ruling, 2026-09-19); method explanations live on the site, not in
   the reader's way.
8. Links go to the full text (arxiv.org/html/... when it exists, the
   abstract page as fallback): one less step between claim and
   evidence is the product promise.
9. The fine-tuned instruction is the foundation. The owner refined
   the digest's prose and structure herself in prompts/digest.md:
   the context-first invariant (never open with a finding cold, why
   before what, situate the reader in the subfield and its stuck
   problem first), institution-first attribution, varied sentence
   rhythm, depth following significance, and her four sections in
   her order: traction leads, then the genuinely new, then what fell
   behind, then the reading list. Her names for those four,
   Trailblazing, Gaining traction, Left behind and Read these
   yourself, label the slots for whoever writes the generator, and
   law 12 governs what the reader sees at the top of a section.
   That instruction is the base layer; the daily adapts
   it shorter, and nobody, chair or seat, invents parallel
   structures or taxonomy headings beside it (her ruling,
   2026-09-19, after "Compounding" and "New and unproven" were
   invented and rejected). Refinements layer ON TOP of her
   fine-tuning through the writer seat, with her merge. The weekly is the
   synthesis and must argue, not list.
10. "You read to decide. Your agents load to act." The dual audience
    appears in every issue's close.
11. Length follows the news. No fixed issue length at any cadence: a
    heavy day runs long, a thin day is honestly short. The amount of
    real news decides, never a template (owner's ruling, 2026-09-19).
12a. The outsider test and the density rule (owner, 2026-09-19).
    The whole issue reads by a smart builder outside the research
    world: every term of art defined in a plain clause at first use,
    no assumed vocabulary, and any sentence that needs the field's
    map already in the reader's head gets rewritten. Density is the
    twin: compression is fewer words per idea, never more ideas per
    line; short paragraphs, air between them, one idea per sentence
    by default. The grading pass reads each issue once AS the
    outsider before grading anything else.
12. Framework names never print. The structural slots (the
    traction-led lead, the new-and-unproven, what fell behind) are
    the generator's internal skeleton; every PRINTED heading is
    written fresh from that day's actual news, the way the title is.
    Printing "Gaining traction" or "Trailblazing" as a heading is a
    violation the owner has now flagged twice (incident 20).

## How an issue is graded

The daily review runs four passes, in this order, and the first one
is not optional (law 12a, the owner's ruling of 2026-09-19).

1. **The outsider read.** Read the issue once, start to finish, at
   reading speed, as a builder from another team who has read none
   of the papers. Grade nothing yet. Record three things: where a
   sentence had to be read twice, where following it needed
   knowledge nobody handed over, and whether a person would have
   finished it. This is a first-class axis and it can fail an issue
   on its own, because an issue that is right line by line and
   cannot be read through has failed at its only job.
2. **The taste gate.** docs/voice/taste.md, ruling by ruling,
   against the issue and against the generator (incident 20:
   recording a ruling is not enforcing it).
3. **The laws**, one verdict each, every verdict carrying a quoted
   line.
4. **The ban list**, including new tells to append.

## Maintenance

The writer seat proposes canon changes in the ledger. The laws
section changes only by the owner's ruling, recorded in
docs/voice/taste.md first.
