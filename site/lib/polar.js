import { createHmac } from "node:crypto";
import { neon } from "@neondatabase/serverless";
import { clerkClient } from "@clerk/nextjs/server";
import {
  verifySignature,
  spineFromEvent,
  spineMetadata,
  checkoutTarget,
} from "./polar-core";

// The payments layer's I/O (ADR-30, ADR-31). Polar is the Merchant of
// Record, so this file never charges anybody and never holds a card. It
// does three things: it proves a request came from Polar, it turns the
// event into one verdict by asking site/lib/polar-core.js, and it writes
// that verdict where reads will find it.
//
// Nothing in here decides anything. Every judgement is in polar-core.js,
// which has no imports and is executed by tests/polar.test.mjs. This half
// is the part that cannot be tested without a Clerk instance and a
// Postgres, so it is kept as thin as it can be made.
//
// Secret names only, and this is all of them:
//   POLAR_WEBHOOK_SECRET      the endpoint's signing secret, from Polar
//   POLAR_CHECKOUT_TRIAL      the 3-day trial product's checkout link
//   POLAR_CHECKOUT_MONTHLY    the $20 monthly product's checkout link
//   POLAR_CHECKOUT_LIFETIME   the $200 lifetime product's checkout link
//   CLERK_SECRET_KEY          already set, read by clerkClient()
//   DATABASE_URL              already set
//
// docs/product/polar-go-live.md is the owner's checklist for filling them.

function db() {
  const url = process.env.DATABASE_URL;
  return url ? neon(url) : null;
}

// The one primitive polar-core.js asks for. Node's HMAC, base64, over the
// raw body, which is why the route reads request.text() before anything
// else touches the request.
export function hmacSha256Base64(keyBytes, message) {
  return createHmac("sha256", Buffer.from(keyBytes)).update(message, "utf8").digest("base64");
}

// Verifies and parses, in that order, and returns the event only when the
// signature held. The body is passed in as text by the caller rather than
// read here, because reading a request body twice is not possible and the
// raw bytes are what the signature covers.
export function readEvent({ body, headers, nowMs = Date.now() }) {
  const check = verifySignature(
    { body, headers, secret: process.env.POLAR_WEBHOOK_SECRET, nowMs },
    hmacSha256Base64,
  );
  if (!check.ok) return { ok: false, reason: check.reason };

  try {
    return { ok: true, event: JSON.parse(body), id: check.id };
  } catch {
    return { ok: false, reason: "the signed body is not JSON" };
  }
}

// Which Clerk user the verdict is about. The id comes first because it is
// one we issued and carried through checkout ourselves. The email is a
// lookup on something the buyer typed, so it is only consulted when there
// is no id, and an email matching two accounts matches neither: granting
// paid access to the wrong one of two people is worse than granting it to
// nobody and logging why.
async function findClerkUser(subject) {
  const client = await clerkClient();

  if (subject.clerkId) {
    const user = await client.users.getUser(subject.clerkId).catch(() => null);
    if (user) return { id: user.id, matchedBy: "reference_id" };
  }

  if (subject.email) {
    const list = await client.users
      .getUserList({ emailAddress: [subject.email], limit: 2 })
      .catch(() => null);
    const found = list?.data ?? [];
    if (found.length === 1) return { id: found[0].id, matchedBy: "email" };
    if (found.length > 1) return { id: null, matchedBy: "email is ambiguous" };
  }

  return { id: null, matchedBy: "no match" };
}

// The entitlement write. This is the one every read consults, so it goes
// first and a failure here is retryable: Polar will bring the event back,
// and writing the same metadata twice produces the same metadata.
async function writeClerkMetadata(clerkId, metadata) {
  const client = await clerkClient();
  await client.users.updateUserMetadata(clerkId, { publicMetadata: metadata });
}

// The billing record. `users` rows are inserted by the Clerk webhook and
// never by this one, because an account is created at Clerk and a payment
// is not an account. An update that matches no row therefore means the
// Clerk webhook has not landed yet, which is temporary and worth a retry.
async function writeBillingRow(clerkId, verdict) {
  const sql = db();
  if (!sql) return { ok: false, retryable: true, reason: "DATABASE_URL is not set" };

  const rows = await sql`
    update users
       set subscription_status = ${verdict.billingStatus},
           polar_customer_id   = coalesce(${verdict.polarCustomerId}, polar_customer_id),
           updated_at          = now()
     where clerk_id = ${clerkId}
    returning clerk_id
  `;
  if (rows.length === 0) {
    return { ok: false, retryable: true, reason: "no users row for that clerk_id yet" };
  }
  return { ok: true };
}

// The whole handler, as a function that returns rather than responds, so
// the route decides the status code and this stays testable in principle.
export async function applyPolarEvent(event, nowIso = new Date().toISOString()) {
  const verdict = spineFromEvent(event);
  if (!verdict) {
    return { ok: true, ignored: event?.type ?? "unknown" };
  }

  const match = await findClerkUser(verdict).catch(() => ({ id: null, matchedBy: "lookup threw" }));
  if (!match.id) {
    // A real case and not only an error case. Somebody can buy through a
    // link that never passed through this site, and then there is no
    // account to grant anything to. Acknowledged rather than retried,
    // because no number of retries produces an account, and logged by the
    // route so the owner can see it and invite them.
    return {
      ok: false,
      retryable: false,
      reason: `no Clerk account for this buyer (${match.matchedBy})`,
      verdict,
    };
  }

  await writeClerkMetadata(match.id, spineMetadata(verdict, nowIso));

  const billing = await writeBillingRow(match.id, verdict);
  if (!billing.ok) {
    return { ...billing, entitled: verdict.hasSpine, clerkId: match.id, verdict };
  }

  return {
    ok: true,
    clerkId: match.id,
    matchedBy: match.matchedBy,
    entitled: verdict.hasSpine,
    tier: verdict.tier,
    until: verdict.until,
    verdict,
  };
}

// Where /api/checkout/<plan> sends a buyer. Separate from the pure
// function only to read the environment, which a pure function must not.
export function checkoutRedirect(plan, account) {
  return checkoutTarget(process.env, plan, account);
}
