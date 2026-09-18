# Pending tracker

Maintained by the PM agent every run (charter §1d): what every seat owes,
what sits in open PRs waiting on your merge, and what waits on an
owner-only action. Each line dated. You should never have to hold this in
your head; if something is owed and has no line here, that is a tracking
failure and the next PM run fixes it on the spot.

Updated 2026-09-18 (Friday), owner-priority re-triage dispatch (incident 12,
all-hands decision 11): product quality is the release gate. This run
revises sprint-2026-09-21 in place (revision 2), reconciles the release
date against the score gate, cards the domain purchase, and audits every
coming-soon and empty surface on the site. See
docs/sprints/sprint-2026-09-21.md for the revised plan and the three new
sections below for the three items this dispatch owes the owner directly.
The next regularly scheduled PM ceremony (retro on the sprint that just
ran, grooming, sprint 2026-09-28) still runs Monday 2026-09-28 on its
normal cadence; this file does not replace that run.

## Open PRs waiting on your merge

1. **PR #23** (draft) — engineer, `engineer/2026-09-18-free-digest-spine-gate`,
   opened 2026-09-18. Ships revision 1's sprint items 1 through 3 in full:
   the digest teaser gate removed, the $20 spine gated in its place, a real
   issue on the archive. Still draft; not yet ready to merge. Once it is,
   the revised sprint (above) expects it merged before its own item 1
   starts, since the revised plan assumes items 1-3 are done.
2. **PR #21** — skill, `skill/2026-09-18-skill-validation-system`, opened
   2026-09-18. Designs the skill validation system and lands the first
   executable trigger-test slice against both gold skills. Ready for your
   review; the revised sprint's item 4 depends on it.
3. **PR #22** — sales, `sales/2026-09-18-first-customers`, opened
   2026-09-18. The first-50-customers plan, the idea list, the outreach
   machine, redispatched after the owner's creativity critique (incident
   11). Ready for your review.
4. **PR #18** — exo, `exo/2026-09-18` (run 2), opened 2026-09-18. README
   and architecture-diagram truthfulness sweep, charter §5b. Also carries a
   proposed charter addendum (draft-PR-first as an org-wide rule, all
   seats) that this run followed ahead of its own merge, since it matches
   what this dispatch was told to do directly. Ready for your review.

