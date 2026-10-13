// Every decision the payments layer makes, as pure functions: whether a
// request really came from Polar, what a Polar event means for one person's
// access, and whether an access flag already written is still good. No
// imports, no network, no database, no clock of its own. The one primitive
// this cannot do without, an HMAC, arrives as an argument.
//
// site/lib/polar.js is the other half and it does the I/O.
//
// Keep this file import-free. tests/polar.test.mjs loads it by reading the
// source and evaluating it, the same way tests/accounts.test.mjs loads
// site/lib/account-core.js, and that works precisely because there are no
// imports to resolve. It is cheaper than making the whole site a module
// package to test a dozen functions.
//
// The design, in one paragraph. Polar is the Merchant of Record (ADR-30),
// so it is the legal seller and the only thing it tells us is that someone
// paid. Turning that into access is this file's job, and the rule lives in
// exactly one function, `spineFromEvent`. The webhook writes that one
// verdict into two places: the Clerk user's metadata, which is what every
// read consults, and the `users` row in Neon, which is the durable billing
// record. Two stores, one decision, so they cannot disagree about who may
// open a paid surface.

// ------------------------------------------------------- the three offers
//
// ADR-31's plan shape. The ids are this codebase's names for the three
// products the owner creates in Polar, and nothing here knows their Polar
// ids: a checkout link is a URL the owner pastes into the environment, so
// the three products can be created, renamed or repriced in the dashboard
// without a deploy.
export const OFFERS = [
  {
    id: "trial",
    env: "POLAR_CHECKOUT_TRIAL",
    label: "Start the 3-day trial",
  },
  {
    id: "monthly",
    env: "POLAR_CHECKOUT_MONTHLY",
    label: "Subscribe for $20 a month",
  },
  {
    id: "lifetime",
    env: "POLAR_CHECKOUT_LIFETIME",
    label: "Buy lifetime access for $200",
  },
];

export function offerById(id) {
  return OFFERS.find((offer) => offer.id === id) ?? null;
}

const clean = (v) => (typeof v === "string" && v.trim() ? v.trim() : null);

// Polar's own checkout links are `https://buy.polar.sh/...` on live and
// `https://sandbox-api.polar.sh/...` style hosts on sandbox. Rather than
// guess the host, this requires https and nothing else: the owner pastes
// the URL Polar gave her, and a typo that is not a URL at all is caught
// here instead of becoming a dead button on the pricing page.
export function checkoutUrl(env, id) {
  const offer = offerById(id);
  if (!offer) return null;
  const raw = clean(env?.[offer.env]);
  if (!raw) return null;
  if (!raw.startsWith("https://")) return null;
  return raw;
}

// What the pricing page renders. Every offer always appears, because the
// three plans are the product's shape whether or not checkout is open yet.
// `live` is what decides between a button and a quiet note.
export function checkoutOffers(env) {
  return OFFERS.map((offer) => ({
    ...offer,
    live: checkoutUrl(env, offer.id) !== null,
    href: `/api/checkout/${offer.id}`,
  }));
}

// The identity the buyer carries into Polar's checkout, and the whole
// reason /api/checkout exists rather than a bare link on the page.
//
// `reference_id` is a documented checkout-link query parameter and Polar
// copies it into the checkout session's metadata, which it then copies onto
// the resulting order and subscription. So a buyer who was signed in when
// they clicked arrives back at the webhook carrying their own Clerk id, and
// matching is exact instead of by email address. `customer_email` only
// prefills the form, so it is a convenience and never the match.
//
// Both are omitted for a stranger. Buying without an account is allowed and
// resolves by email later, which is what `spineFromEvent` falls back to.
export function checkoutTarget(env, id, account) {
  const base = checkoutUrl(env, id);
  if (!base) return null;

  const url = new URL(base);
  const clerkId = clean(account?.clerkId);
  const email = clean(account?.email);
  if (clerkId) url.searchParams.set("reference_id", clerkId);
  if (email) url.searchParams.set("customer_email", email);
  return url.toString();
}

