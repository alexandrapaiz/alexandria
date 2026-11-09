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
2. **The provenance panel's vocabulary has no two-source form**, and that is a
   real gap rather than a typo. A delta drawing on two papers has no way to
   attribute a judgment to this library except by using a singular possessive
   that misdescribes its own sources, or the plural `"the papers'"`, which
   happens to read correctly here only because both sources are papers. The
   phrase the run first reached for, `"ours, not either paper's"`, is the
   clearest English of the three and the one the gate rejects. Filed for the
   engineer seat as a ledger entry rather than worked around again, because the
   next revision that gains a second source will write the same sentence and
   hit the same red.
