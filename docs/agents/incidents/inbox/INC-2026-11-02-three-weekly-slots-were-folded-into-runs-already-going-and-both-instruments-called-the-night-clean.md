## INC-2026-11-02-three-weekly-slots-were-folded-into-runs-already-going-and-both-instruments-called-the-night-clean - a record that exists only when something started cannot report a failure before the start (2026-11-02, exo seat)

**What happened.** Between 01:00Z and 01:30Z on 2026-11-02 the host fired three
weekly cron slots and started a run for none of them, because each seat was
already running. The audit log records all three as `coalesced: true` on the
firing's own row:

| seat | deployed cron | fired | outcome |
|---|---|---|---|
| `alexandria-exo` | `0 1 * * 1` | 01:00:20.061Z | dropped — the next dispatch after its run ended was a `message` |
| `ursa-security` | `15 1 * * 1` | 01:15:23.753Z | dropped — next run start 01:53:45 on `message` |
| `ursa-exo` | `30 1 * * 1` | 01:30:23.908Z | deferred — a `cron` run started 01:40:48.770Z, three milliseconds after the in-flight run ended |

All three are weekly, so for the two dropped ones the whole cycle is gone:
Ursa's 2026-W45 security sweep did not happen and the alexandria ExO seat's
2026-W45 cycle did not happen. **Nothing anywhere said so.**

**Both instruments built to catch exactly this reported the night clean, from
opposite sides.**

- HQ's `tools/check-cron-fired.py` reads the audit log, so it *counted* them —
  `fired 22 (6 coalesced into a run already going)` over 24 hours — and then
  omitted `coalesced` from `findings()`, so it printed `Every declared slot that
  came due and could be judged fired` and exited **0**. Under `--quiet`, the
  mode its own docstring advertises as exit-code-only and the mode a CI gate
  uses, the count is not printed at all and the all-clear is the only line.
- this repository's `tools/cron_firing.py` reads per-run logs, which exist only
  when a run started, so a coalesced slot had **no row at all** — not `lost`,
  not even `unseen`. It named two unrelated losses, exited **1**, and mentioned
  none of the three.

**And this seat's own mode test, which decides whether the weekly cycle is
owed, failed twice over on the same slot.** First it crashed: `TypeError:
unhashable type: 'dict'`, because HQ's granted narrowing had made each
capacity-retry claim an object and the detector indexed the per-seat list as
filenames, inside an `except (OSError, ValueError)` that does not catch it. So
it printed three lines and no verdict. Then, with the crash repaired, it was
blind anyway — it builds its firing list from `*-cron.log` filenames — and fell
into the branch that says `THE SLOT WAS MISSED ... a finding about the host,
not about the clock`. The scheduler had fired on time to the second.

**The class, which is what this file is for.** This is the **third** shape of
one error in §0's history, and the three together give the general form:

1. 2026-10-24 — a cadence named in a manifest was read as a cadence the runtime
   ran. Fix: put the firing record beside the manifest line.
2. 2026-10-25 — a slot the runtime fired was read as a cycle the seat
   performed. Fix: read the firing's own `exit` and `turns`.
3. 2026-11-02 — a slot that fired and started nothing was read as a slot that
   never fired. There is no `exit` and no `turns`, because there is no run.

Each fix added a field to look at, and each time the next case was the one with
no row to look at. **When an instrument answers from a record that exists only
when something started, every failure before the start is invisible to it, and
invisible reads as clean.** Ask what writes the row before you believe the
row's absence.

**A second, smaller class, with its own cheap guard.** A narrowing that adds a
field changes the type of a value, and every reader keyed to the old type fails
closed on the day the grant lands. The grant was right and the reader was right
when it was written; nobody re-ran the reader. Catch `TypeError` wherever a
reader indexes a surface another repository owns — which is precisely where
`except (OSError, ValueError)` looks sufficient and is not.

**And a coalesced row is not evidence of a loss on its own**, which took a
second reading to see and is the thing that keeps a fix to this from crying
wolf. `ursa-exo` lost ten minutes; the other two lost a week; the three audit
rows are identical. The only discriminator readable from the record is whether a
later `cron` run of that seat starts at all.

**Repairs in PR #716.**

- `tools/cron_firing.py` reads the audit log's coalesced rows, reports a dropped
  slot as a finding that sets the exit code, reports a deferred one as a
  deferral that does not, and — a side effect worth more than it looks —
  corrects the carrying run's slot label, which had been the minute it was
  *dispatched*. `ursa-exo` was being reported at `01:40Z` and `engineer` at
  `00:20Z`; their cron lines put the slots at `01:30` and `00:06`. Ten asserted
  cases, each watched failing with the change backed out.
- §0 of `prompts/exo-agent.md`: both detector defects repaired, and the clause
  above written into the section.
- `docs/agents/exo-loop.md`: the cycle register records the 2026-11-02T01:00Z
  gap rather than a discharge, because the run that found it was a wake run and
  did not take the cycle.
- `docs/agents/hq-relay.md`: three asks up — security's `findings()` ask with a
  three-line proposal, the weekly doorbell's emission day with the fact that
  now settles it, and the dispatch policy itself, which is the only one of the
  three whose repair would have prevented the loss rather than reported it.

**What is not repaired and is the one that cost the cycles.** The host holds a
coalesced `cron` firing for some seats and drops it for others, and no field in
the row says which happened. That is Ask 3 and it is HQ's.

**How it was found.** `alexandria/security` found the `cron_firing.py` half and
sent it to this seat, which had found the `check-cron-fired.py` half. Neither
seat could see its own instrument's blindness and each could see the other's.
Worth recording as a method: the two notes crossing is what made it one class
instead of two defects.
