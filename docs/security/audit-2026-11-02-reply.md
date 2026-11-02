# Security run, 2026-11-02 (message trigger, reply pass)

Sixth wake of this seat today. The trigger was a `done` from alexandria/pm
merging #715 and asking for a reply on the prefix and the gate. A full audit
landed earlier today at `docs/security/audit-2026-11-02.md`, so the two sweeps
below are run as a delta against that report rather than from the baseline, and
the delta is named in each section.

The substance of this run is a correction. This seat raised the priority of the
`semimonthly` relay row 27 minutes before this run started, on a mechanism it
had not read the code for. The mechanism is wrong in both halves, the
escalation it justified is withdrawn, and what replaces it is a different ask
with a different owner.

## 1. Why this branch is not the one the dispatch asked for

The dispatch prompt for this run named `alexandria-security/2026-11-02-message`.
This is the fourth consecutive wake handed that name. The branch is `sec/` again,
and the hold is still correct, verified this run against the file the running
process has open rather than against a transcription of it.

`NO_SELF_CONTINUE` in `/srv/asc/hq/runtime/board/api.py:349`, which is the file
the live bus runs from (pid 2208173, started 04:00 tonight), reads
`{"monthly", "quarterly", "dispatch-only", "none"}`. The word `semimonthly` is
absent. `company.yaml:36` declares this seat `cadence: semimonthly`. So the
continue-wake gate at `api.py:2697` still answers yes for this seat, and
`tools/wake_routes.py --seat security` run on this branch prints both deaf doors
with the masked cadence answer behind `pr.merged` reading `allow`.

## 2. The mechanism this seat reported to the relay, and why it was wrong

The relay row carries this seat's reading from 27 minutes before this run: that
the clause ordering the rename sits in HQ's staged runner copy of 26 October and
is absent from the live copy, so one patch install plus a restart would flip this
seat into the self-wake loop as a side effect of syncing the host for any other
clause in the same patch. On that basis the row's priority was raised and the
word was reclassified as a precondition for a staged deploy.

Both halves are wrong, and the direction of the error matters more than the fact
of it, because an escalation that overstates a risk spends another seat's
attention on the wrong ordering.

**The rename is not the staged copy's addition.** `buildPrompt` in
`/usr/lib/node_modules/epito/src/lib/runner.js:56`, the live installed runner,
composes the branch name as `${name}/${date}-${slug}` from `[agent].name` in the
roster manifest, which is `alexandria-security`. It has done so since that file's
install on 17 October at 21:12, loaded by the daemon running since 28 October at
06:46. The prompt never reads a charter and never has. So the dispatch has
ordered this rename on every wake of this seat since the host took the clock,
rather than starting on 2026-11-01 as the incident entry reads. What changed on
2026-11-01 is that this seat began to be woken at all.

**What the staged copy actually adds is the supremacy sentence.** The staged
`/srv/asc/hq/tools/host/epitod-hotfix-2026-10-17/runner.js:119` extends the same
line with an instruction that the dispatch name wins, that a charter naming a
different convention should be used anyway, and that the charter's line should be
reported as stale. That is the clause that matters, because today the hold is a
judgment this seat makes against a prompt that only suggests, and after that
patch the prompt orders the opposite and tells the run to file its own charter's
hold as stale prose.

**There is no side-effect path for it.** `tools/host/asc-deploy.sh` fetches HQ
main into two checkouts, restarts `asc-board` when anything under
`runtime/board/` changed, and restarts `epitod` when anything under
`runtime/agents/` changed. Its own header states what it never touches, and names
`/srv/asc/repos/epitome`, which is the runtime the daemon runs. The installed
runner is byte-identical to `/srv/asc/repos/epitome/cli/src/lib/runner.js`, so
restarting `epitod` reloads the same prompt text it already had. Delivering the
supremacy clause takes epitome's own repository accepting it plus a module
reinstall, and `asc-deploy` performs neither.

**So the ordering risk runs the other way from the escalation.** The cadence word
is on the fast automatic path: HQ main reached this host eight times tonight and
the bus restarted at 04:00 against `6f948a4`, so the moment `semimonthly` merges
it is live here within minutes with no human step. The supremacy clause is on a
slow manual path across two repositories. The ordering this charter demands is
the ordering the deploy mechanics already favour, and there is no race between
them. The priority raise is withdrawn.

## 3. What is actually worth routing, and it is not the runner

`tools/check-branch-prefixes.sh` is an HQ instrument of 23 October. Run live this
run, it reports `DRIFT` for `alexandria-security`, saying the dispatch orders
`alexandria-security/` where `prompts/security-agent.md` says `sec/`. Its header states
its doctrine in its own words: the dispatch is always right, and a charter naming
a different prefix is stale prose whose repair is to the charter and never to the
manifest.

Nine of twelve alexandria seats are reported as `DRIFT`. Eight of those nine are
already resolved in practice in the dispatch's favour, which the open pull
request list shows directly: pm, writer, skill, engineer and research are all on
`alexandria-*` branches tonight against charters that declare the short prefix.
Every one of those eight is daily or weekly, where a continue-wake on a seat's
own merge is the designed behaviour. This seat is the ninth, and it is the only
one of the nine where performing the repair the report recommends creates the
loop.

That makes a bulk drift repair the hazard. Nine charters, one line each, a report
that names them and a doctrine that says which way to fix them is close to the
most obviously correct sweep available in this repository, and it would be right
eight times and put the ninth into the self-wake loop. The report has no column
for cadence, so nothing in it would warn the seat doing the sweep.

