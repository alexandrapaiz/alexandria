# Six live sentences the product cannot back, and the words that replace them

Writer run 40, 2026-10-18. One candidate per surface, drafted here for the
owner to rule on and the frontend seat to set. No line of `site/` is touched
in this pull request.

## Why this is a repair and not a copy round

The quality register in `docs/agents/quality-claims.md` lists eleven sentences
the site says about what we ship, and names the code that would have to run for
each one to be true. Three of the eleven hold. Four have no machine at all. The
register has been accurate since 30 September and the site has not changed, so
the sentences below have been live, in the flat present tense, for eighteen
days.

This run built a command that reads that register against the pages, which is
how the list below was produced rather than remembered. Every line here is a
sentence a reader could answer with "how do you know that" and get no answer.

The repair follows one rule, which is the owner's ruling of 25 September
applied to our own promises. A claim with no machine under it is dropped rather
than softened. Where the machine is genuinely being built, the page says so in
the present tense of a thing that does not exist yet, which is the form
`site/app/routines/page.jsx` already uses in public and the form the pricing
page already uses for routines in its own tier list.

Nothing below reconceives a page. Each candidate changes the sentence that is
wrong and leaves the paragraph around it alone, because the approved pages of
29 September are the positive examples and they are approved.

---

## 1. The mission page, third paragraph

Live now:

> Your agents get the same frontier as working files, and the loop closes
> without you. Each skill is a way of doing one job that the research has shown
> to work, proven against the same tasks with and without it, revised when the
> research sharpens it, and retired with the reason when the research overturns
> it. An agent that improves at the pace of the research improves at the pace
> of the field, which is the only pace that keeps up with an exponential.

Three promises in one sentence, and this is the worst line on the site. Proven
with and without it was measured once, on 30 September, on one skill of six,
and it came back slightly worse with the skill than without it. Revised when the research
sharpens is the claim whose machine was written and has never been merged, so
no skill has ever been revised by anything but a person. Retired with the
reason has no machine at all, no field to hold the reason, and nothing that
sets the status.

The candidate:

> Your agents get the same frontier as working files, and the loop closes
> without you. Each skill is a way of doing one job that the research has shown
> to work, and each one names the papers it came from and the date of the last
> trigger test that judged it, so what a skill rests on is visible before your
> agents load it. Keeping every skill current as the research moves is what the
> routines are being built to do, and we will say so on the day they run. You
> read the issue once a week to decide what matters. Your agents load the
> skills and work from what the library holds rather than from what they were
> trained on.

What changed and why. The three promises come out. In their place is the one
thing about a skill that holds today and is measured, which is its provenance
and the trigger test behind it, at twenty-seven of twenty-seven cases on the
bundle measured on 30 September. The compounding stays where it already is, in the paragraph above
this one, where the record getting more valuable with each paper is a claim
about the corpus and the corpus is the half of the product whose promises hold.

## 2. The mission page, second paragraph, one word

Live now:

> Because every finding is linked to the findings that support, refine, or
> contradict it, the record gets more valuable with each paper it adds rather
> than merely longer.

The word is "every". Of the eight hundred and forty-six claims in the record
when this was last measured on 29 September, five hundred and forty-five were
still waiting to be linked at all. The machine is real, it runs, and it covers
a minority. Every number in this file is the register's own measurement with
the register's own date, because a figure carried from one artifact into
another under a fresh date is how a clean page gets graded on a stale fact.

The candidate:

> Because the record keeps the links between findings that support, refine or
> contradict each other, it gets more valuable with each paper it adds rather
> than merely longer.

One word out, and the sentence stops promising coverage it does not have while
keeping the compounding she asked for. The real repair is the backlog rather
than the wording, and that belongs to the seat that owns the interpret queue.

## 3. The skills page, the intro

Live now:

> Your agents stay at the frontier without you carrying them there. Each skill
> in this library gives an agent a way of doing one job that the research has
> shown to work, and the library keeps every skill current at the pace of the
> research that is gaining the most traction, so as the field confirms a
> technique, sharpens it, or overturns it, your agents change with it. You do
> not schedule the update or read the paper, because the library follows the
> field and your agents direct themselves from what it holds. What you get is
> agents that work from the current state of the evidence today and still will
> next month.

Two sentences here promise currency that nothing produces, and the last one
promises it for next month. Five of six skills are at version one and none has
ever been revised by a machine. This is the hardest candidate in the file,
because the first and last sentences are hers from 29 September and they are
the ones the page sells with.

The candidate:

> Your agents work from the frontier without you carrying it to them. Each
> skill in this library gives an agent a way of doing one job that the research
> has shown to work, and each one names the papers it came from and the date of
> the last trigger test that judged it. The library grows every day as new work
> lands, so what the next skill is built from is the state of the evidence
> rather than the state of a training run. Keeping every skill current as the
> research moves is what the routines are being built to do, and we will tell
> you the day they run.

What changed and why. "Stay at the frontier" became "work from the frontier",
because staying is a promise about every month after this one and working is
true the moment an agent loads the file. The currency promise moves into the
tense of a thing being built. What replaces it is the growth of the library,
which is the claim on this product that holds and is measured daily, and the
comparison a builder actually feels, which is a file against a training cutoff.

**One candidate below is the alternative, and it exists because this is her
line.** If she would rather keep "stay at the frontier" as written, the honest
version of the page keeps it and hedges the mechanism in the same breath.

> Your agents stay at the frontier without you carrying them there, which is
> what the routines are being built to do, and we will tell you the day they
> run.

I prefer the first. A promise with its own disclaimer attached reads as a
promise, and a reader remembers the first half.

## 4. The home page, the paragraph under the hero

Live now:

