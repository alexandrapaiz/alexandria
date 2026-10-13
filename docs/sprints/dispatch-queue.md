# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-13, standup (~18:30 UTC)

**The headline is not the queue gauge, it is launch day itself, read live
from the database just now.** Launch was dated 2026-10-13 (vision.md §0)
— today — and `python3 tools/delivery_health.py`, run this standup against
a working `DATABASE_URL`, says:

```
FAILING  press     the newest issue is 2026-W40 and 2026-W41 has ended; 1 issue(s) missing
FAILING  pipeline  claims has not moved in 6 days, with 2223 papers waiting in distill_queue
unknown  deploy    distill (never recorded); ingest (never recorded)
FAILING  site      the newest issue a reader can read is 2026-W40
ok       archive   the record and the archive both end at 2026-W40
ok       mcp       up, and refusing unauthenticated calls
```

Both red lines are worse than yesterday's ceremony found them (press was
missing then too; pipeline was a 5-day stall with 2173 papers, now 6 days
and 2223). Yesterday's ceremony read item 1 of its own new sprint
("diagnose and close today's press-send gap") as merged via #282 — true,
but #282 shipped the degraded-path *mechanism* (`--allow-fallback`), not a
resend, and the mechanism cannot run anyway: `INC-2026-10-12-the-deploy-
ladder-refuses-the-fix-for-the-outage-it-is-in` already names the reason
— every deploy chain needs `modal deploy`, no agent token holds it, and
the gate that protects a healthy deploy day refuses to open on the one day
its own subject is the outage. `INC-2026-10-11-the-free-tiers-minute-was-
sized-for-one-request-and-never-for-a-drain` and
`INC-2026-10-12-the-free-tiers-day-was-sized-for-one-job-and-never-for-the-
schedule` are the same undeployed-fix shape underneath the pipeline number.

**This is not a new incident** — both are already filed by name above —
**and it is not this standup's to dispatch**, because the engineer seat has
an open pull request from a run in progress right now (#288, started
18:12 UTC today, sprint item 3) and the hard stop forbids dispatching a
seat with an open PR unless told to build on it, which would race a live
run. The fix the org actually needs is a `modal deploy` run, which is a
credential only the owner or chair holds. **Named here, at the top, so it
reaches her without being filed as a complaint**: the press has not sent
on the day this company called launch, and the reachable half of the fix
is already in `main`.

### Today's own open pull request

