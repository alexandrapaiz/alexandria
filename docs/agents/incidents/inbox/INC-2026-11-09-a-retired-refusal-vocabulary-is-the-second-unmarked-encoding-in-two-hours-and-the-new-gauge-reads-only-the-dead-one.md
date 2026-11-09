## INC-2026-11-09-a-retired-refusal-vocabulary-is-the-second-unmarked-encoding-in-two-hours-and-the-new-gauge-reads-only-the-dead-one - A retired refusal vocabulary is the second unmarked encoding found in two hours, and the gauge shipped this morning reads only the dead one (2026-11-09, exo seat)

**What happened.** Grouped by day over every log under
`/srv/asc/state/.epito/logs`, the provider has refused this fleet in three
distinct sentences, and two of them are disjoint in time: `You've hit your
weekly limit · resets <date>, 11pm (UTC)` appears in 488 logs from 2026-10-18
to **2026-11-02** and never after, and `You've hit your org's monthly spend
limit · ask your admin to raise it at claude.ai/admin-settings/usage · your
weekly limit resets <date>, 11pm (UTC)` appears in 257 logs from **2026-11-03**
to 2026-11-08 and never before. No day carries both. `tools/ration.py` in
`alexandrapaiz/alexandra-systems`, the fleet's new fuel gauge, shipped to that
trunk this morning with two regexes — `WEEKLY_ANY` and `WEEKLY_DATED` — that
both require the contiguous phrase `hit your weekly limit`, so **both match the
retired sentence and neither matches the live one.** Checkable in four lines
with no network: run either regex against the live-era string and it returns
`False`. The same match does two jobs in that file: `anchor_cycle` derives the
instant the weekly allowance resets from it, and `walled` decides which cycles
count toward the observed ceiling.

**Why it is in this register.** The standing rule records an issue the moment it
repeats. This is the **second instance of one class in under two hours and the
third in eight days**, each on a different surface:

1. **2026-11-02**, the board's `pr_url` field: filled by a regex over the last
   64 KiB of a run's output, so a run that named its pull request in words
   dropped out of the record while having shipped
   (`INC-2026-11-02-two-owner-actions-from-a-merged-sweep-had-no-surface-but-a-pull-request-body`,
   sibling class).
2. **2026-11-09 08:0xZ**, the audit log's `exit` field: the encoding changed
   from the GitHub Actions runner's signal arithmetic to the host's words on
   2026-10-17, nothing marked it, and twenty-three days later this seat and
   HQ's centralizer tallied the whole file and reached **opposite** wrong
   conclusions eight hours apart. Recorded in `docs/agents/learning-log.md` and
   on `docs/agents/hq-relay.md` under that timestamp; HQ has queued the remedy
   — a field that says which encoding it is in — "for the harvest in those
   words".
3. **This one**, 09:0xZ, the provider's refusal sentence, found by applying the
   method instance 2 produced, to a different field, for an unrelated reason.

The repeat is what makes it a register entry rather than a relay ask. One
unmarked encoding is a defect in one field. Three in eight days, in three
fields, on three surfaces, is a property of how this fleet records state: **no
field anywhere in it carries a generation marker, so every reader silently
inherits whichever era was live when it was written.**

**What it cost.** Instance 2 cost two seats a conclusion each and two rounds of
correspondence. This one has not cost a wrong decision yet, and that is luck
with a date on it rather than a clean bill:

- The gauge's observed ceiling is intact **today** only because all four walled
  cycles it medians over predate 2026-11-03. The next cycle refused in the live
  era has `weekly_refusals == 0`, so it is classified *never hit the wall* and
  excluded from the ceiling as "a floor, not a ceiling" — in the era where the
  monthly cap is what binds.
- `anchor_cycle` is extrapolating the weekly reset instant forward from a
  **2026-11-02** observation, seven days stale, while the identical instant is
  written **257 times** in the live era in a form it cannot read. Stepping
  always produces an answer, so a wrong anchor and a right one are the same
  output.
- One round of correspondence with HQ was spent on which of two readings of the
  2026-11-08 quiet day was correct, when the reason the question was hard is
  this defect: **the live refusal string names two limits and no field says
  which one refused the call.** Both of us read it from the end we already
  believed, which is instance 2's exact failure, on a new surface, between the
  same two seats, ninety minutes later.

**The fix, or why there is not one yet.** `tools/ration.py` is HQ's file, so the
repair is routed and not made here: `docs/agents/hq-relay.md`, 2026-11-09 09:0xZ
entry, Ask 1, delivered as handoff `bb3cd879` at 09:11Z with its live test. The
asked-for shape is a widening — match `hit your (weekly|org's monthly spend)
limit`, or match the `resets … (UTC)` clause and record which limit named it —
and HQ's own code already holds the harder half one surface over: the board's
`/api/capacity` route returns `scope` and `reset_scope` as two separate fields
and prints, for 2026-11-08, that the announced reset "does not raise the cap".

The part that is not routed, because it is this repository's: `L-A180` in
`docs/agents/learning-log.md` — **group a regex's own hits by day before
trusting it, not only the values it selects.** §2 of `prompts/exo-agent.md`
already carries three instrument rules, for the subject, the argument and the
window. None of them covers a selector whose last match is a week old, which
answers every question with the retired era's data and is indistinguishable
from a working one. That charter edit is **owed row 18** in
`docs/agents/exo-owed.md` rather than done: this was a wake run with one
improvement, and the improvement went on the measurement.
