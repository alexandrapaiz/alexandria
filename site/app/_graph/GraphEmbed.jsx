"use client";

import { useEffect, useRef } from "react";

// The one moving thing on the page: a miniature of the live claim graph,
// grayscale, embedded inside the wordmark the way a photograph sits inside
// a headline. Pure canvas, no library.
export default function GraphEmbed() {
  const ref = useRef(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let raf;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const fit = () => {
      const r = canvas.getBoundingClientRect();
      canvas.width = r.width * dpr;
      canvas.height = r.height * dpr;
    };
    fit();

    const N = 34;
    const nodes = Array.from({ length: N }, () => ({
      x: Math.random(),
      y: Math.random(),
      vx: (Math.random() - 0.5) * 0.0012,
      vy: (Math.random() - 0.5) * 0.0012,
      r: 1.1 + Math.random() * 1.9,
    }));

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const draw = () => {
      const w = canvas.width;
      const h = canvas.height;
      ctx.fillStyle = "#000";
      ctx.fillRect(0, 0, w, h);

      if (!reduced) {
        for (const n of nodes) {
          n.x += n.vx;
          n.y += n.vy;
          if (n.x < 0.02 || n.x > 0.98) n.vx *= -1;
          if (n.y < 0.06 || n.y > 0.94) n.vy *= -1;
        }
      }

      for (let i = 0; i < N; i++) {
        for (let j = i + 1; j < N; j++) {
          const a = nodes[i];
          const b = nodes[j];
          const dx = (a.x - b.x) * (w / h);
          const dy = a.y - b.y;
          const d = Math.hypot(dx, dy);
          if (d < 0.22) {
            ctx.strokeStyle = `rgba(255,255,255,${(0.6 * (1 - d / 0.22)).toFixed(3)})`;
            ctx.lineWidth = dpr * 0.8;
            ctx.beginPath();
            ctx.moveTo(a.x * w, a.y * h);
            ctx.lineTo(b.x * w, b.y * h);
            ctx.stroke();
          }
        }
      }

      ctx.fillStyle = "#fff";
      for (const n of nodes) {
        ctx.beginPath();
        ctx.arc(n.x * w, n.y * h, n.r * dpr, 0, Math.PI * 2);
        ctx.fill();
      }

      if (!reduced) raf = requestAnimationFrame(draw);
    };

    draw();
    window.addEventListener("resize", fit);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", fit);
    };
  }, []);

  return <canvas ref={ref} aria-hidden="true" />;
}
