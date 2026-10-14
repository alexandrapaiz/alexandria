// Every decision the unsubscribe path makes, as pure functions: whether a
// link's token is even worth a query, and what the page says afterwards. No
// imports, no network, no database. site/lib/unsubscribe.js does the I/O.
//
// Keep this file import-free. tests/unsubscribe.test.mjs loads it by reading
// the source and evaluating it, the same way tests/waitlist.test.mjs loads
// site/lib/waitlist-core.js.
//
// Sprint 2026-10-05 item 3, and clause 2 of its definition of done: a
// subscriber unsubscribes from the site, "as a request that flips their own
// row, not a reply-to-this-email the owner has to read and act on". Today's
// link is `mailto:...?subject=Unsubscribe`, which pipeline/weekly.py says in
// its own comment is a placeholder.
//
// Why the link carries a token and not an email address. An unsubscribe link
// is published to every recipient and lives in their mail client forever, so
// whatever is in it is readable by anyone who sees the message. With an email
// address in the link, anybody who knows an address can unsubscribe that
// person. With an opaque per-subscriber token, the link only works for the
// subscriber it was sent to, and knowing somebody's address grants nothing.

// A UUID as PostgreSQL writes it. Checked before any query, because a token
// that cannot possibly match is a round trip to the database on behalf of
// somebody scanning for one.
const TOKEN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;

export function normalizeToken(raw) {
  const token = String(raw ?? "").trim().toLowerCase();
  return TOKEN.test(token) ? token : null;
}

// The link, for whoever is building an email. It takes the base rather than
// reading the environment, because this file does no I/O and because the press
// and the site read that value from two different places.
export function unsubscribeUrl(base, token) {
  const clean = normalizeToken(token);
  if (!clean) return null;
  const root = String(base ?? "").trim().replace(/\/+$/, "");
  if (!root) return null;
  return `${root}/unsubscribe?t=${clean}`;
}

// What the page says, from what the update returned. Four states and they are
// all worth telling apart on screen.
//
// `already` exists because this page is reached by clicking a link in an old
// email, and clicking it twice is the most ordinary thing a person can do. It
// must not read as a failure.
//
// `unknown` is deliberately not "that link is invalid". A token nobody
// recognises and a token that was right once are indistinguishable from here,
// and the page should not tell a stranger which one they hold.
export function unsubscribeState(result) {
  if (!result || typeof result !== "object") return "unknown";
  if (!result.ok) return result.retryable ? "unavailable" : "unknown";
  if (!result.found) return "unknown";
  return result.changed ? "done" : "already";
}

// A mutation behind a GET is a mutation email scanners and link previewers
// perform on the subscriber's behalf, which would unsubscribe people who never
// clicked anything. So the link opens a page, the page asks, and the answer is
// a POST. This is the function that says so, and the test that reads it is the
// reason it is a function rather than a comment.
export function methodChangesTheRow(method) {
  return String(method ?? "").toUpperCase() === "POST";
}
