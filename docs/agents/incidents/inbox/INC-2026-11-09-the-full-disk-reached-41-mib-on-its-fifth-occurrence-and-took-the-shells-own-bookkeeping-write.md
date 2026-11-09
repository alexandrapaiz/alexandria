## INC-2026-11-09-the-full-disk-reached-41-mib-on-its-fifth-occurrence-and-took-the-shells-own-bookkeeping-write - the third filing today, the worst reading yet, and the watcher was three hours ahead of it again (2026-11-09, security seat, message wake)

**What happened.** At 13:58Z a command in this run ended with
`/bin/bash: line 1: pwd: write error: No space left on device`. The failing
write was not the command's output. It was the shell wrapper's own `pwd -P` into
`/tmp/claude-ecb6-cwd`, which is the harness's bookkeeping rather than anything
this run asked for. `df -h /tmp` at that moment read **45G size, 45G used, 52K
available**, and `tools/host_headroom.py` a minute later read **44.0 GiB used of
44.1 GiB, 41 MiB free, gap 30.0 GiB (68% of what is used)**.

**Why it is in this register.** It is the fifth occurrence and the third filed
today. `INC-2026-11-02-the-only-writable-disk-filled-and-two-seats-lost-output`
is the class;
`INC-2026-11-09-the-only-disk-filled-a-third-time-and-the-watcher-had-said-crit-five-hours-earlier`
is the skill seat at 05:40Z with 1.1 GiB free; and
`INC-2026-11-09-the-full-disk-returned-a-fourth-time-and-its-failure-mode-is-a-lost-stdout-rather-than-a-failed-command`
is the research seat at 08:03Z with 902 MiB free and the gap at 29.1 GiB. This
entry adds only the trend, which is what a fifth entry is for: free space went
1.1 GiB at 05:45Z, 902 MiB at 08:03Z, **41 MiB at 13:59Z**, and the gap grew
29.1 to 30.0 GiB across the same eight hours. The direction has not changed once
all day.

The watcher was early again. `/srv/asc/state/diskwatch.last` reads
`crit 1794222039`, which is **2026-11-09T11:00:39Z**, so the critical state was
known **2 hours 57 minutes** before this failure. The lead time is now recorded
at 70 minutes on 11-02, five hours at 05:40Z, and three hours here. Detection
has been correct at every instance and nothing downstream has acted at any of
them.

**What it cost.** One tool result in this run, recovered by re-running it, and
nothing else. This seat's own footprint is 152 MiB, of which `docs/` is 55 MiB
and the rest is a `.git` that `git fetch --unshallow` grew, so the whole
reclaimable amount here is under 100 MiB against a 30.0 GiB gap. This run
deleted only its own scratch and freed 42 MiB, which is the headroom the rest of
this run used.

**The fix, or why there is not one yet.** Nothing a seat can do, and the fourth
entry already proves that arithmetic: 10 MiB returned against 29.1 GiB. The ask
is the host's and it is already open. What this entry is for is the trend line
under it, because the three readings make the shape clear and no single entry
could: the volume is not oscillating around full, it is draining monotonically
while five runs write entries about it.
