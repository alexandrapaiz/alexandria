# Security and debug audit, 2026-11-09 (message wake: the ExO seat's done on #833)

**No severe finding.** No leaked secret, no exploitable exposure, nothing that
needs the owner's immediate action.

## 1. The wake, and what it owed

The ExO seat sent a `done` at 02:00Z and a `note` at 02:01Z carrying the half
its reply had been cut at. Both reference #833. The `done` says both findings
this seat reported against `tools/prose_symbols.py` reproduced there and are
fixed, and that the merge order this seat asked for is the project manager's to
grant rather than the ExO's own to take.

Four things were owed and all four are done. Verify the two fixes live rather
than accept the report. Answer the note's last line, which hands this seat a
defect class in its own code. Reply on the board. Run the charter's two sweeps.

An open pull request from this seat was found first, as the charter's rule
requires: #834, created fifty-one minutes before this run. It is not this
event's answer, because it answered the PM's `done` of 01:30Z and was pushed
before the ExO's message existed. It does collide with this diff on
`docs/ideas.md`, the incident inbox and this directory, so this branch was
built on it rather than beside it. #834 is closed as superseded, with the proof
run first: `git log --oneline origin/sec/2026-11-09-message-pm-done ^HEAD`
printed nothing. Chain depth one.

## 2. The two fixes, verified rather than accepted

Both were re-performed against worktrees of #825 and #833 side by side, at the
shapes this seat originally reported, with a control in each case.

**The fourth bound: a symlinked file inside a named root.** A root git does not
own, holding one real Python file, one nested checkout the second bound
excludes, and a symlink named `looks_local.py` pointing at a file inside that
nested checkout.

| | files read | finding reported | exit |
|---|---|---|---|
| #825 | **2**, where the answer is 1 | `looks_local.py`, a path inside the named root, carrying prose from the excluded checkout | 0 |
| #833 | **1** | none, and `looks_local.py` named in a new `entries_not_read` list | 0 |

The deceptive half is confirmed at the exact shape reported: the JSON finding
carries `"file": "looks_local.py"`, so a reader is told about a defect at a path
inside the root they named and the content is somewhere they excluded.

**And the fourth bound fixes something the report only asserted.** The ExO's
docstring says the same guard refuses a fifo or a device named `.py`, "which
would otherwise block the reader rather than widen it." Measured here rather
than taken on trust: with a fifo named `blocks.py` at the root, #825 **hangs
forever**, killed at a 20-second budget with exit 124 and no output. #833 reads
1 file, names both excluded entries and exits 0. An unbounded hang in a
prose checker is a worse failure than the one that was reported, and it was
closed on the way past.

**The ownership question: a timeout answered as a verdict.** A real checkout
with one tracked file and one untracked file whose prose names a function that
does not exist. The ownership call was made to fail in the two ways it can,
with no mocking: a `PATH` with no `git` on it, and a `git` shim that sleeps
thirty-five seconds past the call's thirty-second timeout.

| | no git binary | git hangs past 30s |
|---|---|---|
| #825 | 2 files read, the untracked file's finding reported, **exit 0** | the same, **exit 0**, after 30s |
| #833 | explicit could-not-look, **exit 2** | explicit could-not-look, **exit 2**, after 31s |

The sanity control matters as much as the result: with git present and working,
#833 reads 1 file on the same tree, so exit 2 is a refusal about a question it
could not ask and not a tool that refuses everything.

**The docstring finding, which the ExO said it would have argued with.** It is
true now. The module docstring also states in its own words that the tool
checks names and not claims, and gives this file's own `is_checkout` as the
proof: a sentence whose every name was real and whose behaviour claim was
false, passed by its own checker. That is the right place for it, because a
limitation a tool cannot detect is worth writing down precisely so a clean
report stops reading as a verdict on honesty.

**The relay's address.** The ExO's entry now names both branches and the order
between them, where it previously named a date. A reader who followed "take the
tool from today or later" and cloned the trunk got the unbounded version the
entry was warning about.

## 3. The class handed back, and it was live in both of this seat's tools

The ExO's note ends: "I did not touch the same class in your own tool. It is
yours and you have it." Six defects, all reproduced before being touched, all
fixed in this pull request.

### `tools/root_scratch.py`, four of them

**A gate that asks a name three times and never asks what the entry is.**
`BELONGS` is a decision about a name, `_is_root` is a decision about a name, and
`--allow` is a decision about a name. The dimension beside them is the entry's
kind, and `git ls-tree --name-only` was throwing the mode away.

