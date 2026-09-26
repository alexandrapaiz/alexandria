import { neon } from "@neondatabase/serverless";

// The claim graph, read live from Neon. This replaces lib/graph-data.js, which
// was a hand-committed structural snapshot from 2026-09-13 (254 claims, 88
// edges) and had drifted a long way from the database it described. A page
// that shows a fixture is a page that lies about the product, and the claim
// graph is the product.
//
// Two rules govern what this module returns.
//
// 1. Only claims that carry at least one link. An unlinked claim is a dot with
//    nothing to say in a graph whose whole subject is the relations between
//    claims, and at today's volume that is 214 of 746. The counts below report
//    the full totals so the page can say plainly how much of the library is
//    on screen.
// 2. Claim text is the paid product. Nothing here is called unless hasSpine()
//    has already returned true, so no claim text is ever serialised into a
//    page an unentitled visitor receives.

export const RELATIONS = ["supports", "refines", "contradicts", "duplicates"];

// Fails closed, the same contract as lib/entitlement.js: no connection string,
// or a query that throws, resolves to null rather than to an empty graph. The
// page distinguishes the two, because "no edges" and "could not read the
// database" are different things to tell a subscriber.
export async function loadGraph() {
  const url = process.env.DATABASE_URL;
  if (!url) return null;

  try {
    const sql = neon(url);

    // The linked subgraph, with each claim's paper joined on for the panel.
    const claims = await sql`
      select c.id,
             c.claim,
             coalesce(c.topics, '{}') as topics,
             c.evidence_grade,
             c.paper_id,
             c.created_at,
             p.title as paper_title,
             p.url   as paper_url
      from claims c
      join papers p on p.id = c.paper_id
      where exists (
        select 1 from claim_links l
        where l.from_claim = c.id or l.to_claim = c.id
      )
      order by c.id
    `;

    // Every edge is in-subgraph by construction: both endpoints carry a link,
    // so both are in the set above. No filtering needed and none done.
    const edges = await sql`
      select from_claim, to_claim, relation, confidence
      from claim_links
      order by from_claim, to_claim
    `;

    // One round trip for the four totals the page reports.
    const [counts] = await sql`
      select
        (select count(*) from claims)  as claims,
        (select count(*) from papers)  as papers,
        (select count(*) from claim_links) as edges,
        (select count(*) from (
           select from_claim as id from claim_links
           union
           select to_claim   as id from claim_links
         ) linked) as linked
    `;

    return shape(claims, edges, counts);
  } catch {
    return null;
  }
}

// Kept separate from the query so the shaping is testable and so the volume
// harness can drive the identical structure through the identical component.
export function shape(claimRows, edgeRows, counts) {
  const claims = claimRows.map((r) => ({
    id: Number(r.id),
    claim: r.claim,
    topics: r.topics || [],
    grade: r.evidence_grade || null,
    paperId: r.paper_id,
    paperTitle: r.paper_title,
    paperUrl: r.paper_url,
    created: r.created_at ? String(r.created_at).slice(0, 10) : null,
  }));

  const present = new Set(claims.map((c) => c.id));
  const edges = edgeRows
    .map((r) => ({
      from: Number(r.from_claim),
      to: Number(r.to_claim),
      rel: r.relation,
      confidence: r.confidence == null ? null : Number(r.confidence),
    }))
    .filter((e) => present.has(e.from) && present.has(e.to));

  // Topics, most-used first, so the filter's order is a fact about the library
  // rather than an alphabet. Ties break alphabetically to keep it stable.
  const tally = new Map();
  for (const c of claims) for (const t of c.topics) tally.set(t, (tally.get(t) || 0) + 1);
  const topics = [...tally.entries()]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .map(([name, n]) => ({ name, n }));

  return {
    claims,
    edges,
    topics,
    counts: {
      claims: Number(counts?.claims ?? 0),
      linked: Number(counts?.linked ?? claims.length),
      edges: Number(counts?.edges ?? edges.length),
      papers: Number(counts?.papers ?? 0),
    },
  };
}
