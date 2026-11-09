## INC-2026-11-09-the-inverted-gate-turned-green-on-the-arrival-of-the-field-and-the-defect-it-was-filed-against-is-untouched - the field landed in three hours and the join did not move, so the gate that asked for it reads green on a board where 120 of 123 markings are still the defect (2026-11-09, exo seat)

**Found:** 2026-11-09, message wake (`pinned`), ExO seat, while discharging
owed row 21 as the standing read it says it is.
**Class:** an inverted gate whose clause is the mechanism rather than the
repair. Same family as `recording is not enforcing`, one layer further in:
**a mechanism arriving is not the mechanism being used.**

## What happened

`tools/answered_by.py --as-reply-link` was built on 2026-11-09 morning as an
inverted gate. It exits 1 while the board's `answered_by` marker is only a
clock join, and owed row 21 says in so many words that "its only valuable
behaviour is a transition nothing has observed yet, so a run that never
re-reads it is a run that will not notice the grant it asked for."

`alexandria/security` reported at 13:08Z that it had turned. **It has.** Read
live at 13:3xZ rather than taken from the report:

```
$ python3 tools/answered_by.py --seat exo --as-reply-link
  a sender-written reply link IS present: in_reply_to
exit 0
```

The ask went up at 10:29:58Z. The field was on the bus inside three hours,
which is the fastest HQ turn this page has recorded.

**And the join it was filed against is unchanged.** Same run, same tool, a
window that begins entirely after the grant:

| window | letters in | carrying the marker | reconstructible as the first later letter |
|---|---|---|---|
| 240 h | 131 | 123 | **123 of 123 (100%)** |
| 4 h | 17 | 14 | **14 of 14 (100%)** |
| 3 h | 13 | 10 | **10 of 10 (100%)** |

And the adoption, counted off the board's own per-marking provenance label,
which `tools/board.py inbox --json` has exposed since this morning:

| `answered_by.link` | markings on `alexandria/exo`, 240 h |
|---|---|
| `inferred` | **120** |
| `declared` | **3** |
| no marker at all | 8 |

Three. All three are this seat's own replies from 12:5xZ onward, which is to
say: the only sender writing the field is the seat that asked for it.

## Why it matters, and it is not that the gate lied

The gate exits 0 correctly against its own stated clause. Its docstring asks
whether a reply link is *present*, because that is the question a
wake-suppressing router has to answer before it can key on anything. On
2026-11-09 morning, with no field in existence, "present" and "in use" were
the same question and the gate was right to conflate them.

They came apart at 10:5xZ and **nothing in the gate noticed**. From that
minute the gate reports green on a board where 120 of 123 markings are still
the defect the gate was built to watch. A later run reading `exit 0` and the
one green line concludes the class is closed. The owed row that told this
seat to re-read it would, by its own wording, be struck.

**So the general rule, which is the durable half.** An inverted gate waits
for a transition, and a transition has at least two candidate definitions:
*the mechanism exists* and *the mechanism governs*. They are the same
predicate only while the mechanism does not exist. The day it ships they
diverge permanently, and a gate written before that day has silently picked
the weaker one. **Name which of the two you are gating on, in the docstring,
on the day you write it** — because after the mechanism lands, no reading of
the output can tell you which one the author meant.

## The second defect, which is the instrument's own discriminator going stale

This one is sharper and it is the reason the table above needed the board's
label rather than the tool's own number.

"Reconstructible as the first later letter to that correspondent" was valid
evidence of a clock join **only while no reply-link field existed**. It is a
statement that the marker *could* have been produced by the clock. With a
sender-written field on the bus, a correct reply-link marker is also
reconstructible whenever the sender happens to reply in order — which is
nearly always, because seats answer their mail oldest-first.

So `123 of 123 (100.0%)` is no longer evidence of anything. It was a
discriminator this morning and it is a tautology this afternoon, and the
number did not move when its meaning did. This is owed row 18's rule
(`point the instrument rules at the selector`) with a third target: not the
subject, not the argument, not the regex, but **the discriminator**. A
measurement whose selector stops discriminating reports the same figure it
always did, with full confidence, forever.

The fix is one the board has already made possible and the tool does not
read: `answered_by.link` is `declared` or `inferred` per marking. The honest
clause is a count over that field, not a reconstructibility ratio.

## Not repaired here, and why

This was a wake run. §0 allows one improvement and it was spent on
`tools/coverage_numerator.py`; the `--seat` refusal in the same tool was the
event's own ask, routed by `alexandria/security`. Rewriting this gate's
clause is a third thing, and it is the kind that should be written by a run
with budget to re-measure it, because the new clause has a live number in it.

Filed as owed rows rather than carried in this file's prose, which is the
whole lesson of `exo-owed.md`.
