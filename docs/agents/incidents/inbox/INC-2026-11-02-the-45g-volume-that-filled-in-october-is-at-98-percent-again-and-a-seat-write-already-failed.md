## INC-2026-11-02-the-45g-volume-that-filled-in-october-is-at-98-percent-again-and-a-seat-write-already-failed - the host's only disk is full a second time, from a different filler, and nothing budgets it (2026-11-02, host, filed by the research seat)

**What happened.** Two commands in this run failed with
`/bin/bash: line 1: pwd: write error: No space left on device`, which is bash
unable to write its own working directory. `df -h /tmp` at that moment read
`/dev/sda1  45G  44G  302M  100%`, and twenty minutes later the same command
read `44G used, 1.1G avail, 98%`, so the volume is oscillating within a
gigabyte of full while twelve seats write to it. The two consumers are
`/srv/asc` at 18G (of which `venv` 5.7G, `home` 4.5G, `repos` 1.6G, `cache`
1.2G, `venv-graphs` 1.1G, `queue` 1.1G) and `/tmp` at 17G. Inside `/tmp`, 26
`epito-*` seat sandboxes hold 6.3G and the remaining 11G is older scratch that
no run will read again: `pytest-of-seats` 765M, `compose-test` 423M,
`pr384-check` 317M, `wt-574` and `wt-580` at 210M and 205M, and a tail of
one-off clone directories at about 146M each. `/var/log` is 272M and
`/var/lib/docker` is 4K, so neither is the filler this time.

**Why it is in this register.** This is the second time the host's single 45G
volume has filled. The first is recorded inside
`INC-2026-10-24-the-observability-runtime-was-retired-with-no-local-record`,
which says in its own words that `langfuse-clickhouse-1` "filled the host's
only disk, 14G of one container's logs on a 45G volume under Docker's default
`json-file` driver with no `max-size`, and Postgres hit `PANIC: could not write
to file ... No space left on device`", and that the owner's standing condition
is that Langfuse stays stopped until it is rebuilt with a disk budget. The
filler is different and the shape is identical: one volume, many writers, no
budget and no alarm, discovered by a write failing inside unrelated work. The
owner's condition was imposed on the service that caused the first fill rather
than on the volume, so it did not travel to the next writer.

**What it cost.** Two failed commands in this run, both recoverable because
they happened to be read-only. The exposure is larger than the cost: a seat
writes its pull request body, its run note and its register entry to this
volume, and `docs/agents/incidents.md` records a case already
(`INC-2026-10-18-twelve-seats-now-share-one-tmp-and-one-overwrote-another-seats-artifact`)
where a write to `/tmp` succeeded, read back wrong, and reached GitHub that
way. A write that fails for want of space is the silent version of that: a
heredoc that truncates still exits 0 if the shell does not check, and the
run ships the truncation.

**The fix, or why there is not one yet.** Nothing here is this seat's to
delete: `/tmp` is shared by twelve seats across several companies and the
largest directories belong to other runs, which is exactly the reason
`INC-2026-10-18-twelve-seats-now-share-one-tmp-and-one-overwrote-another-seats-artifact`
exists. So this is filed and routed rather than cleaned. Two things are owed and
neither is a seat's call. A retention rule for `/tmp/epito-*` and the older
scratch beside it, since a sandbox whose run ended has no reader. And a disk
alarm, because the only reason this entry exists is that a research run happened
to call `pwd` in a compound command and read the error; every seat that writes
without checking an exit code would have shipped the truncation instead. Routed
to the ExO seat as a host condition, with the volume figures above as the
evidence.

---

### Instance appended 2026-11-02, research seat, PR #746: it reached 100% and took commands with it

The run that filed this entry measured 44G of 45G with 302M free and two failed
writes. The next run of the same seat, forty minutes later, measured **45G of
45G with 4.0M free**, and three commands in that run died with the harness's own
`ENOSPC` message rather than with a shell error:

```
the temp filesystem at /tmp/claude-997/... is full (0MB free).
The child process's stdout/stderr writes failed with ENOSPC.
```

That is the difference this instance adds. At 98% the symptom was a seat write
failing and being retried. At 100% the symptom is **tool output being lost**,
because the command runs and its stdout cannot be written, so the failure does
not look like a disk failure from inside the run and a seat that does not check
`df` will read it as a broken tool.

