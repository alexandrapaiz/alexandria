## INC-2026-10-26-the-gate-that-asks-whether-a-surface-was-drafted-for-passes-a-candidate-with-no-row - the second writer gate in two days whose pass was vacuous for the case it was built for (2026-10-26, writer seat)

**What happened.** `docs/voice/awaiting-her-word.md` is the register that answers
"has this surface already been written for", and
`docs/voice/check_voice.py candidates` is the command that enforces it. It
compared a run's new candidate files against the register's open rows and failed
where a surface was already held by a different candidate. A candidate for a
surface the register had never held matched nothing, so it registered nothing and
passed, and the pass printed "no candidate here redrafts a surface already
awaiting her word", which reads the same as it reads for a run that did the
bookkeeping right.

Run 57 is the instance, nine hours old when this was filed. It ruled on the live
`2026-W42` issue page, wrote the exact words in
`docs/voice/w42-correction-2026-10-26.md`, raised one line that needs the
owner's word, and merged to `main` in #600 with no row in the register and no
question row either. Re-run against that branch, the widened command fails it:

```
python3 -I docs/voice/check_voice.py candidates 9c8c5973^1
  FAIL    docs/voice/w42-correction-2026-10-26.md
            no row in awaiting-her-word.md names it, and it names 3 live surface(s)
```

The same run's two other failures are on its review file, for citing two
surfaces that do hold open rows. Those were correct and unrecorded: run 57's
review reports `selfcheck` and never ran `candidates`, so the gate was red on
the branch that merged.

**Why it is in this register.** The shape repeats and the count is three. Run 56,
the day before, found that `routed` could only see SCREAMING_CASE identifiers,
so it had never once caught a re-filed finding and printed a reassuring line
anyway. Run 57 found that the claims pass had six questions and not one of them
opened a paper
(`INC-2026-10-26-the-overturn-section-was-graded-six-ways-and-never-against-a-paper`).
Incident 20 is the general case: recording is not enforcing, and every register
needs a gate that writes and a gate that checks. This is the third instance in
three consecutive runs of a narrower claim, which is the one worth carrying: a
gate whose scope was drawn from the defect that produced it, and which is
therefore silent on the first instance of the class it was built for. `routed`
was built from an identifier, so it could not read a law. `candidates` was built
from two candidates colliding on one surface, so it could not read a candidate
standing alone. Both printed green.

A fourth thing makes it worse here than in run 56's case. The regex that reads a
surface out of a candidate was widened on an earlier run precisely so an issue
page would be visible to this gate, and the comment above it says the cost of
not seeing one. That widening fixed what the gate could see and left untouched
what it would say about what it saw.

**What it cost.** Nine hours in which the newest copy candidate this seat holds
existed in no index, with the live page it corrects still serving three
statements measured wrong three for three, and with one line waiting on the
owner under the company standard's forty-eight hour silence rule and no row
anywhere for a later run to re-confirm it from. One merged pull request, #600,
carried a red gate of this seat's own. The register's own stated purpose is that
a row nobody has touched does not quietly expire. An unwritten row expires on
the day it is written.

**The fix.** A floor under the clash test, in this run's diff. A candidate file
that names a live `site/` surface and that no row in the register names back now
fails, cleared by one row. Its scope is pinned in `FLOOR_CASES`, which runs
before any diff is read: candidate directories in, `reviews/` and
`preferences/` out, because a review cites surfaces as evidence and failing a
grade for quoting the line it grades would make the gate unusable by the work it
governs. The first version asked for a row per surface and reported three
failures for the one candidate, since that file also cites the `2026-W39` page
it learned from and the module the correction serves through, so the floor asks
for one row per candidate instead. The two missing rows are written.

One limit stays and is not papered over. The floor reads a candidate's surface
out of the candidate's own prose, so a candidate that names no surface is still
invisible to it. `docs/voice/corrections/2026-W42-corrected.md` is that case: it
is the corrected body itself and names nothing. It is indexed only because the
row for its parent candidate names it by filename.
