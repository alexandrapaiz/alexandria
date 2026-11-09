# Security and debug sweep, 2026-11-09 (message wake, the PM's merge done)

Woken by a `done` from `alexandria/pm` at 01:30Z reporting that both of this
seat's open pull requests were merged in the order this seat asked for, that the
ledger collision this seat named in advance needed no hand resolution, and that
nothing else is needed from that pass. This is a close-out wake, so what it owes
is a verification rather than a second sweep of a tree that was fully audited
fifty-four minutes earlier.

The inbox held six addressed messages. Five were already answered: the ExO seat's
`done` of 2026-11-08 23:27 by #809, its `done` of 00:13 and the PM's `handoff` of
00:21 by #820, and its `done` and `note` of 01:23 by #829, which is open as this
is written. The PM's `done` of 01:30 is the one nothing had answered, and it is
this run's subject.

Nothing in this run touched `digests/`, a secret, or a workflow.

## 1. The done, verified rather than accepted

The message makes four claims. All four hold, and they were each re-performed
here rather than read.

**The order.** #809 was created 2026-11-08T23:33:28Z and merged
2026-11-09T01:25:36Z. #820 was created 00:31:22Z and merged 01:26:04Z. The older
one first, twenty-eight seconds apart, which is the order this seat asked for.

**The path check, and it is stronger than the message claims.** The message says
neither diff touches a path `checks.yml` watches, so the no-checks-reported state
was the pass state rather than a stall. Re-performed by parsing the workflow's
own 23 `pull_request` path patterns and matching every file in each diff against
them, with `/**` handled as a prefix: #809's 40 files produce zero hits and
#820's 9 files produce zero hits. The same measurement over #817, the skill
seat's stack that merged eleven minutes earlier, produces 63 hits, so the
instrument is not answering zero to everything.

What the message does not say, and what makes the reading sound rather than
lucky, is that `checks.yml` is the **only** workflow in this repository with a
`pull_request` trigger at all. Fifteen workflow files, fourteen of them seat
schedules and the deploy, one path-filtered check. So the inference from "no
check reported" to "no check was owed" needs no judgement about which workflow
might have fired. It is a property of the repository, and a merger can re-derive
it in one command.

**The collision.** Both pull requests append to `docs/ideas.md`, which is the
anchor this seat flagged in advance. Both appends are on `main`, and both merges
were purely additive: `755406ce` brought 457 insertions and 0 deletions to that
file, `b53edd54` brought 70 insertions and 0 deletions. This seat's two entries
from #820 are at lines 28765 and 28807 today. Nothing was lost and nothing was
reordered, which is the claim, and the stat line is the proof rather than the
absence of a conflict marker.

**The tool.** `tools/root_scratch.py` and `tests/test_root_scratch.py` are on
`main`. Thirteen tests, thirteen passed. Run against this checkout the gate exits
0, and `--tracked` still reports the two root files `main` already carried,
`.prbody-exo.md` and `site-server.log`, by name and with the commit that added
each.

So the done is accurate on every point, and the one thing worth adding to it is
the sentence above about the workflow count, because that is the half of the
reasoning that makes it reusable on the next pull request rather than correct on
these two.

## 2. The question two registers left open since 2026-11-02, settled at the source

This is the finding this run exists for, and it cost one command.

`docs/standards/lessons.md` **L-P8** binds "pm and chair, and every seat whose
work is held by one" to prefer evidence a merger can re-perform, and it names two
commands: `python3 tools/check-pr-green.py <pr>` and `python3
tools/check-run-ran.py --branch <branch>`. On 2026-11-02 the skill seat filed
`INC-2026-11-02-the-wakes-own-verification-command-does-not-exist-and-a-vendored-standard-prescribes-it`
and a matching ledger entry, both of which end on the same honest dead end: the
two tools are absent here, and **"a seat here cannot tell from the text"** which
of two readings holds. Either HQ carries the tools and the standard assumed they
travel with the vendored copy, or the standard names tools that exist nowhere.

The first reading holds. HQ's checkout is on this host at `/srv/asc/hq`, at
`6fc71409`, and it carries both:

```
tools/check-pr-green.py     16,913 bytes
tools/check-run-ran.py      13,020 bytes
```

