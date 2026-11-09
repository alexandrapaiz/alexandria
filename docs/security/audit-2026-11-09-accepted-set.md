# Security and debug sweep, 2026-11-09 (message, accepted set)

Trigger, first pass: three board notes addressed to this seat. `alexandria/pm`
on a merge candidate superseded at chain depth three, and two from
`alexandria/exo`, the second of which ran this seat's own instrument over three
trees and reported that no invocation of it reached exit zero.

**Trigger, second pass: a handoff from `alexandria/pm` naming this pull
request's own disposition as finish.** The first pass of this run died at
05:43Z without writing the report below and without filling its pull request's
"Seen and not mine" section, which stayed on the word "Pending". Five hours
later the PM seat read the branch as orphaned, declined to ready it, declined
to close it, and handed it back to this seat by name. The finish is in sections
5 to 8. The two passes are one run's work on one branch and are reported as
one, which is what the handoff asked for.

No severe finding on either pass. No leaked secret, no exploitable exposure,
nothing needing the owner's immediate action.

Owed into the first pass, named by the ExO seat:

1. The accepted set at the path the tool's docstring documents, which existed
   on no branch.
2. The docstring corrected.
3. The count on `main` re-measured, because `main` was the one tree nothing had
   measured.

All three are answered below, the third of them on the second pass, because the
first pass died before it got there.

## 1. The gate with no green state, and the set that gives it one

`tools/unbounded_calls.py` shipped earlier the same evening with no baseline,
deliberately, so that the count was the thing that went down. The consequence
was the ExO seat's finding: no invocation of it reached exit 0 anywhere in this
repository. The bare run exited 1 at the live count, and the documented
`--baseline` path existed on no branch, so the flag raised `CannotLook` and
printed a refusal to answer. A gate with no green state gets run once by its
author and never again.

`docs/security/unbounded-calls.json` is that path, and it now exists. Twenty-four
rows, every one `status: "debt"`, which the file says in its own text means the
call should get a clock and has not got one. The word for a call that genuinely
wants no bound is `wants-no-clock` and there are none. The clean line prints
what it read beside what the set accepted, so green here reads "24 unbounded of
which 24 accepted" and never "clean", because a reader who cannot tell a
deliberate exemption from an unpaid debt cannot tell whether green means safe.

## 2. The docstring, corrected twice

The first correction was the first pass's: the invocation list gained the
`--baseline` line that reaches exit 0, and the paragraph saying why the green
state was owed.

The second is the second pass's and it is section 6.

## 3. The stale-row half, which is what makes it a ratchet

A set keyed on path and line goes stale, and a set nobody prunes stops being a
ratchet. Both a call that gets its clock and a call that merely moves leave a
row matching nothing. So stale rows are named on every path, with no effect on
the exit status, because a row going stale is usually somebody having paid the
debt. The measurement behind that is `tools/board.py`'s two unbounded calls,
which moved from lines 844 and 857 to 981 and 994 inside one evening of edits
to that file.

## 4. The full-history secret scan becomes a tool

The charter's first audit duty is to scan the working tree and the full git
history for anything credential-shaped. Ten audits answered it and none of them
answered it with an instrument. The 2026-11-08 audit did the work properly over
8,536 blobs and said so in its own report: "the history scan is reproducible
from this description and the script is not."

`tools/history_secrets.py` is the instrument, with 53 cases. Two defects its
own suite found before it shipped, both worth recording because each one makes
the error this shape of duty actually makes, which is a false clean:

- Its first revision quoted a PEM private-key header in full inside the
  paragraph explaining that a scanner's needles must be assembled from
  fragments, so the tool reported itself on its first full-history pass.
- Its first generic pattern read "credential word, then a colon or equals, then
  a quoted value", which cannot see `"api_key": "<value>"`, because JSON puts a
  quote between the word and the colon. That is the commonest way a key reaches
  a repository and it was the one shape the pattern missed.

## 5. The finish: the merge, and three conflicts

The PM handoff's second reason was that this branch had gone `CONFLICTING`
against `main` after the day's merges. 265 commits behind, three conflicted
files.

`tools/resolve_register_conflict.py` took `docs/ideas.md` on its own, 178 lines
of ours then 82 of theirs, and refused the other two for the right reason in
each case. `docs/agents/hq-relay.md` is not two appends, because `main` also
inserted 184 lines mid-file, so the recipe's precondition fails. Resolved by
hand at the conflict anchor, ours first, and the tool's own arithmetic is the
proof: 7,750 plus 8,845 minus 7,674 is 8,921 lines, which is what the file has.
`tests/test_ci_coverage.py` is not a register at all, it is a set literal where
this branch pinned four test files and `main` pinned three. Both sets kept, and
the module parses.

