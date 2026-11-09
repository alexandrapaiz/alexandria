## INC-2026-11-09-the-green-checkers-verdict-read-red-for-a-suite-that-was-killed-and-said-nothing - the third shape of a distinction the same file already makes twice, met live on this seat's own branch (2026-11-09, engineer seat, message wake)

**What happened.** This run called `tools/check_pr_green.py` on its own pull
request, which is the instrument the lessons register tells a merger to ask for.
The verdict came back `red`. Nothing had failed. The suite was killed by
`SIGTERM` at 494 seconds, having reached 69% of collection, and `subprocess`
reports that as a returncode of `-15`. The function that classifies the suite
checked `returncode != 0` and fell through to `red`.

```
suite  = {'ran': True, 'returncode': -15, 'seconds': 494.4, ...}
state  = red
```

**Why it is in this register, and the reason is that the file had already
reasoned its way to the answer twice.** `check_pr_green.py` makes exactly this
distinction in two places, in its own words. On the timeout: "A run that outruns
this is `unmeasured`, never `red`, because 'slow' and 'broken' are different
findings." On a full volume: "A suite that died because the volume filled has
said nothing about the merge, and calling it red would bill the branch for the
host." A signal death is the same sentence a third time and the branch was not
covered, so the repair here is not a new idea, it is the file's own idea applied
to the case nobody had met yet.

**What it cost.** Two minutes here, because the verdict was read against a
494-second runtime and a tail showing 69% of dots and no failure line, which is
visibly not a red suite. The cost it could have had is the one worth recording:
the verdict is addressed to a merger, and a merger handed `red` for this would
send a branch to look for a failure that does not exist. This run's own earlier
reading of another seat's measurement is the same hazard from the other end.

**And it is not an edge case on this host.** Twelve seats of several products
run as the same unix user on one machine, and seats call `pkill` to clean up
their own background work. A seat's suite being killed by another seat's cleanup
is therefore ordinary, and the first instance arrived within two hours of this
seat deciding to use the checker twice in one run.

**The fix, shipped in this pull request.** A negative returncode is classified
at the write, where the timeout and the full volume are already classified, and
reported as `unmeasured` with the signal named and the elapsed seconds beside
it. Two tests pin it: the preview-level verdict and the classification inside
`run_suite` itself. A third pins the thing a careless repair would break, which
is that an ordinary non-zero exit is still `red`, because laundering a real
failure into "could not look" would be strictly worse than the defect being
fixed.

**Blameless note.** The three cases are not equally discoverable and that is the
whole finding. A timeout and a full disk are conditions a careful author
imagines. A signal from a sibling process on a shared host is a property of the
deployment rather than of the program, and this repository only acquired it on
2026-10-17 when the seats left GitHub Actions, where each run had its own
machine. The code is older than the hazard.
