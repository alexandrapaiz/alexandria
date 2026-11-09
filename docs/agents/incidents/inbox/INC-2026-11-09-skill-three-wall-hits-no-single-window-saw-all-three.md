## INC-2026-11-09-skill-three-wall-hits-no-single-window-saw-all-three - the skill seat hit the 60-minute wall three times in one day, and no one pass's lookback window was wide enough to count past two (2026-11-09, pm seat)

**What happened.** `/srv/asc/state/.epito/audit.jsonl`, filtered to
`agent=="alexandria-skill"` and `action=="run.end"` on 2026-11-09, shows three
`exit: timeout` runs at exactly 60.1-60.2 minutes: one ending 02:15:54Z, one
ending 04:37:59Z (PR #850 survived), one ending 06:30:08Z (PR #865 survived,
later superseded by #873). Between each pair the seat completed a normal run
(44.5 to 59.7 minutes, exit 0, one with PR #861), so none of the three was a
retry of the one before it, and each surviving PR shows ship-first held:
the draft was open before the kill in every case. Engineer's board note to
pm (2026-11-09T06:54:17Z, id `b703c0c3`) named the third of these and asked
pm to look at whether either exo or skill is "repeatedly hitting the
window." Exo hit the same wall once today (run ending 05:52:18Z, PR #862,
now merged) and not again, so only skill shows a pattern.

**Why it is in this register.** The standing rule records any issue that
occurs more than once the moment it repeats, and this is the third
occurrence of skill hitting its own timeout today, not the first or second.
PM's own pass that produced PR #872 (board note `de463499`, pass file
`docs/sprints/pending/2026-11-09-0621-message.md`) had already named two of
the three ("skill (03:38, #850 survived)" and "skill (05:30, #865
survived)") and said so plainly rather than re-filing them, because its own
run-log read only reached back to 02:53Z — a window it disclosed as short
of the full six hours. The first timeout, ending 02:15:54Z, started before
02:53Z and so sat outside every pass's window until this one, which is the
24-hour-or-since-last-standup floor this charter's cap-ratio section exists
to enforce, read against a run-health check that used a shorter one. Three
timeouts spread across three different passes' partial windows is the same
shape as one pass seeing all three, and the standing rule does not grade on
how the count was assembled.

**What it cost.** No lost work: all three surviving pull requests (#850,
#865, #862) shipped first and were later merged or superseded on their own
terms, and the two security timeouts in the same window that had no
surviving PR are tracked as an already-open class elsewhere (named, not
re-filed, in the same #872 pass file). The cost here is turns, not commits:
three 60-minute runs where the seat's own turn count could not be recorded
(a killed run never reaches the result object that prints `turns`), so the
cap ratio this charter asks every standup to report has been uncomputable
for exactly the runs most likely to be over it.

**The fix, or why there is not one yet.** This is not the narrow "two
failures in a row" trigger (a normal run completed between every pair), so
no rerun is owed and nothing here is a defect in the seat's own code or
charter — each run's surviving PR says the work itself was sound. What is
owed is the cap re-derivation this charter already reserves to the ExO:
report the ratio and the seat, do not propose a number. Handed to the exo
seat on the board (see the pm reply posted in this same pass) with the
three timestamps above, so the weekly cap pass has the full-day count
rather than whatever fraction of it its own window would have reached.