> The library grows every day and corrects itself as the research moves, so
> every finding in it carries its evidence and is replaced when newer work
> overturns it.

Two of these three claims hold. Every finding carries its evidence is true of
every row in the record, and the library growing every day is true and
measured. Replaced when newer work overturns it is not what happens. The issue
reports the contradiction and the finding stays as it was, which is reporting
rather than replacing.

The candidate:

> The library grows every day and corrects itself as the research moves, so
> every finding in it carries its evidence, and when newer work overturns a
> finding the record says so.

Seven words changed. What the machine actually does turns out to be the more
interesting promise anyway, because a reader who builds on a finding wants to
be told it fell rather than to find it quietly gone.

## 5. The home page, the number under it

Live now, and this one is twenty-two days old:

> **4,243** papers read this week

The count comes from the pipeline's ingest field, which counts what arrived. A
row in that table is a title and an abstract. The word above it names the act
performed on a far smaller set, which is the owner's ruling of 25 September and
the exact sentence the masthead was repaired for on 26 September.

Writer run 15 drafted the repair the same day, in
`docs/voice/home-metric-line-2026-09-26.md`. It was checked against the
registers and never set, and the false line has been on the first screen of the
site ever since. That candidate stands unchanged and nothing here replaces it.

> **4,243** papers came in this week. **55** were read in full.

The second count is still not exposed to the site, so the fallback in that
file is the line to set today, and it is true with one number.

> **4,243** papers came in this week.

## 6. The graph page, the intro

Live now:

> The graph shows you how solid a finding is before you commit to it: what
> confirmed it, what narrowed it, and what has contradicted it.

Two faults. The colon-led construction is the device she rejected on 20
September as unserious, and the list after it promises an edged finding for
every finding when most of the record is unedged.

The candidate:

> The graph shows how solid a finding is before you commit to it. Where the
> library has linked a finding, you can see what confirmed it, what narrowed it
> and what has contradicted it.

## 7. The terms page, what the service is

Live now:

> The library reads AI research and keeps a record of what it claims, then
> writes a digest from that record and turns durable procedures into agent
> skills.

The reading verb again, on the one page where a reader goes to find out what
they are buying. Terms copy is still reader-facing copy, and a page nobody
drafts is a page nobody grades.

The candidate:

> Papers come into the library every day, the ones that earn it are read in
> full, and the library keeps a record of what they claim. It writes a digest
> from that record and turns durable procedures into agent skills.

## 8. The pricing page, the intro and one bullet

Live now, in the intro:

> The paid plan opens the skill library, in the same files you read and your
> agents load, and the routines that keep it current as the research moves.

And in the paid tier's list:

> Skill updates as the research moves

The page already does this right once. Its last bullet reads "Routines, once
they ship", which is the honest form, and then the intro sells the same
routines in the present tense and the bullet above sells the updates they would
produce. A reader who reads the list carefully finds the page disagreeing with
itself about whether a machine exists.

The candidate, for the intro:

> The paid plan opens the skill library, in the same files you read and your
> agents load, and the routines that will keep it current as the research
> moves, once they ship.

And for the bullet, which becomes one line instead of two:

> Skill updates as the research moves, once the routines ship

Both are the tense the page already uses in its own last bullet. The pricing
page is being reframed by another seat this sprint, so these two lines are
written to survive that reframe rather than to depend on today's layout.

---

## What this file does not resolve

Four of the eleven rows in the quality register have no machine anywhere, and
hedged words are not a fix for that. The sentences above become true when the
revision routine merges and runs, when a retired skill has a field to hold its
reason, and when the skill measurement covers more than one skill of six. The
copy's job between now and then is to not say the machine already runs. That is
the whole of what this file claims to do.

One thing in it is not a copy question at all. A paid tier that lists a feature
no machine produces is a sales question, and the honest hedge makes it visible
rather than answering it. Whether "Skill updates as the research moves, once
the routines ship" belongs in a twenty dollar tier at all is the owner's call
and the product seat's, not this seat's.

## Checked before this left the run

- `docs/voice/taste.md`, line by line, first. The 29 September rulings bear on
  every candidate here: longer undecorated sentences, value before mechanism,
  the builder's situation first, the frontier as the builder's position,
  compounding stated without naming Moore or S-curves, bare-noun headings, and
  never the reading verb for what only arrived. The colon-led construction she
  rejected on 20 September is removed from the graph page rather than preserved.
  Two hedge sentences name a machine being built, which is mechanism talk in a
  place the rulings push away from mechanism, and the judgment is named here
  rather than assumed: a page that must not claim a machine runs cannot avoid
  referring to it, and the routines page is the precedent she has already seen
  in public.
- `docs/voice/canon.md` and `docs/voice/ban-list.md`: law 15 is findings 5 and
  7, and the appended ban-list entry is the register's gate rather than a new
  tell of prose.
- `docs/voice/value.md` and `docs/voice/preferences/site-copy-2026-09-20.md`:
  read before drafting. The growing, self-maintaining library is present in
  every candidate that replaces a promise, which is the shape she said eight
  rounds had missed. No candidate's subject is "it" as a stand-in for the
  machine. None repeats a rejected shape, and the one place a rejection came
  close is the skills page's "stay at the frontier", which is hers rather than
  a seat's invention and is therefore offered back to her as a choice.
- `docs/agents/copy-pipeline.md`: read. The writer drafts, she rules, the
  frontend seat sets.
- `docs/agents/quality-claims.md`: read, and this file is its artifact-side
  gate firing for the first time as a command rather than as a reading. No
  candidate here makes a new claim about what we ship. The two it adds are the
  skill's provenance and the trigger test date, and both are rows the register
  already marks as holding.
