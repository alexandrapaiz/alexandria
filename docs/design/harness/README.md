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

## Getting these to run at all (rewritten 2026-10-24, from a run that did)

The previous version of this section named two things the scripts cannot know
and gave a workaround for neither that still worked. Both are answered here,
and each answer was executed rather than reasoned about
(`INC-2026-10-24-the-visual-harness-was-rebuilt-from-scratch-for-the-second-time`).

**Clerk is solved in the script now.** `shoot.mjs` sets a `__clerk_db_jwt`
cookie on every context, which is what `clerkMiddleware` looks for before it
issues a dev-browser handshake, so the pages render and guard 1 still blocks
everything else. Nothing is validated and nobody is signed in, because the
redirect turns on the cookie's presence. The old advice, a production-shaped
publishable key, is worse: it needs a real key in the environment and reaches
the real Clerk, which guard 1 exists to prevent. If you write a new script in
this directory, copy the `addCookies` block or your frames will be photographs
of `{"code":"host_invalid"}` that audit clean.

**The browser is not solved and may need the whole dance.** What the run of
2026-10-24 found, which is not what the previous version of this file
described: `PLAYWRIGHT_BROWSERS_PATH` was unset, `~/.cache/ms-playwright` held
`chromium-1248`, which matches neither `site/package.json`'s `^1.63.0` nor the
charter's `1.49.1`, and that Chromium would not start at all for want of ATK,
Pango, Cairo and GBM. Ask the one question first, because it answers all of
this in a second:

```bash
~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome --version
```

If it prints a version, point `executablePath` at it. If it prints a missing
`.so`, the image has no browser libraries and this worked, with no root:

```bash
mkdir -p /tmp/ptdeps && cd /tmp/ptdeps
apt-get install --print-uris -y libasound2t64 libatk-bridge2.0-0t64   libatk1.0-0t64 libatspi2.0-0t64 libcairo2 libcups2t64 libdbus-1-3 libdrm2   libgbm1 libglib2.0-0t64 libnspr4 libnss3 libpango-1.0-0 libpangocairo-1.0-0   libx11-6 libxcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3   libxkbcommon0 libxrandr2 libexpat1 libxcursor1 libxi6 libxtst6   2>/dev/null | grep -oP "(?<=')http[^']+" > urls.txt
xargs -n1 -P8 curl -sSLO < urls.txt
for f in *.deb; do dpkg -x "$f" /tmp/ptroot; done
export LD_LIBRARY_PATH=/tmp/ptroot/usr/lib/$(uname -m)-linux-gnu
```

Then, if the cached revision does not match the pin, symlink rather than
download: `ln -sfn ~/.cache/ms-playwright/chromium-1248 ~/.cache/ms-playwright/chromium-1243`. A newer Chromium driven by an older
Playwright is fine over CDP; that is how the frames of 2026-10-24 were taken.
None of this belongs in the repository and none of it was committed. It is a
Dockerfile question and it is in the ledger as one.

**One more thing no incident had recorded.** These scripts `import { chromium }
from "playwright"`, and ESM resolves that from the SCRIPT's directory, not the
working directory, so running them in place can never see `site/node_modules`.
Copy them out and link the modules in:

```bash
mkdir -p /tmp/harness && cp docs/design/harness/*.mjs /tmp/harness/
ln -sfn "$PWD/site/node_modules" /tmp/harness/node_modules
node /tmp/harness/shoot.mjs /tmp/shots after issue
```

## Guard 3 and the `only` filter

`shoot.mjs`'s third guard fails a sweep whose frames are all within 5% of one
size, because two different pages rendering to the same size are the same
render. Until 2026-10-24 it computed that over every frame in the report, so a
run with `only` set, which is one page at three viewports, failed with three
correct frames on disk: full-page shots of the same article reflowed to three
widths weigh about the same, measured at 3.8%. The guard now asks nothing when
the sweep covers one page and says so. It still fires for two, verified at
79.6% spread across the issue and mission pages.
