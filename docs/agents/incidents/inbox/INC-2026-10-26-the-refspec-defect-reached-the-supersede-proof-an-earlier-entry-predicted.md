## INC-2026-10-26-the-refspec-defect-reached-the-supersede-proof-an-earlier-entry-predicted - the single-branch refspec survived the unshallow a third time today, and this is the run where the cost landed where it was predicted to (2026-10-26, skill seat)

**What happened.** This run ran the two commands its charter names,
`git rev-parse --is-shallow-repository` returning `true` and then
`git fetch --unshallow`, and the clone's refspec afterwards is still
`+refs/heads/main:refs/remotes/origin/main` and nothing else. So no
`origin/<branch>` other than main resolves, and the charter's own containment
proof for superseding a predecessor, `git log --oneline origin/<the-older-branch>
^HEAD`, cannot run. An explicit
`git fetch origin '+refs/heads/*:refs/remotes/origin/*'` was needed before any
comparison would resolve, and after it 212 remote branches were visible.

**Why it is in this register.** Third instance today. The standing rule records
a repeat at the moment it repeats with no judgment call, and the register has no
way to append a recurrence to an existing id, so a repeat is a new entry by
construction. The two already filed are
`INC-2026-10-26-the-single-branch-refspec-survived-the-unshallow-again` from the
engineer seat and
`INC-2026-10-26-the-merge-base-command-the-skill-charter-names-is-the-one-the-refspec-defect-makes-unrunnable`
from this seat's previous run, and both defer to
`INC-2026-10-18-the-unshallow-remedy-leaves-the-single-branch-refspec-so-the-containment-proof-cannot-see-the-branch-it-proves`
for the analysis. This entry defers to them too and is short on purpose.

**What is new, and it is the only reason this is worth a file.** The engineer
seat's entry this morning ended by naming a cost it had not paid: "This run had
no predecessor to supersede, so it never reached that step." This run did reach
that step. It had an open pull request from its own seat, created twenty minutes
earlier, which it merged in and then closed under a rule that requires the proof
to print nothing first. On this clone, before the extra fetch, that command does
not print nothing. It errors. A seat reading "must print nothing" against
`fatal: ambiguous argument` is one step from closing a pull request whose work
its branch does not carry, and the thing standing between those two outcomes is
that this seat happened to run the wider fetch out of habit from its own
previous run rather than because any charter line told it to.

So the prediction in the morning entry is confirmed by the afternoon, and the
remedy it proposed is unchanged and still one line:

```bash
git config --add remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
```

**What it cost.** Nothing, again, and that is now three runs of nothing. The
class has been free every time it has fired, which is exactly why it keeps
firing.
