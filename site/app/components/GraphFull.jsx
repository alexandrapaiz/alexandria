"use client";

import { useEffect, useRef } from "react";
import { T, EDGES, hasProcedure } from "../../lib/graph-data";

// The claim graph at full size, inverted from the wordmark embed: black ink
// on paper. Solid dots are claims, hollow dots carry procedures. Supports is
// a hairline, refines heavier, contradicts dashed. Force layout, no library.
export default function GraphFull() {
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

    const N = T.length;
    // seed each node near its topic's angle so clusters form fast
    const nodes = Array.from({ length: N }, (_, i) => {
      const a = (T[i] / 15) * Math.PI * 2 + (Math.random() - 0.5) * 0.9;
      const r = 0.18 + Math.random() * 0.24;
      return {
        x: 0.5 + Math.cos(a) * r,
        y: 0.5 + Math.sin(a) * r * 0.85,
        vx: 0,
        vy: 0,
      };
    });
    const links = EDGES.map(([f, t, rel]) => [f - 1, t - 1, rel]);

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let ticks = 0;

    const step = () => {
      for (let i = 0; i < N; i++) {
        const a = nodes[i];
        // centering
        a.vx += (0.5 - a.x) * 0.0004;
        a.vy += (0.5 - a.y) * 0.0006;
        // repulsion
        for (let j = i + 1; j < N; j++) {
          const b = nodes[j];
          const dx = a.x - b.x;
          const dy = a.y - b.y;
          const d2 = dx * dx + dy * dy + 0.0001;
          if (d2 < 0.02) {
            const f = 0.0000035 / d2;
            a.vx += dx * f; a.vy += dy * f;
            b.vx -= dx * f; b.vy -= dy * f;
          }
        }
      }
      // springs
      for (const [f, t] of links) {
        const a = nodes[f];
        const b = nodes[t];
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const d = Math.hypot(dx, dy) || 0.001;
        const pull = (d - 0.06) * 0.002;
        a.vx += (dx / d) * pull; a.vy += (dy / d) * pull;
        b.vx -= (dx / d) * pull; b.vy -= (dy / d) * pull;
      }
      for (const n of nodes) {
        n.x = Math.min(0.98, Math.max(0.02, n.x + n.vx));
        n.y = Math.min(0.96, Math.max(0.04, n.y + n.vy));
        n.vx *= 0.9;
        n.vy *= 0.9;
      }
    };

    const draw = () => {
      const w = canvas.width;
      const h = canvas.height;
      ctx.clearRect(0, 0, w, h);

      for (const [f, t, rel] of links) {
        const a = nodes[f];
        const b = nodes[t];
        ctx.beginPath();
        ctx.setLineDash(rel === 2 ? [4 * dpr, 4 * dpr] : []);
        ctx.lineWidth = rel === 1 ? 1.3 * dpr : 0.7 * dpr;
        ctx.strokeStyle = rel === 2 ? "rgba(0,0,0,0.75)" : "rgba(0,0,0,0.28)";
        ctx.moveTo(a.x * w, a.y * h);
        ctx.lineTo(b.x * w, b.y * h);
        ctx.stroke();
      }
      ctx.setLineDash([]);

      for (let i = 0; i < N; i++) {
        const n = nodes[i];
        ctx.beginPath();
        ctx.arc(n.x * w, n.y * h, 2.6 * dpr, 0, Math.PI * 2);
        if (hasProcedure(i + 1)) {
          ctx.fillStyle = "#fff";
          ctx.fill();
          ctx.lineWidth = 1.2 * dpr;
          ctx.strokeStyle = "#000";
          ctx.stroke();
        } else {
          ctx.fillStyle = "#000";
          ctx.fill();
        }
      }
    };

    const loop = () => {
      step();
      ticks += 1;
      draw();
      // settle after warm-up unless motion is welcome
      if (ticks < 900 && !(reduced && ticks > 260)) raf = requestAnimationFrame(loop);
    };
    // warm start so the first frame is already a graph, not a scatter
    for (let i = 0; i < 200; i++) step();
    loop();

    window.addEventListener("resize", fit);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", fit);
    };
  }, []);

  return <canvas ref={ref} className="graph-canvas" aria-hidden="true" />;
}