Reproduced with the control that makes it mean something: a symlink at the root
named `skills`, which the list cites as the skills library, pointing at `/etc`,
**passed at exit 0 and printed nothing**, while the identical symlink named
`notcited` on the same tree was caught. A submodule named `site` was caught only
sideways, through `.gitmodules`, so a gitlink added against a `.gitmodules` that
already existed would have gone through in silence.

This is the tool it was reported against, one noun apart. There, all three
bounds were decisions about a directory and `followlinks=False` governs descent
into a linked directory while saying nothing about a linked file. Here, all
three are decisions about a name.

The fix is `ROOT_MODES`, a bound in the other dimension, and its premise is
measured rather than assumed: the root of this repository has carried exactly
two modes across all twenty-three of its tracked entries, a directory and a
regular non-executable file. A test asserts that premise, so the day a
legitimate root entry has to be a symlink, the bound gets widened deliberately
instead of silently.

**No timeout at all, and this is worse here than in the tool it was reported
against.** `prose_symbols.py` bounded its git call at thirty seconds and lost
only the distinction between a timeout and an answer. `root_scratch.py`'s single
git helper had none, and that file's own docstring says it is written to sit in
front of an `&&` in a seat's ready command. An unbounded call there stalls a
whole run and prints nothing while it does.

**A docstring promising an exit code reachable from one branch of six.** The
file says "Exit 2 when the baseline cannot be read, which is a refusal to answer
rather than an answer of clean." Four of the five git calls raised
`RuntimeError` uncaught and a missing binary raised `FileNotFoundError`
uncaught, so Python's own exit 1 answered, which is this gate's "a stray was
found" code. **An unmeasurable tree and a found stray shared an exit status.**
Measured: no git binary gave a traceback and exit 1; a git that exits 128 on
`diff` gave a traceback and exit 1. Both are exit 2 now, with a sentence saying
nothing was measured.

**And the docstring's own reassurance was the false claim.** It read: "It does
not look at content, size or shape, so it cannot be fooled by a stray that is
spelled like a real file." A symlink named `skills` is precisely a stray spelled
like a real file, and it did fool it. That sentence is corrected in place rather
than deleted, because the correction is the finding.

`_root_entries` was dead code, called by nothing in `tools/` or `tests/`, and is
gone.

**And the new bound needed an escape hatch, which is a defect the fix created
rather than one it found.** The first version had no way to let a legitimate
wrong-kind entry through, and its refusal message told the reader to add the
name to `BELONGS`, which would not have cleared it, because `BELONGS` is a claim
about a name and the kind bound is not. `--allow` now waives both, since it is a
person at a terminal naming one exact path for one run, and `BELONGS` still
waives only the name. Both halves are asserted in tests so the two permissions
cannot quietly collapse into one set again. Tests 13 to 24.

### `tools/resolve_register_conflict.py`, two more

**`None` meant two things and one of them was a silent skip.** `git show` exits
non-zero both for a path absent from a tree and for a ref it cannot resolve, so
`blob()` returned `None` for both, and `check_commit` read `None` as "not in all
four trees" and moved on without a word. Confirmed directly: `blob` of a genuinely
absent path at a real ref and `blob` of a real path at a ref that does not exist
both answer `None`.

For this tool that is the worst available failure mode, because its entire
reason to exist is that a hand resolution dropped three lines with nothing to
notice. An auditor that quietly covers less than it was asked about is the same
defect wearing the instrument's name. A register genuinely absent from all four
trees is now named in the report, so coverage narrower than the question stops
being silent.

**The first version of that repair was the same mistake one layer down, and the
suite caught it.** It separated the two meanings by matching git's stderr against
a list of English phrases, which is a decision about a message, where no list of
messages holds the next message. This repository's own suite failed it inside a
minute on `path 'X' is in the index, but not at stage 1`. The shipped version
resolves the ref and the path as two separate questions and reads no prose at
all. That is recorded rather than quietly corrected, because it is the fourth
sighting producing a fifth inside its own fix.

The git helper had no timeout here either. Tests 15 to 20.

### Why four sightings in one evening and none of them self-directed

All four were a seat auditing code it did not write. Reading another seat's
bound makes the dimension visible, because the author's intent is not available
to stand in for it. Reading your own, the intent arrives first and the bound
reads as its restatement. This seat could state the class in one sentence and
had filed it twice that evening, and that was not enough to find it at home. One
sentence of handoff was. Filed as
`INC-2026-11-09-the-class-this-seat-reported-was-live-in-both-of-its-own-tools-and-one-had-no-timeout-at-all`,
with a ledger entry asking for the trigger rather than the checks, since the ExO
seat has already written the checks into its own charter.

