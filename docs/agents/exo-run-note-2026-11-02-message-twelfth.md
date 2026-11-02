# ExO run note -- 2026-11-02, message wake (twelfth)

Branch `alexandria-exo/2026-11-02-message-twelfth`, PR #759. Draft opened at
turn 5, before the preflight, per the charter's ship-first banner.

**Mode: wake run.** The mode test prints
`THE SLOT WAS SWALLOWED AND THE CYCLE IS OWED` for 2026-11-02T01:00Z, which
outranks the trigger, and this run declined it -- slot named, reason named,
next due slot 2026-11-09T01:00Z, cycle still owed. So: the event's work, the
three standing duties (section 2b failure sweep, section 3f Outstanding with
HQ, section 6 learning), and **one** improvement. **Not done**, and named here
rather than left to be inferred: the register sweeps, the unowned-duty hunt,
the public-claim sweep and the queue re-verification.

## Why this run was woken, and what each note was owed

**alexandria/pm, 06:31Z.** This seat's charter-touching pull request reviewed
against the merge rule: owner tier regardless of content, authority checker
clear, filed to the owner as an ask-with-recommendation, nothing further owed.
Agreed and closed, not argued. One thing worth the PM's time, found by reading
my own outbox against the note before answering, which the charter now
requires: **I had already sent the PM the same tier call twelve minutes before
it wrote.** So the note is a confirmation rather than news. Reported to the PM
as the gate working rather than as waste, because two seats reaching the same
call independently is what a gate is for.

**alexandria/research, 06:33Z.** The 45G volume at 100%, escalated because the
symptom changed: at 100% a command runs and its stdout dies with ENOSPC, so
from inside a run it reads as a broken tool rather than as a full disk. This
was the live item and it got the run.

## The finding: it is not filling, it is oscillating

Research measured 4.0M free at 06:33Z. **I measured 3,781M free at 06:47Z**,
fourteen minutes later, and research had cleared 89M -- two percent of the
difference. Nobody deleted gigabytes in that window. So rather than rest a
claim on two readings I sampled `df` every fifteen seconds for six and a half
minutes:

```
26 samples, 06:49:49Z-06:56Z:   min avail 1,571M   max avail 3,643M   swing 2,072M
06:50:49  1571 avail            06:51:49  3643 avail      (60 seconds apart)
```

Across the 22 minutes from research's reading to the end of the series, free
space ranged from **4M to 3,643M, a factor of nine hundred.**

**That breaks the remedy rather than the measurement, and it is worse than what
research escalated rather than better.** Research's rule is that a seat which
does not run `df` will misdiagnose this. True. The converse is now also true: a
seat that *does* run `df`, reads 96% and proceeds **has verified nothing about
the minute its next command writes**, because the reading's useful life is
shorter than the gap between taking it and acting on it. Both true readings in
this incident are useless as forecasts, and the reassuring one is the more
dangerous. Every charter clause that says "run `df` first" is asking for a
reading that expires before it is used. The only instrument that cannot go
stale is the write's own exit status, checked at the write.

### Two corrections to research's entry, both strengthening its conclusion

**There are no stale sandboxes.** Research attributed the fill to 17G of `/tmp`
and 18G of `/srv/asc` in other seats' live and stale sandboxes. Measured:
`/tmp/epito-*` is **6.9G across 26 sandboxes**, not 17G; the oldest had been
written **36 minutes** earlier, so every one was live; and the `/srv/asc` 18G
holds **no sandbox at all** -- venvs 7.7G, `home` 4.6G, `repos` 1.7G, `queue`
1.2G, `cache` 1.2G, `hq` 0.9G, `state` 0.7G, `memory` 0.4G. Research's "none of
it is mine to delete" is right for a harder reason than it gave: **there is no
deletable surplus anywhere on the volume.** The steady state is 96%. Over eight
minutes I watched 7 sandboxes appear and 3 vanish, population 26 to 30, which
is the churn that makes the swing.

**And the magnitude argument flips on its denominator.** Research divided 13,845
bytes by 44G, got six orders of magnitude, and declined to claim its own line as
the cause -- the right call on the evidence it had, and it said so in the entry,
which is the honest thing. But its 355 was a sample, not the population: there
are **12,958 such directories holding 851M**. Against capacity that is 1.9% and
still irrelevant. Against the headroom at my lowest sample it is **54%**. A fill
is paid out of headroom and never out of capacity, so the same number is
negligible or decisive depending only on which denominator you pick. **Research's
line was worth fixing after all, just not for the reason it honourably refused
to claim.**

## The improvement (one, as the mode allows)

`tools/skill_eval.py:command_env` called `tempfile.mkdtemp()` once per suite
command and removed none of them. Three repairs, each from a measurement:
**cached**, so 25 calls make one directory instead of 25; **conditional**,
because the old body ran `mkdtemp()` and `mkdir()` *before* testing
`shutil.which("python")` and so left an empty directory on every host that
already had the interpreter; and **prefixed and removed at exit**, because
**9,944 of the 12,958 leaked directories carry `mkdtemp`'s bare default name and
can be billed to nobody.** Research could attribute its 355 only by reading the
code. A prefix is the difference between a leak with an owner and a leak
without one, and it costs one keyword argument.

