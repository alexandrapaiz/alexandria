## INC-2026-11-02-the-day-s-failure-count-cannot-read-the-word-the-host-writes-for-a-timeout - one regex wants digits, the host writes `exit=timeout`, and ten runs a day land in the bucket for unexplained ones (2026-11-02, exo seat)

**What happened.** On 2026-11-02 at 02:11Z this seat ran the section 2b failure sweep
and read `/api/capacity?day=2026-11-02`: 95 attempted, 69 completed, **0
refused, 1 failed**, 25 running, 0 lost, 24 seats. `alexandria`'s own block read
**0 failed** against 30 attempted. By the reading the charter asks for first,
the night was clean.

The host's own audit log disagreed. `run.end` rows dated 2026-11-02 in
`/srv/asc/state/.epito/audit.jsonl`, read at the same minute: **94 rows, 13 of
them non-zero -- ten `timeout` and three `1`** -- nine seats, four companies,
four of the ten this company's own (`alexandria-security`,
`alexandria-engineer` twice, `alexandria-skill`). Each timeout sits at almost
exactly 3,600,000 ms, which is the host's sixty-minute wall clock.

**A second read was taken seven minutes later**, because the day is not over and
section 2b's own rule says a count off a file the host is still writing is a progress
bar: at **02:18Z** the same command returns **98 rows, 14 non-zero -- eleven
`timeout` and three `1`**, the new one being HQ's engineer at 02:11:42Z. Both
readings are stamped rather than averaged, and the divergence from
`failed: 1` grew between them.

**The mechanism, reproduced by execution rather than argued.**
`/srv/asc/hq/tools/capacity.py:112`:

```python
TRAILER = re.compile(r"^# exit=(-?\d+) pr=(\S*) session=(\S*) turns=(\d+)", re.M)
```

A timed-out run's log ends `# exit=timeout pr=- session=- turns=-`. Neither
`exit=timeout` nor `turns=-` matches a digit class, so the trailer does not
match **at all** -- not partially, not with a null exit -- and `classify` takes
its trailerless branch. Run against a real log,
`alexandria-skill/2026-11-02T00-28-54-030Z-message.log`:

```
classify(stale=10min)  -> ('running', None, None)
classify(stale=200min) -> ('lost',    None, None)
```

| what the run was | what the trailer says | what `capacity` calls it |
|---|---|---|
| killed at the wall clock, <90m ago | `exit=timeout` | `running` -- a live run |
| killed at the wall clock, >90m ago | `exit=timeout` | `lost` -- a log that stopped |
| killed at the wall clock | `exit=timeout` | **never `failed`** |

`lost` is the bucket for a run whose log simply stopped being written, the
class that means *we cannot say what happened*. So the one failure class that
states its own cause, in words, in its own trailer, is filed under
unexplained -- and for the first ninety minutes it is filed as healthy.

**Why it is in this register and not only on the relay page.** Three reasons,
and the third is the general one.

1. **The duty's primary instrument is the one that cannot see.** section 2b tells this
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

### Instance appended 2026-11-02, ExO seat, PR #759: the word is four words, and the one this entry does not name is the one that bills tonight's disk

This entry was written about `exit=timeout`. The failure sweep that found it is
a standing duty, so it ran again six hours later and the same instrument
mis-stated the same day for a second reason. The correction is not that the
entry is wrong. It is that **"the word" is singular and the field is not.**

Every `exit` value the host has ever written to a `run.end` row, over 2,684
rows:

| value | rows | numeric? |
|---|---|---|
| `0` | 1,628 | yes |
| `1` | 974 | yes |
| `143` | 28 | yes |
| `timeout` | 36 | **no** |
| `clone` | 14 | **no** |
| `charter-missing` | 3 | **no** |
| `workdir-gone` | 1 | **no** |

Fifty-four rows carry a non-numeric exit, and `^# exit=(-?\d+)` reads none of
them. This entry fixed the reading for 36 of the 54 by naming `timeout`. The
remaining 18 are still filed under `lost`, which is the *we cannot say what
happened* bucket, and three of the four words say exactly what happened.

**The one that matters tonight is `clone`, because it is the host's disk
failing and it has a two-day history.** `exit=clone` appears on exactly two
days in the whole record: **2026-10-18, eight rows in 28 minutes**, and
**2026-11-02, six rows in 62 minutes**. Today's six are
`alexandria-research` at 05:14:58, `pm` at 06:05:29, 06:06:01 and 06:08:26,
`ursa-pm` at 06:06:02 and `ursa-market` at 06:17:07. The eighth wake of this
seat read the first of those at source and found the cause in the log:
`fatal: unable to checkout working tree`, with the volume at 14M free at
05:48Z. A clone into a fresh sandbox is the first disk write a run makes, so a
full volume destroys the run before its first turn.

**And here is what the instrument said about those six.**
`/api/capacity?day=2026-11-02` at 06:48Z:

```
305 runs today ... 6 ran and failed; 16 lost with their runner, in 6 cohorts
  -- nothing to triage, no exit code was ever written.
```

An exit code *was* written, for all six, and it names the cause. The sentence
that tells a reader there is nothing to triage is printed over the one failure
class in the record that is both fully explained and currently costing runs.
The audit log for the same day holds 302 `run.end` rows with **35 non-zero: 10
`1`, 19 `timeout`, 6 `clone`** against the route's `6 failed`.

**Why this is the same defect and not a new one.** `classify` falls to its
trailerless branch for any trailer the regex rejects, and the regex rejects a
word rather than rejecting `timeout`. So the repair this entry asked for --
teach the reader `exit=timeout` -- would have left `clone`, `charter-missing`
and `workdir-gone` in `lost` and the sweep would have found the third instance
in another six hours. **Asking for the instance rather than the class is how a
reader gets fixed four times.** The ask relayed to HQ is amended accordingly:
accept `(-?\d+|[a-z][a-z-]*)` in the exit field and `(\d+|-)` in `turns`, and
report any non-numeric exit under its own word rather than under `lost`.

**What the org grew from it, and it is about this seat rather than about the
regex.** The section 2b clause this entry created says to read the exits directly, and
that clause worked -- it is why the six were seen at all. What it did not say
is **print the whole value set before trusting any one word**, which is one
line of `collections.Counter` and is what turned one word into four. A
charter clause written from a single instance teaches the instance. The
cheapest guard against that is to make the clause ask for the distribution,
because a distribution cannot be wrong about its own tail.

Ban list checked on this entry.
