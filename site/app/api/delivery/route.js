import { NextResponse } from "next/server";
import { loadDeliveryReceipt } from "../../../lib/delivery.js";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// GET /api/delivery — the delivery receipt, public and unauthenticated.
//
// It is unauthenticated on purpose. Its whole reason for existing is that no
// agent seat holds a database credential and every seat is asked daily whether
// the press printed (docs/agents/delivery-health.md guardrail 4). A receipt
// behind a token would need that token distributed to twelve workflows, which
// is the cost the ledger entry this closes was waiting on the owner to pay.
//
// What it exposes is bounded by lib/delivery-core.js, which builds every field
// by name: the newest issue's week, model and date, when the corpus last moved,
// how many rows wait at each pipeline stage, and the content digests the
// scheduled jobs report. No issue text, no claim text, no subscriber, no
// address, no key. See that file's header for the rule.
//
// Cached at the edge for five minutes. The reader of this is a standup that runs
// once a day and a drift guard whose smallest unit is 24 hours, so freshness
// below five minutes buys nothing, and the host's metered unit is the thing to
// protect: Vercel's Hobby plan counts function invocations and Neon's free tier
// counts compute hours, and HQ incident 5 is this company exhausting a free
// tier's unit by not asking which unit it was. Five minutes is one origin
// request per edge region per five minutes however hard anyone refreshes.
const CACHE = "public, s-maxage=300, stale-while-revalidate=600";

export async function GET() {
  const { receipt, reason } = await loadDeliveryReceipt();

  if (!receipt) {
    // 503 and not an empty receipt. A reader that cannot tell "nothing has
    // been published" from "I could not read the database" will eventually
    // report a healthy press as broken, and a report that does that once
    // teaches its reader to stop reading it.
    //
    // The reason is carried through because it is the only diagnosis available
    // to a seat with no access to this project's environment: a missing
    // DATABASE_URL is one setting away from working and a failing query is not.
    return NextResponse.json(
      { receipt: "alexandria-delivery", ok: false, reason },
      { status: 503, headers: { "Cache-Control": "no-store" } }
    );
  }

  return NextResponse.json(receipt, { headers: { "Cache-Control": CACHE } });
}
