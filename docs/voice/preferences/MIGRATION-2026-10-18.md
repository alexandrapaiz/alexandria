# The migration record, 2026-10-18

`docs/agents/preference-data.md` specified this directory's schema on
2026-09-21 and said of the file that already existed: "Migrating the 2026-09-20
file: worth doing and not worth faking." This page is that migration, and it is
the first data ever written against that schema.

`docs/voice/preferences/site-copy-2026-09-20.md` is unchanged, because the
schema says it stays exactly as it is: it is that session's human companion and
it is also the evidence for the copy-pipeline incident of 2026-09-20.

## What converted

29 rows in `site-copy-2026-09-20.jsonl`. 16 rejected, 3 approved, 10
`no_ruling`.

The schema predicted "sixteen of the 22 rejected rows and all 4 approved lines
convert cleanly" and "five rows convert with `no_ruling`". The rejected count
matches exactly. The other two do not, and both differences are decisions
rather than slips.

**Three approved rows, not four.** The fourth is the skills heading "Research
your agents can use.", which the source file records under "Leaning (not
final)" with her correction attached: "not just research. its the literal
frontier." A leaning that drew a correction is not an approval. Schema rule 2
says no verdict, no label, and rule 3 says never promote an inference to a
ruling, so it is `no_ruling` with her correction in `reason_verbatim`, where a
consumer can read it and no training set will treat it as an accept.

**Ten `no_ruling` rows, not five.** The extra five are candidates whose text
survives in full but whose verdict does not: three round-four skills headings
and two round-seven candidates the source marks "implicit no". They are rows
rather than omissions because their text is complete, and they are `no_ruling`
rather than rejected for the same two rules. What was shown and not ruled on is
real history, and the `verdict` field alone keeps it out of any training set.

## What did not convert, and is gone

Schema rule on `text`: a candidate that cannot be quoted in full is not
recorded, and its absence is noted here.

- **The writer's seven-paragraph mission page draft, round one.** The source
  records it only by description. Her verdict on it was "no".
- **Round four's home candidates.** Recorded only as "smoothed 'frontier moves
  every day' variants". Her verdict was "i hate the tone".
- **Round four's three library candidates.** Recorded as three fragments ending
  in ellipses.
- **Round three's two skills intro candidates.** Same, two fragments.
- **Round five's home A/B/C and library A/B.** Recorded only by slot name.
- **Round seven's library candidate.** One fragment ending in an ellipsis.
- **The reworked home opener of round three.** This one is the worst of the
  list, because it drew a verdict in her own words, "i hate the tone. The
  frontier moves every day,. i dont like it.", and the sentence that drew it was
  never written down. A reason with no candidate teaches nothing.

That is eleven candidates and three of her verdicts with no text under them.
None of it is recoverable, and this list is the honest form of that.

## Two places the record is less verbatim than it claims

Both are in the source file and neither is repaired here, because repairing
either would mean inventing her words.

1. **One reason carries an elision.** Round one's home line 2 is recorded as
   "avoid sentence structures with lots of commas ... uneeded. i prefer plain
   short sentences." The ellipsis is the original recorder's. The row keeps it
   verbatim as recorded, including her spelling of "uneeded", and the schema's
   no-ellipsis rule binds `text` rather than `reason_verbatim`.
2. **One verdict is a question.** Round five's is "can you tell theres a bit of
   a marketing tone?" The source read it as a rejection and the reading is
   defensible, but it is the recorder's rather than hers, so those rows are
   `no_ruling` with the question kept whole.

## The `author` field, which is the one the ExO audits

The schema says this field "makes the process measurable, because a session
where every candidate's author is `chair` is the failure incident 25 records",
so a guess here is worse than a disclosure.

Every 2026-09-20 row is `author: "chair"`. The evidence is the schema's own
worked example, which is a real round-eight candidate from this session and
assigns it `"chair"`, together with the taste ruling of 2026-09-20 that ends
"The chair stops drafting copy live; the writer seat drafts".

**One row contradicts that and is not in the file.** `docs/voice/taste.md`
attributes the round-one mission page draft to the writer. Its text was never
recorded so it is not a row, which means the one candidate in the session known
to have a different author is also the one the dataset cannot hold. Round one
may have been the writer's batch throughout; nothing on the record says so, and
nothing here claims it.

`recorded_by` is `writer` on every row in both files, which is true and is the
point: the schema gives recording to the chair, in the session, as it happens.
These rows were written 28 days later by the seat the schema names as the
consumer.

## What the finished dataset is worth

32 rows across two sessions and six derivable pairs. The per-slot table is in
`2026-09-29-site-copy.md`, and the short version is that the three slots she
rejected most often are the three with no approved row in them.

The dataset is now machine-consumable, which is what the schema asked for and
is a real improvement over prose. It is not yet useful for learning her taste,
and the reason is not the schema. It is that 32 rows exist for two sessions and
one of those sessions was reconstructed from rules, nine days after a page was
written specifically to stop that. Filed as an incident in this pull request.
