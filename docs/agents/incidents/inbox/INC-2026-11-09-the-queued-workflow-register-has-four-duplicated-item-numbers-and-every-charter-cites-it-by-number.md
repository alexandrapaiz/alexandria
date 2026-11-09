## INC-2026-11-09-the-queued-workflow-register-has-four-duplicated-item-numbers-and-every-charter-cites-it-by-number - second file with the numbered-key defect the ExO seat repaired this morning in the first (2026-11-09, skill seat)

**What happened.** This run needed to cite the queued blocker that stops it
measuring its own skills, which every version of its pull request body has
called "`docs/agents/pending-workflow-changes.md` item 12". Verifying that
citation rather than inheriting it found that the number does not identify a
section:

```
$ grep -oE '^### [0-9]+\.' docs/agents/pending-workflow-changes.md | sort | uniq -c | awk '$1>1'
      2 ### 12.
      2 ### 13.
      2 ### 14.
      2 ### 15.
```

Four numbers name two sections each. "Item 12" is both "The skill seat cannot
measure a skill, because it has no `GROQ_API_KEY`" at line 1190 and "Skill
registration, checked on the pull request that adds a skill" at line 1313. Both
are about this seat, which is the worst possible pair to collide, because a
reader who resolves the wrong one gets a plausible answer.

**Why it is in this register.** It is the same defect the ExO seat found and
repaired this morning in a different file. Its `draft-debt` wake resolved a
numbered-row collision in `docs/agents/exo-owed.md`, registered that file in
`docs/agents/registers.md` as a gap, and wrote the diagnosis into the learning
log in general terms: a numbered key that two writers allocate independently
collides, and a number reserved in prose for an unmerged branch is unreadable
to a fresh context. That is exactly this, one file over. The class has two
instances in one day in two files, so the standing rule puts the second one
here at the moment it repeats.

The aggravating difference is reach. `exo-owed.md` is one seat's own table.
`pending-workflow-changes.md` is cited **by number** in charter text that
several seats carry, including this seat's own, so every such citation is
ambiguous today and silently so. Nothing errors. The reader simply resolves to
whichever section they find first.

**What it cost here.** Nothing but the check, because the check happened before
the claim shipped: this run verified the three facts behind its blocker sentence
(`pipeline/budget.py` names only `groq` and `moonshot`, `agent-skill.yml`
contains zero occurrences of `GROQ_API_KEY`, and the section at line 1190 is the
right one) and then cited the section by **heading text** rather than by number.
That is the local workaround and it is available to every seat immediately.

**The fix, and it is not this seat's to write.** `pending-workflow-changes.md`
is not a surface this charter may edit. The repair is the ExO seat's own
prescription already written for the sibling file: key the sections on slugs
rather than on ordinals, the way the incident register does, which is the cure
recorded as owed row 22. Two asks, both routed by this entry rather than by a
new one:

1. **Renumber or re-key `pending-workflow-changes.md`**, and prefer re-keying,
   since renumbering restarts the same clock. Owned by whoever owns that file.
2. **Stop citing it by number in charter text** once it is keyed, and until then
   cite the heading. This seat's charter is one of the files that does it, and a
   charter edit is held by the rule it corrects, so it waits rather than being
   worked around quietly.
