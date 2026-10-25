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

| Surface | Candidate | Drafted | Is the defective line still live? |
|---|---|---|---|
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

| Question | Where it is argued | Asked |
|---|---|---|
| Are the skill files the paid product, or the free distribution that sells something else? The repository is public and all nine are in it, so the entitlement gate guards a door in a wall with no other sides | `skills-copy-2026-10-18.md`, surface 3 | 2026-10-18 |
| Does a paid tier keep a bullet for a machine that does not exist, hedged, or lose the bullet? | `claim-repairs-2026-10-18.md`, finding 8 | 2026-10-18 |
| Is `docs/voice/value.md` the target still owed an approval, or stale against the five pages she approved on 2026-09-29? | `value.md`, the note of 2026-09-30 | 2026-09-30 |

## Closed

| Surface | Candidate | How it closed |
|---|---|---|
| Home, library, skills, graph, mission | `site-copy-2026-09-19.md` and the rounds after it | Superseded by her approvals of 2026-09-29, "good. i like this.", recorded in `docs/voice/taste.md`. The live pages are the positive examples |
| `site/content/issues/2026-W39.md`, line 3 | `archive-masthead-2026-10-23.md` | Set, and on `main`. Verified by writer run 49: line 3 of the file on `origin/main` matches the `MASTHEAD` constant in `pipeline/weekly.py` character for character, and `check_voice.py reading` no longer reports the archive. The open row said moving it was this seat's call, so this is that call |

## What this file is honestly worth

It is a register, and the lesson this seat keeps writing down is that recording
is not enforcing. Nothing fires when a row here goes stale. Two of the nine
statuses above are checkable by command today, because
`docs/voice/check_voice.py claims` and `check_voice.py reading` read the live
surfaces, and the rest are a seat's reading of a page on a date.

So the duty is the smallest one that could work: a writer run opens this file,
and a candidate for a surface already listed here either builds on that
candidate or says why it supersedes it. The alternative is what happened on
2026-10-18, which is three candidates for two surfaces in one day and no way
for any of them to know about the others, and then a fourth candidate four
runs after this file was written to prevent exactly that. The duty is now a
command over the run's own diff, which is the only version of it that has ever
held. What is still a seat's reading on a date is the last column.
