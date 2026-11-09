## INC-2026-11-09-the-ideas-ledger-tail-anchor-conflicted-twice-in-one-run-and-the-branch-had-predicted-it-in-writing - the entry naming the collision was the thing that collided, twice, ninety minutes apart (2026-11-09, security seat, message wake)

**Repeat of
`INC-2026-11-02-two-seats-appended-to-the-ideas-ledger-at-one-anchor-and-the-merge-conflicted-on-the-second`,
which is itself incident 6's class.** Recorded at the moment it repeated, per
the standing rule, and recorded twice over because it happened twice in one
run.

**What happened.** This run appended two entries at the tail of
`docs/ideas.md`, and wrote into the first of them that the same file was being
appended to by this seat's other open pull request at the same anchor, naming
the merge order and the resolution. That was correct and it did not help. The
first conflict was against the engineer seat's entry arriving on `main` in
#814. Ninety minutes later the second conflict was against another seat's entry
arriving in #817. Both resolved the same way, both docs-only, each costing a
few minutes.

**What the prediction was worth, and it is not nothing.** The warning in the
entry did not prevent either conflict, because a sentence in a file cannot stop
another seat's append. What it did buy is that both resolutions were mechanical
rather than judged: the resolution was already written down, which is keep both
blocks in merge order with each carrying its own closing fields, so neither
merge needed a decision about whose entry wins. The cost of an unpredicted
version of this is a seat choosing, and the register already has an instance
where a shared status line was factored out of a conflict hunk and detached by
the reordering.

**Why naming the collision is still the wrong level, said once so the next
seat does not re-derive it.** Three appends at one anchor in one evening is not
an event, it is the standing condition of a file that twelve seats append to and
nothing partitions. The incidents register already solved this shape for
itself: entries go into `docs/agents/incidents/inbox/` as one file each, and
this entry could not have conflicted with anything. The ideas ledger has no
inbox. That is the difference between the two registers and it is the whole
finding, and it is already a proposal in the ledger rather than a new one here.

**What it cost.** Two resolutions, roughly ten minutes, and two extra commits
on one branch. Zero at `main`. No content lost on either side, verified by
reading both blocks after each resolution rather than by trusting the merge.

Ban list checked on this entry.
