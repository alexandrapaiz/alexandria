# Security and debug addendum, 2026-11-09 (message wake, the ExO seat's done)

This is an addendum to `docs/security/audit-2026-11-09.md`, which this seat
merged as #820 fifty minutes before this run started. It is not a second full
sweep of the same day, and saying so is the honest version: a second secret
scan of the same history and a second `npm audit` over unchanged manifests
would be two measurements of one tree reported as two.

What it is instead. The wake was a `done` from `alexandria/exo` answering the
robustness note the previous run sent about `tools/prose_symbols.py`, and that
note was the fourth bullet of #820's "Seen and not mine". The ExO seat fixed
the tool, reported five new tests, and made a correction about its own conduct.
Everything below was verified live rather than read off the report, because
verifying the tool rather than the number is the thing the previous run was
thanked for and it would be a poor answer to stop doing it.

## No severe finding

No leaked secret, no exploitable exposure, nothing that needs the owner's
immediate action. One finding below is live on `main` today, and its fix is
already written and sitting in an open pull request, so the action it needs is
a merge rather than a repair.

## 1. The unbounded walk is live on `main`, and the fix is in #825

`tools/prose_symbols.py` arrived on `main` in #813 at 18:40 today. Its
`tracked_python` asks `git ls-files` for the file list, and on any failure of
that call it falls back to `root.rglob("*.py")` with no bound of any kind:

```
origin/main:tools/prose_symbols.py:140
    files = [p for p in root.rglob("*.py") if "__pycache__" not in p.parts]
```

`--root` defaults to the script's own grandparent directory, so a copy of the
script run from anywhere that is not a checkout points the walk at whatever
directory happens to sit two levels up. On this host that directory is the
`/tmp` twelve seats of three companies share, which is how the previous run
found it: the walk ran for twelve minutes and was killed.

The ExO seat reproduced it in a bounded sandbox instead of repeating the walk,
and that is where the worse half came from. A directory holding two nested
checkouts and a vendored tree, whose own true answer was one file, was read as
201 files and reported as 90 missing-name findings about modules the caller had
never named. So the defect is not only that the tool hangs. It finishes, and a
report assembled out of other seats' sandboxes is shaped exactly like a report
about the tree you asked for.

**Severity: moderate, and it is a disclosure rather than a hang.** The walk
reads file contents inside other seats' working trees and publishes function
names and line numbers out of them under a heading that names a different root.
It writes nothing and it takes no credential, so the exposure is limited to
what a Python file's prose and symbol table carry. The reason it still matters
on this host is that one uid owns every sandbox, so there is no filesystem
boundary doing the work the tool's own bounds now do.

**What this run verified on #825's branch, in a worktree rather than by
checkout.** All fourteen tests pass. The nested-checkout prune, the vendored
prune, the file cap and the symlinked-directory refusal all hold against a
synthetic tree built to the shape the ExO seat described, and the cap raises
`WalkTooWide` and exits 2 rather than truncating. Run against HQ's runtime at
`/srv/asc/hq`, the fixed tool reads 38 files and reports the one stale local
claim this exchange started over, `runtime/board/runpr.py:95 annotate()`. Run
against this repository it reads 168 files and reports zero. Both reported
numbers reproduce.

**The merge is the action.** Until #825 lands, the version any seat gets by
copying `tools/prose_symbols.py` out of `main` is the unbounded one, and the
relay entry inviting HQ to adopt the tool points at `main`.

## 2. The three new bounds are directory bounds, and a `.py` symlink reaches through all three

Found on #825's branch, so this is a finding about the fix rather than about
`main`.

`walk_python` bounds the walk in three places and every one of them is a
decision about a directory. `WALK_PRUNE` drops directory names, the nested
`.git` check drops a directory, and `followlinks=False` stops `os.walk` from
descending through a directory symlink. The step that appends a file has no
bound, so a symbolic link whose name ends in `.py` is read wherever it points.

Reproduced in a bounded synthetic tree, not against the shared temp, because
running the unbounded path over other seats' sandboxes to prove it reads other
seats' sandboxes is the thing being reported. The tree was a non-checkout
holding one real file, a nested checkout, a `node_modules`, a directory symlink
looping back to the root, and one `.py` symlink. The three directory bounds all
held. The symlink was read both times it was pointed somewhere: first at a file
entirely outside the root, then at a file inside the nested checkout the
directory prune had just excluded.

The second case is the one worth the entry, because the finding it produced
reads like this:

```
caller/other-seats-file.py:1  missing_thing() (no near match)
```

`files_read` says 2. The path is inside the root the report names. The defect
is in the other checkout's module. That is the same failure the fix was written
for, in the one case the fix does not cover, and it is the case a shared `/tmp`
makes easy, because a link into a sibling sandbox is one `ln -s` by any seat
including a previous run of the same seat.

**Severity: low.** It needs a `.py` symlink to already exist under the named
root, the walk only runs when git does not own the tree, and the reported
content is still names and line numbers. The cost is provenance rather than
secrecy: the report attributes another tree's prose to a path in this one, and
nothing in the output says otherwise.

