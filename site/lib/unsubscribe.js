import { neon } from "@neondatabase/serverless";
import { normalizeToken } from "./unsubscribe-core";

// The unsubscribe request, against `subscribers`. Sprint 2026-10-05 item 3.
//
// pipeline/weekly.py's own comment says "No unsubscribe endpoint exists yet",
// and the foot of every issue has carried `mailto:...?subject=Unsubscribe`
// since the press started sending. That is a request the owner has to read and
// act on by hand, which clause 2 of this sprint's definition of done rules out.
//
// site/lib/unsubscribe-core.js carries the reasoning about the token and about
// why the change is a POST.

function db() {
  const url = process.env.DATABASE_URL;
  return url ? neon(url) : null;
}

// Who the token belongs to, for the confirm page, so the person can see which
// address they are about to remove. The address is shown only to somebody who
// already holds that subscriber's token, which is to say to the subscriber.
export async function subscriberForToken(rawToken) {
  const token = normalizeToken(rawToken);
  if (!token) return { ok: true, found: false };

  const sql = db();
  if (!sql) return { ok: false, retryable: true, reason: "DATABASE_URL is not set" };

  try {
    const rows = await sql`
      select email, status
      from subscribers
      where unsubscribe_token = ${token}
      limit 1
    `;
    const row = rows[0];
    if (!row) return { ok: true, found: false };
    return {
      ok: true,
      found: true,
      email: row.email,
      alreadyUnsubscribed: row.status === "unsubscribed",
    };
  } catch {
    // Before the owner's next `modal run pipeline/db_setup.py` the column does
    // not exist, and the query raises. Reported as unavailable rather than as
    // an unknown token, because the two want different words on the page and
    // only one of them is the person's problem.
    return { ok: false, retryable: true, reason: "the lookup failed" };
  }
}

// The flip. `where status <> 'unsubscribed'` is what makes a second click
// honest: the row is already correct, so nothing is written, and
// `unsubscribed_at` keeps the date of the request that actually changed
// something rather than the date of the last click on an old email.
export async function unsubscribeByToken(rawToken) {
  const token = normalizeToken(rawToken);
  if (!token) return { ok: true, found: false, changed: false };

  const sql = db();
  if (!sql) return { ok: false, retryable: true, reason: "DATABASE_URL is not set" };

  try {
    const changed = await sql`
      update subscribers
         set status = 'unsubscribed',
             unsubscribed_at = now()
       where unsubscribe_token = ${token}
         and status <> 'unsubscribed'
      returning email
    `;
    if (changed.length > 0) {
      return { ok: true, found: true, changed: true, email: changed[0].email };
    }

    // Nothing was updated, which is two different situations: a token nobody
    // has, and a subscriber who is already unsubscribed. The page says
    // different things for those, so they are told apart here rather than
    // collapsed into one answer the page cannot unpick.
    const existing = await sql`
      select email from subscribers where unsubscribe_token = ${token} limit 1
    `;
    return existing.length > 0
      ? { ok: true, found: true, changed: false, email: existing[0].email }
      : { ok: true, found: false, changed: false };
  } catch {
    return { ok: false, retryable: true, reason: "the update failed" };
  }
}
