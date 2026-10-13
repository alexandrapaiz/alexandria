import { readEvent, applyPolarEvent } from "../../../lib/polar";

// Polar's events, written into the Clerk user's metadata and the `users`
// row (ADR-30, ADR-31). Polar is the Merchant of Record, so this endpoint
// is the only place in the product that learns anybody paid, and the flag
// it writes is the only thing a paid surface reads.
//
// Setup, once, in the Polar dashboard: add a webhook endpoint pointing at
// /api/polar-webhook, subscribe it to the subscription and order events,
// and put its signing secret in the environment as POLAR_WEBHOOK_SECRET.
// docs/product/polar-go-live.md is the full checklist and it is the only
// thing between this code and a live sale.
//
// The route is public because site/middleware.js calls clerkMiddleware()
// with no handler, which protects nothing. If a handler is ever added
// there, this path has to be excluded, the same way /api/clerk-webhook
// does, or Polar's deliveries get a 401 and every payment goes unrecorded.

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request) {
  // The raw text, before anything parses it. The signature covers the
  // bytes that arrived, so a parse-then-reserialize loses the whitespace
  // and the key order and the HMAC stops matching for an honest caller.
  const body = await request.text().catch(() => null);
  if (body === null) {
    return Response.json({ ok: false, error: "no body" }, { status: 400 });
  }

  const read = readEvent({ body, headers: request.headers });
  if (!read.ok) {
    // Says nothing about why. The reasons describe the state of the secret
    // and the freshness window, and the caller who failed verification is
    // exactly the caller who should not learn either.
    console.error(`polar-webhook: rejected, ${read.reason}`);
    return Response.json({ ok: false, error: "invalid signature" }, { status: 401 });
  }

  const type = read.event?.type ?? "unknown";

  try {
    const result = await applyPolarEvent(read.event);

    // An unrecognised subscription status closed a door this code did not
    // know how to read. That is a vocabulary gap rather than a failure, so
    // the event is still acknowledged, and this line is how the gap gets
    // noticed instead of staying quiet until somebody complains.
    if (result.verdict?.unknownStatus) {
      console.error(
        `polar-webhook: ${type} carried an unknown status ` +
          `"${result.verdict.status}", so access was closed`,
      );
    }

    // Two kinds of failure and the status code is the only way to tell
    // Polar which one it was. A missing DATABASE_URL or a users row that
    // has not arrived yet is temporary, and the retry lands it. A buyer
    // with no account will never succeed, so it is acknowledged and logged
    // rather than retried on a schedule for a day.
    if (!result.ok && result.retryable) {
      console.error(`polar-webhook: ${type} deferred, ${result.reason}`);
      return Response.json({ ok: false, error: "not ready" }, { status: 503 });
    }
    if (!result.ok) {
      console.error(`polar-webhook: ${type} skipped, ${result.reason}`);
      return Response.json({ ok: true, skipped: result.reason });
    }

    return Response.json({
      type,
      ok: true,
      ignored: result.ignored,
      entitled: result.entitled,
      tier: result.tier,
      until: result.until,
      matchedBy: result.matchedBy,
    });
  } catch (err) {
    // Clerk or the database being down is worth retrying, so this is a 500
    // and Polar brings the event back. The message stays server-side.
    console.error(`polar-webhook: ${type} failed`, err);
    return Response.json({ ok: false, error: "write failed" }, { status: 500 });
  }
}
