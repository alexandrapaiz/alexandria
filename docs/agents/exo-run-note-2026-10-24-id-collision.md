# ExO run note, 2026-10-24 (message wake): the PM's hold, cleared

## What woke this run

A note from the PM on the board, addressed to this seat, holding pull request
#463 on one blocking finding. The wake delivered 1465 of its 1614 characters
and cut the tail, which is where the sender's disposition lives, so the first
act of this run was to read the whole message in the inbox rather than to act
on the part that arrived. The PM had independently sent the cut sentence as a
second note, so the inbox held both halves.

That mattered less than it usually does, because the ask was in the delivered
part. It would have mattered a great deal if the ask had been in the tail,
and the ordering is luck rather than design.

## What the PM asked for

One thing. The second new incident entry on #463 reused the first entry's
slug, which `tools/check_registers.py` reports as one blocking finding
against `main`'s baseline of none. The PM posted the exact line and the fix
on the pull request itself and said that a distinct slug plus a green check
clears Tier B on its side.

The PM also said, about the turn-cap table and the failure sweep on the same
pull request, that it had read them, verified them against the diff line for
line, believed them, and would not re-derive a cap number because its charter
reserves that to this seat. That is the correct division and it is the one
this seat's charter names too. Nothing was owed back on either beyond landing
them.

## What this run did

**The fix.** The entry is now
`INC-2026-10-24-the-time-scoped-run-record-we-asked-for-was-already-on-our-own-disk`,
and its body says which id it carried first so that a citation against the
old one can still be traced. `python3 tools/check_registers.py` reports 0
blocking and 71 warnings, which is `main`'s own number on the identical
command.

**The convention was already in the register.** Two entries above, the
seventh and eighth instances of the Tier C misread each carry their own slug
and put the instance count in the descriptive half of the heading. So the
numbering rule did not need extending. The entry had simply been written as
though a slug names an event rather than an entry.

**Seven citations of the old id, one of them wrong.** Six mean the first
instance and are correct untouched. `unowned-duties.md` said "both are
recorded under" the single id, which was true while the two entries shared a
slug, so it now names both.

**One finding that was not on the list.** Every seat reaches GitHub as the
owner's own user, so the PM's hold comment and this seat's close comment on
the same pull request are both attributed to her. §10 condition 2 of the PM
standard asks a fresh-context merger whether there has been an owner comment
since the last push, and that question has no answer on this surface.
Registered as
`INC-2026-10-24-the-merge-checklist-asks-whose-comment-it-is-and-the-api-cannot-say`,
the handover page's Identity paragraph corrected against it, and relayed to
the centralizer in the same run, delivered whole at 1180 of 1180 characters.

**One correction to this seat's own file.** The relay page claimed the
board store's 420-character block limit was tighter for items than for
message bodies, twenty lines under its own paragraph saying the message store
enforces the same rule. A refused message settled it this run. One rule, both
surfaces.

## Why this is a new pull request rather than a push to the one the PM held

The supersession clause in this seat's charter requires a new branch and one
pull request per run, and it requires the older one to be closed by its own
author once containment is proved. So the proof came first,
`git log --oneline origin/alexandria-exo/2026-10-24-hook ^HEAD` printing
nothing, and then #463 was closed with a comment pointing here.

The property #463 was split off `main` for is preserved. This branch touches
nothing under `prompts/` and nothing under `.github/`, so the PM can merge it
on the same Tier B grounds it already verified.

**The cost of that choice, stated rather than hidden.** The PM verified
sixteen files on #463 and will verify seventeen here, and it has no memory of
the first pass. The honest reading is that the re-verification cost is the
same either way, because a fresh-context merger re-derives from the pull
request whatever its history. What is not the same is that the review queue
now holds one live item instead of one live and one dead.

## What was deliberately not done

**The charter edit this finding asks for.** Every seat should open its own
pull request comments with its seat name, which is the only disambiguator the
org has and which currently exists as one seat's undocumented habit. That is
a `prompts/` edit, it is the owner's tier, and putting it here would convert
a pull request the PM can merge into one that waits for her. It is written
down as the next run's second item instead.

**A new incident entry for the refused message.** The store's rule was
already in this seat's register, so the instinct was to file this as another
instance of recording not enforcing. That reading is wrong on the facts: the
register stated the rule and then stated, twenty lines later, that it did not
apply to the surface this run was composing for. Composing to the rule as
written was not a violation of a correct rule. It was a register error, and
the fix is the correction, not an entry.
