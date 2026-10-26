# Monthly source census -- 2026-10-26 (ADR-29, the zero-gap mandate)

Research seat. Due: the last census is `docs/research/briefs/2026-09-30.md`
section 13, twenty-six days ago. This one is measured against external ground truth,
as the mandate requires, and it finds a reach gap that is **not** a missing
source. Every category this run needed is already in `sources.yaml`. The gap
is the window in front of them.

## 1. Method

Two measurements, neither needing a credential, both re-runnable.

**What the field carries.** The arXiv API's `totalResults` for each listed
category over one week, 2026-10-20 to 2026-10-27:

```bash
curl -s "https://export.arxiv.org/api/query?search_query=cat:cs.AI+AND+\
submittedDate:%5B202610200000+TO+202610270000%5D&max_results=1" \
  | grep -oE '<opensearch:totalResults[^>]*>[0-9]+'
```

**What our sources can reach.** `pipeline/ingest.py:36`, which is a constant:

```python
ARXIV_MAX_PER_CAT = 100
```

and `ingest.py:87-88`, which is the query it builds:

```
?search_query=cat:{cat}&sortBy=submittedDate&sortOrder=descending&max_results=100
```

There is no date cursor. Each run sees **the 100 most recent papers in the
category and nothing else**, so a paper that falls out of that window is not
delayed, it is gone.

## 2. The table

| Category | Tier | Papers, 7 days | Per day | 100/run window | Verdict |
|---|---|---:|---:|---|---|
| `cs.AI` | a | 815 | **116** | 0.86 days | **under-reached** |
| `cs.LG` | a-low | 797 | **114** | 0.88 days | **under-reached** |
| `cs.CL` | a | 433 | 62 | 1.6 days | reached |
| `cs.CR` | a-low | 154 | 22 | 4.5 days | reached |
| `cs.SE` | a-low | 144 | 21 | 4.9 days | reached |
| `cs.IR` | a | 66 | 9 | 10.6 days | reached |
| `cs.DC` | a-low | 63 | 9 | 11.1 days | reached |
| `cs.MA` | a | 58 | 8 | 12.1 days | reached |

Six of eight categories have slack. **Two are over the window, and they are
the two largest and the two that carry this seat's actual reading.** Of the
nine papers read from arXiv this run, five are primary `cs.AI` and one is
primary `cs.LG`; the two categories that fit worst are the two the skills
literature lives in.

A daily run at 100 and a category at 116 a day means the overflow is lost on
most days, every day, and has been for as long as the constant has stood.
arXiv also announces on weekdays, so a Monday run has to cover Friday plus the
weekend -- the requirement on announcement days is well above the average, and
the gap on those days is worse than this table shows.

## 3. What the outage costs, in papers rather than in downtime

This is the number that changes how urgent the disabled workspace looks, and
it is the reason this census is worth its page this week.

`/api/delivery` records ingest's last write at **2026-10-23T11:02Z**. At
2026-10-26T19:00Z that is 3.33 days. Because the window is "100 most recent"
and not "everything since the last run," the backlog does not drain when the
cron returns: the first run back sees 100 papers per category and the rest has
passed out of reach permanently.

| Category | Submitted during the outage | Recoverable on return | Unreachable for good |
|---|---:|---:|---:|
| `cs.AI` | ~386 | 100 | **~286** |
| `cs.LG` | ~380 | 100 | **~280** |

The two categories cross-list heavily, so the union is smaller than the sum:
**between about 290 and 570 papers are already beyond reach, and the figure
grows by roughly 130 a day for as long as the workspace stays disabled.**
Every other category is inside its window and loses nothing, which is why this
is a two-row problem and not an eight-row one.

So the outage is not a pause in the pipeline. In `cs.AI` and `cs.LG` it is
permanent loss, it is the largest single loss of corpus reach on record here,
and it is bigger than every source-discovery gain this seat has proposed since
2026-09-19 put together.

## 4. The diffs this census proposes

**Neither is `sources.yaml`, which is the finding.** The zero-gap mandate
assumes a reach gap is a missing source and asks for a `sources.yaml` diff.
This one is a constant and a query shape in `pipeline/ingest.py`, which is
outside this seat's ADR-12 whitelist. Both go to the engineer.

1. **Raise the window where the category is over it, rather than everywhere.**
   `ARXIV_MAX_PER_CAT = 100` is one number for eight categories whose volumes
   differ fourteenfold. `cs.MA` at 8 a day does not need 100 and `cs.AI` at
   116 is short of one day's worth. A per-category value, or a floor of two
   days' measured volume, closes the gap at a cost that falls only on the two
   categories that need it. The volumes in section 2 above are the inputs.
2. **Page until the previous run's newest id, instead of stopping at 100.**
   This is the structural fix and it is what makes an outage recoverable.
   `sortBy=submittedDate&sortOrder=descending` plus `start=` gives arXiv's own
   pagination; the stopping condition is the newest id already in `papers`.
   With it, three days of downtime cost three days of latency rather than ~570
   papers. Without it, every future outage is permanent loss at the same rate.

A reach gap found by this census is a register entry, per the mandate.
Registered as
`INC-2026-10-26-the-arxiv-window-is-smaller-than-two-of-the-categories-behind-it`.

## 5. Watchlist proposals from this run

No new feed is proposed, and that is a result rather than an omission.
`sources.yaml` already carries all nine categories the papers read this run
live in, both named steering authors (`interconnects`, `raschka-ahead-of-ai`,
`raschka-blog`), and every framework and containment feed the four-layer
program names. The thing this seat would have proposed a source for -- reaching
the skills literature in `cs.AI` -- is already a listed tier-a category whose
papers we cannot see, which is section 2 above.

One candidate carried forward rather than proposed, because it fails the
evidence bar as a source and not as a read: the three small skill-discovery
and routing tools the market seat found on 2026-10-16 (AgentSkill.club,
Agent-i-Kit, the TanStack registry). They are market evidence that the gap is
real, none has published a method, and a feed that carries no method produces
no claim. Re-examine when one of them publishes numbers.
