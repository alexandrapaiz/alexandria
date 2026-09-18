import { NextResponse } from "next/server";
import { saveWaitlistEmail } from "../../../lib/waitlist";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// Deliberately loose: the only thing worth rejecting here is a typo the
// person can see for themselves. Anything stricter turns a valid address
// into a dead end.
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

export async function POST(request) {
  let body = null;
  try {
    body = await request.json();
  } catch {
    body = null;
  }

  const email = String(body?.email ?? "").trim().toLowerCase();
  const source = String(body?.source ?? "").slice(0, 32);

  if (!EMAIL.test(email) || email.length > 254) {
    return NextResponse.json(
      { ok: false, error: "That does not look like an email address." },
      { status: 400 }
    );
  }

  try {
    await saveWaitlistEmail(email, source);
  } catch {
    return NextResponse.json(
      { ok: false, error: "Something went wrong. Please try again." },
      { status: 500 }
    );
  }

  // A duplicate is a success: the person is on the list either way, and
  // telling them otherwise would only make them wonder.
  return NextResponse.json({ ok: true });
}
