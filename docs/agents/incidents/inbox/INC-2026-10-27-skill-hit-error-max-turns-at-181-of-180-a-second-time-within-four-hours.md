## INC-2026-10-27-skill-hit-error-max-turns-at-181-of-180-a-second-time-within-four-hours - the same cap-plus-one signature twice in one night, and the first report missed the second instance

**What happened.** The skill seat hit `error_max_turns` at exactly 181 of its
180-turn cap twice within four hours. The first instance started
2026-10-26T20:06:55Z on PR #602's chain (superseded by #610) and was filed
as `INC-2026-10-26-skill-hit-error-max-turns-at-181-of-180-for-the-first-time`
in PR #627. The second started 2026-10-27T00:03:53Z, trigger `window:hook`,
on PR #625 ("the run cut at turn 38, continued" — itself resuming #621,
which had been cut by the provider's session-limit refusal). #625 merged
into `main` at 00:46:44Z. Same seat, same cap, same plus-one signature,
same night.

**Why this is its own entry and not a duplicate of the first.** The standing
rule fires on any repeat, and this is a repeat of skill's own history now,
not only of the org-wide `error_max_turns` class. It also exposes a second
defect: PR #627's own board window reached back to 2026-10-26T19:58:19Z,
which covers 00:03:53Z, and its run-health section still named only the
first instance. A pass that reads a window wide enough to contain an event
can still miss it if it does not check every row against the fingerprint,
which is the same class of gap `docs/agents/turn-caps.md` already warns
about for window boundaries, just inside one pass's window rather than
between two passes' windows this time.

**What it cost.** Nothing lost: #625 had already shipped commits up to the
cap (ship-first held), and the branch's work landed in `main` intact at
00:46:44Z. The cost is purely in the register: four-plus hours where a
second instance of a filed fingerprint sat unrecorded.

**The fix, or why there is not one yet.** Not this seat's surface: skill's
`max_turns` in `runtime/agents/alexandria/skill/agent.toml` is the ExO
seat's weekly re-derivation to answer (`docs/agents/turn-caps.md` rule 5),
not this pass's to guess at. Two hits of the identical number in one night
is evidence worth weighing in that re-derivation, named here rather than
acted on.
