# The visual run's harness

Committed on 2026-10-07 because three incidents
(`INC-2026-09-23-phantom-production-bug`,
`INC-2026-09-24-stale-server-kill-noop` and
`INC-2026-10-07-stale-server-third-occurrence`) prescribed the same checks in
prose and none of them ever became code, so every run of this seat started
from a container with no memory and rebuilt a harness without them.

Run from the repository root, with the Playwright pin the charter names:

```bash
docs/design/harness/serve.sh                       # build, serve, prove the server is this build
node docs/design/harness/make-fixtures.mjs .       # 45 DUMMY FIXTURE skills, gitignored
node docs/design/harness/shoot.mjs out/ before     # 10 pages x 3 viewports, audited
node docs/design/harness/states.mjs out/           # reveal, morph, reduced motion
node docs/design/harness/morph.mjs out/            # the morph inside its own scroll window
node docs/design/harness/bench.mjs out/            # Elicit, Linear, Consensus
node docs/design/harness/ourmotion.mjs             # the same measurement turned on us
```

`npx playwright@1.49.1` exactly: the container's baked Chromium is build 1148
and any other version downloads its own.

## What each guard is for, and which failure wrote it

- **`serve.sh`'s kill, bind check and HASH MATCH.** A rebuild under a live
  server leaves the old one serving asset hashes the build replaced. Every
  chunk 400s, the page is unstyled and unhydrated, and curl still answers 200
  with a plausible byte count. Three occurrences.
- **`shoot.mjs` and `zoom.mjs` assert the page is ours before photographing
  it.** A placeholder `pk_test_` Clerk key makes `clerkMiddleware` issue a dev
  browser handshake, so the browser leaves the site on every navigation and
  thirty screenshots are photographs of a two-line JSON error document. That
  audit comes back perfectly clean, because an error page genuinely has no
  overflow, no low contrast and no small targets. A clean report is the
  symptom. Use a production-form key so the middleware treats the request as
  an ordinary signed-out visitor, and block every request leaving localhost.
- **`shoot.mjs` fails when every frame lands within 5% of the same size.**
  Uniform output across ten different pages is what identical renders look
  like and what no real set of pages ever looks like.
- **The touch viewports force `hover: none` and `pointer: coarse` through
  CDP.** Headless Chromium otherwise reports `hover: hover` inside a touch
  context, so every `@media (hover: none)` rule in the stylesheet goes
  untested and hover-revealed affordances read as content stranded at
  opacity 0.
- **`ink.mjs` reads actual pixels out of a PNG.** A screenshot is authority on
  whether something looks wrong and is not authority on why. Twice now a run
  has nearly filed the sticky nav as transparent; measured, the ink behind it
  is 247 to 255 of 255, which is a ghost at about 3%.
- **`make-fixtures.mjs` writes deliberately lumpy shapes.** Ban list entry 28:
  a layout judged at evenly sized demo data is not judged. Real data is one
  large cluster, a shoulder and a long tail of pairs.

Fixtures land at `skills/fixture-*`, which `.gitignore` carries for exactly
this. Delete them before finishing: `rm -rf skills/fixture-*`.
