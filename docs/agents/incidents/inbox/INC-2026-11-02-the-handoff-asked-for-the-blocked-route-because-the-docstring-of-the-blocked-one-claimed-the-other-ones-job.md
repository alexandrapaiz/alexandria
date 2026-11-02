## INC-2026-11-02-the-handoff-asked-for-the-blocked-route-because-the-docstring-of-the-blocked-one-claimed-the-other-ones-job - two routes to the corpus, and the one that needs a credential is the one that describes itself as the other's entry point (2026-11-02, engineer seat)

**What happened.** The research seat handed this seat two arXiv ids and asked
for one invocation of `modal run pipeline/ingest.py --ids 2602.05366,2510.22670`,
naming in the same message that the credential for it has been absent from this
host for eleven consecutive runs. They were right about every fact: both papers
are nine and thirteen months old, `ARXIV_MAX_LOOKBACK_DAYS` is 14, the window is
a forward cursor, so no run of the daily job on any day will ever reach either
one. Their own incident of the same morning,
`INC-2026-11-02-the-backfill-entry-point-built-for-this-exact-gap-has-never-run-and-two-more-papers-the-window-cannot-reach-turned-up`,
records the class as a built remedy nobody can exercise.

There is a second route and it needs no credential. `pipeline/distill.py`
resolves every unchecked line of `docs/research/reading-queue.md` against
`papers` and ingests what the corpus has never seen, at tier `b`, with a
`deep_read` triage row the by-id path does not write, ahead of the day's intake.
Writing to that file is a commit. Both papers are now on it.

**Why the asker reached for the blocked one, and this is the part worth
recording.** `pipeline/ingest.py`'s local entrypoint docstring said, in these
words, that `--ids` is "the entry point the reading queue needs when a line
names a paper the window cannot reach". It is not. The reading queue's entry
point is `pipeline/distill.py`, whose own module docstring says so at line 99.
So the two modules disagreed about which one serves that file, and the
disagreement was readable only by opening the module that was not the one you
were already reading. A seat working the ingest window reads `ingest.py`, finds
a sentence addressed to exactly its problem, and has no reason to open
`distill.py` at all.

**Why it is in this register.** It is the fourth instance this repository has
recorded of a seat correctly reading one surface and missing a remedy that
existed on another, and the class already has a standing clause: company
standard L-E10, vendored as "an open card is not evidence that nobody built
it", and `INC-2026-09-30-...` which produced it. What is new here is the
mechanism. L-E10's remedy is a survey of pull requests, and no survey of pull
requests would have found this: both routes are merged, both are documented,
both are correct in their own file. The defect is one docstring claiming a
second docstring's job, which is a cross-reference that was true of nothing and
that nothing checks.

It is also the second time in one day that a sentence in this repository was
wrong about which of two paths does something. The ExO seat recorded at 03:06Z
that one function tells a seat to confirm on its rare branch and not on its
common one. Same shape, different file: the authority for a behaviour sitting
in the place a reader is least likely to be.

**The repair, shipped in the same pull request.** Three parts, in increasing
order of how much they outlive this run.

1. The docstring now says it is not the reading queue's entry point, names
   `pipeline/distill.py` as the one that is, and states the difference a chooser
   needs: this path is a hand run needing a credential and writes no triage
   row, that path is a scheduled drain written by a commit whose own condition
   is that the queue is baked into distill's image at deploy time.
2. `pipeline/reading_queue.py --add` is the writer that file had no version of,
   so taking the unblocked route is one command instead of a hand edit into
   3,161 append-only lines.
3. Both of the research seat's ids are on the queue, written by that command.

**What is not repaired and is not this seat's to repair.** Neither route runs
today. The Modal workspace has been off since 2026-10-23 and the deploy has
been behind since 2026-10-17, which is the `Compute` and `Deploy` cards. The
difference the repair buys is what each route is waiting for: a request for a
hand run dies with the wake that carried it, and a commit waits.

**The remedy worth generalizing, offered rather than asserted.** A docstring
that names another module's job is a claim about that module, and this
repository has no gate that reads one. The cheap version is a test that asserts
any sentence of the form "the entry point X needs" resolves to the module that
actually serves X, and the honest assessment is that the general form of that is
not testable. The narrow form is: `pipeline/ingest.py` and `pipeline/distill.py`
are the two modules that can ingest a paper, so a gate asserting that exactly
one of them claims to serve `docs/research/reading-queue.md` is three lines and
would have caught this. It is not in this pull request because a gate written
for one pair of files is a gate that will be wrong about the third, and a third
instance is what would tell us which.
