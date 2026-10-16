import { readEvent, applyPolarEvent, notePolarOutcome } from "../../../lib/polar";

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

  // Every outcome below passes through this, which writes the row the daily
  // standup reads: a `payment_exceptions` row when the payment did not become
  // access, and a resolution of any open row for the same delivery when it
  // did. It cannot throw and it cannot fail the webhook, so it is safe to put
  // on the path every branch takes.
  //
  // It is a closure rather than four call sites so that a branch added later
  // cannot forget it. The log line stays beside it, because a row and a log
  // line answer different readers: the row is for the standup tomorrow and the
  // line is for whoever is tailing the function now.
  const note = async (result) => {
    const noted = await notePolarOutcome({ event: read.event, eventId: read.id, result });
    if (noted.exception && !noted.recorded) {
      // The alarm path itself is quiet, which is the one failure that hides
      // every other one. Applying db/schema.sql is a hand step, so a missing
      // `payment_exceptions` table is a state this really meets.
      console.error(
        `polar-webhook: ${type} could not be recorded as a payment exception, ` +
          `${noted.why}`,
      );
    }
    return noted;
  };

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
      const noted = await note(result);
      console.error(
        `polar-webhook: ${type} deferred, ${result.reason}` +
          (noted.attempts > 1 ? ` (attempt ${noted.attempts})` : ""),
      );
      return Response.json({ ok: false, error: "not ready" }, { status: 503 });
    }
    if (!result.ok) {
      await note(result);
      console.error(`polar-webhook: ${type} skipped, ${result.reason}`);
      return Response.json({ ok: true, skipped: result.reason });
    }

    // The success path writes too, and it has to. A delivery that was deferred
    // eleven times and then landed must close its own row, or the count the
    // standup reads only ever rises and the org learns to ignore it.
    await note(result);

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
    //
    // This branch gets a row as well, under `handler_threw`, and it is the one
    // the ledger entry did not name. A throw inside the Clerk write is a
    // payment that arrived, was verified, and left no trace of what happened
    // to it, which is strictly worse than the two refusals that at least knew
    // why they refused. The row carries the error's class and the customer id
    // read off the event, which is enough to find the charge in Polar.
    console.error(`polar-webhook: ${type} failed`, err);
    await note({
      ok: false,
      retryable: true,
      code: "handler_threw",
      reason: `the handler threw: ${err?.name ?? "Error"}`,
    }).catch(() => null);
    return Response.json({ ok: false, error: "write failed" }, { status: 500 });
  }
}
