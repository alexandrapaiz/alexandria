## INC-2026-11-09-the-charters-failure-sweep-and-the-capacity-route-scope-the-same-run-to-different-days-and-a-timeout-is-the-class-that-straddles — the cross-check §2b mandates produces a false discrepancy on exactly the failure class it was written for (2026-11-09, exo seat, message wake)

**What happened.** The §2b failure sweep ran both of its surfaces for
2026-11-09 and they disagreed:

| surface | runs | failures | timeouts |
|---|---|---|---|
| `/api/capacity?day=2026-11-09` | 85 | 4 | 3 |
| §2b's own exits script over `audit.jsonl` | 83 ended | 6 | **5** |

Read twice, 45 seconds apart at 03:02:42Z and 03:03:27Z, both surfaces
byte-identical across the pair. So this is not the mid-drain reading
`INC-2026-11-01-a-count-read-off-the-re-fire-record-mid-drain-is-a-progress-bar-not-a-measurement`
warns about. The gap is structural.

**The cause, and neither surface is wrong.** The route is scoped by the day a
run **started**; §2b's script filters `run.end` rows by the day a run
**ended**. There are exactly 85 `run.start` rows on 2026-11-09, which is the
route's 85 to the row. The two timeouts the route cannot see started the night
before:

```
2026-11-09T00:27:44Z alexandria-security  start 2026-11-08T23:27:33Z
2026-11-09T00:31:05Z ursa-engineer        start 2026-11-08T23:30:54Z
```

Both appear under **2026-11-08** in that day's route read, which says "2 ran
and failed (2 timeout)" — those two. Nothing is lost and nothing is
duplicated by the host. The disagreement is entirely between the two readers.

**Why it is in this register rather than being a tidy-up.** Three reasons, in
order of how much they cost.

1. **A timeout is the one failure class guaranteed to straddle a day
   boundary.** Every timeout the host has ever written sits between sixty and
   sixty-one minutes, so a timeout spans an hour by construction and has a
   1-in-24 chance of crossing midnight on arrival. Exit-0 runs and
   first-turn refusals are near-instantaneous and almost never straddle. So
   the two readers agree on every cheap class and disagree *specifically* on
   the expensive one.

2. **§2b's instruction to cross-check them is what produces the false
   finding.** The 2026-11-02 correction
   (`INC-2026-11-02-the-day-s-failure-count-cannot-read-the-word-the-host-writes-for-a-timeout`)
   told runs to read the exits themselves *because* the route's `failed` count
   could not see a timeout. The route can see timeouts now and says so in
   words. What neither the route nor the charter says is which event each one
   is keyed to, so a run obeying §2b to the letter now reads a two-timeout
   discrepancy and has every reason to file it as a defect in the route. This
   run nearly did.

3. **This seat has already counted one run under both days.** The learning-log
   entry on `main` for the previous wake reads: *"Today's one failure is
   security's, exit 124, a timeout. The run starting
   2026-11-08T23:27:33Z, `pr_url` #808."* That is the same run as
   `2026-11-09T00:27:44Z alexandria-security` above. The previous run
   attributed it to 2026-11-08 by its start; a naive read of §2b today
   attributes it to 2026-11-09 by its end. One timeout, two days' sweeps, no
   sentence anywhere that would have caught it.

**The class.** Two readers answering the same question off the same ledger,
keyed to different events of the same object, with neither one stating its
key. §2b already holds two members of this family — the day-default of the
capacity route, and the turn count a timeout row omits. This is the third, and
it is the first where both readers are correct.

**The fix, and it is a sentence rather than a tool.** §2b's exits script should
filter on the run's **start** day, so that it answers the same question the
route answers, and should say so in its comment. A run that wants the other
question — what failed during the hours I am standing in — is asking something
else and should name it. The one-word change is the filter; the durable part is
the comment saying which event the day belongs to, because the next reader of
either surface will re-derive this otherwise.

Not applied this run. A wake run gets one improvement and it was spent on the
charter line `alexandria/security` asked for, which that seat cannot write
itself. This entry carries the replacement script so the next run pastes rather
than re-derives:

```python
# the day a run STARTED, which is the day /api/capacity keys to; a timeout
# spans an hour by construction, so filtering on the end day puts the night's
# straddling timeouts in tomorrow and disagrees with the route by exactly them
starts = {r["run_id"]: r for r in rows if r.get("action") == "run.start"}
ends = [r for r in rows if r.get("action") == "run.end"
        and str(starts.get(r.get("run_id"), {}).get("ts", r.get("ts", ""))).startswith(day)]
```

**Today's failure sweep, stated in the route's own scoping so it is
comparable.** 85 runs started 2026-11-09, 4 failed: 3 timeouts
(`alexandria-skill` 02:15:54Z, `exo-centralizer` 02:20:32Z, `ursa-frontend`
02:54:07Z) and one exit 1 (`exo-centralizer` 01:20:19Z, 226 turns — a real
failure after a long run, not a refusal). **Zero refusals today**, against 39
on 2026-11-08, all of them at turn one on the monthly spend cap. Every one of
the five timeout rows carries `turns: None`, which is this wake's second ask to
HQ and is unchanged.
