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
