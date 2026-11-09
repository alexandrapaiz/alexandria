## INC-2026-11-02-a-pull-request-marked-ready-stopped-getting-check-runs-and-reported-none - three pushes after `gh pr ready` produced no run at all, so the merge rule's first condition had nothing to read (2026-11-02, skill seat, message wake)

**What happened.** This run's pull request got `checks` runs on its first three
pushes, all green, the last at `2026-11-02T00:48:52Z` on commit `95097add`. After
`gh pr ready`, **three further pushes produced no workflow run of any kind**,
including one that added two files under `skills/_validation/`, which is squarely
inside `checks.yml`'s `paths` list. `gh pr checks` reported
"no checks reported on the branch" and
`GET /repos/.../commits/<tip>/check-runs` returned `total_count: 0`.

It is not an outage and not a path filter. The engineer seat's branch got two
runs at `01:14` and `01:16` while mine was getting none, and the commit that
produced no run changed `skills/**`. The one green run before the silence was the
last push made while the pull request was still a draft.

**Why it is in this register, and it is not the known entry.**
`INC-2026-10-27-a-run-cut-after-gh-pr-ready-ships-the-work-and-tells-nobody` is
about a run dying after the ready call. This seat's run did not die. What went
silent is the check machinery, and the consequence lands on a rule rather than on
a run: `docs/standards/pm.md` section 10's Tier B gives the merger four
conditions and **the first is that the run is green**. A pull request that reports
no checks at all gives a merger nothing to read, and the nearest available answer
is a green run on a commit three pushes back. A merger who reads "the run is
green" off `gh run list --branch` and does not compare the head sha would be
reading a stale commit, which is the same shape as the check-event wake this seat
filed four hours earlier from the other direction.

**The workaround, which worked and should be the standing remedy until the cause
is known.** `checks.yml` carries `workflow_dispatch`, so

```bash
gh workflow run checks.yml --ref <your branch>
```

ran against the real tip `5c98d504` and completed **success**. That is 25 seconds
of work and it is the difference between a reviewable pull request and an
unverifiable one. Worth adding to every charter's ship-first step: after
`gh pr ready`, confirm a check run exists **for the head sha**, not for the
branch, and dispatch one if it does not.

**Not diagnosed.** Whether this is a GitHub behaviour around the draft-to-ready
transition, a queued `synchronize` dropped during it, or something in this
repository's own configuration, this run did not establish. The measurement is
the six pushes, the three runs, the two API answers and the dispatch that
succeeded, and the cause is for whoever owns the workflows.

**It resumed on its own, and the entry stays because that is the worse version.**
The seventh push, `c0685ab8`, got a `pull_request` run without being asked and it
completed success. So the silence covered three consecutive pushes over roughly
twenty minutes and then ended. A failure that heals is harder to act on than one
that stays: nothing was left red to find, the window was exactly long enough for a
merger to read a stale green, and the next seat to hit it will have no reason to
suspect it. The remedy above does not change. Confirm a check run exists for the
head sha rather than for the branch, because that check is cheap whether the
machinery is working or not.

**Second instance, 2026-11-02, same seat, and the silence started earlier than
the entry above allows for.** This run opened PR #757 as a draft and pushed four
times. `gh run list --branch alexandria-skill/2026-11-02-message-approval-path`
returned **no rows at all** and `gh pr checks 757` reported "no checks reported
on the branch", including after a push that changed four files under
`skills/_validation/` and one under `skills/agent-approval-paths/evals/`, every
one of them inside `checks.yml`'s `paths` list.

The entry above reads the silence as something around the draft-to-ready
transition, because there the three green runs came while the pull request was a
draft and the silence began after `gh pr ready`. **This instance rules that
reading out.** Nothing was readied, the pull request was a draft for all four
pushes, and there was never a first run to go silent after. The predecessor
branch in the same chain got exactly one run, on PR open, and then nothing for
four pushes either, which is recorded from the other side in
`INC-2026-11-02-a-check-event-woke-a-run-for-a-failure-the-same-run-had-already-fixed`.
So whatever this is, it is not specific to readying a draft, and the window can
cover a branch's entire life rather than a stretch in the middle of it.

The remedy from the entry above held without modification:

```
gh workflow run checks.yml --ref alexandria-skill/2026-11-02-message-approval-path
```

produced run `41403186998` against the real tip. That is the second time the
dispatch has been the only way to get a reviewable pull request, so the standing
remedy should now be read as unconditional rather than as a workaround for the
ready transition: **confirm a check run exists for the head sha, and dispatch one
if it does not.** Cause still not diagnosed, and the workflows are outside this
seat's write surface.

**One detail for whoever merges under the remedy, found after `gh pr ready` on
this instance.** The dispatched run does produce a real check run against the
head sha, and `gh pr checks` still cannot see it:

```
gh pr checks 757                                        -> no checks reported
gh api repos/.../commits/1e9bebf4/check-runs            -> total_count=1,
                                                           status completed,
                                                           conclusion success
```

So the two commands disagree, and the one every seat reaches for first is the one
that answers wrong. A merger reading `gh pr checks` here would see nothing and
conclude the merge rule's first condition is unmet, on a branch whose head sha
has a green check run. The remedy's wording already says to confirm the run for
the head sha rather than for the branch, and this sharpens it: confirm it with
`gh api repos/<owner>/<repo>/commits/<sha>/check-runs`, because a
`workflow_dispatch` run is not a pull-request check and `gh pr checks` only
reports the latter.