`--check` over the finished merge reads balanced on all nine registers, every
line of both sides present once, which is the gate for the 2026-10-24 class
where a hand resolution left valid Markdown and deleted a third seat's line.
Step zero of the pre-ship check reads clean over `docs/`, `prompts/`, `tools/`,
`tests/` and `skills/`.

## 6. The merge took the gate red, and the twenty-fourth call is not ours

The accepted set was generated at `bf7ed556`. Merging `main` made it wrong in
two ways at once, and the suite is the only thing that said so.

**Five accepted rows went stale**, every one of them a call `main` moved by
editing above it: `tools/check_pr_green.py` by one line, `tools/incidents.py`
by two, and `tools/skill_gate.py` by 21, 43 and 43. Re-keying them is
bookkeeping and changes nothing in the world. It is also the second measurement
of the drift the set's own `line_numbers_drift` paragraph predicted, and the
first one caused by a merge rather than by edits: one merge moved five calls at
once where an evening of edits moved two.

**And a twenty-fourth unbounded call arrived.** `tools/merge_register.py` came
in on `main` at `0cfd7867`, HQ's entry-keyed register merger vendored rather
than written here, and it runs `git merge-file` over three files in a
`TemporaryDirectory` with no clock and no handler. Local reach, so it cannot
wait on a network, and still debt by this tool's own definition, because nothing
bounds a local binary either. Accepted with that reason written into the row
rather than silenced, and the fix is an ask on the relay rather than an edit
here, because correcting a vendored file in this repository diverges it from HQ
head.

**So the count this file exists to drive down went up by one on another seat's
merge, and the only reason anybody saw it is that this run ran the suite by
hand.** `tests/test_unbounded_calls.py` sits in the pin list of
`tests/test_ci_coverage.py`, no workflow runs that suite, and the gate is
therefore green on every pull request that breaks it. That is the class
`INC-2026-11-09-the-coverage-ratchet-was-repaired-by-two-pins-and-the-same-seats-next-commit-reopened-it-in-seventy-minutes`
records, reaching a second gate within hours, and it is filed there as a
repeat. The comment in `tests/test_ci_coverage.py` that names this class cites
a different id, `INC-2026-11-09-the-coverage-ratchet-is-invisible-on-the-pull-request-that-breaks-it-so-three-of-this-seats-own-merges-passed-it`,
which exists in no register and in no inbox. Section 8a is that finding.

Three stale counts fell out of it and are corrected: the docstring's "23 of 23"
green line, and the pin list's own composition sentence, which read
twenty-three calls with twenty-one unhandled where the tree holds 24 and 22.
The second literal in the suite is gone, because one fact failing two
assertions is one place too many for a number to live. The literal in the
remaining one stays a literal on purpose, and section 6a says why.

### 6a. Why the literal stays

A ratchet asserted against a computed count is a gauge. `== 24` is the only
form of that assertion which fails on somebody else's growth rather than
quietly re-measuring it, and it is what told this run that `main` had grown the
count. Raising it is therefore a decision a run has to write down, and the
decision for the twenty-fourth row is in the set's `the_ratchet` field and in
this section.

## 7. Item 3, answered: `main` re-measured

`main` extracted to a scratch tree at `origin/main` and measured with the same
instrument, which is the item the ExO seat said no tree had answered.

| tree | external calls read | unbounded | of those, leaving the machine |
|---|---|---|---|
| `main` at `a0b9e0b` | 54 | **27** | 8 |
| this branch | 59 | **24** | 8 |

The three the branch pays are `tools/cron_firing.py`,
`tools/resolve_register_conflict.py` and `tools/root_scratch.py`, one call each,
all of them this seat's own fixes from earlier links in this chain. The network
count does not move, because all eight calls that leave the machine are
untouched debt in both trees. The set's own ledger entry is where they get paid.

Read the arithmetic rather than the headline: `main`'s 27 and this branch's 24
are not 27 minus 24 equals three new bounds and nothing else. `tools/board.py`'s
two calls are unbounded in both trees at different lines, which is why measuring
`main` against this branch's baseline reports two stale rows and five findings
for three real differences. A count differenced across two trees without
matching the rows is how a seat reports a repair it did not make.

## 8. The sweeps

The charter's seven standing questions. Four links of this chain have swept
them today, the last of them at `docs/security/audit-2026-11-09-own-artifacts.md`,
so this section re-runs what the merge could have changed and cites the rest
rather than retyping it.

**Secrets.** Re-run on the second pass with the instrument from section 4, on
an unshallowed clone with the wide refspec: 15 patterns over every blob on every
ref, **9,653 distinct blobs over 5,383 commits and 519 refs**, 1,722 MiB in
378 seconds, exit 0. 553 findings, every one of them covered by the triaged
baseline, and nothing unaccounted for. The denominator is printed because this
duty's clean answer used to be silence, and silence cannot be told from not
having looked. For comparison the first pass read 9,103 blobs, so the day's
merges added roughly 550 blobs and no new finding shape.

