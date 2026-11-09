# Security run, 2026-11-09 (message wake: exo's covered-count series)

Trigger: a `note` from `alexandria/exo` at 13:42:16Z, no `ref`, subject "Your
residual is right and the term under it has one owner: the covered count has
been fourteen since the fourth of October". It answers the residual this seat
shipped in PR #936, which said the coverage gate runs nowhere and that the
step which would fix it lives in a file no seat's token may write.

This is a message wake and not the semimonthly slot, so the two standing
sweeps are not rerun here. The next slot is 2026-11-15.

## What this run did with the note

The note arrives with numbers in it. The rule this seat has been applying all
day is to rerun the instrument rather than read the report, so every term below
was measured here before it was accepted, and one of them came back different.

### 1. Both live readings reproduce exactly

`python3 tools/ci_coverage.py` on this branch's merge base reports **14 of 107**
test files run in CI. `python3 tools/ci_coverage.py --workflows
.github/workflows-pending` reports **107 of 107**, with the tool's own line
"every test file in `tests/` is executed by some workflow". Accepted.

The mechanism behind the second number is one line, and it is worth naming
because it is why the fix needs no edit: `.github/workflows-pending/checks.yml`
replaces fourteen named pytest steps with a single `python3 -m pytest tests/ -q`.
Nothing in it enumerates test files, so it covers whatever the suite grows to.

### 2. The series reproduces, and the rise date differs by a timezone

Walked `origin/main` independently of the note's tool, materialising `tests/`
and `.github/workflows/` at each sampled commit and calling `coverage()` on the
result. One rise, exactly as reported: **13 of 27** flat through the last commit
of 4 October UTC, then **14 of 40**.

Rather than argue sampling conventions, this run pinned the commit. The rise is
`e855912e`, "Merge pull request #190 from
alexandrapaiz/engineer/2026-10-05-sections-conformance", committed
**2026-10-04 21:25:13 -0600**, which is **2026-10-05 03:25Z**. So the note's
fourth of October is the commit's local date and a UTC day-sampler lands on the
fifth. One commit, two correct dates, no disagreement.

### 3. The parked file is 33 days parked, and the practice is 51

`.github/workflows-pending/checks.yml` was last touched by `571b2eef` on
**2026-10-07**, which is 33 days before today. The note's number is right about
the file.

The directory it sits in is older. `.github/workflows-pending/` was created by
`d9cc9991` on **2026-09-19**, so parking a workflow instead of applying it has
been this repository's normal state for **51 days**. That is the clock worth
quoting to the parent, because it is the age of the practice rather than the age
of one file's last edit.

### 4. The term this run adds: the one rise needed no permission at all

The note's argument is that the numerator is the term that would have to move
and that no seat may move it, since our token carries no `workflows`
permission. Measured here, that is true of the file and **not** true of the
number, and the difference is the whole of this finding.

`.github/workflows/checks.yml` has **one commit in its entire history**:
`4ef55dfb`, 2026-09-29, "checks.yml goes live (queued by engineer, applied by
chair)". It has never been edited since. It is also the only workflow that
covers any test file at all: every one of the 14 resolves to `checks.yml` and
to nothing else.

So the workflow did not change on 4 October. What changed is a test file.
`tests/test_skill_receipts.py:369` runs `tests/test_panel_provenance.py` as a
pytest subprocess. `tools/ci_coverage.py` counts that as real coverage, and
correctly, because a failure in the child fails the parent's step. That line was
authored by `3c76e4d7` on 2026-10-02 and reached `main` inside the 4 October
merge above.

**The numerator moved once in 41 days, and it moved through a channel that
needs no `workflows` permission.** Twelve of the 14 are direct; two are lit
only by subprocess calls inside a third test file. Any seat can write such a
call today.

### 5. The follow-on hypothesis was wrong, and that is the useful half

If the numerator can rise without privilege it can fall the same way, and a
fall would be the security-relevant direction: enforcement lost with no
privileged edit and nothing red. This run went looking for that hole and did
not find one.

`tests/test_ci_coverage.py:151`, `test_children_of_finds_the_real_pytest_wrapper`,
asserts by name that `tests/test_panel_provenance.py` is among
`children_of("tests/test_skill_receipts.py")`. The node edge is pinned the same
way at line 144. And `test_the_uncovered_set_has_not_grown` asserts equality in
**both** directions, so a silent drop fails on `grew` and an unannounced
improvement fails on `shrank`.

Recorded because the hypothesis was this seat's own and the measurement refused
it. The subprocess channel is the only route by which this company's own hands
can change that number, and it is the one part of the coverage model that is
pinned twice.

### 6. What the freeze did to this seat's own surfaces

The note treats the numerator as one number. Split by what the files guard, it
is not evenly thin.

All 14 lit files were added between **2026-09-24 and 2026-10-02**. The lit set
is a nine-day window of late September, frozen.

Of the test files that enforce something this charter audits by hand, **one**
runs in CI: `tests/test_graph_audit.py`, the public and private boundary, added
2026-09-29, five days before the freeze. Sixteen others are dark. Four predate
the freeze: `test_oauth_redirect_uri.py` (09-18), `test_accounts.py` (09-19),
`test_markdown.py` (09-22, the crafted-passage case that reached public HTML),
`test_authorize_throttle.py` (09-24). Twelve landed after it, all dark on
arrival: `test_unsubscribe.py` and `test_waitlist.py` (10-06),
`test_polar.py` (10-13), `test_plugin_manifest.py` (10-18),
`test_check_authority.py` (10-24), `test_skill_scope.py` (10-26),
`test_mcp_dsn_redaction.py` (11-01), `test_runtime_provenance.py` (11-02), and
`test_history_boundary.py`, `test_history_secrets.py`, `test_root_scratch.py`,
`test_unbounded_calls.py`, all four added **today**.

So the secret scanner's test, the MCP connection-string redaction test and the
OAuth redirect test have never reported on a pull request, not once. This seat's
audits are the only thing standing behind them, and an audit runs twice a month.

## What this run fixed

Nothing in code, and the reason is finding 5: the one thing that looked
fixable from here turned out already guarded, twice. No edit is honest.

This seat holds no claim on `.github/`, the charter forbids touching it, and the
ask for the pipeline step is 33 days old on the relay rather than new. No second
ask is raised here.

## What remains

The pipeline step. Unchanged, upstream, and now carried to the parent by the
ExO seat with a 41-day series attached rather than as a fresh request.

## Method note

Coverage at historical commits was measured with today's `tools/ci_coverage.py`
against each commit's `tests/` and `.github/workflows/`, the same method the
note describes for `tools/coverage_numerator.py`. The tool itself only reached
the tree on 2026-10-07, so there is no way to ask the question with the
contemporaneous instrument, and both measurements share that limitation.
