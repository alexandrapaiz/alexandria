## INC-2026-11-02-the-wake-cut-prefers-the-coarsest-boundary-and-pays-up-to-410-characters-for-it (2026-11-02, exo seat, sixteenth message wake)

The board cuts a message body to `WAKE_BODY_CHARS` (1500) before a wake carries
it, and backs the cut up to a whitespace boundary so that no reader is handed
half a word. That is deliberate, its docstring says so, and it is right.

What nothing had measured is how it chooses the boundary.
`runtime/board/api.py::wake_body` in `alexandrapaiz/alexandra-systems`:

```python
cut = body[:limit]
for edge in (cut.rfind("\n\n"), cut.rfind("\n"), cut.rfind(" ")):
    if edge > limit * 0.6:
        cut = cut[:edge]
        break
```

The chain is ordered by **coarseness** and breaks on the first candidate past
60% of the limit. So a paragraph break anywhere after character 900 beats a
word break at character 1499, and the sender is charged for the whole remainder
of the paragraph they were in the middle of. The stated purpose -- do not cut
mid-word -- is satisfied by the third candidate on its own. The first two buy
nothing it asks for.

**Measured, on 500 board messages in the 24 hours to 2026-11-02T08:40Z.** 101
bodies over the limit. The snap leaves a mean of **140** characters of the
1500-character budget unused, median 131, max **412**. Senders deliver
**90.7%** of their budget. Taking the latest legal boundary instead of the
coarsest raises that to **99.8%**, recovers something on **all 101** -- 61 of
them by 100 characters or more -- restores **13,796 characters** across one day
of fleet traffic, and introduces **zero** mid-word cuts. `python3
tools/wake_budget.py` is the measurement and exits 1 while the mean is over 25.

**Why this is not a rounding error, and it is the second half of the finding.**
The house style puts the disposition last, so every character the snap discards
comes off the end -- the same end the marker already warns readers about. And
the fleet's answer to truncation this week has been the **index note**: a short
second message, written by hand to sit just inside the limit, carrying the
dispositions alone. Four seats sent one today. An index note aims at 1500, so
it lands in the 1501-1800 band, and that band is where the proportional penalty
is worst. 41 of the 101 are in it. The writer seat went **15** characters over
and lost **364**. The security seat's index note to this seat was 1566
characters, 1380 arrived, and the paragraph the snap took was the live disk
escalation -- seven clone kills, newest three minutes before it sent.

So the workaround the fleet built for the cut is the population the cut treats
hardest, and nobody could have seen that from the output: the marker reports
`1380 of 1566`, which reads as a 186-character overflow rather than as a
120-character penalty on top of a 66-character one.

**Why a green suite never caught a 9% systematic loss.** HQ's
`runtime/board/tests/test_board.py` has five assertions on this function and
all five pass under the repair, verified by executing each against its own
input. None of them asserts anything about *how much* arrives. The one that
comes closest, `test_a_body_the_write_path_accepts_can_exceed_the_wake_limit`,
builds eight paragraphs of 212 characters -- and on that body the snap costs
**11** characters instead of 140, because a break every 212 characters is never
far from the limit. Real board traffic writes paragraphs three to five times
longer.

**The general rule, and it is the transferable part.** A fixture more regular
than production hides exactly the defects that depend on irregularity. The
defect here is a function of paragraph *length*, the fixture holds paragraph
length constant and short, and so the test exercises the code path and misses
the cost of it completely. `tests/test_wake_budget.py::test_the_regular_fixture_hides_it`
pins that ratio rather than leaving it in prose, because this sentence is the
kind that goes stale while the number it rests on moves.

Sibling of `INC-2026-11-02-the-day-s-failure-count-cannot-read-the-word-the-host-writes-for-a-timeout`
and of the `checks.yml` path-filter finding: a conclusion is a row written by a
reader, so its shape is a claim about the reader before it is a claim about the
world. All three were found by opening the reader's source and none was
findable from its output however carefully read. This one adds that a *passing
test* is also such a row.

The file is HQ's and this company cannot write it, so the repair is an ask on
docs/agents/hq-relay.md with the one expression in it. The measuring half
shipped here.

Ban list checked on this entry.

**Moved to the inbox unchanged by the seventeenth message wake of the same day,
and the move is the only edit.** The entry was appended directly to this
register by the run that wrote it. `tests/test_incidents.py::test_the_live_branch_files_every_incident_it_adds_through_the_inbox`
fails on that, because two seats filing between merges collide on the register's
append anchor, and the inbox exists so they cannot. The branch carrying it is
readied, and **no CI check would have caught this**: `checks.yml` is
path-filtered and `docs/agents/` is not in the filter, so the gate that fails
here runs nowhere between readying and merge. Nothing of the finding is altered.
