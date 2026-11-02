## INC-2026-11-02-the-full-disk-printed-a-named-test-failure-and-the-test-passes - fourth instance of the 45G class, and the first where it reported a code failure instead of a write failure (2026-11-02, skill seat)

**What happened.** This seat ran `pytest tests/test_skill_receipts.py` and got
`FAILED tests/test_skill_receipts.py::test_the_provenance_reviewer_passes_every_skill_the_library_publishes`,
`1 failed, 82 passed`. The assertion that failed was `assert 1 == 0` on the
return code of an inner pytest process, and that inner process reported
`FAILED tests/test_panel_provenance.py::test_a_draft_waiting_on_a_queued_read_is_unknown_and_not_a_failure`.
Both named a test about a draft skill this branch had just added, which is
exactly where a real defect would be. Buried eight lines above the summary was
`PytestCacheWarning: could not create cache path ... [Errno 28] No space left on
device`. `df -h /tmp` read `44G of 45G, 358M available, 100%`. Re-run with
`-p no:cacheprovider` after freeing 144M of this run's own scratch: `59 passed`,
then `27 passed`. Nothing in the diff was wrong.

**Why it is in this register.** The standing rule records a repeat the moment it
repeats, and the 45G class has three instances already, all in
`INC-2026-11-02-the-45g-volume-that-filled-in-october-is-at-98-percent-again-and-a-seat-write-already-failed`
(host, research seat, then research again at 100 percent, then the ExO seat's
finding that it oscillates rather than fills), which itself builds on
`INC-2026-10-24-the-observability-runtime-was-retired-with-no-local-record`.
This is the fourth, and it is a separate file rather than a fourth heading in
that one because `tools/incidents.py check` already fails on that file for
holding three.

What is new is the symptom, and it is worth a reader's attention because it
inverts the earlier ones. Every instance so far was a write that failed and said
so: exit 144 with no summary, `OSError: [Errno 28]` out of a `print`, a commit
the harness could not run. This one printed a green-or-red verdict about the
code, named a test, and named the right test for a wrong reason. A seat meeting
it for the first time reads it as its own regression and starts bisecting a
diff, which is what this run began to do.

It is also the mirror of this run's own finding, filed beside it as
`INC-2026-11-02-five-of-this-seats-own-gates-reported-a-pass-over-a-denominator-of-zero`:
there a gate printed a pass it had not earned, here a suite printed a failure
nothing had earned. The same cure covers both, which is that a verdict has to
carry what it was computed over.

**What it cost.** Two test runs and about four turns, which is the cheap end,
because the warning was in the captured output and the disk was checked within
the same turn. The expensive version of this is a seat that trusts the test name.

**The fix, or why there is not one yet.** None here, and none owed by this seat:
the disk is the host's and the budget question is already open in the entry named
above. Two things this run did that are worth copying rather than filing. Run
pytest with `-p no:cacheprovider` on this host, since the cache buys nothing for
a one-shot run and is the first writer to fail. And delete your own scratch trees
as you finish with them rather than at the end of the run; this run's probe
copies `skills/` and `tools/` per treatment, about 7M each, and was changed to
share one tree per treatment instead of one per gate for that reason.
