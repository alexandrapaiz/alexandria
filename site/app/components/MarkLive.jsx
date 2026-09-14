"use client";

import { useEffect, useRef } from "react";

// The mark holds both identities of the library, morphing along one axis
// and swaying on another:
//
// - Mode (a staged scroll): the page LOADS as the MACHINE — a racked row
//   of slabs sharing one lean, no spine. At the top of the page, wheel
//   input is spent on the transformation itself while the page holds
//   still: scrolling down turns the pages into the fully open BOOK, and
//   only then does the page actually travel. Returning is symmetric —
//   the page arrives back at the top as the open book, and further
//   up-scroll folds it back into the rack.
// - Sway: wherever the cursor is, every page tips a few degrees toward
//   it, so the whole object follows the mouse a little at all times.
//
// Both are eased with a rAF lerp, mutate the SVG directly (no renders),
// and stay still under prefers-reduced-motion.

const SPEC = [
  [72, 170],
  [60, 140],
  [50, 110],
  [40, 80],
  [26, 50],
];
const T = 60;
const B = 840;
const PIVOT_X = 600; // the spine's foot — pages rotate about this point
const DC_CENTER_S = 80;
const DC_W = 50; // every rack slab identical: one width...
const DC_S = 120; // ...and one lean

// The FLARE-OUT book (the approved final): separate page strips with
// white air between them, flanking the thin spine. Each strip's outer
// edge stands full height (nearest the eye) and its spine-facing edge
// is pinched toward the vertical center — hardest beside the spine,
// easing outward — so the whole book reads as pages flaring open
// toward the viewer around a pinched waist.
const BOOK_CY = (T + B) / 2;
// strips sit slightly OUTSIDE their rack slots, so during the morph
// every page drifts outward — from the spine, never into it
const STRIP_GAP0 = 40; // the innermost strip's distance from the spine
const STRIP_PITCH = 96; // slot-to-slot distance of the strips
const stripW = (n) => 46 + ((n - 1) / 4) * 18; // near-even, widest outside
// the pinch concentrates at the spine: the innermost page closes to a
// near-point (the X closes), the second is still strongly tapered, and
// by the outermost the page is a plain full-height rectangle — so the
// taper reads as pages turning at the spine, not a starburst
const stripPinch = (n) => 0.03 + 0.97 * Math.sin(((n - 1) / 4) * (Math.PI / 2));
const DRAW_ORDER = [-1, -2, -3, -4, -5, 1, 2, 3, 4, 5, 0];

const lerp = (a, b, t) => a + (b - a) * t;

function rot(x, y, ang) {
  const dx = x - PIVOT_X;
  const dy = y - B;
  const c = Math.cos(ang);
  const s = Math.sin(ang);
  return [PIVOT_X + dx * c - dy * s, B + dx * s + dy * c];
}

function barSpec(j) {
  if (j === 0) return [10, 0];
  return SPEC[4 - (Math.abs(j) - 1)];
}

// corner sets in TL, TR, BR, BL order
function restCorners(j) {
  const [w, s] = barSpec(j);
  const cx = PIVOT_X + j * 98;
  const x0 = cx - w / 2;
  const x1 = cx + w / 2;
  if (j > 0) return [[x0, T + s], [x1, T], [x1, B - s], [x0, B]];
  if (j < 0) return [[x0, T], [x1, T + s], [x1, B], [x0, B - s]];
  return [[x0, T], [x1, T], [x1, B], [x0, B]];
}

function pageCorners(j) {
  // a page strip of the approved final: outer edge full height, the
  // spine-facing edge pinched toward the vertical center — hardest
  // beside the spine, easing outward — with white air between strips
  if (j === 0) {
    // the spine sits a touch shorter than the pages flanking it
    return [[PIVOT_X - 4, T + 44], [PIVOT_X + 4, T + 44], [PIVOT_X + 4, B - 44], [PIVOT_X - 4, B - 44]];
  }
  const n = Math.abs(j);
  const dir = Math.sign(j);
  const xin = PIVOT_X + dir * (STRIP_GAP0 + (n - 1) * STRIP_PITCH);
  const xout = xin + dir * stripW(n);
  const half = ((B - T) * stripPinch(n)) / 2;
  // a very minor perspective aid: pages step slightly shorter toward
  // the spine, their tops and feet tracing a shallow V into the book
  const short = 26 * ((5 - n) / 4);
  const yT = T + short;
  const yB = B - short;
  if (dir > 0) {
    return [[xin, BOOK_CY - half], [xout, yT], [xout, yB], [xin, BOOK_CY + half]];
  }
  return [[xout, yT], [xin, BOOK_CY - half], [xin, BOOK_CY + half], [xout, yB]];
}

