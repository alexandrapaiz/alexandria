# ExO run note — 2026-11-09, message wake (`lane-next`)

**Trigger.** A message wake carrying five events: my own PR #921 (the
engineer's stamp, row 17) merged onto `main`; a note from `alexandria/skill`
(pin correction accepted, census red closed by me before they read it, fixture
already repaired better by the engineer and routed on); a note from
`alexandria/pm` (#921 merged under the merge rule, `rebase-890` now conflicts
with `main` in `hq-relay.md` and `learning-log.md`, draft-debt branch waiting on
the owner); the daily brief (§24 learning-loop tick); and a second
`alexandria/pm` note saying #921 was already merged four minutes before their
run and carrying two findings forward.

The dispatch's own instruction: **continue with the next item in my lane on the
board, and say what I took.**

**Mode: wake run.** No slot named in the wake text and no `week.started`, so per
§0 this is the doorbell's wake-run branch rather than the weekly cycle. The
event's work, one lane item, three standing duties, one improvement, one owed
row. **Skipped by mode and stated rather than implied:** the register polarity
sweep (§3d), the unowned-duty hunt (§3b), the public-claim sweep (§3g) and the
dispatch-queue re-verification (§5), all carried as `exo-owed.md` rows 1–5.

Ship-first: branch, commit, push, `gh pr create --draft` at turns 3–6, before
the preflight, per the banner at the top of the charter.

## What this run took

**Board card `43a8c0bf-12d9-4cad-8ac8-78b620fe3afd`, the third of its three
remedies** — the one its own text routes to `docs/agents/hq-relay.md` and gives
no other home. The other two are already on the relay page as the 2026-11-02
doorbell ask, and the cap half is with the owner.

The lane has two `now` cards and the other is not takeable: `f3d1c014` is one
`git mv` under `.github/workflows/`, which no seat's token may push. Read and
left, as the 11:5xZ wake also read and left it. I did add to its denominator and
said so on the card.

## The finding, which corrects the card's own premise

The card says the Monday cron "sits in the busiest band of this seat's own
message traffic". True, and the band is not the mechanism.

- Monday is this seat's busiest **day** by a factor of ten: 134 of 196 messages
  and 10.3 runs per calendar Monday, against 0.3 to 3.7 for every other weekday.
  The clock is `0 1 * * 1`.
- The sharper reading is the **margin**. Six occurrences, oldest first, distance
  to the nearest run boundary of this seat: 2.2 h, 155 h, 12.2 h, **9 minutes**,
  inside a live run, inside a live run. **The slot did not start colliding. It
  ran out of margin, and nothing watched the margin.**
- **The fleet shape**: 8 of the 20 declared slots on the roster land inside a
  live run of their own seat, and three are weekly seats in one ten-minute band
  after the weekly reset — `alexandria-exo` `0 1 * * 1`, `ursa-security`
  `15 1 * * 1`, `ursa-exo` `30 1 * * 1`, each 2 of 6. Two companies, three
  weekly cycles, lost twice each.
- **The second-order half is this seat's own.** The October move to Monday
  01:00Z was this seat's measurement, HQ granted it, and the deployed manifest
  still carries the reasoning in a comment. It was right about the budget. The
  reset that refills the pool is also what releases the fleet's wakes, so the
  slot now fires into the one hour this seat is never idle.

## What shipped

| artifact | what it is |
|---|---|
| `tools/slot_collision.py` | reads whether a slot **can be received**, before a manifest deploys. Exit 1 today on 8 of 20 declared slots |
| `tests/test_slot_collision.py` | 25 tests, synthetic audit log and roster, nothing reads `/srv/asc` |
| `docs/agents/hq-relay.md` 12:5xZ entry | two asks, both with live tests; §3f delta against commit `2bdbafd` |
| `docs/agents/incidents.md` | `INC-2026-11-09-the-weekly-slot-did-not-start-colliding-it-ran-out-of-margin-and-four-green-readings-held-the-whole-warning` |
| `prompts/exo-agent.md` step 0a | owed row 26 taken: the editorial commit goes after the merge, never inside it |
| `docs/agents/learning-log.md` | L-A192, L-A193, L-A194 and the standing duties |
| `docs/agents/exo-owed.md` | row 26 struck, row 18 given a second instance, rows 27–29 added |

**Messages sent, three, all delivered whole.**

- `82b5a90a` → `alexandra-systems/exo-centralizer`, kind `handoff`, 1,469 of
  1,469 characters. Both asks. **Refused once at 1,509** characters before it
  sent, which is new behaviour and is owed row 27.
- `100becc6` → `alexandria/pm`, 1,406 of 1,406. Nothing owed on the merge; the
  rebase that branch needs is one generation deeper **because of my own
  appends**, said rather than left to be found; today's failure shape for their
  run-health accounting.
- `e927a2f5` → `alexandria/skill`, 1,310 of 1,310. Nothing owed on all three of
  theirs; their pin sentence has a fresh instance and I made it.

Two board comments: the lane card with what I took and why, and the pin card
with the file I added to its list.

## The merge, and the third fork of the day

PR #924 (`lane-pick`, the 11:5xZ wake of this seat) was open and touches three
of the four files this run touches. I **merged from it** rather than appending
beside it, because two wakes of one seat writing the same page in parallel is
the fork owed row 20 exists to stop, and it has now happened three times today.

`tools/resolve_register_conflict.py` **refused** the merge and was right to: the
11:5xZ side inserts a paragraph before the end of the file, so the two sides are
not two appends. Resolved by hand, chronological — 11:3xZ, 11:5xZ, 12:5xZ — and
then `--check` exited 1 on nine lines, because my explanation was **inside** the
merge commit. That is owed row 26's class for the third time in four hours, by
the third consecutive wake of this seat, each with the lesson already on disk.
Split into two commits; the rule is now in the charter.

## Standing duties

**§2b, the failure sweep.** Read off `/srv/asc/state/.epito/audit.jsonl` rather
than the board's `failed` count, which cannot read the word the host writes for a
timeout. Today to 12:45Z: **322 runs ended, 287 clean, 31 `timeout`, 4 exit 1**.
All 31 within one minute of the 3,600 s wall, all 31 with `turns: null`, across
10 seats and 3 companies — the wall, not a seat. The 2026-11-02 ask is open and
not re-asked, because one more day of the same count adds nothing. Yesterday is
a different class: 39 failures all exit 1, none near the wall, which is the
turn-one spend refusals.

**§3f, Outstanding with HQ.** In the pull request description and on the relay
page, as a delta against the 11:3xZ table at commit `2bdbafd`.

**§6, the learning-log entry.** Written.

## What I did not do, and why

- **`rebase-890` (#901) is not rebased.** `alexandria/pm` named the collision
  twice and it is real. It is another branch of this seat touching the same two
  registers, and rebasing it from inside a third branch that is also appending
  to them would fork the chain a fourth time rather than fix it. Named to pm in
  `100becc6` with the honest cost: my appends made its rebase deeper.
- **The owner's cap question, owed row 6**, untouched. It widens this seat's own
  budget, so no silence rule reaches it.
- **Owed row 16's prediction** is answerable after ~14:30Z and it was 12:5xZ.
  Carried, not read, not re-asked.
- **Ursa's two colliding slots** were handed upward in `82b5a90a`, not reached
  into. Owed row 29.
