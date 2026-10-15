# The voice canon

**Enforced at:** prompts/writer-agent.md, the run's grading step, every run,
one verdict per law with a quoted line as evidence. The mechanical half of
several laws runs as `docs/voice/check_voice.py`, which nothing calls yet
(filed in docs/ideas.md, 2026-10-04). Added 2026-10-09 against the ExO's
filing of 2026-09-19, which asked for this line on three of this seat's files
and got two: taste.md is the owner's and this seat never edits it.

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
10. "Accelerate every builder and agent to frontier speed." The dual audience
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
    **The law binds the reader as well as the archive (owner's
    dispatch, 2026-09-25).** The first version of this law caught the
    sentence that points at a previous issue, and an opening can point
    at nothing and still charge the reader for something they did not
    do. The rehearsal print of 2026-09-26, written by the generator
    with every rule above already in it, opened "You have spent the
    week watching the field argue about whether agents need a heavy
    harness at deployment or whether the thing can be baked in." It
    names no issue. It says no "last week". It still tells a stranger
    what their week was, and only a returning reader could check it.
    That print passed the letter of this law and failed its spirit, and
    the owner's words on it are that law 13 and law 14 are "not yet
    strong enough".
    So the line moves from the reference to the grammar, where it can
    be checked in one pass. **The opening never says what the reader
    has done, read, watched, noticed or felt.** What the FIELD has been
    doing is the issue's whole job and stays, in the third person where
    it belongs. Second person belongs to the present and the future,
    because that is the part a reader can verify from their own chair:
    what they build, what this changes for them, what they should stop
    trusting from today. "You ship agents with a pile of code wrapped
    around the model to keep it honest" is right. "You have spent the
    week watching" is the violation, and so is every tense of it.
    The shape is a subject and a verb and nothing subtler: "you" with a
    past-tense verb, anywhere in the opening. There is no version of it
    this law allows and no material that earns an exception, because the
    sentence is unverifiable for most of the people reading it however
    true it happens to be for some.
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

    **Six rules were read as five, and the count is how (owner's
    dispatch, 2026-09-25, "ENJOYABILITY, again").** Five of the six
    above are measured inside a paragraph: its length, its results, its
    numbers, its plain-meaning line, and the number standing on a line.
    One is measured on the whole page, which is how many shapes are on
    it. A pass that splits long paragraphs satisfies all five and cannot
    reach the sixth, so the cheapest way to obey this law is also the
    way that leaves the reader's experience untouched.
    That is not a hypothetical. The reprint of 2026-W39, set on the site
    and sent to inboxes under this law, cut its longest paragraph from
    191 words to 98 and left nothing over 100. It is twenty-four
    paragraphs, no list, no subheading inside any section, one shape
    from the title to the close. Every count in this law passed and the
    owner read it and said enjoyability is still not fixed. A law whose
    measurable half can be satisfied while its point is missed is a law
    stated in the wrong order.
    **So the page count comes first.** Read the shape before the prose,
    every issue, and if the answer is one shape the issue is not
    finished, whatever the paragraph lengths say. Splitting paragraphs is
    the floor of this law and was never its content.
    **Three devices, now required rather than available.** They are the
    three that separate alexandria from the newsletters builders
    actually enjoy, named in the market seat's ranking of 2026-09-24
    (docs/market/briefs/2026-09-24-b.md), which put Latent Space,
    Interconnects and Ahead of AI at the top and alexandria last on
    enjoyability while first on rigor. Its finding, and it is the one to
    act on: "this is a formatting and craft gap, not a substance gap."
    - **A subheading inside a section that runs long.** Past about four
      paragraphs, a section carries a written turn, and that turn may be
      a third-level heading drawn from that section's own material. It
      is governed by law 12 exactly as a section heading is, so it says
      what this day's material shows and it would be false for
      yesterday's issue. "Why the stages fight each other" is a turn.
      "Analysis" is a label and canon law 12 already bans it.
    - **Shorter units, which is not the same as shorter paragraphs.** A
      unit is what the eye takes in before it rests: a paragraph, a
      bullet, a line standing alone, a subheading. An issue of
      twenty-four units all of one kind reads as long whatever each one
      weighs. Vary the kind, not only the size.
    - **A person on the page.** The top three all read as written by
      somebody, and the ranking names it: Interconnects "signals a
      person on the page, not a report." In this issue that person
      appears in one place and it is enough, which is the opening's
      first line. It greets the reader in the present tense under law
      13, in a voice, and it is one clear sentence a stranger enjoys
      before they know anything about the field. An issue with no such
      line is a report, and a report is what the field already has for
      free.

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

    **The second positive example, and it is about the page rather than
    the paragraph (owner's dispatch, 2026-09-25).** The one above shows
    a block being broken up, which is the five rules this law's own
    reprint satisfied while missing the point. This one shows the three
    devices, and it is the reprinted 2026-W39's opening and one of its
    sections, same facts, same numbers, nothing invented and nothing
    dropped.

    One warning rides with it and it is not optional. This example is
    written from the material the generator gets handed, which is
    exactly what ban list 53 bans, and the transmission path is on the
    record: the first positive example above carried the sentence
    "Teaching the structure in beat leaving it attached, which is the
    part nobody expected" and the reprint printed "Teaching the
    structure beats leaving it attached, which is the part nobody
    expected." This file is not sent to the model, so that sentence did
    not leak through the pipeline. It leaked through a person reading
    this file and setting a page. **So no sentence below is ever copied
    into prompts/digest.md, into an issue, or into a page.** It is held
    here because the owner asked for the comparison in the register the
    writer seat reads, and a worked example in the register the
    generator reads is the answer rather than an illustration of it.

    The opening as reprinted opens on the field in the third person,
    with no greeting at all, and glosses its key term behind a colon:
    "The agent-building world has spent the week arguing about
    scaffolding: the extra instructions and tooling that make frontier
    models reliable on real tasks." Then a second paragraph beginning
    "Today:" lists the same three findings the first one just named. No
    person, one shape, and the term the issue then uses thirty-eight
    times is not the term that got the gloss. Under law 13 as tightened
    above and the three devices:

    > If you ship agents, you also ship a pile of code wrapped around
    > the model to keep it honest. This week three labs tried to throw
    > that pile away.
    >
    > The pile is called scaffolding, and it is the checklists, the
    > retry rules and the step where something checks the answer before
    > it counts. It works. It also runs again on every single request,
    > which is most of what a reliable agent costs.
    >
    > A team from Peking University, Google and HKUST taught the
    > checklists to the model, deleted them, and scored higher with them
    > gone than with them attached. A group at Google Cloud, Stanford
    > and Washington University in St. Louis stopped the tuning of that
    > structure from behaving like a lottery. And a study that trained
    > one agent through four stages back to back found each stage
    > erasing the one before it.
    >
    > One belief also fell, and it was about how much retraining a small
    > model needs before it can drive a robot.

    The first line is one sentence, it is about what the reader builds
    rather than what they did, and a stranger who has never heard of any
    of this can enjoy it before the second sentence arrives. The
    greeting and the news share a paragraph, so nothing clears its
    throat. One name, scaffolding, carries the idea from here to the
    close.

    The section as reprinted is four paragraphs of even prose under the
    heading "What happens when you train agents in stages", which names
    a topic rather than a finding, and its second paragraph carries four
    results and six numbers with a stylistic em dash in it. The same
    material with a written heading, an inventory set as an inventory,
    the number on a line, a turn inside the section, and the evidence
    graded where the numbers are:

    > ## Training an agent one skill at a time undoes the skill before it
    >
    > Teams build a capable agent in stages. Teach it to search, then
    > teach it maths, then teach it to shop, then teach it to follow
    > instructions. Each stage is another round of training stacked on
    > the last one.
    >
    > A team led by Haixin Wang ran exactly that sequence and measured
    > the agent after every stage. The later stages did not add to the
    > earlier ones.
    >
    > Search scores fell from **45.2 to 14.6** once the shopping stage
    > was done.
    >
    > - **One-step search**, meaning a question answered from a single
    >   lookup, fell 45.2 to 14.6.
    > - **Multi-step search**, where the agent has to chain lookups to
    >   get there, fell 37.4 to 9.4.
    > - **The last stage healed some of it.** One-step search came back
    >   to 33.5 and multi-step to 25.0, both still far under where they
    >   started.
    >
    > ### Why the stages fight each other
    >
    > Nothing was forgotten in the ordinary sense. Each round of
    > training pulls the model's settings toward being good at one task,
    > the four tasks pull in directions that do not agree, and the last
    > one to pull wins.
    >
    > What this costs a builder is the plan rather than the result. An
    > agent that needs search and maths and tool use cannot be taught
    > them one after another and keep all three, so they are trained
    > together or measured after every stage. This is one team's own
    > experiment on one agent, nobody outside the group has run it
    > again, and it does not test whether a larger model holds up
    > better.
    >
    > *ACLArena: Agent Continue Learning in Multi-stage Post-training* -
    > [full text](https://arxiv.org/html/2609.23989)

    Four shapes where the reprint had one: paragraphs, a line standing
    alone, a list, and a subheading written from the section's own
    material. The heading states the finding and is false for any other
    day. "Post-training", "single-hop", "multi-hop", "oracle" and
    "parameter space" are gone rather than glossed, because the plain
    words were shorter than the definitions would have been. The
    evidence grade names what the work did not measure, which is the
    half that makes it a grade instead of a compliment. The em dash is
    gone. Nothing the reprint said is missing.
15. The library never claims to have read what it only ingested
    (owner's ruling, 2026-09-25). Every paper in the corpus arrives as a
    title and an abstract. A much smaller number have had their full text
    read. Those are two different acts, the counts are far apart, and the
    gap is permanent, so a sentence that gives the arriving count a verb
    of reading is false about the product.
    The evidence is the print of 2026-09-26 and the masthead that ran
    above it. The issue said "the library read 1,289 papers" on a day when
    1,289 papers had been ingested that week and 164 had ever been read in
    full. The masthead said "read in full and distilled weekly" on every
    issue ever sent, against 166 full reads out of 8,956 papers held.
    Neither line misread a paper or invented a number. Both took a count
    and attached the neighbouring count's verb.
    This law is worth its own number rather than a note under law 6
    because of who the claim is about. An overstated result belongs to a
    lab, is printed with a link, and a reader who cares can check it. A
    claim about alexandria's own work has no link and no way to be
    checked, so the reader either trusts it or stops trusting the issue.
    The words, fixed, so following this law is copying rather than
    composing. Papers **come in**, **arrive**, or **land**: that is
    ingestion, a title and an abstract. Papers are **sorted** or
    **ranked**: that is triage. Papers are **read in full** or **read
    closely**: that is the only act the word "read" may name, and it
    cites the full-read count and no other. Findings are **taken out of**
    the papers that were read. The scale sentence a close may carry is
    both numbers together, what arrived and what was read closely out of
    it, because the pair is true and either number alone invites the
    reader to assume the other.
    The repair is to drop the claim, never to soften it, which is the
    claims pass's standing rule applied to the one subject the pass had
    not been pointed at. "Read or reviewed", "read at some depth",
    "surveyed" and "processed" are hedges on a false sentence and each
    one is ban list 50 with a different coat on. An issue that says
    nothing about its own scale has lost nothing a reader came for.
    This binds every surface, not only the issue: the masthead, the
    email, the site, and any line of copy drafted under this canon.
    Standing copy fixed in code is where it hid for the whole life of the
    product, because a string that never changes is never graded (ban
    list 61), so a reader-facing sentence is graded wherever it lives.

## How an issue is graded

The daily review runs six passes, in this order, and the first one
is not optional (law 12a, the owner's ruling of 2026-09-19).

**Which artifact, by path, before pass 1 begins** (added 2026-09-30,
`INC-2026-09-30-standing-defect-unverified-for-three-grades`, corrected the
same day by the run that first executed it). The issue exists in several
places and they are not the same text. Grade the page under
`site/content/issues/`, because that is the one a stranger reads. Where the
database is reachable, grade the stored `digests` row as well and say where
the two differ, because a difference between them is a defect by itself.
Then read the reader-facing constants in `pipeline/` in this same pass and
grade each one as a sentence in the issue, which is the duty ban list 61
wrote down and handed to nobody.
**The correction, because the first version of this paragraph gave a wrong
reason and a later run would have relied on it.** It said the standing lines
are spliced into the page and the email but not into the stored row, so the
row is the one copy where a masthead defect is invisible. That is not how the
pipeline works. `add_masthead` runs before the `insert into digests`, so the
row carries the standing lines too, and the false masthead sits 84 characters
into the stored body of the newest issue. It was never hidden. Two grades read
a copy that contained it and missed it anyway, which is a plainer and worse
finding than the one first written down.
**So the check that belongs here is not about which copy. It is one integer
against one integer.** Every stored body carries the `prompt_sha` of the
prompt that wrote it. Compare it to the sha of `prompts/digest.md` as it
stands on the branch, and say in the grade whether they match. Where they do
not, the artifact was written by a generator that no longer exists, every
patch landed since is invisible in it, and the grade says so before it grades
a line. The newest print, wherever it lives, is the only artifact that carries
information about the generator this seat is about to patch, so a rehearsal in
`press_rehearsals` whose sha matches the branch is a better subject for passes
1 through 5 than a published issue whose sha does not. The published page is
still graded, because a reader is reading it.
The reason this is written as a path and not as a principle: "read the issue"
was the whole instruction for eleven days, a false masthead sat above the only
published issue through two grades, and the newest `digests` row on 2026-09-30
was written by a bundle from 2026-09-25, so three consecutive grades reported
on a generator five commits out of date without once noticing.

**Then the same question forwards, which is the one this check was missing
(added 2026-10-10).** Everything above compares the artifact to the branch, so
it says what WROTE the last issue. A grade's whole purpose is the next issue,
and nothing here asked what will write it. Four consecutive runs answered that
question with merge status, in those words, saying that unless the branch
merged before Monday the next issue would come from the same generator. The
branches merged. The generator that writes is still the one that wrote
2026-W40, because `prompts/digest.md` reaches the press through a deploy and a
merge is not a deploy.

So take the third integer, and it comes from the job rather than from git:

```
psql "$NEON_RO_URL" -c "select runtime_sha, recorded_at from deploy_runtime
    where app = 'weekly' order by recorded_at desc limit 1"
python3 tools/delivery_health.py --surface deploy --no-notify
```

The second command names the commit the press is running and the commits
landed since. Read `prompts/digest.md` at that commit, take its sha, and put
all three in the grade: what wrote the artifact, what is on the branch, and
what the press holds. Where the third does not match the second, every patch
this seat has merged is absent from the machine that writes on Monday, and the
grade says so at the top, because it changes what the run is for. On
2026-10-10 the press was running `prompts/digest.md` at sha `c48d09624161`,
which is the sha that wrote 2026-W40, with six merged revisions of this seat's
work absent from it, and 11 of the 21 enforcement anchors this register
verifies were not in the file the press reads. The cause is the engineer's and
it is filed. Asking the question is this seat's, and until 2026-10-10 no step
in this procedure did.
The company standard already said it, which makes this a correction rather
than a discovery. L-A16: configured is not in effect, and a capability counts
as live only when a run log, a listing or a response proves it served a real
turn. A merged prompt is configuration, and the press's own Monday row is the
run log. This procedure asked git a question only the job can answer.

**And one question before any of the three shas, because all three assume the
artifact is an edition (added 2026-10-12,
`INC-2026-10-12-the-grade-could-not-tell-an-edition-from-an-archive`).** Every
check above compares the newest artifact to a generator. None of them asks
whether the newest artifact is the current issue or merely the last one that
printed. Those are the same sentence on the morning after a send and different
sentences a week later, and nothing here can tell them apart, so the phrase
"the newest issue" has stood at the top of seven grades while what it named
changed underneath it.

```
python3 tools/delivery_health.py --surface press --no-notify
```

That command already exists and already answers it, in the press surface's own
words: on 2026-10-12 it read FAILING, "the newest issue is 2026-W40 and
2026-W41 has ended; 1 issue(s) missing", while `deploy_runtime` recorded the
weekly job running at 09:00:07 that same morning. The press ran and printed
nothing. So the grade says the artifact's date, the cadence it was published
on, and how many sends are missing between then and today, before it grades a
line. Where an issue is missing, that fact goes above the three shas, because a
seat whose next patch reaches a generator that printed nothing last week is
working on the second-order problem and should say so.

This is the third time this procedure has graded the wrong artifact in the same
shape. The first was which copy (`INC-2026-09-30-standing-defect-unverified-for-three-grades`),
the second was which generator, forwards (2026-10-10), and this is which
edition. Each one was a check that read the thing in front of it and never
asked whether that thing was the thing it was supposed to be reading.

**And one question after the three shas, because every check above reads one
print and a gate's compliance is not a property of one print (added
2026-10-15,
`INC-2026-10-15-the-generator-was-graded-on-one-sample-while-a-second-sat-in-the-database`).**
`rehearse()` writes a full body to `press_rehearsals` on the deploy ladder's
third gate, from the same prompt and the same model as the send. Where a row
there carries the graded week and the artifact's own `prompt_sha`, it is a
second sample of the identical generator and the grade measures both.

```
psql "$NEON_RO_URL" -c "select id, week, model, prompt_sha, created_at
    from press_rehearsals order by created_at desc limit 5"
python3 -I docs/voice/check_voice.py measure <each body>
awk '/^## /{sec=$0} /\[full text\]/{print sec}' <each body> | sort | uniq -c
```

This is not a second artifact to grade. A reader received one of them and the
verdicts belong to that one. It is the only evidence this seat can obtain about
whether a gate's WORDING is what is failing, and the answer on 2026-10-05 was
that it is not: the two bodies of 2026-W40 share a `prompt_sha` to the
character, were written five and a half hours apart, and carry 13 links against
3, with 10 in the three body sections against 0. Three merged patches to the
link-coverage rule had been aimed at a gap narrower than the spread between two
runs of one wording. So where the comparator exists, the grade prints both
measurements, and a verdict that recommends a fourth wording of a gate says
what the comparator showed first. Where no such row exists the grade says so in
one line, because an absent comparator is a fact about the deploy ladder rather
than a step skipped.

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
   **Every measurement names the artifact it came from and the command
   that took it, and is re-taken rather than carried** (added
   2026-10-04, `INC-2026-10-04-measurement-attributed-to-the-wrong-artifact`,
   ban list 91). Pass 3 already says "grade one artifact per verdict",
   because two artifacts sharing a verdict line is where an attribution
   error becomes invisible. That holds harder for a number than for a
   sentence, and a measurement table is the place the rule gets broken,
   because a table has one row per metric and a column per artifact, so
   every row is a verdict line shared by all of them. The grade of
   2026-10-03 reported 152 non-ASCII characters against a published page
   that `file` calls "ASCII text"; the figure is exact and it belongs to
   `2026-W37`, measured correctly on 2026-09-22 when W37 was what
   "published" pointed at. A number outlives its subject by default,
   because a column heading is a pointer and the figure under it is a
   value.
   So no figure enters a grade without the path it was measured on and
   the command, and a figure quoted from an earlier review carries that
   review's date and its subject, both. A FAIL recorded against a clean
   artifact is worse than no grade, because it hides the one thing the
   generator has solved and nobody can tell when to stop working on it.
2. **The taste gate.** docs/voice/taste.md, ruling by ruling,
   against the issue and against the generator (incident 20:
   recording a ruling is not enforcing it).
3. **The laws**, one verdict each, every verdict carrying a quoted
   line. A pass carries evidence too, wherever the law can produce it,
   because a wrong pass is indistinguishable from a right one and that
   is how a violation printed on three artifacts was graded clear
   (2026-09-26, `INC-2026-09-26-grade-cleared-a-printed-violation`).
   Law 12 was written here as the case where this costs nothing: the
   four framework names are a closed set of exact strings, so the
   verdict is a grep of the artifact for "Trailblazing", "Gaining
   traction", "Left behind" and "Read these yourself", and the grade
   records the command and its output rather than the word "pass".
   **That sentence was wrong and this procedure is where the error was**
   (corrected 2026-10-03, `INC-2026-10-03-law-12-graded-by-grep`, ban
   list 87). A closed set of strings makes the grep cheap. It does not
   make the grep the verdict. Five consecutive grades ran that command,
   recorded a clean exit code as instructed, and passed law 12 on an
   artifact whose second line recites three of the four slots in
   plain-English synonyms: `MASTHEAD` in `pipeline/weekly.py`, "what's
   new in AI research, what's gaining acceptance, and what newer
   evidence has overturned", 84 characters into the same body the grep
   was run over. The law forbids the framework from printing. The strings
   are how it printed once.
   So the verdict has three parts and the grep is the first of them.
   Record the command and its output. Then ask the law's IDEA of every
   heading and every label, which is where the grades of 2026-10-01 and
   2026-10-02 correctly found it. Then ask the idea of every STANDING
   line in the artifact, naming the file each line lives in, including
   files this seat cannot edit, because a standing line is the one place
   a violation prints on every issue and is written by nobody who is
   grading. A verdict that stops at the grep is a verdict about four
   strings. Grade one artifact per verdict.
   Two artifacts sharing a verdict line is where an attribution error
   becomes invisible.
   **A law that asserts coverage is graded by a count, never by a
   reading, and the count goes in the grade** (added 2026-09-29,
   `INC-2026-09-29-grade-cleared-link-coverage`). The rule above is
   right and it has one blind spot, which is that it steers a grade
   toward the laws able to produce a quotation. Law 8 and law 6 forbid
   an absence. An absence cannot be quoted, so a grade obeying the
   quotation rule inspects the links and grades that exist, and
   inspecting what exists is the one check that cannot find what is
   missing. On 2026-09-28 that produced "Law 8 [...] PASS. Four distinct
   URLs" on an issue with five items, three named works carrying no link
   between them, and two of three benchmark numbers ungraded.
   So wherever a law's subject is "every item" or "every issue", the
   verdict carries two integers and how they were obtained: the number
   of things the law says must be covered, and the number actually
   covered. The unit is the named piece of work rather than the item,
   because an item can name three. A pass on a coverage law with no
   number beside it has not been graded.
   **A law that relates two quantities carries a number for both** (added
   2026-10-12). The rule above covers a law whose subject is "every item", and
   it leaves the laws whose subject is a RATIO. Law 11 is the case: length
   follows the news, so the verdict is about a relation between how much the
   issue printed and how much real material the week held. Seven grades gave it
   a word count and the phrase "a week with real material", which is a
   measurement on one side and an impression on the other, and padding is
   exactly the defect that looks fine from the length alone.
   The news side has a number and it is in the payload. `press_rehearsals`
   carries a `payload_stats` column, and the rehearsal of 2026-10-05, id 4, on
   the same `prompt_sha` as the published issue, read 22 new claims, 12
   supported, 12 citation movers, 5 superseded, 8 deprecated and 10 deep reads.
   The issue printed 13 named works and 3 of the 10 reading-list candidates.
   That is the verdict law 11 was always asking for and no grade has ever had.
   Two things follow and the second is the finding. The rehearsal row carries
   the payload and the published `digests` row does not, so on the artifact a
   reader actually received this law cannot be graded at all. It is graded on a
   neighbouring row and the grade says which row it came from, per the
   measurement-attribution rule in pass 1. And the fix for that is filed rather
   than written here, because a column on the `digests` table is the engineer's.
4. **The ban list**, including new tells to append.
   **An entry that names a class is swept, not just fixed** (added
   2026-10-04, ban list 90). A tell is found in the one specimen the
   artifact showed and fixed in that specimen, because that is what a
   diff is for, and nothing in between asks the question the entry was
   just written to ask. Entry 89 was added on 2026-10-03 with its own
   giveaway stated in its own text, its two specimens were struck, and
   one grep the next morning found three more live in the generator
   plus a fourth inside the repair itself. So where a new or existing
   entry generalises, run its tell over `prompts/digest.md`, print the
   count in the review, and fix every hit in this pull request or say
   why one stays. A count of one is a result too: it closes the entry.
   **The sweep is per entry the run adds, and the count is printed per
   entry** (added 2026-10-13,
   `INC-2026-10-13-a-ban-list-entry-shipped-without-the-sweep-entry-90-requires`).
   The run of 2026-10-12 added two entries, swept one of them, and reported
   the sweep it ran rather than the sweep it owed. The unswept entry had three
   supplies, one of them in the opening slot, which is the slot its defect
   printed from. Whether an entry generalises is a judgment a tired run makes
   about its own prose, and the entry whose tell a grep can hold is the entry
   that gets swept, so the rule holds for the convenient half. Every entry the
   run adds gets a sweep line in the review, and an entry whose tell is a word
   class rather than a phrase gets one too, by hand if no command can hold it.
   **Then ask the generalisation question, which a sweep cannot** (added
   2026-10-13,
   `INC-2026-10-13-a-generator-gate-read-the-main-clause-and-the-defect-moved-right`).
   A sweep searches the generator for the same words. It cannot find the same
   defect wearing a different grammar, and four entries on this register are
   now that: the turn sentence that moved into the first sentence of a group,
   the grade whose words were fixed and whose position was not, the period word
   written hundreds of words after the rule, and the attributive subject that
   moved into a relative clause while the gate kept reading sentences. Each gate
   inherited the syntax of the one specimen it was written from.
   So before a gate is called finished, restate its defect in a subordinate
   clause, in a different position in the item, and in a different part of
   speech, and ask whether the gate as worded still catches it. Where it does
   not, the gate names the unit it reads, which is usually the clause rather
   than the sentence.
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
   The third question is about alexandria, added 2026-09-26 with law 15
   after a print claimed the library had read a count of papers it had
   only ingested. Take every sentence whose subject is the library, the
   issue or the newsletter, and ask which pipeline count it is about and
   whether its verb is the act that count records. There is usually one
   such sentence, in the close, and it is the only sentence in an issue
   the reader cannot check against a linked paper. Grade the standing
   lines too, meaning the masthead and anything else fixed in code or set
   on a page, because those never come up for review on their own.
   The fourth question is about the issue's own numbers and was added
   2026-09-26, after a print gave one method two scores on one measure. The
   first two questions compare a number in the issue against a number
   somewhere else. This one compares the issue against itself. Group every
   figure by the system it describes, and inside a group two numbers on the
   same named measure are either the same number or two setups the issue has
   told the reader apart where the second one appears. The specimen is the
   rehearsal print of 2026-09-26, which said a distilled model "hits 44.3%"
   on a macro-average and four sentences later said the supervision method
   that produced it "produces 30%" on the same macro-average, with nothing on
   the page to tell them apart. Neither figure was invented. The reader is
   the one who has to reconcile them, and a reader who cannot stops trusting
   both. The repair is to name the setup or to print one number, and the
   worked example under law 14 carries this defect too, in the pair 44.3 and
   30, which is reported to the owner rather than edited here.
   **A fifth question, and it is put to this pass and to every pass above it
   rather than to the issue** (added 2026-10-11,
   `INC-2026-10-11-two-more-gates-cleared-the-half-of-the-sentence-they-were-pointed-at`).
   Where a pass clears a sentence, name which part of that sentence the pass
   actually read, and put the remaining parts to the laws separately. A verdict
   that says PASS on a sentence carrying two claims has graded one claim.
   Two specimens from one artifact, both cleared five times. The close of
   2026-W40 was graded on its verbs, which were right, and never on the
   calendar span it put around them, which the generator forbids in its own
   words. Question four above was run on a latency reported once in
   microseconds and once in milliseconds, and cleared it, because the question
   compares numerals and a unit change makes one quantity into two numerals
   that look nothing like each other. Each gate was pointed at the property
   that failed on the day the gate was written, so the half of the sentence
   that has never failed is the half nothing reads, and it stays unread until
   it fails. Convert, normalise or count before comparing anything a reader
   will read as a quantity, and say in the verdict what was compared.
   The cheap version of this question, and it is the one to run: for every PASS
   in passes 2 through 5, write the half-sentence the verdict is actually
   about. Where that is shorter than the sentence, the rest is ungraded.
   **A sixth question, and it catches what the fifth cannot: the verdict that
   read both halves, wrote the failing one down, and passed anyway** (added
   2026-10-12,
   `INC-2026-10-12-a-pass-verdict-carried-the-evidence-of-its-own-failure`).
   The fifth question finds the half a verdict never reached. This one finds the
   half it reached and forgave, and it is not reachable by the fifth question
   because the verdict's own text already names the whole sentence. Two shapes,
   both from the grade of 2026-10-11, both in pass 3.
   The first is the exception. Law 9 was passed as "attribution is
   institution-first except where a lone researcher is counted among 'three
   labs'", and nothing in the org grades "three labs", so the clause after
   "except" was the defect's only appearance anywhere and it appeared inside a
   PASS. Four days earlier the grade of 2026-10-08 had found the same defect in
   pass 5, written it down, added no ban-list entry and patched nothing. It is
   live today.
   The second is the routing. Law 4 was passed on the title with the note that
   its two undefined nouns "are law 12a's verdict, not this one's". Law 4 has
   two clauses and the second is that a builder knows from one line whether to
   open the issue, which is precisely what an undefined noun defeats. One
   sentence was split across two laws and each passed the half it held.
   So the check is a grep over the finished review, and it runs before `gh pr
   ready`: `grep -nE '(PASS|pass)' docs/voice/reviews/<today>.md` and read every
   hit for a concession. Except, apart from, other than, aside from, though,
   while, only, but. A verdict carrying one of those about its own subject is a
   FAIL with its evidence already attached, and the honest form is a split
   verdict naming both parts, which pass 3 already allows. Routing a defect to
   another law is legitimate exactly once: when that law's verdict actually
   grades it. Say which verdict will, and check that it did.
   This pass is procedure and not a law. It enforces laws 6 and 7,
   which already require the evidence grade to be honest and to be
   about the thing that is actually uncertain, and a grade aimed at
   the wrong risk satisfies neither. With the third question it also
   enforces law 15.
6. **The standing defects.** Added 2026-09-30, from the fourth day of a
   defect that had a law, two ban-list entries, an incident id and a
   ledger entry with a recommendation, and was still printed.
   Every entry in docs/voice/ban-list.md whose ending is a ledger filing
   rather than a prompt change names a defect no prompt can reach, so
   nothing in the generator will ever close it and nothing in the ledger
   will ever fail. Take each of those entries and re-check it against the
   live artifact. Print the check and its output in the grade, the way
   law 12 is graded, and say how many days the entry has been open.
   An entry that is still true is a FAIL line in the review with the same
   weight as a law, and it stays one every run until the artifact is
   clean. A filing has no failing state of its own, and this pass is the
   failing state.
   Do not restate the filed problem. The original ledger entry says it
   better than a rewrite will, so confirm it in place with the day's
   evidence, and where the entry has no check beside it, file the check
   rather than the problem a second time.
   The specimen is the masthead. `MASTHEAD` in `pipeline/weekly.py` was
   corrected on 2026-09-26 and `site/content/issues/2026-W39.md` still
   opened on "read in full and distilled weekly" on 2026-09-30, on a page
   that had been edited that same day to apply a taste ruling four lines
   from the bottom of the file.
   **Then grade the standing lines themselves, against the laws, with no
   filing required** (added 2026-10-03, `INC-2026-10-03-law-12-graded-by-grep`).
   Everything above this paragraph re-checks defects somebody already
   filed, and a pass built out of filings can only find what is already
   known. The grade of 2026-10-02 executed it correctly, opened
   `pipeline/weekly.py`, checked `MASTHEAD` against the law in the filing
   that named it, and wrote that the constant "has been correct since
   2026-09-26". It was correct about law 15 and it was reciting three of
   the four framework slots at the time, which is law 12, which nothing
   had filed.
   So list every reader-facing constant the pipeline splices into an
   issue, name its file and line, and put the ten laws to each one as
   though it were a sentence somebody wrote this morning. These lines
   print on every issue, they are written by no run that is grading, and
   they are the only prose in the product that no prompt gate can reach.
   A standing line is the cheapest place in the product to be wrong for a
   fortnight.
   **The inventory is the delivery path, not the module constants** (added
   2026-10-04). The step above was executed for the first time on
   2026-10-03 and it listed seven names, all of them assignments in
   `pipeline/weekly.py` and `pipeline/email_render.py`, because that is
   what "constant the pipeline splices" reads as. A reader-facing string
   does not have to be a constant. Three were missed in one file. The
   email template `site/emails/digest.html` carries its own standing text
   and its own `{{masthead}}` region, so the masthead a grade reads once
   at the top of the page renders a second time in the footer of every
   email. `normalise()` at `email_render.py:70` substitutes one character
   for another on the way out, which is a reader-facing edit made after
   the last gate. And a glyph chosen in code is a standing line too: the
   bullet marker at `:115` is a middle dot, so the first issue that obeys
   law 14 and sets a list prints a character law 1 forbids on every
   bullet of it.
   So walk the path the words take, from the model's output to the
   reader's eye, and grade every string that joins or changes them on the
   way: the generator's splices, the template's own text and regions, any
   fill-time substitution, and every character the code picks rather than
   the writer. Where the file declares a boundary of its own, as this one
   does with "fill-time typography, not editing", say which side each
   finding falls on and let the owner rule rather than deciding it here.

## What the six passes owe, which is not a review (added 2026-10-12)

A review is prose. The ban list is a register with a gate: its own header says
an entry is not finished when it is written, and every entry carries either the
sentence that now enforces it or the ledger filing saying why no sentence can,
with `docs/voice/check_voice.py enforcements` checking the quoted ones. That
gate exists because two entries were once appended and never reached the
generator.

Only pass 4's output is bound by it. Passes 1, 2, 3, 5 and 6 produce defects
too, and a defect that lives in a review has no failing state at all: pass 4
re-reads the ban list, pass 6 re-checks the entries whose ending is a filing,
and nothing in this procedure ever re-reads a previous review's prose. So a
finding written only into a review is a finding the next issue is free to
commit, which is exactly what the ban list's own header says about a tell that
only gets written down.

The evidence is one defect across three grades. On 2026-10-08 pass 5 found that
the opening's "Three labs showed" covered a lone named researcher with no
institution, wrote it down in the review, and the same review's count paragraph
says "Nothing else was patched". No ban-list entry was added. On 2026-10-11 the
same defect appeared inside a PASS verdict as the clause after "except". On
2026-10-12, four days and two grades after it was first found, it was still live
in the generator and in the artifact.

So: **every new defect a grade finds, in any pass, becomes a ban-list entry in
the same pull request, or the review says in one line why no entry can hold
it.** The entry then inherits the ending rule it was always subject to, which is
the only rule in this seat's registers that a command can check. A grade is
allowed to decide not to patch, and the grade of 2026-10-08 decided that for a
stated reason that was sound. What it is not allowed to do is leave the finding
somewhere nothing will read again.

## The blocks a review quotes are graded, not just cited (added 2026-10-14)

Pass 3 requires every verdict to carry a quoted line, so a review accumulates
extracted artifact text. Pass 5's fifth question covers the half of a SENTENCE
a verdict never reached and its sixth covers the half a verdict reached and
forgave. Neither covers the third place, which is a block of the artifact
pasted into a review as evidence for one law and never put to the others. That
block is the cheapest text in the org to check, because somebody has already
done the extracting.

The evidence is both findings of 2026-10-14, nine and eight grades late, and
both were sitting in this seat's own files the whole time.
`docs/voice/reviews/2026-10-06.md` quotes "Three papers this week test what
happens when you push [...]" in a list of standalone lines, while counting
shapes under law 14. Four items follow that sentence in the artifact and the
counting gate is arithmetic, so law 2 and the claims pass both had a verdict
waiting in the quotation. `docs/voice/reviews/2026-10-05.md` prints all four of
the issue's "The authors' own" grades in one numbered block, while finding that
the grades sat in the position law 14's meaning line needed. Law 6's own gate
forbids two grades beginning alike, and the proof was the block.

So: **after the six passes, re-read every block this review quotes and every
block the two previous reviews of the same artifact quote, and put the laws the
quoting verdict was not about to each one.** It is a short list by construction.
A quotation that survives this says so in one line, because the point of the
step is that a clean result closes it rather than that it always finds
something.

This is pointed at a grade re-reading one artifact, which is the case the seat
has been in since 2026-10-05. Where an issue is new the two previous reviews
are about a different artifact and only this review's own blocks are in scope.

## The run's own prose is measured, not read (added 2026-10-13)

Five times this seat's own review has broken canon law 1 while enforcing it, and
the fifth time the review asserted a check it had run by eye
(`INC-2026-10-12-the-editors-own-prose-broke-canon-law-one-a-fifth-time`). The
four earlier diagnoses are all about where the mark hides. A count does not care
where it hides, so the count is the gate:

```
python3 -I docs/voice/check_voice.py selfcheck origin/main
```

It reads every line the run adds, against the working tree rather than the
commits, because the draft that broke the law five times was uncommitted when it
was measured. A semicolon inside a quotation of the artifact or of a surface's
output is excused in code, because striking it falsifies the quote, and so is
one inside a shell line, where it is the literal character. An em dash is
excused on a heading line, which is the date separator every entry in
docs/agents/incidents.md and docs/ideas.md carries. Everything else is a finding,
and it exits non-zero, so the run either strikes the mark or the review says in
one line why it stands. Run it before `gh pr ready`, in the same step as the
sixth question's grep.

## Maintenance

The writer seat proposes canon changes in the ledger. The laws
section changes only by the owner's ruling, recorded in
docs/voice/taste.md first.
