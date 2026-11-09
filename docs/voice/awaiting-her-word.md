# Awaiting her word

Every copy candidate this seat has drafted and nobody has ruled on, with the
surface it is for and whether the line it replaces is still live.

**Read this before drafting anything.** It is the first file a writer run opens
after the charter, ahead of the taste register, because it answers the one
question the other registers cannot: has this surface already been written for?
On 2026-10-18 the fifth run of the day drafted repairs for the skills page and
the pricing page that the second and fourth runs of the same day had already
drafted, having read every register the charter names. None of them pointed
here, because this file did not exist.

**And that sentence was not enough, four runs later.** The ninth run of
2026-10-18 drafted four candidates for four surfaces, three of which have rows
below, one of them twenty-two days old. It had read seven registers and not
this one, because the charter's shipping step names seven and does not name
this file. So the duty is a command now and not only this paragraph:

```
python3 docs/voice/check_voice.py candidates
```

It reads the open table below against the candidate files a run's own diff
adds, and fails where a new candidate is for a surface already listed here
without naming the candidate already open on it. A run may still supersede a
draft. It may not do so without knowing the draft exists, and naming it is how
it shows that it does.

**A row leaves this file two ways.** She rules on it, in which case the verdict
and her words go into the current file in `docs/voice/preferences/` and the row
moves to the closed list at the bottom. Or the frontend seat sets it and the
live line changes, in which case the row says so with the date. A row nobody
has touched does not quietly expire, which is the whole point: the oldest row
below has been open for twenty-two days and nothing in the org knew that until
a command was written to look.

## Open, newest first

**Re-confirmed 2026-10-23 by command, writer run 42.** Every row below is
still open and every defective line is still live. `check_voice.py reading`
reports the same 4 failures on the same 4 lines as on 2026-10-18, and
`check_voice.py claims` reports 17 unhedged claims live right now. Nothing in
this table has been ruled on or set in five days, and the oldest row is
twenty-seven days old. The re-confirmation is recorded here rather than in the
last column of each row, because what changed is the date and not the reading.

**Widened 2026-10-23 by writer run 44, and the count went up rather than
down.** `reading` was reading 61 surfaces and none of them was the archive, so
it reported 4 failures. It now reads 63 and reports 5. The new row is the top
one and it is the oldest defect in this table by four days, which is the
argument for the row rather than against it: the line has been live for
twenty-eight days and was never drafted, because nothing in the repository
could see it. A table of open rows is only as honest as the scope of the
command that re-confirms it.


**New surface 2026-10-24, writer run 45.** The desk is the eleventh row and
the first one that is not public copy. It is here because the test this table
applies is whether a defective line is live, and the owner's own console is the
surface where a defective line costs the most per reader. Its defect is a
number rather than a sentence, so `check_voice.py ledger` is what re-confirms
it rather than a reading.

**Re-confirmed 2026-10-25 by command, writer run 50, and one number moved the
wrong way.** `check_voice.py reading` now reports 4 failures rather than 5,
and the one that left is the archive masthead in the closed table below, set by
the frontend seat and verified on `main`. So no row above was repaired, one was
completed by another seat, and the rest are untouched at thirty days for the
oldest. `check_voice.py claims` reports 23 unhedged claims live right now
against 17 on 2026-10-23, which is six more than a run that drafted nothing for
these surfaces can account for. The delta is not diagnosed here, because this
run produced no copy and `docs/voice/value.md` still has no recorded approval,
which is the precondition the charter puts ahead of drafting. The same command
reports 9 cited files that no longer carry their claim and 5 drifted line
numbers, and those belong to `docs/agents/quality-claims.md` and its owner
rather than to this table.

**Re-confirmed 2026-10-26 by command, writer run 51, and one number moved
because a gate was repaired rather than because a page changed.**
`check_voice.py reading` reports the same 4 failures on the same 4 lines as on
2026-10-25, so no row below was repaired and the oldest is thirty-one days.
`check_voice.py claims` reports 24 against 23 yesterday, and the one that moved
is this run's own repair: the row for "the library grows every day" has read
`contradicted` since 2026-10-11 and the gate was resolving it to `held`, because
its state cell records what it moved from and `held` was first in the list the
gate searched. So `site/app/page.jsx:33` was printing a sentence the register
calls false while this seat's instrument printed `ok` beside it. That line is
not added to the table below, because the row for that same paragraph is
already open as `claim-repairs-2026-10-18.md` and the charter's precondition
for drafting is unmet: `docs/voice/value.md` still has no recorded approval.
The delta run 50 could not account for is also answered and it was not the
copy. The register went from 11 rows to 13 on 2026-10-24, and the current gate
run against the tree of 2026-10-23 returns 17, so neither the gate nor the
surfaces moved.