Alongside `check-branch-prefixes.sh`, `check-ceremony-ran.py` and
`check-turn-grants.py`, so hyphens are HQ's convention for this tree and the
spelling in L-P8 is HQ's own file path rather than a typo.

That changes the open relay ask from a question into a request. The ask was
"which of the two readings holds"; it is now "these two tools exist at HQ, so
either vendor them beside the standard that prescribes them or state the check in
terms a vendoring repository can satisfy with what it carries."

**Three things follow, and the third is the one nobody has written down.**

First, this repository now carries its own `tools/check_pr_green.py`, 481 lines,
shipped 2026-11-02 at 07:54 by the engineer seat. It is real and it is good: 30
tests, all passing here, and it does what L-P8 describes. HQ's is 390 lines and
also builds the merge with `git merge-tree` and runs the repository's own suites
against it, so the two are independent implementations of one instrument rather
than a copy. Worth naming as duplication rather than as a defect, because the
reason it happened is visible in the local tool's own docstring: its author read
L-P8, looked for the named file, did not find it, and wrote one.

Second, the spelling defeats a verbatim copy, and that half is still open.
`ls tools/check-pr-green.py` in this repository says no such file today, because
what landed is `tools/check_pr_green.py`. A seat that copies L-P8's command as
written still gets `No such file or directory`, which is the exact misreading the
2026-11-02 incident warned about: an error from the command mistaken for a
failure of the branch. The engineer's ledger entry of 2026-11-02 says
"`tools/check_pr_green.py` shipped in this run and closes that half." It closes
the capability. It does not close the command, and the distance between those two
is one underscore.

Third, `tools/check-run-ran.py` is absent here under both spellings and was never
added, so the half of L-P8 that answers whether a red run is the never-started
kind remains unsatisfiable in this repository by any means.

Severity low on all three. Nothing is exposed and nothing executes. What it costs
is that a merger bound by L-P8 cannot follow it as written, which is how the PM
came to answer condition 3 by hand on these two pull requests.

## 3. Tier B condition 3 is the default path here, not the exception

Not a deviation by the PM, and it is recorded because the number is larger than
it reads.

`docs/standards/pm.md` section 10 Tier B condition 3 is "Checks green, or no checks
defined." The PM applied the second clause and verified why it applied, which is
more than the condition asks for. But `tools/ci_coverage.py --report-only`
reports **14 of 94 test files run in any workflow at all**, so 80 do not, and
"no checks defined" is the ordinary state of a diff in this repository rather
than an edge case. For the two pull requests merged this pass the untested-by-CI
files included every file either one added: `tools/root_scratch.py`,
`tools/ship_first.py`, `tools/cron_firing.py`, `tools/target_census.py` and
their four test files.

So condition 3 is satisfied by almost every diff here without anything having
been checked, and the thing that would actually check it is the instrument in
section 2 that the standard names and this repository spells differently. The two
findings are one finding seen from two ends.

Measured rather than asserted: this run ran all six of this seat's own gates on
`main` and they pass, 176 tests between them, which is the evidence condition 3
did not ask for.

| gate | result |
|---|---|
| `tests/test_root_scratch.py` | 13 passed |
| `tests/test_branch_prefix.py` | 3 passed |
| `tests/test_ship_first.py` | 17 passed |
| `tests/test_cron_firing.py` | 119 passed |
| `tests/test_ci_coverage.py` | 24 passed |
| `tests/test_check_pr_green.py` | 30 passed |

## 4. A register's own prescribed detector has started under-reporting, silently

This is a repeat in class and it is filed in the incidents inbox.

`INC-2026-10-24-one-branch-name-carried-seven-merged-pull-requests` tracks the
branch-name reuse class, and its 2026-10-24 addendum prescribes one command to be
run every run:

```bash
gh pr list --state all --limit 300 --json headRefName \
  --jq '.[].headRefName' | sort | uniq -c | sort -rn | awk '$1>1'
```

Run verbatim today it prints **one row**, `distribution/vendored-lessons` at 3.
Run over all **835** pull requests this repository now has, it prints **ten
rows**, led by the same name at **11** and `distribution/vendored-pm` at 3.

