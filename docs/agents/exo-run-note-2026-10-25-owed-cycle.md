# ExO run note — 2026-10-25, the run that took the owed 14:00Z cycle

**Mode.** The **weekly cycle**, taken as an owed slot rather than on a cron.
The trigger was a `message` wake asking for the next item in my lane; §0's
owed-cycle detector returned `THE CYCLE IS OWED` for 2026-10-25T14:00Z and
that outranks the trigger. Chain depth zero, branched from `main`, no open
pull request of this seat.

**The lane item, which is the event's direct answer.** The one card in my
Backlog column is the three-class split of the nine unevidenced duty rows, and
its own body puts classes A and C on the owner's forty-eight-hour silence
clock. The ask was posted 2026-10-25T02:49Z and comes due 2026-10-27T02:49Z, so
there is nothing to take there yet. Taking the owed cycle was the use of this
run rather than a substitute for the lane.

## The one thing this run found

The provider enforces **two** limits and every instrument in this organization
read them as one, because a weekly limit and a session limit both arrive as
`api_error_status: 429` with `exit: 1`. The discriminator is the refusal
sentence in each run's own log. On 2026-10-25 it was **65 weekly against 5
session**; over the host's whole history, 73 against 226.

The weekly limit has a weekday. Both exhaustions on record were hit on a Sunday
and reset at Sunday 23:00Z: 2026-10-18 at 19:21:22Z, 3 h 39 m early, and
2026-10-25 at 03:00:04Z, **19 h 59 m** early. The week that produced the second
ran 675 runs with **467 on the Saturday**.

This seat's cron is Sunday 14:00Z, nine hours inside that window. Three seats
portfolio-wide have their **only** slot of the week there, and on the one
Sunday the host held all three clocks all three were refused. So the owed cycle
was not bad luck. It is a schedule placing the seats with the fewest attempts
per period into the hours the budget is reliably gone.

## What shipped

Three improvements. §0 and §2b learn the second limit, with the splitting
command run verbatim from the file before the commit. §3b gains a fourth
cadence test, which is the only predictive one on that page. `unowned-duties.md`
gains a row for the weekly provider budget, proposed and not assigned because
it is a rate of spend. `registers.md` gains the companion to the dated
conclusion rule: a depth is not a trend.

Plus the standing duties. The relay entry delivered in the same run, two
messages, both accepted first time. The incident registered as the second
instance of its class. The rule-5 cap sweep, three seats over 70%. The §3g
re-measurement, which found a register right about a state and wrong about a
mechanism. The three ideas posted to the owner as a board note.

## What stayed owed, named rather than implied

The §3g live-surface pass, the register polarity pass, and the §5b repository
sweep. The next due slot is **2026-11-01T14:00Z**, a Sunday 14:00Z slot, which
is inside the dead zone on both weeks of evidence. If the cycle is owed again
on that date, the relay ask was not granted and the existing entry takes a
second instance rather than a new write-up.
