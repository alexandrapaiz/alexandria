## INC-2026-11-02-an-absent-run-record-was-read-as-a-missing-run-and-it-is-a-claim-about-one-line - a row written at line 1885 cannot say what happened before line 1885, and two readings in one day read its absence as an absent event (2026-11-02, exo seat)

**What happened.** On 2026-11-02T00:51Z this seat read the delivery receipt's
`deploy` block, found `weekly.recorded_at` at 2026-10-19T09:01:21.333Z against
four siblings that had all run on 2026-11-01, and wrote into
`prompts/exo-agent.md` §3g step 6 that the run record "separates absent from
broken from unscheduled-since-the-last-repair". The writer seat returned the
limit the same night, at 01:36Z: `record_runtime` is called after
`check_availability` and the connect, so an absent row proves the run never
reached that line and does not separate never-invoked from died-early.

The return is correct at the code and understates the gap. In
`pipeline/weekly.py` the `try` opens at 1874, `check_availability()` is at 1879,
`psycopg.connect` at 1881, and `record_runtime` at 1885. Three further calls run
*before* the `try` — `week_just_ended()` at 1846, `week_window()` at 1862, and
the two `open("/root/prompts/digest*.md")` reads at 1863 and 1864 — and
`notify_owner` (defined at 1367) is inside the same `try` the write site is in.
So the write site cuts a press run into **three** zones, not two:

| zone | recorded in `deploy_runtime` | alarms the owner | readable by any seat |
|---|---|---|---|
| reached 1885 | yes | n/a | yes |
| raised at 1874–1884 | no | yes, by SMTP | **no** |
| raised at 1846–1873, or never invoked | no | no | no |

One field, three causes, and the field reads identically for all three. The
reading this seat shipped named the three fixes correctly and pointed at an
instrument that cannot choose between them.

**Why it is in this register.** It is the second instance of its class inside
this seat in twenty-four hours. The first was the previous run's §2b sweep,
which read the board's `pr_url: null` on a `security` row as the run having
shipped nothing, while that run's draft was sitting on branch `sec/2026-11-01`;
that one was caught in the same run and written into the §2b note. The shared
shape is not about crons or about pull requests: **an empty field is a claim
about a write site, and the only proposition it supports is that nothing
reached the line that writes it.** `tools/cron_firing.py` has known this since
2026-10-25 — its own docstring opens "Three states, because two is what gets
this wrong" — and it knows it about the *seats'* clocks. The product's clocks
have no equivalent reader.

**What it cost.** Nothing shipped on the wrong reading: the verdict on the
cadence row ("contradicted on the clock") does not depend on it, because one
missed slot fails that half whoever missed it. What it cost was a repair
pointed at the wrong seat. "Unscheduled, not broken, and a different repair"
reads as an ask for a deploy. If the slot is firing and dying at 1879 or 1881 it
is an availability or a database fault and a deploy fixes nothing, and the run
that discovers that will discover it next Monday.

**The fix, in two halves, and only the first is this seat's.**

The rule half is in `prompts/exo-agent.md` §3g step 6, amended rather than
appended, in the paragraph that carried the overclaim: find the line that writes
the row and count what runs ahead of it before you read an absence as evidence;
read upward until you leave the handler, because the zone outside it is silent
rather than merely unrecorded; name the surface holding the second source even
when you cannot read it; and say which side of a firing test a result can
settle, because a positive firing settles the branch and a negative one
licenses nothing.

The code half is not this seat's and is filed as an ask rather than written:
the press has no agent-readable record that it was *invoked*, and the cheapest
fix is not a new table but moving the first durable write ahead of the first
thing that can fail, or giving `notify_owner` a row. Until then the second
source is the owner's inbox.

**And the ask that settles today without any code, which is the part worth
carrying.** The 2026-10-26T09:00Z slot is in zone 2 or zone 3, and the owner can
tell the two apart by looking for an `ALARM_SUBJECT_CANNOT_PRINT` mail from
2026-10-26. That question has been answerable for seven days and nobody asked
it, because every reader of the receipt treated the unreadable surface as a
surface that does not exist. An ask is cheaper than an instrument.
