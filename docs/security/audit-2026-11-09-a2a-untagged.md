# Security audit, 2026-11-09 (message wake, A2A's untagged authorization clause)

Seat: alexandria/security. Branch: `sec/2026-11-09-message-a2a-untagged`.
Trigger: a `handoff` from alexandria/pm at 11:06Z, board message
`a6a7d6a2-a473-4475-b7de-b9d81f6cd507`, relayed verbatim from research's
merged pull request #913.

The handoff said that A2A's clause requiring an agent not to treat a state
transition as authorization for any particular operation merged on 2026-07-30,
that the latest tagged spec release is still the one of 2026-05-28, and that
research named the clause as this seat's territory rather than its own.

**No severe finding this run.** No leaked secret, no exploitable exposure,
nothing requiring the owner's immediate action.

## This was a duplicate wake, and the earlier run answered half of it

The run behind pull request #860 received this same message at 11:06Z,
eighteen minutes into its own work. It answered the exposure half and wrote
that the rest "is not an exposure question and is not this run's event, so it
is named on the board rather than taken."

That reading was right about its own scope and it left a real question
standing. The charter's duplicate-wake clause says to verify the earlier
report live rather than trust it, so both halves below are re-measured here
from the source rather than carried.

### Verified: the exposure answer is zero, and here is the whole surface

| where A2A appears | what it is | exposure |
|---|---|---|
| `sources.yaml:130` `gh-a2a-protocol` | releases atom feed, tier d | ingestion only |
| `sources.yaml:155` `gh-a2a-spec-changelog` | spec-path atom feed, tier d | ingestion only |
| `pipeline/priority.py:71` | the string `"a2a"` in a keyword list | curation steering |
| `pipeline/topics.py:131` | `"MCP, A2A, agent cards"` in a topic description | curation steering |

Nothing implements A2A. No manifest names it: not `site/package.json`, not
`requirements.txt`, not `requirements-dev.txt`, not `skills-lock.json`, not the
`pip_install` list in `mcp/server.py`. Nothing pins the specification, so
nothing here can be pinned to a release that lacks the clause. The two
`pipeline/` hits are additions to #860's count and they change the answer in
neither direction, because a keyword that steers triage carries no authority.

**So the untagged clause creates no exposure for this repository, and the
reason is that this repository is a consumer of A2A news rather than a builder
on A2A.** That is the honest form of the answer, and it is worth separating
from "we checked and we are fine," because the thing that protects us is a
fact about our architecture rather than a control anybody installed.

## The finding: the feed that exists to catch this clause watches the wrong path

This is the half the handoff was really about, and it is an ingestion defect
rather than an exposure one.

`sources.yaml` already anticipated this exact mechanism, 40 days before the
handoff arrived. Its own comment, written 2026-09-30, says releases feeds on a
specification repository "return the tag while the normative change lives in
the spec tree," and that is why `gh-a2a-spec-changelog` was added beside the
releases feed. The design was correct. The implementation missed.

Measured this run:

| feed | path watched | newest entry | carries A2A PR 2081? |
|---|---|---|---|
| `gh-a2a-spec-changelog` (configured) | `specification/` | **2026-07-21** | **no** |
| `commits/main/docs/specification.md` (corrected) | the spec prose | 2026-10-12 | **yes, in the current window** |
| `gh-mcp-spec-changelog` (sibling row) | `docs/specification` | 2026-11-09 | n/a, correct already |

A2A pull request 2081, "docs(spec): clarify in-task authorization scope
semantics," merged 2026-07-30T20:24:35Z and changed **exactly one file**, and
that file is `docs/specification.md`. The configured feed watches the
`specification/` directory, which holds A2A's machine-readable schema and not
its normative prose. Its newest commit is 2026-07-21, nine days older than the
clause, and it has not moved in 111 days.

So three things are true at once. The feed's stated purpose was to catch
normative spec changes. The clause is a normative spec change. The feed could
not have delivered it, and it is the only A2A source we have that was ever
meant to.

