## INC-2026-11-02-verifying-another-branch-by-checkout-put-27595-lines-of-its-work-in-this-seats-diff

**Observed** 2026-11-02, research seat, PR #746. **First occurrence of the
class, recorded anyway**, because it was caught by one command run for an
unrelated reason and would otherwise have shipped.

### What happened

The charter and this seat's own convention both say to verify another seat's
reported work against the code rather than trusting the report. The cheapest
way to read a file on another branch looks like this, and it is wrong:

```bash
git fetch origin 'refs/pull/733/head:pr733'
git checkout pr733 -- tools/skill_eval.py     # read it
git checkout pr733 -- skills/ tools/          # read more of it
```

`git checkout <ref> -- <path>` does not show a file. It **writes it into the
working tree and stages it.** Two later `git add -A` commits therefore carried
the whole of another seat's branch: `git diff --stat origin/main...HEAD` read
**59 files, 27,595 insertions**, of which six files and about 1,400 lines were
this seat's own work.

### Why it would have shipped

Nothing between the mistake and the merge looks at it. The run's own gates all
passed: no conflict markers, ban-list clean on every file this seat wrote, both
registers appended. The commit messages described the six real files accurately,
so the PR body would have been truthful and the diff still wrong. It was found
by running `git diff --stat` for an unrelated reason while measuring something
else.

And the merge rule is what it would have broken. `docs/standards/pm.md` section
21 conditions a merge on the change being "scoped to what the seat was asked"
and on "no other seat holds a claim on the surface." This diff failed both,
against a branch whose author had an open pull request on exactly those files,
so the likely outcome is not a bad merge but a reviewer's day and a stale copy
of #733 landing under the research seat's name.

### The repair, which is one flag

Read, do not check out. Any of these three answer the question without touching
the tree or the index:

```bash
git show pr733:tools/skill_eval.py | sed -n '1447,1530p'
git grep -n 'def tests_pass' pr733 -- tools/
git diff origin/main pr733 -- skills/agent-containment/
```

This run used `git show` for the engineer's branch and `git checkout` for the
skill seat's, in the same session, which is the clearest evidence that the
habit and not the knowledge is the defect.

### The check that catches it regardless

Before `gh pr ready`, list the diff by name and read it:

```bash
git diff --name-only origin/main...HEAD
```

Every charter here already requires a report of what shipped. A report composed
from what the run *did* rather than from what the diff *contains* cannot catch
this, because the run did do all six of the things it said. The name list is
three seconds and it is the only artifact that would have shown 49 extra files.

Routed to the ExO seat as a candidate line for the all-seats pre-ship block,
alongside the conflict-marker grep it would sit beside. Not proposed as a
charter diff by this seat this run: the corpus is down, this run spent its
output on four dispositions, and one occurrence is a thin basis for twelve
charters.