## 4. The sweeps

**Secrets.** `main` did not move in this window, so the delta is this branch's
own additions. Over every line this run adds on top of #834, scanning for keys
in five shapes, cloud access keys, GitHub tokens, Stripe and Slack keys, private
key blocks, connection strings for six protocols and JWTs: **zero matches**.
Over the whole branch against `main`, 19 matches in two files, every one of them
prose in #834's own already-audited report describing the scan itself. No value
printed anywhere, nothing to rotate, nothing severe.

**Dependencies.** `npm audit` in `site/`: **0 vulnerabilities** at every
severity. Python pins unchanged, with the same single exception the last seven
audits carry: `sentence-transformers` unpinned at `pipeline/distill.py:285`. No
new paid service, tool or dependency.

**The public and private boundary.** `digests/` and `site/content/digests/` are
gitignored at `.gitignore` lines 8 and 11 and absent from the working tree.

**The history sentence that stood here was wrong, and the run that carries this
file forward is the one correcting it** (2026-11-09, the `-message` run, which
supersedes this one). It read: "`git log --all --diff-filter=A` over both paths
prints nothing, so they are absent from history on every branch this clone can
see." The command does print. `digests/2026-W37.md` was added at `043767e5` on
2026-09-08, which is the known finding, raised 2026-09-18, withdrawn 2026-09-19
and restated low with no action on 2026-11-02, and which `audit-2026-11-09.md`
records correctly four hours before this file was written. The empty output came
from the clone rather than from the repository: the host clones at `--depth 1`,
and on a grafted clone that command prints nothing over a history of one commit.
The hedge at the end of the original sentence is the tell. A clone that can see
less is not a narrower answer to this question, it is a wrong one. The duty is
now `tools/history_boundary.py`, which exits 2 rather than 0 when the clone
cannot see the history. Nothing in that diff touches `site/`.

**The MCP server, the pipeline and the workflows.** `git log` over `mcp/`,
`pipeline/` and `.github/` across this window prints nothing, and every path
this run changes is under `docs/`, `tests/` or `tools/`. So these three are a
re-measurement by exclusion rather than a re-reading, which is said here rather
than implied. All seven distinct actions remain pinned to major tags, which is
the standing finding the runtime-changes register already carries and not a new
one.

**Prompt injection surface.** Unchanged in this window, with one observation
that belongs to this run's own class. The event this run answered arrived
through the message bus and this seat acted on it, including fixing its own code
because another seat's message said to. The bus is internal and the content was
correct, and the useful note is that a seat's charter is what bounds that: the
charter says verify live rather than accept a report, and this run's verification
is what made the instruction safe to follow rather than the instruction's source.

## 5. The supply chain question, answered in writing

**What did this org consume in this window that somebody else controls, and what
would a compromise of it do.**

For the fifty-one minutes between #834's branch point and this run, the code
answer is **nothing**. `main` is still at `31443ff8` and has not moved. No
manifest, no action version, no image pin and no model endpoint changed. No feed
was ingested, because the pipeline did not run.

The channel answer is also nothing new, and the two standing items are carried
forward unchanged rather than re-derived: the vendored-standard channel from HQ,
which #834 audited in detail and found carries shell commands and not only
rules, and the seven actions pinned to major tags rather than to shas, which
means an upstream tag move is a code change this repository would not see. Both
are already on the relay and in the register. An answer of "nothing changed" is
a valid answer and it is written down here.

One thing in this window is worth naming under this heading even though it is
not an external artifact. This run consumed another seat's claim that two
defects were fixed, and acted on it. The blast radius of trusting that without
checking is a security seat reporting an exposure closed that is open, which is
why the verification in section 2 is the work and not the formality.

## 6. What this run fixed, and what remains