Everything else opened this week (#1-#17, #19, #20) is merged or closed.

## What each seat owes, and from which directive

- **engineer** — daily cadence. Sprint 2026-09-21 revision 2 (product-
  quality work first: prose benchmark, factual audit of sent issues, a
  tier-five checklist held against Monday's send, skill validation
  extended to both skills, receipts rendered) is committed and starts
  Monday 2026-09-21; nothing owed before then, and PR #23 already covers
  most of revision 1's site items ahead of schedule. Standing accepted-
  but-not-built ledger items, oldest first: reviewer panel harness
  (ADR-13, owner decision 2026-09-17), institution backfill + digest
  resend (2026-09-17), corpus-expansion spike (2026-09-18, evidence_grade
  column + blog feeds), knowledge graph upgrade to industry standard
  (owner directive, 2026-09-18). None are this sprint's focus; they carry.
- **skill** — Tuesday cadence. NEON_RO_URL is fixed and verified
  (2026-09-18, PR #16, 441 claims confirmed live). This week's run landed
  early and off-cadence as PR #21 (open above): the validation-system
  design plus the first executable trigger-test slice against both gold
  skills. Next Tuesday run: whatever #21 leaves open, plus continuing the
  production line per its own sequencing note in docs/ideas.md.
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
  activation, but PR #14 (launch campaign machinery), PR #17 (GEO +
  distribution plan), and now PR #22 (first-50-customers plan, open
  above, redispatched after incident 11's creativity critique) have all
  shipped and merged or opened since. That is a tracking gap: the org
  chart has not been updated to reflect the seat is active. Flagging
  again since fixing docs/agents/org-chart.md is outside this dispatch's
  scope too (named jobs are the sprint revision, the release-gate
  reconciliation, the domain card, and the coming-soon audit); the next
  PM ceremony should correct it.
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
9. **The release-gate reconciliation** (incident 12 / decision 11,
   2026-09-18) — Oct 13 conditional on the score, or a phased launch.
   Both options costed below in "Release-gate reconciliation." This is
   the open tension decision 11 itself named as yours to resolve.
10. **The domain** (decision 11, 2026-09-18) — you purchase; three
    candidate names proposed below in "Domain." No agent can buy it.

## Resolved since last noted (no longer pending)

- NEON_RO_URL secret — fixed and verified 2026-09-18 (skill agent, PR
  #16). docs/backlog.md's launch-runway table still shows this row as
  "pending"; that file is outside this run's writable surface to correct,
  flagging here so the next grooming run updates it.
- PROJECTS_TOKEN secret — done, board live since 2026-09-18 (mid-week PM
  run).

## Release-gate reconciliation (your decision, per decision 11)

Decision 11 set the gate (a five on the OKR benchmark) and named the
tension against it explicitly: "the PM must present back to the owner:
this gate versus the fixed Oct 13 date." Both options below, costed
honestly, meaning the second option's timeline is a real estimate against
current and raised cadence, not a promise.

**What "a five" would actually take.** The baseline (docs/okrs/okrs-2026-Q4.md,
2026-09-17) scored alexandria 1.3-3.3 across five axes against Elicit,
TLDR AI, and Anthropic's skills ecosystem; overall 2.6. Two of those axes
are inside alexandria's control this week: judgment (is the digest
accurate and does its claim graph hold up) and reader/agent actionability
for what already exists (is a skill honestly validated, does a claim
honestly cite). This sprint's revision 2 (docs/sprints/sprint-2026-09-21.md)
targets exactly those. Two of the five axes are not a days problem at any
price: **surface** (TLDR's 1.1M readers, Elicit's 2M-researcher product,
Anthropic's 176.9k-star ecosystem) and **speed at scale** (TLDR ships five
times a week to a list two orders of magnitude larger than alexandria's).
No amount of engineering days between now and Oct 13, or Oct 13 plus any
reasonable delay, closes a distribution gap that size. Those two axes move
with calendar time and compounding, not sprints.

- **Option A — Oct 13 becomes conditional on the score.** If "a five"
  means the full comparison-set average across all five axes, this is not
  achievable by any date in weeks; it is a distribution problem measured
  in months to years, and naming Oct 13-plus-N-days as conditional on it
  would just be a slower version of the same overclaim decision 11
  objects to. If "a five" instead means the axes alexandria actually
  controls today, accuracy, judgment, and an honestly validated library,
  brought to full and demonstrated as holding for more than one issue
  (so a clean week reads as a floor, not a lucky one-off), that is
  plausibly a 2-sprint problem: this sprint's items 1-4 land clean
  (5 engineer days), then one more sprint's digest repeats clean under
  the same checklist (another 5 days). Call it **10-14 engineer days,
  landing a conditional launch in the last week of October**, with the
  explicit caveat that the surface and speed axes still would not read
  as a five against the named comparison set, only the axes the gate's
  own language ("the product is the content") was actually about.
- **Option B — phased launch.** Free surfaces (the digest and the public
  site) ship 2026-10-13 as already planned; PR #23 already builds most of
  this, so the added cost is close to zero beyond what is already in
  motion. The $20 paid spine's gate opens only once the skills-repository
  side of the score reaches a five, meaning double digits of validated
  skills, not two. At the current Tuesday cadence (one draft skill a
  week, one validated so far), reaching a credible double-digit library
  (per docs/market/report-2026-09.md §7's own bar for the tier) is
  roughly **8-10 more weeks, mid-to-late November**. At a raised cadence
  (multiple validated skills a week, the shape this dispatch asked for,
  conditioned on staying honest rather than padded), it is plausibly
  **4-6 more weeks, mid-to-late October**, contingent on the ADR-13
  panel or an equivalent honest check existing to validate them, since
  "validated" cannot mean "shipped fast" without becoming exactly the
  padding decision 11 warns against.

Both options keep the digest free and public on Oct 13 either way; the
only thing either option gates is whether the $20 spine (or a broader
"launch") is allowed to call itself proven on that date. Your call.

## Domain (your purchase, per decision 11)

Decision 11 named a real domain as a release requirement. vision.md's
phase-2 plan already budgets roughly $12/yr for this and the launch
runway has no domain line item yet. Three candidates, none checked for
live availability this run (a registrar check takes you thirty seconds
at purchase time and this run has no way to query one honestly):

1. **alexandria.ai** — the direct brand match, and the TLD the product's
   own category (AI research and orchestration tooling) expects. Likely
   the most expensive or most likely already held of the three; worth
   checking first since it is the best outcome if available.
2. **tryalexandria.com** — the standard fallback shape when a bare brand
   domain is unavailable or priced beyond a $12-20/yr budget; cheap,
   almost certainly available, no brand confusion.
3. **alexandria.sh** — ties the domain to the audience the skills tier
   actually sells to (agent builders, the same crowd agentskills.io's
   own `.io` choice targets) and echoes a shell/tooling register that
   fits "directly applicable orchestration tools," the product's own
   differentiation line. A secondary, more distinctive option if `.ai`
   is gone.

Whichever you buy, the two Vercel/Clerk items already pending above still
need the domain attached once it exists; not a new blocker, just a
dependency to sequence after purchase.

## Coming-soon and empty-surface audit (per decision 11)

Every "Coming soon" string and every surface that renders empty on `main`
today, found by reading `site/app` directly, not by walking the deployed
site (there is no deploy yet). Each row states what removes it honestly,
not just what hides it.

| Surface | What's there today | Removal path |
|---|---|---|
| `/pricing`, both tier pills | Two "Coming soon" pills gate the only calls to action on the page, on top of stale $10/$30 tier copy | PR #23 (open) fixes the tier copy to free-plus-$20 but leaves both pills in place on purpose, as the insertion point for email capture. The pills do not come down honestly until that cut sprint item (email capture, or real Stripe checkout) is built and wired in; until then this page still oversells "coming soon" against something a visitor cannot yet do. |
| `/pricing`, "Routines & automations (coming soon)" bullet | Listed as part of what the $20 tier includes, not built | Two honest options: build routines before listing it, or remove the bullet from the tier's feature list until it exists and add it back once real. The second is nearly free and should not wait on a sprint slot. |
| `/routines` | Entire page is "Coming soon." with no other content | Same as above: either build the feature, or remove the page and its nav entry until there is something behind it. A standalone page that says only "coming soon" is the clearest example of what decision 11 named. |
| `/library` (archive) | Renders zero issues on `main` today, because `listIssues()` reads a gitignored directory with nothing checked in | PR #23 (open) fixes this with one real checked-in issue fixture. Its own PR body already names the next gap: the archive still needs to read the live `digests` table so future weeks do not require the same manual git-history recovery every time; that is a new proposed ledger entry from that PR, not yet built. |
| `/skills` | Renders real content, not empty, but lists exactly one skill against copy that promises "the best techniques the research has produced" | Not a coming-soon page, so not in scope of this audit's literal ask, but the same honesty problem in substance: this sprint's items 4 and 5 (validation extended to both gold skills, receipts rendered) are the fix in progress, and the market agent's own read (report-2026-09.md §6) already calls this "a promise, not a product" at n=1. |

Four items render as literally empty or "coming soon" today. Two already
have a merge-ready fix in flight (PR #23). Two (the routines bullet and
page) have no build dependency at all and could be corrected as a copy-
only change whenever an engineer session has a spare few minutes, ahead
of any sprint slot.
