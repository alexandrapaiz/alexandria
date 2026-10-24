# ExO run note, 2026-10-24, the duty-classes wake

Mode: **wake run** (`window:message`), woken by the merge of PR #492. The
event asked for the next item in this seat's lane on the board. The lane held
five cards: two in Done, two in Review, and exactly one outside both, so there
was no choice to make.

**What I took:** *The nine unevidenced duty rows split into three classes, and
the owner's word is pending on two*, created 2026-10-24T22:18:37Z by the wake
forty minutes before this one.

**What I found:** its class A half does not hold, and the card's own first
recommendation — "say what is true on this page first" — was the half that
needed no owner word and had not been done.

## The one-paragraph version

Class A said `market`, `research` and `security` "are not running at all",
cited zero cron firings and zero pull requests since 2026-10-17 from two
independent sources, and asked the owner to choose between waking the three
seats and marking them dormant. All three are working. Each ran its last
scheduled slot on time and shipped a pull request that merged. The claim was
measured in a window in which **no seat of this company had a loaded cron at
all**, so its reading of zero was the same reading a healthy seat would have
produced, which is precondition 6 of the charter's §0 exactly.

## The two numbers that settle it, both local

`/srv/asc/roster` is a symlink into a working clone at
`/srv/asc/repos/alexandra-systems`, which the host moves with
`git reset --hard`. The clone's reflog is therefore the deploy history, and it
needs no network.

Across its **77 entries**, the six seats I checked take three states and no
others: absent before 2026-09-24T02:56:48Z, present **with no cron line at
all** from 2026-09-24T04:11:25Z, and carrying the crons the repository
declares only from **2026-10-23T17:03:01Z**. GitHub's `schedule:` blocks were
deleted on 2026-10-17. So between those two dates this company had no clock in
either runtime.

Inside the 29.9 hours the scheduler has demonstrably been covering, **four
alexandria slots came due and four fired** — `engineer` twice, `pm` once,
`writer` once. `market`, `research` and `security` had **zero** due, and so
did `exo`, `frontend`, `skill` and `okr`. Three seats of twelve have had their
clock tested at all.

## What the three seats actually did

| Seat | Last scheduled run | Conclusion | Shipped |
|---|---|---|---|
| research | 2026-10-12T23:07:16Z | `success` | `research/2026-10-12`, PR #284, merged |
| security | 2026-10-15T17:25:09Z | `success` | `sec/2026-10-15`, PR #307, merged |
| market | 2026-10-16T15:18:33Z | `success` | `market/2026-10-16`, PR #316, merged |

Each becomes answerable on a date rather than on a decision: `research`
2026-10-26T16:30Z, `market` 2026-10-30T11:00Z, `security` 2026-11-01T13:00Z.

## The hole, and why its distribution is the finding

The clockless stretch from 2026-10-17T17:59:54Z to 2026-10-23T17:03:01Z
swallowed **29 alexandria cron slots**: `engineer` 12, `pm` 6, `writer` 6,
one each for `exo`, `frontend`, `skill`, `market` and `research`, and none for
`security` or `okr`.

The daily seats lost 24 slots between them and **no instrument in this
organization reported it**, because events kept all three awake and a seat
that is working does not notice which door it came through. The weekly seats
lost one slot each, which is their whole week. That is the shape to carry: a
redundant trigger does not prevent an outage, it conceals one.

## The thread the stale date pulled

Class A put `security`'s last pull request on 2026-10-05. It is 2026-10-15.
The seat ships under `alexandria-security/` on a host run and `sec/` on a cron
run, the second being what its own charter tells it to use, and the sweep knew
one era's convention.

Following that: the bus resolves a merged branch's first path segment, strips
`<company>-`, and requires the remainder to name a seat in the roster. Three
charters name `sec/`, `fin/` and `fe/`. The roster holds `security`,
`finance` and `frontend`. **A prefix that names no seat produces no target**,
so those three seats route `pr.merged` and `check.failed` to nobody, silently,
with no log line and no counter.

And behind that, for one of the three, a second defect the first was hiding.
`company.yaml` declares `security` as `cadence: semimonthly`, and the bus
suppresses a seat's own-merge continue-wake only for `monthly`, `quarterly`,
`dispatch-only` and `none`. Run through the bus's own `seat_cadences` parser
against our `company.yaml`, `security` is the one row of twelve that is slower
than a day and still qualifies.

So the obvious one-line repair would have turned a deaf seat into a seat that
wakes itself on every merge, which is HQ's finance loop of 2026-10-18
reproduced exactly. `frontend` and `finance` are corrected here. `security` is
**held on purpose**, with both defects and the ordering written into its own
charter, and the one-word ask is with HQ.

## What this run deliberately did not do

It is a wake run, so it skipped §2c's second half, the unowned-duty hunt, the
register-gate polarity pass, the public-claim sweep, the per-anchor queue
re-verification and the §5b repository sweep. That owed list is now seventeen
wake runs deep and it is in the learning log, unchanged by this run.
