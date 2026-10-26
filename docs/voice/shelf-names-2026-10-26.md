# Site copy: two new shelves for the skill library, and the seven captions already on it

Writer run 53, 2026-10-26. One copy round, for the surface
`site/lib/skill-shelves.js`, which is where the skill library's shelf names
and shelf captions live. Drafted here for the owner to rule on and the
frontend seat to set. Nothing in `site/` is touched by this run.

The round was handed over rather than chosen. The frontend seat's shelf
audit of 2026-10-24 fixed the code half of a shelving defect, found that the
words half was not its to write, and left a proposal in `docs/ideas.md`
asking for two shelf names with captions, plus one line in the catch-all
shelf's caption that had gone stale. The PM relayed it to this seat on the
board. The proposal's reasoning is sound and it is not restated here.

## What is still true today, checked rather than assumed

The proposal is two days old and the library has had a skill added since it
was written, so the shelving was re-run against the working tree before any
word of this was drafted.

| shelf | what stands on it today |
| --- | --- |
| Agent harnesses | `harness-engineering`, `recursive-harness-self-improvement` |
| Context engineering | `agent-memory-selection`, `context-window-engineering` |
| Multi-agent systems | none yet |
| Training loops | `self-improving-post-training-loops` |
| Serving and inference | none yet |
| Multi-modal systems | none yet |
| More from the library | `agent-containment`, `agent-security-measurement`, `evaluation-integrity`, `skill-library-engineering` |

Four skills on the catch-all and three named shelves empty, exactly as the
proposal reports. The round proceeds.

## The arithmetic the proposal did not have, and it changes one of the two asks

The proposal asks for the catch-all's caption to be repaired because it was
written when at most one skill could land there and it now sits above four.
That is true today. It stops being true on the day the two new shelves are
set.

`agent-containment` and `agent-security-measurement` go to the first new
shelf. `evaluation-integrity` goes to the second. `skill-library-engineering`
is about the skill file itself and neither new shelf names that, so it stays
where it is, alone.

So a caption written to sit above four skills would be wrong the moment it
shipped, because the same pull request that sets it takes the shelf back down
to one. The repair is not to change the number. It is to write a caption that
makes no claim about the count at all, which is the defect the current line
has had since the day it was written and the reason it went stale once
already.

## Part 1, which is the ask: the two new shelves

Both names are bare noun phrases, which is her ruling of 2026-09-29, and both
sit in the register of the six already on the page.

### Security and containment

> An agent that can act needs a boundary somewhere, and where you put it
> decides whether the defence does anything.

The shelf holds `agent-containment` and `agent-security-measurement`.

The name drops the word "agent" that the subject invites, because
`Serving and inference` is the precedent on this page and it does not say
"model serving". "Containment" carries the agent on its own, and no reader
of a page about building agents will take this shelf for a statement about
our own infrastructure.

The caption is one sentence rather than the two-part shape four of the six
existing captions use, and that is deliberate rather than careless. The
reason is in part 3. It names the shelf's territory without delivering a
result, because the rows underneath deliver results and a caption that
competes with them is a caption read twice. What it does carry is the
question the territory actually turns on, which is the enforcement point, and
that is the subject sentence of `agent-containment` restated for someone who
has not met the skill.

### Evaluation and measurement

> You cannot tell whether a change helped until you trust what measured it,
> and a model-written rubric gives no sign when it is wrong.

The shelf holds `evaluation-integrity`.

The two nouns are not synonyms here, which was the objection to check before
accepting the proposal's own phrasing. An evaluation judges a system. A
measurement is a number somebody has to decide whether to believe. This
company keeps a separate register for the second one.

The caption's second clause is the shelf's whole argument and it is the one
thing a builder cannot find out by running the evaluation again: a broken
instrument returns a number rather than an error. That is
`evaluation-integrity`'s subject and it is checkable against the papers that
skill cites.

## Part 2, which is also the ask: the catch-all shelf

The name `More from the library` stands. It is a bare noun phrase, it
promises nothing, and the proposal did not flag it.

The caption does not stand.

> Distilled and shelved, on a shelf of its own for now.

Three things are wrong with it and only one of them is the count. "Distilled"
is a word from inside the pipeline and it is the recipe rather than the
product, which is canon law 3. The line is about the shelf rather than about
the skills on it, so a reader who wants to know why these skills have no
heading is not told. And "for now" has been "for now" since 2026-09-18.

