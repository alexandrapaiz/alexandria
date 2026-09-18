# Motion notes — distilled from Kowalski and Freiberg

Working knowledge for the frontend seat, distilled 2026-09-18 from
Emil Kowalski's writing on web animation (emilkowal.ski) and Rauno
Freiberg's "Invisible Details of Interaction Design" (rauno.me).
These are our notes in our words, not their text; read the sources
themselves when a case here is thin. The canon's seven animation
rules still govern; these notes are the craft underneath them.

## From Kowalski: how to make an animation good

1. Keep interactions under 300ms with ease-out. Fast plus ease-out
   is what "snappy" actually is; slow plus ease-in-out is what
   "sluggish" actually is.
2. Animate only transform and opacity. They run on the compositor.
   Padding, margin, width, height trigger layout and will stutter.
   Prefer CSS or the Web Animations API over requestAnimationFrame.
3. Springs for anything that moves like an object. Stiffness,
   damping, and mass are the whole vocabulary; tune until it feels
   like matter, not like a tween.
4. Every animation must be interruptible. The user changing their
   mind mid-motion is normal, not an edge case. CSS transitions
   interrupt gracefully by default; keep that property.
5. Never animate keyboard-initiated actions. A thing triggered
   hundreds of times a day earns zero milliseconds of ceremony.
6. Frequency decides ceremony. The less often an interaction
   happens, the more motion it can carry; the more often, the less.
   Onboarding can be choreographed. A dropdown cannot.
7. Judge with fresh eyes. An animation reviewed the day it was made
   always feels better than it is; re-watch it the next session
   before calling it done.
8. Respect prefers-reduced-motion completely, and make the reduced
   experience a designed one, not a broken one.

## From Freiberg: the invisible details

1. Motion communicates spatial origin. A panel that opens from the
   thing that summoned it teaches the user where it lives; a modal
   that fades in from nowhere teaches nothing. Animate FROM the
   trigger's position.
2. Dismissed things keep their momentum. An element thrown away
   leaves at the velocity and angle it was thrown, never on a
   perfectly centered path. This is the difference between physics
   and PowerPoint.
3. Immediate feedback, then thresholds. Response starts the instant
   the input starts (that is how the user learns the thing is
   interactive at all); the committed action fires only past a
   threshold, and destructive actions only when the gesture ENDS,
   so a change of mind mid-gesture cancels cleanly.
4. High-frequency surfaces get no entrance animation. Command
   menus and context menus should appear instantly; the graceful
   touch is implicit feedback instead, like the selected item
   briefly blinking before the menu closes.
5. Fitts's law is free speed. Edges and corners are infinitely
   large targets; generous hit areas beyond the visual bounds keep
   gestures from cancelling on a near miss. A 44px target that
   accepts 52px of finger is craft.
6. Optical over mathematical. Centering, alignment, and anchor
   points should look right to an eye, which sometimes means being
   numerically wrong on purpose.
7. Under-the-finger problems are real: never let the pointer or
   finger hide the thing it is manipulating; reveal state (the
   caret, the value, the key) beside or above the obstruction.
8. Infer intent from context where it is cheap and honest: what
   has focus, what the user is mid-way through, what device they
   are on. The interface that anticipates one step reads as cared
   for.

## What this means for alexandria specifically

- The skills library and the digest archive are HIGH-frequency
  surfaces for a subscriber: instant, no entrance choreography,
  implicit feedback only.
- The home page is the one LOW-frequency surface: it may carry the
  site's single choreographed moment.
- Hovers follow the Elicit ruling in taste.md: alive, immediate,
  ease-out, under 200ms.
- Everything a paying user touches daily earns the command-menu
  treatment: speed as the aesthetic, motion only as confirmation.