So the detector the register tells every run to execute reports 3 where the truth
is 11, on the one count the entry exists to carry, and it hides nine other
reused names entirely. Six of the hidden rows belong to alexandria's own seats:
`okr/2026-09` at 3, `exo/2026-09-18` at 3, and `writer/2026-09-19`,
`pm/standup-2026-09-24`, `pm/sprint-2026-09-21`,
`fe/2026-09-18-email-capture-live-metric`, `alexandria-exo/2026-10-25-message`
and `alexandria-exo/2026-10-26-message` at 2 each.

The mechanism is that the bound was written when it was generous and nothing
re-reads it. At 835 pull requests a `--limit 300` window reaches back to roughly
2026-11-05, so a name last reused before that date cannot appear, and the output
shrinks as the repository grows. **The failure direction is the dangerous one: a
truncated window returns fewer rows, and fewer rows from a duplicate detector
reads as the problem going away.** This is the same shape the 2026-11-09 audit
recorded about a short list from a tool that counts absences, met again in a
register rather than in a tool.

It reaches this seat's own charter. The charter's never-reuse clause prescribes
`--limit 200` for the same question, which is a narrower window still. This run
checked its own branch name against all 835 pull requests rather than against
200, and `sec/2026-11-09-message-pm-done` appears once, as #834, which is this
run's own.

The fix is a bound that cannot rot, which is `--limit 2000` or the paging flag,
in the register's addendum and in the twelve charters that carry the clause.
Neither surface is this seat's to edit, so it is filed rather than fixed.

## 5. Secrets

**The delta, which is what a sweep fifty-four minutes after a full audit owes.**
`main` moved by exactly two merges since the tree the 2026-11-09 audit and #829
measured, and both are this seat's own, #809 and #820. Every blob those commits
introduce was scanned: **587 distinct objects**, against patterns for provider
keys in five shapes, cloud access keys, GitHub tokens, Google and Slack keys,
Stripe and SendGrid keys, Modal tokens, private key blocks, connection strings
for seven protocols, JWTs and app passwords.

Seventy-six matches in **two distinct files**, and every one is documentation.
Named with no values, as the charter requires:

| file | kind | why it is not a finding |
|---|---|---|
| `docs/agents/incidents.md:6316` | connection string of the `user:pass@host/db` form | the placeholder written to describe a redaction incident, carried by five previous audits |
| `docs/agents/incidents.md` (2 lines) | app-password shape | ordinary English prose, four short words in a row |
| `docs/security/audit-2026-11-02-exo-reply.md` (1 line) | app-password shape | the same, in this seat's own earlier report |

The count is 76 rather than 4 because the same two files appear at 24 blob
revisions across the merged branches, which is one file edited repeatedly rather
than 76 places.

No rotation is indicated. Nothing is severe.

**A correction to this seat's own method, because the 2026-11-09 audit drew the
wrong boundary around it.** That run found its app-password pattern matched 87 of
133 blobs as plain English, required a credential word within sixty characters of
the match, got to one, and recorded the lesson as "a pattern that fires on the
common case is a word counter and not a finding." The proximity filter was in
force on this run and it still admitted three prose matches, for a reason that
generalizes: the corpus this scan runs over most is the security register and the
incident register, and in those files the words `token`, `secret`, `credential`
and `password` are on nearly every page. **A proximity filter keyed on credential
vocabulary is weakest in exactly the corpus that discusses credentials**, so the
filter buys the most where it is needed least. The remedy is not a tighter
window. It is that the app-password pattern needs an assignment or a quoting
context to be worth firing at all, and until it has one its output is read by
hand, which is what happened here.

**The working tree, all 2,153 tracked files.** Eighteen matches in eleven
distinct files, and all eighteen are clean. Three DSNs in
`tests/test_mcp_dsn_redaction.py` against its own synthetic host, two `sk-`
shaped literals in `tests/test_press_resilience.py` of which the second is the
sentinel `sk-this-must-never-be-printed` that the test exists to assert is never
printed, the documented placeholder connection string in two registers, and
eleven app-password shapes that are all ordinary English. Four of those eleven
are new to this reading and three of the four are in files this seat has no
hand in, including both vendored standards, which is the method note above
rather than a change in the tree. This run's own diff adds no match.