**The sibling row had the path right in the same commit that added both.**
`ce640aa2` of 2026-09-30 added `gh-mcp-spec-changelog` pointing at
`docs/specification` and `gh-a2a-spec-changelog` pointing at `specification`.
One row of two carried the transcription error, and the comment above them
asserts the intent that the wrong row defeats. That comment is the charter's
named specimen class, a stale comment that lies about the code, and it had been
lying for 40 days.

**This explains why research found the clause by hand.** The question "why did
our own corpus not surface a normative change on a feed we subscribe to" has an
answer in configuration, and nothing in the pipeline could have reported it,
because a path-filtered feed that returns twenty real entries looks healthy to
every check we run. `tools/feed_health.py` asks whether a feed answers, not
whether it answers about the thing it was added for.

### What this run fixed

`sources.yaml`: added `gh-a2a-spec-prose` pointing at
`commits/main/docs/specification.md.atom`, and corrected the comment above it to
state the measurement rather than the belief. The existing
`gh-a2a-spec-changelog` row is **kept**, because a change to the schema is
still worth one row, and removing a working feed is not the repair for a missing
one. The corrected feed carries the clause commit in its current twenty-entry
window, so the clause is recoverable into the corpus on the next ingest rather
than lost.

Research owns the tier and the curation judgment on any source row and may
revert or retier this; the defect fixed here is the mismatch between a feed's
path and the purpose written above it.

## The clause, read against our own code, which is what research asked for

Research named this "the engineer's and the security seat's territory." The
security half of it is not whether we pin A2A. It is whether our own systems
commit the defect the clause forbids. A clause that reads MUST NOT in somebody
else's specification is free design review for us, and it is worth spending
once even where the specification does not bind us.

Two places in this repository perform the shape the clause describes, which is
a state transition followed by a privileged operation. They answer opposite
ways.

### `tools/panel_merge.py` honours the clause, and it is the pattern

ADR-13's autonomous panel merges pull requests. The state it could treat as
authorization is "three reviewers passed unanimously." It does not:

- `judge()` sets `merge_allowed = verdict == "pass"`, deliberately not
  `verdict != "fail"`, so an `unknown` blocks rather than permits.
- `token_findings()` requires a token minted for the panel and scoped to
  `contents: write` and `pull_requests: write`, and **names and declines** any
  ambient `GH_TOKEN` in the environment, on the stated ground that a seat's
  credential merging a proposal is a seat merging rather than a panel.
- `do_merge()` sends the head `sha` with the merge call, so GitHub refuses if
  the branch moved between the verdict and the merge.

That is per-operation authorization, separately held and re-checked at the
moment of the operation, which is exactly what the clause asks for. Recorded
here because this seat's audits mostly name what is wrong, and a correct
implementation of a clause a specification states as MUST NOT is the cheaper
thing to point other seats at.

### The MCP server does not, and this is already an open finding

`mcp/server.py:628` is one middleware with one binary question, `token_ok`. A
bearer token that verifies reaches every tool on `/mcp`: `semantic_search`,
`sql_query`, `rag_answer`, `discovery_report`, `get_digest`, which returns
private digest bodies, and `propose_skill` and `propose_change`, which hold a
GitHub token that creates branches and opens pull requests against
`prompts/*.md`, meaning against the twelve charters the agents run on. The
access token carries `typ`, `sid`, `iat` and `exp` and **no scope claim at
all**. `GLOBAL_SCOPE` in `mcp/oauth_flow.py:192` is a throttle key, not an
OAuth scope.

**This is not a new finding and it is not reported as one.** It has been open
since the first baseline, `docs/security/audit-2026-09-18.md:204`, under the
name "authorization blast radius," restated on 09-19, 09-24, 10-01 and 11-01.
The server's own docstring at `mcp/oauth_flow.py:720` states the consequence in
its own words: a token "reached every tool on /mcp: the corpus, the
subscriber-bearing database, and a GitHub token that opens pull requests."

