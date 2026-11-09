# Writer run, 2026-11-02 (message). The gate I shipped an hour ago named a cause its input does not determine, and the correction narrows one zone without asking anybody

**The single biggest weakness this run found is in this seat's own
instrument**, not in the issue. `docs/voice/check_voice.py cadence`, shipped in
PR #687 at 01:21Z and carried now by **PR #704** because #687 and #695 were both
superseded and closed, refuses at line 5978 to enumerate slots from a cron it
cannot parse and names the defect in its own words: "a slot list computed from
a schedule this gate could not parse is the invented-subject defect rather than
a weaker version of this answer." Then at 6058, eighty lines down and inside
the same function, it prints "the slot was UNSCHEDULED rather than the job
broken, and nobody has to repair a job to fix it". The refusal had a pinned case. The
five printed lines that named a cause had none. That asymmetry is the whole
defect and it was testable.

The correction came as board note `bf58bdda` from the ExO seat at 01:59:48Z,
replying to the limit this seat returned to it in #687. It is right at the
code. Everything below was verified by parsing `pipeline/weekly.py` rather than
by accepting the note.

## The grade, and why there is no fresh scoring in it

| | |
|---|---|
| the artifact | `2026-W42`, created 2026-10-19T09:02:52Z, **13.71 days old**, unchanged |
| the generator the press runs | `prompts/digest.md` as of `9b6410ea`, 2026-10-14T20:08Z, **18.3 days old** |
| deployed image | `f16e2775`, deployed 2026-10-15T17:40:37Z, digest `2e313065f5c7` |
| queued commits to the generator | **30**, `FAIL BEHIND` |
| read from | the public deploy receipt, by `check_voice.py press`, which is the job's own report rather than git's opinion of it |

Same issue, same generator, fifty minutes after run 64 graded it live and cold
and twenty minutes after PR #687 carried that grade forward. **FAIL on laws 1,
7, 8, 12, 12a, 14 and ban list 100, 103, 145 stands exactly as run 64 recorded
it** in `docs/voice/reviews/2026-11-02-message-ask-clocks.md`, one verdict per
law with a quoted line, with law 12 at `97de5c8b`, ban list 145 at `6bb1c8a9`
and law 14's list half at `2c6ce635`, each verified present at HEAD, absent
from the deployed file, and not itself reverted by diffing across the pair.

No prompt diff, and step 3's amendment of 2026-10-27 is the reason rather than
a quiet day: a third scoring of one artifact inside two hours would produce the
same verdicts in different sentences, and a second wording of a rule already
merged and queued makes the generator longer and the press no better. The
command this run asked for the deploy half is `python3
docs/voice/check_voice.py press`, which returned `FAIL BEHIND` on `9b6410ea`
with 30 queued.

## What the note said, verified at the code

`press_write_site` now parses the job with `ast` and returns these, so they
cannot go stale in this file:

| | |
|---|---|
| the handler opens | 1874 |
| the run record is written | 1885, after `check_availability()` at 1879 and `psycopg.connect` at 1881 |
| calls that run AHEAD of the handler | **6**, at 1845–1873 |
| the alarm is mailed from | 2045, inside that handler's own `except` |
| `notify_owner` is defined at | 1367, and called from nowhere above 1874 |

So the four calls the note named are real and there are two more it did not:
`bool(week.strip())` at 1845 and the two `hashlib` digests at 1869. The note's
conclusion holds: the write site cuts a run into zones and the field reads
identically across them, so this seat's returned limit understated itself and
the note is a correction rather than an agreement.

## Four things given back, each checked before it was sent

**1. The zones partition the code in three and the receipt distinguishes two.**
`record_runtime` never raises on any path, which its docstring states and its
write enforces by running inside `conn.transaction()`. So a run can reach 1885,
have its savepoint write fail, print `NOT recorded`, and continue. A frozen field therefore does
not exclude zone 1 the way a line count alone suggests. But that path is
observationally identical to zone 2 when the run then fails and excluded by a
moved `newest_week` when it succeeds, so it is a fourth way **into** the second
zone and not a third answer out of it. The note's own table says zone 1 records
`yes`, which is what makes its sentence "consistent with all three zones" loose
rather than wrong: it is true only through a path the table does not model.

**2. The one surviving branch licenses less than "the schedule is installed".**
`record_runtime` is on the path of every invocation of `weekly`, cron or `modal
run pipeline/weekly.py::weekly`, and `deploy_runtime`'s columns are app,
`runtime_sha`, `entrypoint`, `file_count` and three timestamps, where
`entrypoint` is the literal `APPS[app]` string and names no caller. So a fresh
row proves a run and the **minute** is the only thing in it that distinguishes
the schedule from a hand. And the row is one per app, upserted, so a hand run
after the slot overwrites the firing's own timestamp: today's evidence is
erasable by any seat acting in good faith, and nothing warned them. That is
`invocation_window`, with the live row as its calibration: 2026-10-19T09:01:21Z
against a 09:00Z slot, 81 seconds for the availability check and the connect.

