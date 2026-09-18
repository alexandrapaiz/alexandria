# Sales agent workspace (ADR-24)

This directory holds the sales agent's campaign machinery: the plan,
the idea bank, the outreach machine, venue-tuned drafts, and results
tracking. One law governs everything here: **the agent prepares, the
owner sends.** Nothing in this directory has been posted, sent,
listed, registered, or contacted on its own.

## What is here

| File | What it is |
|---|---|
| `first-customers.md` | **The plan.** Day 1 to day 30 after launch (2026-10-13): eight lanes, named archetypes, the B2B lane, the day-by-day schedule, the floor plan if the launch post flops |
| `idea-list.md` | **The idea bank.** 49 sales and growth plays ranked by impact per unit of owner-effort, wild ones labelled, plus the explicitly rejected list |
| `outreach-plan.md` | **The machine.** Target categories with real example targets, weekly volumes, the sequence, and every draft written out in her voice |
| `b2b-lane.md` | **Extends `first-customers.md` §5** with three further B2B constructions (contradiction alerts, the deprecation audit, the open provenance spec), a correction to the graph size §5 quotes, and a proposed hard cap on the retainer product |
| `calendar.md` | The campaign calendar keyed to the launch runway and the Monday digest |
| `launch/` | Venue-by-venue launch-day drafts: email, HN, X, LinkedIn, Reddit, referral, pre-launch teasers |
| `outreach/list.md` | The four individually verified outreach targets, with public evidence of fit (absorbed into `outreach-plan.md`'s categories) |
| `distribution-plan.md` | The Thiel doctrine applied: which channel to master, CAC vs CLV at $20/mo, distribution built into the product |
| `geo-plan.md` | Getting cited and loaded by the machines that answer for us |
| `pitch-deck.md` | The deck |
| `results.md` | What actually happened. Real reported numbers only, never an estimate |

## Reading order, if you are new to this seat

`first-customers.md` first (it is the schedule everything else serves),
then `outreach-plan.md` (the engine behind it), then `idea-list.md`
(what to reach for when a lane stalls). `b2b-lane.md` only matters once
the first team conversation actually happens.

## Run log

- 2026-09-18 (run 1): calendar, launch drafts, outreach list,
  distribution plan, GEO plan, pitch deck.
- 2026-09-18 (run 2, owner dispatch answering docs/agents/incidents.md
  item 11): `first-customers.md`, `idea-list.md`, `outreach-plan.md`,
  then `b2b-lane.md` and the verification closure below. Two sales runs
  executed this dispatch concurrently; the second extended the first's
  work rather than overwriting it, which is why the B2B material lives
  in two linked files rather than one.
- 2026-09-18: **lane C3's open verification gap closed.** HN thread
  49689454's commenters, unverifiable on two previous runs because HN
  returned HTTP 429, were read via the public Algolia item API. The
  named practitioners and their exact quotes are in
  `outreach-plan.md` lane C.

Run started 2026-09-18. See docs/decisions.md ADR-24 and
prompts/sales-agent.md for the charter.
