// The payments layer's decision logic, executed (ADR-30, ADR-31).
//
//     node --test tests/polar.test.mjs
//
// tests/test_polar.py runs this too, so `python3 -m pytest tests/ -q`
// covers it and there is still one command for the whole suite.
//
// site/lib/polar-core.js is loaded by reading its source and evaluating it
// as a module, rather than importing it by path, for the reason
// tests/accounts.test.mjs gives: the site is a Next.js app whose
// package.json declares no module type, so Node parses its .js files as
// CommonJS and an ordinary import of an ESM file there fails. This works
// because polar-core.js has no imports.
//
// The HMAC is the one primitive the core does not implement, so these tests
// pass node's real crypto into it. That means the signature assertions below
// are checking the actual bytes a real Polar delivery would carry, computed
// the way Polar's own Standard Webhooks library computes them, rather than
// a stub agreeing with itself.

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { createHmac } from "node:crypto";

const path = fileURLToPath(new URL("../site/lib/polar-core.js", import.meta.url));
const source = await readFile(path, "utf8");
const core = await import(
  "data:text/javascript;base64," + Buffer.from(source).toString("base64")
);

const hmac = (keyBytes, message) =>
  createHmac("sha256", Buffer.from(keyBytes)).update(message, "utf8").digest("base64");

const SECRET = "polar_whsecret_abc123";
const NOW_MS = Date.UTC(2026, 9, 13, 12, 0, 0);

// A delivery, signed the way Polar signs one: HMAC-SHA256 over
// `{id}.{timestamp}.{body}`, base64, in a `v1,` prefixed header.
function delivery(bodyObject, overrides = {}) {
  const body = JSON.stringify(bodyObject);
  const id = overrides.id ?? "msg_2abc";
  const timestamp = overrides.timestamp ?? String(Math.floor(NOW_MS / 1000));
  const secret = overrides.secret ?? SECRET;
  const signature =
    overrides.signature ??
    "v1," + hmac(core.secretKeyBytes(secret), `${id}.${timestamp}.${body}`);
  return {
    body,
    headers: {
      "webhook-id": id,
      "webhook-timestamp": timestamp,
      "webhook-signature": signature,
    },
  };
}

const subscription = (fields = {}) => ({
  type: "subscription.active",
  data: {
    id: "sub_1",
    status: "active",
    amount: 2000,
    currency: "usd",
    recurring_interval: "month",
    current_period_start: "2026-10-13T09:00:00Z",
    current_period_end: "2026-11-13T09:00:00Z",
    trial_start: null,
    trial_end: null,
    cancel_at_period_end: false,
    ends_at: null,
    customer_id: "cus_1",
    product_id: "prod_monthly",
    metadata: {},
    customer: { id: "cus_1", email: "Ada@Example.com", external_id: null },
    ...fields,
  },
});

const order = (fields = {}) => ({
  type: "order.paid",
  data: {
    id: "ord_1",
    status: "paid",
    paid: true,
    billing_reason: "purchase",
    total_amount: 20000,
    currency: "usd",
    customer_id: "cus_1",
    product_id: "prod_lifetime",
    subscription_id: null,
    metadata: {},
    customer: { id: "cus_1", email: "ada@example.com", external_id: null },
    product: { id: "prod_lifetime", name: "Lifetime", is_recurring: false },
    ...fields,
  },
});

// ------------------------------------------------- the signature check

test("a real Polar signature verifies", () => {
  const { body, headers } = delivery(subscription());
  const result = core.verifySignature(
    { body, headers, secret: SECRET, nowMs: NOW_MS },
    hmac,
  );
  assert.equal(result.ok, true);
  assert.equal(result.id, "msg_2abc");
});

test("the signed content is id.timestamp.body, in that order", () => {
  assert.equal(core.signedContent("msg_1", "1760000000", "{}"), "msg_1.1760000000.{}");
});

test("one byte changed in the body fails the check", () => {
  const { body, headers } = delivery(subscription());
  const tampered = body.replace('"status":"active"', '"status":"active" ');
  const result = core.verifySignature(
    { body: tampered, headers, secret: SECRET, nowMs: NOW_MS },
    hmac,
  );
  assert.equal(result.ok, false);
  assert.equal(result.reason, "the signature does not match");
});

test("a signature from a different secret fails the check", () => {
  const { body, headers } = delivery(subscription(), { secret: "someone-elses-secret" });
  const result = core.verifySignature(
    { body, headers, secret: SECRET, nowMs: NOW_MS },
    hmac,
  );
  assert.equal(result.ok, false);
});

