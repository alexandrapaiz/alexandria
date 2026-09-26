# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-09-26 (synchronous session, owner present)

The owner opened a work window tonight and is directing live through the
chair, per docs/standards/pm.md §11.4 (amended today) and
docs/standards/lessons.md L-P7: in sync mode the PM directs, the owner
steers through it, and the two-hour "queue instead" rule stands down for
the duration of the window. This section records that session, not a
normal unattended standup.

**State read at window open.**

- `gh run list --limit 30`: writer-agent, engineer-agent, and
  frontend-agent runs were still `in_progress` (started 00:47-01:00 UTC),
  research-agent and skill-agent had just completed `success`. One
  `cancelled` writer-agent run at 00:52:19Z is already registered as
  `INC-2026-09-24-writer-dispatch-started-twice`'s pattern repeating; not
  re-filed here since it is the same class, not a new one, and no PM
  dispatch caused it.
- `gh pr list --state open`: 7 PRs open, all from tonight's own-cadence
  or earlier dispatches, none from the PM: #112 (writer), #111 (skill),
  #110 (engineer), #109 (research), #108 (frontend), #107 (writer), #60
  (engineer, open since 2026-09-20). This means **engineer, research,
  frontend, writer, and skill are all disqualified from a fresh PM
  dispatch right now** under the hard rule ("never dispatch a seat whose
  last PR is still open, unless the instruction says build on that
  branch in those words") - and three of the five have a run still
  executing, where redispatching would race the same seat's own
  in-flight run on a fresh branch, the exact class incidents 6 and 14
  warn about, regardless of the branch-build carve-out.
- `docs/sprints/pending.md` and the OKR check-in (2026-09-24) flagged a
  28-PR merge bottleneck with no product PR merged since 2026-09-19.
  That is resolved as of tonight: 7 PRs open now, not 28. Noted as good
  news rather than re-flagged.
- `docs/decisions.md` newest entries (ADR-32 through ADR-35) do not yet
  carry tonight's HQ priorities; those arrive live in this session, not
  from a prior file, which is exactly the mechanism L-P7 describes.
- Linear trial (charter §1e2): no new verdict recorded in this run's
  reading. The owner's priority order tonight names "the task
  manager/board that replaces Linear" as item 1, which reads as
  direction to build the replacement, not yet a recorded verdict to
  abandon the trial. Flagged for the owner to confirm explicitly; not
  recorded as abandoned on an inference.

**Owner's priorities tonight, verbatim where it matters (HQ ADR-037 +
amendments, relayed live):**

1. The task manager/board that replaces Linear: own store, seats cannot
   create views, run reports live on the board.
2. Temporal as the runtime engine (HQ ADR-036; server already live on
   the host).
3. The LangGraph implementation with tracing (Phoenix installed).
4. The router.

Own-model hosting (vLLM) is dropped as a priority. Also tonight: HQ
ADR-038 gives agents long-term memory (notebook per seat plus scoped
recall on the company RAG); an HQ engineer is building it in HQ's PR #36,
no local action. HQ ADR-035 sets engineers running twice daily
everywhere; **naming note** - this is a different decision from this
repo's own ADR-35 ("skill creation requires reading," docs/decisions.md,
2026-09-25), a numbering collision across repos worth the ExO's
attention before someone cites the wrong one.

**The plan for the rest of this window.**

1. **okr, fired now.** No open PR, no in-flight run, and a real trigger:
   the 2026-10-01 quarter-turn is five days out and should carry
   tonight's reorder into it rather than re-derive it late.
2. **engineer, queued.** Priority 1's first slice (the board's own-store
   schema, no UI) is the natural next engineer dispatch, but its last
   run (PR #110) is still executing. Firing now would race that run on
   a fresh branch. This seat will be dispatched as soon as `gh run list`
   shows that run finished, inside this same held window.
3. **frontend, queued.** Same block: PR #108's run is still executing.
   Once clear, the natural dispatch is the board's read-only UI on top
   of whatever store shape engineer lands, once that exists - not
   before, so it is not fired in parallel with item 2.

No third dispatch fires in this initial burst. Firing into two
still-running seats to hit a count of three would manufacture the exact
race this charter's hard stops exist to prevent. The queue holds two
proposed entries instead of inventing a third.

### Proposed (not yet fired)

#### engineer - the board's own-store schema (HQ ADR-037 item 1)

**Trigger.** Owner's live ruling tonight, HQ ADR-037: an own-store task
manager/board replaces Linear, seats cannot create views, and run
reports live on the board. PR #110's run has to finish first (see
above).

