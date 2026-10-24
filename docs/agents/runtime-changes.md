# Runtime changes: smoke-test first, always

**Enforced at:** the engineer, frontend, security and ExO charters,
under "Check the register before you ship", before any edit to a
workflow, the image, a secret, a turn cap, a timeout, or the model or
provider a scheduled job calls. For the press, also enforced by the
shell: the deploy command's `&&` chain, which is the only gate in this
file that a seat cannot forget to read.

Standing org law, proposed by the ExO agent 2026-09-19 on the owner's
question, evidenced by incidents 17 and 18 in
[incidents.md](incidents.md). It binds every seat and the chair. It
takes effect on the owner's merge.

## The law

**No change to the environment a seat runs in reaches a scheduled run
until a deliberate smoke test has proved it, on a throwaway branch,
against a written checklist.** The next cron is never the first
execution of new machinery.

## What a runtime is

Amended 2026-09-24 after INC-2026-09-24-press-provider-migration, where
this law was on the books, known to the seat that broke it, and did not
fire, because its own scope excluded the change.

A runtime is anything scheduled that the org depends on and that no
human watches while it executes. That is the container the seats run in.
It is also **the press**, which is a Modal cron, the daily corpus crons,
the site deploy, and the MCP server. The original wording said "the
environment a seat runs in", and a reader applying it honestly concluded
that a Modal function was out of scope. It is not. If it runs on a
schedule and its first execution after a change is unattended, this law
binds it.

## What counts as a runtime change

Not what an agent is asked to do. What it executes inside. If the edit
is to a workflow file, to the image, or to a secret a run depends on, it
is a runtime change:

- the container image, its base, its baked tools, its user or uid
- `container:`, `options:`, `credentials:`, `runs-on`
- the action version (`anthropics/claude-code-action@v1` moving)
- `claude_args`: the model flag, `--permission-mode`, `--max-turns`
- `timeout-minutes`, `permissions:`, cron schedules
- the checkout token, and any new secret a run reads
- a new seat's workflow, on its first run

Turn caps and timeouts are on this list deliberately. They look like
numbers rather than machinery, and incident 15 is a day of six failures
caused by numbers.

**A model or provider change is a runtime change** (added 2026-09-24).
This is the clause the law was missing. It covers:

- the model id a scheduled job calls, including a move within one family
- the provider, the base URL, and the API key a scheduled job reads
- the token reservation, the client timeout, and the retry policy around
  a model call
- the prompt, when the change moves the request across a provider limit

The argument for it is one incident. Moving the press from Groq to Kimi
changed no workflow file, no image and no container setting, and it
produced four distinct production failures in one evening. Every one was
an integration property that only a real call reveals: a reasoning model
spends its output budget thinking before it writes, a call that takes
minutes needs a timeout measured in minutes, a call that takes minutes
must not hold a database transaction open, and a provider swap touches
the owner-facing alarm prose that taste governs. A provider is an
environment. Swapping one is the largest runtime change the org makes,
and it was the only one this law did not cover.

## The audit's questions were all about the past, and a guard lives in the present

Added 2026-09-30, after `INC-2026-09-30-the-guard-went-red-and-nobody-read-it`.

Every question this law told an auditor to ask was a question about
history. Did a merged pull request explain the commit. Was there a smoke
run behind it. Was there a rehearsal. All three are answered by reading
the record of the day the change landed, and all three can be answered
correctly while the thing the change broke is still broken.

That is not a hypothetical distinction. Two commits on the list above
went in on 2026-09-23 and 2026-09-24:

- `281d0af` raised the press's output reservation from 6,000 tokens to
  24,000, which is a token reservation and is named in this file.
- `69a9e7f` stopped the press honouring a short `retry-after` and gave it
  its own schedule, which is a retry policy and is also named in this
  file.

Both were right. Both are still right. Each of them left a guard in
`tests/test_press_resilience.py` asserting the behaviour it had just
replaced, and the second one was written the same day this file gained
the clause that covers it. The guards went red on the day of the change
and stayed red for six days. One of the two was the cost check, whose own
comment says that if the number drifts "finance's books are wrong and
this is where it should surface". It surfaced $0.1628 an issue against
ADR-32's budgeted $0.05, immediately, correctly, and into nothing.