function machineCorners(j) {
  // a rack aisle has no spine, and every slab is identical: one width,
  // one lean, one pitch — the center bar collapses to nothing
  if (j === 0) {
    return [[PIVOT_X, T], [PIVOT_X, T + DC_CENTER_S], [PIVOT_X, B], [PIVOT_X, B - DC_CENTER_S]];
  }
  const cx = PIVOT_X + Math.sign(j) * (Math.abs(j) - 0.5) * 99;
  const x0 = cx - DC_W / 2;
  const x1 = cx + DC_W / 2;
  return [[x0, T], [x1, T + DC_S], [x1, B], [x0, B - DC_S]];
}

function compute(f, sway) {
  // ONE direct morph: f = -1 is the rack, f = +1 the flared book. The
  // two forms almost share their outer edges, so the motion is a clean
  // pinch-and-attach: each slab's inner edge reaches to the spine as
  // its profile pinches, the caps unshear, and the spine grows in — a
  // whisper of cascade, spine outward.
  const k = (f + 1) / 2;
  const pts = [];
  for (const j of DRAW_ORDER) {
    const a = machineCorners(j);
    const g = pageCorners(j);
    const startAt = j === 0 ? 0 : (Math.abs(j) - 1) * 0.05;
    const local = Math.min(1, Math.max(0, (k - startAt) / (1 - startAt)));
    const e = Math.sin((local * Math.PI) / 2);
    const corners = a.map(([ax, ay], c) => [
      lerp(ax, g[c][0], e),
      lerp(ay, g[c][1], e),
    ]);
    // the mouse TURNS the pages in depth — LOCALLY: each page's turn
    // depends on its distance from the cursor. The page under the
    // cursor stays flat, its neighbors lean away hardest, and the wave
    // decays outward, so the pages part around the mouse as it moves.
    // Alive in every stage, rack and book alike. (sway = eased cursor
    // x in viewBox units)
    const cxm = (corners[0][0] + corners[1][0]) / 2;
    const u = (cxm - sway) / 280;
    const th = 0.55 * u * Math.exp((-u * u) / 2); // a gentle swell
    const cs = Math.cos(th);
    const sh = Math.sin(th) * 4;
    const turned = corners.map(([x, y]) => [cxm + (x - cxm) * cs + sh, y]);
    pts.push(turned.map(([x, y]) => `${x},${y}`).join(" "));
  }
  return pts;
}

