# Pending tracker

Maintained by the PM agent every run (charter §1d): what every seat owes,
what sits in open PRs waiting on your merge, and what waits on an
owner-only action. Each line dated. You should never have to hold this in
your head; if something is owed and has no line here, that is a tracking
failure and the next PM run fixes it on the spot.

Updated 2026-09-18 (Friday night), triage dispatch following the closing
all-hands (docs/allhands/2026-09-18-close.md), owner order relayed by the
chair. This run: (1) folds the MCP redirect-URI fix into
sprint-2026-09-21 as a blocking item (see the sprint file's revision 3
note); (2) adopts the OKR seat's phased release gate as the **provisional**
planning assumption (free surfaces ship 2026-10-13, the $20 spine's gate
opens at a benchmark five), subject to the owner's veto when she reads
these minutes; (3) rules on the skill seat's second-extraction-session
proposal (adopted, written as a charter-and-workflow proposal in
docs/ideas.md for the ExO and owner to apply, since this seat cannot
commit to prompts/ or .github/workflows/ itself); (4) adds the new
owner-only items the closing all-hands surfaced; (5) carries a one-line
triage memo of every seat's ask from the closing all-hands, decided or
deferred, at the very end of this file. This supersedes this file's
earlier same-day (Friday daytime) snapshot in place; nothing below
should be read as still current from that earlier pass except where this
version repeats it unchanged. The next regularly scheduled PM ceremony
(retro on the sprint that just ran, grooming, sprint 2026-09-28) still
runs Monday 2026-09-28 on its normal cadence; this file does not replace
that run.

## Updated 2026-09-24 (Thursday standup, synchronous session)

**Why this file went six days stale.** No PM run wrote to this tracker
between 2026-09-18 and today. Not neglect: incident 23 (docs/agents/
incidents.md) put the PM's two runs in that window (2026-09-20 and
2026-09-21) on Kimi routing with no golden-set gate, and both failed at
30 turns before writing anything. The chair pulled the OPENROUTE
secrets the same week and this seat is back on Sonnet. Everything below
this section that is dated 2026-09-18 or earlier is the last real
snapshot; treat the items this section repeats as refreshed and
everything else in the older sections as historical record, not current
state, unless a line here says otherwise.

**Run mode.** Today is Thursday, the current sprint
(sprint-2026-09-21.md) runs through Sunday, and this file already said
the next ceremony is Monday 2026-09-28. This run is the daily standup
(charter §4), not the ceremony: no retro, no grooming, no new sprint
file. It is heavier than a normal standup only because of the six-day
gap above.

**Run health.**
- *GitHub Actions:* every non-success since the last PM run is already
  registered. The PM's own two failures are incident 23 (above). Two
  frontend failures from 2026-09-19 are incidents 17-18 (containerization
  uid fixes), also already closed. No new, unregistered failure class.
  Nine seats (engineer, exo, research, security, market, writer,
  frontend, skill, finance) are mid-run right now, dispatched by a human
  within the same two minutes (02:56-02:58Z) — expected in a synchronous
  session, not a failure.
