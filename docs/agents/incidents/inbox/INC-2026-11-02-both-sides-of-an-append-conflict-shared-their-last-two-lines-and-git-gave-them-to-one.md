## INC-2026-11-02-both-sides-of-an-append-conflict-shared-their-last-two-lines-and-git-gave-them-to-one - keeping both blocks of an append conflict silently stripped the status line off the one that stopped being last (2026-11-02, research seat, message wake)

**What happened.** Two of this seat's sibling pull requests merged while this run
was working, so `main` moved and `docs/ideas.md` conflicted. The conflict is the
ordinary one for this file: both sides appended an entry at the end, which is
incident 6's shape. The resolution is equally ordinary, keep both blocks, and
this run did that.

What it did not expect is that both blocks ended with the same two lines:

```
- Cost: $0.
- Status: proposed
```

Because those two lines are identical on both sides, git does not put them inside
the conflict region. It factors them out and leaves them *after* the
`>>>>>>>` marker, as context belonging to neither side. So a resolution that
takes the text between the markers, concatenates the two blocks in either order,
and leaves the rest of the file alone produces a file where **one shared status
pair serves whichever block ends up last, and the other block has none.** In this
case the trunk's own entry, four lines of someone else's work, silently lost its
status and its cost and became invisible to every status filter in the
repository.

**Caught by a gate, and the margin was one.** `tools/check_registers.py` went
blocking with "63 entries carry no readable status, up from the recorded 62",
which is the ledger's `BASELINE` doing exactly its job. Without that counter the
resolution reads clean: no conflict marker anywhere, both entries present, both
headings intact, the file renders, and the damage is two missing list items in a
22,000-line file. `python3 tools/ledger.py --census` then named the line.

**Why it is in this register.** The append-at-one-anchor class is incident 6 and
has recurred through incident 14, the 2026-10-18 conflict-marker entry, and
`INC-2026-11-02-the-grep-remedy-for-duplicate-reads-cannot-see-a-strike-that-lives-on-a-branch`,
whose own hunk 3 was this shape in the reading queue. The standing rule binds. The
mechanism here is new and worth separating: every earlier instance was found by a
conflict marker or by reading the two blocks, and both of those succeed here. The
marker was in the right place and both blocks were kept. **The loss is in the
lines git decided were not in dispute**, which is the one part of a conflict a
resolver does not look at, because git is telling it there is nothing to decide.

It also generalises past this file. Any register whose entries end in a fixed
footer is exposed: a status line, a cost line, a `Ban list checked on this entry.`
line, a trailing horizontal rule. The more rigidly a file's entries end the same
way, the more of each entry git will factor out of the conflict, and the larger
the silent loss.

**What it cost.** One turn to find and one line to fix, because the gate fired in
the same minute. Had it shipped, the trunk's entry would have been unreadable to
`tools/ledger.py --status`, which is how the PM and the owner read proposals, and
the next seat to append would have inherited a baseline that had absorbed it.

**The fix.** Restored in this pull request: the pair is written back onto the
trunk's entry and this run's own entry keeps the shared one, so both are readable
and `check_registers.py` is 0 blocking with the unreadable count back at the
recorded 62.

The convention this argues for costs one command and is already written for other
reasons. After resolving an append conflict in a register, **run that register's
own reader and compare its counts against the trunk's**, rather than grepping for
markers:

```bash
python3 tools/ledger.py --census          # docs/ideas.md
python3 tools/incidents.py check          # the incident register
python3 pipeline/reading_queue.py         # docs/research/reading-queue.md
```

A marker grep answers "did I leave debris". Only the reader answers "does every
entry still have the fields that make it visible", and this class is invisible to
the first question.

Ban list checked on this entry.
