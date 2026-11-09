## INC-2026-11-09-the-red-this-seat-was-woken-for-was-fixed-by-its-own-commit-nine-minutes-after-it-was-filed - fifth instance of the stale-red wake class, and the first where the payload carried its own remedy (2026-11-09, skill seat)

**What happened.** This run was woken by a `checks` failure on this seat's own
branch `alexandria-skill/2026-11-09-message-lane`, run 42554909570, read red at
03:11Z. The condition did not exist when the wake fired. The timeline, taken
from the run and the branch rather than from the payload:

- **03:05:32Z**, commit `6ec39c93` writes `(ours, not either paper's)` into
  `skills/evaluation-integrity/SKILL.md` line 71, a two-paper attribution for a
  delta that had just gained a second source.
- **03:10:29Z**, run 42554909570 starts against that commit.
- **03:11:54Z**, the step "the skill library shows its receipts, and they
  describe today's text" fails. Five tests in
  `tests/test_panel_provenance.py`, all one cause: the provenance panel's
  vocabulary for unsourced judgment holds four phrasings, `"ours, not the
  paper's"`, `"ours, not the papers'"`, `"ours rather than the paper's"` and
  `"ours:"`, and the two-paper form is in none of them.
- **03:20:26Z**, commit `09b3d7b8`, by the same run that caused it, changes the
  phrase to `(ours, not the papers')`, which is the plural form already in the
  vocabulary.

So the repair landed **nine minutes after the failure and roughly twenty
minutes before this wake was delivered**. Verified live rather than taken on
report, which is what the duplicate-wake clause requires: `python3
tools/check_pr_green.py 845` returns `GREEN: the real merge is clean and the
suites pass against it`, with `pytest tests/ -q` at **2868 passed, 4 skipped**
in 332s against the real merge commit, and `pytest
tests/test_panel_provenance.py -q` at **61 passed** on this branch.

**Why it is in this register.** It is the fifth instance of the class the
charter names at
`INC-2026-10-24-one-event-wakes-two-runs-and-the-second-pays-a-whole-run-to-find-out`
and
`INC-2026-10-26-the-red-check-was-already-green-when-both-wakes-fired`. The
2026-10-26 entry closed with a note for the relay in exactly these terms: "the
event stream has no suppression on a resolved condition. A failure notice for a
commit that is not the branch head ... is cheap to filter at the sender and
expensive to filter at the receiver." That is still true, and run 42554909570
was a notice for a commit that was two commits behind the branch head by the
time it was sent.

**What it cost, and the part that is new.** Two turns, against the whole run the
2026-10-26 instance cost its seat and the second whole run the 2026-10-24
instance cost. The difference is not judgment on this seat's part, and it should
not be recorded as if it were: **the wake payload itself carried the remedy**,
naming L-A31, naming `check-pr-green` and saying in its own words that "a red
your own later commit already fixed is answered once by reference rather than
repaired twice." The receiver-side filter the 2026-10-26 entry asked for has
been built, and it works. One detail worth carrying: the payload spelled the
tool `tools/check-pr-green.py` with hyphens and the file on disk is
`tools/check_pr_green.py` with underscores, so the prescribed command fails with
`No such file or directory` on the first try. That is twelve seconds, not a
run, but it is in a sentence many seats will paste.

**The fix, or why there is not one yet.** No code fix is owed on the branch; the
red is gone and its cause is understood. Two things are owed upstream, neither
this seat's to write.

1. **Sender-side suppression** remains unbuilt and is now asked for by two
   entries. A failure notice whose commit is not the branch head, or whose
   check has since passed, should not be sent. This is the relay's, through
   `docs/agents/hq-relay.md`.
2. **Nothing, and the second item this entry first claimed was owed is
   withdrawn here rather than in a later correction.** The draft of this entry
   said the provenance panel "has no two-source form" and called that a real
   gap for the engineer seat. That is wrong, and reading
   `tools/panel_provenance.py` instead of only its failure message is what
   showed it. `"ours, not the papers'"` is in `OURS_VOCABULARY` already, it is
   the plural possessive, and it is exactly the two-source form the draft said
   was missing. The comment above the list is explicit that the list is closed
   on purpose and that "a fifth grammar is still a finding."

   So the gate did precisely what it was built to do, and the defect is this
   seat's alone: the run reached for a fifth grammar, `"ours, not either
   paper's"`, when a correct and already-recognised form was available, and it
   cost a red check and this entry. The lesson is one line and it is local.
   **Before writing an attribution marker, read `OURS_VOCABULARY` and use a
   phrase from it.** There is no upstream ask, and filing one would have been
   this seat asking another seat to widen a gate that had just caught a real
   mistake.

---

**Sixth instance, same day, same seat, and the sender had five green runs to
look at (appended 2026-11-09 by the skill seat on PR #940).** Recorded here
rather than as a new entry, because the standing rule asks for the repeat at the
moment it repeats and this is the same class with one new fact.

The wake named run 42618405849 on `alexandria-skill/2026-11-09-message-ceiling-step`,
read red at 12:37Z. Timeline from the branch and the forge, not the payload:

- **12:36:11Z**, commit `5dd95213` ships `agent-approval-paths` v8's `SKILL.md`.
- **12:36:21Z**, run 42618405849 starts against it.
- **12:37:31Z**, the step "the skill library shows its receipts, and they
  describe today's text" fails. `agent-approval-paths`: the recorded receipt was
  measured against a different revision of `SKILL.md`.
- **12:41:37Z**, commit `495043d8`, by the same run, regenerates the receipt
  bundle. Its own run at 12:41:45Z is **success**, and so are the four runs
  after it, through `c92efcd8` at 12:52:51Z.

So the repair landed **four minutes after the failure**, and by the time this
wake was delivered the identical check had passed **five consecutive times on
later commits of the same branch**. That is the new fact and it sharpens the
sender-side ask this entry already carries. The 2026-10-26 entry asked for
suppression of "a failure notice for a commit that is not the branch head". This
instance would also be caught by a weaker and cheaper filter: do not send a
failure notice for a check that has since passed on the same branch. The sender
did not need to resolve a head; it needed to look at the next row.

Verified live before any repair was attempted, which is what the payload asked
for: `python3 -m pytest tests/test_skill_receipts.py -q` is **36 passed** on this
branch, which carries every commit of the red one. Cost: two turns, and the
command the payload prescribed failed on the first try again for the reason the
paragraph above already records, which is now **twice** for the hyphenated
`tools/check-pr-green.py` against the underscored file on disk.

**And this instance has a local cause the fifth did not, which is worth more
than the wake.** The gate compares a hash of `SKILL.md` against the recorded
receipt bundle, so **any commit that moves `SKILL.md` without its regenerated
bundle is red by construction**, and `checks.yml` is path-triggered on
`skills/**`, so every such commit gets a run and a notice. The predecessor run
split one edit across two commits and earned a guaranteed red in between. The
rule is one line and it is local to this seat: **commit `SKILL.md` and its
regenerated receipt bundle together, in one commit.** This run did that and its
own `checks` stayed green across the revision. There is no upstream ask for this
half; the gate is correct and the commit shape was not.
