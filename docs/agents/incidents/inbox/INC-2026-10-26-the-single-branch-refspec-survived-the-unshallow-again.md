## INC-2026-10-26-the-single-branch-refspec-survived-the-unshallow-again - a repeat, recorded because the standing rule has no judgment call in it (2026-10-26, engineer seat)

**What happened.** This run did what its charter's first command says, `git
rev-parse --is-shallow-repository` returning `true` and then `git fetch
--unshallow`, and at the end of the run `git log --oneline -1
origin/alexandria-engineer/2026-10-26-message-memory-eval` still failed with
"fatal: ambiguous argument ... unknown revision". The reason is the one already
registered: `--depth 1` implies `--single-branch`, so the clone's fetch refspec
is `+refs/heads/main:refs/remotes/origin/main` and nothing else, and
`--unshallow` deepens history without widening that refspec. `git push -u`
sets upstream config but creates no remote-tracking ref, so a branch this run
pushed is invisible to every command that names `origin/<branch>`.

```
git config --get remote.origin.fetch   # +refs/heads/main:refs/remotes/origin/main
git ls-remote origin <this branch>     # a38bf7e1... refs/heads/...
git log -1 origin/<this branch>        # fatal: ambiguous argument
```

**Why it is in this register.** It is a repeat of
`INC-2026-10-18-the-unshallow-remedy-leaves-the-single-branch-refspec-so-the-containment-proof-cannot-see-the-branch-it-proves`,
and the standing rule says a repeat is recorded at the moment it repeats with
no exceptions and no judgment call. The register has no way to append a
recurrence to an existing id, so a repeat is a new entry by construction; this
one is deliberately short and defers to the earlier entry for the analysis.

**What it cost.** Nothing in this run, which is the only interesting thing
about it. The branch was verified with `git ls-remote` instead and the sha
matched `HEAD` exactly. The cost lands on the charter's own supersede proof,
`git log --oneline origin/<the-older-branch> ^HEAD`, which is required to print
nothing before a seat may close a superseded pull request. On this clone that
command errors rather than printing nothing, and a seat reading "must print
nothing" against an error message is a seat one step from closing a pull
request whose work it does not carry. This run had no predecessor to supersede,
so it never reached that step.

**The fix, or why there is not one yet.** One command, and it belongs in the
charter beside the two that are already there:

```bash
git config --add remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
git fetch origin --unshallow    # or plain fetch when already full
```

The charter is the owner's to edit and this seat may not include a charter diff
in its daily pull request, so what this entry can do is make the second
occurrence legible to the ExO seat that reads this file weekly, which is the
route the earlier entry already took.
