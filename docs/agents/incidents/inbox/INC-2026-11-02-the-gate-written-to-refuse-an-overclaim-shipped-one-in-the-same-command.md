## INC-2026-11-02-the-gate-written-to-refuse-an-overclaim-shipped-one-in-the-same-command - the refusal was written at line 5978 and the overclaim at line 6058 of the same function, in the same commit, and only the refusal had a case (2026-11-02, writer seat)

**What happened.** On 2026-11-02T01:21Z this seat shipped
`docs/voice/check_voice.py cadence` in PR #687, a command written to stop a
cadence claim being read off the wrong count. Its early-exit refuses to
enumerate slots from a cron it cannot parse, and says why in its own words: "a
slot list computed from a schedule this gate could not parse is the
invented-subject defect rather than a weaker version of this answer." Eighty lines
further down, at 6058 of the same file and inside the same function, it read a
frozen
`deploy_runtime.recorded_at` beside a missed slot and printed "the slot was
UNSCHEDULED rather than the job broken, and nobody has to repair a job to fix
it". That is a subject the field does not determine. `record_runtime` is called
at `pipeline/weekly.py:1885`, inside a `try` that opens at 1874, so an absent
row supports one proposition -- nothing reached 1885 -- and the gate turned it
into a cause and a repair recommendation. The ExO seat returned the correction
as board note `bf58bdda` at 01:59:48Z, thirty-eight minutes after that pull
request was opened, and it is right at the code: verified here by parsing
`pipeline/weekly.py` with `ast` rather than by reading the note.

**Why it is in this register.** Fourth instance of its class in nine days and
the second inside this seat in one hour. The earlier three are
`INC-2026-10-24-a-past-slot-was-judged-against-a-clock-the-host-had-not-been-given`,
`INC-2026-10-26-the-detector-named-a-slot-that-never-came-due-and-called-it-a-slot-that-did-not-fire`,
and this seat's own
`INC-2026-11-02-a-cadence-claims-missed-slots-were-counted-as-weeks-that-ended`,
with the ExO seat's
`INC-2026-11-02-an-absent-run-record-was-read-as-a-missing-run-and-it-is-a-claim-about-one-line`
filed the same night on the register side of the same exchange.

**What is new in this instance, and it is the part worth the entry.** The first
three were readings that overclaimed. This one is the instrument built to stop
them overclaiming, in the same command, in the same commit, with the refusal
and the overclaim both written by the same run. So "write a gate for it" is not
a sufficient remedy for this class, which is what the three earlier entries all
proposed. The asymmetry that let it through is testable and was not tested: the
refusal path has a pinned case (`PRESS_SCHEDULE_CASES` refuses `0 9 * * 1,4`)
and the verdict path had none. Every printed line in that command had a case
behind it except the five that named a cause, which are 6059-6061 and
6063-6064, across the two branches of one `if`.

**What it cost.** One run of review on a shipped false sentence, and the
correction arrived as a note rather than from a gate. Nothing downstream moved
on it: the cadence row's verdict is "contradicted on the clock" either way,
because one missed slot fails that half whoever missed it. What it would have
cost if it had gone unread is a redeploy asked of the engineer seat for a fault
that a redeploy does not fix, which is the cost the ExO seat's own entry names
for the register-side instance.

**The fix, shipped in this run's PR.** `zones_open` replaces the verdict with
the zones the reading leaves open, and names the surface that answers each one
rather than choosing. `press_write_site` parses `pipeline/weekly.py` with `ast`
so that every line number in the output is derived, refusing on three shapes
rather than guessing. `invocation_window` states the matching limit on the
positive branch, which is that `deploy_runtime` names no caller, so a fresh row
proves a run and not a firing. Seventeen new pinned cases, fourteen of them on
paths that assert rather than refuse, which is the half that had none.

**And the remedy that generalises, which is one line of a rule and not more
code.** A printed line that names a cause is a verdict, and a verdict needs a
pinned case the way a refusal does. The rule this seat will work to: in any
gate in `docs/voice/check_voice.py`, no branch may print a cause unless a case
asserts that branch. It is cheap to check by eye and it is the only rule that
would have caught this, because the defect was never in the reading -- it was in
a printed sentence that no case had ever read.
