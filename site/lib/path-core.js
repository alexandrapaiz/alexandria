// Every decision the buyer-path measurement makes, as pure functions: which
// requests are worth a row, which step of the path a route is, what the row
// holds, and how a set of counts becomes a funnel a human reads. No imports,
// no network, no database, no clock of its own. site/lib/path.js is the other
// half and it does the I/O.
//
// Keep this file import-free. tests/path.test.mjs loads it by reading the
// source and evaluating it, the same way tests/waitlist.test.mjs loads
// site/lib/waitlist-core.js, and that works precisely because there are no
// imports to resolve.
//
// ## The sentence this file is built around
//
// site/app/privacy/page.jsx promises a reader that "there is no analytics, no
// tracking pixel, no advertising network, and no third-party script watching
// you read". Everything below follows from taking that literally.
//
// So there is no function here that produces an identifier, and that is the
// design rather than an omission. No cookie, no session, no address, no user
// agent, and specifically not the salted irreversible hash of the two that
// every cookieless analytics product ships, because that hash is still a
// pseudonymous identifier for one person and the promise rules it out.
//
// `funnel()` below is where the cost of that lands. It reports counts and it
// refuses to compute a conversion rate, because two steps counted here are
// two counts of events rather than two counts of the same people, and a ratio
// of those two numbers would read like a rate while meaning nothing. The
// refusal is the same discipline tools/delivery_health.py already keeps: a
// thing this cannot answer says so, and never guesses.
//
// What the card asked for survives the refusal. Board card c688ef2e wanted to
// know which skill actually sells, and a count per skill answers that without
// knowing who anybody is.

// ------------------------------------------------------------- the five steps
//
// The buyer's path in order, which is the order the funnel prints in. These
// five words are also the `check` constraint on `path_events.step` in
// db/schema.sql, and tests/path.test.mjs asserts the two lists agree, so a
// step added here and not there fails on the pull request that adds it rather
// than on the first insert in production.
export const STEPS = ["visit", "catalog", "skill", "pricing", "checkout"];

// The sixth step of the path, which is not in the list above and is not a row
// in this table at all. A payment is already recorded, by the Polar webhook,
// onto `users.subscription_status` (site/lib/polar.js). Counting it here as
// well would be a second copy of a number the billing record already holds,
// and the first time the two disagreed the answer would be whichever one the
// reader happened to open.
export const PAYMENT_STEP = "payment";

// And the step between `checkout` and nothing, which no row here can ever
// carry. `/plugin marketplace add alexandrapaiz/alexandria` is a git clone
// from the buyer's terminal to GitHub, so it never touches this site and no
// instrumentation here can see it. Named rather than left out, because a
// funnel that silently skips a step reads as a funnel with no such step.
export const INSTALL_STEP = "install";

// --------------------------------------------------- which requests count
//
// A measurement that records everything measures the crawler budget. Three
// kinds of request are dropped, and the order matters because the first is
// the one that would otherwise dominate the table.

// Next.js prefetches a route when a link scrolls into view, which produces a
// request for a page nobody has looked at. Counting those would turn "how
// many people read a skill" into "how many links were near a viewport".
const PREFETCH_HEADERS = ["next-router-prefetch", "purpose", "x-purpose"];

export function isPrefetch(headers) {
  const get = headerReader(headers);
  if (get("next-router-prefetch")) return true;
  for (const name of PREFETCH_HEADERS) {
    if (String(get(name) ?? "").toLowerCase().includes("prefetch")) return true;
  }
  return false;
}

// Everything that is not a person arriving at a page: the framework's own
// traffic, assets, and the endpoints this measurement is made of. `/api/path`
// is not in the list because there is no such endpoint, which is the point of
// doing this in middleware: there is nothing for a script to call and nothing
// to rate limit.
const NEVER = [
  "/_next",
  "/favicon",
  "/robots.txt",
  "/sitemap.xml",
  "/llms.txt",
  "/api/funnel",
  "/__clerk",
];

export function isCounted({ method = "GET", pathname = "", headers = null } = {}) {
  // A HEAD is a probe and a POST to a form is not a page view. GET only.
  if (String(method).toUpperCase() !== "GET") return false;
  if (!pathname.startsWith("/")) return false;
  if (isPrefetch(headers)) return false;
  for (const prefix of NEVER) {
    if (pathname === prefix || pathname.startsWith(prefix + "/")) return false;
  }
  // An extension in the last segment is an asset the matcher in
  // site/middleware.js already excludes. Checked here too, because the two
  // files are edited by different hands and this one is the one under test.
  const last = pathname.split("/").pop() ?? "";
  if (last.includes(".")) return false;
  return true;
}

// ------------------------------------------------------------- which step
//
// Routes to steps, longest prefix first so that /skills/foo is a skill and
// not the catalogue. Everything that is a page and matches none of these is a
// `visit`, because a visit is the top of the funnel and not a category of its
// own.
const ROUTES = [
  { prefix: "/api/checkout", step: "checkout" },
  { prefix: "/skills", step: "catalog" },
  { prefix: "/pricing", step: "pricing" },
];

export function stepForPath(pathname = "") {
  const path = normalizePath(pathname);
  for (const route of ROUTES) {
    if (path === route.prefix || path.startsWith(route.prefix + "/")) {
      // One skill read is a different question from the catalogue, so a
      // route under /skills with a slug on it is its own step. The catalogue
      // page itself carries no slug.
      if (route.step === "catalog" && path !== "/skills") return "skill";
      return route.step;
    }
  }
  return "visit";
}

