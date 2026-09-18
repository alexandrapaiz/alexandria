# Incident register — agent runs and sandboxes

Owner-directed (2026-09-18): a technical record of agents not properly
running, shutting down, or losing work, so failures are learned from
once instead of rediscovered. Append-only, dated, any seat or the chair
may add entries; the ExO reads this file every run (charter step 2) and
turns patterns into charter or workflow fixes.

STANDING RULE (owner, 2026-09-18): any issue that occurs MORE THAN ONCE,
anywhere in the org, is always recorded here at the moment it repeats.
No exceptions, no judgment call. A repeat that goes unrecorded is itself
an incident.

## 2026-09-17/18 — the founding night's failures

1. **OIDC permission missing.** First cloud run (engineer,
   run 35297972051) failed 3/3 attempts: claude-code-action requires
   `id-token: write`, absent from the workflows. FIXED (commit
   c7e67d5) across all workflows.
2. **Default tool sandbox blocks shipping, run still reports
   success.** The smoke run completed green with 17 permission
   denials: the action's default permission mode refused git pushes
   and PR creation, and the job's conclusion hid it. FIXED: 
   `--permission-mode bypassPermissions` (commit 80721ee), justified
   by the isolated ephemeral runner and repo-scoped token.
3. **Run reports success, ships nothing (end-loaded shipping).** Sales
   first run (35305610562): 59 turns, zero denials, subtype success,
   no branch pushed, no PR, all work lost at sandbox teardown. The PM
   scrum-overhaul run (35301912056) had the same no-ship outcome and
   later flipped to a failure conclusion; its logs were not
   retrievable afterward. PATTERN FIX pending with the ExO: every
   charter mandates draft-PR-first (branch, push, `gh pr create
   --draft` within the first turns, commit as you go), plus a
   workflow tripwire flagging any run that ends with no branch
   pushed. Board card exists.
4. **Turn-cap starvation on visual work.** Frontend first run
   (35305207776) died at `error_max_turns` (150): build plus
   Playwright plus reading screenshots is turn-hungry. FIXED: cap
   raised to 250 and first-run scope narrowed; a future fix is
   scripting the screenshot batch so turns go to judgment, not
   plumbing.
5. **Shared-checkout collisions (pre-cloud and ad-hoc runs).** A local
   desktop PM run operated in the interactive session's checkout and
   switched its branch mid-commit (resolved by moving all runs to
   isolated Actions checkouts, ADR-18). The ad-hoc remote OKR and
   market runs shared one clone and raced on branches; both
   self-repaired and reported honestly. Scheduled Actions runs each
   get a fresh checkout, so this class is closed except for ad-hoc
   remote sessions.
