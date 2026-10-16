import { neon } from "@neondatabase/serverless";

import { shape } from "./left-behind-core.js";

// The Left-Behind Index, read live from Neon over the `deprecated_claims`
// view. Sprint-2026-10-12 item 4.
//
// Why the view and not its predicate. The gate is one line of SQL
// (`contradicts` at confidence >= 0.7) and it already exists in exactly one
// place, db/schema.sql:314, where `skills_needing_revision` and
// pipeline/weekly.py's deprecated section read it too. Copying the predicate
// into the site would have given the page its own opinion of what "left
// behind" means, and the first time the owner moved the threshold the site
// would have gone on publishing the old one. So this joins the view rather
// than restating it, and the page is a surface over a decision the schema
// owns.
//
// What the join adds is the other half of the pair. The view answers "which
// findings are flagged" and a reader needs "and by what", so the newer claim
// and both papers come back with it. That is the same shape
// pipeline/weekly.py:402 already prints in the free weekly issue, which is
// the precedent for showing this pair publicly at all.
//
// Fails closed, the same contract as lib/entitlement.js, lib/graph-live.js and
// lib/issues-live.js: no connection string, or a query that throws, resolves
// to null rather than to an empty index. The page distinguishes the two,
// because "nothing is flagged" and "this page could not read the library" are
// different things to tell a reader and only one of them is about the
// research.
export async function loadLeftBehind() {
  const url = process.env.DATABASE_URL;

  // The volume hook, and the reason it is in the shipped module rather than in
  // a patch the run throws away. This page is a list surface, so the charter
  // judges it at the volume the design targets (fifty findings) and not at the
  // inventory of the day, and there is no database in the agent container. A
  // local patch would mean the screenshots prove a code path that is not the
  // one that ships. Pointing an env var at a file of query rows means the
  // fixture goes through this exact function, the exact `shape()` and the
  // exact component, which is what makes the picture evidence.
  //
  // It cannot lie in production. It is consulted only when there is no
  // connection string, so a deployment that can reach Neon never reads it, and
  // the variable does not exist on Vercel. `site/lib/waitlist.js` carries the
  // same kind of override for the same kind of reason (WAITLIST_FILE).
  const fixture = !url && process.env.LEFT_BEHIND_FIXTURE;
  if (fixture) {
    const { readFileSync } = await import("node:fs");
    try {
      return shape(JSON.parse(readFileSync(fixture, "utf8")));
    } catch {
      return null;
    }
  }

  if (!url) return null;

  try {
    const sql = neon(url);

    const rows = await sql`
      select dc.id,
             dc.claim,
             coalesce(dc.topics, '{}') as topics,
             dc.evidence_grade,
             dc.created_at,
             op.title as paper_title,
             op.url   as paper_url,
             nc.id    as new_id,
             nc.claim as new_claim,
             np.title as new_paper_title,
             np.url   as new_paper_url,
             l.confidence,
             l.created_at as flagged_at
      from deprecated_claims dc
      join claim_links l
        on l.to_claim = dc.id
       and l.relation = 'contradicts'
       and coalesce(l.confidence, 0) >= 0.7
      join claims nc on nc.id = l.from_claim
      join papers op on op.id = dc.paper_id
      join papers np on np.id = nc.paper_id
      order by l.created_at desc nulls last, dc.id desc
    `;

    return shape(rows);
  } catch {
    return null;
  }
}
