"use client";

import { useEffect, useRef } from "react";

// The mark holds both identities of the library. Mouse right (or scroll to
// the top) and it is a codex: pages fan open over the central spine, shear
// deepening, the near side turning its faces into view. Mouse left or
// scroll down and it squares into the machine: shears flatten, widths
// equalize, and each spine splits into stacked units — a rack row in a
// data center. One parameter f in [-0.85, 0.85] morphs between them,
// driven by cursor x and scroll depth, eased with a rAF lerp, mutating the
// SVG directly so nothing re-renders. Still under prefers-reduced-motion.

const SPEC = [
  [72, 170],
  [60, 140],
  [50, 110],
  [40, 80],
  [26, 50],
];
const T = 60;
const B = 840;
const SPAN = B - T;

// bars: five per side plus the center spine; every bar renders as three
// stacked segments so the brick morph can open gaps between them
function bars(f) {
  const k = Math.max(f, 0); // book factor
  const t = Math.min(Math.max(-f, 0) / 0.7, 1); // brick factor, complete by f = -0.7
  const out = [];
  for (let i = 0; i < 5; i++) {
    const [w0, s0] = SPEC[i];
    const d = 490 - i * 98;
    // book: near side spreads and widens, far side tucks thin and edge-on
    const wL = Math.max(w0 * (1 - 0.45 * k), 5);
    const wR = Math.max(w0 * (1 + 0.45 * k), 5);
    const sL = s0 * (1 + 0.3 * k);
    const sR = s0 * (1 - 0.3 * k);
    const cxL = 600 - d * (1 - 0.14 * k);
    const cxR = 600 + d * (1 + 0.14 * k);
    // brick: everything converges on uniform slabs with square ends
    out.push({ cx: cxL, w: wL + (46 - wL) * t, s: sL * (1 - t), side: -1 });
    out.push({ cx: cxR, w: wR + (46 - wR) * t, s: sR * (1 - t), side: 1 });
  }
  out.push({ cx: 600, w: 10 + 36 * t, s: 0, side: 0 });
  return { list: out, gap: 26 * t };
}

function compute(f) {
  const { list, gap } = bars(f);
  const h = (SPAN - 2 * gap) / 3;
  const ov = gap > 0.5 ? 0 : 2; // overlap segments when touching, no seams
  const pts = [];
  for (const { cx, w, s, side } of list) {
    const x0 = cx - w / 2;
    const x1 = cx + w / 2;
    const y1 = T + h;
    const y2a = T + h + gap;
    const y2b = T + 2 * h + gap;
    const y3a = T + 2 * h + 2 * gap;
    // top segment carries the top cap's shear
    if (side < 0) pts.push(`${x0},${T} ${x1},${T + s} ${x1},${y1 + ov} ${x0},${y1 + ov}`);
    else if (side > 0) pts.push(`${x0},${T + s} ${x1},${T} ${x1},${y1 + ov} ${x0},${y1 + ov}`);
    else pts.push(`${x0},${T} ${x1},${T} ${x1},${y1 + ov} ${x0},${y1 + ov}`);
    // middle segment is always a slab
    pts.push(`${x0},${y2a - ov} ${x1},${y2a - ov} ${x1},${y2b + ov} ${x0},${y2b + ov}`);
    // bottom segment carries the bottom cap's shear
    if (side < 0) pts.push(`${x0},${y3a - ov} ${x1},${y3a - ov} ${x1},${B} ${x0},${B - s}`);
    else if (side > 0) pts.push(`${x0},${y3a - ov} ${x1},${y3a - ov} ${x1},${B - s} ${x0},${B}`);
    else pts.push(`${x0},${y3a - ov} ${x1},${y3a - ov} ${x1},${B} ${x0},${B}`);
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
