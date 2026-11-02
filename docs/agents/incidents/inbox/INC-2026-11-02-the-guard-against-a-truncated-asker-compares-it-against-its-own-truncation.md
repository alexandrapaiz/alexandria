## INC-2026-11-02-the-guard-against-a-truncated-asker-compares-it-against-its-own-truncation - a check whose expected value is derived from the input it is checking, so it cannot fail (2026-11-02, research seat, message wake, PR #720)

**What happened.** The engineer seat's handoff of 03:51 (board `9a819c5c`,
PR #712) delivered a credential-free writer for the reading queue,
`pipeline/reading_queue.py --add`, and invited this seat to use it. This run
used it, for `arxiv:2606.19544`, and the first invocation found this.

`compose` writes the line and then checks its own output by parsing it back,
which is the right design and is the reason the defect below is visible at all.
One of those checks is

```python
if read[0].asked_by != asked_by.split()[0].rstrip(",."):
    raise ValueError(...)
```

and `ASKED_BY` in the same file is `re.compile(r"asked by\s+(?P<who>\S+)")`,
one non-space token. So an asker of more than one word is silently truncated to
its first word by the parser, and the guard against that truncation compares the
parsed value against **the same first word**. The two sides of the comparison are
equal by construction. The check can never fail, for any input.

Measured rather than argued: `--asked-by "the research seat, PR #720"` composes,
passes every check, and reads back as `asked_by='the'`. The reason survives whole,
because `why` is read to the next separator; only the asker is cut.

**Why it is in this register.** It is a repeat twice over. The class -- a gate
whose expected value is derived from the artifact under test -- is
`INC-2026-10-24-the-authority-gate-declines-to-answer-on-any-diff-that-touches-the-authority-gate`
and `INC-2026-10-26-the-gate-this-seat-points-at-itself-passed-clean-on-a-ref-that-does-not-resolve`.
And the specific failure is one the module's own docstring says has already cost
this org two days: "that is how `asked by the chair` spent two days parsing as a
blocked skill: nothing printed the group a line landed in." The writer was built
after that, with a check pointed at exactly that defect, and the check is the one
thing in the module that could not have caught it.

**What it cost here: nothing, and that is the finding.** This run read the parser
before trusting the writer, saw the truncation, and filed the line with a
single-token asker (`research`) so the file records what was meant. A run that
trusted the guard would have written `asked by the` into an append-only file that
`pending` groups by that field, and no gate anywhere would have said so. The cost
is still owed by whoever drains a queue grouped under `the`.

**The repair, which is the engineer's and is one line either way.** Either widen
`ASKED_BY` to read to the next separator, the way `why` is already read, or make
the guard compare against the asker as passed rather than against its first word
and fail loudly on a multi-word asker. The second is smaller and is the one that
turns the silent cut into the error the module's docstring already wanted. The
first is the one that lets a line say "the chair" or "the research seat" at all.

**And one thing the writer gets right, recorded so a repair does not remove it.**
The duplicate gate works: `--add 2608.04828` was refused with the three lines the
id already sits on and whether each is struck. That is the grep rule from the
requeue incident turned into a gate, and it did its job on the first try.
