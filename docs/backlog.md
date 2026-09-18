# Backlog — the consolidated board

Built by the project manager agent (prompts/pm-agent.md, ADR-15) on the
owner's directive at the 2026-09-17 all-hands (docs/allhands/2026-09-17.md):
one place holding absolutely everything from every agent. Rebuilt each
Monday during grooming.

This file does not replace the ledger contract. docs/ideas.md remains the
engineer's proposal surface and the owner's verdict surface exactly as
prompts/engineer-agent.md defines: the agent appends, the owner writes
verdicts, statuses only the owner changes. This file is a leverage-ordered
read of that ledger plus every other agent's proposals and the launch
logistics, so nothing needs hunting across four documents to see the whole
board.

Updated 2026-09-18 (PM, mid-week run, owner directive): reconciled against
the GitHub Projects board (below) and against decisions 6-8 recorded at the
2026-09-17 all-hands after this file was first built — the skills-focus
call, ADR-22's skill agent, and the ExO's GitHub stewardship. This file had
gone stale on those three points since its own commit landed before that
grooming did; the reorder below brings it back in sync with what the board
already reflected.

## Launch runway to 2026-10-13

The owner set the launch date at the all-hands. These are the items that
gate it, gathered from vision.md §0, docs/roadmap.md, the market agent's
walkthrough (docs/market/report-2026-09.md §6), and the all-hands owner
logistics.

| Blocker | Owner of the work | Status |
|---|---|---|
| Site pricing and gating match free-digest-plus-$20-spine, not the old $10/$30 teaser design | engineer | in this sprint |
| Digest archive shows real, full content (not an empty page) | engineer | in this sprint |
| A way to leave an email before Stripe exists | engineer | in this sprint |
| Hero metric is real, not hardcoded | engineer | in this sprint |
| Clerk keys + Neon connection string as Vercel env vars | owner | due 2026-09-19, not yet confirmed |
| Site deployed on Vercel (ALEX team) | engineer, blocked on the row above | not started |
| Stripe account and keys | owner | due 2026-09-26 |
| Payments wired to the $20 spine | engineer, blocked on Stripe keys | not started |
| Institution backfill so the digest's metadata is clean | engineer | groomed, carried past this sprint |
| Reviewer panel (provenance, adversary, validator, autonomous merge) | engineer | accepted, split, not this sprint's focus |
| PR-merge token scope for the panel's autonomous merge | owner | not yet minted, not launch-blocking |
| PROJECTS_TOKEN secret for the PM's GitHub Projects board | owner | done 2026-09-18, board live, see below |
| NEON_RO_URL secret for the skill agent's read-only DB access (ADR-22) | owner | pending |

## Leverage-ordered backlog

Ranked against vision.md §0 (autonomy tiebreak, launch mandate) and the
market agent's read of what a stranger needs before paying
(report-2026-09.md §6-7).

### Standing ledger (docs/ideas.md, accepted)

Reordered 2026-09-18 for the skills-focus decision (all-hands decision 6:
"for sellable products lets focus on skills for now") and ADR-22 (the
weekly skill agent, commissioned the same night). This is the order now
live on the GitHub Projects board.

1. **Site pricing and gating for the new model** — not yet a separate
   ledger entry; this sprint's items 1-2 amend the "Member site auth and
   deploy" entry's design in place of adding a new one. See the grooming
   note on that entry. Still this sprint's active work, unaffected by the
   reorder below.
2. **Skill-extract prompt** — ranks up. ADR-22's skill agent runs weekly
   from Tuesday and needs this prompt before it has anything to draft
   from; day-sized as written, next candidate once the site sprint clears
   capacity.
3. **Claim-graph citations rendered in the library** — new, not yet a
   separate ledger entry. Decision 6's composed thesis names claim-graph
   citations as skills' headline differentiator ("skills with receipts,"
   no marketplace does this). Closest existing proposal is the market
   agent's "Show each skill's validation evidence on its page"
   (docs/ideas.md, proposed 2026-09-18); worth a verdict on that entry
   specifically, since it is most of this item already.
4. **Reviewer panel harness (ADR-13)** — still split into five day-sized
   pieces from the 09-17 grooming, but resequenced to lead with the
   validator reviewer (A/B validation gates promotion) rather than
   provenance first, since validated evidence is now the sellable claim.
   Zero engineer PRs exist yet against any of the five.
5. **Trigger tests for every skill before launch** — new, not yet a
   separate ledger entry. ADR-22 already requires a five-prompt trigger
   test in every skill-agent PR; this item is making that a launch gate
   for the library as a whole, not just new skills, after the market
   audit's finding that 69% of public skills never reliably fire
   (docs/allhands/2026-09-17.md, decision 6 background).
6. **Institution backfill, then regenerate and resend digest** — day-sized
   as written, drops to last under the skills reorder, carried past this
   sprint in favor of launch-runway site work. Not skills-related, so it
   waits behind items 2-5 rather than losing its place entirely.
7. **Member site auth and deploy** — superseded in shape by the free
   digest decision; see the dated note on the entry itself.

### Proposed (docs/ideas.md, all under the owner's two-week grace period, none stale yet)

