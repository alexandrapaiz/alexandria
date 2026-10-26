# Engineer run note - 2026-10-26 (message, the next item in the lane)

Woken by #536's merge, with the payload asking for the next item in this
seat's lane on the board. What follows is the part of the run that does not
belong in the pull request description: how the item was chosen, and the two
things the choosing turned up.

## The lane on the board is still owner-blocked, and that is no longer the answer

Four `This sprint` cards sit in the engineer lane and all four close with a
hand this seat does not have: the Modal workspace being switched back on, a
deploy into it, a press resend through it, and three `POLAR_CHECKOUT_*` values
in the site's environment. Three runs of this seat have now written that table,
and `INC-2026-10-25-the-engineer-lane-was-rediscovered-as-owner-blocked-for-the-second-run-running`
already records the rediscovery. This run did not write it a fourth time.

What changed since those runs is that a new sprint exists.
`docs/sprints/sprint-2026-10-26.md` was planned this morning and it is on the
PM's open #531 rather than on `main`, which is why the last five runs of this
seat all reported the newest sprint as fourteen days old. Its goal is written
against exactly this situation: "Build what the Modal outage and the Polar
account can't block." Five engineer items, four of them buildable with no
account and no credential.

So the day's work is that sprint's item 1, read off a branch rather than off
`main`. The charter says the sprint file is the priority queue and the owner's
merge of the plan is the commitment, so taking an unmerged plan's first item is
a deviation in form. It is recorded here and in the pull request for the
Monday retrospective, and the alternative was a sixth consecutive run reporting
that no plan existed.

## What the item asked for, and why the answer was not one thing

Item 1: find the specific gap between "the panel runs and writes a verdict"
and "a verdict merges a pull request," with nothing hand-wavy left in it.

Every document in this repository said the gap was one thing.
`docs/product/reviewer-panel.md` said it in bold, "**this is now the only thing
between ADR-13 and a working loop**", and named a PR-merge-scoped token only
the owner can mint. `README.md`'s status checklist says the same sentence.
`docs/agents/registers.md`'s row for `panel_verdicts` says the write gate
fires.

The gap is four things and the token is the last of them. The three ahead of it
were all checkable from the repository alone:

1. Nothing had ever filed a verdict about a pull request. All three reviewers
   read skills from `main`, so every row in `panel_verdicts` describes text
   that is already merged.
2. ADR-12's whitelist refuses every real proposal, measured rather than
   reasoned, because the skill seat's own charter requires a `docs/` append on
   the branch that carries the work.
3. The whitelist admits `prompts/*.md`, which held one prompt in September and
   holds twelve seat charters now.

That is filed as a repeat in
`INC-2026-10-26-the-panel-build-note-named-one-blocker-and-there-were-four`,
because it is the third time this same document has asserted the state of
machinery nobody had run.

## The one thing this run could not do, and the shape of the refusal

The item also asked for a verdict landed all the way to a CI check status on a
real pull request. The status write is refused by the token every seat on this
host holds: `GET /repos/{repo}/commits/{sha}/statuses` answers 200 and
`POST /repos/{repo}/statuses/{sha}` answers 403, *Resource not accessible by
personal access token*. The missing grant is one checkbox, **Commit statuses:
Read and write**. A check run is not a way around it, because the check-runs
API is writable by a GitHub App installation and never by a personal token.

What did reach a pull request is the comment, which is ADR-13's own words for
it: a failure "leaves the PR open with the verdicts attached." The first one is
on #535, and it carries something the merge gate was not looking for. Both
skills on that branch have an eval suite and no `results.json`, so the trial
was written and never run.

## The machinery diff, and the guard

Seven commits touched `.github/` or `pipeline/` in the last 36 hours and every
one of them is this seat's own, carried by merged #481, #487, #500, #516 and
#536. The two that are runtime changes under
`docs/agents/runtime-changes.md`, `85866beb` and `f4da8c89`, change the call
sizes the daily Kimi draw requests, and `85866beb` is itself the rehearsal
guard that pins those numbers to the jobs' own constants. Both are explained by
#536's description. Nothing here is an unexplained runtime change.

`gh run list --workflow=checks.yml --branch=main` reads success on the four
runs before the one in flight for `3aa3b67d`. Main is green.
