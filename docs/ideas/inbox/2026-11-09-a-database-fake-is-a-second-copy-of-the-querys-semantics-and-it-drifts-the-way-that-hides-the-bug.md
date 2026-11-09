### 2026-11-09 - A database fake is a second copy of the query's semantics, and it drifts in the direction that hides the bug (engineer seat)

- Trigger: the two defects fixed this run had each been covered by a passing
  test suite for weeks. `tests/test_reading_queue.py` and
  `tests/test_distill_explicit_ids.py` both stand a `FakeConn` in for psycopg,
  and both routed their select on `params[0]` alone. The code's query matched one
  id shape; the fake matched one id shape; the test passed. Neither fake was
  wrong about anything the code did. They were wrong about the same thing it was.
- What: this is a general property of a hand-written database fake and it is not
  a property of a bad one. A fake re-implements what the statement means, so the
  suite is comparing the code against a second copy of the code's own
  assumptions, by the same author, in the same sitting. The drift is not random
  either: a fake is written by reading the query, so it inherits precisely the
  misreading that produced the query. That makes the fake strongest exactly where
  the query is right and silent exactly where it is wrong. The counter-measure
  this run used in both files, and which is the proposal, is one assertion per
  fake-backed route **on the statement text**, not on the behaviour: `assert "id
  = %s or id like %s" in statement` fails when the query regresses even though
  the fake would happily serve the regression. That caught nothing today because
  it was added with the fix, and it is the only assertion in either file that
  would have caught the defect on the day it shipped.
- First step: count them before proposing a rule. A grep for `class FakeConn`
  and `class FakeCursor` across `tests/` says how many routes are fake-backed,
  and how many of those already assert their statement text. If the answer is
  "many and almost none", the rule is worth a line in
  `docs/standards/lessons.md` through the relay rather than a local note, because
  it is a property of testing a database and not of this repository. If it is
  two files, this run already fixed both and the card closes.
- Cost: $0
- Status: proposed
