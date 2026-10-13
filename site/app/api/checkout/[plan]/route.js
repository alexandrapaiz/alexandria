import { NextResponse } from "next/server";
import { currentAccount } from "../../../../lib/account";
import { checkoutRedirect } from "../../../../lib/polar";
import { offerById } from "../../../../lib/polar-core";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

// The hop between the pricing page and Polar's checkout, and it exists for
// one reason: identity.
//
// Polar copies a checkout link's `reference_id` onto the order and the
// subscription it produces, so a buyer who passed through here arrives at
// /api/polar-webhook carrying their own Clerk id, and the webhook matches
// them exactly instead of by the email address they typed into a payment
// form. A bare link on the page cannot do that, because the page is static
// and does not know who is reading it.
//
// It also keeps /pricing static. Only this route is dynamic.
//
// GET rather than POST, which is the opposite of /api/unsubscribe's call
// and for the opposite reason: a link preview fetching this one starts a
// checkout session nobody is charged for, where a GET unsubscribe flips a
// row. Nothing here changes any state.
export async function GET(request, { params }) {
  const { plan } = await params;

  if (!offerById(plan)) {
    return NextResponse.redirect(new URL("/pricing", request.url), 303);
  }

  // Sign-in first, and this is what closes the integration's one real gap.
  // A payment with no account behind it has nothing to grant access to, so
  // the webhook can only log it and the owner has to invite the buyer by
  // hand. Asking for the account before the card means that case only
  // arises for someone who found a Polar link somewhere other than here.
  const account = await currentAccount().catch(() => null);
  if (!account) {
    const back = new URL("/sign-up", request.url);
    back.searchParams.set("redirect_url", `/api/checkout/${plan}`);
    return NextResponse.redirect(back, 303);
  }

  // No link configured means the owner has not created the products yet.
  // The pricing page already renders a note instead of a button in that
  // case, so reaching this is a stale tab or a typed URL, and /pricing is
  // the honest place to send it.
  const target = checkoutRedirect(plan, account);
  if (!target) {
    return NextResponse.redirect(new URL("/pricing", request.url), 303);
  }

  return NextResponse.redirect(target, 303);
}