export default function MarkLive(props) {
  const ref = useRef(null);

  useEffect(() => {
    const svg = ref.current;
    if (!svg) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const polys = svg.querySelectorAll("polygon");
    // touch devices get a scroll-linked morph with fully native
    // scrolling; the staged wheel choreography is desktop-only
    const mobile = window.matchMedia("(pointer: coarse)").matches;
    let curF = -1; // the page loads as the machine
    let curS = PIVOT_X; // eased cursor x in viewBox units
    let mouseVX = PIVOT_X;
    let p = 0; // morph progress at the top: 0 machine, 1 open book
    let lastScrollY = 0;
    let raf = null;
    const MORPH_WHEEL = 480; // a short, decisive scroll completes the turn

    const apply = () => {
      const pts = compute(curF, curS);
      polys.forEach((p, i) => p.setAttribute("points", pts[i]));
    };
    const tick = () => {
      // scroll alone tells the story: machine at the top, book once
      // scrolled. The mouse never changes the mode — it only sways the
      // pages toward the cursor.
      // while the page travels, the mark is the open book; at the top,
      // the wheel-driven morph progress decides, shaped by a doubled
      // S-curve: long dwell at rack and at book, a quick flip between
      const s = (x) => x * x * (3 - 2 * x);
      const eased = s(s(p));
      const targetF = !mobile && lastScrollY > 130 ? 1 : eased * 2 - 1;
      const targetS = mouseVX; // the wave's center follows the cursor
      curF += (targetF - curF) * 0.065;
      curS += (targetS - curS) * 0.065;
      if (Math.abs(targetF - curF) > 0.0005 || Math.abs(targetS - curS) > 0.5) {
        apply();
        raf = requestAnimationFrame(tick);
      } else {
        curF = targetF;
        curS = targetS;
        apply();
        raf = null;
      }
    };
    const wake = () => {
      if (raf === null) raf = requestAnimationFrame(tick);
    };
    const onMove = (e) => {
      // map the cursor into the mark's own coordinate space, so each
      // page can measure its distance to it
      const r = svg.getBoundingClientRect();
      if (r.width > 0) {
        mouseVX = ((e.clientX - r.left) / r.width) * 1340 - 70;
      }
      wake();
    };
    const setMorphing = (on) =>
      document.documentElement.classList.toggle("morphing", on);
    let advancing = false;
    let gliding = false;
    let lockUntil = 0; // absorbs trackpad momentum right after a landing
    let flightTimer = null; // the scheduled flight — cancelable by up-scroll

    // our own scene-to-scene travel: one eased flight, wheel input
    // swallowed while it flies
    const glide = (toY) => {
      gliding = true;
      setMorphing(true);
      const fromY = window.scrollY;
      const t0 = performance.now();
      const ms = Math.max(320, Math.min(950, Math.abs(toY - fromY) * 1.2));
      const ease = (x) =>
        x < 0.5 ? 16 * x * x * x * x * x : 1 - Math.pow(-2 * x + 2, 5) / 2;
      const step = (now) => {
        const u = Math.min((now - t0) / ms, 1);
        window.scrollTo(0, fromY + (toY - fromY) * ease(u));
        if (u < 1) requestAnimationFrame(step);
        else {
          gliding = false;
          lockUntil = performance.now() + 380;
          setTimeout(() => setMorphing(false), 80);
        }
      };
      requestAnimationFrame(step);
    };
    const followTop = () => {
      const el = document.querySelector(".hero-follow");
      return el ? el.getBoundingClientRect().top + window.scrollY - 96 : 0;
    };

    const onWheel = (e) => {
      if (gliding) {
        e.preventDefault(); // the flight owns the scroll
        return;
      }
      if (performance.now() < lockUntil) {
        // momentum after a downward landing is never upward: an upward
        // wheel here is the user deliberately leaving — honor it
        if (e.deltaY < 0 && Math.abs(window.scrollY - followTop()) < 60) {
          e.preventDefault();
          glide(0);
          return;
        }
        e.preventDefault();
        return;
      }
      const sy = window.scrollY;
      if (sy < 90) {
        if (e.deltaY > 0 && p < 1) {
          // spend the down-scroll on opening the book, while the page
          // creeps just enough to promise something below
          e.preventDefault();
          p = Math.min(1, p + e.deltaY / MORPH_WHEEL);
          setMorphing(true);
          wake();
          if (p >= 1 && !advancing) {
            // hold the finished book for a beat before flying down
            advancing = true;
            flightTimer = setTimeout(() => {
              flightTimer = null;
              glide(followTop());
            }, 450);
          }
        } else if (e.deltaY > 0 && p >= 1) {
          // standing at the top as the book: the book is already made,
          // so a down-scroll flies at once — no hold
          e.preventDefault();
          if (!advancing) {
            advancing = true;
            glide(followTop());
          }
        } else if (e.deltaY < 0 && p > 0) {
          // spend the up-scroll on folding it back — symmetric; a
          // scheduled flight is aborted
          e.preventDefault();
          if (flightTimer) {
            clearTimeout(flightTimer);
            flightTimer = null;
            advancing = false;
          }
          p = Math.max(0, p + e.deltaY / MORPH_WHEEL);
          setMorphing(true);
          wake();
          if (p <= 0) setMorphing(false);
        }
        return;
      }
      // at scene two, an upward wheel flies home the same way
      if (e.deltaY < 0 && Math.abs(sy - followTop()) < 60) {
        e.preventDefault();
        glide(0);
      }
    };
    // with no CSS snap, a settle guard finishes any scroll that would
    // otherwise rest between the scenes: after input goes quiet, glide
    // to whichever scene is nearer
    let settleTimer = null;
    const settle = () => {
      if (gliding) return;
      const sy = window.scrollY;
      const ft = followTop();
      // only the true between-scenes band settles; the direction of
      // travel decides the destination, so scrolling up never snaps down
      if (sy > 90 && sy < ft - 40) {
        glide(lastDir < 0 ? 0 : ft);
      }
    };
    let lastDir = 1;
    const onScroll = () => {
      lastDir = Math.sign(window.scrollY - lastScrollY) || lastDir;
      lastScrollY = window.scrollY;
      // any real travel (touch, keyboard, scrollbar) rides as the book
      if (lastScrollY > 130) p = 1;
      if (advancing && lastScrollY < 60) advancing = false;
      if (settleTimer) clearTimeout(settleTimer);
      if (!gliding) settleTimer = setTimeout(settle, 170);
      wake();
    };

    if (mobile) {
      // the thumb drives the morph directly; scrolling stays native
      const onScrollM = () => {
        lastScrollY = window.scrollY;
        p = Math.min(1, Math.max(0, lastScrollY / (window.innerHeight * 0.35)));
        wake();
      };
      window.addEventListener("scroll", onScrollM, { passive: true });
      onScrollM();
      return () => {
        window.removeEventListener("scroll", onScrollM);
        if (raf !== null) cancelAnimationFrame(raf);
      };
    }

    window.addEventListener("mousemove", onMove);
    window.addEventListener("wheel", onWheel, { passive: false });
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("wheel", onWheel);
      window.removeEventListener("scroll", onScroll);
      setMorphing(false);
      if (settleTimer) clearTimeout(settleTimer);
      if (raf !== null) cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <svg
      ref={ref}
      viewBox="-70 0 1340 900"
      xmlns="http://www.w3.org/2000/svg"
      preserveAspectRatio="xMidYMid meet"
      aria-hidden="true"
      {...props}
    >
      {compute(-1, 0).map((pts, i) => (
        <polygon
          key={i}
          points={pts}
          fill="currentColor"
          stroke="#fff"
          strokeWidth="2.5"
        />
      ))}
    </svg>
  );
}