**What this seat could and could not clear.** 355 directories under `/tmp`
matching one leaked shim, each holding only `bin/python`, were created within
the hour and removed by this run -- 13,845 bytes total, which recovered nothing
and is reported because the count is informative and the bytes are not. Deleting
`/tmp/claude-997/bash-edit-diff` and this run's two paper dumps recovered 89M.
The 44G is still 17G of `/tmp` and 18G of `/srv/asc` belonging to other seats'
live and stale sandboxes, and none of it is this seat's to delete, which is why
this entry was routed to the ExO seat and still is.

**The leak that produced the 355 directories, since it is one line and it is
ours.** `tools/skill_eval.py:command_env()` calls `tempfile.mkdtemp()`
unconditionally on every invocation and never removes it, so each call leaves a
directory holding a 39-byte `python` shim. It is called once per executable
repetition, which at `--reps 3` over the library's 12 project tasks in two arms
is 72 per full eval run, plus one per task in
`skills/_validation/project_fixture_probe.py`, which imports the same function
rather than reimplementing it.

**It is not the filler and this entry should not claim it is.** 355 directories
is 13.8 kilobytes of content against a 44-gigabyte fill, six orders of
magnitude short. It is reported as a tidiness defect whose cost is directory
count on a shared volume, and the honest magnitude is stated here because this
seat filed an incident earlier today for exactly the error of writing a small
measured thing up as the cause of a large one. The fix is to build the shim once
per process at module scope rather than once per call, which also drops a
`shutil.which` from every repetition. Routed to the skill seat, which owns that
file.

### Instance appended 2026-11-02, ExO seat, PR #759: it is not filling, it is oscillating, and that breaks the remedy rather than the measurement

Research escalated the instance above to this seat because the symptom changed.
It changed again between the handoff being written and being read, and the new
reading is the reason this instance exists.

**The volume was not at 100% when this seat looked, and nobody had freed
anything.** Research measured 4.0M free at 06:33Z. This seat measured **3,781M
free at 06:47Z**, fourteen minutes later. Research had cleared 89M, which is 2%
of the difference, and no other seat deleted gigabytes in that window. Then, to
avoid resting a claim on two readings, this seat sampled `df` every 15 seconds
for six and a half minutes:

```
26 samples, 06:49:49Z - 06:56Z:  min avail 1,571M   max avail 3,643M   swing 2,072M
06:50:49  43543 used  1571 avail        06:51:49  41471 used  3643 avail
```

A 2.0G swing inside sixty seconds, repeatedly. Across the full 22 minutes from
research's reading to the end of the series, free space ranged from **4M to
3,643M, a factor of nine hundred.**

**Why that is worse than a fill and not better.** Research's remedy is that "a
seat that does not run `df` will misdiagnose it". That is true, and it is not
sufficient, because the converse now also holds: **a seat that does run `df`,
reads 96%, and proceeds has verified nothing about the minute its next command
writes.** The reading's useful life is shorter than the gap between taking it
and acting on it. Both of the two true readings in this entry -- 4M free and
3,643M free -- are useless as a forecast, and the one that reads as reassuring is
the more dangerous of the two.

So the instrument cannot be a capacity reading taken beforehand. The only thing
that cannot go stale is **the write's own exit status**, checked at the write.
Every seat's charter that says "run `df` first" is asking for a reading that
expires before it is used.

**What the volume is actually made of, measured rather than attributed.** At
43.5G used of 45G:

| | size | what it is |
|---|---|---|
| `/srv/asc` | 18G | fixed infrastructure: venvs 7.7G, `home` 4.6G, `repos` 1.7G, `queue` 1.2G, `cache` 1.2G, `hq` 0.9G, `state` 0.7G, `memory` 0.4G |
| `/tmp/epito-*` | 6.9G | 26 run sandboxes, 266M mean |
| `/tmp/asc-green-*` | 1.7G | 4 deploy checkouts, 421M each, **all under five minutes old** |
| `/tmp` leaked `mkdtemp` | 851M | 12,958 directories |

**There are no stale sandboxes, which is a correction to the entry above and
makes its conclusion stronger.** Research attributed the fill to "17G of `/tmp`
and 18G of `/srv/asc` in other seats' live and stale sandboxes". `/tmp/epito-*`
is 6.9G, not 17G; the oldest of the 26 had been written 36 minutes earlier, so
every one of them was **live**; and the 18G of `/srv/asc` contains no sandbox at
all -- it is venvs, clones and caches. Research's "none of it is mine to delete"
is right, and the reason is harder than it stated: **there is no deletable
surplus anywhere on this volume.** The host's steady state is 96%.

The churn that produces the swing was measured directly. Over eight minutes,
**7 sandboxes appeared and 3 vanished**, and the population went 26 -> 30. The
oscillation is sandbox setup and teardown against 27G of space left over after
18G of fixed infrastructure, at a concurrency of roughly thirty.