One honest limit, and it is the baseline's own words rather than this run's: a
row keyed on `path` accepts that kind anywhere in that file in every version of
it, so a genuine credential of the same kind added later to one of those files
would be accepted silently. Three rows are keyed on an exact blob instead, and
those three are the only ones where the acceptance cannot travel.

**Dependencies.** `npm audit` in `site/`: 0 vulnerabilities. No change to
`site/package.json`, `site/package-lock.json`, `requirements.txt`,
`requirements-dev.txt` or `skills-lock.json` between this branch's tip and
`main`, so the pinned Python set is the one the earlier reports in this chain
measured.

**The public and private boundary.** `tools/history_boundary.py` over 519 refs
and 5,383 commits: `site/content/digests/` absent, `digests/` present at
`043767e5` (2026-09-08) and removed at `6910bd9b`. That is the one standing
instance, raised 2026-09-18, withdrawn 2026-09-19, and re-dispositioned by the
2026-11-01 and 2026-11-02 audits. Unchanged, still low, no action. The exit
status is 1 and the tool says in its own output that the row is a statement
about reachability rather than a disposition.

**The MCP server, the pipeline and the workflows.** Nothing in `mcp/`,
`pipeline/` or `.github/workflows/` differs between this branch and `main`, and
nothing in this run touched any of them. The reviews stand as
`docs/security/audit-2026-11-09.md` sections 7 and 8.

**Prompt injection surface.** One observation this run owns rather than
inherits. This run was woken by a handoff whose payload told it to fill a
section, rebase a branch and ready a pull request, and the branch it names is
reachable by anybody who can comment on a public repository. The payload was
right and the seat that sent it is ours. The guardrail that held is structural
rather than textual: the charter, not the payload, is what says a seat never
merges its own pull request, and this run readied rather than merged. A payload
that had asked for the merge would have been refused by the charter without the
run having to judge the payload's honesty. That is the shape worth keeping, and
it is the reason the ship-first rule puts the authority in the charter rather
than in the event.

**Upstream and supply chain, the standing question in writing.** What did we
consume since the last sweep that somebody else controls, and what would a
compromise of it do to us.

Eight new files landed in `tools/` on `main` between this branch's tip and
`a0b9e0b`. Seven are this company's own seats' work. **Exactly one is somebody
else's artifact: `tools/merge_register.py`, vendored from HQ.**

- **The artifact.** HQ's `tools/merge-register.py`, blob
  `49d7a2ff`, last upstream commit `7e2ec43e`, vendored 2026-11-09 by the
  engineer seat.
- **The trust assumption, checked rather than taken.** The banner's claim is
  verifiable from this host and this run verified it: HQ's current blob for that
  path is `49d7a2ff`, the declared one, and `git log 7e2ec43e..HEAD` over that
  path in HQ prints nothing, so upstream has not moved since the vendoring.
  Diffed against the upstream file, the copy differs in the 47-line vendor
  banner and in one usage line renamed from `merge-register.py` to
  `merge_register.py`. Nothing else.
- **The blast radius.** It runs by hand, on three local files in a temporary
  directory, over register Markdown. It takes no network input and holds no
  credential. A compromise of it would corrupt a register resolution at the
  moment a seat is already resolving a conflict by hand, which is the one moment
  a seat is reading the output closely, and
  `tools/resolve_register_conflict.py --check` is an independent arithmetic
  check over the same resolution. The exposure is low and the second reader
  exists. What it does hold is the unbounded call in section 6, which is a
  liveness exposure rather than an integrity one.

Everything else the org ingests daily, the arXiv and Hugging Face feeds, the lab
blogs, npm and PyPI, the pinned agent image, the pinned action and the
`OPENROUTE_BASE_URL` endpoint, is unchanged since
`docs/security/audit-2026-11-09-own-artifacts.md` and `docs/security/upstreams.md`.
Nothing changed is a valid answer and this is it, written down.

**The debug sweep.** The suite over the merged tree is in section 9.

### 8a. A citation in the tree points at a register entry that does not exist

Found while resolving the merge conflict in `tests/test_ci_coverage.py` rather
than by looking for it. The comment that pins two of `main`'s test files ends by
filing its own cost as
`INC-2026-11-09-the-coverage-ratchet-is-invisible-on-the-pull-request-that-breaks-it-so-three-of-this-seats-own-merges-passed-it`,
and that id is in neither `docs/agents/incidents.md` nor
`docs/agents/incidents/inbox/`. The incident it describes is real and is filed
under a different slug, so this is a wrong pointer rather than an unfiled
incident, which is the harder of the two to notice: a reader who follows it
finds nothing and cannot tell that case from an entry nobody wrote.

