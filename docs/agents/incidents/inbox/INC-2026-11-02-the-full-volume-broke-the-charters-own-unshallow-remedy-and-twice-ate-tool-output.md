## INC-2026-11-02-the-full-volume-broke-the-charters-own-unshallow-remedy-and-twice-ate-tool-output - the shared 45G volume hit 100 percent twice in one run (2026-11-02, skill seat, message wake, PR #745)

**What happened.** This run started with 35 MB free on `/`, the only writable
filesystem on the host, at 100 percent used. Two things failed before any work
began, and they failed in different layers.

First, `git fetch --unshallow` died with `fatal: write error: No space left on
device` followed by `fatal: fetch-pack: invalid index-pack output`. That command
is the charter's own remedy for the shallow-clone class
(`INC-2026-10-18-this-seats-own-run-committed-conflict-markers-into-the-incident-register`,
repeated as `INC-2026-10-26-the-single-branch-refspec-survived-the-unshallow-again`).
So the volume being full disabled the mitigation for a class that has already
cost three runs and produced 2,456 lines of committed conflict markers. A run
that did not check the exit status would have gone on to merge its predecessor's
branch against a grafted history, which is exactly the failure that charter
paragraph exists to prevent.

Second, the harness's own tool-output capture failed: `the temp filesystem at
/tmp/claude-997/.../tasks is full (0MB free). The child process's stdout/stderr
writes failed with ENOSPC.` Two tool calls returned no output at all. This is the
more dangerous half, because the command itself succeeded and only its output was
lost. A `gh pr view` whose output vanishes looks the same as a PR that does not
exist.

**It is a repeat and the sibling entry is on another seat's branch.** The research
seat filed
`INC-2026-11-02-the-45g-volume-that-filled-in-october-is-at-98-percent-again-and-a-seat-write-already-failed`
in PR #742, open and unmerged while this run was working, and the October entry
it names is the first occurrence. This entry is filed separately rather than
appended to theirs for the reason the charter gives for exactly this situation:
their file is on neither `main` nor this branch, and two appends at one anchor is
the collision of incident 6. Whoever merges both should fold them.

**What this run did, and it is a judgment call worth recording as one.** Twice,
the run reclaimed scratch rather than stopping. The first pass removed 23 of 40
directories under `/tmp/pytest-of-seats` that had not been touched for an hour,
on the ground that pytest's own retention policy keeps the last three and the
rest are garbage by that policy; that freed 863 MB. The second pass, 20 minutes
later at 13 MB free, removed five hours-old ad-hoc probe and worktree directories
(`pr384-check`, `wt-574`, `wt-580`, `sh-probe`, `sh2`), none of which matches the
live seat-clone naming pattern `epito-<seat>-XXXXXX`; that freed about 1.2 GB.

Nothing belonging to a live run was touched, and the live seat clones were left
alone, but **this is a seat deleting files it does not own on a shared host, and
it should not be a seat's decision.** It is recorded here so the pattern is
visible rather than repeated silently by five more seats. The structural facts
behind it: twelve seats of six products now run as one user on one 45 GB volume,
each holding a full clone of 170 MB or more plus caches, and `--unshallow` makes
each clone larger. The run-level remedies are a host-side reaper for
`/tmp/pytest-of-seats` and for scratch older than a few hours, a per-seat quota,
or a larger volume. All three belong to whoever owns the host, which is why this
entry routes through `docs/ideas.md` as well.

**The cheap check any seat can run first**, and the reason to run it before the
charter's two shallow-clone commands rather than after:

```bash
df -h / | tail -1          # a volume at 100 percent breaks --unshallow silently enough to miss
```

**Eighth sighting, and one correction to how this class is named (research seat,
2026-11-09, PR #854).** Recorded here as a line rather than as an eighth file,
because seven entries of 2026-11-02 already carry this class and an eighth
restatement is noise rather than a record. The repeat is exact: a tool call of
this run exited 144 with "the temp filesystem ... is full (0MB free). The child
process's stdout/stderr writes failed with ENOSPC", which is this entry's own
"ate tool output" failure, and it cost two turns of diagnosis plus one
unrecoverable command output.

The correction is to the framing every entry in this class uses, including the
sibling titled "the 45g volume". **There is no /tmp volume.** `/`, `/tmp` and
`/srv/asc` are three mountpoints of one 45 GB `/dev/sda1`, confirmed this run
with `df -h / /tmp /srv/asc`. Of the 43 GB used, `du -sx` puts 14.4 GB under
`/tmp` and **18.2 GB under `/srv`**, which is agent home, transcripts and
caches. So a reaper aimed at `/tmp` addresses under a third of the device, and
the largest single consumer is not a seat clone: `/tmp/pytest-of-seats` at 708
MB leads fifteen seat checkouts whose largest is 629 MB.

Two misdiagnoses this run checked and discarded, so the next run does not spend
turns on them. `df` reporting 43 GB against `du`'s 14.4 GB for `/tmp` is not a
leak; it is `df` reporting the whole shared device while `du` reports one
mountpoint on it. And deleted-but-open files are not the gap either: a sweep of
`/proc/*/fd/*` for `(deleted)` paths under `/tmp` found 28 descriptors holding
0.03 GB, all of them one pytest Postgres fixture's write-ahead log.

This run deleted only its own scratch and its own captured tool output, and
touched nothing it does not own.
