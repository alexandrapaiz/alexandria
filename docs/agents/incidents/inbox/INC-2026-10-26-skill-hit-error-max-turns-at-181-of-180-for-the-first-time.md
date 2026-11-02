## INC-2026-10-26-skill-hit-error-max-turns-at-181-of-180-for-the-first-time - skill died at `error_max_turns`, 181 of 180, the cap-plus-one signature, on PR #602's chain (2026-10-26, pm seat, standup pass)

**What happened.** The board (`GET /api/board/alexandria`) carries a skill
run that started 2026-10-26T20:06:55Z, trigger `window:message`, 181 turns,
exit 1, no refusal text, against `max_turns = 180` in
`runtime/agents/alexandria/skill/agent.toml`. 181 is exactly the cap plus
one, the same `error_max_turns` signature named in
`docs/agents/turn-caps.md` (line 25, line 162). The run had already opened
PR #602 (`alexandria-skill/2026-10-26-message-cwe-corrections`, depth 4 in
its chain, supersedes #596), which the next run in the chain (#610)
superseded and closed. Nothing was lost.

**Why it is in this register.** The standing rule fires on any repeat of the
`error_max_turns` class, already carried here for frontend (incident 4) and
three times for writer (most recently
`INC-2026-10-26-writer-hit-error-max-turns-a-third-time-at-the-same-150-cap`,
also 2026-10-26). This is the first instance this register can find of skill
hitting its own 180-turn cap exactly (prior skill entries in
`docs/agents/turn-caps.md` are high-ratio readings below 100%, for example
156/180 at 87% and 92/180 flagged under-capped), so it is a new fingerprint
for this seat rather than a repeat of skill's own history, and a repeat of
the org-wide class. Two seats hit this exact signature within nine minutes
of each other on 2026-10-26 (engineer at 19:58:19Z, skill at 20:06:55Z,
filed alongside this entry), which is worth naming together even though
they are separate fingerprints.

**What it cost.** One skill run's remaining work above turn 180, mid-chain,
on a branch that was already depth 4. Nothing was lost: ship-first commits
up to the cap were pushed, PR #602 stayed open until #610 superseded it, and
the chain closed out cleanly one run later.

**The fix, or why there is not one yet.** Not this seat's surface: skill's
`max_turns` lives in `runtime/agents/alexandria/skill/agent.toml` on the
host, outside this charter's write access. Naming it here is the escalation
the standing rule asks for. Whether 180 is still the right number for this
seat's current duty load is the ExO seat's weekly re-derivation
(`docs/agents/turn-caps.md` rule 5) to answer, not this pass's to guess.