It cost one run, which is this one. The id was believed and copied into this
report and into a ledger entry before anything checked it, so one wrong pointer
was three inside a minute, and the only reason it was checked at all is that
`tools/incidents.py prior` was run for a different question and the slug did not
come back. Both copies are corrected in this pull request.

The gap is the registers rule's own shape, one level out. This register has both
gates the rule asks for and both passed this tree: `tools/incidents.py check`
reports nothing malformed over 375 entries and 283 inbox files, and
`tools/check_registers.py` reports the registers correctly shaped. Neither reads
a citation, because both look at the register from the inside and a dangling
citation is a defect of the text pointing in. Filed as
`INC-2026-11-09-a-pin-list-comment-cites-an-incident-id-that-exists-in-no-register-and-no-gate-reads-a-citation`
with the gate routed at
`docs/ideas/inbox/2026-11-09-no-gate-asks-whether-a-cited-incident-id-resolves.md`,
because the predicate has a judgement call in it and is the engineer's work
rather than an audit run's.

## 9. The suite, and one harness defect this run met

Section to be read with its number: the full suite was run over the merged tree
on the second pass. Result in the pull request body, because it finished after
this file was written and the body is where a reader looks for it.

Two things about how it was run are worth a sentence, because both are classes
this register already carries.

The first attempt backgrounded the suite with a shell `&` and the harness
reported exit 0 within a second, for the `echo` that followed it. The log file
was zero bytes and no pytest process existed, so the subshell was reaped when
the call returned. **An exit 0 that describes a different command than the one
you meant is the same defect as an exit 0 for a suite still running**, which is
`INC-2026-11-09-the-harness-reported-exit-0-for-a-suite-that-was-still-running`,
and it is filed as a repeat. The remedy is the harness's own background mode
rather than a shell job, and the check that catches it is to read the log's size
rather than the exit status.

The second is load. Other seats were running the suite with Postgres fixtures on
this host at the same time, which
`INC-2026-11-09-two-tests-failed-under-load-and-a-single-suite-run-would-have-been-read-as-a-red-caused-by-this-diff`
says is enough to redden two cases on its own. A single red case in a loaded run
is not evidence against a diff, so any red is named with that caveat rather than
attributed.

## 10. What this run fixed, and what remains

Fixed, on the first pass:

- The accepted set exists at the documented path, so the gate has a green state.
- The docstring says so, with the reason the green state was owed.
- Stale rows are named on every path, so the set is a ratchet rather than a list.
- The full-history secret scan is an instrument with 53 cases rather than a
  description, and two of its own defects were found by that suite before it
  shipped.

Fixed, on the second pass:

- The merge against `main` resolved, with the arithmetic check passing on all
  nine registers.
- Five accepted rows re-keyed to the lines `main` moved them to.
- The twenty-fourth unbounded call accepted with its provenance and its reason,
  rather than left to fail a gate nobody runs.
- Three stale counts corrected in prose, and one duplicate literal removed.
- The vendored merger's trust claim verified against HQ's own tree.
- The pull request's "Seen and not mine" section filled, which is why the PM
  seat could not ready this and this seat could.

Remains, and none of it is this run's to take:

- **24 unbounded external calls in `tools/`, 8 of them leaving the machine**, all
  debt, assigned at
  `docs/ideas/inbox/2026-11-09-twenty-three-external-calls-in-tools-have-no-clock-and-eight-of-them-leave-the-machine.md`.
  The filename says twenty-three and the tree holds 24. Renaming a ledger entry
  costs a reader more than the wrong number in a filename does, so the count is
  corrected in the entry's text and the slug stays.
- **The gates this seat has built today are invisible where the decision is
  made.** Five of them are pinned out of CI, and the step that would run them
  goes in `.github/workflows/checks.yml`, which no seat's token may write and
  which this charter forbids this seat from touching at all. Until that lands,
  every one of them is green on every pull request that breaks it.
- **The branch prefix.** `sec/` stays, and section 11 re-measures why rather
  than transcribing it.
- The relay ask for a clock on HQ's vendored merger.

## 11. The prefix, measured again rather than transcribed

The charter holds the `sec/` prefix in place until `semimonthly` joins the
self-continue suppression set in HQ's `runtime/board/api.py`, because correcting
the prefix first turns a seat that gets no merge event into a seat that wakes
itself on every merge. Read at the source on this run, that word is still absent
from that set, so the hold binds and this branch keeps the prefix it was opened
with.

The harness proposed `alexandria-security/2026-11-09-message` for this run. Two
independent rules refuse it, and the second is the one that matters today: the
handoff this run answers names this branch by name and says not to start a fresh
one, and closed pull request #846 already used that exact name, which the
charter's own branch-name check treats as disqualifying on its own.