// -------------------------------------------------------------- the path
//
// Collapsed to the shape the funnel groups by. A week's issue and the next
// week's issue are one path's worth of reading rather than one path each, and
// the identifier that distinguishes them goes nowhere: it is in the route, it
// is not a fact about a person, and keeping it would make `path` a dimension
// with a new value every Monday.
const COLLAPSE = [
  { prefix: "/library", to: "/library/:week" },
  { prefix: "/skills", to: "/skills/:slug" },
  { prefix: "/api/checkout", to: "/api/checkout/:plan" },
];

const MAX_PATH = 128;

export function normalizePath(raw) {
  let path = String(raw ?? "").trim();
  // A query string is where an address ends up by accident, so it is cut
  // before anything else looks at the value. Same for a fragment, which a
  // server never sees anyway and would be a surprise if it did.
  path = path.split("?")[0].split("#")[0];
  if (!path.startsWith("/")) path = "/" + path;
  // A trailing slash is the same page. Kept for the root, which is only a
  // slash.
  if (path.length > 1 && path.endsWith("/")) path = path.slice(0, -1);
  return path.slice(0, MAX_PATH).toLowerCase();
}

export function groupedPath(raw) {
  const path = normalizePath(raw);
  for (const rule of COLLAPSE) {
    if (path.startsWith(rule.prefix + "/")) return rule.to;
  }
  return path;
}

// ------------------------------------------------------------- the detail
//
// The one varying field, and the only place a value from the request reaches
// the database. Bounded and restricted to what a slug can hold, the same way
// waitlist-core.js bounds `source`, because this arrives in a URL and ends up
// in a column.
//
// It is populated for exactly two steps. A `skill` row carries which skill,
// which is the card's question. A `checkout` row carries which plan, which is
// the only thing that distinguishes one checkout from another. Every other
// step gets null rather than a repetition of its own path.
const MAX_DETAIL = 64;

export function normalizeDetail(raw) {
  const value = String(raw ?? "").trim().toLowerCase().slice(0, MAX_DETAIL);
  const safe = value.replace(/[^a-z0-9_-]/g, "");
  return safe || null;
}

export function detailFor(step, pathname) {
  if (step !== "skill" && step !== "checkout") return null;
  const path = normalizePath(pathname);
  const segments = path.split("/").filter(Boolean);
  return normalizeDetail(segments[segments.length - 1]);
}

// ---------------------------------------------------------------- the row
//
// The whole row, so that the only file that knows what a recorded step is
// worth is this one. Returns null for a request that is not counted, so the
// caller has one question to ask rather than four.
export function pathRow({ method = "GET", pathname = "", headers = null } = {}) {
  if (!isCounted({ method, pathname, headers })) return null;
  const step = stepForPath(pathname);
  return {
    step,
    path: groupedPath(pathname),
    detail: detailFor(step, pathname),
  };
}

// --------------------------------------------------------------- the funnel
//
// Counts in, a funnel out. Three kinds of number arrive and they are kept
// apart on purpose, because they are known with different confidence:
//
//   counts   the five steps above, from `path_events`
//   paid     the payment, from `users`, which is a state and not an event
//   clones   the install, from GitHub, which this org cannot currently read
//
// A step whose number is unknown says `null` and carries the reason. It never
// reads zero. `tools/delivery_health.py` argues this at length and it is the
// same argument: reporting an unmeasured step as zero teaches the reader to
// ignore the report, and a reader who ignores the report is worse than no
// report.
export function funnel({ counts = {}, paid = null, install = null } = {}) {
  const rows = STEPS.map((step) => ({
    step,
    events: numberOr(counts[step], 0),
    measured: true,
    note: null,
  }));

  // The install sits between the catalogue and the payment in the buyer's
  // real order, and it is inserted at that position rather than appended, so
  // that a reader seeing the funnel sees the gap where it actually is.
  rows.splice(STEPS.indexOf("pricing"), 0, {
    step: INSTALL_STEP,
    events: numberOr(install?.clones, null),
    measured: install?.clones != null,
    note: install?.reason ?? "no reader for GitHub's clone traffic",
  });

  rows.push({
    step: PAYMENT_STEP,
    events: numberOr(paid?.accounts, null),
    measured: paid?.accounts != null,
    note: paid?.reason ?? "no reader for the billing record",
  });

  return {
    rows,
    // Said out loud rather than left for a reader to work out from the
    // absence of a percentage. The schema comment and this file's header both
    // explain why, and this is the field a JSON reader sees.
    rate: null,
    rate_reason:
      "these are counts of events and not counts of people, so a ratio of two of them is not a conversion rate",
  };
}

function numberOr(value, fallback) {
  const n = Number(value);
  return Number.isFinite(n) && n >= 0 ? Math.round(n) : fallback;
}

// A headers object from a Request, a plain object, or nothing. Normalised to
// one lower-cased lookup so that the functions above read the same whether
// they are called from middleware or from a test.
function headerReader(headers) {
  if (!headers) return () => null;
  if (typeof headers.get === "function") return (name) => headers.get(name);
  const lower = {};
  for (const [key, value] of Object.entries(headers)) {
    lower[String(key).toLowerCase()] = value;
  }
  return (name) => lower[String(name).toLowerCase()] ?? null;
}
