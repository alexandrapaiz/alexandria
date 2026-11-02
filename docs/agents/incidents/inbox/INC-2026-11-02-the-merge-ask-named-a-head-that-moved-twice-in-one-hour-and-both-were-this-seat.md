## INC-2026-11-02-the-merge-ask-named-a-head-that-moved-twice-in-one-hour-and-both-were-this-seat - the rule requiring a head commit has no rule about when to take the reading (2026-11-02, exo seat)

**What happened.** Twice within sixty-five minutes, a run of this seat sent the
PM a merge ask naming a head commit, committed again, and then sent a
correction naming the new head.

- The run before this one: ask `7341c5e4` at 00:48:02Z naming head
  `91c24be8`, correction `ad7c0380` at 00:48:36Z naming `2ba32cd1`.
- This run: ask `9d9c718c` at about 01:14Z naming head `9d06b401`, correction
  `d0f9ebde` at about 01:19Z naming `e1760c64`.

Both corrections were sent voluntarily and both were correct. Neither ask was
wrong when it was taken. **The repeat is the point**, and the standing rule at
the top of the register is that an issue occurring more than once is recorded
at the moment it repeats, with no exceptions.

**Why it happened technically.** The governing rule is
`INC-2026-10-26-three-disposition-verdicts-on-one-pull-request-in-twenty-two-minutes-and-none-named-the-head-commit`,
written into this charter as *"any claim about a pull request's state carries
the head commit it was measured on and the time of the reading."* That rule is
about the **content** of a claim. It says nothing about **when in a run the
claim may be made**, and both instances obeyed it to the letter: each ask
carried a head and a clock, and each was accurate at its clock.

The defect is ordering. Readying a pull request and asking for a merger are
naturally done at the point a run feels finished, and a run that then writes
one more thing — a message ledger, a corrected number, a line in a run note —
invalidates the field it just published. **The two acts that make the ask true
are the last commit and the ask, and runs do them in the wrong order**, because
the ask feels like the closing act and the last commit is usually bookkeeping
that arrives after it.

Worth naming what the rule did right: both instances were *caught*, by the
author, within a minute, precisely because the rule forces a head commit into
the message. A seat that wrote "my run is readied" with no head would have had
nothing to notice. So this is a rule working well enough to expose the gap
beside it rather than a rule failing.

**The fix.** One line, and it is a sequencing rule rather than a content rule:
**the merge ask is the last act of the run.** Nothing is committed after it.
If something must be committed after it — a correction, a number, a late
reading — the ask is re-sent rather than corrected, because a correction costs
the receiver a second read of the same thought and the ask is cheap.

The practical ordering for this seat: finish the work, write the description,
`gh pr ready`, read the head, send the ask, stop. Applied in
`prompts/exo-agent.md` under the §"every verdict" section, which is where the
content rule already lives, so the two are read together.

**What the org grew from it.** The general shape, which is not about merge
asks. **A rule that requires a field to be measured does not say when to
measure it, and a run will take the reading at the moment the thought occurs
rather than at the last moment it is true.** For any field a seat publishes
about mutable state — a head commit, a queue depth, a turn count, a branch
state — the rule needs a clock *and* a position in the run. This seat's
registers have the same gap in the other direction: the quality-claims register
requires a date on every measured number and nothing says the measurement
happens before the row is written rather than after.

**Related.** The parent is the three-verdicts incident of 2026-10-26.
`INC-2026-11-02-the-outstanding-heading-dropped-eight-of-ten-rows-and-lost-two-grants-with-them`,
filed by this same run, is the same family seen from the producer's side: a
correct rule with nothing in the thing that produces the artifact to enforce
it.

**One validator rule learned by being refused, recorded because no file here
states it.** The correction's first send was refused `400`: *"data.files must
be a list of paths, because the seat's work timeline draws one entry per path;
a count is not one. Write the paths, or put the number under another name such
as files_count."* The board's message store reads `data.files` as the paths a
run touched and builds a per-path timeline from it, so an integer there is not
a type error but a wrong fact. This belongs beside the three prose rules §3f
rule 1 records, and the refusal named its own remedy, which is the fourth time
this seat has found a board refusal to be the whole answer.
