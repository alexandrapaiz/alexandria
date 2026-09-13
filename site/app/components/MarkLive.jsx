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

// The open book faces the viewer, parallel to the screen, and the
// turning pages stand OUT of it, perpendicular. Every page hinges on
// the central spine. Seen head-on with perspective: a page mid-turn
// is horizontally thin but TALLER (its free edge is nearest the eye);
// a settled page lies wide at page height. Thin paper seams keep the
// nested pages readable.
const BOOK_CY = (T + B) / 2;
const PAGE_L = 430; // a page's reach from the spine when it lies flat
const PAGE_PERSP = 0.04; // a whisper of growth toward the eye — a book's
// body stays rectangular; only the near-spine pages lift slightly
const HINGE = 4; // the hinge sits this close beside the spine line

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
  // a page hinged on the spine, caught at its own stage of the turn:
  // the hinge edge is a full-height vertical at the spine; the free
  // edge sits at cos(theta) reach with sin(theta) perspective growth —
  // standing pages thin and tall, settled pages wide at page height
  if (j === 0) {
    return [[PIVOT_X - 4, T], [PIVOT_X + 4, T], [PIVOT_X + 4, B], [PIVOT_X - 4, B]];
  }
  const dir = Math.sign(j);
  const stage = (Math.abs(j) - 1) / 4; // 0 beside the spine .. 1 outermost
  const th = ((82 - 78 * stage) * Math.PI) / 180; // standing -> almost flat
  const xs = PIVOT_X + dir * HINGE;
  const xe = PIVOT_X + dir * (HINGE + PAGE_L * Math.cos(th));
  const half = ((B - T) / 2) * (1 + PAGE_PERSP * Math.sin(th));
  if (dir > 0) {
    return [[xs, T], [xe, BOOK_CY - half], [xe, BOOK_CY + half], [xs, B]];
  }
  return [[xe, BOOK_CY - half], [xs, T], [xs, B], [xe, BOOK_CY + half]];
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
  // f in [-1, 1]: -1 machine, 0 resting emblem, +1 fanned codex
  const k = Math.max(f, 0);
  const t = Math.max(-f, 0);
  const pts = [];
  for (let j = -5; j <= 5; j++) {
    const rest = restCorners(j);
    let corners;
    if (f >= 0) {
      // the pages FLARE OPEN from the spine outward: the columns
      // nearest the spine become the far-reaching leaves (their free
      // edges sweep outward), the cascade starts at the spine and
      // travels out, and every page arcs outward mid-flight before
      // settling — opening, never closing in
      const inv = j === 0 ? 0 : Math.sign(j) * (6 - Math.abs(j));
      const startAt = j === 0 ? 0 : (Math.abs(j) - 1) * 0.06;
      const local = Math.min(1, Math.max(0, (k - startAt) / (1 - startAt)));
      const e = Math.sin((local * Math.PI) / 2);
      const arc = j === 0 ? 0 : Math.sign(j) * 90 * Math.sin(local * Math.PI);
      const goal = pageCorners(inv);
      corners = rest.map(([rx, ry], c) => [
        lerp(rx, goal[c][0], e) + arc,
        lerp(ry, goal[c][1], local),
      ]);
    } else {
      const goal = machineCorners(j);
      corners = rest.map(([rx, ry], c) => [
        lerp(rx, goal[c][0], t),
        lerp(ry, goal[c][1], t),
      ]);
    }
    // the mouse TURNS the pages in depth: each page rotates about its
    // own vertical axis, its width foreshortening from flat toward
    // edge-on as the cursor moves — pages turning, not the image
    // tilting. The effect fades out as the radial book takes over,
    // where widths are the fan itself.
    const effS = sway * (f > 0 ? 1 - 0.85 * Math.min(f, 1) : 1);
    const cxm = (corners[0][0] + corners[1][0]) / 2;
    const cs = Math.cos(effS);
    const sh = Math.sin(effS) * 8;
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
    let curS = 0;
    let mouseF = 0;
    let p = 0; // morph progress at the top: 0 machine, 1 open book
    let lastScrollY = 0;
    let raf = null;
    const MORPH_WHEEL = 700; // wheel pixels that turn machine fully into book

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
      // the turn angle: center screen is flat, screen edges near edge-on
      const targetS = mouseF * 1.25;
      curF += (targetF - curF) * 0.065;
      curS += (targetS - curS) * 0.065;
      if (Math.abs(targetF - curF) > 0.0005 || Math.abs(targetS - curS) > 0.0003) {
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
      // saturating gain: final states arrive well before the screen edges,
      // so the mark spends real time fully open or fully racked
      const x = (e.clientX / window.innerWidth - 0.5) * 2;
      mouseF = Math.max(-1, Math.min(1, x * 1.9));
      wake();
    };
    const setMorphing = (on) =>
      document.documentElement.classList.toggle("morphing", on);
    let advancing = false;
    let gliding = false;
    let lockUntil = 0; // absorbs trackpad momentum right after a landing

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
            setTimeout(() => glide(followTop()), 800);
          }
        } else if (e.deltaY > 0 && p >= 1) {
          // holding as the book: the page belongs to the coming flight
          e.preventDefault();
        } else if (e.deltaY < 0 && p > 0) {
          // spend the up-scroll on folding it back — symmetric
          e.preventDefault();
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