What this run adds is one thing and it is not a measurement. **The finding now
has a normative name outside this repository.** It has been argued here for 52
days as a design preference, which is the weakest form an open finding can
have, and the identical shape is now MUST NOT in a published agent-interop
specification. That changes nothing about the exposure and something about the
priority, and the priority is the engineer's and the owner's to set rather than
this seat's.

**And the clause is untagged, which is the part that matters for anyone
reading this later.** A builder who pins the A2A specification to a release
does not have the sentence. So the external backing this finding just acquired
is invisible to the ordinary way of consuming that specification, and will stay
invisible until A2A cuts a tag. That is the handoff's real content, and its
audience is any seat here who later cites the clause as settled.

### The clause read against our own wake mechanism, which is the sharpest form

Our seats are woken by state transitions. `pr.merged`, `check.failed`, a
message arriving on the bus. The clause's question, asked of us, is whether a
seat treats having been woken as authorization for the operation the waking
event names.

This run is a live instance and the answer held. The host handed this run the
branch name `alexandria-security/2026-11-09-message`. The charter's hold
refused it, on a condition this run re-read at source rather than inferred, and
the refusal came from the charter rather than from judging the payload. The
#860 run recorded the same structure from the other side: it was told by a
payload to ready a pull request, and what forbade self-merge was the charter
rather than anything in the message.

So the guardrail is structural, and that is the right kind. **What is worth
naming is that it is structural by accumulation rather than by design.** No
file in this repository states the rule "a wake authorizes nothing by itself."
Twelve charters each enumerate operations a seat may not perform, and the union
of those enumerations is what has been holding. A union of enumerations is a
weaker guarantee than a stated invariant, because a new operation is permitted
by default until some charter names it, and nothing checks the union for gaps.

That is a proposal rather than a finding, and it is filed as one. It is not
fixed here because writing the invariant into charters is a charter edit, and
this seat does not edit charters.

## The charter's standing sweeps

**Secrets.** Clean. Full-history scan over every blob on every ref, 15
credential patterns, **9,752 blobs over 5,441 commits and 528 refs, 1,737 MiB
in 2,124s**. No value is reproduced anywhere in this report, per the charter.

Four patterns matched and all four triage to false positives:

| pattern | blobs | what it is |
|---|---|---|
| `app-password` | 4,718 | the pattern is four consecutive four-letter lowercase words, which ordinary English prose satisfies constantly. Noise from this run's own pattern choice, not a finding |
| `pg-url` | 4 paths | two prose examples in `docs/`, one triaged baseline file, and `tests/test_mcp_dsn_redaction.py`, where the DSN is built by an f-string from variables |
| `privkey` | 1 | `tools/history_secrets.py`, which carries the `BEGIN PRIVATE KEY` string as a detection pattern and so matches itself. A detector matching its own source |
| `anthropic` | 1 | a synthetic shape literal in `tests/test_check_authority.py`, in a list of three hand-written credential shapes used to assert that the authority checker reserves them. Present only in two blobs of 2026-10-24 and absent from the current tree |

Two of those deserve a sentence beyond the verdict. The `app-password`
pattern's 4,718 hits are this run's own fault and they are worth reporting
rather than quietly dropping, because a pattern that fires on prose makes a
clean answer indistinguishable from an unread one on a repository that is
mostly prose. And `tests/test_check_authority.py` is interesting in the small:
one of its three literals is written as `"ghp_" + "A" * 25` with the comment
"built here so no scanner matches the file," and the one this scan matched is
the one written whole. The careful form and the careless form are four lines
apart in the same test.

**Dependencies.** `npm audit` in `site/`: 0 vulnerabilities across all
severities. No manifest moved between `main` and this branch other than
`sources.yaml`, which carries no code.

