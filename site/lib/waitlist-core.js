// Every decision the signup path makes, as pure functions: which addresses
// are worth accepting, what row a signup becomes, and what to tell the
// person afterwards. No imports, no network, no database. site/lib/waitlist.js
// is the other half and it does the I/O.
//
// Keep this file import-free. tests/waitlist.test.mjs loads it by reading the
// source and evaluating it, the same way tests/accounts.test.mjs loads
// site/lib/account-core.js, and that works precisely because there are no
// imports to resolve.
//
// The row this file describes is the whole point of sprint 2026-10-05 item 2.
// The old holding pen wrote `status: 'waitlist'` to a local JSONL file and its
// own comment asked whoever wired the database to add `'waitlist'` to the
// status check in db/schema.sql. That instruction is now wrong, and it is worth
// saying why rather than quietly not following it. The sprint's definition of
// done, clause 1, is a stranger becoming a real subscriber with "no file, no
// manual promotion, and no owner action between the submit and the row
// existing". pipeline/weekly.py sends to `status = 'active'` and nothing else,
// so any other status is a row somebody has to come back and change by hand,
// which is the human step the clause rules out. So a signup is active and
// comped from the moment it exists, and `'waitlist'` never becomes a status.

// Deliberately loose: the only thing worth rejecting here is a typo the
// person can see for themselves. Anything stricter turns a valid address into
// a dead end. The length ceiling is RFC 5321's, which the column has no
// opinion about and a form field should.
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const MAX_EMAIL = 254;

// Folded to lower case, because `subscribers.email` carries a plain
// `unique` constraint rather than a unique index on `lower(email)`, so
// Ada@example.com and ada@example.com would otherwise be two people. The
// accounts layer folds on the same seam (site/lib/account.js), and the join
// between the two tables is on `lower(email)` either way.
export function normalizeEmail(raw) {
  const email = String(raw ?? "").trim().toLowerCase();
  if (!email || email.length > MAX_EMAIL) return null;
  return EMAIL.test(email) ? email : null;
}

// Where on the site they signed up, kept for attribution and nothing else.
// Bounded and restricted to the characters a page slug can hold, because this
// value arrives in a request body and ends up in a column.
export function normalizeSource(raw) {
  const source = String(raw ?? "").trim().toLowerCase().slice(0, 32);
  const safe = source.replace(/[^a-z0-9/_-]/g, "");
  return safe || null;
}

// The row, in full, so that the only file that knows what a signup is worth is
// this one. `comp` is true because the friends-and-family phase charges
// nobody (db/schema.sql: "comp = free access"), and a signup that claimed to
// be paid would misreport revenue the first time anybody counted.
export function signupRow(rawEmail, rawSource) {
  const email = normalizeEmail(rawEmail);
  if (!email) return null;
  return {
    email,
    tier: "digest",
    status: "active",
    comp: true,
    source: normalizeSource(rawSource),
  };
}

// What happened, as one word, from what the insert returned. Three outcomes
// and they are genuinely different: a new subscriber, somebody who was already
// on the list, and somebody who had unsubscribed and has just asked to come
// back. The third is why the insert updates on conflict instead of doing
// nothing. A person who unsubscribes in March and signs up again in June has
// asked twice and the second ask is the current one.
export function signupOutcome(result) {
  if (!result || typeof result !== "object") return null;
  if (result.inserted) return "created";
  return result.wasUnsubscribed ? "resubscribed" : "already";
}

// Every outcome above is a success to the person who submitted the form. They
// are on the list in all three cases, and telling them which one they were
// would only make them wonder. The distinction is for the owner's counts.
export function isSuccess(outcome) {
  return outcome === "created" || outcome === "resubscribed" || outcome === "already";
}
