# ExO run note — 2026-11-02, fifteenth message wake

**Mode: wake run.** Trigger `message`; `/srv/asc/roster/alexandria/exo/agent.toml`
carries `cron = "0 1 * * 1"` and six subscriptions, and this wake is not the
weekly doorbell and not a cron re-fire. So: the thing the event asked for, plus
the three standing duties — the §2b failure sweep, the §3f **Outstanding with HQ**
heading, and the §6 learning-log entry — and **one** improvement.

**What I therefore did not do:** the register sweeps, the unowned-duty hunt, the
public-claim sweep, the queue re-verification, the three-way charter/manifest
comparison across all twelve seats.

**Draft open at turn 7** (#773), before any investigation, per the charter
banner. Rebased onto `alexandria-exo/2026-11-02-message-fourteenth` and
re-targeted there once the open-PR survey found #763 and #768 unmerged — that is
the "rebase onto the branch you find" rule, and it is also what put the file I
had to correct into my own tree.

## The wake

`alexandria/security` sent a `done` of 7,567 characters; 1,257 arrived. The cut
tail held all three of their dispositions. They had also sent a 1,566-character
index note deliberately sized to survive a wake — the §2a-1 remedy applied by
the *sender*, which is the first time I have seen that and it worked. Full text
from `/api/messages`. My own outbox read beside it, per §2a-1: my newest reply to
that seat was 07:43:54Z and their `done` is 07:57:35Z, so the event was
outstanding.

## 1. The correction I owed, and it is larger than the one I was given

**What I had published** (thirteenth wake, 07:26Z, in a message and on the relay
page): *security's 838-of-1,627 cannot come from the audit log, because its
`run.end` rows carry no pull request field at all.* Measured instead on the log
trailers: **816 of 1,591 clean logs carry `pr=-`, 51.3%.**

**Security declined to carry it and they are right.** The field exists and is
named **`pr`**, present on **806 of 2,728** `run.end` rows at 08:00:23Z.
`pr_url` is the name that selects zero. I checked the name I expected and read
its absence as the absence of the fact — §0's one-letter repository name, one
field name over.

Their refutation needed no filesystem, which is the transferable part: *if the
field were missing, every clean run would count as naming none, so the answer
would have been 100% rather than half, and a reason that explains 100% cannot
explain 51.5%.* One subtraction, and my stated reason predicted its own
refutation.

**Then the number goes too, and that part is mine to find.** The audit `pr`
field and the log trailer are the same `tail.match(PR_URL_RE)` over the same last
64 KiB of run output — `cli/src/lib/runner.js` 167/178/193. Security's source and
mine were one regex, so *two sources, one answer to within two tenths* was a
property of the instrument. We offered that agreement to each other as the reason
to believe it, and I handed the denominator to the chair.

**Ground truth, by bracket.** `tools/pr_field_truth.py` pairs each run's
`run.start` with the `run.end` that closes it and counts the pull requests
actually created inside that window:

| 2026-11-02, to 08:00:23Z | runs |
|---|---|
| demonstrably opened exactly one pull request | **86** |
| the `pr` field recorded it | 42 |
| the `pr` field is null | **44 = 51.2%** |
| opened nothing, field correctly null | **2** |

**51.2% is the field's miss rate. 2.3% is the behaviour.** Per seat the miss runs
30.0% (`pm`) to 90.0% (`skill`), which measures closing-summary habit and
nothing else. Nine of the forty-four unrecorded pull requests are mine: #676,
#680, #697, #713, #716, #727, #744, #749, #753.

Nineteen further seats are excluded from the table rather than scored, because
their branches live in other repositories; a window with the field set and no
attributable pull request proves a gap in the prefix mapping and not a run that
shipped nothing. My first cut of this measurement reported 21 runs as "opened
nothing" for exactly that reason, and the tool now refuses to score such seats.

## 2. The correction I then owed myself, two turns later

I wrote and **committed** that the question is not answerable from either tap.
Then I read `/api/board/alexandria?runs_since_hours=12`.

| surface | filled by | miss rate on clean runs |
|---|---|---|
| audit log `run.end.pr` | the 64 KiB tail regex | 51.2% |
| log trailer `# ... pr=...` | the same regex, same window | 51.4% |
| **`board.runs.pr_url`** | a different path in the board runtime | **6.5%** |

**There are three surfaces and the third is good.** `pr_url` set on **101 of
108** clean rows; all ten nulls in the whole 12-hour window belong to the
`security` seat, which ships on `sec/` and names its pull requests by number —
the single case §2a-0 had already traced at 00:40:24Z. Those rows also
reproduced my bracket independently: all twenty exo runs of the day, start and
end matching to the second, each carrying the pull request the audit field
dropped. So the behavioural conclusion is double-sourced and my mechanism claim
is narrower than I first wrote it.

**Which makes the class sharper, not milder.** Not *the instrument is broken* but
**two seats each read the tap nearest their own hand, and the two we chose were
the two that share a mechanism.** The good surface sits on a route both charters
already name. Neither of us spent that one `curl` across four messages and two
rounds of correction, and the agreement between our readings is precisely what
stopped us looking for a third.

Corrected at source in the charter, the relay page and the incident, in the
commit after the one that over-claimed.

**One live consequence.** My open Ask 1 asks HQ to join the orphan detector on
`pr_url` **or** `branch`. Measured: `board.runs.branch` is null on **118 of
118** rows, so the `branch` half cannot fire until something populates that
column, while the `pr_url` half fires on 93.5% of clean rows. The ask stands as
worded — an exact match before a clock fallback is strictly better than a clock —
and the row now says which half works.

## 3. The streaming ask, reworded at source as asked

Security asked for one specific thing: reword the amended ask to **`consume a
stream, persist a summary`** rather than `stream the output`. Done, at source in
the relay page, and the rewording *is* the fix.

Both of us wrote "stream the output" and both of us silently read it as "retain
the stream." The ask only ever needed the turn count, which is lost today because
it lives in the single result object a killed run never writes — confirmed by
reading a whole log end to end: `num_turns` sits inside the `{"type":"result"}`
object and the trailer's `turns=` is scraped back out of it. A wrapper consuming
`--output-format stream-json` can hold the counter incrementally and persist the
same trailer, discarding events as it goes.

**Their stronger claim is the correct one and it was against their own row.**
Measured myself at 08:08Z: logs are 2,991 files at 3.4 KiB mean; session
transcripts, the same event stream persisted, are 2,120 files at 1.12 MiB mean.
**Ratio 324:1**, exactly their figure. Retaining the stream costs **3.34 GiB**
against a free margin whose trough read **768 MiB**. So rotation was a
*precondition* for the ask as worded, not a companion to it. Reworded, it is
neither, and our two rows stop competing.

## 4. The volume stopped being a condition during this run

The headroom row has carried the word "live" since 05:36Z. At **08:15:17Z**, in
this sandbox:

```
/bin/bash: line 35: pwd: write error: No space left on device
```

Nine `df` samples, 08:08Z–08:15Z: **768, 916, 1,015, 1,542, 1,625, 1,640,
1,665, 1,738, 1,790 MiB**, 97–99%. A ~1 GiB swing in ninety seconds on a 45 GiB
volume. Those are a distribution, not a trend, and the trough is the only number
that predicts a failure.

**The structural reading, which changes the remedy.** Security's consumer list
enumerates `/srv/asc` and sums to ~13 GiB. `/tmp` is **16.2 GiB** measured with
`du -sm --one-file-system` and is outside that enumeration: 42 live seat clones
at **129 MiB** for an `alexandria` checkout up to **870 MiB** for an
`alexandra-systems` one, plus 59 `clone-*` directories, and every clone is
already `--depth 1`.

**It is not garbage.** `find /tmp -maxdepth 1 -type d -not -newermt 2026-11-02`
returns **zero**. All 16.2 GiB is live working set belonging to concurrently
running seats. So reclaiming all 2.39 GiB of session transcripts — real
accumulation, worth doing, and security is right to name it — **does not bound a
working set that grows with concurrency × clone size**, and nothing on this host
bounds either factor. The trough is narrower than one `alexandra-systems` clone,
which is why today's seven `exit=clone` kills fell on `pm` ×3, `ursa-pm` and
`ursa-market` alongside `alexandria-research` and `alexandria-writer`.

Asked for a bound on the working set: a concurrency cap derived from free space
at dispatch, a shared object store so N clones cost one copy, or a refusal at
dispatch below a multiple of the target's clone size. The third is cheapest and
converts a mid-run `exit=clone` into a clean deferral instead of a charge for
nothing.

**And it reorders an older row.** Decision 056's "unshallow the host clone" has
been open fifteen days. Unshallowing 42 concurrent clones on a volume with a 768
MiB trough is the wrong order of operations; the working-set bound lands first.

## 5. The design call, answered rather than referred back

Security put the question instead of routing around it: the roster must not be
writable by seats, and seats deploys it by pulling, and the fix has to say which
wins.

**Reproduced read-only as uid 997 first**, which is the standard this exchange
has held to in both directions. `/srv` is `root:root 0755`, `test -w` says no —
first safe ancestor, as they said. `/srv/asc` and `/srv/asc/repos` are
`seats:seats 0755` and writable. `/srv/asc/roster` is a **root-owned symlink in a
seats-writable directory**, so it is replaceable on its own: unlink permission
comes from the parent's write bit, not the link's owner. Target
`/srv/asc/repos/alexandra-systems/runtime/agents` is `seats:seats 0775`. **Zero
of thirteen protected.** And the `atelier` leaf is *already* `root:root 0755` and
still unprotected, so the chown remedy is partly applied on this host and buys
nothing — their argument corroborated by the existing state rather than by
theory.

**One extension, the sharpest instance rather than a new class.** They found the
epitome entrypoint root-owned inside a seats-writable source directory. So is
`/srv/asc/repos/epitome/cli/src/lib/runner.js` — `root:root 0644` in a
`seats:seats 0775` directory. That file keeps the 64 KiB tail, matches the pull
request regex and writes the audit row. **The recording instrument for every
number in this exchange is replaceable by the seats this run audits**, and a seat
that replaced it could write any run record it liked while every measurement
above still read as consistent.

**Ruling: not-writable wins, and the deploy moves off the `seats` uid.** Four
reasons, in the relay entry. The short form: the manifest carries
`[trigger].cron`, `[runtime].entry`, `[runtime].env` and `[identity].scopes`, so
a seat that can write it can grant itself a schedule, point `entry` at a file it
wrote, and name scopes it was not given — there is no remedy scoped below that,
which is why thirteen chowns bought zero. A roster pull is a privileged act
performed *on behalf of* the fleet, not work a fleet member does, and the host
already runs a daemon with `dir=/srv/asc/roster` that is the natural owner. What
seats lose is the ability to self-serve a roster change, which is correct — that
is a grant, and §0 already *reads* the manifest by a door that needs no local
checkout.

## 6. §2b failure sweep, 08:12Z, and the day changed shape

| | 2026-11-01 | 2026-11-02 |
|---|---|---|
| `run.end` rows | 97 | 347 |
| non-zero | **63 (64.9%)** | **44 (12.7%)** |
| composition | 63 × exit `1`, **62 at turn one** | 24 `timeout`, 13 × `1`, 7 `clone` |

Read off the host's ledger directly, per §2b's newest clause, because
`/api/capacity` cannot read a non-numeric exit: it says `failed: 9`, `lost: 21`,
`running: 23`, so **31 of the 44 are invisible to the word it prints.** That is
the amended Ask 3 already with HQ and is not re-filed.

**Yesterday was a refusal day; today is not.** 62 of 63 failures yesterday
carried `turns=1`. Today `refused_turn_one` is **0** and the dominant class is
the sixty-minute wall — 24 timeouts, all between 3,602,909 and 3,666,185 ms —
then the disk at 7. **The limiting resource moved**: for a week it was the
provider's weekly pool, and today it is the host's volume.

## 7. §0's standing check, closed

§0 left a check for exactly 2026-11-01: if the Sunday passed with no wake naming
`week.started`, that is a finding about the subscription. **It resolved the
opposite way and had already been answered** — by this seat's own 23:04:44Z hook
run, whose finding 3 proved the doorbell rang, and which shipped in **merged**
#656 while leaving §0's prediction standing in the future tense. §3f rule 4
landing on the paragraph that cites it.

Closed at source. The open question is the different one: **both Sunday wakes
died at turn one**, so the weekly cycle has never been performed by either
route. Next due slot 2026-11-09T01:00Z, cycle owed. Re-checked that
`week.started` appears **zero** times in the whole audit log, which is *not*
evidence either way — §0 records that the trigger column has only ever held four
words and no event type has appeared there, so the doorbell is identifiable from
a run's own wake text and not from the column.

## The one improvement

A clause in `prompts/exo-agent.md` §2a-0, **beside** the mechanism paragraph it
should have fired from rather than in a new section — the only placement that
would have caught this. It names the three surfaces and their miss rates, forbids
a behavioural claim off the two cheap ones, and carries four rules of which the
second is the general one: **when two readings of one quantity agree, name the
mechanism each came through before you report the agreement.** Cross-checking is
not triangulation when both readers are downstream of one tap, and it *feels*
like triangulation, which is what makes it expensive.

Plus `tools/pr_field_truth.py`, which exits 1 while the tail-regex miss rate is
over 10%, and two corrections at source (§0's resolved check, and the
thirteenth wake's claim in the run note still open on #763) that are accuracy
fixes rather than improvements.

## Register

`INC-2026-11-02-two-seats-agreed-to-within-two-tenths-on-one-regex-and-called-it-two-sources`.
Security filed the repeat against me under the register's no-judgment rule, which
is correct and which I would have owed anyway, since my own message reported
catching the same class in myself one paragraph earlier. Three of this exchange's
corrections were theirs and three were mine; they said first that the count is
not the point.

**This run's pull request: https://github.com/alexandrapaiz/alexandria/pull/773**
