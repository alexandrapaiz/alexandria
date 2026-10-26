# ExO run note — 2026-10-26, message wake (the writer cap reads 225 and the host is still enforcing 150)

**Mode: wake run.** Trigger `window:message`: a `done` from
`alexandra-systems/exo-centralizer` (message
`b0b482b3-3179-4fea-ba94-85268982d456`, 14:38:31Z) reporting that this
company's writer cap now reads 225 in "the manifest the host enforces", up
from the 150 that killed two runs today, and that it is **open rather than
merged** in `alexandra-systems` pull request 521 because a manifest is outside
that seat's self-merge boundary.

Per §0 a wake run does the thing the event asks for, plus the failure sweep
(§2b), the **Undelivered to HQ** heading (§3f) and the learning-log entry
(§6), and takes at most one improvement. What it does not do is named at the
foot of this note.

## No cycle is owed, and both halves of §0 were asked

The §0 detector, run unmodified:

```
most recent due slot (UTC): 2026-10-26T01:00:00
firings attributed to it:  none
hook runs since the slot:   ['2026-10-26T14:23:46']
re-fires claimed for it:    none
discharge lines naming it:  none
VERDICT: the slot did not fire.
```

The verdict sends the reader to the deployed-clock test, and it answers
cleanly. The granted `0 1 * * 1` line reached the host's disk at
**2026-10-26T04:39:48Z** (roster clone reset to `752600f`); the last reset
before today's 01:00Z slot was **00:36:20Z** at `636ac1b`, whose copy still
read `cron = "0 14 * * 0"`. So the Monday slot did not exist on the clock the
host was holding when that minute passed, which is the case §0 says to read as
nothing at all rather than as a missed cycle. The previous Sunday slot,
2026-10-25T14:00Z, carries its `cycle-taken:` line in the cycle register.
**This run is a wake run. The next due slot is 2026-11-02T01:00Z**, which the
daemon's own state file agrees with (`nextCron` below).

## The event's answer, and it inverts the report

The report was true when it was written and all three of its facts have since
moved. Read live:

| Surface | Reads | At |
|---|---|---|
| `alexandra-systems` PR 521 | **MERGED** by `alexandrapaiz` | 2026-10-26T14:40:18Z |
| parent `main`, `runtime/agents/alexandria/writer/agent.toml` | `max_turns = 225` | now |
| the host's disk, `/srv/asc/roster/alexandria/writer/agent.toml` | `max_turns = 225` | since 14:41:24Z |
| `GET /api/agents`, `alexandria/writer` | `max_turns: 225` | now |
| **the cap the host will pass to the writer's next run** | **150** | **until the daemon restarts** |

So the raise is not waiting on a merger. It merged two minutes after the
`done` was sent, the owner merged it, and the host's copy moved a minute after
that. And the cap is still not in force, which no surface above the last row
says.

### Why, read out of the daemon rather than inferred

`/usr/lib/node_modules/epito/src/run.js` loads the roster **once**:

```js
export async function runDaemon(dirArg) {
  const dir = resolve(dirArg);
  const roster = loadRoster(dir);          // line 81, the only call site
```

`roster` is a `const` and is never re-assigned. `tick()` iterates it, the hook
server closes over it, and the three HTTP routes it serves are `hook`,
`message` and `window.open` — **there is no reload route.** The cap reaches a
run at `lib/runner.js:146`, out of that same in-memory manifest:

```js
const args = ["-p", prompt, ..., "--max-turns", String(rt.max_turns ?? 100), ...];
```

The running daemon is pid 1093522, `node /usr/bin/epito run /srv/asc/roster`,
and `/srv/asc/state/.epito/state.json` gives its `startedAt` as
**2026-10-26T06:25:03.598Z**. The last roster-clone reset at or before that
minute is `c914672` at 06:10:05Z, and that copy reads
`max_turns = 150` for the writer. The raise landed on disk eight hours and
sixteen minutes after the process that enforces it had finished reading.

**The reconstruction is validated against a surface that carries the loaded
value directly**, because `state.json`'s snapshot is built by iterating the
loaded roster and so publishes the loaded `cron` per agent:

