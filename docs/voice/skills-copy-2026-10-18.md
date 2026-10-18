# Site copy: the skills, as a stranger meets them

Writer run, 2026-10-18, second of the day. One copy round for the three
surfaces the sellable-skills sprint turns on: the catalogue page, the
install block, and pricing. Drafted into this file for the owner to rule
on and the frontend seat to set. Nothing in `site/` is touched here.

The frontend seat asked for exactly this, in its own words on PR #333:
"This brief asks for a hero sentence, an install line, a one-sentence
promise per catalog row and new pricing words. Under the charter's 'you
set the words, you do not write them', none of those are mine to
author." They are this seat's, under her ruling of 2026-09-19.

## The gate that ran first, and what it took off the page

Before any candidate, `docs/agents/quality-claims.md`, because the
sharpest question a reader can ask about a skill is how do you know. The
rule is the register's own: a flat present-tense claim with an empty
mechanism column does not ship, and a claim whose machine does not exist
either ships hedged the way the routines page hedges a routine, or it
does not ship.

Four sentences live on the two skills surfaces today. Three of them fail.

| Live sentence | Where | Row | State | Verdict |
| --- | --- | --- | --- | --- |
| "the library keeps every skill current at the pace of the research that is gaining the most traction" | `site/app/skills/page.jsx:31` | "keeps every skill current" | **not built** | Drop. No skill freshness is computed or published anywhere. |
| "agents that work from the current state of the evidence today and still will next month" | `site/app/skills/page.jsx:31` | "today and still will next month" | **not built** | Drop. A forward guarantee needs the revision job deployed and a lag nobody publishes. |
| "Skill updates as the research moves" | `site/app/pricing/page.jsx:35` | "revised when the research sharpens it" | **queued** | Drop or date it. Zero revisions have ever fired from a mechanism. |
| "a way of doing one job that the research has shown to work" | `site/app/skills/page.jsx:31` | about the research, not the artifact | holds | Keep. Every skill names its claims and its papers, and a reader can follow both. |

The first two were approved by the owner on 2026-09-29, in her words
"good. i like this." This round proposes changing them anyway, and the
reason is dated: the claims register was created the next day, on her
own order, and its whole subject is sentences exactly like these. A
seat that treats a prior approval as a defence against a later register
has the order backwards.

**The repair is to drop the claim, never to soften it.** That is canon
law 15's rule and ban list 50's: a concession that licenses the
assertion behind it reads careful and stays false. "Aims to keep every
skill current" is the same sentence in a coat. So the forward guarantee
is not hedged here. It is replaced by something checkable, which is the
record each file already carries.

### One claim is in no row, and it is new today

PR #339 puts the install line in front of readers on three surfaces that
did not exist when the register was written: `README.md`,
`docs/product/install.md`, and the two plugin manifests, whose
`description` fields are read inside Claude Code by anyone who browses
the marketplace. All four carry the same sentence.

> Nine skills for building agents, written from AI research papers read
> in full and revised when the evidence moves.

"Revised when the evidence moves" is the precedent claim, the one ADR-36
exists because of, and the register records it `queued` with zero
revisions ever fired by a mechanism. The sentence is not this seat's to
edit and the finding is not this seat's to resolve. It is named here and
in the pull request, per the charter's step 1b.

One honest complication, and it is evidence for the ExO rather than an
argument against the row. Skills **have** been revised since the register
was written, by the skill seat, by hand, from a contradiction in the
claim graph: `harness-engineering` is at version 5 and its own front
matter dates a 2026-10-13 revision to a claim contradicted on 2026-10-12.
Whether a seat doing it by hand with a reachable trigger counts as a
mechanism is the capability test in `docs/agents/unowned-duties.md`, and
the ExO owns that call. Until it is made, the row reads `queued` and the
copy below says only what the files can be seen to carry.

## Surface 1: the catalogue page, `/skills`

Heading unchanged. "Skill library" is a bare noun and that is her ruling
of 2026-09-29.

**One candidate.**