// ------------------------------------------------- verifying the request
//
// Polar signs webhooks under the Standard Webhooks specification, which is
// three headers and an HMAC over a string the receiver rebuilds itself.
// Polar's own note, read 2026-10-13: secrets created on or after
// 2026-09-08 follow that specification and older secrets use a Polar scheme
// that predates it. Nothing here implements the older scheme, because the
// account does not exist yet and any secret it produces will be new.
export const SIGNATURE_HEADERS = {
  id: "webhook-id",
  timestamp: "webhook-timestamp",
  signature: "webhook-signature",
};

// Five minutes, the specification's own recommendation. A replay of a
// correctly signed body is still an attack, and the timestamp is signed
// alongside the body precisely so the receiver can refuse an old one.
export const SIGNATURE_TOLERANCE_SECONDS = 300;

// Reads a Headers object or a plain object, case-insensitively, because a
// test hands over the second and the runtime hands over the first.
export function headerValue(headers, name) {
  if (!headers) return null;
  if (typeof headers.get === "function") return clean(headers.get(name));
  const key = Object.keys(headers).find((k) => k.toLowerCase() === name.toLowerCase());
  return key ? clean(String(headers[key])) : null;
}

// The HMAC key, and the one place in this integration where the published
// sources disagree with each other.
//
// Standard Webhooks says the secret is `whsec_` followed by base64, and the
// key is those decoded bytes. Polar's dashboard secrets carry no prefix,
// and Polar's own SDKs base64-encode the dashboard string before handing it
// to a Standard Webhooks library, which then decodes it again. The two
// steps cancel, so for a Polar secret the key is the raw bytes of the
// string the owner pasted.
//
// This implements that, and also accepts a `whsec_`-prefixed secret by
// decoding it, since the prefix is unambiguous about which encoding it is.
// A verifier that guessed would be a verifier that could be wrong quietly,
// and a signature check that is quietly wrong is the one bug in this file
// that lets a stranger grant themselves access.
export function secretKeyBytes(secret) {
  const value = clean(secret);
  if (!value) return null;

  if (value.startsWith("whsec_")) {
    const encoded = value.slice("whsec_".length);
    try {
      const binary = atob(encoded);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
      return bytes;
    } catch {
      return null;
    }
  }

  return new TextEncoder().encode(value);
}

// The signed string, rebuilt from the raw body. The body has to be the
// bytes that arrived: parse it first and re-serialize it and the key order,
// the spacing and the unicode escapes all become yours rather than Polar's,
// and the HMAC no longer matches anything.
export function signedContent(id, timestamp, body) {
  return `${id}.${timestamp}.${body}`;
}

// `v1,<base64> v1,<base64>` during a secret rotation, so every v1 entry is
// a candidate and one match is enough. Versions this does not know are
// dropped rather than treated as opaque matches.
export function signatureCandidates(header) {
  const value = clean(header);
  if (!value) return [];
  return value
    .split(" ")
    .map((part) => part.trim())
    .filter((part) => part.startsWith("v1,"))
    .map((part) => part.slice("v1,".length))
    .filter(Boolean);
}

// Length-independent comparison. The lengths are public here (a base64
// SHA-256 is always the same length) but a short-circuit on the first
// differing byte is the habit worth not having in a file like this.
export function constantTimeEqual(a, b) {
  const left = typeof a === "string" ? a : "";
  const right = typeof b === "string" ? b : "";
  let diff = left.length ^ right.length;
  const length = Math.max(left.length, right.length);
  for (let i = 0; i < length; i += 1) {
    diff |= (left.charCodeAt(i) || 0) ^ (right.charCodeAt(i) || 0);
  }
  return diff === 0;
}

export function timestampIsFresh(timestamp, nowMs, toleranceSeconds = SIGNATURE_TOLERANCE_SECONDS) {
  const seconds = Number(timestamp);
  if (!Number.isFinite(seconds)) return false;
  const skew = Math.abs(nowMs / 1000 - seconds);
  return skew <= toleranceSeconds;
}

