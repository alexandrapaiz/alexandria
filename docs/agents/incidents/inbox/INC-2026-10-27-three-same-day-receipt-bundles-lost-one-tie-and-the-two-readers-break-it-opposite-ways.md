## INC-2026-10-27-three-same-day-receipt-bundles-lost-one-tie-and-the-two-readers-break-it-opposite-ways - the fifth same-day receipt collision, and no filename can satisfy both readers (2026-10-27, skill seat, hook run after a capacity return)

**What happened.** This run revised `skills/agent-containment/SKILL.md` and
`skills/agent-security-measurement/SKILL.md`, so both shas moved, and re-ran the
trigger suite into
`skills/_validation/results/2026-10-27-lexical-2.1-span-removal-and-cost-ordering.json`,
which scores all nine skills against the shipped text at 58 of 67. The receipts
check still reported both revised skills STALE, naming
`2026-10-27-lexical-2.1-harness-and-loops-corrections.json` as the newest
receipt. Three bundles already carried `generated: 2026-10-27`, written by this
seat's three earlier runs of the same day, and `rank_bundles` sorts on that date
with a pre-registered tie-break that all four satisfy. The sort is stable and
`load_bundles` feeds it `sorted(glob.glob(...))`, so the tie fell to the
alphabetically first filename, and `harness-and-loops` precedes
`span-removal`.

**Why it is in this register.** It is the third record of one defect and the
fifth collision. `docs/ideas.md` carries it from 2026-09-30 as "sorts on
`generated`, which is a date and not a timestamp."
`INC-2026-10-26-the-library-shows-the-older-of-two-receipts-dated-the-same-day`
records it with a symptom and ends "the next day two bundles land, it recurs."
Four bundles landed instead of two, and `superseded/README.md` already held four
same-day pairs from 2026-10-26 before this run added three more files.

**What is new, and it is the half that kills the obvious workaround.** The
earlier entry says the two consumers "disagree about which receipt is newest."
They disagree in **opposite directions on a lexical tie**, which means the
disagreement cannot be settled by naming the file well.
`skills/_validation/trigger_test.py` keeps the alphabetically **first** name,
because `rank_bundles` is a stable sort over a sorted glob.
`tools/panel_validator.py` takes `sorted(results.glob("*.json"), reverse=True)`
and keeps the alphabetically **last**. `site/lib/content.js` globs and takes
whatever the filesystem listed. So a name chosen to pass the receipts gate is a
name chosen to make the panel quote the other bundle, and neither rule is
recency. Moving the losers out of the glob is the only mitigation all three
readers agree on, which is why that directory grows rather than the names
getting cleverer.

**What it cost.** Three turns of this run: one to write a bundle that lost,
one to read the ranking code and find out why, one to move three pairs and
re-check. Call it the same price the 2026-10-26 run paid, now paid a second
time, which is the whole argument for fixing the ranking rather than the
directory. The 2026-10-26 run also paid it, so two runs of one seat have now
spent a turn each on a sort key.

**The fix, or why there is not one yet.** Unchanged and still owed: give
`generated` a time, or tie-break `rank_bundles` and `rankBundles` on a recorded
timestamp, and record the library composition in `policy` so a receipt says what
it was measured against. It is one sort key in two files. Both
`site/lib/content.js` and `tools/panel_validator.py` are outside this seat's
write boundary, and `skills/_validation/trigger_test.py` is inside it but its
own docstring says the rule "has to stay the same rule or this check and the
page disagree about which bundle is the library's result", so changing one side
alone would make the disagreement worse rather than better. Registered duty:
engineer. This run did what the last one did, which is move the superseded
bundles to `skills/_validation/results/superseded/` with their comparison
written down. Nothing is deleted and the gate passes honestly.

**Further instance, 2026-11-02, skill seat, PR #688.**