**New surface 2026-10-26, writer run 53, and it is the first row here that
arrived as a hand-off rather than as this seat's own finding.** The frontend
seat's shelf audit of 2026-10-24 found the words half of a shelving defect,
left it as a proposal in `docs/ideas.md` because naming a shelf is not its
lane, and the PM relayed it to this seat on the board. So the row below is
owed to two other seats and not only to her. Its candidate carries nine
captions rather than the two the proposal asked for, and the reason is a
count. Not one of the seven captions live on that page contains a finite
verb, and her ruling of 2026-09-29 forbids fragments. The seven predate the
ruling by eleven days and no owner has ruled on one of them.

**Missing row added 2026-10-26, writer run 58, and it was written nine hours
late by the gate that exists to ask for it.** `check_voice.py candidates`
failed a candidate only where the surface it drafted for was already held by
another candidate. A candidate for a surface this register had never held
registered nothing and passed, and the pass line read the same as it reads for
a run that did the bookkeeping right. So run 57 ruled on the live `2026-W42`
page, wrote the exact words, raised one line for her, and reached `main` with
no row anywhere. The regex that reads a surface out of a candidate was widened
on an earlier run precisely so an issue page would be visible here, which fixed
what the gate could see and left untouched what it would say about it. The
floor shipped in this run's diff and the row below is the row it now demands.

**Two rows confirmed against their sources 2026-10-26, writer run 59, and the
clock in one of them became readable.** The PM answered this seat's W42 ruling
on the board at 20:45Z: agreed with the pull, merged it, posted the
correction-notice question to her as a formal ask, and did not dispatch the
frontend seat because that seat's own pull request is still open. Both halves
were read at their sources rather than taken from the note. The ask is board
message `065eda95-92e7-4f94-8625-906c10691b81`, named in the PM's #609, and the
live `2026-W42` page still serves the pulled section, re-read at 21:04Z by
`check_voice.py provenance --live` on the same two findings. What changed in the
rows is therefore the owing rather than the defect: the surface row now says
which seat owes the diff and what it waits behind, and the question row carries
`deadline 2026-10-28T20:44Z` in a fixed form. Run 58 wrote that clock in prose
and prose is the thing no command can read, which is the defect this register
keeps recording about itself. `check_voice.py deadlines` reads the token now and
fails both ways: a row that argues a silence rule and names no deadline, and a
deadline that has passed with the row still open.

**Re-confirmed 2026-10-27 by command, writer run 60, and nothing in this table
moved.** `check_voice.py reading` reports the same 4 failures on the same 4
lines as on 2026-10-26 and `claims` reports the same 24 unhedged claims live
right now, so no row below was repaired and the oldest is thirty-two days.
`provenance --live` re-read the `2026-W42` row's defect at 00:12Z on 2026-10-27
and found the same two findings at lines 47 and 49, which is the fourth live
confirmation and the first one on the day after the ruling. The row's reader
should now expect the live line to outlast the ruling by two days rather than
one, because the frontend seat's #559 is still open. The question row's clock
is unexpired: `deadlines` reads `2026-10-28T20:44Z` against a fixed
`2026-10-27T00:05Z` and says so. This run adds no candidate, because
`docs/voice/value.md` still carries no recorded approval.

**New surface 2026-11-01, writer run 61, and the gate that found it had been
failing on it in silence.** `check_voice.py standalone` fails on the opening
sentence of `2026-W39`, in the repository and on the live page, and canon law
13 quotes the owner rejecting that sentence's near twin by name and then
writes the repair out in full. The row is thirty-eight days old as a defect and
new as a row, because the two commands this register re-confirms itself with
are `reading` and `claims` and neither of them reads an opening. The same run
repaired `standalone --live`, which raised `ValueError` instead of printing the
hit, so a run that pointed it at the product got a traceback rather than the
sentence.

**Re-confirmed 2026-11-02 by command, writer run 62, and the gate that
re-confirms it was looking at the wrong half of the table.** `reading` reports
the same 4 failures on the same 4 lines as on 2026-10-27 and `claims` reports
the same 24 unhedged claims live right now, so no surface row below was
repaired and the oldest is thirty-seven days. `slotheads`, new this run, reports
four framework headings live on the product, three of them on `2026-W40`.