So the audit asks a fourth question, and it is the only one that is not
about the day the change landed.

> **Is the guard that covers this change green right now?**

Run it. Do not look for the run that cleared it, because clearing is a
claim about a past state and this question is about the present one.

```bash
gh run list --workflow=checks.yml --branch=main --limit 5 \
  --json conclusion,headSha,createdAt
```

A `failure` in that list is a finding on its own, before you have read a
single commit, and it is a finding whoever is auditing owns reporting
even when fixing it belongs to another seat.

**Why the other three questions could not have caught it.** Both commits
were direct pushes to `main` by the owner, which is hers to do. There was
therefore no pull request to explain them and no PR check to fail. And
`checks.yml` did not gain its `push: branches: [main]` trigger until
2026-09-29, five days later, so for the whole window the only gate the
repository had was scoped to a channel the changes did not use. A gate
that runs on pull requests only is not a gate on a repository whose owner
commits directly, and the seats could not see this because seats only
ever open pull requests.

**The second-order cost, which is larger than the first.** Once `main` is
red, every open pull request inherits the failure through its own merge
check, so every seat's run ends with a red tick it did not cause. On
2026-09-30 that was 19 of 28 failed runs in a day, all of them the same
two inherited assertions, and one skill pull request whose third failing
step was genuinely its own and sat unread between two that were not. A
red `main` does not cost one bug. It costs the signal on every branch at
once, and the seat that most needs to see its own failure is the seat
least able to.

## The ladder

This is the sequence the chair actually ran on 2026-09-19, written down
so it is repeatable rather than remembered.

1. **Build it in isolation.** Get the image or the config to build and
   publish on its own. A build that fails here has cost nothing.
2. **Smoke one seat, on a throwaway branch, with the narrowest possible
   task.** Dispatch by hand, never by cron. The task is to verify the
   environment, not to do the seat's job. Pick the seat with the most
   demanding environment, because it catches the most: the frontend seat
   was the right choice here, since it is the only one that needs a
   browser.
3. **Fix, rebuild, repeat until the checklist is green.** Two rounds is
   normal. Both of this migration's bugs were found in this step, four
   minutes apart.
4. **One real dispatch of that seat, on real work.** A smoke test proves
   the environment starts. It does not prove the seat can still work.
5. **Then roll to the remaining seats**, and only then let a cron fire.

## The checklist a smoke run must print

Verbatim output, not an agent's assurance that it looks fine. Incident 8
is the standing reason: judge a run by its artifacts, never by its
conclusion.

```bash
id -u && id -g                      # matches the workspace owner
touch "$GITHUB_WORKSPACE/.probe" && rm "$GITHUB_WORKSPACE/.probe"
git --version && gh --version && node --version && python3 --version
gh auth status                      # the token is present and scoped
git push origin HEAD:refs/heads/<throwaway>   # shipping actually works
gh pr create --draft                # and so does the PR channel
```

Plus one line per thing the change was supposed to buy. For the
containerization that was Chromium launching from the image with no
download, which is the entire point of baking it.

Close the throwaway PR when the checklist is green. It is a receipt, not
a contribution.

## Clearing a change is itself a claim, so name the run that cleared it

Added 2026-09-27, after `INC-2026-09-27-post-run-step-audited-from-inside`.
Two clauses, and each one cost the org something.

**1. A post-run step cannot be cleared from inside a run.** Anything that
executes after a seat's agent step has, by construction, not yet run in
the job doing the auditing. `job.status` reads `success` in the log of a
run that is about to fail at its own last step. So the verdict on a
change to a post-run step comes from `gh run view` on a job that has
already concluded, and never from the run you are in.

**2. And from a job of the same kind as the one at risk.** Reading a
completed run is not enough if it is the wrong runtime. The engineer and
the frontend seats run in `container:` and get `sh -e {0}`, where
`/bin/sh` is dash, and the other ten run on the host and get
`bash -e {0}`.
The step that broke five engineer runs was cleared against a completed
`okr-agent` run, read correctly, which could never have exercised the
fault. Ten of twelve workflows would have cleared it forever.

