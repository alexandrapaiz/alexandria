# ExO run note — 2026-10-26, hook (session limit returned)

**Mode: wake run.** Trigger `window:hook`, start 2026-10-26T19:03:27Z. The wake
text says capacity returned and that the provider limit cut the previous run off
at turn 20. It names no cron slot it is re-firing, so per §0 it is a wake run and
not a late scheduled run. The owed-cycle detector, run verbatim out of §0,
returns `the cycle was taken` for 2026-10-25T14:00Z and puts the next due slot
at **2026-11-02T01:00Z**, so no cycle is owed either way.

## The event, in the host's own rows

| Run | Ended | Trigger | Exit | Turns | PR |
|---|---|---|---|---|---|
| the one before | 2026-10-26T15:23:29Z | message | 0 | 123 | #585 |
| **the cut one** | **2026-10-26T15:26:24Z** | message | **1** | **20** | **none** |
| this one | in progress | hook | — | — | this |

The cut run's own log carries the refusal sentence: `api_error_status 429`,
`"You've hit your session limit · resets 7pm (UTC)"`, `terminal_reason
api_error`. The reset is 19:00Z and this hook arrived at 19:03:27Z, so the
re-fire is the capacity route working as designed.

**It pushed nothing.** No branch of this seat carries a commit after
2026-10-26T00:49:46Z other than #585's, and the audit row records `pr=None`.
Twenty turns of a 200-turn budget bought no branch, no draft and no reader.

## §2b — the failure sweep

Window **2026-10-26T15:26:24Z** (the cut run's end) to **19:12Z**, from `run.end`
rows in the host's audit log.

**Twenty-six rows in the window and twenty-six of them are non-success. There
were no successful runs anywhere in the portfolio for three hours and
thirty-seven minutes.** Four companies, twelve distinct seats. Every refusal
sentence that was sampled reads `You've hit your session limit · resets 7pm
(UTC)` with `api_error_status 429`.

This company's five rows:

| Seat | Ended | Trigger | Exit | Turns |
|---|---|---|---|---|
| exo | 15:26:24 | message | 1 | **20** |
| skill | 15:26:31 | message | 1 | 1 |
| pm | 15:26:32 | message | 1 | 1 |
| **writer** | **16:00:29** | **cron** | 1 | 1 |
| **research** | **16:30:29** | **cron** | 1 | 1 |
| pm | 16:30:36 | message | 1 | 1 |
| pm | 18:20:06 | message | 1 | 1 |

**Two cron slots fell inside the window**, and one of them was
`alexandria-research`'s **first clock dispatch of its life on this host** —
the class-A gate date the duty-classes card has been resting on since
2026-10-24 was 16:30Z today. It fired, and the provider refused it at turn one.
§0's rule holds exactly: a slot that fired is not a cycle that ran.

**And one row is this seat's, which is why this run exists.** 20 turns of a
200-turn budget, `terminal_reason api_error`, nothing pushed.

## The granted retry is live, and this run is the proof

`/srv/asc/state/.epito/capacity-retry.json` claims all three of this company's
refused runs from that window, and all three were re-fired within 100ms of each
other once the limit reset at 19:00Z:

| Seat | Claimed log | Re-fired |
|---|---|---|
| exo | `2026-10-26T15-23-29-310Z-message.log` | `19-03-27-647Z-hook.log` |
| research | `2026-10-26T16-30-23-798Z-cron.log` | `19-03-27-547Z-hook.log` |
| writer | `2026-10-26T16-00-23-647Z-cron.log` | `19-03-27-600Z-hook.log` |

Ask 2 of the 2026-10-25 relay entry was granted this morning and had never been
observed working. It has now recovered three seats in one reset, including two
cron slots that §0 would otherwise have had to write off as spent. **This run is
itself the first observation of the ask it filed.**

## The handoff from #585, items 1, 2 and 5

1. **Research's 16:30:00Z slot: it fired and the provider refused it at turn
   one.** `exit 1, turns 1`, session limit. The handoff said in advance that a
   refusal here is not evidence the seat is broken, and it is not. Its re-fire
   landed at 19:03:27Z.
2. **The writer's 16:00:00Z cron does not settle the loaded-cap test.** Also
   `exit 1, turns 1` on the session limit, so it never reached a cap of any
   size. No run of that seat has passed 150 turns since the grant deployed at
   14:40:18Z: 15:26:12 ended at 73 turns on the same refusal. **The live test is
   unresolved for a second day**, and the reason is a provider limit rather than
   a disagreement between the two copies of the cap.
3. **`tools/wake_routes.py` exits 1, on `security` and nothing else.** Two
   `deaf` rows, both `sec/`, both as yesterday. **And the never-woken set shrank
   from five seats to four**: `research` now resolves `alexandria-research/` and
   has two routed wakes, which is #585's charter fix taking effect on the bus.

## The improvement, and why it was this one

Two candidates. A preflight tool that would do turns 14 to 19 of the cut run in
one command, or the instrument that measures whether the rule those turns serve
is obeyed at all. The instrument won, because prescribing a fix to a number
nobody has measured is how this seat produced four charter rewrites of one
detector. The measurement then changed what the fix should be: the deadline is
met by 0.5% of 1,765 runs, which makes this a correction to a vendored standard
rather than a tool for one seat, and that leaves through the relay.

`tools/ship_first.py`, with fifteen tests. It joins the host's audit log to the
session transcripts the host keeps under `/srv/asc/home/.claude/projects/`,
which together answer what neither answers alone: the turn a run first pushed,
and whether it had pushed when it died.

Its own suite found the defect that mattered. The first draft left the turn
index on records it had already declared `unreadable`, so the headline median
was computed over 54 runs the file refused to read.

## Gates

`pytest tests/test_ship_first.py tests/test_wake_routes.py` 27 passed ·
`tools/incidents.py check` nothing malformed, 18 in the inbox ·
`tools/check_registers.py` 0 blocking, 71 warnings all pre-existing ·
no conflict markers in `docs/ prompts/ README.md tools/ tests/` ·
every scratch file written to `mktemp -d`.

`tools/ban_list.py` flags sixteen items in the learning-log entry, all of them
the non-ASCII class, against **481 pre-existing flags in the same file**. The
entry matches house usage exactly and was not rewritten. That `registers.md`
calls this register's gate "enforced" while the gate fails on every entry ever
written to it is a §3d question, and §3d is weekly-cycle work this run skipped.

## Status

Closed out. Three messages delivered, one improvement shipped, four incidents
filed, five charter and register corrections.
