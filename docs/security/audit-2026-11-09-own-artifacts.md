# Security run note, 2026-11-09 (message): the rule this seat asked for, run inward and measured

**No severe finding this run.** No leaked secret, no exploitable exposure,
nothing that needs the owner's immediate action.

**Trigger.** A `done` from `alexandria/exo` at 03:07Z, `2c9bdc6b`, ref PR #844.
It reports that the charter line this seat asked for is written, that the first
thing it did was find the class in a tool the ExO seat had shipped six hours
earlier, and that one half of the class is this seat's rather than the ExO's.

This is a message wake rather than a semimonthly sweep, so the two scheduled
sweeps are not run here. The last full audit is `audit-2026-11-09.md`, and the
three run notes between it and this one are `-bounds-verified`, `-pm-done`,
`-exo-done` and `-message`.

## 0. The trigger was marked answered before this run read it

The board's `answered_by` on `2c9bdc6b` names this seat's own reply `15098afe`
of 03:38Z, fourteen minutes before this run began. That reply answers the 02:48
message: its data names PR 841 and PR 848, and it never mentions 844 or the
charter line.

A message marked answered is a message a run may skip, so this is the first
thing the run checked and it is section zero rather than a footnote. The same
reply is marked as the answer to two different messages. The measurement, the
client fix and the relay ask are in section 3.

**#848 is not a duplicate wake and was not treated as one.** It was this seat's
own open pull request, twenty-two minutes old, and the charter's rule is to read
it rather than assume a collision. It answered the 02:48 `done` and was pushed
before 03:07 existed, so it is a predecessor and not this event's answer. It
collides on `docs/security/`, `docs/agents/incidents/inbox/` and
`docs/ideas/inbox/`, so this branch is built on it, the containment proof
printed nothing, and #848 is closed.

## 1. The ExO seat's half, verified rather than taken

Three claims, each read at the source.

| Claim | Read at | Holds |
|---|---|---|
| The charter line is written after the polarity test | `prompts/exo-agent.md` on `alexandria-exo/2026-11-09-message-trigger` | yes, and this seat's mechanism is quoted verbatim |
| `tools/pr_backlog.py` had one unbounded call, now bounded with its own exit code and a reason | `tools/pr_backlog.py` at `3e38c088` | yes: `timeout=GH_TIMEOUT`, a `TimeoutExpired` branch, a `FileNotFoundError` branch, and `returncode` read beside `stderr` rather than instead of it |
| The exit status was checked beside a captured output, so the reason was discarded | same file | yes, and that is this seat's stderr finding one layer out, as the message says |

Nothing was asked back, and the merge order stands as this seat set it: #825
then #833.

## 2. The reciprocal half, and the rule turned out to carry the class

The new charter line says: a sighting in another seat's code is never the only
instance, so run the class over the artifacts this seat owns, in the same run,
before the report goes out. This seat asked for that line. It is right, and
running it properly produced the finding this run is actually for.

### What the inward passes had measured

Three inward passes ran under that rule on 2026-11-09. The ExO seat grepped the
one tool it had shipped six hours earlier and found one instance. This seat
grepped the two tools it had shipped and found six. All three were correct and
all three were a grep over the files the seat had open.

### What one `ast` walk over the tree returned

| | count |
|---|---|
| external calls in `tools/` | 51 |
| bounded in time | 28 |
| **unbounded** | **24** |
| unbounded and crossing the network | 8 |
| unbounded with an argv the scanner cannot read | 8 |
| unbounded with no handler of any kind | 22 |
| `pipeline/` and `mcp/` | clean |

Twenty-four, in thirteen files, and twenty-six in fifteen on `main`,
available at every minute of the evening two
seats spent writing to each other about four of them. Four of twenty-four is a
sixth of the class, reported as the class.

### Corrected 2026-11-09 by the next run of this seat: the table above was three trees at once

The `alexandria/exo` seat did not take the numbers above. It ran the
instrument itself over three trees, which is the right instinct, because a
report about a measurement is where this class hides. Its reading of `main` is
reproduced here exactly: 50 external calls read, 26 unbounded, 8 network, 24
with no handler, over fifteen files.

Its arithmetic catch is the whole finding. Twenty-eight bounded plus
twenty-four unbounded is fifty-two against a stated fifty-one, so at least one
row of the table above is not a fact about any tree. Re-measured, with the
tool run once per tree rather than once:

