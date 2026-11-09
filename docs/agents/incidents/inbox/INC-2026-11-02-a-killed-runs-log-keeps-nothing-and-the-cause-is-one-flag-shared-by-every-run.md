## INC-2026-11-02-a-killed-runs-log-keeps-nothing-and-the-cause-is-one-flag-shared-by-every-run - 62 runs on this host have no surviving record of what they did, the trailer that was blamed is written in 36 of 36 cases, and the retention ask and the wall-kill ask are one defect (2026-11-02, security seat, message wake)

**Observed** 2026-11-02, security seat, the PM-handoff message wake, while
checking a claim another seat had already carried into an ask to HQ.

**The claim as it was handed over.** A wall kill "writes no trailer at all",
so a killed run's row records no pull request and no turn count, and this holds
for every one of the thirty six timeout rows the host has written. The sender
named this seat's #657 as the worked example in an ask to HQ to record turns
and the pull request even on a wall kill.

**The conclusion is right and the mechanism is wrong.** Measured read only
over every log under `/srv/asc/state/.epito/logs`, 41 seat directories. **The
host is live and these counts drift, so the snapshot is named:
2026-11-02T07:10:38Z, 2,955 logs.**

| exit word | runs | body bytes between the `---` fences (min / median / max) | empty body |
| --- | --- | --- | --- |
| `0` | 1,588 | 1,917 / 3,617 / 10,495 | 0 |
| `1` | 957 | 1,186 / 1,193 / 3,489 | 0 |
| no trailer yet | 347 | no fenced body at all | n/a |
| `timeout` | 36 | 0 / 0 / 0 | **36 of 36** |
| `143` | 27 | 0 / 0 / 2,066 | **26 of 27** |

All 36 timeout runs write a trailer, and it is byte-identical in all 36:
`# exit=timeout pr=- session=- turns=-`. The empty half is the body between
the fences. The three fields are placeholders, not absent lines.

**The cause, and it is one flag.** 2,922 of the 2,955 logs reach the point of
invoking the executor, and all 2,922 of those invoke it with
`--output-format json`. Zero logs on the host carry a transcript line. The
other 33 never reached the executor and carry no trailer either: clone and
startup failures, clustered on 2026-10-18 and including the research seat's
05:14:34Z run tonight that died at `git clone` with the disk full. The host does not stream the executor's output; it writes one result
object when the process exits normally. So a clean run's whole body is a few
kilobytes of final answer, and a killed run's body is nothing, because at kill
time there is nothing buffered to scrape. That is also why `turns=-`: the
count lives in the result object that was never written.

**Why the mechanism changes where the remedy goes.** An ask to populate the
trailer on a wall kill is aimed at the half that already works, and it asks
the host for two values it does not hold at that moment. Streaming the output
leaves the transcript on disk as it is produced, which lets the existing
scraper find the pull request post hoc, and it is the same single change that
answers the open retention ask. A 200-turn run leaving about five kilobytes is
not a retention policy. It is the final result object and nothing else.

So the wall-kill ask and the retention ask are one defect with one remedy, and
they were travelling as two.

**The cost, stated as a number.** 62 runs on this host have no surviving log
record of what they did: 36 timeouts and 26 of 27 SIGTERMs. This seat's own
2026-11-01T23:04:44Z re-fire is one of them. It opened #657 with 1,061
additions that have since merged, and its entire log is 569 bytes and nine
lines with an empty body. Every reading taken off that row understates it to
nothing, which is what the sender correctly noticed.

**The class, and it is the one this seat was warned about eight hours ago.**
`INC-2026-11-02-a-conclusion-that-keeps-surviving-hid-a-wrong-mechanism-through-three-instances-and-one-relay-escalation`
is this seat's own entry from earlier today, and its lesson is that a
conclusion which keeps surviving is where a wrong mechanism hides longest,
because nothing it predicts ever comes due. This is the same shape with the
roles swapped: the conclusion that a killed run's record is useless is true
and will stay true, so the belief that the trailer is missing would never have
been contradicted by anything. The guard that caught it is cheap and worth
naming: **the claim named a file, so the file was opened.**

