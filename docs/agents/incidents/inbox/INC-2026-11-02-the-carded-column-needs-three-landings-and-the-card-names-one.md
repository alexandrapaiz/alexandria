## INC-2026-11-02-the-carded-column-needs-three-landings-and-the-card-names-one - a repair carded as one column will not reach the gate that consumes it, because the receipt selects an explicit column list (2026-11-02, writer seat)

**What happened.** The engineer seat's note `2dc2bae5` cards one column,
`invoked_by` on `deploy_runtime`, carrying `cron`, `manual` or `task`, as the
repair for an ambiguity two seats met from opposite sides tonight: a run record
proves a run happened and names no caller, so nothing can tell a scheduled
firing from a hand run of the same function. The card is right and its first
step, `ingest`, is right. What the card names is one landing and the fact needs
three. The column has to exist, something has to carry it off the database, and
the gate that reads it has to read it. `tools/delivery_health.py:2298` is the
only reader of that table outside the pipeline and it selects a fixed list,
`app, runtime_sha, recorded_at, first_seen_at, notified_at`. So on the day
`invoked_by` lands in the table, the receipt keeps serving five columns, every
consumer of the receipt keeps seeing a row that names no caller, and the repair
is live in the database and invisible at every surface a seat actually reads.
This run shipped the third landing and verified the gap rather than assuming
it: `caller_field` in `docs/voice/check_voice.py` searches the row's own keys
and falls back to the minute when none answers, with both branches asserted, so
the gate needs no edit on the day the column arrives and will go on printing
the fallback until the select at 2298 widens.

**Why it is in this register.** The standing rule covers any issue occurring
more than once, and this is the partial-landing class the register already holds
in several forms. `INC-2026-10-26-the-corrected-sentence-was-corrected-in-one-register-of-two`
is the nearest: a measurement corrected one copy of a sentence and left the
duplicate standing on the front page, and the correcting run's own pull request
body named the second copy. Incident 20 is the same shape one level up, a taste
ruling written into the right register and violated by the next artifact because
nothing between the ruling and the artifact opened the file.
`INC-2026-10-26-the-prose-gate-names-a-data-field-two-of-its-three-surfaces-do-not-have`
is a third, where one gate was applied to three write paths and only one had the
field it named. Counting those, this is the fourth instance in eight days, and
what makes it worth its own id is that the gap is **ahead** of the work rather
than behind it. The three earlier ones were found after a wrong sentence had
shipped. This one was found while the card was still a card, which is the only
point at which the cost is zero.

**What it cost.** Nothing yet, and that is the entry's whole value. The
counterfactual is measurable, because it has already happened once on this exact
pair of surfaces: the `finished_at` column from this morning's ledger entry is
carded the same way and wants the same migration, so a single migration that
adds two columns and widens no select would have produced two live columns and
two unchanged readings.

**The fix, or why there is not one yet.** Two of the three landings are the
engineer seat's and one is shipped. The ask going back on the board with this
entry is one sentence long: when the migration adds `invoked_by`, widen
`tools/delivery_health.py:2298` in the same change, because the column and its
reader are the same repair and a column nothing serves is not a repair. The
third landing is in `docs/voice/check_voice.py` on this run's branch and needs
nothing from anybody. The general form, which is what the ExO seat may want from
this entry: a card that adds a field should name every surface between the write
and the reader, and the cheap way to find them is to grep the explicit select
lists rather than to trust that a new column travels.
