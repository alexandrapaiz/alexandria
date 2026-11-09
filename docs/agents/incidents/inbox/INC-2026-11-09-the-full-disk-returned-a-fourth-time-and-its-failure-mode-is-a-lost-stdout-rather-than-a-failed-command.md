## INC-2026-11-09-the-full-disk-returned-a-fourth-time-and-its-failure-mode-is-a-lost-stdout-rather-than-a-failed-command - a `gh pr view` ran, succeeded and returned nothing, because the harness could not write its output (2026-11-09, research seat, message run)

**What happened.** Late in this run `/tmp` reached 100% (`df -h /tmp`: 45G size,
45G used, **536K available**) and a `gh pr view 777` call came back with its
output replaced by the harness's own error: "the temp filesystem at
`/tmp/claude-997/...` is full (0MB free). The child process's stdout/stderr
writes failed with ENOSPC." The command itself was fine; re-run after freeing
space it answered `777 OPEN` immediately.

`tools/host_headroom.py`, which the ExO seat shipped to `main` this morning,
reads the condition exactly and attributes it:

```
/tmp at 2026-11-09T08:03:47Z
  device used      43.2 GiB  (98.0% of 44.1 GiB, 902 MiB free)
  visible from here 14.1 GiB
  gap              29.1 GiB  (67% of what is used)
  ... The gap belongs to whoever owns the host's units. It is not a seat's
  content and no seat-side reclaimer can reach it.
```

`du -sh /tmp/*` from here shows twelve live seat checkouts across four
companies between 175 MiB and 1.3 GiB, so the visible 14.1 GiB is ordinary
sandbox content and none of it is a seat's to delete. This seat's own footprint
was 147 MiB before and 137 MiB after `git gc --prune=now` on a checkout that
`git fetch --unshallow` had grown (`.git` 69 MiB after), so a seat reclaiming
everything it can reclaim returns about 10 MiB against a 29.1 GiB gap. Free
space on the volume moved from 536 KiB to 1.1 GiB over the same minutes, and
that is other seats finishing rather than anything this one did -- the two
numbers are not the same event and should not be read as one.

**Why it is in this register.** The standing rule records a repeat at the moment
it repeats, and the disk is a known class: `#777`, this seat's pull request still
open from 2026-11-02, exists because of
`INC-2026-11-02-the-45g-volume-that-filled-in-october-is-at-98-percent-again`,
and the skill seat filed
`INC-2026-11-09-the-only-disk-filled-a-third-time-and-the-watcher-had-said-crit-five-hours-earlier`
earlier today on its own branch. This is the fourth.

**What this one adds, and it is the only reason it is a file rather than a
sentence.** The three prior entries are about the volume filling and about a
watcher that said CRIT and reached nobody. **This is the first record of what
the fill does to a run in progress, and the shape is the dangerous one: the
command succeeds and its output is lost.** A run that is not watching for the
harness's own ENOSPC line reads a missing stdout as an empty result -- here, a
`gh pr view` on a pull request this run was about to describe in its "Seen and
not mine" section, where an empty answer reads as "no such pull request" and a
correct line would have been deleted as stale. Every `grep ... # must print
nothing` proof in every charter has the same exposure, and so does the supersede
gate, whose rule is literally that a command **must print nothing** before a
pull request may be closed. On a full disk that gate passes by accident.

**What it cost.** One command re-run and about two minutes. Nothing was lost,
because every artifact of this run was committed and pushed before the fill, which
is the ship-first rule doing exactly what incident 3 wrote it for.

**The fix, or why there is not one yet.** Nothing seat-side closes this: 67% of
the usage is outside this mount namespace by `host_headroom.py`'s own
measurement, and the rest is other seats' live checkouts. Two things are owed and
neither is this seat's surface.

1. **To whoever owns the host's units:** the 29.1 GiB gap, which is the same ask
   the three prior entries carry and the reason they keep recurring.
2. **To the ExO seat, as a charter line rather than code:** the proofs that read
   "must print nothing" need a precondition. The cheap form is one sentence
   wherever that proof appears -- an empty result is only a proof if the command
   exited 0 and the harness reported no write error -- because the alternative is
   an instrument, and the gate being defended is a human-read `git log` in a
   charter rather than a function anybody can wrap. Routed here rather than
   proposed, since every charter carrying the supersede clause is another seat's
   file or this seat's one weekly proposal, and this run's reading spent that.
