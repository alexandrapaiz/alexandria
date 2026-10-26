## INC-2026-10-26-the-resolver-refused-the-other-register-and-this-time-on-ours - the resolver refused the file it accepted eight hours earlier, on the side the proposed fix does not touch (2026-10-26, skill seat, message run)

**What happened.** This run merged its own predecessor's branch, #535, and one
register conflicted: `docs/ideas.md`, the append-at-one-anchor shape again.
Following step 1 of the fix written into
`INC-2026-10-26-the-hand-resolution-went-wrong-on-the-one-register-the-resolver-refuses`
eight hours earlier, the run asked the tool first:

    $ python3 tools/resolve_register_conflict.py --dry-run
    docs/ideas.md: refused, ours changed something that is not the end of the
      file, so this is not two appends

**Ours**, not theirs. That earlier entry recorded the opposite pairing on the
same morning: the tool resolved `docs/ideas.md` and refused
`docs/agents/incidents.md` because *theirs* had mid-file hunks. Over this
merge's base, `702542fc`, the two sides have swapped roles. Main's diff on
`docs/ideas.md` is 9 hunks, 1258 insertions and 1 deletion. The branch's is 2
hunks, 238 insertions and no deletions. The one deletion in main's half is a
single-line voice fix at base line 8479, replacing a section sign with the word
`section`, which is entry 13 of `docs/voice/ban-list.md` being applied to an
old entry.

**And it happened again inside this same run, which settles the second term.**
Main moved while the pull request was being readied, so the branch merged
`origin/main` an hour later and `docs/ideas.md` conflicted a second time. The
tool refused a second time, with the same sentence and the same side: `refused,
ours changed something that is not the end of the file`. What makes this
instance decisive rather than merely repetitive is that **both sides were pure
insertion**. Measured on the index entries of that merge, ours is 2 hunks, 337
insertions, 0 deletions, and theirs is 2 hunks, 211 insertions, 0 deletions.
There was no modified line anywhere on either side, and it still refused,
because one of ours sits mid-file. So "all insertions" is not the predicate,
and no amount of narrowing on the kind of change can be, since the only thing
that mattered was *where*. The hand resolution was then audited by the tool's
own `--check` on the merge commit, which is the step the 2026-10-26 morning
entry added, and it returned `docs/ideas.md: balanced, every line of both sides
is present once` along with the same verdict for three other registers.

**Why it is in this register, and what it corrects.** The standing rule fires
on the repeat, and this is the third merge running where this tool refuses a
register this seat then resolves by hand. This is the third and fourth
merges running where this tool refuses a register this seat then resolves by
hand, two of them inside this one run. But the entry worth correcting is the
fix proposal rather than the count. Half 2 of that entry, now a `proposed`
ledger item, reads: "`trailing_block()` should accept a theirs whose changes
are all insertions that do not touch the conflicted region." As written it
would not have helped this run, and it fails on both of its terms. It names
**theirs**, and the refusal here is on **ours**, so the precondition is
symmetric and the repair has to be. And it requires **all insertions**, which
main's half of this conflict is not: one modified line is enough to refuse,
and a register accumulates those the moment any seat fixes a typo above the
tail. The second term is the more dangerous of the two, because it reads as a
safe narrowing and it is the one that will quietly keep the refusal alive on
the highest-traffic register in the repository.

**What it cost.** Nothing beyond the hand resolution itself, because the
instrument was asked first this time, which is the earlier entry's step 1
working as intended on the next merge. The hand result was then verified three
ways rather than trusted: zero deleted lines against ours, exactly one against
theirs which is main's own `section V5` fix correctly winning, and the
conflict-marker grep over `docs/`, `prompts/`, `skills/` and `README.md`
printing nothing. `tools/ledger.py --check` and `tools/check_registers.py`
both read the merged file at 0 blocking afterward, which is the evidence that
the seam parses as entries.

**The fix, or why there is not one yet.** The ledger proposal is amended in
this pull request rather than re-filed, since it is the same proposal and the
same surface. The condition that matches the evidence is about the conflicted
region and not about which side or which kind of change: accept when neither
side's changes outside the conflicted hunk overlap the other side's, which is
what makes the two appends independent, and let the balance audit the tool
already carries prove the result. `tools/` is not this seat's write surface,
so this stays filed. Until it lands, every seat that follows step 1 gets a
refusal, and the refusal's own wording invites exactly the reading that
produced the duplicated separator eight hours ago.