The mechanical form is one line, and it belongs in whatever writes the
verdict:

```bash
# which runtimes does this change actually reach?
grep -l "container:" .github/workflows/agent-*.yml   # these get sh, the rest get bash
```

**So never write "it is working" without a job id of the right kind
beside it.** A verdict with no run behind it is the same defect as a
runtime change with no smoke run behind it, one level up, and it is
harder to see because it reads as diligence.

## The ladder for a provider or model change

The five-step ladder above is written for the container, where the thing
under test is whether the environment starts. A provider change is a
different shape. The environment always starts. What breaks is the first
real call, and nothing short of a real call finds it.

So a provider or model change gets three gates, in this order, and all
three run before `modal deploy`.

1. **The budget guard.** Does the request fit? `python3
   pipeline/budget.py`, locally, no key needed. Incident 22.
2. **The availability check.** Does the model exist? `modal run
   pipeline/weekly.py::preflight`, which asks the provider's `/models`
   endpoint with the real key. Incident 24.
3. **The rehearsal print.** Does one real call actually work, end to
   end, on the real payload? This is the new gate and it is the one that
   would have caught all four failures of
   INC-2026-09-24-press-provider-migration.

The first two ask questions about the request. Only the third exercises
the provider, and the four failures that produced this clause were every
one of them on the third question. A press that fits and exists and
cannot print is exactly what the org shipped on 2026-09-24.

### What a rehearsal print is

A rehearsal is preflight plus one real model call against the real
payload, and it differs from the scheduled run in exactly two places.

- **It writes to a scratch row, never to `digests`.** The real table is
  the database of record and a rehearsal must not be able to overwrite a
  week the readers can see.
- **It sends nothing.** No subscriber email. It prints every subject
  line it would have sent, success and alarm, so taste can be read
  without a message leaving the building.

Everything else is real: the real prompt, the real gathered payload, the
real provider, the real key, the real token reservation, the real
timeout, the real connection handling. A rehearsal that mocks the model
call tests nothing, because the model call is the entire surface under
test.

The specification for the press's rehearsal, written for the engineer to
build, is `docs/agents/press-rehearsal.md`.

### Who runs it, and when

The chair, by hand, before the deploy that installs the schedule. Not
cron, not CI, and not the seat that wrote the change. The rehearsal is
the last thing a human does before the machinery becomes unattended,
which is the same position step 4 of the container ladder holds.

Run it again when any of the three gates' inputs move: a new model id, a
new provider, a new reservation or timeout, or a prompt change large
enough to move the budget arithmetic.

## The gate has to be in the command, not in the charter

Added 2026-09-24, and it is the harder half of this law.

INC-2026-09-24-press-provider-migration is the fourth time the org has
met the class named in the learning log as **recording is not
enforcing**. The law existed. The chair knew it. It still did not fire.
Writing this amendment does not fix that, and pretending otherwise is
how the org gets a fifth occurrence.

The honest enforcement answer for the press is small and mechanical:
**the deploy command itself refuses without a rehearsal receipt.** The
chair already runs an `&&` chain, and an `&&` chain is already a gate:

```bash
python3 pipeline/budget.py   && modal run pipeline/weekly.py::preflight   && modal deploy pipeline/weekly.py
```

Two of the three questions are already enforced there, by the shell,
with no charter text involved and no way to forget. The third is missing
only because nobody added the link:

```bash
python3 pipeline/budget.py   && modal run pipeline/weekly.py::preflight   && modal run pipeline/weekly.py::rehearse   && modal deploy pipeline/weekly.py
```

That is the whole fix. A rehearsal that raises stops the chain at the
`&&`, the same way a failed preflight already does, and the deploy never
happens. `docs/agents/press-rehearsal.md` adds the receipt half: the
rehearsal writes its scratch row with the model id and the prompt hash,
and `rehearse` refuses to pass if the last receipt does not match what
is about to be deployed. A receipt from a different model is not a
receipt.

The general rule to take from this, for every register in
`docs/agents/registers.md` still marked GAP: **a rule enforced by a
sentence in a charter is enforced at the reliability of a model reading
a file, and a rule enforced by a link in a command is enforced at the
reliability of a shell.** Where a command already exists, put the gate
in the command. The charter line then documents the gate rather than
being it.

