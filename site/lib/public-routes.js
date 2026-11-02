// Which of this site's routes a crawler may index, declared once.
//
// Two files render this list and neither of them types it out: `app/robots.js`
// turns the not-indexable half into `Disallow` lines, and `app/sitemap.js`
// turns the indexable half into `<url>` entries. They cannot disagree with
// each other, because there is nothing here for them to disagree about. That
// is the whole reason this file exists rather than two hand-kept lists; the
// site has already paid once for the same value living in five places.
//
// The classification is not new. `app/llms.txt/route.js` has carried it in
// prose since 2026-10-26 — which routes it names for an agent and which it
// leaves out, each with its reason — and the reasons below are that reading.
//
// **It answers a narrower question than llms.txt does, and the difference is
// declared rather than discovered.** llms.txt answers "what should an agent
// read to use this product", so it names five routes. A crawler asks "what may
// be in a search result", which `/privacy` and `/terms` may be and llms.txt
// leaves out on purpose. Those two are the only routes where the lists differ.
// A route that changes sides changes here, and the prose in llms.txt is the
// other half of the same edit.
//
// `/library/<week>` is not in the table. The weeks are a record rather than a
// route list — `digests` gains a row on Monday morning without a deploy — so
// `app/sitemap.js` reads them from `lib/issues-live.js`, the same source
// `app/library/page.jsx` renders.

// The canonical origin. Absolute URLs are not optional in a sitemap: a
// relative <loc> is not a URL a crawler can fetch.
//
// Three other files hardcode this hostname (`app/privacy/page.jsx`,
// `app/terms/page.jsx`, `app/llms.txt/route.js`), where it is copy rather than
// configuration. This is the first place it is configuration. Pointing those
// three at this constant is a frontend change and is not made here.
export const SITE_ORIGIN = "https://libraryofalexandria.dev";

export const ROUTES = [
  { path: "/", index: true, why: "the front page" },
  {
    path: "/library",
    index: true,
    why: "every weekly issue, free and in full, with no entitlement check on the route",
  },
  {
    path: "/left-behind",
    index: true,
    why: "public by vision.md §0: the findings the library has stopped standing behind",
  },
  {
    path: "/skills",
    index: true,
    why: "the catalogue, the versions and the sources are public; only the skill bodies are entitled",
  },
  { path: "/pricing", index: true, why: "the three offers" },
  { path: "/mission", index: true, why: "why this exists" },
  {
    path: "/privacy",
    index: true,
    why: "the no-tracking promise this site keeps is worth finding; llms.txt omits it because an agent has nothing to do on it",
  },
  {
    path: "/terms",
    index: true,
    why: "same reading as /privacy",
  },
  {
    path: "/graph",
    index: false,
    why: "paywalled by the ruling of 2026-09-19, and app/graph/page.jsx records it as unlisted until its UI is fixed",
  },
  {
    path: "/routines",
    index: false,
    why: "nothing is built behind it yet, so a search result would land a stranger on an empty promise",
  },
  {
    path: "/desk",
    index: false,
    why: "reads a signed-in account and a private token",
  },
  {
    path: "/sign-in",
    index: false,
    why: "an auth form is not an answer to any search",
  },
  { path: "/sign-up", index: false, why: "same reading as /sign-in" },
  {
    path: "/unsubscribe",
    index: false,
    why: "acts on a link from an email, never on a search result",
  },
  {
    path: "/api",
    index: false,
    why: "route handlers, not pages; the prefix covers every one of them",
  },
];

export function indexable() {
  return ROUTES.filter((r) => r.index).map((r) => r.path);
}

export function disallowed() {
  return ROUTES.filter((r) => !r.index).map((r) => r.path);
}
