# The ban list — tells of the vibe-coded look

The owner's order (2026-09-18): alexandria must never read as
AI-generated, because the differentiation is that this is an
engineering product. The vibe-coded look is a short, enumerable list
of habits. This file enumerates them. The frontend seat checks every
change against this list before shipping, and APPENDS newly spotted
tells as the generated-web aesthetic drifts; it never deletes an
entry without the owner's word.

## Banned outright

1. Gradients. Especially purple-to-blue heroes, but all of them; the
   house is black and white and flat.
2. Emoji as interface: section markers, list bullets, button labels,
   empty states.
3. The uniform rounded-card grid: same radius, same shadow, same
   padding stamped on every block so nothing ranks above anything.
4. Hover lift-and-shadow applied to everything that can be hovered.
5. Centered-everything layouts. The grid is left-aligned by default;
   centering is a deliberate exception.
6. The generic 100vh hero with a scroll-down cue.
7. Glassmorphism: frosted blur cards, translucent panels.
8. Neon accents on dark, acid green or vermilion pops.
9. Numbered eyebrows (01 / 02 / 03) on content that is not actually a
   sequence.
10. Decorative blob or wave SVGs, particle backgrounds, matrix rain.
11. Typewriter text effects and cursor-blink taglines.
12. Terminal-window mockups displaying fake code or fake output. If a
    terminal appears it shows something real from the product.
13. Fake social proof: invented logos, testimonials, "trusted by"
    walls, metric tiles without a real number behind them.
14. Skeleton shimmer as decoration on content that loads instantly.
15. Badge pills with pulsing dots ("● New", "● Live") unless the thing
    is literally live and the state is real.
16. Inter or Space Grotesk reached for as the safe default. The house
    face is Public Sans, chosen on purpose.
17. Stock illustration styles of any kind: isometric people, corporate
    Memphis, 3D clay renders.
18. Accent bars or colored rails on cards.
19. Scattered scroll-triggered fade-ups on every section. One
    choreographed moment per page; the rest arrives instantly.
20. Copy tells, which are also design tells: "Unlock", "Seamless",
    "Supercharge", "Empower", rocket and sparkle iconography, and any
    sentence that could sit on any SaaS site unchanged.

## The positive test

After removing the tells, the page must still pass the harder test:
does it read as engineered? Real numbers over claims. Honest empty
states over filler. Monospace where data lives. Receipts visible. If
a page looks clean but says nothing true, it is not done.

## Appended by the frontend seat

21. The same call to action repeated on every row of a list. One offer
    per page, or per section at most. A button that appears forty-eight
    times is not an offer, it is wallpaper, and it is the clearest
    single tell that a list was generated rather than designed.
    (Spotted 2026-09-18 at volume: fifty skill rows carried fifty
    "See pricing" pills.)
22. A list whose every row renders its full description at rest. It
    reads fine at two rows and is unusable at fifty. A row at rest
    carries an identifier and the one or two facts you would sort by;
    everything else waits behind the disclosure.
    (Spotted 2026-09-18: roughly 330px of row for one skill.)
23. Content staged at opacity 0 waiting for a scroll script. The canon
    already forbids it; it earns its own entry here because the failure
    is invisible in a normal browser and total without JavaScript, so
    it survives review. (Spotted 2026-09-18: the whole issue archive.)
