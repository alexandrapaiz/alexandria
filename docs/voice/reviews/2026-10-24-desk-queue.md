# Graded review, 2026-10-24 — the desk's verdict queue

**Writer run 45.** Board card `8787a154`, "The desk's verdict queue needs a cap
or a filter, and the words for it", which is the one card on the board that
names this seat as its blocker. The candidate is
`docs/voice/desk-verdict-queue-2026-10-24.md`.

## The single biggest weakness, plainly

The page prints a wrong number in its largest type, and the entry the number
is missing is the entry about numbers like this one.

`site/app/desk/page.jsx` reads `docs/ideas.md` with its own regular
expression. `tools/ledger.py` exists in this repository because reading that
file by grep hides entries, which is recorded in the incident register on
2026-09-24 and in the ledger's own entry of the same day. The desk is a fourth
grep reader of that file and it is the one the owner opens daily.

The two readers disagree by one entry, and the entry is

> 2026-09-24 — A ledger entry can hide from every consumer by writing its
> status as a sentence (engineer agent)

Its status line reads `proposed`. Twenty lines above it, inside its own first
bullet, it quotes `grep "Status: accepted" docs/ideas.md` as the command that
would have missed the defect it was filed about. The desk's pattern has no
line anchor, so it matches inside that quoted command, reads the entry as
`accepted`, and drops it from the queue. The entry warning that a status
written as a sentence hides an entry from every consumer is hidden from the
owner's console, by a status written as a sentence, in its own body.

That is not a prose finding and it is the reason the words could not be
written without it. Line 1 of the candidate says "the other 485 are
proposals". The repository's own reader of the same file says 486.

## What the card asked for, and what it gets

It asked for one string. It gets four, and a different shape than it proposed,
and the reason is a measurement rather than a preference.

The card reasoned from the merged list beside the queue: "the precedent for
capping already exists on the same page." The cap transfers and the order
under it does not. `gh("pulls?state=closed")` returns newest first;
`parseIdeas` returns file order, and `docs/ideas.md` is appended to. So the
merged list's eight are the last eight merges and the verdict queue's eight
would be

```
2026-09-18 — Skill-verification badge on every library entry
2026-09-18 — Scoped skill delivery by default
2026-09-18 — Agent packs: skill + activation prompt as a priced SKU
```

and five more from the same morning, with row 524 — "URGENT: the Modal
workspace is disabled, so every cron and the MCP server are down" — not
printed. The card's shape, applied as written, would have made the page worse
on the one day the outage was live.

The second asymmetry it hides is the one the words sit on. The merged list is
a record of what happened, so eight of it is a sample. The verdict queue is a
list of decisions she owes, so eight of it is 516 obligations behind a number
nobody reads. A truncation notice under a list of debts is the wrong
instrument, which is why this needed words and not a `slice(0, 8)`.

The shape decided: render every `urgent` entry, render no `proposed` entry,
and say both numbers above the rows rather than below them. 39 rows instead of
524, nothing hidden that was not already unreachable, and no judgment about
which urgent entry matters.

## The numbers, measured at `origin/main`

The ref matters and it is the kind of thing this seat has got wrong before. The
page fetches `docs/ideas.md` from `main` over raw.githubusercontent, so the
figure she reads is main's figure. This run appended three ledger entries, which
moved the working tree to 527 against 528 and left the live surface where it
was. `check_voice.py ledger` takes a ref and prints which one it read.

| | |
|---|---|
| rows the page renders | 524 |
| what the contract reader counts | 525 |
| marked `urgent` | 39 |
| marked `proposed` | 485 on the page, 486 in the contract |
| what the card recorded on 2026-10-14 | 426 |
| oldest row | 2026-09-18 |
| newest row, printed last | 2026-10-23 |

The queue grew by 98 in ten days and nothing left it. That is the figure the
words have to survive, and it is why both counts in the candidate are slots
rather than numerals.

## The taste gate, ruling by ruling, before the laws

Run first, as the charter's shipping step requires. The rulings that reach a
line on this page:

- **2026-09-29 (1), longer undecorated sentences.** "all the subtitles are too
  choppy. prefer longer undecorated sentences." The page fails it today, in a
  string the card never mentioned: the merge list's empty state reads
  `Nothing waiting. The queue is clear.`, which is two fragments. Repaired as
  line 4 of the candidate. **Was failing, repaired.**
- **2026-09-25, graph page copy.** "hints are instructions, not invitations",
  and no personification. Lines 1 to 3 are instructions. "the ledger holds
  them until you rule on them" attributes holding to a file, which is what a
  ledger does and not a character it is given. **Held.**
- **2026-09-20 (1), plain short sentences, no comma chains.** The longest
  candidate line carries one comma. **Held.**
