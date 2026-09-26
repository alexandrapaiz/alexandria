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
    let dpr = Math.min(window.devicePixelRatio || 1, 2);

    const index = new Map(claims.map((c, i) => [c.id, i]));
    const N = claims.length;
    const links = edges
      .map((e) => ({ a: index.get(e.from), b: index.get(e.to), rel: e.rel }))
      .filter((l) => l.a !== undefined && l.b !== undefined);

    // Connected components. At 214 linked claims over 238 edges the graph is
    // an archipelago, not one island: roughly thirty components, one large,
    // and a long tail of pairs. Laying that out well is the whole problem.
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
    const comps = [...groups.values()].sort((a, b) => b.length - a.length);

    const nodes = claims.map(() => ({ x: 0, y: 0, vx: 0, vy: 0, deg: 0 }));
    for (const l of links) { nodes[l.a].deg += 1; nodes[l.b].deg += 1; }

    // Deterministic jitter, so a reload lands on the same picture. A graph
    // that reshuffles every visit cannot be talked about with a colleague.
    const rand = (n) => { const s = Math.sin(n * 12.9898) * 43758.5453; return s - Math.floor(s); };

    const slots = new Array(N);
    const LINK_REST = 0.055;

    // Greedy circle packing, largest component first, each new circle placed
    // at the smallest spiral radius where it touches nothing already placed.
    // This replaces the row packer that shipped in the first draft of this
    // component: rows put every small component at one y, and a pair whose
    // spring rest length exceeded its slot smeared sideways into its
    // neighbours, so the top and bottom of the canvas read as dotted rules
    // rather than as claims. Bubble packing has no row to collapse onto.
    const layout = () => {
      const placed = [];
      // Bias the spiral to the stage's shape. A circular packing on a 870x620
      // stage fits by height and leaves the sides empty; stretching the
      // placement axis fills the frame without distorting any component,
      // because the overlap test below still uses true distance.
      const box = wrapRef.current.getBoundingClientRect();
      const aspect = Math.min(Math.max(box.width / Math.max(box.height, 1), 0.6), 2.2);
      for (const comp of comps) {
        // radius that comfortably holds `comp.length` nodes at the spring's
        // rest length, floored so a pair is still a visible object
        const r = Math.max(LINK_REST * 0.75, Math.sqrt(comp.length) * LINK_REST * 1.05);
        let cx = 0, cy = 0;
        if (placed.length === 0) {
          cx = 0; cy = 0;
        } else {
          const pad = LINK_REST * 0.55;
          let found = false;
          // phyllotaxis spiral: even coverage, no directional bias
          for (let k = 1; k < 6000 && !found; k++) {
            const a = k * 2.399963;
            const rad = Math.sqrt(k) * LINK_REST * 0.42;
            const px = Math.cos(a) * rad * aspect, py = Math.sin(a) * rad;
            let ok = true;
            for (const q of placed) {
              if (Math.hypot(px - q.x, py - q.y) < q.r + r + pad) { ok = false; break; }
            }
            if (ok) { cx = px; cy = py; found = true; }
          }
        }
        placed.push({ x: cx, y: cy, r });
        for (const i of comp) {
          slots[i] = [cx, cy, r];
          const a = rand(claims[i].id) * Math.PI * 2;
          const rr = Math.sqrt(rand(claims[i].id + 7)) * r * 0.8;
          nodes[i].x = cx + Math.cos(a) * rr;
          nodes[i].y = cy + Math.sin(a) * rr;
          nodes[i].vx = 0; nodes[i].vy = 0;
        }
      }
    };

    // Repulsion tuned against the spring rather than guessed. Two nodes sit at
    // equilibrium where K/d balances the spring's 0.016 * (d - rest); solving
    // for a comfortable d of about 0.07 gives K near 1.6e-5. The first tuning
    // used 3e-6, which is five times too weak, and every component collapsed
    // into a knot where no individual edge could be read.
    const K = 0.000016;

    const step = () => {
      for (let i = 0; i < N; i++) {
        const a = nodes[i];
        // Containment, not attraction: a component is held inside its own
        // bubble and is free to open up anywhere within it. A centre-seeking
        // force compresses exactly the structure this page exists to show.
        const dx0 = a.x - slots[i][0], dy0 = a.y - slots[i][1];
        const d0 = Math.hypot(dx0, dy0);
        if (d0 > slots[i][2]) {
          const over = (d0 - slots[i][2]) * 0.06;
          a.vx -= (dx0 / d0) * over;
          a.vy -= (dy0 / d0) * over;
        }
        for (let j = i + 1; j < N; j++) {
          const b = nodes[j];
          const dx = a.x - b.x, dy = a.y - b.y;
          const d2 = dx * dx + dy * dy + 0.00002;
          if (d2 < 0.03) {
            const f = K / d2;
            a.vx += dx * f; a.vy += dy * f;
            b.vx -= dx * f; b.vy -= dy * f;
          }
        }
      }
      for (const l of links) {
        const a = nodes[l.a], b = nodes[l.b];
        const dx = b.x - a.x, dy = b.y - a.y;
        const d = Math.hypot(dx, dy) || 0.0001;
        const pull = (d - LINK_REST) * 0.016;
        a.vx += (dx / d) * pull; a.vy += (dy / d) * pull;
        b.vx -= (dx / d) * pull; b.vy -= (dy / d) * pull;
      }
      for (const n of nodes) {
        n.x += n.vx; n.y += n.vy;
        n.vx *= 0.84; n.vy *= 0.84;
      }
    };

    // The view transform. Computed from the settled bounds rather than
    // assumed, so the graph fills the stage at any aspect and the layout is
    // never stretched by drawing unit coordinates onto a non-square canvas,
    // which is what flattened the first draft horizontally.
    let view = { s: 1, ox: 0, oy: 0 };
    const frame = () => {
      let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
      for (const n of nodes) {
        if (n.x < minX) minX = n.x; if (n.x > maxX) maxX = n.x;
        if (n.y < minY) minY = n.y; if (n.y > maxY) maxY = n.y;
      }
      const pad = 26 * dpr;
      const w = canvas.width - pad * 2, h = canvas.height - pad * 2;
      const gw = Math.max(maxX - minX, 0.001), gh = Math.max(maxY - minY, 0.001);
      const s = Math.min(w / gw, h / gh);
      view = {
        s,
        ox: pad + (w - gw * s) / 2 - minX * s,
        oy: pad + (h - gh * s) / 2 - minY * s,
      };
    };
    const toPx = (n) => [n.x * view.s + view.ox, n.y * view.s + view.oy];

    const draw = () => {
      const w = canvas.width, h = canvas.height;
      ctx.clearRect(0, 0, w, h);
      const m = matchesRef.current;
      const hiddenRels = offRef.current;
      // Refinement 1, 2026-09-26. Hover and selection were one code path, so
      // moving the cursor over a single claim greyed out the other 213. That
      // is the heaviest response in the component fired by its lightest input,
      // and it reverses Freiberg's order: feedback the instant the input
      // starts, the committed state only past a threshold. Hover now emphasises
      // locally and dims nothing; selection is still the heavy state.
      const selIdx = selRef.current == null ? -1 : index.get(selRef.current);
      const hovIdx = hovRef.current == null ? -1 : index.get(hovRef.current);
      const adj = new Set();
      if (selIdx >= 0) {
        for (const l of links) {
          if (l.a === selIdx) adj.add(l.b);
          if (l.b === selIdx) adj.add(l.a);
        }
      }
      const filtering = m.size !== N;

      for (const l of links) {
        if (hiddenRels.has(l.rel)) continue;
        const st = REL_STYLE[l.rel] || REL_STYLE.supports;
        const [ax, ay] = toPx(nodes[l.a]);
        const [bx, by] = toPx(nodes[l.b]);
        const onSel = selIdx >= 0 && (l.a === selIdx || l.b === selIdx);
        const onHov = hovIdx >= 0 && (l.a === hovIdx || l.b === hovIdx);
        const lit = !filtering || (m.has(claims[l.a].id) && m.has(claims[l.b].id));
        let alpha = lit ? 1 : 0.12;
        if (selIdx >= 0) alpha *= onSel ? 1 : 0.22;
        ctx.save();
        ctx.globalAlpha = alpha;
        ctx.beginPath();
        ctx.setLineDash(st.dash.map((d) => d * dpr));
        ctx.lineWidth = (onSel || onHov ? st.width + 0.6 : st.width) * dpr;
        ctx.strokeStyle = st.stroke;
        ctx.moveTo(ax, ay);
        ctx.lineTo(bx, by);
        ctx.stroke();
        ctx.restore();
      }
      ctx.setLineDash([]);

      for (let i = 0; i < N; i++) {
        const id = claims[i].id;
        const lit = !filtering || m.has(id);
        const isSel = i === selIdx;
        const isHov = i === hovIdx;
        const isAdj = adj.has(i);
        let alpha = lit ? 1 : 0.14;
        if (selIdx >= 0 && !isSel && !isAdj) alpha *= 0.35;
        const [px, py] = toPx(nodes[i]);
        const grow = isSel ? 2 : isHov ? 1.6 : 0;
        const r = (2.4 + Math.min(nodes[i].deg, 8) * 0.22 + grow) * dpr;
        ctx.save();
        ctx.globalAlpha = alpha;
        ctx.beginPath();
        ctx.arc(px, py, r, 0, Math.PI * 2);
        ctx.fillStyle = "#000000";
        ctx.fill();
        if (isSel) {
          // paper gap, then ink: the node reads as picked up, not just bigger.
          // The ring is selection's alone; hover gets size and edge weight, so
          // the two states never read as the same commitment.
          ctx.beginPath();
          ctx.arc(px, py, r + 3.5 * dpr, 0, Math.PI * 2);
          ctx.lineWidth = 1 * dpr;
          ctx.strokeStyle = "#000000";
          ctx.stroke();
        }
        ctx.restore();
      }
    };

    const fit = () => {
      const r = wrapRef.current.getBoundingClientRect();
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.max(1, Math.round(r.width * dpr));
      canvas.height = Math.max(1, Math.round(r.height * dpr));
      frame();
      draw();
    };

    // Settled before the first paint, and no animation loop after it.
    // motion.md: a surface a subscriber works in is high-frequency and gets no
    // entrance choreography. The page's one choreographed moment is the mark
    // on the home page, and it stays the only one. The canvas repaints on
    // interaction, which is feedback, and never on a timer.
    layout();
    for (let i = 0; i < 700; i++) step();

    fit();
    simRef.current = { nodes, index, redraw: draw, toPx, canvas };
    // A ResizeObserver, not a window listener: the first fit() can run before
    // the scrollbar has settled, which left the backing store a couple of
    // pixels wider than its own CSS box and scaled every coordinate by half a
    // percent. The observer corrects that on the next frame and also catches
    // the stage changing size when the panel's content reflows the grid.
    const ro = new ResizeObserver(() => fit());
    ro.observe(wrapRef.current);
    return () => ro.disconnect();
  }, [claims, edges]);

  // Reduced motion draws on demand; the animated path is already redrawing.
  useEffect(() => { simRef.current?.redraw?.(); }, [matches, off, selected, hovered]);

  // ---- hit testing ---------------------------------------------------------
  const pick = (ev) => {
    const sim = simRef.current;
    const canvas = canvasRef.current;
    if (!sim || !canvas) return null;
    const r = canvas.getBoundingClientRect();
    // The canvas is drawn in device pixels through the view transform, so hit
    // testing converts the same way rather than assuming unit coordinates.
    const scale = canvas.width / r.width;
    const x = (ev.clientX - r.left) * scale;
    const y = (ev.clientY - r.top) * scale;
    // A 12px grab on a 5px dot: motion.md's note that a target accepting more
    // finger than it draws is craft, and a phone has no hover to aim with.
    const tol = 12 * scale;
    let best = null, bestD = Infinity;
    const filtering = matches.size !== claims.length;
    for (let i = 0; i < claims.length; i++) {
      if (filtering && !matches.has(claims[i].id)) continue;
      const [px, py] = sim.toPx(sim.nodes[i]);
      const d = (px - x) ** 2 + (py - y) ** 2;
      if (d < tol * tol && d < bestD) { bestD = d; best = claims[i].id; }
    }
    return best;
  };

  // Keyboard parity. The canvas is a real control, so it takes focus and the
  // arrows walk the claims that are currently matching, in id order, which is
  // the order the library wrote them in. Without this a keyboard reader could
  // search, filter and toggle every edge type and still never open a single
  // claim, on the one page the subscription is being sold for.
  const walk = (delta) => {
    const ids = claims.filter((c) => matches.has(c.id)).map((c) => c.id);
    if (ids.length === 0) return;
    const at = selected == null ? -1 : ids.indexOf(selected);
    const next = at === -1
      ? (delta > 0 ? 0 : ids.length - 1)
      : (at + delta + ids.length) % ids.length;
    setSelected(ids[next]);
  };

  const onCanvasKey = (e) => {
    if (e.key === "ArrowRight" || e.key === "ArrowDown") { e.preventDefault(); walk(1); }
    else if (e.key === "ArrowLeft" || e.key === "ArrowUp") { e.preventDefault(); walk(-1); }
    else if (e.key === "Enter" || e.key === " ") { e.preventDefault(); if (selected == null) walk(1); }
    else if (e.key === "Escape") { setSelected(null); }
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
            tabIndex={0}
            role="application"
            aria-label="Claim graph. Use the arrow keys to move between claims."
            onKeyDown={onCanvasKey}
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
