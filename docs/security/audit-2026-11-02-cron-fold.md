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
| whole suite | **2477 passed, 2 skipped**, at commit `b72d492c` |

**The suite figure needed a correction and this is it.** The 2,477 was taken
at `b72d492c`. A re-run on the later tree came back **3 failed, 2,474 passed,
2 skipped**, and all three failures were this run's own: one in
`tests/test_check_registers.py` and two in `tests/test_ledger.py`, all caused
by the ledger entry this run filed.

The sequence is worth more than the fix and it is filed as an incident. The
entry was invisible to the parser because of its heading, which blocked
`check_registers.py` on two counts. Fixing the heading made it visible, and a
visible entry must carry four contract fields it did not have. **One fix armed
the gate behind it, and only the whole suite saw the second.** This seat had
already written that the suite was green, on a figure from three commits
earlier plus the targeted cron-firing run it had been repeating all run.

Both are fixed: the entry carries `Trigger`, `What`, `First step` and `Cost`,
71 ledger and register tests pass, `check_registers.py` reports 0 blocking, and
`tests/test_cron_firing.py` passes at 115.

The guard, written down because this seat's charter already contains the
general shape and the seat walked into an instance of it anyway: run the whole
suite on the tree being shipped, after the last commit, before writing that
anything is green. A gate reporting clear is not the same claim as the suite
passing, and they had agreed every previous time this run checked.

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
every log this host holds. **The host is live and these counts drift, so the
snapshot is named: 2026-11-02T07:10:38Z, 2,955 logs across 41 seat
directories.** An earlier pass in this run read 2,930, and the difference is
runs that happened while it was being written.

| exit word | runs | body bytes between the `---` fences (min / median / max) | empty body |
| --- | --- | --- | --- |
| `0` | 1,588 | 1,917 / 3,617 / 10,495 | 0 |
| `1` | 957 | 1,186 / 1,193 / 3,489 | 0 |
| no trailer yet | 347 | no fenced body at all | n/a |
| `timeout` | 36 | 0 / 0 / 0 | **36 of 36** |
| `143` | 27 | 0 / 0 / 2,066 | **26 of 27** |

Every one of the 36 timeout runs **does** write a trailer, and it is the same
trailer in all 36: `# exit=timeout pr=- session=- turns=-`. What is empty is
the body between the fences, not the trailer. The three fields are
placeholders rather than missing lines.

The cause is one flag and it is uniform. **2,922 of the 2,955 logs reach the
point of invoking the executor, and all 2,922 of those invoke it with
`--output-format json`.** Zero logs anywhere on the host carry a transcript
line. So the host does not stream the executor's output. It
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

The other 33 logs never reached the executor at all and carry no trailer
either, which is its own small finding: they are clone and startup failures,
clustered on 2026-10-18 and including the research seat's 05:14:34Z run
tonight that died at `git clone` with the disk full.

The blast radius of the current behaviour, stated plainly: **62 runs on this
host have no surviving log record of what they did**, being the 36 timeouts
and the 26 signal kills with an empty body. This seat's own
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

**Corrected to 81 by the ExO seat and re-measured at 86, and I accept the
correction without qualifying it.** 82 was my arithmetic error. Their 81 was
right when they took it, 86 is right at 07:40Z, and the five classes they
resolved it into are exactly the five the log holds: 40 `exit=timeout`, 27
signal kills at `exit=143`, 15 `exit=clone`, 3 `exit=charter-missing`, 1
`exit=workdir-gone`. Two of those classes neither of us had named before they
did the breakdown.

Their aside about the sign is the useful part and it generalises past this
count. The signal kills record a **positive** 143, so any filter looking for a
negative exit code finds none of them. And `exit` in this log is not even
consistently a number: four of the five classes above are strings in the same
field that otherwise holds `0`, `1` and `143`, so a numeric comparison on it
either throws or silently misclassifies depending on the language. That is a
schema fact worth carrying, because it is a plausible cause of every wrong
count in this exchange, including both of mine.
Every one of those 86 rows also names no session, so none of them reach
`tools/ship_first.py`'s classifier; they are counted as unjoinable, which is
the correct handling and was checked this run rather than assumed.

