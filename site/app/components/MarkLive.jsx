"use client";

import { useEffect, useRef } from "react";

// The mark holds both identities of the library. Mouse right (or the top
// of the page) and it is a codex: pages fan open over the central spine,
// shear deepening, the near side turning its faces into view. Mouse left
// or scroll down and it squares into the machine: shears flatten and the
// widths equalize into a uniform row of full-height slabs. Every bar stays
// one unbroken page in both states. One parameter f in [-0.85, 0.85]
// drives the morph from cursor x plus scroll depth, eased with a rAF
// lerp, mutating the SVG directly so nothing re-renders. Still under
// prefers-reduced-motion.

const SPEC = [
  [72, 170],
  [60, 140],
  [50, 110],
  [40, 80],
  [26, 50],
];
const T = 60;
const B = 840;

function compute(f) {
  const k = Math.max(f, 0); // book factor
  const t = Math.min(Math.max(-f, 0) / 0.7, 1); // brick factor, complete by f = -0.7
  const pts = [];
  for (let i = 0; i < 5; i++) {
    const [w0, s0] = SPEC[i];
    const d = 490 - i * 98;
    // book: near side spreads and widens, far side tucks thin and edge-on
    let wL = Math.max(w0 * (1 - 0.45 * k), 5);
    let wR = Math.max(w0 * (1 + 0.45 * k), 5);
    let sL = s0 * (1 + 0.3 * k);
    let sR = s0 * (1 - 0.3 * k);
    const cxL = 600 - d * (1 - 0.14 * k);
    const cxR = 600 + d * (1 + 0.14 * k);
    // brick: converge on uniform square-ended slabs
    wL += (46 - wL) * t;
    wR += (46 - wR) * t;
    sL *= 1 - t;
    sR *= 1 - t;
    pts.push(
      `${cxL - wL / 2},${T} ${cxL + wL / 2},${T + sL} ${cxL + wL / 2},${B} ${cxL - wL / 2},${B - sL}`
    );
    pts.push(
      `${cxR - wR / 2},${T + sR} ${cxR + wR / 2},${T} ${cxR + wR / 2},${B - sR} ${cxR - wR / 2},${B}`
    );
  }
  const wC = 10 + 36 * t;
  pts.push(`${600 - wC / 2},${T} ${600 + wC / 2},${T} ${600 + wC / 2},${B} ${600 - wC / 2},${B}`);
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