`sentence-transformers` in the MCP image's `pip_install` still has no bound at
all, in a container that holds the database URL, the GitHub token and the login
passphrase. **Re-confirmed, not re-filed:** open since
`docs/security/audit-2026-09-18.md:149` and restated in four audits since.
`requirements.txt` is a single `modal>=1.5`. Unchanged this window.

**The public and private boundary.** `digests/` and `site/content/digests/` are
both gitignored, both absent from the working tree, and both absent from every
current tree. The one standing history row is unchanged: `digests/2026-W37.md`
exists in ten commits between `043767e5` of 2026-09-08 and `6910bd9b` of
2026-09-11, the commit that made digests private. Raised and withdrawn in
September, re-measured here, no change. No subscriber data in the public tree.

**The MCP server.** Audited above against the clause. The rest of its posture
is unchanged from `main` and untouched by this run: `sql_query` is SELECT and
WITH only with a 200-row cap, the authorize throttle and the code ledger both
persist to Postgres and both degrade to in-process counting on a database error
rather than failing closed, and `read_access_token` checks session revocation
on every request. The `sid`-less carve-out in `read_access_token` is a
documented deliberate exception with its reason stated in the code.

**The workflows.** No `pull_request_target` anywhere, so no foot-gun of that
class. Triggers are 12 `repository_dispatch`, 14 `workflow_dispatch`, 2 `push`
and 1 `pull_request`. Every workflow declares a `permissions` block. Actions
are pinned to major tags rather than commit SHAs, which is the standing posture
and unchanged.

All twelve agent workflows interpolate `${{ github.event.client_payload.text }}`
into the model prompt. **Re-confirmed, not re-filed:** already recorded in
`docs/security/audit-2026-10-15.md:392` and
`docs/security/audit-2026-11-01.md:365`. `repository_dispatch` requires a token
with write access on this repository, so the payload is not open to the public
web. These workflows have not run since decision 056 retired the seats'
schedules on 2026-10-17.

**Prompt injection.** The surface this run exercised is its own wake, and the
reading is in the clause section above. Nothing new found and one thing worth
repeating: the thing that held was a condition in a charter checked against the
source, not a judgment about whether the payload looked trustworthy.

**Upstream and supply chain, the written answer.** The charter asks one
question each sweep: what did we consume since the last sweep that somebody
else controls, and what would a compromise of it do to us.

The window since #860's sweep is under two hours, so the inventory is short and
the answer is close to "nothing changed," which the charter admits as valid and
still requires in writing.

- **Nothing new arrived.** No npm dependency, no Python pin, no action version,
  no image change, no new model endpoint. The one artifact #860 reported for
  this day, HQ's vendored `tools/merge_register.py`, is already on `main` and
  this run consumed it in no form.
- **One upstream read for the first time by this seat**, and it is the subject
  of this audit: `github.com/a2aproject/A2A`, read over two public atom feeds
  and the public pull request metadata for PR 2081. Trust assumption: we trust
  it only as a signal source, and the blast radius of a compromise is false or
  poisoned rows in the corpus's tier-d ingestion, triaged by a model and
  reviewed by the research seat before anything becomes a claim. Nothing in
  this repository executes, imports, or pins anything A2A publishes. Adding
  `gh-a2a-spec-prose` keeps the blast radius where it already was: same
  publisher, same transport, same tier, one additional path on a repository we
  already poll twice a day.
- **One row owed to `docs/security/upstreams.md` and deliberately not written
  here.** The standing rule in that file says every new source gets a row in
  the same pull request that adds it. #860 edits that file and this branch
  comes from `main`, so writing the row here creates the same-file collision
  the charter's ledger rule exists to prevent. The row is owed after #860
  merges, it is named in the pull request description, and this paragraph is
  the honest form of a gap rather than a silent one.

## Debug sweep

Build and gates, run against this branch's tree:

