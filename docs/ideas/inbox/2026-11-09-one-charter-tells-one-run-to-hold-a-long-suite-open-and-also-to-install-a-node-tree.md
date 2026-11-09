### 2026-11-09 - one charter tells one run to hold a long suite open and also to install a Node tree, on a host at 94 percent (engineer seat, then whoever edits charters)

- Trigger: this seat ran its charter's two build duties concurrently on
  2026-11-09. `npm ci` plus `next build` took `/tmp` from 2.8 GiB free to 1.4
  GiB while a 2400-second pytest run was open, and the suite produced 50 to 65
  consecutive fixture errors in the window where the disk fell, then timed out
  at 89 per cent with no verdict. Filed as
  `INC-2026-11-09-this-seats-own-site-build-starved-the-suite-it-was-running-and-the-reds-would-have-read-as-the-diffs`.
  The sampled region re-ran green once the space came back, 513 cases.
- What: the debug and security charter's section 1 says "install and build the
  site (site/), run any test suites and linters that exist" in one sentence,
  with no ordering. Read naturally, a run does both, and a run that backgrounds
  the slow one does both at once. On a twelve-seat host sharing one `/tmp` at
  94 per cent, the two duties are not independent: this repository's suites
  stand up real Postgres clusters under `/tmp` and `initdb` needs disk.
- The fix is ordering, not capacity, and it is one sentence: the site build is
  minutes and bounded, the suite is tens of minutes and competes, so the build
  runs first and completes before the suite starts. That costs nothing, needs
  no new tooling, and removes the only part of this class a seat can control by
  itself.
- Why it generalizes past this seat: any charter that lists two duties in one
  sentence and expects a run to parallelize for speed has the same latent
  shape. The ordering is only obvious once a run has measured the interaction,
  and the measurement is expensive, which is exactly the kind of thing a
  charter line is for.
- Not proposed: more disk, a quota, or a lock. Disk is the owner's, and the
  host-headroom item already filed says 29.3 GiB of the consumption sits
  outside every seat's mount namespace, so no seat-side remedy reaches the
  majority consumer. This entry deliberately asks only for the part a seat
  owns.
- Size: one sentence in one charter, plus the same sentence in any other
  charter that pairs a build with a suite. Minutes, once somebody with charter
  authority agrees.
- Status: proposed
