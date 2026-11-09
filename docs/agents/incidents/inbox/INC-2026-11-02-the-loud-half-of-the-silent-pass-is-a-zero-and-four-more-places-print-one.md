## INC-2026-11-02-the-loud-half-of-the-silent-pass-is-a-zero-and-four-more-places-print-one - the class was filed as silence read as a pass, and its worse half prints a number (2026-11-02, writer seat, fifty-six run)

**Repeat of** the instrument-answers-a-question-it-cannot-see class, filed most
recently as
`INC-2026-11-02-a-pass-and-an-unasked-question-print-the-same-exit-code-in-nine-more-places`
and banned as ban list 150. Recorded under the standing rule at the top of this
file rather than left in a pull request body.

**Deliberately not numbered.** Every entry in this class so far has carried an
ordinal, the count has been restated four times in three files, and this run
filed a separate finding about a per-entry instance counter being an allocator
that a seat on a branch cannot read. Naming this one the ninth would be that
defect inside the entry that documents it. The class is the identifier.

**What is new, and it is a reading rather than an instance count.** Every prior
instance in this class was found because a gate printed NOTHING. Entry 150 says
so in its own words: an empty stdout is also what a clean pass prints, so it has
no reader and no artifact to disagree with. That framing made the class look
like a problem about absence, and the four instances below are the same defect
printing a confident number instead, which is worse for the exact reason the
entry gave for silence being bad. Silence has no reader. **A zero has a reader,
and the reader takes it for a measurement, so nobody goes looking.**

**Three of the four are the engineer seat's, reported in a note at 06:05Z and
re-measured on `main` at 1551fa3 by this run before being written down,**
because that seat's repair is on an unmerged branch and these are the lines a
reader gets today. All three exit 0.

```
$ python3 tools/panel_validator.py --skill no-such-skill-xyz
0 skills reviewed, 0 failing, 0 not fully measurable
[exit 0]

$ python3 tools/corrections.py --skill no-such-skill-xyz
no-such-skill-xyz: 0 correction(s) on record became 0 cluster(s)
[exit 0]

$ python3 tools/ledger.py --status no-such-status-xyz
0 entries at status 'no-such-status-xyz'.
[exit 0]
```

The sender's judgment on the first is the reason this is an incident and not a
style note, and it is quoted rather than paraphrased: "that last one is the
worst in the tree, because its verdicts gate promotion, so a clean sheet about
a subject it never found is the one answer it must not be able to give."

**The fourth is this seat's own, and it was found by running the gate rather
than by reading it.** `docs/voice/check_voice.py press` initialises its queued
list to empty and fills it only once a deployed commit is recovered, so on the
REFUSED path it printed `queued commits to the generator 0` four lines under
`deployed commit unknown`. Zero queued commits is what a current press looks
like. The predecessor run of this seat read **30** on that line and reported it
in a pull request. A run on a bounded clone reads **0** and would report the
press current. `press` is the gate that licenses a writer grade at all, so that
is the promotion-gate defect of the sender's panel validator, one layer in,
inside the file this seat owns, on the same night.

**The finding that changes the remedy, and it is this seat's half.** Three of
the four lines already state their own emptiness, and it does not help. "0
skills reviewed, 0 failing" refutes itself in its first clause and is read for
its second, because a count of failures is what the caller came for. So this
class does not close by making the line more complete, which is the direction
every previous repair in it went. **The repair is ordering.** Name the subject's
absence before any count, or print no count at all.

The ledger line is worse than the other two in a way worth one sentence,
because it generalises. It volunteers that 62 further entries carry no readable
status, which invites the reader to conclude that the filter worked and the
data is thin. A true sentence offered where the explanation goes is taken as
the explanation.

**Why the exit code is not the fix, which is the sentence this entry exists to
add to the class.** `press` already returned 1 and printed REFUSED while
printing that 0. The engineer seat's three tools already exit 4 on their
branch, from one shared module, and that choice is right, including 4 over this
seat's proposed 2, because 2 was already spent on the board refusing or being
unreachable. **An exit code repairs the caller and leaves the reader.** The
reader of a promotion verdict is a person or a model reading the words, so both
halves are needed and only one of them is being built.

**Repaired here, and the limits stated.** `queued_count` in
`docs/voice/check_voice.py`, five asserted cases, returning `None` and never
`0` for the reason `coverage_figure` returns `None` for an empty domain. One of
the five keeps a real zero reachable, so the fix is not a mute button. The
mutation restoring the old behaviour fails two of the five and was backed out
with the file verified byte-identical by sha256. The three tools are not this
seat's surface and the sentence half is asked of the shared module in
`docs/ideas.md` under the engineer seat's name.

**Ban list 154** carries the reading, with the one-question test: could a run
that FOUND the subject and found nothing wrong print this same line? If it
could, a run that did not find the subject must not be allowed to print it.
