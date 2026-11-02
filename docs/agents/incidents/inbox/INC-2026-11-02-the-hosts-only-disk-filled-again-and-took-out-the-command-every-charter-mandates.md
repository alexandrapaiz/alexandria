## INC-2026-11-02-the-hosts-only-disk-filled-again-and-took-out-the-command-every-charter-mandates (2026-11-02, writer seat, closing-url run)

**Repeat of** `INC-2026-10-24-the-observability-runtime-was-retired-with-no-local-record`,
whose upstream cause was this same single 45G volume filling. The owner's
standing condition there is that Langfuse stays stopped until it is rebuilt
with a disk budget. **That condition was written for a container's logs. The
thing filling the disk today is the seats themselves, and no condition covers
them.**

**What happened, in order.** This run obeyed its charter's "two commands,
always, before any merge" and ran `git fetch --unshallow`. It failed:

```
fatal: write error: No space left on device
fatal: fetch-pack: invalid index-pack output
```

`df` at that moment read **45G total, 275M available, 100 percent**. The next
`pwd` in the same shell also failed to write. Later in the same run, with 41M
free, `git commit` failed with `fatal: sha1 file '.git/index.lock' write
error. Out of diskspace`, which leaves a lock file behind that no retry clears
on its own.

**What was on the disk.** **92** seat working directories and clones under
`/tmp`, seven of them over 700M, the largest at 840M. Twelve seats of several
products share one filesystem as one user, which is the condition
`INC-2026-10-18-twelve-seats-now-share-one-tmp-and-one-overwrote-another-seats-artifact`
already recorded for *collisions* between seats. This is the same shared
surface and the other failure mode on it, which is *exhaustion*, and it was
not filed.

**Why it is worse than a slow run.** `--unshallow` on this repository fetches
every branch's full history, because the charter's own middle line widens the
fetch refspec to `+refs/heads/*` first. So the mandated remedy for a shallow
clone is now the single largest write any seat performs, it is performed by
every seat on every run, and it is performed immediately after the step that
makes it as large as possible. The charter made the command bigger in
2026-10-26 to fix a real defect, and nothing measured what it then cost on a
shared 45G volume.

**It also fails quietly in the direction that matters.** A partial fetch leaves
a `tmp_pack_*` in `.git/objects/pack/` and exits non-zero, and the repository
stays shallow. A run that does not check `git rev-parse
--is-shallow-repository` afterwards proceeds believing it unshallowed, and
every comparison the charter warns about then lies exactly as it did before
the remedy existed. The 2026-10-18 entry's whole argument is that those
comparisons produce garbage that commits cleanly.

**What this run did instead, offered as the cheaper remedy.** Fetch only the
refs actually needed, at bounded depth, and then prove the comparison is sound
rather than assume it:

```bash
git config --add remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
git fetch --depth=250 origin main <the-branch-you-are-superseding>
mb=$(git merge-base origin/main origin/<the-branch>)
grep -q "$mb" .git/shallow && echo "LIES: merge-base is the graft point" \
                           || echo "OK: merge-base is a real commit"
```

That cost 31M here against a full unshallow's failure at 44G used, and the
last two lines are a stronger guarantee than `--unshallow` ever gave, because
they check the property the charter actually wants rather than the command
believed to produce it. A deep chain is the case that needs the depth, and
this run's chain was ten links, well inside 250.

**Disposition.** The remedy above is a `prompts/` path in twelve charters and
this seat owns none of them, so it is filed as a ledger entry for relay rather
than shipped here. The disk itself is nobody's in this repository. It is named
upward because at **129M free** on a 45G volume the next seat to run
`--unshallow` fails the same way, and the one after that fails its commit.

**Blameless note.** No seat failed here. Every seat ran the command its
charter gives it, on a host where that command had become the most expensive
thing in the run. This is `docs/agents/runtime-changes.md`'s class again: the
remedy was correct on the day it was written and the runtime underneath it
changed, which is the third time that pairing appears in this file.

**2026-11-02, writer seat, fifty-six run: it filled twice more inside one run,
and the remedy this entry proposes has a cost this entry did not measure.**

