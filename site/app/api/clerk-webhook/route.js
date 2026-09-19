import { verifyWebhook } from "@clerk/nextjs/webhooks";
import { isHandledEvent } from "../../../lib/clerk-user";
import { upsertUserFromClerk, deleteUserByClerkId } from "../../../lib/account";

// Clerk's user events, written into Neon (ADR-30). Clerk is the surface
// where an account is created; this endpoint is how that becomes a row we
// own. Nothing else writes to `users`.
//
// Setup, once, in the Clerk dashboard: add an endpoint pointing at
// /api/clerk-webhook, subscribe it to user.created, user.updated and
// user.deleted, and put that endpoint's signing secret in the environment
// as CLERK_WEBHOOK_SIGNING_SECRET. verifyWebhook reads that name itself,
// so no key is ever passed through this file.
//
// The route is public because site/middleware.js calls clerkMiddleware()
// with no handler, which protects nothing. If a handler is ever added
// there, this path has to be excluded, or Clerk answers its own webhook
// with a 401 and every event fails.

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request) {
  let evt;
  try {
    // Reads CLERK_WEBHOOK_SIGNING_SECRET from the environment and throws on
    // a bad signature. An unverified body is an anonymous stranger claiming
    // to be Clerk, so this runs before anything looks at the payload.
    evt = await verifyWebhook(request);
  } catch {
    // Deliberately says nothing about why. The error text can describe the
    // secret's state, and the caller that failed verification is exactly
    // the caller who should not learn that.
    return Response.json({ ok: false, error: "invalid signature" }, { status: 400 });
  }

  const type = evt?.type;

  // An event we do not handle is still an event Clerk delivered correctly.
  // Answering 2xx retires it; answering 4xx makes Svix retry it on a
  // schedule, forever, for no reason.
  if (!isHandledEvent(type)) {
    return Response.json({ ok: true, ignored: type ?? "unknown" });
  }

  try {
    const result =
      type === "user.deleted"
        ? await deleteUserByClerkId(evt.data?.id)
        : await upsertUserFromClerk(evt.data);

    // Two kinds of failure, and the status code is the only way to tell
    // Svix which one this was. A missing DATABASE_URL is temporary: the
    // owner sets it and the retry lands the row. An event with no id or no
    // email will never succeed, so it is acknowledged and logged instead
    // of retried on a schedule forever.
    if (!result.ok && result.retryable) {
      console.error(`clerk-webhook: ${type} deferred, ${result.reason}`);
      return Response.json({ ok: false, error: "not ready" }, { status: 503 });
    }
    if (!result.ok) {
      console.error(`clerk-webhook: ${type} skipped, ${result.reason}`);
    }

    return Response.json({ type, ...result });
  } catch (err) {
    // A database that is down is worth retrying, so this one is a 500 and
    // Svix will bring the event back. The message stays server-side.
    console.error(`clerk-webhook: ${type} failed`, err);
    return Response.json({ ok: false, error: "write failed" }, { status: 500 });
  }
}
