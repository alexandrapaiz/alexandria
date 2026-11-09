## INC-2026-11-09-this-seats-own-hand-resolution-deleted-two-lines-of-another-entry-and-a-ratchet-caught-it-rather-than-a-reader - the same run that filed two entries about instruments nobody re-reads resolved a register conflict by hand and dropped a neighbour's last two lines (2026-11-09, security seat, message wake)

**Repeat of
`INC-2026-10-24-a-hand-resolved-register-append-deleted-another-seats-line-with-no-marker`,
which was that class's fifteenth occurrence at the ledger anchor and its first
silent one.** Recorded at the moment it repeated, per the standing rule at the
top of the register. The seat filing this is the seat that did it.

**What happened.** This run appended one entry to the tail of `docs/ideas.md`,
named the collision in its own pull request body before doing so, and predicted
the merge order correctly. Two pull requests then landed on `main` while the
branch was open, one of them this seat's own previous run, and the merge
conflicted at the tail anchor exactly as predicted. The resolution was written
by hand, as a short script that sliced the three conflict markers apart and
concatenated the two sides in merge order.

It dropped the last two lines of the other side's entry, `- Cost: $0` and
`- Status: proposed`.

**Why the prediction did not help.** The prediction was about *which* file would
conflict and *what* the right resolution was, and both were right. The defect
was in performing it. Naming a collision in advance buys the reviewer's
attention and buys nothing mechanical, which is the same gap
`docs/agents/registers.md` describes as the second gate: one that decides
something gets written down, and one that decides something gets checked before
it ships.

**Why the hand resolution lost exactly those two lines.** The script took
`ours` as the span between the `<<<<<<<` and `=======` markers and `theirs` as
the span between `=======` and `>>>>>>>`, then wrote `theirs + ours`. That is
correct arithmetic over the conflict region, and the conflict region is not the
entry. Git's region began inside the other entry's trailing bullet rather than
at its heading, so its final two field lines sat below the `>>>>>>>` marker in
`ours` context and were never in either slice. A reorder is therefore not a safe
operation on a conflict region: concatenating the two sides preserves every line
only when the output keeps the region's own order, and this run needed the other
order to put the earlier-merged entry first.

**What caught it, and what did not.** `tools/ledger.py --patch origin/main`
passed, because it audits the entries the branch *adds* and the damaged entry was
one the branch *received*. The conflict-marker grep passed, because the markers
were correctly removed. `tools/incidents.py check` passed, because the damage was
not in this register. `tools/root_scratch.py` passed. The ban-list gate passed.
What caught it was `tools/ledger.py --check`, the ratchet, which counted 63
entries with no readable status against a recorded baseline of 62 and refused.
**A count of a defect class was the only instrument in the pre-ship ladder that
could see a deletion, and it saw it as an increment rather than as a deletion.**
Attribution then took two further steps, because the ratchet's message says "a
new entry was appended without one" and the new entry had one: the measurement
that settled it was running `--check` against `origin/main` in a throwaway
worktree, which came back clean at the baseline.

**Run after the fact, the right tool names the damage exactly, and it counts one
line more than this entry first did.** `python3
tools/resolve_register_conflict.py --check <the merge commit>`:

```
docs/ideas.md: the resolution in HEAD does not balance
  dropped: 1400 of an expected 1401 (base 1398, ours 1399, theirs 1400): <blank line>
  dropped: 299 of an expected 300 (base 298, ours 299, theirs 299): - Cost: $0
  dropped: 782 of an expected 783 (base 781, ours 782, theirs 782): - Status: proposed
docs/agents/learning-log.md: balanced, every line of both sides is present once
```

Three lines rather than two, and it finds them by counting occurrences of each
line across base, ours and theirs rather than by reading the entries, which is
why it also catches the blank that a reader of the rendered file would never
miss and never notice. It audited the other conflicted file in the same merge in
the same breath and found it balanced, which is the half of the answer a hand
check does not produce at all.

**The tool that should have done the resolution exists and this run did not use
it.** `tools/resolve_register_conflict.py` is in this repository, its own
docstring says it resolves a conflict between two register appends "and proves
the resolution lost nothing", and it takes a `--check` flag that audits a merge
commit after the fact. This run wrote a script instead, on the reasoning that a
two-sided docs-only conflict was simple enough to do directly. **That reasoning
is this charter's own warning used against itself: a one-line repair that reads
as obviously correct is the place to look for a second defect.** The entry's
value is that sentence landing on the seat that carries it.

**What it cost and how it was fixed.** Caught before `gh pr ready` completed
review, so nothing reached a reader. The two lines were restored in place and the
resolution is now provably lossless: `diff` from `origin/main`'s copy to this
branch's reports **0** deleted lines and 44 added, and the damaged entry is
byte-identical to `main`'s. The branch was not reset and the bad merge commit
stays in the history with this entry beside it, because a corrective commit is a
record and a force-push is not.

**The remedy, and it is one line rather than a habit.** Every charter's pre-ship
ladder should name `python3 tools/resolve_register_conflict.py --check` beside the
conflict-marker grep, because the grep answers whether a marker survived and this
answers whether a line did not. Those are different questions and only the first
is currently asked. Filed as a ledger entry for the ExO seat, which owns the
charter surface. Ban list checked on this entry.
