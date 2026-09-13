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
const BOOK_ANGLE = 0.13; // radians per page of fan spread
const BOOK_GATHER = 30; // horizontal pitch in book mode (pages close up)

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

function bookCorners(j) {
  const [w] = barSpec(j);
  const cx = PIVOT_X + j * BOOK_GATHER;
  const x0 = cx - w / 2;
  const x1 = cx + w / 2;
  const ang = j * BOOK_ANGLE;
  return [rot(x0, T, ang), rot(x1, T, ang), rot(x1, B, ang), rot(x0, B, ang)];
}

function machineCorners(j) {
  // a rack aisle has no spine: the center bar collapses to nothing, and
  // the ten slabs redistribute to one uniform pitch so no gap remains
  if (j === 0) {
    return [[PIVOT_X, T], [PIVOT_X, T + DC_CENTER_S], [PIVOT_X, B], [PIVOT_X, B - DC_CENTER_S]];
  }
  const [w, s] = barSpec(j);
  const cx = PIVOT_X + Math.sign(j) * (Math.abs(j) - 0.5) * 99;
  const x0 = cx - w / 2;
  const x1 = cx + w / 2;
  return [[x0, T], [x1, T + s], [x1, B], [x0, B - s]];
}

function compute(f, sway) {
  // f in [-1, 1]: -1 machine, 0 resting emblem, +1 fanned codex
  const k = Math.max(f, 0);
  const t = Math.max(-f, 0);
  const pts = [];
  for (let j = -5; j <= 5; j++) {
    const rest = restCorners(j);
    const goal = f >= 0 ? bookCorners(j) : machineCorners(j);
    const m = f >= 0 ? k : t;
    const corners = rest.map(([rx, ry], c) => {
      const x = lerp(rx, goal[c][0], m);
      const y = lerp(ry, goal[c][1], m);
      return rot(x, y, sway);
    });
    pts.push(corners.map(([x, y]) => `${x},${y}`).join(" "));
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
      const targetS = mouseF * 0.055; // the follow-the-mouse tip, always on
      curF += (targetF - curF) * 0.1;
      curS += (targetS - curS) * 0.1;
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
      const ms = Math.max(260, Math.min(850, Math.abs(toY - fromY) * 1.1));
      const ease = (x) =>
        x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
      const step = (now) => {
        const u = Math.min((now - t0) / ms, 1);
        window.scrollTo(0, fromY + (toY - fromY) * ease(u));
        if (u < 1) requestAnimationFrame(step);
        else {
          gliding = false;
          lockUntil = performance.now() + 650;
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
      if (gliding || performance.now() < lockUntil) {
        e.preventDefault(); // the flight (or its afterglow) owns the scroll
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
          window.scrollBy(0, e.deltaY * 0.035);
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
          window.scrollBy(0, e.deltaY * 0.035);
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
      // only the true between-scenes band settles; everything at or
      // past scene two is ordinary free scrolling
      if (sy > 90 && sy < ft - 40) {
        glide(sy < ft / 2 ? 0 : ft); // nearest scene wins
      }
    };
    const onScroll = () => {
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
        <polygon key={i} points={pts} fill="currentColor" />
      ))}
    </svg>
  );
}
