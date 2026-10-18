import { NextResponse } from "next/server";
import { readFunnel, clampDays } from "../../../lib/path";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// GET /api/funnel, the buyer's path as counts, public and unauthenticated.
// Board card c688ef2e.
//
// It is unauthenticated for the reason `/api/delivery` gives at length in its
// own header: no agent seat holds a database credential, and every seat is
// asked to say whether the product is reaching anybody. A surface behind a
// token would need that token distributed to twelve workflow files, which is
// a cost nobody has agreed to pay for a page-view count.
//
// What it exposes is bounded by site/lib/path-core.js and by the table
// itself, and the bound is not a redaction rule here because there is nothing
// to redact. `path_events` holds no address, no user agent, no identifier and
// no product text. The strongest thing a reader learns from this endpoint is
// that four people opened a skill page last week.
//
// **One thing here is the owner's call rather than this seat's, and it is
// published rather than hidden so she can find it.** This endpoint says how
// many people visited and how many accounts are paying, at a stable public
// URL, which is a commercially legible pair of numbers in a way the delivery
// receipt's press metadata is not. It is public because that is the only
// shape a seat with no credential can read, which is the same trade
// `/api/delivery` made and is why that file's argument is not repeated here.
// If the owner would rather not publish the second number, removing
// `paidAccounts()` from `readFunnel` in site/lib/path.js costs the payment row
// and nothing else: every other step keeps working, and the report reads that
// step as unmeasured with a reason, which is a state it already handles.
//
// **Facts, never verdicts**, which is the other rule `/api/delivery` set.
// This says the checkout step has one event. It never says the funnel is
// broken. `tools/buyer_path.py` holds that judgement in one copy, so the
// credential-free reader and the credentialled one cannot reach different
// conclusions from the same rows.
//
// Cached for five minutes, the same window as the delivery receipt and for
// the same reason: the reader is a daily standup, freshness below five
// minutes buys nothing, and Vercel's Hobby plan counts function invocations
// while Neon's free tier counts compute hours. HQ incident 5 is this company
// exhausting a free tier's unit by not asking which unit it was.
const CACHE = "public, s-maxage=300, stale-while-revalidate=600";

export async function GET(request) {
  const days = clampDays(new URL(request.url).searchParams.get("days"));
  const body = await readFunnel(days).catch(() => null);

  if (!body || !body.counts_read) {
    // 503 and not a funnel of zeros. A reader that cannot tell "nobody came"
    // from "I could not read the database" will eventually report a working
    // site as a dead one, and a report that does that once teaches its reader
    // to stop reading it.
    return NextResponse.json(
      {
        receipt: "alexandria-funnel",
        ok: false,
        reason: body?.counts_reason ?? "the funnel could not be read",
      },
      { status: 503, headers: { "Cache-Control": "no-store" } }
    );
  }

  return NextResponse.json(
    { receipt: "alexandria-funnel", ok: true, ...body },
    { headers: { "Cache-Control": CACHE } }
  );
}
