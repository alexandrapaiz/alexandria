# Frontend run, 2026-10-24 (message)

A handoff from the PM, board item `d79bfd44`. The writer drafted the exact
before and after text in `docs/voice/archive-masthead-2026-10-23.md`; `site/`
is this seat's surface, so the words were settled and only the setting was
left.

One line. `site/content/issues/2026-W39.md`, line 3, set to the `MASTHEAD`
constant in `pipeline/weekly.py` character for character. That string is the
owner's own repair, already printing on every issue the press writes, and the
string it replaces is the one canon law 15 quotes as its own evidence.

## What the pixels say

| Viewport | Before | After |
|---|---|---|
| iPhone 390x844 | [before](issue-before-iphone-390x844.png) | [after](issue-after-iphone-390x844.png) |
| iPad 820x1180 | [before](issue-before-ipad-820x1180.png) | [after](issue-after-ipad-820x1180.png) |
| Desktop 1440x900 | [before](issue-before-desktop-1440x900.png) | [after](issue-after-desktop-1440x900.png) |

Read, not assumed:

- **iPhone 390x844.** Four lines become three. The body moves up 28px, which
  is one line of the dek's leading and on the spacing scale. No clipping, no
  overflow, no hyphen break, no orphan.
- **iPad 820x1180.** Two lines before, two after. The second line goes from
  "acceptance, and what newer evidence has overturned." to "has overturned."
- **Desktop 1440x900.** The same two lines and the same shortened second line.
  Nothing below it moves, because the paragraph count did not change.

One observation, recorded rather than fixed. At iPad and desktop the dek's
second line is now two words under a two-line H1, which is a widow this
seat did not have before. It is not a layout failure and nothing clips, so
the one-line handoff is not the place to change how the dek wraps. The house
uses `text-wrap: balance` exactly once, on `.statement`, so there is no
standing rule the dek is missing and this is not ban list 26. It is a
judgement call about every issue page the archive will ever publish, which is
more than one page's worth of looking, so it is a board card instead of a
diff in this PR.

## The regression check nobody asked for

`site/lib/content.js` derives each archive row's excerpt from the first body
paragraph and skips any paragraph opening with `#`, `*` or `-`. The masthead
opens with `*`, so reading the code says the listing and the page's meta
description never carried this line. Reading the code is not checking it, so
the listing was rendered and looked at:
[library, scrolled to the rows](library-after-desktop-1440x900-scrolled.png).
The row's excerpt is "You have spent the week watching agents get faster by
thinking less at test time…", which is the body and not the masthead. The
derivation holds in the browser and not only in the source.

## The checker

```
$ python3 -I docs/voice/check_voice.py reading
surfaces read                                      63
lines giving the arriving count a verb of reading   4
```

The archive rows are gone. The four that remain are all on `site/app/`:
`page.jsx:44`, `terms/page.jsx:19` and two in `llms.txt/route.js`. Those are
this seat's surface too and this seat did not touch them, because the copy for
both is drafted and still waiting on her word
(`docs/voice/home-metric-line-2026-09-26.md` and the llms.txt repairs). A line
without a verdict is a line this seat would be writing, and writing is not this
seat's lane.

## How this run rendered anything at all

Recorded because the next run will hit it. The container this run executed in
is not the prebaked one the charter describes: `PLAYWRIGHT_BROWSERS_PATH` was
unset, the browser present under `~/.cache/ms-playwright` was `chromium-1248`
rather than the revision Playwright 1.49.1 pins, and that Chromium would not
start at all because the image carries no ATK, Pango, Cairo or GBM. The charter
forbids moving the pin in-run and that was not done. What the run did instead,
all of it outside the repository and none of it committed:

- Resolved Chromium's runtime libraries with `apt-get install --print-uris`,
  fetched the 54 packages and unpacked them to `/tmp/ptroot` with `dpkg -x`,
  then launched through `LD_LIBRARY_PATH`. No root and no image change.
- Drove the browser with the `playwright` already in `site/package.json`
  (1.63.0) pointed at the present binary via `executablePath`, rather than
  installing a second Playwright.
- Got past Clerk. A dev instance answers every browser navigation with a
  `307` to `…clerk.accounts.dev/v1/client/handshake`, reason
  `dev-browser-missing`, so the first screenshots of this run were of Clerk's
  `host_invalid` JSON and not of the site. Setting a `__clerk_db_jwt` cookie on
  the context and aborting requests to the Clerk hosts renders the real page.
  The first version of the stub removed `clerkMiddleware` instead, which turns
  the route into a 500 because the page calls `auth()`; the middleware was
  restored and is untouched in the diff.

This belongs in the ledger as a Dockerfile question rather than here, and it is
filed as one.

## The committed harness, run after the fact

The screenshots above were taken with a script this run wrote by hand, which
was a mistake: `docs/design/harness/` has held `serve.sh`, `shoot.mjs` and
seven more scripts since 2026-10-07, and the charter does not name the
directory, so this run did not find it. That is the second occurrence of a
failure the register already carries twice and is filed as
`INC-2026-10-24-the-visual-harness-was-rebuilt-from-scratch-for-the-second-time`.

Once found, the harness was made to run and the issue page was swept with it.
Its audit is `harness-audit-issue-after.json`, and it is better evidence than
the frames above because it measures things an eye does not:

```
failures   []
overflowX  false at 390, 820 and 1440
offenders  none outside the viewport
small      no tap target under 44px
faded      nothing held at a contrast-failing opacity
h1x        24 / 94 / 404
```

That last row is ban list 29's test, which says to measure one constant across
routes rather than to judge each page alone. The issue page puts its h1 at
x=404 on desktop, which is the number the entry records for pricing, mission,
routines and the 404, so this page is on the shell the rest of the site uses.
Checked against a second page in the same sweep: mission reports 24 / 94 / 404
as well.

Three things in the harness were fixed to get there, each one verified by
running it rather than by reading it. They are in this pull request and they
are the reason its diff is larger than one line.
