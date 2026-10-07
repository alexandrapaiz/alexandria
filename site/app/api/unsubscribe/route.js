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

  // Two callers, one handler. The confirm page posts the token in the form
  // body. A mail client performing RFC 8058 one-click unsubscribe posts to the
  // URI in the `List-Unsubscribe` header with the fixed body
  // `List-Unsubscribe=One-Click`, so for that caller the token can only be in
  // the query string. Reading both is what lets the press add the header later
  // without a second endpoint, and the scanner problem the confirm page exists
  // for does not come back, because this is still POST-only and a GET still
  // answers 405.
  const url = new URL(request.url);
  const token = (form && form.get("t")) || url.searchParams.get("t");

  const result = await unsubscribeByToken(token).catch(() => ({
    ok: false,
    retryable: true,
    reason: "the update threw",
  }));
  const state = unsubscribeState(result);

  // A redirect rather than JSON, because the caller is a form in a page and
  // not a script. 303 is the code that turns the POST into a GET, so the
  // browser's back button does not offer to submit it again.
  const back = new URL("/unsubscribe", request.url);
  back.searchParams.set("state", state);
  return NextResponse.redirect(back, 303);
}
