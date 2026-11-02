import { SITE_ORIGIN, indexable } from "../lib/public-routes.js";
import { publishedIssues } from "../lib/issues-live.js";

// /sitemap.xml. The eight public routes, plus every published weekly issue.
//
// The issues are the reason this file is worth having. They are the pages a
// stranger could actually arrive on from a search, there is one more of them
// every Monday, and until now nothing told a crawler they existed except a
// link on `/library`.
//
// Dynamic for the same reason `/library` is (`app/library/page.jsx`): the list
// of published weeks is the `digests` table, and that table gains a row on
// Monday morning without a deploy. A statically built sitemap would advertise
// last week's archive until somebody noticed.
export const dynamic = "force-dynamic";

// Fails closed, like every other reader of that table (`lib/issues-live.js`
// says so in its own header). A sitemap that answers 500 teaches a crawler to
// stop asking for it; a sitemap missing this week's issue costs one week. So
// the archive read is allowed to fail and the eight routes are served anyway.
async function weeks() {
  try {
    return await publishedIssues();
  } catch {
    return [];
  }
}

export default async function sitemap() {
  const issues = await weeks();
  return [
    ...indexable().map((path) => ({ url: `${SITE_ORIGIN}${path}` })),
    ...issues.map((issue) => ({ url: `${SITE_ORIGIN}/library/${issue.week}` })),
  ];
}
