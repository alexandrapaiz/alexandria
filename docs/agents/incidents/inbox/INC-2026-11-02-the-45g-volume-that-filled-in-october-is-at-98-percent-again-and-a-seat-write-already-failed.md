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
