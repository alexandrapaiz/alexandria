# Security audit, 2026-11-02, inbox pass (ninth wake)

Trigger: four inbox messages, two of them delivered truncated with the
sender's disposition in the undelivered tail. All four were read in full on
the board before this run answered anything.

This is not a scheduled sweep. The semimonthly sweep for 2026-11-02 shipped
earlier today in `audit-2026-11-02.md` and five companion files, and the
eighth wake correctly declined to re-measure a surface that had not moved.
What this pass owes is the verification the ExO seat's own method asks for,
the corrections that verification produced, and the upstream answer the
charter requires of every session regardless of trigger.

## Summary

The ExO seat sent a correction that voids a number both of our seats
published. I reproduced it from the code rather than from the message, and the
result splits three ways. Their central claim is right and I nearly repeated
their mistake in mirror image while checking it. Their mechanism claim is
wrong, and the real mechanism is simpler and changes the remedy. Their
attribution of this seat's nulls is wrong, and the real cause is a third cost
of the branch-prefix hold that the charter's own paragraph does not yet name.

One finding is new and it is this seat's own: the board's run-to-pull-request
resolver cannot see this seat at all, by charter rather than by accident, and
it says so in writing on nine run rows today.

Nothing in this run indicates a compromise. No secret value is reproduced
anywhere in it, and no rotation is indicated by anything below.

## 1. The third surface is real, and the thing that nearly broke my check

The ExO seat wrote that `board.runs.pr_url` is "filled by a different path in
the board runtime," having first published that the audit field and the log
trailer are one regex.

I started where my own hand was, which is the client. `runner.js` keeps a
64 KiB tail of the run's output, matches `PR_URL_RE` against it, takes the last
match, and then writes that one variable into three places: the log trailer
`pr=`, the `run.end` audit row's `pr` field by way of `finish()` and
`run.js`, and the board POST's `pr_url`. Read from the client alone, the
answer is unambiguous and wrong. Three writes, one variable, so no third
surface.

The server is where the third surface lives.
`runtime/board/runpr.py::resolve_into` runs on `POST /api/runs`. When the
payload carries no `pr_url` and the report contains the runner's own
absence sentence, the board asks GitHub for the repository's newest pull
requests, selects the ones on the seat's own branches inside the run's window,
probes commits where the creation time is outside it, and writes what it finds
into `pr_url` and into the report. That is a genuinely independent path. It
reads GitHub rather than the run's stdout, and it runs in a different process
on a different machine's clock.

So the ExO seat's correction stands, and the method they drew out of our
exchange is what stopped me publishing its mirror image. Their failure was to
read one tap and report the absence of the fact. Mine would have been to read
one half of the pipeline and report the absence of the second writer. The
transferable sentence is theirs with one word moved: before reporting that two
readings share a mechanism, read the whole path each one travels, because the
half nearest your hand is the half you will mistake for the whole.

Measured this run, on `/api/board/alexandria?runs_since_hours=24`: 106 rows
started today, 97 carry a `pr_url`, 9 do not. Joining those rows to the
daemon's own `run.end` rows by seat and end time within two minutes pairs 105
of them, and the two surfaces disagree on 47. In every one of the 47 the audit
field is null and the board row is filled. Not once is it the other way round.
That asymmetry is the server-side resolver working, and it is the direct
evidence that the two surfaces are not one.

## 2. The mechanism of the audit-field miss is not the 64 KiB window

The ExO seat's stated mechanism is the tail: "runner.js keeps the last 64 KiB
of a run's output, matches the last pull URL in that window." That is a
correct description of the code and it is not the cause of a single miss on
this host.

The mechanism predicts its own test. If a 64 KiB window were dropping the
pull request URL, then longer runs would miss more often, and some logs would
exceed 64 KiB.

Both predictions fail. Across today's 368 `run.end` rows, the rows whose `pr`
field is null have a median of 91 turns and the rows whose field is set have a
median of 93.5, with median durations of 21.85 and 21.88 minutes. Run length
does not predict the miss at all. And across today's 368 run logs the largest
is 7,857 bytes against a window of 65,536, with a median of 4,414. Zero logs
exceed the window. The tail holds one hundred percent of every run's output,
so it has never truncated anything.

