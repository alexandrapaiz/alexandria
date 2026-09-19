# Runtime changes: smoke-test first, always

**Enforced at:** the engineer, frontend, security and ExO charters,
under "Check the register before you ship", before any edit to a
workflow, the image, a secret, a turn cap or a timeout.

Standing org law, proposed by the ExO agent 2026-09-19 on the owner's
question, evidenced by incidents 17 and 18 in
[incidents.md](incidents.md). It binds every seat and the chair. It
takes effect on the owner's merge.

## The law

**No change to the environment a seat runs in reaches a scheduled run
until a deliberate smoke test has proved it, on a throwaway branch,
against a written checklist.** The next cron is never the first
execution of new machinery.

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
