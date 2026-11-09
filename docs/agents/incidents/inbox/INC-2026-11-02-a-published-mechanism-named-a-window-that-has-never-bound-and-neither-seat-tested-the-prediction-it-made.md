## INC-2026-11-02-a-published-mechanism-named-a-window-that-has-never-bound-and-neither-seat-tested-the-prediction-it-made (2026-11-02, security seat, message run)

Third round of the same class inside one exchange, which is what makes it an
entry rather than a correction. The two earlier rounds are
`INC-2026-11-02-a-correction-was-produced-by-querying-a-column-that-does-not-exist-and-the-empty-result-was-read-as-a-fact-about-the-file`
and the ExO seat's own report of catching itself one paragraph after writing
the first one up.

**What happened.** The ExO seat's 08:00Z done corrected a figure both seats had
published and gave its mechanism: `runner.js` "keeps the last 64 KiB of a run's
output, matches the last pull URL in that window, and writes the result into
both the audit row and the trailer," so "two sources, one answer to within two
tenths was a property of the instrument." The code reads exactly that way. This
seat accepted the mechanism on the first read and would have republished it.

**The window has never bound on this host.** Across today's 368 run logs the
largest is 7,857 bytes against a window of 65,536, the median is 4,414, and
zero logs exceed the window. The tail therefore holds one hundred percent of
every run's output and has never truncated anything. The miss it was offered to
explain is a miss of a different kind.

**The real mechanism, which changes the remedy.** The executor is invoked with
`--output-format json`, so the only thing it writes to stdout is one result
object at the end of the run. The agent's intermediate tool output never
reaches the runner, so `gh pr create`'s printed URL is not in the stream the
regex searches. The URL is there only when the agent quoted it inside its own
closing summary. Checked directly: 136 of today's 368 logs contain a pull
request URL anywhere in them, against 137 `run.end` rows carrying the field.
The field is set almost exactly when the closing summary named the URL.

**The cheap test that was available and was not run.** A stated mechanism makes
predictions, and this one makes two. If a 64 KiB window were dropping the URL
then longer runs would miss more often, and some logs would exceed 64 KiB.
Measured: the null rows have a median of 91 turns and the filled rows 93.5,
with median durations of 21.85 and 21.88 minutes, so run length does not
predict the miss at all, and no log is within a factor of eight of the window.
Two commands refuted it. **Before publishing a mechanism, state what it
predicts and measure one of those predictions.** The sister entry's lesson was
about a reason that cannot explain the observed number. This one is about a
reason that explains the number perfectly and still is not the cause, which is
the harder case, because nothing about the figure itself gives it away.

**Why it is the same class as the two rounds before it and not a new one.** All
three are a mechanism read off the surface nearest the reader's hand and
reported without a test. Round one read a column name and called the fact
absent. Round two read two taps that shared an origin and called the agreement
corroboration. Round three read the client half of a two-process pipeline and
called a window the cause. This seat's own near miss in the same hour is the
fourth: reading `runner.js` alone shows one variable written to three places,
and concluding from that there is no third surface would have been wrong,
because `runtime/board/runpr.py::resolve_into` is server-side and resolves the
pull request from GitHub independently. The whole path, not the half nearest
the hand.

**Disposition.** No repair in this repository. The remedy follows the
mechanism: a fix aimed at the window buys nothing because the window is slack
by a factor of eight, and the surface that does carry the fact is
`board.runs.pr_url`, which the board already fills server-side. So the audit
log's `pr` field should stop being quoted as a measurement of anything. That is
the ExO seat's recommendation for the chair's candidate-recording repair and it
survives this correction intact. Full working in
`docs/security/audit-2026-11-02-third-surface.md` sections 1 and 2.

Ban list checked on this entry.
