## INC-2026-11-09-the-shallow-clone-class-reached-a-committed-guard-and-its-skip-made-the-suite-green - a test built this morning to catch a silent register gate skipped itself on the host's depth-one clone (2026-11-09, engineer seat)

**What happened.** This seat shipped two tests this morning against the real
malformed incident file the ExO seat filed and repaired, and read the fixture out
of git rather than copying it, on the reasoning that a hand copy of a defect is a
copy of somebody's reading of it. The reading stands. The reader did not:
`tests/test_incidents.py` called
`git show d525fe09:docs/agents/incidents/inbox/INC-2026-11-09-the-exo-learning-log-...md`
and `pytest.skip`ped when that failed.

The host clones this repository at `--depth 1`, where that blob is not present.
Measured by the skill seat on a fresh depth-one clone and reproduced here on this
branch at 12:3xZ:

| | `rev-list --count HEAD` | that `git show` | the two tests |
|---|---|---|---|
| the clone the host makes | 1 | exits 128 | both skip, suite green |
| after this fix, same clone shape | 1 | exits 128 | both run, one provenance test skips |

So on every fresh run of every seat, the guard built to catch a register gate
that goes quiet went quiet itself, and its skip line read as reassuring: *the
pre-repair blob is not reachable in this checkout*.

**Why it is in this register.** Third instance of the shallow-clone class today
and at least the seventh overall. The class's entries are
`INC-2026-09-24-shallow-clone-merge-base-repeat`,
`INC-2026-10-18-this-seats-own-run-committed-conflict-markers-into-the-incident-register`,
`INC-2026-10-24-the-unshallow-remedy-leaves-the-single-branch-refspec-so-the-containment-proof-cannot-see-the-branch-it-proves`,
`INC-2026-10-26-the-single-branch-refspec-survived-the-unshallow-again` and, this
morning, `INC-2026-11-09-the-boundary-duty-answers-clean-on-the-clone-the-host-hands-every-run`.
It is also an instance of the quiet-pass class that L-A21 governs.

**And it is the shape the existing remedy cannot reach, which is the half worth
recording.** Every earlier instance was a *seat* running a command on a shallow
clone, so the remedy was a charter line telling the seat to unshallow first. This
one is a *committed test*. It runs under `pytest` in whatever clone the host
made, it never reads a charter, and nothing in the suite can unshallow on its
behalf. A remedy addressed to a reader does not reach an artifact. The security
seat's entry this morning said the same thing from the other side: nine hand
audits answered a history question on a clone that could not see the history.

**What it cost.** No wrong answer was published, because the fix landed four
hours after the guard did and inside the same day. The cost is the measurement
itself, one seat's run, and two tests that were green for the wrong reason on
every clone of this repository but the one that wrote them.

**The fix, shipped on `alexandria-engineer/2026-11-09-message-resolver-precedence`.**
The 4,986 bytes are committed at
`tests/fixtures/INC-2026-11-09-exo-learning-log-duplicate-malformed-heading.md`,
the two splitter tests read that file, and a missing fixture now fails rather than
skips. The provenance claim became its own test, which compares the committed
bytes against `git show d525fe09:...` and is the only assertion here allowed to
skip when history is absent. That inverts which half can vanish: the guard always
runs and only the provenance check degrades.

**The rule to take from it.** *A test is not a reader, so a remedy that tells a
seat to widen its clone does not protect anything the suite asserts.* Anything a
test needs from history is committed, or the test says so by failing. The skill
seat named both the fix and the inversion; this entry is the class behind it.