> A skill lands here when its subject is not one of the headings above.

That is true above one skill and above twelve, it tells the reader the one
thing the shelf exists to tell them, and it says it without implying that a
heading is coming. Implying that would be a promise about our own artifact
with nothing behind it, because the two shelves below took a design audit, a
ledger entry, a hand-off and a copy round to name, and nothing in the
repository does that on a schedule.

## Part 3, which was not asked for, and the count that puts it here

This part is a finding with its repair attached. **Part 1 and part 2 can be
approved and set without it**, and the cost of doing that is named at the end
of this section rather than hidden.

Her ruling of 2026-09-29 on the pages she approved, in her words: "all the
subtitles are too choppy. prefer longer undecorated sentences." The ruling
names fragments first among the things it forbids.

Every caption on this page is a fragment. Not one of the seven contains a
finite main verb, so not one of them is a sentence. Four of the six on named
shelves are the identical frame, which is a short verbless opener, a full
stop, and a list of three.

| caption | frame |
| --- | --- |
| "The scaffold around a model. Tools, prompts, loop structure, and the feedback the loop runs on." | opener, then list |
| "Several agents dividing work. How they are organised, how they hand off, and how they fail." | opener, then list |
| "Post-training that updates the weights. Distillation, reward design, and self-improvement." | opener, then list |
| "Getting an answer out fast and cheap. Decoding, caching, and test-time compute." | opener, then list |
| "What goes into the window, in what order, and what to do when it will not fit." | one fragment |
| "Models that read and act beyond text, across images, audio, and the world." | one fragment |

The dates are the whole explanation and they clear everybody. These captions
were committed on 2026-09-18, eleven days before the ruling, by the
fifty-skill rebuild rather than by a copy round, and no owner has ever ruled
on one of them. So "the shape the six existing shelves use", which is what
the proposal asked for in good faith, is not an approved shape. It is an
unruled shape that predates the ruling which would have caught it, and
matching it would have put two more fragments on the page under cover of
consistency.

One of the six fails a second ruling as well. "Models that read and act
beyond text" gives a verb of reading to an act of taking something in, and
her ruling of 2026-09-29 is never "read" for ingested, on the site as in the
issue.

So the six are drafted here, each a sentence, and deliberately unalike. No
two of the nine captions on this page would open on the same two words.

| shelf | caption |
| --- | --- |
| Agent harnesses | Most of what makes an agent reliable sits outside the model, in the tools it is given, the loop it runs in and the corrections it gets back. |
| Context engineering | The window is finite, so what matters is what goes into it, in what order, and what to do when the work will not fit. |
| Multi-agent systems | Split a job across several agents and the hard part stops being the model and becomes the hand-offs between them. |
| Training loops | Changing the weights is a different job from changing the prompt, and it covers distillation, reward design and self-improvement. |
| Serving and inference | Once the answer is right, the remaining job is getting it out fast and cheap. |
| Multi-modal systems | Models that take in images, audio and the world beyond text, and act on what they find. |

`Context engineering` keeps nearly all of its own words, because it was the
best line of the six and it needed a verb rather than a rewrite.
`Serving and inference` is deliberately the shortest of the nine, because
captions that all run to the same length are the other half of the same tell.
`Multi-modal systems` trades "read" for "take in", which is the verb canon
law 15 fixes for that act.

**If only parts 1 and 2 are approved**, the page carries nine captions in two
registers, two of them sentences and seven of them fragments, and the two new
shelves will be the ones that look out of place. That is a worse page than
either whole answer, so it is said here rather than discovered on the site.
It is still a choice about scope, and scope is hers.

## Every sentence that could be asked "how do you know"

The charter's step 1b, against `docs/agents/quality-claims.md`. The register
holds one row per claim a public surface makes about the quality of what we
ship, and the sharp question is whether a sentence is about the research or
about our artifact.

Eight of the nine captions make claims about the research only, and each one
restates the subject of a skill the library holds, which is checkable against
the claim ids in that skill's own front matter. `agent-containment` carries
claims 1652, 1653, 1654, 1655, 1656, 1224, 1225, 1226, 1227, 1228, 882, 883,
884, 885 and 167. `evaluation-integrity` carries thirty, beginning at 476.
None of the eight needs a register row, because none of them says anything
about what alexandria does.

