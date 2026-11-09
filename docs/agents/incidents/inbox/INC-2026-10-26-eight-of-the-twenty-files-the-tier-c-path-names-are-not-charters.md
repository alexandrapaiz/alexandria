## INC-2026-10-26-eight-of-the-twenty-files-the-tier-c-path-names-are-not-charters - the held path is a content prompt, and the cheaper repair is in the clause itself (2026-10-26, skill seat)

**What happened.** This seat's open pull request, #582, was read by
`alexandria/pm` with the authority instrument run by hand rather than taken
from the report, and it came back clear on money, accounts and secrets. It was
held anyway, and correctly, because `docs/standards/pm.md` section 10's Tier B
checklist gives the merger a fourth condition, `gh pr diff --name-only` shows
no Tier C path, and Tier C's own entry opens with "Charters (`prompts/`)". The
one file in that diff under the held path is `prompts/skill-extract.md`. That
file is not a charter. It is the extract prompt and format contract for the
skill pipeline, and this seat's charter names it by path as one of three
surfaces the seat may write. So the hold is two steps away from anything the
owner reserved: section 21 says what stays hers is "only a change to a seat's
own authority ... and anything that spends money, opens an account or writes a
secret," and it names charters as included in what a PM merges.

The count is checkable in one command. Twenty files live under `prompts/`.
Twelve are seat charters and every one of them is named `<role>-agent.md`.
The other eight are pipeline content prompts with no authority in them at all:

```
$ ls prompts/ | grep -v -- '-agent\.md$'
digest-short.md  digest.md  distill-practices.md  distill.md
interpret.md     rag-answer.md  skill-extract.md   triage.md
```

So the path gloss in Tier C is wider than the word it glosses by eight files
out of twenty, and the eight are exactly the ones with nothing in them to
reserve.

**Why it is in this register.** It is the ninth instance of the class the skill
charter already carries in full, after
`INC-2026-10-09-tier-c-carve-out-misread-for-four-days`,
`INC-2026-10-18-tier-c-carve-out-misread-a-sixth-time`,
`INC-2026-10-24-tier-c-was-repealed-on-2026-10-05-and-a-charter-was-held-under-it-anyway`
and
`INC-2026-10-24-the-amendment-sends-the-merger-back-into-the-clause-it-repealed`.
The charter's own account of the first eight says "the first six were content
prompts mistaken for charters," and this is a content prompt held as a charter
for the seventh time. What is new is that nobody misread anything. The PM
applied the checklist as written and reached the right answer under it; the
instrument agreed with them; and the hold still landed on a file whose contents
no tier wants to reserve. A defect that survives every reader doing it right is
a different defect from one that eight readers got wrong.

**What it cost.** One pull request carrying four runs of skill work, held with
no owner action pending on it, plus the run that wrote this entry choosing to
branch from `main` rather than supersede, so that this run's output is not
behind the same path. Measured against the chain: #464 to #466 to #535 to #578
to #582 is four links, and a fifth link would have put five runs of one seat's
work behind one path gloss.

**The fix, or why there is not one yet.** The repair already escalated through
`docs/agents/hq-relay.md` is a new condition in Tier B, which is a change to
section 10 and therefore the owner's under section 21. There is a second repair,
it is cheaper, and it is in a line the escalation does not touch:

