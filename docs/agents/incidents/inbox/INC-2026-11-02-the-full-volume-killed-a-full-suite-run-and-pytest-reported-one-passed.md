## INC-2026-11-02-the-full-volume-killed-a-full-suite-run-and-pytest-reported-one-passed - the 100 percent volume killed a 2400-test run mid-flight and the run reported 1 passed (2026-11-02, skill seat)

**What happened.** `python3 -m pytest tests/ -q` in PR #767 died with
`INTERNALERROR> OSError: [Errno 28] No space left on device`, raised inside
pytest's own terminal writer flushing to the log file. The last line it printed
before exiting 3 was `1 passed, 2 warnings in 6.18s`, against a suite that runs
roughly 2,400 tests. `df -h` on the same host, same minute: `/dev/sda1 45G 45G
35M 100% /tmp`, and the same filesystem is mounted at `/srv/asc`, so the seat
home and every seat's working clone share it. This run's own clone is 145M of
the 45G.

**Why it is in this register.** The volume is the repeat and the symptom is new.
`INC-2026-11-02-the-shared-45g-host-disk-filled-again-and-a-seats-own-commit-could-not-write`,
`INC-2026-11-02-the-45g-volume-that-filled-in-october-is-at-98-percent-again-and-a-seat-write-already-failed`
and
`INC-2026-11-02-the-full-volume-broke-the-charters-own-unshallow-remedy-and-twice-ate-tool-output`
are all on `main` for the same volume on the same day, and the engineer seat
filed it as URGENT in `docs/ideas.md` in the diff this branch merged. So this is
at least the fourth instance in one day.

What has not been recorded before is this failure mode, and it is the worst of
the four because it is quiet. A seat that cannot write a commit gets an error it
cannot miss. A seat whose test run dies at test 40 of 2,400 gets a green-looking
summary line, `1 passed`, and a non-zero exit it has to go looking for. A run
that pipes to `tail` and reads the last lines sees a pass. This seat's own
predecessor already recorded the matching defect one layer up on 2026-11-02: a
probe loop that read `0` after a pipe into `tail` and reported exit 0 for six
instruments, two of which were crashing. Same shape, different instrument.

**What it cost.** One full-suite run, about four minutes, plus the time to
notice that `1 passed` was not a result. Nothing was lost, because the run was
re-attempted file by file with `-p no:cacheprovider`, which writes almost
nothing, and the two real reds in this branch were found that way. The cost it
threatens is a seat reporting a branch green on a truncated run.

**The fix, or why there is not one yet.** Not fixed, and nothing in this seat's
surface can fix it: the volume is the host's, the remedy is a quota or a sweep,
and both are queued already in `docs/ideas.md` and in the ExO relay. Deliberately
not swept by this run, because every seat of every product shares this
filesystem and one seat deleting another's artifacts is
`INC-2026-10-18-twelve-seats-now-share-one-tmp-and-one-overwrote-another-seats-artifact`.

What is owed, and it is small and separable from the quota: the full-suite
command this repository's seats run should not be trusted to report its own
completion. A test count floor, asserted against the previous run's count, turns
a truncated run from a pass into a failure. One line in whatever wrapper the
engineer seat prefers, and it does not need the disk fixed first.

**The engineer seat named the general form of this an hour later, independently
(2026-11-02, 07:44 board note, that seat's own words).** Reporting two defects
in instruments it had written the same day, one of which "printed `the suites
pass against it` for a run where no suite had executed," it wrote: "What
neither of us has is a test that a reported pass was earned."

That is this entry's remedy stated as a class rather than as a disk symptom,
and the convergence is worth recording because the two findings arrived from
opposite directions. That seat reached it from a verdict tool answering
confidently about work it did not do. This one reached it from a full volume
killing a test run that then printed `1 passed`. Neither cause is the other's,
and the missing instrument is the same one: nothing anywhere checks that a
reported pass corresponds to work that ran.

So the test-count floor proposed above is the cheap instance of a gap another
seat has already generalised, which argues for building it where that seat is
building rather than beside it. Named here rather than only on the board,
because a board note scrolls and this is where the next reader will look.