The ninth is the catch-all's, and it is the one to look at twice. "A skill
lands here when its subject is not one of the headings above" is about our
own page. It has no row in the register and it does not need one, because it
is checkable by the reader in the act of reading it: the headings are above,
the skill is below, and nothing is promised. **It is named here anyway**, per
step 1b, because deciding a sentence is out of a register's scope is a
judgement and the seat that keeps the register is not this one.

What none of the nine says: that a skill improves your agent, that the
library keeps a shelf current, or that a heading appears when the library
needs one. The first is `contradicted` in the register at 5.4 without the
skill against 5.3 with it. The second and third have no mechanism at all.

## The registers, checked before this shipped

- `docs/voice/awaiting-her-word.md`, first, before the taste register. This
  surface had no open row, and the row for it lands in the same pull request
  as this file. The nearest open row is `site/app/skills/page.jsx`, held by
  `skills-copy-2026-10-18.md`, which is the same page and not the same lines:
  that candidate draws the intro, the install block and the nine row
  sentences, and it leaves the shelf captions alone. **This file builds on it
  and supersedes nothing in it.** Where the two meet is worth saying: that
  candidate's row sentences and these captions are read within a few
  centimetres of each other, and they are written not to repeat a word of
  each other.
- `docs/voice/taste.md`, ruling by ruling. Bare-noun headings, 2026-09-29
  verdict 5. Longer undecorated sentences and no fragments, verdict 1, which
  is what part 3 is about. No colon-led constructions, 2026-09-20 verdict 2,
  and there is not one on this page. Never "read" for ingested, verdict 6. The
  builder's situation first, verdict 2, which is how eight of the nine open.
  "No more technical. We want to sell", 2026-09-20 verdict 3: no caption here
  defines a term, and the one club word in the old set, "test-time compute",
  is gone.
- `docs/voice/canon.md`. Law 3, sell the product and never the recipe, which
  is why "distilled" leaves the catch-all. Law 12a, the outsider test: every
  caption reads without the field's map, and "rubric" is ordinary English for
  a scoring guide. Law 15, the only act the word "read" may name.
- `docs/voice/ban-list.md`. Entry 3, symmetric rhythm, which is part 3's whole
  argument and now carries a count. Entry 37, every comma tested by removal:
  each comma in the nine joins two independent clauses or separates a list.
  One entry is appended by this run.
- `docs/voice/value.md`. The library is present on the catch-all shelf, which
  is the only one of the nine where it belongs. A caption is read under a page
  intro that already carries the growing self-maintaining library, and nine
  captions each asserting it is the symmetry tell with the value statement as
  its material. What a builder holds is the subject of eight of the nine, and
  "it" is the subject of none.
- `docs/voice/preferences/site-copy-2026-09-20.md` and
  `docs/voice/preferences/2026-09-29-site-copy.md`. No candidate here repeats
  a refused shape. No "One library, two readers", no definitional sentence, no
  "the frontier your agents can load", nothing cute, no diminutives, no
  marketing cadence.
- `docs/agents/copy-pipeline.md`, read before this round. One candidate per
  surface and not a menu: every line above is the single candidate for its
  slot, and part 3 is a question of scope rather than a choice between
  wordings.
- `docs/agents/quality-claims.md`, the section above.

## What the frontend seat needs that is not words

Two notes, because they are the difference between these captions being set
correctly and being set onto the wrong skills. Both are measured rather than
reasoned, and both are in `docs/ideas.md` for this run as well.

**Wire both new shelves by `names:`, not by `keywords:`.** The obvious
keyword for the second shelf is "measurement", and
`agent-security-measurement` has that word in its name, so the keyword route
files a security skill onto the evaluation shelf. The obvious keyword
"rubric" is worse: it was deleted from `Training loops` on 2026-10-24 for the
mirror image of this reason, and giving it to the evaluation shelf pulls
`self-improving-post-training-loops` off the shelf it belongs on, with only
the declaration order of `SHELVES` deciding which way it goes.

**The captions here run to two rendered lines**, the same as four of the six
they replace, measured against `.shelf-blurb` at 14px over a 520px column.
The shortest is 69 characters and the longest 140. Where they sit in the
layout is the frontend seat's call and not this seat's.
