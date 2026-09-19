import { neon } from "@neondatabase/serverless";
import { currentUser } from "@clerk/nextjs/server";
import { userRowFromClerk, primaryEmail, displayName, clerkId } from "./clerk-user";

// The account layer (ADR-30). Neon holds the durable row; Clerk holds the
// session. Everything that needs to know who someone is reads through here,
// so there is exactly one place that knows how the two are joined.
//
// Writes come from the Clerk webhook. Reads come from server components.
// Nothing in this module opens a paid surface by itself: it reports what is
// true, and the surface decides.

function db() {
  const url = process.env.DATABASE_URL;
  return url ? neon(url) : null;
}

// Idempotent by clerk_id, which is what makes Svix's retries harmless: the
// same event delivered three times produces one row. Email is stored folded
// to lower case so the unique index on lower(email) and the join to
// subscribers agree with what is actually in the column.
export async function upsertUserFromClerk(user) {
  const row = userRowFromClerk(user);
  if (!row) return { ok: false, retryable: false, reason: "no id or email on the event" };

  const sql = db();
  if (!sql) return { ok: false, retryable: true, reason: "DATABASE_URL is not set" };

  await sql`
    insert into users (clerk_id, email, name)
    values (${row.clerkId}, ${row.email}, ${row.name})
    on conflict (clerk_id) do update
      set email = excluded.email,
          name = excluded.name,
          updated_at = now()
  `;
  return { ok: true, clerkId: row.clerkId };
}

// Deleting the account deletes the account and nothing else. The person's
// subscribers row is untouched on purpose: they asked Clerk to forget them,
// not to unsubscribe from a newsletter they may still want. Those are two
// different requests and the digest list stays independent (ADR-30).
export async function deleteUserByClerkId(id) {
  const key = typeof id === "string" ? id.trim() : null;
  if (!key) return { ok: false, retryable: false, reason: "no id on the event" };

  const sql = db();
  if (!sql) return { ok: false, retryable: true, reason: "DATABASE_URL is not set" };

  const rows = await sql`delete from users where clerk_id = ${key} returning clerk_id`;
  return { ok: true, deleted: rows.length };
}

// What a server component should call. Returns null when nobody is signed
// in, and otherwise the Clerk identity joined to its Neon row.
//
// `linked` is the field worth reading twice. It is false when someone has a
// Clerk session but no row here, which means the webhook has not arrived or
// never did. Webhook delivery is eventually consistent, so this is a normal
// state seconds after signup and a bug days after it. Reporting it beats
// papering over it with a silent insert, which would hide a dead webhook
// for as long as the endpoint stayed broken.
export async function currentAccount() {
  const user = await currentUser().catch(() => null);
  if (!user) return null;

  const id = clerkId(user);
  const email = primaryEmail(user);
  const base = {
    clerkId: id,
    email,
    name: displayName(user),
    linked: false,
    subscriptionStatus: "free",
    subscriber: null,
    entitled: false,
  };

  const sql = db();
  if (!sql || !id) return base;

  try {
    const rows = await sql`
      select clerk_id, email, name, subscription_status,
             subscriber_id, digest_tier, digest_status, digest_comp
      from user_accounts
      where clerk_id = ${id}
      limit 1
    `;
    const row = rows[0];
    if (!row) return base;

    return {
      ...base,
      email: row.email ?? base.email,
      name: row.name ?? base.name,
      linked: true,
      subscriptionStatus: row.subscription_status ?? "free",
      subscriber: row.subscriber_id
        ? { id: row.subscriber_id, tier: row.digest_tier, status: row.digest_status, comp: row.digest_comp }
        : null,
      entitled: isEntitled(row),
    };
  } catch {
    // Fails closed, the same way site/lib/entitlement.js does. A check that
    // opens when the database is unreachable is not a check.
    return base;
  }
}

// Two ways to hold the paid spine today, and they are both legacy-shaped
// because payments are not open yet (ADR-30 keeps the door closed). A
// comped or 'full' subscribers row is how the owner's friends have it now.
// subscription_status is how Polar will write it when it opens. Until then
// nothing sets the second one, so in practice this reads the first.
export function isEntitled(row) {
  if (!row) return false;
  if (row.subscription_status === "active") return true;
  return row.digest_status === "active" && (row.digest_tier === "full" || row.digest_comp === true);
}