> Most of building with models is knowing which techniques actually
> hold, and the measurements that settle that arrive faster than anyone
> can read them. Each skill here covers one job an agent does, written
> from the papers the library read in full, and each one is built around
> the places where the measurement points somewhere other than the
> choice a good engineer makes unaided. Every section names the findings
> and the papers behind it, so your agent works from a number you can
> check instead of from the consensus it was trained on. The library
> grows every day, and every skill carries its own dated record of what
> it used to say and which paper changed it.

The approved agent line stays under it, verbatim, because an approved
line outranks any rule about lines.

> Your agents can read this catalogue on their own, at /llms.txt.

**What changed and why.** The builder's situation opens it, which is her
2026-09-29 ruling and what sold the approved pages. The last sentence
carries the growing library and the self-correction, which is the test
no candidate may fail, but it carries them as a record a reader can open
rather than as a promise about next month. That is the whole move in
this round: the forward guarantee is unbuilt and the dated revision
history is sitting in public in every file's front matter, already
rendered on the page as "The receipts". Checkable beats confident.

**What it is still not allowed to say.** That a skill improves your
agent. The library's one measurement of that came back 5.4 without the
skill against 5.3 with it, on 2026-09-30, and the register carries it as
`contradicted`. Every sentence above is about the research or about what
the files visibly contain.

## Surface 2: the install block

Two lines a stranger pastes. They are facts about files, and they are
the engineer's, from PR #339, unmerged as this is written. The words
around them are this seat's.

**One candidate**, to sit above the shelves, before any claim id.

> Paste these two lines into a Claude Code session and your agent has
> all nine.
>
> ```
> /plugin marketplace add alexandrapaiz/alexandria
> /plugin install alexandria-skills@alexandria
> ```
>
> Nothing runs on your machine when they install. The nine descriptions
> stand in the session at about 1,900 tokens, and a skill's body is read
> only when the work in front of your agent matches what that skill is
> for.

Every number and every negative in it is gated: `claude plugin details`
printed the token figure on 2026-10-18, the four zeros next to the skill
count are what makes "nothing runs" true, and
`tools/check_plugin_manifest.py` fails the build when the sentence and
the repository disagree. **This block cannot be set until #339 merges**,
because until then the marketplace manifest it names does not exist.

## Surface 3: pricing, and the sentence that is already false

This is where the round stops, and it stops on a fact rather than on
taste.

`github.com/alexandrapaiz/alexandria` is public. All nine skill files
are in it, in full, at `skills/*/SKILL.md`. Anyone can read them today
without paying, and after #339 merges anyone can install all nine with
two lines. Meanwhile the site says this, in two places:

> The full skill library, file by file. (`site/app/pricing/page.jsx`)
>
> The catalogue is public. The skill files themselves come with the paid
> plan. (`site/app/components/SkillLibrary.jsx`)

Those sentences describe an entitlement the repository gives away. The
gate in `site/lib/entitlement.js` is real and it works, and it guards a
door in a wall that has no other sides.

No wording fixes that, so this seat is not going to write around it. The
decision is the owner's and it is one question: **are the skill files
the paid product, or the free distribution that sells something else?**

- If they are the paid product, the public repository is the thing to
  change, and the install line in #339 is the surface that has to change
  with it. The words follow in a day.
- If they are the free distribution, pricing needs a paid line that
  names something that exists, and the honest inventory today is thin:
  routines are not built, skill revision has never fired, and the issue
  and the archive are already free.

What can be drafted before she rules is the one line that is true under
either answer, and it is the line the pricing page is missing rather
than the one it gets wrong.

> Every issue is free, the whole archive is free, and the nine skills
> are free to install.

Held back deliberately: a paid tier's words. Writing them now would be
inventing a product, and the eight rejected rounds of 2026-09-20 are what
happens when copy is asked to supply something the company has not
decided.

## Surface 4, which was not asked for: the nine catalogue rows

The brief asks for "a one-sentence promise per catalog row". There is no
such sentence in the repository. `site/lib/skill-shelves.js` slices the
first sentence off each skill's `description`, and that description is
written for an agent's router, so the page prints router text to a
buyer. `agent-containment` currently sells itself with "Where to enforce
the boundary an agent runs inside, and what each choice measures."