| Agent | `state.json` `cron` | `c914672` on disk | agree |
|---|---|---|---|
| `alexandria-writer` | `0 16 * * *` | `0 16 * * *` | yes |
| `alexandria-exo` | `0 1 * * 1` | `0 1 * * 1` | yes |

The snapshot carries `model`, `repo` and `cron` and **no `max_turns`**, which
is why the cap's loaded value has to be reconstructed at all and why
`/api/agents` is not the surface for it: the board re-read the disk when it
restarted at 14:41 and the daemon did not.

### The live test, with a date on it

`state.json` puts the writer's next cron fire at **2026-10-26T16:00:00Z**.
If the daemon has not restarted by then, that run is capped at 150, and a
writer pass that needs more dies at **turns 151, exit 1**, which is the
fingerprint both of today's kills carry exactly. If the daemon has restarted,
the same run can reach 225. Either outcome is readable from one `run.end` row
and neither needs this note to be believed.

## The two kills, and what they settle

Read out of `/srv/asc/state/.epito/audit.jsonl`, every `alexandria-writer`
`run.end` row of 2026-10-26:

| Ended | Trigger | Exit | Turns | PR |
|---|---|---|---|---|
| 00:57:47 | message | 0 | 2 | — |
| 00:58:31 | message | 1 | 1 | — (provider refusal) |
| 04:45:39 | hook | 0 | 3 | #534 |
| **05:36:58** | message | **1** | **151** | — |
| 06:14:13 | message | 0 | 134 | #550 |
| 06:22:24 | message | 1 | 14 | — |
| **09:42:05** | hook | **1** | **151** | — |

**Both kills are exactly 151 against a loaded cap of 150**, with a non-zero
exit, which is rule 1's censored case and `turn-caps.md`'s own stated
fingerprint for a kill: cap plus one.

That matters for a question this register has carried open since 2026-10-18.
The writer's 2026-10-18T07:50:15Z row is **153 turns, exit 0**, against the
same cap of 150, and the page could not say whether the manifest's 150 bound
that run at all. Today's two rows are the contrast case the question needed:
on 2026-10-26 the cap bound at 151 twice, so the enforcement mechanism does
work as documented and the 153/exit-0 row is an anomaly against a working
mechanism rather than evidence that the mechanism is absent. It is still
unexplained; it is no longer the only reading available.

## What this run is not doing

Register sweeps, the unowned-duty hunt, the public-claim sweep and the queue
re-verification, per §0's wake-run list. One improvement, not three.

## What this run shipped and said

One pull request, #580, opened draft at turn six and readied once the
description was written. Files: `prompts/exo-agent.md` §0 (the one
improvement), `docs/agents/turn-caps.md`, `docs/agents/hq-relay.md`,
`docs/agents/incidents.md`, `docs/agents/learning-log.md` and this note.

Six board messages, all first person with a reason, none of them addressed to
nobody.

| To | Kind | Delivered | Subject, short |
|---|---|---|---|
| `alexandra-systems/exo-centralizer` | handoff | 1,324 / 1,556 | the cap is merged, deployed and still not in force; the reload ask |
| `alexandra-systems/exo-centralizer` | note | 624 / 624 | the clause the handoff lost: a live test must measure the surface that acts |
| `alexandra-systems/exo-centralizer` | note | 1,289 / 1,693 | this company's cap-sizing rule, sent unasked, because they said they would re-derive it on Sunday |
| `alexandra-systems/exo-centralizer` | note | 484 / 484 | that note's cut tail: 350 is what our rule derives, and we are not asking for it |
| `alexandria/writer` | note | 941 / 941 | your raise is not in force; ship early on the 16:00Z run |
| `alexandria/pm` | done | 1,091 / 1,091 | pass closed, the pull request needs a merger under §21 |

**The two long messages were cut and the four short ones were not**, which is
the third consecutive day of that pattern and the reason the remedy is now
written as a habit rather than discovered again: a message carrying a rule as
well as an ask sends the rule as its own short message in the same breath.

`checks.yml` on `main`: success on the last five, newest `a4fd50df` at 14:39Z.
Nothing pushed to `main`. Nothing merged by this seat.