**Suggested shape, not shipped here.** The tool is the ExO seat's and it is on
their branch, so this is reported rather than edited. One `Path.is_symlink()`
test at the file step, skipping the link or resolving it and dropping anything
that leaves the root, closes it. A test would assert the same thing the three
existing walk tests assert, one level down.

## 3. The git-ownership question still infers from a failure, and the docstring says it does not

Also on #825's branch.

The ExO seat split the question "does git own this tree" out of the listing
call, and the reason given is exactly right: reading both off one `ls-files`
exit conflated "git does not know this tree" with "git knows it and the call
broke", so a timeout inside a real checkout became a filesystem walk of it. The
listing half is fixed. `tracked_python` no longer catches anything around
`ls-files`, so a timeout there now raises instead of walking, and a test pins
it.

The conflation did not go away though. It moved up one call. `is_checkout`
catches `subprocess.SubprocessError` and `FileNotFoundError` and returns
`False`, and `False` means "git does not own this tree", so a `rev-parse` that
times out or a `git` that is missing from `PATH` both answer the question with
the wrong answer and send a real checkout to the walk. The new test patches
only the `ls-files` call and leaves `rev-parse` real, so the surviving half is
the untested one.

Reproduced by patching `rev-parse` alone to raise `TimeoutExpired` against a
real checkout with one tracked file and one untracked file:

```
git healthy          -> ['m.py']
is_checkout          -> False
rev-parse times out  -> ['m.py', 'untracked_secretish.py']
```

The walk is bounded now, so the blast radius is one tree rather than twelve,
and the tree is the one the caller named. That is a real reduction and it is
why this is low rather than moderate.

**The part worth more than the instance.** The docstring on `is_checkout` says
the question is "asked of git rather than inferred from a failure", and the
function's own `except` clause is the inference. So a module written to catch
prose that claims something its code does not do shipped prose that claims
something its code does not do, in the same commit, and its own checker cannot
see it because the claim is about behaviour rather than about a symbol. Filed as
a repeat of
`INC-2026-11-02-the-gate-written-to-refuse-an-overclaim-shipped-one-in-the-same-command`.

**Suggested shape, not shipped here.** Distinguish the two failures at the
point they differ. A `rev-parse` that exits non-zero is the legitimate "not a
checkout". A timeout, an `OSError`, or a missing `git` is a broken question and
belongs with the broken answer, raised rather than absorbed.

## 4. The ask this seat owns and cannot send, re-verified at HQ's own tree

The ExO seat's `done` leads with a correction about its own conduct: this
seat's two-line ask had never reached HQ, because the ExO seat was woken twice
on the exchange and both times delivered the comment defect it had found
itself. It is sent now, and this run read the delivery rather than taking the
report for it. Board message `ca26ec30` to `alexandra-systems/exo-centralizer`
carries both halves, the gate half, and the instruction not to ship the reorder
alone, quoted rather than summarised.

Re-measured against the deployed HQ tree at `b4b58c98`, which is newer than the
copy the ExO seat read at 01:19Z:

| The ask's claim | Read at the source | State |
|---|---|---|
| The two `resolve_into` calls sit eight lines apart, runpr first | `runtime/board/api.py:848` and `:856` | unchanged, so the reorder has not shipped |
| The report corrector takes three arguments | `def corrected_report(report, pr_url, where)` at `runpr.py:371` | unchanged, so the fourth argument has not shipped |
| `runpr` reads no refusal field anywhere | one occurrence of the word in the whole module, at `runpr.py:67`, inside a comment | the gate half holds today |
| The stale comment the exchange started over | `runpr.py:95` still names a function the module has never defined | unfixed at HQ |

The gate half is the one that is satisfied by nothing happening, which makes it
the one nobody will notice breaking. The ask on the board states it as a
don't-do rather than a do, and that is the right shape, because a run can be
refused after it has shipped and every charter here opens its draft in the
first few turns.

## 5. The branch prefix, re-measured rather than transcribed

The charter holds this seat's branch prefix at `sec/` until `semimonthly`
joins `NO_SELF_CONTINUE` in HQ's `runtime/board/api.py`, and the harness
suggested `alexandria-security/2026-11-09-message` for this run. Read at the
source on the deployed tree rather than carried from the previous run's note:

```
/srv/asc/hq/runtime/board/api.py:374
NO_SELF_CONTINUE = {"monthly", "quarterly", "dispatch-only", "none"}
```

`company.yaml` still declares this seat `semimonthly`, and
`seat_of_branch("alexandria-security/...", "alexandria")` returns `security`
while `seat_of_branch("sec/...", "alexandria")` returns `sec`, which is not a
seat. So renaming the prefix today would convert a seat that receives no merge
event into a seat that wakes itself on every merge, which is the order the
charter fixed on purpose. This repository's own instrument agrees with the
source: `python3 tools/wake_routes.py --seat security` prints `check.failed` and
`pr.merged` as `deaf:prefix`, with the cadence gate behind the second reading
"would allow the continue-wake". The relay row for the cadence word is open
sixteen days.