Found at the start of this run: **#281** (`pm/sprint-2026-10-12`, this
seat's own last scheduled run, the Monday ceremony), still open against
`main`, `MERGEABLE`/`CLEAN`. Built on it — merged into this branch first,
before any new work, per the charter's collision rule, because today's
standup writes the same two files (`dispatch-queue.md`, `pending.md`)
that PR already wrote. This PR (#289) supersedes it; proof
(`git log --oneline origin/pm/sprint-2026-10-12 ^HEAD` printed nothing)
and the close itself both happened before this file was written. Chain
depth 2 (nothing superseded #281 itself).

**Not touched: #287** (`alexandria-pm/2026-10-13-message-second-pass`),
a different PM-surface pull request from a different invocation path (the
host "six-hour pass" system, committer `alexandria-pm@agents.epito.me`,
no corresponding run in `gh run list --workflow=agent-pm.yml`). Six hours
stale at the time of this standup (last commit 12:22 UTC, now past 18:20),
itself superseding a prior stalled pass (#286). Named rather than acted
on, same as every prior pass has treated this seat's other surface: not
enough visibility into that system from here to judge whether it is dead
or still running, and its only file (`docs/agents/incidents.md`) is one
this standup also touches, so a human reading both should pick the order.

## Run health

**Fleet.** `gh run list --status failure` since this run started finds
**zero failed runs in the last 24 hours.** Nothing to triage under §11.7.

**Cap ratio** (turn-caps.md rule 5, 70% of `--max-turns`), over every run
since the last standup:

| Seat | Run | `num_turns` | Cap | Ratio |
|---|---|---|---|---|
| **engineer** | 38341930355 (2026-10-13 03:29) | **147** | 200 | **73.5%** |
| research | 38320445722 (2026-10-12 23:07) | 122 | 180 | 67.8% |
| writer | 38317778377 (2026-10-12 22:38) | 149 | 225 | 66.2% |

Only engineer clears the 70% line. Not a cap proposal, per the standing
rule that this duty reports the ratio and names the seat rather than a
number; the ExO's monthly re-derivation is where a number would come from.

**Delivery health.** Covered above as the headline; repeated here only to
say the standing question was answered rather than skipped: green on what
evidence (a live `DATABASE_URL` read, this run, not a proxy), and did
anything reach a reader (no, not since 2026-W40).

## The queue gauge, four numbers

1. **`main`'s age and checks.** Newest commit `68c49a7`, 2026-10-13T18:16
   UTC (this run's own second Tier B merge), **under 10 minutes old at
   last check.** Newest `checks.yml` run on `main`: **success.**
2. **Open pull requests: 7 total, 1 opened since the last merge to `main`**
   (this standup's own PR, #289).
3. **Conversion, trailing 7 days: 18 merged / 52 opened ≈ 0.35.**
4. **Deepest open supersession chain: 2** (#289 over #281; #287 over #286;
   #203 over #171; #60 over #35). No chain past depth 2 right now.

`main` is fresh and green, so this is not the deadlocked state
`INC-2026-10-04-four-days-of-output-and-no-delivery` describes, and the
dispatch queue below is informative rather than structurally empty.

## Merged this run (Tier B, `docs/standards/pm.md` §10)

- **#283** (writer, "Quality tier held pre-send") — clean, checks green,
  no Tier C path (`prompts/digest.md` is a content prompt, not a seat
  charter; `prompts/<role>-agent.md` is the Tier C boundary per standard
  §16's own vocabulary). Board item `59fcc1f4` moved to Done with the PR
  link.
- **#284** (research, the claim-graph precision brief) — opened
  `CONFLICTING` against `docs/agents/incidents.md` (both #283 and #284
  appended at the same anchor). Docs-only conflict, which §10 rule 5
  allows this seat to resolve: merged `main` into the research branch,
  kept both incident entries in sequence, pushed, then merged clean.

**Not merged, each named rather than acted on:** #272 (exo, touches
`prompts/exo-agent.md`, `prompts/market-agent.md` and this seat's own
`prompts/pm-agent.md` — Tier C by content, and `CONFLICTING` besides;
needs the owner regardless of the conflict). #205 (finance, draft,
dormant seat). #203 (okr, draft). #60 (engineer, Tier C `prompts/daily.md`,
conflicting, 23 days open, unchanged). #288 (engineer, in progress right
now, item 3 of the sprint). #289 (this seat's own PR, waits for the owner
or HQ's PM per Tier B rule 1).

## Proposed dispatches

### 1. frontend — the Left-Behind Index has carried two sprints with no run against it

**Trigger.** `sprint-2026-10-12.md` item 4 (carried from `sprint-2026-10-05`
before it), board item `03029cad`. The frontend seat's last run was six
days ago (2026-10-07, a visual-review pass) — before this sprint existed
— and the PR survey (`gh pr list --state all`, every `fe/*` and
`alexandria-frontend/*` branch, 14 pull requests back to 2026-09-18) shows
every one of them is a visual-review or polish pass. **None has ever
attempted to build this page.** No open frontend PR exists, so the hard
stop against dispatching a seat with open work does not apply.

**Cost of skipping it today.** Two drafted sales outreach notes stay
blocked on a page that has now missed its second full sprint, and the
item ages into a third ceremony finding the same zero progress.

**Dispatch.** Attempted this run, under `PM_DISPATCH_ENABLED=true`:

```bash
gh workflow run agent-frontend.yml \
  -f owner_instructions='Sprint item 4 (sprint-2026-10-12.md, carried across
two sprints): ship the Left-Behind Index as a public page over the
deprecated_claims view. Two drafted sales outreach notes are waiting on it
(board item 03029cad). No frontend PR, open or closed, has ever attempted
this (survey: every fe/* and alexandria-frontend/* PR to date is a visual
review pass). Build the page; this is new work, not a review.'
```

**Result: `HTTP 403: Resource not accessible by integration`**, the same
repeat `INC-2026-09-24-dispatch-403` has named 18+ days running — the
Claude Code action's installation token does not carry `actions: write`
no matter what the workflow's `permissions:` block grants. No run started.
The command above is exact; the owner or chair can run it by hand.

No second or third entry this run: the other idle seats (security, 12
days; skill, 7 days; market, 4 days) have no named trigger — no sprint
item, ADR, or failed run points at any of them — and inventing one would
be the judgment this charter reserves for the owner.

## Dispatched by the PM

**None delivered.** One attempted (frontend, above), refused with `403`
before a run was created. Nothing to log as fired.

## The Linear trial

Not checked this run; no new signal since the last pass noted it was
still on.