## Why this is law rather than advice

The two failures it caught (incidents 17 and 18) cost two red runs and
one 12-turn verification, and neither reached a seat doing real work.
The same two bugs found by a Wednesday morning cron would have taken a
seat out of service until a human read an eight-word stderr line.

The asymmetry is the argument. A smoke test costs minutes and is paid
every time. A runtime failure in production costs a seat's whole cycle
and is paid only sometimes, which is exactly the shape of risk an
organization talks itself out of insuring against.

## Who enforces it

The ExO agent, in step 2 of its charter. Each run diffs
`.github/workflows/` and `.github/docker/` against the previous run's
tree. Any runtime change with no smoke run behind it in `gh run list` is
a finding, recorded in the register whether or not it happened to work.

That diff had a hole in it until 2026-09-24, and the hole is why this
seat did not catch the press migration either. A provider change lands
in `pipeline/`, not in `.github/`, so it was invisible to the only audit
that enforces this law. The ExO charter's step 2 now diffs the delivery
runtimes as well, which means `pipeline/weekly.py`, `pipeline/budget.py`
and the daily crons, and asks the same two questions of every commit
that touches a model id, a provider, a reservation or a timeout.

The engineer's daily §0 check is the faster half of the same duty, and
its command is scoped to `.github/` for the same reason. It now covers
the delivery runtimes too.

## Amendment 2026-10-24: the observability runtime is a runtime, and its retirement went unrecorded for a day

`## What a runtime is` above names the container, the press, the corpus
crons, the site deploy and the MCP server. It does not name the thing that
reports on all five. That omission has now cost a record.

**What happened.** Langfuse, which held every seat's run trace, was stopped
on 2026-10-23 because `langfuse-clickhouse-1` filled the host's only disk
under Docker's default `json-file` driver with no `max-size`, and Postgres
then hit `PANIC: could not write to file ... No space left on device`. The
owner's standing condition, recorded the same day, is that Langfuse stays
stopped until it is rebuilt with a disk budget.

**Where that is written down.** Upstream, in the vendored
`docs/standards/lessons.md`, as part of an alexandra-systems incident. In
this repository, as of 2026-10-24 16:30Z, nowhere at all. Not here, not in
`docs/decisions.md`, not in `docs/agents/incidents.md`, not in
`docs/agents/registers.md`, and not in `docs/agents/delivery-health.md`. The
only local trace was three lines written the same morning into
`docs/agents/exo-loop.md`, on an unmerged branch.

**What still names it as live.** Twelve files. Every
`.github/workflows/agent-*.yml` exports `OTEL_EXPORTER_OTLP_ENDPOINT` to
`${{ secrets.LANGFUSE_HOST }}/api/public/otel`, sets
`langfuse.environment=alexandria` in `OTEL_RESOURCE_ATTRIBUTES`, and runs a
step called "Trace this run to Langfuse" against `LANGFUSE_PUBLIC_KEY` and
`LANGFUSE_SECRET_KEY`. And the vendored `docs/standards/pm.md` still
instructs every standup to read "the run's trace in Langfuse (environment =
this company, session = the run id) when the failure is inside the model
step", which is a step no PM can perform.

**What it cost, measured.** `GET /api/scorecard` answers with a `sources`
block saying `trace_store` is retired and `nothing is listening on
127.0.0.1:8123`, and with a `columns` block mapping five of its columns to
that source: `runs`, `tool_errors`, `tool_errors_per_run`,
`runs_with_errors` and `median_minutes`. The API degrades honestly, which is
why this was findable at all. But five columns of the org's own scorecard
have had no source for a day, and the one rule that reads them,
`docs/standards/lessons.md` L-A81's "the company measured merges per run,
hours to main, runs that shipped nothing and tool errors per run", is
unexecutable on the last of those four.

**The amendment.** A runtime is also **the observability runtime**, meaning
anything that records what the other runtimes did. Stopping one is a runtime
change and takes the same three questions as starting one. The reason it
belongs here rather than in a monitoring doc is the asymmetry this page
already argues from: when a runtime fails, the org finds out loudly. When
the thing that watches the runtimes fails, every number downstream of it
keeps rendering, and the only loud signal is the one the scorecard API chose
to emit about itself. **An observability outage is the one runtime failure
whose symptom is silence.**

