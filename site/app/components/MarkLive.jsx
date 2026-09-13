"use client";

import { useEffect, useRef } from "react";

// The spine mark, alive: the pages fan toward the cursor over the central
// spine. On the side the mouse is on, spines spread apart and widen, so
// more of each page's rectangle turns into view; on the far side they tuck
// thin toward the spine. Geometry matches Mark.jsx at rest (f = 0). DOM is
// mutated directly inside rAF so nothing re-renders, and the listener
// respects prefers-reduced-motion.

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
  // f > 0: mouse right of center — right pages fan open (spread + widen,
  // flatter shear), left pages tuck (narrow, deeper shear). f < 0 mirrors.
  const openR = 1 + 0.14 * f;
  const openL = 1 - 0.14 * f;
  const faceR = Math.max(1 + 0.45 * f, 0.2);
  const faceL = Math.max(1 - 0.45 * f, 0.2);
  const pts = [];
  for (let i = 0; i < 5; i++) {
    const [w, s0] = SPEC[i];
    const d = 490 - i * 98;
    const wL = Math.max(w * faceL, 5);
    const wR = Math.max(w * faceR, 5);
    const sL = s0 * (1 + 0.3 * f);
    const sR = s0 * (1 - 0.3 * f);
    const cxL = 600 - d * openL;
    const cxR = 600 + d * openR;
    pts.push(
      `${cxL - wL / 2},${T} ${cxL + wL / 2},${T + sL} ${cxL + wL / 2},${B} ${cxL - wL / 2},${B - sL}`
    );
    pts.push(
      `${cxR - wR / 2},${T + sR} ${cxR + wR / 2},${T} ${cxR + wR / 2},${B - sR} ${cxR - wR / 2},${B}`
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
      target = Math.max(-0.8, Math.min(0.8, x * 1.8));
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
