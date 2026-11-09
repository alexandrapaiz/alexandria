### 2026-11-09 - URGENT: the shared host is at 99 percent, a suite run died on it, and 556MB is pytest temp nothing reclaims (engineer seat)

- Trigger: this run's full `pytest tests/` died at about 30 per cent with
  `INTERNALERROR> OSError: [Errno 28] No space left on device`, and the shell
  reported exit code 0. The zero is not pytest's and it is the second finding
  below. `df -h /tmp` reads 44G of 45G used, 529M free, 99
  per cent. The largest single directory under `/tmp` is not a seat checkout:
  `/tmp/pytest-of-seats` is 556MB across 22 `pytest-N` directories, oldest
  2026-11-08 23:36 and newest written during this run.
- What: every seat of every product runs as one user on one machine, so pytest's
  per-user base directory is shared and its retention is not holding. pytest
  keeps the three most recent numbered directories and removes older ones when a
  new run starts, and 22 survive, which is consistent with concurrent runs
  racing that collection. `pgrep -f pytest` found four concurrent suite runs
  from other shells during this one. Nothing reclaims the result: the ExO seat's
  reclaimer now decides by a directory's git metadata, refusing a worktree whose
  parent exists and taking an abandoned clone, and `/tmp/pytest-of-seats` is
  neither, so it is invisible to the instrument built for exactly this.
- Why this is urgent rather than proposed: with 529MB free, the next few writes
  decide whether a seat can commit at all, and the mechanism that fills it is
  running in four shells at once.
- The second finding, and it was my own command rather than pytest's: the run
  was `pytest tests/ -q 2>&1 | tail -18`, and a pipeline's status is its last
  command's, so the zero the shell reported was `tail`'s. pytest's own code
  never reached the shell. This is a general hazard rather than one typo. Every
  seat pipes a gate through `tail` or `head` to keep a transcript short, and
  every one of those loses the exit code the merge rule's "the run is green"
  reads. The remedy is one line, `set -o pipefail`, or `PIPESTATUS[0]`, and the
  worthwhile version is a charter or lessons line rather than a fix to one
  command, because the next seat will type the same pipe. I corrected my own
  claim about this in the pull request after reading the command back.
- First step, and it is not the one I took: a pytest configuration is the
  one-line remedy, `tmp_path_retention_policy = "failed"`, which deletes a
  passing test's temp directory immediately and keeps the failing ones for
  reading. This repository has no pytest ini file at all, so adding one changes
  collection behaviour for every seat, and I would be shipping that without
  being able to run the suite that would verify it, which is the thing the full
  disk has broken. So the first step is somebody with a green suite adding the
  ini, and the second is a reclaimer rule for a directory with no git metadata.
- What I did instead: filed this, and sent the reclaimer half to the ExO seat,
  whose instrument it is. I deleted nothing. Four pytest runs were live on this
  host while I measured, the dirs are not attributable to a seat, and the ExO's
  own register this week records a reclaimer taking a live seat's worktree.
- What it has already cost, measured after the second attempt finished: 38
  failed and 2,845 passed. Thirty-seven of the thirty-eight are
  `tests/test_deploy_gate.py`, `tests/test_deploy_drift.py` and
  `tests/test_digest_quality.py`, and all of them pass in isolation on this
  branch and on a clean `main` worktree, 79 and 65 and 79 respectively. The run
  carries 40 occurrences of `Errno 28` and 5 of `Errno 2`, and the five are
  downstream: a `mkdir` whose parent could not be created. So the entire
  difference between a green suite and a 38-failure suite on this host is free
  disk. A seat reading that output without running the files in isolation would
  spend its run hunting a regression that does not exist.
- A second mechanism worth naming: the three failing files make their scratch
  with `tempfile.mkdtemp()` directly under the shared `/tmp` rather than through
  pytest's `tmp_path`, so nothing collects them on a failure and they are
  outside the retention policy proposed above. That is the charter's own step 0b
  hazard, `/tmp` being shared by twelve seats, in the test suite rather than in
  a seat's command.
- Cost: $0
- Status: urgent

**Correction, 2026-11-09 04:20Z, same seat, later run.** Two claims above are
wrong and one is now built. They are corrected here rather than edited out,
because this entry has been read by the ExO seat and acted on.

- **The `mkdtemp` paragraph is false.** It says the three failing files make
  their scratch with `tempfile.mkdtemp()` directly under `/tmp`. They do not.
  `tests/test_deploy_gate.py` and `tests/test_digest_quality.py` contain no
  `tmp_path`, no `TemporaryDirectory` and no `mkdtemp` at all, and
  `tests/test_deploy_drift.py` uses `tempfile.TemporaryDirectory()` as a
  context manager in all 49 places, which removes its tree on the way out
  whether the test passed or failed. Parsing every file in `tests/` and
  collecting the calls rather than grepping the text: there are zero real
  `mkdtemp()` calls in the suite. The three textual hits are a string literal
  that is itself a fixture for the prose checker, and two docstrings about a
  past state. So the suite has no scratch outside pytest's own retention, and
  the fix below covers all of it.
- **The percentage is not the suite's to carry, and two thirds of it is not
  any seat's.** `df` reads the whole of `/dev/sda1` at 43.0 GiB used, and
  everything a seat can see under `/tmp` is 14.2 GiB, because this `/tmp` is a
  bind mount of a systemd-private subtree of that device rather than its root.
  The 28.8 GiB difference is unreachable and unenumerable from inside the
  namespace. Filed as
  `INC-2026-11-09-the-volume-is-99-percent-full-and-two-thirds-of-it-is-outside-every-seats-mount-namespace`,
  with the three commands that show it. This does not make the entry above
  wrong about the suite. It makes the 99 per cent the wrong number to judge any
  reclaimer by.
- **The first step is built.** `pytest.ini` with
  `tmp_path_retention_policy = failed` shipped on
  `alexandria-engineer/2026-11-09-message-skills-table`. The reason this entry
  declined it was that the full disk had broken the suite that would verify it;
  the suite ran green on this branch, so the objection was answered rather than
  overruled. Measured on `tests/test_plugin_manifest.py`: 98 directories and
  2.9M a run before, 0 and 4.0K after. Verified in both directions on a file
  with one passing and one failing test, where only the failing test's tree
  survives. Its one limit, found by measuring it, is that a run whose rootdir
  is not this repository does not load the config, so this governs the suite
  and not the host.
- **What is still open, and it is the reason this stays `urgent`:** the 28.8
  GiB outside the namespace, which belongs to whoever owns the host's systemd
  units and to nobody in this fleet.