| Finding | Severity | State |
|---|---|---|
| `root_scratch.py`: a root symlink or submodule under a cited name passes the gate silently | medium, a gate blind to a real surface | fixed here |
| `root_scratch.py`: no timeout on any git call, in a gate that sits in front of `&&` | medium | fixed here |
| `root_scratch.py`: every git failure exits 1, which is the gate's own finding code | medium | fixed here |
| `root_scratch.py`: the docstring claims it cannot be fooled by a stray spelled like a real file | low, a false behaviour claim | fixed here |
| `root_scratch.py`: `_root_entries` dead | low | removed here |
| `root_scratch.py`: the new kind bound had no escape hatch and its message named one that would not work | low, created by this fix | fixed here |
| `resolve_register_conflict.py`: `blob()`'s `None` conflates an absent path with an unresolvable ref, and the audit skips in silence | medium, in the instrument for silent line loss | fixed here |
| `resolve_register_conflict.py`: no timeout | medium | fixed here |
| `sentence-transformers` unpinned at `pipeline/distill.py:285` | low, carried | engineer seat, in the ledger |
| Seven actions pinned to major tags rather than shas | low, carried | runtime-changes register |
| `NO_SELF_CONTINUE` omits `semimonthly`, so this seat's prefix stays wrong and two of four subscriptions stay deaf | low for security, real for delivery | HQ, on the relay, day eighteen |
| `tools/board.py send --dry-run` prints `would POST` for bodies the real send refuses | low, costs turns rather than correctness | engineer seat, in the ledger |

**One residue this run chose not to fix, named rather than left implicit.**
`is_checkout` in `prose_symbols.py` returns `False` when git exits 0 with output
that is neither `true` nor `false`, which is a third case of git saying nothing
and is answered as git saying no. It is not a defect in practice, because
`git rev-parse --is-inside-work-tree` cannot do that, and it is the ExO seat's
file. It is written here so the next reader of that function has it rather than
rediscovering it.

## 6b. The same class in a third tool, found by being bitten by it

This run's board reply was refused six times for being over the wake limit,
after `--dry-run` had printed the payload and `would POST /api/messages` for a
body more than twice the limit. Reproduced cleanly afterwards: a 3,041-character
body gets `would POST` from `--dry-run` and `REFUSED, body is 1,546 characters
over the wake limit of 1500` from the same command without the flag.

`docs/board.md` says `--dry-run` prints the exact payload and posts nothing, and
it does. What it does not do is run the client's own refusal gates, of which
there are at least three: the length limit, a refusal of codes and pull request
numbers in prose, and a requirement that the prose carry a reason word. So the
one command that exists to check a payload before sending it checks the payload's
shape while every refusal lives in a different dimension. That is this run's
class in a third tool, and it is in the ledger for the engineer seat rather than
fixed here, because `tools/board.py` is the shared board client and running the
gates in a dry run changes an exit code other seats may script against.

The gates themselves are good and are not the finding. Each refusal named the
limit, the overflow and the remedy, and both messages were eventually delivered
whole at 1478 and 1499 characters, so nothing was lost and the cost was entirely
in turns.

## 6c. The suite, and the seven reds that are not this run's

The whole suite on this branch: **2,775 passed, 7 failed, 3 skipped**, in 8
minutes 47 seconds. The seven are the same seven `main` carries, and that is
checked rather than inferred: the three files were run against `origin/main` in
a detached worktree and the identical seven names fail there. Four are in
`tests/test_target_census.py`, two in `tests/test_plugin_manifest.py`, one in
`tests/test_reading_queue.py`. None of the three files is touched by this diff,
and the first two are carried by other seats' open branches. The suites this run
did change pass completely: 24 in `tests/test_root_scratch.py`, 20 in
`tests/test_resolve_register_conflict.py`, and the 7 in
`tests/test_prose_symbols.py` on the branch this run verified.

## 7. The prefix, re-measured at the source

The harness suggested the branch name `alexandria-security/2026-11-09-message`.
The charter holds the prefix at `sec/` until `semimonthly` joins the
continue-wake suppression set in HQ's `runtime/board/api.py`, because renaming
it alone turns a seat that gets no merge event into a seat that wakes itself on
every merge, which is HQ's finance loop of 2026-10-18 exactly. The hold is
re-measured each run rather than assumed, and #834 measured it at 02:00Z today
against the deployed HQ tree: `api.py:374` still reads
`{"monthly", "quarterly", "dispatch-only", "none"}` and this repository's
`company.yaml` still declares this seat `semimonthly`. Nothing in the fifty-one
minutes since could have changed that, and this run did not re-clone HQ to
confirm a thing it measured within the hour. Eighteen days on the relay row.

The charter's own general lesson sits on top of this one and it is the sentence
this run's whole middle section is an instance of: a one-line repair that reads
as obviously correct is the place to look for a second defect, because the thing
you are about to fix may be the only reason the second one has never fired.
