// The accounts layer's decision logic, executed (ADR-30).
//
//     node --test tests/accounts.test.mjs
//
// tests/test_accounts.py runs this too, so `python3 -m pytest tests/ -q`
// covers it and there is still one command for the whole suite.
//
// site/lib/account-core.js is loaded by reading its source and evaluating
// it as a module, rather than importing it by path. The site is a Next.js
// app whose package.json declares no module type, so Node parses its .js
// files as CommonJS and an ordinary import of an ESM file there fails.
// This runs the real source with no build step and no edit to the app's
// package.json, and it works because account-core.js has no imports.

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const path = fileURLToPath(new URL("../site/lib/account-core.js", import.meta.url));
const source = await readFile(path, "utf8");
const core = await import(
  "data:text/javascript;base64," + Buffer.from(source).toString("base64")
);

// A user.created payload, in the snake_case the webhook actually delivers.
const webhookUser = {
  id: "user_2abc",
  primary_email_address_id: "idn_second",
  email_addresses: [
    { id: "idn_first", email_address: "old@example.com", verification: { status: "verified" } },
    { id: "idn_second", email_address: "Ada@Example.com", verification: { status: "verified" } },
  ],
  first_name: "Ada",
  last_name: "Lovelace",
};

// The same person as currentUser() returns them, in camelCase.
const sessionUser = {
  id: "user_2abc",
  primaryEmailAddressId: "idn_second",
  emailAddresses: [
    { id: "idn_first", emailAddress: "old@example.com" },
    { id: "idn_second", emailAddress: "Ada@Example.com" },
  ],
  firstName: "Ada",
  lastName: "Lovelace",
};

test("primary email is the primary one, not the first in the array", () => {
  assert.equal(core.primaryEmail(webhookUser), "Ada@Example.com");
});

test("the same reader handles the session object's camelCase", () => {
  assert.equal(core.primaryEmail(sessionUser), "Ada@Example.com");
});

test("with no primary marked, a verified address beats an unverified one", () => {
  const user = {
    id: "user_x",
    email_addresses: [
      { id: "a", email_address: "unverified@example.com", verification: { status: "unverified" } },
      { id: "b", email_address: "verified@example.com", verification: { status: "verified" } },
    ],
  };
  assert.equal(core.primaryEmail(user), "verified@example.com");
});

test("an account with no email address yields null, not a crash", () => {
  assert.equal(core.primaryEmail({ id: "user_x", email_addresses: [] }), null);
  assert.equal(core.primaryEmail({ id: "user_x" }), null);
  assert.equal(core.primaryEmail(null), null);
});

test("a name is first and last, then username, then nothing", () => {
  assert.equal(core.displayName(webhookUser), "Ada Lovelace");
  assert.equal(core.displayName(sessionUser), "Ada Lovelace");
  assert.equal(core.displayName({ first_name: "Ada", last_name: null }), "Ada");
  assert.equal(core.displayName({ first_name: "", last_name: "  ", username: "ada" }), "ada");
  assert.equal(core.displayName({ first_name: null, last_name: null }), null);
});

// This is the property the whole linkage rests on. The join to subscribers
// is on lower(email) and the unique index is on lower(email), so a row that
// went in with its original casing would still join, but two rows differing
// only by case would collide on insert instead of updating. Folding here
// means what is in the column matches what the index indexes.
test("the row's email is folded to lower case", () => {
  const row = core.userRowFromClerk(webhookUser);
  assert.deepEqual(row, {
    clerkId: "user_2abc",
    email: "ada@example.com",
    name: "Ada Lovelace",
  });
});

test("no id or no email means no row, so the webhook can stop trying", () => {
  assert.equal(core.userRowFromClerk({ id: "user_x", email_addresses: [] }), null);
  assert.equal(core.userRowFromClerk({ email_addresses: [{ email_address: "a@b.co" }] }), null);
  assert.equal(core.userRowFromClerk(null), null);
});

test("only the three user events are handled", () => {
  assert.deepEqual(core.HANDLED_EVENTS, ["user.created", "user.updated", "user.deleted"]);
  assert.ok(core.isHandledEvent("user.created"));
  assert.ok(core.isHandledEvent("user.deleted"));
  // Sessions, orgs and billing events are not this endpoint's business yet.
  assert.equal(core.isHandledEvent("session.created"), false);
  assert.equal(core.isHandledEvent("paymentAttempt.created"), false);
  assert.equal(core.isHandledEvent(undefined), false);
});

// The gate. It must fail closed, because a check that opens when the
// database is unreachable is not a check.
test("entitlement is closed by default and closed on a missing row", () => {
  assert.equal(core.isEntitled(null), false);
  assert.equal(core.isEntitled(undefined), false);
  assert.equal(core.isEntitled({}), false);
});

test("a free account on the free digest list is not entitled", () => {
  assert.equal(
    core.isEntitled({
      subscription_status: "free",
      digest_tier: "digest",
      digest_status: "active",
      digest_comp: false,
    }),
    false
  );
});

test("the three ways to hold the spine today", () => {
  const paid = { subscription_status: "active", digest_tier: null, digest_status: null };
  const full = { subscription_status: "free", digest_tier: "full", digest_status: "active" };
  const comp = {
    subscription_status: "free",
    digest_tier: "digest",
    digest_status: "active",
    digest_comp: true,
  };
  assert.equal(core.isEntitled(paid), true);
  assert.equal(core.isEntitled(full), true);
  assert.equal(core.isEntitled(comp), true);
});

test("unsubscribing closes the door, and a lapsed payment does too", () => {
  assert.equal(
    core.isEntitled({
      subscription_status: "free",
      digest_tier: "full",
      digest_status: "unsubscribed",
    }),
    false
  );
  assert.equal(
    core.isEntitled({ subscription_status: "past_due", digest_tier: "digest", digest_status: "active" }),
    false
  );
});
