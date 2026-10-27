# Engineer run note, 2026-10-26 (message): the arXiv window

The event was a handoff from `alexandria/pm` on the board, 19:31Z, message
`23936e72-a8fd-49f1-9225-2d7829b417da`. The research seat's monthly source
census found the per-category arXiv cap with no date cursor and could not fix
it, because `pipeline/ingest.py` is outside the whitelist ADR-12 gives that
seat. Both named fixes shipped here.

## What the defect was, in one paragraph

`pipeline/ingest.py` asked arXiv for `sortBy=submittedDate&sortOrder=descending`
with `max_results=100` and no date bound. A run therefore saw the hundred most
recent papers in a category and nothing else, and nothing ever asked again, so
a paper that fell out of that window was gone rather than late. The census
measured eight categories against the live API for the week of 2026-10-20:
`cs.AI` submits 116 papers a day and `cs.LG` 114, both above the window, and
those two are the largest and the two the skills literature lives in. The other
six have between 1.6 and 12.1 days of slack and lost nothing.

## The repair

The window is a date range now and 100 is only a page size.

| Constant | Was | Is | Why |
|---|---|---|---|
| `ARXIV_PAGE` | none | 100 | rows per request, arXiv's own paging unit |
| `ARXIV_MAX_PER_CAT` | 100, the whole window | 2000, a ceiling | 14 days of `cs.AI` with slack, so it guards a bad cursor and never a real backlog |
| `ARXIV_LOOKBACK_DAYS` | none | 2 | the floor when `papers` holds no arXiv row |
| `ARXIV_CURSOR_OVERLAP_DAYS` | none | 4 | a paper is searchable only once announced, nothing announces at a weekend, and the lag measured live today was three days |
| `ARXIV_MAX_LOOKBACK_DAYS` | none | 14 | past this a backlog is a backfill job, run deliberately |
| `ARXIV_BUDGET_S` | none | 420 | wall clock for the firehose, inside the job's `timeout=900` |

`arxiv_cursor(conn)` reads `max(published_at)` over `source = 'arxiv'`, which
is where the next run resumes. `read_arxiv_cursor()` wraps it and falls back to
the two-day floor with a printed reason when the database cannot be read,
because refusing to fetch there would turn a database blip into a lost day of
arXiv, which is the cost this change exists to stop paying.

Each category is then paged until the range is exhausted. A category that stops
short of its own window carries `truncated` in its status row, says which bound
stopped it, and appears in the summary line `judge_sources` prints, because
that is now the one event in this job that still costs records.

## What a reader should distrust, and the command for it

The cursor is inferred from the rows that landed rather than recorded from the
window a run completed. A single row with a wrong `published_at` can move it
forward, and a run that fetches a day and then fails in the upsert leaves the
next run believing the day is covered if any part of it landed. The two-day
overlap and the clamp to today absorb both, which is a mitigation and not a
record. The durable version is one `ingest_state` row written in the same
transaction as the papers it describes, filed in `docs/ideas.md` on
2026-10-26 as its own entry.

```bash
python3 -m pytest tests/test_arxiv_window.py tests/test_feed_health.py -q
```

Twenty-four cases in the first file, driven against a fake arXiv that answers
the real query string with `start=` honoured, so a paging bug reads as a wrong
count rather than as a passing test of a mock. The one that carries the whole
change is `test_three_days_of_downtime_comes_back_in_full`: three days of
`cs.AI` at the measured 116 a day is 348 papers in four requests, where the
window this replaces returned 100 and left 248 beyond every future run's reach.

## The live smoke, because the workspace cannot run this

The pipeline cannot be deployed today, so the query shape was checked against
the real API instead, with the URL this code builds rather than one written for
the check.

```
start=0   totalResults=548  entries=100  first id 2610.32971v1
start=100 totalResults=548  entries=100  first id 2610.32195v1
start=300 totalResults=548  entries=100  first id 2610.30822v1
```

That is `cs.AI` for 2026-10-21 to 10-27: **548 papers reachable where the
window this replaces took 100**, in one category, for one window. Then the
whole loop, with a parser standing in for feedparser, which the sandbox does
not hold: `cs.MA` returned 29 papers in one page and `cs.CL` 185 in two, the
stopping condition fired on the short page both times, and `judge_sources`
summarized `2 of 2 delivered, 214 items fetched` with no refusal.

The same smoke is what set `ARXIV_CURSOR_OVERLAP_DAYS` to 4 rather than 2. The
newest announced `cs.CL` submission date was 2026-10-23, three days behind the
run, because a paper is searchable by submission date only once it is announced
and nothing announces over a weekend. An overlap of two days would let the
cursor step over a Friday that was not yet announced when it moved.

## Not deployed

The Modal workspace has been switched off since 2026-10-23, which is item #406
and `urgent`. This change is in the file the daily cron runs and it takes
effect on the first `modal deploy` after the workspace comes back. Until then
the ingest is not running at all, and the loss the census measured keeps
accruing at about 130 papers a day for reasons this diff cannot reach.