**And the question table had an answer in it for four days and eighteen hours.**
The value-statement question was posted as an ask on 2026-10-26T06:19:51Z, it
expired on 2026-10-28T06:19Z, and under the company standard's silence rule it
has been resolved since. It is in the lower table now with the question kept
verbatim. Nothing in this register knew, and neither did this seat's own
instrument: `check_voice.py deadlines` printed "every clock here is readable and
none of them has run out" over that row on every run since 2026-10-26, because
the row carries no `deadline` token and the gate only failed rows that had one.
That is the same failure the W42 notice row produced on 2026-11-01, one week
apart, and the gate repaired on that day is the gate that could not see this.

**The two rows left have never had a clock at all, which is the finding under
the finding.** The gate's own note said a question with no clock is "the
ordinary shape of this table" because "nine of its ten rows wait on her with no
standard attached". That premise was false when it was written. Section 22 has
been law since 2026-10-16 and covers "every other reservation a charter makes,
in every company", with money, accounts, secrets and a seat's own authority as
the only exceptions. No row here is one of the four. So every row in the lower
table is owed an ask with an hour on it, and two of the three never got one in
fifteen days. Both are routed to the PM this run as board handoff
`9574b0d1-b0d8-4230-877f-a33845886017`, with this seat's recommendation on each,
because section 22 puts the posting in that seat's hands and not in this one's.

**Both question rows have a clock 2026-11-02, writer run 64, and the handoff
that asked for it came back inside eleven minutes.** The PM posted both rows to
her as formal asks at 00:32:58Z and 00:33:05Z, each carrying this seat's own
recommendation rather than that seat's, and told this seat the ids so the cells
could stop saying they were clockless. Both now name their ask and both carry
`deadline 2026-11-04T00:32Z`, so `check_voice.py deadlines` reads two rows,
two readable clocks, two named asks and nothing expired, where on the same
tree an hour earlier it read two `unasked`. The ids were read on the bus at
their source rather than taken from the PM's note, which matters because the
note names neither id against its question and this seat had to pair them: the
asks are addressed to `owner`, so the inbox cannot see them, and the pairing
came from each message's own subject and its data field, which carries the row
it answers. That is the second time a row in this register was confirmed from
the message rather than from a seat's report of it, and it is cheaper than the
two-source reconstruction the value-statement row needed on 2026-11-01, because
this time the ask was six hours old rather than six days.

**Re-confirmed 2026-11-02 by command, writer run 65, and the one number that
moved is the gate's and not a page's.** `reading` reports the same 4 failures on
the same 4 lines as on 2026-10-27, and `claims` reports the same 24 unhedged
claims live right now, so no surface row below was repaired and the oldest is
thirty-seven days. `deadlines` reads both question rows with their clocks
unexpired at 2026-11-04T00:32Z.

**What moved is that two of the register's rows now carry a verdict per half,
and this seat's gate was right about them by accident.** The ExO seat's sweep of
2026-11-02 moved "the library grows every day" to `held on the clock,
contradicted on the record` and the weekly row to `contradicted on the record
and on the clock`. `claim_state` resolves both to `contradicted`, because `held`
never wins a tie, and no case asserted that for a split cell: the resolver was
written for a cell that recounts what it moved FROM, and a cell that names two
halves is a different construction that happens to land in the same branch. Both
live cells are pinned now and a split cell prints as `SPLIT` with the failing
half named rather than as `AMBIGUOUS`. **No row in this table changes state on
it**, because both rows read `contradicted` to the gate before the move and both
do after it, so nothing below became newly unshippable and nothing became
shippable.

**And the clock half is a command now rather than a seat's arithmetic.**
`check_voice.py cadence` enumerates the press's firings from the cron in
`pipeline/weekly.py` and prints the periods that closed beside them. This run
earned it: the note that moved the two rows said two press slots had passed when
one had, because two weeks had ended, and
`INC-2026-11-02-a-cadence-claims-missed-slots-were-counted-as-weeks-that-ended`
is the third instance of that class in nine days. The same command answers the
record half from the served library, and returns 2026-W41 and 2026-W43.

**What it does not do is answer either question.** The clock runs until
2026-11-04T00:32Z and resolving a reservation by silence is the PM's to apply
under the standard, not this seat's. What this seat owes on 2026-11-04 is the
reading, and the row is now the thing that will tell it.

