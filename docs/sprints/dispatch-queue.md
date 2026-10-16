# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-16, standup (~15:25 UTC)

**The owner is back after eleven days away** (board note, chair:hq-console,
14:16 UTC today) and the org is in synchronous mode: a human or chair
dispatch landed inside the last two hours on every check this run made
(engineer, writer and market all opened pull requests between 14:19 and
15:25 UTC today, plus two PM "message" passes and an HQ engineer run, all
today). Per `docs/standards/pm.md` §11.4, that means queue, not fire,
regardless of the three daily dispatches of ceiling room available
(0 used today). Nothing below was executed; everything is a proposal.

**No dispatch proposed for any seat.** Every seat that could take one is
already accounted for: engineer and writer each already carry an open
pull request (the hard stop against dispatching a seat with its last
pull request still open), frontend's open pull request is mid-decision
(see below) rather than abandoned, market is running right now, and
research, skill and okr have no observed trigger — no sprint item of
theirs sits unattempted, no ADR or all-hands entry names them since the
last reconciliation (`docs/decisions.md` still stops at ADR-40,
`docs/allhands/` still nothing newer than 2026-09-18-close), and no
dormant-seat signal applies. Zero entries by the four rules, not by
default.

## Own-run check (your-own-last-run rule)

Three of this seat's own pull requests were open at the start of this
run, all from host "six-hour pass" windows rather than from this
Actions standup. Closed all three rather than building on any of them,
because none of them was mine to carry forward honestly:

- **#309** and **#302**, both ship-first placeholders with no follow-up
  commit (one line added, nothing else), 15 hours and more than a day
  stale respectively. Closed; this run supersedes neither in content,
  only in sequence.
- **#305**, a completed pass whose one finding (the dispatch actor-gate
  fix was live but unverified by a real dispatch) is now moot: the
  2026-10-15 15:55 UTC standup already on `main` fired that exact
  verification dispatch and recorded it working. Closed rather than
  resolving its conflict, because landing a day-stale "still unverified"
  line on top of a record that already answers it would misinform the
  next reader.

Branched this run from `main` directly rather than building on any of
the three, since none of them had content worth carrying.

## Tier B merges this run (`docs/standards/pm.md` §10)

**None merged — nothing open was eligible.** Every non-draft open pull
request conflicts against `main` and every draft is still in progress.
Two closed instead, under rule 6 (older than seven days, idle, no
movement since creation, and now conflicting):

- **#205** (finance, the September close), opened 2026-10-05, zero
  activity since, 11 days idle.
- **#203** (OKR, the fifth cadence check-in), opened 2026-10-05, zero
  activity since, 11 days idle, itself already a supersession of #171.

**#306** (frontend, the Left-Behind Index) also conflicts against
`main`, but it is not idle — the frontend seat's own comment on it
(2026-10-15 16:35 UTC) is a live, reasoned decision to ship the route
unlinked pending a data-quality fix, not an abandoned branch. Handed
back to frontend on the board to rebase rather than closing it or
text-resolving a conflict in `site/` and `docs/design/`, which is
product code, not a knowledge surface.

**#272** (exo-centralizer, the weekly orchestration cycle) stays open,
untouched. It is Tier C — the diff touches `prompts/pm-agent.md`,
`prompts/exo-agent.md` and `prompts/market-agent.md` — and it has
conflicted against `main` for 5 days, unmoved since creation, across a
week in which this repo became a subcompany of Alexandra Systems
Company and vendored a much larger PM standard. Worth the exo seat's
own judgment on whether re-deriving it from scratch is cheaper than
rebasing it, not this seat's call either way. Named here as waiting on
the owner (Tier C) and on the exo seat (the rebase), per §18 line 4.

## Failures (`docs/standards/pm.md` §11.7)

**None.** `gh run list --status failure` over the last 24 hours returns
nothing. All three in-flight scheduled runs at the time of this check
(engineer, market, this seat) later completed or are still running
cleanly.

## Run health

Fleet: zero failures to triage, as above.

**Cap ratio** (`docs/agents/turn-caps.md` rule 5): one flag. The
engineer's 2026-10-16 01:10 UTC scheduled run used **148 of 200 turns
(74%)**, above the 70% line. Writer (101/225, 45%) and security
(128/250, 51%) both comfortable. Not proposing a new number; reporting
the ratio and naming the seat, per the rule.

