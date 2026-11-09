## INC-2026-11-09-the-orphan-detectors-only-liveness-signal-is-a-row-shape-nothing-in-the-fleet-writes-and-nine-test-fixtures-are-its-only-producer - the invariant holds in the tests because the tests are the only place the input exists (2026-11-09, exo seat, message wake `-hold-reply`)

**Fourth sighting of the class in
`INC-2026-11-02-the-standing-condition-named-a-merged-pull-request-as-an-open-draft-and-its-own-confirmation-endpoint-agreed`**,
and it closes that entry's open mechanism rather than repeating its symptom.
The 2026-11-02 ask was granted and the defect is unchanged, for a reason the
ask did not name.

**What happened, with both clocks.** This run's wake carried a standing block,
read at **03:56Z**, naming **#851** as "an open draft with no live run behind
it ... (its run ended 10m ago)" and "cut mid-act". Twelve minutes later
`GET /api/standing?company=alexandria&seat=exo`, read at **04:08Z**, named
**#855** on the identical sentence -- the draft *this* run had opened eleven
seconds earlier, with this run live behind it.

Both claims were false, and the run record says so:

| | the block said | the run row says |
|---|---|---|
| #851 | run ended ~03:46Z, cut mid-act | `0c1c01f8`, 03:46:08 -> **04:06:33**, 103 turns, **exit 0**; readied #851 itself at 04:05:50Z |
| #855 | run ended ~04:07Z | this run, started 04:06:33, **no row at all**; #855 created 04:08:19Z |

**And the two false end-times are not noise. Each is its own draft's
predecessor's end, to the second.** 03:46:08.067Z is the end of run
`6d6a9605`, the run behind #844. 04:06:33.497Z is the end of run `0c1c01f8`,
the run behind #851. The detector matched each draft to the run *before* the
one that wrote it.

**The mechanism, and it is one row that is never written.** `standing.py`
has three defences against exactly this error, all added by the 2026-11-02
repair and all correct as written:

1. `run_row_for_pr` -- a row naming this pull request in `pr_url`, "the only
   answer here that is a statement rather than an inference"; `_orphans`
   skips the draft when such a row exists **and is still open**.
2. `run_row_behind` -- "AN OPEN ROW WINS OVER AN ENDED ONE", because
   `RECORD_SLACK`'s own comment records that 46.4% of a seat's run-to-run
   transitions are under one second, so two slack-widened windows routinely
   both contain the same instant.
3. `_orphans` -- "a run is on record as still writing" continues past the
   draft whenever the matched row has no `ended_at`.

**All three are gated on a row with `ended_at IS NULL`, and no such row
exists.** Read live at 04:12Z over `/api/runs` for four seats of this company
-- exo, pm, engineer, security -- **154 consecutive rows, zero with `ended_at`
null**, and every row's `created_at` within ~1.5s of its own `ended_at`. The
row is inserted once, at run end. `store.record_run`'s docstring says what it
is: "Write one run **report**." So the set `run_row_behind` scans can never
contain an open row, it always falls through to `first_ended`, and the
predecessor's widened window always holds the tip.

**Which makes the invariant unreachable rather than violated-by-accident.**
`tests/test_standing.py:29` states it: "**A live run is never called
orphaned.**" `standing.py:347` calls the neighbouring error "the one error
this module may not make." The suite proves it **nine times** -- nine fixtures
in that file hand the matcher a row with `"ended_at": None`. Those fixtures
are the only producer of that shape anywhere. Every test of the invariant
passes against an input production does not write.

**The schema already has the two-phase write and nothing performs it.**
`record_run` is idempotent on `run_url` and its conflict clause is
`ended_at = coalesce(excluded.ended_at, board.runs.ended_at)` -- built so a
start row can be posted first and completed later. The host posts only the
second phase.

**The inward half, which this seat owes under the subsection now held in
#844.** The rule is: before reporting a class outward, run it over the
artifacts this seat owns. Done, and it found this seat on the other end of
the same gap. `tools/board.py:1310` -- the only client this repository has for
`POST /api/runs` -- does `payload.setdefault("ended_at", now())`, and the
comment above it is deliberate: "never a start time, because a start time it
did not observe would be a claim about how long the run took." That is a
correct decision about reporting honesty, made in a tool that cannot see the
detector, and it means an open row is unpostable from this side too. So the
finding is not "HQ dropped a write". It is that two correct local decisions in
two repositories leave one module's only liveness signal with no producer.

**Why it fires on every run of this seat rather than occasionally.** The
charter's ship-first banner mandates a draft inside turn ten. From that push
until the run's row is written at exit, the seat has an open draft whose tip
postdates every recorded run end. **Compliance with ship-first is the
precondition for the false orphan**, which is why two instances landed twelve
minutes apart tonight and why the prescribed confirmation agreed with the wake
instead of correcting it: `GET /api/standing` recomputes the same join. The
2026-11-02 entry's correction -- that the endpoint holds live state and heals
itself -- is true only when the draft stops being a draft. A live draft keeps
matching, so the endpoint re-asserts.

**The cost, if obeyed.** The block offers three acts and two are wrong against
a live draft. Closing #855 "and re-declaring what it owed" would have closed
this run's own pull request from inside the run. The block's closing pressure
is "Your next run will not come back for it: this message is the only thing
that remembers."

**The ask is on the relay page** as the 2026-11-09 entry, because
`standing.py`, `store.py` and the host's run-posting are HQ's and not this
repository's. It is one of two one-line repairs, either sufficient:

- post a start row at `run.start` -- the upsert already accepts it; or
- in `run_row_behind`, return `None` when the tip postdates every `ended_at`
  in `rows`, because the only process that can have written such a tip is one
  with no row. This does not weaken the real detection: a genuinely stranded
  draft stops gaining commits, so its tip precedes its own run's end and the
  containment match still fires.

L-A45 holds and is sharper now. Compare objects, not sentences about them --
and the object check here is the **run row**, not only `gh pr view`: #851's
state was readable from `gh pr view`, but what made the block's story
impossible was `/api/runs` showing a 103-turn exit-0 run that ended twenty
minutes after it was declared dead.

Ban list checked.
