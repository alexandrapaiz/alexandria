# The desk's verdict queue, for the frontend seat to set

**Writer seat, 2026-10-24. One candidate per line, which is the job. `site/`
is the frontend seat's surface, so this file is the words, the rule that
places them, and the numbers they are checked against. The diff is theirs.**

Board card `8787a154` asked for "a cap or a filter, and the words for it", and
said in its own body that the remaining half "needs the writer seat first" and
that "it needs one approved string."

It needs four, and it needs them in a different shape than the card proposed.
The reason is measured below and it is not a matter of taste: the card's
suggested cap would have shown her the eight oldest entries in the ledger and
hidden today's outage.

## What the page does now

`site/app/desk/page.jsx` renders every ledger entry whose status reads
`proposed` or `urgent`, unbounded, in the order they sit in the file.

```
Awaiting your verdict   524
```

Measured today by running the page's own parser over `docs/ideas.md`:

| | count |
|---|---|
| rows rendered | 524 |
| of those, marked `urgent` | 39 |
| of those, marked `proposed` | 485 |
| what the card recorded on 2026-10-14 | 426 |

So the queue grew by 98 rows in ten days and nothing left it. That number is
the subject of the words, and any line that names a remainder has to survive
her reading it again next week with a different figure in it.

## Why the card's shape is the wrong one, with the evidence

The card reasoned from a precedent on the same page. "The 'Recently merged'
list beside it is capped at eight, so the precedent for capping already
exists."

The cap transfers. The order under it does not, and the words sit on top of
the order.

`gh("pulls?state=closed")` returns newest first, so the merged list's eight
are the last eight merges and truncation costs nothing. `parseIdeas` returns
file order, and `docs/ideas.md` is appended to, so the verdict queue is oldest
first. The first three rows it renders today are

```
2026-09-18 — Skill-verification badge on every library entry
2026-09-18 — Scoped skill delivery by default
2026-09-18 — Agent packs: skill + activation prompt as a priced SKU
```

and row 524, the last one a reader reaches, is

```
2026-10-23 — URGENT: the Modal workspace is disabled, so every cron and the
MCP server are down
```

Capping that list at eight prints eight proposals from 2026-09-18 and drops
the compute outage. The two lists look alike and only one of them is sorted.

There is a second asymmetry the precedent hides. The merged list is a record
of what happened, so eight of it is a sample and the rest is history. The
verdict queue is a list of decisions she owes, so eight of it is not a sample,
it is 516 obligations behind a number nobody reads. A truncation notice under
a list of debts is the wrong instrument, and that is the whole reason this
needs words rather than a `slice(0, 8)`.

## The shape, decided

Not a cap by count, and not a filter. A filter asks her to type something in
order to find out what she owes, which hands the choosing back, and the
company standard on filters is that one accepted and not honoured is worse
than none at all.

**Render every entry marked `urgent`, in the order they are in, which is
oldest first. Render no entry marked `proposed`. Say both numbers above the
rows rather than below them.**

That is 39 rows instead of 524, with no judgment about which urgent entry
matters and nothing hidden that was not already unreachable. Oldest first is
correct inside 39 rows, because the longest-unanswered is the one that has
cost the most, and it was only wrong at 524 because 524 buries anything.

Above the rows rather than below because a notice at the bottom tells her what
she was looking at after she has finished looking. Her own fine-tuning of
`prompts/digest.md` carries the same invariant for issues, which is that the
reader is situated before the finding arrives.

## The four lines

The counts are live, so these are written with their slots named. `{urgent}`
and `{proposed}` come from the same parse that builds the rows, and the
section heading's badge keeps the whole `{urgent} + {proposed}`.

**1. The section intro, where there is no line today.** Normal case, both
counts above zero.

```
The 39 marked urgent are below. The other 485 are proposals, and the ledger
holds them until you rule on them.
```

```
The {urgent} marked urgent are below. The other {proposed} are proposals, and
the ledger holds them until you rule on them.
```

**2. The same intro when nothing is urgent.** This one is also the empty
state, since no rows render.

```
Nothing is marked urgent. {proposed} proposals are in the ledger.
```

**3. The empty state when the queue is empty.** It replaces "No proposed
ideas in the ledger."

```
Nothing is awaiting your verdict.
```

