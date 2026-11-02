## INC-2026-11-02-the-only-disk-filled-again-and-a-seat-run-died-at-clone - the host's single 45G volume reached 100% for the second time in ten days, the watcher had said `crit` seventy minutes earlier, one seat's run died before its first turn and this seat's own tooling hit ENOSPC mid-run (2026-11-02, security seat, message wake)

**What happened.** At roughly 05:21Z a tool call in this run failed with
`the temp filesystem ... is full (0MB free)`, because writes to the harness
scratch directory returned ENOSPC. `df` at that moment reported the host's only
data volume, `/dev/sda1`, 45G in size, with **4.6M free**. Four readings over
the following five minutes, with no action taken by this run:

| time (UTC) | free | use |
| --- | --- | --- |
| ~05:21 | 4.6M | 100% |
| 05:23:48 | 1.5G | 97% |
| ~05:26 | 689M | 99% |
| ~05:27 | 698M | 99% |

The volume is not merely full once, it is running with no headroom at all,
oscillating between zero and about a gigabyte and a half as seat checkouts are
created and reaped. Six `asc-green-*` directories holding 1.45G disappeared
between two of those readings, and the count of `/tmp/epito-*` seat checkouts
rose from 24 to 27 over the same minutes.

**It had already been detected.** `/srv/asc/state/diskwatch.last` contains
`crit 1793592679`, which is **2026-11-02T04:11:19Z**, seventy minutes before
this run's ENOSPC. So the host's own watcher classified the volume critical and
the volume went on filling.

**It had already cost a run.** `/srv/asc/state/.epito/audit.jsonl` records
`{"ts":"2026-11-02T05:14:58Z","agent":"alexandria-research","action":"run.end",
"exit":"clone","durationMs":24000}`. That seat died in 24 seconds at the clone
step, inside the window above, and `clone` is the only exit of its kind in all
11,599 rows of that log, which covers 2026-09-24 to today. The timing places it
in the full-disk window and the rarity makes coincidence the less likely
reading, though the log records the exit and not its errno, so this is a strong
inference rather than a proof.

**Where the space is.** `/tmp` 17G, `/srv/asc` 18G, `/usr` 3.6G, of 45G.
`/var/lib/docker` is now 4.0K.

**Why it is in this register.** The standing rule requires a repeat at the
moment it repeats, and this is the same volume failing the same way for the
second time in ten days. The first is recorded inside
`INC-2026-10-24-the-observability-runtime-was-retired-with-no-local-record`:
on 2026-10-23 `langfuse-clickhouse-1` put 14G of one container's logs on this
same 45G volume under Docker's default `json-file` driver with no `max-size`,
and Postgres died with `PANIC: could not write to file ... No space left on
device`. The owner's standing condition is that Langfuse stays stopped until it
is rebuilt with a disk budget.

**That condition was met and the volume filled anyway, which is the thing worth
carrying.** Docker now holds 4.0K, so the 2026-10-23 filler is genuinely gone.
The space it freed was absorbed by ephemeral seat checkouts, which have grown to
17G and which no budget governs either. The remedy was scoped to the filler
rather than to the volume, so the second filler met no limit, and a third will
not either. **A disk budget given to one writer on a shared volume is not a
disk budget.**

**What it cost.** One seat run dead before its first turn. One tool call failed
in this run, which is the only reason the condition was noticed at all, since
the watcher's `crit` goes to a file nothing reads on a seat's path. Both of the
failure modes are bad in the same way: the clone death is loud, and the ENOSPC
write is silent, because a truncated write succeeds from the writer's point of
view. This file's sibling finding this run, the single corrupt line in
`audit.jsonl`, is what a truncated append looks like after the fact.

**The fix, or why there is not one yet.** Nothing is fixed here, because the
volume, the reaper and the watcher are all the host's and none of them is in
this repository. Three things are owed, and the first is the only urgent one.

1. **Reclaim headroom now.** 698M on the volume every seat clones into will kill
   more runs within the hour.
2. **A budget on the volume rather than on a writer.** A cap on total
   `/tmp` seat checkouts, a reaper with a retention the roster can predict, or a
   separate volume for seat scratch.
3. **Make `crit` reach a reader.** `diskwatch` wrote the right verdict at the
   right time into `/srv/asc/state/diskwatch.last`, where no seat's charter and
   no gate has ever looked. That is incident 20's shape exactly: a register that
   decides something gets written down, with nothing that decides it gets
   checked before it matters.
