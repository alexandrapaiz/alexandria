import { SITE_ORIGIN, disallowed } from "../lib/public-routes.js";

// /robots.txt. Until this file existed the site served a 404 there, which is
// not a neutral state: no robots.txt means allow everything, and everything
// here included `/desk`, `/sign-in`, `/sign-up`, `/routines` and the paywalled
// `/graph`, all five of which answer 200 to an anonymous request and none of
// which the product lists anywhere. The crawlers were invited onto them by
// default.
//
// Two jobs, and they are separate:
//
// **It names the sitemap.** That is the one line in robots.txt that a crawler
// uses to find pages it was not already linked to, which for a weekly archive
// is the point of having one.
//
// **It allows the named AI crawlers explicitly.** docs/sales/geo-plan.md item 3
// asks for exactly that, and the reason it is not redundant with `User-agent: *`
// is a rule of the format rather than a preference: a group addressed to a
// named agent *replaces* the wildcard group for that agent rather than adding
// to it. So each named group repeats the same Disallow list — a named group
// with no Disallow would give that crawler more of this site than `*` gets —
// and if the wildcard group is ever tightened, these four do not silently
// lose their access along with it.
//
// The four are the four the GEO plan names, and no more. `Google-Extended` is
// the odd one: it is a training-and-grounding token, not a crawler, and it has
// no effect on whether Google indexes a page. It is listed because the plan
// lists it and because declining it is a decision this seat does not get to
// make quietly by omission.
const AI_CRAWLERS = [
  "GPTBot",
  "ClaudeBot",
  "PerplexityBot",
  "Google-Extended",
];

export default function robots() {
  const disallow = disallowed();
  return {
    rules: [
      { userAgent: "*", allow: "/", disallow },
      ...AI_CRAWLERS.map((userAgent) => ({ userAgent, allow: "/", disallow })),
    ],
    sitemap: `${SITE_ORIGIN}/sitemap.xml`,
  };
}
