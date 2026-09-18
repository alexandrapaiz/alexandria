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

See the "Board hygiene" and "Roadmap/Board views" sections below, filled
in after this run's GitHub Projects work.
