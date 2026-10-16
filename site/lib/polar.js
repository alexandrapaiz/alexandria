import { createHmac } from "node:crypto";
import { neon } from "@neondatabase/serverless";
import { clerkClient } from "@clerk/nextjs/server";
import {
  verifySignature,
  spineFromEvent,
  spineMetadata,
  checkoutTarget,
  paymentExceptionOf,
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

// `findClerkUser`'s own words for how it failed, mapped onto the codes
// db/schema.sql checks. The lookup names its outcome in prose because the
// prose is what the log line reads; the row needs a grouping key, and
// keeping the translation here means the prose can be reworded without
// silently renaming a category the standup counts by.
const MATCH_CODES = {
  "email is ambiguous": "ambiguous_email",
  "lookup threw": "lookup_failed",
  "no match": "no_account",
};

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
  if (!sql) {
    return { ok: false, retryable: true, code: "no_database",
             reason: "DATABASE_URL is not set" };
  }

  const rows = await sql`
    update users
       set subscription_status = ${verdict.billingStatus},
           polar_customer_id   = coalesce(${verdict.polarCustomerId}, polar_customer_id),
           updated_at          = now()
     where clerk_id = ${clerkId}
    returning clerk_id
  `;
  if (rows.length === 0) {
    return { ok: false, retryable: true, code: "no_users_row",
             reason: "no users row for that clerk_id yet" };
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
    //
    // The three ways this happens are three different jobs for the owner,
    // so they are three codes rather than one. An address nobody holds is
    // an invitation to send. An address two accounts hold is a duplicate
    // to merge. A lookup that threw is Clerk being down and says nothing
    // about the buyer at all, so it is retryable where the other two are
    // not: no number of retries produces an account, and one retry may
    // well produce a working Clerk.
    const code = MATCH_CODES[match.matchedBy] ?? "no_account";
    return {
      ok: false,
      retryable: code === "lookup_failed",
      code,
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

// --------------------------------------- the till's alarm path (ADR-30)
//
// Two writes, and neither of them may ever fail a webhook. A payment that
// landed matters more than a tidy record that it was awkward, so both of
// these swallow their own errors and report back in a value. The caller
// logs what they say and then answers Polar on the merits of the payment.

// One row per Polar delivery, however many times Polar retries it.
//
// The upsert is the whole design. This endpoint answers a deferred event
// with a 503 and Polar brings it back on its own schedule, so a plain
// insert would write a row per retry and the count the daily standup reads
// would measure Polar's retry policy rather than the number of people
// locked out. `on conflict (event_id)` collapses the retries onto the row
// they belong to and counts them in `attempts`, which is the number a human
// would actually want: one buyer, eleven attempts, still waiting.
//
// `occurred_at` is deliberately not touched on conflict. The first time the
// payment failed to land is the age of the problem, and an upsert that
// refreshed it would make a payment stuck for a day look like one that just
// arrived, which is the one thing the row is for.
export async function recordPaymentException(row) {
  if (!row) return { recorded: false, why: "nothing to record" };

  const sql = db();
  if (!sql) return { recorded: false, why: "DATABASE_URL is not set" };

  try {
    const rows = await sql`
      insert into payment_exceptions
             (event_id, event_type, reason_code, retryable, detail,
              polar_customer_id, polar_subscription_id, email)
      values (${row.event_id}, ${row.event_type}, ${row.reason_code},
              ${row.retryable}, ${row.detail}, ${row.polar_customer_id},
              ${row.polar_subscription_id}, ${row.email})
      on conflict (event_id) do update
         set attempts     = payment_exceptions.attempts + 1,
             last_seen_at = now(),
             reason_code  = excluded.reason_code,
             retryable    = excluded.retryable,
             detail       = excluded.detail
      returning id, attempts
    `;
    const saved = rows[0] ?? null;
    return saved
      ? { recorded: true, id: saved.id, attempts: saved.attempts }
      : { recorded: false, why: "the upsert returned no row" };
  } catch (error) {
    // The class and nothing else, the same rule lib/delivery.js keeps. This
    // string reaches a server log and never a response, but an absent
    // `payment_exceptions` table is a state this really meets (applying
    // db/schema.sql is a hand step), and "relation does not exist" is the
    // one diagnosis worth having when the alarm path is itself quiet.
    return { recorded: false, why: `the insert failed: ${error?.name ?? "Error"}` };
  }
}

// The other half, and the half that makes the count worth reading. A
// deferred delivery whose retry later succeeds closes its own row, so the
// unresolved count falls back to zero with nobody clearing it by hand.
//
// Without this the table only ever grows, and a number that only rises is
// a number the org learns to read as decoration rather than as an alarm.
// That is incident 20's shape: a register written to faithfully and
// consulted by nothing.
export async function resolvePaymentException(eventId, note) {
  if (!eventId) return { resolved: 0 };

  const sql = db();
  if (!sql) return { resolved: 0, why: "DATABASE_URL is not set" };

  try {
    const rows = await sql`
      update payment_exceptions
         set resolved_at   = now(),
             resolved_note = ${note ?? "a later delivery of this event granted access"}
       where event_id = ${eventId}
         and resolved_at is null
      returning id
    `;
    return { resolved: rows.length };
  } catch (error) {
    return { resolved: 0, why: `the update failed: ${error?.name ?? "Error"}` };
  }
}

// The row this delivery deserves, decided by polar-core.js and written
// here. One call for the route to make on every outcome, so a new failure
// path cannot be added without passing through the thing that records it.
//
// On success it resolves instead of recording, which is the same question
// asked the other way round: this delivery either became access or did not,
// and exactly one of the two writes follows.
export async function notePolarOutcome({ event, eventId, result }) {
  if (result?.ok === true) {
    return { ...(await resolvePaymentException(eventId)), exception: null };
  }
  const row = paymentExceptionOf({ event, eventId, result });
  return { ...(await recordPaymentException(row)), exception: row };
}

// Where /api/checkout/<plan> sends a buyer. Separate from the pure
// function only to read the environment, which a pure function must not.
export function checkoutRedirect(plan, account) {
  return checkoutTarget(process.env, plan, account);
}
