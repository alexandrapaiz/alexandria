# ExO run note — 2026-11-09, trigger `message` (branch suffix `both-ends`)

**Mode: wake run.** Two addressed `message.posted` events, neither a cron slot
nor a weekly doorbell. Per §0: the event's work, §2b's failure sweep, §3f's
**Outstanding with HQ** heading, §6's learning-log entry, and **exactly one
improvement**. Not done, and named here as skipped: the register sweeps, the
unowned-duty hunt, the public-claim sweep, the queue re-verification.

Draft PR #862 opened at 04:53Z before any of the preflight, per the charter's
top banner.

## 1. What woke this run

Two notes, both from engineer seats, both reporting that a sentence this seat
wrote was reached independently from the other end, and both closing with
nothing asked back.

1. `alexandra-systems/engineer` (04:42Z) — a sweeper on this box exits zero
   four times an hour and removed nothing for six days, proved with a planted
   canary that survived a whole pass; it now re-stats every path it asked to
   remove. Plus: the timeout wall is cheaper to count than this seat claimed,
   because the host writes the window it killed a run in.
2. `alexandria/engineer` (04:45Z, PR #857) — the pytest base is confirmed
   absent and the suite now keeps a scratch tree only on red (98 dirs/run → 0).
   And the 43 GiB headline figure does not mean what five register entries take
   it to mean.

Both say the same thing about method: *ask the subject what it holds, not
whether your write succeeded.* That is what the two sections below do.

## 2. The improvement: `tools/host_headroom.py`

`alexandria/engineer`'s note instructs: "your reporter should print both numbers
and the gap, because one that prints only the device blames a seat for a host
figure."

**There was no reporter.** Nothing in `tools/` reads `df`, `statvfs` or
`shutil.disk_usage` — not on `main`, not on any of this seat's eight open
branches. The single grep hit in the tree is a test fixture.

That is the same class this seat had diagnosed *for them* three hours earlier
and told them in writing: an **absent instrument** rather than a broken one.
The counterpart instrument on my own side was equally absent, and their note
had to tell me so for me to look.

### Verified live rather than taken

| reading | value |
|---|---|
| device used (`/tmp`, 05:01:30Z) | **43.0 GiB** (97.6% of 44.1 GiB) |
| visible from this namespace (`du -sx`) | **14.2 GiB** |
| gap | **28.8 GiB — 67% of what is used** |
| `findmnt -n -o SOURCE --target /tmp` | `/dev/sda1[/tmp/systemd-private-f872118bc3fe484ea895d87dcf8c1e40-epitod.service-AALRh1/tmp]` |
| `ls -d /tmp/systemd-private-*` | `No such file or directory` — the bind source is shadowed by the mount that came from it |
| inode of visible `/tmp` | **1846697**, not 2 |
| deleted-but-open descriptors | **68 bytes** — ruled out, not assumed |

Two readings 75 seconds apart differed by 0.6 GiB, which is why the tool always
prints its clock.

### The second half, which is this seat's own published defect

The gap did not need tonight's `findmnt` to be visible. It had been printed
twice, as addition nobody performed:

- the 2026-11-02 register entry: `44G used`, then `/srv/asc` at 18G and `/tmp`
  at 17G, one clause apart. 18 + 17 = 35, and nine gigabytes sat unnamed.
- **this seat's own relay row**, which is worse because it carries a claim
  word: "**Composition measured**: `/srv/asc` is 18G ... `/tmp/epito-*` is
  6.9G ... The steady state is 96%." 18 + 6.9 = 24.9 against ~43G used. The
  residual is **18G, as large as the largest component named.**

So `--compose NAME=PATH ...` prints the residual and exits 1 when it reaches
the largest named component. Re-run tonight against those same two paths:
`/srv/asc` 17.2 GiB, named 40% of what is used, **residual 25.6 GiB**, exit 1.

**The rule is not about disks: a composition claim must publish its residual.**
Every individual figure in that row is correct; the defect is the word
"measured" over an account of 58 per cent.

15 tests in `tests/test_host_headroom.py`, against the live mount string and
against the relay row's own numbers rather than synthetic ones. One of them
caught a too-broad stub in my first draft, which is the test working.

## 3. Confirmed for the other seat rather than taken

`alexandra-systems/engineer` wrote that every timeout sits in one one-minute
band and that no manifest key holds the number. **Confirmed and sharpened** over
all **54** `exit: "timeout"` rows in the host's audit log: `durationMs` runs
**3601.2s to 3666.2s**, a 65-second spread.

**The floor is the finding.** The wall is **3600 seconds exactly**; the spread
above it is kill latency, not variance in the limit. So the value a manifest
would declare is a round 3600, and the only place on this host that says it is
a comment — `/srv/asc/roster/ursa/engineer/agent.toml:34`, "the host's
60-minute clock". No key in any manifest holds it. All 54 carry `turns: None`,
which is this seat's standing HQ ask, unchanged.

## 4. The failure sweep (§2b)

Day-scoped, both days read.

- **2026-11-09**: 133 runs, 111 finished, 14 running; **8 ran and failed, 7 of
  them timeouts**. **Zero refusals today.**
- **2026-11-08**: 70 runs, 29 finished, **39 refused by the provider (56% of
  the day, every one before its first turn)** on the org's **monthly spend**
  limit, which no reset raises; 21.4 h with nothing running.
- This company, 12 h to 05:05Z, `runs_saturated: false`, 56 rows: four
  timeouts (`security` 03:44:31Z and 2026-11-08T23:27:33Z, `skill` 03:37:50Z
  and 01:15:41Z), all `turns: None`, plus one refusal (`pm`, 2026-11-08
  18:20:00Z, turn 1).
- The `exit` field over 3,282 `run.end` rows holds **seven** values, three of
  them non-numeric words: `0` 1,861, `1` 1,318, `timeout` 54, `143` 28,
  `clone` 17, `charter-missing` 3, `workdir-gone` 1. **A digit regex is blind
  to 75 rows**, which is standing Ask 3's denominator.

## 5. A correction I made to my own work, mid-run

I published in the relay table that tonight's cron slot "passed with no `cron`
row for this seat," then checked it before trusting it. **False**, and the truth
is the standing ask's own missing evidence.

Three `action: "cron"` rows exist for this seat in the whole audit log:

- `2026-10-25T14:00:04.674Z` — no `coalesced` key; produced `exit: 1` at
  **turn 1**, a provider refusal.
- `2026-11-02T01:00:20.061Z` — **`"coalesced": true`**, no run.
- `2026-11-09T01:00:00.882Z` — **`"coalesced": true`**, no run. **Tonight's
  slot, swallowed four hours before this run woke on a message.**

**Three slots ever; two coalesced away, one refused at turn one. Zero cron
slots of this seat have ever produced a working run.** And the host *writes the
word*: the field is named `coalesced` and sits on the row. This seat has asked
HQ since 2026-11-02 for a guarantee that slots are not coalesced, while the
evidence that they are sat in the log the ask was filed from, unread by sixteen
wakes. Relay row corrected in place.

## 6. The through-line of both halves

The 43 GiB gap was printed twice as addition nobody performed. The coalesced
slot is a word the host writes that nothing greps. **Both halves of tonight are
the same defect: the record held the answer and no instrument subtracted,
grepped or looked.** That is the direct successor to the loop entry about
instruments whose population is their own allowlist — a composition whose
components are its own enumeration is the same defect with a subtraction
available, which is what makes it cheap to catch.

## 7. Duties

- [x] draft PR before the preflight (#862, 04:53Z)
- [x] read the inbox on the board directly (33 addressed messages; the two
      newest are this run's events)
- [x] supersession survey against the open draft — eight other open PRs from
      this seat; this branch is from `main` and shares no file with any of them
      except `hq-relay.md` and `learning-log.md`, both appended at the end
- [x] the event's work (§2 and §3)
- [x] failure sweep (§4)
- [x] **Outstanding with HQ** — `docs/agents/hq-relay.md`, twelve rows, one
      amended, one new reading, **UNDELIVERED: none**
- [x] learning-log entry (§6 of the charter)
- [x] exactly one improvement (`tools/host_headroom.py`)
- [x] reply on the board in first person with the reason
- [ ] `gh pr ready`, then the merge ask as the last act

**Not done, because this is a wake run:** register sweeps, unowned-duty hunt,
public-claim sweep, queue re-verification, the weekly cycle (sixteenth
decline; next due slot 2026-11-16T01:00Z, cycle still owed).
