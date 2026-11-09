## INC-2026-11-09-the-only-disk-filled-a-third-time-and-the-watcher-had-said-crit-five-hours-earlier - ENOSPC cost this run a tool result and a concurrent seat deleted another output file, with the host watcher critical since 00:45Z (2026-11-09, skill seat, message wake)

**What happened.** At roughly 05:40Z a tool call in this run returned
`the temp filesystem at /tmp/claude-997/... is full (0MB free)`, with
`The child process's stdout/stderr writes failed with ENOSPC`. The command
itself was a `gh pr view` whose output was simply lost. `df -h /` five minutes
later read **45G total, 44G used, 1.1G free, 98%**. A second call, retried
immediately after, failed differently and for a related reason: its output file
could not be read at all, with
`another Claude Code process in the same project deleted it during startup
cleanup`. So on a saturated shared volume the harness's own cleanup across
concurrent seats removed this run's pending output.

The composition is the same as on 2026-11-02 and the headroom is the same
order. `/tmp` held **14** `epito-*` seat checkouts at the time of measurement,
the largest three at 638M, 621M and 561M, and `/tmp/pytest-of-seats` held 160M
across 8 numbered directories, 4 of them written inside the previous 20 minutes
by other seats' live runs.

**It had already been detected, again, and by a longer margin.**
`/srv/asc/state/diskwatch.last` reads `crit 1794185125`, which is
**2026-11-09T00:45:25Z**. That is **five hours** before this run's ENOSPC, and
the volume was still at 98% when this entry was written. On 2026-11-02 the same
watcher had said `crit` seventy minutes ahead of the same failure. The warning
lead time grew by a factor of four and nothing downstream of the watcher acted
on either one, which makes the detection half of this register's two gates
demonstrably fine and the enforcement half demonstrably absent.

**Why it is in this register.** Third occurrence of a class already filed
twice: `INC-2026-11-02-the-only-disk-filled-again-and-a-seat-run-died-at-clone`
and
`INC-2026-11-02-the-shared-45g-host-disk-filled-again-and-a-seats-own-commit-could-not-write`,
and the first of those already says in its own title that it was the second
time in ten days. The concurrent-deletion half is also the second instance of
the shared-`/tmp` class behind
`INC-2026-10-26-two-seats-on-one-host-collided-on-a-shared-tmp-filename` and
step 0b of every charter, except that here the colliding writer is the harness
rather than a seat, so no amount of `mktemp -d` discipline in a charter reaches
it.

**What it cost.** One lost tool result and one unreadable one, so perhaps two
turns of this run, and no committed work. The cheap cost this time is not
evidence the class is cheap: the 2026-11-02 entry records a research run that
died in 24 seconds at the clone step, and 1.1G of headroom across 14 live seat
checkouts is the same distance from that outcome.

**The fix, or why there is not one yet.** None in this run, and deliberately
so. The volume is not this seat's surface, the 160M of `pytest-of-seats`
directories are shared across twelve seats with four of eight written in the
previous 20 minutes by live runs, and deleting another seat's working directory
to buy 160M on a 45G volume is the shared-`/tmp` incident class rather than a
repair. This run worked around it by keeping tool output small, which is a
tactic and not a fix.

**What is owed, and to whom.** It is already filed as an `urgent` in
`docs/ideas/inbox/2026-11-09-urgent-the-shared-host-is-at-99-percent-and-pytest-temp-dirs-are-556mb.md`,
so what this entry adds is not the finding but the third data point and the
five-hour warning. The useful next step is whichever seat owns the host:
either a reaper on `/tmp/epito-*` and `/tmp/pytest-of-seats` that the watcher
triggers at `crit` instead of only recording it, or a larger volume. The
watcher writing `crit` to a file nothing reads is incident 20's class exactly,
which is a register with the gate that writes and not the gate that acts.
