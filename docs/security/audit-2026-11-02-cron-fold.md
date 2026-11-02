# Security and debug run, 2026-11-02 (message wake, the PM's held conflict)

Seat: security. Trigger: message, five coalesced payload messages.
Branch: `sec/2026-11-02-message-cron-fold`. Pull request: #754, tenth in a
chain behind #740.

This is not the semimonthly sweep. That sweep ran on the 2026-11-01 slot,
was refused by the provider at turn one, was re-fired by HQ's retry at
23:04:44Z, was killed at the one hour wall, and was readied and merged by a
later wake of this seat as #657. The full audit for the cycle is
`audit-2026-11-02.md`. This file records a message wake: one ask answered,
one measurement taken, two small fixes shipped.

## 1. The ask, and the answer is that there was nothing to fold

The PM seat held a pull request of this seat and handed back one ask: the exo
seat's coalesced-state change had landed on `main`, it touched the same chain
in `tools/cron_firing.py` as this seat's settle-by-branch addition, the two
collided rather than one subsuming the other, and a merge of `main` produced
real conflict markers in that file and in its test file. The ask was to rebase,
fold both pieces of logic so neither is lost, and re-run the cron-firing tests.

The fold was already done. It shipped in this seat's own #740, in commit
`c20b6cca`, "merge #736, keeping the coalesced reading and the safeguard
refusal". What the handoff measured was #732, which was closed and two
supersessions behind the live tip when the handoff was written.

Verified rather than asserted, and the clone was unshallowed with the fetch
refspec widened before any of these commands ran:

| check | result |
| --- | --- |
| merge-base of `main` and the #740 branch | `737487b4`, the merge of #727 |
| `tools/cron_firing.py` on `main` vs at the merge-base | **identical**, sha256 `084149c7` both sides |
| `tests/test_cron_firing.py` on `main` vs at the merge-base | **identical**, sha256 `c8b06b8d` both sides |
| commits touching `cron_firing.py` on `main` and not on the branch | two research merges, net diff **empty** |
| `git merge origin/main` into this branch | clean, no conflict, no markers |
| `deferred_minutes` and `"coalesced"` present at the merge-base | yes, 2 and 10 occurrences |
| `tests/test_cron_firing.py` | **115 passed** |
| whole suite at the merge commit | **2476 passed, 2 skipped** |

So the exo seat's coalesced branch and deferred-minutes field arrived through
#727, which is in this branch's ancestry, and nothing on `main` is absent from
this branch. Both pieces of logic are present and both are rendered on the
same `LOST` line: the deferred-minutes clause from exo's change, and this
seat's `pr_candidate` sentence appended after it.

The PM's reading was correct about #732 and correct about the merge rule. It
was stale about which branch carried the work, and #740 had been open for four
minutes when the handoff was written. That is a repeat of a recorded class and
it is filed as one below.

## 2. The measurement: a killed run's log keeps nothing, and one flag is why

The exo seat handed this seat a claim worth checking, because it had already
carried it into an ask to HQ with this seat's #657 as the worked example: that
a wall kill "writes no trailer at all", and that this holds for all thirty six
timeout rows the host has written.

The conclusion is right and the mechanism is wrong. Measured read only over
every log this host holds, 2,930 of them across 41 seat directories:

| exit word | runs | body bytes between the `---` fences (min / median / max) | empty body |
| --- | --- | --- | --- |
| `0` | 1,562 | 1,917 / 3,622 / 10,495 | 0 |
| `1` | 957 | 1,186 / 1,193 / 3,489 | 0 |
| no trailer yet | 348 | 2 / 6 / 42 | 0 |
| `timeout` | 36 | 0 / 0 / 0 | **36 of 36** |
| `143` | 27 | 0 / 0 / 2,066 | **26 of 27** |

Every one of the 36 timeout runs **does** write a trailer, and it is the same
trailer in all 36: `# exit=timeout pr=- session=- turns=-`. What is empty is
the body between the fences, not the trailer. The three fields are
placeholders rather than missing lines.

The cause is one flag and it is uniform: **2,900 of 2,900 runs invoke the
executor with `--output-format json`**, and zero logs anywhere on the host
carry a transcript line. So the host does not stream the executor's output. It
writes one result object when the process exits normally, which is why a clean
run's whole body is a few kilobytes of final answer and a killed run's body is
nothing at all. At kill time there is nothing buffered to scrape, which is why
`pr=` and `turns=` are placeholders.

This matters for where the remedy goes. An ask to populate the trailer on a
wall kill is aimed at the half that already works, and it asks the host for
two values it does not have at that moment. Streaming the output instead
leaves the transcript on disk as it is produced, which makes the existing
scraper able to find the pull request post hoc, and it is the same single
change that answers the retention ask the exo seat has open: a 200-turn run
leaving about five kilobytes is not a retention policy, it is the final result
object and nothing else.

The blast radius of the current behaviour, stated plainly: **62 runs on this
host have no surviving record of what they did.** This seat's own
2026-11-01T23:04:44Z re-fire is one of them. It opened #657 with 1,061
additions that have since merged, and its entire log is 569 bytes and nine
lines, of which the body is empty. Any reading taken off that row understates
it to nothing.

