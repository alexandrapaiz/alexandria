"use client";

import { useEffect, useRef } from "react";

// The library page's opening scene, with the same staged scroll as home.
// At rest this is the bookshelf: spines, a few leaning books, flat
// stacks, one fallen diagonal. Wheel input at the top is spent on the
// transformation while the page barely moves: leaning books straighten
// upright, the fallen book settles flat onto its stack, and small LED
// dots light near the tops of scattered spines — the shelves become
// server racks. Then the page holds a beat and glides to the archive.
// Scrolling up runs it all in reverse. Still under reduced motion.

const PITCH = 22;
const W = 9;
const BOOK = 150;
const ROWGAP = 70;

const ROWS = [
  [["v", 17], ["gap", 30], ["lean", -12], ["lean", -10], ["v", 34]],
  [["v", 26], ["gap", 40], ["v", 14], ["gap", 30], ["h", 3, 220]],
  [["v", 6], ["h", 6, 200], ["v", 39]],
  [["v", 2], ["lean", 14], ["v", 40], ["gap", 30], ["lean", -14], ["v", 6]],
  [["v", 14], ["lean", 16], ["gap", 10], ["fallen", 220], ["v", 29]],
];
const HEIGHT = ROWS.length * (BOOK + ROWGAP) - ROWGAP;

// p = 0 shelf at rest, p = 1 the rack (upright, flat, lit)
function shapes(p) {
  const lines = [];
  const leds = [];
  let spineIdx = 0;
  ROWS.forEach((row, r) => {
    const yTop = r * (BOOK + ROWGAP);
    const yBot = yTop + BOOK;
    let x = 0;
    for (const [t, a, b] of row) {
      if (t === "v") {
        for (let i = 0; i < a; i++) {
          lines.push([x + W / 2, yBot, x + W / 2, yTop]);
          if (spineIdx % 7 === 3) leds.push([x + W / 2, yTop + 26]);
          spineIdx += 1;
          x += PITCH;
        }
      } else if (t === "gap") {
        x += a;
      } else if (t === "lean") {
        const rad = (Math.abs(a) * Math.PI) / 180;
        const dxRest = Math.tan(rad) * BOOK * Math.sign(a);
        const dx = dxRest * (1 - p);
        lines.push([
          x + W / 2 + Math.max(dx, 0), yBot,
          x + W / 2 + Math.max(-dx, 0), yTop,
        ]);
        if (spineIdx % 7 === 3) leds.push([x + W / 2 + Math.max(-dx, 0), yTop + 26]);
        spineIdx += 1;
        x += PITCH + Math.abs(dxRest);
      } else if (t === "h") {
        for (let i = 0; i < a; i++) {
          const y = yBot - W / 2 - i * (W + 9);
          lines.push([x, y, x + b, y]);
        }
        x += b + PITCH;
      } else if (t === "fallen") {
        lines.push([x, yBot - W / 2, x + a, yBot - W / 2]);
        lines.push([x, yBot - W / 2 - 18, x + a, yBot - W / 2 - 18]);
        // the resting diagonal settles fully flat onto its stack
        const x1 = x + 10 + (x - (x + 10)) * p;
        const y1 = (yBot - 40) + (yBot - W / 2 - 36 - (yBot - 40)) * p;
        const x2 = (x + a - 15) + (x + a - (x + a - 15)) * p;
        const y2 = (yBot - 105) + (yBot - W / 2 - 36 - (yBot - 105)) * p;
        lines.push([x1, y1, x2, y2]);
        x += a + PITCH;
      }
    }
  });
  return { lines, leds };
}

