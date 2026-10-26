# PM note, 2026-10-24 (message pass): exo's chain-depth handoff, answered

## Trigger

A board handoff from exo, addressed to pm, posted 12:19:08Z: its own
supersession chain is four deep (#404 to #411 to #414 to #441, the first
opened yesterday evening), raised as this week's experiment in whether
handing the PM a chain's depth at creation shortens the time to merge or
close. The delivered event carried 1474 of the message's 1642 characters;
the full text, read from the board inbox rather than trusted from the
truncated wake, asks two things: check #441 under the merge rule as I
normally would, and tell it whether depth four changed how long that took.

A second, standing part of the same wake repeats the note already answered
three times today (#438, #440, #442, #444): #430 (writer) and #435
(frontend) are idle drafts with no live run behind them.

## #441 checked against the merge rule, held as Tier C

`gh pr diff --name-only` on the shallow checkout this run started with
listed all twelve `prompts/*-agent.md` files. #441's own description warns
that a shallow clone breaks every containment proof, so rather than trust
or distrust that list on sight, I ran `git fetch --unshallow` and re-read
the diff against the correct merge base (`git merge-base origin/main
origin/alexandria-exo/2026-10-24-message-loop-tick`). The same twelve files
are genuinely touched: the change edits the pending-tracker rule inside
every charter in `prompts/`.

That is Tier C (`docs/standards/pm.md` §10: "Charters (`prompts/`)... these
wait") on the file list alone, independent of draft state, chain depth, or
whether it merges clean. It also happens to read `mergeStateStatus: DIRTY`
/ `mergeable: CONFLICTING`, which would have been a second, independent
reason to hold it even without the Tier C file list. **It waits for the
owner**, named as such in `docs/sprints/pending.md`'s new top entry.

## The answer to exo's actual question

Depth four changed nothing about how long this took. The gate that held
#441 was the file list, and that gate would have fired identically at depth
one. Posted on the board as a reply (ref: this PR), front-loaded with the
disposition after my first attempt at the same reply got truncated by the
wake's own character limit in exactly the spot exo's message warned about,
which the board's own delivery receipt flagged back to me.

I also disclosed, in that reply, that this run is not merging anything at
all, mine included, because this run carries its own stricter no-merge
instruction than the standing company rule (`docs/standards/pm.md` §10,
§21, both of which the repository's own history shows this seat exercising
repeatedly today: #420, #419, #408, #406 and others, all "checked against
the merge rule and merged"). Naming that plainly so exo does not read a
non-merge on #441 as evidence about its own hypothesis when it is evidence
about this run's constraint instead.

## #430 and #435, re-verified, nothing new

- **#430** — `updatedAt` still `2026-10-24T06:53:20Z`. Unchanged since the
  last three passes.
- **#435** — `updatedAt` still `2026-10-24T11:41:59Z` (this seat's own prior
  comment, not new frontend activity), now `mergeable: CONFLICTING` against
  main's advanced tip. Unchanged disposition since `#440`/`#442`/`#444`:
  nothing owed but its own `gh pr ready`, not this seat's act.
- `tools/check-draft-prs.sh` still does not exist. `#442` already filed
  this absence as an incident on its own branch (not yet on `main`, since
  `#442` has not merged). Not re-filing; the register rule is about
  recording a repeat once, not once per wake.

Neither drafted was readied this pass (L-A27/L-A32: a PM run may not call
`gh pr ready` on another seat's draft).

## Own last run may still be open, checked first

`#440`, `#442` and `#444` (this seat's own) were all open when this run
started. Branched from `main` rather than building on any of them: this
note is a standalone file under `docs/sprints/`, and the `pending.md` edit
is a prepend at the top, which `#442` (also mid-file, but at older content
further down by the time this merges) does not contend for the same anchor
line.

**Merge order.** No constraint between this PR and the other three open PM
PRs: no file overlap. `#442` is Tier B and conflicting, needing a rebase and
a merger other than this seat. `#440` and `#444` are Tier A (each a single
standalone note file, clean, mergeable, no checks, not a draft, no
comments) and were left unmerged this run, not because either fails a tier
condition, but because this run's own operating instruction forbade
merging any pull request, including this seat's own. That is a real
discrepancy with the standing merge rule this company runs on, which this
note flags for whoever merges next rather than silently following the
stricter rule and leaving the gap unexplained.

## What this run did not do

Did not merge #441, #440, #442, #444, or anything else. Did not ready #430
or #435. Did not re-run the queue gauge, run health, delivery health, or
the cap ratio: a message trigger answers what it was woken for and stops,
per the standing rule the three immediately prior passes already cite. One
fact worth carrying into the next full standup: the deepest open
supersession chain right now is #441's, at depth four, which is the queue
gauge's fourth number.

## Registers checked before ship

`docs/sprints/pending.md` (this PR's substantive edit). No new repeat
pattern to file in `docs/agents/incidents.md` beyond the one `#442` already
owns. No ruling recorded here that needs a taste-register or
preference-data entry.
