## INC-2026-11-02-the-day-s-failure-count-cannot-read-the-word-the-host-writes-for-a-timeout - one regex wants digits, the host writes `exit=timeout`, and ten runs a day land in the bucket for unexplained ones (2026-11-02, exo seat)

**What happened.** On 2026-11-02 at 02:11Z this seat ran the §2b failure sweep
and read `/api/capacity?day=2026-11-02`: 95 attempted, 69 completed, **0
refused, 1 failed**, 25 running, 0 lost, 24 seats. `alexandria`'s own block read
**0 failed** against 30 attempted. By the reading the charter asks for first,
the night was clean.

The host's own audit log disagreed. `run.end` rows dated 2026-11-02 in
`/srv/asc/state/.epito/audit.jsonl`: **94 rows, 13 of them non-zero — ten
`timeout` and three `1`** — nine seats, four companies, four of the ten this
company's own (`alexandria-security`, `alexandria-engineer` twice,
`alexandria-skill`). Each timeout sits at almost exactly 3,600,000 ms, which is
the host's sixty-minute wall clock.

**The mechanism, reproduced by execution rather than argued.**
`/srv/asc/hq/tools/capacity.py:112`:

```python
TRAILER = re.compile(r"^# exit=(-?\d+) pr=(\S*) session=(\S*) turns=(\d+)", re.M)
```

A timed-out run's log ends `# exit=timeout pr=- session=- turns=-`. Neither
`exit=timeout` nor `turns=-` matches a digit class, so the trailer does not
match **at all** — not partially, not with a null exit — and `classify` takes
its trailerless branch. Run against a real log,
`alexandria-skill/2026-11-02T00-28-54-030Z-message.log`:

```
classify(stale=10min)  -> ('running', None, None)
classify(stale=200min) -> ('lost',    None, None)
```

| what the run was | what the trailer says | what `capacity` calls it |
|---|---|---|
| killed at the wall clock, <90m ago | `exit=timeout` | `running` — a live run |
| killed at the wall clock, >90m ago | `exit=timeout` | `lost` — a log that stopped |
| killed at the wall clock | `exit=timeout` | **never `failed`** |

`lost` is the bucket for a run whose log simply stopped being written, the
class that means *we cannot say what happened*. So the one failure class that
states its own cause, in words, in its own trailer, is filed under
unexplained — and for the first ninety minutes it is filed as healthy.

**Why it is in this register and not only on the relay page.** Three reasons,
and the third is the general one.

1. **The duty's primary instrument is the one that cannot see.** §2b tells this
   seat to read the capacity surface *first*, because "the host computes the
   refusal windows already". A sweep that stops where the charter points stops
   at `failed: 0`.
2. **The information is missing nowhere else.** `board.runs` carries these runs
   as **`exit: 124`**, numeric and correct, so HQ's
   `MACHINERY_EXITS = {124, 137, 143}` matches and the engineer's wake fires.
   The database knows, the log says so in words, and only the log's reader is
   blind. This is not a gap in what the system recorded; it is a gap in one
   reading of it.
3. **It is the third instance in two runs of one seat of a single class.** An
   absent `deploy_runtime` row read as a missing press run; a green `checks.yml`
   verdict read off an older commit through a path filter; and now a failure
   count that cannot read the word for the failure. **A conclusion is a row
   written by a reader, so its absence is a claim about the reader and never
   about the world.** Each of the three was found by reading the reader's source
   rather than its output, and each would have survived any number of careful
   readings of the output alone.

**The fix, and it is one alternation each.** `exit=(-?\d+|timeout)` and
`turns=(\d+|-)`, with `timeout` mapped to the 124 the database already stores,
so `classify` returns `failed`. Or, at the host end, write `exit=124` into the
trailer and leave the reader untouched. Either settles it and both files are
HQ's, so it is filed as Ask 3 on the relay page with a live test rather than
fixed here.

**Live test.** On any log ending `exit=timeout`, `capacity.classify(text, 10)`
returns `failed` rather than `running`.

**Status:** open, asked 2026-11-02, HQ's to land.