**Both questions were posted to her a second time 2026-11-02, writer run 66,
and recording the new ids as the rows' clocks would have moved them back eight
hours.** The PM posted both reservations as asks at 08:28Z, eight hours after
posting the same two at 00:32:58Z and 00:33:05Z, and told this seat the new ids
with "I will not re-post these; the clock runs from the timestamps above". The
new ids are `46c63f93` and `cbdb86a5`. All four asks are live on the bus and
none was withdrawn, read at the source rather than from the note, which is the
third time a row here was confirmed from the message instead of a seat's report
of it.

The rows keep their first clock and say so in bold. Section 22's forty-eight
hours run from the posting of the reservation, and a second posting of the same
reservation is not a second reservation, so the governing clocks stay
`2cfc0df6` and `8eff5507` at 2026-11-04T00:32Z. The arithmetic is the whole
argument: a reservation re-posted every eight hours would never resolve, and
these two rows have been open for fifteen days.

`check_voice.py deadlines` has a fourth code for it, `duplicated`, and it reads
`expired` against the EARLIEST deadline rather than any of them. The second new
case is the one that makes the code worth having: an earlier clock that has run
out beside a later one that has not, where a row read on its newest id looks
live while the reservation is already resolved. The gate is red on both rows as
this is written and it stays red until one of each pair is withdrawn, because
two live asks for one reservation is an unresolved fact about the bus and not a
bookkeeping slip in this file. Telling the PM is this run's half, and
withdrawing is that seat's.

**How the pairing was made, because neither note did it.** The PM's message
names both ids and neither question against either id, and both new asks
reworded the question rather than quoting it. An ask addressed to `owner` is
neither a broadcast nor addressed here, so the pairing came from each message's
`data` field: the new pair carries `source` and `standard` and no `row`, and
the first pair carries `asked_by: writer handoff` with the row it answers. That
difference is also the evidence that the second posting did not know about the
first.

| Surface | Candidate | Drafted | Is the defective line still live? |
|---|---|---|---|
| `site/content/issues/2026-W39.md:6`, the opening's first sentence | `w39-opening-2026-11-01.md` | 2026-11-01, run 61 | Yes. Thirty-eight days. "You have spent the week watching agents get faster by thinking less at test time." is the shape canon law 13 bans in every tense, and the law's own text holds the replacement verbatim. Read live at 2026-11-01T23:21Z by `check_voice.py standalone --live` and in the repository at the same hour. One sentence, one line, and the ruling carries no notice with it |
| `site/content/issues/2026-W42.md`, the overturn section at lines 43 to 53, the lead's third sentence and the lead's count | `w42-correction-2026-10-26.md`, whose corrected body is `2026-W42-corrected.md` | 2026-10-26, run 57 | Yes. Read live at 20:49Z on 2026-10-26, after the ruling merged: the heading "Hidden reasoning can be encrypted, not merely hidden" still serves, and the research seat scored that section three wrong out of three against the abstracts the issue itself cites. The ruling is to pull the section rather than reword it. Setting it is the frontend seat's diff, and the file does not exist under `site/content/issues/` yet, so the correction lands as a new file that overrides the stored row. Owed to that seat and not dispatched: the PM is holding it until the frontend seat's open #559 clears, said on the board at 20:45Z on 2026-10-26, so the row's reader should expect the live line to outlast the ruling by a day or more |
| `site/lib/skill-shelves.js`, the shelf names and the nine captions | `shelf-names-2026-10-26.md` | 2026-10-26, run 53 | Yes. Four of nine skills stand on the catch-all shelf under a caption written when at most one could land there, and all seven live captions are fragments against her 2026-09-29 ruling. Two shelves do not exist yet |
| `site/app/desk/page.jsx`, the verdict queue | `desk-verdict-queue-2026-10-24.md` | 2026-10-24, run 45 | Yes. The queue renders 524 rows oldest first, so the newest entry on it is the compute outage of 2026-10-23 and a reader reaches it last. The count beside the heading is also wrong by one against `tools/ledger.py --census`, which `check_voice.py ledger` now fails on. Four lines and a one-character anchor, in one diff |
| `site/app/mission/page.jsx`, third paragraph | `claim-repairs-2026-10-18.md` | 2026-10-18, run 40 | Yes. Three unheld claims in one sentence, confirmed by `check_voice.py claims` on 2026-10-18 |
| `site/app/mission/page.jsx`, second paragraph | `claim-repairs-2026-10-18.md` | 2026-10-18, run 40 | Yes. "every finding is linked", contradicted on "every" |
| `site/app/page.jsx`, the paragraph under the hero | `claim-repairs-2026-10-18.md` | 2026-10-18, run 40 | Yes. "replaced when newer work overturns it", which reports rather than replaces |
| `site/app/graph/page.jsx`, the intro | `claim-repairs-2026-10-18.md` | 2026-10-18, run 40 | Yes. The colon-led construction and the universal reading |
| `site/app/terms/page.jsx`, what the service is | `claim-repairs-2026-10-18.md` | 2026-10-18, run 40 | Yes. "The library reads AI research", confirmed by `check_voice.py reading` |
| `site/app/llms.txt/route.js`, the whole body | `llms-txt-2026-10-18.md` | 2026-10-18, run 39 | Yes. Law 15 three times now, two registered claims unhedged, and a launch date five days past. The third instance is the pronoun subject at line 13, which no command saw until `reading` was widened on run 41 |
| `site/app/pricing/page.jsx`, the free column and the intro | `pricing-claims-2026-10-18.md` | 2026-10-18, fourth run | Yes. "The complete archive" over an archive with a hole in it, live for thirty days |
| `site/app/skills/page.jsx` intro, the install block, the nine catalogue rows | `skills-copy-2026-10-18.md` | 2026-10-18, second run | Yes for the intro. The install block is the engineer's surface and moved with PR #339 |
| `site/app/page.jsx:44`, the metric line | `home-metric-line-2026-09-26.md` | 2026-09-26, run 15 | Yes, twenty-two days, confirmed by `check_voice.py reading`. Recorded as an incident the same day this file was created |

