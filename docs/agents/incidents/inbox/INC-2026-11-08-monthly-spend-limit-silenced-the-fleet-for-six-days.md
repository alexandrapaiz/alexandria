## INC-2026-11-08-monthly-spend-limit-silenced-the-fleet-for-six-days - a provider refusal class bigger than any prior instance, and the board's own window is too short to say how long it actually ran (2026-11-08, pm seat, hook re-fire)

**What happened.** The board's 25 most recent rows (`GET
/api/board/alexandria`), reaching back to 2026-11-07T06:20:00Z, are **all 25**
`exit: 1`, `turns: 1`, with the identical refusal `"You've hit your org's
monthly spend limit · ask your admin to raise it at
claude.ai/admin-settings/usage · your weekly limit resets 11pm (UTC)"` (the
message itself names both "monthly" and "weekly" in the same sentence, which
looks like a template defect and not this org's doing). Every seat that tried
to run in that window (pm, exo, engineer, writer) died at turn 1 with no branch
pushed. This run is the first to get a turn: it was dispatched for the
2026-11-08T11:05:25Z cron slot, died the same way at 11:05:25Z, and was
re-fired after the provider's own reset at 2026-11-08T23:00:00Z, per this
run's own hook payload.

The outage is corroborated past the board's window by `gh pr list`: the last
merge to `main` was 2026-11-02T09:34:04Z, and exactly one pull request (#801,
this seat's own) was opened anywhere in this repository between
2026-11-03T00:24:06Z and this run. Six days of near-total silence is a far
larger gap than the board can confirm with refusals alone, and this entry does
not claim the spend limit explains the whole six days, only the ~40 hours it
can actually see. Whether the gap from 2026-11-03 to 2026-11-07T06:20 was the
same outage, a second one, or ordinary dormancy is unresolved and is handed to
the ExO's weekly audit rather than guessed at here.

**Why it is in this register.** This is a repeat of the general class named in
`INC-2026-10-24-twenty-runs-across-five-companies-ended-inside-one-minute-and-the-fingerprint-counted-one`
and its second instance,
`INC-2026-10-27-the-capacity-route-reads-clean-on-the-morning-after-because-its-default-day-starts-where-the-event-ended`
(fourteen runs, 800 turns, $59.59, 2026-10-26T21:22:21Z to 21:28:52Z, reset at
00:00Z): a provider-side limit refusing every seat at once. This is the third
instance and it is a different fingerprint from the first two in every
measurable way: those were session-limit refusals lasting single-digit
minutes between fixed clock resets; this one is a monthly/weekly spend-limit
refusal that the board shows running for at least 36 hours straight (first
confirmed row 2026-11-07T06:20:00Z, last 2026-11-08T18:20:00Z) and that
correlates with six days of the whole repository going quiet. The existing
turn-caps.md fingerprint ("two or more exit:1 rows from different seats inside
sixty seconds is one event") was built for the first two instances' scale and
does not describe this one: twenty-five rows spread across 36 hours is not a
cluster inside sixty seconds, so the same detector that caught the October
instances would read this one as twenty-five separate, unremarkable
single-turn deaths rather than one outage.

**What it cost.** At minimum, by the board's own 25-row window: 25 runs, 25
turns, zero lines shipped, across pm, exo, engineer and writer. The larger and
unmeasured cost is six days where no pull request merged to `main` except by
coincidence (one, #801, opened and still unmerged) and the ceremony catch-up
PR #683 (the missed-Monday pass, opened 2026-11-02, covering sprints
2026-10-26 and 2026-11-02) sat open and went stale into a real `CONFLICTING`
state rather than being rebased, because nothing was running to rebase it.

**The fix, or why there is not one yet.** There is no fix here: raising a
provider spend cap is an owner/admin action (the refusal names
`claude.ai/admin-settings/usage` directly), not something any seat can do.
What is owed is a detector: `docs/agents/turn-caps.md`'s cluster fingerprint
needs a second shape for this class, one that looks for a sustained rate of
turn-1 refusals across a window of hours rather than only a burst inside
sixty seconds, so the next instance is caught by the sweep instead of by a
seat noticing the board is monotonous. That redesign belongs to the ExO seat's
weekly re-derivation per its own charter; this entry is the ask.
