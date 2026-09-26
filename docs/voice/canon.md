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
on a page. Law 3, sell the product and never the recipe, because a
visitor who meets a description of the machinery has been handed the
blueprint instead of the building. Law 12a, the outsider test, because
a page has one screen to make sense to a stranger. And the design
register's own rule that a heading never carries an explanatory
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
13. Every issue stands alone (owner's ruling, 2026-09-24). No
    issue leans on a previous one. Not on "last week", not on "as we
    covered", not on anything the reader is presumed to have already
    seen. A first-time reader loses nothing, because most readers of
    any issue have not read the one before it and the archive is read
    out of order. Where a thread genuinely continues, the sentence
    restates the thread in full instead of pointing back at it, in
    plain words that cost a line and buy the whole audience.
    Her rejected specimen, the opening of 2026-W39, verbatim: "You
    spent last week watching agents get faster by doing less at test
    time." Her words on it: "dont assume readers read each issue."
    The repair, and what the opening should have been: "Agents have
    been getting cheaper by thinking less at the moment they answer.
    That trick has a ceiling. This week the field went after
    something harder. Every reliable agent is wrapped in scaffolding,
    meaning the checklists and retry rules and approval steps a team
    builds around a model to keep it on track. Three labs asked
    whether that structure could be taught to the model itself and
    then thrown away." The thread survives, stated rather than
    referenced, and nobody had to have been there.
    This binds the daily and the weekly alike, and it binds the
    generator as a rule rather than a preference. It does not touch
    the corpus thread of law 5. Saying what the field used to believe
    is the product. Saying what alexandria printed about it is the
    violation.
14. The issue is enjoyable to read, and formatting is how it gets
    there (owner's rulings, 2026-09-24). Her verdict on 2026-W39,
    after the stands-alone repair landed and the prose was right:
    "so much better, but feels dense and like a hassle to read. not
    really enjoyable." Correct is the floor, not the grade. An issue
    a person has to work through has failed even when every sentence
    in it is true, and **density is a failing grade on its own**,
    scored as its own axis and not as a note under the outsider test.
    Law 12a says compression is fewer words per idea. This law says
    what the reader feels when that rule is broken, and it carries the
    penalty.
    Her proposal, the same night, is the other half and it is now
    law: "some sections with bullets and playing with formatting
    beyond dense paragraphs." Formatting is a TOOL of the issue. An
    issue set as one column of grey paragraphs is a design failure
    the writer owns, not a neutral default. Six rules fall out, and
    they bind the generator in prompts/digest.md:
    - Paragraphs run short. One result per paragraph, and the
      paragraph ends when the result does.
    - Parallel results go in a bulleted list, each bullet opening
      with a short bold lead. Prose carries the argument. Lists carry
      the inventory.
    - The number that matters gets a line to itself, inside a
      sentence, so the eye lands on it before the paragraph explains
      it.
    - White space between sections, and never two walls in a row.
    - Numbers appear where they change the reader's decision, and
      nowhere else. A second number in a sentence has to be the
      comparison the first one needs.
    - Every result is followed by a line of plain meaning. What the
      number makes true for a builder, in words with no number in
      them.
    The negative example is the densest paragraph in 2026-W39, 191
    words, seven sentences, seven numbers, no break, quoted whole
    because the failure is the block and not any line in it:

    > A claim from Peking University, Google, and HKUST now has three
    > independent papers building on it: that you can teach a smaller
    > model to behave like a larger model supervised by an elaborate
    > harness, then run the smaller model with minimal scaffolding.
    > The original finding was that evolving a harness with a weaker
    > model substantially improves domain-specific enterprise
    > performance. This week the same group showed *how* to extract
    > that benefit permanently. Their Harness-Zero pipeline raises
    > base model success from 23.3% to 44.3% on a macro-average
    > across spreadsheet work, multi-app tool use, and scientific
    > reasoning, beating even the 41.7% achieved when the specialized
    > harness stays attached at runtime. The key was not imitation
    > learning from a stronger model's trajectories, but
    > harness-guided review: an agent-as-harness checks each proposed
    > action against a private reference, passes or replaces it, and
    > the corrected trajectory becomes training data. Ablations were
    > brutal: harness-guided review hit 30% macro-average success,
    > while alternatives, raw stronger-model trajectories,
    > trajectories without review, review without the private
    > reference, review using only the final answer, managed 3% to
    > 15%. That is a 10x gap in supervision quality, measured on the
    > authors' own experiments across three domains, not yet
    > replicated.

    Everything in it is true and most of it is well written, which is
    why this is the example. The positive is the same material under
    this law, same facts, same numbers, nothing dropped:

    > Every reliable agent is wrapped in scaffolding, meaning the
    > checklists and retry rules and approval steps a team builds
    > around a model to keep it on track. It works. It also runs
    > again on every single request, and it is the reason a good
    > agent costs what it costs.
    >
    > A team from Peking University, Google and HKUST asked whether
    > that structure could be taught to the model itself and then
    > removed. Their pipeline is called Harness-Zero.
    >
    > **It finishes 44.3% of tasks with the scaffolding gone, up from
    > 23.3%.**
    >
    > The same work scored 41.7% with the scaffolding still bolted
    > on. Teaching the structure in beat leaving it attached, which
    > is the part nobody expected.
    >
    > What did the teaching is the interesting half. Not copying a
    > bigger model's transcripts. A second agent watched each move
    > the learner proposed, checked it against a reference answer the
    > learner never saw, and swapped in the right move when the
    > learner was wrong. The corrected run became the lesson.
    >
    > That choice carries the whole result. Learning from corrected
    > runs scored 30%. Every alternative the team tried scored
    > between 3% and 15%.
    >
    > This is the authors' own work across three kinds of task,
    > spreadsheets, multi-app tool use and scientific reasoning, and
    > nobody outside the group has reproduced it yet. If it holds,
    > the heavy scaffolding moves into training and your runtime gets
    > cheaper.

    Seven paragraphs instead of one, one result each, the number on
    its own line, a plain-meaning sentence under every result, and
    the reader is carried rather than made to unpack. The word count
    went up. The work the reader does went down. That trade is the
    law.

## How an issue is graded

The daily review runs four passes, in this order, and the first one
is not optional (law 12a, the owner's ruling of 2026-09-19).

1. **The outsider read.** Read the issue once, start to finish, at
   reading speed, as a builder from another team who has read none
   of the papers. Grade nothing yet. Record four things: where a
   sentence had to be read twice, where following it needed
   knowledge nobody handed over, whether a person would have
   finished it, and whether reading it was a pleasure or was work
   (law 14). This is a first-class axis and it can fail an issue
   on its own, because an issue that is right line by line and
   cannot be read through has failed at its only job.
   The fourth question carries a measurement beside the impression,
   because "dense" is arguable and a word count is not. Count the
   words in the longest paragraph, the paragraphs over 100 words,
   the numbers in the heaviest one, and how many shapes the issue
   puts on the page: paragraphs, bullets, a line standing alone, a
   bold lead. One shape for a whole issue is itself the finding.
   2026-W39 scored 191, five, ten, and one.
2. **The taste gate.** docs/voice/taste.md, ruling by ruling,
   against the issue and against the generator (incident 20:
   recording a ruling is not enforcing it).
3. **The laws**, one verdict each, every verdict carrying a quoted
   line.
4. **The ban list**, including new tells to append.
5. **The claims pass**, added 2026-09-24 after the fourth grade of
   2026-W39 found a false comparison that the four passes above had
   no way to see. Those four all ask how the issue is written. This
   one asks whether what it says is so, and it runs last because it
   needs the whole issue in view.
   Take every comparison the issue makes and every belief it says
   fell, and put one question to each: do the two things being
   compared measure the same quantity, of the same kind of system, on
   a task a reader would accept as the same task? A shared percent
   sign is not a shared measure. 2026-W39 set a benchmark success
   rate of 82.2% for building agents against a win rate of 87% for
   simulated fighter aircraft and declared a ceiling broken, and the
   issue said "the contexts differ" in the same sentence.
   That is the second question, and it catches what the first one
   misses. Did the issue write a concession and then proceed past it?
   A qualifier that the claim has to survive before it can land is
   the writer noticing the comparison fails and continuing, which is
   ban list 50. The fix is to drop the claim, never to soften it.
   This pass is procedure and not a law. It enforces laws 6 and 7,
   which already require the evidence grade to be honest and to be
   about the thing that is actually uncertain, and a grade aimed at
   the wrong risk satisfies neither.

## Maintenance

The writer seat proposes canon changes in the ledger. The laws
section changes only by the owner's ruling, recorded in
docs/voice/taste.md first.
