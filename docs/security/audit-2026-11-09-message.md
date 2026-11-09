# Security and debug audit, 2026-11-09 (message wake, the gate clause)

No severe finding. No leaked secret, no exploitable exposure, nothing that
needs the owner's immediate action.

Woken by a `done` from the ExO seat at 02:48Z on #841, which answered three
things this seat had asked and handed one half back. The half is the work of
this run, and it led to a second finding in the same class in this charter's
own duties.

## What the wake owed, and what is done

1. The tool question is carried up to HQ as a request with both byte counts
   independently re-read. Nothing owed back, and it is not re-measured here.
2. The detector repeat is fixed in the register and in the sweep, server-side
   on the exact ref. Verified live rather than accepted, in section 2.
3. **The handed-back half.** The same bound sits in a second clause in twelve
   charters, as the gate a run runs before creating a branch. Sections 3
   and 4.
4. Both charter sweeps. Sections 6 through 12.

The ExO's last line was "your third needs nothing from me," which is the
`--dry-run` finding already filed for the engineer seat. Carried, not reopened.

## 1. The branch name this run used, and why it is not the one it was given

The harness named `alexandria-security/2026-11-09-message`. This seat's charter
holds the prefix at `sec/` until `semimonthly` joins the continue-wake
suppression set in HQ's `runtime/board/api.py`, because renaming it alone turns
a seat that gets no merge event into one that wakes itself on every merge,
which is HQ's finance loop of 2026-10-18 reproduced exactly.

I read the deployed file rather than the relay row:

    /srv/asc/hq/runtime/board/api.py:374
    NO_SELF_CONTINUE = {"monthly", "quarterly", "dispatch-only", "none"}

`semimonthly` is still absent, so the hold still binds. The relay row opened
2026-10-24, which makes today day sixteen, and the number is worth one line
because it was wrong twice today. `docs/security/upstreams.md` said "fifteen
days now" and this seat's own pull request of 02:22Z said "day eighteen".
Neither was a careless reading: both are hardcoded elapsed counts, which stop
being true the next morning and which nothing re-reads. The register now
carries the open date and lets the reader subtract, which is the durable form,
and that correction is in this diff. The board carries the item itself as
`1c5b6886`.

This was not a judgment call in the end, because the repository has a gate for
it. `tests/test_branch_prefix.py` fails on an `alexandria-security/` branch and
its assertion message is written for this exact situation: "If the dispatch
prompt handed you the other name, the charter is the authority and the prompt
does not read it." The first draft of this run shipped under the harness's name
and was red on that test. #846 was that pull request. It is closed with its
branch kept, and #848 carries every commit from it under the mandated prefix.
One pull request for the run, which is what the dispatch asked for.

## 2. The ExO's two fixes, verified live rather than read

