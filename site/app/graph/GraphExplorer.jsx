"use client";

import { useEffect, useMemo, useRef, useState } from "react";

// The claim graph explorer. Canvas, no graph library: 214 linked claims and
// 238 edges is well inside what plain arithmetic draws at 60fps, and the canon
// wants a ledger proposal before a dependency arrives, not after.
//
// Four relations, four line treatments, and the one semantic red the owner
// approved for `contradicts` on 2026-09-25. Everything else on this surface is
// the site's four tokens.

const REL_ORDER = ["supports", "refines", "contradicts", "duplicates"];

const REL_STYLE = {
  supports: { dash: [], width: 1, stroke: "rgba(0,0,0,0.55)" },
  refines: { dash: [4, 3], width: 1, stroke: "rgba(134,134,139,0.95)" },
  contradicts: { dash: [], width: 1.3, stroke: "#c8102e" },
  duplicates: { dash: [1, 3], width: 1, stroke: "rgba(134,134,139,0.9)" },
};

// Grades come out of the database as enum-ish strings (pipeline/evidence.py).
// These are readings of the stored value, not new prose about the product.
const GRADE_LABEL = {
  controlled: "Controlled",
  field_measured: "Field measured",
  asserted: "Asserted",
  anecdote: "Anecdote",
};