**4. The merge list's empty state, repaired while I am on this page.** It
reads "Nothing waiting. The queue is clear." today, which is two fragments,
and her ruling of 2026-09-29 is "all the subtitles are too choppy. prefer
longer undecorated sentences." A fragment is the choppiest available form.

```
Nothing is awaiting your merge.
```

That makes the two empty states one sentence apart from each other, which is
what two parallel lists on one page should read like.

The word "ledger" in lines 1 and 2 carries the link to `docs/ideas.md`, said
once, which is the other half of the next section.

## The affordance, which is the card's second finding

The card's other entry against this page is that "the same open affordance
appears 426 times and every one points at the same destination. That is
wallpaper rather than an offer."

Thirty-nine of it is still wallpaper. So **`open →` comes off the row.** The
row stays a link. The precedent is on the same page and three sections down:
`desk-row done` carries no `desk-go` span and the merged rows are links
anyway.

One condition returns it. `docs/ideas.md` entries open with
`### 2026-09-18 — name`, and a heading GitHub renders is a heading GitHub
anchors, so a row could link to its own entry rather than to the file. If the
frontend seat produces that link, `open →` is an offer again and should stay,
because then no two rows point at the same place. I have not verified that
GitHub's slug for these particular headings resolves, since they carry em
dashes, colons and parentheses, and asserting a URL I did not open is the
mistake the company standard on verifying location before claiming it names.
So it is a condition on their diff and not a fact in mine.

## The precondition these words have, and it is a defect

A line that prints a count is a claim, and this one is wrong.

`tools/ledger.py` exists to read `docs/ideas.md` through its contract instead
of by grep, because an entry can hide from a grep by writing a status in
prose. That is recorded in the incident register on 2026-09-24 and in the
ledger's own entry of the same day. The desk's `parseIdeas` is a grep, in
JavaScript, on the owner's own page, and the two readers disagree.

```
$ python3 tools/ledger.py --census
605 dated entries in docs/ideas.md, 543 with a status a filter can read
  proposed   486
  urgent     39
```

486 and 39 is 525. The desk prints 524. The one entry it cannot see is

```
2026-09-24 — A ledger entry can hide from every consumer by writing its
status as a sentence (engineer agent)
```

Its real status line reads `- Status: proposed`. Twenty lines above it, inside
its own first bullet, it quotes the command it is warning about:

```
grep "Status: accepted" docs/ideas.md
```

The desk's pattern is `/- Status:\s*(\w+)/`, with no line anchor and no `m`
flag, so it matches inside that quoted command and reads the entry as
`accepted`. The ledger entry whose entire subject is that a status written as
a sentence hides an entry from every consumer is hidden from the owner's
console, by a status written as a sentence, in its own body.

**The safe form, so the fix is copied rather than composed.** One anchor and
one flag:

```js
const status = (rest.join("\n").match(/^-\s+Status:\s*(\w+)/m) || [])[1];
```

Measured both ways over the live file:

| pattern | queue | urgent | proposed |
|---|---|---|---|
| `/- Status:\s*(\w+)/` (today) | 524 | 39 | 485 |
| `/^-\s+Status:\s*(\w+)/m` | 525 | 39 | 486 |

The second agrees with `tools/ledger.py` exactly. `docs/voice/check_voice.py
ledger` fails until it does, and goes green on that one-character diff.

**This is not optional ahead of the words.** Line 1 says "the other 485 are
proposals" out of a page that is reading the file wrongly. Set the anchor in
the same diff as the lines, or the first thing she reads is a number the
repository's own checker contradicts.

## What this candidate does not claim

Nothing here says anything about what alexandria ships, so
`docs/agents/quality-claims.md` has no row to find and needs none. The two
sentences a reader could answer "how do you know that" are the two counts, and
both are computed in front of her from the file the link goes to.

"the ledger holds them until you rule on them" is the one line that asserts a
mechanism. It is true of the file: a status changes in place and no entry is
removed, which is why `closed`, `done` and `built` all appear in it today.

## Checking it

```
$ python3 -I docs/voice/check_voice.py candidates
$ python3 -I docs/voice/check_voice.py ledger
$ python3 -I docs/voice/check_voice.py reading
```

`site/app/desk/page.jsx` has no row in `docs/voice/awaiting-her-word.md`, so
this is the first candidate written for that surface and supersedes nothing.
It gets its row in this diff.
