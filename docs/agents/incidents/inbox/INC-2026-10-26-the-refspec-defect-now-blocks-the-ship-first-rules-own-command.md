## INC-2026-10-26-the-refspec-defect-now-blocks-the-ship-first-rules-own-command - gh pr create refuses a branch that is pushed, and the refusal names the wrong cause (2026-10-26, skill seat)

**What happened.** This run pushed its branch successfully, saw `* [new branch]`
and `set up to track`, and then `gh pr create --draft --title ... --body-file ...
--base main` aborted with:

```
aborted: you must first push the current branch to a remote, or use the --head flag
```

The branch was on the remote at that moment. The cause is the registered one:
`--depth 1` implies `--single-branch`, the clone's fetch refspec stays
`+refs/heads/main:refs/remotes/origin/main` through `--unshallow`, and `git push
-u` writes upstream config without creating a remote-tracking ref, so `gh` finds
no `origin/<branch>` and reports that as an unpushed branch. Passing `--head
<branch>` explicitly opened the pull request on the first retry.

**Recurrence, 2026-10-26, same seat, next run.** The run that opened #590 hit
this identically: push reported `* [new branch]`, `gh pr create --draft` aborted
with the same sentence, and `--head <branch>` opened it on the first retry. That
is the fifth instance on this repository today. It is recorded here as a line
rather than as a sixth id, because the entry it belongs to was written hours
earlier by the same seat and a per-instance id for a defect recurring this fast
makes the register harder to read rather than more complete.

**Why it is in this register.** Fourth instance on this repository today, after
`INC-2026-10-18-the-unshallow-remedy-leaves-the-single-branch-refspec-so-the-containment-proof-cannot-see-the-branch-it-proves`,
`INC-2026-10-26-the-single-branch-refspec-survived-the-unshallow-again` and the
entry an open skill-seat branch carries for its supersede proof. The standing
rule records a repeat at the moment it repeats with no judgment call, and the
register has no way to append a recurrence to an existing id. This entry is
deliberately short and defers to those three for the analysis.

**What is new, and it is the reason this one is worth the lines.** The three
earlier instances all land on commands a seat runs at the *end* of a run:
`git log origin/<branch> ^HEAD` for the supersede proof, and staleness checks.
This one lands on `gh pr create`, which the ship-first rule requires in the
first few turns, before any substantial work. That rule exists because incident
3 records two runs that lost everything at sandbox teardown with nothing pushed.
So the defect has moved from the cheap end of a run to the expensive one.

The second half is the error text. It names the one cause that is not true here
and does not mention the refspec, so a seat that believes it will re-run the
push, see it succeed, and try again, which fails identically. The remedy is in
the message already, as the second half of a sentence a reader stops reading
after the first half.

**What it cost.** One turn in this run, because the `--head` flag is in the same
line as the wrong diagnosis. The cost it threatens is a seat that reads the
first clause, concludes its push failed, and spends the turns the ship-first
rule was written to protect.

**The fix, or why there is not one yet.** The one command the earlier entries
already propose, which repairs every instance of the class at once:

```bash
git config --add remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
git fetch origin
```

It belongs in every charter beside `git fetch --unshallow`, and a charter diff
is held by the merge rule's unrepaired cross reference, which is the subject of
this run's other entry. Until it lands, the cheap local habit is to pass `--head
<branch>` to `gh pr create` rather than trusting the refusal's stated cause.
