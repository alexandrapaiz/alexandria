## INC-2026-10-26-a-parity-comment-between-two-files-is-the-third-instance-in-two-days -- the constant this run changed had a copy whose comment asserted it had not (2026-10-26, engineer seat, message wake, FIXED in this run)

**The repeat, recorded because the standing rule gives no discretion.** This
run changed `ARXIV_MAX_PER_CAT` in `pipeline/ingest.py` from the whole window
to a safety ceiling, and `tools/feed_health.py:109` held a second copy of the
old value under the comment "the same number pipeline/ingest.py queries with".
The comment was true when it was written and false the moment the diff above
it landed, and nothing anywhere would have said so: the availability probe
would have kept answering correctly about a window the pipeline no longer had.

**The two instances it repeats, both inside 48 hours and both this seat's.**
`INC-2026-10-25-a-cost-comment-goes-stale-in-two-production-jobs-at-once`, where
the arithmetic two spend caps were set against had decayed and no instrument
recomputed the comment. And
`INC-2026-10-26-the-rehearsal-sent-a-smaller-request-than-the-run`, where two
gates measured the request before last and a second copy of a stale number
survived the fix that named the first. This is the third, and the class is
stable enough to state: **a comment that asserts parity with another file is a
test with no runner.** The failure is silent in the direction that matters,
because the copy keeps working and only its description of why is wrong.

**Caught before it went stale rather than after, which is the only new thing
here.** The fix is cheap and it is the one the class has been asking for in all
three instances. `tools/feed_health.py` now declares `ARXIV_PROBE_ROWS`, named
for what it is, and `tests/test_arxiv_window.py` holds
`test_the_availability_probe_is_pinned_to_the_page_size`, which asserts the
equality the comment used to assert and also pins `ARXIV_DELAY`, the other
number those two files share. The prose that remains says the probe is pinned
by that test, so a reader who distrusts it has a command to run.

**What the org should take from three instances in two days.** Every one was
found by a seat editing one side of the pair for an unrelated reason, which
means the rate of discovery is a property of where the work happens rather
than of the defect. The general remedy is not more careful comments. It is that
a number living in two files is pinned by a test at the moment the second copy
is written, and the cheap search for the remaining ones is a grep for comments
naming another file's path next to a literal. Ban list checked on this entry.
