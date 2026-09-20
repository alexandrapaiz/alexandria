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

Reconciliation result (first check, mid-week run): no board item needed
changing. The chair's seed already matched the skills-focus reorder above
(skill-extract prompt ranked up, claim-graph citations and trigger-tests
added as new items, reviewer panel resequenced to validator-first,
institution backfill dropped to last) before this file caught up to it.
All ten items were `DraftIssue` content (title and body only, no linked
GitHub issues), consistent with the board staying a lightweight visual
mirror rather than a second tracker. Status was Todo on all ten,
correctly: no engineer PR existed yet against any sprint 2026-09-21 item
(`gh pr list --state all`, checked that run) or any backlog item.

Updated 2026-09-18 (PM, owner-priority board update, off-cycle): between
that check and this run the security agent's PR #8 landed eight more
cards (three `urgent`, five `proposed`, matching docs/ideas.md's security
section), bringing the board to 19 before this run started. This run's
job, per direct owner instruction, was to make the board the complete
truth of everything pending across every seat, verifying each write with
a `gh api graphql` item query before moving to the next (see the
`gh project` quirk note below for why `graphql` rather than
`gh project item-list` directly). Added 17 cards, none duplicating an
existing title, confirmed against a full item dump after each batch:

- Four owner-logistics cards (Clerk keys + Neon in Vercel by 2026-09-19,
  Stripe account by 2026-09-26, the NEON_RO_URL secret for the skill
  agent, and the panel's PR-merge PAT by mid-November) — these were
  already rows in the launch-runway table above but had no board card.
- The skill agent's first extract-to-panel-to-gold run and its Tuesday
  cadence (ADR-22).
- The charter sweep adding board self-assign language to every seat's
  prompt (decision 8, third addendum), assigned to exo.
- The three source-discovery build items PR #10 (unmerged) proposes:
  automating the weekly meta-review seat (`agent-weekly.yml`), storing
  each paper's arXiv category, and a `sources.yaml` watchlist for authors
  and institutions without a feed.
- Aligning Q4 OKRs to the vision.md section 0 mission at the OKR agent's
  next check-in, now that the mission exists and the objectives predate
  it.
- Seven of the market agent's docs/ideas.md proposals not yet carded:
  the permanent free sample issue, llms.txt plus a skills manifest, the
  "left behind" flagship, the published head-to-head, the
  skill-verification badge, scoped skill delivery, and the
  orchestration-pattern benchmark. (Email capture was already sprint
  item 4; not duplicated.)

Board total after this run: 36 items, verified by a final full item dump
(`gh api graphql`, 2026-09-18). This file's launch-runway table and
leverage-ordered backlog above are unchanged by this run: sprint
composition and priorities stay as committed, per the owner's explicit
instruction that this was a board-completeness pass, not a replanning
one.

`gh project item-list`/`view` still fail with "unknown owner type" this
run, same as the mid-week check below documents; every read and write
this run went through `gh api graphql` against
`user(login: "alexandrapaiz") { projectV2(number: 4) }` instead, using
`GH_TOKEN=$PROJECTS_TOKEN`. Future runs: don't re-try the `gh project`
subcommands expecting a different result, they hit the same CLI quirk.

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

Also flagging a likely ledger mistake found while carding this run:
docs/ideas.md's "Permanent free sample issue on the site" (market agent,
2026-09-18) carries `Status: rejected` with the same verdict sentence
used on the four beyond-skills product proposals decision 6 explicitly
named (hosted RAG API, frontier-model synthesis tier, harness audit,
claim graph API). The free sample issue isn't one of those four and
isn't a beyond-skills product proposal at all; this reads like the
verdict text got copied onto the wrong entry rather than a deliberate
rejection. Carded on the board regardless since it's genuinely pending
either way, but worth your eyes to confirm the status is what you
intended.

## Owner orders queued for the frontend seat (2026-09-18, recorded by the chair)

Given live during the working session, to be executed by the next
frontend dispatch on PR #26's branch (a copy-revision run is in flight
as this is written; these fire the moment it lands):

1. **Hide the knowledge graph completely.** Nav link gone, every
   mention on home and pricing gone, the route unreachable. Code stays
   on the shelf; a visitor must have no idea it exists until it is
   industry standard.
2. **Density pass.** Some spaces look dense to the owner. Re-screenshot
   every page at the three viewports hunting for cramped spacing and
   open up the tight scenes.
3. **Reorganize the skills library to grow.** Design for fifty skills,
   not two: grouping, scannable structure, honest small-category
   states. The UX benchmark is Clerk: their flows, small states, and
   interaction quality, translated into the house black and white,
   never their look.
4. **The UI must make clear the product is for you AND your agents.**
   Both audiences, together: the builder reads the digest and library,
   the builder's agents load the same skills and cite the same claims.
   This is a positioning line the whole surface should carry, not one
   sentence on one page.

