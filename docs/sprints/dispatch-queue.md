# Dispatch queue

Maintained by the PM agent's daily standup (charter §4). Replaced in full
each run, because it is a queue rather than a log.

## 2026-10-03 (Saturday standup)

**Run mode.** Today is Saturday, not Monday, so this is a standup run
(charter §4 alone): no retro, no grooming, no new sprint file.

**Branch note.** This seat's last four runs (#150, #167, #173, #179,
2026-09-30 through 2026-10-02) are still open and none has merged since
the 2026-09-29 standup landed on main. Branched from main rather than
building on #179, for the same reason #179 itself gave against #173:
`dispatch-queue.md` is replaced in full every run, so there is nothing in
any of the four to carry forward. This PR supersedes #179, which
transitively supersedes #173, #167, and #150. Close all four without
merging once this lands.

## Queue is empty

Checked every one of the eight dispatchable seats (engineer, research,
market, writer, frontend, skill, security, okr) against `gh pr list
--state open`, grouped by branch. Every single one already holds an open
pull request from its own last run, which is the hard stop under charter
§5 with no exception for firing:

- **engineer** — a brand-new pull request opened minutes into this run
  (its second window today), building on and superseding its first,
  itself still open.
- **writer** — newest pull request open since Friday evening, on top of
  two older ones in the same chain.
- **market, security, okr** — each has one pull request open from its
  most recent run, 1 to 2 days old.
- **research, frontend, skill** — each has at least one pull request
  still open from 2026-09-30, three days old and unmerged.

`PM_DISPATCH_ENABLED` is `true` and no `workflow_dispatch` ran in the
last two hours (the two runs active when this standup started were both
`schedule`-triggered, landing in the same minute by coincidence, not an
owner-driven synchronous session), so neither guardrail is why the queue
is empty today. The open-pull-request hard stop is the whole reason, same
as yesterday's standup.

## Run health

**Fleet health.** One repeat to account for since the last PM run
(2026-10-02, 16:44 UTC): the writer seat's newest pull request failed the
same two tests four more times late Friday evening (20:13 to 20:42 UTC),
the identical already-registered defect (a cost/backoff assertion in the
press-resilience test, and a `gh pr list` warning on stdout breaking a
JSON parse in the run-report test). Both are named in the incident
register's existing entries and tracked as a standing backlog item on the
company board, which this run updated with the new occurrences rather
than filing a fresh incident. No new failure class. The dash-echo defect
that cost six to eight runs earlier this week shows no further
occurrences; the scheduled engineer runs since have all completed
`success`, consistent with its fix having landed. Everything else since
the last PM run is green.

**Delivery health.**

- **The press and the daily pipeline.** `unknown`, read with
  `tools/delivery_health.py`: no `DATABASE_URL` in this sandbox, so
  guardrail 4's evidence (the newest row in `digests`) cannot be read
  here. Same gap as every standup since 2026-09-27; still unresolved.
- **The site.** `ok` — one issue published, newest `2026-W39`, matching
  the expected week.
- **The MCP server.** `ok` — up, and correctly refusing an
  unauthenticated call.

## The company board

Reachable this run (`BOARD_API_URL`/`BOARD_RUNTIME_TOKEN`). Added a
follow-up comment to the standing repeat-failure backlog item, written in
plain words per the owner's no-codes ruling (the board itself now
enforces that ruling on every comment, rejecting a first draft of this
one for naming a pull request by number).

One finding worth naming rather than leaving quiet: the board's own
sprint record still reads "Launch-ready newsletter," dated 2026-09-21 to
2026-09-27. That window closed six days ago and nobody has rolled it
forward to match the sprint file actually in force. Not this standup's to
fix (charter §4 reads the board, it does not groom it), but it is now 11
days stale rather than the 5 days a prior standup already flagged, so the
gap is widening rather than closing.

## Linear trial

Not checked this run, no new signal. Still on trial per the 2026-09-19
ruling.

## Pending items past their date

Not reconciled this run (standup mode writes this file alone, per
charter §4; full `pending.md` reconciliation is ceremony-only, §1d, next
due 2026-10-05). One item worth repeating here rather than waiting for
Monday: the `DATABASE_URL` read-only credential is still missing from
this seat's workflow and is the single reason the press and pipeline
read `unknown` above instead of a real answer.

## Dispatched by the PM

None. No dispatch was fired or proposed this run: every dispatchable seat
is excluded by the hard stop above.