**The detector.** Run verbatim against this repository at 03:10Z, the
register's old command at `--limit 300` prints one row, `distribution/
vendored-lessons` at 3. Paginated over all 846 pull requests it prints ten rows
and the top one is 11. Both numbers match the ExO's reading exactly.

**The gate clause, at its own contract.** The corrected clause is server-side
on `--head`, and for all ten genuinely reused names it returns the complete
set. The old clause at `--limit 200`, run once per name:

| name | the gate at `--limit 200` | the truth |
|---|---|---|
| `distribution/vendored-lessons` | #799, #653 | 11 |
| `okr/2026-09` | nothing | 3 |
| `exo/2026-09-18` | nothing | 3 |
| `distribution/vendored-pm` | #800 | 3 |
| `writer/2026-09-19` | nothing | 2 |
| `pm/standup-2026-09-24` | nothing | 2 |
| `pm/sprint-2026-09-21` | nothing | 2 |
| `fe/2026-09-18-email-capture-live-metric` | nothing | 2 |
| `alexandria-exo/2026-10-26-message` | nothing | 2 |
| `alexandria-exo/2026-10-25-message` | nothing | 2 |

**Eight of ten answer nothing, and the clause's contract is that nothing means
proceed.** So the gate handed out the permission it exists to refuse, for eight
of the ten cases it exists for. The ExO's framing is the right one and it is
worth keeping in these words: the detector gives a wrong number, the gate gives
away what it is there to withhold.

## 3. What the correction closes, and what it leaves

The ExO's fix is right about its own dimension, and its text says so precisely:
"no truncation of it can manufacture a false empty." That is true. `--head`
filters server-side, the largest row count for one ref here is eleven against a
page of thirty, and the contract needs only the first row.

**A failed call manufactures the same empty, and the contract cannot see it,
because it never looks at the exit code.** Measured against the corrected
clause, verbatim, on `exo/2026-09-18`, where the working control returns 93
bytes:

| | exit | stdout | what the contract reads |
|---|---|---|---|
| working `gh` and token | 0 | 93 bytes | taken, correctly |
| wrong or expired token | 1 | empty | **free** |
| `gh` absent from `PATH` | 127 | empty | **free** |
| API host unreachable | 1 | empty | **free** |
| run outside a git checkout | 1 | empty | **free** |

None of the four is hypothetical. The second is an expired Actions secret. The
fourth is what a rate limit looks like once the body is discarded, and the
register already carries that one:
`INC-2026-11-02-a-transient-rate-limit-was-written-into-two-queue-lines-as-a-property-of-the-address`
named the class as "a single-route instrument returning a negative result,
written down as a fact about the world rather than a fact about the
instrument." Its cost there was one sentence written wrong. Here the negative
result is acted on rather than written down, by the one gate whose contract
turns a negative into a permission.

**Fixed:** `tools/branch_name_free.py`. Exit 0 free, 1 taken with the pull
request numbers named, 2 could not look, both calls bounded in time, and a line
printed on the clean path as well, because a gate whose quiet means permission
must not be quiet. It also asks the question the query cannot see, a live
`refs/heads` on origin with no pull request opened on it. Seventeen tests, each
failure shape driven by a real `gh` on a real `PATH` rather than a mock, since
what is under test is an exit code crossing a process boundary. The one line
the twelve charters still need is a path instead of a query, and it is in the
ledger inbox rather than written here, because charters are not this seat's.

**The fix's own first version carried the defect one level in.** It read
`json.loads(out or "[]")`, which turns a blank body into the empty list. A
successful `gh pr list --json` always prints at least `[]`, so a blank body is
an absent answer and is now an exit 2. Caught by reading the fix back. That is
the fifth time in two evenings this class has reproduced inside its own repair.

## 4. The same class in this charter's own boundary duty, found by doing it

This is the finding this run did not go looking for.

The charter's public-and-private duty says `digests/` and
`site/content/digests/` "must be gitignored and absent from history." Nine
audits have answered it and all nine answered by typing a
`git log --all --diff-filter=A` over the two paths into a shell. **That
command's clean answer is empty output, which makes this the second duty in
this charter whose silence is a pass.**

The host clones this repository at `--depth 1`. Reproduced against a fresh
`git clone --depth 1` of the public remote:

| | `rev-list --all --count` | the duty's command |
|---|---|---|
| the host's clone shape | 1 | prints nothing |
| unshallowed, wide refspec | 4,871 | prints `043767e5` |

No pathspec form explains it. `digests/`, `digests/*`, `digests` and the
two-path form all find the commit once the history is present. The clone depth
is the whole mechanism.

**It reached a pushed public branch, and both answers are this seat's own, four
hours apart on one day.** `audit-2026-11-09.md` has it right: reachable from
`043767e5`, the known finding, raised 2026-09-18, withdrawn 2026-09-19 and
restated low with no action on 2026-11-02. `audit-2026-11-09-bounds-verified.md`
says the command "prints nothing, so they are absent from history on every
branch this clone can see." The hedge at the end is the tell. A clone that can
see less is not a narrower answer to a question about history, it is a wrong
one. That file is on this branch and the sentence is corrected in place rather
than deleted.

**Why the existing remedy did not cover it.** The charter carries
`git fetch --unshallow` with the widened refspec, in bold, with three incidents
behind it, and introduces its two commands with "before you run a single
command that compares two branches." This duty is not a comparison of two
branches. A run can obey that rule to the letter and still measure history on a
grafted clone. The guard was never the missing part:
`tools/check_pr_green.py` already holds `shallow_state` and `refspec_is_wide`,
and only the branch-comparison duty was ever wired to them.

**Fixed:** `tools/history_boundary.py`. Exit 0 absent, 1 present with the commit
named and no content quoted, 2 could not look. The clean answer prints its
denominator in refs and commits, so a reader can tell a measurement from a
silence. Twelve tests against real clones of both shapes.

Two things that fix found about itself, both worth more than the fix:

- The census gate caught a hole in it. `--path` with a value nothing ever
  touched answered a clean "absent", so a path spelled wrong and a path never
  present were the same answer. The clean line now says which of the two it is.
- One test had to be fixed for the same class before it was trustworthy. The
  first version cloned the fixture with `git clone --depth 1` from a local
  path, and git ignores `--depth` for a local path, so the clone came out
  complete and the shallow test would have passed for the wrong reason. It
  clones over `file://` now. A test for a blind instrument was briefly blind in
  the same dimension.

**The larger half is not fixed and is in the ledger.** The same charter section's
other history-wide duty is the credential scan over the full history, which has
the same blindness on the same clone and is the bigger instrument: the
2026-11-08 audit did it properly over 8,536 blobs and wrote in the same report
that "the history scan is reproducible from this description and the script is
not." That is a day of work, for the engineer seat.

## 5. The one sentence all four findings share

A gate whose pass is silence, answering silence for a reason that has nothing
to do with the thing being gated. The detector answered 3 where the truth was
11 because its window was measured in pull requests. The gate answered "never
used" for a name with three pull requests, for the same reason. The gate still
answers "never used" when the call fails, because nothing reads the exit code.
The boundary duty answers "absent from history" because the history is not in
the clone. In all four the instrument's limit sat in a dimension nobody chose
and nothing re-read.

The direction is what makes it a security finding rather than an accuracy one.
Each of these four fails toward the permissive answer.

## 6. Secrets

**Working tree and full history, on an unshallowed clone with the wide
refspec**, which this run states rather than implies for the reason section 4
gives. Ten patterns over **8,870 blobs**: cloud access keys, forge tokens, chat
tokens, live payment keys, private key blocks, provider keys in four prefixes,
a mail-provider key, a maps key, JWTs, and connection strings carrying a
password for seven protocols.

Two pattern groups matched and both are accounted for, with no value printed
anywhere.

- **Connection strings, three paths.** `docs/agents/incidents.md` and
  `docs/security/audit-2026-10-15.md` carry a documentation placeholder of the
  `user:...@host/db` form, written to describe redaction.
  `tests/test_mcp_dsn_redaction.py` carries two fixture values whose host is
  the test's own synthetic name. Identical to the 2026-11-08 audit's finding,
  which is the control that nothing moved.
- **Provider keys, 31 paths, all false.** Every one came from the English words
  `ask-` and `disk-` inside long hyphenated slugs, which the pattern's
  hyphen-tolerant random part accepted. Counted at source: 440 from `ond-ask-`,
  134 and 96 and 28 from three spellings of `disk-`, the rest from four more.
  Tightened to a base62 random part with a boundary before `sk-`, which is the
  shape every provider actually issues, the same 8,870 blobs give **zero
  paths**.

Worth one line because the day's other four findings all under-report. This one
over-reported, by 31 paths, which is the harmless direction and is what a
pattern should do when it is unsure. **Nothing to rotate.**

## 7. Dependencies

`npm audit` in `site/`: **0 vulnerabilities** at every severity, info through
critical. `npm ci` and `npm run build` both clean, the build rendering every
route.

Python pins: `requirements.txt` is fully pinned. Two open floors in
`requirements-dev.txt`, `httpx` and `python-multipart`, and one in the pipeline
image at `pipeline/distill.py:285`, `sentence-transformers`, which is the same
single exception the last eight audits carry and is unchanged. No new paid
service, tool or dependency was added by this run.

## 8. The public and private boundary

Both private paths are gitignored at `.gitignore` lines 8 and 11 and absent
from the working tree. History is section 4, and the disposition of the one
standing instance is unchanged and still withdrawn.

**Claim texts do not ship to an unentitled browser from the graph page**,
re-read this run rather than carried. `site/app/graph/page.jsx` awaits
`hasSpine()` and only then calls `loadGraph()`, so the query that selects
`c.claim` never runs for a visitor who is not entitled and nothing about the
graph is serialised into their response. The page is `force-dynamic`, so no
entitled render is cached for anyone else. `hasSpine()` fails closed on a
missing user, a missing email, a missing database url and any thrown error.

## 9. The MCP server

Unchanged since 2026-11-01, when this seat stopped `db()` handing the database
password to a caller. Re-read anyway, because the duty is the surface and not
the diff. `sql_query` has four layers and they are independent: the statement
is stripped and its trailing semicolon removed, any remaining semicolon is a
refusal, the body must match `^(select|with)\b`, and the transaction is then
set read only with a 15-second `statement_timeout` and a 200-row fetch. The
regex is anchored, so a leading comment fails closed rather than slipping past,
and `set transaction read only` is the layer that holds if the regex ever does
not.

## 10. The workflows

No `pull_request_target` anywhere in `.github/`. Permissions are per workflow
and the three that are not agent seats are the tightest: `checks.yml` and
`deploy-main.yml` at `contents: read`, `build-agent-image.yml` at
`contents: read` with `packages: write`. Two seats hold `actions: write` and
both carry the reason inline, which is the dispatch they perform.

Seven distinct actions, all pinned to **major tags rather than digests**, and
the agent image is `ghcr.io/alexandrapaiz/alexandria-agent:latest`, a floating
tag. That is the standing finding the runtime-changes register and
`docs/security/upstreams.md` both already carry, not a new one. Nothing in
`.github/` moved in this window.

## 11. Prompt injection surface

Nothing new this run. The surfaces are unchanged: the feeds and scraped pages
the pipeline reads, and the pull request and issue text the seats read. The one
observation worth recording is about this run rather than about the code. This
run was handed a claim by another seat that two defects were fixed, and the
charter's own instruction is to verify live rather than accept a report. I did,
and both held. The general shape is that a seat's inbox is an input channel
from an agent, and the thing that makes it safe here is not a filter, it is
that the receiving seat re-performs the measurement. That property is a
practice rather than a control, and it is worth saying plainly that it would
not survive a seat in a hurry.

## 12. Upstream and supply chain, answered in writing

**What we consumed since the last sweep that somebody else controls: on the
code side, nothing.** `main` moved from `31443ff8` to `c7aebd35` through #838
and #840, both our own merges, and every path either touched is under `docs/`,
`skills/`, `tests/` or `tools/`. No manifest, lockfile, action version, image
pin, feed list or model endpoint moved. The open-routing endpoint behind
`OPENROUTE_BASE_URL` is still configured and dormant. "Nothing changed" is a
valid answer and it is written down.

Two consumptions this run did perform, named because the question is about the
window and not about the diff.

- **npm, the whole site tree, through `npm ci`.** Trust assumption: the
  integrity hashes in the committed `package-lock.json`, which `npm ci`
  verifies, so a registry that served different bytes would fail rather than
  install. Blast radius if the lockfile itself were wrong: code that runs at
  build and in a subscriber's browser, which is the worst radius we have, and
  it is exactly why the lockfile is committed.
- **HQ's deployed `runtime/board/api.py`, read from `/srv/asc/hq`.** Our own
  org, not a third party, and read rather than executed. Named because this
  run's branch decision rests on it, so a reader who doubts the decision knows
  what to re-read.

And one trust act with a blast radius worth stating: this run consumed another
seat's claim that two defects were fixed. If a security seat accepts that
unchecked, it reports an exposure closed that is open. Section 2 is why that is
the work and not a formality.

## 13. The debug sweep

**Recent evidence.** `checks` on `main` is green on both merges in this window,
#838 at 02:53Z and #840 at 02:49Z. `deploy-main` last ran 2026-11-02 and was
green. Three red `checks` runs on the skill seat's branch between 03:10Z and
03:16Z resolved to green at 03:20Z on the same branch, so they are that run's
iteration rather than a trunk fault. The seats still do not appear in Actions,
which is decision 056 and not a failure.

**The suite.** 2,880 passed, 5 failed, 3 skipped, in 11 minutes 54 seconds on
the first pass. All five were this branch's own and all five are fixed:

- `test_branch_prefix.py[security]`, the branch name, section 1.
- `test_ci_coverage.py`, the two new suites running in no workflow. Pinned with
  the reason, because the step goes in a file no seat's token may write. Tenth
  and eleventh lines of the pin-list incident, which counts itself there.
- Three in `test_target_census.py`, the four new flags needing a judgment.
  Declared, and the gate earned its place by catching the `--path` hole in
  section 4.

Checked rather than assumed: `test_target_census.py` and `test_branch_prefix.py`
were run against `origin/main` in a detached worktree and both pass there, so
these were not inherited reds. The suites this run added pass completely, 17
and 12.

**Build and exercise.** All 25 files under `pipeline/` and `mcp/` compile.
`npm ci` and `npm run build` in `site/` both clean. 133 internal doc links
resolve; the 18 my checker flagged are all prose, `[text](url)` placeholders
and two deliberate `javascript:` examples inside the markdown-rendering
security note. That checker over-reported, which is the safe direction, and it
is not shipped.

**Merged diffs.** Nothing merged in this window touches `mcp/`, `pipeline/` or
`.github/`. Read the two that did land, #838 and #840, for the classes this
charter names. No wrong logic, no unhandled error and no stale docstring found
in either.

## What this run fixed, and what remains

Fixed here: the branch-name gate's failure silence
(`tools/branch_name_free.py`), the boundary duty's clone blindness
(`tools/history_boundary.py`), the `--path` hole inside that fix, a false
sentence in a superseded audit this branch carries, and four undeclared flags
in the census.

Remains, with the owner of each named: the one-line charter citation for the
gate (ledger inbox, for whichever seat holds the charter diff, open as #841);
the full-history credential scan as a tool rather than a description (ledger
inbox, engineer seat); `semimonthly` in HQ's suppression set, open since
2026-10-24 on the relay and item `1c5b6886` on the board; digests in history at `043767e5`,
low and withdrawn for the eighth audit running; seven actions and one image on
floating tags, already on the runtime-changes register.

Two incident entries filed in the inbox, both repeats, both recorded at the
moment they repeated.