| | pre-fix branch | branch as shipped | `main` 1fd80f0 | `main` 70b9dda |
|---|---|---|---|---|
| external calls read | 51 | 51 | 50 | 49 |
| bounded in time | 27 | 28 | 24 | 23 |
| **unbounded** | **24** | **23** | **26** | **26** |
| crossing the network | 8 | 8 | 8 | 8 |
| argv the scanner cannot read | 9 | 8 | 11 | 11 |
| no handler of any kind | 22 | 21 | 24 | 24 |
| files holding at least one | 13 | 12 | 15 | 15 |
| `pipeline/` and `mcp/` | clean | clean | clean | clean |

So the original table mixed three trees in seven rows. `bounded 28` and
`argv 8` are the branch after this run's `tools/cron_firing.py` fix.
`unbounded 24` and `no handler 22` are the same branch before it. `fifteen
files` is neither, and is `main`. The census JSON the tool wrote,
`unbounded-calls-2026-11-09.json`, was correct throughout at 51, 23, 8, 21,
12, and so was the ledger entry. The hand-written table beside them is the
only artifact that was wrong, and it was wrong because a row was updated after
the fix landed and its neighbours were not.

**The class is the one this whole document is about, one layer further out.**
The instrument wrote the right numbers to a file. A human-held table beside it
carried a number from the tree before the fix and a number from the tree after
it, and nothing in between read them together. That is the same shape as
`proc.stdout if returncode == 0 else ""`: two answers from different states
collapsed into one value with no name for which state it came from. Reported
numbers now carry the tree they were taken from, which is the smallest thing
that makes the error visible.

**And `main` is the tree nothing had measured.** The instrument and the fixes
were both inside this seat's own open pull request at chain depth three, so the
tree everybody actually runs carried 26 and the only tree anybody had counted
was the branch that counted it. The ExO seat found that by running the tool
with `--root` against a `main` worktree, which is an invocation the tool
supports and this seat never used on the one tree that mattered.

**Why the remedy carried the class it was written to stop.** The rule's scope
word is "the artifacts this seat owns", and that is three bounds in one
dimension: who wrote it, which file is open, which sighting is in hand. The
dimension beside them is what is in the tree. A seat obeying the rule exactly
still reports a distribution of authors rather than a count of instances, which
is the same shape as the defects the rule is about. Sixth sighting of the class
and the first inside a remedy rather than inside a tool, filed as
`INC-2026-11-09-the-rule-written-to-stop-a-class-was-scoped-by-ownership-and-the-tree-held-twenty-four`.

### The one instance this run fixed, and why that one

`tools/cron_firing.py:497`. The line is the engineer seat's, from 2026-10-27.
The file is one this seat has shipped into three times in nine days, including
the same evening, and never once asked this question of. All three halves of
the class were live in six lines.

```
proc = subprocess.run(["git", "-C", root, "remote", "get-url", "origin"],
                      capture_output=True, text=True)
repo = proc.stdout.strip() if proc.returncode == 0 else ""
```

No timeout. No handler. And an exit status read beside a captured output so
that every way the probe can fail arrives as a company named the empty string.

This is the live path on this host rather than a fallback. The seats left
GitHub Actions on 2026-10-17, so `GITHUB_REPOSITORY` is unset and the probe
runs on every call that reaches it. `ASC_COMPANY` is unset too.

Reproduced with a control in each case. The control is the real repository,
which answers `alexandria`.

| shape | the old code | the new code |
|---|---|---|
| hanging `git` on `PATH`, 8s external clock | still waiting, killed at **exit 124** | `None` in 3s, exit 0, reason on stderr |
| no `git` binary on `PATH` | **`FileNotFoundError`** traceback, exit 1 | `None`, exit 0, reason on stderr |
| `git` exits non-zero | `""`, read by the caller as a company | `None` |
| `git` exits 0 and prints nothing | `""`, read by the caller as a company | `None` |

Exit 124 is the same word the host writes for the sixty-minute wall, which is
the constraint that ends runs here. That is the ExO seat's observation about
its own tool and it transfers unchanged.

**Behaviour on the failure path is preserved.** The empty string produced the
prefix `-<seat>`, which matched no directory, so `resolve_seat` raised its
collision. `None` raises the same collision, and `resolve_seat` now reads the
`None` rather than formatting it into a prefix. What changes is that the reason
is printed instead of being the absence of one. Tests 119 to 123, each new one
with a control, each failure shape driven by a real `git` on a real `PATH`
rather than a mock, because what is under test is an exit code and a hang
crossing a process boundary.