// The whole check, in the order that matters: a missing secret refuses
// before a missing header, a missing header refuses before any arithmetic,
// and the timestamp is judged before the HMAC is computed at all, so an old
// replay costs no hashing.
//
// `hmacSha256Base64(keyBytes, message)` is the injected primitive. The
// caller passes node's crypto, the test passes node's crypto too, and this
// file stays import-free.
export function verifySignature({ body, headers, secret, nowMs }, hmacSha256Base64) {
  const key = secretKeyBytes(secret);
  if (!key) return { ok: false, reason: "POLAR_WEBHOOK_SECRET is not set" };

  const id = headerValue(headers, SIGNATURE_HEADERS.id);
  const timestamp = headerValue(headers, SIGNATURE_HEADERS.timestamp);
  const signature = headerValue(headers, SIGNATURE_HEADERS.signature);
  if (!id || !timestamp || !signature) {
    return { ok: false, reason: "a signature header is missing" };
  }

  if (!timestampIsFresh(timestamp, nowMs)) {
    return { ok: false, reason: "the signed timestamp is outside the tolerance" };
  }

  const candidates = signatureCandidates(signature);
  if (candidates.length === 0) {
    return { ok: false, reason: "no v1 signature in the header" };
  }

  const expected = hmacSha256Base64(key, signedContent(id, timestamp, body ?? ""));
  const matched = candidates.some((candidate) => constantTimeEqual(candidate, expected));
  return matched ? { ok: true, id } : { ok: false, reason: "the signature does not match" };
}

// ----------------------------------------------- what an event means
//
// Polar sends forty event types. These are the ones that change whether a
// person may open a paid surface, and anything else is acknowledged and
// ignored. The list is deliberately wider than it strictly needs to be:
// `subscription.updated` already carries every transition, and the specific
// events are also handled so that an endpoint subscribed to only some of
// them in the dashboard still works.
export const HANDLED_EVENTS = [
  "subscription.created",
  "subscription.active",
  "subscription.updated",
  "subscription.canceled",
  "subscription.uncanceled",
  "subscription.past_due",
  "subscription.paused",
  "subscription.resumed",
  "subscription.cycled",
  "subscription.revoked",
  "order.paid",
  "order.refunded",
];

export function isHandledEvent(type) {
  return HANDLED_EVENTS.includes(type);
}

// Polar's SubscriptionStatus, from its OpenAPI schema, read 2026-10-13:
// incomplete, incomplete_expired, trialing, active, past_due, canceled,
// unpaid, paused. Mapped here onto the two questions this product asks.
//
// `open` is whether the door is open. `billing` is what the `users` row
// records, and its vocabulary is the check constraint in db/schema.sql,
// which is free, active, past_due or canceled and predates this file.
//
// past_due opens the door. The customer paid for the period they are in
// and the renewal is what failed, so access runs to `current_period_end`
// and stops there. That is the owner's billing principle on the pricing
// page, which is that we would rather earn the renewal than collect it,
// applied to the one case where a card is the thing that lapsed.
const SUBSCRIPTION_STATUS = {
  trialing: { open: true, billing: "active" },
  active: { open: true, billing: "active" },
  past_due: { open: true, billing: "past_due" },
  paused: { open: false, billing: "past_due" },
  incomplete: { open: false, billing: "past_due" },
  incomplete_expired: { open: false, billing: "canceled" },
  unpaid: { open: false, billing: "canceled" },
  canceled: { open: false, billing: "canceled" },
};

// An unrecognised status closes the door and records the end of access.
// Polar can add a status and this file will not know it, so the choice is
// between a stranger's door and a customer's complaint, and the complaint
// is recoverable. The route logs the unknown value, which is how a
// vocabulary gap becomes visible rather than quiet.
export const UNKNOWN_SUBSCRIPTION_STATUS = { open: false, billing: "canceled", unknown: true };

export function subscriptionStatusMeaning(status) {
  return SUBSCRIPTION_STATUS[status] ?? UNKNOWN_SUBSCRIPTION_STATUS;
}

const iso = (v) => {
  const value = clean(v);
  if (!value) return null;
  const t = Date.parse(value);
  return Number.isFinite(t) ? new Date(t).toISOString() : null;
};

// Which Clerk user this event is about, in the order of how much it can be
// trusted. `reference_id` is what /api/checkout put there and it is a Clerk
// id we issued. `external_id` is the same idea if the owner ever sets it
// through the API. The email is a fallback and it is a match on a string
// the buyer typed, which is why it is last.
export function subjectOf(data) {
  const customer = data?.customer ?? null;
  const metadata = data?.metadata ?? {};
  return {
    clerkId:
      clean(metadata.reference_id) ??
      clean(metadata.clerk_id) ??
      clean(customer?.external_id) ??
      null,
    email: clean(customer?.email)?.toLowerCase() ?? null,
    polarCustomerId: clean(data?.customer_id) ?? clean(customer?.id) ?? null,
  };
}

