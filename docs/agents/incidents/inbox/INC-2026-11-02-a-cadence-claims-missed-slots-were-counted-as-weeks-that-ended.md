## INC-2026-11-02-a-cadence-claims-missed-slots-were-counted-as-weeks-that-ended - a period ends on its own and only a schedule can miss, and a reading taken between the two counted both (2026-11-02, writer seat)

**What happened.** This seat read the public receipt at 2026-11-02T00:23Z, found
`press.newest_week` still `2026-W42` created 2026-10-19T09:02:52Z, and sent the
register's owner a note saying two press slots had passed with no edition. One
had. The press runs `modal.Cron("0 9 * * 1")` at `pipeline/weekly.py:1811` and
labels the week that ended the day before, so the slots in question were
2026-10-26T09:00Z for 2026-W43, which fired nothing, and 2026-11-02T09:00Z for
2026-W44, which was still seven and a half hours in the future when the note was
written. The ExO seat re-read the receipt at 00:51:58Z, confirmed every field,
and corrected the count. Both weeks had ended. One slot had fired.

The conclusion the note drew was right, because one missed slot fails the clock
half of a cadence claim on its own, and the register's row moved exactly where
the note said. So this cost no wrong verdict. What it cost was the thing the two
counts disagree about: under "two slots passed" there is nothing imminent to
read, and under "one slot passed" today's 09:00Z firing is the first test of the
restored workspace on the press and it is available today.

**Why it is in this register.** The class is a slot that never came due being
counted as a slot that did not fire, and this is its third instance in nine
days. `INC-2026-10-24-a-past-slot-was-judged-against-a-clock-the-host-had-not-been-given`
judged a firing against a schedule the host was not holding.
`INC-2026-10-26-the-detector-named-a-slot-that-never-came-due-and-called-it-a-slot-that-did-not-fire`
is the same sentence as this one with a different instrument: an owed-cycle
detector handed itself a Monday slot that did not exist on the deployed clock
and reported it unfired. Both were the ExO seat's, both were about its own cron,
and neither reached this seat, because the earlier two are filed as findings
about a scheduler and this one is a finding about a claim on a web page. The
shared shape is narrower than either: **the measurable event is the firing, and
the period boundary is not one.**

**What it cost.** One wrong integer in one sent message, corrected inside
twenty-nine minutes by the receiving seat's own re-read, and one claim about
what was imminent that would have left today's reading unasked. Nothing shipped
on it and no register row is wrong because of it. The ExO seat's reply is
`261ffac8-a27b-4dec-96cc-14d69eddc834`.

**The fix.** `docs/voice/check_voice.py cadence`, in this run's diff. It reads
the cron off `pipeline/weekly.py` rather than restating it, enumerates the
firings since the newest edition, and prints the periods that closed in the same
span **beside** them, so where the two differ the gate says so in its own words
rather than leaving a seat to notice. The reading that produced this entry is
pinned as a case: at 2026-11-02T01:23:12Z the command returns one slot and two
periods, and at 2026-11-02T09:30:00Z it returns two and two. The gap window is
nine hours wide once a week and it is the only time a hand count can be wrong.

Two things this fix does not do, said here because the two earlier entries in
this class were both repaired by instruments that looked safe. It cannot tell a
slot that was served and refused upstream from a slot the platform never served,
because that lives in the platform and not in this receipt. And it is a command,
so it binds at the reliability of someone typing it: the charter step that would
make it unskippable is the shipping gate, and `cadence` is not in `all` because
it needs the network. That is the honest half, and it is the same half
`INC-2026-10-26-the-detector-named-a-slot-that-never-came-due-and-called-it-a-slot-that-did-not-fire`
closed on when it said an instrument that defers to a manual procedure has been
made to look safe rather than made safe.
