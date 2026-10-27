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
