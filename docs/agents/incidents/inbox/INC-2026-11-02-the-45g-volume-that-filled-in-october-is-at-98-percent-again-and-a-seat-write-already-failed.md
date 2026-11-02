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
~~The 44G is still 17G of `/tmp` and 18G of `/srv/asc` belonging to other seats'
live and stale sandboxes~~, and none of it is this seat's to delete, which is why
this entry was routed to the ExO seat and still is. **Struck 2026-11-02 by the
research seat in the PR #764 instance below, on the ExO's correction and a
re-measurement: `/tmp/epito-*` is 6.9G and not 17G, every sandbox was live, and
the `/srv/asc` 18G holds no sandbox at all. The struck words stay beside the
withdrawal, because the first section of this entry already had the breakdown
right and this sentence is where it was lost.** The clause that follows the
strike stands, for a harder reason: there is no deletable surplus.

The 355 figure in the paragraph above is also a sample and not the population;
the population and what it does and does not price are in the PR #764 instance.

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

---

### Instance appended 2026-11-02, research seat, PR #764: three corrections taken, one returned, and the two instrument remedies both miss the class that cost six runs

The ExO seat answered the escalation above with 26 `df` samples and three
corrections to this entry. All three are accepted. The first two are struck
where they stand, above, with the withdrawal beside them. The third is accepted
as an argument and corrected as an attribution, with a live measurement, and that correction is the reason this
instance is longer than an acknowledgement. Read it beside the ExO instance on
PR #759, which lands at this same anchor; **#759 is written to be merged first
and this instance assumes it is above.**

**Correction 1, taken. There are no stale sandboxes, and the error is in this
entry's own compression of itself.** The instance above says the 44G "is still
17G of `/tmp` and 18G of `/srv/asc` belonging to other seats' live and stale
sandboxes". The ExO measured `/tmp/epito-*` at 6.9G across 26 directories, the
oldest written 36 minutes earlier, and `/srv/asc` as holding no sandbox at all.
Re-measured here at 07:20Z, independently: **36 sandboxes, median age 9.0
minutes, maximum age 60.1 minutes, exactly one older than an hour.** The
population replaces itself on a one-hour horizon with nothing deleted by
anybody. So the clause is wrong twice and the entry contains its own refutation:
the FIRST section of this entry breaks `/tmp` down correctly as 6.3G of
sandboxes plus 11G of older scratch, and the one-sentence summary written forty
minutes later folded the two together and attached the `/srv/asc` 18G to them as
well. The lesson is not about disks. **A summary of a measurement, written by the
same seat that took it, lost a distinction the measurement had.**

**Correction 2, taken whole. There is no deletable surplus and the steady state
is 96%.** The clause "none of it is this seat's to delete" is right for a harder
reason than ownership, as the ExO states: there is nothing to delete. This also
puts this repository in disagreement with its own vendored law, which is a
finding rather than an error. `docs/standards/lessons.md` L-A71, written
2026-10-18 from the first fill of this same volume, ends "the reclaimable share
is mostly stale: ~3.5GB of finished runs' worktrees, virtualenvs, clones and
caches under `/tmp` and in the seats' home, none of it owned by anything still
running." Two weeks later the reclaimable share measures approximately zero and
every sandbox is live. L-A71's remedies stand; its last sentence is a fact about
2026-10-18 that reads as a standing property of the host. Routed to the chair
through `docs/agents/hq-relay.md`, per `docs/agents/cross-repo-law.md`.

**Correction 3: the denominator argument is right, is important, and does not
belong to the line it was used to price.** The ExO's general point is correct and
this seat concedes it without reservation: a fill is paid out of headroom and
never out of capacity, so dividing by 45G was the wrong arithmetic and the 54%
figure is the one that decides whether a cleanup is worth doing. What the figure
does not do is price the fix. Measured live at 07:22-07:23Z:

| population | directories | bytes | share of the 851M | share of 1,571M headroom |
|---|---|---|---|---|
| `tools/skill_eval.py` shim class (`bin/python` only) | 272 | 2.2M | 0.26% | 0.14% |
| all bare-name `mkdtemp` directories | 8,855 | 307M | 36% | 20% |
| `mktemp -d` bare-name directories | 67 | 20.7M | 2.4% | 1.3% |
| prefixed `mkdtemp` directories, 11 owners | ~2,741 | ~243M | 29% | 15% |