- *Modal press cron (incident 24), tracked here per today's owner
  instruction:* still down. `groq/compound` 404s, the free tier has no
  model that fits the digest prompt at any size (engineer PR #75's
  finding: the entire viable free-tier catalog tops out at 8K TPM
  against a 9,865-token prompt before payload), and the fix is not yet
  merged, let alone deployed. Deployment has historically been a manual
  `modal deploy pipeline/<app>.py` step (see "Deploy action owed" below
  in this file's 2026-09-19 section, the same pattern), so merging PR
  #75 will not by itself make Monday's issue print — someone needs to
  run the deploy afterward. This seat has no Modal CLI access to check
  the schedule history directly; the ExO (PR #77) is postmortem-ing the
  same incident with more access than this seat has.

**Sprint 2026-09-21 progress** (evidence: merged PRs). Items 1 and 3
are done: item 1 (MCP redirect-URI validation) merged as PR #29
(2026-09-19); item 3 (factual verification audit) merged as PR #40
(2026-09-19). Items 2 and 4 are built but unmerged: item 2 (blind prose
benchmark) is PR #66, open, its own title says "built but unscored."
Item 4 (pre-send quality checklist) is PR #60, open. Item 5 (skill
validation on both gold skills) is in flight across PR #70 (open) and
PR #83 (today, draft) — see the PR-backlog section below for the
conflict between them. The full retro against this is Monday's job, not
today's; this paragraph exists so the owner does not have to reconstruct
sprint status from 26 open PR titles herself.

**The open pull request backlog: 26 PRs, oldest ~126 hours old.**
Nearly every one of them appends to `docs/ideas.md` and/or
`docs/agents/incidents.md`, so almost every merge after the first will
carry a one-hunk append conflict — cheap and expected (take both sides),
not a reason to reorder anything. The real complexity is that several
seats opened a new PR daily this week without their prior one merging,
so each day's PR says "built on" and "supersedes" the previous one. Once
the chains are collapsed, the 26 PRs are about 12 real merge decisions:

*Live chains — wait for today's head to finish, merge only the head,
close the rest of the chain unmerged (their content is already inside
the head, per each PR's own "supersedes" claim):*
- Writer: #55 → #62 → #67 → #71 → #74 → **#81** (today, draft). Merge
  #81 alone when ready; close #55, #62, #67, #71, #74 unmerged.
- Frontend: #56 → #73 → **#82** (today, draft). Merge #82 alone; close
  #56, #73 unmerged.
- ExO: #61 → #65 → **#77** (today). #77 itself says it must merge after
  #75 (below). Merge #77 alone; close #61, #65 unmerged.
- Research: #68 → **#78** (today, draft). Merge #78 alone; close #68
  unmerged.
- Security: **#31** (5 days old) → today's #79 (draft) explicitly says
  "close #31 unmerged." Trust the newer run's own call; close #31
  without merging once #79 lands.
- Skill: #70 (open, ready) and today's #83 (draft) are NOT a clean
  chain — #83 says plainly "close #70 in favour of this PR, or merge
  #70 first [then #83 after]," i.e. it names both orders as workable
  and leaves the choice to you rather than claiming one. Pick either;
  it is not a case where merging the wrong one loses work.

*Independent, ready to merge now, in the order their own dependency
notes imply:*
1. **#69** (engineer, sanitize digest HTML) — live XSS break-fix,
   branched from main, no stated dependency. Merge first on urgency.
2. **#75** (engineer, incident 24 press fix) — time-sensitive (the press
   is down), branched from main, ready. Merge before #77 (above).
3. **#66** (engineer, prose benchmark, sprint item 2) — branched from
   main, ready.
4. **#60** (engineer, quality checklist, sprint item 4) — ready, but its
   own body says "merge after #55 and #31." Flagging rather than
   resolving: #31 is being closed unmerged (not merged) per security's
   own #79, and #55 is superseded up the writer chain to #81 rather than
   being merged on its own. If #60's actual code dependency is "whatever
   #55 and #31 changed needs to already be on main" rather than
   literally those two PR numbers, merging after #81 and #79 land should
   satisfy it; if it depends on something PR-specific, that needs the
   engineer seat's own confirmation, not a guess from this seat.
5. **#72** (engineer, evidence-grade spike step 1) — its own body says
   "merge this PR last" relative to #35, #60, #66, #69. Sequence it
   after the other four engineer PRs above.
6. **#35** (engineer, daily digest, ~120h old) — superseded by #60
   itself (per #60's own title). Close unmerged once #60 lands rather
   than merging both.
7. **#80** (market, today, draft) — no chain, no stated dependency.
   Merge whenever it's ready.
8. **#84** (finance, today, ready) — no chain. See the finance note
   below.

**A ruling this file cannot make for you.** PR #83 (skill, today)
reports that incident numbers 23 through 29 are each claimed by at
least one currently-open branch in `docs/agents/incidents.md` — a
numbering collision across seats that write to the same append-only
file in the same week. This is exactly the kind of cross-seat collision
this tracker exists to surface rather than let you discover at a failed
merge. Worth a one-line ruling on which branch's numbering wins and
which seats renumber, the same way incident 19's renumbering was
handled.

**Finance ran today (PR #84), dormant-seat question.** `docs/agents/
org-chart.md` still lists finance as dormant, owner-activates (ADR-24).
Today's synchronous dispatch ran it directly and it shipped real work
(mid-month ledger refresh, GH Actions cost line resolved, MoR renaming,
lifetime-tier breakeven). Worth your one-line confirmation on whether
this is a one-off synchronous check-in or an actual activation — if the
latter, org-chart.md's dormant table needs updating, and that update
belongs to a PM run once you've said which it is, not to this seat's
guess today. Finance also repeats its one standing ask, verbatim from
2026-09-18: **the Claude subscription's monthly figure** — still the
only number it cannot get from any repo or public surface.

**Owner-only items still open, refreshed from the 2026-09-18 list
below** (see that list for full context on each):
1. Clerk keys + Neon connection string as Vercel env vars — still not
   confirmed. This may also explain a pattern in the open-PR backlog:
   most open PRs from #55 through #73 show a Vercel preview-build
   `FAILURE` status check (`gh pr view --json statusCheckRollup`),
   while the newest ones (#74 onward) show `SUCCESS`. That is consistent
   with these env vars having been missing and then fixed partway
   through the week, but this seat has no Vercel dashboard access to
   confirm the cause directly — flagging the correlation, not claiming
   the diagnosis.
4. Public git history holds a pre-privacy-pivot digest — still your
   call (rewrite vs. accept exposure).
5/13. The workflow-scope PAT / GitHub App `workflows` permission
   decision — ADR-33 (2026-09-24, this morning) found that
   `workflow_dispatch` works fine with the plain `GITHUB_TOKEN` given
   `permissions: actions: write`, which resolves the *dispatch* half of
   why this was blocking. It does not resolve the other half: a seat's
   own token still cannot push a fix to `.github/workflows/*` itself.
   Worth confirming whether ADR-27's shared-App plan is still wanted for
   that reason alone, or whether it's been overtaken by events.
11. The Claude subscription's monthly figure — repeated by finance today
   (above).
- Linear trial (charter §1e2): still on, no verdict since 2026-09-18
  (docs/finance/opex.md still has it "under evaluation").

Everything else in the 2026-09-18 snapshot below not repeated here is
either resolved (see "Resolved since last noted") or still genuinely
open with nothing new to add; read it as background, not as a live
picture of today.

## Board reorg (owner dispatch, 2026-09-18, done)

A second same-day dispatch, separate from the ops dispatch above: bring
GitHub Projects board #4 ("alexandria scrum") up to real Scrum
structure. Done entirely via `gh api graphql` with
`GH_TOKEN=$PROJECTS_TOKEN` against project 4 (`PVT_kwHOBqunQs4Bj3sN`);
nothing here touches this repo except this note.

**1. Status field rebuilt as a real flow.** Old: Todo / In Progress /
Done. New, in this order: **Backlog / Sprint Ready / In Progress / In
Review / Done**. `Todo` was renamed to `Backlog` in place
(`updateProjectV2Field`, same option ID), which is why every item that
was `Todo` came along automatically; `In Progress` and `Done` kept their
IDs too, so nothing on the board silently reset. `Sprint Ready` and `In
Review` are new options, added empty and populated below.

**2. A weekly `Sprint` iteration field**, one-week iterations starting
Monday 2026-09-21 as directed: Sprint 2026-09-21, -09-28, -10-05,
-10-12, -10-19 (5 iterations, covers the runway through launch with one
week of buffer after). Note the one-day drift from the runway plan's own
prose, which anchors its weeks to launch day (Tuesday 2026-10-13) and so
describes sprint 3 as "10-06 to 10-12": a Monday-start iteration can't
match that exactly. I mapped by nearest overlapping Monday week rather
than force a non-Monday iteration start, since "starting Mon 2026-09-21"
was explicit in the dispatch.

**3. Every card mapped truthfully**, checked against `gh pr list` and
this file's own open-PR tracking, not left as whatever the prior pass
left it:

- Moved to **Done** (all previously `Todo`, all confirmed merged):
  Sprint 09-21 items 1-3 (PR #23), "Design the skill validation system"
  (PR #21), "Define alexandria's distribution system (Thiel)" (PR #17;
  was stale at `In Progress`), "Charter fix: draft PR first" (landed in
  commit d47148b), "Carry: finish the 2026-09-18 visual run" (its three
  named pieces — desk alignment, mobile nav, focus ring, hover polish —
  all shipped across PR #15 and #19).
- Moved to **Sprint Ready** (committed to the current sprint, not
  started): Sprint 09-21 items 4-6 (email capture, hero metric,
  positioning.md).
- **In Progress and In Review are both empty right now**, and that's
  the truthful state, not a gap: nothing is mid-build outside a tracked
  PR at this moment, and no board card maps 1:1 to either of the two
  currently-open PRs (#22 sales first-customers, #24 PM sprint
  re-triage) closely enough to claim. Noted below as a real gap.
- **Iteration assigned only to genuinely committed/runway cards** (6
  Sprint 09-21 items + the 4 "Launch runway ·"/press-release/pre-mortem
  milestones dated to a specific runway week). Everything else keeps its
  existing Start/Target dates but carries no Sprint iteration, per the
  dispatch's "everything else stays Backlog with no iteration" — this
  includes items that happen to have this-week dates (e.g. the two
  urgent security findings) but were never part of the committed
  five-item sprint backlog itself.

**4. Backlog reordered product-first per decision 11** (digest and
skills quality first, plumbing after): the prose benchmark vs. TLDR,
institution backfill + digest resend, skill trigger tests, claim-graph
citations, the verification badge, the reviewer panel, and the
market-proposed proof pieces (head-to-head, "left behind" flagship, free
sample issue) now lead the 43-item Backlog. Launch-mechanics and urgent
items sit in the middle. Pipeline/architecture plumbing (traction-score,
discovery audit, arXiv category, sources.yaml, knowledge-graph upgrade,
CI/security hardening) sits at the bottom. This is a coarse two-ended
triage (quality pulled to the top, plumbing pushed to the bottom), not a
full 43-item hand ranking; the exact resulting order is on the board
itself (Table view, sorted by position) if you want to nudge anything.

**5. Views.** Board view already groups by Status and needs no action —
same field ID, so it inherits the new five-stage flow automatically.
Table and Board views now also show the new Sprint column (added via
`updateProjectV2View`). **Roadmap needs one owner click**: the GraphQL
API confirmed (tried it, got `"Roadmap views do not support visible
fields"`) that Roadmap view configuration — which field it groups
swimlanes by — isn't exposed to the API at all, unlike Board/Table's
`visibleFieldIds`. To see the runway by sprint: open the Roadmap view →
the "Group by" control in the view's toolbar → select **Sprint**. One
click, nothing else needed.

**Gap worth a verdict, not a build**: PR #22 (sales, open, the
first-customers plan) has no board card of its own — it's related to
but distinct from "Define alexandria's distribution system," which this
run marked Done against PR #17. Adding a card for it would be scope
creep on a board-craftsmanship-only dispatch; flagging instead for the
next PM ceremony or your call.

## Open PRs waiting on your merge

Refreshed twice this run: first when PR #18, #19, #21, #23 merged, then
again mid-run when PR #22 and #25 also merged (both while this PR was
still being written; that is why the "Board reorg" section above and the
sales docs/ tree above it are already on this branch — merged into it
directly). Two PRs remain open:

1. **PR #24** — pm, `pm/sprint-2026-09-21` (this PR). Carries the
   product-first sprint re-triage (revision 2) plus this closing all-hands
   triage (revision 3): the MCP fix as a blocking sprint item, the
   provisional phased-gate decision, the second-extraction-session ruling,
   and the triage memo at the end of this file. **Merge this one first**:
   it is the sprint plan and pending-tracker of record, and #26 also
   touches docs/ideas.md.
2. **PR #26** — frontend, `fe/2026-09-18-email-capture-live-metric`
   (draft). Ships the two site items revision 2 of the sprint cut (email
   capture, the live hero metric) on its own lane, screenshotted at three
   viewports. Touches docs/ideas.md; small risk of a grooming-note
   conflict with #24 there, cheap to rebase either way since #26's
   ideas.md edit is additive. Merge after #24 if a conflict appears.

## What each seat owes, and from which directive

- **engineer** — daily cadence. Sprint 2026-09-21 revision 3 (the MCP
  fix blocking and first, then the product-quality trio, then skill
  validation extended to both skills) is committed and starts Monday
  2026-09-21. Standing accepted-but-not-built ledger items, oldest first:
  reviewer panel harness (ADR-13, owner decision 2026-09-17), institution
  backfill + digest resend (2026-09-17), corpus-expansion spike
  (2026-09-18, evidence_grade column + blog feeds), knowledge graph
  upgrade to industry standard (owner directive, 2026-09-18). None are
  this sprint's focus; they carry. Revision 2's cut item 5 (receipts
  rendering) also carries, to sprint 2026-09-28.
- **skill** — Tuesday cadence, next run 2026-09-22. Owes two things from
  this triage: apply the harness-engineering trigger-vocabulary fix
  (docs/ideas.md, accepted this run) and re-run the trigger test, and
  continue the production line per PR #21's own sequencing note. A
  second weekly session (Fridays) is proposed but not yet charter text;
  it does not change this seat's obligations until the ExO applies it
  and the owner merges it.
- **frontend** — Wednesday cadence. This week's scoped visual run
  shipped early as PR #26 (open above, draft), covering both of
  revision 2's cut sprint items. Nothing further owed until next
  Wednesday.
- **market** — Friday cadence. Two runs shipped this week (PR #3, #6,
  merged). Proposals sit in docs/ideas.md under `proposed` or newly
  `accepted` this run (the Left-Behind flagship); none past the two-week
  grace period yet. One flagged action: positioning.md still carries
  stale $10/$30 numbers pending the market agent's own next-run update.
- **okr** — 1st-of-month cadence. First run shipped 2026-09-18 (Q4 OKRs +
  baseline benchmark, PR #2, merged). Its closing-all-hands floor
  statement proposed the phased gate this triage adopted provisionally;
  no further action owed until 2026-10-01, when it scores every KR
  against merged evidence and reruns the benchmark, except folding the
  mission (vision.md §0) into the objectives, already a noted follow-up.
- **security** — 1st and 15th cadence. First run shipped 2026-09-18
  (PR #8, merged). Of its three `urgent` findings: the MCP fix is now an
  assigned, blocking sprint item (no longer waiting on a separate owner
  go-ahead, per this dispatch); the digest-history rewrite and the
  workflows-permission grant still wait on the owner (below). Next
  scheduled run: 2026-10-01.
- **exo** — Sunday cadence, plus synchronous dispatches. Baseline run
  (PR #4) and run 2 (PR #18, README/diagram truthfulness sweep) both
  merged 2026-09-18. Owes, from this triage: applying the second-
  extraction-session charter-and-workflow text (docs/ideas.md, this run)
  to `prompts/skill-agent.md` and `.github/workflows/agent-skill.yml`, at
  its own discretion on timing, gated by the owner's merge like any
  charter change.
- **sales** — active (not dormant; org-chart.md is stale on this, flagged
  below). PR #14, #17, and now #22 (first-50-customers plan, redispatched
  after incident 11's creativity critique) have all merged. Its closing
  all-hands floor statement's three morning triggers (route the
  multi-seat Stripe question to engineer, send ten warm outreach notes,
  greenlight the Left-Behind Index page) are triaged in the memo at the
  end of this file.
- **research** — Monday 16:30 UTC cadence. `agent-research.yml` now
  exists (ADR-25 renamed the weekly seat; merged since this file's last
  snapshot), so this is the seat's first real scheduled run, expected
  today. Its closing all-hands floor statement said its one ask (direct
  Neon access) is already satisfied. Nothing else owed from this triage.
- **finance** — dormant, owner-activation pending (ADR-24). Its closing
  all-hands floor statement's one ask, the Claude subscription's monthly
  figure, is owner-only; see below.

## Owner-only actions waiting

1. **Clerk keys + Neon connection string as Vercel env vars** — due
   2026-09-19 (tomorrow). Not yet confirmed. Blocks the site deploy step
   of the launch runway.
2. ~~Stripe account and keys~~ — **REPLACED by ADR-30 (2026-09-19):
   Merchant of Record.** Owner creates the Polar account (Lemon
   Squeezy fallback), sets the API key and webhook secret as repo
   secrets, and adds the payout method. Due 2026-09-26. The engineer
   wires the product, checkout, and the webhook-to-Clerk entitlement.
3. ~~MCP OAuth redirect_uri validation gap~~ — **no longer waiting on
   you.** This dispatch made it a blocking, assigned sprint item (item 1
   of docs/sprints/sprint-2026-09-21.md revision 3), due before Stripe
   goes live 2026-09-26, per the owner's own order for this triage. Still
   worth your read of the finding (docs/ideas.md, security agent,
   2026-09-18) since it names PR-opening tools as what a stolen token
   would reach, but no action is waiting on you to unblock the build.
4. **Public git history holds a pre-privacy-pivot digest**
   (security, urgent, 2026-09-18) — nine historical commits of
   `digests/2026-W37.md` are readable by anyone who clones the public
   repo. Needs your call on rewriting history (BFG/`git filter-repo`,
   disruptive) versus accepting the exposure.
5. **DECIDED (ADR-27): one shared GitHub App.** Remaining owner step
   is the two-minute App creation (steps from the chair), then the
   chair wires it. Was: Grant the GitHub App `workflows` permission,
   or don't**
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
9. ~~The release-gate reconciliation~~ — **resolved by the owner,
   2026-09-18: ADR-26.** The gate is a benchmark FOUR, Oct 13 holds,
   product-first until launch. Supersedes the provisional phased gate.
   (Original framing kept below for the record.) Was: a provisional
   ruling awaiting her veto (incident 12 / decision 11, 2026-09-18, updated per the
   closing all-hands and this triage) — the OKR seat's phased-gate
   proposal (free surfaces ship Oct 13, the paid spine's gate opens at a
   benchmark five) is adopted **provisionally** as of this dispatch so no
   seat sat blocked overnight. Both options remain costed below in
   "Release-gate reconciliation" exactly as before. This is not yet your
   decision to make from scratch; it is your decision to ratify or veto.
   If you veto it or pick Option A instead, the sprint's item ordering
   does not need to change, only this framing and the paid-spine timeline
   in docs/agents/org-chart.md's initiatives and docs/okrs/.
10. **Sending the first ten warm outreach notes** — sales' plan (PR #22,
    merged) has these finished and ready; per the standing law, agents
    draft, only you send. Triaged in the memo below.
11. **The Claude subscription's monthly figure** — finance's one ask at
    the closing all-hands, so "gastamos" stops being a $0 placeholder in
    its unit-economics runs. A number only you can supply.
12. **Ten minutes of your eyes on the new email capture and live metric**
    — frontend's ask, once PR #26 (open above) lands. Not launch-blocking,
    but named directly as needing your attention, not a build.
13. **The workflow-scope PAT / GitHub App `workflows` permission
    decision** — restated here because the ExO's closing all-hands floor
    statement asked for it directly: it is the same decision as item 5
    above, blocking every seat's ability to land a workflow-file fix
    (including the second skill-extraction cron this run proposes in
    docs/ideas.md) without going through you by hand each time.
14. ~~The domain~~ — **DONE, 2026-09-18: the owner purchased
    libraryofalexandria.dev on GoDaddy.** Remaining: point it at Vercel
    (two DNS records at GoDaddy plus adding the domain in the Vercel
    project) once the env vars land. Decision 11's "real domain"
    non-negotiable is satisfied.

## Resolved since last noted (no longer pending)

- NEON_RO_URL secret — fixed and verified 2026-09-18 (skill agent, PR
  #16). docs/backlog.md's launch-runway table still shows this row as
  "pending"; that file is outside this run's writable surface to correct,
  flagging here so the next grooming run updates it.
- PROJECTS_TOKEN secret — done, board live since 2026-09-18 (mid-week PM
  run).

## Release-gate reconciliation (provisionally decided; yours to ratify or veto)

Decision 11 set the gate (a five on the OKR benchmark) and named the
tension against it explicitly: "the PM must present back to the owner:
this gate versus the fixed Oct 13 date." Both options below, costed
honestly, meaning the second option's timeline is a real estimate against
current and raised cadence, not a promise.

**Update, closing all-hands triage, 2026-09-18 night:** the OKR seat's
floor statement at the closing all-hands named Option B directly as its
recommendation, and the owner's dispatch for this triage run adopted it
as the provisional planning assumption, explicitly so no seat sits
blocked overnight. Read everything below as the reasoning behind that
choice, not as a menu still fully open; if you veto it when you read
these minutes, the sprint's item order (docs/sprints/sprint-2026-09-21.md)
does not need to change, since items 2-5 serve Option A's path just as
much as Option B's. Only the paid-spine timeline framing would change.

**What "a five" would actually take.** The baseline (docs/okrs/okrs-2026-Q4.md,
2026-09-17) scored alexandria 1.3-3.3 across five axes against Elicit,
TLDR AI, and Anthropic's skills ecosystem; overall 2.6. Two of those axes
are inside alexandria's control this week: judgment (is the digest
accurate and does its claim graph hold up) and reader/agent actionability
for what already exists (is a skill honestly validated, does a claim
honestly cite). This sprint (docs/sprints/sprint-2026-09-21.md, now
revision 3, items 2-5) targets exactly those; item 1, added this triage,
is the MCP security fix and does not itself move this score. Two of the
five axes are not a days problem at any
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
  plausibly a 2-sprint problem: this sprint's items 2-5 land clean
  (5 engineer days, unchanged from before item 1 was added, since item 1
  is a same-week security fix that does not add engineer-days to this
  count), then one more sprint's digest repeats clean under
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
  (a second weekly extraction session, adopted this triage as a
  charter-and-workflow proposal in docs/ideas.md, conditioned on staying
  honest rather than padded), it is plausibly
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
| `/pricing`, both tier pills | Two "Coming soon" pills gate the only calls to action on the page, on top of stale $10/$30 tier copy | PR #23 (merged) fixed the tier copy to free-plus-$20 but left both pills in place on purpose, as the insertion point for email capture. PR #26 (open, draft) now wires real email capture into both pages; once it merges these pills should come down as part of that same change, not linger as leftover copy over a feature that now exists. |
| `/pricing`, "Routines & automations (coming soon)" bullet | Listed as part of what the $20 tier includes, not built | Two honest options: build routines before listing it, or remove the bullet from the tier's feature list until it exists and add it back once real. The second is nearly free and should not wait on a sprint slot. Still open as of this triage. |
| `/routines` | Entire page is "Coming soon." with no other content | Same as above: either build the feature, or remove the page and its nav entry until there is something behind it. A standalone page that says only "coming soon" is the clearest example of what decision 11 named. Still open as of this triage. |
| `/library` (archive) | Renders zero issues on `main` today, because `listIssues()` reads a gitignored directory with nothing checked in | PR #23 (merged) fixed this with one real checked-in issue fixture. Its own PR body already names the next gap: the archive still needs to read the live `digests` table so future weeks do not require the same manual git-history recovery every time; that is a proposed ledger entry (docs/ideas.md, engineer agent), not yet built. |
| `/skills` | Renders real content, not empty, but lists exactly one skill against copy that promises "the best techniques the research has produced" | Not a coming-soon page, so not in scope of this audit's literal ask, but the same honesty problem in substance: this sprint's item 5 (validation extended to both gold skills) is the fix in progress; the receipts-rendering item that would surface it on the page itself carried to sprint 2026-09-28 (see revision 3 note). The market agent's own read (report-2026-09.md §6) already calls this "a promise, not a product" at n=1. |

Four items were flagged as literally empty or "coming soon." Two now have
a merged fix (`/pricing` tier copy via PR #23, `/library` via PR #23) or
an open one close behind (`/pricing`'s pills via PR #26). Two (the
routines bullet and page) still have no build dependency at all and could
be corrected as a copy-only change whenever an engineer session has a
spare few minutes, ahead of any sprint slot.

## Triage memo: the closing all-hands, 2026-09-18 night

One line per seat's ask (docs/allhands/2026-09-18-close.md), decided or
deferred-to-owner, and why. Seats with no explicit ask (ExO's floor
statement named one, folded in below) are omitted.

1. **Engineer** — "merge #24 or say which sprint file is live." Decided:
   revision 3 of sprint-2026-09-21.md (this file's companion) is the live
   plan as of this triage; it becomes binding on your merge of PR #24,
   same as every sprint.
2. **PM (self)** — "the decision 11 ruling." Decided provisionally: the
   phased gate (Option B), pending your veto. See "Release-gate
   reconciliation" above.
3. **OKR** — "the written decision 11 ruling, so October's KR1 has one
   target." Decided provisionally, same ruling as above; the OKR seat's
   own Oct 1 check-in is the next point it gets re-confirmed against
   evidence.
4. **Market** — "whether positioning and pricing claims stay frozen until
   decision 11 resolves." Decided: yes, frozen, since the provisional
   ruling could still be vetoed and a published price claim is harder to
   walk back than a ledger entry. This is a backlog/schedule call within
   PM authority, not a pricing decision itself.
5. **ExO** — "the workflow-scope PAT decision." Deferred to owner: this
   is a GitHub App installation permission, a real authority question
   (per decision 4's carve-out for what the owner alone reserves), not
   something decidable by any agent. Tracked above as items 5 and 13.
6. **Security** — "a decision on the digest-history rewrite." Deferred to
   owner: rewriting public git history is disruptive (force-push, breaks
   two in-flight branches and any existing clones) and irreversible in
   practice; squarely the kind of call decision 4 reserves. Tracked above
   as item 4.
7. **Skill** — "the decision 11 ruling, and whether the failing trigger
   case gets fixed before launch or ships red." Decision 11: same
   provisional ruling as above. The trigger case: decided, fix it on the
   seat's normal Tuesday cadence (docs/ideas.md, accepted this run).
8. **Frontend** — "ten minutes of the owner's eyes on the new email
   capture and live metric." Deferred to owner: her attention is the ask
   itself. Tracked above as item 12.
9. **Research** — no decision needed; its one ask (direct Neon access)
   was already satisfied before this triage.
10. **Finance** — "the Claude subscription's monthly figure." Deferred to
    owner: it is a real dollar figure, squarely money, decision 4's other
    carve-out. Tracked above as item 11.
11. **Sales** — "merge PR #22." Merged by you since this triage started
    (no further action). Its three named morning triggers, decided
    separately: the multi-seat Stripe question is already a proposed
    ledger entry inside PR #22's own docs/ideas.md addition, no new action
    needed; sending the first ten outreach notes is deferred to owner
    (item 10 above, "you send, per the law"); the Left-Behind Index page
    is decided (accepted, docs/ideas.md, this run), since greenlighting a
    page build is a product/backlog call
    within PM authority, not money, a secret, or purpose.

## Deploy action owed: the triage fix (engineer, 2026-09-19)

Added by the engineer seat under the owner's URGENT dispatch of 2026-09-19,
which directed this seat to write the deploy command into this file. This is
the one exception to the rule that the engineer seat never edits
`docs/sprints/`; it is append-only and the PM should treat it as a handover
note, not as planning.

**Merging the PR does not deploy anything.** `docs/scaling.md` states the
current CI/CD honestly: "Push to main, `modal deploy` by hand". Modal runs the
last deployed version of the app, so the tier-fairness fix in
`pipeline/triage.py` sits inert on `main` until someone runs:

    modal deploy pipeline/triage.py

Owner's or chair's action, dated 2026-09-19. Until it runs, the daily 12:00
UTC triage cron keeps executing the old inverted `ORDER BY` and the arXiv
firehose keeps going unread.

Two things to check in the first run's logs afterwards, both new in this
change and both one line:

1. `queue: tier <t>: <n> waiting, oldest <date>` for every tier. The `oldest`
   date on tier `a` is the real expiry deadline for the backlog, which
   `docs/product/triage-capacity.md` could only estimate.
2. `triaged <n> papers ... (a=..., b=...)`. More than one tier in that split
   is the acceptance evidence. One tier means the inversion is back.

Related and separate: research's PR #42 adds `cs.CR` to `sources.yaml`. The
chair redeployed ingest on 2026-09-19, so that one flows with the next ingest
deploy and needs no action here. The two changes are independent, but `cs.CR`
is inert without this one, since new tier `a-low` papers would queue behind
the same wall.

While the logs are open, `modal app logs alexandria-triage` also answers the
open throughput question: the 429's body names which Groq limit binds, and
`docs/product/triage-capacity.md` §"What would actually raise throughput" says
what to do with each possible answer.
