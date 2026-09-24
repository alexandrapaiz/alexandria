# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run. Holds at most three proposed dispatches, ordered, and is
allowed to hold none.

## 2026-09-24, ~15:50 UTC (message-triggered standup, chair holding presence)

The owner closed her laptop around 05:30 UTC. This run was triggered by
the chair's handoff message, not by a workflow_dispatch, and no
`workflow_dispatch` has fired anywhere in the last two hours (the last
one was the writer run at 05:09Z). The org is not in synchronous mode,
so dispatch is procedurally open, but this run could not confirm the
first condition: `gh variable get PM_DISPATCH_ENABLED` returned
**HTTP 403** under this session's token ("Resource not accessible by
personal access token"), so the switch's state is unverifiable from
here. Section 5 requires both conditions confirmed before firing, so
nothing below was fired. This is a proposal-only queue.

### 1. market — the overnight ranking brief the owner is waiting on was never written

**Trigger.** The owner's evening dispatch asked the market seat to rank
W39 against newsletters builders actually enjoy and rank the product
against the $20/month competitive set, deliver both in one PR with a
one-page decision brief, then hand the PR to the PM itself. Run
`35958636133` (market-agent, `workflow_dispatch`, 05:08–05:12Z) shows
`conclusion: success`, `num_turns: 34`, `total_cost_usd: 1.73` in its own
transcript. Against that, PR #93 (`market/2026-09-24-b`, still draft)
holds exactly one commit: the ship-first stub. `docs/market/briefs/
2026-09-24-b.md` still reads "Status: draft, in progress... This stub is
the ship-first commit. The full brief... land[s] in this same file
before the PR comes out of draft." No second commit ever landed, and
step 3 of the owner's own instructions (dispatch the PM with the PR
number) never fired — no `agent-pm.yml` workflow_dispatch appears
anywhere in `gh run list` after 05:08Z. This is the pattern incident 8
named on 2026-09-17/18: a run reports success and ships something far
short of the deliverable. Logged below as
`INC-2026-09-24-market-ranking-stub-only`.

**Cost of skipping it today.** The owner wakes up to a draft PR titled
as her overnight priority with no ranking and no brief inside it, and
the "PM decides from market's rank" flow her own instructions describe
stays blocked for a second day. Nothing in this standup can substitute
for it: inventing a rank or a decision list without the market seat's
research would violate the relay rule below.

**Dispatch.**

```bash
gh workflow run agent-market.yml \
  -f owner_instructions='Build on the open branch market/2026-09-24-b
(PR #93) rather than branching from main; do not open a second PR for
this dispatch. That branch holds only the ship-first stub from run
35958636133, which reported success but never wrote the ranking. Finish
what the owner asked for last night: rank issue 2026-W39 against
newsletters builders actually enjoy (Interconnects, Ahead of AI, Latent
Space, The Batch, Import AI, TLDR AI, Bens Bites, and comparable),
scored on enjoyability, density, and whether a reader opens the next
one, naming the specific paragraphs that lose a reader; rank alexandria
against the competitive set on what a builder and their agents get for
$20/month; and write both ranks plus a one-page, priority-ordered
decision brief for the PM into docs/market/briefs/2026-09-24-b.md before
marking the PR ready. Confirm in the PR body that the file now holds the
full brief, not the stub, before ending the run.'
```

## Run health

**Fleet health.** `gh run list --limit 30` shows one new failure class
since the last PM run: the market stub above, `success` in Actions but
short of its deliverable (incident-8 pattern, logged this run). Every
other run in the window is `success`, including a `cancelled` writer run
(`35958638663`) that PR #92's own body already accounts for as
`INC-2026-09-24-writer-dispatch-started-twice`, a repeat of incident 14 —
recorded by the writer seat, not owed here. Two runs are `in_progress`
as this standup writes (`pm-agent` `36022688185` and `engineer-agent`
`36022750452`, both scheduled, started 15:46–15:47Z): this session and
that scheduled `pm-agent` run may be concurrent. Checked for a collision
before writing: no PM pull request was open when this run started.

**Delivery health.**

- **The press.** Checked at the artifact, not the scheduler, per
  `docs/agents/delivery-health.md`. This sandbox has no `DATABASE_URL`,
  so the `digests` table itself could not be queried directly. Indirect
  but direct-enough evidence: `https://libraryofalexandria.dev/library`
  returns 200 and lists `2026-W39` (the current week), and
  `https://libraryofalexandria.dev/library/2026-W39` returns 200 with a
  real, non-generic title ("Harness distillation without the harness at
  runtime"), consistent with the chair's report that W39 sent at 05:05Z.
  Not a full substitute for reading the table; said so rather than
  reporting "all green" on evidence not actually gathered.
- **The site.** Live and serving current content (checked above).
- **The MCP server.** `https://ap4509--alexandria-mcp-serve.modal.run/`
  returns HTTP 404 on a bare GET, which is not a defined route on a
  mounted MCP app (POST `/mcp` is the real endpoint) — the server
  answered rather than timing out or refusing the connection, so it is
  reachable. Not a full protocol-level health check.

## Pending items past their date

`docs/sprints/pending.md` was last updated around 04:49Z tonight (the
"Thursday night standup, owner present" entry at its top) and has not
been touched since; nothing in it is yet a day past its own date, so
there is nothing new to flag here beyond what it already carries. Two
items already recorded there remain open and worth restating in this
PR's description for visibility: PR #60 (engineer) is `CONFLICTING`
against main, per the chair's handoff, and the engineer's current open
PR (#94) branches from main rather than from #60, so #60's rebase is
still unstarted. PR #92 (writer, the canon-14 promotion and W39
rewrite) and PR #94 (engineer, the rehearsal print) are both open and
awaiting the owner's read and merge; full reconciliation of `pending.md`
is a ceremony-run duty and stays there.

## Linear trial

Not checked this run; no new signal on adoption or abandonment since
the last note in `pending.md`. Still a trial per the 2026-09-19 ruling.

## Dispatched by the PM

None this run. `PM_DISPATCH_ENABLED`'s state could not be confirmed
(see above), so the entry above is a proposal only, for the chair or
owner to fire by copying the command.