test("no secret set refuses before it looks at a header", () => {
  const result = core.verifySignature(
    { body: "{}", headers: {}, secret: "", nowMs: NOW_MS },
    hmac,
  );
  assert.equal(result.ok, false);
  assert.match(result.reason, /POLAR_WEBHOOK_SECRET/);
});

test("a missing header refuses, and names the class rather than the header", () => {
  const { body, headers } = delivery(subscription());
  for (const name of ["webhook-id", "webhook-timestamp", "webhook-signature"]) {
    const partial = { ...headers };
    delete partial[name];
    const result = core.verifySignature(
      { body, headers: partial, secret: SECRET, nowMs: NOW_MS },
      hmac,
    );
    assert.equal(result.ok, false, `${name} missing should refuse`);
    assert.equal(result.reason, "a signature header is missing");
  }
});

test("a correctly signed body from an hour ago is a replay and is refused", () => {
  const old = String(Math.floor(NOW_MS / 1000) - 3600);
  const { body, headers } = delivery(subscription(), { timestamp: old });
  const result = core.verifySignature(
    { body, headers, secret: SECRET, nowMs: NOW_MS },
    hmac,
  );
  assert.equal(result.ok, false);
  assert.equal(result.reason, "the signed timestamp is outside the tolerance");
});

test("the tolerance is five minutes and it is symmetric", () => {
  assert.equal(core.SIGNATURE_TOLERANCE_SECONDS, 300);
  const seconds = Math.floor(NOW_MS / 1000);
  assert.equal(core.timestampIsFresh(String(seconds - 299), NOW_MS), true);
  assert.equal(core.timestampIsFresh(String(seconds - 301), NOW_MS), false);
  assert.equal(core.timestampIsFresh(String(seconds + 299), NOW_MS), true);
  assert.equal(core.timestampIsFresh(String(seconds + 301), NOW_MS), false);
  assert.equal(core.timestampIsFresh("not-a-number", NOW_MS), false);
});

test("the replay check runs before the HMAC, so an old body costs no hashing", () => {
  let calls = 0;
  const counting = (...args) => {
    calls += 1;
    return hmac(...args);
  };
  const old = String(Math.floor(NOW_MS / 1000) - 3600);
  const { body, headers } = delivery(subscription(), { timestamp: old });
  core.verifySignature({ body, headers, secret: SECRET, nowMs: NOW_MS }, counting);
  assert.equal(calls, 0);
});

test("a rotation sends two signatures and either one is enough", () => {
  const { body, headers } = delivery(subscription());
  const real = headers["webhook-signature"];
  const stale = "v1," + hmac(core.secretKeyBytes("the-old-secret"), "nonsense");
  for (const header of [`${stale} ${real}`, `${real} ${stale}`]) {
    const result = core.verifySignature(
      { body, headers: { ...headers, "webhook-signature": header }, secret: SECRET, nowMs: NOW_MS },
      hmac,
    );
    assert.equal(result.ok, true);
  }
});

test("a version this code does not know is not treated as a match", () => {
  assert.deepEqual(core.signatureCandidates("v2,abc"), []);
  assert.deepEqual(core.signatureCandidates("v1,abc v2,def"), ["abc"]);
  assert.deepEqual(core.signatureCandidates(""), []);
  assert.deepEqual(core.signatureCandidates(null), []);
});

test("the key is the raw bytes of a Polar dashboard secret", () => {
  // Polar's SDKs base64-encode the dashboard secret and hand it to a
  // Standard Webhooks library, which base64-decodes it. The two steps
  // cancel, so this is what a real delivery is signed with.
  assert.deepEqual(
    Buffer.from(core.secretKeyBytes("abc")),
    Buffer.from("abc", "utf8"),
  );
});

test("a whsec_ prefixed secret is base64-decoded instead", () => {
  const raw = Buffer.from([1, 2, 3, 250]);
  const secret = "whsec_" + raw.toString("base64");
  assert.deepEqual(Buffer.from(core.secretKeyBytes(secret)), raw);
});

test("an unreadable secret is no key at all, rather than an empty one", () => {
  assert.equal(core.secretKeyBytes(""), null);
  assert.equal(core.secretKeyBytes(null), null);
  assert.equal(core.secretKeyBytes("whsec_!!!not-base64!!!"), null);
});

test("headers read the same from a Headers object as from a plain one", () => {
  const h = new Headers({ "Webhook-Id": "msg_9" });
  assert.equal(core.headerValue(h, "webhook-id"), "msg_9");
  assert.equal(core.headerValue({ "WEBHOOK-ID": "msg_9" }, "webhook-id"), "msg_9");
  assert.equal(core.headerValue({}, "webhook-id"), null);
});

