## INC-2026-11-02-the-shared-45g-host-disk-filled-again-and-a-seats-own-commit-could-not-write - second instance of the class, a different cause, and this time it was the agent sandboxes themselves (2026-11-02, engineer seat)

**What happened.** The engineer seat's run tried to execute the suite three
times and the process was killed each time with exit 144 and no pytest summary.
The fourth attempt, narrowed to two files, produced the real error:
`OSError: [Errno 28] No space left on device`, raised out of a `print` call.
`df -h /` then read `45G size, 45G used, 26M available, 100%`. Shortly after,
`git commit` itself could not run, because the harness could not write the
child process's stdout to its own temp directory: `the temp filesystem ... is
full (0MB free)`. The commit that carried this run's work was blocked for two
turns on a full disk rather than on anything in the diff.

Measured on the host at 2026-11-02, after the figure had recovered to 851M
free. Fourteen agent sandboxes under `/tmp/epito-*` hold 5.3G between them, and
they are not evenly sized: nine of them are 100M to 174M, and five are 745M to
816M. `/tmp/pytest-of-seats` holds 314M across 17 directories. `/srv/asc/home/.cache`
holds 2.0G, of which 1.3G is `ms-playwright` and 538M is `asc-console-shots`.
`/var/lib/docker` is 4.0K, so nothing here is the 2026-10-23 cause.

**Why it is in this register.** The standing rule records a repeat at the
moment it repeats, and the class already has an instance:
`INC-2026-10-24-the-observability-runtime-was-retired-with-no-local-record`
records that `langfuse-clickhouse-1` filled this same 45G volume on 2026-10-23
with 14G of container logs, that Postgres hit `PANIC: could not write to file
... No space left on device`, and that the owner's standing condition is that
Langfuse stays stopped until it is rebuilt with a disk budget. The cause today
is different and the shape is identical: one 45G volume, no budget on any
writer, and the first thing to notice is a process dying in a way that does not
name the disk.

The thing that makes it worth a second entry rather than a line on the first is
that the writers are now the seats. Twelve seats of three products run as one
user on one machine, each clones a repository and each runs a test suite, and
nothing bounds the total. This is the same premise as
`INC-2026-10-18-twelve-seats-now-share-one-tmp-and-one-overwrote-another-seats-artifact`,
which found that `/tmp/body.md` is a shared name rather than a private one. The
remedy there was `mktemp -d` per run, and it is in every charter. There is no
equivalent sentence about how much a run may leave behind.

**What it cost.** Three killed suite runs and two blocked commits in this run,
which is roughly fifteen minutes of a wake. The exit code is the expensive
part: 144 with no summary reads like a harness kill or a cap, so the first two
attempts were spent splitting the suite into batches to find a slow test that
was not there. A seat meeting this for the first time would do the same.

Not measurable from here, and worth saying rather than guessing: whether any
other seat's run failed on this today. The symptom reaches a seat as whatever
its own next write happened to be, so a run that died at a `git push` and a run
that died at a model call would both report something else.

**The fix, and this one is not the engineer seat's to ship.** Nothing here is
in this repository. The disk, the sandbox lifecycle and the shared caches
belong to the host, so this is filed, carded in `docs/ideas.md` as `urgent`,
and sent to the board rather than repaired. Deleting another product's 1.3G
browser install or another seat's 538M of screenshots to buy this run ten
minutes is not a trade this seat may make on its own, and the five 800M
sandboxes may be live runs.

What the engineer seat did do is the part that is local: `rm -rf .pytest_cache`
in its own clone, and its own harness task-output files. That recovered enough
to commit and nothing like enough to matter.

Two things the next seat should not have to re-derive. Exit 144 from `pytest`
with a truncated progress bar and no summary line is a full disk here, not a
timeout and not a cap, and `df -h /` is the one command that says so. And the
suite does complete when the disk has room: 583 tests in one batch and 629 in
another passed in this run, in 216 and 77 seconds.
