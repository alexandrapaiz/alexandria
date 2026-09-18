# Sprint review — content for the owner's presentation, 2026-09-18

Slide-by-slide content, prepared by the PM agent for the owner to lift
directly into slides. Source data: docs/sprints/pending.md (this run),
docs/sprints/sprint-2026-09-21.md, docs/backlog.md, docs/ideas.md, and
`gh pr list --state all` as of 2026-09-18.

## Slide 1 — The launch runway

One sentence: **free digest, $20 spine, live by 2026-10-13.**

| Date | Milestone | Status |
|---|---|---|
| 2026-09-17 | All-hands: pricing decided (free digest + $20 spine), launch date set | done |
| 2026-09-19 | Clerk keys + Neon connection string in Vercel (owner) | due tomorrow, not yet confirmed |
| 2026-09-21 to 09-27 | Sprint 1: site pricing/gating, real archive content, email capture, live hero metric | starts Monday |
| 09-26 | Stripe account + keys (owner) | due |
| 09-28 to 10-05 | Runway sprint 2: deploy + payments wiring | planned |
| 10-06 to 10-12 | Sprint 3: hardening, panel, polish | planned |
| 10-13 | **Launch** | target |

Three items still gate the runway and wait on you: Clerk/Neon env vars,
Stripe keys, and the three urgent security findings below.

## Slide 2 — This sprint's goal and items

Sprint 2026-09-21, goal: *give the site a truthful front door for the
free-plus-$20 launch runway.* Not yet started (opens Monday 2026-09-21).

| # | Item | Owner | Status |
|---|---|---|---|
| 1 | Remove the digest teaser gate; issue pages render full content | engineer | not started |
| 2 | Gate the skill library, claim graph, and automations behind the $20 spine | engineer | not started, depends on 1 |
| 3 | Real digest content on the site's archive | engineer | not started |
| 4 | Email capture on home and pricing | engineer | not started |
| 5 | Make the hero metric live | engineer | not started |

Plan capacity note: engineer ships at most one PR per day, so five items
is a ceiling for the week, not a guarantee all five land.

## Slide 3 — Triage summary (the week so far)

- 19 PRs opened since 2026-09-17; 15 merged, 2 closed, 2 still open
  awaiting your merge (exo run 2, frontend nav/hover polish).
- Every active seat has now run at least once: engineer, skill, frontend,
  market, okr, security, exo, sales, pm. Only the weekly/research seat
  has no workflow file yet (still a `proposed` engineer build).
- Three security findings landed `urgent` and need your decision, not an
  engineer build: an MCP OAuth redirect_uri gap, a pre-privacy-pivot
  digest still readable in public git history, and whether to grant the
  GitHub App `workflows` permission.
- The skill production line's blocker (empty NEON_RO_URL) is fixed and
  verified; the first real draft skill was pulled from a live 5-paper
  claim cluster this week.
- Two incidents this week: agent runs shipping nothing under a low turn
  cap (docs/agents/incidents.md #10, escalated to the ExO, cap raised to
  140) and one run operating in a shared checkout (#5, closed by moving
  to isolated Actions checkouts). Both have fixes in place or in
  progress.
- One tracking gap found this run: the org chart marks the sales seat
  dormant, but it already shipped two merged PRs this week. Needs a
  correction at the next PM ceremony.

## Slide 4 — Top pending items

The three most important lines from docs/sprints/pending.md, in order:

1. **Clerk + Neon env vars in Vercel** — due tomorrow (2026-09-19), still
   unconfirmed. Blocks the site deploy step of the launch runway.
2. **Two open PRs waiting on your merge** — exo's README/diagram sweep
   (still in draft) and frontend's nav/focus/hover polish (ready now).
3. **Three urgent security findings need a decision, not a build** — the
   OAuth redirect_uri gap, the exposed pre-pivot digest in git history,
   and the workflows-permission question. None are launch-blocking by
   date, but all three gate real fixes that are otherwise ready to ship.

Full detail on every pending item: docs/sprints/pending.md.

## Slide 5 — Board and views (project 4, "alexandria scrum")

56 items on the board, all now carrying Start date and Target date. State
verified live via `gh api graphql` with `GH_TOKEN=$PROJECTS_TOKEN` (the
`gh project` CLI subcommands still hit the known "unknown owner type"
quirk on a user-owned project; go straight to `graphql`).

**Start date / Target date fields.** Already existed on the board,
carried over from an earlier attempt at this same mandate (GraphQL
mutations against a live project persist even when the agent run that
made them dies mid-session and ships no PR, unlike file edits — this
explains why the board was already partway done going into this, the
third attempt). 51 of 56 items already carried correct dates matching
the requested ranges (sprint 09-21 to 09-27, runway sprint 2 09-28 to
10-05, sprint 3 10-06 to 10-12, launch 10-13). This run populated the 5
that were still blank: the press release/FAQ and launch pre-mortem
(sprint 3 / pre-launch), the board's own WIP-limit task (this week), and
two carried frontend items (next Wednesday's cadence and the runway-2
best-in-class benchmark pass).

**Stale statuses.** Checked all three categories you named:
- Agent-weekly automation: already `Done` on the board, and correctly
  so. `prompts/weekly-agent.md` was renamed to `prompts/research-agent.md`
  at some point, and `.github/workflows/agent-research.yml` runs it
  Mondays 16:30 UTC. docs/ideas.md's engineer-agent entry proposing a new
  `agent-weekly.yml` predates this and is now itself stale (the need it
  names is already met under a different file name); worth a note at the
  next grooming pass, not fixed here since docs/ideas.md grooming isn't
  one of this run's four jobs.
- Mission-on-site: already `Done`, and correctly so — PR #15 (the
  purpose line on /mission) is merged.
- Security items fixed in merged PRs: checked PR #8's actual file diff
  (db/schema.sql, pipeline/weekly.py) against the board. The "two
  stale-doc fixes" mentioned in that PR's title never had their own
  board card (too minor to have been carded individually), so there is
  no stale status to correct here. Every `Security ·` card still on the
  board (redirect_uri gap, git-history purge, workflows permission, and
  five smaller findings) is genuinely still open and correctly `Todo`.

**Roadmap and Board views.** Attempted `createProjectV2View` via
GraphQL: it works (the mutation exists and is not blocked by scope).
Turned out to be moot for this project specifically — GitHub creates a
Table, a Board, and a Roadmap view by default on every new Projects v2
board, and project 4 already has all three (verified via a `views`
query before touching anything). Board groups by Status already, and
Roadmap will now render a real timeline since every item carries a
Start/Target date as of this run. No UI fallback steps needed: the API
path worked end to end, confirmed by creating then cleanly deleting a
throwaway pair of views as a live test (`deleteProjectV2View` takes only
`viewId`, not `projectId`, worth remembering for next time).

Net result: the views-and-presentation mandate is done. Nothing on this
list needs a manual UI step from you.