```
check_registers.py            0 blocking, 71 warning(s)
incidents.py check            375 entries, 276 in the inbox, nothing malformed
ledger.py --inbox             ok
target_census.py --check      ok: all 161 judgment-needing flags classified
npm ci (site/)                42 packages, 0 vulnerabilities, exit 0
next build (site/)            exit 0, every route built
python -m ast over pipeline/  every module parses
internal doc links            1,060 markdown files, 188 internal links, 0 broken
pytest, the sources.yaml files  197 passed
pytest, three sampled batches   678 passed, 3 skipped
```

The 71 `check_registers` warnings are all pre-existing on `main` and none is
blocking. The doc-link check reported 21 apparent failures and all 21 are
literal `(url)` placeholders in prose or `javascript:` strings inside this
seat's own earlier write-ups of the unsanitized-render finding, so the real
count of broken internal links is zero.

**The full suite has no verdict this run, and that is reported rather than
implied.**

```
SENTINEL run=952a74ac9ddc label=suite INCOMPLETE code=timeout limit=2400 seconds=2400.2
```

It reached roughly 89 per cent and was terminated. The cause was this run's
own doing: the site build ran while the suite was open, `/tmp` fell from 2.8
GiB free to 1.4 GiB on a host already at 94 per cent, and this repository's
suites stand up real Postgres clusters under `/tmp`. The failures were `E`
rather than `F`, which is a fixture that could not start rather than an
assertion that disagreed, and they cluster exactly in the minutes the disk
fell.

What stands in place of a suite verdict is 875 cases re-run green after
`site/node_modules` was removed: every test file that reads `sources.yaml`,
which is the only non-documentation file this run changed, plus three batches
sampled from the error region including the densest block. Filed as
`INC-2026-11-09-this-seats-own-site-build-starved-the-suite-it-was-running-and-the-reds-would-have-read-as-the-diffs`,
with the ordering repair routed to the engineer, because two duties in one
sentence of this charter told one run to race itself.

No defect found in recently merged diffs beyond the `sources.yaml` comment
fixed above, which is the charter's named specimen class and the second
confirmed instance of it after `pipeline/weekly.py`'s mail-provider docstring.

## Findings table

| # | severity | finding | state |
|---|---|---|---|
| 1 | medium | `gh-a2a-spec-changelog` watches `specification/`, the schema, so the normative clause it existed to catch was unreachable and the comment above it asserted otherwise for 40 days | **fixed this run** |
| 2 | low | no check asks whether a path-filtered feed answers about the thing it was added for; `feed_health.py` asks only whether it answers | filed for the engineer |
| 3 | low | no file states the invariant "a wake authorizes nothing by itself"; twelve charters' enumerations are holding it by accumulation | filed, charter work, not this seat's |
| 4 | medium | one bearer token reaches every MCP tool, including two that hold GitHub PR authority; the access token carries no scope claim | **open since 2026-09-18, re-confirmed, now with external normative backing** |
| 5 | low | `sentence-transformers` unbounded in the MCP image | open since 2026-09-18, re-confirmed |
| 6 | low | `client_payload.text` interpolated into twelve agent prompts | open, re-confirmed, workflows dormant since 2026-10-17 |
| 7 | low | this charter pairs a site build and a test suite in one sentence with no ordering, so one run races itself for disk on a shared host | filed, charter work, not this seat's |

Findings 4, 5 and 6 are re-confirmations and are listed so that a reader of
this file alone sees the standing posture rather than only this run's delta.

## What remains

For the engineer, filed in `docs/ideas/inbox/`: a feed-purpose check that
compares what a path-filtered source delivers against why it was added.

For the owner and the engineer: finding 4's priority, now that the shape has a
MUST NOT in a published specification. This seat does not set that priority and
does not propose a design, because scoping the MCP token is the engineer's work
and spends a deploy.

Owed after #860 merges: the `docs/security/upstreams.md` row for
`gh-a2a-spec-prose`.

Owed by somebody with charter authority: the one sentence putting this
charter's site build before its suite.
