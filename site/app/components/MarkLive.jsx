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
const DC_W = 46; // slab width in the machine state
const DC_S = 115; // shared lean of every slab in the machine state

const lerp = (a, b, t) => a + (b - a) * t;

function compute(f) {
  const k = Math.max(f, 0); // book factor
  const t = Math.min(Math.max(-f, 0) / 0.7, 1); // machine factor, complete by f = -0.7
  const pts = [];
  // bars indexed -5..5 around the spine; pitch is already uniform (98)
  for (let j = -5; j <= 5; j++) {
    const i = Math.abs(j) - 1;
    const [w0, s0] = j === 0 ? [10, 0] : SPEC[4 - i];
    // book state (mirrored fan): near side spreads and widens with k,
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
    // book corner ys: left group leans one way, right group mirrors,
    // center stands straight
    const bookTL = j > 0 ? T + s : T;
    const bookTR = j > 0 ? T : T + s;
    const bookBL = j > 0 ? B : B - s;
    const bookBR = j > 0 ? B - s : B;
    // machine state: every slab identical, same lean, uniform pitch
    const W = lerp(w, DC_W, t);
    const CX = lerp(cx, 600 + j * 98, t);
    const tl = lerp(bookTL, T, t);
    const tr = lerp(bookTR, T + DC_S, t);
    const bl = lerp(bookBL, B - DC_S, t);
    const br = lerp(bookBR, B, t);
    const x0 = CX - W / 2;
    const x1 = CX + W / 2;
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
      target = Math.max(-0.85, Math.min(0.85, mouseF + scrollF));
      if (raf === null) raf = requestAnimationFrame(tick);
    };
    const onMove = (e) => {
      mouseF = (e.clientX / window.innerWidth - 0.5) * 1.7;
      retarget();
    };
    const onScroll = () => {
      scrollF = -Math.min(window.scrollY / 450, 1) * 0.85;
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