test("the comparison does not stop at the first differing byte", () => {
  assert.equal(core.constantTimeEqual("abc", "abc"), true);
  assert.equal(core.constantTimeEqual("abc", "abd"), false);
  assert.equal(core.constantTimeEqual("abc", "ab"), false);
  assert.equal(core.constantTimeEqual("abc", null), false);
});

// ------------------------------------------------- what an event means

test("an active monthly subscription opens the door until the period ends", () => {
  const verdict = core.spineFromEvent(subscription());
  assert.equal(verdict.hasSpine, true);
  assert.equal(verdict.tier, "monthly");
  assert.equal(verdict.until, "2026-11-13T09:00:00.000Z");
  assert.equal(verdict.billingStatus, "active");
});

test("a trial opens the door and expires at the trial's own end, not the period's", () => {
  const verdict = core.spineFromEvent(
    subscription({
      status: "trialing",
      trial_start: "2026-10-13T09:00:00Z",
      trial_end: "2026-10-16T09:00:00Z",
      current_period_end: "2026-11-13T09:00:00Z",
    }),
  );
  assert.equal(verdict.hasSpine, true);
  assert.equal(verdict.tier, "trial");
  assert.equal(verdict.until, "2026-10-16T09:00:00.000Z");
  assert.equal(verdict.billingStatus, "active");
});

test("the trial's three days are ADR-31's, and the expiry is what enforces them", () => {
  const verdict = core.spineFromEvent(
    subscription({
      status: "trialing",
      trial_start: "2026-10-13T09:00:00Z",
      trial_end: "2026-10-16T09:00:00Z",
    }),
  );
  const start = Date.parse("2026-10-13T09:00:00Z");
  const end = Date.parse(verdict.until);
  assert.equal((end - start) / 86400000, 3);
  // One second after it ends, the flag written from this verdict is shut,
  // whether or not Polar has sent anything.
  const meta = core.spineMetadata(verdict, "2026-10-13T09:00:00.000Z");
  assert.equal(core.spineFromMetadata(meta, end - 1000), true);
  assert.equal(core.spineFromMetadata(meta, end + 1000), false);
});

test("a cancellation at period end keeps the door open to that end", () => {
  // Polar's own documented shape: status stays active and the flag moves.
  const verdict = core.spineFromEvent({
    type: "subscription.canceled",
    data: { ...subscription().data, status: "active", cancel_at_period_end: true },
  });
  assert.equal(verdict.hasSpine, true);
  assert.equal(verdict.until, "2026-11-13T09:00:00.000Z");
});

test("a revoked subscription closes the door with no expiry to wait for", () => {
  const verdict = core.spineFromEvent({
    type: "subscription.revoked",
    data: { ...subscription().data, status: "canceled", ends_at: "2026-10-13T09:00:00Z" },
  });
  assert.equal(verdict.hasSpine, false);
  assert.equal(verdict.until, null);
  assert.equal(verdict.tier, null);
  assert.equal(verdict.billingStatus, "canceled");
});

test("past_due keeps the month that was paid for and records that it lapsed", () => {
  const verdict = core.spineFromEvent({
    type: "subscription.past_due",
    data: { ...subscription().data, status: "past_due" },
  });
  assert.equal(verdict.hasSpine, true);
  assert.equal(verdict.until, "2026-11-13T09:00:00.000Z");
  assert.equal(verdict.billingStatus, "past_due");
});

test("every status in Polar's own enum has a meaning here", () => {
  // Read out of Polar's OpenAPI schema on 2026-10-13. A status this file
  // does not list is the one case `UNKNOWN_SUBSCRIPTION_STATUS` exists for,
  // and the point of this test is that none of today's eight need it.
  const enumerated = [
    "incomplete",
    "incomplete_expired",
    "trialing",
    "active",
    "past_due",
    "canceled",
    "unpaid",
    "paused",
  ];
  for (const status of enumerated) {
    const meaning = core.subscriptionStatusMeaning(status);
    assert.notEqual(meaning.unknown, true, `${status} has no mapping`);
    assert.ok(["free", "active", "past_due", "canceled"].includes(meaning.billing));
  }
  const open = enumerated.filter((s) => core.subscriptionStatusMeaning(s).open);
  assert.deepEqual(open, ["trialing", "active", "past_due"]);
});