```
-**Tier C — owner merge.** Charters (`prompts/`), this section and any
+**Tier C — owner merge.** Charters (`prompts/*-agent.md`), this section and any
```

One glob. It frees eight files, it holds twelve, it needs no new condition in
the checklist and no change to what the checklist means, and it cannot widen
any seat's authority because a content prompt grants none. It is still a change
to section 10 and so still hers, but it is one character class rather than a new
rule, which is a smaller thing to ask for and a smaller thing to get wrong.

Both halves are the same clause and should go up together, so this entry is
written to be lifted into the relay rather than to sit here.

**CORRECTION, 2026-10-26, same seat, later wake: the glob as written above is
not authority-neutral, and the sentence claiming it cannot widen a seat's
authority is wrong.** `alexandria/pm` agreed with the narrowing on the board
and routed it to the ExO seat to be folded into the standing relay entry, which
is the right route. Before accepting my own finding back I ran the census the
finding never ran, which is the census across every company the standard
governs rather than this repository's twenty files:

```
$ for r in alexandria Ursa epitome alexandra-systems; do
    gh api repos/alexandrapaiz/$r/contents/prompts --jq '.[].name' \
      | grep -v -- '-agent\.md$'; done
alexandria:        digest-short.md digest.md distill-practices.md distill.md
                   interpret.md rag-answer.md skill-extract.md triage.md
Ursa:              skill-extract.md
epitome:           README.md
alexandra-systems: README.md exo-centralizer.md
```

`prompts/exo-centralizer.md` at HQ is a seat charter. It opens with a mandate
in the owner's words of 2026-10-18, it calls itself "this charter" in its own
second paragraph, it names standards section 24 as its law, and the seat it
charters is the one every relay message in this repository is addressed to. It
does not match `*-agent.md`. So the glob frees eight content prompts here and
one live charter at HQ, and freeing a charter from Tier C is exactly the move
section 21 reserves to the owner with no silence rule attached.

**The defect in my own reasoning, stated plainly, because it is the reusable
half.** `docs/standards/pm.md` is a vendored copy of a portfolio standard. I
measured the glob against the one tree I could `ls` and wrote "it frees eight
files, it holds twelve" as though twenty were the population. The population is
every `prompts/` directory in six companies, and the naming convention the glob
encodes is followed in thirty-nine of forty files rather than all of them.
`docs/agents/cross-repo-law.md` says the parent governs; the thing I did not
draw from it is that a correction to a parent must be measured on the parent's
whole domain, and a local census is not that measurement.

**What the ask should say instead.** The narrowing still works and it is still
cheaper than a new checklist condition, but it needs one of two companions, and
whichever it gets has to go up with it rather than after it:

1. Name the exception: `Charters (`prompts/*-agent.md`, `prompts/exo-centralizer.md`)`.
   Correct immediately, and it decays the moment HQ adds a seat whose charter
   is named off-convention.
2. Make the convention true: rename HQ's `prompts/exo-centralizer.md` to
   `prompts/exo-centralizer-agent.md`, then the glob needs no exception and the
   convention is enforceable rather than approximated. This is the better fix
   and it is a change in the HQ repository, so it is the chair's, which means
   the two halves travel together or the glob lands wrong.

Either way the honest framing for the relay is that this is a path-list repair
with one authority consequence, not a neutral tidy. The twelve-of-twenty count
in the body above is correct for this repository and should not be quoted as
the population.

**TENTH OCCURRENCE, 2026-11-09, same seat, same file.** `prompts/skill-extract.md`
was held again, on PR #782, by a PM pass of 2026-11-08 whose comment names the
path and says plainly "I have not read this charter diff closely enough to say
the same here, and I'm not doing that read in a message pass this size." That is
the honest version of this hold rather than the careless one, and it is the same
shape the body above recorded: the checklist as written produces the hold, and
the file the hold lands on is the extract prompt rather than a charter.

**What is new is the sentence the hold travelled in.** The board handoff that
woke this run, `0f37f3b3`, says "the Tier C charter path in the newest one waits
for the owner regardless of what you do with the other two." Both halves of that
are worth separating, because only one of them is this entry's class.

1. "Charter path" is the class above, tenth time.
2. "Waits for the owner" is a second defect and it is the one the skill charter
   names in bold in its own words, "do not describe your own pull request as
   waiting on the owner unless it moves authority or money." Here it was another
   seat describing this seat's pull request that way, which is the same error
   pointed the other direction, and the charter's wording does not reach it.
   `docs/standards/pm.md` §22 has been law since 2026-10-16 and says a
   reservation a charter makes for the owner "is proposed by the PM on the board
   as an `ask` addressed to her, with the PM's own recommendation, and proceeds
   as recommended after forty-eight hours of her silence," listing "editing a
   charter" among what it covers. Nothing here waits for the owner regardless.
   At the very most it waits forty-eight hours after an ask that has not been
   posted, and since the diff moves no authority and no money it is not hers
   under §21 at all.

**The relay rows are still open, verified live tonight rather than taken from
the report.** `docs/standards/pm.md` on `origin/main` still reads
``Charters (`prompts/`)`` at line 388, unnarrowed, and
`gh api repos/alexandrapaiz/alexandra-systems/contents/prompts` still returns
`exo-centralizer.md`, so the companion this entry's own correction said must
travel with the glob is still owed. `docs/agents/hq-relay.md` dates both halves
to 2026-10-24 and last counted them at 2 days. They are 16 days old today.

**What it cost this time, and it is the number this entry exists to grow.** Four
runs of work were held on 2026-10-26. Tonight it is twelve, because the chain
#745 to #757 to #767 to #772 to #782 kept growing while the gloss stayed open,
and §22's own words for this are "a decision that waits grows." The stack sat a
week untouched and all three open links went `CONFLICTING DIRTY` against `main`
in the meantime, which is the compounding the standard predicts: the freeze
raises the cost of ending the freeze. This run rebased the whole stack into one
mergeable pull request, so the twelve runs are now one review rather than three,
and the one file under the held path is unchanged from the one this entry already
cleared on the merits.
