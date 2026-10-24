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

---

# Second run of 2026-10-24: the full sweep, and the pricing page's dead ends

The run above set one line and stopped. This run took the next item in the
lane and ran the whole charter around it: the sweep at eleven pages and three
viewports, the fixes, the benchmark, and the states the charter names.

## The sweep

Thirty-three frames before, thirty-three after, every page at 390, 820 and
1440. `sweep-audit-before.json` and `sweep-audit-after.json` are the machine
half, and every frame was read.

The mechanical result is clean and it is worth stating plainly, because a
review that only lists defects implies the rest was not looked at. Across all
thirty-three frames, in both sweeps: no horizontal overflow, nothing rendered
outside the viewport, no tap target under 44 by 44, and nothing held at a
contrast-failing opacity. Thirty-three of thirty-three.

The states the charter names, all re-measured after the harness was repaired:

```
scene two, computed opacity at rest -> after scroll
  iphone   [0,0,0] -> [1,1,1]
  ipad     [0,0,0] -> [1,1,1]
  desktop  [0,0,0] -> [1,1,1]
prefers-reduced-motion, opacity at rest
  iphone   [1,1,1]     ipad [1,1,1]     desktop [1,1,1]
morph, scrollY
  0 at half the turn, 0 at the end of it, 0 on the phone
```

Scene two's scroll-driven range opens at all three viewports, which is ban
list entry 24's test and the one that is invisible in a normal browser. Under
reduced motion everything is legible at rest, which is canon rule 5. The
morph holds the page still through the whole turn.

## What was wrong, worst first

**1. Both paid plans on the pricing page were dead ends.** Board card
`e0a238b6`. `Offer` returned `<span className="pill ghost">` with no href, so
a visitor who clicked either paid plan reached nothing.

Measured before, at all three viewports: the three plan controls are 251x43
and pixel-identical, one is an `<a>` and two are `<span>` at tabIndex -1; the
tab order through `<main>` has three stops and neither paid plan is among
them; and `.pill:hover` scaled the dead control to `matrix(1.06)` under the
cursor. The featured card inverts `.pill` to solid white, so the loudest
control on the page was the one that did nothing, playing the feedback
animation whose only job under canon rule 1 is to answer "did that work".

| | Before | After |
|---|---|---|
| Keyboard focus on the last plan | [no ring, focus skips it](plan-controls-focus-before-desktop-1440x900.png) | [the house 3px ring](plan-controls-focus-after-desktop-1440x900.png) |

The two frames are the same `.focus()` call on the same element. Nothing at
rest changed, which is why the evidence has to be a state.

**2. Every in-page anchor on the site landed its target behind the masthead.**
`.nav` is `position: sticky` at 85px desktop and 83 on the phone, and nothing
set `scroll-margin`. So an anchor put its target's top at y=0, under the bar.

| | Before | After |
|---|---|---|
| iPhone, after clicking a plan | [heading gone, first line sliced](anchor-landing-before-iphone-390x844.png) | [the section lands clear](anchor-landing-after-iphone-390x844.png) |

Measured: clearance -83px before, 13px after on the phone and 19 at desktop.
At 1440 the defect escaped, and only because the page runs out of scroll 104px
before the target reaches the top. That is luck rather than design, and it is
why this survived every desktop review the page has had. The before frame was
reproduced by injecting `scroll-margin-top: 0`, so it is this defect exactly
and not an approximation of it.

**3. The billing note's two paragraphs had nothing between them.** Measured at
0px inside a block whose own leading is 24px, so the gap between paragraphs
was smaller than the gap between two lines of one of them, and they read as
one paragraph with a hard break. [After](billing-note-after-desktop-1440x900.png),
at 16 off the 8-point grid.

## What was tried and rejected, with the frame

The Left-Behind Index at 50 fixture findings
([as shipped](left-behind-as-shipped-desktop-1440x900.png)) puts a three-column
table inside the 680px prose shell. Measured at 1440: the index is 632 wide,
the claim cell is 420, 44 characters fit, the sample claim is 73 characters,
and 380px of viewport sits empty on each side. That is the same shape as the
pricing page's refinement of 2026-10-14, where `.tiers.three` was allowed to
break out to 980 on the same centre axis.

So the same breakout was tried here, and then looked at:
[rejected](left-behind-980-breakout-rejected-desktop-1440x900.png). The
measurement improved and the page got worse. The index starts at x=230 and the
h1 it belongs to starts at x=404, so the column labels and every identifier
hang 174px past the title and the page has two left edges. On pricing the
breakout works because the tiers are a centred band of cards; a hairline-ruled
list under a left-aligned title is not that, and the eye reads the offset as a
mistake.

Reverted, and nothing shipped for it. The measurement is real and the fix is
not obvious, so it goes to the ledger with the frame rather than into the
stylesheet. Noted against card `eb85b8d1`, which already owns the shell-width
question: the site's data-list page, `/skills`, uses a 760px shell, so moving
`/left-behind` onto 760 would gain 80px without adding a fourth width. That is
a smaller gain than the measurement wants and it is the only version of this
that does not make something else worse.