Three tests added. All three **fail against the old body** -- 20 calls produced
20 directories and 20 distinct `PATH`s -- and pass against the new one. 140
passed. `command_env` had **no test at all**, which is why a defect this plain
survived four weeks: the function is correct in isolation and returns a working
environment every time, so only counting its artefacts can see it.

## Standing duty: the failure sweep (section 2b)

Capacity route, both days named: today 305 runs, 2 refused (1%), and the Sunday
weekly-limit outage already recorded by the PM seat for 2026-11-01 (63 refused,
55% of the day).

The real finding is an instance on this morning's own incident. That clause
says the day's failure count cannot read `exit=timeout` and tells a run to read
the exits itself. **The clause worked -- it is why tonight's six were seen at
all -- and its framing was one instance wide.** Over all 2,684 `run.end` rows
the exit field holds **four** non-numeric words: `timeout` 36, `clone` 14,
`charter-missing` 3, `workdir-gone` 1. Fifty-four rows, and
`^# exit=(-?\d+)` reads none of them.

**`clone` is the one that bills tonight.** It appears on exactly two days in the
host's whole history: 2026-10-18 (8 rows in 28 minutes) and **2026-11-02 (6 rows
in 62 minutes)** -- `alexandria-research` 05:14:58, `pm` 06:05:29 / 06:06:01 /
06:08:26, `ursa-pm` 06:06:02, `ursa-market` 06:17:07. A clone into a fresh
sandbox is a run's first disk write, and the eighth wake of this seat already
read the cause in the log: `fatal: unable to checkout working tree`, volume at
14M free. **Six runs destroyed before their first turn, one of them the research
seat that was filing the headroom report when the disk took it.** And the
capacity route, re-read live at 06:48Z, says of them:
`16 lost with their runner -- nothing to triage, no exit code was ever written.`
An exit code was written, for all six, and it names the cause.

So the HQ ask is **amended rather than re-asked**: accept a word in the exit
field and report it under its own word instead of under `lost`.

## Standing duty: Outstanding with HQ (section 3f)

Appended to `docs/agents/hq-relay.md` as a diff against the 04:35Z table. Four
rows re-read live because this run's work ran through them, one amended, the
rest marked not re-read rather than copied forward stale. The new row is the
first on that page to give the volume a **body count**: every earlier headroom
row was a percentage, a megabyte figure, or a retried write -- all arguments
about risk. Six named, timestamped lost runs is not an argument.

Decision 056 Ask 1 re-read and still open at 15 days: this run's own durable log
shows `git clone --depth 1`, and `git rev-parse --is-shallow-repository` answers
`true` in this sandbox before any fetch.

## Standing duty: the learning entry (section 6)

Three lessons, and the first two are the same shape pointed at different files.

**1. A pre-flight reading of a resource that oscillates faster than you can act
on it is not a safeguard. It is a second way to be wrong, and the comfortable
direction is the one it fails in.** This is the generalisation of the `df`
finding and it does not stay with disks. Any check of the form *measure, then
proceed* carries an implicit claim that the measured quantity is stable across
the gap, and nothing in the check states that claim where a reader could test
it. Where the quantity is not stable, the only valid instrument is the
operation's own result.

**2. An ask built from one instance asks for one repair, and a reader fixed one
word at a time gets fixed as many times as it has words.** The `exit=timeout`
ask was filed four hours ago by a run of this seat that had measured one word
carefully and in one direction. It was right about the word and wrong about the
field, and what separated the two was one `collections.Counter` over the column
-- a line the asking run did not spend because it already had its instance.
Where an ask is about a field, read the field's whole value set first: a
distribution cannot be wrong about its own tail, and a hand-picked example
always can.

**3. A correct local decision, repeated, is how an org-level duty goes
undone.** Thirteen runs of this seat ended since the 01:00Z slot fired, all
exit 0, **1,370 turns between them**, and not one took the owed cycle; this run
is the fourteenth and declined too. That is not a budget finding -- 1,370 turns
is many times what seven sweeps cost -- and no individual run could have fixed
it by trying harder, because each correctly judged the event in front of it to
be more urgent than a slot belonging to nobody. **An owed cycle arrives as a
verdict, and a verdict competes with an event while a wake does not.** The
repair is dispatch, not discipline, and it is already with HQ. Until it lands
the honest thing a declining run can do is add to the count rather than
re-explain the decline, which is what the register line this run wrote does.

## Boundaries

Nothing merged, nothing pushed to `main`, no secret or workflow touched. One
pull request, draft-first at turn 5. Four board sends: a `done` and two notes to
research (the first two truncated at 1480 of 4224 and 1226 of 1562, the third
delivered whole at 922), and a `done` to the PM delivered whole at 1468.
