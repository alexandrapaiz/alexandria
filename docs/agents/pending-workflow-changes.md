# Workflow changes the agents cannot apply themselves

The ExO's charter (§5) puts `.github/workflows/agent-*.yml` in its lane.
The runner's token cannot actually write those files. GitHub refuses any
push from `GITHUB_TOKEN` that touches a workflow file, with

```
refusing to allow a GitHub App to create or update workflow
`.github/workflows/agent-engineer.yml` without `workflows` permission
```

and there is no `workflows:` key in a workflow's `permissions:` block to
grant, because `GITHUB_TOKEN` cannot hold that scope at all. Only a
personal access token with the `workflow` scope can push these files.

So workflow edits queue here instead, written out in full and ready to
apply, and the owner applies them. When she would rather not hand-apply
them, the durable fix is in incident 11 of [incidents.md](incidents.md):
mint a PAT with the `workflow` scope, store it as a repository secret,
and have `actions/checkout` use it in the agent workflows. That is an
owner-only step, since secrets never pass through the system.

Applied items get deleted from this file by the next ExO run, which
verifies against the workflow files themselves rather than trusting this
page.

---

## Pending, queued 2026-09-18 by the ExO agent

### 1. The no-ship tripwire, for all eleven agent workflows

**Why.** Incident 3: runs that worked for dozens of turns, reported
success, and lost every line at teardown because nothing was pushed. The
run's own conclusion hid it. The charter half of this fix shipped in the
same PR as this file, as the "Ship first, then work" rule now in all
eleven charters. This is the other half, which is the check that does not
depend on an agent remembering to obey.

**How.** Append to the `steps:` list of every
`.github/workflows/agent-*.yml`, after the `anthropics/claude-code-action`
step. Indentation is six spaces for the `- name:` line.

```yaml
      # Incident 3 (docs/agents/incidents.md): runs that worked for dozens of
      # turns, reported success, and lost everything at teardown because
      # nothing was pushed. A green conclusion is not evidence of shipping.
      - name: No-ship tripwire
        if: always()
        run: |
          git fetch origin --quiet 2>/dev/null || true
          branch=$(git rev-parse --abbrev-ref HEAD)
          dirty=$(git status --porcelain)
          pushed=$(git branch -r --contains HEAD 2>/dev/null | tr -d ' ')
          pr=$(gh pr list --head "$branch" --state all --json number --jq '.[0].number' 2>/dev/null || true)
          {
            echo "### Did this run ship anything?"
            echo ""
            echo "- branch: \`$branch\`"
            echo "- pushed to a remote branch: ${pushed:-NO}"
            echo "- pull request: ${pr:-none}"
          } >> "$GITHUB_STEP_SUMMARY"
          if [ -n "$dirty" ]; then
            echo "::warning::Uncommitted changes were left in the sandbox and are lost at teardown."
            printf '%s\n' "$dirty" | head -20
          fi
          if [ -z "$pushed" ]; then
            echo "::error::This run made commits that were never pushed, so the work dies with the sandbox. See incident 3 in docs/agents/incidents.md and the 'Ship first, then work' rule in this seat's charter."
            exit 1
          fi
          if [ -z "$pr" ]; then
            echo "::warning::No pull request exists for branch $branch. A run with nothing to ship must say so in a draft PR and close it, rather than ending silently."
          fi
```

**What each outcome means.** `git branch -r --contains HEAD` is empty
only when the run made commits that reached no remote branch, which is
lost work with no ambiguity, so that case fails the run. A dirty tree and
a missing pull request are warnings rather than failures, because both
have innocent explanations, and both are written to the run summary so a
reviewer sees what shipped without reading logs. Every step of this was
run by hand against this repository before it was written down, and the
one case it cannot see is a run that does nothing at all and leaves the
checkout pristine. That case is the missing-PR warning's job.

**Cost.** One shell step per run, no network beyond a fetch, $0.

### 2. Three turn caps are still below what the rule requires

**Why.** The chair right-sized every cap on 2026-09-18 (commit c6bc2c4)
and raised the pm and frontend job timeouts to match (57135da). That
cleared the queue's previous cap item, which is deleted here as applied.
Re-measuring afterwards against the standing rule in
[turn-caps.md](turn-caps.md), twice the highest observed turn count
rounded up to the next 50, three seats still come up short, because
those raises were also read from the day's failures rather than from the
ratio. Evidence and full table in turn-caps.md and in incident 15.

**How.** One number per file, in the `claude_args` line. Nothing else on
the line moves.

| File | From | To | Peak observed | Why this number |
|---|---|---|---|---|
| `agent-frontend.yml` | 400 | 600 | 286 (run 35306459296) | twice the org's highest demand; 600 turns lands near 65 minutes at the measured rate, inside the 90-minute timeout already in force |
| `agent-pm.yml` | 250 | 300 | 141, censored (run 35311930240) | that run died at its cap, so 141 is a lower bound and 300 is the floor the rule gives, not a settled number |
| `agent-security.yml` | 200 | 250 | 108 (run 35299288455) | one sample only, and it is the run that overshot |

Correct under the rule and not to be touched: `agent-exo.yml` at 200
against 93, `agent-sales.yml` at 160 against 76, `agent-engineer.yml` at
200 against 73, `agent-skill.yml` at 180 against 67, `agent-market.yml`
at 160 against 47, `agent-okr.yml` at 160 against 33. Provisional and
unmeasured because the seat has never run: `agent-research.yml` at 180,
`agent-finance.yml` at 120.

**Timeouts.** No change needed. Every seat's current `timeout-minutes`
clears its required cap at the measured rate of roughly nine turns per
minute.

**Cost.** None standing. Turns are only spent if a run needs them, so a
cap is a ceiling rather than a budget.

---

## Applied and deleted

- **Turn caps, re-derived from run logs** (queued 2026-09-18, applied by
  the chair in c6bc2c4, verified against the workflow files this run).
  The chair went further than the queued numbers on several seats. Item
  2 above is the remainder, measured fresh rather than carried over.
