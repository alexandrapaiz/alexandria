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

1. Press-send gap. **In flight today on #312 and #315**, both this
   seat, both message-dispatched. Not this run's.
2. Polar, three products end to end. **Already shipped.** #285 merged
   ("the spine is purchasable"), #301 merged (the till's alarm path).
   `site/app/api/polar-webhook`, `site/app/api/checkout`,
   `site/app/pricing`, `tests/test_polar.py` and `tests/polar.test.mjs`
   all exist on main. The card outlived the work by three days.
3. Institution backfill, then regenerate and resend. **Half shipped, and
   the other half is not reachable from here.**
   `pipeline/backfill_institutions.py` exists, #303 merged the distill
   header fix it depends on. The backfill run, the regeneration and the
   resend all need Neon, Groq and Modal, none of which this runner holds.
4. Left-Behind Index. Frontend seat, open on #306.
5. Same-day guardrail for a quiet send. **Already shipped, and in flight
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

## Act

### What was built

`tools/feed_health.py`, a credential-free census of all 53 sources, and the
gate that goes with it. One command, no secrets, runs anywhere:

```
python3 tools/feed_health.py                  # the census, and the gate
python3 tools/feed_health.py --report-only    # same output, exit 0
python3 tools/feed_health.py --json
python3 tools/feed_health.py --offline        # read sources.yaml, fetch nothing
python3 tools/feed_health.py --only qwen,gh-vllm
python3 tools/feed_health.py --census docs/evals/2026-10-16-feed-health.json
```

`pipeline/ingest.py` stops swallowing a dead source. `fetch_arxiv` and
`fetch_feeds` now report per-source counts to the caller rather than only
to a log, and `ingest()` raises `NothingToIngest` when the whole run came
back empty or when every arXiv category did.

`tools/deploy_gate.py` gains `LOCAL_GATES`, so ingest's deploy chain is
`python3 tools/feed_health.py && modal deploy pipeline/ingest.py` instead
of a bare deploy. That file's own docstring had named the gap: ingest
calls no model, so `preflight` and `rehearse` are the wrong shape, and it
was the one scheduled app whose deploy proved nothing.

### What the first run found

7 of 53 sources were delivering nothing, and no deploy had ever been able
to notice. Before and after, both measured today:

| | before | after |
|---|---|---|
| delivering | 46 of 53 | 48 of 53 |
| failing, unrecorded | 7 | 0 |
| failing, pinned with a reason | 0 | 5 |
| gate exit code | 1 | 0 |

The two that moved are the two this seat could fix on its own judgement.
`gh-spiffe` was a real URL error: it pointed at `spiffe/spiffe`, the
specification repository, which cuts no releases, so it answered 200 with
zero entries forever. It now points at `spiffe/spire`, the implementation,
verified at 10 entries and 0.8 days. `gh-autogen` was never broken:
`sources.yaml` already said in a comment that it is kept for its archive
because development moved to the AG2 fork, and it now carries
`expect: archive`, which forgives age and refuses to forgive reachability.

The remaining five are real and are pinned rather than deleted, because
retiring a source is editorial and ADR-7 and ADR-12 give `sources.yaml`
the shape of a proposal surface. They are in `docs/ideas.md` today with
the measurement that found them.

### Two mechanisms, and why not one

`expect: archive` lives in `sources.yaml` because it is a permanent
statement about a source. `KNOWN_DEAD` lives in `tools/feed_health.py`
because it is a dated list of defects nobody has ruled on, and it may
shrink and may not grow. Both exist to stop the gate from crying wolf
without letting it go quiet, which is the needle
`INC-2026-09-30-the-guard-went-red-and-nobody-read-it` threads: a
permanently red gate is one nobody reads, and a gate with no pin is one a
seat switches off. The pin changes the exit code and never the verdict, so
a pinned source is still measured, still printed, and still in the JSON.

### Evidence

- `python3 -m pytest tests/ -q`: **1532 passed, 11 skipped**.
- `tests/test_feed_health.py`: 55 cases, no network and no database. The
  six that matter most drive `ingest()` end to end with its four I/O calls
  faked, because `fetch_arxiv` and `fetch_feeds` changed from returning a
  list to returning a pair, and a mistake unpacking either one is
  invisible to every unit test: `judge_sources` stays correct, the suite
  stays green, and the cron raises `TypeError` on its next unattended run.
- `python3 tests/test_deploy_gate.py`: all checks passed, both under pytest
  and as a direct run. Its existing ladder assertion caught this change
  honestly and is now stronger rather than looser.
- `python3 tools/check_registers.py`: `0 blocking, 6 warning(s)`, all six
  pre-existing and all six already filed by the security seat on
  2026-10-15.
- `python3 tools/ci_coverage.py` via `tests/test_ci_coverage.py`: green.
  `tests/test_feed_health.py` is pinned in `UNCOVERED` with its reason,
  because the step that would run it goes in a workflow no seat's token may
  write. The staged replacement runs it already, since that file runs the
  suite rather than naming files.

### What this run could not do, and what it refused to do

**The guard does not reach production until someone deploys.**
`docs/agents/runtime-changes.md` binds this change: ingest is a Modal cron
and its first execution after a deploy is unattended. This runner has no
`modal` CLI and no `NEON_*`, `GROQ_*` or `MOONSHOT_*`, so the smoke run
the law requires is the owner's or the chair's. The decision half is
testable without Modal and is tested, which is why `judge_sources` is a
separate function.

**The guard is deliberately narrow.** It does not raise on dead blogs,
even all 44 of them, and a test asserts that. The firehose is the corpus,
and a guard that turns a bad day into an outage is a guard someone
switches off.

**It did not delete five lines from `sources.yaml`.** That is the owner's
call, and the ledger is where it goes.
