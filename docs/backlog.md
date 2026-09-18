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
| PROJECTS_TOKEN secret for the PM's GitHub Projects board | owner | pending, see below |

## Leverage-ordered backlog

Ranked against vision.md §0 (autonomy tiebreak, launch mandate) and the
market agent's read of what a stranger needs before paying
(report-2026-09.md §6-7).

### Standing ledger (docs/ideas.md, accepted)

1. **Site pricing and gating for the new model** — not yet a separate
   ledger entry; this sprint's items 1-2 amend the "Member site auth and
   deploy" entry's design in place of adding a new one. See the grooming
   note on that entry.
2. **Reviewer panel harness (ADR-13)** — split into five day-sized pieces
   in the 09-17 grooming. Zero engineer PRs exist yet against any ledger
   item, so none of the five have shipped. Not scheduled this sprint;
   next candidate after the launch-runway items clear.
3. **Institution backfill, then regenerate and resend digest** — day-sized
   as written, carried past this sprint in favor of launch-runway site
   work. Next sprint's leading candidate if launch items land early.
4. **Member site auth and deploy** — superseded in shape by the free
   digest decision; see the dated note on the entry itself.
5. **Skill-extract prompt** — day-sized as written, not scheduled; the
   panel needs it before drafts exist to judge, but the panel itself is
   not this sprint's focus either.

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

**Note on pricing references:** the market report's numeric analysis
(§1-2, positioning.md's ladder) is built against the $10/$30 tiers the
owner's 2026-09-17 decision superseded (vision.md §0). The competitive
reads, the why-pay argument's structure, and the demand evidence still
hold; only the price points changed to free-plus-$20. This is the market
agent's own document to update (its next-run directive already includes
"update positioning.md for free-plus-$20"), noted here so nobody plans
against stale numbers in the meantime.

### Owner logistics (docs/allhands/2026-09-17.md, dated)

- Clerk keys and Neon connection string as Vercel env vars: by 2026-09-19.
- Stripe account and keys: by 2026-09-26.
- Merge or reject PRs #1, #2, #3 (72-hour window proposed, unanswered as
  of this run).
- Panel PR-merge PAT: by mid-November, not launch blocking.
- PROJECTS_TOKEN repo secret (fine-grained PAT, Projects read/write plus
  this repo's contents read), whenever convenient, to activate the PM's
  GitHub Projects board.

## GitHub Projects board

Not yet active. The owner's directive activates it once `PROJECTS_TOKEN`
exists as a repo secret; this run's token cannot read repo secrets to
confirm it either way (`gh secret list` returned a 403, expected for the
default Actions token). Until the owner confirms the secret is set, this
markdown backlog and the committed sprint file stay the source of truth,
per the charter's own instruction that the committed sprint file remains
authoritative regardless.

## Awaiting your verdict

Nothing has sat two weeks yet. Everything proposed above was opened
2026-09-17 or 2026-09-18. Flagging here anyway because there are ten
proposed entries and three open PRs stacked up after one all-hands: worth
a batch verdict pass rather than waiting for the two-week clock.