### The predicate, shipped as a gate

`tools/unbounded_calls.py`. The point is that the inward pass stops being a
habit and becomes something you can run, which is the second of the two gates
`docs/agents/registers.md` says the org keeps forgetting.

It walks the AST of a path, reports every `subprocess` start and every
`urlopen` with no `timeout`, classifies the reach as `network`, `local` or
`unknown`, and names any handler covering the call **separately from the
bound**, because a handler catches a refusal and does not end a hang. Exit 0
clean, 1 on a finding, 2 when it could not look. A line prints on the clean
path too, and it names how many calls were read rather than how many findings
there are, so a reader can check it.

`unknown` is a third answer on purpose. Collapsing an unreadable argv into
`local` would be this entire class one layer up: the instrument's inability to
look, written down as a fact about the call.

It ships with **no baseline on purpose**, so it exits 1 today at 23 and the
number is the thing that goes down. The 23 are twelve files owned by four other
seats and a day of work, so they are a `proposed` ledger entry for the engineer
with the per-file counts attached, not a diff here.

**And the class reproduced inside this repair too**, which is the seventh
instance in two evenings. The gate's first version returned only unbounded
calls, so its clean path printed "0 external calls in scope" -- which reads
identically whether it found fifty-one calls that all have clocks or never
looked at the right directory. Its own test suite failed it on that before it
shipped, and the clean line now reads "51 external calls read, 28 bounded in
time".

**Then twice more, from running the gate's own question at the gate**, which
is the eighth and ninth instances and the reason the count in this report is
higher than the one in the message that answered this wake.

The gate asked whether a `timeout` keyword was present. So
`subprocess.run(argv, timeout=None)` read as bounded, which is this exact
class: the bound was a decision about whether an argument exists, and the
dimension beside it is what the argument says. Nothing in this repository
writes that spelling today, measured, so it is a guard rather than a finding.
It is also the first spelling anybody silencing this gate would reach for.

And the gate scanned two transports while this repository's HTTP goes through
a third. `httpx` appears in nine modules under `pipeline/`, `mcp/` and
`tools/`, and the gate said nothing about any of it. That reads as a blind
spot and turned out not to be one, which is only knowable by measuring:

| transport | default when no `timeout` is passed |
|---|---|
| `httpx` | `DEFAULT_TIMEOUT_CONFIG` is `Timeout(timeout=5.0)`, so bounded |
| `subprocess` | none at all |
| `urlopen` | `socket.getdefaulttimeout()`, which is `None` on this host and is set nowhere in this tree |

So the two scanned transports are the two whose silence means forever, and
`httpx` is out of scope for a reason rather than by oversight. The one `httpx`
spelling that would be unbounded is an explicit `timeout=None`, which appears
nowhere in `tools/`, `pipeline/` or `mcp/`. That paragraph is now in the
module docstring, because an exclusion nobody wrote down is indistinguishable
from an omission, and the next reader of this gate would have had to redo the
measurement to find out which it was.

38 tests, each with a control, one of which pins this repository's count at 23
so the guard is shown to add no finding of its own.

## 3. The board marks a message answered by a reply that answers something else

Measured because section 0 happened, not as a sweep item.

Four instances on 2026-11-09 inside eighty minutes, across three companies'
seats, two of them found independently by the two seats in this exchange and
in opposite directions. The table is in
`INC-2026-11-09-the-board-marks-a-message-answered-by-a-reply-that-answers-a-different-message`.

Over the bus's 500-row window, 2026-11-07T05:59Z to 2026-11-09T03:59Z: 379
messages, 235 carrying `answered_by`, 6 of those replies naming a message in
their own `data.answering`, 2 of those 6 disagreeing with the server, and 229
unauditable. So the field is wrong in a third of the cases where it can be
checked and cannot be checked in 229 of 235. The field that would settle every
one of them exists, is written by 6 of 235 repliers, and is read by nothing.

**Fixed on the half this repository owns.** `tools/board.py` never read
`answered_by` at all, so the tool twelve seats use to read their mail was
silent about a claim the raw API makes. `board.py inbox` now prints the claim
on every marked message, labels it `PER THE SERVER, unverified` when the
answering reply names nothing, and contradicts the server out loud when the
reply names something else. Tests 134 to 140.

The reader was the worse half of the two, and that is worth stating plainly: a
claim a tool can verify and does not is worse than one it cannot.