## Questions awaiting her word, which no wording can answer

Empty as of 2026-11-09, and the table is gone rather than left standing with
no rows in it. Both questions that stood here moved to the table below when
their clocks were read, so nothing in this register waits on her word today.
That is a fact about the standard's silence rule rather than about her: two
reservations were posted, neither was answered, and section 22 answered both.

A run that needs her word on something new posts it as an ask through the PM,
with the recommendation in the ask's own body, and opens a row here carrying
`deadline <hour>` in the fixed form `check_voice.py deadlines` reads. A row
here with no clock is the shape that let one answer sit unread for four days
and eighteen hours.

**This paragraph governs this table and not the one above it.** A question no
wording can answer belongs here and takes the clock. A copy candidate belongs
in the open table and does not, for the reason the closing section gives: the
silence rule would set lines she never ruled on. Moving a candidate down here
to borrow a clock is the one move this register forbids.

## Resolved on the clock, without her word

A row here was a question for her and is not one any more, because the
standard's silence rule answered it. The row keeps its question verbatim, so
the record shows what was asked rather than only what came of it.

| Question | Resolution | Read at |
|---|---|---|
| Are the skill files the paid product, or the free distribution that sells something else? The repository is public and all nine are in it, so the entitlement gate guards a door in a wall with no other sides | **The free distribution, as recommended.** `docs/standards/pm.md` section 22 proceeds as the PM recommended after forty-eight hours of her silence, and the governing clock on this row was `deadline 2026-11-04T00:32Z` on ask `2cfc0df6`. So the paid product is the maintenance and the nine files in the public repository are the distribution that sells it, which is the recommendation this seat argued in full and the PM took unchanged. It spends no money, opens no account, writes no secret and widens no seat's authority, so it is none of the four section 22 reserves to her regardless of the clock. Applying it is the PM's under that standard and this row is the reading, routed to that seat the hour it was read. What the resolution does NOT decide is what any line of copy now says, which is a drafting run and is not done here. The argument stays at `skills-copy-2026-10-18.md`, surface 3, and the asking history is kept below because the duplicate-ask fact is part of why this clock is the clock | 2026-11-09T00:41Z, writer run 67, by `check_voice.py deadlines`, which went red on both rows. The hour had passed five days earlier and this register still called it a question, which is the one failure that gate exists to produce and the second time it has produced it. What the evidence is: no reply on the card, none in 101 messages of this seat's bus window, and none in any PM pass under `docs/sprints/pending/`. What it is not: this seat cannot read a message addressed to `owner` and cannot read her chat, so this is five days of nothing recorded anywhere this seat can look, which is the same evidence base the two rows above were resolved on. Asking history as it stood: 2026-10-18, and it had a clock fifteen days later. Routed to the PM 2026-11-02 as board handoff `9574b0d1`, posted by that seat to her the same minute as ask `2cfc0df6` at 00:32:58Z, so `deadline 2026-11-04T00:32Z` under the company standard's silence rule. It carries this seat's recommendation unchanged, which is that the files are the free distribution and the paid product is the maintenance, and the PM's own words for taking it are that it had "no basis to substitute my own reading" for a finding already argued in full. Read at the source and not from the note: the message on the bus, whose data field names this row, this recommendation and the same hour. **Re-posted 2026-11-02 as ask `46c63f93` with `deadline 2026-11-04T08:28Z`, and that is not this row's clock.** The PM posted this reservation a second time at 08:28Z, eight hours after the first, and told this seat the new id with "the clock runs from the timestamps above". All four asks are live on the bus and nothing was withdrawn. Section 22's forty-eight hours run from the posting of the reservation and a second posting of the same reservation is not a second reservation, so **the governing clock is `2cfc0df6` at 2026-11-04T00:32Z** and the later id buys no further silence. The newer ask carries `source` and `standard` in its data and no `row`, where the first carries `asked_by: writer handoff` and the row it answers, which is how the two were told apart |
| Does a paid tier keep a bullet for a machine that does not exist, hedged, or lose the bullet? | **The bullet is lost, as recommended.** Section 22 proceeds as the PM recommended after forty-eight hours of her silence, and the governing clock was `deadline 2026-11-04T00:32Z` on ask `8eff5507`. The ground is canon law 15 and the ask's own body gives it: softening leaves a false sentence standing, so a bullet for a machine that does not exist is cut rather than hedged. None of section 22's four reservations applies. Applying it is the PM's and setting the line is the frontend seat's, so this row is the reading and the diff is two other seats'. The argument stays at `claim-repairs-2026-10-18.md`, finding 8 | 2026-11-09T00:41Z, writer run 67, by `check_voice.py deadlines`, which failed this row twice over: once for the expired clock and once for `duplicated`, two live asks for one reservation with the later id buying no further silence. Both halves were already written into the row by run 66 and neither had been acted on. Asking history as it stood: 2026-10-18, and it had a clock fifteen days later. Routed to the PM 2026-11-02 as board handoff `9574b0d1`, posted by that seat to her as ask `8eff5507` at 00:33:05Z, so `deadline 2026-11-04T00:32Z` under the silence rule. The recommendation is this seat's own and unchanged, which is that the bullet is lost rather than hedged, on canon law 15, and the ask's own body gives the ground as softening leaving a false sentence standing. Read on the bus at the source, data field included. **Re-posted 2026-11-02 as ask `cbdb86a5` with `deadline 2026-11-04T08:28Z`, and that is not this row's clock either.** Same duplication as the row above and the same minute, so **the governing clock is `8eff5507` at 2026-11-04T00:32Z**. Both newer asks reworded the question rather than quoting it, which is the second reason the pairing had to be made from the data field and not from the subject |
| Does the corrected `2026-W42` page carry a notice saying a section was removed and why, on that page only? Recommended yes, quoted in full in the candidate, and canon law 7 is the ground it stands on rather than an exception to her ban: that law's first clause asks for a limitation that materially affects the day's content in one plain sentence, and its second bans narrating the method | **Yes, as recommended.** `docs/standards/pm.md` §22 proceeds as the PM recommended after forty-eight hours of her silence, and the clock in the row was `deadline 2026-10-28T20:44Z`. No reply arrived on the card or on the bus. So the notice is settled text and not a proposal: the sentence is the one quoted verbatim in `w42-correction-2026-10-26.md`, the anchor is a new plain-prose paragraph directly under the masthead, and that candidate's sequencing section already decided the form so nobody decides it twice. It moves no authority and no money, which is what §22 reserves to her regardless of the clock | 2026-11-01T23:18Z, writer run 61, by `check_voice.py deadlines`. The hour had passed four days earlier and this register still called it a question, which is the one failure that gate exists to produce |
| Is `docs/voice/value.md` the target still owed an approval, or stale against the five pages she approved on 2026-09-29? | **Stale against the five pages, and the gate is open.** The PM posted this to her as ask `db6d191e` at 2026-10-26T06:19:51Z with its own recommendation in the body, which was to treat the five pages she approved on 2026-09-29 as having cleared it and open the gate, and with the forty-eight-hour line named. The clock was therefore `deadline 2026-10-28T06:19Z`. No reply arrived on the card or on the bus, so under `docs/standards/pm.md` section 22 it proceeds as recommended. Approving a value statement spends no money, opens no account, writes no secret and widens no seat's authority, so it is none of the four section 22 reserves to her regardless of the clock. What this does NOT decide is what the page should now say, which is one run of this seat's ordinary work and is not done here: the status line records that the precondition is cleared and the 2026-09-30 note stays verbatim, because that note is the record of what was asked | 2026-11-02T00:18Z, writer run 62, by `check_voice.py deadlines` once the gate was widened to report a row with no clock. The ask itself was read at two sources on `main` rather than taken from one: `docs/sprints/pending/2026-10-26-0619-message.md`, the PM pass that posted it and quoted its own recommendation, and `docs/sprints/pending/2026-10-26-0906-hook.md`, a later PM pass that verified the message exists on the bus with that id, that recipient and that second. This seat could not read `db6d191e` directly, because an ask addressed to `owner` is neither a broadcast nor addressed here, and 500 messages of this seat's own window held nothing matching |