**And the magnitude argument flips on its denominator, which is the one place
this entry disagrees with the entry above.** Research divided 13,845 bytes by
44G, got six orders of magnitude, and declined to claim its own line as the
cause -- correctly, and it was right to say so in the entry. But the population
is not its sample. It is **12,958 directories holding 851M**, sixty times the
count and sixty thousand times the bytes. Against *capacity* that is 1.9% and
still irrelevant. Against the *headroom* at this series' minimum, 1,571M, it is
**54%**. A fill is paid out of headroom and never out of capacity, so headroom
is the denominator that decides whether a cleanup is worth doing, and the same
851M is negligible or decisive depending only on which one you divide by.

The practical consequence is that research's line was worth fixing after all,
just not for the reason it had honourably declined to claim.

**And 9,944 of the 12,958 cannot be billed to anyone.** They carry `mkdtemp`'s
bare default name. The remaining ~3,000 carry prefixes -- `ledger-check` 767,
`relevance-sweep` 590, `attrs` 460, `check-evidence` 455, `image-metadata` 273  -- 
and those are the only ones a sweep could route to an owner. Research could
attribute its 355 solely because it read the code. **A prefix is the difference
between a leak with an owner and a leak without one**, and it costs one keyword
argument.

**Fixed here, for the one line that is ours.** `tools/skill_eval.py:command_env`
now builds at most one shim directory per process instead of one per call,
builds none at all when `python` already exists (the old body ran `mkdtemp()`
and `mkdir()` *before* testing `shutil.which`), names it `skill-eval-shim-*`,
and removes it at exit. Three tests added; all three fail against the old body  -- 
20 calls produced 20 directories and 20 distinct `PATH`s -- and pass against this
one. `command_env` had no test at all, which is why a defect this plain
survived: the function is correct in isolation and returns a working
environment every time, so only counting its artefacts can see it.

**What is still owed and whose it is.** Provisioning. 18G of fixed
infrastructure on a 45G volume leaves 27G for a steady state of thirty
concurrent sandboxes averaging 266M plus deploy checkouts at 421M each, and the
measured result is a volume that touches 100% several times an hour. No seat can
fix that by deleting, and this seat has no authority over the host's disk, so it
goes up with the asks already filed. The general lesson is the instrument one:
**when a resource oscillates faster than the interval between checking it and
using it, a pre-flight reading of that resource is not a safeguard -- it is a
second way to be wrong, and the comfortable direction is the one it fails in.**

Ban list checked on this entry.

**One last reading, taken at 07:02Z as this run closed, because it extends the
series in the direction that matters: 996M free, 98%.** That is below every one
of the 26 samples above it. So inside 29 minutes the volume read 4M, then
3,781M, then swung twice through a two-gigabyte band, and ended lower than it
started. Nothing in that sequence is a trend and every point in it is true,
which is the whole of this instance in one line: **a quantity this unstable has
no reading that a run can act on, only readings a run can quote.**

**It reached zero later the same day and the failure was a tool result rather
than a seat write (2026-11-02, skill seat, during the Parallax reading run).** The entry above ends on the reading that a
quantity this unstable has no actionable reading. This instance is the one
where it stopped being a reading at all: `df -h /tmp` reported **71M free,
100%**, and the thing that broke was the harness writing a child process's
stdout to its own task directory, `ENOSPC`, so a `git log` and `git status`
this run had already executed returned no output and exited 128 with the
command's output lost. Not a seat's artifact write, which every sample above
measured, and not a write the seat chose: it was the plumbing that carries
every command's result back to the agent. A seat cannot guard against that by
checking free space first, because the check itself needs the same pipe.

Two things that make this instance worth the lines rather than a twenty-eighth
sample. First, it is self-inflicted in a way the series had not recorded: this
run's own background full-suite test run was the writer, so a seat following
the ordinary advice to run its tests off the critical path is one of the ways
this volume reaches zero. Second, the recovery was trivial and that is the bad
news, not the good: deleting this run's own scratch and cache files took the
volume from 71M to 996M, roughly a gigabyte held by one seat's intermediate
files on a volume twelve seats share. Nothing deletes those at the end of a
run, so the floor the volume drifts toward is set by how many runs have ended
without cleaning up rather than by anything anybody is storing on purpose.

What this run did about it: stopped the background suite, deleted its own
scratch, re-ran the suite with `-p no:cacheprovider` so it writes no cache, and
recorded the number. The repair is still the engineer's and still unchanged.
