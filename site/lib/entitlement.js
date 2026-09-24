import { neon } from "@neondatabase/serverless";

// The paid spine (docs/vision.md §0, priced 2026-09-17) is the operational
// layer: the skill library, the claim graph, and automations. It costs $20 a
// month and it is the only thing on this site that is gated. The weekly
// digest is free in full, so no digest route ever calls into this module.
//
// `subscribers.tier` is 'digest' (the free list) or 'full' (the spine); see
// db/schema.sql. 'full' is the $20 tier.
export const SPINE_TIER = "full";

// STILL THE PRE-CLERK STUB, and the comment that used to sit here said Clerk
// was not wired yet. It is. `@clerk/nextjs` landed 2026-09-17: middleware.js
// runs clerkMiddleware, /sign-in and /sign-up are real routes, and
// /api/clerk-webhook exists. What did not change is this function, so it still
// returns null for everyone and `hasSpine()` below can therefore never return
// true, for a paying subscriber or for anyone else.
//
// The consequence is that the whole $20 spine is shut. It fails closed, so
// nothing leaks, and that is the only good news in it. Rewiring this to read
// the signed-in user's primary email address is the engineer's `urgent` item
// in docs/ideas.md and it is deliberately not done here, because a security
// run fixes defects and does not build the accounts path.
export async function currentEmail() {
  return null;
}

// Fails closed by design. No session, no connection string, or a query that
// throws all resolve to "not entitled", because a check that opens when the
// database is unreachable is not a check.
export async function hasSpine() {
  const email = await currentEmail();
  if (!email) return false;

  const url = process.env.DATABASE_URL;
  if (!url) return false;

  try {
    const sql = neon(url);
    const rows = await sql`
      select 1
      from subscribers
      where lower(email) = lower(${email})
        and status = 'active'
        and tier = ${SPINE_TIER}
      limit 1
    `;
    return rows.length > 0;
  } catch {
    return false;
  }
}