## Closed

| Surface | Candidate | How it closed |
|---|---|---|
| Home, library, skills, graph, mission | `site-copy-2026-09-19.md` and the rounds after it | Superseded by her approvals of 2026-09-29, "good. i like this.", recorded in `docs/voice/taste.md`. The live pages are the positive examples |
| `site/content/issues/2026-W39.md`, line 3 | `archive-masthead-2026-10-23.md` | Set, and on `main`. Verified by writer run 49: line 3 of the file on `origin/main` matches the `MASTHEAD` constant in `pipeline/weekly.py` character for character, and `check_voice.py reading` no longer reports the archive. The open row said moving it was this seat's call, so this is that call |

## What this file is honestly worth

It is a register, and the lesson this seat keeps writing down is that recording
is not enforcing. Two of the nine statuses above are checkable by command
today, because `docs/voice/check_voice.py claims` and `check_voice.py reading`
read the live surfaces, and the rest are a seat's reading of a page on a date.

**"Nothing fires when a row here goes stale" stood here for fourteen days and
something does now.** `check_voice.py deadlines` read only the questions table
below, on a premise written into its own source: that the rows up here wait on
a seat's diff and so nothing about them expires. That premise is false, and it
was the half holding the whole arrangement up. A row leaves the open table when
she rules or when the frontend seat sets it, and that seat sets APPROVED copy,
so a candidate she has never ruled on is not waiting on anybody's diff. It is
waiting on her.

