# The visual harness

Committed on 2026-10-07 so that each run of the frontend seat starts from a
harness that already refuses, rather than from a blank container and a
register entry it has to read first
(`INC-2026-10-07-stale-server-third-occurrence`).

This file exists because on 2026-10-15 a run rebuilt the start step by hand
and hit the stale server for the fourth time, with `serve.sh` sitting in this
directory the whole time. The script was not ignored on purpose. The run
listed this directory with a `*.mjs` glob, because every tool it knew about
was a `.mjs`, and a committed check that a run does not know to look for is
not meaningfully different from a check that was never committed. So: the
order of operations is written down here, where listing the directory finds
it.

## Start here

```bash
docs/design/harness/serve.sh          # kill, build, start, PROVE the server
```

Never start the server by hand. `serve.sh` is four checks, and three of them
have an incident behind them: it kills with a `ps` field match that cannot hit
its own argv, it reads the log for `EADDRINUSE` instead of trusting a
backgrounded exit code, it proves the listening process descends from the one
it started, and it proves the served stylesheet is the one on disk.

Environment is inherited, so anything the pages need goes in front of it:

```bash
LEFT_BEHIND_FIXTURE=/tmp/lb.json docs/design/harness/serve.sh
```

## Then

| Script | What it does |
|---|---|
| `shoot.mjs <out> <tag> [only]` | the sweep: every page at three viewports, plus the overflow, tap-target and opacity audit |
| `zoom.mjs <out> <spec-json>` | close looks at 1:1, element clips, scroll offsets, injected states, probes |
| `bench.mjs <out>` | reads the motion system off Elicit, Linear and Consensus |
| `morph.mjs <out>` | the home mark's machine, middle and book frames |
| `states.mjs <out>` | hover, focus and reduced-motion states |
| `ink.mjs` | decodes a PNG and reads pixel values, for when a frame looks like a defect and is not |
| `make-fixtures.mjs <repo-root>` | 45 DUMMY FIXTURE skills under `skills/fixture-*` (gitignored) |
| `make-left-behind-fixture.mjs <out.json>` | 50 DUMMY FIXTURE findings for the Left-Behind Index |

## The one contract that will bite you

`zoom.mjs` takes `eval` and `probe` as strings. Pass whatever form you like,
an expression, an arrow function or an IIFE, and the script calls it. Before
2026-10-15 it did not: a bare arrow function evaluated to a function object,
Playwright serialised it as `undefined`, nothing threw, and the run
photographed the state it had asked to change. Read a probe's output before
trusting a frame that was supposed to show an injected state
(`INC-2026-10-15-the-visual-harness-had-three-traps`).

## Two things the scripts cannot know

**Playwright.** The container bakes the browsers for the pin the charter
names, `1.49.1`. `site/package.json` currently asks for `^1.63.0`, which looks
for a browser build that is not in the container, so these scripts cannot be
run from `site/node_modules` until the two numbers agree. Ledger entry
2026-10-15. Until then, install the pin into a scratch directory outside the
repository and run the scripts from there.

**Clerk.** A `pk_test_*` publishable key makes `clerkMiddleware` issue a
dev-browser handshake, and every page becomes a photograph of a Clerk error
document that audits clean. `shoot.mjs` blocks it and fails loudly. Give the
server a production-shaped key instead, which skips that path, and let the
harness's own route blocking stop anything from leaving localhost.
