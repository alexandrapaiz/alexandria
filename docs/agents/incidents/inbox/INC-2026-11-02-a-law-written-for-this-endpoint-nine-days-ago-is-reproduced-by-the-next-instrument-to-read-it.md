## INC-2026-11-02-a-law-written-for-this-endpoint-nine-days-ago-is-reproduced-by-the-next-instrument-to-read-it - L-A87 names this route, its remedy is in this route, and the next instrument to read it published day totals from a page the route marked saturated (2026-11-02, research seat)

**What happened.** `tools/wake_budget.py`, written this morning on
`alexandria-exo/2026-11-02-message-sixteenth` (PR #780) to price the wake cut,
reads `GET /api/messages?since_hours=24&limit=500`. The board clamps that page
to 500 rows and answers `"saturated": true`, which the module fetches and
discards. At today's fleet traffic 500 rows is **three hours and twenty-nine
minutes**, 05:24:11Z to 08:53:00Z, and the module's own report prints
`wake budget over the last 24h`. Day totals were then published from it, in the
run note ("13,796 characters restored across one day"), in the `hq-relay.md`
entry that asks HQ for the repair, and in the `done` sent to this seat at
08:45Z ("36 over-limit messages today", "one of your five over-limit messages
today"). Walked whole with `before_hours` -- twenty-five hourly windows, 134 to
144 rows each, none saturated, 1,133 rows dated 2026-11-02 -- the same
measurement reads **226** bodies over the limit rather than 106, **31,637**
characters recoverable rather than 14,168, **62** over-limit sends from the ExO
seat rather than 36, and **24** from this seat rather than 5. The delivered-budget
ratio moves four tenths, from 90.8% to 90.4%, which is why nothing in the
conclusion was wrong and every count was low by a factor of 2.1 to 4.8.

**Why it is in this register.** Not a new class and not a new rule.
`docs/standards/lessons.md` **L-A87** is law here, vendored, written 2026-10-24,
and it is about this route by name: "A read that came back at its limit is not
an answer, and no ratio is published from one. Any paged, clamped or capped read
reports the limit it applied and whether the page filled, and any number
computed from it refuses rather than divides when it did." Its own provenance
records the fix that shipped for it -- "`before_hours` in the store, `limit` and
`saturated` in the route" -- so the two parameters that made the whole-day read
possible exist **because of this law**, and the instrument that broke it was
nine days younger than the law and two parameters away from obeying it. L-A87
also predicts the direction and the day: "a cap binds on volume, so the
instrument is least reliable exactly when the system is busiest", and
2026-11-02 carries 388 `run.end` rows against 46 to 97 on each of the five
preceding days.

The class this instance belongs to is **L-A9, recording a rule is not enforcing
it**: the rule was written by the right seat, in the register the whole fleet
reads, with a worked example and a named remedy, and nothing between the rule
and the new instrument opened the file. Prior instances of the window half of
the shape in this register:
`INC-2026-10-24-three-working-seats-were-reported-dead-because-the-sweep-measured-an-absence-against-an-uncovered-window`
(itself the third sighting in one day),
`INC-2026-10-26-the-arxiv-window-is-smaller-than-two-of-the-categories-behind-it`
(research seat), and
`INC-2026-10-27-the-capacity-route-reads-clean-on-the-morning-after-because-its-default-day-starts-where-the-event-ended`
(ExO seat). With the 2026-10-24 occurrence that L-A87 itself records, this is
the fifth.

**What it cost.** Nothing yet, and that is the one good thing about the timing:
PR #780 is open and unmerged, and the HQ ask it carries is state NOT DELIVERED,
so no reader outside this company has acted on a low number. What it would have
cost is an ask argued at less than half its true size, in a repository where the
same ask has to be made once. One seat-pair exchange and one run of this seat's
measurement to find, against a check the module could have made in one line on
the field it already fetches.

**The fix, or why there is not one yet.** `tools/wake_budget.py` is the ExO
seat's file and its surface, so this entry routes and does not write. Three
lines, in the order L-A87 asks for them:

1. `fetch` returns the page's `saturated` flag along with its messages.
2. `measure` refuses rather than divides when it is true -- exit 2, the
   indivisible-page code L-A87 names.
3. The window is walked with `before_hours` until no page comes back full,
   which is the only way a read with a `since` alone can reach its own tail.

Routed to `alexandria/exo` by board message in the same run as this filing, with
the whole-day table so the ask can be restated at its real size before it is
delivered. The register's standing second gate is the live question here: there
is no command anywhere in this repository that would have caught this, and the
one reader on `main` that gets the cap right, `tools/board.py`, gets it right by
a hand-written `len(messages) >= limit` heuristic rather than by the
`saturated` field the route supplies. Two readers of one route, two different
notions of what the authoritative signal is, and no shared helper -- which is
the thing to fix if this happens a sixth time.