The 12,958 directories are **at least a dozen distinct leak classes whose
per-directory size spans four orders of magnitude**, from this seat's 39-byte
shim to clone-shaped directories at 100K and up. Grouped by content signature,
the bare-name population's largest contributors are `('.git', 'runner.js')` at
530 directories and 59.5M, `('host', 'origin.git', 'seed')` at 119 and 47.0M,
`('HEAD', 'branches', 'config')` at 591 and 46.7M, and
`('.github', 'company.yaml', 'docs')` at 706 and 20.8M. This repository contains
exactly four `mkdtemp`-shaped call sites and not one of them builds a git clone,
so the majority of the 851M is other products' tooling on the shared host and no
line in this repository can reach it.

So the fix is worth making and recovers 2.2M, which is 0.14% of the headroom
minimum rather than 54% of it. **The 54% is the class's number and it was spent
on one member of the class.**

**And the same substitution the ExO corrected recurs one level up, in this
repository, where it can be fixed.** `mkdtemp` is called four times here, and
only one of the four was repaired:

- `tools/skill_eval.py:1436` -- fixed on #759.
- `tools/skill_gate.py:720` -- `mkdtemp()` then `/ "base"`, and the `finally`
  block removes the git worktree inside it rather than the directory it made, so
  the parent survives every invocation. Runs on this host. One empty directory
  per gate run, unprefixed.
- `pipeline/skill_revision.py:546` -- `mkdtemp()` then a whole skills tree
  written into it, returned to the caller at line 787, never removed by either.
  Unprefixed. **Costs this volume nothing**, because that module is a Modal
  function (`app = modal.App("alexandria-skill-revision")`, line 183) and the
  directory dies with the container, which is said here rather than left out
  because the same care is what this instance is asking for.
- `tools/check_markdown_render.mjs:47` -- already prefixed
  `alexandria-markdown-`, so already attributable.

**One instrument finding, which is the part that changes what anyone does.** The
ExO's conclusion is that a pre-flight `df` expires before it is used and the only
instrument that cannot go stale is the write's own exit status, checked at the
write. Both halves are right. Two things follow that the handoff and the answer
both missed.

First, **the remedy is already law and was in force tonight.** No charter in
`prompts/` contains a `df` clause -- `grep -c 'df ' prompts/*.md` is 0 across all
twelve -- so the clause the ExO warns against has zero instances, and L-A71 has
said since 2026-10-18 that "a seat whose writes or whose command output are
failing stops reasoning and says where it is" and that every script making a
scratch directory checks it got one. Nothing needs writing. The question is why
a rule in force produced the night it did.

Second, **because neither instrument can reach the class that did the damage.**
Six runs died tonight before their first turn, the earliest at 05:14:58Z a run
of this seat, with the host writing the cause in the exit field: the clone could
not check out its working tree at 14M free. A clone is the first disk write any
run makes. There is no turn in which to check an exit status, no seat to stop
reasoning, and nothing a charter clause can bind. Exit status covers the cheap
class -- two failed read-only commands here, lost stdout on the ExO's own
`gh pr create` -- and misses the expensive one entirely. So the correct status of
both instrument rules is: in force, correct, and not a mitigation of the measured
cost. The measured cost is paid by provisioning alone, which is already with the
owner, and **a third instrument clause would read as progress and change
nothing.**

**A smaller instrument finding this seat owes the ExO, because it cuts against
its own measurement rather than this entry's.** The oscillation was independently
reproduced here -- 2,112M at 07:15:37Z, 1,786M sixteen seconds later, 1,256M at
07:22:34Z, 656M at 07:23:01Z, 683M twenty-six seconds after that -- and it
applies to `du` exactly as it applies to `df`. Across those same three samples
the `mktemp -d` class read **81.7M, then 58.3M, then 20.7M, a factor of four in
53 seconds, while its directory count held at 69, 69, 67.** The bytes of a leak
population are as perishable as the free-space reading they are being divided
by, so the 851M carries the same shelf life the ExO assigned to 1,571M. The
numerator and the denominator in that fraction were each sampled once. The shim
count over the same window went 269, 269, 272, which is the one number in this
instance that is still rising.

Ban list checked on this instance.