- **2026-09-20 (2), no colon-led constructions, no diminutives, no cute
  asides.** None. **Held.**
- **2026-09-27, codes are never owner-facing.** The desk is the most
  owner-facing surface in the company. No candidate line carries an
  identifier, a number, or a code. The board card's own id appears in this
  review and in the candidate, neither of which she reads as copy. **Held.**
- **2026-09-29 (5), headings are bare nouns.** `Awaiting your verdict` is
  unchanged and stays. **Held, untouched.**
- **2026-09-29 (6), never "read" for ingested.** No candidate line uses the
  word at all. The ruling is still red on the page as a whole and the five
  failures are the five open rows in `awaiting-her-word.md`, none of them on
  the desk. **Held in this candidate, failing elsewhere and already drafted.**

`python3 -I docs/voice/check_voice.py taste` reports one FAIL, verdict 6, and
it is the same FAIL run 44 reported for the same reason: the archive masthead
is drafted and not set. This run adds nothing to it.

## The laws

Laws 4 to 8, 10 to 14 and 16 govern an issue's findings, headings, evidence
grades, links, close, length and title. This run's artifact is four lines on a
console, so those laws have no surface here to score and scoring them would be
the flattering grade the charter warns about. The laws that do bind:

1. **Law 1, plain sentences and transition words, no stylistic em dashes, no
   semicolon joins.** Held. One comma across four lines, one "and" doing the
   joining, no dashes, no semicolons.
2. **Law 2, no buzzwords, every line targeted and actionable.** Held. The four
   lines carry two counts, one location and one instruction between them.
3. **Law 3, sell the product, never the recipe.** Not applicable. The desk is
   her own console and sells nothing. Recorded rather than scored, because a
   law marked held on a surface it does not reach is how a grade becomes
   decoration.
9. **Law 9, the fine-tuned instruction is the foundation.** Held, and it is
   the reason the intro goes above the rows instead of below them. Her
   context-first invariant in `prompts/digest.md` is that the reader is
   situated before the finding arrives. A truncation notice under a list tells
   her what she was looking at after she has finished looking.
15. **Law 15, the library never claims to have read what it only ingested.**
   Held. No candidate line uses "read" in any form.

## No generator patch, and the evidence for that

Step 3 of the charter is the whole point of this seat, so its absence needs an
argument rather than a silence.

`prompts/digest.md` is byte-identical to main in this pull request. The press
has printed nothing since 2026-10-05. `site/content/issues/` holds `2026-W37`
and `2026-W39` and nothing else, and line 3 of `2026-W39` still reads "read in
full and distilled weekly", which is the same line run 44 drafted the repair
for. `check_voice.py measure`, `links`, `firstuse` and `generator` return the
figures run 44 recorded, on the same two files.

Run 44 graded that artifact against eight gates and found that four of the
five rules it fails are younger than the print itself. A third grade of an
unchanged artifact against unchanged rules produces a third wording of a rule
aimed at a number that does not exist yet, which is the patching the ban list
keeps refusing in its own words. The first real test of those rules is the
next send, and the next send is blocked on the compute outage that is row 524
of the list this run is about.

## What this run added to the instruments

`python3 -I docs/voice/check_voice.py ledger`. It reads the status pattern out
of the desk page rather than holding a copy of it, computes the queue both
ways over the live file, and fails where the page and the contract disagree.

```
  FAIL    proposed   desk  485   contract  486
  OK      urgent     desk   39   contract   39
            total      desk  524   contract  525
```

Probed against the one-character fix in a scratch copy of the page: `rc=0`,
486 and 486. `site/` is untouched in this diff and `git diff site/` is empty,
because setting it is the frontend seat's work.

It compares the two counts rather than grepping the page for a known-good
regex, because a check that looks for a string passes on any pattern
containing it and says nothing about the number on the surface. The company
standard the last two runs kept hitting is that a gate is judged by what it
can see, and what this one has to see is the figure the owner reads.

## What leaves this run unresolved, and for whom

- **The frontend seat.** Four lines and one anchor, in one diff. The anchor is
  not optional ahead of the lines, because line 1 prints a count the
  repository's own checker contradicts until it is set.
- **The frontend or engineer seat, conditionally.** Whether GitHub's heading
  slug resolves for ledger entries carrying em dashes, colons and parentheses.
  If it does, each row can link to its own entry and `open →` earns its place
  back. I did not open one, so it is a condition on their diff rather than a
  fact in this file.
- **Nobody yet, and it is the oldest thing here.** 62 ledger entries carry no
  status a filter can read, 30 of them scan notes that may owe none. The
  heading says "Awaiting your verdict" and the count behind it excludes all
  62. `tools/ledger.py --check` already ratchets that number and the statuses
  belong to the owner, so this is cited rather than refiled.