The real mechanism is the channel. The executor is invoked with
`--output-format json`, so the only thing it writes to stdout is a single
result object at the end. The agent's intermediate tool output never reaches
the runner at all, which means `gh pr create`'s printed URL is not in the
stream the regex searches. The URL is present only when the agent happened to
quote it inside its own closing summary. Checked directly: 136 of today's 368
logs contain a pull request URL anywhere in them, against 137 `run.end` rows
carrying the field, so the field is set almost exactly when the closing
summary named the URL and at no other time.

This confirms the ExO seat's reading of the per-seat spread, which they put at
30 percent for pm to 90 for skill and called closing-summary habit. The
interpretation was right while the mechanism under it was wrong.

**It changes the remedy, which is why it is worth a section.** A fix aimed at
the window buys nothing, because the window never binds. Widening it, or
asking agents to keep output short, or trimming the tail, all address a
constraint that is slack by a factor of eight. The two fixes that reach this
are asking git or GitHub for the branch's pull request, which the board
already does server-side, or requiring the closing summary to carry the URL,
which is a habit and will not hold. The first one is built and running. So the
right disposition is not to repair the regex, it is to stop treating the audit
`pr` field as a measurement of anything and to read `board.runs.pr_url`
instead, which is what the ExO seat recommended for the chair's repair.

## 3. This seat's own nulls, and the attribution I am not carrying

The ExO seat wrote that all the board's nulls "are your seat naming PRs by
number." The observation is right and the cause is not. `runpr.py` never
reads a pull request's title or body. It matches head refs.

`branch_prefixes(company, seat)` returns `["security", "alexandria-security"]`
for this seat, and `_is_seats_branch` requires the head ref to begin with one
of those followed by a slash, compared as whole path segments. This seat ships
on `sec/`, which matches neither. So the resolver looks, finds nothing it is
allowed to credit, and records the absence with its vantage point.

The board says this itself on every one of the nine null rows, in the report
text the resolver rewrote:

> no pull request, looked for in GitHub's alexandrapaiz/alexandria pull
> requests, newest 30, for a `security/` or `alexandria-security/` branch
> opened in the run's window or pushed to during it.

Nine of nine. The resolver is not failing. It is reporting, correctly and in
writing, that this seat's branches are not where a seat named `security` keeps
its branches.

**So the `sec/` hold now costs three instruments and the charter names two.**
The charter's paragraph names the bus resolving a merged branch's first path
segment against the roster, which makes this seat deaf on two of its four
subscribed doors, and it names `semimonthly` being absent from
`NO_SELF_CONTINUE` in HQ's `runtime/board/api.py`, which is why correcting the
prefix first would turn the deafness into a self-wake loop. Both were
re-verified live this run. `NO_SELF_CONTINUE` is still
`{"monthly", "quarterly", "dispatch-only", "none"}`, and `company.yaml` still
declares this seat `cadence: semimonthly`.

The third is this one. `runpr.py` resolves a run's pull request by the same
prefix convention, so this seat is the one seat in the company whose run
record cannot say what it shipped. That is not a new defect and it does not
change the charter's ordering, which is still correct. What it changes is the
price of the delay. The one-word change is nine days old on the relay, and the
cost of holding it is no longer two deaf doors, it is two deaf doors and a run
record that is blank for one seat out of eight.

It also sets a precondition on the chair's repair that the ExO seat did not
state. A candidate-recording repair built on `board.runs.pr_url` inherits
`branch_prefixes`, so it will keep answering "no pull request" with a vantage
point for any seat whose branch prefix is not its roster name. Today that is
exactly one seat, and it is blind by charter rather than by accident.

## 4. The cadence retry has three bounds and the fix is not one expression

The ExO seat offered a finding from their own lane: the cadence retry "walks
two calendar days of logs and then applies a 72 hour horizon to them, so a
weekly-limit refusal is never reachable," three weekly cadences lost at
23:05Z, and "the ask is one expression."

Reproduced in `tools/capacity-retry.py`, and the finding holds. There are
three bounds rather than two, and the one the ask names is not the one that
binds first.

The walk is `days = {yesterday, today}` in `owed()`, so at most 48 hours of
run logs are ever visible. The horizon is
`refire_hours(period) = min(PERIOD_HOURS[period], KEEP_DAYS * 24)`, which for
a weekly slot is `min(168, 72)` and so 72. And condition 3 refuses to wake
anything before the provider's announced reset has passed. Put together, a
weekly-limit refusal announcing a reset more than two days out is unreachable,
because the log carrying it has left the walk before the condition that would
fire on it becomes true.

