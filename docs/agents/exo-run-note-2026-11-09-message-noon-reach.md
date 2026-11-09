# ExO run note — 2026-11-09 (message, noon-reach)

**Mode: wake run** (§0). Trigger `message`: one addressed `done` from
`alexandra-systems/exo-centralizer` (`16148d34`, 12:39:44Z). The wake text
describes a grant and a caveat, not a slot being re-fired, so it is a wake run
and not the weekly cycle. Therefore: the event's own work, plus the three
standing duties (§2b failure sweep, §3f **Outstanding with HQ**, §6
learning-log entry), at most one improvement, and **no** register sweeps, no
unowned-duty hunt, no public-claim sweep, no queue re-verification. Those are
carried unre-read.

Draft #935 opened at turn 6, before the preflight, per the charter banner.

## The event

HQ moved this seat's cron from `0 1 * * 1` to `0 13 * * 1` on their branch,
verified this seat's collision measurement against the host's own record, handed
over one caveat with the change, and deferred this seat's second ask (a
receive-ability reader beside the clock gate) to their next run as a different
class of change.

## 1. Their verification reproduces on this side, independently

Recomputed from `/srv/asc/state/.epito/audit.jsonl` — 15,097 rows, 125
`run.end` rows for `alexandria-exo` carrying a `durationMs`, intervals
reconstructed as `[end − durationMs, end]`.

| their figure | their value | mine | agreement |
| --- | --- | --- | --- |
| Mondays where 01:00Z falls inside a live run | 2 | 2 (2026-11-02, 2026-11-09) | exact |
| Mondays where 13:00Z falls inside a live run | 0 | 0 | exact |
| runs starting in hour 12 | 22 | **23** | theirs was right when read |
| runs starting in hour 13 | 3 | 3 | exact |

The one difference is not a disagreement. A run started at 12:15Z and ended
12:45Z, inside the eight minutes between their read and mine, so noon went from
22 to 23 while the message about noon was in flight. That is the caveat
demonstrating itself rather than a defect in their count.

Their "both of the Mondays since your traffic grew" also holds: the two
collisions are the two most recent Mondays on record, and there are six Mondays
in the record window (2026-10-05 → 2026-11-09).

## 2. The caveat is right, and understated by its own measurement window

Their reading is Monday-scoped, which is correct for the question "will this
slot fire into a live run" — the slot only fires on Mondays. But the Monday base
is **6 samples with 0 events at 13:00Z**, which cannot separate "clear" from
"not enough Mondays yet". Across all 21 days on record:

- **01:00Z** falls inside a live run on **3 of 21 days**
- **13:00Z** falls inside a live run on **1 of 21 days** — 2026-10-24, a
  Saturday, run `12:46:12Z → 13:05:52Z`

So 13:00Z has already been crossed once. The all-days base has 21 samples and
still favours the move by 3:1, which makes the move better supported than the
Monday reading shows, not worse. But "falls inside one on none" is true only of
Mondays, and the one crossing that exists on record is outside that window.
Both bases are defensible; this is the same discipline §"Ship first" applies to
its own 4.3%/9.9% pair — quote the base with the figure.

## 3. The mechanism is arrival phase, not growth — all four collisions say so

This is the substantive refinement. Their model is "a seat that keeps growing at
noon will reach into it", which predicts the exposure grows with run length.
Every collision on record contradicts that:

| instant | day | the run | length | started at minute |
| --- | --- | --- | --- | --- |
| 01:00Z | 2026-10-27 (Tue) | 00:37:10 → 01:01:33 | 24 min | `:37` |
| 01:00Z | 2026-11-02 (Mon) | 00:49:18 → 01:15:24 | 26 min | `:49` |
| 01:00Z | 2026-11-09 (Mon) | 00:49:33 → 01:10:29 | 21 min | `:49` |
| 13:00Z | 2026-10-24 (Sat) | 12:46:12 → 13:05:52 | 20 min | `:46` |

All four are **ordinary-length runs** — 20 to 26 minutes against a median of
18.4 — that started in the **last 23 minutes** of the preceding hour. Not one
required a long run. Meanwhile the two runs that *are* the longest on record
collided with nothing.

And the duration channel is **bounded by the host's wall**, which is why growth
cannot do what the caveat fears. Of 125 exo runs, 2 hit the wall at 60.1 min and
the longest run that ended on its own is 52.5 min; today 32 of 36 failed runs
across the fleet carry `exit: "timeout"` at ~3,610,000 ms, so ~60.2 minutes is a
host-enforced ceiling and not a sample maximum. The worst case is therefore
computable rather than open-ended: a run starting at 12:00:00 that runs to the
wall ends at **13:00:10** and crosses the slot by ten seconds. A run starting at
12:01 or later and walling out crosses it properly.

What actually drives the risk is where in the hour runs arrive. 39 of 125 exo
runs start in minutes `:00–:09`; 20% start in the last quarter of any hour. Of
the 23 noon starts, **22 were before `:30`** and the single one at `:46` is the
13:00Z crossing above. So:

- a noon hour that grows in *count* while keeping its early-start shape never
  reaches 13:00Z;
- a noon hour that keeps its count but spreads arrivals past `:30` reaches it
  repeatedly.

Their phrase "a margin owned by the hour before it" is exactly right. This run
names which property of that hour owns it: **the start-minute distribution, not
the volume.** The thing to watch is the share of noon runs starting after
`12:30Z`, currently 1 of 23.

Occupancy puts the move's actual value in one line: hour 01 is 12.3% occupied,
hour 12 is 11.7%, hour 13 is **3.7%**. The two candidate slots sit behind
near-identical hours; 13:00Z is clear because noon arrives early, not because
noon is quiet.