**Cost of skipping it today.** The highest-priority item the owner named
tonight gets no engineering hours in the one window she is present to
direct it.

**Dispatch, once #110's run shows `completed` in `gh run list`.**

```bash
gh workflow run agent-engineer.yml -f owner_instructions='Owner priority
1 tonight (HQ ADR-037, sync session 2026-09-26): an own-store task
manager and board that replaces Linear. Seats never create views; only
the PM and the owner do. Every seat run posts a structured report onto
the board (seat, run id, PR if any, one-line result) as part of its
normal workflow step. Build the first slice only: the store (a table or
file format under a path the PM and other seats can read and append to,
your call on Postgres/Neon vs. a repo-tracked format, name the
tradeoff), a minimal write function a workflow step can call to post a
run report, and one read path that lists the current board state. No UI
this run, frontend takes that next. Do not touch GitHub Projects or
Linear integration. PR #110 is your last PR; build on that branch if it
is still open when you start, otherwise branch from main.'
```

#### frontend - read-only board view (HQ ADR-037 item 1, follow-on)

**Trigger.** Same ADR-037 item 1. Sequenced after engineer's store
lands, not parallel to it, since there is nothing to render before then.

**Cost of skipping it today.** Same as above; this is the second half of
the one item the owner marked highest priority.

**Dispatch, once engineer's board-store PR exists and PR #108's run
shows `completed`.**

```bash
gh workflow run agent-frontend.yml -f owner_instructions='Owner priority
1 tonight (HQ ADR-037, sync session 2026-09-26): a read-only board view
of the task manager/board engineer is building this window (see its PR
for the store shape). Render current board state only: seats, their
latest run report, and any open PR. No view-creation UI for seats, the
owner ruled seats cannot create views. If engineer'"'"'s store PR has not
merged yet, build against its branch directly rather than waiting. PR
#108 is your last PR; build on that branch if it is still open when you
start, otherwise branch from main.'
```

## Run health

**Fleet health.** Since the last PM run (schedule, 2026-09-25T15:46:46Z,
success), `gh run list --limit 30` shows one `cancelled` writer-agent run
(00:52:19Z), already registered as
`INC-2026-09-24-writer-dispatch-started-twice`'s pattern, and three runs
`in_progress` at window-open time (writer, engineer, frontend) with no
result to grade yet. No new failure class.

**Delivery health.** Not independently re-checked this run beyond what
the 2026-09-25 standup already recorded (site 200, MCP endpoint alive,
no digests DB access from this sandbox); this session's focus was the
owner's live priorities, not a fresh delivery sweep. Flagged as
unchecked rather than reported as green on stale evidence.

## Pending items past their date

Not re-audited line by line this run; see `docs/sprints/pending.md`
directly. Nothing in this session's reading surfaced a new lapse.

## Linear trial

Still on trial. The owner's priority 1 tonight (own-store board
replacing Linear) reads as direction to build the replacement, not yet
a recorded verdict to abandon Linear. Asking the owner to confirm
explicitly rather than recording an inferred abandonment.

## Dispatched by the PM

### 2026-09-26 - okr

**Instruction.**

```
Owner's live sync-session ruling tonight (2026-09-26) reorders company
priorities per HQ ADR-037: 1) an own-store task/board that replaces
Linear (seats cannot create views, run reports live on the board), 2)
Temporal as the runtime engine (HQ ADR-036, server live on host), 3) the
LangGraph implementation with tracing (Phoenix installed), 4) the
router. Own-model hosting (vLLM) is dropped. Read
docs/okrs/okrs-2026-Q4.md and note, for the 2026-10-01 quarter-turn,
which O3 KRs (autonomy loop, reviewer panel) should be reframed around
Temporal and LangGraph as the runtime and agent architecture rather than
the current ad hoc design, and where a board KR belongs next quarter. Do
not add or change a KR outside the quarter-turn rule; record findings as
notes for the turn, not as edits to the committed KRs. Cite this session
(alexandria-pm/2026-09-26-window) as the source.
```

**Run URL.** https://github.com/alexandrapaiz/alexandria/actions/runs/36207911573

**Note.** `INC-2026-09-24-dispatch-403` recorded this exact call 403ing
on 2026-09-24 despite every documented condition met. It did not repeat
tonight: the call above returned a run URL on the first attempt. Worth
the ExO's eye on whether something changed (a token, an app
installation, an org setting) or whether the earlier failure was
transient - recording the data point here rather than closing the
incident myself, since I did not diagnose the cause.
