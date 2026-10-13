import { neon } from "@neondatabase/serverless";
import { currentUser } from "@clerk/nextjs/server";
import { primaryEmail } from "./account-core";
import { spineFromMetadata } from "./polar-core";

// The paid spine (docs/vision.md §0, priced 2026-09-17) is the operational
// layer: the skill library, the claim graph, and automations. It costs $20 a
// month and it is the only thing on this site that is gated. The weekly
// digest is free in full, so no digest route ever calls into this module.
//
// `subscribers.tier` is 'digest' (the free list) or 'full' (the spine); see
// db/schema.sql. 'full' is the $20 tier.
export const SPINE_TIER = "full";

// The signed-in person's primary address, or null when nobody is signed in.
//
// This was the pre-Clerk stub until 2026-10-13 and it returned null for
// everyone, which meant `hasSpine()` below could never return true for
// anybody, paying or not. The whole $20 spine was shut. It failed closed,
// which was the only good thing about it.
export async function currentEmail() {
  const user = await currentUser().catch(() => null);
  return primaryEmail(user);
}

// Two ways to hold the spine, and they are read in that order.
//
// 1. A Polar payment (ADR-30, ADR-31). /api/polar-webhook writes the flag
//    onto the Clerk user's metadata, so this read is the session token and
//    costs no round trip. The flag carries its own expiry, which is what
//    makes it safe: Polar's revoke event can be late or can go missing,
//    and an entitlement that expires by itself cannot outlive what was
//    paid for.
// 2. A `tier = 'full'` subscribers row, which is how the owner's friends
//    have it and predates payments entirely.
//
// What is deliberately NOT a second way is `subscribers.comp`, and the
// reason is worth the four lines. The column reads as "free access
// (friends)" in db/schema.sql, and `site/lib/account-core.js`'s
// `isEntitled` treats it as entitling. But `site/lib/waitlist-core.js`
// sets `comp: true` on every signup the site takes, because the
// friends-and-family phase charges nobody for the digest. So a gate that
// opened on `comp` would hand the skill library and the claim graph to the
// whole free list. The tier is what says which product somebody has. The
// comp flag only says nobody billed them for it.
//
// Fails closed at every step. No session, no flag, an unreadable expiry, no
// connection string, or a query that throws all resolve to "not entitled",
// because a check that opens when something is unreachable is not a check.
export async function hasSpine() {
  const user = await currentUser().catch(() => null);
  if (!user) return false;

  if (spineFromMetadata(user.publicMetadata, Date.now())) return true;

  const email = primaryEmail(user);
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
