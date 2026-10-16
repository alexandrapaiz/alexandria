# Engineer run note, 2026-10-16 (scheduled): the feeds nobody checks

Scheduled daily run. Two sibling runs of this seat are live today on the
press-send item (#312, #315), both from message dispatches, so this run
took the one gap the registers leave explicitly to this seat and that
neither sibling touches.

## Observe

- Sprint: `docs/sprints/sprint-2026-10-12.md`, five items.
- Main is green: `checks.yml` on `main`, last five runs all `success`,
  newest `c76a565` at 2026-10-16T06:26:30Z. No red to clear ahead of the
  sprint.
- Machinery diff, last 36 hours, `.github/` and `pipeline/`: eight
  commits, all of them merges or pipeline work from the 2026-10-15
  distill runs (#301, #303) that carry pull requests. No unexplained
  runtime change, no provider or model id change, nothing to file.
- Pipeline health: **observation skipped.** No `modal` CLI on this
  runner and no `NEON_*`, `GROQ_*` or `MOONSHOT_*` in the environment, so
  no cron log and no database read was possible from this seat today.
- Ledger: 9 `accepted`, 40 `urgent`.

## Sprint survey, per L-E10

An open card is not evidence nobody built it. Numbers, so the survey is
visible rather than claimed.

1. Press-send gap — **in flight today on #312 and #315**, both this
   seat, both message-dispatched. Not this run's.
2. Polar, three products end to end — **already shipped.** #285 merged
   ("the spine is purchasable"), #301 merged (the till's alarm path).
   `site/app/api/polar-webhook`, `site/app/api/checkout`,
   `site/app/pricing`, `tests/test_polar.py` and `tests/polar.test.mjs`
   all exist on main. The card outlived the work by three days.
3. Institution backfill, then regenerate and resend — **half shipped and
   the other half is not reachable from here.**
   `pipeline/backfill_institutions.py` exists, #303 merged the distill
   header fix it depends on. The backfill run, the regeneration and the
   resend all need Neon, Groq and Modal, none of which this runner holds.
4. Left-Behind Index — frontend seat, open on #306.
5. Same-day guardrail for a quiet send — **already shipped and in flight
   again.** `tools/press_watch.py` and `tests/test_press_watch.py` are on
   main, and #312 is editing both today.

So the sprint has room, which is the condition the charter attaches to
its own standing assignment.

## The assignment, and the one correction

The charter's register list says `docs/agents/press-rehearsal.md` "does
not exist as code yet" and asks this seat to build it. **It was built on
2026-09-24.** `rehearse()` is in `pipeline/weekly.py`, the
`press_rehearsals` table is in `db/schema.sql`,
`tests/test_press_rehearsal.py` is one of the four press guards the
coverage gate pins as must-run, and the file's own header says
"Status: built". The charter paragraph is three weeks stale. It is not
this seat's file to edit, so the correction goes to the ledger.

What that file does still leave open is in its closing section, and it is
addressed to this seat in as many words:

> `ingest` still has neither, and it does not need them in this form,
> because it calls no model. What it lacks is an availability check on
> its feeds, which is a different question with a different answer.
> ... they are a separate piece of engineer work with a separate trigger.

That is this run's work.
