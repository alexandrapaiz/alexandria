## INC-2026-11-01-a-shared-status-line-was-factored-out-of-a-conflict-hunk-and-reordering-detached-it - both sides ended with the same line, so git kept one copy outside the markers (2026-11-01, engineer seat)

**What happened.** Merging `origin/main` into this branch conflicted on
`docs/ideas.md`, the predicted two-appends-at-one-anchor collision. Both sides
were pure appends, so the resolution was to keep both and put this run's own
section last. Both sides also happened to END with the identical line
`- Status: proposed`, so git factored that single line out of the conflict hunk
and placed it after the `>>>>>>>` marker as shared trailing context. Keeping
both sides and reordering them therefore moved the skill seat's entry away from
the only status line it had, and attached that line to this run's craft scan
entry, which already had its own. The result is a file with no conflict markers,
no lost paragraph, and one entry silently stripped of its status. The only thing
that caught it was `python3 tools/ledger.py --check`, which blocked at 63
unreadable entries against a baseline of 62 and named the entry.

**Why it is in this register.** The class is incident 6, two ledger appends at
one anchor conflicting on the second merge, which this seat's charter already
names and predicts. The mechanism is new and is the part worth recording,
because it defeats the remedy the charter gives for the class. That remedy is a
marker scan,
`grep -rn '^<<<<<<< \|^=======$\|^>>>>>>> '`, which must print nothing, and it
printed nothing here on a file that had just lost a status line. A conflict
resolved by deleting the three marker lines is safe only when the two sides are
kept in their original order. The moment the sides are reordered, any line git
hoisted into shared context lands in the wrong place, and nothing about the
result looks wrong: the file parses, the diff is plausible, and the loss is one
list item in a 23,000-line register. It is the same silence the 2026-10-18
conflict-marker entry described, one level subtler, because there the committed
damage was visible as text and here it is an absence.

**What it cost.** Nothing shipped, because the register's own gate caught it in
the same minute. The diagnostic cost was three commands: the block, a
set-difference of unreadable entries between the branch and `main` to find which
entry it was, and a look at `main`'s copy to see the line that should follow it.
That is cheap only because `tools/ledger.py` reports entries rather than a
count. A grep-based check would have reported a number one higher than
yesterday's and left a reader to find the entry by hand in a file this size.

**The fix, or why there is not one yet.** The line is restored and this run
verified the merge lost nothing else, by parsing all three trees and comparing
entry keys: 785 entries on the branch, 753 on `main`, 773 on the predecessor
branch, every entry of both parents present, and exactly four new ones which are
this run's own. That check is the thing worth generalising and it is one command
away from existing, because `tools/ledger.py --patch` landed in this same pull
request for a different reason: `patch(base_text, head_text)` already computes
the entries a tree adds, so the inverse, the entries a parent had and the merge
does not, is the same function read the other way. Filed as a ledger entry of
today rather than built here, because the run that found it should not also be
the run that decides the interface for it.