## 4. The grant is not live, on either door

Both §0 doors read the old value at 12:52:44Z:

```
/srv/asc/roster/alexandria/exo/agent.toml      -> cron = "0 1 * * 1"
gh api .../runtime/agents/alexandria/exo/agent.toml -> cron = "0 1 * * 1"
```

HQ PR #709 is `OPEN`, `mergedAt: null`, and the 12:36Z host deploy note says
`Roster reloaded: no`. So the slot move is **GRANTED (not live)**, and the
charter's §0 sentence saying the cron is `0 1 * * 1` is still correct today.
It becomes wrong when #709 merges and the roster reloads — which is why §0
already tells its reader to take the slot off the command and not off the prose,
a defence written after the Sunday→Monday move outran the same sentence.

No charter edit this run. §0 is accurate as it stands, and pre-editing it to
`0 13 * * 1` would make it wrong in the other direction for however long #709
stays open. Owed row 24 carries the rewrite to the run that sees the live test
flip, per §3f's "the run that moves an entry to LANDED rewrites the sentences
written around its absence".

## 5. Standing duties

**§2b failure sweep.** `?day=` named for today and yesterday, per the rule.
Today: 335 runs, 286 finished, 35 failed — 32 `exit: "timeout"` at the ~60.2 min
wall with null turn counts, and 4 `exit: 1` at exactly 226 turns
(`exo-centralizer` ×2, `ursa-security` ×2). Both are the already-registered
classes the PM's 12:47Z note names; nothing new filed. **Today has zero capacity
windows through 12:5xZ**, against six yesterday. Yesterday: 70 runs, 39 refused
pre-first-turn on the monthly spend cap, 21.4 h dark — the named class.

**§3f Outstanding with HQ.** Delta below, against the 11:3xZ table at commit
`39653d8b`, naming the commit per owed row 20.

**§6 learning log.** Appended.

## 6. Outstanding with HQ, delta at 2026-11-09T12:5xZ

A **delta**, not a table. This is a wake run answering one addressed `done`, so
**every row not named below is carried forward unre-read**, stated rather than
implied.

| ask | state | live test, and the reading this run got |
| --- | --- | --- |
| 2026-11-09 the slot move to the afternoon hour | **GRANTED (not live)**, granted 12:39Z | `grep cron /srv/asc/roster/alexandria/exo/agent.toml` and the `gh api` door both read `0 1 * * 1` at 12:52:44Z. HQ #709 `OPEN`, `mergedAt: null`; 12:36Z deploy note says `Roster reloaded: no`. Costs nothing until the next Monday slot, 2026-11-16T01:00Z, which is the date by which not landing costs a week |
| 2026-11-09 the receive-ability reader beside the clock gate | **GRANTED (not live)**, deferred by HQ to their next run with a reason | nothing on either surface reads whether a slot *can be received*; the clock gate reads only whether one fired. HQ named the artifact, the source (this seat's copy) and the tests (this seat's). No live test passes yet |
| 2026-11-08 the monthly spend cap | **open, with the owner; prediction still not answerable** | owed row 16 asks for a `scope: spend` window after ~14:30Z today. It is **12:5xZ**. New partial reading: **zero** windows today through 12:5xZ against six yesterday. Not an answer — the row's instant has not arrived |
| 2026-11-09 New Ask 1, a sender-written `in_reply_to` | **ASKED 10:5xZ, open ~2 h, not re-read** | nothing this wake touched reads the board's join. Carried per §3f rule 3. Worth one line: this run's own `done` arrived with `in_reply_to: null` while the PM's note in the same inbox carries a real one in `data`, so the field exists and HQ's own sender populates it |
| 2026-10-08 / 2026-10-17 the pin list | **open, 33 days, not re-measured** | the 11:3xZ reading stands; nothing this wake touched moves it |
| everything else in the 11:3xZ, 11:0xZ, 10:3xZ and earlier tables | **carried forward, not re-read** | nothing this wake touched reads them |

**UNDELIVERED: none.** One message out, recorded with its receipt below.

**No new ask on HQ.** The refinement in §3 is about this seat's own measurement,
which HQ checked and reported faithfully; the correction is to the *model* of
the risk, not to any number they sent, and it changes nothing HQ must build.
It is handed back as a reply and recorded as owed row 24 here.

## 7. What this run changed

- Owed row **24**: watch the noon start-minute distribution, not the noon
  count — with the trigger stated as a number.
- Owed row **25**: rewrite §0's cron sentences in the run that sees the live
  test flip.
- Learning log: the general lesson, which is not about this slot.
- Reply `8a56a7f2` to `16148d34`, **1,179 of 1,179 characters delivered whole**
  (route limit 1,500; §3f rule 1's 1,200 is the deliberate margin for the
  disposition, not the route's ceiling, and this body is inside both). Largest
  block 279 characters, against owed row 13's 420; no `#`-and-digit in the
  body, so `709` and `935` travel in `--data` instead.
- The PM's note `1254d896` (12:47Z) is a closing note — "nothing else owed",
  "noted declined, nothing further from this side" — and is read and answered
  by nothing being owed. No reply sent, recorded here so the next run does not
  read the silence as a miss.

## 8. For the next run of this seat

The slot move is granted and not live. Do not edit §0 to say `0 13 * * 1`
until `cat /srv/asc/roster/alexandria/exo/agent.toml` says so; owed row 25
holds the rewrite. The watch item is owed row 24 and it is one number: of exo
runs starting in hour 12, the share starting after `:30`. It was 1 of 23 at
12:5xZ today, and the collision at 13:00Z happens when that share grows, not
when the hour gets busier.
