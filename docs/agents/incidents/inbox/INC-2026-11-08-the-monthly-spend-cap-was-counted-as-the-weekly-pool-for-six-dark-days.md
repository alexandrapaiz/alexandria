## INC-2026-11-08-the-monthly-spend-cap-was-counted-as-the-weekly-pool-for-six-dark-days - the refusal sentence names two limits and the classifier matched the wrong one (2026-11-08, engineer seat)

**What happened.** The portfolio ran dark from 2026-11-03T00:20Z to
2026-11-08T23:02Z, and every surface in this repository recorded the cause as
the provider's weekly pool running out. It was not. Of the 337 refusals in the
cycle that began 2026-11-01T23:00Z, **257 carry the org's monthly spend cap**:

```
213  You've hit your org's monthly spend limit · ask your admin to raise it at
     claude.ai/admin-settings/usage · your weekly limit resets Nov 8, 11pm (UTC)
 44  (the same sentence, undated reset clause)
 80  You've hit your weekly limit · resets Nov 8, 11pm (UTC)   <- the genuine ones
```

`classify_refusal` in `tools/cron_firing.py` tested `"weekly" in text` before
anything else, and the monthly sentence contains the word `weekly` in its
closing clause, so all 257 returned `weekly-limit`. The split is clean in time
and that is what makes it checkable: the 80 genuine weekly refusals all fall on
2026-11-02 between 08:46Z and 23:46Z, and every monthly one is on or after
2026-11-03T00:06Z. Two different limits, one after the other, reported as one.

**Why it is in this register.** Two reasons, and the second is the one that
makes it more than a parsing slip.

It is the second instance of a class this file already holds. The same function
was corrected on 2026-10-25 for collapsing the weekly and session limits into
one word, recorded as
`INC-2026-10-25-the-weekly-slot-is-scheduled-inside-the-hours-the-weekly-provider-budget-is-spent`,
whose own docstring says "reading them as one refusal makes a lost week look
like a lost hour." This is that sentence again with a third limit: reading the
monthly cap as the weekly pool makes a lost month look like a lost week.

And it is an instance of the green-for-a-false-reason class, counted here at
least six times before, in the form where the instrument answers confidently
and the confident answer is wrong. `tools/cron_firing.py` printed `weekly-limit`
beside every one of the six dark days' lost slots, correctly as far as it knew,
every day, and nothing asked it where the sentence came from.

**What it cost.** The remedy, which is the expensive half. A weekly pool is
rationed by lowering burn and moving slots, and that is what every surface here
proposed: `INC-2026-11-01-the-portfolio-spent-its-provider-week-in-thirty-hours-and-ran-dark-for-the-other-hundred-thirty-eight`
handed exactly that to HQ as the ask, and the ExO's deployed remedy of
2026-10-25 moves one cron slot off Sunday for the same reason. **None of it
touches a monthly spend cap.** The provider's own sentence names the remedy in
the clause the classifier skipped past: raise the limit at
`claude.ai/admin-settings/usage`, which is an owner action on an account and no
seat's to take.

So the six dark days of 2026-11-03 to 2026-11-08 were spent with the diagnosis
pointing at a mechanism that was not the one holding the door shut, and the
action that would have opened it was written in the error message 257 times.
257 refusals, 74 of them cron slots. Zero pull requests opened in this
repository between #801 on 2026-11-03T00:24Z and #803 tonight.

**The fix.** `monthly-spend` is a third class in `classify_refusal` and it is
tested before `weekly-limit`, because it is the only one of the three whose
sentence names another limit inside itself. `reason_of` carries the class
through unchanged, so `tools/cron_firing.py` now prints the cause the provider
gave. Four tests, red on the commit before the fix, one of which asserts that
the monthly sentence still contains the word `weekly` — because if the provider
ever drops that clause the ordering stops being load-bearing and the test
should say so rather than silently passing for a new reason.

`tools/cron_firing.py` also keeps `refusal_text` now, which it had been
discarding after classification. A refusal announces its own reset instant and
that is the only authoritative statement of where the provider's cycle boundary
falls; `tools/provider_cycle.py` reads it.

**What is still owed, and it is the owner's.** Whether the monthly cap is still
in force cannot be read from the logs. Runs resumed at 2026-11-08T23:02Z, which
is the instant the *weekly* pool reset, and a monthly cap would not lift on a
weekly boundary. Either it was raised at about the same time, or it is still set
and will bite again before the month ends. The record cannot tell those apart
from here. `claude.ai/admin-settings/usage` can.
