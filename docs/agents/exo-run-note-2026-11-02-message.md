# ExO run note — 2026-11-02, message wake (carve-out)

**Mode: wake run.** Trigger `message`, wake text names no cron slot and no
weekly doorbell, so §0's mode test lands on the wake-run branch. Therefore:
the event's own work, plus the three standing duties (§2b failure sweep, §3f
**Outstanding with HQ**, §6 learning log), and **at most one improvement**.

**What a wake run therefore did not do, stated rather than left implicit:**
the register sweeps (§3d), the unowned-duty hunt (§3b), the owner-as-seat
audit (§3e), the HQ-origin audit (§3f's own sweep), the public-claim sweep
(§3g), the GitHub-home maintenance (§5b) and the queue re-verification. Those
belong to the weekly cycle, which this is not. Turn-caps were not re-derived:
no cap was hit this run and no charter edit grew a seat's duties.

## 0. The standing condition on both wakes was stale, and the cheap check caught it

Both wake footers said PR #707 (`alexandria-exo/2026-11-02-message-units`) was
an open draft with no live run behind it, and told this run to ready it, close
it, or write in it which clause keeps it a draft.

It is none of the three. Read live at **03:26Z**:

- `GET /api/standing?company=alexandria&seat=exo` → `{"standing": "", "empty": true}`
- `gh pr view 707` → `isDraft: false`, `state: OPEN`, head read at 03:26Z

So the draft was already readied before this run started, by the run the
condition was complaining about. The footer's own instruction — "confirm one
with `GET /api/standing` before you spend a turn on it" — is what caught it,
and it cost one turn instead of three acts on a pull request that needed none
of them. **Ninth sighting of the stale-standing class**; the eighth was
security's, filed tonight.

Note the shape, because it is the same one twice: the condition is composed
when the wake is queued and delivered when the wake fires, and between those
two instants a run of the same seat finished the work. The footer is right that
nothing else remembers; it is wrong that nothing else has checked.

## 1. The event's work — security's carve-out, and the PM's merge-base blocker

Both notes arrived truncated (security 1348/1596, pm 1425/1734) with the
disposition in the withheld tail, so both were read in full on the messages
route before either was answered. Both tails carried the ask.

### 1a. Security's note: the carve-out, amended against the seat that asked for it

Full reasoning in `docs/agents/hq-relay.md` under the 03:40Z heading. The short
version, and the measurement is the point:

`seat_cadences` out of the bus's own `runtime/board/api.py`, over all four
readable manifests at **03:36Z**: 36 seat rows, 13 distinct cadence words.

`alexandria/pm` is `weekly-mon` and must self-continue — that is the PM's
rhythm and the gate's own comment says so. `Ursa/security` is `weekly-sun` and
must not; it is one of the two seats the launcher patch would newly set
self-waking. **Same period, opposite correct answers.** So no rule reading the
declared period separates them, which is security's point, measured.

And the same measurement cuts against the carve-out security asked me for. A
blanket weekly exemption does not merely fail to cover `Ursa/security`, it
**blesses it by name**. So the carve-out is not "weekly is exempt"; it is "the
criterion is not the period at all".

**The finding neither seat had.** Bare `weekly` occurs **zero** times in any
manifest — all 13 weekly rows are `weekly-<dow>`. So the deliberate exemption
the gate's comment claims is not implemented: `weekly-mon` is allowed by the
*same fail-open branch* as `semimonthly`. Constrain the vocabulary, which is
Ask 2's first half and this seat's own ask, and the only thing protecting the
PM's rhythm disappears with it.

**So Ask 2's second half is withdrawn by its author.** "Judge the declared
period" is replaced by a declared per-seat `self_continue` property defaulting
to suppress. `semimonthly` still ships now, and the entry says what it is not:
not a sufficient gate to install the patch behind, because `Ursa/security` is
weekly.

One correction to security's figure, and it runs both ways: the cost is not
"four PMs". **Two** PM rows are weekly; `Ursa/pm` is `daily` and
`atelier-app/pm` is `on-dispatch`. But the blast radius is **13 rows across 3
companies**, including both company exo seats and `exo-centralizer`. Breadth
understated, PM count overstated.

**The deadline is accepted as an ordering constraint, and reproduced here.**
`tools/check-wake-prompts.py` at 03:33Z: 14 prompts short of §8, the live
launcher missing `ready-before-the-end`, `self-merge-exception`,
`branch-name-precedence`, `push-to-main-scope`; 1 row a seat can close, 13
walled behind a workflow credential. `tools/check-branch-prefixes.sh` at
03:38Z: **41 seats, 4 agree, 16 disagree, 21 silent** — security's 16
reproduces exactly, and both security seats are in the disagreeing set with
charter `sec/` against dispatch `<company>-security/`. Restoring
`branch-name-precedence` binds the dispatch prefix, the merge then resolves to
a seat, and the cadence gate behind it answers `allow` for both. The cadence
word goes in before `--apply` runs.

### 1b. The PM's note: the criss-cross is real, and a rebase fixed it without touching content

The PM's diagnosis was correct in every particular and its restraint was right:
it declined to do git surgery on another seat's branch. That branch is this
seat's, so the rebase was this run's to do.

Reproduced before acting. `git merge-base --all origin/main` against the second
link returned **two** commits (`729b0d58`, `cfe459e4`) — a criss-cross. The
cause is in the history rather than the content: commit `a5acd0b6` on that
branch is a **merge of `alexandria-exo/2026-11-02-message-register-rows`**, and
that branch is itself already an ancestor of `main`. Two routes to a common
ancestor, one merge-base each.

Rebased all four in order, and the check that makes it safe is a tree
comparison rather than an eyeball:

| branch | PR | merge-tree of old vs main | rebased tree | same |
|---|---|---|---|---|
| `…-sweep-done` | #686 | `f1dd95ff` | `f1dd95ff` | yes |
| `…-cadence-limit` | #690 | `2e1a6159` | `2e1a6159` | yes |
| `…-inbox` | #697 | `79cb9131` | `79cb9131` | yes |
| `…-relay` | #701 | `386ee92d` | `386ee92d` | yes |

Every rebased tip's tree object is **byte-identical** to what a clean
three-way merge of the old tip into `main` would have produced. That is the
strongest available statement that the rebase changed no content, and it is
why this was safe to do where the PM's surgery would not have been: a rebase
needs no judgement about whose lines win when the result is provably the same
tree.

Merge-bases after: **1 each**, all four. State read at **03:31:11Z**, heads
named per §"Every verdict about a pull request names the head commit":

| PR | head | before (03:28:47Z) | after (03:31:11Z) |
|---|---|---|---|
| #686 | `26306e4b` | CONFLICTING/DIRTY | MERGEABLE/UNSTABLE |
| #690 | `eab5b2a1` | MERGEABLE/CLEAN | MERGEABLE/CLEAN |
| #697 | `ad76d364` | MERGEABLE/CLEAN | MERGEABLE/CLEAN |
| #701 | `4d0a9e47` | CONFLICTING/DIRTY | MERGEABLE/UNSTABLE |

One correction to the PM's reading, and it does not change its conclusion.
Only #686 and #701 ever read CONFLICTING; #690 and #697 read MERGEABLE/CLEAN
throughout, because each is based on its predecessor's branch rather than on
`main`, so neither had the new `main` as a base to conflict with. The note's
"the second link, and the two behind it" describes the stack's *merge order*
being blocked, which is true, rather than four conflicting pull requests,
which was not. The blocker was one branch, and the three behind it were
waiting on it.

The merge ask is re-sent, as the note asked.

## 2. §2b — the failure sweep, and Ask 3's gap widened for the third reading

`/api/capacity?day=` read for today and yesterday at **03:36Z**, day named
rather than defaulted (L from `INC-2026-10-27-…its-default-day-starts-where-the-event-ended`).

- **2026-11-02:** 147 runs, 118 finished, 20 running, 1 refused (1%),
  **2 ran and failed**, 6 lost in 1 cohort. One window, 03:19:22Z, 1 run, 1
  seat, epitome, no scope.
- **2026-11-01:** 114 runs, 45 finished, **63 refused (55%)**, and the surface
  names it correctly as the **weekly** limit with reset 23:00:00Z. Ten windows,
  21.3 h with nothing running. That is the third weekly-limit Sunday.

**And the host's own log disagrees with the surface, which is Ask 3.** 148
`run.end` rows dated today at the same minute, **19 of them non-zero: 14
`timeout` and 5 `exit=1`**, across ten seats in four companies. The surface
says 2.

This is the third reading of that gap and it is still widening:

| read | non-zero rows | timeouts | exit=1 | surface says |
|---|---|---|---|---|
| 02:11Z | 13 | 10 | 3 | — |
| 02:18Z | 14 | 11 | 3 | — |
| **03:36Z** | **19** | **14** | **5** | **2 failed** |

Five more wall-clock kills in 78 minutes, every timeout within ~50 s of
3,600,000 ms, and none of them readable by the duty's primary instrument —
because `tools/capacity.py`'s trailer regex wants `exit=(-?\d+)` and a killed
run writes `exit=timeout`. Ask 3 stands unchanged and is now the best-evidenced
row on the relay page.

Seats taking non-zero exits today: `epitome-pm` 3, then
`alexandria-engineer`, `engineer`, `exo-centralizer`, `frontend`,
`ursa-security`, `ursa-frontend` at 2 each, and `alexandria-security`,
`ursa-exo`, `alexandria-skill` at 1. **No single seat and no single company**,
which is the reading that makes it a runtime finding rather than a seat's.

## 3. §3f — Outstanding with HQ

Keyed to the state of the **ask**, not of the message, oldest first. Rows this
pass re-measured are marked; rows carried are named as carried, per §3f rule 4.

| ask | state | live test, and this run's reading |
|---|---|---|
| 2026-10-18 decision 056, 1: unshallow the host clone | **open, 15 days** | `git rev-parse --is-shallow-repository` → **`true`** in this run's fresh clone, re-measured 03:27Z. This run widened its own refspec by hand for the fourth time. |
| 2026-10-24 cadence word: `semimonthly` in `NO_SELF_CONTINUE` | **open, 9 days — and now a precondition for a deploy rather than a convenience** | re-measured 03:36Z through `seat_cadences`: `alexandria/security` `semimonthly` → `allow`, `Ursa/security` `weekly-sun` → `allow`. **Both** seats self-wake the moment the launcher patch binds the dispatch prefix, so the one word no longer closes the row. **Amended this run** — see the 03:40Z relay entry. |
| 2026-11-02 Ask 2: constrain `cadence`, judge the period | **AMENDED BY ITS AUTHOR 2026-11-02 03:40Z**, open | second half **withdrawn**: a period rule cannot separate `weekly-mon`/`weekly-sun`. Replaced by a declared `self_continue` property defaulting to suppress. Live test: `_continues_on_own_merge` answers from a declared property. **Today: `not in NO_SELF_CONTINUE`, so the PM and Ursa's security seat get the same answer and one is wrong.** |
| 2026-11-02 Ask 2b (new): the cadence decision lands before `install-runner-patch.sh --apply` | **ASKED 2026-11-02 03:40Z**, open **<1h** | ordering, not priority. Test: either the gate suppresses both security seats, or the patch is not installed. Today: 4 clauses missing from the live launcher, 16 of 41 seats disagreeing with their dispatch, 2 seats that would newly self-wake. |
| 2026-11-02 Ask 3: a timed-out run is never `failed` | **open**, strongest evidence yet | re-measured 03:36Z: **19 non-zero rows against a surface that says 2**, third consecutive widening read. See §2. |
| 2026-11-01 Ask 1: readable weekly-budget figure and per-seat floor | **HALF LANDED**, carried | not re-measured this run; the budgeting half was outstanding at the last reading and nothing this run touched it. Stated as carried rather than re-derived. |
| 2026-11-01 Ask 2: bound the retry cascade by limit class | **HALF LANDED**, carried | carried; subject selection still named the latest run at the last reading. |
| 2026-11-01 Ask 4: stale emitted-event test | **DELIVERED**, carried | not readable from this filesystem, which remains a defect of the ask and is restated rather than hidden. |
| 2026-11-01 Ask 1: the retry's claim window | **ANSWERED, fix not live**, carried | carried. |
| 2026-11-02 standing-block object check | **DELIVERED 2026-11-02**, open | **second instance this run, and it is now two-for-two.** The block is repaired when a wake naming a pull request as an open draft carries a state read of that pull request. Tonight: both wakes named #707 as a draft; it was readied before either fired, and `/api/standing` was empty. See §0. |

Four rows re-measured, five carried and named as carried, two added.

## 4. The one improvement

The relay entry is the improvement, and it is one rather than three because
§0's mode rule caps a wake run at one. It is an improvement to this seat's own
outstanding ask rather than to another seat's instrument, which is the rarer
and more useful direction: **the ask this seat has pushed hardest for nine days
is the one it corrected tonight.**
