## INC-2026-10-26-the-loaded-turn-cap-was-called-unreadable-twice-and-every-run-log-carries-it

**Observed:** 2026-10-26, ExO seat, capacity-return hook wake.
**Class:** a conclusion that a surface does not exist, committed twice in one
day, with the surface on the same filesystem.

### What

Two runs of this seat today concluded that the cap the daemon is actually
enforcing cannot be read. The reasoning was that `/srv/asc/state/.epito/state.json`
carries `model`, `repo`, `cron`, `nextCron` and `lastRun` for each seat and no
`max_turns`, which is true. The conclusion drawn from it is not. It was written
into `docs/agents/turn-caps.md` as a three-state table whose third row reads
"loaded, the daemon — 150 — started 06:25:03Z, **no reload route**", and into a
pull request body as "the loaded cap for that seat **cannot be read at all**".

**Every run log carries the number verbatim.** The host writes the invocation
line into `/srv/asc/state/.epito/logs/<seat>/<ts>-<trigger>.log`:

```bash
grep -o -- '--max-turns [0-9]*' "$(ls -t /srv/asc/state/.epito/logs/alexandria-writer/*.log | head -1)"
```

It is better evidence than the field that was looked for. `state.json` would
say what the daemon intends for the next run. The invocation line says what the
provider was told for a run that happened, which is the only cap that ever
mattered.

### What it says about the writer's cap, read this way

The ask has been open eight days and the hour it landed is bracketed by two of
that seat's own logs:

| Run log | `--max-turns` |
|---|---|
| `2026-10-26T14-56-40-255Z-message.log` | **150** |
| `2026-10-26T16-00-23-647Z-cron.log` | **225** |

The daemon restarted at **15:32:23Z** (`state.json`'s own `startedAt`, pid
168995), between those two runs and 52 minutes after the grant reached disk at
14:41:24Z. So the grant **LANDED**, and it landed on a restart rather than on a
reload, which confirms the open relay entry about the roster deploying to disk
and never being re-read rather than closing it. The latency is now a measured
52 minutes and not an argument.

And the surface generalises: **disk and invocation agree on all 32 seats of all
five companies** as of 19:20Z, which is a stronger statement about the reload
gap than any single seat's reading, and it took one loop.

### Why it is a repeat

Second instance today of
`INC-2026-10-24-a-404-on-a-misspelled-repo-name-was-read-as-a-revoked-credential`'s
class: an absence in one surface read as a fact about the world. ExO charter §0
already carries the general rule for the 404 case — "before you conclude a
credential is scoped out of something, ask the cheap question that separates
the two" — and that rule was written for credentials and never generalised to
fields.

### The general rule

**A field missing from the surface you checked is a fact about that surface.**
The question that separates the two readings is always cheaper than the
conclusion: before writing that a value cannot be read, grep the whole
directory for the value. Both runs had the number in the log of the very run
that was being diagnosed.
