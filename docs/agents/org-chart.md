# Org chart

**Enforced at:** prompts/pm-agent.md §1b, which updates this page whenever seats or initiatives change and flags any initiative with no seat.

Maintained by the PM agent (charter §1b). Owner is Product Owner and
merges everything; the ExO reviews the workers; every seat is one PR
per run. Seeded 2026-09-18 by the chair; the PM keeps it current.

## Active seats

Cadence below is each seat's scheduled cron, read fresh this run from the
host manifest (`gh api .../runtime/agents/alexandria/<seat>/agent.toml`),
corrected from the GitHub-Actions-era wording this table carried since
2026-09-18. **The cron is the floor, not the whole picture.** Since
decision 056 (2026-10-17) moved every seat's clock off GitHub Actions, the
dominant trigger all day, every day, is an event-driven `message` wake, not
the cron: today alone (2026-11-09) this seat's own board rows show pm,
exo, research, security, skill, and engineer all running repeatedly on
`window:message` triggers between runs, dozens of times across the fleet.
Cadence is a lower bound on how often a seat runs, not a description of
how often it actually does.

| Seat | Charter | Cron cadence | Max turns | Lane | Current initiative |
|---|---|---|---|---|---|
| engineer | prompts/engineer-agent.md | daily 11:06, 23:06 UTC | 300 | product code, pipeline | deploy/archive catch-up; first skill differential (sprint-2026-11-09) |
| skill | prompts/skill-agent.md | Tue 12:00 UTC | 270 | skills/ gold production | skills-with-receipts (O2), now `provisional`-only pending a measured delta |
| frontend | prompts/frontend-agent.md | Wed 12:00 UTC | 600 | site UI, visual quality | visual audit; mission on site |
| market | prompts/market-agent.md | Fri 11:00 UTC | 160 | docs/market/ | positioning under free+$20 |
| pm | prompts/pm-agent.md | daily 11:05 UTC (Mon: ceremony, Tue-Sun: standup) | 300 | sprints, backlog, board, org chart, dispatch queue, PR merges (§21) | overdue-ceremony catch-up (this run); O1 launch runway, missed |
| research | prompts/research-agent.md | Mon 16:30 UTC | 180 | input curation: digest review, curation brief, meta-review | what deserves attention; source discovery |
| exo | prompts/exo-agent.md | Mon 01:00 UTC (moved off Sunday 2026-10-25, provider-budget timing) | 200 | charters, workflows, org | org learning; GitHub upkeep |
| security | prompts/security-agent.md | 1st + 15th, 13:00 UTC | 250 | debug + defensive audits | pre-launch hardening |
| okr | prompts/okr-agent.md | 1st monthly, 10:00 UTC | 160 | docs/okrs/ | Q4 OKRs; benchmark trendline, O1 missed at launch, O2/O3 at-risk |
| writer | prompts/writer-agent.md | daily 16:00 UTC | 225 | newsletter voice: prompts/digest.md, docs/voice/, editorial structure | digest worth reading (O1) |

**Gap closed 2026-09-24 (ceremony-lite sync).** The writer seat
(ADR-28, editor-in-chief, owner's decision 2026-09-19) has run
`.github/workflows/agent-writer.yml` daily since 2026-09-19 and merged
seven PRs (#36, #47, #48, and the #55→#81 chain) but was never added
to this table — a seat with no line here is exactly the gap charter
§1b asks this run to flag. Fixed in place rather than left for Monday
since it costs one row.

## Dormant seats (ADR-24, owner activates)

ADR-24 defines dormant precisely: `workflow_dispatch` only, no cron,
"activation is a one-line schedule addition." Both seats below have
been hand-dispatched repeatedly this week (finance: PR #32, #84;
sales: PR #14, #17, #22) but neither has a cron in its workflow file,
so this table is accurate as written, not stale — a prior pending.md
note flagged sales as possibly stale here; checked against ADR-24's
own text this run, and it isn't. Finance's dormant-vs-activated status
is a live question for the owner regardless (see pending.md).

| Seat | Charter | Planned cadence | Lane | Waits on |
|---|---|---|---|---|
| finance | prompts/finance-agent.md | monthly | docs/finance/ OPEX, later revenue | owner activation (cron) |
| sales | prompts/sales-agent.md | on dispatch | docs/sales/ campaigns, drafts only | launch proximity, owner activation (cron) |

## Company initiatives

1. **Launch (dated Oct 13, missed on all three O1 KRs)** — pm leads;
   engineer, frontend, skill execute; sales activates near launch. Per the
   OKR agent's 2026-11-01 check-in, KR1 (purchasable end-to-end), KR2
   (profitable), and KR3 (citation coverage) are all graded `missed`. The
   remaining code-complete, owner-gated blocker is the Polar secrets (see
   pending.md); nothing else named here is unbuilt.
2. **Skills as the product** — skill leads; engineer (receipts rendering), market (positioning) support.
3. **Digest worth reading** — writer leads (voice, structure, ADR-28);
   research (curation, meta-review, ADR-25 renamed the old "weekly"
   seat); engineer (prompt plumbing); market (prose benchmark) support.
   Corrected 2026-09-24: this line still named the pre-ADR-25/28
   "weekly" seat as sole lead.
4. **The org improves itself** — exo leads; okr guards purpose; security guards the boundaries.
5. **Books and growth (dormant)** — finance and sales, when activated.

## Dispatch authority (company standard pm.md §11, ADR-033 v3, ACTIVE)

The PM seat may fire `gh workflow run` against engineer, research,
market, writer, frontend, skill, security, and okr, inside the ceilings
in prompts/pm-agent.md §5 and pm.md §11.4, when the repository variable
`PM_DISPATCH_ENABLED` is `true`. It may never dispatch exo (its own
auditor), itself, or a dormant seat. Every fired dispatch is logged in
docs/sprints/dispatch-queue.md under "Dispatched by the PM".

**The old `HTTP 403` saga (INC-2026-09-24-dispatch-403) is superseded, not
current.** That defect was `GITHUB_TOKEN` lacking `workflow_dispatch`
rights, fixed when the dispatch-probe workflow proved a `workflow_dispatch`
made with the runner's own token does work (2026-09-24,
`permissions: actions: write`), and §5 reflects that fix. **The live gate
today is `PM_DISPATCH_ENABLED` itself**, read from the environment or the
dispatching workflow's own prompt text, never from `gh variable list`
(403, wrong scope, per the ExO's 2026-10-11 correction). This run's own
environment read it empty, so no dispatch fires from this ceremony;
see this run's own PR for the proposed queue the owner can copy instead.

## The board (company standard pm.md §14, since 2026-09-27)

The company board at board.libraryofalexandria.dev (the `asc-board`
service) is now the state of the work, not GitHub Projects. Every seat
reads it at the start of a run and writes to it as it works, via
`BOARD_API_URL`/`BOARD_RUNTIME_TOKEN` on GitHub runners. The sprint file
in docs/sprints/ is a rendered export of the board's current sprint from
now on, not the other way around.

## Operating modes (owner's rule, 2026-09-18)

Two modes, one org. **Synchronous**: when the owner is present in a
working session, the relevant seats work WITH her, convened live by
the chair or dispatched immediately with her instructions carried in.
**Asynchronous**: when she is away, the schedules are the heartbeat
and every seat works its cadence unattended. Scheduled runs never wait
for her presence; live sessions never duplicate what a scheduled run
is already doing.
