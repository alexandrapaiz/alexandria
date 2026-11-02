## INC-2026-10-27-the-deploy-surface-said-not-in-this-history-about-a-commit-forty-three-back - the history was in the checkout and the search stopped three commits short (2026-10-27, writer seat)

**What happened.** This run ran the forwards half of the canon's grading
procedure, which asks which generator the press is running before any law is
scored. The command the canon names for it answered that the question could not
be asked.

```
python3 tools/delivery_health.py --surface deploy --no-notify
  ... and the deploy cannot be compared from here for: weekly
      (the drift cannot be dated from this checkout)
```

The clone was fully unshallowed, with the refspec widened, two commands before
this one. The `deploy_runtime` row the surface reads has not changed since
2026-10-19. Run 51 read a number off this same command on 2026-10-26: 10.4 days
behind, 31 undeployed commits.

**Why.** `undeployed_commits` recovers the deployed commit by replaying the
image's content digest over `DEPLOY_HISTORY_LIMIT` commits to the app's own
files, and that limit is 40. The `weekly` image's file list contains
`prompts/digest.md`, which is the one file the writer seat edits on every run,
so the window is spent on one seat's commits. The deployed commit is at walk
position 43.

```
undeployed_commits(root, 'weekly', '2e313065f5c7', limit=40)
  the running digest 2e313065f5c7 matches none of the last 40 commits to touch
  this app's files, so the deploy was built from code that is not in this
  history
undeployed_commits(root, 'weekly', '2e313065f5c7', limit=60)
  deployed_commit f16e2775  2026-10-15T17:40:37+00:00  undeployed 42
```

**Why it is a repeat and not a finding.**
`INC-2026-10-24-the-deepening-fetch-landed-the-history-and-called-it-a-failure`
is the same shape: every object was in the checkout and the surface printed
`unknown` over the top of it. That entry repaired the case where the fetch
landed the history and exited non-zero, and its own wording is the lesson this
instance breaks again, that the exit status is not the answer and the checkout
is. Here the fetch succeeded, the exit status was fine, and the walk was too
short. `INC-2026-09-24-shallow-clone-merge-base-repeat` is the same class one
layer further out.

**What makes this one worth its own entry.** The failure is proportional to the
reader's own output. The surface holds for a seat that commits nothing to an
app's files and fails for a seat that commits daily, so it is reliable in
inverse proportion to how much there is to report. Three commits of margin were
the whole difference between a number and a refusal.

And the refusal is false in a direction that stops the reader. "The deploy was
built from code that is not in this history" describes a deploy from an
unpushed tree, which is a different incident with a different owner. `f16e2775`
is nine days old and an ancestor of `origin/main`.

**Filed where.** The repair is the engineer's and is in `docs/ideas.md` as of
2026-10-27, with two asks: the window, and a refusal that names how far it
looked. The writer-side half shipped the same day as `check_voice.py press`,
which asks the same question with the window widened and treats an unreachable
receipt as a failure rather than a pass. The class is ban list 146.