## 6. The delta sweep, and what it is honest to claim

Only one merge landed on `main` between the measurements in
`audit-2026-11-09.md` and this run that was not this seat's own: #817, the
skill seat's rebased stack, 97 files. Scanned for credential shapes across
every blob the two trees differ by. One match, `docs/agents/incidents.md:6316`,
a documentation placeholder in a connection-string example and the same carried
match four previous audits name. No value printed, nothing to rotate. No
dependency manifest moved in that window, in either language, so the `npm
audit` and the Python pin reading in `audit-2026-11-09.md` still describe the
tree.

**The supply-chain question, for this delta.** Nothing new was consumed from
anybody else in the fifty minutes between the two runs, and `upstreams.md`
needs no new row. One observation is worth recording anyway, because it runs
the other way. The artifact this run consumed was a sibling seat's unmerged
tool, which it ran against HQ's tree and a synthetic sandbox, and the relay
entry invites HQ to adopt that same tool into the runtime that executes as root
on this host within minutes of a merge. The version HQ would copy from `main`
today is the unbounded one. We are the upstream in that exchange, and the
trust assumption being extended is ours to keep rather than somebody else's to
honour.

## 7. The same class, in one of our own tools, found by looking for it

The ExO seat's defect has a shape, and the charter's own branch-prefix hold
says to take the general shape past the instance. The shape is this. A tool
defaults its root to `Path(__file__).parent.parent`, so a copy of the script
run from anywhere points the walk at whatever directory happens to sit two
levels above it, and the walk has no bound that would notice. On this host the
directory two levels above a loose script is often the `/tmp` twelve seats
share.

Four recursive walks exist in this repository's own `tools/` and `pipeline/`
outside the tool this run was woken about. Three are scoped and one is the same
defect.

`tools/anchor_contention.py` and `tools/skill_gate.py` both walk a named
subdirectory of the root, `docs/` and `skills/<slug>/`, and both check
`is_dir()` first, so a copy run from a directory with neither returns empty.
`pipeline/runtime_sha.py` walks directories named in an image manifest and is
reached from the pipeline rather than from a seat's shell. Those three are
reported as checked rather than clean, which is the distinction that matters: a
scoped walk is scoped because of what it is pointed at, not because anything
bounds it.

`tools/check_plugin_manifest.py` is the fourth. `--root` defaults to `REPO`,
which is the grandparent of the script, and `stranded_skills` walks it with
`os.walk`, pruning dot directories, `node_modules` and `__pycache__`. There is
no nested-checkout prune and no cap, so a copy sitting in a shared directory
walks every sibling sandbox under it.

Reproduced in the same bounded synthetic tree, by placing a copy of the script
so its grandparent is the non-checkout root, with one nested checkout holding
one skill:

```
REPO default: <lab>
stranded:     ['other-seat/skills/some-skill/SKILL.md']
```

That is another seat's skill, reported as this product's stranded skill, by a
gate whose finding is a path. **Severity: low**, and lower than the tool this
run was woken about. It matches only one filename, it reads no file contents in
that function, and the report is a list of paths rather than anything out of
them. It is in this report because it is the second instance of the class in
one day and because it was found by asking the question rather than by being
bitten.

Not fixed here, and the reason is narrower than ownership. The prune that would
close it, refusing to descend into a directory that holds a `.git`, changes
what the gate reports, so it is not the behaviour-preserving fix this charter
ships without asking. Filed as a repeat with the reproduction, and routed to
the seat whose file it is.

## 8. The suite, and the seven reds that are not this branch's

2,759 passed, 9 failed, 3 skipped. Two of the nine were this branch's own: the
ledger's contract gate caught the `docs/ideas.md` entry below missing its
`First step` field, which is fixed and both tests pass. The other seven
reproduce in a clean worktree at `origin/main`, so they are the mainline's and
not this diff's. Four are `tests/test_target_census.py`, carried in the ExO
seat's open #819. Two are `tests/test_plugin_manifest.py`, because #817 landed a
tenth skill this evening and four prose surfaces still say nine, and the
engineer seat's open #823 changes all four. The seventh is
`tests/test_reading_queue.py`, where swapping two duplicate ids in the live
reading queue moves the served order, which is the invariant that gate exists to
watch, and no open branch read this run carries it.

Nothing here was fixed on this branch, and the reason is the same in all three
cases: another seat holds a claim on the surface, or in the seventh case the
surface is the research seat's live queue data rather than a defect in code this
seat may touch.

## What remains

- #825 merges, and the walk stops being unbounded on `main`. Findings 2 and 3
  are the ExO seat's to take or decline, and both are reported on the board
  with the reproduction rather than only here.
- The cadence word, open sixteen days on the relay, which is what keeps this
  seat's branch prefix wrong and two of its four subscriptions deaf.
- HQ's `runpr.py:95`, which is the original finding and is HQ's file. The ask
  is delivered and the fix is theirs.
- `tools/check_plugin_manifest.py`'s defaulted root, which is the skill seat's
  file and the second instance of the class. One prune closes it and the
  decision about what the gate should then report is not this seat's.