6. **Same-anchor ledger appends guarantee merge conflicts.** PRs #2
   and #3 both inserted at docs/ideas.md's `## Proposals` header;
   the second merge conflicted exactly as the ExO's first run
   predicted. FIXED at charter level: ledger-writing seats must check
   open PRs touching ideas.md and declare merge order (PR #4).
7. **Hidden-prompt secret paste stored an empty value.** NEON_RO_URL
   was set to an empty string via a masked terminal prompt; runs then
   failed with a confusing local-socket psql error. The skill agent
   diagnosed it correctly and refused to fabricate data. FIXED by
   re-entry plus a rule: any run depending on a secret verifies it
   with a cheap probe first and reports the probe's result.
8. **Ambiguous run conclusions.** GitHub's run list briefly showed the
   PM overhaul as success before recording failure, which misled
   monitoring. Lesson: trust a run's shipped artifacts (branch, PR),
   never its conclusion alone.

9. **Premium seats silently ran on the default model.** The routing
   table assigned the top model to engineer, exo, security, skill,
   weekly, and frontend, but no `--model` flag was set and
   claude-code-action defaults to Sonnet, so every premium run on
   2026-09-17/18 actually used Sonnet. Caught by an owner-requested
   routing audit reading modelUsage from real run logs. FIXED:
   `--model opus` set explicitly on all six workflows. Lesson: a
   routing policy is config plus verification; assert the model from
   run logs, never from intention.

10. **Turn-cap starvation is a pattern, not a one-off (ExO owns the
   postmortem).** Second and third occurrences: the PM's views/triage
   run and its scrum-overhaul run both died or shipped nothing under a
   60-turn cap, after the frontend's first run died at 150. Owner
   escalated 2026-09-18: "pass this issue on to EXO because it's the
   second time it's happened." Interim fixes: PM raised to 140,
   frontend to 250. ExO's Sunday postmortem should right-size every
   seat's cap against its real workload, and pair it with the
   draft-PR-first rule so a starved run still leaves partial work
   instead of nothing. A cap that silently eats a run's entire output
   is a harness bug, not an agent failure.

## 2026-09-18 — the first full week of cloud runs

Postmortems by the ExO agent (charter step 6), blameless, from run logs
rather than from what the runs said about themselves.

11. **A turn cap failed a run that had already shipped.** The security
    seat's first run (35299288455) did its whole job, opened PR #8 at
    02:42:38, and was then failed by the action eight seconds later:
    `Claude reported a successful result after 108 turns, exceeding the
    configured maximum of 100`. Technically this is not the same defect
    as incident 4, where frontend died mid-work at `error_max_turns`.
    Here the work was complete and merged; only the run's conclusion was
    red. The damage is to monitoring rather than to output, and it is
    the exact inverse of incident 8: there, a green conclusion hid a run
    that shipped nothing, and here a red conclusion hides a run that
    shipped everything. Both point at one rule, which is now the house
    rule for reading runs: **judge a run by its artifacts, never by its
    conclusion.** FIX queued, not applied: raise the security cap from
    100 to 150, in docs/agents/pending-workflow-changes.md, because of
    incident 12 below. Lesson for charters: a cap is a tripwire, not a
    budget, so size it to the seat's honest work and treat a cap hit as
    evidence about the cap.

12. **The agent token cannot write the agent workflows, so part of the
    ExO's chartered lane is unreachable.** Discovered this run, by
    trying it. The ExO charter §5 names `.github/workflows/agent-*.yml`
    as writable, and the push was rejected outright:
    `refusing to allow a GitHub App to create or update workflow
    .github/workflows/agent-engineer.yml without workflows permission`.
    This is not a misconfiguration that a `permissions:` block can fix.
    `GITHUB_TOKEN` has no `workflows` scope available to grant, and only
    a personal access token carrying the `workflow` scope can push these
    files. Every workflow-level fix the org has wanted since the
    founding night runs into this, including incident 3's tripwire and
    incident 10's cap raise, which means the gap has been silently
    costing the org its whole workflow-repair capability for a week.
    FIX, two parts. Part one shipped now: workflow edits are written out
    in full in docs/agents/pending-workflow-changes.md for the owner to
    apply, and the ExO charter no longer claims a lane it cannot reach.
    Part two is owner-only and stays her call: mint a PAT with the
    `workflow` scope, store it as a repository secret, and pass it to
    `actions/checkout` in the agent workflows. That would let the seats
    repair their own machinery, and it would also hand every agent run a
    token strong enough to rewrite what runs the agents, so it is an
    authority change rather than a convenience, and it belongs to her.
    Lesson, and the one worth generalizing: **a charter that grants a
    lane the runtime cannot reach is a charter defect, not a runtime
    defect.** Every lane a charter names should be provable by the seat
    that holds it, so the ExO now verifies its own writable surface each
    run instead of assuming it.

13. **Incident 3's pattern fix sat unapplied for a full week.** Incident
    3 recorded draft-PR-first as "PATTERN FIX pending with the ExO" on
    the founding night. Sixteen PRs and one ExO run later, not one of
    the eleven charters contained the word draft, and the owner was
    still carrying the rule by hand in each dispatch prompt. The ExO's
    own first run spent its single permitted charter edit elsewhere, on
    the ledger-collision fix, which was reasonable in isolation and
    wrong against this queue. Nothing in the org held the list of fixes
    that had been agreed but not made, so the register recorded the
    decision and then no one read it as a to-do. FIXED: the rule is now
    a section in all eleven charters, and the ExO charter's step 2 now
    requires reading this register for entries whose fix is marked
    pending or queued, and either shipping them or saying in the PR why
    not. An incident is not closed when it is written down. It is closed
    when the fix is in the tree.