**And the rule that falls out of the record being upstream.** The retirement
was recorded correctly, in the parent's own register, by the company that
owned the disk. It was not relayed down. `docs/agents/cross-repo-law.md`
covers a parent decision arriving as a commit or an ADR. This one arrived as
a line inside a vendored file that twelve local workflows contradict, which
is the §3f reading that `grep -rn "HQ Incident 5" docs/` was written for,
pointed the other way: **a parent record that lands in a vendored copy is
filed and not delivered, and a seat reading the local machinery sees only
the contradiction.** So when a vendored standard changes under a local
runtime, the local register gets the entry too, written by whoever notices.

## Amendment 2026-10-24: the text the host attaches to a wake is a runtime, and ours names a tool we do not have

`## What a runtime is` above names the container, the press, the corpus
crons, the site deploy, the MCP server and, since this morning, the thing
that reports on all five. It does not name the thing that **starts** them.
Every seat run in this company now begins with text the host composed, and
until this amendment no clause here put a single word of that text in scope.

**What happened.** `alexandrapaiz/alexandra-systems`,
`runtime/board/standing.py` appends a standing block to every wake the bus
delivers. Its `strays()` branch tells a merging seat to read other seats'
orphaned drafts with `tools/check-draft-prs.sh --repo alexandrapaiz/<repo>`,
with the repository filled in from a five-company map, and then says "the act
is yours under the merge rule: ready it and merge it". That script exists in
the repository the module lives in and has never existed in this one. The PM
seat was told to run it seven times on 2026-10-24, checked for it seven
times, found nothing seven times, and wrote the refusal down seven times. See
`INC-2026-10-24-the-fabricated-tool-has-a-source-and-it-is-our-own-standing-block`.

**Why none of this law's four questions could fire.** A wake is not a commit
here. There is no local pull request to explain it, no local check to go red,
no `pipeline/` diff to catch it, and the guard-is-green question has nothing
to run. The change is authored in another repository, it reaches this one
without touching a file in it, and the surface it changes is read by a seat
before that seat has read anything else. **That is strictly less visible than
the press provider migration this law was amended for in September**, which
at least left a commit somewhere a seat could `git log`.

**The amendment.** A runtime is also **the wake layer**, meaning anything
that composes the instructions a seat receives before the seat has read a
file. A change to the wake text, the standing block, the launcher prompt or
the operator notice that rides on them is a runtime change, and it takes the
same three questions. Since this repository cannot ask them of a change
authored upstream, the clause that does the work is the one below.

**Where the audit actually lives, because it cannot live in a smoke run.**
The ExO seat reads the generator rather than the generated text, once a run,
and asks two questions of it:

```bash
# the generator, and every tool path it tells a seat to run
gh api repos/alexandrapaiz/alexandra-systems/contents/runtime/board/standing.py \
  --jq .content | base64 -d | grep -nE 'tools/|\.sh|\.py'
```

1. **Does every path it names resolve in this repository?** A path in
   portfolio-wide text is true in at most one repository unless something
   checks. `find . -path './.git' -prune -o -iname '<the basename>' -print`
   settles it in one command.
2. **Does it assert an authority this repository's law does not grant?** The
   block's own docstring says it "never acts" and is "additive", and the
   sentence above hands a seat another seat's draft under a rule that, here,
   does not reach it. A runtime that describes a permission is making a claim
   about law, and the claim is audited where it lands.

**The rule that generalizes, and it is the reason this is law rather than a
note.** Everything else this file governs fails loudly or leaves a trace in
this repository. The wake layer does neither: a defective sentence arrives as
an instruction, is obeyed or declined by judgment, and leaves no artifact
unless the declining seat chooses to write one. **The PM seat chose to, seven
times, and that is the only reason this was findable at all.** So the
companion duty is in `docs/agents/unowned-duties.md` rather than here: a seat
that declines an instruction in its own wake says so in its pull request, and
a decline that repeats goes in the incident register under the standing rule
like anything else.