test("a status invented after today closes the door rather than opening it", () => {
  const verdict = core.spineFromEvent(subscription({ status: "scheduled" }));
  assert.equal(verdict.hasSpine, false);
  assert.equal(verdict.unknownStatus, true);
  assert.equal(verdict.status, "scheduled");
});

test("the billing status a row records is always in the schema's vocabulary", () => {
  // db/schema.sql's check constraint on users.subscription_status. Writing
  // anything else is a 23514 at runtime, in a webhook, under retry.
  const allowed = ["free", "active", "past_due", "canceled"];
  for (const status of ["trialing", "active", "past_due", "paused", "canceled", "nonsense"]) {
    const verdict = core.spineFromEvent(subscription({ status }));
    assert.ok(allowed.includes(verdict.billingStatus), `${status} wrote ${verdict.billingStatus}`);
  }
});

// -------------------------------------------------------- the lifetime tier

test("a paid one-time order grants the lifetime tier with no expiry", () => {
  const verdict = core.spineFromEvent(order());
  assert.equal(verdict.hasSpine, true);
  assert.equal(verdict.tier, "lifetime");
  assert.equal(verdict.until, null);
  assert.equal(verdict.billingStatus, "active");
});

test("a lifetime flag never expires, which is the only case where it does not", () => {
  const meta = core.spineMetadata(core.spineFromEvent(order()), "2026-10-13T00:00:00.000Z");
  assert.equal(meta.spineUntil, null);
  assert.equal(core.spineFromMetadata(meta, Date.UTC(2099, 0, 1)), true);
});

test("a refunded lifetime order revokes it", () => {
  const verdict = core.spineFromEvent({ ...order(), type: "order.refunded" });
  assert.equal(verdict.hasSpine, false);
  assert.equal(verdict.billingStatus, "canceled");
});

test("a subscription's own orders say nothing, because its events already did", () => {
  // Otherwise every renewal would be a second opinion on a settled
  // question, and a renewal order arrives as `pending` before it is paid.
  assert.equal(
    core.spineFromEvent(
      order({
        billing_reason: "subscription_cycle",
        subscription_id: "sub_1",
        product: { id: "prod_monthly", is_recurring: true },
      }),
    ),
    null,
  );
  assert.equal(
    core.spineFromEvent(
      order({ billing_reason: "subscription_create", product: { is_recurring: true } }),
    ),
    null,
  );
});

test("an unpaid order grants nothing", () => {
  assert.equal(core.spineFromEvent(order({ paid: false, status: "pending" })), null);
  assert.equal(core.spineFromEvent(order({ paid: false, status: "draft" })), null);
});

// --------------------------------------------------- who the event is about

test("the Clerk id carried through checkout is what matches the buyer", () => {
  const verdict = core.spineFromEvent(
    subscription({ metadata: { reference_id: "user_2abc" } }),
  );
  assert.equal(verdict.clerkId, "user_2abc");
  assert.equal(verdict.email, "ada@example.com");
});

test("an external id on the customer matches too, and the email is the fallback", () => {
  const external = core.spineFromEvent(
    subscription({ customer: { id: "cus_1", email: "ada@example.com", external_id: "user_9" } }),
  );
  assert.equal(external.clerkId, "user_9");

  const none = core.spineFromEvent(subscription());
  assert.equal(none.clerkId, null);
  assert.equal(none.email, "ada@example.com");
});

test("the email is folded to lower case, because the users index is", () => {
  const verdict = core.spineFromEvent(subscription());
  assert.equal(verdict.email, "ada@example.com");
});

test("the Polar customer id is carried so a row can be reconciled later", () => {
  assert.equal(core.spineFromEvent(subscription()).polarCustomerId, "cus_1");
  assert.equal(core.spineFromEvent(order()).polarCustomerId, "cus_1");
});

// ------------------------------------------------- events and non-events

test("an event this code does not handle produces no verdict", () => {
  for (const type of ["benefit.created", "customer.updated", "checkout.created", ""]) {
    assert.equal(core.spineFromEvent({ type, data: subscription().data }), null);
  }
});

test("the handled list covers both halves of ADR-31's plan shape", () => {
  for (const type of ["subscription.active", "subscription.revoked", "order.paid", "order.refunded"]) {
    assert.equal(core.isHandledEvent(type), true, `${type} must be handled`);
  }
});

test("an event with no data produces no verdict instead of throwing", () => {
  assert.equal(core.spineFromEvent(null), null);
  assert.equal(core.spineFromEvent({}), null);
  assert.equal(core.spineFromEvent({ type: "subscription.active" }), null);
});

// ------------------------------------------------- reading the flag back

