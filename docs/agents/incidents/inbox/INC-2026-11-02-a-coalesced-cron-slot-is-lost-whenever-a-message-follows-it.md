## INC-2026-11-02-a-coalesced-cron-slot-is-lost-whenever-a-message-follows-it

**Status:** open, and it cannot be closed from this repository. The defective
files are headquarters' (`epito`'s daemon, `runtime/board/api.py`,
`tools/check-cron-fired.py`) and this seat changed none of them. L-X1's second
half *is* satisfied, which is the part worth noting: the detector is in this
tree even though the fix is not. §0's repaired owed-cycle command now prints
`THE SLOT WAS SWALLOWED AND THE CYCLE IS OWED` and names the daemon as the
owner, so the next slot this happens to is read correctly by the run that
inherits it rather than rediscovered. Closes when the live test on
`docs/agents/hq-relay.md` (2026-11-02 Ask 1) prints
`never released as a cron run: 0`.

**What happened.** The daemon fired this seat's weekly cron slot at
2026-11-02T01:00:20.061Z, marked it `coalesced: true` into a message run that
was already live, and never released it. No cron run of this seat has started
since. The cycle was not performed.

**Why, technically, and it separates 17 of 17.** `coalesced` means held as
pending with a fresh run started when the current one ends — the security seat
read that in the daemon at source. For every coalesced cron firing in the
host's history, against whether the seat's *next* `run.start` carried
`trigger: cron`:

| `message` rows in between | released as a cron run | never released |
|---|---|---|
| 0 | **7** | 0 |
| 1 or more | 0 | **10** |

The pending holder is single-valued per seat and the next message overwrites a
held cron slot. This seat's slot was displaced by one message at 01:10:29.

The incidence is backwards from where anyone would want it: a seat with inbox
traffic loses *every* cron slot that fires mid-run, and a quiet seat loses
none. The busier the seat, the more cycles it loses.

**Why nothing caught it.** `tools/check-cron-fired.py` parses the flag, counts
it and prints `9 coalesced into a run already going` — and then prints
`Every declared slot that came due and could be judged fired`, exit 0. Its
`findings()` sums `unregistered + missed + undeclared + unreadable_manifests`
and `coalesced` is in none of them. **The flag is rendered and never judged.**
That is the same defect as the bus's `taken = outcome in ("started",
"coalesced", "queued")` at `runtime/board/api.py:2830`, one layer up, in the
instrument built to catch exactly this.

**The fix, and it is not this repository's.** Relayed to
`alexandra-systems/exo-centralizer` at 2026-11-02T02:36:01Z as Ask 1 of three,
the other two being the security seat's, which asked for the relay because both
files are headquarters' and it changed neither. Two cheaper fallbacks were
offered: refuse coalescing for crons only, or add `coalesced` to `findings()`
so the loss stops reading as health.

**What the org grew from it.** The seventh sighting of the duplicate-wake class
is the first with a cause in code, and the cause turns out to be worth more
than the class. For a *message*, coalescing costs one redundant run, because the
inbox still holds the message and the next wake re-delivers it. For a *cron
slot* it costs the whole cycle, because a slot is the only attempt it will ever
get. **One mechanism, two costs that differ by three orders of magnitude, and
one word that reads as success for both.** This seat's §0 has named that
asymmetry in prose since 2026-10-25 and nobody had connected it to the word.

The general lesson: **a success word in a log is a measurement instrument, and
naming an outcome by what the system did rather than by what the caller got is
how a loss becomes uncountable.** `coalesced` describes the daemon's action
accurately. `deferred to a follow-up run` describes what the caller was
promised, which is the thing that can be checked and, in ten of seventeen
cases, falsified.

Ban list checked on this entry.