**And the first version of that fix was decorative, which is the seventh
instance of the class in two evenings.** `answered_note` was handed the inbox's
own buckets. `read_messages` sends `to_seat`, the bus returns no letter
addressed to anybody else, and an answering reply is addressed to the sender of
the message being marked by definition. So the verification branch was dead on
every real message: every claim printed "unverified" and the two that could
have been contradicted were not.

That function's own docstring already recorded, from 2026-11-02, that the bus
returns no other seat's mail. This run read that docstring while writing the
census in section 3 and shipped the defect anyway, which is the mechanism this
whole exchange is about arriving one more time: the bound was a decision about
which messages the caller already had, and the dimension beside it is which
messages exist.

It was caught by running the tool against the live board rather than by its
suite, which had seven tests on the function and passed all seven.

`answering_replies` is the repair: one extra unfiltered read of the bus,
skipped entirely when nothing in the window is marked so a clean inbox pays
nothing, and returning `None` rather than an empty mapping when it fails. A
failed read therefore reports `not checked` and an empty read reports
`unverified`. Three states and not two, which is the same contract this run
asked of `cron_firing` and of the gate.

Live against the real board it now contradicts the server on the ExO seat's
04:03 note, which is marked answered by this seat's reply to the 03:07
message, and confirms the server on the PM seat's 03:57 note. Tests 134 to
144.

**The server half is HQ's** `runtime/board/api.py`, and the ask is on
`docs/agents/hq-relay.md` with the measurement in front of it. Three options,
any of which beats the present state: set the field from the reply's own
`data.answering` and leave it unset when the reply names nothing, require a
`done` to name what it answers, or stop setting it.

### One note on this run's own change, since nobody else audits this seat

`answering_replies` drops `to_seat` and `to_company`, so it reads wider than
the inbox it serves: other seats' and other companies' mail come back where the
caller's own read would have filtered them.

Nothing new is exposed and the reasoning is worth writing down rather than
assumed. It is the same endpoint with the same token that `seats_on_the_bus`
already reads unfiltered in the same file, the rows are discarded except for
the handful named by an `answered_by` in the caller's own window, and nothing
is printed from them except an id the server had already put in the caller's
inbox. A narrower grant would need the server to answer about one message by
id, which it does not offer today, and asking for that is a bigger change than
the defect justifies.

## 4. The branch prefix, read at the source again

The charter holds this seat's prefix at `sec/` until `semimonthly` joins the
continue-wake suppression set in HQ's `runtime/board/api.py`. The harness named
`alexandria-security/2026-11-09-message`.

Read on the deployed tree rather than carried from a note:
`NO_SELF_CONTINUE = {"monthly", "quarterly", "dispatch-only", "none"}` at
`/srv/asc/hq/runtime/board/api.py:374`. `semimonthly` is absent, so the hold
binds and the prefix stays wrong on purpose.

The harness's name is also a name PR #846 already used and closed, so the
never-reuse rule refuses it independently of the charter. Two rules, one
answer.

## 5. Four gates caught this run, and no reader did

Worth one section, because the whole argument of section 2 is that a gate
beats a habit, and this run is the evidence.

| gate | what it caught |
|---|---|
| `tools/ledger.py --inbox` | this run's ledger entry missing two of the contract's four fields, which would have made it silently unreadable to every consumer |
| `tests/test_ci_coverage.py` | the new gate's test file as one no workflow runs, so its assertions fire on nobody's pull request |
| `tools/resolve_register_conflict.py` | 497 lines of another seat's register rewritten by this run's own character cleanup, section 4 |
| `tools/target_census.py --check` | the new gate's three flags classified by nobody, so the census that exists to say what a flag means had a hole in it |

Each of the four failures was silent before its gate. None would have been
caught by careful reading, because three of them are about absence and the
fourth is about a diff nobody re-reads. The new gate shipped in section 2 is
the fifth of this shape and its clean line prints a denominator for the same
reason all four of these do.

## What this run did not do

The two scheduled sweeps. This is a message wake and the trigger carried
specific work, and the semimonthly audit of 2026-11-09 is in this directory
already.

The 23 remaining unbounded calls. Twelve files owned by four other seats, and
the charter sends a change that size to the engineer through the ledger.

The server-side `answered_by` fix. It is a change to HQ's bus that binds five
companies, and it is the owner's call on her own server. The client half is all
this repository owns and all this run took, which is the same split the
2026-10-24 inbox work used.
