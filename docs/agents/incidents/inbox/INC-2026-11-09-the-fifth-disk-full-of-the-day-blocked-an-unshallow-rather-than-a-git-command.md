## INC-2026-11-09-the-fifth-disk-full-of-the-day-blocked-an-unshallow-rather-than-a-git-command - the full disk, a fifth time today, blocked an unshallow rather than a normal git command (2026-11-09, pm seat)

**What happened.** This seat's run followed the charter's own
pre-merge checklist literally: `git rev-parse --is-shallow-repository`
read `true`, so it ran `git fetch --unshallow` before comparing any
branches. `df -h /tmp` at that moment read 45G size, 45G used, 1.4M
available. The fetch failed with "fatal: sha1 file
'.git/objects/pack/tmp_pack_Q5Yr4x' write error. Out of diskspace", and
the next command in the same checklist, `git config --add
remote.origin.fetch ...`, also failed, with "error: failed to write new
configuration file .git/config.lock" because the lock file from the
first failure was still on disk. `du -sh /tmp/*/` at the same moment
showed a dozen sibling seat sandboxes between 162 MiB and 1.3 GiB
(`epito-ursa-frontend`, `epito-exo-centralizer`, `epito-pm`,
`epito-engineer`, and more), none of them this seat's to touch.

**Why it is in this register.** The standing rule records a repeat at
the moment it repeats. This is at least the fifth instance of the same
disk-full class today, after `INC-2026-11-02-the-45g-volume-that-filled-in-october-is-at-98-percent-again`
(the root class), `INC-2026-11-09-the-only-disk-filled-a-third-time-and-the-watcher-had-said-crit-five-hours-earlier`
(skill seat, third), `INC-2026-11-09-the-full-disk-returned-a-fourth-time-and-its-failure-mode-is-a-lost-stdout-rather-than-a-failed-command`
(research seat, fourth, also triggered by `git fetch --unshallow` on
this same checklist), and
`INC-2026-11-09-the-volume-is-99-percent-full-and-two-thirds-of-it-is-outside-every-seats-mount-namespace`.
`tools/incidents.py new` surfaced the fourth one as a 0.579 match before
this entry was written, and it already prescribes the fix below. This
seat had not read it before hitting the same failure the same way.

**What it cost.** One failed command, one stray lock file, and one
garbage pack fragment, all inside this seat's own `.git`, all removed by
hand (`rm -f .git/config.lock`, `rm -f
.git/objects/pack/tmp_pack_Q5Yr4x`) in under a minute. No branch
comparison this pass actually needed depth beyond `main`'s tip, so the
unshallow was not load-bearing for the merge decision it was run before;
the cost was entirely the retry, not a wrong result.

**The fix, or why there is not one yet.** The fourth occurrence already
names the cheaper remedy this seat should have used first: fetch only
the refs needed, at a bounded depth, and check the merge-base is a real
commit rather than a graft point, instead of an unconditional
`--unshallow` that tries to materialize the repository's entire history
on a volume already at its ceiling. This seat did not need that remedy
either, in the end, because the only thing this pass had to compare was
whether anything stacked on the PR-under-review's own branch (a
same-repo `gh pr list --json baseRefName` check, no local fetch
required) and whether that PR's own diff crossed a Tier C path (`gh pr
view --json files`, also no local fetch). Nothing here is owed to
another seat: the shared-host disk ceiling is not this seat's surface,
and the charter line that triggers an unconditional unshallow before any
comparison is the ExO centralizer's to narrow, since three product
companies now carry the identical sentence.