From the OKR agent (docs/okrs/okrs-2026-Q4.md, PR #2, unmerged):

- Public digest archive page — now largely absorbed into this sprint's
  item 3 (the digest is free, so the "archive" and the "library preview"
  are the same problem). Worth a verdict regardless, since it also covers
  older issues once more than one exists.
- List the gold skills at agentskills.io — a distribution move for later,
  once more than one skill is promoted. Low leverage until O2's library
  has more than one entry.

From the market agent (docs/market/report-2026-09.md, PR #3, unmerged),
eight proposals, ranked by this sprint's read of leverage:

1. Permanent free sample issue on the site — folded into this sprint's
   item 3; the free-digest decision makes the whole archive the sample,
   not just one issue.
2. Email capture before payments exist — this sprint's item 4.
3. Make the hero metric live — this sprint's item 5.
4. A published head-to-head (alexandria skill vs. a free marketplace
   skill) — high value for the $20 spine's credibility, but needs a
   second skill to be interesting and the panel to validate it first.
   Next quarter's work, tracked here so it is not lost.
5. Show each skill's validation evidence on its page — same dependency,
   one skill is not yet a "library."
6. Make "left behind" the public flagship — good marketing idea, waits on
   the site actually being deployed.
7. Agent-readable public surface (llms.txt, skills manifest) — cheap and
   real, but behind deploying the site at all.
8. A free teaser skill on public directories — needs the owner to do the
   actual listing; prepare the files once a second skill exists.

From the engineer agent (docs/ideas.md, 2026-09-18 run): four sellable-
product proposals beyond skills (hosted RAG API, frontier-model synthesis
tier for RAG, harness audit as a sellable service, claim graph API) all
carry owner verdicts of rejected-for-Q4, per decision 6. They stay in the
ledger as later candidates, not current work; may be re-proposed after Q4.
The "Claim graph API" entry was missing its Status line in the ledger
(likely dropped in one of the same-night ideas.md merges) despite the
other three carrying theirs; added the matching rejected verdict this run
so all four read consistently. "Agent packs: skill + activation prompt as
a priced SKU" is a fifth, separate engineer proposal, still `proposed`,
not one of the four decision 6 named — it is itself a skills-focused idea,
not a beyond-skills one, so decision 6 does not resolve it either way.

Also new since this file's first build: ADR-22 commissions a weekly
skill agent (Tuesdays), owning extract-to-panel-to-gold for the skill
library; its database access waits on the owner's NEON_RO_URL secret
(added to the launch-runway table above). Decision 8 adds GitHub
stewardship (stale-PR flags, merged-branch cleanup, this Projects board)
to the ExO's charter, not the PM's; noted here so nobody assumes the PM
owns repo hygiene beyond its own writable surface.

**Note on pricing references:** the market report's numeric analysis
(§1-2, positioning.md's ladder) is built against the $10/$30 tiers the
owner's 2026-09-17 decision superseded (vision.md §0). The competitive
reads, the why-pay argument's structure, and the demand evidence still
hold; only the price points changed to free-plus-$20. This is the market
agent's own document to update (its next-run directive already includes
"update positioning.md for free-plus-$20"), noted here so nobody plans
against stale numbers in the meantime.

### Owner logistics (docs/allhands/2026-09-17.md, dated)

- Clerk keys and Neon connection string as Vercel env vars: by 2026-09-19,
  not yet confirmed.
- Stripe account and keys: by 2026-09-26.
- Merge or reject PRs #1-#7: done, all merged or closed as of this run
  (`gh pr list --state all`, checked 2026-09-18). PR #8 (security agent's
  first-run audit) is open and unreviewed.
- Panel PR-merge PAT: by mid-November, not launch blocking.
- NEON_RO_URL secret for the skill agent's read-only DB access (ADR-22):
  whenever convenient.
- PROJECTS_TOKEN repo secret: done. Board verified live this run, see
  below.

## GitHub Projects board

Live as of 2026-09-18 (mid-week run, owner directive). The chair seeded
user project #4, "alexandria scrum"
(https://github.com/users/alexandrapaiz/projects/4), with all five sprint
2026-09-21 items and five backlog items, all in Todo. This run verified
`PROJECTS_TOKEN` access and reconciled the board's contents against this
file and docs/sprints/sprint-2026-09-21.md.

Verification note: `gh project view/item-list` fail with "unknown owner
type" and, on `--owner @me`, a missing-scope error asking for
`read:org`/`read:discussion` — the token's actual scopes are `project`,
`repo`, `workflow`, `write:packages`, which the GitHub Projects v2
GraphQL API (`user(login:...) { projectV2(number:...) }`) accepts fine.
This is a `gh` CLI subcommand quirk (it over-requests org scopes even for
a user-owned project), not a real access gap. Future PM runs: use
`gh api graphql` directly against the board rather than `gh project *` if
the same error recurs.

Reconciliation result: no board item needed changing. The chair's seed
already matched the skills-focus reorder above (skill-extract prompt
ranked up, claim-graph citations and trigger-tests added as new items,
reviewer panel resequenced to validator-first, institution backfill
dropped to last) before this file caught up to it. All ten items are
`DraftIssue` content (title and body only, no linked GitHub issues),
consistent with the board staying a lightweight visual mirror rather than
a second tracker. Status is Todo on all ten, correctly: no engineer PR
exists yet against any sprint 2026-09-21 item (`gh pr list --state all`,
checked this run) or any backlog item.

Board stewardship, for future runs: the committed sprint file stays the
source of truth, as the charter and the owner's directive both say. This
backlog file is the leverage-ordered narrative behind it. The board is a
visual mirror of both, kept in sync at each Monday grooming-and-planning
ceremony by default; an off-cycle reconciliation like this run happens
only on explicit owner instruction. If the board and the committed files
ever disagree, the files win and the board gets corrected to match, never
the reverse.

## Awaiting your verdict

Nothing has sat two weeks yet. Everything proposed above was opened
2026-09-17 or 2026-09-18. Flagging here anyway because there is one open
PR (#8, security agent) and a worthwhile early pick given this run's
reorder: "Show each skill's validation evidence on its page" (market
agent, proposed 2026-09-18) is now most of standing-ledger item 3 above
(claim-graph citations in the library), so a verdict on it sooner rather
than later would unblock that item directly instead of waiting on a
fresh proposal to duplicate it.