export default function ShelvesLive(props) {
  const ref = useRef(null);

  useEffect(() => {
    const svg = ref.current;
    if (!svg) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      // no staging: everything visible, shelf at rest
      document.querySelector(".lib-scene2")?.classList.add("arrived");
      return;
    }

    const lineEls = svg.querySelectorAll("line");
    const dotEls = svg.querySelectorAll(".led-dots circle");
    const glowEls = svg.querySelectorAll(".led-glows circle");
    let cur = 0;
    let p = 0;
    let lastScrollY = 0;
    let raf = null;
    const MORPH_WHEEL = 700;

    const s = (x) => x * x * (3 - 2 * x);
    const apply = (v, tms) => {
      const { lines, leds } = shapes(v);
      lineEls.forEach((el, i) => {
        const [x1, y1, x2, y2] = lines[i];
        el.setAttribute("x1", x1);
        el.setAttribute("y1", y1);
        el.setAttribute("x2", x2);
        el.setAttribute("y2", y2);
      });
      // LEDs light through the second half of the transformation, each
      // glowing with a slow breath once lit
      const lit = Math.max(0, (v - 0.45) / 0.55);
      const r = 3.4 * lit;
      leds.forEach(([cx, cy], i) => {
        dotEls[i].setAttribute("cx", cx);
        dotEls[i].setAttribute("cy", cy);
        dotEls[i].setAttribute("r", r);
        const breath = 1 + 0.2 * Math.sin(tms / 300 + i * 1.7);
        glowEls[i].setAttribute("cx", cx);
        glowEls[i].setAttribute("cy", cy);
        glowEls[i].setAttribute("r", r * 2.5 * breath);
        glowEls[i].setAttribute("opacity", (0.85 * lit).toFixed(3));
      });
    };
    const tick = (tms) => {
      const target = lastScrollY > 130 ? 1 : s(s(p));
      cur += (target - cur) * 0.1;
      const settled = Math.abs(target - cur) <= 0.0005;
      if (settled) cur = target;
      apply(cur, tms || performance.now());
      // keep the frame loop alive while the LEDs are lit, so they breathe
      if (!settled || cur > 0.5) raf = requestAnimationFrame(tick);
      else raf = null;
    };
    const wake = () => {
      if (raf === null) raf = requestAnimationFrame(tick);
    };

    let advancing = false;
    let gliding = false;
    const glide = (toY) => {
      gliding = true;
      const fromY = window.scrollY;
      const t0 = performance.now();
      const ms = 850;
      const ease = (x) =>
        x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
      const step = (now) => {
        const u = Math.min((now - t0) / ms, 1);
        window.scrollTo(0, fromY + (toY - fromY) * ease(u));
        if (u < 1) requestAnimationFrame(step);
        else gliding = false;
      };
      requestAnimationFrame(step);
    };
    const sceneTop = () => {
      const el = document.querySelector(".lib-scene2");
      return el ? el.getBoundingClientRect().top + window.scrollY - 96 : 0;
    };

    const onWheel = (e) => {
      if (gliding) {
        e.preventDefault();
        return;
      }
      const sy = window.scrollY;
      if (sy < 90) {
        if (e.deltaY > 0 && p < 1) {
          e.preventDefault();
          p = Math.min(1, p + e.deltaY / MORPH_WHEEL);
          window.scrollBy(0, e.deltaY * 0.035);
          wake();
          if (p >= 1 && !advancing) {
            // linger on the finished rack, lights breathing, before the
            // flight to the archive
            advancing = true;
            setTimeout(() => glide(sceneTop()), 2200);
          }
        } else if (e.deltaY < 0 && p > 0) {
          e.preventDefault();
          p = Math.max(0, p + e.deltaY / MORPH_WHEEL);
          window.scrollBy(0, e.deltaY * 0.035);
          wake();
        }
        return;
      }
      if (e.deltaY < 0 && Math.abs(sy - sceneTop()) < 60) {
        e.preventDefault();
        glide(0);
      }
    };
    let settleTimer = null;
    const settle = () => {
      if (gliding) return;
      const sy = window.scrollY;
      const st = sceneTop();
      if (sy > 90 && sy < st - 40) {
        glide(sy < st / 2 && p < 1 ? 0 : st);
      }
    };
    const onScroll = () => {
      lastScrollY = window.scrollY;
      if (lastScrollY > 130) p = 1;
      if (advancing && lastScrollY < 60) advancing = false;
      // reveal the archive only as the header reaches the top
      document
        .querySelector(".lib-scene2")
        ?.classList.toggle("arrived", lastScrollY > sceneTop() - 180);
      if (settleTimer) clearTimeout(settleTimer);
      if (!gliding) settleTimer = setTimeout(settle, 170);
      wake();
    };

    window.addEventListener("wheel", onWheel, { passive: false });
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => {
      window.removeEventListener("wheel", onWheel);
      window.removeEventListener("scroll", onScroll);
      if (settleTimer) clearTimeout(settleTimer);
      if (raf !== null) cancelAnimationFrame(raf);
    };
  }, []);

  const init = shapes(0);
  return (
    <svg
      ref={ref}
      viewBox={`0 0 1240 ${HEIGHT}`}
      xmlns="http://www.w3.org/2000/svg"
      preserveAspectRatio="xMidYMid meet"
      aria-hidden="true"
      {...props}
    >
      <defs>
        <filter id="ledglow" x="-200%" y="-200%" width="500%" height="500%">
          <feGaussianBlur stdDeviation="5" />
        </filter>
      </defs>
      {init.lines.map(([x1, y1, x2, y2], i) => (
        <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="currentColor" strokeWidth={W} />
      ))}
      <g className="led-glows" filter="url(#ledglow)">
        {init.leds.map(([cx, cy], i) => (
          <circle key={`g${i}`} cx={cx} cy={cy} r="0" fill="#fff" opacity="0" />
        ))}
      </g>
      <g className="led-dots">
        {init.leds.map(([cx, cy], i) => (
          <circle key={`l${i}`} cx={cx} cy={cy} r="0" fill="#fff" />
        ))}
      </g>
    </svg>
  );
}
