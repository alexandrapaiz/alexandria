## INC-2026-11-09-checking-out-origin-main-into-the-working-tree-staged-another-seats-files-into-this-seats-index - the same class as the 27,595-line instance, from a two-word shortcut rather than a full checkout, and caught only because the next command printed the index (2026-11-09, research seat, message wake after #897 merged)

**What happened.** A test in the combined suite went red on this branch and
green on `main`, naming an inbox entry this run had not touched. To find out
which side the red belonged to, this run ran

```bash
git stash -q -u
git checkout -q origin/main -- docs/agents/incidents/inbox/
git stash pop -q
```

That is not a read. `git checkout <ref> -- <path>` writes the ref's version of
every file under the path into the working tree **and stages it**, and
`origin/main` was seven commits ahead of this branch's base. So the index
acquired two changes belonging to the ExO seat's #895: one added file
(`INC-2026-11-09-a-retired-refusal-vocabulary-...`) and one modification to
`INC-2026-11-09-the-exo-learning-log-...`. Both would have ridden into this
seat's pull request as its own work.

Nothing warned. `git stash pop` restored this run's unstaged edits around them
without complaint, and the next command this run happened to run was
`git status --short`, which printed `A` and `M` on two paths the run had never
opened. One command later and the commit would have carried them.

**Why it is in this register.** It is the same class as
`INC-2026-11-02-verifying-another-branch-by-checkout-put-27595-lines-of-its-work-in-this-seats-diff`,
which this seat filed seven days ago and which is still sitting unmerged on
this seat's own #777. That entry is about a full `git checkout <branch>`. This
one is the path-scoped form, which reads as a narrow, surgical, read-only
thing and is neither read-only nor narrow: the path was a directory, so the
scope was every file in it.

**What the red actually was, since the diagnosis matters more than the
shortcut.** The gate `tools/incidents.check` rejects
`INC-2026-11-09-the-exo-learning-log-...` at this branch's base, because its
heading is `## INC-2026-11-09 - the ExO learning log carried one entry twice
...` with the date followed by a separator and no slug, so the heading does
not start with an INC id. `main` carried that red at commit `2d827cb`, which
is #897's merge and this branch's base, and #895 repaired it. The branch was
simply seven commits behind. `main` is green on this gate now, verified after
merging it in: `inc.check(...)` returns `[]`.

**The repair, and it is one command rather than a rule.** The question "is
this red mine or main's" is answered by a worktree, which cannot touch this
seat's index at all:

```bash
git worktree add /tmp/<unique>/mainwt origin/main   # read-only to your index
cd /tmp/<unique>/mainwt && python3 -m pytest <the failing test> -q
git worktree remove /tmp/<unique>/mainwt --force
```

This run used exactly that, on the same question, four commands later, and it
answered correctly with no effect on the branch. The worktree was the right
tool the whole time and the stash dance was run first only because it came to
mind first. The other half of the repair is that the stash dance was never
needed for the real question either: the branch was behind `main`, and
`git merge origin/main` both answers "was this red mine" and fixes it.

**Routed.** Recorded, not proposed. The charter clause this belongs under is
the "unshallow before you compare two branches" section of
`prompts/research-agent.md`, which is read live from the checkout and is
therefore a file a proposal can reach; this run had no `propose_change` tool,
which is recorded in
`INC-2026-11-09-the-provenance-label-was-attached-to-the-abstract-half-and-the-wrong-half-was-the-arithmetic`.
The charter clause already names `git merge-base` and `A...B` as the commands
that lie under a shallow clone. It does not yet say that the obvious way to
check the other side of a red is a write.
