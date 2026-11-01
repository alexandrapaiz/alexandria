## INC-2026-11-01-a-count-read-off-the-re-fire-record-mid-drain-is-a-progress-bar-not-a-measurement - this run read a file something else was still writing, got a confident alarming wrong number, and caught it only because it read twice (2026-11-01, exo seat)

**What happened.** At **2026-11-01T23:05Z** this run read
`/srv/asc/state/.epito/capacity-retry.json` and found **8** seats. It had just
measured **31** seats refused on the weekly limit. The subtraction gave a
finding that was specific, alarming and ready to ship: *23 of 31 refused seats
get no re-fire at all, and 76 refused cron slots across 21 seats are
unrecovered.* It survived two rounds of adversarial checking — a write-race
hypothesis was tested and eliminated (most unqueued seats were refused alone in
their own second), a daemon-restart hypothesis was eliminated (no `daemon.start`
row since 2026-10-31), and a last-run-per-seat hypothesis was eliminated. At
**23:10Z** the same file held **11** seats, including three — `finance`, `okr`,
`ursa-finance` — that were absent five minutes before. The `hook` rows in
`audit.jsonl` settle it: **8 hooks at 23:04, 3 hooks at 23:09, 11 hooks and 11
entries, exact match.** The file is not a queue of pending claims that can be
short. It is an **append-only record of re-fires already issued**, written in
waves minutes apart as the host works through the refused seats, and a read
taken during the drain is a partial count of progress rather than a total.

**Why it is in this register.** This is the third sighting of §2b's standing
lesson about believing a number an instrument hands you, and the first where the
instrument was *correct* and the **reading** was mistimed. The first two were
adversarial selection in instruments that sample failures
(`INC-2026-10-24-eighty-of-ninety-nine-failures-were-refusals-and-the-field-that-says-so-is-always-null`,
`INC-2026-10-24-the-refusal-column-is-filled-for-the-refusals-that-cost-nothing`);
the third was a remedy that records the cheapest instance
(`INC-2026-10-27-the-capacity-retry-rescues-the-seat-and-claims-the-cheapest-of-its-refused-runs`).
That 2026-10-27 filing read the **same file** and recorded "claims in
`capacity-retry.json`: **20, one per seat, none missing**", treating
one-per-seat-none-missing as an invariant. It was not wrong: it was taken on a
43-minute session window whose drain had finished, so the file was final when it
was read. Nothing in that note or in §2b said the reading had a validity window,
so the next run to read the file mid-drain had no sentence to stop it. It is
also the second sighting this week of
`INC-2026-10-27-two-readers-answer-a-wrong-seat-name-with-a-confident-zero`
generalised: **prove the instrument is finished before you believe a total from
it**, which is the same shape as proving it can see the seat before you believe
a zero.

**What it cost.** Nothing shipped, which is the only reason this is cheap: the
error was caught at turn 30 by a second read taken for an unrelated reason. Had
it shipped, the cost would have been a false incident naming 23 seats and 76
lost cron slots, handed to HQ as a defect in a mechanism that was working
correctly — and the 2026-10-25 register correction already warns that this
family of false positive "would retire three working seats." Four turns of this
run went to hypotheses that were eliminating a cause for an effect that did not
exist.

**The fix, or why there is not one yet.** Shipped with this filing, as this wake
run's one improvement: §2b gains the reading rule. Never quote a count from
`capacity-retry.json` without a second read minutes later; never compare it to a
refusal total during the hour after a limit reset; and when the two reads differ,
the file is still being written and no total from it is quotable yet. The
charter carries the **wrong** version of the finding as its worked example,
because a near miss teaches the rule better than the corrected number does.
One thing is deliberately left open rather than resolved: whether the drain
reaches all 31 refused seats is unknown — it stood at 11 of 31 at 23:10Z, and
this run says so with its clock rather than guessing, which is the rule applied
to itself.
