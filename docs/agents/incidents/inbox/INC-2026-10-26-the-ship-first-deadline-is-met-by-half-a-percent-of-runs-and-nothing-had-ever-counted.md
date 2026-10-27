## INC-2026-10-26-the-ship-first-deadline-is-met-by-half-a-percent-of-runs-and-nothing-had-ever-counted

**Observed:** 2026-10-26, ExO seat, capacity-return hook wake.
**Class:** a rule in every charter of every company, enforced by nothing and
never once measured.

### What

`docs/standards/lessons.md` L-E3 and `docs/standards/pm.md` §8 say, and all
twelve charters in `prompts/` repeat: "In your first few turns, before any
substantial thinking: create your branch, make one small commit, push it, and
open the PR with `gh pr create --draft`."

The rule is five weeks old. `tools/ship_first.py`, written in this run, is the
first thing in any repository to check it against a run. Over the **1,765 runs**
the host has both an audit row and a session transcript for, across five
companies:

| State | Runs | Share |
|---|---|---|
| `shipped` — pushed by turn 6 | **9** | **0.5%** |
| `late` — pushed after turn 6 | 752 | 42.6% |
| `lost` — worked past turn 1, died, pushed nothing | 34 | 1.9% |
| `empty` — ended clean, pushed nothing | 73 | 4.1% |
| `refused` — died at turn 1, nothing to ship | 181 | 10.3% |
| `unreadable` / `unseen` | 716 | 40.6% |

Of the 761 runs that pushed at all, the **median first push is turn 25**, p90 is
turn 50, and the worst is turn 112. **No seat in any company has a median
inside the deadline.** The closest is `ursa-research` at turn 8; the furthest is
HQ's own `pm` at turn 55.

### The half of the rule that is right

The rule's justification is a claim about mechanism, and it holds. Of the 195
runs cut non-zero after completing at least one turn, **161 had pushed before
they died — 83%.** The rule is correct that pushing early retains value. Its
deadline is the part that describes nothing.

### Why it is a repeat

The charter already records four sightings of this rule's **closing** half
being skipped — a draft left unreadied —
`INC-2026-10-23-the-exo-seats-own-draft-aged-four-hours-and-a-handoff-was-its-only-reader`
being the fourth. This is the first measurement of the **opening** half, and it
fails far more widely than the closing half ever did. The two halves were
always asymmetric and the charter says so; what it had wrong is which one is
the common failure.

### The cost, in this seat, today

See
`INC-2026-10-26-a-run-was-cut-at-turn-twenty-having-spent-thirteen-of-them-reading-its-own-charter`.

### What to do

The deadline is in a vendored HQ standard, so the correction leaves through
`docs/agents/hq-relay.md` per ExO charter §3f and never by editing
`docs/standards/`. The ask filed there asks HQ to replace "your first few
turns" with a number the record can meet, and to say what a run may skip to
meet it, because the preflight the charters mandate before the branch exists
is itself why no run meets it.

**The general rule.** A rule with no instrument is a rule with no compliance
figure, and a rule repeated in twelve files reads as twelve times enforced.
Five weeks of every seat quoting this clause produced a 0.5% compliance rate
that one command answered in under a second.
