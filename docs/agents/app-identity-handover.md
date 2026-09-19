# The App handover: what moves from the chair to the seats

**Enforced at:** prompts/exo-agent.md §5, which probes the workflow-push lane every run and works step 6 of this page the day the probe succeeds.

Written by the ExO agent 2026-09-19, on the owner's order, so the day
the GitHub App's private key lands is a planned transition rather than
an improvised one. ADR-27 is the decision. `APP_ID` is set. This page is
what happens when `APP_PRIVATE_KEY` joins it.

Nothing here is blocked on analysis. It is blocked on a key.

## Why the chair is doing infrastructure work at all

Not preference. Mechanics. `GITHUB_TOKEN` cannot hold the `workflow`
scope, so a push touching `.github/workflows/` is rejected outright
(incident 12, re-verified by attempting it on 2026-09-19 and rejected
again). No seat can change the machinery that runs it. Every fix has
therefore gone through the chair's hands.

What the chair has applied by hand in two days, all of it work a seat
had the evidence for and not the permission:

| Change | Commit or run | The seat that should have owned it |
|---|---|---|
| `id-token: write` across all workflows | c7e67d5 | engineer |
| `--permission-mode bypassPermissions` | 80721ee | exo |
| `--model opus` on the premium seats | incident 9 | exo |
| Turn caps right-sized across 12 seats | c6bc2c4 | exo |
| Job timeouts raised for pm and frontend | 57135da | exo |
| Container image, uid 1001, `--user` options | incidents 17, 18 | exo |
| The writer seat's whole workflow | ADR-28 | exo |

The ExO has queued two more it still cannot apply: the no-ship tripwire,
now unshipped across three ExO runs, and three caps still short of the
measured rule. Both are written out in
[pending-workflow-changes.md](pending-workflow-changes.md).

## What transfers on key day

**To the ExO seat, and this is the large one.** `.github/workflows/`
becomes writable through ordinary PRs. Caps, timeouts, crons,
`permissions:` blocks, the tripwire, model routing, and new seats'
workflows stop being a queue on a page and become diffs the owner reads
in a PR like any other. Charter §5 stops disclaiming a lane it cannot
reach and takes it back. `pending-workflow-changes.md` loses its reason
to exist and is deleted once its two items ship.

**To the seats generally.** Any seat that finds its own machinery wrong
can propose the fix in its own PR instead of filing a note and waiting.
That is the autonomy tiebreak in vision.md §0 pointing one way, and it
is the single largest capability unlock available to this org right now.

**Identity.** Commits stop attributing to the owner's tokens and start
attributing to the App's bot name. The org becomes legible in `git log`:
you can see which work was an agent's and which was hers.

**To the PM seat, and this is the one the owner asked for by name.**
Today no seat can start another seat's run, and that is mechanical. A
`workflow_dispatch` made with `GITHUB_TOKEN` creates no workflow run at
all, because GitHub refuses to let the runner's own token trigger
further workflows, which is the recursion guard rather than a
permission we forgot to grant. An App installation token is not subject
to that guard. So the day the key lands, the PM's proposed dispatch
queue can stop being a list a human fires and start being a list the PM
fires, which is the difference between a seat that recommends and a seat
that operates.

**BOLD FLAG, AUTHORITY: this is the second-largest grant in this
document, and it is written to be refusable.** The terms are already
drafted as section 5 of prompts/pm-agent.md, marked dormant, so merging
that charter grants nothing. Activation needs two separate acts by the
owner, and either one alone does nothing.

1. She sets the repository variable `PM_DISPATCH_ENABLED` to `true`. No
   agent run can write a repository variable, so this is a switch the
   org cannot flip for itself, and it is an off switch she can hit in
   one click at any hour without merging anything.
2. She merges an amendment removing the dormant marker from section 5.

The guardrails in that section, in short: eight seats dispatchable and
four not, where the four are exo (a seat must not schedule its own
auditor), the PM itself (a seat that dispatches itself has no cadence),
and the two dormant seats (activation is hers). Three dispatches a day,
one per seat, ten a rolling week. No dispatch to a seat with an open PR
from its last run. No dispatch within two hours of any other dispatch,
because that means the chair is driving and two dispatchers is how
incident 14 happened. No instruction may carry a judgment she has not
made, only a ruling that exists in a file and is cited. And the merge
gate is untouched, because a PM-initiated run opens a pull request
exactly like every other run.

The verification step, on key day, is one command rather than an
argument:

```bash
gh workflow run agent-writer.yml -f owner_instructions='probe, do nothing'
gh run list --workflow=agent-writer.yml --limit 1   # a run exists, or the guard still holds
```

