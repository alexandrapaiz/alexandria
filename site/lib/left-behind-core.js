// The Left-Behind Index, shaped. Pure and import-free, so the volume harness
// drives this exact source with no database and no build step, the same
// contract lib/issues-core.js keeps.
//
// One row of the query is one EDGE, and one row of the page is one FINDING.
// The two are not the same number, because `deprecated_claims` gates on the
// existence of an incoming `contradicts` edge and a finding can carry several:
// the graph is append-only by ADR-10, so a second opinion is a second row and
// nothing is ever corrected in place. Grouping is therefore not a tidying
// step, it is the difference between "22 findings are flagged" and "33 edges
// exist", and the page says the first because a reader counts findings.
//
// Within a finding the contradictions are ordered by confidence, highest
// first, so the strongest reading of why something was flagged is the one
// directly under the disclosure.

// Newest first, by the date the flag was written rather than by the date the
// finding was distilled. The question this page answers is "what has the
// library stopped standing behind", and the answer moves when an edge is
// written, not when the claim was read.
export function shape(rows) {
  const byClaim = new Map();

  for (const r of rows || []) {
    const id = Number(r.id);
    if (!byClaim.has(id)) {
      byClaim.set(id, {
        id,
        claim: r.claim,
        topics: r.topics || [],
        grade: r.evidence_grade || null,
        paper: paperOf(r.paper_title, r.paper_url),
        created: day(r.created_at),
        contradictions: [],
      });
    }
    byClaim.get(id).contradictions.push({
      id: Number(r.new_id),
      claim: r.new_claim,
      paper: paperOf(r.new_paper_title, r.new_paper_url),
      // The judge writes this number and no rubric anywhere says what a given
      // value means (docs/product/graph-quality.md §1). It is shown because it
      // is what the gate reads, not because it is calibrated.
      confidence: r.confidence == null ? null : Number(r.confidence),
      flagged: day(r.flagged_at),
    });
  }

  const findings = [...byClaim.values()];
  for (const f of findings) {
    f.contradictions.sort(
      (a, b) => (b.confidence ?? 0) - (a.confidence ?? 0) || a.id - b.id,
    );
    // The row at rest carries one date, and it is the most recent flag rather
    // than the first: a finding contradicted again last week is news, and the
    // oldest edge on it would hide that.
    f.flagged = f.contradictions[0]
      ? f.contradictions.map((c) => c.flagged).filter(Boolean).sort().pop() || null
      : null;
  }

  findings.sort(
    (a, b) => String(b.flagged || "").localeCompare(String(a.flagged || "")) || b.id - a.id,
  );

  return {
    findings,
    counts: { findings: findings.length, edges: (rows || []).length },
  };
}

function paperOf(title, url) {
  if (!title && !url) return null;
  return { title: title || null, url: url || null };
}

// Dates arrive from Neon as a Date or as a string depending on the driver's
// mood about the column type, so both are reduced to the same ten characters
// the archive already prints.
function day(value) {
  if (!value) return null;
  const s = typeof value === "string" ? value : String(value);
  return s.slice(0, 10);
}

// The identifier the rest of the organization uses for a claim. The research
// briefs, the skill receipts and the graph all write C-then-id, so the page
// does too rather than inventing a second spelling of the same key.
export function claimRef(id) {
  return `C${id}`;
}
