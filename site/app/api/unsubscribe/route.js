import { NextResponse } from "next/server";
import { unsubscribeByToken } from "../../../lib/unsubscribe";
import { unsubscribeState } from "../../../lib/unsubscribe-core";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// POST only, and there is no GET export in this file on purpose. A link in an
// email is fetched by mail scanners, link previewers and corporate security
// proxies before any person reads it, so a GET that flipped the row would
// unsubscribe people who never clicked anything. The link opens
// /unsubscribe, that page asks, and the button posts here.
export async function POST(request) {
  const form = await request.formData().catch(() => null);
  const token = form ? form.get("t") : null;

  const result = await unsubscribeByToken(token).catch(() => ({
    ok: false,
    retryable: true,
    reason: "the update threw",
  }));
  const state = unsubscribeState(result);

  // A redirect rather than JSON, because the caller is a form in a page and
  // not a script. 303 is the code that turns the POST into a GET, so the
  // browser's back button does not offer to submit it again.
  const url = new URL("/unsubscribe", request.url);
  url.searchParams.set("state", state);
  return NextResponse.redirect(url, 303);
}
