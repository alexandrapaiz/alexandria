// Pure translation between a Clerk user payload and an alexandria `users`
// row. No imports, no network, no database: everything here is a function
// of its argument, which is what makes the webhook's behaviour testable
// without a Clerk instance, a signing secret, or a Postgres.
//
// Two shapes arrive at these functions and they are not the same shape.
// A webhook event carries raw API JSON (snake_case: `email_addresses`,
// `primary_email_address_id`, `first_name`). A server-side `currentUser()`
// carries Clerk's resource object (camelCase: `emailAddresses`,
// `primaryEmailAddressId`, `firstName`). Anything that reads a user has to
// accept both, so all of these do.

export const HANDLED_EVENTS = ["user.created", "user.updated", "user.deleted"];

export function isHandledEvent(type) {
  return HANDLED_EVENTS.includes(type);
}

const clean = (v) => (typeof v === "string" && v.trim() ? v.trim() : null);

// The primary address, not the first one in the array. Clerk's array order
// is not a promise, and a user who adds a second address and promotes it
// would otherwise keep syncing under the old one. Falling back to the first
// verified address, then to any address, keeps a user with an unusual
// account from syncing as nothing at all.
export function primaryEmail(user) {
  if (!user) return null;

  const addresses = user.emailAddresses ?? user.email_addresses ?? [];
  if (!Array.isArray(addresses) || addresses.length === 0) return null;

  const primaryId = user.primaryEmailAddressId ?? user.primary_email_address_id ?? null;
  const address = (a) => clean(a?.emailAddress ?? a?.email_address);
  const verified = (a) =>
    (a?.verification?.status ?? a?.verification?.Status) === "verified";

  const primary = addresses.find((a) => a?.id && a.id === primaryId);
  return address(primary) ?? address(addresses.find(verified)) ?? address(addresses[0]);
}

// Clerk lets both names be null, and a person with neither is not an error.
// Null beats the empty string here: the column is nullable and "" would
// render as a blank name rather than as no name.
export function displayName(user) {
  if (!user) return null;
  const first = clean(user.firstName ?? user.first_name);
  const last = clean(user.lastName ?? user.last_name);
  const joined = [first, last].filter(Boolean).join(" ");
  return clean(joined) ?? clean(user.username) ?? null;
}

export function clerkId(user) {
  return clean(user?.id);
}

// The whole row, or null when the event cannot produce one. A user with no
// id is unusable, and a user with no email cannot be joined to a subscriber,
// which is the one thing this table exists to make possible. Returning null
// rather than throwing lets the webhook acknowledge the event instead of
// making Svix retry something that will never succeed.
export function userRowFromClerk(user) {
  const id = clerkId(user);
  const email = primaryEmail(user);
  if (!id || !email) return null;
  return { clerkId: id, email: email.toLowerCase(), name: displayName(user) };
}
