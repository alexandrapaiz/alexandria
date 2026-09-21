# Reader-facing copy — who drafts, who rules, who sets

**Enforced at:** prompts/writer-agent.md §"Site copy is yours to draft",
prompts/frontend-agent.md run step 0, and prompts/exo-agent.md §3e every
run.

Written by the ExO agent on 2026-09-21, on the owner's order, after the
site-copy session of 2026-09-20. This page exists because of one day of
evidence and it is the fix for incident 25.

## What happened, plainly

The chair drafted site copy live with the owner for eight rounds. Every
round was rejected. The full verbatim record, every candidate with her
verdict and her reason in her words, is
[docs/voice/preferences/site-copy-2026-09-20.md](../voice/preferences/site-copy-2026-09-20.md).

Nobody was lazy and nobody was careless. The rounds got better at prose
and never got closer to shipping, which is the signature of a process
defect rather than a craft defect. Her diagnosis of the eighth round is
the one sentence to keep: "its describing the mechanism not what it
delivers. or the value to a builder."

This is the same anti-pattern as incident 22, where she said "right now i
feel like im doing the PMs job, i want the pm to be proactive." There the
owner did the PM's work because the PM was asleep. Here the owner did the
writer's work because the writer was forbidden from doing it. The shape
is identical. **The owner was the only actor in the loop, and she was
doing a seat's job by hand.**

## Why it happened, in three layers

All three are real and no one of them alone explains eight rounds.

### 1. The duty was assigned to a seat whose charter forbade it

On 2026-09-19 the owner widened the voice canon to cover site copy and
ruled how the work divides. The ruling is in
[docs/voice/taste.md](../voice/taste.md): "The writer drafts, the
frontend seat sets, both under the outsider test."

On 2026-09-20, `prompts/writer-agent.md` line 78 still read:

> Never site copy (frontend's lane)

So the seat the ruling named was told by its own charter not to do it.
Meanwhile the frontend charter's five run steps are entirely visual,
which are screenshots, layout repair, benchmarking and interaction
polish. Not one of them says write a line. Its writable surface includes
`site/`, so the seat that *could* change the words was never asked to
choose them, and the seat that was asked was not allowed.

The result is the worst available shape. The duty read as owned in both
directions and was performed by neither, so it fell to whoever was
present. That was the owner, for eight rounds.

This is incident 20's class again. The ruling was recorded correctly, in
the right register, within the hour, and the charter that had to change
for the ruling to take effect was never opened. **Recording is not
enforcing**, and a ruling that contradicts a live charter line is worse
than unrecorded, because the seat now has two instructions and will obey
the one in front of it.

### 2. There was no positive specification to converge on

`docs/voice/taste.md` on the morning of 2026-09-20 held about forty
rulings. Nearly every one of them is a rejection. It says no colon-led
constructions, no cute asides, no diminutives, no marketing tone, no
mechanism, no long comma chains, no defensive framing, no ad rhythm. It
is an excellent record of what the words must not be.

It never says what the product is worth to a builder.

A register of rejections cannot converge, and that is arithmetic rather
than an opinion. Each "no" removes one candidate from an unbounded space.
Eight rounds removed eight regions and the target was never located,
because nothing in the repo had written the target down. Her own
instruction says so: "no mention of a growing self mantaining corpus,
nothing. thats my point."

So the missing artifact is not better copy. It is the **value
statement**, and it has to exist before copy is attempted again. See the
next section.

### 3. The drafting happened in chat, so nothing accumulated

Eight rounds produced no file until the ninth act, which was the chair
writing the session down after the fact. While the session ran, each
round started from the last verdict held in conversation rather than from
a register any run could read. Nothing was cumulative, so round seven
could and did repeat the failure of round two in a new costume.

Drafting into a file is what makes a round cheap. Drafting in chat makes
every round cost the owner's attention twice, once to read and once to
remember.

## The pipeline, as it now stands

Two phases, and the first one gates the second.

### Phase 0, once: the value statement

The writer seat drafts `docs/voice/value.md`, one page, and the owner
approves it in chat. Nothing about the site's words is drafted until she
has. The spec is below.

### Phase 1, per round: draft, rule, record, set

1. **The writer drafts**, into a file, never into chat. One candidate per
   surface, not three, because a menu asks the owner to do the choosing
   that the seat was hired for. Every candidate is written against
   `docs/voice/value.md` first, then `docs/voice/taste.md`, then the
   newest file in `docs/voice/preferences/`, then
   `docs/market/positioning.md`.
2. **The owner rules in chat**, line by line, in her own words. Her
   verdict is the only verdict. This step is hers and it does not move.
3. **The verdict is recorded** the same session, into the current
   preference file under `docs/voice/preferences/`, in the schema in
   [preference-data.md](preference-data.md). The chair records. A round
   whose verdicts were not written down did not happen, because the next
   round cannot read a conversation.
4. **The frontend seat sets** the approved lines into `site/`, as a diff
   from the writer's file. It sets what she approved and it writes
   nothing new.

### The tripwire that would have stopped this

**After one rejected round on the same surface, the chair stops drafting
and hands the round to the writer seat.** One round is how a direction
gets probed live, which is legitimate and often the fastest thing in the
room. Two is a pattern. Eight is a missing seat.

That number is deliberately low and it is the whole enforcement. The
chair is the seat with no cron and no cap, so it is always the cheapest
actor to reach for, and that is exactly why it needs a stated stopping
rule. Every other seat's limit is enforced by a workflow. The chair's has
to be written down.

## The value statement, specified

The artifact is `docs/voice/value.md`. The writer seat drafts it and owns
the file. The owner approves it. This page specifies what it must
contain, and it deliberately does not contain a draft, because writing
the line is the writer's craft and ruling on it is hers.

**What it is for.** One page that states what alexandria is worth to a
builder, in her register, so that every later line of copy has a target
to converge on instead of a space of rejections to wander.

**What it must answer, in this order.**

1. What the builder has, once they have alexandria. The answer she has
   already given is the **growing, self-maintaining, compounding library
   of the frontier**. Not the issue. Not the daily email. The corpus, and
   the fact that it keeps itself correct.
2. What having that does for them, stated as a change in what they can
   do. The mission is the frame: accelerate every builder to frontier
   speed (docs/vision.md §0).
3. Why the compounding matters, which is that a library that corrects
   itself is worth more next month than this month, and a link dump is
   worth the same forever.
4. What their agents get, which is the same corpus, loadable.

**The constraints it inherits.** Every rejection in taste.md still binds.
Three of them bind hardest here, because they are the three the eight
rounds kept breaking.

- **Value, never mechanism.** Do not describe what the system does. State
  what the builder ends up holding. "Every day it reads the new papers,
  extracts the findings, and checks them" is mechanism and was rejected.
- **"It" is not the subject.** Her ruling on round eight names the word.
  Sentences whose subject is the machine describe the machine.
- **The corpus must be present.** A page about this product that does not
  say the library grows and maintains itself has missed the point, in her
  words, and that is the sentence she had to say twice.

**Length.** One page. Short enough that the writer opens it every round
and long enough to be a specification rather than a slogan.

**When it is done.** When she says so in chat, and the approval is
recorded in the preference file with her words. Until that line exists,
phase 1 does not start.

## What this page is not

It is not a verdict on any candidate line, and it is not the value
statement. Both of those are the owner's and the writer's. This page is
the process only, which is this seat's lane.
