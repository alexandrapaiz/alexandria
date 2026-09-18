# Pending tracker

Maintained by the PM agent every run (charter §1d): what every seat owes,
what sits in open PRs waiting on your merge, and what waits on an
owner-only action. Each line dated. You should never have to hold this in
your head; if something is owed and has no line here, that is a tracking
failure and the next PM run fixes it on the spot.

Snapshot as of 2026-09-18 (Friday), ad-hoc operations dispatch. The next
scheduled PM ceremony (retro on sprint-2026-09-21, grooming, sprint
2026-09-28) runs Monday 2026-09-28 on its normal cadence; this file does
not replace that run.

## Open PRs waiting on your merge

1. **PR #18** — exo, `exo/2026-09-18` (run 2), opened 2026-09-18. Still in
   draft/in-progress per its own body ("full description lands before this
   leaves draft"). README and architecture-diagram truthfulness sweep,
   charter §5b. Not yet ready to merge; watch for it to leave draft.
2. **PR #19** — frontend, `fe/2026-09-18-nav-focus-hover`, opened
   2026-09-18. Mobile nav, focus ring, and Elicit-benchmarked hover polish,
   the second half of this week's scoped visual run (PR #15 carried the
   first half and already merged). Ready for your review.

No other PRs are open. Everything else from this week (#1-#17) is merged
or closed.

## What each seat owes, and from which directive

- **engineer** — daily cadence. Sprint 2026-09-21 (launch-runway site
  work, 5 items) is committed and starts Monday 2026-09-21; nothing owed
  before then. Standing accepted-but-not-built ledger items, oldest
  first: reviewer panel harness (ADR-13, owner decision 2026-09-17),
  institution backfill + digest resend (2026-09-17), corpus-expansion
  spike (2026-09-18, evidence_grade column + blog feeds), knowledge graph
  upgrade to industry standard (owner directive, 2026-09-18). None are
  this sprint's focus per docs/sprints/sprint-2026-09-21.md; they carry.
- **skill** — Tuesday cadence. NEON_RO_URL is fixed and verified
  (2026-09-18, PR #16, 441 claims confirmed live); the blocker recorded
  earlier this week is closed. Next Tuesday run continues the production
  line: parser fix for nested frontmatter (`provenance.claims`) and the
  verification-badge data schema, both proposed 2026-09-18, both waiting
  on an engineer or skill-agent build turn, not on the owner.
- **frontend** — Wednesday cadence. This week's scoped visual run is done
  (PR #15 merged, PR #19 open above). Nothing further owed until next
  Wednesday.
- **market** — Friday cadence. Two runs shipped this week (PR #3, #6,
  both merged). Eight proposals sit in docs/ideas.md under `proposed`,
  none older than 2026-09-18, so none are past the two-week grace period
  yet. Next Friday run continues; one flagged action below (positioning.md
  still carries stale $10/$30 numbers pending the market agent's own
  next-run update).
- **okr** — 1st-of-month cadence. First run shipped 2026-09-18 (Q4 OKRs +
  baseline benchmark, PR #2, merged). No further OKR-seat action owed
  until 2026-10-01, except folding the newly-written mission
  (vision.md §0) into the objectives at its next check-in, which it
  already carries as a noted follow-up.
- **security** — 1st and 15th cadence. First run shipped 2026-09-18
  (PR #8, merged). Three findings are `urgent` in docs/ideas.md and wait
  on an owner decision, not an engineer build (listed below). Next
  scheduled run: 2026-10-01.
- **exo** — Sunday cadence, plus this week's synchronous dispatches.
  Baseline run shipped (PR #4, merged). Run 2 (PR #18) is still in
  draft, see above.
- **sales** — org-chart.md lists this seat dormant pending owner
  activation, but PR #14 (launch campaign machinery) and PR #17 (GEO +
  distribution plan) already shipped and merged 2026-09-18. That is a
  tracking gap: the org chart has not been updated to reflect the seat
  is active. Flagging here since fixing docs/agents/org-chart.md is
  outside this run's scope (the owner's dispatch for this run named four
  specific jobs, board hygiene and presentation prep, not org-chart
  maintenance); the next PM ceremony should correct it.
- **research / weekly** — Monday 16:30 UTC cadence per org-chart.md, but
  `agent-weekly.yml` does not exist yet (engineer's 2026-09-18 proposal to
  add it is still `proposed`, unbuilt). This seat is not actually running
  on any cadence today. Nothing is owed because nothing is scheduled;
  flagging so it does not silently look "on cadence" when it is not.

## Owner-only actions waiting

1. **Clerk keys + Neon connection string as Vercel env vars** — due
   2026-09-19 (tomorrow). Not yet confirmed. Blocks the site deploy step
   of the launch runway.
2. **Stripe account and keys** — due 2026-09-26. Blocks payments wiring
   to the $20 spine.
3. **MCP OAuth redirect_uri validation gap** (security, urgent,
   2026-09-18) — phishing-link token theft risk in mcp/server.py's
   `/authorize` flow. Needs your read and a go-ahead before an engineer
   applies the fix.
4. **Public git history holds a pre-privacy-pivot digest**
   (security, urgent, 2026-09-18) — nine historical commits of
   `digests/2026-W37.md` are readable by anyone who clones the public
   repo. Needs your call on rewriting history (BFG/`git filter-repo`,
   disruptive) versus accepting the exposure.
5. **Grant the GitHub App `workflows` permission, or don't**
   (security, urgent, 2026-09-18) — no seat's token can currently push a
   workflow-file fix (including ExO's, whose charter names this as
   writable). The pinning fix for `actions/checkout` and
   `claude-code-action` is ready and waiting on this decision.
6. **Verdict on "Show each skill's validation evidence on its page"**
   (market proposal, 2026-09-18) — not yet two weeks old, but flagged
   early: it is most of the skills-library standing item 3
   (claim-graph citations rendered in the library) already, so a verdict
   now unblocks that item instead of waiting on a duplicate proposal.
7. **Panel PR-merge token scope** (2026-09-17) — due mid-November, not
   launch-blocking. The current fine-grained PAT is contents read/write
   only; the reviewer panel's autonomous merge needs PR-merge scope
   minted by you.
8. **A likely mis-copied verdict** flagged by a prior PM run
   (docs/backlog.md, "Awaiting your verdict" section): docs/ideas.md's
   "Permanent free sample issue on the site" carries the same rejection
   sentence used on the four beyond-skills product proposals decision 6
   named, but it is not one of those four. Worth confirming the status
   is what you intended.

## Resolved since last noted (no longer pending)

- NEON_RO_URL secret — fixed and verified 2026-09-18 (skill agent, PR
  #16). docs/backlog.md's launch-runway table still shows this row as
  "pending"; that file is outside this run's writable surface to correct,
  flagging here so the next grooming run updates it.
- PROJECTS_TOKEN secret — done, board live since 2026-09-18 (mid-week PM
  run).