export default function GraphExplorer({ claims, edges, topics, counts }) {
  const canvasRef = useRef(null);
  const wrapRef = useRef(null);
  const simRef = useRef(null);

  const [selected, setSelected] = useState(null);
  const [hovered, setHovered] = useState(null);
  const [query, setQuery] = useState("");
  const [topic, setTopic] = useState("");
  const [off, setOff] = useState(() => new Set());

  const byId = useMemo(() => new Map(claims.map((c) => [c.id, c])), [claims]);

  // Neighbours, precomputed once: the panel needs every neighbour with its
  // relation, and recomputing that per render at this volume is waste.
  const neighbours = useMemo(() => {
    const m = new Map();
    for (const c of claims) m.set(c.id, []);
    for (const e of edges) {
      m.get(e.from)?.push({ id: e.to, rel: e.rel, dir: "out", confidence: e.confidence });
      m.get(e.to)?.push({ id: e.from, rel: e.rel, dir: "in", confidence: e.confidence });
    }
    return m;
  }, [claims, edges]);

  const relCounts = useMemo(() => {
    const m = Object.fromEntries(REL_ORDER.map((r) => [r, 0]));
    for (const e of edges) if (m[e.rel] !== undefined) m[e.rel] += 1;
    return m;
  }, [edges]);

  // A claim matches when the search is empty or its text, id, or paper title
  // contains the query, AND the topic filter is unset or it carries the topic.
  const matches = useMemo(() => {
    const q = query.trim().toLowerCase();
    const set = new Set();
    for (const c of claims) {
      if (topic && !c.topics.includes(topic)) continue;
      if (q) {
        const hay = `${c.id} ${c.claim} ${c.paperTitle || ""}`.toLowerCase();
        if (!hay.includes(q)) continue;
      }
      set.add(c.id);
    }
    return set;
  }, [claims, query, topic]);

  const matchesRef = useRef(matches);
  const offRef = useRef(off);
  const selRef = useRef(selected);
  const hovRef = useRef(hovered);
  matchesRef.current = matches;
  offRef.current = off;
  selRef.current = selected;
  hovRef.current = hovered;

  // ---- layout and paint ----------------------------------------------------
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || claims.length === 0) return;
    const ctx = canvas.getContext("2d");
    let raf = 0;
    let dpr = Math.min(window.devicePixelRatio || 1, 2);

    const index = new Map(claims.map((c, i) => [c.id, i]));
    const N = claims.length;
    const links = edges
      .map((e) => ({ a: index.get(e.from), b: index.get(e.to), rel: e.rel }))
      .filter((l) => l.a !== undefined && l.b !== undefined);

    // Connected components, so the sim lays out an archipelago rather than
    // letting twenty small clusters drift to the edges. Union-find.
    const parent = Array.from({ length: N }, (_, i) => i);
    const find = (i) => {
      while (parent[i] !== i) { parent[i] = parent[parent[i]]; i = parent[i]; }
      return i;
    };
    for (const l of links) {
      const ra = find(l.a), rb = find(l.b);
      if (ra !== rb) parent[ra] = rb;
    }
    const groups = new Map();
    for (let i = 0; i < N; i++) {
      const r = find(i);
      if (!groups.has(r)) groups.set(r, []);
      groups.get(r).push(i);
    }
    // Biggest component first, so it takes the middle of the frame.
    const comps = [...groups.values()].sort((a, b) => b.length - a.length);

    // Each component gets a slot sized by sqrt(members). Slots are packed in
    // rows across the frame, largest first, which keeps the canvas evenly
    // inked instead of one dense knot and a lot of white.
    const slots = new Array(N);
    const radii = new Array(N);
    const total = comps.reduce((s, c) => s + Math.sqrt(c.length), 0);
    const scale = 0.62 / Math.max(total / 4.2, 1);
    let x = 0.08, y = 0.2, rowH = 0;
    for (const comp of comps) {
      const r = Math.max(0.035, Math.sqrt(comp.length) * scale);
      if (x + r * 2 > 0.94) { x = 0.08; y += rowH + 0.06; rowH = 0; }
      const cx = x + r, cy = y + r;
      for (const i of comp) { slots[i] = [cx, cy]; radii[i] = r; }
      x += r * 2 + 0.05;
      rowH = Math.max(rowH, r * 2);
    }
    // Recentre the whole packing vertically so it sits in the frame.
    const maxY = y + rowH;
    const shift = maxY > 0 ? (1 - maxY) / 2 : 0;
    for (let i = 0; i < N; i++) slots[i][1] += shift;

    // Seed inside the slot, with a deterministic jitter so a reload lands on
    // the same picture. A graph that reshuffles every visit cannot be talked
    // about with a colleague.
    const rand = (n) => { const s = Math.sin(n * 12.9898) * 43758.5453; return s - Math.floor(s); };
    const nodes = claims.map((c, i) => {
      const a = rand(c.id) * Math.PI * 2;
      const rr = Math.sqrt(rand(c.id + 7)) * radii[i] * 0.85;
      return { x: slots[i][0] + Math.cos(a) * rr, y: slots[i][1] + Math.sin(a) * rr, vx: 0, vy: 0, deg: 0 };
    });
    for (const l of links) { nodes[l.a].deg += 1; nodes[l.b].deg += 1; }

    const step = () => {
      for (let i = 0; i < N; i++) {
        const a = nodes[i];
        // pull toward the component's slot, not toward the frame's centre
        a.vx += (slots[i][0] - a.x) * 0.006;
        a.vy += (slots[i][1] - a.y) * 0.006;
        for (let j = i + 1; j < N; j++) {
          const b = nodes[j];
          const dx = a.x - b.x, dy = a.y - b.y;
          const d2 = dx * dx + dy * dy + 0.00002;
          if (d2 < 0.01) {
            const f = 0.0000022 / d2;
            a.vx += dx * f; a.vy += dy * f;
            b.vx -= dx * f; b.vy -= dy * f;
          }
        }
      }
      for (const l of links) {
        const a = nodes[l.a], b = nodes[l.b];
        const dx = b.x - a.x, dy = b.y - a.y;
        const d = Math.hypot(dx, dy) || 0.0001;
        const pull = (d - 0.035) * 0.012;
        a.vx += (dx / d) * pull; a.vy += (dy / d) * pull;
        b.vx -= (dx / d) * pull; b.vy -= (dy / d) * pull;
      }
      for (const n of nodes) {
        n.x = Math.min(0.985, Math.max(0.015, n.x + n.vx));
        n.y = Math.min(0.975, Math.max(0.025, n.y + n.vy));
        n.vx *= 0.86; n.vy *= 0.86;
      }
    };

    const fit = () => {
      const r = wrapRef.current.getBoundingClientRect();
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.max(1, Math.round(r.width * dpr));
      canvas.height = Math.max(1, Math.round(r.height * dpr));
    };

    const draw = () => {
      const w = canvas.width, h = canvas.height;
      ctx.clearRect(0, 0, w, h);
      const m = matchesRef.current;
      const hiddenRels = offRef.current;
      const sel = selRef.current;
      const hov = hovRef.current;
      const focus = sel ?? hov;
      const focusIdx = focus == null ? -1 : index.get(focus);
      const adj = new Set();
      if (focusIdx >= 0) {
        for (const l of links) {
          if (l.a === focusIdx) adj.add(l.b);
          if (l.b === focusIdx) adj.add(l.a);
        }
      }
      const filtering = m.size !== N;
      const px = (v) => v * dpr;

      // edges first, so nodes always sit on top of their own lines
      for (const l of links) {
        if (hiddenRels.has(l.rel)) continue;
        const s = REL_STYLE[l.rel] || REL_STYLE.supports;
        const a = nodes[l.a], b = nodes[l.b];
        const onFocus = focusIdx >= 0 && (l.a === focusIdx || l.b === focusIdx);
        const lit = !filtering || (m.has(claims[l.a].id) && m.has(claims[l.b].id));
        let alpha = lit ? 1 : 0.12;
        if (focusIdx >= 0) alpha *= onFocus ? 1 : 0.18;
        ctx.save();
        ctx.globalAlpha = alpha;
        ctx.beginPath();
        ctx.setLineDash(s.dash.map((d) => px(d)));
        ctx.lineWidth = px(onFocus ? s.width + 0.5 : s.width);
        ctx.strokeStyle = s.stroke;
        ctx.moveTo(a.x * w, a.y * h);
        ctx.lineTo(b.x * w, b.y * h);
        ctx.stroke();
        ctx.restore();
      }
      ctx.setLineDash([]);

      for (let i = 0; i < N; i++) {
        const n = nodes[i];
        const id = claims[i].id;
        const lit = !filtering || m.has(id);
        const isFocus = i === focusIdx;
        const isAdj = adj.has(i);
        let alpha = lit ? 1 : 0.14;
        if (focusIdx >= 0 && !isFocus && !isAdj) alpha *= 0.28;
        const r = px(2.5 + Math.min(n.deg, 8) * 0.22 + (isFocus ? 2.2 : 0));
        ctx.save();
        ctx.globalAlpha = alpha;
        ctx.beginPath();
        ctx.arc(n.x * w, n.y * h, r, 0, Math.PI * 2);
        ctx.fillStyle = "#000000";
        ctx.fill();
        if (isFocus) {
          // the selection ring: paper gap, then ink, so the node reads as
          // picked up rather than merely bigger
          ctx.beginPath();
          ctx.arc(n.x * w, n.y * h, r + px(3), 0, Math.PI * 2);
          ctx.lineWidth = px(1);
          ctx.strokeStyle = "#000000";
          ctx.stroke();
        }
        ctx.restore();
      }
    };

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    // Warm start: the first painted frame is already a graph, never a scatter.
    for (let i = 0; i < 260; i++) step();

    let ticks = 0;
    const loop = () => {
      if (ticks < 420) { step(); ticks += 1; }
      draw();
      raf = requestAnimationFrame(loop);
    };

    fit();
    if (reduced) {
      // Reduced motion gets the settled layout, drawn once, and redrawn only
      // when the reader changes something. A designed reduced experience.
      for (let i = 0; i < 420; i++) step();
      draw();
      simRef.current = { nodes, index, redraw: draw, fit };
      const onResize = () => { fit(); draw(); };
      window.addEventListener("resize", onResize);
      return () => window.removeEventListener("resize", onResize);
    }
    loop();
    simRef.current = { nodes, index, redraw: draw, fit };
    const onResize = () => fit();
    window.addEventListener("resize", onResize);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", onResize);
    };
  }, [claims, edges]);

  // Reduced motion draws on demand; the animated path is already redrawing.
  useEffect(() => { simRef.current?.redraw?.(); }, [matches, off, selected, hovered]);

  // ---- hit testing ---------------------------------------------------------
  const pick = (ev) => {
    const sim = simRef.current;
    const canvas = canvasRef.current;
    if (!sim || !canvas) return null;
    const r = canvas.getBoundingClientRect();
    const x = (ev.clientX - r.left) / r.width;
    const y = (ev.clientY - r.top) / r.height;
    // Generous radius: a 10px grab on a 5px dot, per motion.md's note that a
    // target which accepts more finger than it draws is craft.
    const tolX = 11 / r.width, tolY = 11 / r.height;
    let best = null, bestD = Infinity;
    for (let i = 0; i < claims.length; i++) {
      if (matches.size !== claims.length && !matches.has(claims[i].id)) continue;
      const n = sim.nodes[i];
      const dx = (n.x - x) / tolX, dy = (n.y - y) / tolY;
      const d = dx * dx + dy * dy;
      if (d < 1 && d < bestD) { bestD = d; best = claims[i].id; }
    }
    return best;
  };

  const sel = selected == null ? null : byId.get(selected);
  const selNeighbours = selected == null ? [] : (neighbours.get(selected) || []);

  const toggleRel = (rel) =>
    setOff((prev) => {
      const next = new Set(prev);
      next.has(rel) ? next.delete(rel) : next.add(rel);
      return next;
    });

  const shown = matches.size;

  return (
    <div className="gx">
      <div className="gx-controls">
        <div className="gx-search">
          <input
            type="search"
            className="gx-input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search claims"
            aria-label="Search claims"
          />
        </div>
        <div className="gx-topics">
          <select
            className="gx-select"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            aria-label="Filter by topic"
          >
            <option value="">All topics</option>
            {topics.map((t) => (
              <option key={t.name} value={t.name}>
                {t.name} ({t.n})
              </option>
            ))}
          </select>
        </div>
        <p className="gx-count" aria-live="polite">
          {shown} of {counts.linked} linked claims
        </p>
      </div>

      <div className="gx-body">
        <div className="gx-stage" ref={wrapRef}>
          <canvas
            ref={canvasRef}
            className="gx-canvas"
            onMouseMove={(e) => {
              const id = pick(e);
              setHovered(id);
              e.currentTarget.style.cursor = id ? "pointer" : "default";
            }}
            onMouseLeave={() => setHovered(null)}
            onClick={(e) => setSelected(pick(e))}
          />
          {shown === 0 && (
            <p className="gx-empty">No claim matches that filter.</p>
          )}
        </div>

        <aside className="gx-panel" aria-live="polite">
          {sel ? (
            <>
              <div className="gx-panel-head">
                <span className="gx-id">Claim {sel.id}</span>
                <button
                  type="button"
                  className="gx-close"
                  onClick={() => setSelected(null)}
                  aria-label="Close claim"
                >
                  Close
                </button>
              </div>
              <p className="gx-claim">{sel.claim}</p>

              <dl className="gx-meta">
                <dt>Evidence</dt>
                <dd>{sel.grade ? GRADE_LABEL[sel.grade] || sel.grade : "Ungraded"}</dd>
                <dt>Paper</dt>
                <dd>
                  {sel.paperUrl ? (
                    <a href={sel.paperUrl} target="_blank" rel="noreferrer" className="gx-paper">
                      {sel.paperTitle || sel.paperId}
                    </a>
                  ) : (
                    sel.paperTitle || sel.paperId
                  )}
                </dd>
                {sel.topics.length > 0 && (
                  <>
                    <dt>Topics</dt>
                    <dd>{sel.topics.join(", ")}</dd>
                  </>
                )}
              </dl>

              <h3 className="gx-sub">
                {selNeighbours.length} {selNeighbours.length === 1 ? "link" : "links"}
              </h3>
              <ul className="gx-neighbours">
                {selNeighbours.map((n, i) => {
                  const other = byId.get(n.id);
                  if (!other) return null;
                  return (
                    <li key={`${n.id}-${n.rel}-${n.dir}-${i}`}>
                      <button type="button" onClick={() => setSelected(n.id)}>
                        <span className={`gx-rel gx-rel-${n.rel}`}>
                          {n.dir === "out" ? n.rel : `${n.rel} by`}
                        </span>
                        <span className="gx-neighbour-text">{other.claim}</span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </>
          ) : (
            <p className="gx-hint">Select a claim to read it with its links.</p>
          )}
        </aside>
      </div>

      <ul className="gx-legend">
        {REL_ORDER.map((rel) => (
          <li key={rel}>
            <button
              type="button"
              className={`gx-legend-btn${off.has(rel) ? " is-off" : ""}`}
              onClick={() => toggleRel(rel)}
              aria-pressed={!off.has(rel)}
            >
              <span className={`gx-swatch gx-swatch-${rel}`} aria-hidden="true" />
              <span className="gx-legend-label">{rel}</span>
              <span className="gx-legend-n">{relCounts[rel]}</span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