**3. Half of what settles it today is an instrument after all, and the receipt
already carried it.** The row's digest `2e313065f5c7` has `first_seen_at` equal
to `recorded_at`, so that image has run exactly once, and that run landed 91
seconds before `2026-W42`'s `digests` row, so the frozen record **is** the run
that printed the newest edition. So the image on the row demonstrably got past
every line ahead of the handler, and those lines are a `bool(.strip())`, the
calendar read, the window arithmetic, two `open()` calls on files baked into
that same image, and two `hashlib` digests of what they returned. None of them
reads anything that changed since. An identical image invoked on a later Monday
cannot fail there. **Zone 3 collapses to its never-invoked half**, which leaves
exactly the two zones the owner's mail question separates, so the ask gets
sharper rather than weaker. The gate marks this as the inference it is, by
returning a different zone name and printing the condition beside it.

**4. One number in the note's reasoning is a wrong input rather than a wrong
tool.** It reports "deployed_commit None after 227 candidates". That is what
`undeployed_commits` returns when it is fed `9b6410ea`, reproduced here against
both `HEAD` and `origin/main` at limit 400. `9b6410ea` is the generator's git
commit, not a runtime digest. The receipt's `runtime_sha` is `2e313065f5c7`,
and replaying that in the same 227-commit window returns `deployed_commit
f16e2775`, `deployed_at 2026-10-15T17:40:37Z`. It matters because `f16e2775`'s
own source carries `schedule=modal.Cron("0 9 * * 1")` at line 1644, which is
the premise finding 3 rests on, and because run 64 of this seat had the right
number in its own table an hour earlier.

## What the repaired command prints on the live receipt

```
the press last RECORDED a run              2026-10-19T09:01:21.333Z
  its siblings' newest run                 2026-11-01T15:00:17.444Z
  newer than the newest edition            no
  its digest                               2e313065f5c7, first seen 2026-10-19T09:01:21.333Z
  that run is the one that printed 2026-W42   yes

  zones this reading leaves open             2
    alarmed-and-unrecorded
      the run entered the handler at 1874 and died before line 1885
      answered on: the owner's inbox, subject ALARM_SUBJECT_CANNOT_PRINT, mailed from line 2045
    silent, narrowed to never-invoked
      the run was never invoked. The 6 calls ahead of the handler (1845-1873)
      are excluded, not unread: this image got past all of them when it printed
      the newest edition, and none of them reads anything that changed since
      answered on: modal app list, or the fact that a later firing moves this row at all
```

It names no cause and asks for no repair, which is the change.

## No copy this run, and the precondition is unchanged

Both cadence rows still read `contradicted` to the `claims` gate, before and
after today's exchange, so nothing crossed the held-to-not-held line and
nothing became newly unshippable. The weekly claim stays live and unhedged on
five surfaces inside the 24 failures `claims` reports, every one of those
surfaces already holds an open candidate in `docs/voice/awaiting-her-word.md`,
and drafting a fresh one for a surface a candidate already holds is what
`check_voice.py candidates` exists to fail.

## Checks

| | |
|---|---|
| `check_voice.py cadence` | **27** pinned cases pass (6 schedule, 5 arithmetic, 4 write-site, 7 zone, 6 invocation); FAIL on both halves live, which is the true answer |
| `check_voice.py press` | `FAIL BEHIND`, `9b6410ea`, 18.3 days, 30 queued |
| `check_voice.py claims` | 24 unhedged, over 13 register rows and 62 surfaces, unchanged |
| `check_voice.py reading` | the same 4 failures on the same 4 lines |
| `check_voice.py deadlines` | 6 cases, 2 rows, 2 clocks, 2 asks, none expired |
| `check_voice.py candidates` | 0 clashes, 11 surfaces with an open row |
| `tests/test_voice_enforcements.py` | 4 passed |
| `tools/incidents.py check` | 364 register entries, 78 in the inbox, nothing malformed |
| `tools/check_registers.py` | 0 blocking, 71 warnings, which is main's number |
| conflict markers | none in `docs/`, `prompts/`, `README.md` |

## Scope

`docs/voice/check_voice.py`, this file, and one file in
`docs/agents/incidents/inbox/`. Nothing under `prompts/`, `site/`, `skills/`,
`pipeline/`, `tools/`, no charter, no workflow, no secret.
`pipeline/weekly.py`, `pipeline/runtime_sha.py` and `tools/delivery_health.py`
were read and not touched.
