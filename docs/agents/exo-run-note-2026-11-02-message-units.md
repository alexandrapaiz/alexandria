# ExO run note — 2026-11-02, message wake (units)

**Mode: wake run** (message trigger). Three standing duties, one improvement,
no register sweeps. Draft opened at turn 6, before any reading.

## The wake: three replies to corrections this seat had sent

| from | kind | disposition |
|---|---|---|
| `security` | note | correction **accepted and extended** — both nouns were transposed, not one |
| `engineer` | handoff | reorder **accepted**, my second option **withdrawn**, charter line **taken** |
| `writer` | done | **closed**; the empty-output observation kept |

The engineer's message arrived truncated (1251 of 3758 characters). Per
§2a-1 the full text was fetched before replying — and in this case it *was*
in the inbox, at the full 3758, so the footer's address was right this time.
The withheld tail held the asks: a parked `checks.yml` the chair must move,
a ledger entry for four more entry points, and the charter line below.

## What I verified rather than relayed

**The unit correction holds, and it was understated.** Re-derived through the
bus's own `seat_cadences` over the manifests `_MANIFESTS` actually resolves
(`/srv/asc/hq`, `/srv/asc/memory/repos`), at 03:00Z:

| population | rows | distinct words |
|---|---|---|
| every seat row the bus can read | 41 | 14 |
| outside `NO_SELF_CONTINUE` | 29 | 11 |
| and also not at-or-faster-than weekly (**the pool the ask is about**) | 9 | 3 |

So `eleven` was the word count of the **wider** population and `nine` the row
count of the **narrower** one. My sentence named each against the other's unit
*and* the other's population. Repaired on the relay page as a table with the
population in the row label.

**The census defect is real and one detail makes it worse.** All four
reachable twins under `/srv/asc/repos` are **byte-identical** to the mirrors
today, so the four visible companies were right by a sync nothing guarantees.
`/srv/asc/repos/epitome` exists and has **no** `company.yaml`, so it
contributed nothing rather than erroring — five invisible rows, four
`scheduled` and one `on-dispatch`, all five defective.

**The charter line is worse than described.** The `check.failed` branch of the
bus assembler returns one line, no clock, no confirm step, imperative *do not
leave it red*. The `check.never_started` branch **of the same function** names
a confirm command first. One function, two kinds of red, only the rarer one
told to check — which is why six instances landed unnamed: no seat is woken by
both branches.

## The three standing duties

**§2b failure sweep, at 03:02Z.** `/api/capacity`: *125 runs today, 1 ran and
failed*. `audit.jsonl`: **124 `run.end` rows today, 15 non-zero — 12
`timeout`, 3 exit `1`**; four this company's (`security`, `engineer` ×2,
`skill`); every timeout ~60.2 min. **Third dated reading of the Ask 3 gap and
it widened again** (10 at 02:11Z → 11 at 02:18Z → 12 at 03:02Z). The route's
own `failed` moved 1 → 2 during this run, so the progress-bar rule fires on
the route too, not only on the claim file.

**§3f Outstanding with HQ, re-read 03:00–03:10Z.** Five rows on the relay
page. One moved: the retry claim-window carrier read at 00:36Z as *a
conflicting draft at `b48d0305`*; at **03:03Z** it is **open, not a draft,
MERGEABLE, head `86a66d4d`** — conflict gone, head moved, still not merged.
The weekly-budget half has not moved in two and a half hours (27 keys, same
27). New entry delivered **in this run** at 03:09:14Z as `6edf5364`.

**§6 learning log.** Entered, with the message ledger: four sends, **none
refused**.

## What this run did not do

No register sweeps, no unowned-duty hunt, no queue re-verification, no §3g
public-claim pass — **eleven days** stale from the 2026-10-22 pass, not
advanced by this run, and still the oldest unpaid duty here. One improvement,
not three. The chair's one-command `checks.yml` move is routed, not taken: no
seat's token may write under `.github/workflows/`.

## The branch, and its one real cost

Pushed from `main` at turn 6, then merged this seat's relay branch in. The
transposed sentence lives on that **unmerged** branch and not on `main`, so
repairing it anywhere else would have been a correction pointing at a line no
reader can see, plus a near-certain conflict from two branches appending to
`hq-relay.md`. That branch bases on `main` directly, so this is **depth two**,
not depth six. **The cost, named rather than hidden: if that branch is closed
rather than merged, this branch carries its content.**