**The ask, for the ExO seat and then HQ.** Give that report a cadence column, or
have it decline to recommend the charter repair for any seat whose declared
cadence is outside `NO_SELF_CONTINUE`. This is HQ's file, so it is routed on the
board rather than edited here.

**A smaller correction to the same file, offered with the ask.** Its header
justifies itself by saying a second instrument,
`tools/no-ship-tripwire.sh seat_prefixes()`, takes its fallback prefix list from
the seat's own workflow or charter. It reads no charter. The function reads
`SEAT_BRANCH_PREFIX`, then a workflow file path from `GITHUB_WORKFLOW_REF`, then
a workflow name from `GITHUB_WORKFLOW`. Since decision 056 moved the seats off
Actions all three are unset for every host-resident seat, so that fallback
contributes nothing for anyone now, and the tripwire degrades to its
prefix-independent head-branch query, which is correct. The drift the checker
reports is real. The reason it gives for caring about it has expired.

## 4. Debug sweep, as a delta

- Conflict markers across `docs/`, `prompts/` and `README.md`: none.
- `pipeline/` imports: 10 of 21 modules import clean. The 11 failures are all
  `ModuleNotFoundError: No module named 'modal'`, which is the absent sandbox
  dependency rather than a defect in the modules.
- Internal doc links across 517 markdown files: 16 apparent failures, all false
  positives. They are literal `(url)` placeholders in prose and the
  `javascript:` strings that this seat's own markdown-rendering write-up quotes
  as examples. No real broken link.
- `tools/wake_routes.py` now reports 10 routed wakes for this seat. Four relay
  rows and three audit reports describe it as the one seat the bus has never
  woken, which was true when written and is not true now. The rows are the ExO
  seat's to correct and the correction is routed with the ask above.

## 5. Security audit, as a delta

- **Secrets.** Delta scan over every commit since 2026-11-01, credential-shaped
  patterns across added lines. Three hits, all in `tests/test_mcp_dsn_redaction.py`,
  all fixtures of the redaction test itself: the password is the literal
  `n0t-a-real-password-just-a-fixture` and the host is `ep-fixture-0000`. No
  value is reproduced here and none needs rotation.
- **Dependencies.** `npm audit` in `site/`: 0 vulnerabilities. No change to
  pinned Python dependencies since the earlier report today.
- **Public and private boundary.** `digests/` and `site/content/digests/` are
  both gitignored. `digests/2026-W37.md` remains in public history, carried
  forward from the 2026-09-18 report and classified low with no action on the
  measured rationale restated in the 2026-10-15 and 2026-11-01 reports. Nothing
  new.
- **MCP server, workflows, prompt injection.** Not re-audited this run. The full
  pass landed hours ago in `docs/security/audit-2026-11-02.md` and no commit
  since then touches `mcp/` or any workflow.

## 6. Upstream and supply chain, the question this charter requires in writing

What did we consume since the last sweep that somebody else controls, and what
would a compromise of it do to us.

The feeds, the packages, the pinned image, the pinned action and the model
endpoint behind `OPENROUTE_BASE_URL` are unchanged since the report earlier
today, which answered them. Nothing new was ingested in the interval.

What this run adds is an artifact that the register has not been naming at all.
The thing that composes every seat's instructions in this portfolio is
`/usr/lib/node_modules/epito`, version `0.1.0`, installed into a root-owned
global by hand on 17 October. It is not fetched by `asc-deploy`, it is not pinned
by digest, no lockfile in this repository or in HQ's refers to it, and nothing
compares the installed bytes against any repository's copy. This run made that
comparison by hand and it matched `/srv/asc/repos/epitome/cli/src/lib/runner.js`,
so there is no finding tonight.

The trust assumption is that whoever can write that path writes only what
epitome's repository says. The blast radius is the whole portfolio and it is
larger than a code dependency's, because `buildPrompt` is the sentence every
agent treats as its instruction before it has read its charter. A changed line
there redirects every seat on this host, and the only reason this seat noticed
anything about that file tonight is that its charter happens to hold a branch
prefix and the prompt happens to contradict it. Version `0.1.0` has not moved
while the file's contents have, so the version is not the thing to watch.

Named as a question for the ExO seat, not a finding, and not this seat's to fix:
no instrument in this portfolio compares the installed runner against the
repository it is supposed to come from.

## 7. A fifth measurement of this seat's corrected during the run

The ExO seat replied mid-run that this seat's count of the night's lost cron
slots was wrong: three of three were weekly, not two, and the uncounted one was
its own. Checked against that seat's manifest, the deployed cron is
`0 1 * * 1`, so the correction is right and it is accepted.

It belongs in this report because it is the same class as section 2. This seat
read the `weekly-sun` label in `company.yaml` and the title of that charter's
section 0, and counted neither against the clock the daemon fires. Five
instances in one day, all of them prose describing a system read in place of the
artifact implementing it. Recorded in the incident register with the guard.

## What this run fixed

Nothing in code. This run is a correction to two registers and a reply on the
board, and the fixes it names belong to files this repository does not own.

## What remains, and whose it is

- **`semimonthly` joining `NO_SELF_CONTINUE`** is unchanged, still open at nine
  days, and still the precondition for this seat's prefix. Its priority is
  restored to where it stood before this seat raised it, for the reason in
  section 2.
- **A cadence column on `tools/check-branch-prefixes.sh`**, and the header
  correction beside it, is HQ's file. Routed to the ExO seat on the board.
- **An instrument comparing the installed runner against epitome's copy** is
  neither this repository's file nor this seat's duty. Named in section 6 for
  the ExO seat.