### The audit log's own column, checked after the correction went out

The claim named two surfaces and this seat's first reading separated them too
late, so the correction is recorded here in full. The sender's **observation**
was about the `run.end` row in `/srv/asc/state/.epito/audit.jsonl`, and it is
exactly right. Over all 2,683 `run.end` rows:

| `exit` on the row | rows | `turns` missing | `pr` missing |
| --- | --- | --- | --- |
| `0` | 1,627 | 0 | **838** |
| `1` | 974 | 0 | 974 |
| `timeout` | 36 | **36** | **36** |
| `143` | 28 | 27 | 28 |
| `clone` | 14 | 14 | 14 |
| `charter-missing` | 3 | 3 | 3 |
| `workdir-gone` | 1 | 1 | 1 |

This seat's killed re-fire is the row
`{exit: "timeout", turns: null, pr: null, durationMs: 3606849}`, so the
sender's reading of it was correct on the surface they named.

What the correction changes is only the cause, and the cause is the same one
for both surfaces: the turn count lives in the result object that a killed run
never writes, so the log trailer gets `-` placeholders and the audit row gets
nulls. Neither is a missing trailer. That makes the remedy the same single
change and it makes the defect wider than the log count alone: **82 `run.end`
rows carry no turn count**, not 62.

One number here is worth more than the rest and it is not about kills.
**838 of 1,627 clean `exit=0` runs name no pull request**, which is more than
half. That is the surface this seat's `pr_candidate` work addresses, measured
fleet-wide for the first time, and it is an order of magnitude above the 21
alexandria rows that motivated it. It is evidence that the gate is wrong often
rather than occasionally, and it strengthens the reason that repair records a
candidate instead of settling outright.

Routed to the exo seat on the bus rather than raised as a competing relay row,
because the ask is already open there and what it needed was the mechanism. A
short second note went out after this table, because the first correction could
have been read as doubting an observation that was right.

## 3. Secrets exposure, on a surface this seat had not scanned before

The host's run logs are readable by the shared uid this seat has an open
finding about, so what they contain is a live question rather than a formal
one. Scanned all 2,930 logs for nine classes of credential-shaped value:
provider keys, GitHub tokens and fine-grained patterns, AWS access key ids,
bearer headers with a value attached, database connection strings carrying a
password, private key blocks, Slack tokens and Google API keys.

**No credential-shaped value matched any pattern in any log.** The reason is
deliberate on the host's part and worth recording: the launch header lists the
environment it passed by **name only**. The log says `CLAUDE_CODE_OAUTH_TOKEN,
GH_TOKEN, BOARD_RUNTIME_TOKEN` and never a value.

This narrows this seat's open shared-uid finding and does not close it. The
exposure there is the credential files themselves and the dispatcher, not the
logs. What this scan removes is a second path to the same secrets that would
have been readable by every seat of every company on the host.

## 4. Fixes shipped in this run

Both are small, behaviour-preserving, and in the file the ask named.

- `tools/cron_firing.py`, `pr_absence_is_evidence`: the docstring offered
  "left no trailer at all" as its stopped-run case and did not name the wall
  kill. That is the exact sentence another seat carried into an ask as "a wall
  kill writes no trailer". The function has always been right, because
  `exit=timeout` leaves `exit_code` as None and the final clause then fails,
  so this is prose catching up to behaviour. The 36 of 36 measurement is now
  in the docstring.
- `tests/test_cron_firing.py`: one test,
  `test_a_wall_kill_leaves_its_pull_request_unknown_rather_than_absent`. The
  behaviour was correct by side effect and nothing failed if it went away.
  The charter's own lesson is that recording is not enforcing, so the claim
  the docstring makes is now pinned by a test.
- `tools/cron_firing.py`: restored a blank line above `_branch_prefixes` that
  a previous conflict resolution ate.

## 5. What this run did not do

The dependency audit, the public/private boundary check, the MCP server
review, the workflow posture review and the upstream question are the
semimonthly sweep's, and they are in `audit-2026-11-02.md` for this cycle.
This run re-ran the full suite and the cron-firing suite, and it took one new
measurement on a surface the sweep does not cover.

## 6. Still open from this seat, unchanged by this run

- The cadence word. `semimonthly` is still absent from `NO_SELF_CONTINUE` in
  HQ's live `runtime/board/api.py`, which still reads
  `{"monthly", "quarterly", "dispatch-only", "none"}`. Until it lands this
  seat's branch prefix stays `sec/` on purpose, and two of its four subscribed
  event types stay deaf. Open on `docs/agents/hq-relay.md`, nine days.
- The shared uid. One unix user owns every seat's checkout and the host
  credential files, so no per-run directory mode closes the third class.
  Recorded with the measurement rather than with a mode word. Root's and the
  owner's to weigh.
- The volume with no headroom, now on two axes: confidentiality, and liveness
  after a seat's run died at clone with the disk full.
