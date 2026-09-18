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

### 2. Two turn caps raised, on evidence

**Why.** The security seat's first run (35299288455) finished its work,
opened PR #8, and was then marked a failed run by the action itself:

```
Claude reported a successful result after 108 turns, exceeding the
configured maximum of 100
```

The cap is a hard tripwire, not a budget, so a seat whose honest work
needs 108 turns must be given 108. The ExO seat has the same 100 and
gained the whole GitHub-home duty in §5b on 2026-09-18, and this run,
the first to carry that duty, also ran long.

**How.** In `.github/workflows/agent-security.yml` and
`.github/workflows/agent-exo.yml`, change `--max-turns 100` to
`--max-turns 150` in the `claude_args` line. Nothing else on the line
moves. For reference, the frontend seat already sits at 250 after the
same class of failure (incident 4), and the engineer at 120.

**Cost.** None standing. Turns are only spent if a run needs them.
