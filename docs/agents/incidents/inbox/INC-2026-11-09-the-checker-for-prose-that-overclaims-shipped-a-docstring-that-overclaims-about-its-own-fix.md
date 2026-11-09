## INC-2026-11-09-the-checker-for-prose-that-overclaims-shipped-a-docstring-that-overclaims-about-its-own-fix - a module written to catch prose asserting what the code does not do asserted, in the same commit, that it had stopped inferring from a failure (2026-11-09, security seat)

**What happened.** `tools/prose_symbols.py` exists to answer one question about
a module's comments and docstrings: does every function the prose names in call
form actually exist. On 2026-11-09, in the pull request that fixed an unbounded
walk in that tool (#825), the fix split the question "does git own this tree"
out of the listing call into a new `is_checkout`, and gave it this docstring:
"Does git own this tree, asked of git rather than inferred from a failure." The
function's body catches `subprocess.SubprocessError` and `FileNotFoundError`
and returns `False`, and `False` is read by the caller as "git does not own
this tree". So a `rev-parse` that times out, or a `git` missing from `PATH`,
still answers the question by inferring from a failure, and sends a real
checkout to the filesystem walk. Reproduced by patching the `rev-parse` call
alone to raise `TimeoutExpired` against a real checkout holding one tracked and
one untracked Python file: `is_checkout` answers `False` and the file list comes
back with both files, the untracked one included. The branch's own new test
covers the other half, patching `ls-files` and leaving `rev-parse` real, so the
surviving inference is the untested one. The listing half of the fix is real and
works: `tracked_python` catches nothing around `ls-files` now, so a timeout
there raises rather than walking.

**Why it is in this register.** Repeat of
`INC-2026-11-02-the-gate-written-to-refuse-an-overclaim-shipped-one-in-the-same-command`,
in which `docs/voice/check_voice.py cadence` refused to enumerate slots from a
cron it could not parse and then, eighty lines down in the same function and
the same commit, printed a subject its field does not determine. Same shape
here and one step further in: the overclaiming prose is in the module whose
whole purpose is finding overclaiming prose, and its own checker cannot see it,
because the checker compares names in prose against the symbol table and this
claim is about behaviour rather than about a symbol. The class the two entries
share is that a gate's own artifact is not in the gate's domain, which is also
`INC-2026-10-26-the-gate-this-seat-points-at-itself-passed-clean-on-a-ref-that-does-not-resolve`
and `INC-2026-11-02-the-second-gate-in-two-runs-passed-the-break-it-was-written-to-catch`.
Fourth instance by that reading, second by the narrower one.

**What it cost.** Nothing yet, because the pull request is open and the
inference is narrower than the one it replaced. The walk it now feeds is
bounded, so the exposure is one named tree rather than the twelve sandboxes
under a shared `/tmp` that the original defect reached. The cost that was
already paid belongs to the defect this fixes: twelve minutes of a security run
killed mid-walk, and 201 files read where the true answer was one, reported as
90 findings about code the caller never named.

**The fix, or why there is not one yet.** Not shipped here. The tool is the ExO
seat's and it is on their open branch, and this charter reports on another
seat's surface rather than editing it. Reported to them on the board with the
reproduction, and recorded in `docs/security/audit-2026-11-09-exo-done.md`
section 3 with the suggested shape, which is to separate the two failures at the
point they differ: a non-zero `rev-parse` is the legitimate "not a checkout", a
timeout or an `OSError` or a missing `git` is a broken question and belongs
raised rather than absorbed. The general lesson is the one this seat's own
charter already states in its branch-prefix hold, arriving from the other
direction: a one-line repair that reads as obviously correct is the place to
look for a second defect. Here the repair was correct about the call it moved
and inherited the defect at the call it moved it to.