test("the gate fails closed on everything it cannot read", () => {
  assert.equal(core.spineFromMetadata(null, NOW_MS), false);
  assert.equal(core.spineFromMetadata({}, NOW_MS), false);
  assert.equal(core.spineFromMetadata({ hasSpine: "true" }, NOW_MS), false);
  assert.equal(core.spineFromMetadata({ hasSpine: 1 }, NOW_MS), false);
  assert.equal(
    core.spineFromMetadata({ hasSpine: true, spineUntil: "not a date" }, NOW_MS),
    false,
  );
});

test("an expiry that has passed is shut without anyone being told", () => {
  const meta = { hasSpine: true, spineUntil: "2026-10-13T11:59:59Z" };
  assert.equal(core.spineFromMetadata(meta, NOW_MS), false);
});

test("a revoked verdict writes a flag that is shut, not a missing flag", () => {
  const verdict = core.spineFromEvent({
    type: "subscription.revoked",
    data: { ...subscription().data, status: "canceled" },
  });
  const meta = core.spineMetadata(verdict, "2026-10-13T12:00:00.000Z");
  assert.equal(meta.hasSpine, false);
  assert.equal(core.spineFromMetadata(meta, NOW_MS), false);
});

test("the written flag records what produced it", () => {
  const meta = core.spineMetadata(core.spineFromEvent(subscription()), "2026-10-13T12:00:00.000Z");
  assert.equal(meta.spineSource, "polar");
  assert.equal(meta.spineEvent, "subscription.active");
  assert.equal(meta.spineUpdatedAt, "2026-10-13T12:00:00.000Z");
  assert.equal(meta.polarCustomerId, "cus_1");
  assert.equal(meta.polarSubscriptionId, "sub_1");
});

// ------------------------------------------------------------- checkout

test("the three offers are ADR-31's three and no others", () => {
  assert.deepEqual(
    core.OFFERS.map((o) => o.id),
    ["trial", "monthly", "lifetime"],
  );
});

test("an offer with no link in the environment is not live", () => {
  const offers = core.checkoutOffers({});
  assert.deepEqual(
    offers.map((o) => o.live),
    [false, false, false],
  );
  assert.deepEqual(
    offers.map((o) => o.href),
    ["/api/checkout/trial", "/api/checkout/monthly", "/api/checkout/lifetime"],
  );
});

test("a link that is not https is not a link", () => {
  const env = { POLAR_CHECKOUT_MONTHLY: "buy.polar.sh/abc" };
  assert.equal(core.checkoutUrl(env, "monthly"), null);
  assert.equal(
    core.checkoutUrl({ POLAR_CHECKOUT_MONTHLY: "https://buy.polar.sh/abc" }, "monthly"),
    "https://buy.polar.sh/abc",
  );
});

test("a signed-in buyer carries their Clerk id into checkout as reference_id", () => {
  const env = { POLAR_CHECKOUT_MONTHLY: "https://buy.polar.sh/abc" };
  const target = core.checkoutTarget(env, "monthly", {
    clerkId: "user_2abc",
    email: "ada@example.com",
  });
  const url = new URL(target);
  assert.equal(url.searchParams.get("reference_id"), "user_2abc");
  assert.equal(url.searchParams.get("customer_email"), "ada@example.com");
});

test("the id that goes out is the id that comes back", () => {
  // The round trip this whole mechanism exists for: what /api/checkout puts
  // on the link is what the webhook reads off the event.
  const env = { POLAR_CHECKOUT_MONTHLY: "https://buy.polar.sh/abc" };
  const sent = new URL(core.checkoutTarget(env, "monthly", { clerkId: "user_2abc" }));
  const reference = sent.searchParams.get("reference_id");
  const verdict = core.spineFromEvent(subscription({ metadata: { reference_id: reference } }));
  assert.equal(verdict.clerkId, "user_2abc");
});

test("a stranger's checkout link carries nothing it does not know", () => {
  const env = { POLAR_CHECKOUT_LIFETIME: "https://buy.polar.sh/xyz" };
  const url = new URL(core.checkoutTarget(env, "lifetime", null));
  assert.equal(url.searchParams.get("reference_id"), null);
  assert.equal(url.searchParams.get("customer_email"), null);
  assert.equal(url.toString(), "https://buy.polar.sh/xyz");
});

test("an unknown plan has no checkout target", () => {
  const env = { POLAR_CHECKOUT_MONTHLY: "https://buy.polar.sh/abc" };
  assert.equal(core.checkoutTarget(env, "annual", { clerkId: "user_1" }), null);
  assert.equal(core.offerById("annual"), null);
});
