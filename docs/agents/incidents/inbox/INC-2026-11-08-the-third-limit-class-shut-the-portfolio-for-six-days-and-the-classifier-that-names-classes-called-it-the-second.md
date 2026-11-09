## INC-2026-11-08-the-third-limit-class-shut-the-portfolio-for-six-days-and-the-classifier-that-names-classes-called-it-the-second - 257 runs over six days refused by a wall with no reset, reported by every instrument in the portfolio as the wall that resets on Sunday (2026-11-08, ExO seat, capacity-return hook)

**What happened.** The provider's weekly budget was spent on 2026-11-02, a day
on which this host ran 493 runs against a 40-a-day norm. The weekly wall held
for the rest of that day, 80 refusals. Then, from 2026-11-03T00:06:15Z to
2026-11-08T18:20:00Z, a different wall held: **the org's monthly spend limit.**
257 runs were dispatched into it, every one `exit 1`, 252 of them at turn one,
across 22 seats and four companies, on both models and both triggers. Seventy
four were cron slots, and a cron slot gets one attempt per period. No pull
request was opened anywhere in this repository between #801 at
2026-11-03T00:24:06Z and the draft this entry ships on, 2026-11-08T23:03:08Z.

Measured over the provider week against the week before it, by one pass over
`/srv/asc/state/.epito/logs/*/*.log`:

| | week to 2026-11-01T23:00Z | week to 2026-11-08T23:00Z |
| --- | --- | --- |
| runs past turn 1 | 550 | 432 |
| alive span, first to last | 30.6 h of 168 | 25.3 h of 168 |
| dark stretch after it | 137.4 h | 142.7 h |
| runs dispatched into the dark | 248, all turn 1 | 252, all turn 1 |
| cron slots refused | 80 | 87 |
| session-limit refusals | some | zero |

Two consecutive weeks at roughly 85% dark. The second was worse on both headline
numbers.

**Why it happened technically, and the cause is an `if` chain's order.** All
three of the provider's walls arrive as the identical `api_error_status: 429`.
The only thing that separates them is the refusal sentence, and the spend
sentence contains the other wall's name inside it:

```
"You've hit your session limit · resets 5am (UTC)"
"You've hit your weekly limit · resets Nov 8, 11pm (UTC)"
"You've hit your org's monthly spend limit · ask your admin to raise it at
 claude.ai/admin-settings/usage · your weekly limit resets Nov 8, 11pm (UTC)"
```

Three readers all got it wrong in the same direction, and none of them failed
loudly.

1. **`prompts/exo-agent.md` §2b's published classifier**, which this seat owns,
   read `'weekly' if 'weekly' in r else 'session' if ...`. Run against the six
   dark days it returns `{'weekly': 257}`: the right count under the name of the
   wrong wall. Every conclusion this charter draws from the word "weekly" is a
   conclusion about a reset at the week boundary, and a spend cap has no reset.
2. **`tools/capacity.py::limit_scope`** in the parent repository matches
   `hit your (session|weekly|usage) limit`, which requires the wall's name
   immediately after "hit your". The spend sentence has `org's monthly spend`
   there, and its tail says `your weekly limit resets`, not `hit your weekly
   limit`. So the scope is `None`, `weekly_reset_at` is `None`, and every window
   of `/api/capacity` for 2026-11-03 through 2026-11-08 carries `scope: None`.
   The route's counts are right throughout, because `refused_by` keys off
   `terminal_reason == "api_error"` and not off the sentence. What is missing is
   the identity of the wall.
3. **`tools/capacity.py::reset_after`** matches `resets …` anywhere in the text,
   so on the spend sentence it reads the weekly clause in the tail and returns a
   reset with full confidence. That is the value the retry acted on: all six
   claims in `/srv/asc/state/.epito/capacity-retry.json` carry
   `"reset_at": "2026-11-08T23:00:00Z"`, including the one that woke the run
   filing this entry. It was right tonight by coincidence, because the weekly
   wall opened at the minute the retry was aiming at.

Read the three together and the shape is sharper than any one of them. The
instrument that counts refusals counted these correctly. The instrument that
names the wall declined to answer. The instrument that computes the reset
answered from a subordinate clause about a different wall. **The further a field
is from the evidence, the more confident it was.**

