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

### Addendum: it did reach a surface, and that surface can no longer be cleared (added 2026-11-02 by the next run of this seat, PR #755)

The entry above says nothing between the mistake and the merge looks at the
diff. One thing did, and it answered red. `checks.yml` is a `pull_request`
workflow with a `paths:` filter and `skills/**` is in it, so the 49 extra files
put this branch inside the filter's scope. Seven runs fired between 06:17:07Z
and 06:27:35Z and every one concluded `failure`.

Two tests, and both are the foreign half of the tree meeting main's half:

- `tools/skill_registrar.py` as #733 has it holds `FRONTMATTER_QUARANTINE = {}`,
  because that branch carries the newline that spends the entry. On `main` the
  dict still holds `harness-engineering`, and
  `tests/test_skill_receipts.py:271` asserts it does. Red.
- `skills/agent-containment/SKILL.md` as #733 has it, without #733's re-run
  validation receipt, makes that skill's `current` false, so
  `test_every_skill_the_page_receives_shows_a_dated_validation_result` fails on
  the message it is written to give: re-run `skills/_validation/trigger_test.py`.

Neither is a defect in either branch, and the bisect says so in three runs:
`2 failed, 24 passed` at `cbb2cf1d`, `26 passed` at this branch's tip after the
revert, and `26 passed` on #733's live successor #745's own head. **The red
belonged to the mixture, and the mixture existed nowhere but in this seat's
working tree.**

**The part worth an addendum is what the repair did to the red.** The reverted
diff is eight documents:

```bash
$ git diff --name-only origin/main...30105969      # 8 files, all under docs/
$ gh pr checks 746
no checks reported on the 'alexandria-research/2026-11-02-message-four-dones' branch
$ gh pr view 746 --json statusCheckRollup --jq '.statusCheckRollup|length'
0
```

Both commands were run, per the measurement note in
`INC-2026-10-13` on this class: `gh pr checks` reads the head commit and
`gh run list --branch` reads the branch, and here they agree. No run has fired
since the revert, because the net diff matches no entry in the filter.

So reverting the files that caused the red also removed the branch from the
only workflow that could ever have turned it green. **Red was reachable and
green is not.** A reviewer opening #746 sees seven failures and nothing after
them, and the merge rule's green condition cannot be satisfied on that diff at
any amount of further work -- not because anything is broken, but because the
filter is behaving exactly as written. The honest report is L-A31's third
colour, "no check ran", which is neither green nor red, with a re-performable
local command attached rather than an adjective.

**And the shape generalises past this branch.** Any diff that is inside a
workflow's path filter only because of files it later removes ends here: the
repair that removes the cause removes the instrument with it. The seat that
caused such a red cannot clear it, and the only thing it can do is say so where
the reviewer reads, which is the board and the pull request body.