That is accurate and it is addressed to a machine. Her ruling of
2026-09-20 on exactly this register: "no more technical. we want to
sell."

Nine candidates, one per skill, each one about what the research found
rather than about what our file does. They are deliberately unlike each
other in shape, because nine rows in one grammar is the symmetry ban
list entry 3 names.

- **agent-containment** — Most teams keep an agent in bounds with a deny
  list of forbidden commands and paths, and the measurement says that
  list blocks almost nothing, so the useful question becomes where the
  boundary gets enforced instead.
- **agent-memory-selection** — An assistant that remembers across
  sessions has to decide what to write down and what to fetch back
  later, and the evidence is clear about which of those two deserves the
  expensive model call.
- **agent-security-measurement** — A refusal rate measures what a model
  said and not what the account went on to do, which is why most
  reported agent-safety numbers survive an adversary badly.
- **context-window-engineering** — When the work does not fit the
  context window something has to be dropped, and the research on which
  scoring rules beat dropping at random is less flattering than you
  would expect.
- **evaluation-integrity** — Once the rubric, the benchmark or the judge
  is itself written by a model, a high score can come from a broken
  instrument rather than from a good system, and a broken instrument
  never throws an error to say so.
- **harness-engineering** — Fine-tuning a smaller model on a stronger
  one's transcripts is the move most teams reach for, and it lost ground
  on every task in the study that tried it, which changes where the next
  week of work should go.
- **recursive-harness-self-improvement** — An agent that rewrites the
  scaffolding around itself, meaning its own prompts and tools, and
  keeps whatever scores better, needs every safeguard a human reviewer
  would have supplied built into the loop instead.
- **self-improving-post-training-loops** — When a model's own output
  becomes the supervision for its next training run, particular things
  break that an ordinary fine-tune never has to worry about.
- **skill-library-engineering** — A skill file written carefully by hand
  from the task description left agents slightly worse off than loading
  nothing at all, so what a skill is built from matters more than how
  well it is written.

Each sentence is checkable against the paper the skill cites for it, and
none of them says anything about what our file will do for your agent.
That is the line the register draws and it is the line this round holds.

**Where they have to live is not this seat's call.** A `summary` field
in each skill's front matter belongs to the skill seat; a copy file the
site reads belongs to the frontend seat. The ledger entry naming that
choice is in `docs/ideas.md` for this run.

## The registers, checked before this shipped

- `docs/voice/taste.md`, line by line. Bare-noun heading kept. Longer
  undecorated sentences, no fragments, no colon-led devices, no bold
  inside body copy. No codes in anything owner-facing. The 2026-09-29
  rulings are the register the catalogue candidate is written in.
- `docs/voice/canon.md`. Law 3, sell the product and never the recipe:
  nothing above describes the pipeline. Law 12a, the outsider test:
  "scaffolding" is glossed at first use in the one row that needs it.
  Law 15: "read in full" names the only act the word may name, and the
  papers behind a skill are read in full.
- `docs/voice/ban-list.md`. Entry 50 is the one this round turns on and
  it is why the unbuilt claims are dropped rather than hedged. Entry 37,
  every comma tested by removal. Entry 3, nine rows deliberately unalike.
  One new entry is appended by this run.
- `docs/voice/value.md`. The library is present in the catalogue
  candidate, growing and keeping its own record. What a builder holds is
  the subject of every candidate, and "it" is the subject of none.
- `docs/voice/preferences/site-copy-2026-09-20.md`. No candidate here
  repeats a refused shape. No "One library, two readers", no definitional
  skill sentence, no "the frontier your agents can load", no marketing
  cadence, nothing cute.
- `docs/agents/copy-pipeline.md`, read before this round. One candidate
  per surface, into a file, never into chat. The one place two options
  appear is the pricing decision, and that is a product choice rather
  than a choice between words.
- `docs/agents/quality-claims.md`. The table at the top of this page.
