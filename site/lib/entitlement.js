import { neon } from "@neondatabase/serverless";

// The paid spine (docs/vision.md §0, priced 2026-09-17) is the operational
// layer: the skill library, the claim graph, and automations. It costs $20 a
// month and it is the only thing on this site that is gated. The weekly
// digest is free in full, so no digest route ever calls into this module.
//
// `subscribers.tier` is 'digest' (the free list) or 'full' (the spine); see
// db/schema.sql. 'full' is the $20 tier.
export const SPINE_TIER = "full";

// STUB. Clerk's components and middleware landed on 2026-09-18 (sign-in,
// sign-up, ClerkProvider, clerkMiddleware), but this function was never
// switched over, so it still reports every visitor as signed out and
// hasSpine() below can therefore never return true for anybody. That is safe
// (it fails closed) but it means the $20 spine is shut to paying subscribers
// too, which matters before Stripe goes live 2026-09-26.
//
// Finishing it needs Clerk's server-side session, plus the Clerk keys that
// are still the owner's pending action, so it belongs to the engineer seat
// and not to a comment. Tracked as urgent in docs/ideas.md (2026-09-18).
// When it lands, this stays the only function that changes, and it returns
// the signed-in user's primary email address.
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
