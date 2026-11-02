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

// The canonical host, derived rather than retyped, because the whole point of
// the block below is that one name is canonical and the others are not.
export const SITE_HOST = new URL(SITE_ORIGIN).host;

// The hosts that serve this same deployment under a name that is not the
// canonical one.
//
// On 2026-11-02 the custom domain and the Vercel alias answered 200 for every
// page and returned byte-identical HTML on the same read, so this is one
// deployment reachable under two names. The alias became crawlable that
// morning, when the robots file landed and invited everything; before it there
// was no invitation at all, so the duplicate is downstream of a correct change
// rather than a defect in it. Two complete copies of a site compete for the
// same queries, and the stronger of the two available answers is to stop
// serving one of them, which `middleware.js` now does with a 308.
//
// **This is an explicit list of retired names and not the rule "everything
// that is not SITE_HOST".** The inverted rule is shorter and it breaks two
// things this one cannot. Every Vercel preview deployment answers on its own
// generated `*.vercel.app` hostname, so a blanket redirect sends every review
// of every pull request to production and there is no way to look at a branch
// again. And the dev server answers on `localhost`, which the visual harness
// drives. A name is added here when it is deliberately aliased to this
// deployment and is not the one we want indexed, which is an act somebody
// performs in the Vercel dashboard rather than a shape a regex can recognise.
//
// What covers the gap that leaves: an alias nobody declared here is still
// crawlable, and the thing that notices is the crawler-policy probe the
// distribution seat runs against each origin.
export const DUPLICATE_HOSTS = ["alexandria-lilac.vercel.app"];

// A `Host` header carries the port when there is one and its case is not
// guaranteed, so neither is compared raw.
function sameHost(a, b) {
  if (!a || !b) return false;
  return a.toLowerCase().split(":")[0] === b.toLowerCase().split(":")[0];
}

export function isDuplicateHost(host) {
  return DUPLICATE_HOSTS.some((h) => sameHost(host, h));
}

// Where a request that arrived on a retired name should have gone, or null when
// the name is one this deployment keeps. `pathWithQuery` is passed in rather
// than read from a request, so this stays testable without a Next request
// object and this module stays free of framework imports.
export function canonicalRedirect(host, pathWithQuery) {
  if (!isDuplicateHost(host)) return null;
  return SITE_ORIGIN + pathWithQuery;
}

// The absolute URL of one of this site's paths. A canonical link, like a
// sitemap <loc>, cannot be relative.
export function canonicalUrl(path) {
  return new URL(path, SITE_ORIGIN).toString();
}

// The non-HTML representation the whole site offers, which `app/layout.jsx`
// declares on every page.
//
// It is repeated here for one reason worth knowing before touching it. Next
// merges `metadata` one top-level key at a time, so a page that exports
// `alternates` REPLACES the layout's `alternates` rather than adding to it,
// and the layout's is exactly this map. A page that set only `canonical` would
// silently drop the plain-text alternate from its own head, which is a
// regression no screenshot can show and no page renders differently for. So
// `canonicalAlternates` below hands back both halves together and the pages
// never assemble the object themselves.
//
// `app/layout.jsx` still types this map out rather than importing it, so the
// value lives in two places for now. That file is claimed by the distribution
// seat's open pull request #786, and pointing it here is one line that belongs
// in whichever diff touches it second. Filed in docs/ideas.md.
export const ALTERNATE_TYPES = { "text/plain": "/llms.txt" };

export function canonicalAlternates(path) {
  return { canonical: canonicalUrl(path), types: ALTERNATE_TYPES };
}

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
