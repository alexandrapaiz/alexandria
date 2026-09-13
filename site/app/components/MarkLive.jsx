"use client";

import { useEffect, useRef } from "react";

// The spine mark, alive: as the mouse moves across the page the fan of
// pages leans and opens a little, like a book easing open and closed.
// Geometry matches Mark.jsx at rest (f = 0); f in [-0.65, 0.65] deepens
// the shear and spreads the spines. DOM is mutated directly inside rAF so
// nothing re-renders, and the listener respects prefers-reduced-motion.

const SPEC = [
  [72, 170],
  [60, 140],
  [50, 110],
  [40, 80],
  [26, 50],
];
const H = 900;
const T = 60;
const B = H - 60;

function compute(f) {
  const pts = [];
  for (let i = 0; i < 5; i++) {
    const [w, s0] = SPEC[i];
    const s = s0 * (1 + 0.5 * f);
    const spread = (5 - i) * 9 * f;
    const cxL = 110 + i * 98 - spread;
    const cxR = 1090 - i * 98 + spread;
    pts.push(
      `${cxL - w / 2},${T} ${cxL + w / 2},${T + s} ${cxL + w / 2},${B} ${cxL - w / 2},${B - s}`
    );
    pts.push(
      `${cxR - w / 2},${T + s} ${cxR + w / 2},${T} ${cxR + w / 2},${B - s} ${cxR - w / 2},${B}`
    );
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
    const onMove = (e) => {
      const x = e.clientX / window.innerWidth - 0.5;
      target = Math.max(-0.65, Math.min(0.65, x * 1.4));
      if (raf === null) raf = requestAnimationFrame(tick);
    };

    window.addEventListener("mousemove", onMove);
    return () => {
      window.removeEventListener("mousemove", onMove);
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
      <rect x="595" y={T} width="10" height={B - T} fill="currentColor" />
    </svg>
  );
}