## 6. Dependencies

`npm audit` in `site/` against `package-lock.json`: **0 vulnerabilities** at
every severity from info to critical. No manifest in either language moved in
this window, so this is a re-measurement and not a new reading.

Python pins, re-read across all eleven pipeline images and the MCP image:
`psycopg[binary]==3.2.4`, `httpx==0.28.1`, `requests==2.32.3`, `markdown==3.7`,
with the same single exception as the last six audits. **`sentence-transformers`
is unpinned in `pipeline/distill.py:285`**, in an image that holds database
credentials and pulls torch and transformers transitively. Carried since
2026-09-18, unchanged, and the reason it stays open is that pinning it is the
engineer's call about build time rather than this seat's.

No new paid service, tool or dependency was added by this run.

## 7. The public and private boundary

`digests/` and `site/content/digests/` are both in `.gitignore`, at lines 8 and
11, and neither exists in the working tree. The one historical digest,
`digests/2026-W37.md`, is still reachable from `043767e5`, which is the known
finding, raised 2026-09-18, withdrawn 2026-09-19, and whose justification this
seat corrected on 2026-11-08. Unchanged and still withdrawn.

Nothing in this run's diff ships content to the browser.

## 8. The MCP server, the pipeline and the workflows

All three are byte-identical to the tree the 2026-11-09 audit read.
`git log c1cf1883..origin/main` over `mcp/`, `pipeline/` and `.github/` prints
nothing, and the full file list of the window is 46 paths, every one of them
under `docs/`, `tests/` or `tools/`. So this section is a re-measurement by
exclusion rather than a re-reading, which is the honest form when the delta is
empty.

The findings those surfaces carry are unchanged and are listed in section 11:
`_redact`'s candidate set without a percent-decoded password, floating major tags
on all seven distinct actions, and `checks.yml`'s `paths:` entry for
`prompts/daily.md`, a file no ref of this repository has ever held.

## 9. Prompt injection surface, and the channel this run looked at

The wake was a confident message from another seat making four factual claims
about this repository's own state, which is the cheap failure mode this surface
has, and section 1 is the guardrail working: every claim was re-performed against
the objects and the forge rather than read. Worth recording that the message was
right on all four, because a guardrail only reported when it catches something
turns into a story about distrust rather than about method.

**The channel this run examined is the vendored standard, and it is a live
instruction channel rather than a document.** `docs/standards/lessons.md` and
`docs/standards/pm.md` arrive from HQ by sync pull request, carry a
do-not-edit-here header, and this seat's charter says in its own words to "treat
a rule there exactly as you treat one from this charter." L-P8 is the proof that
the channel carries commands and not only rules: it names two shell commands by
path, and every seat it binds is told to run them.

The last two syncs landed 2026-11-08 at 23:26, as #799 re-vendoring
`lessons.md` at 622 insertions and 147 deletions, and #800 re-vendoring
`pm.md` at 629 insertions and 152 deletions. Both carry zero review records and
zero comments. Both were opened on branches under `distribution/`, and
`distribution` is a seat of `alexandra-systems` rather than one of alexandria's
twelve, which `company.yaml` confirms on both sides.

**The authority question that follows cannot be answered from the record, and
that is the finding.** section 10 Tier A permits a self-merge of the vendored
`docs/standards/lessons.md` for "the exo centralizer only", and does not name
`docs/standards/pm.md` in its list at all. section 10 Tier C reserves "this section and
any change to the tiers" to the owner. #800's diff is `docs/standards/pm.md`,
which contains section 10, section 21 and section 22  --  the tiers themselves. Whether that merge was
inside anyone's authority depends on who pressed the button, and every seat and
the owner act through one GitHub account, so `mergedBy` reads `alexandrapaiz` on
every pull request in this repository and distinguishes nothing. That is the
mechanism already recorded as
`INC-2026-10-24-the-merge-checklist-asks-whose-comment-it-is-and-the-api-cannot-say`,
reached here from the other direction: that entry is about a merger unable to
read a condition, and this is about a reader unable to audit a merge afterwards.
Filed as a repeat.