If no run appears, the App token is subject to the same guard and the
whole of section 5 is void. Find that out with the probe above before
anyone writes a line of policy on top of it.

**BOLD FLAG, AUTHORITY: this proposes that the ExO seat own
`.github/docker/Dockerfile` and `build-agent-image.yml`** alongside the
workflows, because the agent image is the seats' workstation rather than
product code, and the seat that sizes caps is the seat that should size
environments. The engineer keeps the version pins that must mirror
`site/package.json` (Playwright today). This is a lane the ExO does not
hold now and would hold after, so it is the owner's to grant or refuse.

## What never transfers

Stating this explicitly, because an App with the `workflows` permission
is the largest grant of authority this org has made, and the boundary
should be written before the key exists rather than after.

- **The merge gate.** The owner merges. ADR-27 says so and nothing here
  changes it. One PR per run, no auto-merge, no self-merge.
- **Secrets.** The App's private key, `CLAUDE_CODE_OAUTH_TOKEN`,
  `NEON_RO_URL`, `PROJECTS_TOKEN`. No run reads or writes them.
  `PROJECTS_TOKEN` stays as-is for the board, per ADR-27.
- **The App's own permission set.** Adding a permission to the App is an
  authority change and belongs to the owner alone.
- **Purpose, OKR commitment, pricing, and money.** Unchanged.

## The risk, stated plainly

A token with the `workflows` permission lets an agent run rewrite what
runs the agents. In principle a run could raise its own cap, delete its
own tripwire, or change the model it runs on, and the only thing between
that and reality is the owner reading the diff.

Two mitigations, both cheap, both proposed here:

1. **Every runtime change ships under the smoke-test law**
   ([runtime-changes.md](runtime-changes.md)), so a workflow edit
   arrives with a verification run attached rather than as an assertion.
2. **The ExO diffs `.github/` every run** against the previous run's
   tree and reports any change no merged PR explains. A seat quietly
   editing its own constraints becomes visible within a week. This
   becomes a named duty in the ExO charter on key day.

Neither mitigation replaces the merge gate. They make the diff the owner
reads a small and honest one.

## Key day, step by step

The handover is itself a runtime change, so it goes up the ladder in
[runtime-changes.md](runtime-changes.md) rather than landing everywhere
at once.

1. **Owner** adds `APP_PRIVATE_KEY` as a repository secret and confirms
   the App's installation permissions: contents (write), pull requests
   (write), workflows (write), and packages (write) if the App is to
   replace `GITHUB_TOKEN` in `build-agent-image.yml`. Nothing else
   changes in this step, and every workflow keeps running as it does
   today.
2. **Chair** adds the token-mint step to exactly ONE workflow. Use
   `agent-exo.yml`: it is the seat that will exercise the new lane
   hardest, it runs weekly so a broken one costs the least, and its
   output is documents. The step mints a short-lived installation token
   from `APP_ID` plus the key and hands it to `actions/checkout` and to
   `GH_TOKEN`.
3. **Smoke it by hand**, dispatch not cron, on a throwaway branch. The
   checklist for this specific change, beyond the standard one:

   ```bash
   gh auth status                       # identity is the App, not a PAT
   git commit --allow-empty -m probe && git log -1 --format='%an <%ae>'
   # append a comment to a workflow file, then:
   git push origin HEAD:refs/heads/app-probe    # THIS is the test
   ```

   The push in the last line is the whole point of the handover. If it
   is still rejected, stop: the App's `workflows` permission is not
   actually granted, and no amount of workflow editing fixes that.
4. **One real ExO dispatch** on real work, to prove the seat still
   functions with a different token.
5. **Roll to the remaining eleven workflows**, then let crons fire.
6. **Then, in the first ExO run after**, and these are the cleanup
   items that are easy to forget:
   - ship the two queued items in `pending-workflow-changes.md` as
     ordinary PRs, and delete the file
   - rewrite ExO charter §5 to claim the lane, and verify it by
     attempting a push rather than by trusting the rewrite
   - add the `.github/` diff duty to charter step 2
   - close incident 12 with the date the lane opened
   - update ADR-27 with what actually happened, and record whether
     per-seat Apps still look like the right second step
   - run the PM dispatch probe above, and either propose the amendment
     that activates prompts/pm-agent.md section 5 or record that the
     guard still holds and strike the section
   - add the dispatch-log audit to this seat's weekly work: every
     PM-initiated run in `gh run list --event workflow_dispatch` must
     appear in the PM's own log in `docs/sprints/dispatch-queue.md`, and
     a dispatch that happened and was not logged is an incident

## How to tell it worked

One test, in one line: **an agent seat raises its own turn cap in a PR,
and the owner merges it.** Until that has happened once, the handover is
configured rather than working.