Three bundles again carried one date. `2026-11-02-lexical-2.1-routed-corrections`
(from #669), `2026-11-02-lexical-2.1-adr40-certificates` (from #675) and
`2026-11-02-lexical-2.1-caption-correction` (this run). `trigger_test.py
--receipts` kept the alphabetically first, `adr40-certificates`, and reported
`skill-library-engineering` STALE against a receipt that measures the
pre-correction text. The run that had just re-run the trigger test and committed
its bundle in the same commit as the `SKILL.md` edit, exactly as the gate's own
error message instructs, still got a red gate for it.

So the instruction the tool prints is not sufficient on a day when the same seat
ships twice, and this seat shipped three times on 2026-11-02. The mitigation was
again to move the two older bundles into `results/superseded/`, which is the
third consecutive day that directory has grown for this reason. Nothing new is
proposed here: the repair is still a timestamp in `generated` plus the library
membership recorded in the bundle, and it is still in the ledger.

**Further instance, 2026-11-02, skill seat, PR #706, and the first one that
arrived from the other direction.** Two bundles carried `2026-11-02` under
lexical/2.2: `2026-11-02-lexical-2.2-instrument-repairs.json` from the previous
run of this seat, and `2026-11-02-lexical-2.2-delta3-third-paper.json` from this
one, written after revising `skill-library-engineering` delta 3.

Every instance recorded above was discovered by `trigger_test.py --receipts`
going red. This one passed that gate clean, all nine receipts reported as
describing today's text, and failed `tools/panel_validator.py`, which said
`skill-library-engineering` was "measured against an earlier text
(43f9a8f08daadd2e, and this one is 596ea1c9e2a73054)". A seat that ran only the
gate its own charter names would have shipped believing the receipt was current.

This is the opposite-directions claim observed from its other side, so it is now
confirmed rather than reasoned. `delta3-third-paper` sorts before
`instrument-repairs`, so the stable sort over a sorted glob in `trigger_test.py`
kept the correct new bundle while the `reverse=True` sort in
`panel_validator.py` kept the stale one. Name this run's bundle anything sorting
after `instrument-repairs` and the two verdicts swap. There is no filename that
satisfies both, which is exactly what the entry above says, and the practical
consequence for the next seat is that **passing `--receipts` is not evidence the
receipt is current.** Run `tools/panel_validator.py` as well, and when they
disagree the newer measurement is the right one regardless of which gate is
complaining.

The mitigation was the same holding pattern as every entry above, which is the
fifth consecutive day for it: the superseded pair moved to
`skills/_validation/results/superseded/` with its comparison written into that
directory's README. The pair is a clean control, since the delta 3 revision left
the `description` byte-identical and all nine suites scored identically across
the two bundles at 61 of 67.

The repair is unchanged and still owed, and this instance narrows it by one
sentence. A timestamp in `generated` fixes the ordering, and it does not fix the
fact that two readers implement two different rules. The tie-break has to be one
function the gate, the panel and the page all call. It is registered to the
engineer and it is in the ledger.

**Sixth consecutive day, 2026-11-02, skill seat, and the configuration is the
one this entry predicted.** Four lexical bundles carried the date 2026-11-02 by
the time this run wrote its own: `approval-paths`, `containment-horizon`,
`mechanism-column` and then `parallax-asm`. `trigger_test.py` sorts a sorted
glob with a stable sort, so the first of the four won and `--receipts` reported
`agent-security-measurement` STALE against `approval-paths` while holding this
run's correct, newer bundle in the same directory. That is the gate a seat is
told to run before committing a SKILL.md edit telling the seat its current
measurement is the stale one, which is the sentence at the end of the entry
above arriving from its third side. The mitigation was the documented holding
pattern again: the three earlier bundles moved to `results/superseded/`, which
leaves one same-day bundle and no tie. This run did not observe the
`panel_validator.py` half, because the files were moved before that reader was
run, so the opposite-direction claim is reasoned from `reverse=True` here rather
than measured, and `parallax-asm` sorting last of the four is what would have
made the two readers disagree. The repair is unchanged and still owed to the
engineer: one tie-break function that the gate, the panel and the page all call,
on a timestamp rather than a date.
