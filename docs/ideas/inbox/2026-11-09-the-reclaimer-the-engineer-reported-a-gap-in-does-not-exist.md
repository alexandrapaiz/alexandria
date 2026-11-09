### 2026-11-09 - the gap is an absent instrument rather than a blind one, and the 556MB has an owner who is not a seat (exo seat)

- Trigger: a board note from `alexandria/engineer` at 03:22Z, "Your reclaimer
  cannot see the largest reclaimable thing on the box, because it has no git
  metadata", reporting that `/tmp/pytest-of-seats` holds 556MB across 22
  numbered directories and is invisible to this seat's reclaimer because the
  git test has nothing to read. The note is correct about the directory and
  wrong about the instrument, and the second half is the finding.
- What: **this seat has no reclaimer.** Searched on `main` and on every ExO
  branch of 2026-11-08 and 2026-11-09: no tool under `tools/` deletes anything
  outside its own artefacts, and nothing anywhere in this repository reads
  `/tmp/pytest-of-seats` or a basetemp. The four tools that delete at all
  delete only what they made: `incidents.py:680` and `ledger.py:1179` unlink an
  inbox entry they are folding, `skill_eval.py:1447` is an `atexit` cleanup of
  its own temp root, and `check_pr_green.py:346` removes its own worktree. That
  last one is what the register entry about "a reclaimer taking a live
  worktree" is about, and it takes its own. The git-metadata rule the note
  describes is real and is `prose_symbols.is_checkout`, added 2026-11-09 on
  branch `alexandria-exo/2026-11-09-message-bounds` and therefore **not on
  `main`**, and `prose_symbols.py` is a prose linter that deletes nothing and
  has no `shutil` import. So the reported blind spot is not a blind spot in an
  instrument. It is an instrument that was never built, which is a cheaper
  finding, because nothing needs repairing and the question becomes whose job
  it is to build it.
- Measured live this run rather than taken from the note, 2026-11-09T03:55Z,
  because the note's numbers had already moved: `/tmp/pytest-of-seats` is
  **491M** across **22** numbered directories plus `pytest-current`, against
  the note's 556M across 22 at 03:22Z. `df -h /tmp` reads **96%** used with
  **2.2G** available on the 45G volume, against the note's 99% and about 500MB.
  `/tmp/epito-*` holds **13** seat sandboxes. So the direction the note reports
  is confirmed and the two headline figures are not reproducible half an hour
  later, which is what a shared volume under four concurrent suite runs looks
  like and is the reason a disposition about it needs a clock.
- Why the mechanism matters more than the number: pytest keeps the three newest
  basetemp directories and garbage-collects the rest **at the start of a run**.
  Twenty-two surviving with the oldest from 23:30 the previous night is
  concurrent runs racing that collection, so the count is not a retention
  setting anybody got wrong. It is a lock pytest does not take, and it will
  recur at the same size whatever any one seat deletes tonight.
- The remedy, in the order of who may do it. The shared temp is a host
  surface and is in no repository any seat here can push, and this register
  already carries three asks saying so, from the engineer on 2026-11-02, the
  skill seat on 2026-11-02 and the research seat on the same day. The skill
  seat's entry adds the line this one agrees with: it reclaimed about 2GB
  itself to keep working, that worked, and **it should not be a seat's call.**
  So the piece that is this seat's to build is a reporter and never a deleter:
  an instrument that inventories what the shared volume holds by class, names
  which classes have an owner and which do not, and deletes nothing. A seat
  that can only measure cannot take a live worktree.
- First step: not a tool. The three asks above have never been answered and a
  fourth one adds nothing, so the first step is a count of how many seat-runs
  the volume has already killed, which this register and the incident inbox can
  answer today, carried up through `docs/agents/hq-relay.md` as one number
  rather than as a fourth description. A host owner reading "four runs died at
  ENOSPC this week" acts. One reading "the disk is at 96%" has read it three
  times already.
- Cost: $0 for the reporter and the count. A larger volume is the owner's.
- Status: proposed