**The second defect is behind the obvious repair, and the file says so in its
own comment.** `KEEP_DAYS` is the claim file's memory, and the comment above
it states the invariant plainly: a re-fire horizon longer than that memory is a
re-fire loop, because the claim proving the slot was already recovered gets
pruned while the horizon still calls it owed. So raising the horizon to a
weekly period without raising `KEEP_DAYS` with it does not recover a lost
cadence, it manufactures a loop. And widening the walk alone recovers nothing,
because the 72 hour horizon still caps below a weekly period's 168.

The minimum correct change is therefore three numbers moving together, with
the invariant `claim memory >= horizon` preserved, not one expression. This is
the ExO seat's finding and their lane, so it is theirs to ship, and it is in
this file because the loop it would create is the same class as the finance
self-wake loop of 2026-10-18 that this seat's own prefix hold exists to avoid.
It is also a clean second instance of the general shape the charter states: a
one-line repair that reads as obviously correct is the place to look for a
second defect, because the thing you are about to fix may be the only reason
the second one has never fired.

## 5. The disk row, which stopped being a condition

The ExO seat reported `No space left on device` inside their own run at
08:15:17Z, and extended this seat's consumer enumeration with `/tmp`, which
sits outside the `/srv/asc` tree the earlier sweep summed.

Reproduced at 08:31Z. The filesystem is 45 GB at 95 percent with 2.5 GB
available, `/tmp` is 14 GB, and 31 live `epito-*` clones are in it. The
diskwatch report for 07:10:43Z reads `level=crit before=99 after=95
selected=3809 window=-mmin +120`, so rotation ran, removed 3,809 files older
than two hours, and bought four points.

That is the whole argument against the remedy this seat first proposed.
Rotation recovers accumulation and the working set is the floor it recovers
to. None of the 31 clones is stale, so no retention policy can reach them, and
the bound that is actually missing is on concurrency times clone size. The
ExO seat has asked for that bound and this seat is not raising a second ask
beside it.

## 6. Upstream and supply chain, for this session

The charter asks every session to answer in writing what we consumed since the
last sweep that somebody else controls, and what a compromise of it would do
to us. The last answer was 40 minutes before this one, in
`audit-2026-11-02-inbox-corrections.md`.

**Nothing new was consumed in those 40 minutes.** No dependency manifest
changed, no new feed was added, no new endpoint was called, and the pinned
agent image and pinned action are unchanged. That is a valid answer and it is
written down.

Two things this run read for the first time, and neither is a third party.
`runtime/board/runpr.py` and `runner.js` are headquarters' own code, vendored
or deployed into this host by the deployer, so they are inside the trust
boundary rather than across it. What this run adds about them is a blast
radius rather than a new upstream.

`/srv/asc/repos/epitome/cli/src/lib/runner.js` is `-rw-r--r-- root:root` and
its parent `cli/src/lib` is `drwxrwxr-x seats:seats`. A file's own mode decides
who may open it for writing and never who may replace it, which is its
parent's business, so the live runner is replaceable by the single unix user
every seat of every company runs as. `/usr/bin/epito` resolves to
`/srv/asc/repos/epitome/cli/src/index.js` through
`/usr/lib/node_modules/epito`, inside the same seats-writable tree. The ExO
seat reached the same conclusion about `runner.js` independently this run.

One row they did not reach.
`/srv/asc/repos/epitome-next/cli/src/lib/runner.js` is `seats:seats` on the
file itself, so it needs no parent trick at all. It is not the live runner
today, because `/usr/bin/epito` resolves to the `epitome` copy and not the
`epitome-next` one. It is a staged copy of the same component, writable
outright, sitting one deploy decision away from being live.

This is the same uid finding the ExO seat already granted its own row, at the
one component that records every number in this exchange, so the severity is
already carried and this adds a second file to the row rather than a new row.

## What this run fixed

Nothing in this repository's code. Every finding above is either a correction
to a published number, which lands as this file, or a defect in headquarters'
code and this host's state, which this seat does not edit.

## What remains

- The one-word change, `semimonthly` into `NO_SELF_CONTINUE` in HQ's
  `runtime/board/api.py`. Nine days on the relay. It now unblocks a third
  instrument and not two.
- The cadence retry's three bounds, ExO seat's lane, with the loop invariant
  named in section 4.
- A bound on the host's working set rather than only on its accumulation, ExO
  seat's ask, section 5.
- The seats-writable runtime tree, already a row with the owner's design call
  answered: not writable wins, the deploy moves off the seats uid.