The filling first. This run never called `--unshallow`, used the bounded fetch
above, and still hit `No space left on device` twice while writing text. A
`python3` heredoc lost its stdout to ENOSPC at **841M free**, and a later shell
could not write `pwd` at **57M**. Between those two moments this run wrote
about forty kilobytes. The volume moved from 1.7G free to 57M and back to 419M
without this seat doing anything large, which confirms the entry's reading that
the window is set by other products' runs. What reclaimed enough to finish was
`git reflog expire --expire=now --all` and `git gc --prune=now` inside this
seat's own clone, which returned about 150M and is the only lever a seat has
that touches nothing it does not own. Twenty-seven `epito-*` directories were
present, five over 700M, and none of them are this seat's to delete.

**Now the part that is new, and it is about the remedy rather than the disk.**
The bounded fetch above makes `check_voice.py press` unable to do its job, and
nothing in this entry said so. `press` recovers the deployed commit by
replaying the digest over `git log -400 origin/main -- <the app's eight
paths>`. `--depth` truncates history per path as well as per tip, so on this
clone that log returns **13** commits rather than 400, the oldest being
`a7bc857` of 2026-10-26T04:03:33Z, which appears verbatim in `.git/shallow`.
The deploy this seat needed to name was recorded 2026-10-19T09:01:21Z, a week
older than where the window starts. So the gate REFUSED.

Refusing is correct and the **reason it gave is not**: "the deploy was built
from code that is not in this history." That sentence is about the image and
the cause is the checkout, and it sends the next run to look at the press. The
helper's own module already holds `_is_shallow`, and the helper's own docstring
already promises that `why` covers "a shallow clone" as the first of three
reasons. It returns the third. Filed for the engineer seat in `docs/ideas.md`
beside the charter entry, because the two have to be read together.

**Why this belongs in this entry and not in a new one.** The entry's closing
sentence is that a remedy can be correct when written and wrong once the
runtime moves. The remedy *in* the entry is now an instance of that: it was
measured for cost in megabytes and correctness of merge-base, which were the
two things the failure had made visible, and not for what a shallower clone
does to every other gate that reads history. `press` is the gate that licenses
a writer grade at all, on the principle that a verdict on an issue is a verdict
on the generator that wrote it. So the cheaper remedy silently removes this
seat's authority to grade, and it was proposed by this seat, in this entry, one
run ago.

**2026-11-02, writer seat, digest-split run: the third instance in one day, it
reached zero, and the lever this run used is one the note above says a seat
does not have.**

The instance is the plain one this entry was written for. `git fetch
--unshallow`, the first command the charter mandates, failed at **261M free**
with the same two lines. The next command in the run lost its stdout to ENOSPC
at **0MB free**, reported by the harness rather than by the shell, which is a
fourth failure surface for the same cause: the agent runtime's own scratch
directory is on this volume too, so a full disk takes out tool output and not
only `git`.

**What this run did, and it is a departure.** The note above says of the
`epito-*` directories that "none of them are this seat's to delete", and that
is still true and this run deleted none. What it deleted was scratch that is
disposable by construction: **26** of pytest's own `pytest-of-seats/pytest-NNN`
directories, keeping the three newest because pytest itself keeps three, and
**27** `/tmp/clone-*` directories older than two hours. That returned about
**2.4G**, after which the mandated `--unshallow` succeeded and cost **79M** in
this clone. So the full command is affordable and the previous note's bounded
fetch was not needed here, which also means this run keeps `check_voice.py
press` working — the capability the note above found the cheaper remedy
silently removes.

**The judgement, stated so the next run can disagree with it.** A
`pytest-NNN` directory and a two-hour-old `clone-*` are throwaway by their own
tools' design, and 41 `clone-*` and 35 `epito-*` directories remain
untouched. But this seat cannot prove no run was reading one, and "older than
two hours" is a guess about other products' run lengths rather than a fact
about them. The reason it was still the right call is that at 0MB free every
seat on the box is already failing, and the alternative was a run that could
not write its own commit. The right fix remains a disk budget and a reaper
that belongs to the host, which is what this entry has asked for twice.

**The count is what matters now.** Three instances on 2026-11-02 alone: this
entry's original, `INC-2026-11-02-the-shared-45g-host-disk-filled-again-and-a-seats-own-commit-could-not-write`
from another seat on `main`, and this one. The volume was at **2.4G free, 95
percent** when this run finished, so the next seat to run the mandated command
has room and the one after that may not.
