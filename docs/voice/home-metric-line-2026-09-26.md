# The home page's metric line, repaired under canon law 15

Writer run 15, 2026-09-26. One candidate for one surface, drafted here and
set by the frontend seat, per the copy pipeline.

## This is a repair, not a copy round

`docs/voice/value.md` still reads "Status: awaiting her approval", so phase 0
of the copy pipeline is open and a copy round is the wrong work this run.
What follows is narrower than a round and the charter's precondition does not
block it. A line on the home page states something false about alexandria,
canon law 15 is her ruling of 2026-09-25, and the law says in its own words
that it binds every surface and not only the issue. Correcting a false claim
is the law being applied. Reconceiving the page would be the round, and this
draft does not touch a word of the page beyond the sentence that is wrong.

## What is live, and why it is wrong

`site/app/page.jsx` line 49, under the hero:

> **4,243** papers read this week

The number comes from `weeklyIngestCount()` in `site/lib/metrics.js`, which
reads the `papers_ingested` field. That field is `count(*) from papers where
fetched_at > now() - interval '7 days'`, and a row in `papers` is a title and
an abstract. It counts what arrived. The word above it is the act performed
on a far smaller set. Read at 2026-09-26: 8,999 papers held, 4,243 of them in
the last seven days, 174 ever read in full, and 55 read in full this week.

So this is ban list 60 exactly, one count wearing the neighbouring count's
verb, on the first screen a stranger sees. It is also ban list 61, a
reader-facing line that no editorial pass has ever read, because the passes
run on what the model writes and this line is set in a component.

The masthead carrying the same defect was repaired this morning. This one was
not, because the fix was made where the defect was found. That is recorded as
an incident in this pull request.

## The candidate

> **4,243** papers came in this week. **55** were read in full.

The first number is the field the page already fetches, with the verb that
field records. The second is the act the word "read" may name, in the same
seven-day window, which is `count(*) from papers where distilled_at > now() -
interval '7 days'`, which returns 55 today. It is not exposed at
`INGEST_COUNT_URL` yet and the ledger entry in this pull request asks the
engineer seat for it. Both figures above are today's readings, and the page
renders whatever the source returns, never a typed number.

Both numbers together is the shape law 15 names for a scale claim, and it is
the right shape here for the same reason it is right in an issue's close.
Either number alone invites the reader to assume the other. The pair is the
whole truth about the library in eleven words: a lot arrives, a little is
read closely, and the second number is the one doing the work.

Nothing was added to sell it. A line that starts arguing for the ratio is the
next failure in this sequence and not a fix for this one.

**If the second count is not available when this ships**, the line prints the
first sentence alone.

> **4,243** papers came in this week.

That is true, it is cheap, and it says less than the pair does. What it never
does is go back to the reading verb. There is no third option and no
qualifier, per law 15 and the claims pass: cite the count that makes the
sentence true, or say nothing about scale.

## The hero sentence, flagged and not redrafted

Three lines above the metric, the page says:

> Every week the library reads new AI research and tells you what changed.

This one is not clearly false. It attaches no count to the verb, and the
library does read new research, some of it, closely. It is reported here
rather than rewritten because a rewrite of the hero is a copy round, the
value statement it would have to hit is unapproved, and eight rounds on that
surface were rejected. The owner may want it narrowed anyway. That is her
call and it is one sentence away from the ledger entry that would make it
checkable.

## Checked before it left this run

- `docs/voice/taste.md`: plain short sentences, no colon-led construction, no
  cute aside, no mechanism sentence with "it" as its subject. The candidate
  is two short sentences of fact.
- `docs/voice/value.md` and `docs/voice/preferences/site-copy-2026-09-20.md`:
  read in full. The growing, self-maintaining corpus is the part of the value
  statement a line of two counts can carry, and the pair carries the growth
  honestly. None of the five shapes she has refused appears here, and this
  candidate sells nothing, which is correct for a metric line and would be
  wrong for a headline.
- `docs/agents/copy-pipeline.md`: read. This seat drafts, she rules, the
  frontend seat sets. No line of `site/` is touched in this pull request.
