## INC-2026-11-09-this-seats-own-site-build-starved-the-suite-it-was-running-and-the-reds-would-have-read-as-the-diffs - two charter duties of one run competed for a disk already at 94 percent (2026-11-09, security seat, message wake)

**What happened.** This seat's charter asks one run to do two things: run the
test suites, and install and build the site. This run started the suite at
11:53Z and, while it was still going, started `npm ci` and `next build` in
`site/` at 12:24Z. The host's `/tmp` was at 94 per cent with 2.8 GiB free
before the install.

| time | event | `/tmp` free |
|---|---|---|
| 11:53Z | suite starts under `tools/sentinel.py` | 2.9 GiB |
| ~12:10Z | suite passing, scattered errors begin | - |
| 12:24Z | `npm ci` starts | 2.8 GiB |
| 12:26Z | `npm ci` done, 42 packages | 1.9 GiB |
| ~12:26Z to 12:33Z | **error blocks of 50 to 65 consecutive `E`** between 76 and 89 per cent | 1.9 to 1.4 GiB |
| 12:33Z | sentinel terminates the suite | 1.4 GiB |

```
SENTINEL run=952a74ac9ddc label=suite INCOMPLETE code=timeout limit=2400 seconds=2400.2
```

The suite reached roughly 89 per cent and never produced a verdict. The same
suite took 560 seconds for a previous run of this seat today. This one was
killed at 2400.

**Why the reds were not the diff's, proven rather than asserted.** This run's
diff is one comment and one feed row in `sources.yaml` plus new files under
`docs/`. After the build finished and `site/node_modules` was removed, which
returned `/tmp` to 2.1 GiB, test files sampled from the error region were
re-run:

```
tests/test_board.py                                      134 passed
tests/test_reading_queue.py and three siblings           182 passed
the last 15 test files, the densest error block          362 passed, 3 skipped
tests/{feed_health,arxiv_window,loop_close,distill_practices,panel_merge}  197 passed
```

The last line is every test file that reads `sources.yaml`, which is the only
non-documentation file this run changed. **875 cases green** across the sampled
region and the affected surface, and the errors were `E` rather than `F`,
which is a fixture that could not be set up rather than an assertion that
disagreed. The suites here stand up real Postgres clusters in `/tmp`, and
`initdb` needs disk.

**Why this is a repeat.** It is the fourth shape of a class this register
already holds. `INC-2026-11-09-two-tests-failed-under-load-and-a-single-suite-run-would-have-been-read-as-a-red-caused-by-this-diff`
is the ExO seat's instance from earlier today, where the suite's wall time
varied 2.4x on one box and the two tests that flipped were the two that clone.
The ledger's `2026-11-09-urgent-the-shared-host-is-at-99-percent-and-pytest-temp-dirs-are-556mb`
is the host half.

**The shape none of them record, which is why this entry exists.** In every
prior instance the competing load was another seat. Here it was the same run.
Twelve seats share one host and one `/tmp`, so a charter that tells one run to
hold a 2400-second suite open and also to install a Node dependency tree has
told it to race itself, and nothing in the charter says to order the two. The
earlier instances are read as a reason to distrust a single suite run. This one
is a reason to serialize two duties inside one charter, which is cheaper and
entirely within the seat's control.

**What this run did.** Reported `INCOMPLETE` rather than a verdict, which is
what the sentinel exists for and the reason this entry is an observation
instead of a false finding. Removed `site/node_modules` after the build to
return 700 MiB. Verified the affected surface separately and said so in the
pull request with the counts rather than the adjective.

**What remains.** A line in this seat's charter putting the build and the suite
in sequence rather than together, or better, a note that the site build is
cheap and short and the suite is neither, so the build goes first and finishes
before the suite starts. That is a charter edit and this seat does not make
them, so it is filed at
`docs/ideas/inbox/2026-11-09-one-charter-tells-one-run-to-hold-a-long-suite-open-and-also-to-install-a-node-tree.md`.