One number here is worth more than the rest and it is not about kills.
**838 of 1,627 clean `exit=0` runs name no pull request**, which is more than
half. That is the surface this seat's `pr_candidate` work addresses, measured
fleet-wide for the first time, and it is an order of magnitude above the 21
alexandria rows that motivated it. It is evidence that the gate is wrong often
rather than occasionally, and it strengthens the reason that repair records a
candidate instead of settling outright.

**Checked again 2026-11-02 07:40Z and kept, against a correction that said it
could not have come from this source.** The ExO seat's 07:26Z message
(`c1692d84`) held that the audit log's `run.end` rows "carry no pull request
field at all, so a count there returns every clean run", and offered 816 of
1,591 from the log trailers instead. The field is there. It is named `pr`, it
is present on 802 of 2,716 `run.end` rows, and re-measured on the grown corpus
the count is **851 of 1,653 clean runs with no `pr`, 51.5 percent**, against my
original 51.5 and their trailer figure of 51.3. Three measurements, two
sources, one answer to within two tenths of a point.

The correction's own number disproves its reason, which is the part worth
keeping. If the field were absent then every clean run would count as naming no
pull request, so the result would have been 1,653 of 1,653 and 100 percent
rather than a hair over half. A reason that predicts 100 percent cannot be the
explanation for an answer of 51.5.

The likely cause is a field name. `pr_url` selects 0 rows in this log and `pr`
selects 802, and my own earlier note in `audit-2026-11-02-exo-reply.md` already
recorded that `pr_url` selects 0 without my drawing the inference. So the
correction was produced by querying a column that does not exist and reading
the empty result as a fact about the file. That is the same failure the same
message reports catching in itself one paragraph earlier, about a timeout
trailer, which is why it is filed as a repeat rather than noted in passing.

Nothing in the conclusion moves either way. Both sources say the gate is wrong
about half the time, and the trailer figure is a genuine independent
confirmation rather than a replacement. Their denominator is the better one to
hand the chair for the repair, because the trailer is what `tools/cron_firing.py`
reads.

Routed to the exo seat on the bus rather than raised as a competing relay row,
because the ask is already open there and what it needed was the mechanism. A
short second note went out after this table, because the first correction could
have been read as doubting an observation that was right.

## 3. Secrets exposure, on a surface this seat had not scanned before

The host's run logs are readable by the shared uid this seat has an open
finding about, so what they contain is a live question rather than a formal
one. Scanned all 2,956 logs, at 2026-11-02T07:12Z, for nine classes of
credential-shaped value:
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

## 5. The find that came from running the tool rather than testing it

After the suite was green this seat ran `tools/cron_firing.py` against the
host's real record, which is the step a passing suite makes easy to skip, and
the result is a finding about this seat's own change from earlier today.

The `pr_candidate` repair works. Run over every alexandria run the host holds,
`resolve_shipped` finds **109 runs with a candidate** out of 157 that are
silent-eligible, from 665 alexandria runs. It is not dead code.

The sentence it renders has **never fired**. `judge` is its only caller and
`judge` reports cron slots. Of the 109 candidates, 20 sit on `hook` runs and 89
on `message` runs, and **none sits on a `cron` run**, so the clause added to
the `LOST` line produced no output on any of the twelve days checked with
`--day` against a live pull request list. The number is computed and then
discarded for every row that is not a cron slot.

Nothing was changed for it, deliberately. The computation is correct, the
tests cover it, and moving where it renders is a new view rather than a
behaviour-preserving repair. It is filed as a `proposed` ledger entry for the
engineer, with the 838 of 1,627 figure as the reason the surface is worth
building rather than patching.

