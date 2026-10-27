## INC-2026-10-26-the-supersede-proof-errored-on-the-first-run-that-actually-had-a-predecessor - the single-branch refspec, third occurrence, and this time the predicted cost was reached (2026-10-26, writer seat)

**What happened.** This run ran the two commands its charter puts ahead of every
branch comparison. `git rev-parse --is-shallow-repository` returned `true`, `git
fetch --unshallow` completed, and the clone was no longer shallow. The next
command was the charter's own supersede step, and it failed:

```
git checkout -b <mine> origin/alexandria-writer/2026-10-26-message-unregistered-candidate
  fatal: '...' is not a commit and a branch cannot be created from it
git log --oneline origin/alexandria-writer/2026-10-26-message-unregistered-candidate ^HEAD
  fatal: ambiguous argument '...': unknown revision or path not in the working tree
```

The cause is already registered twice. `--depth 1` implies `--single-branch`, so
the clone's fetch refspec is `+refs/heads/main:refs/remotes/origin/main` and
nothing else, and `--unshallow` deepens history without widening that refspec.
One command fixed it and then everything worked, which is the fix the second
occurrence already wrote down:

```
git config --add remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
git fetch origin
```

**Why it is in this register.** Third occurrence. It repeats
`INC-2026-10-18-the-unshallow-remedy-leaves-the-single-branch-refspec-so-the-containment-proof-cannot-see-the-branch-it-proves`
and `INC-2026-10-26-the-single-branch-refspec-survived-the-unshallow-again`, and
the standing rule has no judgment call in it. The register still has no way to
append a recurrence to an existing id, so a repeat is a new entry by
construction and this one defers to the first for the analysis.

**What it cost, and this is the part that is new.** Two minutes of commands, and
the exact cost the second occurrence predicted and could not demonstrate. That
entry closes with "This run had no predecessor to supersede, so it never reached
that step." This run had one, pull request #612 from this seat's own previous
run, and it reached the step. The charter says the proof `git log --oneline
origin/<the-older-branch> ^HEAD` must print nothing before a superseded pull
request may be closed. On a single-branch clone that command prints nothing to
stdout and writes a fatal error to stderr, so a seat reading it the way the
charter words it, as emptiness rather than as an exit code, closes a pull
request whose work its own branch does not carry. Here the error was read as an
error, the refspec was widened, and the proof was then run for real and printed
nothing before #612 was closed.

**The fix, or why there is not one yet.** The charter line is the owner's to
edit and this seat may not ship a charter diff, which is the same wall the
second occurrence hit. What this entry adds for the ExO seat that reads the file
weekly is that the proof itself is written in the weaker of two available forms.
A command whose pass condition is empty output cannot distinguish a pass from a
failure to run. The same proof exists in a form that cannot:

```
git merge-base --is-ancestor origin/<the-older-branch> HEAD   # exit 0 is the proof
```

That exits non-zero when the older branch is not contained and exits non-zero
when the ref does not resolve, so both ways of being wrong look wrong. Changing
it is one line in every charter that carries the supersede clause, and the
refspec repair is one line beside the two unshallow commands they already carry.
