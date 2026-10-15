# Frontend visual review — 2026-10-15

Dispatch: Sprint-2026-10-12 item 4, the Left-Behind Index as a public page
over the `deprecated_claims` view. Board item
03029cad-e613-41ea-9295-3e3e15342f22, moved to In progress at the start of
this run.

Every page was built, screenshotted at three viewports, and looked at. The
new page was judged at fifty findings rather than at the twenty two the
database holds, because it is a list surface. Two defects were found and
fixed, one refinement was earned, and two candidate findings were killed by
measurement.

## Survey (company standard L-E10)

Open pull requests at the start of this run: 305, 304, 303, 302, 301, 297,
272, 205, 203. None is a frontend run and none writes under `site/` or
`docs/design/`. The last frontend PR, #299, merged during this run's window.

Closed-PR search for `left-behind`, `left behind index` and
`deprecated_claims` returns pipeline and research work on the view itself
(#284, #134, #140, #228) and no pull request that has ever built this page.
So this run branched from main with nothing to supersede. Chain depth: one.

## The decision the sprint asked for: public, not paywalled

The sprint said to decide public-versus-paywalled against vision §4 before
writing the route. §4 prices a $10 digest tier and says the digest must be
worth $10 to a stranger before a paywall goes up, but §0's amendment of
2026-09-17 supersedes those tiers in its own words: the digest is free, full
issues, as the acquisition engine, and the paid spine is the operational
layer at $20. §1 names "left behind" as one of the digest's three kinds of
finding and names `deprecated_claims` as its evidence.

So the line is drawn around the operational layer, the Left-Behind Index
sits on the free side of it, and two things already in the repository agree.
`site/lib/entitlement.js` says in its own header that no digest route ever
calls into it, and this route does not. And `pipeline/weekly.py:402` already
prints this exact pair, the flagged finding against the newer one that
contradicts it, inside the weekly issue that `/library/[week]` serves free
and in full to a signed-out visitor. The pair is public today. This is a
second surface over it rather than a new disclosure.

What the page does not do is mention or link the claim graph, which is
paywalled by the ruling of 2026-09-19 and unlisted until its UI is fixed.

## The blocker this run could not clear, and did not route around

**19 of the 22 findings this page would publish are not superseded.**

`docs/research/briefs/2026-10-12.md` §5 measured `contradicts` precision at
**0.172** against the full population of 33 edges rather than a sample: 5
correct, 24 wrong, 4 unsure. `deprecated_claims` gates on `contradicts` at
confidence >= 0.7, which is precisely the band measured at 0.19, and the
brief states the consequence in its own words: "19 of 22 claims on the
Left-Behind Index are not superseded." Only C322, C431 and C533 rest on an
edge that holds.

Three things make this the page's problem rather than someone else's.

1. `docs/product/graph-quality.md:91` anticipated it by name: the view
   "decides a customer-facing page by a number the model was asked for and
   never taught to vary."
2. Confidence carries no signal and is inverted at the top, so there is no
   threshold this seat could raise to filter the page clean. Precision is
   0.19 in the band holding 22 of the edges and **0.0 in both bands above
   it**; the two most confident edges in the graph, at 0.88 and 0.90, are
   both wrong. A stricter gate in `site/lib/` would have made the page worse
   while looking like diligence.
3. The failure is live rather than historical. Four edges have been written
   since the previous brief and all four are wrong.

The frontend seat cannot fix this. The defect is in `pipeline/interpret.py`
and its prompt, which this charter puts outside this lane, and the brief's
§7 already carries the diff.

So the route is built, complete and verified, and it is **not linked from
the nav or from any page**. The sprint's done-means has three parts and this
run delivers two of them: a real route, public, not linked. The third is one
line and it is the owner's call, because merging it is what publishes the
claim. The one-line diff is in the pull request.

This follows the charter's own instruction rather than inventing a position:
a line whose quality-claim row is `contradicted` "stops here and goes back as
a ledger note naming the claim and the surface." The nearest row in
`docs/agents/quality-claims.md` is "replaced when newer work overturns it"
(`site/app/page.jsx:40`), state **reports, does not replace**. That row is
already public on the home page. This page would make it the headline.

## The copy gate, and why the page has no intro

The owner's division of 2026-09-19 is that the writer drafts and the frontend
seat sets. No approved line under `docs/voice/` covers this surface:
`docs/voice/preferences/site-copy-2026-09-20.md` holds approved lines for the
home statement, the library heading and the skills `/llms.txt` line, and
nothing for a Left-Behind Index.

So the page carries no intro paragraph. The kicker is `Library`, the way the
library page's is, and the heading is `Left behind`, which is the product's
own name for this class of finding in vision §1 rather than a sentence
written at the keyboard. Taste's standing rule that headings are bare nouns
with no explanatory subtitle is what the heading follows.

Two state lines are the only prose on the page and both are named here as
provisional, pending the writer's round:

- `No finding is flagged.` (the index is empty)
- `The library could not be read.` (the query failed or there is no
  connection string)

They are kept as named constants at the top of the route so the writer's line
replaces them in one place. They distinguish the two states on purpose,
because one is a fact about the research and the other is a fact about our
infrastructure, and `site/lib/graph-live.js` already makes that distinction
for the same reason.

## What was verified

Eleven routes at 390x844, 820x1180 and 1440x900, which is thirty three
frames, all of them read. The skills library was judged at 54 entries
(`skills/fixture-*`, gitignored, deleted before the run finished) and the new
page at 50 findings over 77 edges, generated by
`docs/design/harness/make-left-behind-fixture.mjs`.

The fixture is deliberately lumpy, because ban list entry 28 says a layout
judged at evenly sized demo data is not judged: claim text from 71 to 401
characters, most findings carrying one contradiction and some carrying four,
ids at three and four digits, nullable confidence, and a paper with no url.

States exercised: every row at rest, a row open at every viewport, a finding
carrying four contradictions, `prefers-reduced-motion`, hover under a real
`hover: none` and `pointer: coarse` profile, the home morph's machine, middle
and book frames, the home scene-two reveal after scrolling, and a 44 by 44
hit probe on every control.

The volume fixture reaches the page through the production path rather than
through a patch, by an env hook in `site/lib/left-behind-live.js` that is
consulted only when there is no connection string. A local patch would have
meant the screenshots proved a code path that does not ship.

## A note on the before and after frames

At desktop and iPad the resting list is byte-identical before and after this
run's changes, because both defects and the refinement only show on the phone
or inside an open row. Those two duplicate frames are not committed; the
`-before` frame that exists is `left-behind-iphone-before.png`, which is the
one that differs. The changes that do not show in a full-page frame have their
own isolated pairs, named below.

## Two defects, found by looking and fixed

**1. The column labels wrapped into a stray row on the phone.**
`fix-phone-header-iphone-before.png` against `-after.png`. At 390 the row
restacks, so the identifier and the date share the first line and the finding
takes the second. The label row was built on the same grid, so it wrapped to
two lines of its own and read as data sitting above the list rather than as a
key to it. It only shows at 1:1; in the full-page frame it looks like a row.
The labels are now hidden below 560px, which is what the skills library does
at every width, and the row says what each field is by how it is set.

**2. The paper link did not read as a link at rest.**
`fix-paper-link-desktop-before.png` against `-after.png`. The links were
shipping a 1px `var(--line)` border-bottom, which measures 1.2:1 against
paper. The house already has a treatment for exactly this kind of link: the
citations inside an issue, `.digest a`, underline at a 3px offset with the
hairline wash on hover, refined on 2026-10-14 after a run measured every
interactive element on the site and found those links answering nothing. The
papers under a finding are the same kind of evidence link, so they now get
the same treatment rather than a second one. Ban list entry 26 is the general
case and entry 25 is why one more treatment is not free.

The after frame also carries the refinement below, because both changes are
live in the same code. The refinement is isolated in its own pair.

## The refinement, and the benchmark that shaped it

Benchmarked Elicit, Consensus and Linear with
`docs/design/harness/bench.mjs`, which reads every distinct
(property, duration, easing) triple actually computed on a page rather than
remembering what the sites feel like.

- **Linear** runs `cubic-bezier(0.25, 0.46, 0.45, 0.94)` with 0.1s and 0.16s.
  That is our `--ease`, `--fast` and `--slow` exactly. Its most common single
  transition is `color | 0.1s` on 38 elements: a text link answering in
  colour at 100ms is the most frequent piece of craft on the site.
- **Consensus** runs one clock, 0.1s, and transitions `outline-color` on 12
  elements, which is the focus-ring practice the house already copied.
- **Elicit** runs 0.2s, and its nav and buttons today change **background
  only, with no transform**. The bouncy quality the owner named on
  2026-09-18 is not in Elicit's current nav; the house keeps it where she
  approved it, on `.pill` and `.issue` at
  `cubic-bezier(0.34, 1.56, 0.64, 1)` and 190ms.

So the benchmark justified no new timing value, which is the finding. One
micro curve and two clocks is the house rule and the three best-in-class
sites are stricter than we are, not looser.

**The refinement: an open row holds the wash.**
`refine-open-row-desktop-before.png` and `-skills-before.png`, against their
`-after` pair. At fifty rows an open row's resting line was identical to a
closed one except for an 11px marker at the far right, and a panel runs to
700px when a finding carries four contradictions, so a reader who scrolls
into the panel and back has nothing that says which row they are inside. The
skills library has the same shape and the same gap, so the rule covers both
list surfaces rather than giving the new page a habit of its own.

It holds the state the row already has under the pointer. No new colour, no
new curve, no new clock, nothing that moves, nothing that costs layout. It
works on touch where there is no hover to carry it, and it reads under
`prefers-reduced-motion`, where the transition is muted and the state is not.
This is Freiberg's implicit feedback rather than an animation, which is also
what the benchmark argues for: none of the three sites animates a disclosure.

That is one refinement of the two this charter allows. The second slot went
unspent because the benchmark did not earn one.

## Two candidate findings that measurement killed

Recorded because the next run will see the same two numbers in the audit and
should not spend its turns the same way.

**The home page stages three elements at opacity 0.** `.statement`,
`.hero-act` and `.about-inline` read 0 at rest at all three viewports, which
is ban list entries 23 and 24 verbatim. Measured after scrolling: all three
compute to opacity 1 at 390, at 1440, and under `prefers-reduced-motion`. The
reveal is the owner's own ruling of 2026-09-19 ("the text stays hidden until
she scrolls") and it works. No defect.

**The desk page reports twelve elements at opacity 0 on desktop.** They are
the `review →` affordances. The rule is a deliberate hover reveal with a
touch fallback at `globals.css` `.desk-go`: `@media (hover: none)` sets them
to opacity 1, which is why the phone and iPad frames report none. Confirmed
in the phone frame, where every row carries its arrow. No defect.

## Two things outside this lane, reported rather than touched

**The Playwright pin in `site/package.json` has drifted off the container.**
It reads `^1.63.0` and resolves to 1.63.0, which looks for
`chromium_headless_shell-1243`. The agent container bakes `chromium-1148`,
which is 1.49.x, so the harness cannot launch from `site/node_modules`:
`browserType.launch: Executable doesn't exist at /ms-playwright/
chromium_headless_shell-1243/...`. This run used the charter's pin,
`playwright@1.49.1`, installed into a scratch directory outside the repo, and
changed neither the package nor the Dockerfile, because the charter says
moving the pin is a Dockerfile change proposed in the ledger and never an
in-run install. Ledger entry filed. Whoever reconciles them should check
whether CI installs its own browsers before changing either number.

**The pricing page's paid CTAs read "Opens shortly" in these frames.** That
is a container artifact and not a defect: `site/app/pricing/page.jsx:12`
renders it when no checkout link is set in the environment, and this run has
no Polar variables. On production, with the links #285 landed, the same code
renders a real button.

## One repeat, filed

The stale server from `INC-2026-10-07-stale-server-third-occurrence` happened
again: a restart appeared to succeed, every route answered 200, and the
process answering was the previous server with the previous environment, which
had bound the port first. The page rendered its empty state while this run
believed it was photographing fifty fixture rows.

The part worth reporting is why. That incident's fix was committed, as
`docs/design/harness/serve.sh`, and its `EADDRINUSE` check would have caught
this at the moment it happened. This run never ran it, because it inventoried
the harness with a `*.mjs` glob and `serve.sh` is a `.sh`, so the script never
appeared in the listing and the start step got rebuilt by hand without the
guard. A committed check that a run does not know to look for is not
meaningfully different from a check that was never committed.

Two changes rather than a fifth prescription. `docs/design/harness/README.md`
is new, so listing the directory finds the order of operations and the two
environment traps. And `serve.sh` gains the one check it lacked: its existing
proof compares the served stylesheet to the one on disk, which proves the
server is this BUILD, and today the stale server was the same build with a
different environment, so it served a byte-identical stylesheet and passed.
It now also proves the listening process descends from the PID it started.

Filed as `INC-2026-10-15-stale-server-survives-restart-fourth-occurrence`,
together with a second instance of the same root cause: `pkill -f` killed this
run's own shell, which is the "kill that cannot match its own argv" from
`INC-2026-09-24`, fired by the seat that was editing the script written to
avoid it.

## Contrast, noted and not changed

`--gray` (#86868b) on paper measures 3.6:1, which is under WCAG AA's 4.5:1
for text under 24px. The new page uses it exactly where the house already
does: the kicker, the row metadata and the definition-list labels, all at 11
to 13px. This is a site-wide standing value rather than anything this page
introduced, so changing it is a proposal and not a polish diff. It is in the
ledger as an observation with the number attached.