**The class is this charter's own**, and it is the reason this section exists
rather than a footnote: a predicate that never selects a row reads exactly
like a predicate that found nothing wrong. Both print nothing. The only thing
that separates them is running the code against data that should make it
speak.

One smaller thing found the same way, and this one is fixed. `--now`'s help
text opened with "an ISO stamp to read the day as of, rather than the wall
clock". It does not set the day. `--day` does, and `--now` pins only the grace
window, which the second half of the same help text described correctly. A
reader following the first clause gets today's rows with a past grace window
and no error, which is how this seat spent four commands reading what it
thought were six different days. Rewritten to say which flag does what, and
to say that `--now` alone still reads today.

## 6. The public/private boundary, re-verified and unchanged

Cheap enough to check on a message wake, and checked because it carries this
seat's oldest severe finding. On the now-unshallowed clone:

- `.gitignore` carries `digests/` and `site/content/digests/`, and
  `git check-ignore -v` confirms both patterns match paths under them.
- Neither directory exists in the working tree and neither has a tracked file.
- The git history still holds `digests/2026-W37.md`, deleted at `6910bd9b`,
  "digests go private", on 2026-09-11.

**Nothing here is new.** The history exposure was found by this seat's own
baseline audit on 2026-09-18, is recorded there as severe, and is filed as an
`urgent` ledger entry whose remedy is a history rewrite and a force push. That
is irreversible and disruptive, so it is the owner's call and it is still
waiting on her. No credential is involved and no rotation applies.

One note on method, because it nearly became a false finding. `git check-ignore
-q digests` returns 1 and reads as "not ignored", because the pattern is
`digests/` and the bare name with no trailing slash and no directory on disk
does not match it. The correct test is the path form, `digests/` or a file
beneath it. A seat running the first form and believing it has found an
unignored private directory would raise a severe finding that is not there.

## 7. A near-miss in this run's own method

Step 0b was obeyed and then undone one command later. This run wrote its pull
request description into a `mktemp -d` directory as the rule requires, and then
addressed that file as `sorted(glob.glob('/tmp/tmp.*/body.md'))[0]`, which
resolved to **another seat's live pull request description**. At that moment 25
`body.md` files existed under `/tmp/tmp.*`, one per live seat run, every one
owned by the same `seats` uid, so every seat can write every other seat's.

Nothing was overwritten, and the reason is luck: the script's first assertion
compared a replacement string against the file and failed, because another
seat's prose does not contain this seat's sentences. A guard that fires by
coincidence is not a guard, and that assertion existed to protect the
replacement rather than the path.

The refinement is small and worth carrying: a unique directory only helps if it
is addressed by its exact path, because **the scratch pattern is shared even
when the directory is not.** Filed as a repeat of the October instance of the
same defect. Nothing in another seat's scratch was read further or touched, for
the same reason this seat declined to free another seat's disk tonight.

### One trap found by tripping it, for the next seat that files a ledger entry

`tools/ledger.py`'s `ENTRY` pattern requires `### YYYY-MM-DD` followed by a
dash, and `docs/voice/ban-list.md` forbids the em dash that every existing
heading in the file uses. An entry titled with a colon instead parses as no
entry at all: its status line is then read as prose that merely looks like a
verdict, `check_registers.py` blocks on two counts, and the entry is invisible
to `ledger.py --status`. This run hit exactly that and the gate caught it,
which is the gate working.

The heading that satisfies both is a plain ASCII hyphen. Worth one line
somewhere a filer reads, because the two rules are in different files and
neither mentions the other. Not raised as an ask: it is one sentence of
documentation and the gate already refuses the mistake loudly.

## 8. What this run did not do

The dependency audit, the public/private boundary check, the MCP server
review, the workflow posture review and the upstream question are the
semimonthly sweep's, and they are in `audit-2026-11-02.md` for this cycle.
This run re-ran the full suite and the cron-firing suite, and it took one new
measurement on a surface the sweep does not cover.

## 9. Still open from this seat, unchanged by this run

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
