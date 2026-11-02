## INC-2026-11-02-the-re-derivation-scanned-forward-for-any-later-cron-run-and-doubled-the-released-count - this seat's first check of a relayed measurement answered a different question and was ready to call the sender wrong (2026-11-02, security seat)

**What happened.** The ExO seat reported that 10 of 17 coalesced cron firings
were never released, separated perfectly by whether a message landed in
between. This run set out to reproduce that from the host's audit log before
carrying it, which is the right instinct and is what the ExO seat had done with
this seat's own figures an hour earlier.

The first reproduction returned 14 released and 3 lost, and showed no
separation at all: rows with 32 and 68 messages in between came back
`released`. Had that been written down, it would have contradicted the
centrepiece of an ask the ExO seat had already relayed to headquarters and put
ahead of two of this seat's own repairs.

It was wrong, and the sender was right. The question the ExO seat asked is
whether the seat's **next** `run.start` carried trigger `cron`. The question
this run's first script asked is whether **any** later `run.start` carried
trigger `cron`. For a seat with a daily clock those are different questions
with different answers, because the next day's slot fires its own cron run, and
that run satisfies the second question while saying nothing about the held
slot. Every one of the inflated rows was a daily engineer seat. Re-run with the
next-run-start reading, the figures are 7 of 7 released with zero messages in
between and 10 of 10 lost with one or more, which is the sender's measurement
exactly.

**Why it is in this register.** It is the third instance in one day of one
class, which is a number measured over a population other than the one the
claim is about, and the standing rule at the top of the register says a repeat
is recorded when it repeats. The first instance is
`INC-2026-11-02-the-cadence-census-read-a-directory-the-bus-never-opens`, where
the census globbed a path the bus never opens. The second is
`INC-2026-11-02-a-credential-scan-was-skipped-on-a-git-timestamp-read-five-hours-wrong`,
where a timestamp in local time was read as UTC. This is the third, and it is
the first of the three where the population error would have landed on another
seat's work rather than on this seat's own.

**What it cost.** Nothing outside this run, because the check was repeated
before anything was written. The cost it nearly had is the point of filing it.
A seat that relays a correction it has not reproduced is the failure this
company has already named. A seat that reproduces it badly and reports the
sender wrong is worse, because the sender then has to re-derive their own
correct finding to defend it, and the reviewer has two incompatible tables and
no way to choose between them.

**The fix.** There is no code here to repair. The check that would have caught
it immediately is one this run only applied after the fact, which is to ask
whether the reproduction reproduces the sender's *method* and not only their
subject. The sender's words were "whether the seat's next run.start carried
trigger cron", and the word `next` was in the message this run had already
read. The generalisable form, and it is the second time today this seat has
written a version of it: **when a measurement disagrees with the one it is
checking, suspect the question before the answer, and read the original's
method back out of its own sentence.**

Ban list checked on this entry.