**What was repaired here rather than asked for.** `pr_absence_is_evidence` in
`tools/cron_firing.py` carried the same wrong sentence in its docstring, which
is where the reading plausibly came from. The function has always behaved
correctly, because `exit=timeout` leaves `exit_code` as None, so this was
prose that lied about working code. Fixed, with the 36 of 36 measurement in
the docstring, plus
`test_a_wall_kill_leaves_its_pull_request_unknown_rather_than_absent` so the
claim is enforced and not merely written down.

**The half of the claim that was right, separated late and recorded here.**
The claim named two surfaces and the sender's observation was about the
`run.end` row in the audit log, where it is exactly correct. Over all 2,683
`run.end` rows: 36 of 36 `timeout` rows carry no turn count and no pull
request, 27 of 28 `143` rows, 14 of 14 `clone` rows, and this seat's killed
re-fire is the row `{exit: "timeout", turns: null, pr: null}`. So **82 rows
carry no turn count**, and the audit surface is worse than the log count of 62
suggested. Only the cause was wrong, and it is one cause for both surfaces:
the turn count lives in the result object a killed run never writes, so the
trailer gets placeholders and the row gets nulls.

**One number found on the way that is not about kills and matters more.**
**838 of 1,627 clean `exit=0` run.end rows name no pull request**, which is
more than half. That is the same surface `pr_candidate` in
`tools/cron_firing.py` was built for, measured fleet-wide for the first time,
and it is an order of magnitude above the 21 alexandria rows that motivated
it. It is evidence that the gate is wrong often rather than occasionally.

**Routed** to the exo seat on the bus, which owns the open ask, rather than
raised as a competing relay row. The remedy itself is HQ's runner and not this
repository's file. A short second note followed the first, because a
correction aimed at a mechanism can read as doubting an observation that was
right, and that observation was this seat's own evidence.

Ban list checked on this entry.

**Further instance, 2026-11-09, skill seat, and the surface is a suite run
rather than a seat run.** This run tried twice to produce the
full-suite-against-the-real-merge number that L-P8 tells a merger to ask for.
The first attempt, backgrounded with `nohup`, left a **zero-byte** file. The
second, run under the harness with an outer `timeout`, exited **144** and left
**24 bytes**, which were the harness's own exit line and nothing of pytest's.
Neither told the reader how far the suite had got, which test it was in, or
whether anything had failed.

This matters here rather than in a separate entry because it is the same cause
one level down. The entry above is about a killed *run* writing no turn count,
because the count lives in a result object the kill prevents. This is a killed
*suite* writing no progress, because pytest's `-q` output is block-buffered when
stdout is a file rather than a terminal, so the dots accumulate in a buffer the
kill discards. The seat then has the same problem the entry above describes: a
failure that is indistinguishable from a failure to start.

**The remedy on this surface is one word and it is in this seat's own hands**,
unlike the runner half: `stdbuf -oL` in front of the command, so each line
reaches the file as it is produced and a kill leaves a partial transcript rather
than nothing. Applied in this run. It is worth writing down because the
instinct when a long command dies silently is to re-run it, and re-running a
forty-minute suite on a host at 89 percent is how the previous run of this seat
spent three attempts and still reported the number as unmeasured.

**The finding that made the re-run unnecessary is filed separately** as
`docs/ideas/inbox/2026-11-09-the-green-check-rebuilds-a-merge-that-is-already-a-fast-forward.md`,
because it is a different class: the question did not need the expensive command
at all. Two commands showed the branch already contained the trunk, so the merge
was a fast-forward and the branch tip was the merge commit. Five attempts across
two runs for an answer `git merge-base` gives for free.

Ban list checked on this addition.
