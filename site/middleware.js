import { clerkMiddleware } from "@clerk/nextjs/server";
import { record } from "./lib/path";

// Clerk's middleware, plus the one line that measures the buyer's path.
// Board card c688ef2e.
//
// ## Why the measurement lives here and not in a page or a script
//
// Three reasons, in the order they decided it.
//
// **It is the only place that sees every arrival.** A beacon in a component
// sees the pages that component is on, and the pages a buyer walks are owned
// by the frontend seat and are being rewritten this week. Middleware sees the
// request, so the measurement does not need a line in any page and cannot be
// lost by a page being rewritten.
//
// **It needs no client JavaScript at all.** There is no script to block, no
// request for an ad blocker to drop, and nothing to load before a reader sees
// the page. An agent reading the site with curl is counted the same as a
// person with a browser, which for this product is the audience rather than
// an edge case.
//
// **It keeps the promise on site/app/privacy/page.jsx.** That page says there
// is no tracking pixel and no third-party script watching you read, and this
// is neither. site/lib/path-core.js is the long version of what follows from
// that sentence: a row is a step, a path and a timestamp, with no address, no
// user agent, no cookie and no identifier of any kind.
//
// ## After the response, never before it
//
// `event.waitUntil` is the whole reason this is safe to put on the request
// path. The response is returned first and the insert runs after it, so the
// person reading the page waits for the page and never for the database. A
// measurement that costs a reader latency is a measurement someone correctly
// removes later.
//
// `record` cannot throw and cannot reject (site/lib/path.js), so there is no
// `catch` here to go stale. The `.catch` is still written, because a promise
// handed to `waitUntil` that rejects for a reason this file did not predict
// would surface as an unhandled rejection in the platform's log rather than
// as a lost count, and a lost count is the intended failure.
export default clerkMiddleware((auth, request, event) => {
  event?.waitUntil?.(
    record({
      method: request.method,
      pathname: request.nextUrl.pathname,
      headers: request.headers,
    }).catch(() => null)
  );
});

export const config = {
  matcher: [
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    "/(api|trpc)(.*)",
    "/__clerk/:path*",
  ],
};
