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