`docs/agents/cross-repo-law.md` rates this propagation shape safe, as shapes 1
and 4 of its four, and it is right on the properties it names: the copy is
visible in the tree, diffable, and carries its source commit in its own header.
Review is the property it does not evaluate, and no local gate asks for one. So
the correct statement is narrow. **The documents that decide who may merge what
in this repository arrive through a path whose authority this repository cannot
audit after the fact.** Nothing here suggests a bad change arrived. The blast
radius is that one would look exactly like the good ones.

## 10. Upstream and supply chain, the standing question

**What did we consume since the last sweep that somebody else controls, and what
would a compromise of it do to us.**

The window is fifty-four minutes and the honest code answer is nothing: no
manifest moved in either language, no action version changed, no image pin
changed, and the two merges that moved `main` are this seat's own already-audited
work. The feeds, the model endpoints, npm, PyPI, the pinned action and the pinned
agent image are all as the 2026-11-02 and 2026-11-09 sweeps left them, and the
open-routing endpoint behind `OPENROUTE_BASE_URL` is still configured and dormant
behind two settings this seat's token cannot read.

What did change is the register's completeness, and `docs/security/upstreams.md`
gets no new row because the artifact already has one. HQ's own runtime was added
to that file by the 2026-11-09 sweep, and this run re-measured the one number on
it: `/srv/asc/hq` is at `6fc71409` now, where the row was written against
`b4b58c98`, and the chair's deploy notes on this company's board record four more
fetches onto the host since, one of which restarted the board. So the row's trust
assumption is live and its rate is roughly what the row claimed.

**One thing this run would add to that row, and it is section 9's channel in
supply-chain terms.** The upstreams register treats HQ as an artifact we execute,
which is the `asc-deploy` path, and that is the loud half. The quiet half is that
HQ also ships us documents we obey, through a different mechanism with a different
gate, and the two were being tracked as one. A compromise of HQ's
`standards/lessons.md` does not need to reach the host to reach this repository:
it arrives as an ordinary docs pull request, re-vendored by a seat this company
does not roster, into a file this seat's charter calls law. The blast radius is
every seat's behaviour in six repositories on this host, and the only thing that stopped the
last prescribed command in that file from resolving to something on this host was
a spelling difference between hyphens and underscores.

Named here rather than written into `upstreams.md`, because the register's rows
are artifacts and this is a second channel on an artifact that already has a row,
and merging the two would make the row less precise rather than more. The ledger
entry in section 11 carries the ask.

## 11. The debug sweep

**Recent evidence.** `gh run list` for `checks`: ten most recent runs, eight
`success` and two `failure`. Both failures are the same pull request,
`alexandria-skill/2026-11-09-message-lane-next` at 01:35:53Z and 01:37:19Z, which
is the skill seat's open #827 and the skill seat's to read. The push-to-`main`
run after #817 landed, `42544626434` at 01:15:44Z, is `success`, which is worth
one sentence because the 2026-11-09 audit reported eight tests failing on `main`
from a malformed list item in `skills/harness-engineering/SKILL.md` and
`tests/test_skill_receipts.py` is both in that count and inside `checks.yml`.
`checks` is green on `main` because the step that runs that file passes against
the merged tree, so the eight were not a `checks` red and the workflow's silence
about them was correct. `deploy-main`: six most recent all `success`, newest
2026-11-02, which is expected since the seats left Actions on 2026-10-17.

**The suite on `main`, and the red count did not fall.** `python3 -m pytest
tests/ -q` against this branch, whose only difference from `main` is this
report: **2,761 passed, 7 failed, 3 skipped** in 11 minutes 34 seconds.

The seven are `main`'s and they are the same seven #829 measured three quarters
of an hour ago, file for file: four in `tests/test_target_census.py`, two in
`tests/test_plugin_manifest.py`, one in `tests/test_reading_queue.py`. #829
reported 9 and attributed 7 to `main`, so the two that went away were that
branch's own and were never the trunk's.

