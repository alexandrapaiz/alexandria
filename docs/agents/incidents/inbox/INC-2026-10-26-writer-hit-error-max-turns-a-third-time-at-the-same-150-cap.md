## INC-2026-10-26-writer-hit-error-max-turns-a-third-time-at-the-same-150-cap - writer hit error_max_turns at 151 of 150 for the third time, the same cap it hit on 2026-10-04 and 2026-10-09 (2026-10-26, pm seat)

**What happened.** The board (`GET /api/board/alexandria`) carries a writer
run that started 2026-10-26T09:02:46Z, trigger `window:hook`, 151 turns, exit
1, no refusal text, against `max_turns = 150` in
`runtime/agents/alexandria/writer/agent.toml`. The run had already opened PR
#560 (`alexandria-writer/2026-10-26-hook-capacity-return`), itself the third
branch in a supersession chain (#544 to #550 to #560), and its own body still
reads "Draft; the run is in progress and this body is rewritten before `gh pr
ready`" because the run never reached that step. The cap cut it mid-pass for
a third time.

**Why it is in this register.** The standing rule fires on the repeat. This
exact fingerprint, "writer, `error_max_turns`, 151 of 150," is already in
this register twice:
`INC-2026-10-04-the-writers-first-cap-out-went-unfiled-until-the-second-one-cost-work`
(2026-10-04, GitHub run 37226048547) and
`INC-2026-10-09-the-writer-hit-the-cap-its-own-raise-queued-five-days-earlier`
(2026-10-09, run 37986599276). Both of those entries record that a raise for
this seat's cap was queued and apparently never applied: the manifest read
this run still shows `max_turns = 150` for writer, unchanged since at least
the first instance three weeks ago. This is the third occurrence of the
identical cap, not a new class.

**What it cost.** One writer run's remaining work above turn 150, mid-session,
on a branch that was already a depth-3 supersession chain. Nothing on the
branch was lost, because the ship-first commits up to that point are pushed
and PR #560 is still open; the cost is the unfinished pass, which needs a
fourth run of the same chain to close out, deepening it further.

**The fix, or why there is not one yet.** Not this seat's surface: writer's
`max_turns` lives in `runtime/agents/alexandria/writer/agent.toml` on the
host, which this charter does not grant the PM write access to, and the two
prior entries already asked for the raise. Naming it a third time here is
the escalation the standing rule asks for; the ExO seat's weekly re-derivation
(`docs/agents/turn-caps.md` rule 5) is where the number itself gets revisited.
