## INC-2026-11-09-a-library-bar-was-measured-in-a-unit-that-does-not-match-the-rules-subject-twice-in-one-day - and the second number was acted on in the same run that produced it (2026-11-09, skill seat)

**What happened.** An earlier 2026-11-09 run of this seat measured two of the
ADR-38 quality bars and published both numbers in one ledger entry. The first,
rule 4's line cap, was correct and is the entry's headline: the rule counts
`wc -l`, every `SKILL.md` writes one paragraph per physical line, so 10 of 10
skills pass the cap and 10 of 10 exceed it once wrapped. The second, carried as a
sub-finding of the same entry, was **0 of 10 skills reach their checklist within
twenty rendered lines**, median 103, worst 182, with the cause named as the YAML
provenance block in all ten. That number was measured from byte zero of the file,
which counts the frontmatter, and the frontmatter is 93 of `agent-containment`'s
101 and 131 of `agent-security-measurement`'s 143. Rule 3's own wording is
"immediately after the opening paragraph", and a document's opening paragraph
begins after the frontmatter. Re-measured this run with
`skills/_validation/checklist_position.py`, same 100-column unit:

    from byte zero, frontmatter counted                 0 of 10 within 20
    from the body, rule 3's first sentence             10 of 10 within 20
    to the end of the checklist, its second sentence    2 of 10 within 20

So the published 0 of 10 belongs to no reading of the rule, and on the reading
that does fail the cause is checklist length rather than the frontmatter.

**Why it is in this register.** Two reasons, and the second is the one that
matters. First, it is the second instance in one day of one class: a bar measured
in a unit that does not match what the bar is about. The first instance is filed
in this inbox as
`INC-2026-11-09-the-length-gate-reports-a-pass-in-a-unit-that-stopped-measuring-when-the-files-changed-shape`,
which diagnoses the class in its own words, "nothing re-validated it against the
artifact after the shape changed", and the rule-3 sub-finding published in the
same ledger entry then commits it. Second,
and this is what makes it an incident rather than an arithmetic slip, **the run
acted on the number inside the same run that produced it**: it moved 1,837 words
of revision history out of `agent-containment` with the 0 of 10 as the stated
reason. A measurement published and acted on in one run never meets a second
reader, which is the same structural hole as a register with one gate.

**What it cost.** No work lost. The move was independently right on grounds that
survive, which are that the history had reached 26 percent of the file and the
site renders none of it, so nothing has to be reverted. What it cost was one
wrong cause in a register entry that is in front of the owner for a charter
ruling, and it would have cost nine more skills' history moves if this run had
taken the number on trust. It did not, which is the only reason the cost stops
here.

**The fix, or why there is not one yet.** The instrument shipped this run:
`skills/_validation/checklist_position.py` reports all three readings and is
wired into no gate, because choosing which one rule 3's bound applies to is a
charter edit and so the owner's. The correction is filed in the ledger inbox as
`2026-11-09-rule-3s-0-of-10-counted-a-block-no-consumer-renders`, pointing at the
entry it corrects rather than replacing it, so the owner reads both. The
generalisable half, and it is cheap: when a run both measures a bar and acts on
the measurement, the acting half states the unit it is acting on. Two of the
three readings here were one line of code apart.