**Queue gauge, four numbers.**

1. `main`'s newest commit: `d30e1b9`, 2026-10-16T14:31:14Z — about an
   hour old. Newest *applicable* `checks.yml` run: success (the newest
   merge was docs-only and path-filtered out of that workflow, which is
   expected, not a gap).
2. Open pull requests: **8** total, **4** opened since the last merge to
   `main` (#315, #316, #317, and this standup's own #318).
3. Conversion, trailing 7 days: **33 merged / 64 opened (0.52)**.
4. Deepest open supersession chain: **2** — writer's #311 over #308, and
   separately engineer's #312 over #310. Neither is a problem at this
   depth.

No deadlock: main is fresh (about an hour since the last merge) and
conversion is healthy, so the queue-gauge threshold (nothing merged for
48+ hours) does not apply today. The empty dispatch queue above is a
product of synchronous mode and existing open work, not of a stalled
merge gate.

## Delivery health (`docs/agents/delivery-health.md`, live via
`tools/delivery_health.py`)

**The headline, and it is dated.** The press owes 2026-W41 and has not
sent it. The newest row in `digests` is still 2026-W40 (2026-10-05).
The engineer's own board comments today (14:31–14:32 UTC, on the
"Press: no issue for 2026-W41" card) found the exact cause — the
production image for `pipeline/weekly.py` is 9.9 days behind `main` and
was built before today's fallback-budget fix, and the Moonshot account
behind it was out of balance on the day it mattered — and named the two
commands that close it, both needing a Modal token no agent seat holds:

```
modal run pipeline/weekly.py::resend --week 2026-W41   # ~$0.18, verified against today's budget guard
modal deploy pipeline/weekly.py                          # so next Monday runs this week's code, not the 4th's
```

**The window to recover 2026-W41 specifically closes 2026-10-18 23:59
UTC** (Sunday night) — after that the same command writes 2026-W42
instead, the way 2026-W38 was already lost the same way. This is an
`ask` on the board to the owner, not flagged urgent (she is already
active on the board today), because WhatsApp urgency is for what stops
the whole company and this is one weekly product, bounded and costed.

Other three surfaces, read from the artifact rather than the scheduler:

- **pipeline**: ok — papers and claims both moved within the last
  half hour.
- **deploy** (the other three scheduled jobs): `interpret` and `triage`
  both ok, roughly 22 hours of ordinary drift; `ingest` has never
  recorded a runtime at all and is the same undeployed commit as the
  press, 6.9 days old.
- **site / archive**: tracking the same W41 gap, nothing beyond it.
- **mcp**: ok, reachable, correctly refusing an unauthenticated call.
- **payments**: unknown, no credential in this environment to check it.

## Board

Read the inbox first. Nothing addressed to `pm`/`alexandria` specifically
needed an answer; the traffic was HQ-internal (the engineer's clock
migration) and other companies' PMs posting their own six-hour notes.

Touched four items directly rather than leaving them for later:

- Commented on the Left-Behind Index card about the handoff above.
- Commented on the "Press: no issue for 2026-W41" card, naming that
  this standup is carrying it to the owner.
- **Resolved the "Declining the staffing-authority note" card**, open
  in Backlog since 2026-10-05 awaiting the owner's word. The company
  standard vendored today (§22, the 48-hour silence rule) now covers
  exactly this kind of reservation, and 11 days of silence is well past
  48 hours, so the decline this seat already recorded stands as the
  resolved outcome. Moved to Done. Nothing changed hands: no seat was
  created or switched on.
- **Moved the 2026-10-05 "Monday ceremony" card from Review to Done.**
  Its own comments already confirm it closed out that week; it had sat
  in Review for 11 days with nothing left to review.

**The board's sprint object still reads `sprint-2026-10-05`** ("The
press runs itself"), six ceremonies behind the real sprint file on
`main` (`sprint-2026-10-12`). Still not a standup fix: creating or
renaming a sprint is outside every seat's board permission per §14, this
seat included. Named again rather than silently re-attempted.

## Dispatched by the PM

None this run. Synchronous mode (above) means queue, not fire.
