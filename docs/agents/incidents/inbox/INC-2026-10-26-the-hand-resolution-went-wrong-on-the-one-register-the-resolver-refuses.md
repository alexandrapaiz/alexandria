## INC-2026-10-26-the-hand-resolution-went-wrong-on-the-one-register-the-resolver-refuses - the resolver would have resolved one of the two conflicted registers and refuses the other, and the hand got the refused one wrong (2026-10-26, skill seat, message run)

**What happened.** The PM handed this seat back its own pull request #466 to
clear a conflict against main. Two registers conflicted, `docs/ideas.md` and
`docs/agents/incidents.md`, both the append-at-one-anchor shape. This seat
resolved both by hand and pushed, and only then ran
`python3 tools/resolve_register_conflict.py --check`, which exists for exactly
this job and which reported `docs/agents/incidents.md` two lines over its own
identity, naming both duplicated lines:

    docs/ideas.md: balanced, every line of both sides is present once
    docs/agents/incidents.md: the resolution in HEAD^ does not balance
      duplicated: 3351 of an expected 3350 (base 2987, ours 3017, theirs 3320): <blank line>
      duplicated: 53 of an expected 52 (base 48, ours 48, theirs 52): ---

The cause was a seam this seat wrote by hand: a blank, a `---` and a blank
between the two blocks, where main's half of the conflict already opened with
its own `---` and blank.

Then the run replayed the same merge in a detached worktree and asked the tool
what it would have done, which is the part worth keeping:

    docs/agents/incidents.md: refused, theirs changed something that is not the end of the file, so this is not two appends
    docs/ideas.md: kept both appends, ours first (142 lines) then theirs (1096 lines)

The tool's `docs/ideas.md` is byte-identical to the hand's. So the tool would
have resolved one file and did refuse the other, and the file it refuses is
precisely the file the hand got wrong. The file it accepts, the hand got right
by luck.

Why it refuses is measurable rather than mysterious. `trailing_block()`
requires theirs to be the base plus one block at the end of the file. Main's
diff on `docs/agents/incidents.md` over this branch's merge base is four hunks,
at lines 18611, 18969, 19386 and 19452, and every one of them is a pure
insertion with no deletions. Three of the four are mid-file, because seats
insert an entry next to the entry it relates to. So the precondition fails on
additions that could not possibly conflict, on the register with the most
append traffic in the repository, and it fails for the second merge running:
#466's own body records the same refusal on the same file two days earlier.

**Why it is in this register.** The standing rule. The class is an instrument
that exists in `tools/` and was not opened before the hand went in, which is
incident 20's shape and L-A9's, and the nearest named instance is
`INC-2026-10-24-the-time-scoped-run-record-we-asked-for-was-already-on-our-own-disk`.
The sharper repeat is inside one branch and one seat: on 2026-10-24 this seat
ran `--dry-run` first, got the refusal, resolved by hand, and audited with
`--check` afterward, and wrote all three steps into #466's description. Two days
later the same seat on the same branch skipped the first step. What the 10-24
refusal taught was "this file needs a hand" rather than "ask first, every
time", and the second lesson is the one that was load-bearing.
`INC-2026-10-24-a-hand-resolved-register-append-deleted-another-seats-line-with-no-marker`
is the deletion direction of the same arithmetic; this is the duplication
direction, which the tool's own docstring already names as what `merge=union`
does and the measured reason L-A49 forbids that attribute.

**What it cost.** Two lines in one pushed commit, caught inside the run, three
turns to find and amend. Nothing reached main. The honest accounting is that
the cost was small because the counter existed, and the counter is the only
reason anybody would ever know: a duplicated separator leaves valid Markdown
and no marker, so the next merge of that file would carry it in silently, which
is the shape of
`INC-2026-10-18-this-seats-own-run-committed-conflict-markers-into-the-incident-register`.

**The fix, or why there is not one yet.** Two halves, and this seat can only do
the first.

1. Done here. Run `python3 tools/resolve_register_conflict.py --dry-run` before
   touching a conflicted register by hand, and `--check` on the merge commit
   after, and treat a refusal as the instruction to hand-resolve that one file
   rather than as permission to hand-resolve the rest.
2. Filed, not built. `trailing_block()` should accept a theirs whose changes are
   all insertions that do not touch the conflicted region, because the audit
   the tool already carries is what proves the result rather than the
   precondition. `tools/` is not this seat's write surface, so it is a ledger
   proposal in `docs/ideas.md` dated 2026-10-26 rather than a patch here. Until
   it lands, the highest-traffic register in the repository is hand-resolved
   every time, by a seat the refusal has just told to stop asking.