So the gate read the one table whose every row had been asked, `unasked` was a
code it could produce and never would, and on 2026-11-09 it printed green over
thirteen rows carrying no ask, no clock and no trail between them, the oldest
forty-four days old, four of them red in `reading` that same minute. It reads
both tables now and prints each open row with its age.

**What it does not do is put a clock on them, and that is a ruling rather than
an omission.** The obvious repair is to post each row as a section 22 ask,
which is what the first version of the widened gate told its reader to do. That
is wrong and it is worth stating why, because the advice reads as diligence.
Section 22's ask proceeds as recommended after forty-eight hours of her
silence, so taking it here would set thirteen lines of copy she never ruled on,
on the recommendation of the seat whose last eight unsupervised rounds she
rejected one after another. `docs/agents/copy-pipeline.md` reserves the ruling
to her in terms that leave no room, "Her verdict is the only verdict. This step
is hers and it does not move", and that is a safety clause with evidence under
it rather than a courtesy. `docs/agents/cross-repo-law.md` rule 3 is what
settles it: a local law's preconditions survive a parent override unless the
override names them, and section 22 names none of this.

The open table therefore has no silence rule and will not get one from this
seat. What the rows are owed is to be in front of her with their age attached,
and the age is the thing that was missing for forty-four days.

So the duty is the smallest one that could work: a writer run opens this file,
and a candidate for a surface already listed here either builds on that
candidate or says why it supersedes it. The alternative is what happened on
2026-10-18, which is three candidates for two surfaces in one day and no way
for any of them to know about the others, and then a fourth candidate four
runs after this file was written to prevent exactly that. The duty is now a
command over the run's own diff, which is the only version of it that has ever
held. What is still a seat's reading on a date is the last column.
