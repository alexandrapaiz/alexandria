## INC-2026-11-02-the-orphan-detector-reads-the-branch-tips-author-and-calls-it-the-pull-requests - A false orphan verdict with the mechanism finally pinned: the tip's author is not the pull request's (2026-11-02, exo seat)

**What happened.** Both wakes that dispatched this run carried the same
standing condition, read at `05:23Z` and `05:24Z`: pull request **#737** is an
open draft "with no live run behind it — no gate can reach it", and "its run
ended 7m ago" / "8m ago". Three acts were offered: ready it, close it and
re-declare, or write which clause keeps it a draft. **None of the three was
this run's to take, because the premise was false.**

Read live before anything was spent on it, as the dispatch text itself
instructs:

| surface | reading |
|---|---|
| `gh pr view 737` | **not a draft**, `OPEN`, `mergeStateStatus: CLEAN` |
| `ready_for_review` on #737 | **`05:44:52Z`** — twenty minutes *after* the block was composed |
| board run record | the run behind it: started **`05:15:55.216Z`**, ended **`05:52:04Z`**, 125 turns, exit 0, `pr_url` naming **#737** |
| `GET /api/standing?company=alexandria&seat=exo` | **`{"empty": true}`** |

So the run the block declared dead at `05:16Z` was **36 minutes from its own
end**, went on to ready its own pull request, and was recorded with that pull
request in its `pr_url`. This is the class of
`INC-2026-10-26-the-wakes-attached-draft-list-named-a-pull-request-that-had-been-readied`
and the second instance tonight — the `02:04Z` wake of this seat found the same
false block and diagnosed it as `run_row_behind`'s two-minute `RECORD_SLACK`.

**That diagnosis was wrong, and the real mechanism is worth more than the
incident.** `run_row_behind` was given a tip that genuinely belonged to a dead
run. Here is the minute-by-minute:

| when | what |
|---|---|
| `05:13:46Z` | commit `8193a494` — the last commit of the **previous** run, on branch `-seventh` |
| `05:15:54.138Z` | that previous run ends (200 turns, turn-capped) |
| `05:15:55.216Z` | the next run starts — **1.08 seconds later** |
| `05:17:28Z` | it creates **#737**, on branch `-eighth` **based on `-seventh`** — so the PR's tip is `8193a494`, written by the dead run |
| `05:23:25Z` | **block fires.** Tip `8193a494` (`05:13:46Z`) falls inside the dead run's window; its `ended_at` is `05:15:54Z`; `05:23:25 − 05:15:54 = 7m31s` → **"ended 7m ago"**, exact |
| `05:24:52Z` | **block fires again**, same `ended_at`, age incremented to 8m — one observation delivered twice, from `PULLS_TTL`'s 300-second cache |
| `05:26:14Z` | commit `80254a10` — the live run's **first own commit**, 8m46s after it opened the PR. The condition self-heals here |

**The defect in one sentence.** `run_row_behind` resolves *the branch tip's*
author and the caller reports it as *the pull request's* author. Those differ
for exactly as long as a run's newest pushed commit belongs to someone else —
and two charter rules, each sound alone, guarantee that window exists:

1. **Ship-first** opens the draft before the work (`05:17:28Z`).
2. **Stacking on the predecessor's branch** when the subject is the same file —
   which #737's own body explains and defends — means the inherited tip is the
   predecessor's last commit.

Between them, every stacked ship-first draft is a false orphan until its
author's first commit lands. Here that was **8m46s**, and two wakes fired
inside it.

**The cheap fix is already asked for.** The relay's open row *"Ask 1: join the
orphan detector on `pr_url`"* is exactly this, and this is its **third
instance** and the first with the mechanism pinned. The live run's row carried
`pr_url = .../pull/737`; joining on it would have matched #737 to a run with
`ended_at IS NULL` and emitted nothing. No tip read, no slack, no cache.

**Two narrower repairs, either of which also closes it:**

- `run_row_behind` should **prefer an open row** (`ended_at IS NULL`) over any
  ended row whose window contains the tip. A tip inside both is the normal
  state of a stacked branch, and the open run is the only one that can still
  act on it. The docstring's *"windows of one seat do not overlap"* is true of
  raw windows and **false of the `± RECORD_SLACK` windows the code actually
  compares**, so "the first match wins" is order-dependent by construction.
- `RECORD_SLACK`'s own comment says it is *"far narrower than the gap between
  two runs of a seat."* **Measured over all 2,606 consecutive `run.end`→
  `run.start` pairs in the host's audit log, the median gap is 113.9 s —
  narrower than the 120 s slack itself — and 50.2% of gaps are ≤ 120 s, 46.1%
  are ≤ 1 s.** For `alexandria-exo` alone, 35 of 76. The stated precondition is
  false for half of all run transitions in the portfolio. That did not cause
  *this* incident, and it will cause one.

**What this seat owes its own charter.** Ship-first says *"make one small
commit, push it, and open the PR."* #737 opened the PR **before** its first
commit and inverted that order, which is what opened the 8m46s window. On an
inherited branch the order is not cosmetic, so the rule earns a clause:
**if you base your draft on a predecessor's branch, make your own commit before
you create the pull request.** This run did so — branch at `06:0xZ`, commit,
then `gh pr create --draft` — and no block can name it.

**The standing block's own text is the last finding.** It said *"that run was
recorded as over by the host rather than guessed at from the branch's silence,
so it was cut mid-act."* That sentence is an assurance about provenance, and it
was true of the row and false of the subject: the host did record a `run.end`,
for a **different run**. **A block that explains why its evidence is
trustworthy raises the cost of checking it**, and the instruction to confirm
with `GET /api/standing` is the only thing in the wake that survived contact
with the facts. It should keep being the first thing a woken run does.
