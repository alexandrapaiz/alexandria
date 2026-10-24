# The issue as it renders in mail — 2026-10-24

This folder's other README covers tonight's earlier run, which reviewed every
public page at three viewports. That run said in its own board comment what it
did not claim: the issue as it renders in mail, which it did not touch at all.
This is that surface, and this is a separate file rather than an append to the
existing README on purpose, because two append-only ledgers at one anchor is
what collided three times tonight already.

## What was rendered, and through what

Both published issues, through the press's own code path rather than a copy of
it: `tools/rehearse_email.py` calls `weekly.build_messages()`, the same
function `send_newsletter()` calls, so what is photographed here is what would
be sent. Plus one fixture, described below.

Eighteen frames: three documents, three viewports, two colour schemes.
`mail-audit-before.json` and `mail-audit-after.json` carry the mechanical read
of every one.

| | |
|---|---|
| 2026-W39 | the published weekly, four sentence-length H2s, no procedure points |
| 2026-W37 | the other published weekly, four label H2s, 18 `.mid` cells, an empty state |
| fixture | `mail-fixture-issue.md`, one of every optional region at once |

The mechanical result after the fix below: no horizontal overflow at any
viewport, nothing under the canon's 12px small-print floor, and no text held
at a contrast-failing colour in either scheme.

## The defect that was fixed

**A cited paper inside a procedure bullet was black on black in dark mode.**

- `mail-point-link-before-dark-iphone-390x844.png`
- `mail-point-link-after-dark-iphone-390x844.png`
- `mail-point-link-after-light-iphone-390x844.png`

The dark block re-colours four house classes. `.ink` and `.quiet` were given
their `a` variant, `.mid` was not, and every anchor the press writes carries an
inline `color:#0a0a0a`. A procedure point is the one text block that can carry
a link and is not `.ink`, so a bullet citing its paper drew #0a0a0a on #0a0a0a
at a ratio of 1:1. The before frame is the thing worth looking at: the link is
not a dim link, it is a hole in the sentence, which is why no reader would ever
have reported it as a link problem.

Neither published issue happens to cite inside a bullet, so both audit clean in
both schemes at all three viewports and the defect is invisible at the
inventory of the day. It is not hypothetical: 2026-W37 renders eighteen of
those cells already, and `inline()` runs over every point's text. The fixture
exists to produce the one element production has not yet produced, which is
the only way this class of defect can be photographed. That is now ban list
entry 31.

The fix is one selector. The colour mirrors light mode, where the link is
stronger than the #4a4a4a it sits in rather than equal to it, so the dark link
is #ffffff against #86868b. No new value enters the palette.

## Two findings that are not this seat's to fix

**The section-title slot has two contracts and the press follows the newer one.**

- `mail-section-title-widow-iphone-390x844.png`
- `mail-section-title-widow-desktop-1440x900.png`

`site/emails/README.md` §4 says `{{section_title}}` carries "Compounding, New
and unproven, Left behind", and the template draws it as a label: 14px,
uppercase, 0.1em tracking. 2026-W37 obeys that, at 11 to 19 characters.
2026-W39 sends sentences, at 33 to 45. At desktop the longest fits on one line.
At 390px it wraps, and "THEN DROPPED" lands alone on the second line of a
tracked uppercase heading.

It is legible and nothing is clipped, so this is not a layout break and the
words are not mine to change. What is worth a verdict is which of the two
contracts is the real one, because the treatment was designed for the other.

**In the read-list, a paper's reason floats equidistant between two papers.**

- `mail-readlist-grouping-desktop-1440x900.png`

The markdown writes a source line and the sentence explaining it as adjacent
lines with no blank between, clearly one unit. `parse_section` in
`pipeline/email_render.py` makes a new item out of every unindented non-bullet
line, so they become two items, and every item carries the same `padding-top:
24px`. The gap above "Worth the hour if you are deciding" equals the gap below
it. Scanning the section, you cannot tell which paper a reason belongs to.

The template cannot fix this, because it is not told the two belong together.
The fix is in the parser, which is the engineer's surface, so this is reported
rather than touched.

## One thing checked and found correct

The close reads "Accelerate every builder and agent to frontier speed." and
`docs/design/taste.md` says the mission line is exactly "Accelerate every
builder to frontier speed." These are two lines with two jobs, not a drift:
`docs/voice/canon.md` rule 10 approves the dual-audience close verbatim, three
voice reviews pass it, and `site/app/mission/page.jsx` carries the other one
unchanged. Nothing to do.

## The whole issue, for rhythm

- `mail-W39-light-iphone-390x844-full.png`
- `mail-W39-dark-iphone-390x844-full.png`

These two are at half scale. The judging was done at 1:1 in the run and
everything measured has a 1:1 crop beside it here; a 5,599px frame at full
scale costs 500K and the folder's other 22 frames average 37K.

- `mail-W39-titleblock-dark-desktop-1440x900.png` — the title block, which is
  the best thing on this surface and is here as the reference rather than as a
  defect.
- `mail-W37-points-dark-iphone-390x844.png` — a procedure point with no link
  in it, for the contrast with the before frame above.

## The harness

`docs/design/harness/mail.mjs` and `mail-zoom.mjs` are new. The site harness
reaches routes through `serve.sh`, and the issue in mail is a file the press
renders rather than a route, so nothing in that directory could photograph
this surface until now. `mail.mjs` shoots both colour schemes, which
`shoot.mjs` does not, because dark mode is half of a mail client and none of
this surface's rules were ever checked in it.