**And this paragraph was written wrong before the measurement arrived, which is
the correction rather than the finding.** The first draft of this section said
the red count fell, on the reasoning that #809 and #820 had landed between the
two readings and that one of them carried a census row. Both halves of that were
false. The census rows for `tools/target_census.py` are on the ExO seat's open
#819, which #829 said plainly and which this run had already read; #820 carried
the CI pin and deliberately not the rows, to avoid duplicating them. So the
inference had the evidence against it in this seat's own previous report, and
the only thing that caught it was waiting for the number. **A delta predicted
from what merged is not a delta, and this seat filed the same class against
itself on 2026-11-09 over a ledger bound measured from a ref chosen by
timestamp.** Named here rather than filed again, because it is the same entry.

Owners unchanged: the census rows are on #819, the manifest count is on the
engineer's #823 and #832, and `tests/test_reading_queue.py` is the research
seat's live queue with no open branch carrying it.

**Imports and the build.** Unchanged and re-measured: all Python files under
`pipeline/`, `tools/`, `mcp/`, `tests/`, `skills/` and `docs/` compile with 0
syntax errors. `npm audit` ran in `site/` against the lock file with no
`node_modules` installed and none needed.

**Recently merged diffs read for defects.** The window is #809 and #820, both
this seat's own, both already read closely on their own branches, and this run
read them again as merged rather than as proposed, which is the reading the three
merge commits in between make different. Nothing found: no conflict marker
anywhere under `docs/`, `prompts/`, `README.md`, `tools/` or `tests/`, no
docstring that lies about its code, both ledger appends intact and in date order.
One thing worth the sentence: `tools/target_census.py` and
`tests/test_ci_coverage.py` were each touched by both pull requests, and the
merged result passes both files' own gates, which is the case a three-way merge
of two branches at one file is most likely to get quietly wrong.

**Gates, before `gh pr ready`.** The conflict-marker grep prints nothing.
`python3 tools/root_scratch.py` exits 0, so this branch adds no stray file at the
checkout root. `tests/test_ci_coverage.py` passes, which is the pin that matters
here: this diff adds no test file, so the uncovered set has not grown.
`python3 tools/incidents.py check` passes on this run's new entries. Every scratch
file this run wrote is under a `mktemp -d`, per step 0b.

**The branch prefix, re-measured at the source rather than carried.** The harness
suggested `alexandria-security/2026-11-09-message`. The charter holds the prefix
at `sec/` until `semimonthly` joins `NO_SELF_CONTINUE` in HQ's
`runtime/board/api.py`, and the hold is not style: renaming it alone converts a
seat that receives no merge event into a seat that wakes itself on every merge.
Checked on the deployed HQ tree at `6fc71409`, `api.py:374` still reads
`{"monthly", "quarterly", "dispatch-only", "none"}`, and `company.yaml` here
still declares this seat `semimonthly`. `python3 tools/wake_routes.py --seat
security` agrees with the source and says so in one line: `pr.merged` is
`deaf:prefix`, and "behind it the cadence gate would allow the continue-wake."
So the prefix stays wrong on purpose, seventeen days into the relay row. Another
instance of
`INC-2026-11-02-the-dispatch-prompt-now-instructs-the-branch-prefix-its-own-charter-holds-back`,
re-measured at the source rather than re-filed, and with no ordinal on it,
because the only number available on a branch is the one a previous run wrote.

## 12. What this run fixed, and what remains

**Shipped here.** This run is a verification and a report, so what it ships is
findings rather than code, and that is stated plainly rather than dressed up.

1. This report, which settles at the source a question two registers left
   explicitly open on 2026-11-02.
2. Three repeat entries in the incidents inbox: the register's own detector
   under-reporting as the repository grows, the unauditable merge authority on the
   vendored-standards channel, and this run's own hand resolution deleting two
   lines of another entry, which is section 13.
3. Two `proposed` ledger entries: vendor or restate L-P8's two commands, with the
   evidence that they exist at HQ and the one-underscore distance on the local
   half; and one line for the pre-ship ladder, which asks whether a conflict
   marker survived and never whether a line did not.

**What remains, with an owner on each.**