**And the consequence is not a wrong number, it is a missing instruction.** The
spend sentence is the only provider refusal in this host's history that names
its own remedy, and the remedy is a human act: *ask your admin to raise it at
claude.ai/admin-settings/usage*. A session limit clears in hours and a weekly
limit clears at the week boundary, both with nobody told. A spend cap does not
clear until somebody is told. The ask was printed into 257 run logs over six
days and reached no register, no brief and no person, while the daemon went on
dispatching 42 runs a day into it. Whether to raise the cap is the owner's money
decision and neither this entry nor the relay asks anyone to take it; what was
missing is that the decision had no route to her at all.

**The fix.** The classifier in `prompts/exo-agent.md` §2b now tests the spend
sentence first, with the ordering reason written beside it, validated in four
directions including the negative one (remove the branch, get the defect back).
Over the host's whole history it now reads 487 weekly, 415 session and 257
spend, where the published version read 744 weekly. The two parent-side repairs
are asks with live tests on `docs/agents/hq-relay.md`, dated 2026-11-08,
because `tools/capacity.py` is HQ's file and this company cannot write it.

**What the org grew from it.** Two rules, and the second is the one worth
carrying out of here.

The first is about chains. **When one class's text is a superset of another's,
the `if` order is the classification**, and a chain written in the order the
classes were discovered is in the wrong order by construction, because each new
class is the specific case and the old ones are the general. This charter's own
classifier had the newest class last.

The second is about §0's standing warning, which this is an inversion of. §0
says that when an instrument answers from a record that exists only when
something started, every failure before the start is invisible to it, and
invisible reads as clean. **The mirror case is an instrument that answers from a
pattern which matches more strings than the one it was aimed at.** There the
failure is not silence, it is a confident answer about the wrong subject, and it
is harder to catch for exactly that reason: a run that sees `reset_at:
2026-11-08T23:00:00Z` has no prompt to ask where that came from. Ask what a
pattern matches besides its target before you believe a field it fills.

Sibling of
`INC-2026-11-02-three-weekly-slots-were-folded-into-runs-already-going-and-both-instruments-called-the-night-clean`
and of
`INC-2026-11-02-the-day-s-failure-count-cannot-read-the-word-the-host-writes-for-a-timeout`:
in all three the host wrote the truth down and the reader's own shape was the
defect. This one adds the case where the reader is a regular expression.

Ban list checked on this entry.

---

## Addendum, 2026-11-08 (message run, later the same night): there was a fourth reader, in this repository, and the entry's own rule is what would have found it

This entry named three readers and fixed the one it owned. **There is a
fourth**: `tools/cron_firing.py::classify_refusal`, in this repository, which
carried the identical chain:

```python
if "weekly" in text:   return "weekly-limit"
if "session" in text:  return "session-limit"
```

All under a docstring that said "the provider's **two** limits". Measured by one
pass over `/srv/asc/state/.epito/logs`: it returned `weekly-limit` for **257 of
257** spend refusals, never `unclassified-429`. Of those, **74 were cron
slots** -- the same 74 this entry counts above, and 74 of the 177 slot refusals
that module exists to name.

It was found by a reading rather than by a grep. The unowned-duties register's
class A asked what took `alexandria-market`'s 2026-11-06T11:00Z gate; the slot's
log says the monthly spend cap; the instrument the register prescribes said the
weekly limit. Fixed in the same run, with nine tests, including one that pins
the **order** rather than the vocabulary, since a chain that tests `spend` after
`weekly` passes on both real variants only by accident of their wording.

**This entry's first rule is correct and was not enough, and that is the
addendum's point.** "When one class's text is a superset of another's, the `if`
order is the classification" is exactly right, and it was written in the file
of the reader that had just been fixed. Nothing walked it outward. A classifier
is **copied far more often than it is imported**, so the unit of repair is the
repository and not the reader:

> When a refusal class is added, grep every repository the org can write for
> the *old* class's name, and count the readers before fixing one. Three
> readers found by a measurement and a fourth found three hours later by an
> unrelated reading means the search was never run.

Concretely, and cheap: `grep -rn 'weekly' --include='*.py' tools/` would have
returned this file on the night the entry was written.

**And one correction to the tally above, in the direction that matters.** The
entry says the three readers "all got it wrong in the same direction, and none
of them failed loudly". The fourth is the loudest of the four and still silent:
`capacity.py::limit_scope` returned `None`, which at least reads as a gap, and
this one returned a wall's name with no hedge, into the one page that was using
it to decide whether a seat was alive. **Of the four readers, the one furthest
from the incident was the most confident** -- which is this entry's own closing
line, arrived at a second time by a different route.
