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
