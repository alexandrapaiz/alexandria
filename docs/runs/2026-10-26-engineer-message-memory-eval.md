# Run note, engineer, 2026-10-26 (message), sprint item 2

Opened as a draft before the work, per the ship-first rule.

**Payload.** #542 merged (sprint 2026-10-26 item 1, ADR-13's merge slice).
Asked to continue with the next item in the lane.

**Item taken.** Sprint 2026-10-26 item 2: land agent-memory-selection's first
real differential eval result on file.

## The thing this run got wrong first, recorded because it changes the number

The first reading of item 2 was that the seven findings against
`agent-memory-selection` were a mix of certificates, exploits and audits,
because that is the order the sprint item lists them in. They are not. All
seven are ADR-40 item 6 audits:

```
python3 tools/skill_eval.py --check | grep '^finding: agent-memory-selection'
```

returns seven lines and every one of them ends "never audited for ambiguity,
gameability and realism". The certificate and exploit findings in that output
belong to the other eight skills. That matters because an audit is judge-only,
so the cheapest path to closing every open finding on this skill is 7 calls
rather than the 87 a full differential run needs, and the sprint item's own
wording would have sent a reader at the expensive one.

## What the credential check actually returned

Five environment names checked for presence, never for value:
`GROQ_API_KEY`, `MOONSHOT_API_KEY`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`,
`OPENAI_API_KEY`. All five unset. The Modal CLI is not installed in this
sandbox either, so the `groq` Modal secret is not reachable from here and the
once-only cheap Modal check the sprint asks for returns "unavailable" rather
than "off".

So no arm of the eval could run, and the sprint item's done condition, a
result file stating the delta in numbers, could not be met today. The split is
in the pull request.

## The numbers behind the $0 route

Measured on this branch with `--plan` and with tiktoken against the real
suite, not estimated:

| | calls | tokens | pause each | 
|---|---|---|---|
| subject arm, `openai/gpt-oss-20b` | 42 | ~92,600 | 22.7s |
| judge, `openai/gpt-oss-120b` | 45 | ~135,900 | 23.9s |
| the audit alone, judge only | 7 | ~25,000 | 23.9s |

Worst-case with-skill request is 3,023 tokens (42 system, 1,638 skill body,
143 longest ask, 1,200 reservation) against the free tier's 6,800-token
margined minute, so nothing 413s. The full run is about 34 minutes, all of it
pacing. The audit is about three minutes and 13 percent of one free-tier day.

## What a second count changed

The first pass at the judge-side token total came back 19,104 over 6 calls,
because the loop looked for `check.statements` and the suites write
`check.assertions` and `check.secondary_assertions`. The corrected count is 45
calls and ~135,900 tokens, which is seven times the first number and the
difference between "an eval run is a rounding error on the free tier's day"
and "an eval run is 68 percent of it". Both numbers came from the same
session; the second one is the one in the pull request.

## The register duties

- `gh run list --workflow=checks.yml --branch=main --limit 5`: five successes,
  newest 04:53:07Z. Main is green, so there was nothing to fix ahead of the
  sprint item.
- Machinery diff, 36 hours over `.github/` and `pipeline/`: seven commits, all
  from this seat, all explained by merged pull requests (#536, #516, #507,
  #500). Three carry token-reservation changes, which
  `docs/agents/runtime-changes.md` makes runtime changes whose third gate is a
  rehearsal, and all three were shipped with the missing rehearsal named in the
  pull request and already filed as
  `INC-2026-09-30-triage-runtime-change-with-no-rehearsal`. Nothing new to
  register.
- `docs/agents/press-rehearsal.md` declined again today, same reason #536 gave:
  it needs a Modal function and the workspace has been off since 2026-10-23.
- Conflict markers: none in `docs/`, `prompts/`, `README.md`, `tools/`,
  `tests/`, `site/`.
- Ban list on every file this run wrote: no non-ASCII in any added line. Three
  ledger headings and one README reference were rewritten from `—` and `§` to
  ASCII after the check caught them.
- `python3 tools/incidents.py check`: 332 entries, 7 in the inbox, nothing
  malformed. `python3 tools/ledger.py --check`: 0 blocking, at baseline.

## Two things that went wrong after the pull request went ready

**The guard said yes and its test said no.** `tools/skill_eval.py` was added to
`budget.PACED_CALLERS` and verified by calling the guard, which is what the
guard's own docstring tells a seat to do:

```
python3 -c "import budget; print(budget.check_fallback_pacing())"   # []
python3 pipeline/budget.py                                          # passed
```

`checks.yml` then failed on `tests/test_corpus_drain.py`, which asserts that
guard plus the literal `cap.last_tokens` in each paced caller's source. The
code read the same number through `getattr`. Filed as
`INC-2026-10-26-the-pacing-rule-has-two-gates-and-they-do-not-agree`, fixed by
spelling the attribute access, and the fold that would make the two enforcers
one is a ledger proposal rather than a commit, because it changes what fails a
deploy.

**The README edit restated a list instead of pointing at it.** The first version
of the corrected paragraph listed the four blockers from #542's pull request
body. `docs/product/reviewer-panel.md`'s own numbered list is a different four:
it carries the Commit statuses grant and not the `prompts/*.md` charter
reading. Restating a list from memory is the exact defect that paragraph was
being edited to fix, so it now names them in the doc's terms and points at the
one place the list lives.

## What the whole-suite claim is worth, which is nothing

`python3 -m pytest tests/ -q` was attempted three times. The first returned
exit 0 with an empty log, the second was killed at the sandbox's command
ceiling with `EXIT=143`, and both were backgrounded. An empty log and exit 0 is
indistinguishable from a pass and is not one, and the pull request's first
description claimed the suite passed on that basis. The claim was replaced with
the thing that is actually true: 795 tests across the 18 files that import
`skill_eval` or `budget`, enumerated with grep rather than judgment, run to
completion twice with the same number.

## The late register entries

- `INC-2026-10-26-the-corrected-sentence-was-corrected-in-one-register-of-two`
- `INC-2026-10-26-the-pacing-rule-has-two-gates-and-they-do-not-agree`
- `INC-2026-10-26-the-single-branch-refspec-survived-the-unshallow-again`,
  a repeat of the 2026-10-18 entry, recorded because the standing rule has no
  judgment call in it and the register has no way to append a recurrence to an
  existing id.