// The tier a subscription is on, for the record rather than for the gate.
// A trial and a paid month open the same door, and the difference is worth
// writing down because the trial is the one that converts or does not.
function subscriptionTier(sub) {
  if (sub?.status === "trialing") return "trial";
  return "monthly";
}

// The one rule, for one event. Returns null when the event says nothing
// about access, and otherwise the whole verdict, which the caller writes to
// Clerk and to Neon without deciding anything further.
//
// `until` is when the door closes by itself, which matters because nothing
// here runs on a clock. Polar's revoke event may be late or may never
// arrive, so an entitlement that carries its own expiry is an entitlement
// that cannot outlive what was paid for. A lifetime purchase has no expiry
// and that is the only case where `until` is null with the door open.
export function spineFromEvent(event) {
  const type = clean(event?.type);
  const data = event?.data ?? null;
  if (!type || !data) return null;
  if (!isHandledEvent(type)) return null;

  const subject = subjectOf(data);

  if (type.startsWith("subscription.")) {
    const meaning = subscriptionStatusMeaning(data.status);
    const open = meaning.open;
    return {
      ...subject,
      event: type,
      status: clean(data.status),
      unknownStatus: meaning.unknown === true,
      hasSpine: open,
      tier: open ? subscriptionTier(data) : null,
      // The trial's own end beats the period end while a trial is running,
      // because Polar sets both and the trial is the shorter of the two.
      until: open
        ? (data.status === "trialing" ? iso(data.trial_end) : null) ??
          iso(data.current_period_end) ??
          iso(data.ends_at)
        : null,
      billingStatus: meaning.billing,
      polarSubscriptionId: clean(data.id),
    };
  }

  // An order. The only order that grants anything by itself is a one-time
  // purchase of a non-recurring product, which is ADR-31's $200 lifetime
  // tier. Every other paid order is a subscription's first charge or its
  // renewal, and the subscription events above already said what it means,
  // so handling it here would be a second opinion on a settled question.
  const product = data.product ?? null;
  const recurring = product?.is_recurring === true || clean(data.subscription_id) !== null;
  if (recurring) return null;

  const refunded = type === "order.refunded";
  const paid = data.paid === true || data.status === "paid";
  if (!refunded && !paid) return null;

  return {
    ...subject,
    event: type,
    status: clean(data.status),
    unknownStatus: false,
    hasSpine: !refunded,
    tier: refunded ? null : "lifetime",
    until: null,
    billingStatus: refunded ? "canceled" : "active",
    polarSubscriptionId: null,
  };
}

// ------------------------------------------- reading the flag back out
//
// What the webhook writes onto the Clerk user, under publicMetadata. Public
// rather than private for one reason: it rides in the session token, so a
// server component can gate a surface without a round trip to Clerk's API,
// and there is nothing in it a person should not see about themselves.
export function spineMetadata(verdict, nowIso) {
  if (!verdict) return null;
  return {
    hasSpine: verdict.hasSpine === true,
    spineTier: verdict.tier ?? null,
    spineUntil: verdict.until ?? null,
    spineSource: "polar",
    spineEvent: verdict.event ?? null,
    spineUpdatedAt: nowIso ?? null,
    polarCustomerId: verdict.polarCustomerId ?? null,
    polarSubscriptionId: verdict.polarSubscriptionId ?? null,
  };
}

// The read every paid surface makes, and it fails closed at every step: no
// metadata, no flag, an expiry that has passed, or an expiry that cannot be
// parsed all come back false. A gate that opens on a value it could not
// read is not a gate.
export function spineFromMetadata(metadata, nowMs) {
  if (!metadata || metadata.hasSpine !== true) return false;

  const until = metadata.spineUntil;
  if (until === null || until === undefined || until === "") return true;

  const t = Date.parse(until);
  if (!Number.isFinite(t)) return false;
  return t > nowMs;
}