5. **The Alexandria line.** The owner wants a phrase in the UI built on
   this idea, in her words: "what we'd know if the library of
   alexandria was never burned down. like this product gets us there."
   The owner chose the line: "Catching up to the world where the
   library never burned." But NOT as a subtitle or any visible copy.
   She wants it as a hidden easter egg. Hide it where the curious
   look, one to three tasteful placements from: a comment at the top
   of the page's HTML source, a single quiet console message on
   load, a line in llms.txt where agents will genuinely find it (the
   best fit for "for you and your agents"), or the 404 page. Never
   a tooltip or hover on the hero mark, whose behavior stays
   untouchable. The visible surface does not carry the line at all.
   The mission-page compounding line is VETOED by the owner
   (2026-09-18): no visible Alexandria motif appears anywhere on the
   site. The hidden easter egg is the only place the idea lives. The seat places it where it carries most
   (likely the hero's supporting line or the mission page) and may
   tighten the wording, but the idea is fixed: the knowledge that
   compounds when the library never burns. It must not crowd the
   mission line, which stays exactly "Accelerate every builder to
   frontier speed." The retired subtitle stays retired.

## Agent identity: the Entra question (owner, 2026-09-18, ExO to deepen)

The owner saw Microsoft Entra Agent ID at NEXO: agents get first-class
directory identities like employees. She wants the alternatives for
alexandria considered before anything is adopted. The chair's opening
analysis is in the session record; candidates to compare properly:
one shared GitHub App (badge for all seats, holds the workflows
permission, closes the PAT question), per-seat GitHub Apps (full
least-privilege, more setup), machine user accounts (crude, seat-count
billing risk), per-seat fine-grained PATs (simplest, all minted off
the owner), and actual Entra with OIDC federation (enterprise-grade,
Microsoft dependency, overkill today). ExO's Sunday run should turn
this into a one-page recommendation with the migration cost of each.

## Daily digest cadence (owner order, 2026-09-19) + graph visualization

The owner: "lets produce a newsletter daily so we can see and improve
the product very easily." Cadence becomes daily; the engineer
implements (dispatched 2026-09-19); site and llms.txt copy that says
"weekly" follows once the cadence actually ships, not before. Related
card: evaluate a Neo4j AuraDB Free READ-ONLY MIRROR of the claims
graph for visualization (Bloom explorer) — Neon Postgres stays the
source of truth, nothing migrates; the mirror is a nightly export so
the owner can finally SEE the graph while the product graph page
stays hidden until industry standard. Proposal first, per the ledger
contract.

## Pipeline triage: weight traction over recency (owner's standing rule)

The owner, restated 2026-09-19 and stated repeatedly before: relevance
is impact of discovery, revealed by traction (citations, adoption,
being built upon), not release date. The research charter now carries
this as law; the PIPELINE should too. Card for the engineer and the
research seat's meta-review: audit prompts and triage scoring for
recency bias, and propose the change that makes citation velocity and
evidence of uptake outrank newness in what gets ingested, distilled,
and featured. Ledger proposal with the diff, owner merges.

## Signal/evidence source roles (owner direction, 2026-09-19)

The owner: our news-awareness exists so curation knows what to look
for in research; maybe RSS feeds to know what's actually gaining
traction. Design agreed: tag sources.yaml entries by role, evidence
(arXiv, HF papers, distilled into claims) versus signal (the 19
existing blog/release feeds plus a small news tier, e.g. Hacker News
front-page RSS), where signal sources are never distilled into
claims and instead feed the research seat's weekly signal read
(spikes cross-referenced against corpus coverage, ending in
ingestion steering). Engineer wires the role field and the signal
extraction; research consumes it in the brief. Ledger proposal with
the diff, owner merges.

## Sign-up → newsletter consent flow, and pricing via Clerk (owner, 2026-09-19)

Owner order for the queue: a login/signup flow with Clerk so that
after sign-up a person can consent to the newsletter (the waitlist
today writes a local file; after this, a signed-up user's consent
writes their email to subscribers with an explicit opt-in). Engineer
builds it on the Clerk foundation already wired (Core 3 Show API,
middleware live). Design the consent moment with the frontend seat:
one screen after sign-up, one checkbox, honest copy, no dark pattern.
The owner also asked how pricing links to the account: see the chair's
answer in the session record; the decision space is Clerk Billing
(subscription state on the Clerk user, Stripe underneath) versus a
Merchant of Record (Polar or Lemon Squeezy, required if Stripe is
unsupported in her country) with entitlement synced to Clerk metadata.
Engineer to write the ledger proposal with both wired end to end on
paper, since site/lib/entitlement.js (hasSpine) is the one seam either
option fills.