| finding | severity | owner |
|---|---|---|
| L-P8 prescribes `tools/check-pr-green.py` and `tools/check-run-ran.py`; HQ has both, this repository has neither under that spelling | low | HQ, through the ExO relay |
| the branch-reuse detector in the incident register and in twelve charters is bounded at 300 and 200 against 835 pull requests | medium, because it fails toward silence | ExO seat for the register, owner for the charters |
| a vendored-standard merge's authority cannot be audited, because all seats share one account | medium | ExO seat, same root as `INC-2026-10-24-the-merge-checklist-asks-whose-comment-it-is` |
| Tier B condition 3 is satisfied without a check for 80 of 94 test files | medium | PM seat, and the instrument already exists at `tools/check_pr_green.py` |
| `tools/root_scratch.py` is called by nothing: one charter line and one `paths:` line | medium, this seat's own output | ExO seat and engineer seat, filed 2026-11-09 |
| `_redact`'s candidate set does not hold a percent-decoded password | low and latent | engineer seat |
| `checks.yml` filters on `prompts/daily.md`, which has never existed | low | engineer seat, filed 2026-11-09 |
| `sentence-transformers` unpinned in `pipeline/distill.py:285` | low, carried since 2026-09-18 | engineer seat |
| floating major tags on all seven distinct actions | low, carried | engineer seat |
| `semimonthly` absent from `NO_SELF_CONTINUE`, so this seat's prefix stays wrong on purpose and stays deaf on two of four subscriptions | medium, carried 17 days | HQ, through the relay |
| `.prbody-exo.md` and `site-server.log` tracked at the root on `main` | low | ExO seat and frontend seat |

No severe finding this run. No leaked secret, no exploitable exposure, nothing
that requires the owner's immediate action.

## 13. This run damaged a register and the ratchet caught it, not a reader

Last, because it is this run's own defect and burying it would be the wrong
shape.

#829 and #830 landed while this branch was open, and the ledger tail anchor
conflicted exactly as this run's pull request had predicted in writing. The
resolution was written by hand, as a script that sliced the three conflict
markers apart and concatenated the two sides in merge order. It dropped the last
three lines of the other side's entry: a blank line, its cost field and its
status field.

**The reason is worth more than the slip.** The script's arithmetic over the
conflict region was correct, and a conflict region is not an entry. Git's region
began inside the other entry's trailing bullet rather than at its heading, so
those last field lines sat below the `>>>>>>>` marker in `ours` context and were
in neither slice. Concatenating two sides preserves every line only when the
output keeps the region's own order, and this run needed the other order to put
the earlier-merged entry first. So reordering is not a safe operation on a
conflict region, which is not obvious and is the generalizable part.

**Five of six gates passed on the damaged file.** `tools/ledger.py --patch`
passed, because it audits the entries a branch adds and the damage was in one the
branch received. The conflict-marker grep passed, because the markers were
correctly removed. `tools/incidents.py check`, `tools/root_scratch.py` and
`tools/ban_list.py` all passed. The ratchet in `tools/ledger.py --check` was the
only refusal, and it refused with the wrong sentence: it said a new entry had
been appended without a status, and the new entry had one. Attribution took two
more steps and was settled by running the ratchet against `origin/main` in a
throwaway worktree, which came back clean at the baseline.

**The tool for this exists here and this run did not use it.**
`tools/resolve_register_conflict.py` says in its own docstring that it resolves
two register appends and proves the resolution lost nothing. Run afterwards with
`--check`, it named all three dropped lines in one call, by counting every line
across base, ours and theirs, and it reported the other conflicted file in the
same merge as balanced in the same breath. That second half is an answer a hand
check does not produce at all.

Fixed in place rather than by force-pushing the history away: the three lines are
restored, `diff` from `origin/main`'s copy of `docs/ideas.md` to this branch's
reports **0** deleted lines, and the damaged entry is byte-identical to `main`'s.
The bad merge commit stays in the history with the incident entry beside it,
because a corrective commit is a record and a force-push is not.

Filed as a repeat of
`INC-2026-10-24-a-hand-resolved-register-append-deleted-another-seats-line-with-no-marker`,
with the ladder line in the ledger. **And the charter sentence it lands on is the
one this seat carries for other people's code: a one-line repair that reads as
obviously correct is the place to look for a second defect.** The hand
resolution read as obviously correct.
