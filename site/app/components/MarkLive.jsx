"use client";

import { useEffect, useRef } from "react";

// The mark holds both identities of the library. Mouse right (or the top
// of the page) and it is a codex: pages fan open MIRRORED around the
// central spine, shear deepening as it opens. Mouse left or scroll down
// and it becomes the machine: eleven identical slabs, uniform width and
// pitch, all leaning the SAME way — racked units seen down a data-center
// aisle. Every bar is one unbroken page in both states; what morphs is
// the symmetry. One parameter f in [-0.85, 0.85] drives it from cursor x
// plus scroll depth, eased with a rAF lerp, mutating the SVG directly so
// nothing re-renders. Still under prefers-reduced-motion.

const SPEC = [
  [72, 170],
  [60, 140],
  [50, 110],
  [40, 80],
  [26, 50],
];
const T = 60;
const B = 840;
const DC_CENTER_S = 80; // the center spine's lean once racked

const lerp = (a, b, t) => a + (b - a) * t;

function compute(f) {
  // f in [-1, 1]: -1 full machine (far left), 0 the resting mark (the
  // middle of the animation), +1 fully fanned book (far right)
  const k = Math.max(f, 0); // book factor
  const t = Math.max(-f, 0); // machine factor, complete only at f = -1
  const pts = [];
  // bars indexed -5..5 around the spine
  for (let j = -5; j <= 5; j++) {
    const i = Math.abs(j) - 1;
    const [w0, s0] = j === 0 ? [10, 0] : SPEC[4 - i];
    // book side (mirrored fan): near side spreads and widens with k,
    // far side tucks thin and edge-on
    let w, s, cx;
    if (j < 0) {
      w = Math.max(w0 * (1 - 0.45 * k), 5);
      s = s0 * (1 + 0.3 * k);
      cx = 600 + j * 98 * (1 - 0.14 * k);
    } else if (j > 0) {
      w = Math.max(w0 * (1 + 0.45 * k), 5);
      s = s0 * (1 - 0.3 * k);
      cx = 600 + j * 98 * (1 + 0.14 * k);
    } else {
      w = w0;
      s = 0;
      cx = 600;
    }
    // book corner ys: left group leans one way, right group mirrors
    const bookTL = j > 0 ? T + s : T;
    const bookTR = j > 0 ? T : T + s;
    const bookBL = j > 0 ? B : B - s;
    const bookBR = j > 0 ? B - s : B;
    // machine: sizes and pitch keep their character — only the lean
    // unifies, every page sharing one direction at its own depth
    const sDC = j === 0 ? DC_CENTER_S : s0;
    const tl = lerp(bookTL, T, t);
    const tr = lerp(bookTR, T + sDC, t);
    const bl = lerp(bookBL, B - sDC, t);
    const br = lerp(bookBR, B, t);
    const x0 = cx - w / 2;
    const x1 = cx + w / 2;
    pts.push(`${x0},${tl} ${x1},${tr} ${x1},${br} ${x0},${bl}`);
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
    let cur = 0;
    let target = 0;
    let mouseF = 0;
    let scrollF = 0;
    let raf = null;

    const apply = (f) => {
      const pts = compute(f);
      polys.forEach((p, i) => p.setAttribute("points", pts[i]));
    };
    const tick = () => {
      cur += (target - cur) * 0.08;
      if (Math.abs(target - cur) > 0.001) {
        apply(cur);
        raf = requestAnimationFrame(tick);
      } else {
        cur = target;
        apply(cur);
        raf = null;
      }
    };
    const retarget = () => {
      target = Math.max(-1, Math.min(1, mouseF + scrollF));
      if (raf === null) raf = requestAnimationFrame(tick);
    };
    const onMove = (e) => {
      // symmetric 50/50 travel: center of the screen is the resting mark,
      // full machine only at the far-left edge, full book at the far right
      mouseF = (e.clientX / window.innerWidth - 0.5) * 2;
      retarget();
    };
    const onScroll = () => {
      scrollF = -Math.min(window.scrollY / 450, 1);
      retarget();
    };

    window.addEventListener("mousemove", onMove);
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("scroll", onScroll);
      if (raf !== null) cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <svg
      ref={ref}
      viewBox="0 0 1200 900"
      xmlns="http://www.w3.org/2000/svg"
      preserveAspectRatio="xMidYMid meet"
      aria-hidden="true"
      {...props}
    >
      {compute(0).map((pts, i) => (
        <polygon key={i} points={pts} fill="currentColor" />
      ))}
    </svg>
  );
}
