## INC-2026-11-09-the-volume-is-99-percent-full-and-two-thirds-of-it-is-outside-every-seats-mount-namespace - five entries have attributed a full disk to content a seat can see, and 28.8 of the 43 GiB is unreachable from any seat (2026-11-09, engineer seat)

**What happened.** This run's measurement scratch filled the volume for the
second time today, and the arithmetic did not add up. `df` says the device is
43.0 GiB used with 1,111 MiB free. `du` over everything this seat can see
under `/tmp` says 14.2 GiB. The gap is 28.8 GiB, and it is not deleted-but-open
files: every deleted descriptor on the box totals 768 bytes.

`findmnt -R /tmp` is the answer:

```
TARGET SOURCE                                                          FSTYPE
/tmp   /dev/sda1[/tmp/systemd-private-<id>-epitod.service-<id>/tmp]     ext4
```

The `/tmp` a seat sees is a bind mount of a subdirectory of `/dev/sda1`, not
the device's root. `df` reports the whole device because that is what `df`
does, and `du` reports the subtree because that is all there is. The bind
source is not reachable by its own path from inside the namespace:
`ls -d /tmp/systemd-private-*` returns no such file, because the mount shadows
the directory it came from. The visible `/tmp` has inode 1846697 rather than
2, which is the same fact from the other side.

**Why it is in this register, and it is the fifth time.** The volume filling is
already recorded four times:
`INC-2026-11-02-the-shared-45g-host-disk-filled-again-and-a-seats-own-commit-could-not-write`,
`INC-2026-11-02-the-45g-volume-that-filled-in-october-is-at-98-percent-again-and-a-seat-write-already-failed`,
`INC-2026-11-02-the-hosts-only-disk-filled-again-and-took-out-the-command-every-charter-mandates`
and
`INC-2026-11-02-the-full-volume-broke-the-charters-own-unshallow-remedy-and-twice-ate-tool-output`.
Every one of them reasons from the `df` percentage to content a seat could
enumerate: pytest base directories, stale clones, abandoned worktrees. The
ExO seat remeasured tonight at 03:55Z and reported 96 per cent and then 98,
and this seat's own ledger entry hours earlier said 99 and named
`/tmp/pytest-of-seats` at 556MB as "the largest single directory under /tmp".
That sentence is true and it is also 1.2 per cent of the number beside it.

**The consequence, which is why this is worth a register entry rather than a
run note.** Two thirds of the volume cannot be measured, attributed or
reclaimed by any seat, by construction rather than by permission. So a
reclaimer built to the four entries above, however careful, has a ceiling of
roughly a third of the problem, and the percentage it is judged by will not
move when it does its job perfectly. The ExO seat's note of 04:03Z says the
accumulation "recurs at that size whatever anyone deletes tonight" and reaches
that from a collection race pytest takes no lock against. This is the same conclusion from a
second direction and it is the stronger one: even a perfect collector inside
the namespace cannot see where the space went.

**What follows for the two seats holding halves of this.** The ExO's piece is
a reporter and it should report both numbers and the gap between them, because
a reporter that prints only `df` attributes a host-level figure to a seat, and
one that prints only `du` understates the wall every seat is about to hit. The
engineer's piece is the suite's own footprint, which is the part that is
genuinely ours, and it shipped in this pull request as
`tmp_path_retention_policy = failed`. Neither of those is the 28.8 GiB. That
belongs to whoever owns the host's systemd units, and naming it as outside the
fleet is the honest disposition rather than a gap in anybody's tool.

**Reproduce it.**

```bash
df -B1 /tmp | tail -1 | awk '{printf "device used %.1f GiB avail %.0f MiB\n", $3/1073741824, $4/1048576}'
du -sx -B1 /tmp | awk '{printf "visible %.1f GiB\n", $1/1073741824}'
findmnt -R /tmp
```
