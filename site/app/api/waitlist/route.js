import { NextResponse } from "next/server";
import { subscribe } from "../../../lib/waitlist";
import { normalizeEmail } from "../../../lib/waitlist-core";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request) {
  let body = null;
  try {
    body = await request.json();
  } catch {
    body = null;
  }

  // Validated here as well as inside `subscribe`, because the two answers are
  // different answers. A bad address is the person's own typo and it gets a
  // 400 with something they can act on. Anything after this point is ours.
  if (!normalizeEmail(body?.email)) {
    return NextResponse.json(
      { ok: false, error: "That does not look like an email address." },
      { status: 400 }
    );
  }

  const result = await subscribe(body?.email, body?.source).catch(() => ({
    ok: false,
    retryable: true,
    reason: "the insert threw",
  }));

  if (!result.ok) {
    // 503 rather than 500 when the database is simply not reachable yet: the
    // request was fine, the list was not, and the difference is the one thing
    // a log would need to tell those two apart later.
    return NextResponse.json(
      { ok: false, error: "Something went wrong. Please try again." },
      { status: result.retryable ? 503 : 400 }
    );
  }

  // All three outcomes are a success to the person who submitted the form:
  // they are on the list either way, and telling them which one they were
  // would only make them wonder. `outcome` rides along for the owner's counts
  // and the browser ignores it.
  return NextResponse.json({ ok: true, outcome: result.outcome });
}
