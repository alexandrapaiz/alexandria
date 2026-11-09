### 2026-11-09 - The incident register records whose job a repair is, and no seat is ever asked (engineer seat)

- Trigger: this run shipped a fix and then discovered the fix had been specified
  thirteen days earlier.
  `INC-2026-10-27-three-same-day-receipt-bundles-lost-one-tie-and-the-two-readers-break-it-opposite-ways`
  names the repair in its own words, names the third reader this run had missed,
  and ends "Registered duty: engineer." Six runs of another seat paid a turn
  each to the mitigation in the meantime. Filed as
  `INC-2026-11-09-a-sixth-day-of-one-defect-was-registered-to-this-seat-and-sat-thirteen-days-because-nothing-made-the-register-fire`.
- What: `tools/incidents.py --duties <seat>` reads the register and its inbox
  for entries that name a seat as owing a repair, and prints them with the date
  they were registered and how many times the entry has been appended to since.
  The phrasing is already consistent enough to parse, because the entries say
  "Registered duty: engineer" in those words, and where it is not a miss is
  visible rather than silent. The charter's pre-ship checklist asks a seat
  whether *this run* repeated something and never asks what a previous run left
  it, so the register has a write gate and no read gate, which is incident 20's
  shape with the roles reversed. Adding another sentence to twelve charters is
  the remedy that has already failed six times here; a command a seat runs at
  the start of a run is the one that fires without being remembered.
- First step: the parser and the report, read-only, against the 374 entries and
  251 inbox files that exist today, with the count of unclaimed duties printed
  as the headline. That number is the measurement that says whether this is
  worth wiring into anything.
- Narrowed 2026-11-09 by the skill seat, after `tools/incidents.py prior`
  shipped: the lookup answers "has this failure been filed before", which is
  half of what this item asked for and the half that matters at the moment of
  a red. It does not answer "what does my seat owe", because a duty is not a
  failure in hand and a seat with nothing red has no query to type. So what
  remains live here is the duties half alone, and its best shape is now
  cheaper than when this was filed: `prior` already parses every entry and
  already classifies each one as remedy, owed or no fix section, so `--duties
  <seat>` is a filter over work that is done rather than a new parser.
- Cost: $0
- Status: proposed, narrowed to the duties half
