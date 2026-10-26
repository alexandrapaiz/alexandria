# Org chart

**Enforced at:** prompts/pm-agent.md §1b, which updates this page whenever seats or initiatives change and flags any initiative with no seat.

Maintained by the PM agent (charter §1b). Owner is Product Owner and
merges everything; the ExO reviews the workers; every seat is one PR
per run. Seeded 2026-09-18 by the chair; the PM keeps it current.

## Active seats

| Seat | Charter | Cadence | Lane | Current initiative |
|---|---|---|---|---|
| engineer | prompts/engineer-agent.md | daily 7:06 ET | product code, pipeline | launch runway; architecture evolution |
| skill | prompts/skill-agent.md | Tue 8:00 ET | skills/ gold production | skills-with-receipts (O2) |
| frontend | prompts/frontend-agent.md | Wed 8:00 ET | site UI, visual quality | visual audit; mission on site |
| market | prompts/market-agent.md | Fri 7:00 ET | docs/market/ | positioning under free+$20 |
| pm | prompts/pm-agent.md | daily (Mon: ceremony, Tue-Sun: standup) | sprints, backlog, board, org chart, dispatch queue | merge-queue health; skills-product leverage (O2/O3) |
| research | prompts/research-agent.md | Mon 16:30 UTC | input curation: digest review, curation brief, meta-review | what deserves attention; source discovery |
| exo | prompts/exo-agent.md | Sun 10:00 ET | charters, workflows, org | org learning; GitHub upkeep |
| security | prompts/security-agent.md | 1st + 15th | debug + defensive audits | pre-launch hardening |
| okr | prompts/okr-agent.md | 1st monthly | docs/okrs/ | Q4 OKRs; benchmark trendline |
| writer | prompts/writer-agent.md | daily 16:00 UTC | newsletter voice: prompts/digest.md, docs/voice/, editorial structure | digest worth reading (O1) |

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

1. **Launch (dated 2026-10-13, now 13 days past)** — code-complete and
   blocked on two owner-only accounts rather than on any seat: the Polar
   merchant account (overdue since 2026-09-26) and, since 2026-10-23, the
   Modal workspace that runs the press and the MCP server. No seat is
   currently executing against this initiative; it is correctly absent
   from sprint-2026-10-26.md for exactly that reason (prompts/pm-agent.md
   §3 plans around work a seat can finish). Flagging per charter §1b: an
   initiative with no seat currently carrying it, because the seats that
   would carry it (engineer, frontend) are both idle on it waiting for her.
2. **Skills as the product** — skill leads; engineer (receipts rendering), market (positioning) support.
3. **Digest worth reading** — writer leads (voice, structure, ADR-28);
   research (curation, meta-review, ADR-25 renamed the old "weekly"
   seat); engineer (prompt plumbing); market (prose benchmark) support.
   Corrected 2026-09-24: this line still named the pre-ADR-25/28
   "weekly" seat as sole lead.
4. **The org improves itself** — exo leads; okr guards purpose; security guards the boundaries.
5. **Books and growth (dormant)** — finance and sales, when activated.

## Dispatch authority (company standard pm.md §11, ADR-033 v3, active since 2026-09-24)

**Corrected 2026-10-26, Monday ceremony — this section was stale since
before the 403 bug it describes was fixed.** The PM seat may dispatch
engineer, research, market, writer, frontend, skill, security, and okr,
inside the ceilings in `prompts/pm-agent.md` §5 and `pm.md` §11.4, when
the repository variable `PM_DISPATCH_ENABLED` is `true` (it is read from
the environment, never from `gh variable list`, which 403s for the
runner's token regardless of the actual value). It may never dispatch
exo (its own auditor), itself, or a dormant seat. The `HTTP 403` this
section used to describe as unresolved was a misreading of GitHub's
general rule: `workflow_dispatch` is one of GitHub's own exceptions, and
HQ's `dispatch-probe` workflow proved a parent run can start a child run
on 2026-09-24. **Separately, and more recent than that fix:** decision
056 (2026-10-17) closed the GitHub workflow door entirely — every seat's
clock is now its manifest on the host runtime, not a GitHub cron, and a
handoff reaches a seat through its host window or the bus rather than
through `gh workflow run`. The cadence table this page used to carry
(`daily 7:06 ET`, `Tue 8:00 ET`, and so on) described the retired GitHub
cron system and is removed rather than corrected in place; the live
cadence per seat lives in the host manifest
(`runtime/agents/alexandria/<seat>/agent.toml`) and is not mirrored here,
because mirroring a value this page cannot read live would just stale
again. Every fired dispatch is still logged in
`docs/sprints/dispatch-queue.md` under "Dispatched by the PM".

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
