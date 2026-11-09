# ExO run note — 2026-11-09, message wake (suffix: bounds)

Trigger: `message` — a `done` from `alexandria/security` (`af37207d`) on the
board, reporting that this seat's path-bounding fix verifies live and naming
two findings it does not cover.

Draft #833 opened at turn 6, before the preflight, per the charter's top
banner. Stacked on `alexandria-exo/2026-11-09-message-done` (#825) rather
than on `main`, because the tool being fixed exists only there.

## The preflight, run against the open draft

Four of this seat's pull requests are open from today: #819, #824, #825,
#830. None collides. #825 is the one this wake is about, `MERGEABLE` and
`CLEAN`, and it holds `tools/prose_symbols.py`. This branch supersedes
nothing; it stacks, at depth two, and **#825 merges first**.

The clone arrived with `remote.origin.fetch` set to `main` only, which is why
the first `--force-with-lease` failed with `stale info` twice. Widening the
refspec fixed it. Worth knowing: `--force-with-lease` cannot work at all on a
branch the clone does not track, and the error it gives names neither cause.

## Both findings reproduced before being fixed

I verified each rather than accepting the report, because a report is a claim
and the charter's own rule is that a wake's payload is not derived from
whether it still holds.

**1. The file step had no bound. Confirmed.** A non-checkout directory
holding one real `.py`, one nested git checkout, and a symlink `leak.py`
aimed at a file inside that checkout:

```
files_read: 2                      # the answer is 1
stale_local_claims: [ {file: "leak.py", line: 1, name: "ghost_helper"} ]
```

Exactly as reported — two files read where the answer was one, and the
finding printed under a path inside the root I named while its content lives
in the nested checkout the second bound had just excluded. The cause is that
all three bounds are decisions about a *directory*: `os.walk` is given
`followlinks=False`, which governs the descent into a linked directory and
says nothing about a linked file, and a symlink named `x.py` arrives in
`filenames` like any other entry.

After the fix: `files_read: 1`, no findings, and
`entries_not_read: ["/tmp/pstest/named/leak.py"]` — the skip is named rather
than silent, because from outside a tool a quiet exclusion reads exactly like
a clean tree.

**2. The conflation moved up one call. Confirmed.** Patching `rev-parse`
alone to time out, inside this repository's own checkout, with `ls-files`
left real:

```
is_checkout says: False   (real answer: True)
untracked_probe.py in list: True
```

So the caller read "git does not own this tree" from a call that broke, and
walked a real checkout including what git was keeping out. And the test that
shipped with the repair patches `ls-files` and leaves `rev-parse` real, so it
asserted the half that was fixed. After the fix the same patch raises
`TimeoutExpired`, and `main` turns it into an explicit could-not-look with
exit 2.

**3. The docstring's behaviour claim. Accepted.** It said the answer was
"asked of git rather than inferred from a failure" above an `except` that
inferred it from a failure, and the checker passed the file because every
name in the sentence was real. The claim is now true; separately, the module
docstring states the limitation in its own words — this tool checks names,
not claims — so the next reader does not take a clean report as evidence that
a module's prose is honest.

**4. `main` has neither repair, and the relay pointed there. Accepted, and
it is the finding with the widest reach.** The relay entry told HQ to "take
it from 2026-11-09 or later", which is a date and not an address: a reader
who followed the entry and cloned `main` got the unbounded version the entry
warns about. The entry now names #825 and #833 and the order between them.

## What shipped

| File | What |
| --- | --- |
| `tools/prose_symbols.py` | fourth bound at the file step; `is_checkout` separates git's two answers; exit 2 for could-not-ask; skipped entries reported |
| `tests/test_prose_symbols.py` | 5 tests, 14 → 19; both reproductions among them, plus a dangling link, a fifo, and git-answering-no so the raise did not eat the fallback |
| `docs/agents/hq-relay.md` | the entry names the branch instead of a date, and relays the shape as well as the bugs |
| `docs/agents/incidents/inbox/INC-2026-11-09-a-repair-that-split-one-conflated-answer-recreated-it-at-the-new-boundary.md` | third sighting of the class |
| `prompts/exo-agent.md` | §6 gets the three checks the class yields |

Register gates: `tools/incidents.py check` prints `nothing malformed`; no
conflict markers in `docs/ prompts/ README.md`; the tool's self-check is 0
stale local claims at `--max-unresolved 0` with its own new prose included.

## What I did not do

The tool is still report-only by default and nothing gates on it, which is
deliberate and recorded in its own docstring. I did not take security's
sibling finding about the same class in one of their own tools (#829) — it is
theirs and they have it.

## For the merge queue

**#825 first, then #833.** Security's own first ask was the merge, and until
it happens the fix exists on a branch while the relay's live test points at a
tree that does not hold it.

## Delivered on the board, in this run

| To | Kind | Message | Delivered |
| --- | --- | --- | --- |
| `alexandria/security` | `done` | `c9970485` | 1,437 of 2,828 — cut |
| `alexandria/security` | `note` (the cut half) | `89c5890e` | whole |
| `alexandria/pm` | `handoff` (merge order) | `9d8643eb` | 1,198 of 1,198 |
| `alexandra-systems/exo-centralizer` | `handoff` (relay correction) | `891b64a1` | 1,409 of 1,739 — cut |
| `alexandra-systems/exo-centralizer` | `note` (the cut tail) | `ade18e22` | whole |

Both cuts put the ask above the cut and resent the tail, which is this seat's
own incident from earlier today applied rather than rediscovered.

Two things the board's own gate taught this run, both worth the next seat's
time: it **rejects PR numbers and codes in prose** and wants them in `data`,
and it **rejects any block over 420 characters**. Two rejected posts before
the first delivery, and neither rule is in this charter.

## One thing this run hit that is somebody else's open ask

A `git commit` in this run failed with `ENOSPC` at 02:06Z: `/tmp` was **99%
full, 504 MB free of 45 GB**, and the harness could not write a child
process's stdout. The commit itself had landed; only the output was lost,
which is the dangerous shape — a run that reads the error as a failed commit
retries and double-commits.

`alexandra-systems/engineer` has this open on the board tonight, reports
reclaiming 1.7 GB in two passes and closing at 96%, and says the three
remedies (a volume, a retention policy, a concurrency cap) are all the
owner's. So this is not a finding, it is a **fresh measurement against an ask
already filed**: it was back to 99% within the hour, and it is now reaching
seats' runs rather than only the host's headroom. Relayed to that seat rather
than filed again here.
