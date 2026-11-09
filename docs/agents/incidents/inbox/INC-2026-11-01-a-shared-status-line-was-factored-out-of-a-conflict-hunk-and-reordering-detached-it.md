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

**SECOND OCCURRENCE, 2026-11-09, skill seat, and the mechanism fired exactly as
described.** Merging `origin/main` into this seat's four-run stack conflicted on
`docs/ideas.md` and on nothing else, 1 file of 93. Both sides were pure appends,
both sides ended with the identical line `- Status: proposed`, and git hoisted
that single line out of the hunk into shared trailing context after the
`>>>>>>>` marker, exactly as this entry predicted. The resolution reorders the
sides, main's entries first and this stack's eight passes after them, so it is
precisely the case this entry says is unsafe.

**What this entry bought.** The trap was seen before it was sprung rather than
after. The tell is countable without reading any prose: each side carried one
more `### ` heading than it carried `- Status:` lines, 30 against 29 on this
stack's side and 20 against 19 on main's, which is the signature of a status
line hoisted out of both. So both sides got their own `- Status: proposed` back
and the shared one was left to close the side that now sits last. No line was
moved between entries.

**And the generalised check this entry asked for was run here, by hand, for the
first time.** This entry's closing section says the inverse of
`tools/ledger.py --patch` is "one command away from existing" and filed the
interface decision rather than building it. Run as a script over all three trees,
comparing `(date, name)` keys:

```
entries: main=871  predecessor=870  merge=904
main entries missing from the merge        : 0
predecessor entries missing from the merge : 0
merge entries in neither parent (new)      : 0
union of both parents = 904, merge = 904, equal: True
```

That last line is the assertion worth having, and it is stronger than the count
the marker grep and the unreadable ratchet can give between them. A merge of two
pure-append branches must produce exactly the union of its parents' entries, so
one equality catches a dropped entry, a dropped status line, a duplicated entry
and a reordering that detaches a field, without a baseline to maintain and
without anybody choosing a threshold.

**And `tools/ledger.py --check` would have caught this one too, which is worth
saying because the first draft of this occurrence claimed otherwise and the claim
was tested rather than argued.** The naive mis-resolution was reconstructed and
parsed: it reads **63** unreadable entries against the shipped resolution's 62,
and `BASELINE = 62` in `tools/ledger.py`, so `--check` blocks at one over. That
is the same 62 to 63 the 2026-11-01 instance above was caught by, on the same
gate, to the same numbers. The gate works and it worked twice.

So the union equality is not a replacement for it, and the honest case for it is
narrower. It needs no maintained baseline, which matters because this register's
other ratchet is red on `main` tonight for exactly the reason a baseline drifts
(`INC-2026-11-09-the-ledger-ratchet-is-red-on-main-again-and-its-register-is-the-most-contested-path-with-no-inbox`).
And it localises: `--check` reports a count one higher than yesterday's and names
the entry that lost its status, while the equality names which parent lost what,
which is the question a merging seat actually has. The cheapest tell of all is
neither, and it is the arithmetic above: a side carrying one more `### ` heading
than `- Status:` lines has had a line hoisted, and that is countable before the
file is parsed at all.

Proposed in this pull request as a ledger entry, `--parents`, because this run
found it and should not also be the run that fixes the interface, which is this
entry's own rule.
