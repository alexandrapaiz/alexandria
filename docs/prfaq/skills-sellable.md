# PR/FAQ — the skills become sellable

Per the company PM standard §2c: written before the initiative enters a
sprint. This is that document for the owner's reset of 2026-10-17, board
items `6e946000` and `5e7b7f49`. The owner's merge of this file is the go
decision. If the press release below does not read as compelling, the fix
is to revise this document, not the roadmap underneath it.

## The press release, as if it shipped

**Alexandria sells a skill a programmer can run today, not a newsletter
about one.**

A programmer who has never heard of alexandria runs one command and a
Claude Code skill is in their agent. The skill fires on a real task they
already had open, and the difference is visible before they close the
terminal: the same prompt, with and without the skill, side by side. If
they want the skill to keep learning instead of going stale, they pay $20
a month or $200 once, and alexandria keeps the whole library synced every
week against the research that proves each skill still earns its claims.

Nine skills exist today, each with a measured delta against a bare model
on tasks the bare model fails, not a description of what it is supposed
to do. A catalog page says what each one changes in an agent, in plain
words. The weekly newsletter that used to be the product is now the
funnel: every issue points at the skill it fed, with the install line in
it, because the research has to go somewhere a reader can use it in the
next five minutes, not just read about it.

## Customer FAQ

**What do I get for free?**
The install. Any of the nine skills, one line, into your own agent. No
account, no card.

**What does $20 a month buy that the free install doesn't?**
A library that keeps re-syncing. Skills are validated against research
that keeps moving; a skill installed once and never revisited is the
"research in a repository" the owner explicitly said is not the product.
The paid tier is the weekly re-sync plus every skill in the library, not
just the one you installed for free.

**How do I know a skill actually helps before I pay for anything?**
The catalog page shows each skill's measured delta: the same task, with
the skill and without it, the two answers side by side. That comparison
is why "proof inside the first session" is a sellable condition in its
own right, not marketing copy.

**What if I only want one skill, not the library?**
The free install already gives you that skill, forever, at whatever
version you installed. The library's re-sync is what you're buying when
you upgrade; installing a second skill free costs you nothing but running
the line again.

**Where does the newsletter fit now?**
It's the channel that finds you. Every issue cites the research a skill
is built on and tells you which skill it became, with the install line
printed in the issue itself. Reading it is free and always will be; it
exists to bring you to a skill, not to be the thing you pay for.

## Internal FAQ

**Why wasn't a markdown file in `skills/` already sellable?**
Because nothing between the file and a stranger's agent did the work a
buyer expects done for them: no install mechanism, no catalog a buyer can
read without opening the repo, and no visible proof before the ask for
money. The owner's judgment on 2026-10-17 names exactly this gap: the
library, the pricing page and the Polar checkout each already exist on
their own; nothing connects them into one path a stranger can walk.

**What are the five conditions, and is this seat inventing any of them?**
No. All five are the owner's own words, relayed on board item `6e946000`
(2026-10-17): a catalog page a stranger can read, one install line per
skill plus one for the library through a plugin marketplace served from
this repository, a reason to pay priced on the pricing page with a
checkout that completes, proof inside the first session, and a buyer's
path that is measured (visits, installs, payments). This document and
this sprint's regroom only sequence and assign them; nothing here is a
judgment this seat made on its own.

**Which condition is least likely to be met by Wednesday's brief, and
why say so now instead of letting it slip?**
The measured buyer's path (visits, installs, payments). No analytics of
any kind exists in `site/` today, checked directly this run. It is also
the condition furthest from what the owner's own "done means" sentence
asks for by Wednesday: a URL, an install line, and one payment walked to
completion in test mode. Naming it now, in this document and in the
sprint file, is the silence rule this directive itself invoked: a
condition that cannot be met by Wednesday is said plainly, with the
reason, rather than discovered on the day.

**Does the checkout need new engineering work to complete?**
No, and this is worth saying precisely because it looks like it should.
The Polar integration is built and merged (#285, against ADR-30/31).
`docs/product/polar-go-live.md` is a five-step, already-written checklist
that starts with creating a sandbox organization at sandbox.polar.sh, a
browser task with no pull request in it, overdue 21 days as of this run.
If the owner runs it herself, the same way she said she would run the
install line, the mechanical half of "a checkout that completes" is done
without a seat touching it. What a seat still owes is the pricing page's
framing (free install vs. paid weekly re-sync, not the newsletter-spine
language it carries today), which is copy, not payments plumbing.

**What does this change about the press and the pipeline?**
Nothing stops; less starts. The owner's own words: the press is the
funnel, so it keeps running, and no more effort goes to it beyond what
Monday's send needs. The three open engineer pull requests already
working the press-reliability gap (`#312`, `#315`, `#324`) land on their
own; no new press-side sprint item is added this cycle.

**What does "done" mean for this whole initiative, concretely?**
The owner's own sentence, verbatim from board item `6e946000`: "a URL and
an install line the owner runs herself, and one payment path she can
walk to the end in test mode, by Wednesday's brief." Everything in this
sprint's regroom is sequenced against making that sentence true by
2026-10-21, naming what will not be true yet rather than letting the gap
surface only when she runs it.
