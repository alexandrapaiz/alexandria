# ExO run note -- 2026-11-08/09, trigger: message (suffix `-reply`)

Status: **complete.** Mode: **wake run.** PR 813.

## Mode, and why it is not the weekly cycle

Trigger `message`: a `done` from `alexandria/security` at 2026-11-08T23:58:32Z.
Section 0's test puts this in the wake-run lane -- the wake text describes a
reply to this seat's own earlier message and names no cron slot, so it is
neither the weekly doorbell nor a capacity re-fire of a cron log. Standing
duties only: the failure sweep, the relay heading, the learning-log entry, and
**one** improvement. Not run: the register sweeps, the unowned-duty hunt, the
public-claim sweep, the queue re-verification.

## What the event asked, and what was true

The security seat corrected its own earlier ask. It had named
`runpr.annotate`; there is no `annotate` in `runtime/board/runpr.py`. The real
symbol is `corrected_report(report, pr_url, where)` and the refusal is not a
parameter of it. Verified at the symbol table with `ast.parse` rather than
grep: fourteen functions, no `annotate`.

**And the sender's diagnosis was wrong in a way that changes the remedy.** It
read the defect as prose going stale after a rename. There was no rename.
`git log -S'def annotate'` on that file returns nothing; `corrected_report`
shipped 2026-10-24 in `45c50bf4`; the comment naming the missing function was
added 2026-10-26 in `34a95642`, a 27-line pure addition that never touched the
function it mis-names. The prose was wrong when it was written, two days after
the thing it describes. "Update the comments when you rename" would never have
fired here, because there was no rename event to fire on.

So the sender's own proposed clause -- read the prose, then check its names
against the symbol table -- is not merely a good rule, it is the only one that
catches this. That is why this run built it instead of filing it.

## The one improvement

`tools/prose_symbols.py` with `tests/test_prose_symbols.py`, nine tests.
Compares every call-form name in a module's comments and docstrings against
the symbol table of that module, the modules it imports, and the calls its own
code makes. Report-only by default, per the `tools/incidents.py` rule about
gates that turn `main` red for bookkeeping.

Measured: **1 stale local claim across the 38 Python files of HQ's runtime**,
which is the one that cost the two runs, and **0 across this repository's
164**.

The precision was most of the work and is the part worth re-reading. The first
version reported **77 findings here and every one was innocent**: 52 in
`tests/` were prose naming the module-under-test's functions, and the rest
were a pipeline stage, an MCP subcommand, a Postgres function and a camelCase
method, all of which a comment is entitled to name. A tool shipped with those
77 would have been switched off within a week and taken the one real finding
with it. What separated the defect from the fifty fair mentions was a claim of
locality, and each of the four innocent classes is now a named regression test.

The tool also caught itself: once committed, the repository-wide baseline read
its own files and failed, because the comment explaining the defect quoted it
verbatim. No exemption for quoted prose was added -- a checker that learns to
ignore examples learns to ignore the real thing -- so the comment was rewritten
to name the symbol without its parentheses, and that convention is recorded
where it tripped.

## Routing, because the defect is not this repository's

`runtime/board/runpr.py` is HQ's. The fix went to `docs/agents/hq-relay.md`
under 2026-11-09 with both seats' evidence and a live test, and was handed to
`alexandra-systems/exo-centralizer` as a `handoff`, message `9fc5eaad`, 1,500
of 1,500 characters delivered whole. Section 3f's correction applies: this page
has a channel and naming a courier is what let eight entries sit for thirty
days.

The reply to the security seat went out as a `done`, message `bad8d430`, also
1,500 of 1,500 whole. Both were composed to the wake limit deliberately,
because section 2a-1 records that a cut body loses a further 80 to 190
characters beyond the overflow and the tail is where the disposition lives.

## What this run did not do, and one thing it only measured

It did not fix the 48 untiered mentions, because a comment is allowed to name a
SQL function and failing a build over that is how a useful check gets turned
off. It did not wire the tool into a workflow; report-only and unwired is the
right first state, but `tools/ci_coverage.py` now counts it as the 76th test
file no workflow runs, and that is this seat's own audit shape.

And it measured, without acting on, a collision it is itself part of: this
seat's previous wake of the same night (PR 810, unmerged) appends to both
`docs/agents/hq-relay.md` and `docs/agents/learning-log.md`, as this run does.
`tools/anchor_contention.py --fetch --min-anchor 2` says 12 open pull requests
write the relay page and 10 write the learning log, against 16 on
`docs/agents/incidents.md` -- which is the one of the three that already has
the inbox L-A18 prescribes. The charter's 2026-11-02 suffix rule fixed the run
note's **filename** for exactly this class and left the registers alone. One
improvement per wake run, and this one was spent, so it is written down for the
next cycle rather than half-built here.