Also measured and not taken, because both already have cards and owners: the
desk's verdict queue renders 524 rows to a 38,262px page at 1440
(card `8787a154`, with the writer's candidate drafted and awaiting her word),
and the h1 left edge at 1440 reads 404 on eight routes, 364 on `/skills`, 264
on `/desk` and 478 on home (card `eb85b8d1`).

## The benchmark

`bench.mjs` read the live motion off Elicit, Linear and Consensus;
`benchmark-elicit-linear-consensus.txt` is the raw output.

```
elicit      0.2s          ease-in-out on transform, ease on opacity
linear      0.1s / 0.16s  cubic-bezier(0.25, 0.46, 0.45, 0.94) on 38 of 38 colour
                          transitions at 0.1s and everything structural at 0.16s
consensus   0.1s          ease, colour only
```

The finding is that nothing needs to change, and that is worth one paragraph
rather than a silent omission. Our `:root` carries one curve,
`cubic-bezier(0.25, 0.46, 0.45, 0.94)`, and two clocks, `--fast` 0.1s and
`--slow` 0.16s. That is Linear's curve and Linear's two clocks exactly, and it
is what the 2026-10-14 run set from the same three sites. Reading them again
tonight reproduced it, which is the useful result: the system did not drift in
ten days, and the discipline the references have is the discipline we have.

One delta recorded rather than acted on. Elicit reads 0.2s tonight where the
note of 2026-09-20 measured its primary CTA at 167ms. Our `.pill` bounce runs
190ms on the owner's approved curve, which now sits between Elicit's two
readings rather than below both. No change: the owner approved that curve and
clock by name, and a 10ms drift on one reference is not evidence.

## The harness, which is why the diff is not small

Three defects in the harness itself, each found by running it and each fixed
and re-run rather than reasoned about.

**The Clerk cure reached one of the four scripts that needed it.** The run
above found that `clerkMiddleware` 307s to a dev-browser handshake without a
`__clerk_db_jwt` cookie, that guard 1 then aborts the redirect because it
leaves localhost, and that the navigation dies before anything is
photographed. It wrote the cure into `shoot.mjs` and into the README as advice
for "a new script". The five context sites that already existed were not a new
script, so `zoom.mjs` could not load a single page tonight. Guard 1 and the
cookie now live together in `local-context.mjs`, one definition, and shoot,
zoom, states, morph and ourmotion all go through it. `bench.mjs` does not,
because it visits the public web on purpose.

**`states.mjs` was photographing scene two and labelling it the morph.**
`MORPH_WHEEL` is 480px of wheel delta for the whole turn. The script spent
1260 before its "mid" frame and 3420 more before its "book" frame. Both land
past the turn, the finished morph flies to scene two 450ms later, and the two
frames it filed were photographs of scene two with no mark in them at all.

| | Before | After |
|---|---|---|
| "the middle of the turn" | [scene two](morph-mid-before-desktop-1440x900.png) | [the rack mid-turn](morph-mid-after-desktop-1440x900.png) |

They audited clean and the script reported success, which is
`INC-2026-10-15-the-visual-harness-had-three-traps` happening again on a
different script. `morph.mjs` in the same directory had the number right the
whole time, so this is a second implementation that reinvented a constant and
got it wrong. Both frames assert `scrollY === 0` now, because the page holding
still is what distinguishes the turn from the scroll past it.

**`zoom.mjs`'s `clip` could not reach anything below the fold.** The clip is
viewport-relative and its height is clamped by the viewport, so a target 2000px
down threw `Expected options.clip.height to be greater than 0` with nothing
naming the cause. It scrolls the target into view first now, unless the spec
pinned an offset on purpose.

## What this container was, which is not what the charter says

Recorded because the charter's step 1 is wrong about it for the third run
running, and the charter is not this seat's file to edit.

- `PLAYWRIGHT_BROWSERS_PATH` unset. `site/node_modules` resolves Playwright
  1.63.0, which wants `chromium-1243`, not the charter's 1.49.1.
- The cache held `chromium-1243` at the start of this run and the libraries to
  start it were missing. The README's `apt-get --print-uris` recipe worked.
- **`chromium-1243` was then deleted out from under the run**, mid-sweep, by
  something that is not this run. The cache held 1243 and 1248 at 00:50 and
  only 1248 twenty minutes later, and a launch that had worked four times
  started failing. Symlinking 1243 to 1248 recovered it. This is the
  shared-container finding the run above filed against `next-server`, now
  reaching the browser cache: the home directory is shared too.
- There is **no Clerk publishable key in this container at all**, so the
  middleware 500s every route before any of the above matters. The run above
  met a `pk_test` key and a handshake; this one met no key and a stack trace.
  A locally synthesised test-shaped key, never committed and never a real
  credential, gets the server up.
